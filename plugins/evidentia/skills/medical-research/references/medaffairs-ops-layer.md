# Medical Affairs Operations Layer (0.5.E)

**Loaded:** when axis 0.5.E fires. **Adım 1 package:** §1.K.
**Recreated v8.2.0 (UP-003).**

**Triggers (full):** MSL, medical science liaison, advisory board, danışma kurulu, KOL/KOL
engagement, GPP3, ICMJE, EFPIA, IFPMA, İEİS, AİFD, IIS/ISR (investigator-initiated study), MLR,
medical-legal-regulatory, FCPA, ToV/transfer of value, Sunshine, scientific exchange,
non-promotional, publication plan, congress.

---

## 1. Standards & codes (Tier 1 / primary)
- **Publication:** GPP 2022 (Good Publication Practice), ICMJE authorship/recommendations,
  CONSORT/PRISMA reporting, trial-registration + results-posting obligations.
- **Conduct/transparency:** IFPMA Code of Practice, EFPIA Code + Disclosure, **İEİS / AİFD** (TR),
  FCPA + local anti-bribery, ToV disclosure.
- **Scientific exchange vs. promotion** boundary (non-promotional medical information).

## 2. Operational artifacts
- Advisory-board scientific framing; KOL identification & tiering (→ §8 KOL map; US **NPI** +
  **YÖK Akademik** TR); IIS/ISR scientific-merit review; MLR readiness of medical materials.

## 3. KOL identification wiring (§8)
OpenAlex/Semantic Scholar (output, h-index, citation network) → EPMC (recent activity) → **NPI**
(US verification) → **YÖK Akademik** (Turkish academics: h-index, co-author network, supervised
theses). Tier by scientific output + guideline authorship + trial leadership.

## 4. Boundary / handoff
medical-research provides the **scientific evidence + KOL/landscape** layer. **Promotional**
material compliance review → `promo-censor` (NOT in-skill). Individual HCP ToV/contracting →
out of scope. Output → §8 KOL map + a compliance-aware framing note.
