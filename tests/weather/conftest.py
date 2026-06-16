"""Fixtures specific to the Open-Meteo (weather) tests.

These tests hit a live third-party API, which can be slow or unreachable from
CI runners even when the test code is correct. Rather than fail the build on
someone else's downtime, we check reachability once per session and SKIP the
weather tests if the API can't be reached. A skip honestly reports "couldn't
verify this right now" -- it is not the same as a failure.

The PokeAPI tests are reliable from CI and are unaffected by this.
"""

import pytest
import requests

WEATHER_BASE_URL = "https://api.open-meteo.com/v1"
# A short probe: if Open-Meteo can't answer a minimal request quickly, the
# full tests almost certainly won't either, so we skip rather than wait.
PROBE_TIMEOUT = 15


@pytest.fixture(scope="session")
def open_meteo_available():
    """Return True if Open-Meteo answers a minimal request, else False.

    Session-scoped so the probe runs once per test run, not once per test.
    """
    try:
        resp = requests.get(
            f"{WEATHER_BASE_URL}/forecast",
            params={"latitude": 0, "longitude": 0, "current_weather": True},
            timeout=PROBE_TIMEOUT,
        )
        return resp.status_code == 200
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return False


@pytest.fixture(autouse=True)
def skip_if_open_meteo_down(open_meteo_available):
    """Automatically skip every weather test when the API is unreachable.

    autouse=True means this runs for every test in this folder without each
    test having to ask for it.
    """
    if not open_meteo_available:
        pytest.skip("Open-Meteo API is unreachable from this environment; skipping live weather tests.")
