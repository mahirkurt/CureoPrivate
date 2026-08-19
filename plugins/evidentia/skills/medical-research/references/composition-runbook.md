# Composition Runbook — Cross-Skill Pipelines (v8.2)

**Loaded:** cross-skill / pipeline context. **Recreated v8.2.0 (UP-003).**
Mirrors `skill-manifest.yaml` → `composition`.

## 1. Downstream handoffs (pipe_to)
- **carbon-html-report / carbon-pptx** — consume `.data.json` sidecar; consume-and-strip VIZ/OPS;
  do NOT re-author content. Trigger when a publication-quality HTML/PDF or deck is requested.
- **pharmaintel** — commercial deep-dive (medical-research supplies the evidence layer).
- **pharmapatent** — FTO/IP landscape (with Türk Patent output).
- **thoughtspot-roche** — IQVIA MIDAS market sizing (ThoughtSpot connector).
- **onko-erisim / saglik-sigorta** — individual TR access / SGK / insurance.
- **cureolex / lex-mercator / promo-censor** — regulatory reform / commercial law / promo compliance.
- **rxos (rxpraxis)** — generic/biosimilar opportunity scan.

## 2. Scope guard (what medical-research does NOT do)
- Individual SGK appeal/litigation → onko-erisim / saglik-sigorta.
- Promotional MLR review → promo-censor.
- Net-new commercial strategy → pharmaintel.
medical-research owns the **evidence + landscape + KOL + epidemiology** layer and hands the rest off.

## 3. Sidecar as the contract
The `.data.json` sidecar (`output-templates.md` §4) is the machine interface for every downstream
skill; keep `connectors_used` + `gaps[]` accurate so consumers can trust provenance.
