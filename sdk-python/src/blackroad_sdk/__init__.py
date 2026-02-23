"""
blackroad-sdk — Python SDK for BlackRoad OS

Usage:
    from blackroad_sdk import BlackRoadClient

    async with BlackRoadClient() as client:
        await client.health()
        reply = await client.chat("Hello from Python!")
        await client.memory_write("key", {"data": "value"})
"""
from .client import BlackRoadClient, ChatMessage
from .memory import MemoryClient
from .agents import AgentsClient

__version__ = "0.2.0"
__all__ = ["BlackRoadClient", "ChatMessage", "MemoryClient", "AgentsClient"]


def create_client(gateway_url: str | None = None, **kwargs) -> BlackRoadClient:
    """Factory for creating a configured BlackRoadClient."""
    import os
    url = gateway_url or os.getenv("BLACKROAD_GATEWAY_URL", "http://127.0.0.1:8787")
    return BlackRoadClient(gateway_url=url, **kwargs)
