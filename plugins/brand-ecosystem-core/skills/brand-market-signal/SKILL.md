---
name: brand-market-signal
description: >
  Turns brand-audit's competitive-landscape step from assumption into real
  market signal — share-of-voice, sentiment, and positioning white-space — by
  driving the EXISTING socius-vigil social-listening connector (not a new data
  service). USE for: share of voice, ses payı, brand sentiment, marka duyarlılığı,
  competitor mention volume, rakip analizi, white-space / beyaz alan, positioning
  gap, "how is our brand perceived", "who owns which message", market perception,
  buzz/mention tracking. Composes with brand-audit (diagnostic) and brand-maker
  (white-space feeds the naming brief). No fabrication — every number comes from
  a socius-vigil result and is triangulated; absence is reported as absence.
---

# brand-market-signal — Real Market Signal via socius-vigil

`brand-audit` and `brand-maker` both have a "competitive landscape / white-space"
step that is too often filled from assumption. This skill makes it **evidence-based**
by driving the already-deployed **`socius-vigil`** connector (social listening / OSINT:
SearXNG→Brave→DDG search chain + Perplexity/Exa enrichment + sentiment). It adds **no new
data source** — it is the *methodology* for using an existing one for brand questions.

> **Not a new MCP.** market-signal is deliberately a skill, not a Worker: socius-vigil
> already provides the data. A separate service would only re-package it.

## Prerequisite

The `socius-vigil` connector must be connected (Settings → Connectors, or `claude mcp`).
If it is **not** connected, say so plainly and stop — do **not** fabricate share-of-voice
or sentiment numbers. (Connector: `https://socius-vigil-mcp.cureonics.workers.dev/mcp`.)

## The three signals

### 1. Share of Voice (SOV) — who dominates the conversation

1. Build the competitor set (from the brief or brand-audit output): the brand + its 3–6
   closest competitors.
2. For each name, run `sv_search` (or `sv_collect_pipeline`) with a consistent query
   template and window (e.g. last 90 days). Use `sv_build_query_library` to keep the
   queries comparable across names.
3. **SOV = a brand's mention volume ÷ the total across the set.** Report the raw counts
   AND the share, and state the query/window used (so it is reproducible).
4. **Triangulate** with `sv_triangulate` and weight sources by `sv_admiralty_score` —
   a spike from one low-reliability source is not real SOV.

> **No-fabrication:** SOV is only as good as the counts socius-vigil returns. If a
> provider is degraded, report the degraded coverage, never a smoothed guess.

### 2. Sentiment — how the conversation feels

1. Run `sv_sentiment` on the brand's mention set (and optionally each competitor's).
2. Report the distribution (pos/neu/neg) with the sample size, not a single adjective.
3. Pull representative quotes via `sv_search`/`sv_fetch` so the score is auditable.
4. For product-review depth, `sv_retail_review_scan` / `sv_extract_reviews` /
   `sv_extract_rating` give structured ratings; note the platform + count.

### 3. White-space — the unclaimed positioning territory

1. From the competitor word-map (brand-audit §1.2 or brand-maker Step 3.1), list the
   messages/attributes each competitor **owns** (high SOV + positive sentiment on that
   theme).
2. Search the theme space (`sv_search` per candidate positioning word) to find themes
   with **low competitor SOV** — the white-space.
3. Cross-check that low SOV = genuine gap, not a dead category (a theme nobody discusses
   because nobody wants it). Report both interpretations.
4. **Hand the confirmed white-space to `brand-maker` Step 3.1** as the strategic anchor,
   or to `brand-platform` as the positioning territory.

## Output contract

Every figure carries: **the socius-vigil query + window + provider chain + source count**,
and a triangulation/reliability note. Present:
- SOV table (brand + competitors, raw counts + %),
- sentiment distribution with sample size + representative quotes,
- a ranked white-space list with the "gap vs dead-category" caveat.

Absence of data for a name/market is reported as **"no signal in the queried window"** —
never as zero-and-therefore-safe, and never invented. If `socius-vigil` is unavailable,
the deliverable is "market signal unavailable — connect socius-vigil", not a fabricated one.

## Composition

- **Upstream:** `brand-audit` (competitor set + word-map) feeds the SOV/white-space queries.
- **Downstream:** confirmed white-space → `brand-maker` Step 3.1 anchor / `brand-platform`
  positioning; sentiment/SOV → `brand-launch` KPI baseline.
- **Connector:** `socius-vigil` (existing). Optionally `exa` for semantic breadth.
