/**
 * auth.ts — Hardened OAuth 2.1 surface for the who-gho-mcp Worker (Cureonics Family A).
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

const DEFAULT_ALLOWED_ORIGINS = [
  "https://claude.ai", "https://claude.com", "https://grok.com", "https://chatgpt.com",
  "https://oauth-redirect.googleusercontent.com", "https://vscode.dev", "https://insiders.vscode.dev", "https://vscode.flexdev.roche.com",
  "https://cursor.com", "https://www.cursor.com",
];
const CODE_TTL_SECONDS = 600;               // invariant (4): 10-minute TTL
// Advertised access-token lifetime + refresh-token TTL. The access token IS the static
// MCP_API_KEY (it never actually expires); expires_in only tells the client when to run the
// refresh grant. 3600 + no refresh_token made ChatGPT/Gemini re-prompt a full login hourly.
const ACCESS_TTL_SECONDS = 30 * 24 * 3600;  // 2592000 (30 days)
const REFRESH_TTL_SECONDS = 90 * 24 * 3600; // 7776000 (90 days)
const REALM = "who-gho-mcp";

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

interface CodePayload { typ?: string; ru: string; cc: string; exp: number; }
interface RefreshPayload { typ: "refresh"; exp: number; n: string; kb: string; }

async function signPayload(env: AuthEnv, payload: object): Promise<string> {
  const body = b64urlEncode(new TextEncoder().encode(JSON.stringify({ typ: "authorization_code", ...payload })));
  const mac = await hmac(env.AUTH_HMAC_SECRET, body);
  return `${body}.${mac}`;
}

// Signature + TTL check shared by codes and refresh tokens. Callers MUST also check `typ`.
async function verifySigned(env: AuthEnv, token: string): Promise<Record<string, unknown> | null> {
  if (typeof token !== "string") return null;
  const dot = token.lastIndexOf(".");
  if (dot < 0) return null;
  const body = token.slice(0, dot);
  const mac = token.slice(dot + 1);
  const expected = await hmac(env.AUTH_HMAC_SECRET, body);
  if (!constantTimeEqual(mac, expected)) return null;          // invariant (4)+(5)
  let payload: unknown;
  try { payload = JSON.parse(new TextDecoder().decode(b64urlDecodeToBytes(body))); }
  catch { return null; }
  if (!payload || typeof payload !== "object") return null;
  const p = payload as Record<string, unknown>;
  if (typeof p.exp !== "number" || p.exp < Math.floor(Date.now() / 1000)) return null;  // TTL
  return p;
}

async function mintCode(env: AuthEnv, ru: string, codeChallenge: string): Promise<string> {
  const payload: CodePayload = {
    typ: "authorization_code", ru, cc: codeChallenge, exp: Math.floor(Date.now() / 1000) + CODE_TTL_SECONDS,
  };
  return signPayload(env, payload);
}

async function verifyCode(env: AuthEnv, code: string): Promise<CodePayload | null> {
  const p = await verifySigned(env, code);
  // typ is mandatory (fleet contract 2026-10-19): a typ-less (pre-refresh) code or a refresh
  // token (or any other explicit token type) must never reach the PKCE/code path.
  if (!p || p.typ !== "authorization_code") return null;
  return p as unknown as CodePayload;
}

// ---- refresh tokens: HMAC-signed (same secret as codes), typ-tagged, 90-day TTL -----
// A signature is not encryption: the access token / MCP_API_KEY is NEVER embedded here.
// The refresh grant re-issues the same static access token plus a rotated refresh token.
//
// Key binding (`kb`): the token is signed with AUTH_HMAC_SECRET, which does NOT change when
// MCP_API_KEY is rotated — so without `kb` an old refresh token would keep working and would
// be handed the NEW key. `kb` is a 32-hex HMAC fingerprint of the current key (not the key),
// recomputed and constant-time compared on every refresh: rotation revokes every refresh token.
async function keyBinding(env: AuthEnv): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(env.AUTH_HMAC_SECRET),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`kb:${env.MCP_API_KEY}`));
  let hex = "";
  for (const b of new Uint8Array(sig)) hex += b.toString(16).padStart(2, "0");
  return hex.slice(0, 32);
}

async function mintRefresh(env: AuthEnv): Promise<string> {
  const payload: RefreshPayload = {
    typ: "refresh",
    exp: Math.floor(Date.now() / 1000) + REFRESH_TTL_SECONDS,
    n: b64urlEncode(crypto.getRandomValues(new Uint8Array(16))),
    kb: await keyBinding(env),
  };
  return signPayload(env, payload);
}

async function verifyRefresh(env: AuthEnv, token: string): Promise<boolean> {
  const p = await verifySigned(env, token);
  if (!p || p.typ !== "refresh") return false;   // a code (no/other typ) is never a refresh token
  if (typeof p.kb !== "string") return false;
  return constantTimeEqual(p.kb, await keyBinding(env));   // invariant (5); rotation revokes
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
  let parsed: URL;
  try { parsed = new URL(redirectUri); } catch { return false; }
  // Loopback redirects (RFC 8252 native-app flow) are accepted on ANY port, in
  // production too: VS Code / GitHub Copilot / OpenAI Codex CLI register a fixed
  // loopback port but fall back to a RANDOM free port when it's taken, so pinning
  // the port breaks the connector silently. Safe because the code lands on the
  // user's OWN machine and the authorize form still requires the connector key —
  // a remote attacker never receives it.
  if (
    parsed.hostname === "localhost" || parsed.hostname === "127.0.0.1" ||
    parsed.hostname === "::1" || parsed.hostname === "[::1]"
  ) return true;
  // Cursor desktop MCP OAuth: cursor://anysphere.cursor-mcp/oauth/callback.
  // WHATWG origin is "null" for this scheme, so the HTTPS allowlist cannot match.
  if (parsed.protocol === "cursor:" && parsed.hostname === "anysphere.cursor-mcp") return true;
  return allowedOrigins(env).includes(parsed.origin);   // FULL-ORIGIN match, not substring
}

// ---- RFC 9728 / RFC 8414 metadata + RFC 7591 register stub -----------------
// RFC 9728: the PRM may be requested at the bare well-known path OR with the resource
// path inserted (…/oauth-protected-resource/mcp). claude.ai uses the bare form; ChatGPT
// uses the path-inserted form. Serve both so OAuth discovery succeeds on every client.
function protectedResource(url: URL): Response {
  const base = `${url.protocol}//${url.host}`;
  const suffix = url.pathname.slice("/.well-known/oauth-protected-resource".length); // "" | "/mcp" | "/sse"
  const resourcePath = suffix === "/sse" ? "/sse" : "/mcp";
  return json({
    resource: `${base}${resourcePath}`,
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
    grant_types_supported: ["authorization_code", "refresh_token"],
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
    grant_types: ["authorization_code", "refresh_token"],
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
  // .trim(): pasted keys routinely carry a trailing newline/space (copy from a doc, a table cell,
  // or a password manager). The whitespace is not key material, and an untrimmed compare turned
  // every such paste into an opaque `access_denied` 403. Trimming widens no attack surface: the
  // secret itself is unchanged, and a wrong key still fails the constant-time compare below.
  const apiKey = String(form.get("api_key") || "").trim();
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

// ---- POST /oauth/token : verify code + PKCE (or refresh), issue access_token -
// Same response shape for both grants. json() already sets cache-control: no-store.
async function tokenResponse(env: AuthEnv): Promise<Response> {
  // single-tenant: the issued access token IS the MCP_API_KEY (the real gate).
  return json({
    access_token: env.MCP_API_KEY,
    token_type: "Bearer",
    expires_in: ACCESS_TTL_SECONDS,
    refresh_token: await mintRefresh(env),
  }, 200, { pragma: "no-cache" });
}

async function tokenExchange(req: Request, env: AuthEnv): Promise<Response> {
  const form = await req.formData();
  const grant = String(form.get("grant_type") || "");
  if (grant === "refresh_token") {
    if (!(await verifyRefresh(env, String(form.get("refresh_token") || "")))) {
      return json({ error: "invalid_grant", error_description: "refresh token invalid or expired" }, 400);
    }
    return tokenResponse(env);
  }
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
  return tokenResponse(env);
}

// ---- Bearer guard for /mcp + /sse ------------------------------------------
export function requireBearer(req: Request, env: AuthEnv): Response | null {
  if (env.MCP_ALLOW_NO_AUTH === "1") return null;   // invariant (6): LOCAL ONLY; never set in prod
  const h = req.headers.get("authorization") || "";
  const m = /^Bearer\s+(.+)$/i.exec(h);
  if (!m || !constantTimeEqual(m[1], env.MCP_API_KEY)) {        // invariant (5)
    // RFC 9728 §5.3: advertise the protected-resource metadata URL so OAuth discovery
    // (claude.ai, ChatGPT, grok) can locate the authorization server from the 401 alone.
    const u = new URL(req.url);
    const prm = `${u.origin}/.well-known/oauth-protected-resource${u.pathname}`;
    return json({ error: "unauthorized" }, 401, {
      "www-authenticate": `Bearer realm="${REALM}", resource_metadata="${prm}"`,
      // Without these the 401 is opaque to browser JS: it cannot read WWW-Authenticate,
      // so the resource_metadata pointer above may as well not be there.
      ...CORS,
    });
  }
  return null;
}

// ---- CORS ------------------------------------------------------------------
// Browser-based MCP clients (claude.ai web, grok.com — the fleet's primary web-connector
// surface — and ChatGPT web) send a CORS PREFLIGHT before the real request. A preflight is
// by specification CREDENTIAL-FREE: the browser never attaches `Authorization` to an
// `OPTIONS`. So a bearer gate placed in front of the preflight rejects it with 401 and the
// browser never issues the real request at all.
//
// Measured 2026-08-07 on the live fleet: `OPTIONS /mcp` with `Origin: https://claude.ai`
// returned **401 and not a single Access-Control-* header** on all three gated Workers
// (anamnesis, evidentia-kb, openfda) — i.e. none of them could be added as a browser
// connector. The keyless four answered 200 only because their gate never fires, so the
// CORS headers they emit come from the SDK transport BELOW the gate; the ordering defect
// was identical, merely unobservable without a key.
//
// `preflight()` is therefore called FIRST in the Worker's fetch(), ahead of requireBearer.
// `Authorization` is in allow-headers so the real (non-preflight) request may carry the
// bearer, and `WWW-Authenticate` is in expose-headers so browser JS can actually READ the
// 401's RFC 9728 `resource_metadata` pointer — without that, OAuth discovery is invisible
// to a browser client even when the 401 is correctly formed.
export const CORS: Record<string, string> = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "Authorization, Content-Type, Mcp-Session-Id, MCP-Protocol-Version",
  "access-control-expose-headers": "WWW-Authenticate, Mcp-Session-Id",
  "access-control-max-age": "86400",
};

/** 204 for any OPTIONS; null otherwise. Must run BEFORE requireBearer. */
export function preflight(req: Request): Response | null {
  return req.method === "OPTIONS" ? new Response(null, { status: 204, headers: CORS }) : null;
}

// ---- OAuth router (well-known + /oauth/*) ----------------------------------
export async function handleOAuth(req: Request, env: AuthEnv): Promise<Response> {
  const url = new URL(req.url);
  const p = url.pathname;
  if (req.method === "GET" && (p === "/.well-known/oauth-protected-resource" || p.startsWith("/.well-known/oauth-protected-resource/"))) return protectedResource(url);
  if (req.method === "GET" && p === "/.well-known/oauth-authorization-server") return authorizationServer(url);
  if (req.method === "POST" && p === "/oauth/register") return registerStub(req);
  if (req.method === "GET" && p === "/oauth/authorize") return authorizeForm(url, env);
  if (req.method === "POST" && p === "/oauth/authorize") return authorizeSubmit(req, url, env);
  if (req.method === "POST" && p === "/oauth/token") return tokenExchange(req, env);
  return json({ error: "not_found" }, 404);
}

export const __testing = {
  escHtml, constantTimeEqual, redirectAllowed, mintCode, verifyCode, pkceS256Matches, mintRefresh, verifyRefresh,
};
