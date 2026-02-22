/**
 * @blackroad/sdk — Webhook Client
 * Register and manage webhooks for BlackRoad OS events
 */

export type WebhookEvent =
  | 'agent.started'
  | 'agent.stopped'
  | 'task.created'
  | 'task.completed'
  | 'task.failed'
  | 'memory.stored'
  | 'system.alert'
  | '*';

export interface Webhook {
  id: string;
  url: string;
  events: WebhookEvent[];
  secret?: string;
  active: boolean;
  createdAt: string;
}

export interface WebhookPayload<T = unknown> {
  id: string;
  event: WebhookEvent;
  timestamp: string;
  data: T;
  signature?: string;
}

export class WebhookClient {
  constructor(
    private baseUrl: string,
    private apiKey: string
  ) {}

  private headers() {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.apiKey}`,
    };
  }

  async register(url: string, events: WebhookEvent[], secret?: string): Promise<Webhook> {
    const res = await fetch(`${this.baseUrl}/webhooks`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ url, events, secret }),
    });
    return res.json() as Promise<Webhook>;
  }

  async list(): Promise<Webhook[]> {
    const res = await fetch(`${this.baseUrl}/webhooks`, { headers: this.headers() });
    return res.json() as Promise<Webhook[]>;
  }

  async delete(id: string): Promise<void> {
    await fetch(`${this.baseUrl}/webhooks/${id}`, {
      method: 'DELETE',
      headers: this.headers(),
    });
  }

  /** Verify a webhook signature */
  async verify(payload: string, signature: string, secret: string): Promise<boolean> {
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      'raw',
      encoder.encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify']
    );
    const sigBuffer = Buffer.from(signature.replace('sha256=', ''), 'hex');
    return crypto.subtle.verify('HMAC', key, sigBuffer, encoder.encode(payload));
  }
}
