# brand-maker — CHANGELOG

Tüm önemli değişiklikler bu dosyaya eklenir. Semantic Versioning 2.0.0 uygulanır.

---

## [2.0.1] — 2026-04-24 — "Sector-Agnostic Positioning Correction"

### Felsefi Düzeltme

v2.0.0'ın yayımlanmasının ardından kullanıcıdan gelen geri bildirimle tespit edildi: skill **mimari olarak** sektör-agnostik (pharma modülü conditional/brief-triggered) olmasına rağmen, **sunum katmanı** (description, Raison d'être, örnekler) pharma'ya orantısız ağırlık vererek yanlış bir algı yaratıyordu. Skill'in temel işlevi fintech'ten lüks modaya, SaaS'tan otomotiva kadar **her sektör** için aynı kalitede isim üretmektir. Pharma yalnızca **regüle sektörlerden biri**dir.

### Changed

- **SKILL.md description**: "pharma-regulation-compliant" öne çıkarımı kaldırıldı; onun yerine "Sector-agnostic verbal identity protocol" açılışı ve 12 sektörlük örneklem listesi (B2B SaaS, consumer DTC, fintech, automotive, luxury, FMCG, pharma ve ötesi). Pharma artık "opt-in" modül olarak tanımlanıyor.
- **Raison d'être bölümü**: "Sektör-Agnostik Mimari Prensibi" alt-başlığı eklendi. Regüle sektörlerin **brief-triggered opt-in modüller** olarak ele alındığı, pharma modülünün bu mimarinin **canlı ilk örneği** olduğu, gelecekte fintech/food-beverage/cosmetics gibi ek modüllerin aynı çerçevede eklenebileceği netleştirildi.
- **Tipik Çağrı Örnekleri**: Tek örnek (B2B SaaS AI platform) yerine **üç örnek** (B2B SaaS, consumer DTC, pharma). Üçünün de aynı 5-adımlı çekirdeği paylaştığı ama farklı referans dosyaları tetiklediği gösteriliyor.
- **Routing tablosu (Kural 11 pharma)**: "Pharma kuralı diğerlerine dominant" ifadesi yumuşatıldı. Artık "regüle sektör tetikleyicileri aktifleştiğinde sessizdir, aksi halde sessiz" formulasyonu.
- **skill-manifest.yaml**: Versiyon 2.0.0 → 2.0.1, release_name güncellendi.

### Unchanged (Mimari bozulmadı)

- Routing tablosu işlevsel olarak aynı — pharma tetikleyicileri zaten conditional idi
- Python scriptlerinde hiçbir değişiklik yok
- Data asset'lerinde hiçbir değişiklik yok
- 18 referans dosyasının 17'si hiç değişmedi (SKILL.md dışında)
- Çağrı API'si tamamen aynı
- Backward compatibility %100 korundu

---

## [2.0.0] — 2026-04-24 — "Post-Digital Era"

### Kanonik Değişim
Brand-maker'ın **Post-Digital Era** dönemine evrimsel yükseltmesi. 40 yıllık bilişsel-konumlandırma paradigmasının (Ries & Trout 1981 → Watkins 2014) üzerine 4 yeni gerçeklik eklenmiştir: AI-mediated search (GEO/LLMO), motion-first identity, voice commerce, pharma regulatory integration.

### Added (Yeni)

#### Protokol Yapısal Değişimler
- **5-adımlı metodoloji** (önceden 4). Yeni **Adım 3.5 — Post-Digital Validation** eklendi
- **Post-Digital Readiness Scorecard** — 6-eksen, 0–12 puanlama sistemi (pharma-only eksende 0–10)
- **5. naming kategorisi — E (Sezgisel/Kontraryen)** — Neumeier 2024 tezi
- **SMILE+M** — Watkins'in 5 kriterine **M (Morphable)** eklenmesi (Wolff Olins 2025 Fluid Identity tezi)
- **SCRATCH 3-katmanlı dilution** — C (Copycat) kriteri Levenshtein + Phonetic + Conceptual-aura 3-layer test
- **Purpose-axis coordinate** — purpose-driven brief'ler için 4-eksen meaning matrisi

#### Yeni Referans Dosyaları (8)
- `geo-llm-readiness.md` — LLM namespace cleanliness doctrine
- `voice-first-naming.md` — ASR compatibility protocol
- `pharma-naming-constraints.md` — FDA/EMA/WHO/USAN/TİTCK kapsamlı (Mahir profili için derinleştirilmiş)
- `motion-kinetic-readiness.md` — kinetic identity compatibility
- `ai-fingerprint-avoidance.md` — algoritmik jeneriklik kaçınma
- `purpose-axis-matrix.md` — 4-axis meaning matrix
- `modern-canon-2022-2026.md` — 2022–2026 branding literatürü
- `category-creator-protocol.md` — kategori yaratan isim protokolü

#### Yeni Python Scriptleri (6)
- `llm_namespace_probe.py` — Axis 1 LLM namespace probe (4 LLM proxy)
- `morpheme_saturation_check.py` — Axis 2 algoritmik jeneriklik
- `asr_simulation.py` — Axis 3 ses-ilk readiness
- `entity_disambiguation.py` — Axis 4 Wikipedia/Wikidata namespace
- `inn_stem_collision.py` — Axis 5 WHO INN/USAN stem çakışması (pharma-only)
- `famous_mark_dilution.py` — Axis 6 3-katmanlı famous mark dilution

#### Yeni Data Asset'leri (3)
- `usan_stems.json` — WHO INN + USAN 178+ stem (onkoloji/hematoloji derinleştirilmiş)
- `yc_ph_morpheme_corpus.json` — YC + ProductHunt son-24-ay morpheme frekansı
- `famous_marks_2026.json` — Top 130 global marka (Interbrand/Forbes/BrandZ)

