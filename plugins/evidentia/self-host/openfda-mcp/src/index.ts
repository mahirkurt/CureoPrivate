/**
 * index.ts — openfda-mcp Worker entrypoint (Cureonics Family A).
 *
 * Router:
 *   GET  /health                      -> "ok" (liveness; no auth)
 *   GET  /.well-known/oauth-*          -> OAuth discovery metadata (RFC 9728 / RFC 8414)
 *   *    /oauth/*                      -> OAuth authorize/token/register surface
 *   POST /mcp   (Streamable HTTP)      -> Bearer-gated MCP  (requireBearer)
 *   GET  /sse   (legacy SSE)           -> Bearer-gated MCP  (requireBearer)
 *
 * The Durable Object class `OpenFda` is exported and bound as MCP_OBJECT in wrangler.jsonc.
 */

import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools, type OpenFdaEnv } from "./server.js";
import { preflight, handleOAuth, requireBearer, type AuthEnv } from "./auth.js";
// serverInfo.version is fed from package.json so `initialize` can distinguish deployments.
// Until 2026-08-08 every Worker advertised a hardcoded "1.0.0" that never moved, so the
// handshake could not tell one deploy from another — the audit had to read wrangler output
// instead. Bump package.json on a behaviour change and the wire reflects it.
import pkg from "../package.json";

export interface Env extends AuthEnv, OpenFdaEnv {
  MCP_OBJECT: DurableObjectNamespace;
}

export class OpenFda extends McpAgent<Env> {
  server = new McpServer({ name: "openfda-mcp", version: pkg.version });
  async init(): Promise<void> {
    // icd11_search needs ICD11_CLIENT_ID/SECRET from env -> register here where this.env exists.
    registerTools(this.server, this.env as unknown as OpenFdaEnv);
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
      const denied = requireBearer(req, env);   // 401 without a valid Bearer (unless MCP_ALLOW_NO_AUTH=1)
      if (denied) return denied;
      return p === "/sse"
        ? OpenFda.serveSSE("/sse").fetch(req, env, ctx)
        : OpenFda.serve("/mcp").fetch(req, env, ctx);
    }

    return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
  },
};
