# HTA & Market Access Layer (0.5.D)

**Loaded:** when axis 0.5.D fires (+ `regulatory-intelligence.md`). **Adım 1 package:** §1.J.
**Recreated v8.2.0 (UP-003).**

**Triggers (full):** HTA, maliyet etkililik, cost-effectiveness, ICER, QALY, ICUR, NICE, CADTH/CDA,
PBAC, IQWiG, HAS, TLV, ZIN, budget impact, bütçe etkisi, SGK, SUT, geri ödeme, reimbursement,
MAIC, NMA, indirect comparison, willingness-to-pay, threshold, managed entry, risk-sharing.

---

## 1. HTA bodies (Tier 1)
NICE (TA/HST), CADTH/CDA-AMC, PBAC, IQWiG/G-BA (AMNOG added-benefit), HAS, TLV, ZIN. No native
MCP → Exa (`nice.org.uk`, `iqwig.de`, `cadth.ca`, etc.). **TR:** SGK SUT (Mevzuat native) +
TİTCK reference price (`find_reference_prices_for_drug`, `get_price_history`) — TR access is
price-/SUT-determined.

## 2. Economic-model appraisal
- Model type (Markov/partitioned-survival/DES), time horizon, discount rate, perspective.
- **Comparator appropriateness** (standard of care in the decision context).
- Survival extrapolation assumptions (parametric fit, external validity).
- **Indirect comparison rigor:** MAIC (anchored vs. unanchored), NMA (transitivity, heterogeneity).
- Sensitivity analysis (deterministic + probabilistic; CEAC).

## 3. Epidemiologic denominator (co-fire with 0.5.K)
Budget impact needs the eligible population → pull WHO GHO / GLOBOCAN / ICD-11 prevalence
(`regulatory-intelligence.md` §epi) and Turkish incidence where available.

## 4. Output → §1.J / §F-format
Feeds the HTA table (body, decision, ICER, QALY, date) + SUT status + price chain. Handoff: deep
SGK/individual access → `onko-erisim` / `saglik-sigorta`. Surrogate-endpoint → value caveats
inherited from `evidence-grading.md`.
