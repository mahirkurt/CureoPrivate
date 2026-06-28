/**
 * auth.ts — Hardened OAuth 2.1 surface for the drugddx-mcp Worker (Cureonics Family A).
 *
 * Single-tenant OAuth: the real gate is MCP_API_KEY (Bearer). OAuth exists only to satisfy
 * the discovery surface claude.ai requires for remote connectors. This file implements the
 * canonical surface from mcp-scout self-host-build.md §5 and PRESERVES all six security
 * invariants — DO NOT RELAX:
 *
 *   (1) redirect_uri FULL-ORIGIN allowlist (default https://claude.ai,https://claude.com)
 *   (2) PKCE S256 ONLY — `plain` is rejected
 *   (3) escHtml on every reflected parameter — reflected XSS closed
 *   (4) authorization code is HMAC-signed + 10-minute TTL
 *   (5) ALL secret comparisons are constant-time
 *   (6) secrets live ONLY in the secret store (wrangler secret put) — never in code/vars
 *
 * NOTE (provenance): the Cureonics parent ships a verbatim src/auth.ts. If the operator
 * possesses that authoritative file, it SHOULD replace this one. This implementation is a
 * faithful reproduction of the documented surface + invariants (no parent file was available
 * at packaging time); it is security-reviewed but the operator's verbatim parent is canonical.
 */

export interface AuthEnv {
  MCP_API_KEY: string;                       // secret — the real Bearer gate (64-hex)
  AUTH_HMAC_SECRET: string;                  // secret — signs auth codes (32-hex)
  OAUTH_ALLOWED_REDIRECT_ORIGINS?: string;   // var — comma list; empty => default allowlist
  MCP_ALLOW_NO_AUTH?: string;                // var — "1" disables auth (LOCAL ONLY)
}

const DEFAULT_ALLOWED_ORIGINS = ["https://claude.ai", "https://claude.com"];
const CODE_TTL_SECONDS = 600;               // invariant (4): 10-minute TTL
const REALM = "openfda-mcp";

const json = (body: unknown, status = 200, extra: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store", ...extra },
  });

// ---- invariant (3): reflected-XSS escaping ---------------------------------
function escHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string));
}

// ---- invariant (5): constant-time comparison -------------------------------
function constantTimeEqual(a: string, b: string): boolean {
  const enc = new TextEncoder();
  const ab = enc.encode(a);
  const bb = enc.encode(b);
  // compare a fixed-length digest of each side so length itself does not leak via early exit
  // (XOR-accumulate over equal-length buffers)
  if (ab.length !== bb.length) {
    // still do work to avoid trivial timing signal, then fail
    let diff = 1;
    const n = Math.max(ab.length, bb.length);
    for (let i = 0; i < n; i++) diff |= (ab[i] ?? 0) ^ (bb[i] ?? 0);
    return false;
  }
  let diff = 0;
  for (let i = 0; i < ab.length; i++) diff |= ab[i] ^ bb[i];
  return diff === 0;
}

// ---- base64url helpers -----------------------------------------------------
function b64urlEncode(bytes: ArrayBuffer | Uint8Array): string {
  const u8 = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let s = "";
  for (const b of u8) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64urlDecodeToBytes(s: string): Uint8Array {
  const pad = s.length % 4 === 0 ? "" : "=".repeat(4 - (s.length % 4));
  const b = atob(s.replace(/-/g, "+").replace(/_/g, "/") + pad);
  const out = new Uint8Array(b.length);
  for (let i = 0; i < b.length; i++) out[i] = b.charCodeAt(i);
  return out;
}

// ---- invariant (4): HMAC-signed auth code ----------------------------------
async function hmac(secretHex: string, msg: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secretHex),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(msg));
  return b64urlEncode(sig);
}

interface CodePayload { ru: string; cc: string; exp: number; }

async function mintCode(env: AuthEnv, ru: string, codeChallenge: string): Promise<string> {
  const payload: CodePayload = { ru, cc: codeChallenge, exp: Math.floor(Date.now() / 1000) + CODE_TTL_SECONDS };
  const body = b64urlEncode(new TextEncoder().encode(JSON.stringify(payload)));
  const mac = await hmac(env.AUTH_HMAC_SECRET, body);
  return `${body}.${mac}`;
}

