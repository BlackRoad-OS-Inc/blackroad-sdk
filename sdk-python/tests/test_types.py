"""Tests for SDK types."""

import pytest
from blackroad.types import Agent, MemoryEntry, Task, ChatResponse


def test_agent_is_online():
    a = Agent(name="LUCIDIA", type="reasoning", status="active")
    assert a.is_online is True

def test_agent_offline():
    a = Agent(name="CIPHER", type="security", status="offline")
    assert a.is_online is False

def test_memory_truth_states():
    m_true = MemoryEntry(hash="abc", prev="GENESIS", content="sky is blue", timestamp_ns=0, truth_state=1)
    m_false = MemoryEntry(hash="def", prev="abc", content="sky is red", timestamp_ns=1, truth_state=-1)
    m_unknown = MemoryEntry(hash="ghi", prev="def", content="sky may be green", timestamp_ns=2, truth_state=0)
    
    assert m_true.is_true
    assert not m_true.is_false
    assert m_false.is_false
    assert m_unknown.is_uncertain

def test_task_status():
    t = Task(title="Deploy", task_id="t001", status="available")
    assert t.is_available
    assert not t.is_done
    
    t.status = "completed"
    assert t.is_done

def test_chat_response_str():
    r = ChatResponse(agent="LUCIDIA", response="Hello world!", memory_hash="abc")
    assert str(r) == "Hello world!"
    assert "LUCIDIA" in repr(r)

def test_agent_repr():
    a = Agent(name="ECHO", type="memory", status="idle")
    assert "ECHO" in repr(a)
