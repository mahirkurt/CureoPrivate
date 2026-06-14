---
name: figma-forge
description: >-
  Design-system-agnostic DS-to-Figma library operationalization.
  Takes ANY W3C DTCG JSON, Style Dictionary, or built-in mapper (Carbon v11,
  Material 3, Tailwind) and forges production-ready Figma libraries —
  Variables, paint/text/effect styles, multi-file architecture, variant
  ComponentSets, Code Connect. Transport layer drives five live build stages
  (Foundations, Icons, Components, Patterns, Code Connect) via run_pipeline
  over MCP/REST/TS-Plugin. Modes: SCAFFOLD, TOKENS_IMPORT, COMPONENTS_BUILD,
  MIGRATE, CODE_CONNECT, PUBLISH_AUDIT, AUTO_REMEDIATE, ORCHESTRATE,
  BUNDLE_MANIFEST, AUDIT_DIFF, AUDIT_TREND. Plus stable API + Sigstore signing
  + SLSA provenance. USE for: Figma kütüphanesi kur, tasarım sistemini
  Figma'ya aktar, DS to Figma, DTCG to Figma, design tokens to Figma
  Variables, Carbon, Material 3, Tailwind, variant components, Code Connect,
  auto-remediation, supply-chain attestation. Works with any design system.
  Composable: brand-visual + brand-platform → figma-forge → frontend-design.
  When in doubt — USE.
---

# figma-forge — Design-System-to-Figma Library Operationalization Protocol

**Version:** v1.7.0 (Granularity & Scale-Out — GA)
**Status:** Stable — **v1.x is feature-complete and in maintenance mode** (declared 2026-05-30; see §15 and [`docs/rfc/v1.x-maturity-and-stability.md`](docs/rfc/v1.x-maturity-and-stability.md)). Eighth minor release — **the scale-out release**, increasing the granularity of two v1.5/v1.6 mechanisms: the observation log's physical granularity (one file → per-process shards) and freshness's logical granularity (one `"collection"` class → `collection_id`/`collection_name` sub-classes). Shipped across alpha.1 → alpha.2 → beta.1 → GA on **Path 1** (RFC v1.7 §8). Three deliverables, all **+0 public symbols**: (1) **ID-vs-name freshness split** — `validate_mcp_plan(freshness_window_overrides=)` accepts `collection_id`/`collection_name` keys with distinct TTLs (opt-in; `"collection"` alone stays the v1.6 combined class; most-specific-wins); (2) **per-process `ObservationLog` sharding** — `shard_per_process=True` gives each CI worker its own **lock-free** shard (`{stem}.{shard-id}{suffix}`, identity `pid-host_token-start_token`), with `read_recent` merging all shards by `logged_at` (plus a bare single-file path, mode cross-compat) and `compact` working per shard; (3) **dead-shard reaping** — `compact(reap_after_seconds=...)` deletes shards from exited processes (on by default at a conservative one week; `None` disables; own shard and bare file never reaped). This was the project's first **prospective** RFC (written before any code, fixing scope up front — the "RFC-first" discipline). The RFC v1.6 §6 tail is now fully discharged. Public API: **48 stable symbols** (unchanged across the entire v1.7 line; +0); `API_VERSION` unchanged at `"1.0"` across all twelve releases v1.0.0 → v1.7.0. 457 pytest + 8 verification = **465/465**; 14/15 acceptance criteria met (live-Figma deferred to operator pilot, per v1.1–v1.6 precedent). RFC: [`docs/rfc/v1.7-granularity-and-scale-out.md`](docs/rfc/v1.7-granularity-and-scale-out.md) (Accepted & Shipped).
**Position:** Operationalization layer in the SMP v1.0 ecosystem. Sits between strategy/identity skills (brand-visual, brand-platform) and consumption skills (roche-design, frontend-design).

---

## 1. What This Skill Does (Purpose)

`figma-forge` is the operationalization layer that turns a **design-system specification** into a **publish-ready Figma library ecosystem**. It accepts three classes of input:

1. **W3C DTCG JSON** — the community-standard token format (`$value`, `$type`, `$description`) from the Design Tokens Community Group at the W3C.
2. **Style Dictionary export** — Amazon's multi-platform DS tooling format (`tokens.json` or per-file output).
3. **Built-in DS reference** — name an established system (Carbon v11, Material 3, Tailwind v3/v4), and the skill maps its canonical tokens via bundled translation tables.

It then produces, depending on the active mode:

