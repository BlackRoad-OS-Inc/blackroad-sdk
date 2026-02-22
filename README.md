# blackroad-sdk

> TypeScript SDK — `@blackroad/sdk` — for building on BlackRoad OS.

[![CI](https://github.com/BlackRoad-OS-Inc/blackroad-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/BlackRoad-OS-Inc/blackroad-sdk/actions/workflows/ci.yml)

## Overview

The official TypeScript SDK for BlackRoad OS. Build agents, integrations, and tools that connect to the BlackRoad ecosystem.

## Install

```bash
npm install @blackroad/sdk
```

## Quick Start

```typescript
import { createSDK } from '@blackroad/sdk';

const sdk = createSDK({ agentId: 'my-agent' });

// Memory
await sdk.memory.remember('User prefers dark mode');
await sdk.memory.search('user preferences');

// Agents
const agents = await sdk.agents.list({ type: 'backend' });

// Coordination
await sdk.coordination.publish('tasks', 'new', { title: 'Build feature' });
await sdk.coordination.delegate({ taskType: 'analysis', description: '...' });
```

## Structure

```
blackroad-sdk/
├── src/
│   ├── index.ts          # SDK entry point + createSDK factory
│   ├── agents/           # Agent registry & communication
│   ├── memory/           # PS-SHA∞ memory system
│   ├── coordination/     # Event bus, pub/sub, delegation
│   └── types/            # TypeScript types & interfaces
├── test/                 # Tests
└── package.json
```

## API Reference

### `sdk.memory`
| Method | Description |
|--------|-------------|
| `.remember(content)` | Store a fact |
| `.observe(content)` | Store an observation |
| `.infer(content)` | Store an inference |
| `.search(query)` | Search memories |

### `sdk.agents`
| Method | Description |
|--------|-------------|
| `.list(filter?)` | List agents |
| `.findByCapabilities(caps)` | Find agents by skill |

### `sdk.coordination`
| Method | Description |
|--------|-------------|
| `.publish(topic, event, payload)` | Publish event |
| `.delegate(task)` | Delegate task to best agent |
| `.broadcast(message)` | Broadcast to all agents |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

© BlackRoad OS, Inc. — All rights reserved. Proprietary.
