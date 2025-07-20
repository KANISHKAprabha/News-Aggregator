# app/database.py
from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base

from sqlalchemy.orm import sessionmaker
from .config import get_settings




engine = create_engine(get_settings().db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()