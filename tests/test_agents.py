"""Tests for AgentClient."""
import pytest
from unittest.mock import AsyncMock, patch
from blackroad_sdk.agents import AgentClient
from blackroad_sdk.client import BlackRoadClient


@pytest.fixture
def client():
    return BlackRoadClient(base_url="http://test.local", agent_id="test-agent-001")


@pytest.fixture
def agents(client):
    return AgentClient(client)


def test_agent_client_init(agents):
    assert agents._client is not None


@pytest.mark.asyncio
async def test_list_agents(agents):
    with patch.object(agents._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [
            {"id": "octavia-001", "name": "Octavia", "type": "orchestrator", "status": "active"},
            {"id": "lucidia-001", "name": "Lucidia", "type": "reasoning", "status": "active"},
        ]
        results = await agents.list()
        assert len(results) == 2
        assert results[0]["name"] == "Octavia"


@pytest.mark.asyncio
async def test_get_agent(agents):
    with patch.object(agents._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {
            "id": "octavia-001",
            "name": "Octavia",
            "capabilities": ["deploy", "monitor", "orchestrate"]
        }
        agent = await agents.get("octavia-001")
        assert agent["capabilities"] is not None
        assert "deploy" in agent["capabilities"]


@pytest.mark.asyncio
async def test_wake_agent(agents):
    with patch.object(agents._client, '_post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"status": "active", "message": "Octavia is now ONLINE"}
        result = await agents.wake("octavia-001")
        assert result["status"] == "active"


@pytest.mark.asyncio
async def test_assign_task(agents):
    with patch.object(agents._client, '_post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"task_id": "t_001", "assigned": True}
        result = await agents.assign_task("octavia-001", "Deploy to Railway")
        assert result["assigned"] is True
