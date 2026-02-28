/**
 * TypeScript types for the BlackRoad OS SDK.
 */

export type AgentStatus = "online" | "offline" | "busy" | "idle";
export type AgentCapability =
  | "reasoning"
  | "routing"
  | "compute"
  | "analysis"
  | "memory"
  | "security"
  | "creative";

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: AgentStatus;
  capabilities: AgentCapability[];
  uptime?: number;
  tasks_completed?: number;
  model?: string;
  last_seen?: string;
}

export type TruthState = 1 | 0 | -1;
export type MemoryType = "fact" | "observation" | "inference" | "commitment";

export interface MemoryEntry {
  hash: string;
  prev_hash: string;
  content: string;
  type: MemoryType;
  truth_state: TruthState;
  timestamp: string;
  agent?: string;
  tags?: string[];
}

export type TaskPriority = "low" | "medium" | "high" | "critical";
export type TaskStatus =
  | "available"
  | "claimed"
  | "in_progress"
  | "completed"
  | "cancelled";

export interface Task {
  id: string;
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;
  skills: string[];
  assigned_to?: string;
  posted_by: string;
  posted_at: string;
  completed_at?: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface ChatOptions {
  model?: string;
  agent?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
}

export interface ChatResponse {
  id: string;
  model: string;
  message: ChatMessage;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
  };
}

export interface BlackRoadClientOptions {
  /** Gateway URL. Defaults to http://127.0.0.1:8787 */
  gatewayUrl?: string;
  /** API key for authenticated endpoints */
  apiKey?: string;
  /** Request timeout in ms. Defaults to 30000 */
  timeout?: number;
}

export interface ClientConfig {
  /** API key for authenticated endpoints */
  apiKey?: string;
  /** Base URL for the API. Defaults to https://api.blackroad.io/v1 */
  baseUrl?: string;
  /** Request timeout in ms. Defaults to 30000 */
  timeout?: number;
  /** Max retries for failed requests. Defaults to 3 */
  maxRetries?: number;
}

export interface HealthStatus {
  status: string;
  uptime?: number;
  version?: string;
}

export interface Stats {
  total: number;
  active?: number;
  pending?: number;
  completed?: number;
}

export interface AgentListOptions {
  type?: string;
  status?: string;
  division?: string;
  level?: number;
}

export interface RegisterAgentOptions {
  name: string;
  type?: string;
  division?: string;
  level?: number;
  metadata?: Record<string, unknown>;
}

export interface MemoryQueryOptions {
  search?: string;
  action?: string;
  entity?: string;
  tags?: string[];
  since?: Date;
  until?: Date;
  limit?: number;
  offset?: number;
}

export interface LogMemoryOptions {
  action: string;
  entity: string;
  details?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface TaskListOptions {
  status?: string;
  priority?: string;
  division?: string;
}

export interface DispatchTaskOptions {
  title: string;
  description?: string;
  priority?: TaskPriority;
  division?: string;
  target_level?: number;
  metadata?: Record<string, unknown>;
}
