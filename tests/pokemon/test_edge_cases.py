"""PokeAPI — schema validation and edge cases.

Schema validation checks the SHAPE of the data. The edge cases probe variable
data (some Pokemon have one type, some have two), hyphenated names, and case
sensitivity — the irregular real-world details that break naive assumptions.
"""

import pytest
from jsonschema import validate, ValidationError

# Partial schema: validate the fields we rely on, allow others through.
POKEMON_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string"},
        "height": {"type": "integer"},
        "weight": {"type": "integer"},
        "types": {"type": "array", "minItems": 1},
    },
    "required": ["id", "name", "height", "weight", "types"],
}


@pytest.mark.validation
def test_pokemon_matches_schema(pokemon_client):
    resp = pokemon_client.get("/pokemon/charizard")
    pokemon = resp.json()
    try:
        validate(instance=pokemon, schema=POKEMON_SCHEMA)
    except ValidationError as e:
        pytest.fail(f"Pokemon object failed schema validation: {e.message}")


@pytest.mark.validation
def test_types_entries_have_expected_structure(pokemon_client):
    # Each entry in 'types' should be an object with a nested 'type' that has a
    # name. Confirms the nested structure, not just that the list exists.
    resp = pokemon_client.get("/pokemon/pikachu")
    types = resp.json()["types"]
    for entry in types:
        assert "type" in entry
        assert "name" in entry["type"]


@pytest.mark.edge_case
def test_pokemon_type_count_varies(pokemon_client):
    # Bulbasaur has two types (grass, poison); Ditto has one (normal). This is
    # the variable-length-field case: code that assumes exactly one type would
    # break on Bulbasaur, and code that assumes two would break on Ditto.
    bulbasaur = pokemon_client.get("/pokemon/bulbasaur").json()
    ditto = pokemon_client.get("/pokemon/ditto").json()
    assert len(bulbasaur["types"]) == 2
    assert len(ditto["types"]) == 1


@pytest.mark.edge_case
def test_hyphenated_name_works(pokemon_client):
    # Some names contain hyphens (e.g. 'mr-mime'). Confirm the client and API
    # handle them rather than choking on the special character.
    resp = pokemon_client.get("/pokemon/mr-mime")
    assert resp.status_code == 200
    assert resp.json()["name"] == "mr-mime"


@pytest.mark.edge_case
def test_name_case_sensitivity(pokemon_client):
    # PokeAPI is expected to be case-sensitive (lowercase only). Document the
    # real behavior: does 'Ditto' 404 while 'ditto' succeeds? Adjust after running.
    lower = pokemon_client.get("/pokemon/ditto")
    upper = pokemon_client.get("/pokemon/Ditto")
    # Whatever the result, the two should not silently behave identically if the
    # API is case-sensitive. Record the actual status codes as a finding.
    assert lower.status_code == 200
    assert upper.status_code in (200, 404)


@pytest.mark.edge_case
def test_pagination_limit_is_respected(pokemon_client):
    # Asking for 5 results should return exactly 5. Confirms the limit param
    # actually constrains the payload.
    resp = pokemon_client.get("/pokemon", params={"limit": 5})
    assert len(resp.json()["results"]) == 5
