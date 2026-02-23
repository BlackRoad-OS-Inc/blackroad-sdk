/**
 * BlackRoad SDK — React Hooks
 * SWR-style hooks for agents, tasks, memory, and chat.
 * No external dependencies — uses native fetch + useState/useEffect.
 */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";

// ── Config ────────────────────────────────────────────────────────────────────

const DEFAULT_GATEWAY = typeof window !== "undefined"
  ? (process.env.NEXT_PUBLIC_GATEWAY_URL ?? "http://127.0.0.1:8787")
  : (process.env.BLACKROAD_GATEWAY_URL ?? "http://127.0.0.1:8787");

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Agent {
  id: string;
  type: string;
  status: "online" | "offline" | "busy";
  role: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  priority: "low" | "medium" | "high" | "critical";
  status: "available" | "claimed" | "in_progress" | "completed" | "cancelled";
  agent: string | null;
  tags: string[];
  createdAt: string;
}

export interface MemoryEntry {
  hash: string;
  prevHash: string;
  content: string;
  type: "fact" | "observation" | "inference" | "commitment";
  truthState: 1 | 0 | -1;
  timestamp: string;
  agent: string | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  agent?: string;
  timestamp: string;
}

// ── Generic fetch hook ────────────────────────────────────────────────────────

function useFetch<T>(url: string | null, options?: RequestInit) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    if (!url) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(url, { cache: "no-store", ...options });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setData(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)));
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => { refresh(); }, [refresh]);
  return { data, loading, error, refresh };
}

// ── useAgents ─────────────────────────────────────────────────────────────────

export function useAgents(gateway = DEFAULT_GATEWAY) {
  const { data, loading, error, refresh } = useFetch<{ agents: Agent[]; total: number }>(`${gateway}/agents`);
  return {
    agents: data?.agents ?? [],
    total: data?.total ?? 0,
    loading,
    error,
    refresh,
  };
}

export function useAgent(id: string, gateway = DEFAULT_GATEWAY) {
  const { agents } = useAgents(gateway);
  return agents.find(a => a.id === id) ?? null;
}

// ── useTasks ──────────────────────────────────────────────────────────────────

export interface UseTasksOptions {
  status?: Task["status"];
  priority?: Task["priority"];
  limit?: number;
  gateway?: string;
}

export function useTasks({ status, priority, limit = 50, gateway = DEFAULT_GATEWAY }: UseTasksOptions = {}) {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (priority) params.set("priority", priority);
  params.set("limit", String(limit));

  const { data, loading, error, refresh } = useFetch<{ tasks: Task[]; total: number }>(
    `${gateway}/tasks?${params}`
  );

  const createTask = useCallback(async (input: Pick<Task, "title" | "description" | "priority" | "tags">) => {
    const res = await fetch(`${gateway}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const task = await res.json();
    await refresh();
    return task as Task;
  }, [gateway, refresh]);

  const claimTask = useCallback(async (taskId: string, agent: string) => {
    const res = await fetch(`${gateway}/tasks/${taskId}/claim`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await refresh();
    return (await res.json()) as Task;
  }, [gateway, refresh]);

  return {
    tasks: data?.tasks ?? [],
    total: data?.total ?? 0,
    loading,
    error,
    refresh,
    createTask,
    claimTask,
  };
}

// ── useMemory ─────────────────────────────────────────────────────────────────

export interface UseMemoryOptions {
  type?: MemoryEntry["type"];
  agent?: string;
  limit?: number;
  gateway?: string;
}

export function useMemory({ type, agent, limit = 20, gateway = DEFAULT_GATEWAY }: UseMemoryOptions = {}) {
  const params = new URLSearchParams();
  if (type) params.set("type", type);
  if (agent) params.set("agent", agent);
  params.set("limit", String(limit));

  const { data, loading, error, refresh } = useFetch<{ entries: MemoryEntry[]; total: number; chainValid: boolean }>(
    `${gateway}/memory?${params}`
  );

  const addMemory = useCallback(async (input: Pick<MemoryEntry, "content" | "type" | "truthState" | "agent">) => {
    const res = await fetch(`${gateway}/memory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: input.content, type: input.type, truth_state: input.truthState, agent: input.agent }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await refresh();
    return (await res.json()) as MemoryEntry;
  }, [gateway, refresh]);

  return {
    entries: data?.entries ?? [],
    total: data?.total ?? 0,
    chainValid: data?.chainValid ?? true,
    loading,
    error,
    refresh,
    addMemory,
  };
}

// ── useChat ───────────────────────────────────────────────────────────────────

export interface UseChatOptions {
  agent?: string;
  gateway?: string;
}

export function useChat({ agent = "LUCIDIA", gateway = DEFAULT_GATEWAY }: UseChatOptions = {}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(async (content: string) => {
    const userMsg: ChatMessage = { role: "user", content, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    abortRef.current?.abort();
    abortRef.current = new AbortController();

    try {
      const res = await fetch(`${gateway}/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: [...messages, userMsg].map(m => ({ role: m.role, content: m.content })), agent }),
        signal: abortRef.current.signal,
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: data.content ?? data.choices?.[0]?.message?.content ?? "",
        agent,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMsg]);
      return assistantMsg;
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        const errMsg: ChatMessage = { role: "assistant", content: "Gateway offline.", agent: "SYSTEM", timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, errMsg]);
      }
    } finally {
      setLoading(false);
    }
  }, [messages, agent, gateway]);

  const clear = useCallback(() => setMessages([]), []);
  const setAgent = useCallback((newAgent: string) => {
    setMessages(prev => [...prev, { role: "assistant", content: `Switched to ${newAgent}.`, agent: newAgent, timestamp: new Date().toISOString() }]);
  }, []);

  return { messages, loading, send, clear, setAgent, currentAgent: agent };
}

// ── useGatewayHealth ──────────────────────────────────────────────────────────

export function useGatewayHealth(gateway = DEFAULT_GATEWAY) {
  const { data, loading, error, refresh } = useFetch<{ status: string; uptime: number; version: string }>(
    `${gateway}/health`
  );
  return {
    online: !error && data?.status === "ok",
    uptime: data?.uptime ?? 0,
    version: data?.version ?? "unknown",
    loading,
    refresh,
  };
}