#### SMP v1.0 Compliance
- `skill-manifest.yaml` — Skill Manifest Protocol v1.0 uyumlu
- 17 process gate (G1–G17) tanımlı
- **pipe_from**: medsearch (≥5.0), pharmaintel (≥7.0), lex-mercator (≥1.0)
- **pipe_to**: brand-visual (≥1.1), carbon-html-report (≥6.0), carbon-pptx (≥1.6), pharmapatent (≥1.0), lex-mercator (≥1.0), docx

#### Kanonik Kaynak Genişletme
- 7 → 13 canonical source (1981–2026)
- **Yeni 2022–2026 kaynakları**:
  - Murphy, C. (2023) *The Ultimate Naming Book*
  - Yuen, R. (2024) *Decoding Branding* 2nd ed.
  - Meyerson, R. (2024) *Brand Naming: The Complete Guide*
  - Neumeier, M. (2024) *Scratch: The Contrarian Branding Book* rev.
  - Interbrand (2024–2026) *Best Global Brands* annual
  - Pentagram (2025) *AI + Brand Craft Whitepaper*
  - Wolff Olins (2025) *Fluid Identity*

#### Rapor Formatı Değişiklikleri
- Section 5 eklendi: **Post-Digital Readiness Scorecard**
- Section 4A eklendi: **Pharma-Specific Regulatory Screening** (pharma-only)
- Stratejik Tavsiye Matrisi'ne **Post-Digital** ve **Pharma-Reg** sütunları

### Changed (Değişen)

- `SKILL.md` — 5-adımlı metodoloji, 15 routing kuralı, v2.0 yasak listeleri eklendi
- `smile-scratch-filter.md` — SMILE+M + 3-katmanlı dilution
- `naming-categories.md` — 4 kategori → 5 kategori (E. Sezgisel/Kontraryen)
- `output-template.md` — Section 5 + Section 4A eklendi, uzunluk hedefleri revize
- `creation-techniques.md` — AI-fingerprint avoidance bölümü appended (~80 satır)
- `exemplar-catalog.md` — 2022-26 exemplar'lar eklendi

### Preserved (Değişmeyen)

- `positioning-foundation.md` — 1.2'den aynen korundu (Ries & Trout doktrini zaman-bağımsız)
- `phonetic-laws.md` — 1.2'den aynen korundu (Bouba-Kiki, Paivio dual-coding zaman-bağımsız)
- `disaster-check.md` — 1.2'den aynen korundu (9-dil disaster check)
- `domain-trademark-strategy.md` — 1.2'den aynen korundu (WIPO Madrid temel)
- `godaddy-mcp-integration.md` — 1.2'den aynen korundu
- `phonetic_analyzer.py`, `disaster_checker.py`, `turkish_semantic_check.py`, `domain_recon.py` — 4 script 1.2'den aynen korundu

### Backward Compatibility

- v1.2 çağrı API'si değişmedi — mevcut brief'ler v2.0'da aynı şekilde çalışır
- Yeni özellikler **opt-in**: post-digital validation, 5. kategori, pharma modülü brief-triggered
- v1.2 SMILE kriter takım (5 kriter) korundu; +M opsiyonel stack olarak eklendi

### Breaking Changes

- 3-adımlı iç metodoloji yapısı değişti: Adım 3.1–3.4 idi, şimdi 3.1–3.6 (Step 3.5 inserted; önceki 3.4 = Domain, 3.5 = Post-Digital, 3.6 = Sunum)
- Yeni çıktı formatı Section 5 ve Section 4A bekliyor — bu bölümleri içermeyen raporlar v2.0 kriterini karşılamaz

### Known Limitations

- `llm_namespace_probe.py` heuristik fallback mode içerir; tam live LLM probe `web_search` tool'u ile runtime'da çalıştırılmalı
- `morpheme_saturation_check.py` veri snapshot'ı 2026 Q1 — periyodik güncelleme gerekir
- `famous_marks_2026.json` top 130 marka ile başlatıldı — genişletme extensibility destekli
- Layer C (conceptual-aura) heuristik seviyede; tam semantic reasoning LLM-assist gerektirir

---

## [1.2.0] — 2025-05-16

### Added
- Türkçe semantic katman (`turkish_semantic_check.py`)
- 5-layer TR semantic check (ofansif, olumsuz çağrışım, dilbilgisel, kültürel, fonetik)
- `--suggest` mode: TR-safe varyant üretimi

### Changed
- `disaster-check.md` içinde Türkçe bölümü genişletildi

---

## [1.1.0] — 2024-11-02

### Added
- GoDaddy MCP integration (`godaddy-mcp-integration.md` + `domain_recon.py`)
- Live .com availability check
- `.com` absolute priority rule

### Changed
- `SKILL.md` Adım 3.4 "Live Domain Verification" olarak rewrite

---

## [1.0.0] — 2024-06-18

### Added
- İlk public release
- 4-adımlı metodoloji (Stratejik Deşifre → 4-Kategori Beyin Fırtınası → Dilbilimsel Lab → Ajans Sunumu)
- 4 naming kategorisi (A. Tanımlayıcı, B. Sentez, C. Soyut, D. Çağrışımsal)
- SMILE / SCRATCH filter (Watkins 2014)
- 8-dil disaster check
- Fonetik analiz (phonetic_analyzer.py — CMU pronouncingpy clone)
- 6 referans dosyası
- 3 Python script

### Canonical Base
- Ries & Trout (1981)
- Millman (2011)
- Wheeler (2013)
- Watkins (2014)
- Miller (2017)
- Burmann et al. (2017)
- Yuen (2021)
