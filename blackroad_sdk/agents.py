"""BlackRoad OS — Agent Registry Client"""
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import BlackRoadClient

@dataclass
class Agent:
    id: str
    name: str
    type: str
    status: str
    capabilities: list[str]
    model: str

BUILTIN_AGENTS = [
    Agent("lucidia-001", "LUCIDIA", "reasoning", "active", ["analysis","philosophy","strategy"], "qwen2.5:3b"),
    Agent("alice-001",   "ALICE",   "worker",    "active", ["execution","automation","devops"], "qwen2.5:3b"),
    Agent("octavia-001", "OCTAVIA", "devops",    "active", ["infrastructure","deployment","monitoring"], "qwen2.5:3b"),
    Agent("prism-001",   "PRISM",   "analytics", "active", ["patterns","data","insights"], "qwen2.5:3b"),
    Agent("echo-001",    "ECHO",    "memory",    "active", ["recall","storage","synthesis"], "nomic-embed-text"),
    Agent("cipher-001",  "CIPHER",  "security",  "active", ["auth","encryption","scanning"], "qwen2.5:3b"),
]

class AgentClient:
    """Agent registry and coordination."""

    def __init__(self, client: BlackRoadClient):
        self._client = client
        self._local = {a.id: a for a in BUILTIN_AGENTS}

    async def list(self, type: Optional[str] = None, status: Optional[str] = None) -> list:
        """List agents from the gateway (falls back to local registry)."""
        try:
            result = await self._client._get("/agents")
            if isinstance(result, list):
                return result
        except Exception:
            pass
        agents = list(self._local.values())
        if type:
            agents = [a for a in agents if a.type == type]
        if status:
            agents = [a for a in agents if a.status == status]
        return agents

    async def get(self, agent_id: str) -> Optional[dict]:
        """Get an agent by ID from the gateway."""
        try:
            return await self._client._get(f"/agents/{agent_id}")
        except Exception:
            a = self._local.get(agent_id)
            return {"id": a.id, "name": a.name, "capabilities": a.capabilities} if a else None

    async def wake(self, agent_id: str) -> dict:
        """Wake up an agent."""
        return await self._client._post(f"/agents/{agent_id}/wake", {})

    async def assign_task(self, agent_id: str, description: str, **kwargs) -> dict:
        """Assign a task to an agent."""
        return await self._client._post(f"/agents/{agent_id}/task", {
            "description": description,
            **kwargs,
        })

    def find_by_capability(self, capability: str) -> list[Agent]:
        """Find agents in local registry by capability."""
        return [a for a in self._local.values() if capability in a.capabilities]

    def register(self, agent: Agent):
        """Register an agent in the local registry."""
        self._local[agent.id] = agent
