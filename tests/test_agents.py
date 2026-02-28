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


@pytest.mark.asyncio
async def test_list_agents_fallback_local(agents):
    """When gateway is unreachable, falls back to BUILTIN_AGENTS."""
    with patch.object(agents._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Connection refused")
        results = await agents.list()
        assert len(results) > 0


@pytest.mark.asyncio
async def test_list_agents_filter_by_type(agents):
    with patch.object(agents._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Connection refused")
        results = await agents.list(type="reasoning")
        assert all(a.type == "reasoning" for a in results)


@pytest.mark.asyncio
async def test_list_agents_filter_by_status(agents):
    with patch.object(agents._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Connection refused")
        results = await agents.list(status="active")
        assert all(a.status == "active" for a in results)


@pytest.mark.asyncio
async def test_get_agent_fallback_found(agents):
    """Falls back to local registry when gateway raises an exception."""
    with patch.object(agents._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Not found")
        agent = await agents.get("lucidia-001")
        assert agent is not None
        assert agent["id"] == "lucidia-001"
        assert "capabilities" in agent


@pytest.mark.asyncio
async def test_get_agent_fallback_not_found(agents):
    """Returns None when agent is not in local registry either."""
    with patch.object(agents._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Not found")
        agent = await agents.get("nonexistent-agent-xyz")
        assert agent is None


def test_find_by_capability(agents):
    from blackroad_sdk.agents import Agent
    agents.register(Agent("cap-test-001", "CAP", "test", "active", ["unique-cap-xyz"], "test-model"))
    results = agents.find_by_capability("unique-cap-xyz")
    assert len(results) == 1
    assert results[0].id == "cap-test-001"


def test_register_agent(agents):
    from blackroad_sdk.agents import Agent
    new_agent = Agent("test-agent-001", "TEST", "testing", "active", ["testing"], "test-model")
    agents.register(new_agent)
    assert "test-agent-001" in agents._local
    assert agents._local["test-agent-001"].name == "TEST"
