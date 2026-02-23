"""BlackRoad OS — Main SDK client"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Optional

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from .memory import MemoryClient
from .agents import AgentClient

GATEWAY_DEFAULT = "http://127.0.0.1:8787"
API_DEFAULT = "http://127.0.0.1:8000"


@dataclass
class BlackRoadClient:
    """Main client for interacting with BlackRoad OS gateway."""
    gateway_url: str = GATEWAY_DEFAULT
    api_url: str = API_DEFAULT
    agent_id: str = "sdk-client"
    timeout: float = 30.0

    def __post_init__(self):
        self.gateway_url = self.gateway_url or os.environ.get("BLACKROAD_GATEWAY_URL", GATEWAY_DEFAULT)
        self.api_url = self.api_url or os.environ.get("BLACKROAD_API_URL", API_DEFAULT)
        self.memory = MemoryClient(self)
        self.agents = AgentClient(self)

    def _headers(self) -> dict:
        return {"X-Agent-Id": self.agent_id, "Content-Type": "application/json"}

    async def health(self) -> dict:
        """Check gateway health."""
        if not HAS_HTTPX:
            raise ImportError("httpx required: pip install httpx")
        async with httpx.AsyncClient(timeout=self.timeout) as http:
            resp = await http.get(f"{self.gateway_url}/health", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def chat(self, message: str, agent: Optional[str] = None, **kwargs) -> str:
        """Send a chat message through the gateway. Returns response string."""
        if not HAS_HTTPX:
            raise ImportError("httpx required: pip install httpx")
        payload = {"message": message}
        if agent:
            payload["agent"] = agent
        payload.update(kwargs)
        async with httpx.AsyncClient(timeout=self.timeout) as http:
            resp = await http.post(
                f"{self.gateway_url}/chat",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", data.get("content", ""))

    async def completions(self, model: str, messages: list, temperature: float = 0.7) -> dict:
        """OpenAI-compatible chat completions endpoint."""
        if not HAS_HTTPX:
            raise ImportError("httpx required: pip install httpx")
        async with httpx.AsyncClient(timeout=self.timeout) as http:
            resp = await http.post(
                f"{self.gateway_url}/v1/chat/completions",
                json={"model": model, "messages": messages, "temperature": temperature},
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def generate(self, model: str, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        result = await self.completions(model, [{"role": "user", "content": prompt}], **kwargs)
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def list_agents(self) -> list:
        """List all registered agents from the gateway."""
        if not HAS_HTTPX:
            raise ImportError("httpx required: pip install httpx")
        async with httpx.AsyncClient(timeout=self.timeout) as http:
            resp = await http.get(f"{self.gateway_url}/agents", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def remember(self, key: str, value: dict) -> dict:
        """Store a memory entry via the gateway."""
        if not HAS_HTTPX:
            raise ImportError("httpx required: pip install httpx")
        async with httpx.AsyncClient(timeout=self.timeout) as http:
            resp = await http.post(
                f"{self.gateway_url}/memory",
                json={"key": key, "value": value},
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()
