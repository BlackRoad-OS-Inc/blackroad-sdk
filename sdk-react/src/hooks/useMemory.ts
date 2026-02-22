import { useState, useCallback } from 'react';

export interface Memory {
  id: string;
  hash: string;
  content: string;
  type: 'fact' | 'observation' | 'inference' | 'commitment';
  truthState: 1 | 0 | -1;
  createdAt: string;
}

export function useMemory(gatewayUrl: string) {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(false);

  const search = useCallback(async (query: string, limit = 10) => {
    setLoading(true);
    const res = await fetch(
      `${gatewayUrl}/v1/memory/search?q=${encodeURIComponent(query)}&limit=${limit}`
    );
    const results = await res.json() as Memory[];
    setMemories(results);
    setLoading(false);
    return results;
  }, [gatewayUrl]);

  const remember = useCallback(async (
    content: string,
    type: Memory['type'] = 'observation'
  ) => {
    const res = await fetch(`${gatewayUrl}/v1/memory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, type }),
    });
    const memory = await res.json() as Memory;
    setMemories(prev => [memory, ...prev]);
    return memory;
  }, [gatewayUrl]);

  return { memories, loading, search, remember };
}
