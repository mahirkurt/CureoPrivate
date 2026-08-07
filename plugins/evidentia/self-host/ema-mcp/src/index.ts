/**
 * index.ts — ema-mcp Worker entrypoint (Cureonics self-host, evidentia Tier-O).
 *
 * Router:
 *   GET  /health                      -> "ok" (liveness; no auth)
 *   GET  /.well-known/oauth-*          -> OAuth discovery metadata (RFC 9728 / RFC 8414)
 *   *    /oauth/*                      -> OAuth authorize/token/register surface
 *   POST /mcp   (Streamable HTTP)      -> MCP  (requireBearer — but KEYLESS: MCP_ALLOW_NO_AUTH=1)
 *   GET  /sse   (legacy SSE)           -> MCP  (requireBearer)
 *
 * KEYLESS by design (drugddx precedent): serves a BAKED public dataset (EMA EPAR medicines, built
 * from the authless EMA XLSX by scripts/build_corpus.mjs) — no upstream call at runtime, no
 * server-side secret, no confused-deputy surface. The hardened OAuth layer is retained (additive)
 * for claude.ai/ChatGPT connector flows. Set MCP_ALLOW_NO_AUTH="0" to re-gate.
 *
 * The Durable Object class `Ema` is exported and bound as MCP_OBJECT in wrangler.jsonc.
 */

import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools } from "./server.js";
import { preflight, handleOAuth, requireBearer, type AuthEnv } from "./auth.js";

export interface Env extends AuthEnv {
  MCP_OBJECT: DurableObjectNamespace;
}

export class Ema extends McpAgent<Env> {
  server = new McpServer({ name: "ema-mcp", version: "1.0.0" });
  async init(): Promise<void> {
    registerTools(this.server);
  }
}

export default {
  async fetch(req: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(req.url);
    const p = url.pathname;

    // CORS preflight is answered FIRST — ahead of the bearer gate. A preflight carries no
    // Authorization (browsers never attach credentials to OPTIONS), so gating it returns 401
    // and the browser abandons the request before it is ever made. Measured 2026-08-07: all
    // three gated Workers rejected `OPTIONS /mcp` from https://claude.ai with a bare 401 and
    // no Access-Control-* headers, making them un-addable as browser connectors.
    const pf = preflight(req);
    if (pf) return pf;

    if (p === "/health") {
      return new Response("ok", { status: 200, headers: { "content-type": "text/plain" } });
    }

    if (p.startsWith("/.well-known/oauth") || p.startsWith("/oauth/")) {
      return handleOAuth(req, env);
    }

    if (p === "/mcp" || p === "/sse") {
      const denied = requireBearer(req, env);   // null when MCP_ALLOW_NO_AUTH=1 (keyless)
      if (denied) return denied;
      return p === "/sse"
        ? Ema.serveSSE("/sse").fetch(req, env, ctx)
        : Ema.serve("/mcp").fetch(req, env, ctx);
    }

    return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
  },
};
