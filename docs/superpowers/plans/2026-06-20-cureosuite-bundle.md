# Cureosuite Bundle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package `bist-analyst`, `fon-uzmani`, and a midas-stripped `rxpraxis` (plus their MCP connectors) into a private `cureosuite` Claude Code marketplace, gated by a single shared Bearer key, for authorized external users.

**Architecture:** Two phases across two repos. **Phase 0 (CureoHub `mcp-servers/`)** adds a non-breaking *additive* "suite key" to the three gated MCP `/mcp` Bearer gates (fon-mcp Worker, titck-mcp + mevzuat-mcp Cloud Run) so one key authorizes all three. **Phases 1–4 (new `cureosuite` repo)** derive the three plugins from the canonical `marketplace` repo via a deterministic `sync-from-canonical.sh`, relicense them under a shared EULA, wire the gated `.mcp.json` headers to `${CUREONICS_MCP_KEY}`, and publish to a private GitHub repo.

**Tech Stack:** TypeScript/Cloudflare Workers (fon-mcp, vitest), Python/Starlette on Cloud Run (titck-mcp, mevzuat-mcp, pytest), Bash (sync script), Claude Code plugin/marketplace JSON manifests, `gh` CLI, Doppler (`cureohub/dev_personal`).

## Global Constraints

