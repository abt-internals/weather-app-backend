from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


username = "postgres"
password = quote_plus("Yadnyesh@7841")
host = "localhost"  # or "::1" for IPv6
port = "5432"
database = "postgres"

# SQLAlchemy connection URL
DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Create the PostgreSQL engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker( bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
