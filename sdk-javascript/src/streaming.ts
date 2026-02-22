/**
 * @blackroad/sdk — Streaming Client
 * Server-Sent Events (SSE) for real-time agent updates
 */

export type StreamEvent = 
  | { type: 'agent_update'; agentId: string; status: string; message: string }
  | { type: 'task_update'; taskId: string; status: string; progress: number }
  | { type: 'memory_update'; memoryId: string; content: string }
  | { type: 'heartbeat'; timestamp: string }
  | { type: 'error'; message: string };

export type StreamHandler = (event: StreamEvent) => void;

export class StreamClient {
  private eventSource: EventSource | null = null;
  private handlers = new Map<string, Set<StreamHandler>>();

  constructor(
    private baseUrl: string,
    private apiKey: string
  ) {}

  connect(topics: string[] = ['*']): void {
    const url = new URL(`${this.baseUrl}/stream`);
    url.searchParams.set('topics', topics.join(','));
    url.searchParams.set('token', this.apiKey);

    this.eventSource = new EventSource(url.toString());

    this.eventSource.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data) as StreamEvent;
        this.emit(event.type, event);
        this.emit('*', event);
      } catch {}
    };

    this.eventSource.onerror = () => {
      this.emit('error', { type: 'error', message: 'Stream connection error' });
    };
  }

  on(event: string, handler: StreamHandler): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
    return () => this.handlers.get(event)?.delete(handler);
  }

  private emit(event: string, data: StreamEvent): void {
    this.handlers.get(event)?.forEach(h => h(data));
  }

  disconnect(): void {
    this.eventSource?.close();
    this.eventSource = null;
  }
}

/** Node.js SSE client (no EventSource in Node) */
export async function* streamEvents(
  url: string,
  apiKey: string,
  topics: string[] = ['*']
): AsyncGenerator<StreamEvent> {
  const endpoint = new URL(`${url}/stream`);
  endpoint.searchParams.set('topics', topics.join(','));
  
  const res = await fetch(endpoint.toString(), {
    headers: { Authorization: `Bearer ${apiKey}`, Accept: 'text/event-stream' },
  });

  if (!res.body) throw new Error('No response body');
  
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          yield JSON.parse(line.slice(6)) as StreamEvent;
        } catch {}
      }
    }
  }
}
