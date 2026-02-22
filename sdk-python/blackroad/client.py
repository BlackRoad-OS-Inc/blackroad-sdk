"""
BlackRoad API Client
"""

import os
import json
import time
from typing import Optional, Dict, Any, List
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .exceptions import (
    BlackRoadError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError
)


class BlackRoadClient:
    """
    Official BlackRoad API Client

    Usage:
        from blackroad import BlackRoadClient

        client = BlackRoadClient(api_key="your-api-key")

        # List agents
        agents = client.agents.list()

        # Dispatch a task
        task = client.tasks.dispatch(
            title="Deploy service",
            priority="high",
            division="Security"
        )

        # Access memory
        entries = client.memory.query("deployment")
    """

    DEFAULT_BASE_URL = "https://api.blackroad.io/v1"
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3
    ):
        """
        Initialize the BlackRoad client.

        Args:
            api_key: Your BlackRoad API key. If not provided, reads from
                     BLACKROAD_API_KEY environment variable.
            base_url: API base URL. Defaults to https://api.blackroad.io/v1
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
        """
        self.api_key = api_key or os.environ.get("BLACKROAD_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key required. Set BLACKROAD_API_KEY or pass api_key parameter.")

        self.base_url = (base_url or os.environ.get("BLACKROAD_API_URL", self.DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Initialize API modules
        from .agents import AgentAPI
        from .tasks import TaskAPI
        from .memory import MemoryAPI

        self.agents = AgentAPI(self)
        self.tasks = TaskAPI(self)
        self.memory = MemoryAPI(self)

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"blackroad-python/1.0.0"
        }

        body = json.dumps(data).encode() if data else None

        for attempt in range(self.max_retries):
            try:
                request = Request(url, data=body, headers=headers, method=method)
                response = urlopen(request, timeout=self.timeout)
                return json.loads(response.read().decode())

            except HTTPError as e:
                error_body = e.read().decode() if e.fp else ""

                if e.code == 401:
                    raise AuthenticationError("Invalid API key")
                elif e.code == 404:
                    raise NotFoundError(f"Resource not found: {endpoint}")
                elif e.code == 422:
                    raise ValidationError(f"Validation error: {error_body}")
                elif e.code == 429:
                    if attempt < self.max_retries - 1:
                        retry_after = int(e.headers.get("Retry-After", 1))
                        time.sleep(retry_after)
                        continue
                    raise RateLimitError("Rate limit exceeded")
                else:
                    raise BlackRoadError(f"API error ({e.code}): {error_body}")

            except URLError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise BlackRoadError(f"Connection error: {e.reason}")

        raise BlackRoadError("Max retries exceeded")

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a POST request."""
        return self._request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a PUT request."""
        return self._request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict:
        """Make a DELETE request."""
        return self._request("DELETE", endpoint)

    def health(self) -> Dict[str, Any]:
        """Check API health status."""
        return self.get("/health")

    def version(self) -> str:
        """Get API version."""
        return self.get("/version").get("version", "unknown")
