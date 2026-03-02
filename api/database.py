"""Database setup and models for hw-cotacao-brasil."""
import os
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_PATH = os.environ.get("DB_PATH", "hw_cars.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    year = Column(Integer, index=True)
    series = Column(String, index=True)
    series_number = Column(String)
    color = Column(String)
    tampo = Column(String)
    base_color = Column(String)
    window_color = Column(String)
    interior_color = Column(String)
    wheel_type = Column(String)
    toy_number = Column(String)
    country = Column(String)
    image_url = Column(String)
    fandom_url = Column(String)
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
