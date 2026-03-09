/**
 * BlackRoad OS — Cloudflare Workers Gateway
 *
 * Handles long-running and async tasks proxied from the BlackRoad SDK.
 * Endpoints:
 *   GET  /health           — Liveness check
 *   GET  /agents           — List registered agents
 *   GET  /agents/:id       — Get agent by ID
 *   POST /agents/:id/wake  — Wake a specific agent
 *   POST /agents/:id/task  — Assign a task to an agent
 *   POST /chat             — Send a chat message (with optional long-running timeout)
 *   POST /v1/chat/completions — OpenAI-compatible completions
 *   POST /memory           — Store a memory entry
 *   GET  /memory           — Retrieve recent memories
 *   POST /coordination/publish   — Publish a coordination event
 *   POST /coordination/delegate  — Delegate a task
 *   POST /coordination/broadcast — Broadcast to all agents
 */

export interface Env {
  /** URL of the upstream BlackRoad API (set in wrangler.toml or Cloudflare dashboard) */
  BLACKROAD_API_URL: string;
  /** Optional bearer token for authenticating with the upstream API */
  BLACKROAD_API_KEY?: string;
  /** KV namespace for caching short-lived responses (optional) */
  BLACKROAD_CACHE?: KVNamespace;
}

const BUILTIN_AGENTS = [
  { id: "lucidia-001", name: "LUCIDIA", type: "reasoning", status: "active", capabilities: ["analysis", "philosophy", "strategy"], model: "qwen2.5:3b" },
  { id: "alice-001",   name: "ALICE",   type: "worker",    status: "active", capabilities: ["execution", "automation", "devops"],  model: "qwen2.5:3b" },
  { id: "octavia-001", name: "OCTAVIA", type: "devops",    status: "active", capabilities: ["infrastructure", "deployment", "monitoring"], model: "qwen2.5:3b" },
  { id: "prism-001",   name: "PRISM",   type: "analytics", status: "active", capabilities: ["patterns", "data", "insights"],      model: "qwen2.5:3b" },
  { id: "echo-001",    name: "ECHO",    type: "memory",    status: "active", capabilities: ["recall", "storage", "synthesis"],    model: "nomic-embed-text" },
  { id: "cipher-001",  name: "CIPHER",  type: "security",  status: "active", capabilities: ["auth", "encryption", "scanning"],   model: "qwen2.5:3b" },
];

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Agent-Id, Authorization",
    },
  });
}

