import { useState, useEffect, useCallback } from 'react';

export interface Task {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assignedTo?: string;
  priority: number;
  createdAt: string;
}

export function useTasks(gatewayUrl: string, filter?: { status?: string; assignedTo?: string }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    const params = new URLSearchParams(filter as Record<string, string>);
    const res = await fetch(`${gatewayUrl}/v1/tasks?${params}`);
    setTasks(await res.json() as Task[]);
    setLoading(false);
  }, [gatewayUrl, filter]);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const createTask = useCallback(async (task: Partial<Task>) => {
    const res = await fetch(`${gatewayUrl}/v1/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    const created = await res.json() as Task;
    setTasks(prev => [...prev, created]);
    return created;
  }, [gatewayUrl]);

  return { tasks, loading, createTask, refetch: fetchTasks };
}
