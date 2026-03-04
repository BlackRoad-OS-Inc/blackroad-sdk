"""
BlackRoad SDK — Multi-Agent Coordination
Task delegation, broadcasts, and agent registry queries
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from .client import BlackRoadClient


class CoordinationClient:
    """Coordinate tasks across the agent mesh."""
    
    def __init__(self, client: BlackRoadClient):
        self._client = client
    
    async def publish(self, topic: str, event_type: str, payload: dict) -> dict:
        """Publish an event to the coordination bus."""
        event = {
            "id": f"evt_{uuid.uuid4().hex[:12]}",
            "topic": topic,
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        response = await self._client._post("/coordination/publish", event)
        return response
    
    async def delegate(self, task_type: str, description: str, 
                       required_skills: list[str] = None,
                       priority: int = 5) -> dict:
        """Delegate a task to the best available agent."""
        return await self._client._post("/coordination/delegate", {
            "task_type": task_type,
            "description": description, 
            "required_skills": required_skills or [],
            "priority": priority,
            "submitted_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        })
    
    async def broadcast(self, message: str, channel: str = "all") -> dict:
        """Broadcast a message to all agents or a specific channel."""
        return await self._client._post("/coordination/broadcast", {
            "message": message,
            "channel": channel,
            "from": self._client.agent_id or "sdk-client",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        })
    
    async def list_agents(self, agent_type: str = None, 
                          status: str = "active") -> list[dict]:
        """List agents in the registry."""
        params = {"status": status}
        if agent_type:
            params["type"] = agent_type
        return await self._client._get("/agents", params=params)
    
    async def find_by_skills(self, skills: list[str]) -> list[dict]:
        """Find agents with specific capabilities."""
        return await self._client._get("/agents/find", {"skills": ",".join(skills)})
    
    async def send_dm(self, agent_id: str, message: str, 
                      requires_response: bool = True) -> dict:
        """Send a direct message to a specific agent."""
        return await self._client._post(f"/agents/{agent_id}/message", {
            "content": message,
            "requires_response": requires_response,
            "from": self._client.agent_id or "sdk-client",
            "id": f"msg_{uuid.uuid4().hex[:12]}"
        })


# Integration point: add to BlackRoadClient
def _attach_coordination(client: BlackRoadClient) -> CoordinationClient:
    """Attach coordination capabilities to a BlackRoadClient instance."""
    coord = CoordinationClient(client)
    client.coordination = coord
    return coord
