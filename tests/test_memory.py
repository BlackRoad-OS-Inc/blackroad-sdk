"""Tests for PS-SHA-inf memory chain."""
import hashlib, time, pytest
from blackroad_sdk.memory import MemoryChain


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
