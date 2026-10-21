from database import engine, Base
from models import Event, Registration

Base.metadata.create_all(bind=engine)

print("EventSphere tables created successfully")