# orchestration.md

**Multi-Agent Orchestration Reference (v3.0.0)**

> **Architectural role:** Cross-cutting capability reference for coordinating parallel sub-protocol execution, task dependency management, and intelligent caching in complex pharmaintel workflows. Applies primarily to multi-layer T3 analyses and multi-sponsor comparative tasks where sequential execution would be inefficient.

---

## §1. When Orchestration Applies

### 1.1 Single-layer tasks — no orchestration needed

Simple pharmaintel queries resolve with sequential single-template execution:
- "What is Enhertu's FDA approval history?" → T2 asset task → `task-asset.md`
- "Pluvicto mechanism" → T2 → direct answer
- "Who are the top KOLs in NSCLC?" → T3 modality task + simple search

For these, **no orchestration layer activates**. Claude follows linear workflow.

### 1.2 Multi-layer / multi-sponsor tasks — orchestration beneficial

Orchestration becomes valuable when:
- **Multi-modality comparison** — "Compare ADC vs CAR-T vs bispecific for DLBCL"
- **Cross-sponsor sweep** — "Analyze the top 10 ADC developers' pipelines"
- **Multi-jurisdiction analysis** — "FDA vs EMA vs PMDA vs NMPA positions on glofitamab"
- **Layered T3 analysis** — "HER2+ mBC treatment landscape" (Layer 0 generic + Layer 1 ADC modality + Layer 2 oncology TA)
- **Multi-catalyst watch** — 10+ readout events tracked simultaneously

### 1.3 Decision threshold

Activate orchestration when the analytical task requires:
- ≥4 distinct template/sub-protocol executions, AND
- Template executions are parallelizable (no inter-dependence), AND
- Total wall-clock time without orchestration would exceed user patience threshold

For <4 templates, sequential execution is simpler + more debuggable.

---

## §2. Parallel Execution Patterns

### 2.1 Independent sub-protocol parallelism

When multiple sub-protocols can run on independent inputs without cross-dependency:

```
Task: "Compare FDA + EMA + PMDA + NMPA + TİTCK positions on trastuzumab deruxtecan"
                                │
                    ┌───────────┼───────────┬──────────┬──────────┐
                    ▼           ▼           ▼          ▼          ▼
                sub-protocol  sub-proto  sub-proto  sub-proto  sub-proto
                -label        -pmda       -nmpa      -turkey    -sponsor-sweep
                (FDA)         (Japan)     (China)    (Türkiye)  (global)
                    │           │           │          │          │
                    └───────────┴───────────┴──────────┴──────────┘
                                    ▼
                            Merge results with
                            cross-jurisdiction
                            discipline framework
```

### 2.2 Map-reduce pattern

For sponsor-sweep tasks across N companies:

```
Map phase:  For each sponsor in [S1, S2, ..., S10]:
             - Apply task-company.md framework
             - Generate standardized output per sponsor
             → returns N parallel results

Reduce phase: Aggregate into comparative report with:
               - Ranking by dimension (pipeline size, modality focus, etc.)
               - Cross-company pattern identification
               - Strategic positioning narrative
```

### 2.3 Fan-out with conditional branches

When exploratory analysis depth depends on earlier findings:

```
Phase 1: Quick assessment of each sponsor
             ↓
Phase 2: Full deep dive on only those sponsors meeting threshold criteria
             (e.g. only sponsors with >$100M R&D in the therapeutic area)
             ↓
Phase 3: Cross-sponsor synthesis
```

---

## §3. Task Dependency Graph Patterns

### 3.1 Typical dependency structures

```
LINEAR:        A → B → C → D  (each depends on prior)
               (no parallelism possible)

DIAMOND:       A → B ─┐
                    ↘ D   (B and C independent; both feed D)
               A → C ─┘

FAN-OUT:       A → [B, C, D, E]  (single upstream, multiple independent downstream)

TREE:          A → B → [C, D]
                 → E → [F, G]  (hierarchical decomposition)

DAG:           Arbitrary directed acyclic graph of dependencies
```

Most pharmaintel multi-layer tasks form DIAMOND or FAN-OUT structures.

### 3.2 Dependency declaration pattern

When orchestrating, Claude declares task graph explicitly in planning phase:

```
Plan:
  1. [parallel-1] Fetch Enhertu asset data (T2 asset task)
  2. [parallel-1] Fetch Datroway asset data (T2 asset task)
  3. [parallel-1] Fetch Kadcyla asset data (T2 asset task)
  [depends: 1,2,3] 4. Modality comparative analysis (T3 ADC template)
  [depends: 4] 5. Synthesis report
```

Tasks in same bracket = parallel group.

### 3.3 Dependency violation detection

