/**
 * BlackRoad React Hooks — useAgents, useMemory, useChat, useTasks
 * 
 * Usage:
 *   import { useAgents, useChat } from '@blackroad/sdk/react';
 *   
 *   function Dashboard() {
 *     const { agents, loading } = useAgents();
 *     const { send, messages } = useChat('LUCIDIA');
 *     ...
 *   }
 */

import { useState, useEffect, useCallback } from 'react';
import type { Agent, MemoryEntry, Task } from './types';

const DEFAULT_BASE_URL = process.env.NEXT_PUBLIC_BLACKROAD_API_URL || 'https://api.blackroad.io';

// ──────────────────────────────────────────────────
// useAgents
// ──────────────────────────────────────────────────

export interface UseAgentsOptions {
  type?: string;
  status?: string;
  refreshInterval?: number;
}

export function useAgents(options: UseAgentsOptions = {}) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAgents = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (options.type) params.set('type', options.type);
      if (options.status) params.set('status', options.status);

      const res = await fetch(`${DEFAULT_BASE_URL}/v1/agents?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json() as { agents?: Agent[] };
      setAgents(data.agents ?? []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  }, [options.type, options.status]);

  useEffect(() => {
    fetchAgents();
    if (options.refreshInterval) {
      const id = setInterval(fetchAgents, options.refreshInterval);
      return () => clearInterval(id);
    }
    return undefined;
  }, [fetchAgents, options.refreshInterval]);

  return { agents, loading, error, refetch: fetchAgents };
}

// ──────────────────────────────────────────────────
// useAgent (single)
// ──────────────────────────────────────────────────

export function useAgent(name: string) {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(`${DEFAULT_BASE_URL}/v1/agents/${name.toUpperCase()}`)
      .then(r => r.json())
      .then(data => { setAgent(data); setLoading(false); })
      .catch(err => { setError(err); setLoading(false); });
  }, [name]);

  return { agent, loading, error };
}

// ──────────────────────────────────────────────────
// useChat
// ──────────────────────────────────────────────────

export interface ChatMessageLocal {
  role: 'user' | 'assistant';
  content: string;
  agent?: string;
  timestamp: Date;
  memoryHash?: string;
}

export interface UseChatOptions {
  agent?: string;
  sessionId?: string;
  apiKey?: string;
}

export function useChat(options: UseChatOptions = {}) {
  const agentName = options.agent || 'LUCIDIA';
  const [messages, setMessages] = useState<ChatMessageLocal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const send = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMsg: ChatMessageLocal = { role: 'user', content, timestamp: new Date() };
    setMessages((prev: ChatMessageLocal[]) => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${DEFAULT_BASE_URL}/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(options.apiKey ? { Authorization: `Bearer ${options.apiKey}` } : {}),
        },
        body: JSON.stringify({
          agent: agentName,
          message: content,
          session_id: options.sessionId,
          use_memory: true,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json() as Record<string, unknown>;

      const memoryHash = data.memory_hash as string | undefined;
      const assistantMsg: ChatMessageLocal = {
        role: 'assistant',
        content: (data.response as string) ?? '',
        agent: (data.agent as string) ?? agentName,
        timestamp: new Date(),
        ...(memoryHash !== undefined ? { memoryHash } : {}),
      };
      setMessages((prev: ChatMessageLocal[]) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  }, [agentName, options.sessionId, options.apiKey]);

  const clear = useCallback(() => setMessages([]), []);

  return { messages, send, clear, loading, error };
}

// ──────────────────────────────────────────────────
// useMemory
// ──────────────────────────────────────────────────

export function useMemory(query?: string, limit = 10) {
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(!!query);
  const [error, setError] = useState<Error | null>(null);

  const recall = useCallback(async (q: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${DEFAULT_BASE_URL}/v1/memory/recall`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, limit }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json() as { memories?: MemoryEntry[] };
      setMemories(data.memories ?? []);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    if (query) recall(query);
  }, [query, recall]);

  return { memories, loading, error, recall };
}

// ──────────────────────────────────────────────────
// useTasks
// ──────────────────────────────────────────────────

export function useTasks(status?: string) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      const params = status ? `?status=${status}` : '';
      const res = await fetch(`${DEFAULT_BASE_URL}/v1/tasks${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json() as { tasks?: Task[] };
      setTasks(data.tasks ?? []);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const claim = useCallback(async (taskId: string, agentId: string) => {
    const res = await fetch(`${DEFAULT_BASE_URL}/v1/tasks/${taskId}/claim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await fetchTasks();
  }, [fetchTasks]);

  return { tasks, loading, error, refetch: fetchTasks, claim };
}
