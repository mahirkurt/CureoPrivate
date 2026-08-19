---
description: Connector preflight + roster tazeleme + canlı G-PROBE. 20 bundled sunucu + 13 companion'ı PRISMA faz sırasıyla (execution-map) yürür; claude.ai vs Claude Code yüzeyini ayırır; G-BUNDLE/G-IDENTITY/G-PROBE çalıştırır.
argument-hint: "[opsiyonel: yenile | probe | grup-adı]"
allowed-tools: Bash(python:*), Bash(curl:*)
---

# /evidentia-connectors — Preflight & Roster Doğrulama

İstek kipi (opsiyonel): **$ARGUMENTS** — boşsa tam preflight raporu.

Normatif sıra: [`execution-map.md`](../skills/medical-research/references/execution-map.md)
(MUST/SHOULD/MAY/OUT). Envanter: [`CONNECTORS.md`](../CONNECTORS.md). Filo SSOT: `fleet.yaml`
→ **20 server** (11 gated / 9 public) + **13 companion**. Mevzuat yok.

## 1. Yüzey-Bilinçli Bağlanırlık (faz sırasıyla yürü)

**Claude Code** → `.mcp.json` otomatik bağlar. **claude.ai** → Settings → Connectors /
Directory. Directory/OAuth companion'lar `.mcp.json`'da YOKTUR.

Her satır: ✅ bağlı / ⚠️ manuel-gerekli / 🔴 eksik → fallback (`execution-map` degrade) /
`SKIP-REASON` kodu.

### 1.1 Bundled 20 (`.mcp.json`) — playbook home phase

| # | Server | Phase / duty | Beklenen |
|---|---|---|---|
| 1 | `openalex` | P1.1 MUST | gated `OPENALEX_MCP_API_KEY` |
| 2 | `pubmed-epmc` | P1.2 MUST | gated `PUBMED_MCP_API_KEY` |
| 3 | `semantic-scholar` | P1.3 MUST | gated `SEMANTICSCHOLAR_MCP_API_KEY` |
| 4 | `evidentia-kb` | P0 SHOULD | gated; unreachable = map-only |
| 5 | `marmara-ebsco` | P4.T3 MUST try | gated `MARMARA_EBSCO_MCP_API_KEY` |
| 6 | `openathens` | P4.T4 MUST try | gated; challenge_required → T5/T6 |
| 7 | `annas-reader` | P4.T6 MUST* | gated; last resort after licensed band |
| 8 | `anamnesis` | P4+P6 MUST* | gated; exclusive `evidentia:run:<id>` |
| 9 | `openfda` | P7 MAY 0.5.C/K | gated; serial + 1 retry |
| 10 | `ema` | P7 MAY 0.5.C | keyless |
| 11 | `titck` | P2/P7 MAY TR | gated; canonical (no cache Worker) |
| 12 | `yok-akademik` | P7 KOL MAY | gated; `yok_search(term=)` |
| 13 | `pophive` | P7 MAY 0.5.K | keyless; **US-only** |
| 14 | `who-gho` | P7 MAY 0.5.K | keyless; global/TR |
| 15 | `globocan` | P7 MAY 0.5.K | keyless; cancer + `ui` |
| 16 | `drugddx` | P4 MAY 0.5.I | keyless; not a pairwise engine |
| 17 | `med-terminologies` | P4 MAY coding | keyless; MeSH/ICD-11/ATC; SNOMED if Snowstorm |
| 18 | `nih-clinicaltables` | P4 MAY | pipeworx `includeTools` |
| 19 | `nlm-rxnorm` | P4 MAY | D1/D2 never call |
| 20 | `iuphar-gtopdb` | P4 MAY 0.5.I | pipeworx `includeTools` |

### 1.2 Companions (13 — hesap düzeyi; Cursor yüklemeyebilir)

| Companion | Phase | Claude vs fleet |
|---|---|---|
| PubMed (HCLS) | P1.2b SHOULD | Fleet `pubmed-epmc` birincil; HCLS supplement |
| Clinical Trials | P1.4 SHOULD | Directory only |
| bioRxiv / medRxiv | P1.5 SHOULD | Hub stdio veya HCLS; HCLS bug → stdio |
| Consensus | P1.6 SHOULD | Directory / session consensus MCP |
| Paper Search | P1.7 / P4.T2 SHOULD | Directory |
| Elicit | P1.8 / P3 MAY | OAuth |
| Scite | P1.9 / P3 SHOULD | Directory |
| AdisInsight | P1.10 / P2 / P7 MAY 0.5.I | OAuth |
| YÖK Tez | P1.11 SHOULD | Directory / yoktez MCP |
| Wiley | P4.T5 SHOULD | OAuth publisher full-text |
| Literatür | P4 MAY TR | TR tam-metin |
| SNOMED CT Terminology | P4 coding MAY | Directory; ICD-11 primary elsewhere |
| BioRender | P7 visual MAY | Figures only — not evidence |

Unloaded = `SKIP-REASON companion_unloaded`.

Directory-only (filo companion DEĞİL): Scholar Gateway, ChEMBL, NPI, Türk Patent, Synapse, OpenTargets.

## 2. G-BUNDLE — Roster ↔ SSOT

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/g_bundle.py
```

## 2b. G-IDENTITY — Self-host Worker adı

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/g_identity.py
```

## 3. G-PROBE — Canlı initialize

`probe`/`yenile` istendiğinde:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/g_probe.py
```

Beklenen (connector-registry §8; D6 2026-08-17 emekli): med-terminologies 200 (`icd11_search`
CANLI) · nih/rxnorm/gtopdb 200 (D1 interactions=404, D2 related=400, D3 icd10cm isim→0) ·
drugddx 200 · openfda Bearer · PopHIVE 200 US-only · who-gho / globocan / ema keyless.
**Yalnız §2.6 whitelist.** Elicit/Scite/BioRender/SNOMED: OAuth/Directory — tools/list canlı probe.

## 4. Roster bakımı

Kalıcı düşüş / yeni kaynak → mcp-scout yargısı; sonuç `.mcp.json` + `CONNECTORS.md` +
`execution-map.md` birlikte.

## 5. Güven

Tier-K topluluk-yayıncı; hasta-etkili çıktı otoriter kaynakla çapraz-doğrulanır
(CONNECTORS.md §5). Pipeworx jenerikleri çağrılmaz (guard allowlist).
