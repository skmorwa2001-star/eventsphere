from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from pwdlib import PasswordHash

from database import SessionLocal, Base , engine
import models
from models import Event, Registration, User
from schemas import EventCreate, RegistrationCreate, UserCreate, UserLogin
import uuid
import qrcode
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(title="EventSphere API")

# Create database tables for all imported models
Base.metadata.create_all(bind=engine)

if "role" not in {
    column["name"] for column in inspect(engine).get_columns("users")
}:
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE users ADD COLUMN role "
                "VARCHAR(20) NOT NULL DEFAULT 'participant'"
            )
        )

# Add events.event_date to databases created before this column existed
if "event_date" not in {
    column["name"] for column in inspect(engine).get_columns("events")
}:
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE events ADD COLUMN event_date TIMESTAMP"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
QR_FOLDER=Path("qr_codes")
QR_FOLDER.mkdir(exist_ok=True)  # must exist before StaticFiles mounts it

app.mount(
    "/qr_codes",
    StaticFiles(directory="qr_codes"),
    name="qr_codes"
)

QR_FOLDER.mkdir(exist_ok=True)

def iso(value):
    return value.isoformat() if value else None

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()    

@app.get("/")
def home():
    return{
        "message":"Welcome to EventSphere!",
        "status":"running"}

@app.post("/events",status_code=201)
def create_event(event_data:EventCreate, db:Session= Depends(get_db)):
    new_event=Event(title=event_data.title, description=event_data.description, location=event_data.location, event_date=event_data.event_date, capacity=event_data.capacity)

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return{
        "message":"Event created successfully",
        "event":{
            "id":new_event.id,
            "title":new_event.title,
            "description":new_event.description,
            "location":new_event.location,
            "capacity":new_event.capacity,
            "event_date":iso(new_event.event_date)
        }
    }

@app.get("/events")
def get_events(db:Session=Depends(get_db)):
    events=db.query(Event).all()

    return{
        "message":"Event fetched successfully",
        "total":len(events),
        "events":[
            {
                "id":event.id,
                "title":event.title,
                "description":event.description,
                "location":event.location,
                "capacity":event.capacity,
                "event_date":iso(event.event_date)
            }
            for event in events
        ]
    }


