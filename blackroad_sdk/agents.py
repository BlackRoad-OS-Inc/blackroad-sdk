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
        self._registry = {a.id: a for a in BUILTIN_AGENTS}
    
    def list(self, type: Optional[str] = None, status: Optional[str] = None) -> list[Agent]:
        agents = list(self._registry.values())
        if type: agents = [a for a in agents if a.type == type]
        if status: agents = [a for a in agents if a.status == status]
        return agents
    
    def get(self, agent_id: str) -> Optional[Agent]:
        return self._registry.get(agent_id)
    
    def find_by_capability(self, capability: str) -> list[Agent]:
        return [a for a in self._registry.values() if capability in a.capabilities]
    
    def register(self, agent: Agent):
        self._registry[agent.id] = agent
