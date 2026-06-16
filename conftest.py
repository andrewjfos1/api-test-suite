"""Shared pytest fixtures available to every test in the suite.

Fixtures defined here are discovered automatically by pytest, so any test can
request a `pokemon_client` or `weather_client` simply by naming it as an
argument. This is the standard pytest pattern for shared setup.
"""

import pytest

from src.client import APIClient

POKEMON_BASE_URL = "https://pokeapi.co/api/v2"
WEATHER_BASE_URL = "https://api.open-meteo.com/v1"


@pytest.fixture(scope="session")
def pokemon_client():
    """A client pointed at the PokeAPI.

    Session-scoped: one instance is reused across all tests in a run, since the
    client holds no per-test state.
    """
    return APIClient(POKEMON_BASE_URL)


@pytest.fixture(scope="session")
def weather_client():
    """A client pointed at the Open-Meteo API."""
    return APIClient(WEATHER_BASE_URL)
