---
name: start
description: >
  evidentia süitine giriş ve yönlendirme. 20 bundled MCP + 13 companion bağlanırlığını
  PRISMA faz sırasıyla kontrol eder, flagship medical-research 9.0.4 skill'ini ve yedi
  komutu tanıtır, niyete göre doğru komuta yönlendirir. İlk kez süitle çalışırken, hangi
  connector'ların bağlı olduğunu görmek için, ya da "evidentia nedir / nereden başlamalıyım
  / hangi komutu kullanmalıyım / connector'larım bağlı mı" türü oryantasyon sorularında
  kullanın. Tetikleyiciler — evidentia başlat, süit oryantasyonu, connector kontrolü,
  "ne yapabilirsin", "nereden başlayayım", araştırma motoru kurulumu, kanıt sentezi.
metadata:
  version: "1.1.0"
---

# evidentia — Başlangıç & Yönlendirme

Bu skill, `evidentia` araştırma süitine **giriş kapısıdır**. Beş adımı sırayla yürütün; ağır
işi flagship `medical-research` ve yedi komut yapar.

---

## Adım 1 — Karşılama

evidentia, **PRISMA 2020 / PRISMA-ScR tıbbi literatür inceleme** motorudur. Flagship
`medical-research` **9.0.4**: her derleme **P0–P7** hattından geçer. Filo: **20 bundled
server** (11 gated / 9 public) + **13 companion** (hesap düzeyi; Cursor yüklemeyebilir).
Opsiyonel zenginleştirme (onko/heme/regülatuar/HTA/KOL/immün/nöro/nadir/drug-intel/
Türkiye/epidemiyoloji) yalnız bağlam-tetiklemeli — varsayılan yol **hiçbirini yüklemez**.

Araç sırası bağlayıcıdır: `skills/medical-research/references/execution-map.md`
(MUST/SHOULD/MAY/OUT + `SKIP-REASON`; sessiz atlama yok).

---

## Adım 2 — Connector Preflight (yüzey-bilinçli)

[`CONNECTORS.md`](../../CONNECTORS.md) ve
[`shared/canonical-cache-contract.md`](../../shared/canonical-cache-contract.md) **normatiftir**.
Tam yürüyüş: `/evidentia-connectors`.

### Adım 2.0 — Proje Ayarları (varsa)

`.claude/evidentia.local.md` varsa **Read** ve YAML'ı uygula:
- `enabled: false` → ayarı yok say.
- `known_connected: [...]` → bunları bağlı kabul et, tekrar probe etme.
- `default_modules` → Adım 0.5 tohumu (hiçbiri zorunlu değil).
- `fulltext_tier`, `completeness_gate`, `auto_ingest_rag` → koşuma taşı.

Dosya yoksa varsayılanlar (tam preflight · copyright_gated · standard).

Kontrol listesi (**execution-map sırası**):
1. **P1 bibliographic MUST** — `openalex`, `pubmed-epmc`, `semantic-scholar`.
2. **P1 companions SHOULD** — PubMed, Clinical Trials, bioRxiv, Consensus, Paper Search,
   Scite, YÖK Tez (Elicit MAY; AdisInsight MAY 0.5.I).
3. **P4 cascade** — `marmara-ebsco` (T3) → `openathens` (T4) → Wiley companion (T5) →
   `annas-reader` (T6) → pubmed-epmc Unpaywall (T7) → `anamnesis` (exclusive `evidentia:run:<id>`).
4. **P0 booster SHOULD** — `evidentia-kb` (`kb_search`; kapı değil).
5. **MAY enrichment (yalnız sinyal)** — `openfda`/`ema` (reg) · `pophive` (US-only) /
   `who-gho` (global/TR) / `globocan` (kanser) · `titck` / `yok-akademik` · `drugddx` ·
   med-terminologies / nih-clinicaltables / nlm-rxnorm / iuphar-gtopdb (TOOL-whitelist;
   D1/D2 never; D6 `icd11_search` ALLOW).
6. **İkincil** — Elicit, AdisInsight, Literatür, SNOMED companion, BioRender (P7 visual)
   (`companion_unloaded` dürüst).

> **Yüzey:** Claude Code `.mcp.json` (`${VAR}`) + Cursor `.cursor-plugin/mcp.json`
> (`${env:VAR}`, örn. `MARMARA_EBSCO_MCP_API_KEY`) otomatik; claude.ai Settings → Connectors. Directory
> OAuth (PubMed, CT.gov, Consensus, Elicit, Wiley…) roster'da STATİK URL ile yok.

Eksik connector → graceful: `SKIP-REASON` + fallback merdiveni; araştırmayı durdurma.

---

## Adım 3 — Flagship Skill Tanıtımı

`medical-research` 9.0.4 ağır işi yapar: P0–P7, native-MCP-first, ordered playbook,
Adım 0.5 opsiyonel zenginleştirme, Completeness Gate (`SKIP-REASON` zorunlu), temiz-kopya.
Kullanıcı doğrudan bir araştırma sorusu sorduğunda bu skill devreye girer; `start`
yalnızca yönlendirir.

---

## Adım 4 — Komut Tanıtımı

| Komut | Ne yapar |
|---|---|
| `/evidentia <soru>` | **P0→P7 tam derleme** — playbook sırası + insan-onay (P3/P5) |
| `/evidentia-protocol <soru>` | **P0–P1** protokol + MeSH/arama dizesi |
| `/evidentia-fulltext <ref>` | **P4 cascade** — EPMC→Paper Search→OpenAthens→Wiley→annas→Unpaywall |
| `/evidentia-synthesize <konu>` | **P4+P6** anamnesis exclusive-run `hybrid_query` |
| `/evidentia-appraise <set>` | **P5–P6** RoB + GRADE (korpusta scoped hybrid) |
| `/evidentia-kol <alan>` | **Opsiyonel KOL** — OpenAlex MCP→S2→EPMC→NPI→YÖK Akademik |
| `/evidentia-connectors` | **20+13 preflight** + G-BUNDLE / G-IDENTITY / G-PROBE |

Ağır fan-out: `evidence-synthesizer` alt-ajanı (filo `tools:` izinli; WebSearch yok).

---

## Adım 5 — Niyet Yönlendirme + Scope Guard

| Kullanıcı niyeti | Yönlendir |
|---|---|
| "Şu molekül/hastalık için kanıt" | `/evidentia` |
| "Connector'larım bağlı mı" | `/evidentia-connectors` |
| "Şu makalenin tam metni" | `/evidentia-fulltext` |
| "Bu alanda KOL kim" | `/evidentia-kol` |
| "Derin / çok-belge sentez" | `/evidentia-synthesize` |
| "RoB / GRADE" | `/evidentia-appraise` |
| "Yalnız protokol / arama dizesi" | `/evidentia-protocol` |
| Belirsiz | `/evidentia` |

**Scope Guard:** bireysel SGK/dava → `ius-salutis` / `onko-erisim`; MLR → `promo-censor`;
ticari/OSINT → `pharmaintel`; patent → `pharmapatent`; TR mevzuat/SUT → `cureolex`
(bu plugin'de mevzuat MCP yok); render → `carbon-html-report` / `carbon-pptx`.