@app.put("/events/{event_id}")
def update_event(
    event_id:int,
    event_data:EventCreate,
    db:Session=Depends(get_db)
):
    event=db.query(Event).filter(Event.id==event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    event.title=event_data.title
    event.description=event_data.description
    event.location=event_data.location
    event.event_date=event_data.event_date
    event.capacity=event_data.capacity

    db.commit()
    db.refresh(event)

    return{
        "message":"Event updated successfully",
        "event":{
            "id":event.id,
            "title":event.title,
            "description":event.description,
            "location":event.location,
            "capacity":event.capacity,
                "event_date":iso(event.event_date)
        }
    }

@app.delete("/events/{event_id}")
def delete_event(
    event_id:int,
    db:Session=Depends(get_db)
):
    event=db.query(Event).filter(Event.id==event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    db.delete(event)
    db.commit()

    return{
        "message":"Event deleted successfully",
        "event_id":event_id
    }


@app.post("/events/{event_id}/register", status_code=201)
def register_attendee(
    event_id: int,
    registration_data: RegistrationCreate,
    db: Session = Depends(get_db)
):
    # 1. Check whether the event exists
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    # Check if email is already registrated
    existing_registration=(
        db.query(Registration)
        .filter(
            Registration.event_id==event_id,
            Registration.attendee_email==registration_data.attendee_email
        )
        .first()
    )
    if existing_registration is not None:
        raise HTTPException(
            status_code=400,
            detail="This email is already registrated for this event"
        )

    # 2. Check current registrations
    registered_count = (
        db.query(Registration)
        .filter(Registration.event_id == event_id)
        .count()
    )

    # 3. Enforce event capacity
    if registered_count >= event.capacity:
        raise HTTPException(
            status_code=400,
            detail="Event is full"
        )

    # 4. Save the registration
    new_registration = Registration(
        attendee_name=registration_data.attendee_name,
        attendee_email=registration_data.attendee_email,
        event_id=event_id,
        ticket_code=str(uuid.uuid4())
    )

    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    # Generate OR code using the unique ticket code
    qr=qrcode.make(new_registration.ticket_code)

    # SAve QR image with registration ID as filename
    qr_path=QR_FOLDER/f"ticket_{new_registration.id}.png"
    qr.save(qr_path)

    return {
        "message": "Registration successful",
        "registration": {
            "id": new_registration.id,
            "attendee_name": new_registration.attendee_name,
            "attendee_email": new_registration.attendee_email,
            "event_id": new_registration.event_id,
            "ticket_code": new_registration.ticket_code,
            "checked_in":bool(new_registration.checked_in),
            "qr_code_url":f"/qr_codes/ticket_{new_registration.id}.png"
        }
    }

@app.get("/events/{event_id}/registrations")
def get_event_registrations(
    event_id:int,
    db:Session=Depends(get_db)
):
    # Check whether the event exists
    event=db.query(Event).filter(
        Event.id==event_id
    ).first()

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    # Fetch all registrations for this event
    registrations=(db.query(Registration).filter(Registration.event_id==event_id).all())

    return{
        "event_id":event_id,
        "total_registrations":len(registrations),
        "attendees":[
            {
                "id":registration.id,
                "attendee_name":registration.attendee_name,
                "attendee_email":registration.attendee_email,
                "checked_in":bool(registration.checked_in)
            }
            for registration in registrations
        ]
    }

@app.delete("/registrations/{registration_id}")
def cancel_registration(
    registration_id:int,
    db:Session=Depends(get_db)
):
    # find the registration
    registration=(
        db.query(Registration).filter(Registration.id==registration_id).first()
    )

    # Check wheather registration exists
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Delete the registration
    db.delete(registration)
    db.commit()

    return{
        "message":"Registration cancelled successfully",
        "registration_id":registration_id
    }

@app.post("/registrations/check-in/{ticket_code}")
def check_in_attendee(
    ticket_code:str,
    db:Session=Depends(get_db)
):
    registration=(
        db.query(Registration).filter(Registration.ticket_code==ticket_code).first()
    )

    if registration is None:
        raise HTTPException(status_code=404, detail="Invalid ticket code")
    if registration.checked_in==1:
        raise HTTPException(status_code=400, detail="Ticket already checked in")

    registration.checked_in=1
    db.commit()
    db.refresh(registration)

    return{
        "message":"Check-in successfully",
        "attendee_name":registration.attendee_name,
        "event_id":registration.event_id,
        "checked_in":True
    }

@app.get("/events/{event_id}/analytics")
def get_event_analytics(
    event_id:int,
    db:Session=Depends(get_db)
):
    event=db.query(Event).filter(Event.id==event_id).first()

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    registrations=(db.query(Registration).filter(Registration.event_id==event_id).all())

    total_registrations=len(registrations)

    checked_in_count=sum(1 for r in registrations if r.checked_in==1)

    pending_count=total_registrations-checked_in_count

    return{
        "event_id":event.id,
        "event_title":event.title,
        "capacity":event.capacity,
        "total_registrations":total_registrations,
        "checked_in":checked_in_count,
        "pending_count_in":pending_count,
        "available_seats":max(event.capacity-total_registrations,0)
    }


password_hash = PasswordHash.recommended()

@app.post("/auth/signup", status_code=201)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=password_hash.hash(user_data.password),
        role=user_data.role
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not create account"
        )

    return {
        "message": "Account created successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }


@app.post("/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if user is None or not password_hash.verify(
        user_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if user.role != user_data.role:
        raise HTTPException(
            status_code=403,
            detail=f"This account uses the {user.role} role."
        )

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }
