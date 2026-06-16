"""Open-Meteo API — boundary and edge cases.

Boundary values are where input validation tends to be off-by-one. The poles,
the date line, and the equator/prime-meridian zero point are the natural
boundaries for geographic coordinates. Testing them shows you think about
limits, not just typical inputs.
"""

import pytest


@pytest.mark.edge_case
def test_north_pole_is_valid(weather_client):
    # Latitude 90 is the exact boundary — valid, not out of range.
    resp = weather_client.get(
        "/forecast", params={"latitude": 90, "longitude": 0, "current_weather": True}
    )
    assert resp.status_code == 200


@pytest.mark.edge_case
def test_zero_zero_coordinates_are_valid(weather_client):
    # (0, 0) is a real point in the Atlantic (Null Island). A naive validator
    # might treat 0 as "missing"; confirm the API accepts it.
    resp = weather_client.get(
        "/forecast", params={"latitude": 0, "longitude": 0, "current_weather": True}
    )
    assert resp.status_code == 200


@pytest.mark.edge_case
def test_date_line_longitude_is_valid(weather_client):
    # Longitude 180 is the boundary at the international date line.
    resp = weather_client.get(
        "/forecast", params={"latitude": 0, "longitude": 180, "current_weather": True}
    )
    assert resp.status_code == 200


@pytest.mark.edge_case
def test_high_precision_coordinates(weather_client):
    # Many decimal places of precision. Confirm the API doesn't choke on it and
    # still snaps to its internal grid.
    resp = weather_client.get(
        "/forecast",
        params={"latitude": 36.850769, "longitude": -76.285873, "current_weather": True},
    )
    assert resp.status_code == 200