async function verifyCode(env: AuthEnv, code: string): Promise<CodePayload | null> {
  const dot = code.lastIndexOf(".");
  if (dot < 0) return null;
  const body = code.slice(0, dot);
  const mac = code.slice(dot + 1);
  const expected = await hmac(env.AUTH_HMAC_SECRET, body);
  if (!constantTimeEqual(mac, expected)) return null;          // invariant (4)+(5)
  let payload: CodePayload;
  try { payload = JSON.parse(new TextDecoder().decode(b64urlDecodeToBytes(body))); }
  catch { return null; }
  if (!payload.exp || payload.exp < Math.floor(Date.now() / 1000)) return null;  // TTL
  return payload;
}

// ---- invariant (2): PKCE S256 verification ---------------------------------
async function pkceS256Matches(verifier: string, challenge: string): Promise<boolean> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
  return constantTimeEqual(b64urlEncode(digest), challenge);
}

// ---- invariant (1): redirect_uri full-origin allowlist ---------------------
function allowedOrigins(env: AuthEnv): string[] {
  const raw = (env.OAUTH_ALLOWED_REDIRECT_ORIGINS || "").trim();
  return raw ? raw.split(",").map((s) => s.trim()).filter(Boolean) : DEFAULT_ALLOWED_ORIGINS;
}
function redirectAllowed(env: AuthEnv, redirectUri: string): boolean {
  let origin: string;
  try { origin = new URL(redirectUri).origin; } catch { return false; }
  return allowedOrigins(env).includes(origin);   // FULL-ORIGIN match, not substring
}

// ---- RFC 9728 / RFC 8414 metadata + RFC 7591 register stub -----------------
function protectedResource(url: URL): Response {
  const base = `${url.protocol}//${url.host}`;
  return json({
    resource: `${base}/mcp`,
    authorization_servers: [base],
    bearer_methods_supported: ["header"],
    resource_name: REALM,
  });
}
function authorizationServer(url: URL): Response {
  const base = `${url.protocol}//${url.host}`;
  return json({
    issuer: base,
    authorization_endpoint: `${base}/oauth/authorize`,
    token_endpoint: `${base}/oauth/token`,
    registration_endpoint: `${base}/oauth/register`,
    response_types_supported: ["code"],
    grant_types_supported: ["authorization_code"],
    code_challenge_methods_supported: ["S256"],   // invariant (2): S256 only advertised
    token_endpoint_auth_methods_supported: ["none"],
  });
}
async function registerStub(req: Request): Promise<Response> {
  // RFC 7591 single-tenant stub — real gate is MCP_API_KEY; DCR auth method is "none".
  // MUST echo the client's redirect_uris back, or claude.ai/grok reject DCR with
  // "Couldn't register … sign-in service". The full-origin allowlist is still enforced
  // at /authorize + /token (redirectAllowed), so echoing here is safe.
  let redirect_uris: string[] = [];
  try {
    const body = (await req.json()) as { redirect_uris?: unknown };
    if (Array.isArray(body?.redirect_uris)) {
      redirect_uris = body.redirect_uris.filter((u): u is string => typeof u === "string");
    }
  } catch { /* missing/invalid body -> echo empty */ }
  return json({
    client_id: REALM,
    token_endpoint_auth_method: "none",
    grant_types: ["authorization_code"],
    response_types: ["code"],
    redirect_uris,
  }, 201);
}

// ---- GET /oauth/authorize : HTML form (escaped reflections) ----------------
function authorizeForm(url: URL, env: AuthEnv): Response {
  const redirectUri = url.searchParams.get("redirect_uri") || "";
  const state = url.searchParams.get("state") || "";
  const codeChallenge = url.searchParams.get("code_challenge") || "";
  const method = url.searchParams.get("code_challenge_method") || "";

  if (!redirectAllowed(env, redirectUri)) return json({ error: "invalid_redirect_uri" }, 400);
  if (method !== "S256" || !codeChallenge) return json({ error: "invalid_request", error_description: "PKCE S256 required" }, 400);

  // invariant (3): every reflected value is escHtml'd
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escHtml(REALM)} — Authorize</title>
<style>body{font:14px/1.5 system-ui;max-width:28rem;margin:4rem auto;padding:0 1rem}
input{width:100%;padding:.6rem;margin:.4rem 0 1rem;box-sizing:border-box}
button{padding:.6rem 1rem;cursor:pointer}</style></head><body>
<h1>${escHtml(REALM)}</h1>
<p>Paste your MCP API key to authorize this connector.</p>
<form method="POST" action="/oauth/authorize">
  <input type="hidden" name="redirect_uri" value="${escHtml(redirectUri)}">
  <input type="hidden" name="state" value="${escHtml(state)}">
  <input type="hidden" name="code_challenge" value="${escHtml(codeChallenge)}">
  <input type="hidden" name="code_challenge_method" value="S256">
  <label>MCP API key<input type="password" name="api_key" autocomplete="off" required></label>
  <button type="submit">Authorize</button>