- **Repo name:** `cureosuite`; GitHub slug `mahirkurt/cureosuite`; **private** visibility.
- **Three plugins only:** `bist-analyst`, `fon-uzmani`, `rxpraxis` (lite). No `brand-ecosystem-core`, no `vekayinuvis`.
- **midas fully removed** from the cureosuite `rxpraxis`: no `midas` server, no `skills/thoughtspot-roche/`, no `commands/rxpraxis-midas.md`, no midas/ThoughtSpot/Roche references (grep-clean except historical changelog lines).
- **Single user-facing key:** env var `CUREONICS_MCP_KEY`; its value === backend secret `SUITE_MCP_API_KEY` on all three gated MCPs.
- **Gated MCP set:** `fon-mcp`, `titck`, `mevzuat`. (`borsa` is public/no-auth; `titck-cache` stays **open by design** — pure public-data cache-proxy; `pubmed`/`clinical-trials`/`biorxiv` come from the user's own claude.com connections.)
- **Suite key is additive/non-breaking:** existing per-service `MCP_API_KEY` values keep working; OAuth machinery stays keyed to the primary `MCP_API_KEY`; the suite key is only an *additional accepted static Bearer* on `/mcp`.
- **No secrets in any repo:** `.mcp.json` uses `${CUREONICS_MCP_KEY}` placeholder only; the key is delivered out-of-band. Run a leak scan before publish.
- **License:** all three plugins relicensed to the shared cureosuite EULA (incl. bist-analyst; MIT is dropped).
- **Correct gated URLs:** `fon-mcp` = `https://fon-mcp.cureonics.workers.dev/mcp`; `titck` = `https://titck-mcp-to7lqjgdkq-ew.a.run.app/mcp` (already correct in source); `mevzuat` = `https://mevzuat-mcp-to7lqjgdkq-ew.a.run.app/mcp` (**replaces stale `…864144140896…` URL**).
- **Canonical source paths:** `/mnt/thunderbolt/workspaces/marketplace/plugins/{bist-analyst,fon-uzmani,rxpraxis}`.
- **Backend source paths:** `/mnt/thunderbolt/workspaces/CureoHub/mcp-servers/{fon-mcp,titck-mcp,mevzuat-mcp}`.

---

## Phase 0 — Suite key (additive, non-breaking) across the three gated MCPs

### Task 0.1: Generate the suite key and record it in Doppler

**Files:** none (secret store only).

**Interfaces:**
- Produces: `CUREONICS_SUITE_MCP_KEY` — a 64-hex string, stored in Doppler `cureohub/dev_personal`; this same value becomes `SUITE_MCP_API_KEY` (backend) and `CUREONICS_MCP_KEY` (user env). Referenced by all later Phase-0 tasks.

- [ ] **Step 1: Generate a 64-hex key and store it**

```bash
cd /mnt/thunderbolt/workspaces/CureoHub
SUITE_KEY=$(openssl rand -hex 32)
doppler secrets set CUREONICS_SUITE_MCP_KEY="$SUITE_KEY" --silent
echo "stored; sha8=$(printf '%s' "$SUITE_KEY" | sha256sum | cut -c1-8)"
```

- [ ] **Step 2: Verify it is retrievable**

Run: `doppler secrets get CUREONICS_SUITE_MCP_KEY --plain | wc -c`
Expected: `65` (64 hex chars + newline).

---

### Task 0.2: fon-mcp accepts the suite key (Cloudflare Worker)

**Files:**
- Modify: `/mnt/thunderbolt/workspaces/CureoHub/mcp-servers/fon-mcp/src/auth.ts` (`AuthEnv` interface ~line 19; `requireBearer` ~line 80)
- Modify: `/mnt/thunderbolt/workspaces/CureoHub/mcp-servers/fon-mcp/src/types.ts` (`Env` — add `SUITE_MCP_API_KEY`)
- Test: `/mnt/thunderbolt/workspaces/CureoHub/mcp-servers/fon-mcp/test/auth.suite-key.test.ts`

**Interfaces:**
- Consumes: `CUREONICS_SUITE_MCP_KEY` value from Task 0.1.
- Produces: `requireBearer` returns `null` (allow) when the token equals **either** `env.MCP_API_KEY` **or** `env.SUITE_MCP_API_KEY`; 401 otherwise.

- [ ] **Step 1: Write the failing test**

```ts
// test/auth.suite-key.test.ts
import { describe, it, expect } from "vitest";
import { requireBearer } from "../src/auth.js";

const env = { MCP_API_KEY: "primary-aaa", SUITE_MCP_API_KEY: "suite-bbb", AUTH_HMAC_SECRET: "h" };
const mk = (tok?: string) =>
  new Request("https://fon-mcp.example/mcp", {
    method: "POST",
    headers: tok ? { authorization: `Bearer ${tok}` } : {},
  });

describe("requireBearer suite key", () => {
  it("allows the primary key", async () => {
    expect(await requireBearer(mk("primary-aaa"), env as any)).toBeNull();
  });
  it("allows the suite key", async () => {
    expect(await requireBearer(mk("suite-bbb"), env as any)).toBeNull();
  });
  it("rejects an unknown key with 401", async () => {
    const r = await requireBearer(mk("nope"), env as any);
    expect(r?.status).toBe(401);
  });
  it("rejects no token with 401", async () => {
    const r = await requireBearer(mk(), env as any);
    expect(r?.status).toBe(401);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/fon-mcp && npm test -- auth.suite-key`
Expected: FAIL — the suite-key case errors (`SUITE_MCP_API_KEY` not consulted yet) or types reject the field.

- [ ] **Step 3: Add `SUITE_MCP_API_KEY` to the `AuthEnv` interface**

In `src/auth.ts`, extend the interface:

```ts
export interface AuthEnv {
  MCP_API_KEY?: string;
  SUITE_MCP_API_KEY?: string;
  AUTH_HMAC_SECRET: string;
  MCP_ALLOW_NO_AUTH?: string;
  OAUTH_ALLOWED_REDIRECT_ORIGINS?: string;
}
```

- [ ] **Step 4: Accept the suite key in `requireBearer`**

In `src/auth.ts`, replace the single-key check inside `requireBearer` (the line `if (token && (await constantTimeEqual(token, expected))) return null;`) with:

```ts
  const suite = (env.SUITE_MCP_API_KEY ?? "").trim();
  if (token && (await constantTimeEqual(token, expected))) return null;
  if (token && suite && (await constantTimeEqual(token, suite))) return null;
```

- [ ] **Step 5: Mirror the binding in `types.ts`**

In `src/types.ts`, add to the `Env` interface (next to `MCP_API_KEY`):

```ts
  SUITE_MCP_API_KEY: string;  // additional accepted /mcp bearer (cureosuite shared key)
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/fon-mcp && npm test -- auth.suite-key`
Expected: PASS (4/4).

- [ ] **Step 7: Run the full fon-mcp suite (no regression)**

Run: `cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/fon-mcp && npm test`
Expected: all existing tests still PASS.

- [ ] **Step 8: Set the Worker secret and deploy**

```bash
cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/fon-mcp
doppler secrets get CUREONICS_SUITE_MCP_KEY --plain | npx wrangler secret put SUITE_MCP_API_KEY
npx wrangler deploy
```

- [ ] **Step 9: Verify live — suite key 200, no key 401**

```bash
SK=$(doppler secrets get CUREONICS_SUITE_MCP_KEY --plain)
B='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"v","version":"0"}}}'
echo "no-auth:  $(curl -s -o /dev/null -w '%{http_code}' -X POST https://fon-mcp.cureonics.workers.dev/mcp -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' -d "$B")"
echo "suite:    $(curl -s -o /dev/null -w '%{http_code}' -X POST https://fon-mcp.cureonics.workers.dev/mcp -H "authorization: Bearer $SK" -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' -d "$B")"
```
Expected: `no-auth: 401`, `suite: 200`.

- [ ] **Step 10: Commit (on a feature branch in CureoHub)**

```bash
cd /mnt/thunderbolt/workspaces/CureoHub
git checkout -b feat/cureosuite-suite-key 2>/dev/null || git checkout feat/cureosuite-suite-key
git add mcp-servers/fon-mcp/src/auth.ts mcp-servers/fon-mcp/src/types.ts mcp-servers/fon-mcp/test/auth.suite-key.test.ts
git commit -m "feat(fon-mcp): accept additive SUITE_MCP_API_KEY on /mcp bearer gate

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 0.3: titck-mcp accepts the suite key (Cloud Run / Python)

**Files:**
- Modify: `/mnt/thunderbolt/workspaces/CureoHub/mcp-servers/titck-mcp/src/titck_mcp/http_app.py` (the `/mcp` gate, ~lines 89–107)
- Test: `/mnt/thunderbolt/workspaces/CureoHub/mcp-servers/titck-mcp/tests/test_suite_key_gate.py`

**Interfaces:**
- Consumes: `CUREONICS_SUITE_MCP_KEY` from Task 0.1.
- Produces: the `/mcp` gate accepts a Bearer token equal to **either** `MCP_API_KEY` **or** `SUITE_MCP_API_KEY` env vars.

- [ ] **Step 1: Read the exact gate block**

Run: `sed -n '85,110p' /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/titck-mcp/src/titck_mcp/http_app.py`
Confirm the block computes `expected = (os.environ.get("MCP_API_KEY") or "").strip()` and rejects with `hmac.compare_digest(token, expected)`.

- [ ] **Step 2: Write the failing test**

```python
# tests/test_suite_key_gate.py
import hmac, os

def _accepts(token: str, primary: str, suite: str) -> bool:
    """Mirror of the /mcp gate predicate after the change."""
    expected = (primary or "").strip()
    suite = (suite or "").strip()
    if not token:
        return False
    return hmac.compare_digest(token, expected) or (bool(suite) and hmac.compare_digest(token, suite))

def test_primary_key_accepted():
    assert _accepts("primary", "primary", "suite")

def test_suite_key_accepted():
    assert _accepts("suite", "primary", "suite")

def test_unknown_rejected():
    assert not _accepts("nope", "primary", "suite")

def test_empty_rejected():
    assert not _accepts("", "primary", "suite")
```

> NOTE: this test pins the *predicate contract*; Step 4 makes `http_app.py` implement exactly this predicate.

- [ ] **Step 3: Run the test to verify it passes as a spec, then make the app match**

Run: `cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/titck-mcp && uv run pytest tests/test_suite_key_gate.py -q`
Expected: PASS (the predicate test is self-contained). This locks the contract Step 4 must satisfy.

- [ ] **Step 4: Implement the additive check in `http_app.py`**

Replace the gate rejection block (around line 89–99):

```python
            expected = (os.environ.get("MCP_API_KEY") or "").strip()
            suite = (os.environ.get("SUITE_MCP_API_KEY") or "").strip()
            if not expected:
                # ... existing auth_not_configured handling unchanged ...
                ...
            else:
                auth = request.headers.get("authorization", "")
                token = auth.removeprefix("Bearer ").strip()
                ok = bool(token) and (
                    hmac.compare_digest(token, expected)
                    or (bool(suite) and hmac.compare_digest(token, suite))
                )
                if not ok:
                    # ... existing 401 response unchanged ...
                    ...
```

(Keep the surrounding `auth_not_configured` and 401-response code exactly as-is; only `expected`/`suite`/`ok` change.)

- [ ] **Step 5: Run the predicate test + full suite**

Run: `cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/titck-mcp && uv run pytest -q`
Expected: all PASS.

- [ ] **Step 6: Deploy to Cloud Run with the new env var**

```bash
cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/titck-mcp
# Use the server's existing deploy path; confirm with: ls scripts/ ; cat Makefile 2>/dev/null
SK=$(doppler secrets get CUREONICS_SUITE_MCP_KEY --plain)
gcloud run services update titck-mcp --project cureonics-ai-hub --region europe-west1 \
  --update-env-vars "SUITE_MCP_API_KEY=$SK"
```

> If titck-mcp reads secrets via Secret Manager rather than plain env, add the value as a new secret and `--update-secrets SUITE_MCP_API_KEY=...:latest` instead. Confirm by inspecting the current service: `gcloud run services describe titck-mcp --project cureonics-ai-hub --region europe-west1 --format='value(spec.template.spec.containers[0].env[].name)'`.

- [ ] **Step 7: Verify live — suite key 200, no key 401**

```bash
SK=$(doppler secrets get CUREONICS_SUITE_MCP_KEY --plain)
B='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"v","version":"0"}}}'
echo "no-auth: $(curl -s -o /dev/null -w '%{http_code}' -X POST https://titck-mcp-to7lqjgdkq-ew.a.run.app/mcp -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' -d "$B")"
echo "suite:   $(curl -s -o /dev/null -w '%{http_code}' -X POST https://titck-mcp-to7lqjgdkq-ew.a.run.app/mcp -H "authorization: Bearer $SK" -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' -d "$B")"
```
Expected: `no-auth: 401`, `suite: 200`.

- [ ] **Step 8: Commit**

```bash
cd /mnt/thunderbolt/workspaces/CureoHub
git add mcp-servers/titck-mcp/src/titck_mcp/http_app.py mcp-servers/titck-mcp/tests/test_suite_key_gate.py
git commit -m "feat(titck-mcp): accept additive SUITE_MCP_API_KEY on /mcp bearer gate

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 0.4: mevzuat-mcp accepts the suite key (Cloud Run / Python)

**Files:**
- Modify: `/mnt/thunderbolt/workspaces/CureoHub/mcp-servers/mevzuat-mcp/src/mevzuat_mcp/http_app.py` (the `/mcp` gate, ~lines 111–129)
- Test: `/mnt/thunderbolt/workspaces/CureoHub/mcp-servers/mevzuat-mcp/tests/test_suite_key_gate.py`

**Interfaces:**
- Consumes: `CUREONICS_SUITE_MCP_KEY` from Task 0.1.
- Produces: identical additive predicate to Task 0.3, applied to mevzuat's gate.

- [ ] **Step 1: Write the failing test** — identical body to Task 0.3 Step 2, at `mevzuat-mcp/tests/test_suite_key_gate.py`.

- [ ] **Step 2: Run it** — `cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/mevzuat-mcp && uv run pytest tests/test_suite_key_gate.py -q` → PASS (contract lock).

- [ ] **Step 3: Implement the additive check** in `http_app.py` at lines ~111–121, applying the exact same `expected`/`suite`/`ok` pattern from Task 0.3 Step 4 (the surrounding `auth_not_configured` and 401 blocks stay byte-identical).

- [ ] **Step 4: Run full suite** — `cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/mevzuat-mcp && uv run pytest -q` → all PASS.

- [ ] **Step 5: Deploy with the new env var**

```bash
cd /mnt/thunderbolt/workspaces/CureoHub/mcp-servers/mevzuat-mcp
SK=$(doppler secrets get CUREONICS_SUITE_MCP_KEY --plain)
gcloud run services update mevzuat-mcp --project cureonics-ai-hub --region europe-west1 \
  --update-env-vars "SUITE_MCP_API_KEY=$SK"
```
(Same Secret-Manager caveat as Task 0.3 Step 6; the repo's `scripts/deploy.sh` is the canonical deploy path — prefer it if it already wires env.)

- [ ] **Step 6: Verify live**

```bash
SK=$(doppler secrets get CUREONICS_SUITE_MCP_KEY --plain)
B='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"v","version":"0"}}}'
echo "no-auth: $(curl -s -o /dev/null -w '%{http_code}' -X POST https://mevzuat-mcp-to7lqjgdkq-ew.a.run.app/mcp -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' -d "$B")"
echo "suite:   $(curl -s -o /dev/null -w '%{http_code}' -X POST https://mevzuat-mcp-to7lqjgdkq-ew.a.run.app/mcp -H "authorization: Bearer $SK" -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' -d "$B")"
```
Expected: `no-auth: 401`, `suite: 200`.

- [ ] **Step 7: Commit** (analogous message to Task 0.3 Step 8).

---

### Task 0.5: Cross-verify one suite key authorizes all three

**Files:** none (verification only).

- [ ] **Step 1: One key, three services**

```bash
SK=$(doppler secrets get CUREONICS_SUITE_MCP_KEY --plain)
B='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"v","version":"0"}}}'
for u in https://fon-mcp.cureonics.workers.dev/mcp \
         https://titck-mcp-to7lqjgdkq-ew.a.run.app/mcp \
         https://mevzuat-mcp-to7lqjgdkq-ew.a.run.app/mcp; do
  echo "$u → $(curl -s -o /dev/null -w '%{http_code}' -X POST "$u" -H "authorization: Bearer $SK" -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' -d "$B")"
done
```
Expected: all three print `→ 200`.

- [ ] **Step 2: Push the CureoHub feature branch** (does not touch `main`):

```bash
cd /mnt/thunderbolt/workspaces/CureoHub && git push -u origin feat/cureosuite-suite-key
```

---

## Phase 1 — `cureosuite` repo scaffold

### Task 1.1: Create the repo skeleton, EULA, README, .gitignore

**Files:**
- Create: `/mnt/thunderbolt/workspaces/cureosuite/.gitignore`
- Create: `/mnt/thunderbolt/workspaces/cureosuite/EULA.md`
- Create: `/mnt/thunderbolt/workspaces/cureosuite/README.md`

**Interfaces:**
- Produces: a git repo at `/mnt/thunderbolt/workspaces/cureosuite`; `EULA.md` referenced by every plugin's `LICENSE`.

- [ ] **Step 1: Init the repo**

```bash
mkdir -p /mnt/thunderbolt/workspaces/cureosuite && cd /mnt/thunderbolt/workspaces/cureosuite
git init -q
printf '%s\n' '.DS_Store' 'node_modules/' '*.code-workspace' '.env' '.env.*' '.mcp.local.json' > .gitignore
```

- [ ] **Step 2: Write `EULA.md`** (verbatim):

```markdown
# Cureonics Suite — Son Kullanıcı Lisans Sözleşmesi (EULA)

© Cureonics. Tüm hakları saklıdır.

Bu depo ("Cureonics Suite") ve içindeki `bist-analyst`, `fon-uzmani`, `rxpraxis`
plugin'leri Cureonics'in tescilli fikri mülkiyetidir ve yalnızca **yetkilendirilmiş
kullanıcılara** sunulur.

## 1. İzin verilen kullanım
Cureonics'in açık daveti üzerine bu depoya erişim verilen kullanıcılar, plugin'leri
yalnızca kendi iç değerlendirme ve karar-destek amaçlarıyla çalıştırabilir.

## 2. Kısıtlamalar
- **Yeniden dağıtım yasaktır.** Kod, skill, komut veya bağlı `CUREONICS_MCP_KEY`
  anahtarı üçüncü kişilere kopyalanamaz, yayımlanamaz veya devredilemez.
- Tersine mühendislik ile gated connector'ların kimlik doğrulamasını aşmaya çalışmak yasaktır.
- Anahtar sızıntısı durumunda Cureonics anahtarı bildirimsiz döndürebilir.

## 3. Garanti reddi
Yazılım "OLDUĞU GİBİ" sunulur; açık veya zımni hiçbir garanti verilmez.

## 4. Yatırım / tıbbi sorumluluk reddi
`bist-analyst` ve `fon-uzmani` çıktıları **karar desteğidir; SPK anlamında yatırım
danışmanlığı veya tavsiyesi değildir.** `rxpraxis` çıktıları farmasötik pazar-zekâsı
karar desteğidir; **tıbbi, regülatif veya hukuki tavsiye değildir.** Tüm kararların
sorumluluğu kullanıcıya aittir.

## 5. Fesih
Bu şartların ihlali erişimin (depo daveti ve anahtar) derhal feshini doğurur.
```

- [ ] **Step 3: Write `README.md`** (top-level overview, points to `ACCESS.md`):

```markdown
# Cureonics Suite

Yetkilendirilmiş kullanıcılar için üç Cureonics Claude Code plugin'i, bağlı MCP
connector'larıyla birlikte, tek bir private marketplace altında.

| Plugin | Ne yapar | Bundle connector'lar |
|---|---|---|
| **bist-analyst** | BIST analist kopilotu (teknik + temel + KAP + TCMB) | borsa (public) |
| **fon-uzmani** | TEFAS/EMK fon karar-destek süiti | borsa (public) + fon-mcp* |
| **rxpraxis** | Türkiye farma pazar-zekâsı / jenerik-fırsat tarama | titck* · titck-cache · mevzuat* · pubmed · clinical-trials · biorxiv |

`*` = `CUREONICS_MCP_KEY` gerektirir (aşağıya bkz. **[ACCESS.md](ACCESS.md)**).

Kurulum, yetki ve anahtar adımları için **[ACCESS.md](ACCESS.md)**'i okuyun.
Kullanım şartları için **[EULA.md](EULA.md)**.
```

- [ ] **Step 4: Commit**

```bash
cd /mnt/thunderbolt/workspaces/cureosuite
git add .gitignore EULA.md README.md
git commit -q -m "chore: scaffold cureosuite repo (EULA, README, gitignore)" && echo OK
```

---

## Phase 2 — Deterministic derivation (`sync-from-canonical.sh`)

### Task 2.1: Write the sync script (copy + lite-transform + relicense + key-wire)

**Files:**
- Create: `/mnt/thunderbolt/workspaces/cureosuite/scripts/sync-from-canonical.sh`

**Interfaces:**
- Consumes: canonical plugins at `/mnt/thunderbolt/workspaces/marketplace/plugins/*`.
- Produces: `plugins/{bist-analyst,fon-uzmani,rxpraxis}/` under `cureosuite/`, each EULA-licensed, with gated `.mcp.json` headers wired and rxpraxis midas-stripped; and `.claude-plugin/marketplace.json`.

- [ ] **Step 1: Write the script** (verbatim):

```bash
#!/usr/bin/env bash
# Derive the cureosuite bundle deterministically from the canonical marketplace repo.
# Re-runnable: wipes and regenerates plugins/ + marketplace.json. No secrets are written.
set -euo pipefail

CANON="/mnt/thunderbolt/workspaces/marketplace/plugins"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/plugins"
KEY_PLACEHOLDER='${CUREONICS_MCP_KEY}'

rm -rf "$DEST"
mkdir -p "$DEST"

# ---- copy the three plugins verbatim ----
for p in bist-analyst fon-uzmani rxpraxis; do
  cp -a "$CANON/$p" "$DEST/$p"
  rm -f "$DEST/$p/LICENSE"
done

# ---- relicense: every plugin LICENSE -> points at the shared EULA ----
for p in bist-analyst fon-uzmani rxpraxis; do
  cat > "$DEST/$p/LICENSE" <<'EOF'
Cureonics Suite — Proprietary. Authorized use only; redistribution prohibited.
Full terms: ../../EULA.md (Cureonics Suite EULA).
Decision support only — not investment / medical / legal advice.
EOF
done

# ---- rxpraxis lite-transform: strip midas / thoughtspot-roche entirely ----
RX="$DEST/rxpraxis"
rm -rf "$RX/skills/thoughtspot-roche"
rm -f  "$RX/commands/rxpraxis-midas.md"

python3 - "$RX" <<'PY'
import json, sys, pathlib
rx = pathlib.Path(sys.argv[1])

# 1) .mcp.json: drop the midas server; fix the stale mevzuat URL; wire gated bearer headers.
mcp = json.loads((rx / ".mcp.json").read_text())
servers = mcp["mcpServers"]
servers.pop("midas", None)
GATED = {"fon-mcp", "titck", "mevzuat"}
URLFIX = {"mevzuat": "https://mevzuat-mcp-to7lqjgdkq-ew.a.run.app/mcp"}
for name, cfg in servers.items():
    if name in URLFIX:
        cfg["url"] = URLFIX[name]
    if name in GATED:
        cfg.setdefault("headers", {})["Authorization"] = "Bearer ${CUREONICS_MCP_KEY}"
(rx / ".mcp.json").write_text(json.dumps(mcp, indent=2) + "\n")

# 2) plugin.json: drop thoughtspot-roche from smp.source_skills.
pj_path = rx / ".claude-plugin" / "plugin.json"
pj = json.loads(pj_path.read_text())
smp = pj.get("smp", {})
if "source_skills" in smp:
    smp["source_skills"] = [s for s in smp["source_skills"] if s != "thoughtspot-roche"]
pj_path.write_text(json.dumps(pj, indent=2) + "\n")

# 3) tool-manifest.json: drop midas tool entries if present.
tm_path = rx / "shared" / "tool-manifest.json"
if tm_path.exists():
    tm = json.loads(tm_path.read_text())
    def strip_midas(obj):
        if isinstance(obj, dict):
            return {k: strip_midas(v) for k, v in obj.items()
                    if "midas" not in k.lower() and "thoughtspot" not in k.lower()}
        if isinstance(obj, list):
            return [strip_midas(x) for x in obj
                    if not (isinstance(x, str) and ("midas" in x.lower() or "thoughtspot" in x.lower()))]
        return obj
    tm_path.write_text(json.dumps(strip_midas(tm), indent=2) + "\n")
PY

# 4) Scrub midas/thoughtspot/roche reference LINES from rxpraxis prose contracts.
#    (Whole-line removal in CONNECTORS.md + rxos/start skills; manual review flagged below.)
for f in "$RX/CONNECTORS.md" "$RX/skills/rxos/SKILL.md" "$RX/skills/start/SKILL.md"; do
  [ -f "$f" ] && sed -i -E '/midas|thoughtspot|roche/Id' "$f" || true
done

# ---- fon-uzmani: wire fon-mcp gated bearer header (borsa stays public) ----
python3 - "$DEST/fon-uzmani" <<'PY'
import json, sys, pathlib
fu = pathlib.Path(sys.argv[1])
mcp = json.loads((fu / ".mcp.json").read_text())
fon = mcp["mcpServers"].get("fon-mcp")
if fon:
    fon.setdefault("headers", {})["Authorization"] = "Bearer ${CUREONICS_MCP_KEY}"
(fu / ".mcp.json").write_text(json.dumps(mcp, indent=2) + "\n")
PY

echo "sync complete → $DEST"
```

- [ ] **Step 2: Make it executable and run it**

```bash
cd /mnt/thunderbolt/workspaces/cureosuite
chmod +x scripts/sync-from-canonical.sh
./scripts/sync-from-canonical.sh
```
Expected: prints `sync complete → …/plugins`.

- [ ] **Step 3: Verify midas/thoughtspot is fully stripped from rxpraxis**

Run: `grep -riE 'midas|thoughtspot|roche' /mnt/thunderbolt/workspaces/cureosuite/plugins/rxpraxis --include='*.md' --include='*.json' | grep -viE 'changelog|date|history' || echo "CLEAN"`
Expected: `CLEAN` (any remaining hits must be hand-fixed before proceeding — see Task 2.2).

- [ ] **Step 4: Verify gated headers + mevzuat URL wired**

```bash
cat /mnt/thunderbolt/workspaces/cureosuite/plugins/rxpraxis/.mcp.json
cat /mnt/thunderbolt/workspaces/cureosuite/plugins/fon-uzmani/.mcp.json
```
Expected: `midas` absent; `mevzuat` URL = `…mevzuat-mcp-to7lqjgdkq-ew…`; `fon-mcp`/`titck`/`mevzuat` each carry `"Authorization": "Bearer ${CUREONICS_MCP_KEY}"`; `borsa`/`titck-cache`/`pubmed`/`clinical-trials`/`biorxiv` carry **no** auth header.

- [ ] **Step 5: Commit the script + generated plugins**

```bash
cd /mnt/thunderbolt/workspaces/cureosuite
git add scripts/sync-from-canonical.sh plugins/
git commit -q -m "feat: derive 3 plugins from canonical (rxpraxis lite, gated headers, EULA)" && echo OK
```

---

### Task 2.2: Hand-fix residual midas/thoughtspot prose in rxpraxis

**Files:**
- Modify (as needed): `cureosuite/plugins/rxpraxis/CONNECTORS.md`, `cureosuite/plugins/rxpraxis/skills/rxos/SKILL.md`, `cureosuite/plugins/rxpraxis/.claude-plugin/plugin.json` (description), `cureosuite/plugins/rxpraxis/README.md`

**Interfaces:**
- Consumes: Task 2.1 Step 3 grep output (the list of non-clean hits).
- Produces: grep-clean rxpraxis (except historical changelog) with coherent prose (no dangling "4 source skills" counts, no orphaned fallback rows).

- [ ] **Step 1: List residual hits**

Run: `grep -rniE 'midas|thoughtspot|roche' /mnt/thunderbolt/workspaces/cureosuite/plugins/rxpraxis | grep -viE 'changelog|"date"'`

- [ ] **Step 2: Fix each hit** — for every file in the list: remove the midas/thoughtspot connector row, fix any "source_skills: 4" → "3" counts and orchestrator stage lists in `rxos/SKILL.md`, and update the `plugin.json` `description` (drop "thoughtspot-roche" from the source-skill enumeration). Edit the actual prose so sentences stay grammatical.

- [ ] **Step 3: Re-verify clean**

Run: `grep -rniE 'midas|thoughtspot|roche' /mnt/thunderbolt/workspaces/cureosuite/plugins/rxpraxis | grep -viE 'changelog|"date"' || echo CLEAN`
Expected: `CLEAN`.

- [ ] **Step 4: Commit**

```bash
cd /mnt/thunderbolt/workspaces/cureosuite
git add plugins/rxpraxis && git commit -q -m "fix(rxpraxis): scrub residual midas/thoughtspot prose, fix counts" && echo OK
```

---

### Task 2.3: Generate `marketplace.json`

**Files:**
- Create: `/mnt/thunderbolt/workspaces/cureosuite/.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the three derived `plugin.json` versions.
- Produces: a marketplace manifest Claude Code can `marketplace add`.

- [ ] **Step 1: Write `marketplace.json`** (verbatim):

```json
{
  "name": "cureosuite",
  "description": "Cureonics Suite — yetkilendirilmiş kullanıcılar için BIST, TEFAS-fon ve Türkiye farma pazar-zekâsı plugin'leri (gated MCP connector'larıyla).",
  "owner": { "name": "Cureonics", "url": "https://cureonics.com" },
  "metadata": { "version": "1.0.0" },
  "plugins": [
    { "name": "bist-analyst", "source": "./plugins/bist-analyst", "strict": true },
    { "name": "fon-uzmani",   "source": "./plugins/fon-uzmani",   "strict": false },
    { "name": "rxpraxis",     "source": "./plugins/rxpraxis",     "strict": false }
  ]
}
```

- [ ] **Step 2: Validate JSON**

Run: `python3 -c "import json; json.load(open('/mnt/thunderbolt/workspaces/cureosuite/.claude-plugin/marketplace.json')); print('valid')"`
Expected: `valid`.

- [ ] **Step 3: Commit**

```bash
cd /mnt/thunderbolt/workspaces/cureosuite
git add .claude-plugin/marketplace.json && git commit -q -m "feat: add cureosuite marketplace manifest (3 plugins)" && echo OK
```

---

## Phase 3 — Access documentation

### Task 3.1: Write `ACCESS.md`

**Files:**
- Create: `/mnt/thunderbolt/workspaces/cureosuite/ACCESS.md`

**Interfaces:**
- Consumes: the suite key (`CUREONICS_MCP_KEY`) and the install flow.
- Produces: the authoritative onboarding doc for an invited user.

- [ ] **Step 1: Write `ACCESS.md`** (verbatim):

```markdown
# Cureonics Suite — Erişim ve Kurulum

## Yetki katmanları
1. **Depo daveti** — Cureonics seni `mahirkurt/cureosuite` private deposuna GitHub
   collaborator (read) olarak davet eder. Daveti kabul et.
2. **Suite anahtarı** — Cureonics sana `CUREONICS_MCP_KEY` değerini **özel kanaldan**
   iletir. Bu anahtar gated connector'ları (fon-mcp, titck, mevzuat) açar. Paylaşma.

## Kurulum (Claude Code)
```bash
# 1) Anahtarı ortam değişkeni olarak ayarla (gated connector'lar bunu okur)
export CUREONICS_MCP_KEY="<sana iletilen değer>"   # kalıcı için ~/.bashrc / shell profili

# 2) Marketplace'i ekle (GitHub kimliğinle private repo'yu klonlar)
/plugin marketplace add mahirkurt/cureosuite

# 3) İstediğin plugin'i kur
/plugin install bist-analyst@cureosuite
/plugin install fon-uzmani@cureosuite
/plugin install rxpraxis@cureosuite
```

> `CUREONICS_MCP_KEY` ayarlı değilse gated connector'lar 401 döner ve ilgili
> plugin degrade modda çalışır. Public connector'lar (borsa, pubmed,
> clinical-trials, biorxiv) anahtarsız çalışır.

## Connector tablosu
| Connector | Plugin | Anahtar? |
|---|---|---|
| borsa | bist-analyst, fon-uzmani | Hayır (public) |
| fon-mcp | fon-uzmani | **Evet — CUREONICS_MCP_KEY** |
| titck | rxpraxis | **Evet — CUREONICS_MCP_KEY** |
| mevzuat | rxpraxis | **Evet — CUREONICS_MCP_KEY** |
| titck-cache | rxpraxis | Hayır (public ilaç-indeksi cache'i) |
| pubmed / clinical-trials / biorxiv | rxpraxis | Hayır (Claude tarafından barındırılır) |

## Şartlar
Kullanım, [EULA.md](EULA.md)'ye tabidir: yetkili kullanım, yeniden dağıtım yok,
karar-destek — yatırım/tıbbi tavsiye değildir.
```

- [ ] **Step 2: Commit**

```bash
cd /mnt/thunderbolt/workspaces/cureosuite
git add ACCESS.md && git commit -q -m "docs: add ACCESS.md (invite + key + install flow)" && echo OK
```

---

## Phase 4 — Validation and publish

### Task 4.1: Validate manifests, scan for secret leaks, smoke-test gated connectors

**Files:** none (validation only).

- [ ] **Step 1: Validate all three plugin manifests** — dispatch the `plugin-dev:plugin-validator` agent on each of `cureosuite/plugins/{bist-analyst,fon-uzmani,rxpraxis}`. Expected: no structural errors.

- [ ] **Step 2: Secret-leak scan** — there must be no real Bearer/key anywhere; only the `${CUREONICS_MCP_KEY}` placeholder.

Run:
```bash
grep -rnE 'Bearer [A-Za-z0-9._-]{16,}|mcp_[A-Za-z0-9]{16,}|[0-9a-f]{64}' /mnt/thunderbolt/workspaces/cureosuite/plugins \
  | grep -v 'Bearer ${CUREONICS_MCP_KEY}' || echo "NO LEAKS"
```
Expected: `NO LEAKS`.

- [ ] **Step 3: Smoke-test the gated connectors with the suite key**

```bash
SK=$(doppler secrets get CUREONICS_SUITE_MCP_KEY --plain)
B='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"v","version":"0"}}}'
for u in https://fon-mcp.cureonics.workers.dev/mcp \
         https://titck-mcp-to7lqjgdkq-ew.a.run.app/mcp \
         https://mevzuat-mcp-to7lqjgdkq-ew.a.run.app/mcp; do
  echo "$u → $(curl -s -o /dev/null -w '%{http_code}' -X POST "$u" -H "authorization: Bearer $SK" -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' -d "$B")"
done
```
Expected: all `→ 200`.

---

### Task 4.2: Create the private GitHub repo and push

**Files:** none (publish).

**Interfaces:**
- Consumes: the committed local `cureosuite` repo.
- Produces: `https://github.com/mahirkurt/cureosuite` (private) with `main` pushed.

- [ ] **Step 1: Create the private repo and push** (requires authenticated `gh`)

```bash
cd /mnt/thunderbolt/workspaces/cureosuite
git branch -M main
gh repo create mahirkurt/cureosuite --private --source=. --remote=origin --push
```

- [ ] **Step 2: Confirm visibility is private**

Run: `gh repo view mahirkurt/cureosuite --json visibility -q .visibility`
Expected: `PRIVATE`.

- [ ] **Step 3: (User action — not automated) Invite authorized collaborators**

The user invites each authorized external user as a **read** collaborator:
`gh api -X PUT repos/mahirkurt/cureosuite/collaborators/<github-user> -f permission=pull`
and delivers `CUREONICS_MCP_KEY` to them out-of-band. Document who received the key (informal ledger) for future rotation.

---

## Self-review notes (coverage)

- Spec §3 decisions → Global Constraints + phases. ✓
- Spec §4 repo structure → Phase 1 + 2.3 + 3.1. ✓
- Spec §5.1 rxpraxis strip → Task 2.1 (script) + 2.2 (residual prose). ✓
- Spec §6 auth (single key, gate) → Phase 0 (additive suite key, verified live) + 2.1 header wiring. ✓
- Spec §6.3 blocking unknown → resolved by live probe; titck-cache confirmed open (left open per decision), mevzuat URL fixed. ✓
- Spec §7 EULA → Task 1.1 + per-plugin LICENSE in 2.1. ✓
- Spec §8 sync/drift → Task 2.1 re-runnable script. ✓
- Spec §9 tests → Phase 0 unit tests + Task 4.1 validate/leak/smoke. ✓
- Spec §10 R2 (GitHub-less users) → out of scope for v1 (.mcpb fallback deferred); noted in ACCESS.md degrade behavior.
```
