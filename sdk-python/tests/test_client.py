# Copyright 2025-2026 BlackRoad OS, Inc. All rights reserved.
"""Tests for BlackRoad Python SDK."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from blackroad import BlackRoadClient, AsyncBlackRoadClient
from blackroad.exceptions import AuthenticationError, NotFoundError, RateLimitError
from blackroad.types import Agent, MemoryEntry, Task, ChatResponse, HealthStatus


# ── Type Tests ──────────────────────────────────────────────────────

class TestTypes:
    def test_agent_creation(self):
        agent = Agent(name="LUCIDIA", type="reasoning", status="active")
        assert agent.name == "LUCIDIA"
        assert agent.is_online
        assert "LUCIDIA" in repr(agent)

    def test_agent_offline(self):
        agent = Agent(name="TEST", type="worker", status="dead")
        assert not agent.is_online

    def test_memory_entry_truth_states(self):
        true_entry = MemoryEntry(hash="abc123", prev="GENESIS", content="fact", timestamp_ns=0, truth_state=1)
        assert true_entry.is_true
        assert not true_entry.is_false
        assert not true_entry.is_uncertain

        false_entry = MemoryEntry(hash="def456", prev="abc123", content="lie", timestamp_ns=0, truth_state=-1)
        assert false_entry.is_false

        uncertain = MemoryEntry(hash="ghi789", prev="def456", content="maybe", timestamp_ns=0, truth_state=0)
        assert uncertain.is_uncertain

    def test_task_states(self):
        task = Task(title="Deploy", task_id="t1", status="available")
        assert task.is_available
        assert not task.is_done

        done = Task(title="Done", task_id="t2", status="completed")
        assert done.is_done

    def test_chat_response_str(self):
        resp = ChatResponse(agent="LUCIDIA", response="Hello!", memory_hash="abc")
        assert str(resp) == "Hello!"
        assert "LUCIDIA" in repr(resp)

    def test_health_status(self):
        h = HealthStatus(status="ok", version="1.0.0", agents_online=5)
        assert h.is_healthy
        h2 = HealthStatus(status="degraded", version="1.0.0")
        assert not h2.is_healthy


# ── Client Init Tests ───────────────────────────────────────────────

class TestClientInit:
    def test_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError):
                BlackRoadClient()

    def test_accepts_api_key_param(self):
        client = BlackRoadClient(api_key="test-key-123")
        assert client.api_key == "test-key-123"

    def test_reads_env_var(self):
        with patch.dict(os.environ, {"BLACKROAD_API_KEY": "env-key"}):
            client = BlackRoadClient()
            assert client.api_key == "env-key"

    def test_custom_base_url(self):
        client = BlackRoadClient(api_key="key", base_url="http://localhost:8000/v1")
        assert client.base_url == "http://localhost:8000/v1"

    def test_default_base_url(self):
        client = BlackRoadClient(api_key="key")
        assert "api.blackroad.io" in client.base_url

    def test_has_subclients(self):
        client = BlackRoadClient(api_key="key")
        assert hasattr(client, "agents")
        assert hasattr(client, "tasks")
        assert hasattr(client, "memory")


# ── Mock Server for Integration Tests ───────────────────────────────

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/v1/health":
            self._respond(200, {"status": "ok", "agents": 5, "tasks": 10, "memory": 100})
        elif self.path == "/v1/version":
            self._respond(200, {"version": "1.0.0"})
        elif self.path.startswith("/v1/agents"):
            self._respond(200, {"agents": [
                {"name": "LUCIDIA", "type": "reasoning", "status": "active", "capabilities": ["reasoning"]},
                {"name": "ALICE", "type": "worker", "status": "active", "capabilities": ["execution"]},
            ], "total": 2})
        elif self.path.startswith("/v1/tasks"):
            self._respond(200, {"tasks": [], "count": 0})
        elif self.path.startswith("/v1/memory"):
            self._respond(200, {"entries": [], "total": 0})
        else:
            self._respond(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/v1/chat":
            self._respond(200, {
                "agent": body.get("agent", "LUCIDIA"),
                "response": f"Echo: {body.get('message', '')}",
                "memory_hash": "abc123",
            })
        elif self.path.startswith("/v1/tasks"):
            self._respond(201, {"task_id": "task_abc123", "status": "available"})
        elif self.path.startswith("/v1/memory"):
            self._respond(201, {"hash": "sha256_test", "prev_hash": "GENESIS", "timestamp_ns": 0})
        else:
            self._respond(404, {"error": "not found"})

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass  # Suppress output


@pytest.fixture(scope="module")
def mock_server():
    server = HTTPServer(("127.0.0.1", 0), MockHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


# ── Integration Tests ───────────────────────────────────────────────

class TestIntegration:
    def test_health(self, mock_server):
        client = BlackRoadClient(api_key="test", base_url=f"{mock_server}/v1")
        health = client.health()
        assert health["status"] == "ok"

    def test_version(self, mock_server):
        client = BlackRoadClient(api_key="test", base_url=f"{mock_server}/v1")
        v = client.version()
        assert v == "1.0.0"

    def test_list_agents(self, mock_server):
        client = BlackRoadClient(api_key="test", base_url=f"{mock_server}/v1")
        agents = client.agents.list()
        assert len(agents) == 2
        assert agents[0]["name"] == "LUCIDIA"

    def test_list_tasks(self, mock_server):
        client = BlackRoadClient(api_key="test", base_url=f"{mock_server}/v1")
        tasks = client.tasks.list()
        assert isinstance(tasks, list)


# ── Async Tests ─────────────────────────────────────────────────────

class TestAsync:
    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_server):
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        async with AsyncBlackRoadClient(
            api_key="test",
            base_url=mock_server,
        ) as client:
            health = await client.health()
            assert health["status"] == "ok"

    @pytest.mark.asyncio
    async def test_async_agents(self, mock_server):
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        async with AsyncBlackRoadClient(api_key="test", base_url=mock_server) as client:
            agents = await client.agents.list()
            assert len(agents) >= 1
