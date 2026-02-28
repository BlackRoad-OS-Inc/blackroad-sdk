"""Tests for PS-SHA-inf memory chain."""
import hashlib, time, pytest
from pathlib import Path
from blackroad_sdk.memory import MemoryChain, MemoryClient, Memory
from blackroad_sdk.client import BlackRoadClient


def test_genesis_hash():
    chain = MemoryChain()
    entry = chain.remember("test", "hello world")
    assert entry["prev_hash"] == "GENESIS"
    assert len(entry["hash"]) == 64  # sha256 hex


def test_chain_links():
    chain = MemoryChain()
    e1 = chain.remember("k1", "v1")
    e2 = chain.remember("k2", "v2")
    assert e2["prev_hash"] == e1["hash"]


def test_verify_clean_chain():
    chain = MemoryChain()
    chain.remember("fact", "gateway is tokenless")
    chain.remember("obs", "uptime 99.1%")
    chain.remember("inf", "fleet healthy")
    valid, broken = chain.verify()
    assert valid is True
    assert broken == []


def test_tamper_detection():
    chain = MemoryChain()
    chain.remember("k1", "original")
    chain.remember("k2", "also original")
    chain.remember("k3", "third entry")
    # Tamper entry 0
    chain.chain[0]["content"] = "TAMPERED"
    valid, broken = chain.verify()
    assert valid is False
    assert 0 in broken
    # Cascade: entry 1 and 2 also broken (prev_hash chain is disrupted)
    assert len(broken) >= 1


def test_hash_determinism():
    """Same inputs must produce same hash."""
    chain = MemoryChain()
    e = chain.remember("k", "v")
    raw = f"{e['prev_hash']}:k:v:{e['timestamp_ns']}"
    expected = hashlib.sha256(raw.encode()).hexdigest()
    assert e["hash"] == expected


def test_search():
    chain = MemoryChain()
    chain.remember("fact", "The gateway is tokenless and secure")
    chain.remember("obs", "aria64 is online")
    chain.remember("inf", "tokens never leave the gateway")
    results = chain.search("gateway")
    assert len(results) >= 1
    assert any("gateway" in r.get("content", "").lower() for r in results)


# ---- MemoryClient tests ----

@pytest.fixture
def mem_client(tmp_path):
    client = BlackRoadClient(base_url="http://test.local", agent_id="test-agent")
    mc = client.memory
    # Redirect journal to an isolated temp file and reset chain state
    mc._journal = tmp_path / "test-journal.jsonl"
    mc._chain = []
    mc._prev_hash = "GENESIS"
    return mc


def test_memory_client_remember(mem_client):
    m = mem_client.remember("the sky is blue")
    assert isinstance(m, Memory)
    assert m.type == "fact"
    assert m.truth_state == 1
    assert m.content == "the sky is blue"
    assert m.key == "memory"


def test_memory_client_remember_custom_key(mem_client):
    m = mem_client.remember("gateway is tokenless", key="security")
    assert m.key == "security"


def test_memory_client_observe(mem_client):
    m = mem_client.observe("rain detected")
    assert m.type == "observation"
    assert m.truth_state == 0
    assert m.key == "observation"


def test_memory_client_infer(mem_client):
    m = mem_client.infer("storm incoming")
    assert m.type == "inference"
    assert m.truth_state == 0
    assert m.key == "inference"


def test_memory_client_search(mem_client):
    mem_client.remember("gateway is tokenless", key="security")
    mem_client.observe("uptime 99%", key="health")
    results = mem_client.search("gateway")
    assert len(results) >= 1
    assert any("gateway" in m.content for m in results)


def test_memory_client_search_by_key(mem_client):
    mem_client.remember("some content", key="findable-key")
    results = mem_client.search("findable-key")
    assert len(results) >= 1


def test_memory_client_recent(mem_client):
    mem_client.remember("entry 1")
    mem_client.remember("entry 2")
    mem_client.remember("entry 3")
    recent = mem_client.recent(2)
    assert len(recent) == 2
    # recent() returns newest first
    assert recent[0].content == "entry 3"


def test_memory_client_chain_length(mem_client):
    assert mem_client.chain_length == 0
    mem_client.remember("test entry")
    assert mem_client.chain_length == 1


def test_memory_client_head_hash_genesis(mem_client):
    # "GENESIS"[:16] == "GENESIS" since the string is only 7 chars
    assert mem_client.head_hash == "GENESIS"


def test_memory_client_head_hash_after_store(mem_client):
    mem_client.remember("test entry")
    assert len(mem_client.head_hash) == 16


def test_memory_client_journal_persistence(mem_client, tmp_path):
    """Entries written to journal are reloaded on next instantiation."""
    mem_client.remember("persisted fact", key="persist-test")
    assert mem_client._journal.exists()

    # Simulate a fresh client loading from the same journal
    client2 = BlackRoadClient(base_url="http://test.local", agent_id="test-agent")
    mc2 = client2.memory
    mc2._chain = []
    mc2._prev_hash = "GENESIS"
    mc2._journal = mem_client._journal
    mc2._load_journal()
    assert mc2.chain_length == 1
    assert mc2._chain[0].content == "persisted fact"


def test_memory_client_load_journal_corrupt_line(mem_client):
    """Corrupt lines in journal are silently skipped."""
    mem_client._journal.write_text("not-valid-json\n")
    mem_client._chain = []
    mem_client._prev_hash = "GENESIS"
    mem_client._load_journal()
    assert mem_client.chain_length == 0
