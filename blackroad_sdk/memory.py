"""BlackRoad OS — PS-SHA∞ Memory Client"""
from __future__ import annotations
import hashlib, time, json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .client import BlackRoadClient

TruthState = Literal[1, 0, -1]
MemoryType = Literal["fact", "observation", "inference", "commitment"]

@dataclass
class Memory:
    hash: str
    prev_hash: str
    key: str
    content: str
    type: MemoryType
    truth_state: TruthState
    created_at: str
    agent_id: str

class MemoryClient:
    """PS-SHA∞ persistent memory with hash-chain integrity."""
    
    def __init__(self, client: BlackRoadClient):
        self._client = client
        self._chain: list[Memory] = []
        self._prev_hash = "GENESIS"
        self._journal = Path.home() / ".blackroad" / "memory" / "sdk-journal.jsonl"
        self._journal.parent.mkdir(parents=True, exist_ok=True)
        self._load_journal()
    
    def _pssha(self, key: str, content: str) -> str:
        ts = str(time.time_ns())
        return hashlib.sha256(f"{self._prev_hash}:{key}:{content}:{ts}".encode()).hexdigest()
    
    def _load_journal(self):
        if self._journal.exists():
            for line in self._journal.read_text().splitlines():
                try:
                    m = Memory(**json.loads(line))
                    self._chain.append(m)
                    self._prev_hash = m.hash
                except Exception:
                    pass
    
    def _store(self, key: str, content: str, type: MemoryType, truth_state: TruthState) -> Memory:
        h = self._pssha(key, content)
        m = Memory(
            hash=h, prev_hash=self._prev_hash,
            key=key, content=content, type=type,
            truth_state=truth_state,
            created_at=datetime.utcnow().isoformat(),
            agent_id=self._client.agent_id,
        )
        self._chain.append(m)
        self._prev_hash = h
        with open(self._journal, "a") as f:
            f.write(json.dumps(asdict(m)) + "
")
        return m
    
    def remember(self, content: str, key: str = "memory") -> Memory:
        """Store a verified fact (truth_state=1)."""
        return self._store(key, content, "fact", 1)
    
    def observe(self, content: str, key: str = "observation") -> Memory:
        """Store an observation (truth_state=0, pending verification)."""
        return self._store(key, content, "observation", 0)
    
    def infer(self, content: str, key: str = "inference") -> Memory:
        """Store an inference from observations."""
        return self._store(key, content, "inference", 0)
    
    def search(self, query: str) -> list[Memory]:
        """Search memory by keyword."""
        q = query.lower()
        return [m for m in reversed(self._chain) if q in m.content.lower() or q in m.key.lower()]
    
    def recent(self, n: int = 20) -> list[Memory]:
        """Return n most recent memories."""
        return list(reversed(self._chain[-n:]))
    
    @property
    def chain_length(self) -> int:
        return len(self._chain)
    
    @property
    def head_hash(self) -> str:
        return self._prev_hash[:16]
