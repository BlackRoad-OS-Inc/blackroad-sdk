"""Tests for BlackRoad Python SDK."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from blackroad_sdk.client import BlackRoadClient


@pytest.fixture
def client():
    return BlackRoadClient(
        gateway_url="http://localhost:8787",
        api_url="http://localhost:8000",
    )


@pytest.mark.asyncio
async def test_health(client, respx_mock):
    respx_mock.get("http://localhost:8787/health").mock(
        return_value=MagicMock(status_code=200, json=lambda: {"status": "ok"})
    )
    result = await client.health()
    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_chat(client, respx_mock):
    respx_mock.post("http://localhost:8787/chat").mock(
        return_value=MagicMock(
            status_code=200,
            json=lambda: {"response": "Hello from Lucidia!"},
            raise_for_status=lambda: None,
        )
    )
    response = await client.chat("Hello!", agent="lucidia")
    assert response == "Hello from Lucidia!"


@pytest.mark.asyncio
async def test_list_agents(client, respx_mock):
    respx_mock.get("http://localhost:8787/agents").mock(
        return_value=MagicMock(
            status_code=200,
            json=lambda: [{"name": "lucidia", "status": "active"}],
            raise_for_status=lambda: None,
        )
    )
    agents = await client.list_agents()
    assert len(agents) == 1
    assert agents[0]["name"] == "lucidia"


@pytest.mark.asyncio
async def test_remember_and_recall(client, respx_mock):
    respx_mock.post("http://localhost:8787/memory").mock(
        return_value=MagicMock(
            status_code=200,
            json=lambda: {"key": "test-key", "ps_sha": "abc123"},
            raise_for_status=lambda: None,
        )
    )
    result = await client.remember("test-key", {"value": 42})
    assert result["key"] == "test-key"
