"""Database session configuration and initialization."""

from typing import Generator
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# For SQLite, check_same_thread=False allows multiple threads
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining a SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables and ensure all model columns exist in SQLite."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    # Import all models to ensure they are registered on Base.metadata
    from app.models.user import User  # noqa: F401
    from app.models.issue import Issue  # noqa: F401
    from app.models.issue_update import IssueUpdate  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Lightweight SQLite schema synchronization for newly added columns
    try:
        with engine.begin() as conn:
            result = conn.exec_driver_sql("PRAGMA table_info(issues)")
            columns = [row[1] for row in result.fetchall()]
            if columns and "ai_status" not in columns:
                conn.exec_driver_sql("ALTER TABLE issues ADD COLUMN ai_status VARCHAR(50) DEFAULT 'fallback'")
    except Exception:
        pass
