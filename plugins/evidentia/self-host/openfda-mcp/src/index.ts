/**
 * index.ts — openfda-mcp Worker entrypoint (Cureonics Family A).
 *
 * Router:
 *   GET  /health                      -> "ok" (liveness; no auth)
 *   GET  /.well-known/oauth-*          -> OAuth discovery metadata (RFC 9728 / RFC 8414)
 *   *    /oauth/*                      -> OAuth authorize/token/register surface
 *   POST /mcp   (Streamable HTTP)      -> Bearer-gated MCP, STATELESS  (requireBearer)
 *   GET  /sse   (retired)              -> Bearer-gated 410 + hint
 *
 * STATELESS TRANSPORT (2026-09-09). This Worker used to serve /mcp through
 * `McpAgent.serve()`, which routes every session into a Durable Object and makes
 * `McpAgent._ensureSchema` write the session tables into DO SQL storage. Measured live:
 * once the account crossed the Durable Objects free-tier storage cap, EVERY `initialize`
 * threw —
 *
 *     Exceeded allowed bytes stored in Durable Objects free tier.
 *     Only writes shrinking your database size are allowed.
 *
 * — surfacing as HTTP 500 / Cloudflare 1101 on six sibling Workers at once. Nothing here
 * ever kept state in the DO (no ctx.storage, no sql): the DO was only the transport. So
 * /mcp now builds a fresh McpServer per request with `sessionIdGenerator: undefined`,
 * exactly as anamnesis-mcp already does, and no DO SQL is written at all.
 *
 * The DO class is still exported (as an EMPTY shell) and still bound as MCP_OBJECT so the
 * wrangler migration history stays valid; an empty shell also means a stray wake cannot
 * re-run _ensureSchema against the cap.
 *
 * CORS: the old McpAgent transport emitted the CORS headers itself, from BELOW the bearer
 * gate. The stateless handler does not, so responses are wrapped here — otherwise browser
 * connectors (claude.ai, ChatGPT web, vscode.dev) would lose them silently.
 */

import { DurableObject } from "cloudflare:workers";
import { createMcpHandler } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools, type OpenFdaEnv } from "./server.js";
import { preflight, handleOAuth, requireBearer, CORS, type AuthEnv } from "./auth.js";
// serverInfo.version is fed from package.json so `initialize` can distinguish deployments.
// Until 2026-08-08 every Worker advertised a hardcoded "1.0.0" that never moved, so the
// handshake could not tell one deploy from another — the audit had to read wrangler output
// instead. Bump package.json on a behaviour change and the wire reflects it.
import pkg from "../package.json";

export interface Env extends AuthEnv, OpenFdaEnv {
  MCP_OBJECT: DurableObjectNamespace;
}

/**
 * Legacy SQLite DO class — exported so wrangler migrations stay valid.
 * NOT on the /mcp hot path. Empty shell so a stray wake cannot run
 * McpAgent._ensureSchema against the free-tier SQL write cap.
 */
export class OpenFda extends DurableObject<Env> {}

/** Fresh server per request; tools close over env (icd11_search needs ICD11_CLIENT_ID/SECRET). */
function buildServer(env: Env): McpServer {
  const server = new McpServer({ name: "openfda-mcp", version: pkg.version });
  registerTools(server, env as unknown as OpenFdaEnv);
  return server;
}

function withCors(res: Response): Response {
  const h = new Headers(res.headers);
  for (const [k, v] of Object.entries(CORS)) h.set(k, v);
  return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
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

    // Prefix-match /sse so leftover clients are bearer-gated (then 410), not DO-routed.
    if (p === "/mcp" || p.startsWith("/sse")) {
      const denied = requireBearer(req, env);   // 401 without a valid Bearer (unless MCP_ALLOW_NO_AUTH=1)
      if (denied) return withCors(denied);
      if (p.startsWith("/sse")) {
        return withCors(
          new Response(
            JSON.stringify({
              error: "sse_retired",
              hint: "Use POST /mcp (Streamable HTTP, stateless). Durable Object SSE hit the free-tier SQL write cap.",
            }),
            { status: 410, headers: { "content-type": "application/json" } },
          ),
        );
      }
      const handler = createMcpHandler(buildServer(env), {
        sessionIdGenerator: undefined,
        enableJsonResponse: true,
      });
      return withCors(await handler(req, env, ctx));
    }

    return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
  },
};
