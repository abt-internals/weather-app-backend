from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()


# username = "postgres"
# password = quote_plus("Yadnyesh@7841")
# host = "localhost"  # or "::1" for IPv6
# port = "5432"
# database = "postgres"

# SQLAlchemy connection URL
DATABASE_URL = os.getenv("Database_url")

# Create the PostgreSQL engine
engine = create_engine(DATABASE_URL,pool_pre_ping=True)

# Create a session factory
SessionLocal = sessionmaker( autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
