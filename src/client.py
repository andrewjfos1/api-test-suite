"""A thin, reusable HTTP client for testing public REST APIs.

The same client serves two very different APIs in this suite (PokeAPI and
Open-Meteo) by taking the base URL as configuration. Keeping all HTTP logic in
one place means a change to timeouts, retries, or error handling happens once,
not in every test.
"""

import time

import requests

# A request that hasn't responded within this many seconds is treated as a
# transient failure and retried. Set generously because public APIs can be slow
# from CI runners (data-center IPs) even when they're fast from a home connection.
DEFAULT_TIMEOUT = 30

# How many times to attempt a request before giving up. Public APIs are
# occasionally slow or briefly unavailable; one slow response shouldn't fail a
# test run. We retry on timeouts and connection errors only -- NOT on HTTP error
# status codes, because a 404 or 400 is a real answer the tests need to see.
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 2


class APIClient:
    """Minimal wrapper around requests for a single base URL, with retries."""

    def __init__(self, base_url, timeout=DEFAULT_TIMEOUT):
        # Strip a trailing slash so path joining is predictable.
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path="", params=None):
        """Send a GET request to base_url + path, retrying transient failures.

        Returns the raw requests.Response so tests can assert on status code,
        headers, and body independently. We deliberately do NOT raise on 4xx/5xx
        here, because testing error responses is half the point of this suite.

        Timeouts and connection errors are retried up to MAX_ATTEMPTS times with
        a short backoff. If every attempt fails, the last exception is raised so
        the failure is still visible rather than silently swallowed.
        """
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url

        last_error = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return requests.get(url, params=params, timeout=self.timeout)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as err:
                # Transient network problem. Wait briefly and try again, unless
                # this was the final attempt.
                last_error = err
                if attempt < MAX_ATTEMPTS:
                    time.sleep(RETRY_BACKOFF_SECONDS)

        # Every attempt failed; surface the last error so the test reports it.
        raise last_error