Each parallel group must verify no cross-dependence. Common pitfalls:
- ❌ Task 2 uses output from Task 1 → NOT parallel, declare as dependency
- ❌ Two tasks both writing to same cache key → race condition
- ❌ Tasks share mutable state → serialize or use immutable inputs

---

## §4. Intelligent Caching Discipline

### 4.1 Cache scope principles

Pharmaintel caching operates within-session primarily:
- Claude session-level (within single user conversation) — stateless across turns unless restated
- Tool-level (MCP tools may cache internally) — out of Claude's direct control
- Future: persistent caching layer (not v3.0.0 scope)

### 4.2 What to cache

| Data type | Cache? | TTL |
|---|---|---|
| FDA approval dates | **Yes** | Session-lifetime (stable facts) |
| ClinicalTrials.gov search results | **Yes** | 6 hours (may shift) |
| openFDA drug label content | **Yes** | 24 hours |
| SEC filings index | **Yes** | 24 hours |
| FAERS adverse event counts | **Yes** | Weekly |
| Pivotal trial publications | **Yes** | Session-lifetime |
| Live catalyst calendar | **No** | re-fetch per query |
| Sponsor pipeline guidance | **No** | re-fetch (frequent updates) |
| User-supplied data | **Yes** | Session only (never persist) |

### 4.3 Cache key discipline

Cache keys should be deterministic + collision-free:
```
cache_key = f"{source}:{endpoint}:{hash(params)}"

Examples:
  openfda:drugsfda:sha1("vertex+BLA+2023")
  ctg:search:sha1("HER2+phase3+recruiting")
  edgar:10k:sha1("CIK1067083+2024")
```

### 4.4 Cache invalidation triggers

Invalidate cache entry when:
- TTL expired
- User explicitly requests fresh data ("fetch latest...")
- Known catalyst event in cached domain (e.g. PDUFA date passed → invalidate label cache)
- Source API returns updated timestamp ≠ cached timestamp

### 4.5 Stale-while-revalidate discipline

For less time-sensitive queries, acceptable to:
1. Return cached data immediately
2. Trigger background refresh
3. Flag to user if data is >N hours old

For time-sensitive queries (live catalysts, active recalls), always fetch fresh.

---

## §5. Result Merging Patterns

### 5.1 Symmetric merge (map-reduce output)

When parallel tasks produce structurally identical outputs:
```
results = [task1_output, task2_output, task3_output]
merged = {
    "items": results,
    "summary": {
        "count": len(results),
        "successful": [r for r in results if r.status == "ok"],
        "failed": [r for r in results if r.status != "ok"]
    }
}
```

### 5.2 Heterogeneous merge (diamond pattern)

When parallel tasks produce different structural outputs merging into synthesis:
```
synthesis_input = {
    "layer_0_generic": generic_result,
    "layer_1_modality": modality_result,
    "layer_2_ta": ta_result,
    "cross_cutting_data": api_integration_result
}
final_report = synthesis_template.render(synthesis_input)
```

### 5.3 Confidence propagation in merge

Merged claim confidence = **minimum** of source confidences (not average, not maximum). Per `triangulation.md` discipline.

Example:
- Source A claim confidence: High
- Source B claim confidence: Medium
- Merged statement referencing both: Medium (downgraded to minimum)

### 5.4 Conflict resolution

When parallel sources disagree:
1. Prefer more recent data (timestamp comparison)
2. Prefer higher-primary source (FDA > analyst report > press release)
3. Prefer higher-specificity (full-text trial pub > abstract > news article)
4. If unresolvable, **present both + flag disagreement**

---

## §6. Error Handling + Partial Failure

### 6.1 Graceful degradation

When N parallel tasks execute, if M of N fail:
- Continue with N-M successful results
- Explicitly note failures in output ("M sources unavailable: [list]")
- Downgrade confidence of merged output proportionally
- Never silently drop failures

### 6.2 Retry discipline

For transient errors (rate limits, timeouts):
- 2 retry attempts with exponential backoff (1s → 2s → 4s)
- Non-retryable for permanent errors (404, 403, bad request)

### 6.3 Fallback cascade

If primary source fails, cascade:
1. MCP tool → if fails →
2. REST API → if fails →
3. web_fetch on known URL → if fails →
4. web_search for alternative source → if fails →
5. Flag data unavailable in report

---

## §7. Integration with Pharmaintel Layers

### 7.1 T1-T6 task types

