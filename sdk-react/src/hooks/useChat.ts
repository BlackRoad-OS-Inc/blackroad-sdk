// Copyright (c) 2025-2026 BlackRoad OS, Inc. All Rights Reserved.
import { useState, useCallback, useRef } from 'react'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  agent?: string
  timestamp: Date
}

export interface UseChatOptions {
  agent?: string
  model?: string
  gatewayUrl?: string
  onError?: (err: Error) => void
}

export interface UseChatReturn {
  messages: ChatMessage[]
  input: string
  isLoading: boolean
  setInput: (value: string) => void
  send: (message?: string) => Promise<void>
  sendStream: (message?: string) => Promise<void>
  clear: () => void
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const {
    agent,
    model,
    gatewayUrl = process.env['NEXT_PUBLIC_GATEWAY_URL'] ?? 'http://127.0.0.1:8787',
    onError,
  } = options

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const send = useCallback(async (message?: string) => {
    const text = message ?? input
    if (!text.trim()) return

    setMessages(prev => [...prev, { role: 'user', content: text, timestamp: new Date() }])
    setInput('')
    setIsLoading(true)

    try {
      const res = await fetch(`${gatewayUrl}/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent, message: text, model, stream: false }),
      })
      if (!res.ok) throw new Error(`Gateway error: ${res.status}`)
      const data = await res.json()
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: data.content, agent: data.agent, timestamp: new Date() },
      ])
    } catch (err) {
      onError?.(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsLoading(false)
    }
  }, [input, agent, model, gatewayUrl, onError])

  const sendStream = useCallback(async (message?: string) => {
    const text = message ?? input
    if (!text.trim()) return

    setMessages(prev => [...prev, { role: 'user', content: text, timestamp: new Date() }])
    setInput('')
    setIsLoading(true)

    // Add empty assistant message to fill with streamed content
    const assistantMsg: ChatMessage = { role: 'assistant', content: '', timestamp: new Date() }
    setMessages(prev => [...prev, assistantMsg])

    abortRef.current = new AbortController()

    try {
      const res = await fetch(`${gatewayUrl}/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent, message: text, model, stream: true }),
        signal: abortRef.current.signal,
      })
      if (!res.ok) throw new Error(`Gateway error: ${res.status}`)
      if (!res.body) throw new Error('No response body')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(l => l.startsWith('data: '))
        for (const line of lines) {
          const data = line.slice(6)
          if (data === '[DONE]') break
          try {
            const { content } = JSON.parse(data)
            setMessages(prev => {
              const updated = [...prev]
              const last = updated[updated.length - 1]
              if (last.role === 'assistant') {
                updated[updated.length - 1] = { ...last, content: last.content + content }
              }
              return updated
            })
          } catch { /* skip malformed */ }
        }
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        onError?.(err instanceof Error ? err : new Error(String(err)))
      }
    } finally {
      setIsLoading(false)
    }
  }, [input, agent, model, gatewayUrl, onError])

  const clear = useCallback(() => {
    abortRef.current?.abort()
    setMessages([])
    setInput('')
  }, [])

  return { messages, input, isLoading, setInput, send, sendStream, clear }
}
