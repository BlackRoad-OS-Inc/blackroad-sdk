import { describe, it, expect, vi, beforeEach } from "vitest";
import { BlackRoadClient, createClient } from "../src/index";

const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("BlackRoadClient", () => {
  let client: BlackRoadClient;

  beforeEach(() => {
    client = createClient({ baseUrl: "http://localhost:8787", apiKey: "test-key" });
    vi.clearAllMocks();
  });

  it("sends chat message", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
    });
    const res = await client.chat({ message: "Hi", agent: "LUCIDIA" });
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8787/chat",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("lists agents", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ agents: [{ name: "LUCIDIA", status: "online" }] }),
    });
    const { agents } = await client.listAgents();
    expect(agents).toHaveLength(1);
    expect(agents[0].name).toBe("LUCIDIA");
  });

  it("stores memory", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ hash: "abc123", stored: true }),
    });
    const res = await client.remember({ key: "test", value: "data", type: "fact" });
    expect(res.stored).toBe(true);
    expect(res.hash).toBe("abc123");
  });

  it("recalls memory by key", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ key: "test", value: "data", truth_state: 1 }),
    });
    const res = await client.recall("test");
    expect(res.value).toBe("data");
    expect(res.truth_state).toBe(1);
  });

  it("searches memory semantically", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ results: [{ key: "test", score: 0.95 }] }),
    });
    const { results } = await client.search("test query");
    expect(results).toHaveLength(1);
  });

  it("assigns task to agent", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ task_id: "t-001", status: "assigned" }),
    });
    const res = await client.assignTask({ type: "analysis", description: "Analyze logs", agent: "PRISM" });
    expect(res.task_id).toBe("t-001");
    expect(res.status).toBe("assigned");
  });

  it("wakes sleeping agent", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ agent: "ECHO", status: "online", message: "ECHO is awake" }),
    });
    const res = await client.wakeAgent("ECHO");
    expect(res.status).toBe("online");
  });

  it("handles api errors", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 429,
      json: () => Promise.resolve({ error: "Rate limit exceeded" }),
    });
    await expect(client.chat({ message: "Hi" })).rejects.toThrow("Rate limit exceeded");
  });

  it("createClient factory works", () => {
    const c = createClient({ baseUrl: "https://api.blackroad.io", apiKey: "bk_live_abc" });
    expect(c).toBeInstanceOf(BlackRoadClient);
  });
});
