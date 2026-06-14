# thoughtspot-roche — Changelog

Bu dosya `skill-manifest.yaml` içindeki `build.changelog_location` referansını karşılar. Tüm sürüm değişiklikleri kronolojik sırayla burada listelenir.

---

## v2.0.0 — 2026-06-13 (Session-based Spotter Migration + REST Extraction)

**Release name:** Session-based Spotter Migration + REST getAnswer-First Extraction + n_countries Geographic Layer

### Breaking Changes

- **Tool surface migration.** Canlı MCP araç yüzeyi `ping / getRelevantQuestions / getAnswer / createLiveboard` dörtlüsünden **oturum-tabanlı Spotter beşlisine** geçti: `check_connectivity`, `create_analysis_session`, `send_session_message`, `get_session_updates`, `create_dashboard`. Eski→yeni eşleme SKILL.md §2.3'te.
- **Execution Protocol yeniden yazıldı** (Step 1–9): check_connectivity → create_analysis_session → send_session_message → get_session_updates (poll) → dual-path veri edinimi → opsiyonel coğrafi genişletme → CSV normalize → output synthesis → create_dashboard.

### Critical Finding

- **MCP ham hücre döndürmez.** `get_session_updates` yalnız NLG özeti (`text_chunk`) + `answer` meta nesnesi (`answer_id`, `answer_query`, `iframe_url`) döndürür; tablo hücre değerleri akışta yer almaz. Ajan dahi hücreleri göremediğini beyan eder. SKILL.md §2.4 + G10.

### Notable Additions

- **REST getAnswer-first çıkarım yolu.** `auth/token/full` → `metadata/search` (GUID) → `searchdata` akışı; doğrulanmış istek gövdeleri (ThoughtSpot Developer dokümanı, 2026-06). Yeni referans: `references/rest-getanswer-guide.md`. v1 fallback (`/callosum/v1/tspublic/v1/searchdata`) belgelendi.
- **Coğrafi katman.** Molekül başına ülke kırılımı + türev `n_countries`, `top_country`, `top_country_share_pct`, `hhi_country`. Yeni script: `scripts/ts_getanswer_country_extractor.py`. Top-N-only varyant: `scripts/ts_getanswer_extractor.py`. İkisi de env-driven, secret koda gömülü değil.
- **Registry v2.0.** Üçüncü küp eklendi: MIDAS Quarterly (Taiwan-only, 12y). MIDAS Monthly boyut envanteri genişletildi (ATC2/3/4 hiyerarşisi, Molecule List, Manufacturer/Corporation, 7 metrik). Küçük-harf ATC kod kuralı (`l1` ≠ `L01`) belgelendi.
- **Yeni gate'ler.** G9 (no fabrication — görselden okunamayan rakam uydurulmaz) ve G10 (MCP raw-cell asimetrisi → niceliksel ihtiyaçta REST). G1 adı `check_connectivity` olarak güncellendi.
- **query-templates.md.** `last 12 months` ✅ doğrulandı; tek-attribute ATC2 filtresi (küçük-harf kod) ✅ doğrulandı.

### Production Validation Tests Executed (v2.0.0)

| Test | Araç/Yol | Sorgu | Sonuç |
|---|---|---|---|
| T1 | `check_connectivity` | — | ✅ `{"success": true}` |
| T2 | Oturum + send/poll | Country × top-10 ATC3, son 12 ay | ✅ Çözüldü (grafik render; ham hücre akışta yok) |
| T3 | Oturum + send/poll | ATC2='l1' top-10 molekül, son 12 ay | ✅ Molecule List düzeyine indi; ham değer yalnız iframe'de |
| T4 | Ham çıkarım denemesi | CSV transkripsiyon talebi | ✅ Bulgu: ajan ham hücreyi göremiyor → REST yolu zorunlu (G9/G10) |
| T5 | Script derleme | `ts_getanswer_country_extractor.py` | ✅ `py_compile` temiz |

### Known Open Items (v2.0.0)

- REST çıkarıcılar canlı tenant kimlik bilgileriyle uçtan-uca henüz çalıştırılmadı (kimlik bilgisi ortam dışında). İlk canlı koşuda `column_names`/`data_rows` alan adları teyit edilmeli.
- MIDAS Quarterly query-validated değil (yalnız discovery).
- `create_dashboard` canlı test edilmedi.
- Çoklu filter / coğrafi filter semantiği kısmen haritalı.



**Release name:** Initial Release — ThoughtSpot MCP + MIDAS Monthly + MIDAS Disease Monthly + 8-Gate Verification Contract

### Notable Additions

- **Skill foundation.** ThoughtSpot MCP entegrasyonu Roche EMEA tenant'ında (`emea.thoughtspot.roche.com`) Mahir Kurt (kurtm1) authentication'ı ile doğrulandı.
- **Datasource registry.** `assets/datasource-registry.yaml` iki doğrulanmış küple seed edildi:
  - MIDAS Monthly (`210eb567-3d53-4f62-a41a-c8c38d3fe00d`) — audited sales, ATC1-merkezli, NLG mature
  - MIDAS Disease Monthly (`7e0a9470-f4d6-427d-88ae-54434c2085d0`) — disease panel, NLG weak (yansıma davranışı)
