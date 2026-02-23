"""
BlackRoad SDK — type definitions for all API objects.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Agent:
    name: str
    type: str
    color: str = "#ffffff"
    capabilities: list[str] = field(default_factory=list)
    status: str = "unknown"
    uptime_seconds: int = 0
    
    def __repr__(self):
        return f"Agent(name={self.name!r}, type={self.type!r}, status={self.status!r})"
    
    @property
    def is_online(self) -> bool:
        return self.status in ("active", "idle")


@dataclass
class MemoryEntry:
    hash: str
    prev: str
    content: str
    timestamp_ns: int
    truth_state: int = 1
    type: str = "fact"
    
    @property
    def is_true(self) -> bool:
        return self.truth_state == 1
    
    @property
    def is_false(self) -> bool:
        return self.truth_state == -1
    
    @property
    def is_uncertain(self) -> bool:
        return self.truth_state == 0
    
    def __repr__(self):
        return f"Memory(hash={self.hash[:8]}..., type={self.type!r})"


@dataclass
class Task:
    title: str
    task_id: str = ""
    description: str = ""
    priority: str = "medium"
    status: str = "available"
    tags: list[str] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    posted_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: str = ""
    
    @property
    def is_available(self) -> bool:
        return self.status == "available"
    
    @property
    def is_done(self) -> bool:
        return self.status == "completed"
    
    def __repr__(self):
        return f"Task(id={self.task_id!r}, title={self.title!r}, status={self.status!r})"


@dataclass
class ChatResponse:
    agent: str
    response: str
    memory_hash: str = ""
    truth_state: int = 1
    timestamp: str = ""
    session_id: Optional[str] = None
    
    def __str__(self) -> str:
        return self.response
    
    def __repr__(self):
        return f"ChatResponse(agent={self.agent!r}, len={len(self.response)})"


@dataclass
class HealthStatus:
    status: str
    version: str
    agents_online: int = 0
    gateway_url: str = ""
    timestamp: str = ""
    
    @property
    def is_healthy(self) -> bool:
        return self.status == "ok"
