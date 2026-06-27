# evidentia

**Çok-kaynaklı bilimsel kanıt sentezi ve Türkiye-pazarı araştırma motoru** — bir Claude
Code / claude.ai marketplace plugin'i. `medical-research` v8.3.0 flagship skill'ini, 20+ doğrulanmış
connector'ı (13'ü bundled roster'da) ve `mcp-scout` ile canlı-doğrulanmış klinik genişletme
MCP'lerini tek kurulabilir pakette toplar.

---

## Ne sağlar

- **Flagship skill:** `medical-research` v8.3.0 — 10 uzmanlık ekseni (Onko, Heme, Regülatuar,
  HTA, MedAffairs, İmmün, Nöro, Nadir, DrugIntel, Epidemiyoloji), native-MCP-first çözümleme,
  temiz-kopya doktrini, copyright-kapılı tam-metin. v8.3.0 ekler: `references/knowledge-map.md`
  semantik indeks, Adım 0.4 Semantic Scope Scan (soru ayrıştırma → `coverage_set`), Completeness
  Gate ve G-COVERAGE bütünlük kapısı (ADR-05-safe, çekirdek değişmedi).
- **`start` skill'i:** süit oryantasyonu + connector preflight + niyet yönlendirme.
- **5 komut:** `/evidentia` (tam koşum), `/evidentia-connectors` (preflight + roster tazeleme),
  `/evidentia-fulltext` (tam-metin kademe, copyright-kapılı), `/evidentia-kol` (KOL haritası),
  **`/evidentia-synthesize`** (graph-temelli derin sentez — anamnesis RAG/GraphRAG).
- **1 alt-ajan:** `evidence-synthesizer` — ağır fan-out araştırmayı izole eder; RAG/GraphRAG ile
  retrieve-don't-dump.
- **Tam-metin connector'ı:** **Annas Reader** (operatör-bağlı Cloud Run, OAuth-gated) — makale/kitap
  tam-metin erişimi (`article_search`/`download`, `book_search`/`download`).
- **RAG/GraphRAG substratı:** **anamnesis** self-host Worker — semantik chunking (bge-m3 1024-d) +
  Vectorize + D1 bilgi grafiği. Tam-metin/büyük araç çıktılarını **bağlama dökmeden** indeksler;
  `hybrid_query` ile context-window'a sığan, provenance-damgalı kanıt paketi sunar
  (**`evidence_index`** kanonik artefaktı — context-window taşma koruması).
- **Bundled connector roster** (`.mcp.json`) — dört katman; tek doğruluk kaynağı
  [`CONNECTORS.md`](./CONNECTORS.md).
- **Dört self-host bileşeni** — sertleştirilmiş OAuth 2.1 Cloudflare Worker'ları (`self-host/`):
  [`drugddx-mcp`](./self-host/drugddx-mcp/BUILD-BRIEF.md) (klinik DDI boşluğu) ·
  [`anamnesis-mcp`](./self-host/anamnesis-mcp/BUILD-BRIEF.md) (RAG/GraphRAG substratı) ·
  [`openfda-mcp`](./self-host/openfda-mcp/BUILD-BRIEF.md) (FDA openFDA + WHO ICD-11; deploy talimatı §3.3) ·
  [`evidentia-kb-mcp`](./self-host/evidentia-kb-mcp/BUILD-BRIEF.md) (KB semantik-kapsam takviyesi, opsiyonel; §3.4).

---

## Kurulum

**Claude Code (marketplace):**
```bash
/plugin marketplace add <marketplace-repo>
/plugin install evidentia
```
Kurulum `.mcp.json` roster'ını yükler; Claude Code restart sonrası `start` skill'i ve komutlar
aktif olur.

**claude.ai (web):** Tier-K/Tier-O remote connector'ları **Settings → Connectors → Add custom
connector** ile, Tier-A OAuth connector'ları Advanced settings ile eklenir. Yüzey ayrımı için
[`CONNECTORS.md` §6](./CONNECTORS.md).

---

## Hızlı başlangıç

```
/evidentia-connectors      # önce bağlanırlığı doğrula
/evidentia <araştırma sorusu>   # tam kanıt sentezi koşumu
```
Örnekler: *"emicizumab inhibitörsüz Hemofili A — kanıt + TR ruhsat/fiyat manzarası"* ·
*"CAR-T DLBCL 3L — kılavuz + HTA + pipeline"* · *"pirfenidon biyobenzer fizibilitesi TR"*.

---

## Connector katmanları (özet)

