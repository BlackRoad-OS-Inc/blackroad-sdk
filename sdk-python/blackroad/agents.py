"""
BlackRoad Agents API
"""

from typing import Optional, Dict, Any, List


class AgentAPI:
    """
    Agent management API.

    Usage:
        # List all agents
        agents = client.agents.list()

        # Get specific agent
        agent = client.agents.get("agent-id")

        # Register a new agent
        agent = client.agents.register(
            name="my-agent",
            type="ai",
            division="OS"
        )

        # Send heartbeat
        client.agents.heartbeat("agent-id")

        # Update agent status
        client.agents.update_status("agent-id", "active")
    """

    def __init__(self, client):
        self._client = client

    def list(
        self,
        level: Optional[int] = None,
        division: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List agents with optional filters.

        Args:
            level: Filter by hierarchy level (1-4)
            division: Filter by division name
            status: Filter by status (active, standby, dead)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of agent dictionaries
        """
        params = {"limit": limit, "offset": offset}
        if level:
            params["level"] = level
        if division:
            params["division"] = division
        if status:
            params["status"] = status

        return self._client.get("/agents", params=params).get("agents", [])

    def get(self, agent_id: str) -> Dict[str, Any]:
        """Get a specific agent by ID."""
        return self._client.get(f"/agents/{agent_id}")

    def register(
        self,
        name: str,
        agent_type: str = "ai",
        division: Optional[str] = None,
        level: int = 4,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Register a new agent.

        Args:
            name: Agent name
            agent_type: Type of agent (ai, hardware, human)
            division: Division assignment
            level: Hierarchy level (1-4)
            metadata: Additional metadata

        Returns:
            Created agent dictionary
        """
        data = {
            "name": name,
            "type": agent_type,
            "level": level
        }
        if division:
            data["division"] = division
        if metadata:
            data["metadata"] = metadata

        return self._client.post("/agents", data=data)

    def heartbeat(self, agent_id: str, load: Optional[float] = None) -> Dict[str, Any]:
        """
        Send a heartbeat for an agent.

        Args:
            agent_id: Agent ID
            load: Current load (0.0 to 1.0)

        Returns:
            Heartbeat response
        """
        data = {}
        if load is not None:
            data["load"] = load

        return self._client.post(f"/agents/{agent_id}/heartbeat", data=data)

    def update_status(self, agent_id: str, status: str) -> Dict[str, Any]:
        """
        Update agent status.

        Args:
            agent_id: Agent ID
            status: New status (active, standby, maintenance)

        Returns:
            Updated agent
        """
        return self._client.put(f"/agents/{agent_id}", data={"status": status})

    def delete(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent."""
        return self._client.delete(f"/agents/{agent_id}")

    def stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return self._client.get("/agents/stats")

    def by_division(self, division: str) -> List[Dict[str, Any]]:
        """Get all agents in a division."""
        return self.list(division=division)

    def commanders(self) -> List[Dict[str, Any]]:
        """Get all Level 2 commanders."""
        return self.list(level=2)

    def managers(self) -> List[Dict[str, Any]]:
        """Get all Level 3 managers."""
        return self.list(level=3)

    def workers(self) -> List[Dict[str, Any]]:
        """Get all Level 4 workers."""
        return self.list(level=4)
