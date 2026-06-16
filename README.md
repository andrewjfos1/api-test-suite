# API Test Suite

An automated test suite that probes the behavior and error handling of two public REST APIs — the [PokeAPI](https://pokeapi.co) and the [Open-Meteo weather API](https://open-meteo.com). Written in Python with pytest.

## Why this exists

Most of the value in supporting an API integration comes from understanding how it behaves with *bad* input — invalid IDs, out-of-range parameters, missing fields — not just the happy path. This suite is built around that idea: many of the tests deliberately misuse the APIs to document how they fail, and the two APIs were chosen because they break in different ways.

- **PokeAPI** has variable, nested data (a Pokemon may have one type or two; names can contain hyphens) and returns plain-text errors, so its tests focus on data shape, optional fields, and error-body handling.
- **Open-Meteo** is driven by query parameters with defined valid ranges (latitude, longitude), so its tests focus on input validation and boundary conditions.

A single shared client serves both APIs, configured by base URL.

> **Note on the original target.** This suite was first written against the REST Countries API (v3.1). On the first full run, every countries test failed — the API had been deprecated and was returning a migration notice instead of data. Rather than chase an unverified new version, I migrated the suite to PokeAPI, a stable keyless API. See *Findings* below; catching that deprecation through a failing test run is exactly the kind of break a support engineer untangles in production.

## How to run it

```bash
git clone <your-repo-url>
cd api-test-suite
pip install -r requirements.txt
pytest
```

On Windows, if the `pytest` command isn't found, use `py -m pytest`.

Run a subset by marker:

```bash
pytest -m error_handling     # only the error-handling tests
pytest -m smoke              # quick reachability checks
pytest tests/weather         # only the Open-Meteo tests
```

These tests hit the live APIs, so an internet connection is required.

## How the suite is organized

```
src/client.py              Shared HTTP client (one place for all request logic)
conftest.py                pytest fixtures that hand each test a configured client
tests/pokemon/             PokeAPI tests
    test_happy_path.py     baseline: correct usage works as documented
    test_errors.py         invalid names/ids, plain-text 404 bodies
    test_edge_cases.py     schema validation, variable type counts, case sensitivity
tests/weather/             Open-Meteo tests
    test_happy_path.py     baseline: valid coordinates return a forecast
    test_errors.py         out-of-range and malformed parameters
    test_edge_cases.py     boundary coordinates (poles, date line, 0,0)
```

## Findings

Notable observations from building and running this suite:

- **REST Countries v3.1 was deprecated mid-project.** The original suite targeted it; a full test run surfaced that every call now returns a deprecation/migration notice instead of country data. The failing tests caught this immediately, which is the point of having them. I migrated to PokeAPI.

- **The two APIs report errors in completely different formats.** PokeAPI returns a plain-text "Not Found" body on a 404 — calling `.json()` on it raises an error, so a client that assumes every response is JSON would crash. Open-Meteo, by contrast, returns a structured JSON object on a 400 with a `reason` field explaining the problem. Code written to parse one API's errors would break on the other's. This is the kind of mismatch that causes real integration bugs.

- **A single PokeAPI lookup and a list query return different shapes.** Fetching one Pokemon (`/pokemon/ditto`) returns a single object, while the list endpoint (`/pokemon`) returns a paginated wrapper with `count` and `results` fields. A client has to expect a different shape depending on which endpoint it calls.

- **Tests passed locally but timed out in CI against Open-Meteo.** On the first CI run, the five Open-Meteo tests that wait for a real forecast failed with read timeouts, while the same tests passed reliably from a home connection. Public APIs can respond more slowly to CI runners (data-center IPs) than to a normal client. The fix was to make the shared client resilient: a longer timeout plus automatic retries on transient network errors (timeouts and connection failures), while still NOT retrying real HTTP error responses, since those are answers the tests need to see. This is the difference between "the API is slow right now" and "the API is broken."

- **The `types` field is variable-length.** Bulbasaur has two types; Ditto has one. Code that assumed a fixed number of types would break on one or the other — a small but concrete reason to test against real, irregular records instead of a single "typical" example.

## What I'd add next

- A GitHub Actions workflow runs the suite on every push (see `.github/workflows/tests.yml`).
- Possible extensions: response-time assertions, retry handling for transient failures, and parametrizing the happy-path tests across many Pokemon rather than a few.
