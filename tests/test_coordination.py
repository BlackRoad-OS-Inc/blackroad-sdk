"""Tests for CoordinationClient (sync/offline mode)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from blackroad_sdk.coordination import CoordinationClient
from blackroad_sdk.client import BlackRoadClient


@pytest.fixture
def client():
    return BlackRoadClient(base_url="http://test.local", agent_id="test-agent-001")


@pytest.fixture
def coord(client):
    return CoordinationClient(client)


def test_coordination_init(coord):
    assert coord._client is not None


@pytest.mark.asyncio
async def test_publish_event_structure(coord):
    """publish() should build correct event structure."""
    with patch.object(coord._client, '_post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"status": "published"}
        result = await coord.publish("tasks", "created", {"title": "test task"})
        assert mock_post.called
        call_args = mock_post.call_args[0]
        assert call_args[0] == "/coordination/publish"
        payload = call_args[1]
        assert payload["topic"] == "tasks"
        assert payload["type"] == "created"
        assert "id" in payload
        assert payload["id"].startswith("evt_")


@pytest.mark.asyncio
async def test_delegate_task(coord):
    with patch.object(coord._client, '_post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"assigned_to": "agent-007", "task_id": "t_abc"}
        result = await coord.delegate(
            task_type="analysis",
            description="Analyze Pi fleet data",
            required_skills=["python", "data"],
            priority=8
        )
        call_args = mock_post.call_args[0]
        payload = call_args[1]
        assert payload["task_type"] == "analysis"
        assert payload["priority"] == 8
        assert "python" in payload["required_skills"]


@pytest.mark.asyncio
async def test_broadcast_message(coord):
    with patch.object(coord._client, '_post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"recipients": 30000}
        result = await coord.broadcast("System maintenance in 5 minutes")
        call_args = mock_post.call_args[0]
        assert call_args[0] == "/coordination/broadcast"
        assert "message" in call_args[1] or "content" in call_args[1]


@pytest.mark.asyncio
async def test_find_by_skills(coord):
    with patch.object(coord._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [{"id": "agent-1", "skills": ["python", "api"]}]
        results = await coord.find_by_skills(["python", "api"])
        assert isinstance(results, list)


@pytest.mark.asyncio
async def test_list_agents(coord):
    with patch.object(coord._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [{"id": "agent-1", "status": "active"}]
        results = await coord.list_agents()
        assert isinstance(results, list)
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["params"]["status"] == "active"


@pytest.mark.asyncio
async def test_list_agents_with_type(coord):
    with patch.object(coord._client, '_get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [{"id": "agent-1", "type": "reasoning"}]
        await coord.list_agents(agent_type="reasoning")
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["params"]["type"] == "reasoning"


@pytest.mark.asyncio
async def test_send_dm(coord):
    with patch.object(coord._client, '_post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"delivered": True, "response": "Acknowledged"}
        result = await coord.send_dm("lucidia-001", "Execute analysis task")
        assert result["delivered"] is True
        call_args = mock_post.call_args[0]
        assert call_args[0] == "/agents/lucidia-001/message"
        payload = call_args[1]
        assert payload["content"] == "Execute analysis task"
        assert payload["requires_response"] is True


def test_attach_coordination(client):
    from blackroad_sdk.coordination import _attach_coordination
    coord_instance = _attach_coordination(client)
    assert hasattr(client, "coordination")
    assert isinstance(coord_instance, CoordinationClient)
