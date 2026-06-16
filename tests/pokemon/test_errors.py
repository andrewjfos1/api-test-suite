"""PokeAPI — error handling.

The core of the Pokemon half. Each test asserts the ACTUAL observed behavior.

KNOWN CONTRAST worth highlighting in the README: PokeAPI returns a plain-text
"Not Found" body on a 404 (not a JSON error object), whereas Open-Meteo returns
structured JSON on a 400. A client that blindly calls .json() on every response
will crash on PokeAPI's 404s. That difference is exactly the kind of thing that
causes real integration bugs.

NOTE TO SELF before publishing: run these and confirm each asserted status code
and body type matches what the live API actually returns. Record any surprises
in the README findings.
"""

import pytest


@pytest.mark.error_handling
def test_nonexistent_pokemon_returns_404(pokemon_client):
    resp = pokemon_client.get("/pokemon/notarealpokemon")
    assert resp.status_code == 404


@pytest.mark.error_handling
def test_404_body_is_not_json(pokemon_client):
    # PokeAPI's 404 body is plain text, so .json() should fail. This documents
    # that the client can't assume JSON on every response. If the live API
    # actually returns JSON here, flip this test and note it as a finding.
    resp = pokemon_client.get("/pokemon/notarealpokemon")
    assert resp.status_code == 404
    with pytest.raises(Exception):
        resp.json()


@pytest.mark.error_handling
def test_id_zero_returns_404(pokemon_client):
    # There is no Pokemon with id 0. Confirm it 404s rather than returning
    # something misleading.
    resp = pokemon_client.get("/pokemon/0")
    assert resp.status_code == 404


@pytest.mark.error_handling
def test_absurdly_high_id_returns_404(pokemon_client):
    resp = pokemon_client.get("/pokemon/9999999")
    assert resp.status_code == 404


@pytest.mark.error_handling
def test_garbage_endpoint_does_not_return_200(pokemon_client):
    resp = pokemon_client.get("/this-endpoint-does-not-exist")
    assert resp.status_code != 200


@pytest.mark.error_handling
def test_trailing_segment_on_valid_pokemon(pokemon_client):
    # A valid name with an extra garbage path segment. Confirm it doesn't
    # silently succeed.
    resp = pokemon_client.get("/pokemon/ditto/notreal")
    assert resp.status_code != 200
