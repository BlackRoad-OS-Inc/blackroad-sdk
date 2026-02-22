import { createContext, useContext, type ReactNode } from 'react';

interface BlackRoadContextValue {
  gatewayUrl: string;
  apiKey?: string;
}

const BlackRoadContext = createContext<BlackRoadContextValue>({
  gatewayUrl: 'http://127.0.0.1:8787',
});

export function BlackRoadProvider({
  children,
  gatewayUrl = 'http://127.0.0.1:8787',
  apiKey,
}: { children: ReactNode; gatewayUrl?: string; apiKey?: string }) {
  return (
    <BlackRoadContext.Provider value={{ gatewayUrl, apiKey }}>
      {children}
    </BlackRoadContext.Provider>
  );
}

export function useBlackRoad() {
  return useContext(BlackRoadContext);
}
