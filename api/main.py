"""FastAPI application — hw-cotacao-brasil."""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import services
from database import create_tables, get_db
from schemas import CarRead, CarsResponse, SeriesResponse, YearsResponse


@asynccontextmanager
async def lifespan(app_: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="HW Cotação Brasil",
    description="API de carrinhos Hot Wheels para o mercado brasileiro",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Cars
# ---------------------------------------------------------------------------


@app.get("/api/v1/cars", response_model=CarsResponse, tags=["cars"])
def list_cars(
    year: Optional[int] = None,
    series: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Lista carrinhos com filtros opcionais."""
    if limit > 100:
        limit = 100
    total, items = services.get_cars(
        db, year=year, series=series, search=search, skip=skip, limit=limit
    )
    return CarsResponse(total=total, skip=skip, limit=limit, items=items)


@app.get("/api/v1/cars/most-viewed", response_model=list[CarRead], tags=["cars"])
def most_viewed(limit: int = 10, db: Session = Depends(get_db)):
    """Retorna os carrinhos mais visualizados."""
    if limit > 50:
        limit = 50
    return services.get_most_viewed(db, limit=limit)


@app.get("/api/v1/cars/{car_id}", response_model=CarRead, tags=["cars"])
def get_car(car_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de um carrinho pelo ID."""
    car = services.get_car(db, car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")
    return car


@app.post("/api/v1/cars/{car_id}/view", response_model=CarRead, tags=["cars"])
def record_view(car_id: int, db: Session = Depends(get_db)):
    """Registra uma visualização e retorna o carrinho atualizado."""
    car = services.record_view(db, car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")
    return car


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


@app.get("/api/v1/years", response_model=YearsResponse, tags=["metadata"])
def list_years(db: Session = Depends(get_db)):
    """Retorna a lista de anos disponíveis no catálogo."""
    return YearsResponse(years=services.get_years(db))


@app.get("/api/v1/series", response_model=SeriesResponse, tags=["metadata"])
def list_series(db: Session = Depends(get_db)):
    """Retorna a lista de séries disponíveis no catálogo."""
    return SeriesResponse(series=services.get_series(db))
