"""PokeAPI — happy path.

Baseline tests confirming correct usage works as documented. Note one structural
contrast worth remembering for the README: unlike the old REST Countries API
(which returned a list even for a single lookup), PokeAPI returns a single
OBJECT for a single Pokemon and a paginated wrapper for list queries.
"""

import pytest


@pytest.mark.smoke
def test_get_pokemon_returns_200(pokemon_client):
    resp = pokemon_client.get("/pokemon/ditto")
    assert resp.status_code == 200


@pytest.mark.smoke
def test_response_is_valid_json(pokemon_client):
    resp = pokemon_client.get("/pokemon/ditto")
    assert resp.json() is not None


def test_known_pokemon_has_expected_name(pokemon_client):
    resp = pokemon_client.get("/pokemon/ditto")
    data = resp.json()
    # Single lookup returns an object, not a list.
    assert isinstance(data, dict)
    assert data["name"] == "ditto"


def test_pokemon_object_has_required_fields(pokemon_client):
    resp = pokemon_client.get("/pokemon/bulbasaur")
    pokemon = resp.json()
    for field in ("id", "name", "height", "weight", "types"):
        assert field in pokemon, f"expected field '{field}' missing from response"


def test_weight_is_a_positive_number(pokemon_client):
    resp = pokemon_client.get("/pokemon/pikachu")
    pokemon = resp.json()
    assert isinstance(pokemon["weight"], int)
    assert pokemon["weight"] > 0


def test_lookup_by_numeric_id_works(pokemon_client):
    # Pokemon can be fetched by name OR numeric id. Id 1 is Bulbasaur.
    resp = pokemon_client.get("/pokemon/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "bulbasaur"


def test_list_endpoint_is_paginated(pokemon_client):
    # The list endpoint returns a wrapper object with count + results, not a
    # bare list. Confirm the pagination shape.
    resp = pokemon_client.get("/pokemon", params={"limit": 20})
    data = resp.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)
    assert data["count"] > 100