- a **multi-file Figma architecture** with `Foundations`, `Components`, `Patterns`, and `Icons` files, each with proper team library structure (`SCAFFOLD`)
- **Figma Variables** (modes, collections, primitive + semantic layers) and **paint/text/effect styles** that bridge tokens to Figma's native rendering (`TOKENS_IMPORT`)
- **Foundation primitives** — type ramp with line-heights and letter-spacing, color tokens grouped by hue + role, layout grids (4/8 baseline), elevation/shadow ramps (`FOUNDATIONS_BUILD`)
- **Variant-aware components** with auto-layout, boolean properties, instance swap properties, and state variants (default/hover/pressed/disabled/focus) (`COMPONENTS_BUILD`)
- **Adapted forks of established systems** — e.g., Material 3 baseline tokens overlaid with brand primary + custom font family (`MIGRATE`)
- **Code Connect stubs** — `.figma.tsx` or `.figma.html` files mapping Figma nodes to code components in a target repo (`CODE_CONNECT`)
- a **19-gate publish-readiness audit** detecting orphan styles, missing tokens, naming-convention violations, missing variants, library-asset hygiene failures (`PUBLISH_AUDIT`)

---

## 2. Limitations / Out-of-Scope (What This Skill Is NOT)

- It is **not** an identity-design protocol. Choosing brand palette, type ramp, or archetype is `brand-visual`'s job — `figma-forge` takes those decisions as input.
- It is **not** a brand-naming or strategic-positioning tool. Use `brand-platform`, `brand-maker`.
- It is **not** a runtime DS consumer. Once the library is published, downstream skills like `roche-design` or `frontend-design` consume it. `figma-forge` builds; they use.
- It is **not** a Figma file viewer or screenshot tool — `Figma:get_screenshot` and the regular `Figma:get_design_context` handle that.
- It is **not** a frontend code generator. It produces Code Connect *mapping* stubs (Figma↔code wiring); actual component code lives in your repo or `frontend-design`'s domain.
- It does **not** create the brand's design philosophy. It executes specifications.

---

## 3. When to Invoke

| If your task is... | Mode |
|---|---|
| Set up empty Figma file structure for a new DS | `SCAFFOLD` |
| Import token JSON (DTCG/Style Dict) into Figma Variables | `TOKENS_IMPORT` |
| Build type ramp, color styles, grids, elevations from tokens | `FOUNDATIONS_BUILD` |
| Build variant-aware library components (Button, Input, Card...) | `COMPONENTS_BUILD` |
| Adapt Carbon/Material 3/Tailwind to a branded local fork | `MIGRATE` |
| Generate Code Connect mappings to a code repo | `CODE_CONNECT` |
| Pre-publish audit of an existing Figma file | `PUBLISH_AUDIT` |

Trigger keywords (Turkish + English): *Figma kütüphanesi, design system Figma, token import, Variables API, DTCG, Carbon Figma library, Material 3 Figma, Tailwind tokens, design system scaffold, library publish, Code Connect, component variants, build Figma library, library audit, orphan styles, "Figma'da kütüphane kur", "DS'yi Figma'ya çek", "Carbon kütüphanesi forge'la"*.

---

## 4. The Three-Channel Connection Strategy

Different Figma plans, tenants, and tasks support different write paths. `figma-forge` uses a **deterministic fallback chain** to maximize the chance of success on whatever account the user has.

### Channel 1: Figma MCP (default — try first)

The Figma MCP exposes agentic tools that can create, edit, and read Figma files:

| MCP Tool | Use in figma-forge |
|---|---|
| `Figma:create_new_file` | `SCAFFOLD` mode — create empty file per layer |
| `Figma:use_figma` | All build modes — create nodes, components, variants |
| `Figma:get_design_context` | Read existing file structure (audit, migration) |
| `Figma:get_variable_defs` | Read existing variables (audit, migration) |
| `Figma:search_design_system` | Find existing components to extend |
| `Figma:get_libraries` | Discover linked libraries for the target file |
| `Figma:add_code_connect_map` | Code Connect mapping (single node) |
| `Figma:send_code_connect_mappings` | Code Connect bulk save |
| `Figma:get_code_connect_suggestions` | AI-suggested mappings |
| `Figma:get_metadata` | File-level metadata for audit |

**Strength:** Native, agentic, no Enterprise plan required for most operations.
**Weakness:** `use_figma` for complex variants (boolean/instance-swap props, interactive states) is still best-effort. For these, fall back to Channel 3.

### Channel 2: Figma REST API (fallback for Variables write)

Use when MCP cannot handle the operation, or when the target file requires the **Variables API** (the only programmatic write path for Figma Variables — and **available only on the Enterprise plan**).

Endpoints used:

- `GET /v1/files/:file_key` — file read
- `GET /v1/files/:file_key/variables/local` — read local variables (any plan)
- `POST /v1/files/:file_key/variables` — write variables (**Enterprise only**)
- `GET /v1/files/:file_key/styles` — read styles
- `GET /v1/teams/:team_id/styles` — team library styles
- `POST /v1/files/:file_key/library_publish` — publish library

Authentication: `X-Figma-Token: <PAT>` header. Skill prompts the user for their PAT when entering REST mode. **Never log or persist the PAT.** See `references/figma-rest-api.md`.

