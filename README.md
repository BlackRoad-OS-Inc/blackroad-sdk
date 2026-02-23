# blackroad-sdk

[![CI](https://github.com/BlackRoad-OS-Inc/blackroad-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/BlackRoad-OS-Inc/blackroad-sdk/actions/workflows/ci.yml)

> BlackRoad OS Python + TypeScript SDK

## Python SDK

```bash
pip install -e .
```

```python
from blackroad_sdk import BlackRoadClient
import asyncio

async def main():
    client = BlackRoadClient(gateway_url="http://localhost:8787")
    
    # PS-SHA-infinity persistent memory
    m = client.memory.remember("Gateway uses tokenless architecture")
    print(f"Hash: {m.hash[:8]}  Chain length: {client.memory.chain_length}")
    
    # Agent registry
    for agent in client.agents.list():
        print(f"{agent.name}: {', '.join(agent.capabilities)}")
    
    # Generate text
    text = await client.generate("qwen2.5:3b", "Describe the BlackRoad OS")
    print(text)

asyncio.run(main())
```

## TypeScript SDK

```bash
npm install @blackroad/sdk
```

```typescript
import { BlackRoadClient } from '@blackroad/sdk';

const client = new BlackRoadClient({ gatewayUrl: 'http://localhost:8787' });
await client.memory.remember('Gateway uses tokenless architecture');
const agents = await client.agents.list({ type: 'reasoning' });
```

## Memory System (PS-SHA∞)

Hash-chained persistent memory — tamper-evident, distributed:

```python
client.memory.remember("fact")          # truth_state=1
client.memory.observe("observation")    # truth_state=0
client.memory.infer("inference")        # truth_state=0
print(client.memory.head_hash)          # chain integrity
```

## License

Proprietary — BlackRoad OS, Inc. All rights reserved.
