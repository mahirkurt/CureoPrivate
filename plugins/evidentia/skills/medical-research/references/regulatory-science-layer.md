# Regulatory Science Layer (0.5.C)

**Loaded:** when axis 0.5.C fires (+ `regulatory-intelligence.md`). **Adım 1 package:** §1.I.
**Recreated v8.2.0 (UP-003).**

**Triggers (full):** ruhsat, MAA, NDA/BLA, FDA approval, EMA, CHMP, TİTCK, AdComm/ODAC,
accelerated approval, conditional approval, BTD/breakthrough, PRIME, fast track, orphan
designation, REMS, RMP, withdrawal, label change, post-marketing, supplementary protection,
505(b)(2), biosimilar pathway, ICH, GxP.

---

## 1. Agency pathways & milestones (Tier 1 / primary)
- **FDA:** approval type (full vs accelerated), AdComm/ODAC vote, CRL, REMS — via **native openFDA**
  (`drug/drugsfda`, `drug/label`, `drug/enforcement`). *(Federal Register has no native API → documented gap; the legacy Regulatory MCP was removed v8.5 D-α.)*
- **EMA:** CHMP opinion, conditional/exceptional, PRIME — EMA has **no native MCP/API → documented gap**
  (EPAR/CHMP not web-scraped, v1.4.0); cross-check with AdisInsight `history_events`.
- **TİTCK (TR, native):** ruhsat status, Madde-23 başvuru (`search_regulation_article23`),
  authorization cancellations (`find_authorization_cancellations_for_drug`), withdrawal trend.
- **EUR-Lex** (reg MCP `eurlex_expert_search`) for EU legal basis.

## 2. Designation flags
Track orphan (FDA ODD / EMA OMP / TİTCK), breakthrough/PRIME, fast track, accelerated — from
AdisInsight flags (`is_orphan_drug`/`is_btt`/`is_prime`) cross-validated against agency sources.

## 3. Appraisal checklist
- Accelerated-approval **confirmatory-trial status** (verified benefit vs. withdrawn indication).
- Label scope vs. trial population (indication creep).
- Safety signals: openFDA FAERS `count` (PT-level) — **reporting, not incidence**; never present as rate.
- TR lag: time from FDA/EMA approval → TİTCK ruhsat → SGK reimbursement.

## 4. Output → §1.I / §4
Feeds §4 Ruhsat & Etiket (milestone timeline FDA/EMA/TİTCK) and the regulatory_table sidecar.
Latency note: regulatory MCP is slow — call singly, retry, skippable. Handoff: deep TR regulatory
reform → `lex-sanitas`; promotional compliance → `promo-censor`.
