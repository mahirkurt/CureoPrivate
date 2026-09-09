/**
 * index.ts — ema-mcp Worker entrypoint (Cureonics self-host, evidentia Tier-O).
 *
 * Router:
 *   GET  /health                      -> "ok" (liveness; no auth)
 *   GET  /.well-known/oauth-*          -> OAuth discovery metadata (RFC 9728 / RFC 8414); 404 when KEYLESS
 *   *    /oauth/*                      -> OAuth authorize/token/register surface; 404 when KEYLESS
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

import { DurableObject } from "cloudflare:workers";
import { createMcpHandler } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools } from "./server.js";
import { preflight, handleOAuth, requireBearer, type AuthEnv, CORS } from "./auth.js";
// serverInfo.version is fed from package.json so `initialize` can distinguish deployments.
// Until 2026-08-08 every Worker advertised a hardcoded "1.0.0" that never moved, so the
// handshake could not tell one deploy from another — the audit had to read wrangler output
// instead. Bump package.json on a behaviour change and the wire reflects it.
import pkg from "../package.json";

export interface Env extends AuthEnv {
  MCP_OBJECT: DurableObjectNamespace;
}

/**
 * STATELESS TRANSPORT (2026-09-09). /mcp used to run through `McpAgent.serve()`, which routes
 * every session into a Durable Object and makes `McpAgent._ensureSchema` write session tables
 * into DO SQL storage. Measured live: once the account crossed the Durable Objects free-tier
 * storage cap, EVERY `initialize` threw —
 *   "Exceeded allowed bytes stored in Durable Objects free tier."
 * — surfacing as HTTP 500 / Cloudflare 1101 on six sibling Workers at once. Nothing here ever
 * kept state in the DO (no ctx.storage, no sql): the DO was only the transport. /mcp now builds
 * a fresh McpServer per request with `sessionIdGenerator: undefined`, exactly as anamnesis-mcp
 * already does. The DO class stays exported as an EMPTY shell so migration history stays valid.
 *
 * CORS: the old McpAgent transport emitted the CORS headers itself, from BELOW the bearer gate.
 * The stateless handler does not, so responses are wrapped here.
 */
export class Ema extends DurableObject<Env> {}

/** Fresh server per request — no DO session SQL. */
function mcpServerFor(env: Env): McpServer {
  const server = new McpServer({ name: "ema-mcp", version: pkg.version });
  registerTools(server);
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

    // In KEYLESS mode the gate is off (requireBearer returns null), so advertising an OAuth
    // surface is a lie that BREAKS discovery-driven clients rather than helping them: they read
    // the RFC 9728 PRM, conclude the resource is protected, and run the dance — whose authorize
    // form asks for a connector key that CANNOT exist, because MCP_API_KEY is unset in a keyless
    // deploy (`wrangler secret list` -> []) and every submission 403s. Measured 2026-08-08:
    // Codex (`codex mcp login`) prompted for a key against this Worker for exactly this reason,
    // while an anonymous — or garbage-Bearer — `initialize` returned 200. Public mode must
    // therefore 404 the whole OAuth surface, so clients see an open server and just connect.
    if (p.startsWith("/.well-known/oauth") || p.startsWith("/oauth/")) {
      if (env.MCP_ALLOW_NO_AUTH === "1") {
        return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
      }
      return handleOAuth(req, env);
    }

    if (p === "/mcp" || p.startsWith("/sse")) {
      const denied = requireBearer(req, env);   // null when MCP_ALLOW_NO_AUTH=1 (keyless)
      if (denied) return withCors(denied);
      if (p.startsWith("/sse")) {
        return withCors(new Response(JSON.stringify({ error: "sse_retired",
          hint: "Use POST /mcp (Streamable HTTP, stateless). Durable Object SSE hit the free-tier SQL write cap." }),
          { status: 410, headers: { "content-type": "application/json" } }));
      }
      const handler = createMcpHandler(mcpServerFor(env), { sessionIdGenerator: undefined, enableJsonResponse: true });
      return withCors(await handler(req, env, ctx));
    }

    return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
  },
};
