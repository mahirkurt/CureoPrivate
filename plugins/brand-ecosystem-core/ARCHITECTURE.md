# brand-ecosystem-core — Architecture & Roadmap

This document records the primitive-layer design of the plugin and the P0/P1/P2
roadmap for hardening the brand pipeline against the 2026 expert-audit findings.
It is the durable home for the MCP-fleet build-specs (the connectors live as
**user-bound Cloudflare Worker connectors**, not plugin-bundled servers).

## 0. Design doctrine — which primitive does what

A capability placed in the wrong layer produces inconsistent, non-reproducible
behaviour. The canonical split:

| Primitive | Structurally best at | Here |
|---|---|---|
| **Skill** | In-context methodology, reasoning, output template | The brand disciplines (brand-maker, brand-verify, …) |
| **Subagent** | Isolated context, parallel/role-expert reasoning, one-way report | Critic / persona / examiner roles (`agents/`) |
| **Hook** | Event-triggered deterministic guarantee, blocking | No-fabrication + verification gates (`hooks/`) |
| **MCP** | Live external data/tools | Domain / trademark / colour / font / regulatory verification |

Doctrine: keep the always-on layer small; push procedures into skills; give every
guarantee a hook; isolate heavy work in subagents; connect external systems via
MCP and teach their use with a skill.

**Security constraint that shapes the architecture:** plugin-bundled agents do
**not** support `hooks`, `mcpServers`, or `permissionMode`. Therefore MCPs live as
**user-connected connectors** (the Cloudflare fleet), and hooks are defined at the
plugin root (`hooks/hooks.json`) or in skill/subagent frontmatter — scoped to the
component's lifecycle.

## 1. What v2.1 shipped (P0, delivered & tested)

- **brand-maker v2.1** — the five audit remediations, each with regression
  fixtures (`skills/brand-maker/tests/`, 14/14 green):
  - (A) two-source live domain verification (`domain_recon.py` → RDAP+WHOIS; no
    single-signal "available"; auronza/nortanza blocked)
  - (B) portfolio diversity gate + second-round trigger
    (`shortlist_diversity_check.py`)
  - (C) two-axis score discrimination (`phonetic_analyzer.py`: ease vs strength)
  - (D) naive first-reading perception layer (`turkish_semantic_check.py` Layer 6)
  - (E) pharma brand-name collision beyond INN stems (`pharma_brand_collision.py`)
  - (F) output-contract honesty (provisional/confirmed; pre-screen ≠ formal)
- **Hooks (`hooks/`)** — the guarantee layer:
  - `SessionStart` → injects the verification doctrine
  - `UserPromptSubmit` → regulated-sector + final-lock intent routing
  - `Stop` → provenance self-check (blocks a finish that presents a domain/mark as
    available/clean without a status label)
- **Subagents (`agents/`)** — isolated critique:
  - `diversity-auditor`, `naive-reader`, `brand-skeptic`, `trademark-examiner`,
    `etymology-verifier`
- **brand-verify skill** — teaches live verification + provenance interpretation,
  with the offline script fallback.

## 2. End-to-end composition (a naming run)

```
brand-maker (skill) generates ~12 candidates
  → Stop/PostToolUse provenance discipline stamps every claim
  → diversity-auditor (subagent) measures homogeneity; -anza cluster → 2nd round
  → brand-verify-mcp (connector) verifies domain multi-source + TM multi-jurisdiction
     (auronza now "taken"); scripts are the offline fallback
  → naive-reader (subagent) reports perception (Ortanza→"orta")
  → trademark-examiner + brand-skeptic (subagents) attack (Claranta flagged)
  → Stop hook blocks the finish until provenance is complete
  → brand-asset-registry-mcp (connector, P1) persists the decision + rationale
```

Skill reasons · subagent critiques in isolation · MCP verifies · hook guarantees.

## 3. MCP fleet — build-specs (user-bound Cloudflare connectors)

These are **not** shipped inside the plugin. They are deployed on the Cureonics
Cloudflare Worker fleet and connected by the user (Settings → Connectors), so the
plugin's skills/subagents can call them. Each tool returns provenance
(`{value, source, checked_at, status: confirmed|provisional}`).

### P0 — brand-verify-mcp — **BUILT** (`CureoHub/mcp-servers/brand-verify-mcp`)

