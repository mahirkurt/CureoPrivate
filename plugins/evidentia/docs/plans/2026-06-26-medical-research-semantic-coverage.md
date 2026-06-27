# medical-research Semantic Coverage Mechanism — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the `medical-research` skill a semantic, deterministic, full-coverage scan of its own knowledge base — eliminating recall gaps, cross-axis blindness, depth loss, and inconsistent coverage.

**Architecture:** Additive to v8.2 (no core rewrite). **Backbone A** (always-on, every surface): a semantic `knowledge-map.md` + a new Adım 0.4 "Semantic Scope Scan" that emits an auditable `coverage_set`, a mandatory multi-axis fan-out feeding the existing 0.5 loader, a full-detail discipline, and a Completeness Gate before finalising — verified by a new `G-COVERAGE` integrity gate. **Booster B** (optional, graceful-degrade): a standalone `evidentia-kb` Cloudflare Worker exposing one read-only `kb_search` tool over a bge-m3 Vectorize index of the KB, ingested at setup.

**Tech Stack:** Markdown skill content; Python (`check_integrity.py`, `kb_ingest`); TypeScript Cloudflare Worker (McpAgent + DO + Vectorize + D1, Family-A OAuth); `wrangler`; `doppler`; `claude plugin` CLI.

## Global Constraints

- Skill version bump: `8.2.0` → **`8.3.0`** — update verbatim in `SKILL.md` frontmatter, `SKILL.md` H1/changelog, and `skill-manifest.yaml` (G-VERSION asserts agreement on base `8.3`).
- **Additive only** (ADR-05): do not delete/rewrite existing Adım 0 / 0.5 / layer-file content; new steps wrap/feed the existing machinery. The keyword fast-path is a floor — it may only *add* to `coverage_set`, never shrink it.
- `coverage_set` is an **invisible Ops/Layer-B sidecar** artifact (per `report-presentation.md`), never in the visible clean-copy body.
- Booster is **degradable**: every `kb_search` call is guarded by reachability; absence degrades to A-only (still complete). Booster may only raise recall, never gate the flow.
- Worker family invariants (Family-A): hardened OAuth 2.1 **S256-only**, redirect-origin allowlist, escHtml, HMAC-signed codes, constant-time compares, `access_token == MCP_API_KEY`, secrets only in CF secret store (`MCP_ALLOW_NO_AUTH="0"`). `grok.com`/`claude.ai`/`claude.com`/`chatgpt.com` default redirect origins per fleet convention.
- Cloudflare bot-filter GOTCHA: any Python MCP client hitting `*.cureonics.workers.dev/mcp` MUST send a real `User-Agent` (default `Python-urllib` → 403).
- Paths are relative to the plugin root `/mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia/` unless absolute.
- Secrets live in Doppler `cureohub/dev_personal`. Vectorize index dim = 1024, metric = cosine (bge-m3).

---

## File Structure

| File | Responsibility |
|---|---|
| `references/knowledge-map.md` | NEW. Semantic index of the whole KB (forward per-file map + inverted concept→sections map). Always-loaded. |
| `skills/medical-research/SKILL.md` | MODIFY. Add Adım 0.4 (Semantic Scope Scan), Completeness Gate step, full-detail rule, knowledge-map in always-load, v8.3 stamps. |
| `skills/medical-research/skill-manifest.yaml` | MODIFY. Register knowledge-map; version 8.3.0; add `G-COVERAGE`; add optional `evidentia-kb`/`kb_search` to runtime.mcp_servers. |
| `skills/medical-research/evals/check_integrity.py` | MODIFY. Add `G-COVERAGE` gate (map ↔ corpus exhaustiveness/consistency). |
| `self-host/evidentia-kb-mcp/` | NEW. Standalone Worker: `kb_search`; Vectorize `evidentia-kb` + D1 `evidentia-kb-db`; Family-A `auth.ts`; tests; `BUILD-BRIEF.md`. |
| `scripts/kb_ingest.py` | NEW. Section-chunk + embed + upsert the KB into `evidentia-kb`. |
| `.mcp.json` + `CONNECTORS.md` | MODIFY. Add `evidentia-kb` Tier-O entry (degradable) + SSOT row. |
| `README.md` | MODIFY. Note semantic-coverage mechanism + kb_search. |

---

# PHASE A — Backbone (deliver first; works on every surface)

### Task A1: Author `references/knowledge-map.md`

**Files:**
- Create: `references/knowledge-map.md`

**Interfaces:**
- Produces: a Markdown doc with (1) a **Forward Map** — one `### <file>` block per `SKILL.md` + every `references/*.md` (EXCEPT itself, `benchmark-*.md`, `composition-runbook.md`, `execution-map.md`, `v8-wiring-patch.md` which are process/tooling, not knowledge axes — but they MUST still be listed under a "Process/tooling (not question-routed)" section so G-COVERAGE sees full coverage); each block lists the file's `##`/`###` section titles + concept clusters + synonyms + cross-axis links. (2) An **Inverted Map** — `- concept → file#section, …` lines across dimensions: disease/indication, drug/INN/brand, MoA/target/class, specialty axis, geography, regulatory, HTA/access, epidemiology, evidence-type, full-text/KOL/pipeline.
- Consumed by: Adım 0.4 (Task A3), G-COVERAGE (Task A2).

