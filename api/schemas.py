"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CarBase(BaseModel):
    name: str
    year: Optional[int] = None
    series: Optional[str] = None
    series_number: Optional[str] = None
    color: Optional[str] = None
    tampo: Optional[str] = None
    base_color: Optional[str] = None
    window_color: Optional[str] = None
    interior_color: Optional[str] = None
    wheel_type: Optional[str] = None
    toy_number: Optional[str] = None
    country: Optional[str] = None
    image_url: Optional[str] = None
    fandom_url: Optional[str] = None


class CarCreate(CarBase):
    pass


class CarRead(CarBase):
    id: int
    view_count: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CarsResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[CarRead]


class YearsResponse(BaseModel):
    years: list[int]


class SeriesResponse(BaseModel):
    series: list[str]
