from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

class EventCreate(BaseModel):
    title:str=Field(min_length=3, max_length=150)
    description:str | None=None
    location:str=Field(min_length=2, max_length=200)
    event_date:datetime | None=None
    capacity:int=Field(gt=0)

class RegistrationCreate(BaseModel):
    attendee_name:str=Field(min_length=2, max_length=100)
    attendee_email:EmailStr

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["organizer", "participant"] = "participant"

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    role: Literal["organizer", "participant"] = "participant"
