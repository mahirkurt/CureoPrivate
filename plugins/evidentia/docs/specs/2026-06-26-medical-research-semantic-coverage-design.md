# Design — medical-research Semantic Coverage Mechanism (v8.3)

> Status: APPROVED (brainstorming) · 2026-06-26 · target skill: `evidentia / medical-research` v8.2.0 → **v8.3.0**
> Approach: **C (Hybrid)** — Claude-native semantic backbone (always-on) + optional `evidentia-kb` vector booster (graceful-degrade).

## 1. Problem

`medical-research` scans its own ~90 KB / ~22 k-token knowledge base (`SKILL.md` + ~20 `references/*.md` layer files) via **lexical keyword-signal routing** (Adım 0.5): each axis carries *representative* keyword triggers in `SKILL.md`, with the full keyword dictionaries hidden inside the layer files (progressive disclosure). A layer loads only when its keywords fire.

This produces four failure modes the user wants eliminated (all four selected):

1. **Recall gap** — a question phrased without the trigger words fails to load the relevant layer (lexical ≠ semantic).
2. **Cross-axis blindness** — a multi-domain question loads only the top axis; sibling axes (e.g. heme + regulatory + HTA + Türkiye) are skipped.
3. **Depth/detail loss** — a loaded layer is summarised, dropping sub-details.
4. **Inconsistent coverage** — the same question is sometimes scanned broadly, sometimes narrowly; non-deterministic.

**Goal:** the skill must scan its KB **semantically, in the context of the question, at the widest consistent and correct scope, without skipping details.**

## 2. Non-goals

- Not rewriting the v8.2 core. The mechanism is **additive** (ADR-05 preservation): it sits *above* the existing Adım 0 / 0.5 / layer machinery and feeds it a superset; existing files keep their content.
- Not indexing external evidence (that is what the main `anamnesis` Worker already does, separately). This mechanism indexes only the skill's **own static KB**.
- No global GraphRAG / community summarisation over the KB. Out of scope.

## 3. Architecture overview

Two cooperating layers; the backbone alone satisfies all four goals on every surface, the booster only raises recall when reachable.

```
question
  │
  ├─(0.4) Semantic Scope Scan  ── reads knowledge-map.md ──►  coverage_set  (axes + sections, written out)
  │            └─(optional) kb_search(question) ──► merge top-k KB sections into coverage_set   [BOOSTER B]
  │
  ├─(0.5) existing layer loader  ── loads the UNION of coverage_set (mandatory multi-axis fan-out)
  │
  ├─ … existing research pipeline … (full-detail extraction discipline applied to every loaded section)
  │
  └─(N) Completeness Gate  ── re-scan knowledge-map (+ optional kb_search): any relevant axis/section/connector
                              NOT consulted? list gaps → load + address → only then finalise.
```

### Backbone A — Claude-native semantic coverage (always-on, deterministic, every surface)

**A1. `references/knowledge-map.md` (NEW, always-load).** The semantic index of the KB. Two complementary views:
- **Forward map** — one block per reference file: its sections, the **concept clusters** each section covers, **synonyms/related terms**, and **cross-axis links** ("also load when … is present").
- **Inverted map** — `concept → [file#section, …]` across the dimensions a medical question decomposes into: *disease/indication, drug/INN/brand, MoA/target/class, specialty axis, geography (TR/EU/US/global), regulatory angle, HTA/access angle, epidemiology/burden, evidence type, full-text/KOL/pipeline*.

The map is **semantic by construction**: Claude matches the question's *meaning* against rich concept clusters + synonyms, not against the question's literal tokens.

**A2. Adım 0.4 — Semantic Scope Scan (NEW, mandatory, runs BEFORE 0.5).** Fixed procedure:
1. Decompose the question into its concept set across the dimensions above.
2. For **each** concept, resolve **all** relevant sections via the inverted map (+ cross-axis links).
3. Emit an explicit, written **`coverage_set`** = the union of axes + sections. This artifact is auditable and is what makes coverage deterministic. **It lives in the invisible Ops/Layer-B sidecar** (alongside the existing "Cömertlik Garantisi" active-layers disclosure per `report-presentation.md`), **never in the visible clean-copy body** — it is a coverage-audit trail, not reader-facing content.

→ directly fixes **recall gap** + **cross-axis blindness**.

**A3. Mandatory multi-axis fan-out.** Adım 0.5's existing loader consumes `coverage_set` and loads the **union** of its axes/layers — never just the single highest-signal axis. The existing keyword fast-path remains as a floor (a keyword hit can only *add* to, never *shrink*, the coverage set).

**A4. Full-detail extraction discipline.** Every section in `coverage_set` is **loaded and its sub-details surfaced**, never summarised away. Tie-in to the existing `report-presentation.md` extraction doctrine: "loaded KB section ⇒ its specifics appear in reasoning/output; no silent compression." → fixes **depth/detail loss**.

**A5. Adım N — Completeness Gate (NEW, immediately before finalising).** A critic pass: re-scan `knowledge-map.md` against the question and the work done — *is there any axis, section, or connector relevant to this question that was NOT consulted?* Produce a gap list; if non-empty, load + address each; only then finalise. Deterministic and repeatable. → fixes **inconsistent coverage** and back-stops recall.

