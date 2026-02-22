"""
BlackRoad Memory API
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class MemoryAPI:
    """
    Memory system API for persistent state and coordination.

    Usage:
        # Query memory entries
        entries = client.memory.query("deployment")

        # Log an entry
        client.memory.log(
            action="deployed",
            entity="auth-service",
            details="Deployed to Security division",
            tags=["security", "keycloak"]
        )

        # Get recent entries
        recent = client.memory.recent(limit=50)

        # Get agent state
        state = client.memory.agent_state("agent-id")
    """

    def __init__(self, client):
        self._client = client

    def log(
        self,
        action: str,
        entity: str,
        details: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Log an entry to the memory system.

        Args:
            action: Action type (announce, progress, deployed, created, etc.)
            entity: Entity being acted upon
            details: Additional details
            tags: List of tags for categorization
            metadata: Additional metadata

        Returns:
            Created memory entry with hash
        """
        data = {
            "action": action,
            "entity": entity
        }
        if details:
            data["details"] = details
        if tags:
            data["tags"] = tags
        if metadata:
            data["metadata"] = metadata

        return self._client.post("/memory", data=data)

    def query(
        self,
        search: Optional[str] = None,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        tags: Optional[List[str]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query memory entries.

        Args:
            search: Full-text search query
            action: Filter by action type
            entity: Filter by entity
            tags: Filter by tags (any match)
            since: Start datetime
            until: End datetime
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of memory entries
        """
        params = {"limit": limit, "offset": offset}
        if search:
            params["q"] = search
        if action:
            params["action"] = action
        if entity:
            params["entity"] = entity
        if tags:
            params["tags"] = ",".join(tags)
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()

        return self._client.get("/memory", params=params).get("entries", [])

    def get(self, entry_hash: str) -> Dict[str, Any]:
        """Get a specific memory entry by hash."""
        return self._client.get(f"/memory/{entry_hash}")

    def recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get most recent memory entries."""
        return self.query(limit=limit)

    def agent_state(self, agent_id: str) -> Dict[str, Any]:
        """Get current state for an agent."""
        return self._client.get(f"/memory/agents/{agent_id}/state")

    def sync_state(self, agent_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync agent state to memory.

        Args:
            agent_id: Agent ID
            state: State dictionary to sync

        Returns:
            Sync confirmation
        """
        return self._client.post(f"/memory/agents/{agent_id}/state", data=state)

    def broadcast(self, message_type: str, payload: str) -> Dict[str, Any]:
        """
        Broadcast a message to all agents via memory.

        Args:
            message_type: Type of message (alert, info, command)
            payload: Message content

        Returns:
            Broadcast confirmation
        """
        return self._client.post("/memory/broadcast", data={
            "type": message_type,
            "payload": payload
        })

    def til(self, category: str, learning: str) -> Dict[str, Any]:
        """
        Share a "Today I Learned" entry.

        Args:
            category: Category (discovery, pattern, gotcha, tip, tool)
            learning: What was learned

        Returns:
            Created TIL entry
        """
        return self.log(
            action="til",
            entity=category,
            details=learning,
            tags=["til", category]
        )

    def stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return self._client.get("/memory/stats")

    def verify_chain(self, start_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify the PS-SHA-infinity hash chain integrity.

        Args:
            start_hash: Optional starting hash for verification

        Returns:
            Verification result
        """
        params = {}
        if start_hash:
            params["start"] = start_hash

        return self._client.get("/memory/verify", params=params)
