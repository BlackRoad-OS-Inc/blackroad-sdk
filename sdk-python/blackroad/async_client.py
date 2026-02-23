"""
BlackRoad Async Client — asyncio-native SDK for the BlackRoad OS API.

Usage:
    import asyncio
    from blackroad import AsyncBlackRoadClient

    async def main():
        async with AsyncBlackRoadClient(api_key="...") as client:
            agents = await client.agents.list()
            response = await client.chat("LUCIDIA", "Hello!")
            print(response.message)

    asyncio.run(main())
"""

import asyncio
import os
from typing import AsyncIterator, Optional, Any
import json

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from .exceptions import BlackRoadError, AuthenticationError, RateLimitError
from .types import Agent, MemoryEntry, Task, ChatResponse


class AsyncAgentsMixin:
    """Async agents operations."""
    
    async def list(self, status: str = None, type: str = None) -> list[Agent]:
        params = {}
        if status: params["status"] = status
        if type: params["type"] = type
        data = await self._client._get("/v1/agents", params=params)
        return [Agent(**a) for a in data.get("agents", [])]
    
    async def get(self, name: str) -> Agent:
        data = await self._client._get(f"/v1/agents/{name.upper()}")
        return Agent(**data)
    
    async def message(self, name: str, message: str, session_id: str = None) -> ChatResponse:
        payload = {"message": message}
        if session_id: payload["session_id"] = session_id
        data = await self._client._post(f"/v1/agents/{name.upper()}/message", payload)
        return ChatResponse(**data)
    
    def __init__(self, client):
        self._client = client


class AsyncMemoryMixin:
    """Async memory operations."""
    
    async def store(self, content: str, type: str = "fact", truth_state: int = 1) -> MemoryEntry:
        data = await self._client._post("/v1/memory/store", {
            "content": content, "type": type, "truth_state": truth_state
        })
        return MemoryEntry(**data)
    
    async def recall(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        data = await self._client._post("/v1/memory/recall", {"query": query, "limit": limit})
        return [MemoryEntry(**m) for m in data.get("memories", [])]
    
    async def verify(self) -> bool:
        data = await self._client._get("/v1/memory/verify")
        return data.get("valid", False)
    
    async def context(self, max_entries: int = 20) -> str:
        data = await self._client._get("/v1/memory/context", {"max_entries": max_entries})
        return data.get("context", "")
    
    def __init__(self, client):
        self._client = client


class AsyncTasksMixin:
    """Async task marketplace operations."""
    
    async def list(self, status: str = None, limit: int = 20) -> list[Task]:
        params = {"limit": limit}
        if status: params["status"] = status
        data = await self._client._get("/v1/tasks", params=params)
        return [Task(**t) for t in data.get("tasks", [])]
    
    async def create(self, title: str, description: str = "", priority: str = "medium",
                     tags: list = None, required_skills: list = None) -> Task:
        data = await self._client._post("/v1/tasks", {
            "title": title, "description": description, "priority": priority,
            "tags": tags or [], "required_skills": required_skills or [],
        })
        return Task(**data.get("task", data))
    
    async def claim(self, task_id: str, agent_id: str) -> dict:
        return await self._client._post(f"/v1/tasks/{task_id}/claim", {"agent_id": agent_id})
    
    async def complete(self, task_id: str, result: str = "") -> dict:
        return await self._client._post(f"/v1/tasks/{task_id}/complete", {"result": result})
    
    def __init__(self, client):
        self._client = client


class AsyncBlackRoadClient:
    """
    Async BlackRoad OS API Client.
    
    Supports:
    - Context manager (async with)
    - All agent, memory, and task operations
    - Streaming chat responses
    - Automatic retry with exponential backoff
    """
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        if not HAS_HTTPX:
            raise ImportError("httpx is required for async client: pip install httpx")
        
        self.api_key = api_key or os.getenv("BLACKROAD_API_KEY", "")
        self.base_url = (base_url or os.getenv("BLACKROAD_API_URL", "https://api.blackroad.io")).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._http: httpx.AsyncClient | None = None
        
        # Sub-clients
        self.agents = AsyncAgentsMixin(self)
        self.memory = AsyncMemoryMixin(self)
        self.tasks = AsyncTasksMixin(self)
    
    async def __aenter__(self):
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=self.timeout,
        )
        return self
    
    async def __aexit__(self, *args):
        if self._http:
            await self._http.aclose()
    
    async def _get(self, path: str, params: dict = None) -> dict:
        return await self._request("GET", path, params=params)
    
    async def _post(self, path: str, body: dict = None) -> dict:
        return await self._request("POST", path, json=body)
    
    async def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._http:
            raise RuntimeError("Use 'async with AsyncBlackRoadClient() as client:'")
        
        for attempt in range(self.max_retries):
            try:
                r = await self._http.request(method, path, **kwargs)
                
                if r.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                if r.status_code == 429:
                    retry_after = int(r.headers.get("Retry-After", 5))
                    await asyncio.sleep(retry_after)
                    continue
                
                r.raise_for_status()
                return r.json()
                
            except httpx.HTTPStatusError as e:
                if attempt == self.max_retries - 1:
                    raise BlackRoadError(str(e)) from e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def chat(self, agent: str, message: str, session_id: str = None) -> ChatResponse:
        """Shorthand for chatting with an agent."""
        payload = {"agent": agent.upper(), "message": message, "use_memory": True}
        if session_id: payload["session_id"] = session_id
        data = await self._post("/v1/chat", payload)
        return ChatResponse(**data)
    
    async def stream_chat(self, agent: str, message: str) -> AsyncIterator[str]:
        """Stream a chat response token by token."""
        if not self._http:
            raise RuntimeError("Use 'async with' context manager")
        
        async with self._http.stream(
            "POST", "/v1/chat/stream",
            json={"agent": agent.upper(), "message": message, "stream": True},
        ) as r:
            async for line in r.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break
                    yield json.loads(chunk).get("token", "")
    
    async def health(self) -> dict:
        """Check API health."""
        return await self._get("/health")
