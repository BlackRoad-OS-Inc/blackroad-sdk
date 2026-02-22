/**
 * @blackroad/sdk-react — React hooks for BlackRoad OS
 * Provides hooks for agents, tasks, memory, and streaming
 */

export { useAgents } from './hooks/useAgents';
export { useTasks } from './hooks/useTasks';
export { useMemory } from './hooks/useMemory';
export { useStream } from './hooks/useStream';
export { BlackRoadProvider, useBlackRoad } from './context';
export { useChat } from './hooks/useChat.js'
export type { ChatMessage, UseChatOptions, UseChatReturn } from './hooks/useChat.js'
export { useGateway } from './hooks/useGateway.js'
export type { GatewayHealth, UseGatewayOptions } from './hooks/useGateway.js'
