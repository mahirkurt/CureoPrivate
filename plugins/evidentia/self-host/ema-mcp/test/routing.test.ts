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

  // RFC 9728 path-insertion — ChatGPT requests the PRM at .../oauth-protected-resource/mcp
  it("protected-resource metadata is also served at the path-inserted URL", async () => {
    const res = await worker.fetch(
      new Request("https://w.example/.well-known/oauth-protected-resource/mcp"), ENV, ctx);
    expect(res.status).toBe(200);
    const meta = await res.json() as any;
    expect(meta.resource).toBe("https://w.example/mcp");
    expect(meta.authorization_servers).toEqual(["https://w.example"]);
  });

  it("401 WWW-Authenticate advertises resource_metadata (RFC 9728)", async () => {
    const res = await worker.fetch(new Request("https://w.example/mcp", { method: "POST" }), ENV, ctx);
    expect(res.status).toBe(401);
    const wa = res.headers.get("www-authenticate") || "";
    expect(wa).toContain('resource_metadata="https://w.example/.well-known/oauth-protected-resource/mcp"');
  });
});

// The production deploy is KEYLESS (wrangler.jsonc vars: MCP_ALLOW_NO_AUTH="1"). An open server
// that still answers OAuth discovery tells clients "I am protected", sending them into a dance
// whose authorize form demands a key that cannot exist — MCP_API_KEY is unset in this mode, so
// every submission 403s. The whole OAuth surface must disappear, not merely be bypassable.
describe("router — KEYLESS mode (MCP_ALLOW_NO_AUTH=1)", () => {
  const OPEN = { ...ENV, MCP_ALLOW_NO_AUTH: "1" } as Env;
  const get = (p: string) => worker.fetch(new Request(`https://w.example${p}`), OPEN, ctx);

  it("protected-resource metadata is NOT advertised", async () => {
    expect((await get("/.well-known/oauth-protected-resource")).status).toBe(404);
  });

  it("path-inserted protected-resource metadata is NOT advertised", async () => {
    expect((await get("/.well-known/oauth-protected-resource/mcp")).status).toBe(404);
  });

  it("authorization-server metadata is NOT advertised", async () => {
    expect((await get("/.well-known/oauth-authorization-server")).status).toBe(404);
  });

  it("the authorize form — which prompts for a connector key — does not render", async () => {
    const res = await get("/oauth/authorize?response_type=code&client_id=ema-mcp");
    expect(res.status).toBe(404);
    expect(await res.text()).not.toContain("api_key");
  });

  it("dynamic client registration does not succeed", async () => {
    const res = await worker.fetch(
      new Request("https://w.example/oauth/register", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ client_name: "codex", redirect_uris: ["http://127.0.0.1:1455/cb"] }),
      }), OPEN, ctx);
    expect(res.status).toBe(404);
  });

  it("token exchange does not succeed", async () => {
    const res = await worker.fetch(
      new Request("https://w.example/oauth/token", { method: "POST" }), OPEN, ctx);
    expect(res.status).toBe(404);
  });

  it("/health stays public", async () => {
    expect((await get("/health")).status).toBe(200);
  });
});
