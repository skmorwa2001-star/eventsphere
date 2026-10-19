from pydantic import BaseModel, Field, EmailStr

class EventCreate(BaseModel):
    title:str=Field(min_length=3, max_length=150)
    description:str | None=None
    location:str=Field(min_length=2, max_length=200)
    capacity:int=Field(gt=0)

class RegistrationCreate(BaseModel):
    attendee_name:str=Field(min_length=2, max_length=100)
    attendee_email:EmailStr    