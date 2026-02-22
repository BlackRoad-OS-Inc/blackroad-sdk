// Copyright (c) 2025-2026 BlackRoad OS, Inc. All Rights Reserved.
import { useState, useEffect, useCallback } from 'react'

export interface GatewayHealth {
  status: 'healthy' | 'degraded' | 'unreachable'
  version?: string
  uptime?: number
  providers?: string[]
}

export interface UseGatewayOptions {
  url?: string
  pollInterval?: number  // ms, 0 = no polling
}

export function useGateway(options: UseGatewayOptions = {}) {
  const {
    url = process.env['NEXT_PUBLIC_GATEWAY_URL'] ?? 'http://127.0.0.1:8787',
    pollInterval = 30_000,
  } = options

  const [health, setHealth] = useState<GatewayHealth>({ status: 'unreachable' })
  const [isChecking, setIsChecking] = useState(false)

  const check = useCallback(async () => {
    setIsChecking(true)
    try {
      const res = await fetch(`${url}/v1/health`, { cache: 'no-store' })
      if (!res.ok) {
        setHealth({ status: 'degraded' })
        return
      }
      const data = await res.json()
      setHealth({
        status: 'healthy',
        version: data.version,
        uptime: data.uptime,
        providers: data.providers,
      })
    } catch {
      setHealth({ status: 'unreachable' })
    } finally {
      setIsChecking(false)
    }
  }, [url])

  useEffect(() => {
    check()
    if (pollInterval > 0) {
      const id = setInterval(check, pollInterval)
      return () => clearInterval(id)
    }
  }, [check, pollInterval])

  return { health, isChecking, check, gatewayUrl: url }
}
