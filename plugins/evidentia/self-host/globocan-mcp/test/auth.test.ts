import { describe, it, expect } from "vitest";
import { handleOAuth, requireBearer, preflight, __testing, type AuthEnv } from "../src/auth.js";

const { escHtml, constantTimeEqual, redirectAllowed, mintCode, verifyCode, pkceS256Matches } = __testing;

const ENV: AuthEnv = {
  MCP_API_KEY: "key-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  AUTH_HMAC_SECRET: "hmac-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  OAUTH_ALLOWED_REDIRECT_ORIGINS: "",
  MCP_ALLOW_NO_AUTH: "0",
};

// Helper: a valid PKCE pair
async function pkcePair(verifier: string): Promise<string> {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
  let s = "";
  for (const b of new Uint8Array(d)) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

describe("invariant 3 - reflected-XSS escaping", () => {
  it("escapes HTML metacharacters", () => {
    expect(escHtml(`<script>"&'`)).toBe("&lt;script&gt;&quot;&amp;&#39;");
  });
});

describe("invariant 5 - constant-time comparison", () => {
  it("true for equal, false for unequal", () => {
    expect(constantTimeEqual("abc", "abc")).toBe(true);
    expect(constantTimeEqual("abc", "abd")).toBe(false);
    expect(constantTimeEqual("abc", "abcd")).toBe(false);
  });
});

describe("invariant 1 - redirect_uri full-origin allowlist", () => {
  it("accepts default claude origins, rejects others & substring tricks", () => {
    expect(redirectAllowed(ENV, "https://claude.ai/callback")).toBe(true);
    expect(redirectAllowed(ENV, "https://claude.com/x")).toBe(true);
    expect(redirectAllowed(ENV, "https://claude.ai.evil.com/cb")).toBe(false);
    expect(redirectAllowed(ENV, "https://evil.com/claude.ai")).toBe(false);
    expect(redirectAllowed(ENV, "not-a-url")).toBe(false);
  });
  it("honors a custom origin list", () => {
    const e = { ...ENV, OAUTH_ALLOWED_REDIRECT_ORIGINS: "https://example.org" };
    expect(redirectAllowed(e, "https://example.org/cb")).toBe(true);
    expect(redirectAllowed(e, "https://claude.ai/cb")).toBe(false);
  });
});

describe("invariant 4 - HMAC-signed auth code + TTL", () => {
  it("mints a code that verifies and carries the payload", async () => {
    const ch = await pkcePair("verifier-123");
    const code = await mintCode(ENV, "https://claude.ai/cb", ch);
    const p = await verifyCode(ENV, code);
    expect(p).not.toBeNull();
    expect(p!.ru).toBe("https://claude.ai/cb");
    expect(p!.cc).toBe(ch);
  });
  it("rejects a tampered code (bad signature)", async () => {
    const ch = await pkcePair("v");
    const code = await mintCode(ENV, "https://claude.ai/cb", ch);
    const tampered = code.slice(0, -2) + (code.endsWith("aa") ? "bb" : "aa");
    expect(await verifyCode(ENV, tampered)).toBeNull();
  });
  it("rejects an expired code", async () => {
    // forge an expired payload signed with the real secret
    const past = { ru: "https://claude.ai/cb", cc: "x", exp: Math.floor(Date.now() / 1000) - 10 };
    const body = btoa(JSON.stringify(past)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(ENV.AUTH_HMAC_SECRET),
      { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
    const sig = await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(body));
    let s = ""; for (const b of new Uint8Array(sig)) s += String.fromCharCode(b);
    const mac = btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    expect(await verifyCode(ENV, `${body}.${mac}`)).toBeNull();
  });
});

describe("invariant 2 - PKCE S256 only", () => {
  it("verifier matching the S256 challenge passes", async () => {
    const ch = await pkcePair("the-verifier");
    expect(await pkceS256Matches("the-verifier", ch)).toBe(true);
    expect(await pkceS256Matches("wrong-verifier", ch)).toBe(false);
  });
  it("GET /oauth/authorize rejects non-S256 method", async () => {
    const url = "https://w.example/oauth/authorize?redirect_uri=" +
      encodeURIComponent("https://claude.ai/cb") + "&code_challenge=abc&code_challenge_method=plain";
    const res = await handleOAuth(new Request(url), ENV);
    expect(res.status).toBe(400);
  });
});

describe("token endpoint - full PKCE round trip", () => {
  it("issues a Bearer token for a valid code + verifier, rejects a wrong verifier", async () => {
    const verifier = "round-trip-verifier-xyz";
    const ch = await pkcePair(verifier);
    const code = await mintCode(ENV, "https://claude.ai/cb", ch);

    const ok = await handleOAuth(new Request("https://w.example/oauth/token", {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code", code, redirect_uri: "https://claude.ai/cb", code_verifier: verifier,
      }),
    }), ENV);
    expect(ok.status).toBe(200);
    const body = await ok.json() as any;
    expect(body.token_type).toBe("Bearer");
    expect(body.access_token).toBe(ENV.MCP_API_KEY);

    const bad = await handleOAuth(new Request("https://w.example/oauth/token", {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code", code, redirect_uri: "https://claude.ai/cb", code_verifier: "WRONG",
      }),
    }), ENV);
    expect(bad.status).toBe(400);
  });
});