| Katman | Ne | Auto-wire |
|---|---|---|
| **Tier-K** keyless remote-ready | Clinical Trials, NPI, bioRxiv + **genişletme:** med-terminologies, NIH Clinical Tables, NLM RxNorm, IUPHAR GtoPdb, **OpenAlex** (KOL/atıf-ağı), **PubMed-EPMC** (Europe PMC + Unpaywall yasal-OA), **Semantic Scholar** | ✅ |
| **Tier-O** operatör Worker'ları | TİTCK Cache, YÖK Akademik, **Annas Reader** (tam-metin), **openfda** (FDA/WHO ICD-11), **evidentia-kb** (KB takviyesi, opsiyonel) | ✅ |
| **Tier-A** auth-gerekli | PubMed/EPMC, Consensus, AdisInsight, TİTCK, Mevzuat, Türk Patent, … | env / Settings |
| **Tier-R** REST fallback | PubChem, DailyMed, DOAJ, J-STAGE, … | (native MCP değil — bundle dışı; OpenAlex/Unpaywall/S2 artık native Tier-K) |

Tam envanter, fallback merdivenleri ve probe kanıtı: [`CONNECTORS.md`](./CONNECTORS.md).

---

## Güvenlik notu

- **Tier-K genişletme connector'ları topluluk-yayıncıdır** (`io.github.*`) → least-privilege,
  sandbox-first; **hasta-etkili** çıktı (DDI, terminoloji, doz) otoriter kaynakla
  çapraz-doğrulanmadan klinik karar olarak sunulmaz.
- **No-fabrication:** her connector URL'i registry + canlı `initialize` probe'una izlenebilir
  (probe tarihi 2026-06-25). `drug-interaction-mcp`'in HTTP 500'ü gizlenmemiş, self-host'a
  yönlendirilmiştir.
- **Self-host Worker'lar** sertleştirilmiş OAuth 2.1 değişmezlerini korur (redirect-origin
  allowlist, PKCE S256-only, HMAC+TTL kod, escHtml, constant-time, secret store). Detay: BUILD-BRIEF.md
  her `self-host/<worker>/` altında. Tüm dört Worker `auth.ts` birebir aynı 6 invariant paylaşır.
  openfda WHO ICD-11 erişimi sunucu-tarafı OAuth ile (`ICD11_CLIENT_ID`/`SECRET` secrets) — istemci
  kimlik bilgisi açığa çıkmaz.
- **anamnesis RAG dürüstlüğü:** varlık/ilişki çıkarımı orchestrator (Claude) tarafından yapılır
  (LLM-in-the-loop GraphRAG); Worker yalnız depolar+gezer. Microsoft-GraphRAG global community
  özetleri Cloud Run indeksleyiciye ertelendi — sahte in-Worker yaklaşımla taklit edilmez. Annas
  tam metni yalnız analiz içindir; chunk'lar sınırlı/provenance'lı, toplu birebir çoğaltma yok.

---

## Doğrulama kapıları

`G-REF` · `G-CONN` · `G-ALWAYS` · `G-VERSION` · `G-COVERAGE` · **`G-RAG`** (skill bütünlüğü + çıktı faithfulness §7.2.1) + `G-PROBE` · `G-BUNDLE` ·
`G-TRUST` · `G-SURFACE` · `G-REGRESSION` · `G-COPYRIGHT` (plugin). Koşum:
```bash
python scripts/g_probe.py        # .mcp.json URL'lerinde canlı initialize
python scripts/g_bundle.py       # .mcp.json ↔ CONNECTORS.md tutarlılık
python skills/medical-research/evals/check_integrity.py        # yapısal: G-REF/G-CONN/G-ALWAYS/G-VERSION/G-COVERAGE
python skills/medical-research/evals/rag_quality.py            # G-RAG: çıktı faithfulness (§7.2.1) — yapısal taban; --judge ile LLM-judge (EVIDENTIA_JUDGE_KEY)
```

---

## İlişkili skill'ler

- **Upstream:** `mcp-scout` (connector roster bakımı — bundle edilmez, dış araçtır).
- **Downstream composable:** `pharmaintel` / `pharmapatent` (ticari/IP), `onko-erisim` /
  `ius-salutis` (bireysel erişim/dava), `carbon-html-report` / `carbon-pptx` (yayın render'ı).

---

*AS IS; no warranty. Internal-use grant. medical-research çekirdeği ADR-05-safe genişletildi
(skill v8.3.0: semantic coverage — knowledge-map + Adım 0.4 + G-COVERAGE; çekirdek değişmedi).
Plugin v1.1.0, Phase 2.1: openfda + evidentia-kb self-host Workers eklendi; RegulatoryMCP/Lex-Sanitas
Tier-A girdisi çıkarıldı. Bundled roster: 13 server (2026-06-26).*
