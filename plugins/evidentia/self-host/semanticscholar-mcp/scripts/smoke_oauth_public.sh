#!/usr/bin/env bash
# smoke_oauth_public.sh — post-deploy smoke test for who-gho-mcp (KEYLESS).
# who-gho is keyless by design (MCP_ALLOW_NO_AUTH=1): the upstream WHO GHO OData is authless and the
# Worker holds no secret. So /mcp accepts unauthenticated requests. The additive OAuth surface is
# still present (metadata advertises S256) for web-connector flows.
#
# Usage:
#   BASE=https://who-gho-mcp.<your-subdomain>.workers.dev ./scripts/smoke_oauth_public.sh
set -euo pipefail

BASE="${BASE:?set BASE to the deployed Worker origin}"
pass() { printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; exit 1; }

echo "smoke: $BASE"

# 1) health
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/health" || true)
[ "$code" = "200" ] && pass "/health 200" || fail "/health expected 200 got $code"

# 2) additive OAuth AS metadata still advertises S256 only
meta=$(curl -s "$BASE/.well-known/oauth-authorization-server")
echo "$meta" | grep -q '"S256"' && pass "AS metadata advertises S256" || fail "S256 not advertised"
echo "$meta" | grep -q '"plain"' && fail "metadata must NOT advertise plain" || pass "no plain advertised"

# 3) protected-resource metadata
pr=$(curl -s "$BASE/.well-known/oauth-protected-resource")
echo "$pr" | grep -q '/mcp' && pass "protected-resource -> /mcp" || fail "protected-resource missing /mcp"

# 4) keyless initialize (no Bearer) -> result
body=$(curl -s -X POST "$BASE/mcp" \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -H 'mcp-protocol-version: 2025-06-18' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"1"}}}')
echo "$body" | grep -q 'serverInfo\|"result"' && pass "keyless initialize ok (no Bearer)" \
  || fail "keyless initialize did not return a result: $body"

echo "smoke complete."