| Task type | Orchestration typical |
|---|---|
| T1 (sanity check) | None |
| T2 (asset deep-dive) | Minimal (serial) |
| T3 (modality + TA landscape) | Diamond (modality + TA parallel, then synthesize) |
| T4 (deal analysis) | Fan-out (each comparable deal in parallel) |
| T5 (catalyst watch) | Map-reduce (per-catalyst status in parallel) |
| T6 (comparison/defense) | Diamond (per-asset deep-dive parallel, then comparison) |

### 7.2 Sub-protocol activation order

When multiple sub-protocols activate for a single task:
```
Pre-synthesis phase (parallel):
  sub-protocol-label          (FDA + EMA labeling)
  sub-protocol-pmda           (Japan)
  sub-protocol-nmpa           (China)
  sub-protocol-turkey         (TİTCK + SGK)
  sub-protocol-sponsor-sweep  (global pipeline)
  sub-protocol-catalyst-watch (pipeline timing)

Synthesis phase (serial, depends on all above):
  Merge + confidence stamp + report assembly
```

### 7.3 Layer resolution order in T3

For multi-layer T3 analysis:
```
Layer 0: task-modality.md (always loaded)
Layer 1: task-modality-{specific}.md (query-content-based, 0-2 sub-templates)
Layer 2: task-ta-{specific}.md (query-content-based, 0-1 TA template)
Cross-cutting: api-integrations.md (loaded if structured data needed)
               analytics-framework.md (loaded if quantitative projection requested)

All layers load in parallel (no ordering dependence). Synthesis phase serial.
```

---

## §8. Task Execution Plan Template

Before executing orchestrated task, Claude produces explicit plan:

```markdown
## Execution Plan

Task: [User query]
Task classification: [T1-T6]
Complexity: [simple/multi-layer/multi-sponsor]

Layers to activate:
  - Layer 0: task-modality.md
  - Layer 1: [modality template(s)]
  - Layer 2: [TA template]
  - Cross-cutting: [api-integrations / analytics / orchestration]

Sub-protocols to activate:
  - [list]

Parallel group 1: [independent tasks]
Parallel group 2: [depends on group 1]
...

Estimated wall-clock: [N] seconds
Source priority: MCP > API > web_fetch > web_search
```

User may override plan before execution.

---

## §9. Monitoring + Observability

### 9.1 Execution log structure

For debugging complex orchestrated workflows:
```json
{
  "task_id": "uuid",
  "plan": [ ... ],
  "executions": [
    {
      "step": "T2-asset-fetch:Enhertu",
      "start": "...",
      "duration_ms": 2100,
      "source": "openFDA",
      "cached": false,
      "confidence_stamp": "High"
    },
    ...
  ],
  "merge_phase": { ... },
  "final_output_length": 4521,
  "total_duration_ms": 12430
}
```

### 9.2 Confidence audit trail

Every claim in final output traceable to:
- Source (MCP tool / API endpoint / fetch URL / search result)
- Confidence level at source
- Any merge-based confidence downgrade

---

## §10. Forbidden Orchestration Patterns

- ❌ Parallelizing tasks with hidden dependencies (silent race conditions)
- ❌ Caching user-supplied confidential data beyond session
- ❌ Silently dropping parallel failures without noting in output
- ❌ Inflating confidence via cross-source averaging (use minimum, not mean)
- ❌ Exceeding API rate limits via uncoordinated parallel calls
- ❌ Orchestrating simple queries where serial execution is cleaner
- ❌ Bypassing generic-by-default discipline via orchestration complexity
- ❌ Using orchestration to paper over individual task quality issues

---

## §11. Versioning & Changelog

- **v3.0.0 (2026-04-15):** Initial release. Cross-cutting orchestration reference covering: when orchestration applies (multi-layer T3 / multi-sponsor sweep / multi-jurisdiction / ≥4 template threshold), parallel execution patterns (independent sub-protocol parallelism + map-reduce for sponsor sweeps + fan-out with conditional branches), task dependency graph patterns (linear + diamond + fan-out + tree + DAG) with explicit declaration in planning phase, intelligent caching discipline with TTL framework per data type (approval dates session-lifetime stable; ClinicalTrials.gov 6 hours; openFDA label 24 hours; FAERS weekly; live catalysts never cache) + cache key discipline + stale-while-revalidate pattern, result merging patterns (symmetric + heterogeneous + confidence propagation via minimum not average + conflict resolution by recency/primacy/specificity), error handling with graceful degradation + retry discipline + fallback cascade (MCP → API → web_fetch → web_search), integration with T1-T6 task types + sub-protocol activation ordering + Layer 0/1/2 resolution in T3 multi-layer analysis, execution plan template, monitoring + observability with execution log structure + confidence audit trail, forbidden patterns. New manifest gate G40. Cross-cutting infrastructure used by complex multi-layer tasks.