### Channel 3: TypeScript Plugin Fallback (last resort, but most reliable)

When neither MCP nor REST suffices (e.g., user is on Professional plan and needs Variables import), `figma-forge` generates a **complete Figma plugin** — `manifest.json` + `code.ts` — that the user imports into Figma via *Plugins → Development → Import plugin from manifest*. The plugin then reads a JSON file the user uploads in-Figma and writes Variables using the Plugin API (`figma.variables.createVariable`, `figma.variables.createVariableCollection`).

**Strength:** Works on every Figma plan (Free, Starter, Professional, Organization, Enterprise). The Plugin API is the most powerful Figma write surface.
**Weakness:** Requires user to import the plugin once and run it manually.

See `templates/figma-plugin/` for the bundled plugin template.

### Channel Selection Decision Tree

```
Is the operation TOKENS_IMPORT (writing Variables)?
├── YES → Is user on Figma Enterprise?
│           ├── YES → Channel 2 (REST API) — fastest path
│           └── NO  → Channel 3 (Plugin) — only reliable path
└── NO (other build mode)
    ├── First try → Channel 1 (Figma MCP use_figma)
    ├── Fallback path when the Figma MCP cannot express the construct → Channel 3 (Plugin)
    └── For reading existing file → Channel 1 (Figma MCP get_design_context)
```

---

## 5. The Eight Working Modes

Each mode has a precondition (what the skill needs to know before starting), a workflow (what the skill does), and a postcondition (what the user gets out).

### Mode 1: `SCAFFOLD`

**Precondition:** A name for the DS, a chosen architecture (default: 4-file Foundations/Components/Patterns/Icons).
**Workflow:** Create 4 empty Figma files via `Figma:create_new_file`. Set canonical naming: `<DS Name> — Foundations`, etc. Establish file-key registry in output.
**Postcondition:** 4 file URLs + a `library-registry.json` mapping layer → file_key.

### Mode 2: `TOKENS_IMPORT`

**Precondition:** Token source identified — DTCG JSON, Style Dictionary export, or named built-in DS.
**Workflow:**
1. Normalize input → canonical DTCG-shaped intermediate.
2. Group tokens into **collections** (Primitives, Semantic, Component) and **modes** (Light/Dark, Density, Brand variant if multi-brand).
3. Choose Channel (2 if Enterprise, else 3 — never 1 for Variables; MCP `use_figma` does not reliably handle Variables yet).
4. Push: REST batch POST or plugin write.
5. Cross-link semantic variables to primitives (alias resolution).
6. Produce paint styles + text styles for legacy consumption (Variables are newer; styles still required for many older consumer files).

**Postcondition:** Variables published to the Foundations file; alias map preserved; legacy styles created; intermediate DTCG JSON saved.

See `references/w3c-dtcg-tokens.md` and `references/figma-plugin-fallback.md`.

### Mode 3: `FOUNDATIONS_BUILD`

**Precondition:** `TOKENS_IMPORT` completed (Foundations file has variables).
**Workflow:**
1. Build **type ramp** — for each text token, create a Figma text style bound to font-family/weight/size/line-height/letter-spacing variables.
2. Build **color system swatches** — visual frames in the Foundations file showing each color token with name, hex, contrast info.
3. Build **layout grids** — column grids (4/8/12 cols), row grids, baseline grids tied to spacing tokens.
4. Build **elevation/shadow ramp** — effect styles per elevation token.
5. Build **radius scale** — corner-radius variables wired into a visual scale.
6. Generate a **Foundations cover page** with auto-layout summarizing the system.

**Postcondition:** Foundations file is publish-ready.

### Mode 4: `COMPONENTS_BUILD`

**Precondition:** Foundations file is published or about to be (its variables/styles must be linked into the Components file).
**Workflow:**
1. Establish Components file structure: one page per component family (Buttons, Inputs, Surfaces, Navigation, Feedback, Data Display).
2. For each component spec (input JSON or built-in mapper):
   - Create the base node with auto-layout.
   - Bind colors/typography/spacing to Foundations variables (no hard-coded values).
   - Create boolean variants (e.g., `iconLeading`, `iconTrailing`).
   - Create enum variants (`size: sm|md|lg`, `state: default|hover|pressed|disabled|focus`).
   - Create instance-swap properties for slot content.
   - Add component description (Markdown), keywords, and the Code Connect tag if Channel 1 supports it.
3. Validate: every paint must come from a variable; no detached overrides.
4. Stage in a "candidate" page, then promote to publishable pages.

**Postcondition:** Components file populated with publish-ready variant-aware components.

See `references/component-spec-templates.md`.

### Mode 5: `MIGRATE`

