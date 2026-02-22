import { useState, useEffect, useRef } from 'react';

export interface StreamEvent {
  type: string;
  data: unknown;
  timestamp: string;
}

export function useStream(gatewayUrl: string, topics: string[] = ['*']) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const url = `${gatewayUrl}/stream?topics=${topics.join(',')}`;
    const es = new EventSource(url);
    esRef.current = es;

    es.onopen = () => setConnected(true);
    es.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data) as StreamEvent;
        setEvents(prev => [event, ...prev].slice(0, 100)); // keep last 100
      } catch {}
    };
    es.onerror = () => setConnected(false);

    return () => {
      es.close();
      setConnected(false);
    };
  }, [gatewayUrl, topics.join(',')]);

  return { events, connected };
}
