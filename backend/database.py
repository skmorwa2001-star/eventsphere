
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from local .env
load_dotenv()

# Use PostgreSQL in deployment; SQLite locally by default.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./eventsphere.db"
)

# SQLite needs a special connection argument; PostgreSQL does not.
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
