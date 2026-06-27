import { describe, it, expect } from "vitest";
import worker from "../src/index.js";
import type { Env } from "../src/index.js";

// Minimal env for router tests (DO binding not exercised on these paths).
const ENV = {
  MCP_API_KEY: "key-cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  AUTH_HMAC_SECRET: "hmac-dddddddddddddddddddddddddddddddddddddddddddddddd",
  OAUTH_ALLOWED_REDIRECT_ORIGINS: "",
  MCP_ALLOW_NO_AUTH: "0",
  MCP_OBJECT: {} as DurableObjectNamespace,
} as Env;

const ctx = { waitUntil() {}, passThroughOnException() {} } as unknown as ExecutionContext;

describe("router", () => {
  it("GET /health -> ok", async () => {
    const res = await worker.fetch(new Request("https://w.example/health"), ENV, ctx);
    expect(res.status).toBe(200);
    expect(await res.text()).toBe("ok");
  });

  it("unknown path -> 404", async () => {
    const res = await worker.fetch(new Request("https://w.example/nope"), ENV, ctx);
    expect(res.status).toBe(404);
  });

  it("authorization-server metadata advertises S256 only", async () => {
    const res = await worker.fetch(
      new Request("https://w.example/.well-known/oauth-authorization-server"), ENV, ctx);
    expect(res.status).toBe(200);
    const meta = await res.json() as any;
    expect(meta.code_challenge_methods_supported).toEqual(["S256"]);
    expect(meta.token_endpoint).toContain("/oauth/token");
  });

  it("protected-resource metadata points at /mcp", async () => {
    const res = await worker.fetch(
      new Request("https://w.example/.well-known/oauth-protected-resource"), ENV, ctx);
    expect(res.status).toBe(200);
    const meta = await res.json() as any;
    expect(meta.resource).toContain("/mcp");
  });

  it("POST /mcp without Bearer -> 401", async () => {
    const res = await worker.fetch(new Request("https://w.example/mcp", { method: "POST" }), ENV, ctx);
    expect(res.status).toBe(401);
    expect(res.headers.get("www-authenticate")).toContain("Bearer");
  });
});
