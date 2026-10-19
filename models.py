from sqlalchemy import Column, Integer, String, Text
from database import Base


class Event(Base):
    __tablename__="events"

    id=Column(Integer, primary_key=True, index=True)
    title=Column(String(150),nullable=False)
    description=Column(Text,nullable=False)
    location=Column(String(200),nullable=False)
    capacity=Column(Integer, nullable=False)

class Registration(Base):
    __tablename__="registrations"

    id=Column(Integer, primary_key=True, index=True)
    attendee_name=Column(String(100), nullable=False)
    attendee_email=Column(String(150), nullable=False)
    event_id=Column(Integer, nullable=False)    
    ticket_code=Column(String(36),unique=True, nullable=True)
    checked_in=Column(Integer, default=0, nullable=False)