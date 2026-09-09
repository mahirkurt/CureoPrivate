#!/usr/bin/env bash
# smoke_oauth_public.sh — post-deploy smoke test for anamnesis-mcp.
# Verifies: /health, OAuth metadata advertises S256, /mcp rejects unauthenticated,
# and an authenticated initialize succeeds. Run AFTER `wrangler deploy` + secret put.
#
# Usage:
#   BASE=https://anamnesis-mcp.<your-subdomain>.workers.dev MCP_API_KEY=<key> ./scripts/smoke_oauth_public.sh
set -euo pipefail

BASE="${BASE:?set BASE to the deployed Worker origin}"
KEY="${MCP_API_KEY:-}"
pass() { printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; exit 1; }

echo "smoke: $BASE"

# 1) health
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/health" || true)
[ "$code" = "200" ] && pass "/health 200" || fail "/health expected 200 got $code"

# 1b) deep health — must stay bearer-gated, and must name a failing dependency rather than
# reporting a blanket ok. A green liveness probe says nothing about whether retrieval can run.
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/health?deep=1" || true)
[ "$code" = "401" ] && pass "/health?deep=1 gated (401)" || fail "/health?deep=1 expected 401 got $code"
if [ -n "${MCP_API_KEY:-}" ]; then
  deep=$(curl -s -H "Authorization: Bearer $MCP_API_KEY" "$BASE/health?deep=1")
  echo "$deep" | grep -q '"status": *"ok"' \
    && pass "/health?deep=1 all dependencies ok" \
    || fail "/health?deep=1 degraded: $deep"
fi

# 2) OAuth AS metadata advertises S256 only
meta=$(curl -s "$BASE/.well-known/oauth-authorization-server")
echo "$meta" | grep -q '"S256"' && pass "AS metadata advertises S256" || fail "S256 not advertised"
echo "$meta" | grep -q '"plain"' && fail "metadata must NOT advertise plain" || pass "no plain advertised"

# 3) protected-resource metadata
pr=$(curl -s "$BASE/.well-known/oauth-protected-resource")
echo "$pr" | grep -q '/mcp' && pass "protected-resource -> /mcp" || fail "protected-resource missing /mcp"

# 4) /mcp without Bearer -> 401
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/mcp" \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"1"}}}' || true)
[ "$code" = "401" ] && pass "/mcp unauthenticated -> 401 (gate active)" || fail "/mcp expected 401 got $code"

# 5) authenticated initialize (only if a key is provided)
if [ -n "$KEY" ]; then
  body=$(curl -s -X POST "$BASE/mcp" \
    -H "authorization: Bearer $KEY" \
    -H 'content-type: application/json' \
    -H 'accept: application/json, text/event-stream' \
    -H 'mcp-protocol-version: 2025-06-18' \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"1"}}}')
  echo "$body" | grep -q 'serverInfo\|"result"' && pass "authenticated initialize ok" \
    || fail "authenticated initialize did not return a result: $body"
else
  printf '  \033[33mSKIP\033[0m  authenticated initialize (set MCP_API_KEY to run)\n'
fi

echo "smoke complete."
