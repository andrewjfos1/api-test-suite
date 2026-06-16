"""A thin, reusable HTTP client for testing public REST APIs.

The same client serves two very different APIs in this suite (REST Countries
and Open-Meteo) by taking the base URL as configuration. Keeping all HTTP
logic in one place means a change to timeouts, headers, or error handling
happens once, not in every test.
"""

import requests

# A single timeout applied to every request. Hung requests are a real failure
# mode in production integrations; a test suite that never times out is hiding
# that risk rather than surfacing it.
DEFAULT_TIMEOUT = 10


class APIClient:
    """Minimal wrapper around requests for a single base URL."""

    def __init__(self, base_url, timeout=DEFAULT_TIMEOUT):
        # Strip a trailing slash so path joining is predictable.
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path="", params=None):
        """Send a GET request to base_url + path.

        Returns the raw requests.Response so tests can assert on status code,
        headers, and body independently. We deliberately do NOT raise on 4xx/5xx
        here, because testing error responses is half the point of this suite.
        """
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        return requests.get(url, params=params, timeout=self.timeout)