async function proxyToUpstream(env: Env, path: string, init: RequestInit): Promise<Response | null> {
  if (!env.BLACKROAD_API_URL) return null;
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(env.BLACKROAD_API_KEY ? { Authorization: `Bearer ${env.BLACKROAD_API_KEY}` } : {}),
    };
    const res = await fetch(`${env.BLACKROAD_API_URL}${path}`, { ...init, headers });
    if (res.ok) return res;
  } catch {
    // fall through to built-in responses
  }
  return null;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const { pathname } = url;
    const method = request.method.toUpperCase();

    // CORS pre-flight
    if (method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, X-Agent-Id, Authorization",
        },
      });
    }

    // ── GET /health ──────────────────────────────────────────────────────────
    if (method === "GET" && pathname === "/health") {
      return json({
        status: "ok",
        service: "blackroad-gateway",
        version: "1.0.0",
        timestamp: new Date().toISOString(),
        agents: BUILTIN_AGENTS.length,
      });
    }

    // ── GET /agents ──────────────────────────────────────────────────────────
    if (method === "GET" && pathname === "/agents") {
      const upstream = await proxyToUpstream(env, "/agents", { method: "GET" });
      if (upstream) return upstream;
      const type = url.searchParams.get("type");
      const status = url.searchParams.get("status") ?? "active";
      let agents = BUILTIN_AGENTS.filter((a) => a.status === status);
      if (type) agents = agents.filter((a) => a.type === type);
      return json(agents);
    }

    // ── GET /agents/:id ──────────────────────────────────────────────────────
    const agentMatch = pathname.match(/^\/agents\/([^/]+)$/);
    if (method === "GET" && agentMatch) {
      const id = agentMatch[1];
      const upstream = await proxyToUpstream(env, `/agents/${id}`, { method: "GET" });
      if (upstream) return upstream;
      const agent = BUILTIN_AGENTS.find((a) => a.id === id);
      if (!agent) return json({ error: "Agent not found", id }, 404);
      return json(agent);
    }

    // ── POST /agents/:id/wake ────────────────────────────────────────────────
    const wakeMatch = pathname.match(/^\/agents\/([^/]+)\/wake$/);
    if (method === "POST" && wakeMatch) {
      const id = wakeMatch[1];
      const body = await request.text();
      const upstream = await proxyToUpstream(env, `/agents/${id}/wake`, { method: "POST", body });
      if (upstream) return upstream;
      const agent = BUILTIN_AGENTS.find((a) => a.id === id);
      if (!agent) return json({ error: "Agent not found", id }, 404);
      return json({ status: "active", message: `${agent.name} is now ONLINE`, agent_id: id });
    }

    // ── POST /agents/:id/task ────────────────────────────────────────────────
    const taskMatch = pathname.match(/^\/agents\/([^/]+)\/task$/);
    if (method === "POST" && taskMatch) {
      const id = taskMatch[1];
      const body = await request.text();
      const upstream = await proxyToUpstream(env, `/agents/${id}/task`, { method: "POST", body });
      if (upstream) return upstream;
      let payload: Record<string, unknown> = {};
      try { payload = JSON.parse(body); } catch { /* ignore */ }
      return json({
        task_id: `t_${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`,
        agent_id: id,
        status: "queued",
        description: payload["description"] ?? "Task queued",
      });
    }

    // ── POST /chat ────────────────────────────────────────────────────────────
    if (method === "POST" && pathname === "/chat") {
      const body = await request.text();
      const upstream = await proxyToUpstream(env, "/chat", { method: "POST", body });
      if (upstream) return upstream;
      let payload: Record<string, unknown> = {};
      try { payload = JSON.parse(body); } catch { /* ignore */ }
      const agent = payload["agent"] as string | undefined;
      const agentName = agent
        ? (BUILTIN_AGENTS.find((a) => a.id === agent || a.name.toLowerCase() === agent.toLowerCase())?.name ?? agent)
        : "LUCIDIA";
      return json({
        response: `[${agentName}] Received: "${payload["message"] ?? ""}" — Gateway is running in offline mode. Connect BLACKROAD_API_URL to enable full inference.`,
        agent: agentName,
        timestamp: new Date().toISOString(),
      });
    }

    // ── POST /v1/chat/completions ─────────────────────────────────────────────
    if (method === "POST" && pathname === "/v1/chat/completions") {
      const body = await request.text();
      const upstream = await proxyToUpstream(env, "/v1/chat/completions", { method: "POST", body });
      if (upstream) return upstream;
      let payload: Record<string, unknown> = {};
      try { payload = JSON.parse(body); } catch { /* ignore */ }
      const messages = (payload["messages"] as Array<{ role: string; content: string }>) ?? [];
      const lastMsg = messages[messages.length - 1]?.content ?? "";
      return json({
        id: `chatcmpl-${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`,
        object: "chat.completion",
        created: Math.floor(Date.now() / 1000),
        model: payload["model"] ?? "blackroad-default",
        choices: [{
          index: 0,
          message: {
            role: "assistant",
            content: `[Offline mode] Echo: ${lastMsg}`,
          },
          finish_reason: "stop",
        }],
        usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
      });
    }

    // ── POST /memory ─────────────────────────────────────────────────────────
    if (method === "POST" && pathname === "/memory") {
      const body = await request.text();
      const upstream = await proxyToUpstream(env, "/memory", { method: "POST", body });
      if (upstream) return upstream;
      let payload: Record<string, unknown> = {};
      try { payload = JSON.parse(body); } catch { /* ignore */ }
      const key = (payload["key"] as string) ?? `mem_${Date.now()}`;
      const encoder = new TextEncoder();
      const data = encoder.encode(`GENESIS:${key}:${JSON.stringify(payload["value"])}:${Date.now()}`);
      const hashBuf = await crypto.subtle.digest("SHA-256", data);
      const hashArr = Array.from(new Uint8Array(hashBuf));
      const ps_sha = hashArr.map((b) => b.toString(16).padStart(2, "0")).join("");
      // Cache in KV if available (TTL: 24h)
      if (env.BLACKROAD_CACHE) {
        await env.BLACKROAD_CACHE.put(key, JSON.stringify({ key, value: payload["value"], ps_sha }), { expirationTtl: 86400 });
      }
      return json({ key, ps_sha, stored: true });
    }

    // ── GET /memory ──────────────────────────────────────────────────────────
    if (method === "GET" && pathname === "/memory") {
      const upstream = await proxyToUpstream(env, "/memory", { method: "GET" });
      if (upstream) return upstream;
      return json({ entries: [], message: "Connect BLACKROAD_API_URL for persistent memory." });
    }

    // ── POST /coordination/publish ────────────────────────────────────────────
    if (method === "POST" && pathname === "/coordination/publish") {
      const body = await request.text();
      const upstream = await proxyToUpstream(env, "/coordination/publish", { method: "POST", body });
      if (upstream) return upstream;
      return json({ status: "published", queued: true });
    }

    // ── POST /coordination/delegate ───────────────────────────────────────────
    if (method === "POST" && pathname === "/coordination/delegate") {
      const body = await request.text();
      const upstream = await proxyToUpstream(env, "/coordination/delegate", { method: "POST", body });
      if (upstream) return upstream;
      let payload: Record<string, unknown> = {};
      try { payload = JSON.parse(body); } catch { /* ignore */ }
      const skills = (payload["required_skills"] as string[]) ?? [];
      const candidate = BUILTIN_AGENTS.find((a) =>
        skills.some((s) => a.capabilities.includes(s))
      ) ?? BUILTIN_AGENTS[0];
      return json({
        assigned_to: candidate.id,
        task_id: `t_${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`,
        agent: candidate.name,
        status: "delegated",
      });
    }

    // ── POST /coordination/broadcast ─────────────────────────────────────────
    if (method === "POST" && pathname === "/coordination/broadcast") {
      const body = await request.text();
      const upstream = await proxyToUpstream(env, "/coordination/broadcast", { method: "POST", body });
      if (upstream) return upstream;
      return json({ recipients: BUILTIN_AGENTS.length, status: "broadcast_sent" });
    }

    // ── 404 ──────────────────────────────────────────────────────────────────
    return json({ error: "Not found", path: pathname }, 404);
  },
};
