"""
BlackRoad SDK — Python Memory Mixin + PS-SHA∞ chain verifier.
Extends AsyncBlackRoadClient with memory operations.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Optional


# ── Data classes ─────────────────────────────────────────────────────────────

class MemoryEntry:
    __slots__ = ("hash", "prev_hash", "content", "type", "truth_state", "timestamp", "agent", "tags")

    def __init__(
        self,
        hash: str,
        prev_hash: str,
        content: str,
        type: str = "observation",
        truth_state: int = 0,
        timestamp: str = "",
        agent: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ):
        self.hash = hash
        self.prev_hash = prev_hash
        self.content = content
        self.type = type
        self.truth_state = truth_state
        self.timestamp = timestamp
        self.agent = agent
        self.tags = tags or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "content": self.content,
            "type": self.type,
            "truth_state": self.truth_state,
            "timestamp": self.timestamp,
            "agent": self.agent,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MemoryEntry":
        return cls(**{k: d[k] for k in cls.__slots__ if k in d})


class ChainVerification:
    def __init__(self, valid: bool, total: int, checked: int, first_invalid: Optional[str] = None):
        self.valid = valid
        self.total = total
        self.checked = checked
        self.first_invalid = first_invalid

    def __repr__(self) -> str:
        status = "✓ VALID" if self.valid else f"✗ INVALID at {self.first_invalid}"
        return f"<ChainVerification {status} ({self.checked}/{self.total})>"


# ── PS-SHA∞ helpers ──────────────────────────────────────────────────────────

def ps_sha_hash(prev_hash: str, content: str, timestamp_ns: Optional[int] = None) -> str:
    """Compute a PS-SHA∞ hash: SHA256(prev_hash:content:timestamp_ns)"""
    ts = timestamp_ns if timestamp_ns is not None else time.time_ns()
    payload = f"{prev_hash}:{content}:{ts}"
    return hashlib.sha256(payload.encode()).hexdigest()


def verify_chain(entries: list[MemoryEntry]) -> ChainVerification:
    """
    Verify local chain integrity.
    Note: does NOT recompute hash (timestamp_ns is embedded),
    instead checks that each entry's prev_hash points to predecessor's hash.
    """
    if not entries:
        return ChainVerification(valid=True, total=0, checked=0)

    for i, entry in enumerate(entries):
        if i == 0:
            if entry.prev_hash not in ("GENESIS", ""):
                return ChainVerification(valid=False, total=len(entries), checked=i, first_invalid=entry.hash)
        else:
            if entry.prev_hash != entries[i - 1].hash:
                return ChainVerification(valid=False, total=len(entries), checked=i, first_invalid=entry.hash)

    return ChainVerification(valid=True, total=len(entries), checked=len(entries))


# ── Mixin ────────────────────────────────────────────────────────────────────

class MemoryMixin:
    """
    Mixin providing memory operations for AsyncBlackRoadClient.

    Usage:
        from blackroad_sdk import AsyncBlackRoadClient
        client = AsyncBlackRoadClient()
        entries = await client.memory.list(type="fact")
        new = await client.memory.add("Sky is blue", type="fact", truth_state=1)
    """

    # _request is injected by AsyncBlackRoadClient
    async def _request(self, method: str, path: str, **kwargs) -> Any: ...

    async def list(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        type: Optional[str] = None,
        agent: Optional[str] = None,
        truth_state: Optional[int] = None,
    ) -> list[MemoryEntry]:
        """List memory entries from the chain."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if type: params["type"] = type
        if agent: params["agent"] = agent
        if truth_state is not None: params["truth_state"] = truth_state

        data = await self._request("GET", "/memory", params=params)
        return [MemoryEntry.from_dict(e) for e in data.get("entries", [])]

    async def add(
        self,
        content: str,
        *,
        type: str = "observation",
        truth_state: int = 0,
        agent: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> MemoryEntry:
        """Append a new entry to the PS-SHA∞ chain."""
        body = {
            "content": content,
            "type": type,
            "truth_state": truth_state,
            "agent": agent,
            "tags": tags or [],
        }
        data = await self._request("POST", "/memory", json=body)
        return MemoryEntry.from_dict(data)

    async def get(self, hash: str) -> MemoryEntry:
        """Get a specific memory entry by hash."""
        data = await self._request("GET", f"/memory/{hash}")
        return MemoryEntry.from_dict(data)

    async def verify_remote(self) -> ChainVerification:
        """Verify chain integrity via the gateway endpoint."""
        data = await self._request("GET", "/memory/verify")
        return ChainVerification(
            valid=data.get("valid", True),
            total=data.get("total", 0),
            checked=data.get("checked", 0),
            first_invalid=data.get("first_invalid"),
        )

    async def verify_local(self, entries: Optional[list[MemoryEntry]] = None) -> ChainVerification:
        """
        Download all entries and verify chain locally (offline-safe).
        Pass pre-fetched entries or None to fetch automatically.
        """
        if entries is None:
            entries = await self.list(limit=1000)
        return verify_chain(entries)


# ── Standalone usage example ─────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio
    import sys

    sys.path.insert(0, ".")

    # Show local verify_chain demo
    entries = [
        MemoryEntry(hash="abc", prev_hash="GENESIS", content="Sky is blue", type="fact", truth_state=1, timestamp="2026-01-01T00:00:00Z"),
        MemoryEntry(hash="def", prev_hash="abc", content="Water is wet", type="fact", truth_state=1, timestamp="2026-01-01T00:00:01Z"),
        MemoryEntry(hash="ghi", prev_hash="def", content="AI is uncertain", type="observation", truth_state=0, timestamp="2026-01-01T00:00:02Z"),
    ]

    result = verify_chain(entries)
    print(f"Chain valid: {result.valid}")
    print(f"Entries: {result.checked}/{result.total}")

    # Tamper test
    entries[1].prev_hash = "TAMPERED"
    result2 = verify_chain(entries)
    print(f"\nAfter tamper:")
    print(f"Chain valid: {result2.valid}")
    print(f"First invalid: {result2.first_invalid}")
    print(result2)
