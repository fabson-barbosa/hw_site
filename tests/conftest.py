"""Shared pytest fixtures for hw-cotacao-brasil API tests."""
import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Make the api package importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from database import Base, Car, get_db  # noqa: E402
from main import app  # noqa: E402

TEST_DATABASE_URL = "sqlite://"  # in-memory SQLite


@pytest.fixture(scope="session")
def engine():
    _engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=_engine)
    yield _engine
    _engine.dispose()


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_cars(db_session):
    """Insert a handful of test cars and return them."""
    cars = [
        Car(
            name="Camaro SS",
            year=2022,
            series="Mainline",
            series_number="1",
            color="Red",
            toy_number="HW001",
            view_count=5,
        ),
        Car(
            name="Dodge Charger",
            year=2022,
            series="Mainline",
            series_number="2",
            color="Blue",
            toy_number="HW002",
            view_count=3,
        ),
        Car(
            name="Ford Mustang",
            year=2023,
            series="Fast & Furious",
            series_number="1",
            color="Green",
            toy_number="HW003",
            view_count=0,
        ),
    ]
    for car in cars:
        db_session.add(car)
    db_session.commit()
    for car in cars:
        db_session.refresh(car)
    return cars