describe("Bearer guard", () => {
  it("401 without Bearer; passes with the right key", () => {
    const noAuth = requireBearer(new Request("https://w.example/mcp", { method: "POST" }), ENV);
    expect(noAuth).not.toBeNull();
    expect(noAuth!.status).toBe(401);

    const good = requireBearer(new Request("https://w.example/mcp", {
      method: "POST", headers: { authorization: `Bearer ${ENV.MCP_API_KEY}` },
    }), ENV);
    expect(good).toBeNull();
  });
  it("MCP_ALLOW_NO_AUTH=1 bypasses (local only)", () => {
    const e = { ...ENV, MCP_ALLOW_NO_AUTH: "1" };
    expect(requireBearer(new Request("https://w.example/mcp"), e)).toBeNull();
  });
});

describe("RFC 9728 - OAuth discovery surface (claude.ai / ChatGPT / grok)", () => {
  it("serves protected-resource metadata at the bare well-known path", async () => {
    const res = await handleOAuth(
      new Request("https://w.example/.well-known/oauth-protected-resource"), ENV);
    expect(res.status).toBe(200);
    const meta = await res.json() as any;
    expect(meta.resource).toBe("https://w.example/mcp");
    expect(meta.authorization_servers).toEqual(["https://w.example"]);
  });

  it("also serves it at the path-inserted URL ChatGPT requests (.../oauth-protected-resource/mcp)", async () => {
    const res = await handleOAuth(
      new Request("https://w.example/.well-known/oauth-protected-resource/mcp"), ENV);
    expect(res.status).toBe(200);
    const meta = await res.json() as any;
    expect(meta.resource).toBe("https://w.example/mcp");
    expect(meta.authorization_servers).toEqual(["https://w.example"]);
  });

  it("401 WWW-Authenticate advertises resource_metadata pointing at the PRM", () => {
    const res = requireBearer(new Request("https://w.example/mcp", { method: "POST" }), ENV);
    expect(res).not.toBeNull();
    const wa = res!.headers.get("www-authenticate") || "";
    expect(wa).toContain("Bearer realm=");
    expect(wa).toContain('resource_metadata="https://w.example/.well-known/oauth-protected-resource/mcp"');
  });
});

describe("CORS preflight (browser connector surface)", () => {
  // Regression for the 2026-08-07 measurement: `OPTIONS /mcp` with `Origin: https://claude.ai`
  // returned a bare 401 with ZERO Access-Control-* headers on every gated Worker, so browser
  // clients (claude.ai web, grok.com, ChatGPT web) failed preflight and could never reach /mcp.
  // Root cause: no CORS layer existed and requireBearer ran first — but a preflight is
  // credential-free by specification, so it can never satisfy a bearer gate.
  it("answers OPTIONS with 204 and never consults the bearer gate", () => {
    const r = preflight(new Request("https://w.example/mcp", {
      method: "OPTIONS",
      headers: { origin: "https://claude.ai", "access-control-request-method": "POST" },
    }));
    expect(r).not.toBeNull();
    expect(r!.status).toBe(204);
    expect(r!.headers.get("access-control-allow-origin")).toBe("*");
  });

  it("allows Authorization on the real request, else the bearer can never be sent", () => {
    const r = preflight(new Request("https://w.example/mcp", { method: "OPTIONS" }))!;
    expect(r.headers.get("access-control-allow-headers")!.toLowerCase()).toContain("authorization");
    expect(r.headers.get("access-control-allow-methods")).toContain("POST");
  });

  it("exposes WWW-Authenticate so browser JS can read the RFC 9728 pointer", () => {
    // Without this the 401 is opaque to fetch(): the resource_metadata URL is unreadable and
    // OAuth discovery silently dead-ends in the browser.
    const r = preflight(new Request("https://w.example/mcp", { method: "OPTIONS" }))!;
    expect(r.headers.get("access-control-expose-headers")!.toLowerCase()).toContain("www-authenticate");
  });

  it("returns null for non-OPTIONS, so real requests still reach the gate", () => {
    for (const method of ["GET", "POST"]) {
      expect(preflight(new Request("https://w.example/mcp", { method }))).toBeNull();
    }
  });

  it("the 401 itself carries CORS headers", () => {
    const denied = requireBearer(new Request("https://w.example/mcp", { method: "POST" }), ENV)!;
    expect(denied.status).toBe(401);
    expect(denied.headers.get("access-control-allow-origin")).toBe("*");
    expect(denied.headers.get("access-control-expose-headers")!.toLowerCase())
      .toContain("www-authenticate");
    expect(denied.headers.get("www-authenticate")).toContain("resource_metadata=");
  });
});
