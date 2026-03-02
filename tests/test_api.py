"""Unit tests for the FastAPI endpoints."""


# ---------------------------------------------------------------------------
# GET /api/v1/cars
# ---------------------------------------------------------------------------


def test_list_cars_empty(client):
    """Should return empty list when no cars exist."""
    response = client.get("/api/v1/cars")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["skip"] == 0
    assert data["limit"] == 20


def test_list_cars_returns_all(client, sample_cars):
    """Should return all sample cars without filters."""
    response = client.get("/api/v1/cars")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(sample_cars)
    assert len(data["items"]) == len(sample_cars)


def test_list_cars_filter_by_year(client, sample_cars):
    """Should filter cars by year."""
    response = client.get("/api/v1/cars?year=2022")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert item["year"] == 2022


def test_list_cars_filter_by_series(client, sample_cars):
    """Should filter cars by series."""
    response = client.get("/api/v1/cars?series=Fast+%26+Furious")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Ford Mustang"


def test_list_cars_search(client, sample_cars):
    """Should search cars by name (case-insensitive partial match)."""
    response = client.get("/api/v1/cars?search=camaro")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Camaro SS"


def test_list_cars_pagination_skip(client, sample_cars):
    """Should respect skip parameter."""
    response = client.get("/api/v1/cars?skip=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(sample_cars)
    assert len(data["items"]) == 1  # 3 total - 2 skipped


def test_list_cars_pagination_limit(client, sample_cars):
    """Should respect limit parameter."""
    response = client.get("/api/v1/cars?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(sample_cars)
    assert len(data["items"]) == 1


def test_list_cars_limit_capped(client, sample_cars):
    """Limit should be capped at 100."""
    response = client.get("/api/v1/cars?limit=9999")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 100


# ---------------------------------------------------------------------------
# GET /api/v1/cars/{id}
# ---------------------------------------------------------------------------


def test_get_car_found(client, sample_cars):
    """Should return car details by ID."""
    car = sample_cars[0]
    response = client.get(f"/api/v1/cars/{car.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == car.id
    assert data["name"] == car.name


def test_get_car_not_found(client):
    """Should return 404 for unknown car ID."""
    response = client.get("/api/v1/cars/99999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/cars/{id}/view
# ---------------------------------------------------------------------------


def test_record_view_increments_count(client, sample_cars):
    """Should increment view_count on each call."""
    car = sample_cars[2]  # view_count starts at 0
    initial = car.view_count

    response = client.post(f"/api/v1/cars/{car.id}/view")
    assert response.status_code == 200
    data = response.json()
    assert data["view_count"] == initial + 1

    # Call again
    response2 = client.post(f"/api/v1/cars/{car.id}/view")
    assert response2.status_code == 200
    assert response2.json()["view_count"] == initial + 2


def test_record_view_not_found(client):
    """Should return 404 for unknown car ID."""
    response = client.post("/api/v1/cars/99999/view")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/years
# ---------------------------------------------------------------------------


def test_list_years_empty(client):
    """Should return empty years list when no cars exist."""
    response = client.get("/api/v1/years")
    assert response.status_code == 200
    assert response.json() == {"years": []}


def test_list_years(client, sample_cars):
    """Should return distinct years in descending order."""
    response = client.get("/api/v1/years")
    assert response.status_code == 200
    years = response.json()["years"]
    assert set(years) == {2022, 2023}
    assert years == sorted(years, reverse=True)


# ---------------------------------------------------------------------------
# GET /api/v1/series
# ---------------------------------------------------------------------------


def test_list_series_empty(client):
    """Should return empty series list when no cars exist."""
    response = client.get("/api/v1/series")
    assert response.status_code == 200
    assert response.json() == {"series": []}


def test_list_series(client, sample_cars):
    """Should return distinct series in alphabetical order."""
    response = client.get("/api/v1/series")
    assert response.status_code == 200
    series = response.json()["series"]
    assert set(series) == {"Mainline", "Fast & Furious"}
    assert series == sorted(series)


# ---------------------------------------------------------------------------
# GET /api/v1/cars/most-viewed
# ---------------------------------------------------------------------------


def test_most_viewed(client, sample_cars):
    """Should return cars ordered by view_count descending."""
    response = client.get("/api/v1/cars/most-viewed")
    assert response.status_code == 200
    items = response.json()
    # Ford Mustang has 0 views, should not appear
    for item in items:
        assert item["view_count"] > 0
    if len(items) >= 2:
        assert items[0]["view_count"] >= items[1]["view_count"]


def test_most_viewed_limit(client, sample_cars):
    """Should respect the limit parameter."""
    response = client.get("/api/v1/cars/most-viewed?limit=1")
    assert response.status_code == 200
    assert len(response.json()) <= 1
