"""
BlackRoad SDK — Python Agents Module
List, get, and ping agents via the gateway.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

AgentStatus = Literal["online", "offline", "busy"]


@dataclass
class Agent:
    id: str
    type: str
    status: AgentStatus
    role: str
    capabilities: list[str] = field(default_factory=list)
    model: Optional[str] = None
    uptime: Optional[float] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Agent":
        return cls(
            id=d["id"],
            type=d.get("type", "unknown"),
            status=d.get("status", "offline"),
            role=d.get("role", ""),
            capabilities=d.get("capabilities", []),
            model=d.get("model"),
            uptime=d.get("uptime"),
        )

    def is_available(self) -> bool:
        return self.status == "online"

    def __repr__(self) -> str:
        return f"<Agent {self.id} [{self.status}] — {self.role}>"


@dataclass
class PingResult:
    agent_id: str
    reachable: bool
    latency_ms: Optional[float]
    message: str

    def __repr__(self) -> str:
        status = f"{self.latency_ms:.1f}ms" if self.reachable else "unreachable"
        return f"<PingResult {self.agent_id}: {status}>"


class AgentsMixin:
    """
    Mixin providing agent operations for AsyncBlackRoadClient.

    Usage::

        client = AsyncBlackRoadClient()
        agents = await client.agents.list()
        lucidia = await client.agents.get("LUCIDIA")
        ping = await client.agents.ping("ALICE")
    """

    async def _request(self, method: str, path: str, **kwargs) -> Any: ...

    async def list(
        self,
        *,
        status: Optional[AgentStatus] = None,
        type: Optional[str] = None,
    ) -> list[Agent]:
        """List all agents, optionally filtered by status or type."""
        params: dict[str, str] = {}
        if status: params["status"] = status
        if type: params["type"] = type

        data = await self._request("GET", "/agents", params=params)
        return [Agent.from_dict(a) for a in data.get("agents", [])]

    async def get(self, agent_id: str) -> Optional[Agent]:
        """Get a specific agent by ID. Returns None if not found."""
        agents = await self.list()
        return next((a for a in agents if a.id == agent_id), None)

    async def ping(self, agent_id: str) -> PingResult:
        """
        Ping an agent and measure latency.
        Returns PingResult with reachable=False if gateway is offline.
        """
        import time
        t0 = time.perf_counter()
        try:
            data = await self._request("POST", f"/agents/{agent_id}/ping", json={})
            latency_ms = (time.perf_counter() - t0) * 1000
            return PingResult(
                agent_id=agent_id,
                reachable=True,
                latency_ms=latency_ms,
                message=data.get("message", "pong"),
            )
        except Exception as e:
            return PingResult(
                agent_id=agent_id,
                reachable=False,
                latency_ms=None,
                message=str(e),
            )

    async def online(self) -> list[Agent]:
        """Return only online agents."""
        return [a for a in await self.list() if a.is_available()]

    async def find_by_capability(self, capability: str) -> list[Agent]:
        """Find agents that have a specific capability."""
        return [a for a in await self.list() if capability in a.capabilities]
