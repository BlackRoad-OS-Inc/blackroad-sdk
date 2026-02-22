/**
 * @blackroad/sdk — GraphQL Client
 * Query agents, tasks, and memory via GraphQL
 */

export interface GraphQLConfig {
  endpoint: string;
  apiKey?: string;
  headers?: Record<string, string>;
}

export interface GraphQLResponse<T = unknown> {
  data?: T;
  errors?: Array<{ message: string; path?: string[] }>;
}

export class GraphQLClient {
  private endpoint: string;
  private defaultHeaders: Record<string, string>;

  constructor(config: GraphQLConfig) {
    this.endpoint = config.endpoint;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...(config.apiKey && { Authorization: `Bearer ${config.apiKey}` }),
      ...(config.headers ?? {}),
    };
  }

  async query<T = unknown>(
    query: string,
    variables?: Record<string, unknown>
  ): Promise<T> {
    const res = await fetch(this.endpoint, {
      method: 'POST',
      headers: this.defaultHeaders,
      body: JSON.stringify({ query, variables }),
    });
    const json = (await res.json()) as GraphQLResponse<T>;
    if (json.errors?.length) {
      throw new Error(json.errors.map(e => e.message).join(', '));
    }
    return json.data as T;
  }

  async mutate<T = unknown>(
    mutation: string,
    variables?: Record<string, unknown>
  ): Promise<T> {
    return this.query<T>(mutation, variables);
  }
}

// Pre-built queries
export const Queries = {
  AGENTS: `
    query ListAgents($type: String) {
      agents(type: $type) {
        id name type status capabilities
      }
    }
  `,
  AGENT: `
    query GetAgent($id: String!) {
      agent(id: $id) {
        id name type status uptime tasksCompleted
      }
    }
  `,
  TASKS: `
    query ListTasks($status: String) {
      tasks(status: $status) {
        id title status priority assignedTo createdAt
      }
    }
  `,
  MEMORIES: `
    query SearchMemory($query: String!, $limit: Int) {
      memories(query: $query, limit: $limit) {
        id content type truthState createdAt
      }
    }
  `,
};

export const Mutations = {
  CREATE_TASK: `
    mutation CreateTask($input: TaskInput!) {
      createTask(input: $input) { id title status }
    }
  `,
  ASSIGN_TASK: `
    mutation AssignTask($taskId: String!, $agentId: String!) {
      assignTask(taskId: $taskId, agentId: $agentId) { id status assignedTo }
    }
  `,
  REMEMBER: `
    mutation Remember($content: String!, $type: String) {
      remember(content: $content, type: $type) { id hash }
    }
  `,
};