**Precondition:** A reference DS named (Carbon v11, Material 3, Tailwind v3 or v4) AND a brand overlay specification (e.g., primary color override, font family override, density overlay).
**Workflow:**
1. Load the reference DS canonical token table from `references/<ds>-mapping.md`.
2. Apply brand overlay: override specific token values while preserving structure.
3. Pipe through `TOKENS_IMPORT` → `FOUNDATIONS_BUILD` → `COMPONENTS_BUILD`.
4. Generate a **migration delta report** showing what's identical to reference vs. what's branded.

**Postcondition:** A branded local fork of the reference DS in Figma, with migration delta documented for future reference-DS updates.

### Mode 6: `CODE_CONNECT`

**Precondition:** A target code repo with components, AND the Components Figma file published.
**Workflow:**
1. Discover components in the Figma file via `Figma:search_design_system` or `Figma:get_design_context`.
2. For each component, generate a `.figma.tsx` (React), `.figma.ts` (Web Components), or `.figma.html` stub.
3. Use `Figma:get_code_connect_suggestions` for AI-suggested mappings where available.
4. Bulk save via `Figma:send_code_connect_mappings`.

**Postcondition:** Code Connect stubs in the target repo + Figma node-to-code map persisted.

See `references/code-connect-patterns.md`.

### Mode 7: `PUBLISH_AUDIT`

**Precondition:** A Figma file or library that the user believes is ready to publish.
**Workflow:** Run the 19-gate publish checklist (see `references/publish-checklist.md`). Each gate is either pass/fail or warn. The output is a Markdown report with gate-by-gate diagnosis and concrete remediation guidance.

**Postcondition:** A `publish-audit.md` report. If all error-severity gates pass, the file is publish-ready.

### Mode 8: `AUTO_REMEDIATE` *(v0.3.0-rc)*

**Precondition:** A `publish_audit` report (Markdown or JSON) that contains at least one FAIL/WARN gate, plus the static source-of-truth bundle (DTCG tokens, component specs, code-connect mappings, library-registry, SVG icons).

**Workflow:** Parse the audit report → for each FAIL/WARN gate, look up a registered :class:`RemediationStrategy` → call its `plan(failure, ctx)` to produce concrete :class:`RemediationAction` objects → render each action to the chosen output channel (`pr` for git diff/patch, `plugin` for Figma TS script). The framework is side-effect-free until the CLI's apply step writes patches to disk.

**Seven strategies in rc.1:**

| Gate | Strategy | Channels | Closes lesson |
|------|----------|----------|---------------|
| **G02** | Composite typography → text-styles router | pr · plugin | L2 |
| **G07** | Variant matrix Cartesian product calculator | pr | L5 |
| **G08** | Component naming PascalCase rewriter | pr | — |
| **G13** | DTCG alias path normalizer | pr | L1 |
| **G14** | Icon SVG canonical normalizer | pr | L6 |
| **G15** | Icon size grid normalizer | pr | — |
| **G17** | Code Connect mapping generator | pr | L9 |

**Postcondition:** A `remediations/` directory containing either unified-diff `.patch` files (PR channel, one per action) or a single consolidated `figma-forge-remediations.ts` script (plugin channel), plus a `_summary.json` machine-readable index. Patches apply cleanly via `git apply`; the TS script pastes into Figma → Plugins → Development → Open Console.

**CLI:** `python3 scripts/auto_remediate.py --audit-report <path> --library-dir <dir> --output-channel pr|plugin [--strategies 2,7,8,13,14,15,17] [--locale tr-TR|en-US] [--dry-run] [--apply]`

**Empirical grounding:** Every strategy traces back to a Düstur build friction point. **G07 caught Düstur's Button spec bug** (`expected_count: 60` vs 4×3×5 − 1 disabled = 59) on its first end-to-end run. **G15 caught a second inconsistency** — 6 document SVGs at 24×24 vs default doc grid `[32, 48]`; resolved by `library-registry.icon_size_grid` override (defensive design validated).

### Mode 9: `ORCHESTRATE` *(v0.3.0-rc, new)*

**Precondition:** A library bundle with an `orchestration.json` manifest declaring an ordered pipeline of stages.

**Workflow:** Parse manifest → for each stage spec, dispatch to its registered `Stage` executor → aggregate per-stage `StageResult` records. Live scaffolds (SCAFFOLD / FOUNDATIONS_BUILD / COMPONENTS_BUILD / ICONS_BUILD / PATTERNS_BUILD / CODE_CONNECT / PUBLISH) defer to the v0.4.0 transport layer with structured "would have executed" log entries; real executors (TOKENS_IMPORT, PUBLISH_AUDIT, AUTO_REMEDIATE) shell out to sibling scripts and succeed today.

**Three execution modes**: default (fail-fast), `--dry-run` (zero I/O), `--resume <STAGE>` (skip stages strictly before the named one — by mode name or 1-indexed integer). `--only <modes>` restricts to a subset; `--continue-on-failure` overrides fail-fast.

