"""Tests for BlackRoad Python SDK."""
import pytest
import httpx
from blackroad_sdk.client import BlackRoadClient
import respx


@pytest.fixture
def client():
    return BlackRoadClient(
        gateway_url="http://localhost:8787",
        api_url="http://localhost:8000",
    )


@pytest.mark.asyncio
@respx.mock
async def test_health(client):
    respx.get("http://localhost:8787/health").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    result = await client.health()
    assert result["status"] == "ok"


@pytest.mark.asyncio
@respx.mock
async def test_chat(client):
    respx.post("http://localhost:8787/chat").mock(
        return_value=httpx.Response(200, json={"response": "Hello from Lucidia!"})
    )
    response = await client.chat("Hello!", agent="lucidia")
    assert response == "Hello from Lucidia!"


@pytest.mark.asyncio
@respx.mock
async def test_list_agents(client):
    respx.get("http://localhost:8787/agents").mock(
        return_value=httpx.Response(200, json=[{"name": "lucidia", "status": "active"}])
    )
    agents = await client.list_agents()
    assert len(agents) == 1
    assert agents[0]["name"] == "lucidia"


@pytest.mark.asyncio
@respx.mock
async def test_remember_and_recall(client):
    respx.post("http://localhost:8787/memory").mock(
        return_value=httpx.Response(200, json={"key": "test-key", "ps_sha": "abc123"})
    )
    result = await client.remember("test-key", {"value": 42})
    assert result["key"] == "test-key"
