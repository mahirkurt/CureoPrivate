# Rare Disease Layer (0.5.H)

**Optional enrichment module** — loaded only when the question's context enters rare-disease. NOT
mandatory; the core PRISMA pipeline (P0–P7) runs without it. Output → clearly-labelled enrichment
appendix (not the core SR report).
**Recreated v8.2.0 (UP-003).**

**Triggers (full):** nadir hastalık, rare disease, orphan, ODD/orphan drug designation, OMP,
Orphanet, OMIM, ORPHAcode, natural history, doğal seyir, registry endpoint, ultra-rare,
gene therapy, gen tedavisi, CFTR, enzyme replacement, ERT, substrate reduction, n-of-1, expanded
access, named-patient.

---

## 1. Reference resources (Tier 1 / primary)
- **Orphanet** (ORPHAcode, epidemiology, expert centres), **OMIM** (genetic basis),
  **GARD/NORD**; gene–disease via Orphanet/OMIM (no native MCP/API → **documented gap**, not web-scraped).
- Designations: FDA ODD, EMA OMP, TİTCK orphan handling; AdisInsight `is_orphan_drug`.

## 2. Evidence specifics (small-n methodology)
- **Natural-history studies** as comparators — validate matching, era, ascertainment; the
  external control is often the only "comparator," so its validity is the crux.
- Registry endpoints & surrogate acceptance; Bayesian/adaptive small-n designs; n-of-few caveats.
- Gene/cell therapy durability, immunogenicity (AAV pre-existing antibodies), one-time-dosing
  economics → strong HTA co-fire (0.5.D) and epidemiology co-fire (0.5.K, prevalence denominator).

## 3. Epidemiology denominator (co-fire 0.5.K)
Prevalence is decisive for rare-disease HTA and access. Pull Orphanet prevalence + WHO GHO/ICD-11
(`regulatory-intelligence.md`) + Turkish prevalence/registry availability (a recurring gap →
Phase 4 gap note).

## 4. Output → enrichment appendix (domain-specific guideline placement / pipeline note), never the core SR sections
Feeds the enrichment appendix's epidemiology note (prevalence), HTA/access note (one-time-therapy
economics), and TR access note (named-patient/expanded-access where no ruhsat). `specialty_payload`:
ORPHAcode + natural-history comparator validity note.
