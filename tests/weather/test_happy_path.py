"""Open-Meteo API — happy path.

Open-Meteo is parameter-driven (latitude, longitude, requested variables), so
it's a strong surface for testing how an API handles query input. These
happy-path tests confirm correct behavior before test_errors.py probes bad input.
"""

import pytest

# Norfolk, VA coordinates — a valid, real location to use as the baseline.
NORFOLK_LAT = 36.85
NORFOLK_LON = -76.29


@pytest.mark.smoke
def test_forecast_returns_200(weather_client):
    resp = weather_client.get(
        "/forecast",
        params={"latitude": NORFOLK_LAT, "longitude": NORFOLK_LON, "current_weather": True},
    )
    assert resp.status_code == 200


@pytest.mark.smoke
def test_forecast_returns_valid_json(weather_client):
    resp = weather_client.get(
        "/forecast",
        params={"latitude": NORFOLK_LAT, "longitude": NORFOLK_LON, "current_weather": True},
    )
    assert resp.json() is not None


def test_response_echoes_requested_coordinates(weather_client):
    # A good API tells you what location it actually used. Confirm the response
    # coordinates are close to what we requested (the API snaps to a grid, so
    # they won't match exactly — assert proximity, not equality).
    resp = weather_client.get(
        "/forecast",
        params={"latitude": NORFOLK_LAT, "longitude": NORFOLK_LON, "current_weather": True},
    )
    data = resp.json()
    assert abs(data["latitude"] - NORFOLK_LAT) < 1.0
    assert abs(data["longitude"] - NORFOLK_LON) < 1.0


def test_current_weather_has_temperature(weather_client):
    resp = weather_client.get(
        "/forecast",
        params={"latitude": NORFOLK_LAT, "longitude": NORFOLK_LON, "current_weather": True},
    )
    data = resp.json()
    assert "current_weather" in data
    assert "temperature" in data["current_weather"]
    assert isinstance(data["current_weather"]["temperature"], (int, float))
