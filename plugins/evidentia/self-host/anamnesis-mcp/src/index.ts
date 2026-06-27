/**
 * index.ts — anamnesis-mcp Worker entrypoint (Cureonics Family A).
 *
 * Router:
 *   GET  /health                  -> "ok" (liveness; no auth)
 *   GET  /.well-known/oauth-*      -> OAuth discovery metadata (RFC 9728 / RFC 8414)
 *   *    /oauth/*                  -> OAuth authorize/token/register surface
 *   POST /mcp   (Streamable HTTP)  -> Bearer-gated MCP  (requireBearer)
 *   GET  /sse   (legacy SSE)       -> Bearer-gated MCP  (requireBearer)
 *
 * Bindings (wrangler.jsonc): AI (Workers AI), VECTORIZE (Vectorize index, 1024-d cosine),
 * DB (D1), MCP_OBJECT (Durable Object -> Anamnesis). Tools are registered in init() so they
 * close over this.env (the canonical Cloudflare McpAgent pattern when tools need bindings).
 */

import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools, type AnamEnv } from "./server.js";
import { handleOAuth, requireBearer, type AuthEnv } from "./auth.js";

export interface Env extends AuthEnv, AnamEnv {
  MCP_OBJECT: DurableObjectNamespace;
}

export class Anamnesis extends McpAgent<Env> {
  server = new McpServer({ name: "anamnesis-mcp", version: "1.0.0" });

  async init(): Promise<void> {
    // tools need bindings (AI/VECTORIZE/DB) -> register here where this.env is available
    registerTools(this.server, this.env as unknown as AnamEnv);
  }
}

export default {
  async fetch(req: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(req.url);
    const p = url.pathname;

    if (p === "/health") {
      return new Response("ok", { status: 200, headers: { "content-type": "text/plain" } });
    }

    if (p.startsWith("/.well-known/oauth") || p.startsWith("/oauth/")) {
      return handleOAuth(req, env);
    }

    if (p === "/mcp" || p === "/sse") {
      const denied = requireBearer(req, env);   // 401 without a valid Bearer (unless MCP_ALLOW_NO_AUTH=1)
      if (denied) return denied;
      return p === "/sse"
        ? Anamnesis.serveSSE("/sse").fetch(req, env, ctx)
        : Anamnesis.serve("/mcp").fetch(req, env, ctx);
    }

    return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
  },
};
