/**
 * @blackroad/sdk — JavaScript/TypeScript SDK for BlackRoad OS
 *
 * @example
 * ```ts
 * import { BlackRoadClient } from "@blackroad/sdk";
 *
 * const client = new BlackRoadClient({ gatewayUrl: "http://127.0.0.1:8787" });
 * const agents = await client.agents.list();
 * ```
 */

export { BlackRoadClient } from "./client";
export type {
  BlackRoadClientOptions,
  Agent,
  AgentStatus,
  AgentCapability,
  MemoryEntry,
  MemoryType,
  TruthState,
  Task,
  TaskPriority,
  TaskStatus,
  ChatMessage,
  ChatOptions,
  ChatResponse,
} from "./types";

// React hooks (only available in React environments)
export {
  useAgents,
  useAgent,
  useChat,
  useMemory,
  useTasks,
} from "./react";
