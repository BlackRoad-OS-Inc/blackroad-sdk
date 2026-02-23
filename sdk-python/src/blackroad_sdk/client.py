"""
BlackRoad SDK — Unified Python Client
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import AsyncIterator
import httpx

GATEWAY_URL = os.getenv("BLACKROAD_GATEWAY_URL", "http://127.0.0.1:8787")


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class BlackRoadClient:
    """
    Unified client for the BlackRoad Gateway.

    Usage:
        client = BlackRoadClient()

        # Chat
        reply = await client.chat("What is consciousness?", agent="LUCIDIA")

        # Memory
        await client.memory_write("user.prefs", {"theme": "dark"})
        data = await client.memory_read("user.prefs")

        # Agents
        agents = await client.list_agents()
        await client.route_task("ALICE", "Deploy to Railway")
    """
    gateway_url: str = field(default_factory=lambda: GATEWAY_URL)
    timeout: float = 60.0

    def __post_init__(self):
        self._client = httpx.AsyncClient(
            base_url=self.gateway_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
        )

    # ── Chat ──────────────────────────────────────────────────────────

    async def chat(self, message: str, agent: str = "LUCIDIA",
                   model: str = "llama3.2", system: str | None = None,
                   history: list[ChatMessage] | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        for h in (history or []):
            messages.append({"role": h.role, "content": h.content})
        messages.append({"role": "user", "content": message})
        r = await self._client.post("/v1/chat/completions", json={
            "model": model, "messages": messages,
            "metadata": {"agent": agent}, "stream": False
        })
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    async def stream_chat(self, message: str, agent: str = "LUCIDIA",
                          model: str = "llama3.2") -> AsyncIterator[str]:
        """Yield content tokens as they arrive (SSE stream)."""
        async with self._client.stream("POST", "/v1/chat/completions", json={
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "metadata": {"agent": agent}, "stream": True
        }) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    import json
                    data = json.loads(line[6:])
                    delta = data["choices"][0].get("delta", {}).get("content", "")
                    if delta:
                        yield delta

    # ── Memory ────────────────────────────────────────────────────────

    async def memory_write(self, key: str, value: object) -> dict:
        r = await self._client.post("/memory", json={"key": key, "value": value})
        r.raise_for_status()
        return r.json()

    async def memory_read(self, key: str) -> object:
        r = await self._client.get(f"/memory/{key}")
        r.raise_for_status()
        return r.json().get("value")

    async def memory_list(self) -> list[dict]:
        r = await self._client.get("/memory")
        r.raise_for_status()
        return r.json().get("entries", [])

    # ── Agents ────────────────────────────────────────────────────────

    async def list_agents(self) -> list[dict]:
        r = await self._client.get("/agents")
        r.raise_for_status()
        return r.json().get("agents", [])

    async def route_task(self, agent: str, task: str) -> dict:
        r = await self._client.post("/tasks", json={"agent": agent, "task": task, "priority": 5})
        r.raise_for_status()
        return r.json()

    # ── Health ────────────────────────────────────────────────────────

    async def health(self) -> dict:
        r = await self._client.get("/health")
        r.raise_for_status()
        return r.json()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self._client.aclose()