The single MCP that closes the audit's data-accuracy defects. 6 read-only tools,
each source **empirically verified** (see the server's `VALIDATION.md`) and wired
`live` / `best_effort` / `manual_required` accordingly — every value carries
`source` + `status` (confirmed|provisional|best_effort|manual_required|unverified)
+ `timestamp`:

- `domain_multi` — RDAP + raw WHOIS:43 (**two-source live**; "available" only when
  both agree — auronza/nortanza can no longer be false-positive).
- `trademark_multi` — EUIPO **TMview live** search; WIPO/USPTO/TÜRKPATENT →
  `manual_required` deep-links (they block datacenter access).
- `inn_usan_check` — baked WHO INN/USAN + drug-brand collision (**catches
  Claranta**→clarithromycin/Claritin, which a stem-only scan misses).
- `social_handles` — GitHub/YouTube live, X best_effort, IG/LinkedIn manual.
- `llm_namespace` — Wikipedia + Wikidata live entity-collision probe.
- `brand_verify_info` — per-source modes + reachability.

Status: **56 tests green, typecheck clean.** Deploy-pending (user-gated: `wrangler
kv namespace create` + `wrangler secret put MCP_API_KEY/AUTH_HMAC_SECRET` + `npm run
deploy` → `brand-verify-mcp.cureonics.workers.dev`). Registered in
`mcp.optional.json`; taught by the `brand-verify` skill; single-tenant OAuth 2.1
(grok-default) byte-for-byte from the fleet-hardened gate.

### P1

- **color-a11y-mcp** — **BUILT + DEPLOYED** (`CureoHub/mcp-servers/color-a11y-mcp`,
  `color-a11y-mcp.cureonics.workers.dev`). WCAG 2.x + APCA contrast, CVD
  simulation (Machado 2009), Radix-style 12-step accessible scale generation
  (WCAG-enforced), OKLCH/CMYK/nearest-Pantone conversion, palette audit —
  **deterministic** for brand-visual, every algorithm pinned to an authoritative
  spec + test vectors (39 tests green). Registered in `mcp.optional.json`.
- **type-foundry-mcp** — font licensing/embedding rights, variable-font
  axes/metadata, Google Fonts + foundry verification.
- **brand-asset-registry-mcp** — **BUILT + DEPLOYED** (`CureoHub/mcp-servers/
  brand-asset-registry-mcp`, `brand-asset-registry-mcp.cureonics.workers.dev`).
  The plugin's memory: Cloudflare Workers + **D1** append-only versioned store of
  name-decision provenance, W3C DTCG design tokens, logo-lockup refs, and notes.
  6 tools (registry_put/get/list/history/delete/info); gives the pipeline
  cross-session continuity — it durably holds brand-verify-mcp's verification
  snapshots, and figma-forge + brand-touchpoint read tokens back next session.
  23 tests green; live put→get→history→delete verified. (C2PA/R2 binary blobs
  are a future extension.)

### P2

- **culture-linguistics-mcp** — **BUILT + DEPLOYED** (`CureoHub/mcp-servers/
  culture-linguistics-mcp`, `culture-linguistics-mcp.cureonics.workers.dev`).
  Real multi-market meaning (Wiktionary + Wikidata live) / IPA / taboo (LDNOOBW,
  11 langs baked) / naive-reading (FrequencyWords, 8 langs baked) — extends the
  brand-maker Turkish naive-parse + 9-language disaster-check to multi-market
  (e.g. Veridya→"ver" in pt/es/tr). 6 tools, 28 tests green. Registered in
  `mcp.optional.json`.
- **market-signal** — **BUILT as a SKILL, not an MCP** (`skills/brand-market-signal/`).
  socius-vigil already provides the data, so a separate Worker would be redundant;
  the value is the *methodology* for share-of-voice / sentiment / white-space over
  the existing `socius-vigil` connector (registered in `mcp.optional.json`). Feeds
  white-space to brand-maker Step 3.1 / brand-platform; SOV/sentiment to brand-launch KPIs.
- **regulated-claims-mcp** — **BUILT + DEPLOYED** (`CureoHub/mcp-servers/
  regulated-claims-mcp`, `regulated-claims-mcp.cureonics.workers.dev`). EU
  advertising-claim screening (cosmetic Reg 1223/2009+655/2013, medical-device
  MDR Art 7, supplement Reg 1924/2006, pharma Dir 2001/83/EC Art 87–90) — a
  deterministic guidance screen (`mcp_verified:false`, no-match ≠ clearance),
  rules pinned to the primary EU instruments. 4 tools, 32 tests green. INN stem
  check delegated to brand-verify-mcp. Registered in `mcp.optional.json`.

## 4. Subagent & hook roadmap (beyond P0)

- **P1 subagents:** `stakeholder-persona` panel (KOL/physician, pharmacist,
  "researcher parent", procurement), `pipeline-orchestrator` (runs the full chain,
  delegating heavy stages to keep the main context lean).
- **P1 hooks:** `PreToolUse` publish-gate (when a publish/registry MCP exists —
  block writing the final brand book until verification artefacts exist);
  `PostToolUse` auto-run remaining validators + stamp; `PostToolUseFailure`
  honest-degrade (network error on RDAP/TM → force "unverified", never optimistic).

## 5. Priority summary

- **P0 (closes the audit's defects) — DELIVERED:** brand-maker v2.1 · Stop
  provenance + UserPromptSubmit routing + SessionStart doctrine hooks ·
  diversity-auditor + naive-reader + brand-skeptic + trademark-examiner +
  etymology-verifier subagents · brand-verify skill · brand-verify-mcp
  connector-registration + build-spec.
- **P1 (deepens quality):** color-a11y-mcp + type-foundry-mcp · brand-asset-
  registry-mcp (memory) · stakeholder-persona panel · PreToolUse publish-gate.
- **P2 (widens the range):** market-signal-mcp + brand-metrics · culture-
  linguistics-mcp · regulated-claims-mcp · pipeline-orchestrator.

> The MCP Workers themselves are deployed and connected separately on the
> Cloudflare fleet; this plugin ships the skills, subagents, and hooks that
> *use* them, plus the offline script fallbacks so every discipline works
> connector-free on the free tier.
