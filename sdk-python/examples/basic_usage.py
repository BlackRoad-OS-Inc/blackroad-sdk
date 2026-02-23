"""
BlackRoad Python SDK — Usage Examples

Run these examples to see the SDK in action.
"""

import asyncio
from blackroad import BlackRoadClient, AsyncBlackRoadClient


# ──────────────────────────────────────────────────
# Synchronous (simple)
# ──────────────────────────────────────────────────

def sync_examples():
    """Synchronous SDK usage."""
    client = BlackRoadClient(
        api_key="your-api-key",
        base_url="http://127.0.0.1:8000"  # or https://api.blackroad.io
    )
    
    # List agents
    agents = client.agents.list()
    for agent in agents:
        print(f"  {agent.name} ({agent.type}) — {agent.status}")
    
    # Store a memory
    memory = client.memory.store(
        content="User prefers dark mode and concise responses",
        type="fact",
        truth_state=1,
    )
    print(f"\nStored memory: {memory}")
    
    # Recall memories
    memories = client.memory.recall("user preferences")
    print(f"\nRecalled {len(memories)} memories")
    
    # Create a task
    task = client.tasks.create(
        title="Review PR #42",
        description="Security review needed",
        priority="high",
        tags=["security", "code-review"],
        required_skills=["python", "security"],
    )
    print(f"\nCreated task: {task}")


# ──────────────────────────────────────────────────
# Async (recommended for production)
# ──────────────────────────────────────────────────

async def async_examples():
    """Async SDK usage — recommended for production."""
    async with AsyncBlackRoadClient(
        api_key="your-api-key",
        base_url="http://127.0.0.1:8000",
    ) as client:
        
        # Chat with LUCIDIA
        response = await client.chat("LUCIDIA", "What should I focus on today?")
        print(f"LUCIDIA: {response}")
        
        # Stream a response
        print("\nStreaming response:")
        async for token in client.stream_chat("ALICE", "Summarize today's deployments"):
            print(token, end="", flush=True)
        print()
        
        # Parallel operations
        agents, memories = await asyncio.gather(
            client.agents.list(),
            client.memory.recall("deployment", limit=5),
        )
        print(f"\n{len(agents)} agents, {len(memories)} relevant memories")
        
        # Memory with trinary logic
        await client.memory.store("API v2 deployed successfully", "fact", truth_state=1)
        await client.memory.store("API v1 is deprecated", "fact", truth_state=1)
        
        # Check chain integrity
        is_valid = await client.memory.verify()
        print(f"\nMemory chain integrity: {'✓ valid' if is_valid else '✗ corrupted'}")


if __name__ == "__main__":
    print("=== Sync Examples ===")
    try:
        sync_examples()
    except Exception as e:
        print(f"(Gateway offline: {e})")
    
    print("\n=== Async Examples ===")
    try:
        asyncio.run(async_examples())
    except Exception as e:
        print(f"(Gateway offline: {e})")
