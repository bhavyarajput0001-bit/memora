"""MEMORA database — SQLite + SQLAlchemy session management."""
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

from backend.config import DB_PATH
from backend.models import Base

# Ensure parent dir exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """FastAPI dependency — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session() -> Session:
    """Context manager for non-FastAPI code."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def table_exists(name: str) -> bool:
    inspector = inspect(engine)
    return name in inspector.get_table_names()


def row_count(table_name: str) -> int:
    with get_session() as db:
        result = db.execute(__import__("sqlalchemy").text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar() or 0