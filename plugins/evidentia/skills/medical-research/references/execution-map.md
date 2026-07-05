# Execution Map — Fan-Out Planning (v8.2)

**Loaded:** large/multi-layer queries. **Recreated v8.2.0 (UP-003).**

For heavy queries (3+ axes, ~100–220 calls), plan the parallel fan-out before issuing calls.

## 1. Order of operations (Adım 1)
1. Academic core — **ALWAYS-ON: fire ALL discovery connectors in parallel** (PubMed/EPMC, CT.gov, bioRxiv, Consensus, Scholar Gateway, Paper Search, YokTez, OpenAlex, Semantic Scholar, pubmed-epmc); an unreachable connector is logged as a visible OPS gap, never silently dropped.
2. 6-country AFF matrix (EPMC) — mandatory loop, not skippable.
3. Türkiye Dörtlüsü (TİTCK + Mevzuat + YokTez + AFF:Turkey) — native; TİTCK Cache fallback on stall.
4. Specialty packages (per active 0.5 axis) — injected.
5. AdisInsight (0.5.I) → Synapse/OpenTargets (0.5.J, conditional).
6. Regulatory MCP stack — **singly, not parallel** (180 s timeout risk); retry; skippable.

## 2. Latency & quota budgeting
- Regulatory MCP: serialize, 1 retry, skippable flag.
- AdisInsight/Wiley: generous but retry-resilient.
- Record the realized call count + active layers in the `<!-- OPS -->` annex.

## 3. Call-count expectations (no upper cap)
general ~48–60 · single specialty ~60–78 · two-layer ~72–95 · 3+ heavy ~100–150 · strategic ~150–220.
