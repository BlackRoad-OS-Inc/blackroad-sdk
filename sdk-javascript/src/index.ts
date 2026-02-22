/**
 * BlackRoad JavaScript/TypeScript SDK
 * Official client for the BlackRoad API
 */

export { BlackRoadClient } from './client';
export { AgentAPI } from './agents';
export { TaskAPI } from './tasks';
export { MemoryAPI } from './memory';
export * from './types';
export * from './errors';

// Default export
export { BlackRoadClient as default } from './client';

// Extended capabilities
export { GraphQLClient, Queries, Mutations } from './graphql';
export type { GraphQLConfig, GraphQLResponse } from './graphql';

export { WebhookClient } from './webhooks';
export type { Webhook, WebhookEvent, WebhookPayload } from './webhooks';

export { StreamClient, streamEvents } from './streaming';
export type { StreamEvent, StreamHandler } from './streaming';
