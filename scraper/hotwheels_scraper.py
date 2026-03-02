"""
Fandom Hot Wheels Wiki Scraper
Populates the SQLite database with mainline car data.

Usage:
    python hotwheels_scraper.py            # incremental update (current year)
    python hotwheels_scraper.py --full     # full initial load (all years)
    python hotwheels_scraper.py --year 2023
"""
import argparse
import logging
import os
import sys
import time
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FANDOM_BASE = "https://hotwheels.fandom.com"
MAINLINE_INDEX = "/wiki/List_of_Hot_Wheels_vehicles"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; hw-cotacao-scraper/1.0; "
        "+https://github.com/fabson-barbosa/hw_site)"
    )
}
REQUEST_DELAY = 1.5  # seconds between requests (be polite)

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "api", "hw_cars.db"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database (mirrors api/database.py — kept local to avoid import path issues)
# ---------------------------------------------------------------------------

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
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def fetch(url: str) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# Scraping helpers
# ---------------------------------------------------------------------------


def get_year_urls() -> list[tuple[int, str]]:
    """Return a list of (year, url) pairs for mainline year pages."""
    soup = fetch(urljoin(FANDOM_BASE, MAINLINE_INDEX))
    if soup is None:
        return []

    year_urls: list[tuple[int, str]] = []
    current_year = datetime.utcnow().year

    # The index page lists year links in a table or navigation section
    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = link.get_text(strip=True)
        # Year links look like /wiki/Hot_Wheels_YYYY or similar
        if "/wiki/Hot_Wheels_" in href and text.isdigit():
            year = int(text)
            if 1968 <= year <= current_year + 1:
                full_url = urljoin(FANDOM_BASE, href)
                if (year, full_url) not in year_urls:
                    year_urls.append((year, full_url))

    year_urls.sort(key=lambda x: x[0], reverse=True)
    return year_urls


def parse_car_table(soup: BeautifulSoup, year: int) -> list[dict]:
    """Parse mainline car table rows from a year page."""
    cars: list[dict] = []
    tables = soup.find_all("table", class_="wikitable")

    for table in tables:
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if not any(h in ("name", "col.", "color", "toy#") for h in headers):
            continue

        col_map = {h: i for i, h in enumerate(headers)}

        def cell(row, key: str, fallback: str = "") -> str:
            idx = col_map.get(key)
            if idx is None:
                return fallback
            cells = row.find_all(["td", "th"])
            if idx >= len(cells):
                return fallback
            return cells[idx].get_text(strip=True)

        for row in table.find_all("tr")[1:]:
            cols = row.find_all(["td", "th"])
            if len(cols) < 2:
                continue

            # Try to extract image URL from the first image tag in the row
            img_tag = row.find("img")
            image_url: Optional[str] = None
            if img_tag:
                image_url = img_tag.get("src") or img_tag.get("data-src")
                if image_url and "data:image" in image_url:
                    image_url = img_tag.get("data-src")

            # Try to get the car detail page URL
            name_link = None
            for td in cols:
                a = td.find("a", href=True)
                if a and "/wiki/" in a["href"] and not a["href"].startswith("#"):
                    name_link = a
                    break

            name = cell(row, "name") or (name_link.get_text(strip=True) if name_link else "")
            fandom_url: Optional[str] = None
            if name_link:
                fandom_url = urljoin(FANDOM_BASE, name_link["href"])

            if not name:
                continue

            cars.append(
                {
                    "name": name,
                    "year": year,
                    "series": cell(row, "series") or "Mainline",
                    "series_number": cell(row, "#") or cell(row, "no."),
                    "color": cell(row, "col.") or cell(row, "color"),
                    "tampo": cell(row, "tampo"),
                    "base_color": cell(row, "base"),
                    "window_color": cell(row, "win.") or cell(row, "window"),
                    "interior_color": cell(row, "int.") or cell(row, "interior"),
                    "wheel_type": cell(row, "ww") or cell(row, "wheel"),
                    "toy_number": cell(row, "toy#") or cell(row, "toy #"),
                    "country": cell(row, "ctry.") or cell(row, "country"),
                    "image_url": image_url,
                    "fandom_url": fandom_url,
                }
            )

    return cars


# ---------------------------------------------------------------------------
# Upsert helper
# ---------------------------------------------------------------------------


def upsert_car(db: Session, data: dict) -> None:
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


# ---------------------------------------------------------------------------
# Main entry points
# ---------------------------------------------------------------------------


def scrape_year(year: int, url: str, db: Session) -> int:
    """Scrape a single year page and return the number of cars upserted."""
    logger.info("Scraping year %d from %s", year, url)
    soup = fetch(url)
    if soup is None:
        return 0

    cars = parse_car_table(soup, year)
    logger.info("  Found %d cars for year %d", len(cars), year)

    for car_data in cars:
        upsert_car(db, car_data)

    time.sleep(REQUEST_DELAY)
    return len(cars)


def initial_load(years: Optional[list[int]] = None) -> None:
    """Populate the database with mainline cars.

    Args:
        years: specific years to load; if None, loads all available years.
    """
    create_tables()
    db = SessionLocal()
    try:
        year_urls = get_year_urls()
        if not year_urls:
            logger.warning("No year URLs found. The Fandom page structure may have changed.")
            return

        if years:
            year_urls = [(y, u) for y, u in year_urls if y in years]

        total = 0
        for year, url in year_urls:
            total += scrape_year(year, url, db)

        logger.info("Initial load complete. Total cars upserted: %d", total)
    finally:
        db.close()


def incremental_update() -> None:
    """Update data for the current year only (used by weekly cron)."""
    current_year = datetime.utcnow().year
    initial_load(years=[current_year, current_year - 1])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hot Wheels Fandom Scraper")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full initial load — scrape all years",
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Scrape a specific year only",
    )
    args = parser.parse_args()

    if args.year:
        initial_load(years=[args.year])
    elif args.full:
        initial_load()
    else:
        incremental_update()