- **8-gate verification contract** (G1–G8): pre-flight ping, datasource validation, prompt pattern compliance, Sage NLG fallback discipline, CSV normalization, confidential data handling, cross-cube triangulation, currency unit verification.
- **Mandatory Execution Protocol** (Steps 1–8): pre-flight ping → datasource selection → query formulation → optional NLG probe → getAnswer execute → CSV normalization → output synthesis → optional liveboard materialization.
- **Composability contract** SMP v1.0:
  - `pipe_from`: pharmaintel (≥8.0), medical-research (≥1.0)
  - `pipe_to`: pharmaintel (≥8.0), pharmapatent (≥2.0), carbon-html-report (≥6.0), carbon-pptx (≥1.9)
- **Validated query template catalog** (`references/query-templates.md`): breakdown, top-N, monthly trend (🟡), pairwise comparison (🟡) pattern'leri; soyut keşif sorguları, fiilsiz prompt'lar ve Türkçe sorgu anti-pattern'ler olarak işaretlendi.
- **Sage NLG asimetri keşfi.** MIDAS Monthly soyut prompt'lara somut sorular üretirken, MIDAS Disease Monthly aynı prompt'u yansıtır. Operasyonel sonuç: getAnswer-first stratejisi (G4 gate) kodlandı.
- **CSV normalization rehberi** (`references/csv-normalization-guide.md`): 3-satır header skip kuralı, bilimsel notasyon → Türkçe milyar/trilyon CHF dönüşüm tablosu, Unclassified/Various/Other bucket handling disiplini, currency mertebesi sanity check matrisi (G8).
- **Programmatik normalizer** (`scripts/normalize_csv.py`): stdlib-only Python helper. Library API (`format_chf`, `magnitude_interpretation`, `normalize_thoughtspot`, `render_markdown`, `render_csv`) + CLI entry point. Self-test ile doğrulandı.
- **Roche confidential data handling** tüm output pipeline'ı boyunca korunur; G6 gate her yanıtta etiketin yansıtılmasını zorunlu kılar.
- **Bilinen sınırlılıklar** açıkça belgelendi: schema discovery yok, datasource discovery yok, multi-cube join desteklenmiyor, time window filter syntax kısmen haritalanmadı, Türkçe sorgu davranışı doğrulanmadı.

### Production Validation Tests Executed

| Test | Cube | Sorgu | Sonuç |
|---|---|---|---|
| T1 | MIDAS Monthly | "What is the breakdown of Swiss Franc sales by ATC1 Description?" | ✅ 16 ATC1 satırı; toplam 13,3 trilyon CHF (multi-year all-manufacturer plauzibl) |
| T2 | MIDAS Disease Monthly | "What are the top 15 diseases by Swiss Franc sales?" | ✅ 15 disease satırı; Unclassified rank #2 (~17%); top: DIABETES 22% |
| T3 | Cross-cube | ATC1 oncology vs disease oncology toplam karşılaştırması | ✅ Mantıksal tutarlı; G7 başarılı |
| T4 | Pipeline self-test | normalize_csv.py end-to-end | ✅ Header skip + format + percent + G8 + provenance hepsi başarılı |

### Known Open Items

- `createLiveboard` aracı henüz canlı test edilmedi. v1.1.0'da liveboard materialization workflow doğrulanmalı.
- Time window expressions (MAT, YTD, last-N-months) henüz haritalanmadı. v1.1.0'da Step-4 query templates'a explicit aralık testleri eklenmeli.
- Filter/where-clause semantiği bilinmiyor. v1.1.0'da single-attribute filter testi yapılmalı.
- Multi-cube join MCP üzerinden mümkün değil; sıralı getAnswer + manuel triangulation tek seçenek. ThoughtSpot tarafından native multi-cube join eklenirse v2.0.0 breaking change olur.
- Türkçe sorgu davranışı EMEA tenant'ında doğrulanmadı. v1.1.0'da kontrollü test yapılmalı.

---

## Sonraki Sürüm Adayları

### v1.1.0 (Planlanan)

- [ ] `createLiveboard` workflow validation
- [ ] Time window expression catalog (MAT/YTD/last-N-months/explicit ranges)
- [ ] Single-attribute filter syntax mapping
- [ ] Türkçe sorgu kontrollü testi
- [ ] `references/query-templates.md` — 🟡 → ✅ promotion'ları

### v2.0.0 (Speculative — ThoughtSpot tarafında değişiklik gerekirse)

- [ ] Native multi-cube join API desteği geldiğinde tek-call triangulation
- [ ] `getDataSourceSuggestions` aracı eklenirse otomatik datasource discovery