**Postcondition:** Pipeline executed (or planned), with `orchestrate-summary.json` written alongside the manifest containing per-stage status, duration, artifacts, and any errors. Exit 0 = all stages succeeded, 1 = at least one failed, 2 = cannot run (invalid manifest / missing library).

**CLI:** `python3 scripts/orchestrate.py --manifest orchestration.json --library-dir <dir> [--dry-run] [--resume <stage>] [--only <modes>] [--continue-on-failure] [--locale en-US|tr-TR] [--list-stages] [--validate-only]`

**Closes Düstur build lesson L8.**

### Mode 10: `BUNDLE_MANIFEST` *(v0.3.0-rc, new)*

**Precondition:** A library bundle directory (DTCG tokens + component specs + code-connect mappings + SVG icons + library-registry).

**Workflow:** Walk the bundle (skipping `__pycache__`, `.git`, `node_modules`, `.DS_Store`, etc.) → compute SHA-256 for each file → categorize by canonical path prefix (`tokens.primitive`, `tokens.semantic`, `tokens.merged`, `components.spec`, `patterns.spec`, `code-connect.mapping`, `icons.tier-svg`, `icons.selcuklu-svg`, `icons.legal-svg`, `icons.generic-svg`, `icons.spec`, `docs`, `remediations`, `root`) → emit schema-v1.0 `manifest.json`.

**Verify mode** (`--verify`): re-compute the manifest fresh, diff against the on-disk version, surface `ADDED:` / `REMOVED:` / `CHANGED:` lines. Exit 1 on drift, 0 on match.

**Postcondition:** `manifest.json` written; bundle integrity check passes against any future re-computation until intentional modification.

**CLI:** `python3 scripts/bundle_manifest.py --library-dir <dir> [--output manifest.json] [--bundle-name X] [--bundle-version Y] [--verify]`

**Closes Düstur build lesson L7.** Düstur's 103-file bundle has a deterministic, supply-chain-attestable inventory (input ready for v1.0.0 Sigstore/Cosign signing).

### Mode 11: `AUDIT_DIFF` *(v0.3.1-alpha, new)*

**Precondition:** Two schema-v1.0 audit JSON reports produced by `publish_audit.py --output-format json` (or static-lint equivalent) — typically the baseline from the `main` branch and the current from the PR branch.

**Workflow:** Load both snapshots → iterate the union of gate ids → classify each transition (regression / improvement / no_change / new / removed) using a severity-aware result ordinal that promotes PASS, demotes FAIL by severity (error worst, warn middle, info mildest), and treats SKIP / N_A as neutral → diff sample-level failure messages set-wise → aggregate into a `DiffReport` carrying score delta, band shift, regression list, improvement list. Three exit modes: `--fail-on regression` (default; exit 1 on any regression), `--fail-on any-change` (exit 1 on any movement), `--fail-on never` (always exit 0).

**Postcondition:** A schema-v1.0 diff document written in Markdown (PR-comment friendly, with regression and improvement sections, sample-level resolved/introduced lines, band-shift symbols) or JSON (CI-friendly, gate on `summary.regressions > 0`). Exit code semantics support CI gating directly.

**CLI:** `python3 scripts/audit_diff.py --baseline <baseline.json> --current <current.json> [--output diff.md] [--output-format markdown|json] [--fail-on regression|any-change|never]`

**Closes Düstur build lesson L10** (calibration delta). The diff JSON shape is the input format consumed by Mode 12 (`AUDIT_TREND`).

### Mode 12: `AUDIT_TREND` *(v0.3.1 GA, new)*

**Precondition:** N ≥ 2 schema-v1.0 audit JSON reports (typically a rolling 30-day or 90-day window of daily audits, accumulated by a scheduled CI job).

**Workflow:** Load all snapshots into time-ordered series → compute score statistics (mean, stdev, min, max, OLS slope per-audit and per-day) → compute **Calibration Drift Index** (σ/μ; thresholds: 0 perfectly stable, <0.02 stable, <0.05 minor, <0.10 moderate, ≥0.10 high) → tabulate band frequency distribution → for each gate, count observations, fail ratio, P→F + F→P transitions, derive stability label (stable / improving / regressing / flapping / absent), compute **Mean Time To Fix** (mean audit gap between FAIL appearance and return to PASS, when a fix occurred within the window). Date-range filtering via `--since`/`--until`.

**Postcondition:** A trend report in one of three forms — (a) schema-v1.0 JSON (downstream tooling, future v0.4.0+ web dashboards); (b) Markdown (PR comment with score summary, band distribution bars, gate stability table, per-audit series); (c) **single-file HTML dashboard** with inline SVG sparkline, dependency-free, dark-themed, drop-in for CI artifact servers or GitHub Pages. Optional `--fail-on-high-drift` exits 1 when CDI > 0.10.

