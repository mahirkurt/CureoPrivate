/**
 * index.ts — anamnesis-mcp Worker entrypoint (Cureonics Family A).
 *
 * Router:
 *   GET  /health                  -> "ok" (liveness; no auth)
 *   GET  /.well-known/oauth-*      -> OAuth discovery metadata (RFC 9728 / RFC 8414)
 *   *    /oauth/*                  -> OAuth authorize/token/register surface
 *   POST /mcp   (Streamable HTTP)  -> Bearer-gated MCP  (requireBearer)
 *   /sse (retired)                 -> 410 + hint (DO SQL write-cap avoidance)
 *
 * Bindings (wrangler.jsonc): AI (Workers AI), VECTORIZE (Vectorize index, 1024-d cosine),
 * DB (D1), MCP_OBJECT (legacy empty DO shell — /mcp is stateless). Tools close over env
 * via createMcpHandler(buildServer(env)).
 */

import { DurableObject } from "cloudflare:workers";
import { createMcpHandler } from "agents/mcp";
import { buildServer, type AnamEnv } from "./server.js";
import { preflight, handleOAuth, requireBearer, type AuthEnv } from "./auth.js";
import { reapExpired } from "./reaper.js";
import { embedOne, EMBED_DIMS, EMBED_MODEL } from "./embed.js";
import pkg from "../package.json";

export interface Env extends AuthEnv, AnamEnv {
  MCP_OBJECT: DurableObjectNamespace;
}

/**
 * Legacy SQLite DO class — exported so wrangler migrations stay valid.
 * It is NOT on the /mcp hot path. Empty shell so a stray wake cannot
 * run McpAgent._ensureSchema against the free-tier SQL write cap.
 * Vectorize + D1 remain the durable stores for RAG/graph data.
 */
export class Anamnesis extends DurableObject<Env> {}

// CORS for browser connectors (preflight() already covers OPTIONS; add headers on responses).
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET,POST,OPTIONS",
  "access-control-allow-headers": "authorization,content-type,mcp-session-id,mcp-protocol-version,last-event-id",
  "access-control-expose-headers": "mcp-session-id,www-authenticate",
  "access-control-max-age": "86400",
};

function withCors(res: Response): Response {
  if (res.status === 101) return res;
  const h = new Headers(res.headers);
  for (const [k, v] of Object.entries(CORS)) h.set(k, v);
  return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
}

/** Probe each dependency independently so a failure names itself instead of hiding behind "ok". */
async function deepHealth(env: Env): Promise<Response> {
  const check = async (fn: () => Promise<unknown>): Promise<string> => {
    try { await fn(); return "ok"; } catch (e: unknown) {
      return `error: ${e instanceof Error ? e.message : String(e)}`.slice(0, 200);
    }
  };
  const d1 = await check(() => env.DB.prepare("SELECT 1 AS ok").first());
  const vectorize = await check(() => env.VECTORIZE.query(new Array(EMBED_DIMS).fill(0), { topK: 1 }));
  const ai = await check(() => embedOne(env, "health"));
  const status = [d1, vectorize, ai].every((v) => v === "ok") ? "ok" : "degraded";
  return new Response(
    JSON.stringify({ status, d1, vectorize, ai, version: pkg.version, embed_model: EMBED_MODEL }, null, 2),
    { status: 200, headers: { "content-type": "application/json" } },
  );
}

export default {
  /**
   * Nightly garbage collection (audit finding A2). Expired scratch used to accumulate forever:
   * D1 grew unbounded and, worse, expired vectors kept occupying Vectorize and stealing slots
   * in the candidate pool, so retrieval recall decayed silently over time.
   */
  async scheduled(event: ScheduledController, env: Env, _ctx: ExecutionContext): Promise<void> {
    // Use the trigger's own timestamp rather than wall-clock: a delayed or replayed run then
    // reaps against the time it was scheduled for, which is also what makes it testable.
    await reapExpired(env, { now: event.scheduledTime });
  },

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
      // Plain liveness stays public and cheap — uptime probes must not need a credential.
      if (url.searchParams.get("deep") !== "1") {
        return withCors(new Response("ok", { status: 200, headers: { "content-type": "text/plain" } }));
      }
      // The DEEP probe touches D1, Vectorize and Workers AI, so it is bearer-gated: it costs
      // real calls and it reports internal topology. Without it a green /health said nothing
      // about whether retrieval could actually run.
      const denied = requireBearer(req, env);
      if (denied) return withCors(denied);
      return withCors(await deepHealth(env));
    }

    if (p.startsWith("/.well-known/oauth") || p.startsWith("/oauth/")) {
      return withCors(await handleOAuth(req, env));
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
      // Stateless Streamable HTTP: fresh McpServer + WorkerTransport per request.
      // sessionIdGenerator unset → no MCP session SQL; Vectorize/D1 remain durable.
      const handler = createMcpHandler(buildServer(env), {
        sessionIdGenerator: undefined,
        enableJsonResponse: true,
      });
      return withCors(await handler(req, env, ctx));
    }

    return withCors(new Response("not found", { status: 404, headers: { "content-type": "text/plain" } }));
  },
};
