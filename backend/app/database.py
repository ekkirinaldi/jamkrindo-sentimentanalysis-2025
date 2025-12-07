"""
Database setup and configuration.
SQLAlchemy engine and session management for SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import DATABASE_URL

# Create engine with UTF-8 encoding for proper Indonesian text storage
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from app.models import company, sentiment, legal_record, analysis_summary
    from app.models.company import Base
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