- [ ] **Step 1: Enumerate the corpus to be mapped**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
ls references/*.md | sort
grep -h '^## ' SKILL.md references/*.md | sort -u | head -80
```
Expected: the list of ~20 reference files + their section headings. This is the raw material the map must cover.

- [ ] **Step 2: Write the Forward Map skeleton — one block per file**

Create `references/knowledge-map.md` starting:
```markdown
# Knowledge Map — medical-research semantic coverage index (v8.3)

> Adım 0.4 (Semantic Scope Scan) reads this to build `coverage_set` by MEANING, not keywords.
> G-COVERAGE asserts this map is exhaustive vs. the real corpus. Keep in sync with the layer files.

## Forward Map (file → sections → concepts → cross-links)

### connector-registry.md  — [ALWAYS]
- Sections: native-first ladder, verified tool table, α-layer (§2.5), per-connector notes, limitations
- Concepts: tool selection, connector routing, rate limits, fallback chains
- Cross-links: every axis depends on this for tool resolution

### oncology-layer.md  — [axis 0.5.A]
- Sections: <copy the ## / ### titles from the file>
- Concepts: solid tumours, NSCLC/breast/CRC/melanoma, ADC, IO/PD-(L)1, RECIST, NCCN/ESMO, OS/PFS/ORR, biomarkers (KRAS/EGFR/HER2/MSI), staging
- Synonyms: kanser, tümör, malignite, neoplazi, …
- Cross-links: hematology (heme-onc), drug-intelligence (onco pipeline), turkiye (TR onco reimbursement), hta (onco cost-effectiveness)
```
Continue a block for EVERY file from Step 1 (oncology, hematology, regulatory-science, hta, medaffairs-ops, immunology, neurology, rare-disease, drug-intelligence, regulatory-intelligence, turkiye, evidence-grading, output-templates, fulltext-retrieval, report-presentation, extended-api, osint-playbook). Fill `Sections:` from the actual `##`/`###` headings of each file (Step 1 output). Add a final block:
```markdown
### Process/tooling (not question-routed, listed for coverage completeness)
- benchmark-suite.md, benchmark-protocol.md, composition-runbook.md, execution-map.md, v8-wiring-patch.md, skill-manifest.yaml
```

- [ ] **Step 3: Write the Inverted Map**

Append:
```markdown
## Inverted Map (concept → file#section)

### Geography
- Türkiye / TR ruhsat / SGK / SUT / fiyat → turkiye-layer.md (all) · regulatory-intelligence.md#TR
- EU / EMA / CHMP → regulatory-science-layer.md · regulatory-intelligence.md
- US / FDA → regulatory-science-layer.md · drug-intelligence-layer.md

### Regulatory angle
- approval / withdrawal / accelerated / BTD / PRIME / REMS → regulatory-science-layer.md + regulatory-intelligence.md
### HTA / access
- cost-effectiveness / ICER / QALY / NICE/CADTH/PBAC/IQWiG / budget impact / MAIC / NMA → hta-layer.md + regulatory-intelligence.md
### Epidemiology / burden
- incidence / prevalence / GBD / WHO GHO / GLOBOCAN → regulatory-intelligence.md#epi
### Drug / pipeline
- INN/brand / MoA / target / class / pipeline / PDUFA / LoE / deal → drug-intelligence-layer.md
### Full-text / KOL
- full-text / PMC / copyright / KOL / author network → fulltext-retrieval.md · turkiye-layer.md (TR KOL)
### Evidence appraisal
- GRADE / RoB / certainty / endpoints → evidence-grading.md
```
Extend with disease/MoA clusters that route into the specialty axes (each disease family → its layer + sibling links).

- [ ] **Step 4: Verify every corpus file is referenced**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
for f in $(ls references/*.md | xargs -n1 basename | grep -v '^knowledge-map.md$'); do
  grep -q "$f" references/knowledge-map.md && echo "OK  $f" || echo "MISSING  $f"
done
```
Expected: every file `OK` (none `MISSING`). Fix the map until all OK. (Task A2 turns this into an enforced gate.)

- [ ] **Step 5: Commit**

```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
git add references/knowledge-map.md 2>/dev/null || true
# evidentia-cc is not a git repo; if it is later, this commits. Otherwise the file is tracked via the zip.
```
(If not in git, skip commit; the repackage task ships it. Do not fail the task on missing git.)

---

### Task A2: `G-COVERAGE` gate in `check_integrity.py`

**Files:**
- Modify: `skills/medical-research/evals/check_integrity.py`
- Test: same file (the gate is self-testing when run)

**Interfaces:**
- Consumes: `references/knowledge-map.md` (A1), `references/*.md`, `SKILL.md`.
- Produces: a `g_coverage()` check that prints PASS/FAIL lines and contributes to the script's overall exit code, exactly like the existing `G-REF`/`G-ALWAYS`/`G-VERSION` blocks.

- [ ] **Step 1: Read the existing gate structure**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
grep -n 'def \|G-REF\|G-ALWAYS\|G-VERSION\|ALL RUN GATES\|sys.exit\|ok=\|fail' skills/medical-research/evals/check_integrity.py | head -40
```
Expected: see how gates are defined, how PASS/FAIL is recorded, and how the final exit code is computed. Match that style.

- [ ] **Step 2: Write the G-COVERAGE function (insert before the final summary/exit)**

Add (adapt PASS/FAIL helper names to the file's existing ones found in Step 1):
```python
def g_coverage(base_dir):
    """G-COVERAGE — knowledge-map.md is exhaustive & consistent vs the corpus."""
    import os, re
    refs = os.path.join(base_dir, "references")
    km = os.path.join(refs, "knowledge-map.md")
    print("\nG-COVERAGE  knowledge-map exhaustiveness")
    if not os.path.exists(km):
        print("  FAIL  references/knowledge-map.md missing")
        return False
    map_text = open(km, encoding="utf-8").read()
    ok = True
    # (1) every reference file (except the map itself) is mentioned in the map
    ref_files = [f for f in os.listdir(refs) if f.endswith(".md") and f != "knowledge-map.md"]
    for f in sorted(ref_files):
        if f in map_text:
            print(f"  PASS  forward-map references {f}")
        else:
            print(f"  FAIL  knowledge-map.md does not reference {f}"); ok = False
    # (2) every Adım 0.5 axis id (0.5.A .. 0.5.K) appears in the map
    skill = open(os.path.join(base_dir, "SKILL.md"), encoding="utf-8").read()
    axes = sorted(set(re.findall(r"0\.5\.[A-K]", skill)))
    for ax in axes:
        if ax in map_text:
            print(f"  PASS  map covers axis {ax}")
        else:
            print(f"  FAIL  map omits axis {ax}"); ok = False
    # (3) no dangling entries: every *.md token in the map exists on disk
    for m in sorted(set(re.findall(r"\b([a-z0-9-]+\.md)\b", map_text))):
        if m == "knowledge-map.md":
            continue
        if os.path.exists(os.path.join(refs, m)) or os.path.exists(os.path.join(base_dir, m)):
            pass
        else:
            print(f"  FAIL  map references non-existent file {m}"); ok = False
    print("  " + ("PASS  map consistent with corpus" if ok else "FAIL  map drift detected"))
    return ok
```

- [ ] **Step 3: Wire G-COVERAGE into the run + exit code**

Find where existing gates are called and ORed into the pass/fail total (Step 1). Add `g_coverage(BASE)` to that aggregation using the same variable the file already uses (e.g. `all_pass = all_pass and g_coverage(BASE)`), and ensure the final "ALL RUN GATES PASSED" / nonzero-exit logic includes it.

- [ ] **Step 4: Run — expect PASS against the A1 map**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
python3 skills/medical-research/evals/check_integrity.py 2>&1 | grep -A30 'G-COVERAGE'
echo "exit=$?"
```
Expected: every `PASS`, no `FAIL`, and overall `ALL RUN GATES PASSED`. If any `FAIL`, fix `knowledge-map.md` (A1) until green — this is the gate doing its job.

- [ ] **Step 5: Negative test (gate actually catches drift)**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
cp references/knowledge-map.md /tmp/km.bak
# remove a file's mention to simulate drift:
sed -i '0,/oncology-layer.md/{/oncology-layer.md/d}' references/knowledge-map.md
python3 skills/medical-research/evals/check_integrity.py 2>&1 | grep -i 'oncology-layer.md\|FAIL' | head
mv /tmp/km.bak references/knowledge-map.md
```
Expected: a `FAIL ... does not reference oncology-layer.md`, proving the gate detects drift; then the map is restored.

- [ ] **Step 6: Commit** (skip if no git, per A1 Step 5 note).

---

### Task A3: SKILL.md — Adım 0.4 + Completeness Gate + always-load + v8.3

**Files:**
- Modify: `skills/medical-research/SKILL.md`

**Interfaces:**
- Consumes: `references/knowledge-map.md` (A1).
- Produces: a new mandatory step `Adım 0.4` and a `Completeness Gate` step referenced by the pipeline; `knowledge-map.md` in the Adım-0 always-load list; version `8.3.0`.

- [ ] **Step 1: Add knowledge-map.md to the Adım 0 always-load list**

In `SKILL.md` find the "Adım 0: Mandatory Loading" block (around the six always-load files). Add a line:
```markdown
- `references/knowledge-map.md` — semantic coverage index (drives Adım 0.4). Always-load.
```
Update the "Always-load = these six" sentence to "these seven".

- [ ] **Step 2: Insert Adım 0.4 immediately before the Adım 0.5 axis section**

Add:
```markdown
## Adım 0.4: Semantic Scope Scan (MANDATORY — runs before 0.5)

Using `references/knowledge-map.md`, scan the KB by MEANING, not keywords:

1. Decompose the question into its concept set across: disease/indication · drug (INN/brand) · MoA/target/class · specialty axis · geography (TR/EU/US/global) · regulatory angle · HTA/access · epidemiology/burden · evidence type · full-text/KOL/pipeline.
2. For EACH concept, resolve ALL relevant sections via the knowledge-map Inverted Map + each block's cross-links. A concept maps to a section by semantic relatedness even when the question does not use that section's trigger words.
3. (Booster, optional) If `kb_search` is reachable, call `kb_search(question, k=8)` and merge its returned sections into the set. If unreachable, continue map-only.
4. Emit `coverage_set` = the UNION of axes + sections, written into the invisible Ops/Layer-B sidecar (NOT the clean copy). This is the auditable coverage trail.

`coverage_set` is a SUPERSET: the Adım 0.5 keyword fast-path may add axes but may never remove any. Then proceed to Adım 0.5 loading the full union.
```

- [ ] **Step 3: Make Adım 0.5 consume the union (mandatory multi-axis fan-out)**

In the Adım 0.5 intro, add one sentence:
```markdown
> Adım 0.5 loads the UNION of `coverage_set` from Adım 0.4 — every axis in the set is mandatorily loaded, not only the highest-signal one. Keyword signals here can only ADD to the set.
```

- [ ] **Step 4: Add the full-detail discipline note (near the extraction/output doctrine)**

Add:
```markdown
**Full-detail discipline:** every section in `coverage_set` is loaded and its sub-details surfaced in reasoning/output. A loaded KB section is never silently summarised away (consistent with report-presentation.md extraction doctrine).
```

- [ ] **Step 5: Add the Completeness Gate as the final pre-finalise step**

In the pipeline/closing section add:
```markdown
## Completeness Gate (MANDATORY — immediately before finalising)

Re-scan `references/knowledge-map.md` against the question and the work done:
"Is there any axis, section, or connector relevant to this question that was NOT consulted?"
- Produce a gap list (in the Ops sidecar). (Booster: if `kb_search` reachable, run it once more on the question to catch misses.)
- If the gap list is non-empty: load + address each gap, then re-check.
- Finalise only when the gap list is empty. This makes coverage deterministic and repeatable.
```

- [ ] **Step 6: Bump version to 8.3.0**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
grep -n '8\.2\.0\|8\.2' skills/medical-research/SKILL.md | head
```
Replace the frontmatter `version:` and the H1/changelog occurrences of `8.2.0` with `8.3.0` (and add a changelog line: `v8.3.0 — semantic coverage mechanism: Adım 0.4 + knowledge-map + Completeness Gate + G-COVERAGE; optional evidentia-kb booster`). Do NOT touch unrelated version strings of other components.

- [ ] **Step 7: Verify G-REF/G-ALWAYS/G-VERSION still pass**

Run:
```bash
python3 skills/medical-research/evals/check_integrity.py 2>&1 | tail -6
```
Expected: `ALL RUN GATES PASSED` (G-ALWAYS now also checks knowledge-map.md is present; G-VERSION agrees on 8.3).

- [ ] **Step 8: Commit** (skip if no git).

---

### Task A4: skill-manifest.yaml — register map, version, gate, optional booster

**Files:**
- Modify: `skills/medical-research/skill-manifest.yaml`

- [ ] **Step 1: Inspect current manifest structure**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
grep -n 'version\|reference\|gates\|G-REF\|mcp_servers\|always' skills/medical-research/skill-manifest.yaml | head -40
```

- [ ] **Step 2: Apply edits**

- Set the manifest `version:` to `8.3.0`.
- Add `knowledge-map.md` to the reference/always-load list with role "semantic coverage index".
- Add `G-COVERAGE` to the verification gates list.
- Add an OPTIONAL `evidentia-kb` entry to runtime.mcp_servers marked degradable (tool `kb_search`), e.g. `{ name: evidentia-kb, tool: kb_search, tier: O, optional: true, role: "KB semantic recall booster (graceful-degrade)" }`.

- [ ] **Step 3: Validate YAML + integrity**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
python3 -c "import yaml;yaml.safe_load(open('skills/medical-research/skill-manifest.yaml'));print('yaml ok')"
python3 skills/medical-research/evals/check_integrity.py 2>&1 | tail -4
```
Expected: `yaml ok` + `ALL RUN GATES PASSED`.

- [ ] **Step 4: Commit** (skip if no git).

---

### Task A5: Phase-A acceptance — gates + reinstall + multi-axis proof

**Files:** none (verification only)

- [ ] **Step 1: All offline gates green**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
python3 skills/medical-research/evals/check_integrity.py 2>&1 | tail -3
python3 scripts/g_bundle.py 2>&1 | tail -2
```
Expected: `ALL RUN GATES PASSED` + `BUNDLE CONSISTENT`.

- [ ] **Step 2: Reinstall plugin so the new skill content loads**

Run:
```bash
claude plugin uninstall evidentia@cureonics 2>&1 | tail -1
claude plugin marketplace update cureonics 2>&1 | tail -1
claude plugin install evidentia@cureonics 2>&1 | tail -1
claude plugin details evidentia@cureonics 2>&1 | grep -iE 'Skills \(|version'
```
Expected: install OK; medical-research present.

- [ ] **Step 3: Manual multi-axis dry-run check (success criterion)**

Read `references/knowledge-map.md` and trace the question *"tisagenlecleucel — global evidence + TR access + HTA + pipeline + KOL"*. Confirm the Inverted Map routes it to: hematology + drug-intelligence + regulatory-science + hta + turkiye + fulltext(KOL) sections — WITHOUT depending on each trigger keyword. Document the resulting `coverage_set` in the commit message / a scratch note.
Expected: ≥6 axes resolved from meaning.

- [ ] **Step 4: Commit** (skip if no git). **Phase A complete — the goal is met on every surface even if Phase B is never built.**

---

# PHASE B — Booster (optional recall; standalone evidentia-kb Worker)

### Task B1: Scaffold `evidentia-kb-mcp` Worker (Family-A clone)

**Files:**
- Create: `self-host/evidentia-kb-mcp/{src/auth.ts,src/index.ts,src/server.ts,package.json,wrangler.jsonc,tsconfig.json,vitest.config.ts,test/auth.test.ts,test/routing.test.ts}`

**Interfaces:**
- Produces: a deployable Worker exporting DO class `EvidentiaKb`, with bindings `MCP_OBJECT` (DO), `KB_VECTORIZE` (Vectorize), `DB` (D1), `AI` (Workers AI for bge-m3). Tool surface defined in Task B2.

- [ ] **Step 1: Clone the proven openfda scaffold (boilerplate copy, not re-authoring)**

Run:
```bash
SH=/mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia/self-host
cd "$SH"; rm -rf evidentia-kb-mcp; mkdir -p evidentia-kb-mcp/src evidentia-kb-mcp/test
cp openfda-mcp/src/auth.ts evidentia-kb-mcp/src/auth.ts
cp openfda-mcp/test/auth.test.ts evidentia-kb-mcp/test/auth.test.ts
cp openfda-mcp/test/routing.test.ts evidentia-kb-mcp/test/routing.test.ts
cp openfda-mcp/tsconfig.json openfda-mcp/vitest.config.ts evidentia-kb-mcp/
sed -i 's/const REALM = "openfda-mcp"/const REALM = "evidentia-kb-mcp"/' evidentia-kb-mcp/src/auth.ts
grep -n 'const REALM' evidentia-kb-mcp/src/auth.ts
```
Expected: `const REALM = "evidentia-kb-mcp";`

- [ ] **Step 2: Write `package.json`**

```json
{
  "name": "evidentia-kb-mcp",
  "version": "1.0.0",
  "private": true,
  "description": "Hardened-OAuth Cloudflare Worker MCP — read-only semantic search over the medical-research knowledge base (bge-m3 Vectorize). One tool: kb_search. Recall booster for evidentia Adım 0.4 / Completeness Gate.",
  "type": "module",
  "main": "src/index.ts",
  "scripts": { "typecheck": "tsc --noEmit", "test": "vitest run", "dev": "wrangler dev", "deploy": "wrangler deploy", "cf-typegen": "wrangler types" },
  "dependencies": { "@modelcontextprotocol/sdk": "^1.12.0", "agents": "^0.0.80", "zod": "^3.23.8" },
  "devDependencies": { "@cloudflare/vitest-pool-workers": "^0.8.0", "@cloudflare/workers-types": "^4.20250620.0", "typescript": "^5.6.0", "vitest": "~3.2.0", "wrangler": "^4.20.0" }
}
```

- [ ] **Step 3: Write `wrangler.jsonc`**

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "evidentia-kb-mcp",
  "main": "src/index.ts",
  "compatibility_date": "2025-06-01",
  "compatibility_flags": ["nodejs_compat"],
  "ai": { "binding": "AI" },
  "vectorize": [{ "binding": "KB_VECTORIZE", "index_name": "evidentia-kb" }],
  "d1_databases": [{ "binding": "DB", "database_name": "evidentia-kb-db", "database_id": "REPLACE_WITH_D1_DATABASE_ID" }],
  "durable_objects": { "bindings": [{ "name": "MCP_OBJECT", "class_name": "EvidentiaKb" }] },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["EvidentiaKb"] }],
  "vars": { "MCP_ALLOW_NO_AUTH": "0", "OAUTH_ALLOWED_REDIRECT_ORIGINS": "" },
  "observability": { "enabled": true }
}
```

- [ ] **Step 4: Write `src/index.ts`**

```typescript
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools, type KbEnv } from "./server.js";
import { handleOAuth, requireBearer, type AuthEnv } from "./auth.js";

export interface Env extends AuthEnv, KbEnv { MCP_OBJECT: DurableObjectNamespace; }

export class EvidentiaKb extends McpAgent<Env> {
  server = new McpServer({ name: "evidentia-kb-mcp", version: "1.0.0" });
  async init(): Promise<void> { registerTools(this.server, this.env as unknown as KbEnv); }
}

export default {
  async fetch(req: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const p = new URL(req.url).pathname;
    if (p === "/health") return new Response("ok", { status: 200, headers: { "content-type": "text/plain" } });
    if (p.startsWith("/.well-known/oauth") || p.startsWith("/oauth/")) return handleOAuth(req, env);
    if (p === "/mcp" || p === "/sse") {
      const denied = requireBearer(req, env); if (denied) return denied;
      return p === "/sse" ? EvidentiaKb.serveSSE("/sse").fetch(req, env, ctx) : EvidentiaKb.serve("/mcp").fetch(req, env, ctx);
    }
    return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
  },
};
```

- [ ] **Step 5: Typecheck won't pass yet (server.ts missing) — that's expected; B2 adds it.** Skip running; commit after B2.

---

### Task B2: `kb_search` tool + embed/query (`src/server.ts`)

**Files:**
- Create: `self-host/evidentia-kb-mcp/src/server.ts`

**Interfaces:**
- Consumes: `KB_VECTORIZE` (`.query`), `DB` (`kb_chunks` table: `id TEXT PK, file TEXT, section TEXT, ord INT, text TEXT`), `AI` (`@cf/baai/bge-m3`).
- Produces: `export interface KbEnv { AI:any; KB_VECTORIZE:any; DB:any }` and `export function registerTools(server, env)` registering `kb_search(query:string, k?:number)`.

- [ ] **Step 1: Write `src/server.ts`**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export interface KbEnv {
  AI: { run: (model: string, opts: any) => Promise<any> };
  KB_VECTORIZE: { query: (vec: number[], opts: any) => Promise<any> };
  DB: { prepare: (q: string) => any; batch?: (s: any[]) => Promise<any> };
}

const EMBED_MODEL = "@cf/baai/bge-m3";

async function embed(env: KbEnv, text: string): Promise<number[]> {
  const r: any = await env.AI.run(EMBED_MODEL, { text: [text] });
  const v = r?.data?.[0] ?? r?.[0];
  if (!Array.isArray(v)) throw new Error("embed: unexpected AI response shape");
  return v as number[];
}

export function registerTools(server: McpServer, env: KbEnv): void {
  server.tool(
    "kb_search",
    "Semantic search over the medical-research knowledge base (SKILL.md + references/*.md), " +
      "bge-m3 vectors. Returns the top-k most relevant KB sections with {file, section, score} " +
      "provenance — a recall booster for Adım 0.4 / Completeness Gate. Read-only.",
    {
      query: z.string().describe("The research question or concept to find relevant KB sections for"),
      k: z.number().int().min(1).max(25).optional().describe("Max sections (default 8)"),
    },
    async ({ query, k }) => {
      try {
        const qv = await embed(env, query);
        const res: any = await env.KB_VECTORIZE.query(qv, { topK: k ?? 8, returnMetadata: "all" });
        const matches: any[] = res?.matches ?? [];
        const ids = matches.map((m) => m.id);
        let textById: Record<string, any> = {};
        if (ids.length) {
          const ph = ids.map(() => "?").join(",");
          const rows = await env.DB.prepare(
            `SELECT id, file, section, text FROM kb_chunks WHERE id IN (${ph})`,
          ).bind(...ids).all();
          for (const r of (rows.results ?? [])) textById[String(r.id)] = r;
        }
        const hits = matches.map((m) => {
          const row = textById[m.id] ?? m.metadata ?? {};
          return { file: row.file ?? m.metadata?.file ?? null, section: row.section ?? m.metadata?.section ?? null, score: m.score, snippet: String(row.text ?? "").slice(0, 500) };
        });
        return { content: [{ type: "text", text: JSON.stringify({ query, k: k ?? 8, hits, note: "KB section pointers for coverage; load the named file#section for full detail." }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `kb_search failed: ${e.message}` }] };
      }
    },
  );
}
```

- [ ] **Step 2: Install deps + typecheck**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia/self-host/evidentia-kb-mcp
npm install --no-fund --no-audit 2>&1 | tail -2
npm run typecheck 2>&1 | tail -8
```
Expected: typecheck exit 0.

- [ ] **Step 3: Run tests (auth + routing)**

Run:
```bash
npm test 2>&1 | tail -12
```
Expected: auth tests pass (12). `routing.test.ts` will fail to LOAD with the known ajv × vitest-pool-workers ESM-shim SyntaxError — this is the documented fleet gotcha, NOT a defect; typecheck + auth tests passing is the bar.

- [ ] **Step 4: Commit** (skip if no git).

---

### Task B3: Provision + deploy + secrets + smoke

**Files:**
- Modify: `self-host/evidentia-kb-mcp/wrangler.jsonc` (paste D1 id)

- [ ] **Step 1: Create Vectorize index + D1**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia/self-host/evidentia-kb-mcp
npx --yes wrangler vectorize create evidentia-kb --dimensions=1024 --metric=cosine 2>&1 | tail -4
npx --yes wrangler d1 create evidentia-kb-db 2>&1 | tail -6
DBID=$(npx --yes wrangler d1 list --json 2>/dev/null | python3 -c "import json,sys;[print(d['uuid']) for d in json.load(sys.stdin) if d['name']=='evidentia-kb-db']")
echo "DBID=$DBID"
sed -i "s/REPLACE_WITH_D1_DATABASE_ID/$DBID/" wrangler.jsonc
grep database_id wrangler.jsonc
```
Expected: index created, D1 created, `database_id` pasted.

- [ ] **Step 2: Create the kb_chunks table (ensureSchema-free: do it once explicitly)**

Run:
```bash
npx --yes wrangler d1 execute evidentia-kb-db --remote --yes --command \
"CREATE TABLE IF NOT EXISTS kb_chunks (id TEXT PRIMARY KEY, file TEXT, section TEXT, ord INTEGER, text TEXT); CREATE INDEX IF NOT EXISTS idx_kb_file ON kb_chunks(file);" 2>&1 | tail -5
```
Expected: `changed_db: true` / success.

- [ ] **Step 3: Generate + set secrets, then deploy**

Run:
```bash
SCR=/tmp/claude-1000/-mnt-thunderbolt-workspaces-CureoHub/<SESSION>/scratchpad/secrets   # use the real session scratchpad
mkdir -p "$SCR"; umask 077
KKEY=$(openssl rand -hex 32); KHMAC=$(openssl rand -hex 16)
printf 'EVIDENTIA_KB_MCP_API_KEY=%s\nEVIDENTIA_KB_AUTH_HMAC_SECRET=%s\n' "$KKEY" "$KHMAC" > "$SCR/evidentia-kb.env"
npx --yes wrangler deploy 2>&1 | grep -E 'Uploaded|Deployed|workers.dev|Version ID'
echo -n "$KKEY"  | npx --yes wrangler secret put MCP_API_KEY 2>&1 | tail -1
echo -n "$KHMAC" | npx --yes wrangler secret put AUTH_HMAC_SECRET 2>&1 | tail -1
doppler secrets upload "$SCR/evidentia-kb.env" --project cureohub --config dev_personal 2>&1 | tail -1
```
Expected: deployed to `https://evidentia-kb-mcp.cureonics.workers.dev`; both secrets uploaded; Doppler updated.
> NOTE: this is a production deploy — requires explicit user authorization at execution time (the executor must confirm before running, consistent with prior Worker deploys).

- [ ] **Step 4: OAuth smoke**

Run:
```bash
B=https://evidentia-kb-mcp.cureonics.workers.dev
curl -s -o /dev/null -w "health=%{http_code}\n" "$B/health"
curl -s "$B/.well-known/oauth-authorization-server" | python3 -c "import json,sys;m=json.load(sys.stdin).get('code_challenge_methods_supported');print('S256-only:', m==['S256'])"
curl -s -o /dev/null -w "mcp-noauth=%{http_code}\n" -X POST "$B/mcp" -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"s","version":"1"}}}'
```
Expected: `health=200`, `S256-only: True`, `mcp-noauth=401`.

- [ ] **Step 5: Commit** (skip if no git).

---

### Task B4: `scripts/kb_ingest.py` — ingest the KB + live `kb_search` E2E

**Files:**
- Create: `scripts/kb_ingest.py`

**Interfaces:**
- Consumes: the deployed Worker's `kb_search` (read) and a write path. Because `kb_search` is read-only, ingest writes vectors+rows directly via wrangler: embeddings come from the Worker's AI binding is not callable externally → ingest computes chunks, then writes to D1 via `wrangler d1 execute` and to Vectorize via `wrangler vectorize insert` using vectors obtained from a temporary `kb_ingest` admin tool OR the WHO-style approach below.

- [ ] **Step 1: Decide ingest vector source (no extra tool)**

Vectorize requires vectors. Add a TEMPORARY admin-gated `kb_ingest` tool to the Worker for setup, OR (simpler, chosen) compute embeddings via a one-off `wrangler ai` call. Implement ingest as: (a) section-chunk the corpus in Python; (b) for each chunk, get a bge-m3 vector by POSTing to the Worker's `kb_search`-sibling `kb_embed` admin tool. To avoid a public embed tool, add `kb_embed`/`kb_upsert` tools GATED so they only work with the Bearer (already gated) and mark them in the description as setup-only.

Add to `src/server.ts` `registerTools` (then redeploy):
```typescript
  server.tool("kb_upsert", "SETUP-ONLY: embed + upsert one KB chunk (Bearer-gated).",
    { id: z.string(), file: z.string(), section: z.string(), ord: z.number().int(), text: z.string() },
    async ({ id, file, section, ord, text }) => {
      try {
        const v = await embed(env, text);
        await env.KB_VECTORIZE.upsert([{ id, values: v, metadata: { file, section } }]);
        await env.DB.prepare("INSERT OR REPLACE INTO kb_chunks (id,file,section,ord,text) VALUES (?,?,?,?,?)").bind(id, file, section, ord, text).run();
        return { content: [{ type: "text", text: JSON.stringify({ upserted: id }) }] };
      } catch (e: any) { return { isError: true, content: [{ type: "text", text: `kb_upsert failed: ${e.message}` }] }; }
    });
```
Re-run B2 typecheck, redeploy (B3 Step 3 deploy only).

- [ ] **Step 2: Write `scripts/kb_ingest.py`**

```python
#!/usr/bin/env python3
"""Section-chunk SKILL.md + references/*.md and upsert into evidentia-kb via the Worker's kb_upsert (Bearer-gated, setup-only)."""
import os, re, json, sys, urllib.request, hashlib, glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # plugin root
SKILL = os.path.join(BASE, "skills", "medical-research")
URL = "https://evidentia-kb-mcp.cureonics.workers.dev/mcp"
KEY = os.environ["EVIDENTIA_KB_MCP_API_KEY"]
SID = {"v": None}

def call(method, params=None, notif=False):
    b = {"jsonrpc": "2.0", "method": method}
    if not notif: b["id"] = 1
    if params is not None: b["params"] = params
    r = urllib.request.Request(URL, data=json.dumps(b).encode(), method="POST")
    for k, v in {"authorization": "Bearer " + KEY, "user-agent": "Mozilla/5.0 (kb-ingest)", "content-type": "application/json", "accept": "application/json, text/event-stream"}.items():
        r.add_header(k, v)
    if SID["v"]: r.add_header("mcp-session-id", SID["v"])
    resp = urllib.request.urlopen(r, timeout=60)
    if resp.headers.get("mcp-session-id"): SID["v"] = resp.headers["mcp-session-id"]
    raw = resp.read().decode()
    if "text/event-stream" in (resp.headers.get("content-type") or ""):
        for ln in raw.splitlines():
            if ln.startswith("data:"):
                try: return json.loads(ln[5:].strip())
                except Exception: pass
    return json.loads(raw)

def chunks():
    files = [os.path.join(SKILL, "SKILL.md")] + sorted(glob.glob(os.path.join(SKILL, "references", "*.md")))
    for fp in files:
        fname = os.path.basename(fp)
        if fname == "knowledge-map.md":  # the map indexes the others; still ingest it for self-recall
            pass
        txt = open(fp, encoding="utf-8").read()
        # split on ## / ### headings, keep heading with body
        parts = re.split(r"(?m)^(#{2,3}\s+.*)$", txt)
        # parts: [pre, head1, body1, head2, body2, ...]
        cur_head = fname
        buf = parts[0]
        ord_ = 0
        def emit(head, body):
            nonlocal ord_
            body = (head + "\n" + body).strip()
            if len(body) < 30: return
            cid = f"{fname}#{ord_}:" + hashlib.md5((fname+head).encode()).hexdigest()[:8]
            yield_obj = {"id": cid, "file": fname, "section": head.strip("# ").strip()[:120], "ord": ord_, "text": body[:4000]}
            ord_ += 1
            return yield_obj
        out = []
        o = emit(cur_head, buf)
        if o: out.append(o)
        for i in range(1, len(parts) - 1, 2):
            head = parts[i]; body = parts[i+1] if i+1 < len(parts) else ""
            o = emit(head, body)
            if o: out.append(o)
        for c in out: yield c

def main():
    call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "ingest", "version": "1"}})
    call("notifications/initialized", notif=True)
    n = 0
    for c in chunks():
        res = call("tools/call", {"name": "kb_upsert", "arguments": c})
        ok = not (isinstance(res, dict) and res.get("result", {}).get("isError"))
        n += 1
        if n % 20 == 0: print(f"  upserted {n}…", flush=True)
    print(f"DONE — {n} chunks ingested")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the ingest**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
export EVIDENTIA_KB_MCP_API_KEY=$(doppler secrets get EVIDENTIA_KB_MCP_API_KEY -p cureohub -c dev_personal --plain)
python3 scripts/kb_ingest.py
```
Expected: `DONE — N chunks ingested` (N ≈ 150–300 for the corpus).

- [ ] **Step 4: Live kb_search E2E (allow Vectorize indexing lag)**

Run:
```bash
python3 - "$EVIDENTIA_KB_MCP_API_KEY" <<'PY'
import json,sys,urllib.request,time
KEY=sys.argv[1]; URL="https://evidentia-kb-mcp.cureonics.workers.dev/mcp"; SID={"v":None}
def call(m,p=None,n=False):
    b={"jsonrpc":"2.0","method":m}
    if not n: b["id"]=1
    if p is not None: b["params"]=p
    r=urllib.request.Request(URL,data=json.dumps(b).encode(),method="POST")
    for k,v in {"authorization":"Bearer "+KEY,"user-agent":"Mozilla/5.0","content-type":"application/json","accept":"application/json, text/event-stream"}.items(): r.add_header(k,v)
    if SID["v"]: r.add_header("mcp-session-id",SID["v"])
    resp=urllib.request.urlopen(r,timeout=60)
    if resp.headers.get("mcp-session-id"): SID["v"]=resp.headers["mcp-session-id"]
    raw=resp.read().decode()
    if "text/event-stream" in (resp.headers.get('content-type') or ''):
        for ln in raw.splitlines():
            if ln.startswith("data:"):
                try: return json.loads(ln[5:])
                except: pass
    return json.loads(raw)
call("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"1"}}); call("notifications/initialized",n=True)
r=call("tools/call",{"name":"kb_search","arguments":{"query":"Turkey reimbursement and HTA for an oncology drug","k":5}})
print(r["result"]["content"][0]["text"][:600])
PY
```
Expected: hits referencing `turkiye-layer.md`, `hta-layer.md`, `oncology-layer.md` (semantic, no keyword overlap required). If 0 hits, wait ~30s for Vectorize indexing and re-run.

- [ ] **Step 5: Commit** (skip if no git).

---

### Task B5: Wire `evidentia-kb` into roster + SSOT + gates + reinstall

**Files:**
- Modify: `.mcp.json`, `CONNECTORS.md`

- [ ] **Step 1: Add the Tier-O entry to `.mcp.json`** (after `openfda`, before `tavily`)

```jsonc
"evidentia-kb": {
  "type": "http",
  "url": "https://evidentia-kb-mcp.cureonics.workers.dev/mcp",
  "_tier": "O",
  "_trust": "operator self-host (Cloudflare Worker — hardened OAuth 2.1 S256 + Bearer)",
  "_probe": "2026-06-26 HTTP 401 SECURED · authenticated initialize 200 · kb_search live",
  "_role": "OPSIYONEL recall takviyesi (Adım 0.4 + Completeness Gate): KB semantik araması (bge-m3). Bağlı değilse akış map-only'ye degrade eder — asla kapı değil."
}
```

- [ ] **Step 2: Document in `CONNECTORS.md`** (add a row to the §1.6 self-host table + the inventory). Use the exact URL so `g_bundle` (URL ⊆ CONNECTORS.md) passes.

```markdown
| **evidentia-kb** | `https://evidentia-kb-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-26) | **KB semantik recall takviyesi** (`self-host/evidentia-kb-mcp/`) — `kb_search` (bge-m3 Vectorize over SKILL.md+references). Adım 0.4 / Completeness Gate için OPSIYONEL; bağlı değilse map-only degrade. **Deployed + Tier-O** (401 SECURED · kb_search live). |
```

- [ ] **Step 3: Gates**

Run:
```bash
cd /mnt/thunderbolt/workspaces/evidentia-cc/plugins/evidentia
python3 scripts/g_bundle.py 2>&1 | tail -3
timeout 150 python3 scripts/g_probe.py 2>&1 | grep -E 'evidentia-kb|summary|HEALTHY'
python3 skills/medical-research/evals/check_integrity.py 2>&1 | tail -3
```
Expected: `BUNDLE CONSISTENT`; `evidentia-kb 🔒401`; `ALL RUN GATES PASSED`.

- [ ] **Step 4: Reinstall**

Run:
```bash
claude plugin uninstall evidentia@cureonics 2>&1 | tail -1
claude plugin marketplace update cureonics 2>&1 | tail -1
claude plugin install evidentia@cureonics 2>&1 | tail -1
claude plugin details evidentia@cureonics 2>&1 | grep -iE 'MCP servers \('
```
Expected: 13 MCP servers incl. `evidentia-kb`.

- [ ] **Step 5: Commit** (skip if no git).

---

### Task B6: Repackage zip + memory + keys-md

**Files:**
- Modify: `/mnt/thunderbolt/workspaces/CureoSuite/evidentia-claude-code.zip`; memory files; `EVIDENTIA-KURULUM-VE-KEYLER.md`

- [ ] **Step 1: Repackage zip (no node_modules)**

Run:
```bash
cd /mnt/thunderbolt/workspaces
zip -r CureoSuite/evidentia-claude-code.zip \
  evidentia-cc/plugins/evidentia/.mcp.json \
  evidentia-cc/plugins/evidentia/CONNECTORS.md \
  evidentia-cc/plugins/evidentia/README.md \
  evidentia-cc/plugins/evidentia/skills/medical-research \
  evidentia-cc/plugins/evidentia/references/knowledge-map.md \
  evidentia-cc/plugins/evidentia/docs \
  evidentia-cc/plugins/evidentia/scripts/kb_ingest.py \
  evidentia-cc/plugins/evidentia/self-host/evidentia-kb-mcp \
  -x '*/node_modules/*' '*/.wrangler/*' 2>&1 | tail -5
echo "node_modules in zip: $(unzip -l CureoSuite/evidentia-claude-code.zip | grep -c node_modules)"
```
Expected: updated; `node_modules in zip: 0`.

- [ ] **Step 2: Update memory** `project_evidentia_plugin.md` (+ MEMORY.md pointer): note v8.3 semantic-coverage mechanism, knowledge-map, Adım 0.4, Completeness Gate, G-COVERAGE, evidentia-kb Worker (kb_search, `EVIDENTIA_KB_MCP_API_KEY` in Doppler), 13 servers. Mirror to dotfiles copy.

- [ ] **Step 3: Update keys-md** `EVIDENTIA-KURULUM-VE-KEYLER.md`: add `evidentia-kb` to §0 status, §2 keys table (its Bearer), §6 DO table.

- [ ] **Step 4: Done — full functional retest** of the new mechanism: ask evidentia a multi-axis question, confirm the Ops sidecar `coverage_set` lists ≥6 axes and kb_search corroborated (when connected).

---

## Self-Review

**1. Spec coverage:**
- Backbone A1 knowledge-map → Task A1 ✓; Adım 0.4 → A3 ✓; multi-axis fan-out → A3 Step 3 ✓; full-detail discipline → A3 Step 4 ✓; Completeness Gate → A3 Step 5 ✓.
- G-COVERAGE → A2 ✓; version bump → A3 Step 6 + A4 ✓.
- Booster B (separate Worker) → B1–B2 ✓; provision/deploy/secrets → B3 ✓; ingest → B4 ✓; graceful degrade → encoded in A3 Step 2/3 (guarded calls) + .mcp.json `_role` B5 ✓; wiring/gates → B5 ✓; repackage/memory/keys → B6 ✓.
- coverage_set in Ops sidecar → A3 Step 2 ✓. Determinism (written coverage_set + Completeness Gate + G-COVERAGE) ✓.

**2. Placeholder scan:** `REPLACE_WITH_D1_DATABASE_ID` is replaced in B3 Step 1; `<SESSION>` scratchpad path is a real substitution the executor fills from the live session. No TODO/TBD logic.

**3. Type consistency:** `KbEnv` defined in B2 and imported in B1 `index.ts` — consistent. `registerTools(server, env)` signature matches openfda/anamnesis pattern. `kb_chunks` columns match between B3 schema, B2 `kb_search` SELECT, and B4 `kb_upsert` INSERT (id,file,section,ord,text). DO class `EvidentiaKb` consistent across index.ts + wrangler.jsonc migration.

**Note:** B4 introduces `kb_upsert` (setup-only, Bearer-gated) which B1/B2 didn't pre-declare — B4 Step 1 explicitly adds it to `server.ts` + redeploys; this is intentional, not a dangling reference.
