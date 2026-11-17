"""PostgreSQL engine and per-request SQLAlchemy sessions."""

import os
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import MetaData, URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class Base(DeclarativeBase):
    """Base class for the application's SQLAlchemy models."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


database_url = URL.create(
    drivername="postgresql+pg8000",
    username=os.getenv("POSTGRES_USER", "fleetflow_app"),
    password=os.getenv("POSTGRES_PASSWORD", ""),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("POSTGRES_DB", "fleetflow_db"),
)

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Yield a database session and close it after the request finishes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
