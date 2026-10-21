from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from database import Base


class Event(Base):
    __tablename__="events"

    id=Column(Integer, primary_key=True, index=True)
    title=Column(String(150),nullable=False)
    description=Column(Text,nullable=False)
    location=Column(String(200),nullable=False)
    event_date=Column(DateTime, nullable=True)  # date + time of the event
    capacity=Column(Integer, nullable=False)

class Registration(Base):
    __tablename__="registrations"

    __table_args__=(UniqueConstraint("event_id","attendee_email",name="uq_event_attendee_email",),)

    id=Column(Integer, primary_key=True, index=True)
    attendee_name=Column(String(100), nullable=False)
    attendee_email=Column(String(150), nullable=False)
    event_id=Column(Integer, ForeignKey("events.id", ondelete="CASCADE") , nullable=False)    
    ticket_code=Column(String(36),unique=True, nullable=True)
    checked_in=Column(Integer, default=0, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="participant")
