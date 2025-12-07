import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define the absolute path for the SQLite database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "./scraped_data.db")

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is required for SQLite with FastAPI
# to allow concurrent access from multiple threads/requests.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get a database session for FastAPI endpoints.
    Ensures the session is closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()