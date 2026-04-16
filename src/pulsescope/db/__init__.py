"""Database configuration and session management."""

import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

def get_database_url() -> str:
    """Get database URL from environment or use local SQLite for development."""
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return db_url
    
    # Default to SQLite for easy development
    # Use PostgreSQL in production via DATABASE_URL env var
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "pulsescope.db")
    return f"sqlite:///{os.path.abspath(db_path)}"

# Create engine
# For SQLite, we need to configure it differently
db_url = get_database_url()
if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


@contextmanager
def get_db():
    """Get a database session as a context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