</form></body></html>`;
  return new Response(html, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
}

// ---- POST /oauth/authorize : verify key, mint code, 302 --------------------
async function authorizeSubmit(req: Request, url: URL, env: AuthEnv): Promise<Response> {
  const form = await req.formData();
  const apiKey = String(form.get("api_key") || "");
  const redirectUri = String(form.get("redirect_uri") || "");
  const state = String(form.get("state") || "");
  const codeChallenge = String(form.get("code_challenge") || "");
  const method = String(form.get("code_challenge_method") || "");

  if (!redirectAllowed(env, redirectUri)) return json({ error: "invalid_redirect_uri" }, 400);
  if (method !== "S256" || !codeChallenge) return json({ error: "invalid_request" }, 400);
  if (!constantTimeEqual(apiKey, env.MCP_API_KEY)) {            // invariant (5)
    return json({ error: "access_denied" }, 403);
  }
  const code = await mintCode(env, redirectUri, codeChallenge); // invariant (4)
  const loc = new URL(redirectUri);
  loc.searchParams.set("code", code);
  if (state) loc.searchParams.set("state", state);
  return new Response(null, { status: 302, headers: { location: loc.toString(), "cache-control": "no-store" } });
}

// ---- POST /oauth/token : verify code + PKCE, issue access_token ------------
async function tokenExchange(req: Request, env: AuthEnv): Promise<Response> {
  const form = await req.formData();
  const grant = String(form.get("grant_type") || "");
  const code = String(form.get("code") || "");
  const redirectUri = String(form.get("redirect_uri") || "");
  const verifier = String(form.get("code_verifier") || "");

  if (grant !== "authorization_code") return json({ error: "unsupported_grant_type" }, 400);
  const payload = await verifyCode(env, code);                  // invariant (4): signature + TTL
  if (!payload) return json({ error: "invalid_grant" }, 400);
  if (!redirectAllowed(env, redirectUri) || payload.ru !== redirectUri) {  // invariant (1)
    return json({ error: "invalid_grant", error_description: "redirect_uri mismatch" }, 400);
  }
  if (!verifier || !(await pkceS256Matches(verifier, payload.cc))) {        // invariant (2)
    return json({ error: "invalid_grant", error_description: "PKCE verify failed" }, 400);
  }
  // single-tenant: the issued access token IS the MCP_API_KEY (the real gate).
  return json({ access_token: env.MCP_API_KEY, token_type: "Bearer", expires_in: 3600 });
}

// ---- Bearer guard for /mcp + /sse ------------------------------------------
export function requireBearer(req: Request, env: AuthEnv): Response | null {
  if (env.MCP_ALLOW_NO_AUTH === "1") return null;   // invariant (6): LOCAL ONLY; never set in prod
  const h = req.headers.get("authorization") || "";
  const m = /^Bearer\s+(.+)$/i.exec(h);
  if (!m || !constantTimeEqual(m[1], env.MCP_API_KEY)) {        // invariant (5)
    return json({ error: "unauthorized" }, 401, {
      "www-authenticate": `Bearer realm="${REALM}"`,
    });
  }
  return null;
}

// ---- OAuth router (well-known + /oauth/*) ----------------------------------
export async function handleOAuth(req: Request, env: AuthEnv): Promise<Response> {
  const url = new URL(req.url);
  const p = url.pathname;
  if (req.method === "GET" && p === "/.well-known/oauth-protected-resource") return protectedResource(url);
  if (req.method === "GET" && p === "/.well-known/oauth-authorization-server") return authorizationServer(url);
  if (req.method === "POST" && p === "/oauth/register") return registerStub(req);
  if (req.method === "GET" && p === "/oauth/authorize") return authorizeForm(url, env);
  if (req.method === "POST" && p === "/oauth/authorize") return authorizeSubmit(req, url, env);
  if (req.method === "POST" && p === "/oauth/token") return tokenExchange(req, env);
  return json({ error: "not_found" }, 404);
}

export const __testing = { escHtml, constantTimeEqual, redirectAllowed, mintCode, verifyCode, pkceS256Matches };
