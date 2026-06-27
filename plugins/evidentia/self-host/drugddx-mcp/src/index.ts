/**
 * index.ts — drugddx-mcp Worker entrypoint (Cureonics Family A).
 *
 * Router:
 *   GET  /health                      -> "ok" (liveness; no auth)
 *   GET  /.well-known/oauth-*          -> OAuth discovery metadata (RFC 9728 / RFC 8414)
 *   *    /oauth/*                      -> OAuth authorize/token/register surface
 *   POST /mcp   (Streamable HTTP)      -> Bearer-gated MCP  (requireBearer)
 *   GET  /sse   (legacy SSE)           -> Bearer-gated MCP  (requireBearer)
 *
 * The Durable Object class `DrugDdx` is exported and bound as MCP_OBJECT in wrangler.jsonc.
 */

import { McpAgent } from "agents/mcp";
import { buildServer } from "./server.js";
import { handleOAuth, requireBearer, type AuthEnv } from "./auth.js";

export interface Env extends AuthEnv {
  MCP_OBJECT: DurableObjectNamespace;
}

export class DrugDdx extends McpAgent<Env> {
  server = buildServer();
  async init(): Promise<void> {
    // tools are registered in buildServer(); nothing stateful to hydrate.
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
        ? DrugDdx.serveSSE("/sse").fetch(req, env, ctx)
        : DrugDdx.serve("/mcp").fetch(req, env, ctx);
    }

    return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
  },
};
