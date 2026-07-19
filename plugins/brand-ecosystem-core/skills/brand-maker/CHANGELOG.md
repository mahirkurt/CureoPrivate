# brand-maker — CHANGELOG

Tüm önemli değişiklikler bu dosyaya eklenir. Semantic Versioning 2.0.0 uygulanır.

---

## [2.1.0] — 2026-07-19 — "Expert-Audit Remediation"

### Bağlam

Gerçek bir kurumsal-marka kısa listesi (14 aday) bağımsız bir marka uzmanı tarafından denetlendi ve hem **veri-doğruluğu** hem **metodoloji** düzeyinde altı kusur SINIFI bulundu. v2.1, bu kusur sınıflarının tekrarlamamasını **yapısal olarak** sağlar. Denetimdeki beş somut başarısız vaka `tests/` altında regresyon fixture'ı yapıldı.

### Added

#### Yeni Python Scriptleri (2)
- `shortlist_diversity_check.py` — **küme düzeyinde** çeşitlilik kapısı (Modül B). Terminal-kafiye satürasyonu + tek-morfem-ailesi payı + küme-içi Levenshtein karışabilirliği + fonetik-aile dağılımı. FAIL → ikinci-tur tetikleyicisi (`missing_territories`). `morpheme_saturation_check.py`'nin tek-isim bakışının göremediği homojenliği yakalar. `--json`, CI-uyumlu exit kodu.
- `pharma_brand_collision.py` — INN stem **ötesi** marka çakışması taraması (Modül E, Eksen 5b). Mevcut ilaç MARKA adları + yüksek-çakışma INN jeneriklerine karşı substring + distinctive-prefix + LASA. Zorunlu provenance + `live_tm_checked:false` caveat'ı — "temiz" tek aramadan asla verilmez.

#### Yeni Data Asset (1)
- `pharma_brand_names.json` — kürasyonlu ilaç marka tohumu (klaritromisin ailesi: Klacid/Biaxin/Klaricid/Claritek/Claranta-IN + Claritin dahil).

#### Yeni Naif-Algı Katmanı (Layer 6)
- `turkish_semantic_check.py` içinde `naive_parse()` — dil-bağımsız naif ilk-okuma ayrıştırıcısı + Türkçe PERCEPTION_LEXICON. Niyet-kök ≠ algı-kök sapması ve olumsuz/değer-düşürücü algı (orta=vasat, selva=orman) FIRST-CLASS uyarı olarak yüzeyde. `--intent` ve `--json` bayrakları.

#### Yeni Process Gate'ler (G18–G22)
- G18 iki-kaynak domain, G19 çeşitlilik kapısı+ikinci tur, G20 iki-eksen skor ayrımı, G21 naif algı first-class, G22 pharma marka çakışması.

#### Tests
- `tests/test_brand_maker_v2_1.py` — beş başarısız vaka fixture'ı (auronza/nortanza domain false-positive, Claranta pharma marka, 14-isim homojen küme, Ortanza/Ortanta "orta", Selvanza "selva", skor tavanı).

### Changed

- **`domain_recon.py`** (Modül A) — heuristic-yalnız araç, gerçek **iki-kaynak canlı doğrulayıcı**ya dönüştürüldü: RDAP (birincil, HTTPS) + WHOIS (port 43, ikincil). **Hiçbir alan adı tek sinyalle "müsait" DÖNMEZ**; `confirmed_available` (2 kaynak) / `confirmed_taken` / `provisional_available` (tek kaynak) / `unverified` (offline). Her sonuç doğrulama-durumu + kaynak + UTC zaman damgası taşır. Ağ yoksa `unverified`'e nazik degrade. `--offline`, `--json`, `--tlds` bayrakları. **Kanıt:** `auronza.com`/`nortanza.com` artık asla "müsait" dönmez (offline→unverified; online→confirmed_taken).
- **`phonetic_analyzer.py`** (Modül C) — tek-skor tavan (95–100 yığını) kırıldı: **iki ayrı eksen** — `pronunciation_ease` (kolay-telaffuz) + `brand_strength` (kurumsal marka gücü/ayırt edicilik, template/me-too `-anza` register cezası). `readiness_score` artık ayrıştırıcı bir kompozit (0.45·ease + 0.55·strength). `--json`.
- **`turkish_semantic_check.py`** (Modül C+D) — verdict baseline 100→80 (eski baseline her adayı 85–100'e yığıyordu); naif algı ana faktör; `analyze(name, intended_root)`.
- **Referanslar (Modül F):** `output-template.md` (doğrulama-durumu/kaynak/zaman damgası sütunları + çeşitlilik-kapısı bölümü 2.1 + naif-algı finalist satırı + pharma marka satırı + provisional/confirmed ayrımı), `godaddy-mcp-integration.md` (iki-kaynak zorunluluğu), `domain-trademark-strategy.md` (heuristic artık hüküm değil + §4.6 marka ön-tarama), `pharma-naming-constraints.md` (§8.2b marka-çakışma katmanı + Claranta vakası), `naming-categories.md` (çeşitlilik kapısı notu).
- **`SKILL.md`** — v2.1 description/başlık, iki-kaynak domain kuralı (Adım 3.4), çeşitlilik kapısı + ikinci-tur tetikleyicisi (Adım 3.2), naif ilk-okuma + skor ayrımı (Adım 3.3), Eksen 5b (Adım 3.5), routing kuralları 16–18, 5 yeni yasak, versiyon logu.
- **`skill-manifest.yaml`** — 2.0.1 → 2.1.0, G18–G22, `brand-verify-mcp` opsiyonel connector, build metadata.

### No-Fabrication Disiplini (korundu + güçlendirildi)
- Domain: ağ yoksa "unverified" (asla iyimser "müsait").
- Pharma marka: provenance + "resmî TM araştırması gerekli" — "temiz" tek aramadan yok.
- Naif algı: olumsuz algı gömülmez, first-class.

### Backward Compatibility
- v1.2/v2.0 çağrı API'si korundu; yeni davranışlar opt-in değil **zorunlu kalite kapıları** (mevcut brief'ler aynı çalışır, çıktı daha dürüst).
- Script çıktı şekilleri genişletildi (domain/phonetic/turkish) — downstream JSON tüketicileri yeni alanları görebilir; eski alan adları korundu (`readiness_score`).

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
