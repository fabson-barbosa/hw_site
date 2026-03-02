"""Business logic / service layer for the API."""
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Car


def get_cars(
    db: Session,
    year: Optional[int] = None,
    series: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    query = db.query(Car)
    if year is not None:
        query = query.filter(Car.year == year)
    if series:
        query = query.filter(Car.series == series)
    if search:
        query = query.filter(Car.name.ilike(f"%{search}%"))
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return total, items


def get_car(db: Session, car_id: int) -> Optional[Car]:
    return db.query(Car).filter(Car.id == car_id).first()


def record_view(db: Session, car_id: int) -> Optional[Car]:
    car = get_car(db, car_id)
    if car is None:
        return None
    car.view_count = (car.view_count or 0) + 1
    db.commit()
    db.refresh(car)
    return car


def get_years(db: Session) -> list[int]:
    rows = (
        db.query(Car.year)
        .filter(Car.year.isnot(None))
        .distinct()
        .order_by(Car.year.desc())
        .all()
    )
    return [r[0] for r in rows]


def get_series(db: Session) -> list[str]:
    rows = (
        db.query(Car.series)
        .filter(Car.series.isnot(None))
        .distinct()
        .order_by(Car.series)
        .all()
    )
    return [r[0] for r in rows]


def get_most_viewed(db: Session, limit: int = 10) -> list[Car]:
    return (
        db.query(Car)
        .filter(Car.view_count > 0)
        .order_by(Car.view_count.desc())
        .limit(limit)
        .all()
    )


def upsert_car(db: Session, data: dict) -> Car:
    """Insert or update a car record identified by toy_number + year."""
    toy_number = data.get("toy_number")
    year = data.get("year")
    car = None
    if toy_number and year:
        car = (
            db.query(Car)
            .filter(Car.toy_number == toy_number, Car.year == year)
            .first()
        )
    if car is None:
        car = Car(**data)
        db.add(car)
    else:
        for key, value in data.items():
            setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car
