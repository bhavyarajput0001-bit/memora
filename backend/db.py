"""
MEMORA Database - Support for both SQLite and PostgreSQL (Supabase)
"""
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Optional

from backend.config import DB_PATH
from backend.models import Base


def get_database_url() -> str:
    """Get database URL from environment or default to SQLite."""
    # Check for Supabase connection string
    supabase_url = os.environ.get("MEMORA_DATABASE_URL", "")
    
    if supabase_url and ("supabase" in supabase_url or "postgres" in supabase_url):
        return supabase_url
    
    # Default to SQLite
    return f"sqlite:///{DB_PATH}"


# Engine setup
_database_url = get_database_url()
_is_postgres = "postgres" in _database_url or "supabase" in _database_url

if _is_postgres:
    # PostgreSQL with connection pooling
    engine = create_engine(
        _database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )
else:
    # SQLite
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
    """Check if a table exists."""
    inspector = inspect(engine)
    return name in inspector.get_table_names()


def row_count(table_name: str) -> int:
    """Get row count for a table."""
    with get_session() as db:
        from sqlalchemy import text
        result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar() or 0


def get_db_type() -> str:
    """Return 'postgres' or 'sqlite'."""
    return "postgres" if _is_postgres else "sqlite"


def is_supabase() -> bool:
    """Check if using Supabase."""
    return _is_postgres