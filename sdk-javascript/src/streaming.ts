// BlackRoad SDK — SSE Streaming Utilities
// Helpers for consuming gateway streaming responses

export type StreamChunk = {
  id: string;
  delta: string;
  finish_reason: string | null;
};

/** Parse a single SSE `data:` line into a chunk or null */
function parseChunk(line: string): StreamChunk | null {
  if (!line.startsWith("data: ")) return null;
  const raw = line.slice(6).trim();
  if (raw === "[DONE]") return null;
  try {
    const obj = JSON.parse(raw);
    return {
      id: obj.id,
      delta: obj.choices?.[0]?.delta?.content ?? "",
      finish_reason: obj.choices?.[0]?.finish_reason ?? null,
    };
  } catch {
    return null;
  }
}

/** Stream a chat completion from the gateway, yielding text deltas */
export async function* streamChat(
  gatewayUrl: string,
  model: string,
  messages: Array<{ role: string; content: string }>,
  options?: { temperature?: number; max_tokens?: number }
): AsyncGenerator<string> {
  const resp = await fetch(`${gatewayUrl}/v1/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, messages, stream: true, ...options }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Gateway error ${resp.status}: ${err}`);
  }

  const reader = resp.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const chunk = parseChunk(line.trim());
      if (chunk?.delta) yield chunk.delta;
    }
  }
}

/** Collect a full streaming response into a string */
export async function collectStream(
  gatewayUrl: string,
  model: string,
  messages: Array<{ role: string; content: string }>
): Promise<string> {
  const parts: string[] = [];
  for await (const delta of streamChat(gatewayUrl, model, messages)) {
    parts.push(delta);
  }
  return parts.join("");
}

/** React-friendly hook-compatible stream consumer */
export function createStreamReader(
  onDelta: (delta: string) => void,
  onComplete: (full: string) => void,
  onError: (err: Error) => void
) {
  let full = "";
  return {
    onDelta(delta: string) {
      full += delta;
      onDelta(delta);
    },
    onComplete() { onComplete(full); },
    onError,
  };
}
