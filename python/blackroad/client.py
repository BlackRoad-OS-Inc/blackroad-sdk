"""
BlackRoad Python SDK
Async client for the BlackRoad Gateway + API.
"""
from __future__ import annotations
import os, json, asyncio
from typing import Any, AsyncIterator, Optional
import httpx

GATEWAY_URL = os.getenv("BLACKROAD_GATEWAY_URL", "http://127.0.0.1:8787")
API_URL = os.getenv("BLACKROAD_API_URL", "https://api.blackroad.systems")
API_KEY = os.getenv("BLACKROAD_API_KEY", "")


class BlackRoadClient:
    """Async Python client for BlackRoad OS."""

    def __init__(
        self,
        gateway_url: str = GATEWAY_URL,
        api_url: str = API_URL,
        api_key: str = API_KEY,
        timeout: float = 30.0,
    ):
        self.gateway_url = gateway_url.rstrip("/")
        self.api_url = api_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._timeout = timeout

    # ──────────────────────────────────────────────
    # Chat / Completions
    # ──────────────────────────────────────────────

    async def chat(
        self,
        message: str,
        agent: str = "lucidia",
        session_id: Optional[str] = None,
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        """Send a chat message to an agent."""
        payload = {
            "message": message,
            "agent": agent,
            "session_id": session_id,
            "stream": stream,
        }
        if stream:
            return self._stream_chat(payload)
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(
                f"{self.gateway_url}/chat",
                json=payload,
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json().get("response", "")

    async def _stream_chat(self, payload: dict) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                f"{self.gateway_url}/chat",
                json=payload,
                headers=self._headers,
            ) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            yield json.loads(data).get("token", "")
                        except json.JSONDecodeError:
                            yield data

    # ──────────────────────────────────────────────
    # Agents
    # ──────────────────────────────────────────────

    async def list_agents(self) -> list[dict]:
        """List all agents."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(f"{self.gateway_url}/agents", headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def wake_agent(self, name: str) -> dict:
        """Wake up an agent."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(
                f"{self.gateway_url}/agents/{name}/wake",
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()

    async def sleep_agent(self, name: str) -> dict:
        """Put an agent to sleep."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(
                f"{self.gateway_url}/agents/{name}/sleep",
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()

    async def assign_task(self, agent: str, task: str, priority: str = "normal") -> dict:
        """Assign a task to an agent."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(
                f"{self.api_url}/tasks/",
                json={"title": task[:100], "description": task, "priority": priority, "agent_hint": agent},
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()

    # ──────────────────────────────────────────────
    # Memory (PS-SHA∞)
    # ──────────────────────────────────────────────

    async def remember(self, key: str, value: Any, session_id: Optional[str] = None) -> dict:
        """Store a value in persistent memory."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(
                f"{self.gateway_url}/memory",
                json={"key": key, "value": value, "session_id": session_id},
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()

    async def recall(self, key: str) -> Any:
        """Retrieve a value from memory."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(
                f"{self.gateway_url}/memory/{key}",
                headers=self._headers,
            )
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json().get("value")

    async def search_memory(self, query: str, limit: int = 10) -> list[dict]:
        """Search memory by key prefix or content."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(
                f"{self.gateway_url}/memory",
                params={"q": query, "limit": limit},
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()

    # ──────────────────────────────────────────────
    # Health
    # ──────────────────────────────────────────────

    async def health(self) -> dict:
        """Check gateway health."""
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{self.gateway_url}/health")
            r.raise_for_status()
            return r.json()

    # ──────────────────────────────────────────────
    # Sync convenience wrappers
    # ──────────────────────────────────────────────

    def chat_sync(self, message: str, agent: str = "lucidia") -> str:
        return asyncio.run(self.chat(message, agent))

    def remember_sync(self, key: str, value: Any) -> dict:
        return asyncio.run(self.remember(key, value))

    def recall_sync(self, key: str) -> Any:
        return asyncio.run(self.recall(key))


# Convenience singleton
_default_client: Optional[BlackRoadClient] = None


def get_client() -> BlackRoadClient:
    global _default_client
    if _default_client is None:
        _default_client = BlackRoadClient()
    return _default_client


# Quick usage
async def quick_chat(message: str, agent: str = "lucidia") -> str:
    return await get_client().chat(message, agent)