**CLI:** `python3 scripts/audit_trend.py [--glob 'audits/*.json' | --inputs path1.json path2.json ...] [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--output trend.html] [--output-format markdown|json|html] [--fail-on-high-drift]`

**Empirical validation:** Synthetic 10-audit Düstur tarihçesi spanning 9 days with deliberate 3-audit regression — analyzer correctly produced μ=9.39, σ=0.93, CDI=0.0994 (moderate drift), score slope ↗ +0.0964/audit, G102 flagged as flapping with MTTF=3.0 audits. HTML dashboard rendered 139-line single-file output with inline SVG polyline + dashed reference line at score=8 (STRONG threshold).

---

## 6. The Library Architecture (Default Layout)

The default Figma library architecture is a **4-file split**, a convention common to mature modular design systems (Material 3, IBM Carbon, and many enterprise systems organize their Figma libraries this way):

```
<DS Name> — Foundations    ← Variables, paint/text/effect styles, grids,
                             elevation, radius, spacing primitives
                             (Consumed by: every other file)

<DS Name> — Components     ← Variant-aware base components (Button, Input,
                             Tag, Card, Modal, Tooltip, etc.)
                             (Consumes: Foundations)
                             (Consumed by: Patterns + product files)

<DS Name> — Patterns       ← Compositional patterns (Form, DataTable,
                             EmptyState, OnboardingFlow, etc.)
                             (Consumes: Foundations + Components)

<DS Name> — Icons          ← Iconography library (SVG-imported components)
                             (Consumed by: Components + Patterns)
```

For smaller systems, the architecture can collapse to **2-file** (Foundations + Components) or even **1-file**. The skill asks the user which depth they want during `SCAFFOLD`.

For larger systems (some enterprise design systems use a 5-file split with Data Visualization separated into its own library), additional layers can be added — but **never publish-cycle layers below Foundations**; the Foundations file is always atomic.

---

## 7. Token-to-Figma Mapping Logic

Tokens map to Figma constructs via this canonical table:

| Token type ($type) | Figma construct | Channel notes |
|---|---|---|
| `color` | Variable (`COLOR` resolved type) + paint style | Variables: Channel 2/3. Paint style: Channel 1. |
| `dimension` (spacing, radius) | Variable (`FLOAT`) | Channel 2/3 only |
| `fontFamily` | Variable (`STRING`) bound to font name | Channel 2/3 (note: Figma fonts must be installed) |
| `fontWeight` | Variable (`FLOAT`) — 100-900 | Channel 2/3 |
| `dimension` (fontSize) | Variable (`FLOAT`) | Channel 2/3 |
| `dimension` (lineHeight) | Variable (`FLOAT`) | Channel 2/3 |
| `dimension` (letterSpacing) | Variable (`FLOAT`) | Channel 2/3 |
| `typography` (composite) | Text style bound to component variables | Channel 1/3 |
| `shadow` (composite) | Effect style + (optional) component variable references | Channel 1/3 |
| `gradient` (composite) | Paint style (Figma supports gradient paints) | Channel 1/3 |
| `cubicBezier` (motion) | Not natively supported; documented in description metadata | N/A — saved as metadata |
| `duration` (motion) | Not natively supported; documented in description metadata | N/A |
| `transition` (composite) | Not natively supported | N/A |

**Alias resolution:** A DTCG alias like `{color.primary.500}` resolves to either a direct value (if target is primitive) or another variable (if Figma supports cross-variable aliasing — which it does, in Channel 2/3). The skill builds a topological order before pushing to Figma so aliases are always defined after their targets.

---

## 8. Built-in Mapper Routing

When the user names a known DS, the skill loads the canonical token table from `references/`:

| User says... | Skill loads | Notes |
|---|---|---|
| "Carbon", "IBM Carbon", "Carbon v11", "carbon-react" | `references/carbon-mapping.md` | Maps all g10/g90/g100 themes, IBM Plex type ramp |
| "Material 3", "M3", "Material You", "material-design-3" | `references/material3-mapping.md` | Baseline tokens; user supplies brand primary for dynamic color generation |
| "Tailwind", "Tailwind CSS", "TW v3", "TW v4" | `references/tailwind-mapping.md` | Tailwind utility scale → DTCG; v4 uses CSS @theme |
| "Custom" or DTCG JSON path | Use input directly | DTCG-shaped |
| Style Dictionary | `scripts/style_dict_to_dtcg.py` first | Normalize → DTCG |

---

## 9. Output Contract

Every figma-forge run produces, at minimum:

1. A **run report** — `figma-forge-run-<timestamp>.md` summarizing what was done, which channel(s) used, what succeeded/failed, what the user should do next manually.
2. A **library registry** — `library-registry.json` mapping layer → file_key → URL, with linked-library declarations.
3. The **canonical DTCG intermediate** — `tokens.dtcg.json` saved even if input was Style Dictionary or built-in mapper (preserved for future round-tripping).
4. For Channel 3 runs: the **plugin bundle** — `figma-forge-plugin.zip` with `manifest.json`, `code.ts`, and `ui.html` ready to import into Figma.