### Booster B — `evidentia-kb` Worker (separate, optional, graceful-degrade)

A **standalone** Cloudflare Worker (Cureonics Family-A: hardened OAuth 2.1 S256 + Bearer, McpAgent + DO), independent of the evidence `anamnesis` Worker so the static KB index is never touched by evidence ingest/purge.

- **One read-only tool: `kb_search(query, k=8) → ranked KB sections`** with provenance `{file, section, score}`. Returns bounded section pointers/snippets, not the whole corpus.
- **Storage:** own Vectorize index `evidentia-kb` (bge-m3, 1024-d cosine) + D1 `evidentia-kb-db` (`kb_chunks` table: file, section, text, ord). Reuses the proven anamnesis chunk/embed approach.
- **Ingest:** `scripts/kb_ingest.{py,sh}` walks `skills/medical-research/SKILL.md` + `references/*.md`, section-chunks them (by Markdown headings), embeds via the Worker, writes to `evidentia-kb`. Run once at setup; re-run on KB change (idempotent upsert keyed by `file#section`).
- **Wiring:** added to `.mcp.json` as a Tier-O entry; documented in `CONNECTORS.md` (g_bundle one-way gate).

**Graceful degradation (critical invariant):** Adım 0.4 and the Completeness Gate call `kb_search` **only if it is reachable**; if absent (e.g. claude.ai without the connector, or pre-deploy), the steps proceed **map-only** and still produce a complete `coverage_set`. The booster can only *add* recall, never gate the flow.

## 4. Determinism & verification

- The protocol is a fixed numbered sequence; `coverage_set` is written out explicitly (auditable, repeatable).
- **New gate `G-COVERAGE`** in `evals/check_integrity.py`: asserts `knowledge-map.md` is **exhaustive and consistent** with the real corpus — every reference file and every layer axis appears in the map; the map references no non-existent file/section (no dangling entries). Keeps the map from silently drifting from the layer files it indexes.
- Existing gates unchanged: `G-REF` / `G-ALWAYS` (knowledge-map.md added to the always-load set) / `G-VERSION` (8.2.0 → 8.3.0 across `SKILL.md` frontmatter + H1/changelog + `skill-manifest.yaml`).
- Booster gates: `evidentia-kb` typecheck + auth tests (Family-A pattern); post-deploy live smoke (`/health`, S256-only, 401/200, `kb_search` returns ranked sections); `g_bundle` consistency; `g_probe` 🔒401.

## 5. File-level change list

| File | Change |
|---|---|
| `references/knowledge-map.md` | **NEW** — forward + inverted semantic map of the whole KB |
| `SKILL.md` | **+ Adım 0.4** (Semantic Scope Scan) · **+ Completeness Gate** step · knowledge-map.md added to Adım-0 always-load · full-detail discipline note · **v8.3.0** stamps |
| `skill-manifest.yaml` | register `knowledge-map.md`; add `kb_search`/`evidentia-kb` to runtime.mcp_servers (optional/degradable); version → 8.3.0; add `G-COVERAGE` to gates |
| `evals/check_integrity.py` | **+ G-COVERAGE** gate (map ↔ corpus exhaustiveness/consistency) |
| `self-host/evidentia-kb-mcp/` | **NEW** Worker — `kb_search`; Vectorize `evidentia-kb` + D1; `auth.ts` (Family-A); tests; `BUILD-BRIEF.md` |
| `scripts/kb_ingest.{py,sh}` | **NEW** — section-chunk + embed + upsert the KB into `evidentia-kb` |
| `.mcp.json` + `CONNECTORS.md` | add `evidentia-kb` Tier-O entry (degradable) |
| `README.md` | note the semantic-coverage mechanism + kb_search |

## 6. Build order (high level; detailed plan via writing-plans)

1. **Backbone A first** (delivers the goal alone, every surface): knowledge-map.md → SKILL.md Adım 0.4 + Completeness Gate + v8.3 → G-COVERAGE gate → run gates.
2. **Booster B**: `evidentia-kb` Worker (build → typecheck/test → deploy → secrets → smoke) → `kb_ingest` (ingest the KB) → live `kb_search` E2E → wire `.mcp.json`/CONNECTORS.md → gates → reinstall.
3. Repackage zip + memory + keys-md.

## 7. Risks / mitigations

- **Map drift** (map and layer files diverge) → `G-COVERAGE` gate catches it.
- **Over-broad coverage / context bloat** → coverage_set is *relevant* sections, not "load everything"; full-detail discipline applies to the selected set; the existing "Cömertlik Garantisi" call-count ethos already accepts generous scanning.
- **Booster unreachable on claude.ai** → graceful degrade to A-only (explicit invariant).
- **bge-m3 over-engineering for 90 KB** → accepted as an *optional* recall booster only; A is the mandatory backbone.

## 8. Success criteria

- A multi-axis question (e.g. "tisagenlecleucel — global evidence + TR access + HTA + pipeline + KOL") loads heme + drug-intel + regulatory + HTA + Türkiye + KOL sections **without** relying on each trigger keyword being present — verifiably via the written `coverage_set`.
- `G-COVERAGE` green; map ↔ corpus consistent.
- `kb_search` (when connected) returns the same-or-superset of sections the map produced; A-only path is complete when it is absent.
- Coverage for a fixed question is **repeatable** across runs.
