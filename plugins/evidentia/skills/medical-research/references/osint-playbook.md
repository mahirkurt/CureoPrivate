# OSINT Playbook (Competitive / Regulatory / PV / Market-Access / KOL)

**Loaded:** when OSINT triggers fire (competitive intel, patent, market-access, PV signal,
KOL-network) or dev context. **Recreated v8.2.0 (UP-003).**

**Cardinal rule:** **OSINT ≠ evidence.** Every OSINT item is **Tier 6** (`evidence-grading.md`) —
context only; it may raise a hypothesis but never supports a clinical claim. Source-tag everything;
flag items older than 6 months; FAERS/spontaneous reports are **reporting, not incidence**.

---

## 1. Playbooks
- **Competitive intelligence** — pipeline & positioning: AdisInsight (`search_drug_companies`,
  `generate_chart`), CT.gov sponsor view, SEC/press via Exa/Tavily. Handoff to `pharmaintel` for
  the full commercial deep-dive.
- **Patent / IP** — Türk Patent (native) + Espacenet/USPTO via Exa; FTO/landscape → `pharmapatent`.
- **Regulatory watch** — AdComm/ODAC dates, CHMP agendas, PDUFA via openFDA + Federal Register +
  Exa (`ema.europa.eu`).
- **Pharmacovigilance signal (triage only)** — openFDA FAERS `count` (PT-level); patient-reported /
  social signal via web search (Tavily → Exa). Triage only — never a substitute for formal PV.
- **Market access** — payer/SUT signal: Mevzuat (native) + Exa; handoff to `onko-erisim`/`saglik-sigorta`.
- **KOL network** — OpenAlex/S2 co-authorship + NPI (US) + **YÖK Akademik** (TR) → §8.

## 2. Connector wiring (α-layer)
- Social / web OSINT (patient-reported & PV signal) is served via **web search** — Tavily
  (domain-scoped, when live) → Exa fallback. On failure note the gap. (No dedicated social-listening
  connector is bundled — deep social-listening is out of scope; see §4 boundary.)

## 3. Source-tag discipline
Each OSINT line carries: source, type (press/abstract/social/registry), date, and a Tier-6 tag.
Conference abstracts (ASCO/ESMO/ASH/EHA) are OSINT-grade until peer-reviewed publication.

## 4. Output → §20 cross-layer + competitive-intel artifact
OSINT findings live in §20 Cross-Layer Notes and the `competitive-intel` output, never inside the
graded clinical sections. Boundary: deep social-listening market research → `socius-vigil` skill;
this playbook only triages signal into the research synthesis.