For `PUBLISH_AUDIT` runs, additionally: `publish-audit.md`.

---

## 10. Quality Gates (19-Gate Publish Checklist)

The full gate list is in `references/publish-checklist.md`. The summary:

| # | Gate | Severity |
|---|---|---|
| 1 | All color paints come from a variable (no hard-coded hex) | error |
| 2 | All text uses a text style (no detached typography) | error |
| 3 | No orphan styles (every published style is referenced somewhere) | warn |
| 4 | No missing variable references (every alias resolves) | error |
| 5 | All components have descriptions (markdown) | warn |
| 6 | All components have keywords for search | warn |
| 7 | Every variant axis is fully populated (no empty variants) | error |
| 8 | Component naming follows convention (Pascal/BEM/Material) | warn |
| 9 | Variant property naming follows convention (camelCase or kebab) | warn |
| 10 | Foundations file has cover page | warn |
| 11 | Each component family has a section header | warn |
| 12 | No unpublished local styles in a publishable file | warn |
| 13 | Effect styles are bound to elevation tokens | warn |
| 14 | All icons are components (not raw SVG nodes) | error |
| 15 | All icons follow size/grid convention | warn |
| 16 | Library has at least one mode (Light) defined per collection | error |
| 17 | Component descriptions reference Code Connect status | info |
| 18 | License/version/contact metadata present in cover page | warn |
| 19 | No detached instance overrides outside the candidate page | warn |

`PUBLISH_AUDIT` mode runs all 19 gates and reports.

### Implementation status

As of figma-forge **v0.2.0**, **all 19 gates have registered checker functions**. The audit engine no longer reports `skip` results for missing implementations — every gate either passes, fails (with at least one concrete failure entry), or returns `n_a` when its preconditions are not met (e.g., G8 component-naming requires a `LibraryRegistry` and degrades to `n_a` in v0.1.x-style single-file mode).

Coverage progression:

| Sprint | Gates added | Cumulative |
|--------|-------------|-----------|
| v0.1.x baseline | G1, G2, G5, G16 | 4/19 |
| v0.2.0 Sprint 1 | G3, G4, G10, G12, G17, G18 | 10/19 |
| v0.2.0 Sprint 2 | G7, G8, G9, G11, G19 | 15/19 |
| v0.2.0 Sprint 3 | G6, G13, G14, G15 | **19/19** |

The publish-audit framework runs three test suites that must all pass before release: 8 SMP self-validation gates (`tests/run_tests.py`), 37 per-gate isolation tests against synthetic fixtures (`tests/test_publish_audit.py`), and 7 end-to-end multi-file scenarios (`tests/test_publish_audit_e2e.py`). See `references/publish-checklist.md` for the full per-gate implementation matrix.

### Calibration framework (v0.2.1)

Four heuristic gates — G7, G13, G14, G15 — make graded, threshold-dependent decisions. As of v0.2.1, each has an opt-in **calibration probe** that captures the feature distributions and boundary decisions it observes during an audit run. Operators enable calibration by passing `--calibration-mode` to the CLI; the probe output is written to a local JSON sidecar (default: `calibration.json`) and never transmitted off-device. The skill maintainer can offline-analyze multiple anonymized sidecars (`tools/calibration_analyzer.py`) to propose evidence-driven threshold adjustments in future releases. See `references/calibration-methodology.md` for the complete operator + maintainer workflow and the privacy governance regime.

---

## 11. Composability (SMP v1.0)

`figma-forge` is a clean composability hub:

**Upstream (pipe_from):**
- `brand-visual` — visual identity tokens (palette, type ramp, archetype) feed into TOKENS_IMPORT
- `brand-platform` — brand voice/personality informs component description copy
- `brand-maker` — verbal identity provides DS name + naming conventions
- `brand-audit` — competitive audit informs differentiation in token + component design

**Downstream (pipe_to):**
- `roche-design` — one example of a design-system-specific consumer: when a library is published, a DS-specific skill (such as roche-design for the Roche Design System) can consume its outputs. figma-forge itself is design-system-agnostic; this is just one possible downstream binding.
- `brand-touchpoint` — touchpoint specifications cite the published Figma library
- `frontend-design` — frontend code generation uses Code Connect mappings as ground truth
- `carbon-html-report` / `carbon-pptx` — deliverable generators can use forged Carbon-derived tokens
- `smp-orchestrator` — audits the resulting library's manifest

See `skill-manifest.yaml` for formal composition declarations.

---

## 12. Reference Files

