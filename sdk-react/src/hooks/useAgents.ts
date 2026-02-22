import { useState, useEffect, useCallback } from 'react';

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'busy' | 'offline';
  capabilities: string[];
}

export function useAgents(gatewayUrl: string, apiKey?: string) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAgents = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`${gatewayUrl}/v1/agents`, {
        headers: apiKey ? { Authorization: `Bearer ${apiKey}` } : {},
      });
      setAgents(await res.json() as Agent[]);
    } catch (e) {
      setError(e as Error);
    } finally {
      setLoading(false);
    }
  }, [gatewayUrl, apiKey]);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  return { agents, loading, error, refetch: fetchAgents };
}
