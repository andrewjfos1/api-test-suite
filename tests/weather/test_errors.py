"""Open-Meteo API — input and parameter error handling.

Open-Meteo's strength as a test target is its query parameters: latitude,
longitude, and date ranges all have valid ranges and obvious ways to misuse
them. This file probes how the API responds to out-of-range, malformed, and
missing parameters. This is the "how does it break" core for the weather half
of the suite.

NOTE TO SELF before publishing: run these and confirm the asserted status
codes match the live API. Open-Meteo tends to return 400 with a JSON error
body containing a 'reason' field for bad input. Verify that and record it in
the README findings.
"""

import pytest

NORFOLK_LAT = 36.85
NORFOLK_LON = -76.29


@pytest.mark.error_handling
def test_missing_longitude_returns_error(weather_client):
    # latitude without longitude is an incomplete request. Expect a 400.
    resp = weather_client.get("/forecast", params={"latitude": NORFOLK_LAT})
    assert resp.status_code == 400


@pytest.mark.error_handling
def test_latitude_out_of_range_returns_error(weather_client):
    # Valid latitude is -90 to 90. 200 is out of range.
    resp = weather_client.get(
        "/forecast", params={"latitude": 200, "longitude": NORFOLK_LON}
    )
    assert resp.status_code == 400


@pytest.mark.error_handling
def test_longitude_out_of_range_returns_error(weather_client):
    # Valid longitude is -180 to 180.
    resp = weather_client.get(
        "/forecast", params={"latitude": NORFOLK_LAT, "longitude": 999}
    )
    assert resp.status_code == 400


@pytest.mark.error_handling
def test_non_numeric_latitude_returns_error(weather_client):
    resp = weather_client.get(
        "/forecast", params={"latitude": "not_a_number", "longitude": NORFOLK_LON}
    )
    assert resp.status_code == 400


@pytest.mark.error_handling
def test_error_body_explains_the_problem(weather_client):
    # A well-designed API doesn't just return 400 — it tells you WHY. Open-Meteo
    # returns a 'reason' field. Confirm the error body is actionable, not blank.
    resp = weather_client.get("/forecast", params={"latitude": 200, "longitude": 0})
    body = resp.json()
    assert "reason" in body


@pytest.mark.error_handling
def test_unknown_endpoint_returns_error(weather_client):
    resp = weather_client.get("/not-a-real-endpoint")
    assert resp.status_code != 200