| File | When to read |
|---|---|
| `references/figma-mcp-cookbook.md` | Building any Channel-1 invocation; details every Figma MCP tool with input/output examples |
| `references/figma-rest-api.md` | Channel-2 fallback; REST endpoints + Variables API specifics |
| `references/figma-plugin-fallback.md` | Channel-3 fallback; how to ship the plugin to the user |
| `references/w3c-dtcg-tokens.md` | Whenever input is DTCG JSON; the schema authority |
| `references/style-dictionary.md` | Whenever input is Style Dictionary; the conversion rules |
| `references/carbon-mapping.md` | `MIGRATE` mode with Carbon as source |
| `references/material3-mapping.md` | `MIGRATE` mode with Material 3 as source |
| `references/tailwind-mapping.md` | `MIGRATE` mode with Tailwind as source |
| `references/library-architecture.md` | `SCAFFOLD` mode; multi-file split logic |
| `references/component-spec-templates.md` | `COMPONENTS_BUILD` mode; component JSON spec schema |
| `references/code-connect-patterns.md` | `CODE_CONNECT` mode; per-framework stub templates |
| `references/naming-conventions.md` | All build modes; BEM / Carbon / Material naming |
| `references/publish-checklist.md` | `PUBLISH_AUDIT` mode; all 19 gates with remediation |

For large refs (>300 lines), each file opens with its own table of contents.

---

## 13. Conventions and Style

Throughout this skill, prefer **explicit reasoning over rigid MUSTs**. When the skill instructs the consumer model to do something, it explains why — because the consumer model is smart and operates better with intent than with prohibitions.

Naming: when in doubt, follow Carbon's `kebab-case` for tokens and `PascalCase` for components. Variant property names are camelCase. These are not religious — adapt to the source DS being mapped.

Mode handoffs: a mode may invoke another mode internally (e.g., `MIGRATE` invokes `TOKENS_IMPORT` then `FOUNDATIONS_BUILD` then `COMPONENTS_BUILD`). When this happens, the run report records the chain.

Channel handoffs: if Channel 1 cannot express a construct, fall through to Channel 3 silently — but **always** log the channel switch in the run report so the user understands what happened.

---

## 14. Failure modes and recovery

**Figma MCP not connected:** Skip Channel 1 entirely; route through Channel 2 (if Enterprise + PAT) or Channel 3 (always available).

**User on Free/Starter/Professional plan + needs Variables:** Channel 3 is the only path. Generate the plugin bundle, walk the user through plugin import, hand off the JSON for the user to upload in-plugin.

**Font not installed in user's Figma:** Text styles will be created but render as fallback. The skill warns the user in the run report and lists the missing fonts with download/installation links if known (e.g., IBM Plex via Google Fonts, Roboto, Inter).

**Variables API rate limit hit (REST):** Back off with exponential delay (2s, 4s, 8s, 16s, 32s, then fail). Resume token-import from the last successful batch.

**Variant explosion (too many variants):** If a component spec yields >256 variants (Figma's practical limit), the skill warns and suggests collapsing axes. Default: warn at 64 variants.

**Aliased token target not found:** Halt push; report the broken alias; ask user to fix the source spec.

---

## 15. Maturity and Stability

**figma-forge v1.x is stable and feature-complete** (declared 2026-05-30; see [`docs/rfc/v1.x-maturity-and-stability.md`](docs/rfc/v1.x-maturity-and-stability.md)).

Across eight minor releases (v1.0.0 → v1.7.0), the public API grew from 22 to 48 symbols — **every change additive, zero breaking, zero retired symbols** — while `API_VERSION` stayed `"1.0"` throughout. The deferral lists of v1.4, v1.5, and v1.6 are all discharged; the core capability set (twelve modes, three transport channels, the 19-gate publish checklist, the self-tuning concurrency runtime, the durable scale-out observation log) is complete.

The line is now in **maintenance mode**. For any proposed change:

1. **Breaks something** (signature, default, wire format)? → a v2.0 question, out of scope for v1.x (not currently planned).
2. **Fixes a defect, or corrects docs / tests / live-Figma fidelity?** → patch (v1.7.x).
3. **Adds capability for a real, encountered need?** → minor (v1.8.0+), RFC-first, strictly additive and default-preserving.
4. **Speculative / "nice to have"?** → declined; the idea is recorded, not built.

**Stability guarantees for the life of v1.x:** the 48 public symbols retain their names and signatures (fields and keyword parameters may be added, never removed or redefined); `API_VERSION` stays `"1.0"`; any v1.x release runs any artifact or configuration produced by an earlier v1.x release; new parameters default to prior behavior.

**The one open item:** a live-Figma integration test against a real Figma file under a real PAT, deferred at every GA because the test environment has no network. The mock-server suite reaches functional parity; real-network confirmation is left to an operator pilot. This is the only forward work the maturity charter keeps open.

---

End of SKILL.md. For mode-specific workflows in depth, see the referenced files in `references/`.
