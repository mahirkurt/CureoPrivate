# pharmaintel — Sub-Protocol: Türkiye Ürün Geliştirme & Entegre Veri Katmanı (v8.0.0)

**Codename:** `product-development-tr`
**Status:** Optional layer — default OFF, explicit invocation ON
**SMP version:** 1.0
**Companion:** `sub-protocol-turkey.md` (regulatory + reimbursement frame); this protocol focuses on **product development decision-making** (in/out, fizibilite, fiyat tavanı, pazar potansiyeli)

---

## §1. Raison d'être

Türkiye'de ilaç geliştirme kararları (originatör in-licensing, jenerik portföy seçimi, biyobenzer geliştirme, Reliance Pathway hedef listesi) çok-kaynaklı bir **veri triangülasyonu** gerektirir:

- **Türkiye regulatuar gerçeği:** Ruhsat statüsü, eşdeğer grup, fiyat tavanı, withdrawal trend, biyobenzer ilk-onay, kullanım protokolü kısıtları → **TİTCK**
- **ABD originatör + jenerik referansı:** NDA/ANDA, Orange Book TE rating, patent + exclusivity tail, biowaiver eligibility → **openFDA + Orange/Purple Book**
- **Global pipeline + clinical durum:** Geliştirme fazı, sponsor, indikasyon kapsamı, deal terms → **AdisInsight MCP**
- **Pazar büyüklüğü + 36-ülke kıyaslaması:** Aylık IQVIA MIDAS satış (TRx/NRx volume, value, market share) → **ThoughtSpot MCP**

Tek bir veri kaynağı yeterli değildir; her kaynak farklı bir karar boyutunu cevaplar. Bu sub-protocol bu dört kaynağı **single coherent feasibility framework** içinde orkestre eder.

> **Mimari konum:** `sub-protocol-turkey.md` Türkiye operasyon yürüten bir ürünün regulatuar/reimbursement durumunu açıklar (post-launch discipline). Bu sub-protocol **pre-development feasibility**'yi cevaplar: *"Bu molekülü Türkiye'de geliştirmeli miyiz / lisanslamamalı mıyız / portföye almalı mıyız?"*

---

## §2. Trigger Logic (v1.0.0 — generic-by-default discipline)

Bu sub-protocol **yalnızca query content**'ine göre tetiklenir (`generic-by-default.md` Article 5 ile uyumlu). Kullanıcının coğrafi konumu, işvereni, rolü trigger değildir.

### (A) Explicit triggers (keyword-based)

Aşağıdaki Türkçe / İngilizce ürün geliştirme + fizibilite terimleri query'de geçtiğinde tetiklenir:

**Türkçe:** ürün geliştirme fizibilitesi, jenerik fizibilite, jenerik portföy seçimi, biyobenzer fizibilitesi, Türkiye ürün giriş kararı, in-licensing değerlendirmesi, eşdeğer grup analizi, fiyat tavanı simülasyonu, referans fiyat hesabı, 5-ülke fiyat referansı, ATC sınıf doygunluğu, ürün canlandırma, withdrawal trend, ruhsat iptal trendi, IQVIA MIDAS Türkiye, IQVIA MIDAS 36 ülke, Türkiye pazar büyüklüğü, ülkeler-arası pazar kıyaslaması, biowaiver, BCS sınıflandırması, dissolution profile, Q1/Q2 (kalitatif/kantitatif aynılık), patent peyzajı Türkiye, jenerik eligibility Türkiye, Reliance hedef analizi.

**İngilizce:** product development feasibility, generic feasibility, generic portfolio selection, biosimilar feasibility, Turkey market entry decision, in-licensing assessment, equivalent group analysis, price ceiling simulation, reference price calculation, 5-country reference, ATC class saturation, product revival, withdrawal trend, IQVIA MIDAS Turkey, IQVIA MIDAS 36-country, Turkey market size, cross-country market comparison, biowaiver, BCS classification, dissolution profile, Reliance target analysis, generic eligibility Turkey.

### (B) Semantic auto-triggers (content-based)

Sub-protocol auto-load edilir eğer query:

- TİTCK barkod, ATC kodu, eşdeğer grup, withdrawal/iptal terimleri içeriyor **VE** development/feasibility intent var (örn. "X molekülünün Türkiye'de jenerik fizibilitesi nedir")
- Cross-country pazar kıyaslama talebi var (örn. "GLP-1 RA Türkiye + Almanya + İtalya satış kıyası")
- Orange Book RLD + TE rating + Türkiye eşdeğer grup birlikte sorgulanıyor
- BCS classification + biowaiver eligibility + Türkiye jenerik eligibility'si tartışılıyor
- AdisInsight pipeline + Türkiye pazar büyüklüğü + jenerik patent landscape üçlü kombinasyonu

### (C) Forbidden triggers

❌ Kullanıcının Roche / yerli pharma / multinational'da çalışıyor olması
❌ Memory'den gelen "user works on product development in Turkey"
❌ Query yazım dilinin Türkçe olması (sadece **content** trigger; bkz. `generic-by-default.md` §5.3)

---

## §3. Source Acquisition Layer — 4-Channel Integrated Data Stack

Bu sub-protocol pharmaintel'in mevcut MCP-first / API-first / web-fetch-fallback hiyerarşisini (`api-integrations.md` §1) aşağıdaki dört kanalla **genişletir**. Her kanal farklı bir sorgu profili ve confidence tier'ına sahiptir.

### §3.1 Channel A — TİTCK MCP (Türkiye regulatuar primary)

**Confidence tier:** Tier-0 primary (Türkiye regulatuar zemin gerçeği)
**Coverage:** Ruhsatlı ürünler, fiyat zinciri, eşdeğer grup, kullanım protokolü, withdrawal, biyobenzer ilk-onay, ATC sınıf snapshot, holder portföy

**Tool catalogue (mandatory pre-Phase-2 read):**

| Tool | Use case | Pharmaintel pattern |
|---|---|---|
| `TİTCK:search_drugs` | Barkod-bazlı veya brand/INN bazlı tam-metin arama | İlk kontak; "X molekülü Türkiye'de var mı" |
| `TİTCK:get_drug` | Tek bir barkod/record için tam veri | KÜB metadata, fiyat zinciri, holder, ATC |
| `TİTCK:get_drug_snomed_profile` | Master record + SNOMED/ATC özeti | INN harmonization (yabancı ↔ Türkçe etken madde) |
| `TİTCK:search_by_atc` | ATC kodu bazlı portföy taraması | Sınıf doygunluğu, white-space identification |
| `TİTCK:search_by_substance` | SNOMED CT substance bazlı arama | Cross-language substance harmonization |
| `TİTCK:get_atc_class_summary` | ATC sınıfı için aggregate snapshot | Pazar yapısı, holder dağılımı, yeni-onay frekansı |
| `TİTCK:get_atc_hierarchy` | ATC parent/sibling/child seti | Sınıf-içi pozisyonlama analizi |
| `TİTCK:find_equivalent_products_by_substance` | Aynı substance'a sahip diğer TR ürünler | **Eşdeğer grup mapping** — fiyat tavanı kalkülasyonu için kritik |
| `TİTCK:find_shared_substance_peers` | Substance-paylaşan peer'lar | Combination + multi-API ürünler için |
| `TİTCK:find_biosimilar_group` | Aynı SNOMED substance peer'ları, en eski authorization flag | Biyobenzer ilk-onay verifikasyonu |
| `TİTCK:find_first_in_class` | ATC sınıfında ilk authorization + sponsor | First-mover advantage analizi |
| `TİTCK:get_price_history` | Fiyat zinciri (FSF/depocu/eczacı/perakende) + İŞLEM GEÇMİŞİ | TL fluctuation impact + tavan fiyat |
| `TİTCK:find_reference_prices_for_drug` | Referans fiyat listesi linking | 5-ülke referans rasyo |
| `TİTCK:compare_drug_to_alternatives` | Same-substance + same-ATC peer kıyası | Düz competitive landscape |
| `TİTCK:compare_holders` | İki MAH portföy yan-yana | Yerli vs multinational competitive map |
| `TİTCK:get_holder_portfolio` | MAH için ATC/substance/withdrawal roll-up | Sponsor diligence |
| `TİTCK:find_authorization_cancellations_for_drug` | Ruhsat iptali kayıtları | Withdrawal / market exit signal |
| `TİTCK:get_withdrawal_trend` | Yıl-bazlı iptal aggregation | ATC class viability proxy |
| `TİTCK:find_new_authorizations_since` | Belirli tarih sonrası master records | Pipeline early-warning |
| `TİTCK:find_off_label_uses_for_drug` | Onkoloji off-label list linking | Endikasyon dışı kullanım intelligence |
| `TİTCK:find_regulation_article23_for_drug` | Madde 23 başvuruları | Compassionate use sinyali |
| `TİTCK:find_documents_for_drug` | KÜB/KT/scientific assessment PDF/DOCX | Hekim bilgi metni veri katmanı |
| `TİTCK:find_supply_tracked_ingredients_for_drug` | Tedarik takibi | Supply security risk |
| `TİTCK:find_scheduling_records_for_drug` | Aylık takvimlendirme listesi | Yakın-vade ruhsat etkinlikleri |
| `TİTCK:get_dataset_overlap` | Modüller arası Jaccard/coverage | Veri kalite diagnostics |
| `TİTCK:list_unmapped_ingredients` | SNOMED CT mapping eksikleri | Veri gap awareness |

**Discipline rules:**

1. TİTCK MCP **HER ZAMAN** Türkiye regulatuar/fiyat claim'leri için Tier-0 primary'dir. Web search / Fetch sonuçları TİTCK MCP ile çelişiyorsa TİTCK MCP'ye uy.
2. SNOMED substance harmonization olmadan multi-INN combination ürünler için "eşdeğer grup" çıkarımı yapma (`find_equivalent_products_by_substance` kullan).
3. Fiyat history her zaman `get_price_history` ile çek; KAP/Resmi Gazete fiyat duyuruları ek-validation.
4. Withdrawal trend için tek bir cancellation **trend değildir**; `get_withdrawal_trend` aggregate veriyi tercih et.

### §3.2 Channel B — ThoughtSpot MCP (IQVIA MIDAS analytical layer)

**Confidence tier:** Tier-1 commercial primary (sponsor-curated IQVIA verisi, third-party panel)
**Coverage:** 36 ülke aylık satış (volume + value + price + share), product/molecule/ATC class/sponsor/country dimension'larında

**Pre-condition:** ThoughtSpot MCP server ThoughtSpot tenant'ı IQVIA MIDAS data feed ile bağlanmış olmalı; her invokasyon OAuth ile RLS/CLS kuralları altında çalışır.

**Tool catalogue:**

| Tool | Use case | Pharmaintel pattern |
|---|---|---|
| `ping` | Health check | Erken erişilebilirlik teyidi |
| `getDataSourceSuggestions` | Mevcut data model'leri öner | İlk kontak — hangi MIDAS scope erişilebilir |
| `getRelevantQuestions` | Yüksek-seviye soruyu alt-analitik sorulara böl | Cross-country market sizing decomposition |
| `getAnswer` | Alt-soru için preview data + frame_url + session_identifier + generation_number | Aslı analitik dönüş |
| `createLiveboard` | Konuşma sonu Liveboard üretimi | Persistent paylaşılabilir analiz çıktısı |

**Canonical query patterns:**

**Pattern 1 — Türkiye + 5-country reference + EU peer set monthly trend:**

```
Step 1: getDataSourceSuggestions
  → Identify "MIDAS Monthly Sales by Country" model

Step 2: getRelevantQuestions(
  prompt: "Show monthly TRx volume and EUR value sales for [INN/ATC] in
           Turkey, France, Spain, Italy, Greece, Portugal, Germany, UK
           over last 36 months, broken by molecule and corporation",
  data_source: "MIDAS Monthly Sales by Country"
)
  → Returns 4-7 sub-questions

Step 3: For each sub-question, getAnswer(...)
  → Each call returns:
    - preview data (~200 rows)
    - frame_url (embeddable)
    - session_identifier + generation_number (for Liveboard)

Step 4: (optional) createLiveboard(
  question_array: [<each Q + sid + gen>],
  title: "[INN] cross-country MIDAS monthly trend"
)
  → Returns Liveboard frame_url for sharing
```

**Pattern 2 — ATC class share analysis across 36 countries (single snapshot):**

```
getRelevantQuestions(
  prompt: "Show market share by molecule within ATC [ATC4-code] for the
           latest available month across all 36 MIDAS countries; rank by
           USD value sales",
  data_source: "MIDAS Sales by ATC Class"
)
→ Decomposes into per-country share + leaders + emerging entrants

Multiple getAnswer calls run in parallel (orchestration.md §2.1)
```

**Pattern 3 — Genericization trajectory after LOE:**

```
getRelevantQuestions(
  prompt: "For [INN], show monthly volume and value evolution by brand/
           generic flag in Turkey vs. EU5 vs. US over the 24 months
           pre/post first generic entry",
  data_source: "MIDAS Brand vs Generic Trajectory"
)
→ Decomposes into: pre-LOE baseline, post-LOE month-3/6/12 erosion,
  generic share build-up by quartile
```

**Pattern 4 — Cross-country price benchmarking:**

```
getRelevantQuestions(
  prompt: "For [INN/strength/dosage form], compare ex-manufacturer EUR
           price across France, Spain, Italy, Greece, Portugal, Germany,
           UK, and Turkey for the latest month",
  data_source: "MIDAS Ex-Manufacturer Pricing"
)
→ Output feeds 5-country reference price calculation (§4.2)
```

**Discipline rules:**

1. **Provenance stamp:** Every ThoughtSpot-derived claim must record `(data_source, query_sid, gen_number, retrieved_at_iso)` in §Provenance Disclosure.
2. **RLS/CLS respect:** ThoughtSpot tenant'ında uygulanan row/column-level security rules MCP üzerinden de geçerlidir; MCP atlatma yoktur. Erişilemeyen veri "data-redacted" olarak raporlanır.
3. **MIDAS panel kısıtları:** MIDAS bir **panel-projected estimate**'tir; gerçek ünite-bazlı şipping verisi değildir. Hospital-only ürünler için kapsama düşüktür; OTC ürünler için panel asimmetriktir. Bu kısıtlar her rapor §Limitations'ta açıkça belirtilmelidir.
4. **Currency normalization:** MIDAS hem local currency hem EUR/USD verir. Türkiye için TL-bazlı verinin EUR/USD'ye normalizasyonu kur tarihiyle eşleştirilmelidir; aksi halde TL deprecation yanılsama yaratır.
5. **Liveboard creation OPSIYONEL:** Default olarak `getAnswer` preview data ile rapor üret; `createLiveboard` ancak kullanıcı "kalıcı paylaşılabilir analiz" isterse çağrılır.
6. **No regional inference from user identity:** Kullanıcı Türkiye'de çalışıyor olsa bile, query Türkiye'yi çağırmadıysa default 36-ülke global scope korunur (`generic-by-default.md` Article 5).

### §3.3 Channel C — AdisInsight MCP (pipeline + drug intelligence)

**Confidence tier:** Tier-1 curated commercial intelligence (Springer Adis editorial team)
**Coverage:** Global drug pipeline (preclinical → marketed), clinical trials, sponsor company portfolios, M&A, indication mapping, drug class taxonomy

**Tool catalogue:**

| Tool | Use case |
|---|---|
| `AdisInsight:search_drugs` | INN/brand/development phase/therapeutic area filtering |
| `AdisInsight:get_drug` | Tek-ilaç deep dive: dev_phase, dev_company, indications, mechanisms, targets |
| `AdisInsight:search_trials` | Clinical trial discovery (AdisInsight curated, ClinicalTrials.gov ile çakışan ama metadata zenginleştirilmiş) |
| `AdisInsight:get_trial` | Trial deep dive |
| `AdisInsight:search_drug_companies` | Şirket portföy analizi (drug development emphasis) |
| `AdisInsight:search_trial_companies` | Şirket trial sponsorship analizi |
| `AdisInsight:analyze_endpoints` | Primary/secondary endpoint pattern |
| `AdisInsight:generate_chart` | Hızlı pipeline grafiği (phase/sponsor/indication breakdown) |

**Canonical patterns for product development:**

**Pattern 1 — Pre-development pipeline scan:**

```
search_drugs(
  filters: {
    therapeutic_area_contains: "[TA]",
    dev_phase: ["Phase III", "Pre-registration", "Marketed"],
    available_for_licensing: true   # eğer in-licensing araştırılıyorsa
  }
)
→ Returns shortlist of in-licensable assets
```

**Pattern 2 — Modality landscape for "next biosimilar candidate":**

```
search_drugs(
  filters: {
    drug_class_type: "biological",
    dev_phase: "Marketed",
    has_patent_data: true   # patent-cliff yakın olanlar için
  }
)
→ Sort by years-to-LOE; cross-reference with TİTCK biyobenzer onay durumu
```

**Pattern 3 — Endpoint pattern für rare disease:**

```
analyze_endpoints(
  therapeutic_area: "[rare]",
  phase: "Phase III"
)
→ Identifies registry-enabled endpoint trends (natural history controls,
  external comparator, single-arm + Bayesian) — feasibility input for
  Türkiye'de RWE-driven dossier strategy
```

**Discipline rules:**

1. AdisInsight Tier-1'dir, **Tier-0 değil** — primary FDA/EMA/TİTCK kaynağı ile triangüle edilmelidir (`triangulation.md` §2).
2. AdisInsight curated subset'tir; absent of an asset ≠ confirmed non-existence (özellikle Çinli/Hintli pre-clinical asset'ler için).
3. `get_drug` tek-call'da geniş veri verir — pharmaintel default olarak BU çağrıyı `search_drugs` shortlist'inden sonra kullanmalı.

### §3.4 Channel D — openFDA + Orange Book + Purple Book (US regulatory primary)

**Confidence tier:** Tier-0 primary (FDA regulatory truth)
**Coverage:** US NDA/ANDA/BLA history, label, FAERS, recall, NDC, Orange Book TE rating + patent + exclusivity, Purple Book biosimilar/interchangeability

`api-integrations.md` §2-4 zaten bu kanalları kodlar; bu sub-protocol Türkiye **product development** bağlamında özel sorgu örüntülerini ekler.

**Pattern 1 — Generic eligibility decision tree (US Orange Book → TR feasibility bridge):**

```
Step 1: openFDA Drugs@FDA: Identify RLD (Reference Listed Drug) for [INN]
  GET /drug/drugsfda.json?search=openfda.generic_name:"[INN]"+
                                AND submissions.submission_class_code:NDA

Step 2: Orange Book products.txt + patent.txt + exclusivity.txt
  → Determine: TE rating (AB-rated → biowaiver-eligible bioequivalence;
                AA-rated → no biowaiver; BX-rated → unresolved;
                BC-rated → controlled-release pair restrictions)
  → Patent expiry list (filter by Use Code U-XXXX for indication-specific)
  → Exclusivity expiry (NCE = 5y, NPP = 3y, ODE = 7y, PED = +6mo, GAIN = +5y)

Step 3: BCS classification check (FDA BCS biowaiver guidance)
  → API: openFDA does NOT directly expose BCS class
  → Fallback: WHO/EMA biowaiver lists + literature search (CRP-validated
     dissolution profile)

Step 4: TİTCK eşdeğer grup mapping
  → TİTCK:find_equivalent_products_by_substance(barcode/record_id)
  → Identify Türkiye'deki existing eşdeğer grup üyeleri + price ceiling

Step 5: Feasibility verdict synthesis
  Inputs:
    - US Orange Book pathway clarity (RLD identified, TE rating known)
    - Patent + exclusivity tail (US-side; TR patent ayrı SMK 6769 frame)
    - BCS class (biowaiver eligibility)
    - TR eşdeğer grup saturation (number of existing generics)
    - TR price ceiling (5-country reference + 30-40% generic discount)
  Output: structured feasibility scorecard (§5.1)
```

**Pattern 2 — Biosimilar candidate scan via Purple Book → TR biyobenzer durum:**

```
Step 1: Purple Book monthly Excel
  → Filter: BLA holders, reference products, biosimilar/interchangeable flags

Step 2: BPCIA exclusivity arithmetic
  → 12y RP exclusivity floor; 4y biosimilar application bar
  → Actual LOE landing date

Step 3: TİTCK:find_biosimilar_group(barcode of TR-marketed innovator)
  → Identify Türkiye'deki existing biyobenzer count + first-onay yılı

Step 4: Cross-country biosimilar uptake via ThoughtSpot MIDAS
  → Pattern: post-biosimilar share trajectory in EU5
  → Project Türkiye uptake under analogous conditions

Step 5: Synthesis: TR biyobenzer market entry timing + projected share
```

**Pattern 3 — Withdrawal/discontinuation signal (US Recall + TR cancellation):**

```
Step 1: openFDA Recall enforcement: Recent recalls for [INN]
Step 2: TİTCK:find_authorization_cancellations_for_drug
Step 3: TİTCK:get_withdrawal_trend (ATC class level)
Step 4: Cross-correlate: US recall → TR cancellation lag pattern
        (typical: 6-18 months for Class I recalls)
```

---

## §4. Decision-Support Modules

Bu sub-protocol pre-defined modüller içerir; her modül belirli bir geliştirme sorusuna cevap üretir.

### §4.1 Module M1 — Generic Feasibility Scorecard

**Soru:** "[INN] molekülü için Türkiye'de jenerik geliştirme yapmalı mıyız?"

**Inputs (auto-acquired):**

| Input | Source | Tool |
|---|---|---|
| US RLD identification | openFDA | Drugs@FDA |
| US TE rating | Orange Book | products.txt |
| US patent + exclusivity tail | Orange Book | patent.txt + exclusivity.txt |
| BCS class (proxy) | EMA/WHO biowaiver list | web_fetch |
| TR ruhsat statüsü | TİTCK MCP | search_drugs / get_drug |
| TR eşdeğer grup saturation | TİTCK MCP | find_equivalent_products_by_substance |
| TR fiyat zinciri | TİTCK MCP | get_price_history |
| TR ATC sınıf doygunluğu | TİTCK MCP | get_atc_class_summary |
| Yerli vs multinational holder map | TİTCK MCP | search_by_atc + get_holder_portfolio |
| TR Reliance pathway eligibility | sub-protocol-turkey §Reliance | inline |
| Cross-country generic uptake pattern | ThoughtSpot MIDAS | Pattern 3 (§3.2) |
| Pipeline pre-emption risk | AdisInsight | search_drugs (filter dev_phase Phase III/Marketed, generic) |

**Scoring framework (10-point composite):**

| Dimension | Weight | Scoring rubric |
|---|---|---|
| **Patent + exclusivity proximity** | 25% | LOE >5y away → 0; 2-5y → 5; <2y → 8; expired → 10 |
| **BCS biowaiver eligibility** | 15% | Class I (high sol/perm) → 10; Class III → 7; Class II/IV → 3 (full bioequivalence required) |
| **TR eşdeğer grup density** | 15% | 0 generics → 10; 1-3 → 7; 4-6 → 4; 7+ → 1 (saturated) |
| **TR price ceiling viability** | 15% | Post-discount margin >25% → 10; 15-25% → 6; <15% → 2 |
| **TR ATC class growth (3y MIDAS CAGR)** | 10% | >10% → 10; 5-10% → 7; 0-5% → 4; declining → 1 |
| **Cross-country generic uptake reference** | 10% | EU5 12-month post-LOE share >50% → 10; 30-50% → 6; <30% → 3 |
| **TR Reliance pathway eligibility** | 10% | Eligible (FDA/EMA approved + WHO PQ) → 10; partial → 5; ineligible → 0 |

**Verdict thresholds:**

- **8.0+ → STRONG GO:** High-priority development candidate
- **6.0-7.9 → CONDITIONAL GO:** Develop with mitigations (e.g., 505(b)(2)-style differentiation, niche dosage form)
- **4.0-5.9 → STAND BY:** Monitor for window; revisit at LOE -24 months
- **<4.0 → NO GO:** Saturated/economically non-viable

**Output template:**

```markdown
## Module M1 — [INN] Türkiye Jenerik Fizibilite Skorkartı

**Karar:** [STRONG GO / CONDITIONAL GO / STAND BY / NO GO] (Toplam skor: X.X / 10)

| Boyut | Ham veri | Skor | Ağırlıklı katkı |
|---|---|---|---|
| Patent + exclusivity yakınlığı | [LOE: YYYY-MM-DD; X yıl] | X/10 | X.XX |
| BCS biowaiver eligibility | [Class I/II/III/IV; gerekçe] | X/10 | X.XX |
| TR eşdeğer grup yoğunluğu | [N existing generics] | X/10 | X.XX |
| TR fiyat tavanı uygunluğu | [Post-discount margin %X] | X/10 | X.XX |
| TR ATC sınıf büyümesi (3y CAGR) | [X.X% (MIDAS)] | X/10 | X.XX |
| Cross-country uptake referansı | [EU5 12mo post-LOE share %X] | X/10 | X.XX |
| TR Reliance eligibility | [eligible/partial/ineligible + gerekçe] | X/10 | X.XX |

**Kritik gerekçeler:** [3-5 paragraflık narrative]
**Riskler:** [identified risks per dimension]
**Mitigation önerileri:** [if CONDITIONAL GO]
```

### §4.2 Module M2 — Price Ceiling Simulation

**Soru:** "[INN] için Türkiye'de uygulanabilecek maksimum fabrika fiyatı + son tüketici fiyatı nedir?"

**Türkiye fiyatlandırma referans sistemi (Cumhurbaşkanlığı Kararı No. 11031, 11038 ve sonrası TİTCK Fiyat Değerlendirme Komisyonu uygulaması):**

```
Step 1: 5-ülke referans fiyat tabanı
  → Sources: France (CEPS), Spain (Nomenclator/BotPlus), Italy (AIFA),
    Greece (EOF), Portugal (INFARMED)
  → Acquisition: ThoughtSpot MIDAS Pattern 4 (§3.2) — ex-manufacturer
    EUR price for [INN/strength/form] for the latest reference month
  → Selected price: minimum of 5-country panel ex-manufacturer EUR price

Step 2: TL conversion at TİTCK Euro-Değer (avro-değer)
  → Reference Euro-Değer published by TİTCK; updated periodically
  → As of v8.0.0 release: ~10.50 TL/EUR (snapshot — VERIFY at runtime)

Step 3: Generic discount mandate
  → New generic must be priced ≤ 60-70% of innovator ex-manufacturer
  → Per equivalence group rules (Beşeri Tıbbi Ürünlerin Fiyatlandırılmasına
    Dair Karar; specific % depends on equivalence group position)

Step 4: Apply mark-up chain (sub-protocol-turkey §Pricing)
  Ex-manufacturer (depocu fiyatı)
    → +Depocu margin (4-9% sliding)
    → +Eczacı margin (12-25% sliding)
    → +KDV (currently 8% for human drugs)
  = Pharmacy retail price

Step 5: Apply mandatory discount Ek-4B
  → 4-41% sponsor discount per equivalence group + reimbursement status
```

**Auto-acquisition workflow:**

```
Inputs needed:
  - INN, strength, dosage form, pack size
  - Equivalent group classification (TİTCK find_equivalent_products_by_substance)
  - Reference month for 5-country price (ThoughtSpot MIDAS)
  - Current TİTCK Euro-Değer (web_fetch titck.gov.tr fiyat duyuruları)
  - Innovator status (originator vs already-generic) (TİTCK get_drug)
  - Reimbursement status (SUT, Ek-4A/4B/4D) (cross-reference SGK)

Output:
  - Ex-manufacturer ceiling (TL)
  - Pharmacy retail ceiling (TL)
  - Sponsor net realized price after Ek-4B (TL)
  - Margin % vs assumed COGS
  - Sensitivity: TL ±10% deprecation impact
```

**Output template:**

```markdown
## Module M2 — [INN] Türkiye Fiyat Tavanı Simülasyonu

**Snapshot tarihi:** [YYYY-MM-DD]
**Euro-Değer (TİTCK):** X.XX TL/EUR

| Adım | Değer | Kaynak |
|---|---|---|
| 5-ülke en-düşük ex-manufacturer EUR | X.XX EUR | MIDAS [country/month] |
| TL'ye çevrim | X.XX TL | TİTCK Euro-Değer |
| Jenerik indirimi sonrası ex-manufacturer | X.XX TL | -%XX (eşdeğer grup pozisyonu) |
| +Depocu marjı | X.XX TL | %X (ilaç bedeli skalası) |
| +Eczacı marjı | X.XX TL | %X (ilaç bedeli skalası) |
| +KDV %8 | X.XX TL | — |
| **Eczane perakende fiyatı** | **X.XX TL** | — |
| -Sponsor Ek-4B zorunlu indirimi | -%X | SUT |
| **Sponsor net realize fiyat** | **X.XX TL** | — |

**Sensitivity (TL ±10%):** Fiyat aralığı X.XX–X.XX TL
**Implied gross margin:** assumed COGS X.XX TL → margin %XX
**Karar implikasyonu:** [3-5 cümle]
```

### §4.3 Module M3 — Cross-Country Market Sizing (36-country comparison)

**Soru:** "[INN/ATC class] için Türkiye'nin pazar büyüklüğü 36-ülke kıyasında nerede?"

**Inputs:**
- 36-ülke MIDAS aylık satış (volume + value)
- ATC class sınıflandırma
- Brand/generic split
- Population denominator (TÜİK/UN World Population Prospects)
- Healthcare expenditure denominator (WHO GHO / OECD Health Statistics)

**Workflow:**

```
Step 1: ThoughtSpot MIDAS — get value sales (USD/EUR) by country, latest 12 months
Step 2: Per-country: divide by population (per-capita unit access)
        + divide by healthcare expenditure (intensity index)
Step 3: Rank Türkiye position in distribution
Step 4: Identify "structural peers" (similar GDP per capita, similar
        epidemiology — typically Spain, Italy, Greece, Portugal, Poland,
        Mexico, Brazil, Argentina)
Step 5: Calculate gap-to-peer-median (potential under-utilization signal)
Step 6: Cross-reference with TİTCK ATC class growth → access gap may be
        regulatory-bound vs access-bound
```

**Output template:**

```markdown
## Module M3 — [INN/ATC] Cross-Country Market Sizing (MIDAS 36-country)

**Period:** [YYYY-MM to YYYY-MM, 12 months]

| Country | Value sales (USD M) | Volume (DDD M) | Per-capita value (USD) | % of TR |
|---|---|---|---|---|
| Türkiye | X.X | X.X | X.X | 100% (ref) |
| France | X.X | X.X | X.X | XX% |
| Spain | X.X | X.X | X.X | XX% |
| ... (36 countries) | | | | |

**Türkiye position:** N/36 by absolute value, N/36 by per-capita
**Structural peer median (Spain+Italy+Greece+Portugal+Poland+Mexico+Brazil):** USD X.X per-capita
**Türkiye gap to peer median:** ±%X
**Inferred under-/over-utilization:** [narrative]
**ATC class growth rationale:** [TİTCK class summary cross-ref]
```

### §4.4 Module M4 — Equivalent Group Mapping & Saturation Analysis

**Soru:** "[INN] için Türkiye eşdeğer grup yapısı nedir? Yeni bir entrant için yer var mı?"

**Workflow:**

```
Step 1: TİTCK find_equivalent_products_by_substance(barcode of any
        marketed product with [INN])
Step 2: Group result by SNOMED substance combination
        + strength class + dosage form
Step 3: For each equivalence group, retrieve get_drug(barcode) to obtain:
        - Holder
        - Authorization date
        - Current price (get_price_history)
        - Withdrawal status (find_authorization_cancellations_for_drug)
Step 4: Compute saturation metrics:
        - Active members count
        - Holder concentration (Herfindahl-Hirschman style)
        - Years since last new entry
        - Authorized but discontinued count (zombie products)
Step 5: White-space identification:
        - Missing strengths/forms
        - Missing dosing schedule (e.g., XR not yet generic)
        - Missing combinations
```

**Output template:**

```markdown
## Module M4 — [INN] Türkiye Eşdeğer Grup Mapping

| Eşdeğer grup | Strength | Form | Active üye | Holder concentration | Son giriş |
|---|---|---|---|---|---|
| EG-A | XX mg | tablet | N | HHI: X.XX | YYYY-MM |
| EG-B | XX mg | XR tablet | N | HHI: X.XX | YYYY-MM |
| EG-C | combo X+Y | tablet | N | HHI: X.XX | YYYY-MM |

**Saturation verdict:** [SATURATED / EMERGING / WHITE-SPACE]
**Identified white-space:** [list]
**Yerli vs MNC dominance:** [HHI breakdown by ownership type]
**Zombie product count:** [authorized-but-discontinued]
**Recommendation:** [development thesis]
```

### §4.5 Module M5 — Biowaiver / BCS Eligibility Assessment

**Soru:** "[INN] için Türkiye'de jenerik geliştirirken biowaiver başvurabilir miyiz?"

**Türkiye biowaiver framework:**

TİTCK, bioequivalence çalışması zorunluluğunu **EMA Bioequivalence Guideline (CPMP/EWP/QWP/1401/98 Rev. 1/Corr **)** ile harmonize etmiştir. Biowaiver kabul edilebilir koşullar:

1. **BCS Class I (yüksek çözünürlük + yüksek geçirgenlik)** + immediate-release oral solid dosage form
2. **BCS Class III (yüksek çözünürlük + düşük geçirgenlik)** — sınırlı koşullar (FDA 2017 guidance + EMA 2010 amendment); özellikle excipient compatibility
3. **Strength biowaiver** — proportional formulation + dissolution similarity (f2 ≥ 50)
4. **Solution forms** — bioequivalence varsayılır

**Workflow:**

```
Step 1: BCS class identification
  → Source A: WHO Essential Medicines BCS list
  → Source B: EMA/FDA biowaiver assessment reports (literature)
  → Source C: Peer-reviewed Cmax/AUC + solubility/permeability data
  → Source D: Literature review (PubMed via medsearch handoff)

Step 2: Dosage form check
  → Immediate-release oral solid? (BCS biowaiver applicable)
  → Modified-release? (no BCS biowaiver; full BE study required)
  → Solution? (BE assumed; no clinical study)
  → Topical/inhalation/parenteral? (no BCS framework; specific guidance)

Step 3: Excipient compatibility
  → Are excipients quantitatively/qualitatively similar to RLD?
  → Q1/Q2 (qualitative + quantitative sameness) requirement varies by jurisdiction

Step 4: Dissolution similarity (if proportional strength biowaiver applied)
  → f2 calculation (FDA/EMA both accept f2 ≥ 50 as sufficient similarity)
  → 12-tablet × 3 media (pH 1.2, 4.5, 6.8)

Step 5: Verdict
  → BIOWAIVER ELIGIBLE / BIOWAIVER POSSIBLE WITH SUPPLEMENTARY DATA / FULL BE REQUIRED
```

**Output template:**

```markdown
## Module M5 — [INN] Biowaiver Eligibility (Türkiye)

| Boyut | Değerlendirme | Kaynak |
|---|---|---|
| BCS class | I / II / III / IV (gerekçe) | [WHO list / EMA EPAR / literature] |
| Dosage form | IR oral solid / MR / solution / other | [pharmacopeia / RLD label] |
| Çözünürlük (highest dose / 250 mL) | High / Low | [WHO list / EMA / literature] |
| Geçirgenlik (Caco-2, in vivo) | High / Low | [literature] |
| Excipient Q1/Q2 alignment | Yes / partial / No | [planned formulation] |
| Dissolution similarity (f2) | ≥50 / <50 / not yet tested | [development plan] |

**Verdict:** [BIOWAIVER ELIGIBLE / POSSIBLE WITH SUPPLEMENTARY / FULL BE REQUIRED]
**Gerekçe:** [3-5 cümle bilimsel temellendirme]
**Türkiye TİTCK position:** [kullanılan pathway + emsal başvurular]
**Ek-veri ihtiyacı:** [list of studies still needed]
**Maliyet implikasyonu:** [BE çalışması ~150-300K USD vs biowaiver dossier ~30-60K USD]
```

### §4.6 Module M6 — Withdrawal Trend & Market Exit Risk

**Soru:** "[ATC class / INN] için Türkiye'de withdrawal trend'i ne diyor? Geliştirme bittikten sonra pazardan çekilme riski yüksek mi?"

**Workflow:**

```
Step 1: TİTCK get_withdrawal_trend(atc_code)
  → Yıl-bazlı iptal aggregation
Step 2: Cross-reference: TİTCK find_authorization_cancellations_for_drug
        for each marketed product in the equivalence group
Step 3: Identify cancellation reason patterns:
  - Holder voluntary withdrawal (commercial)
  - Compulsory (safety, GMP, supply)
  - Renewal failure
Step 4: Calculate "active member half-life" — average years from
        authorization to withdrawal for the class
Step 5: Cross-reference: openFDA Recall enforcement (US) for the same INN
Step 6: ThoughtSpot MIDAS volume trajectory for the class — declining vs growing
```

**Output template:**

```markdown
## Module M6 — [ATC/INN] Withdrawal Trend (Türkiye)

**ATC class:** [code + WHO label]
**Withdrawals 2020-2026 (annual):** [N, N, N, N, N, N, N]
**5-year trend slope:** [+X% / -X% / flat]
**Active member half-life:** X.X years
**Top cancellation reasons:**
  1. [reason] — N cases
  2. [reason] — N cases
  3. [reason] — N cases
**Cross-correlation with US recalls:** [+X.X correlation; N matched events]
**MIDAS volume trajectory (3y):** [+X% CAGR / -X% CAGR]
**Risk verdict:** [LOW / MEDIUM / HIGH]
```

### §4.7 Module M7 — Reliance Pathway Target Identification

**Soru:** "TR Reliance Pathway için en yüksek-değerli geliştirme hedefleri hangi ürünler/sınıflar?"

**Workflow:**

```
Step 1: openFDA + EMA EPAR — fetch list of approved products in last 24 months
        with FDA Priority Review / Breakthrough OR EMA PRIME/conditional approval
Step 2: Filter: products NOT yet authorized in Türkiye
        (TİTCK search_drugs returns empty for INN)
Step 3: AdisInsight — verify dev_company has Turkey presence OR
        active in-licensing programs
Step 4: ThoughtSpot MIDAS — per-country rollout trajectory of comparable
        Reliance candidates (typical 4-6 month TİTCK timeline post-EMA/FDA)
Step 5: Score by:
  - Indication unmet need in Turkey (epidemiology + existing SUT alternatives)
  - Reimbursement viability (cost vs SGK budget impact)
  - Licensing availability
```

**Output:** Ranked list with feasibility narrative.

---

## §5. Cross-Source Triangulation Patterns

Bu sub-protocol pharmaintel'in standart `triangulation.md` framework'üne özel patterns ekler.

### §5.1 Pattern P1 — TİTCK ↔ openFDA (US-TR regulatory harmonization)

```
Claim: "[INN] is approved in Türkiye and FDA-approved with same indication"
Verification:
  Source A: TİTCK MCP get_drug → KÜB indication text
  Source B: openFDA Drug Label → INDICATIONS_AND_USAGE
  Source C: EMA EPAR (if EMA-approved) → SmPC indication
  → Triangulation: 3 primary sources, exact text alignment expected
  → Discrepancy alert if KÜB indication is narrower than FDA label
    (TR-spesifik label trimming common)
```

### §5.2 Pattern P2 — ThoughtSpot MIDAS ↔ TİTCK (volume vs authorized count)

```
Claim: "Türkiye'de N adet [INN] eşdeğer grubu pazarda + aylık X adet TRx"
Verification:
  Source A: TİTCK find_equivalent_products_by_substance → authorized N
  Source B: TİTCK find_authorization_cancellations_for_drug → cancelled M
  Source C: ThoughtSpot MIDAS Turkey monthly → reported volume
  → If MIDAS volume reflects fewer brands than (N - M) → potential supply
    interruption or panel coverage gap; flag for explicit acknowledgement
```

### §5.3 Pattern P3 — AdisInsight ↔ TİTCK (pipeline vs marketed reality)

```
Claim: "[Sponsor] has [phase] pipeline in [TA] for Türkiye"
Verification:
  Source A: AdisInsight search_drugs(filters: dev_company, dev_phase, TA)
  Source B: TİTCK search_holders + get_holder_portfolio
  Source C: ClinicalTrials.gov MCP search_trials with location:Turkey
  → AdisInsight pipeline + TİTCK holder presence + active TR trial site
    = highest-confidence "true Turkish development engagement"
```

### §5.4 Pattern P4 — 5-country reference price triangulation

```
Claim: "5-ülke en-düşük fiyat = X EUR for [INN/strength]"
Verification:
  Source A: ThoughtSpot MIDAS Pattern 4 — ex-manufacturer EUR per country
  Source B: National sources (CEPS BotPlus / Nomenclator / AIFA / EOF / INFARMED)
            via web_fetch where accessible
  Source C: TİTCK reference price registry (find_reference_prices_for_drug)
  → MIDAS often reflects published list; national sources may include
    confidential discounts (rebates) — flag the difference if material
```

---

## §6. Standard Deliverable: TR-PD Feasibility Report

Bu sub-protocol'ün kanonik çıktısı **TR-PD Feasibility Report** template'idir. Yapı:

```markdown
# [INN/Brand] — Türkiye Ürün Geliştirme Fizibilite Raporu

**Rapor tarihi:** YYYY-MM-DD
**Sub-protocol version:** product-development-tr v1.0.0
**G22 audit:** [PASS]
**Sources triangulated:** TİTCK MCP + ThoughtSpot MIDAS + AdisInsight + openFDA

---

## §1. Executive Summary

[3-paragraph C-suite-ready synthesis]

## §2. Asset Profile (T2 layer handoff)

[task-asset.md output, US/EMA/TR regulatory triangulation]

## §3. Türkiye Regulatuar Durum

### 3.1 TİTCK ruhsat durumu
[get_drug + get_holder_portfolio output]

### 3.2 Eşdeğer grup yapısı
[Module M4 output]

### 3.3 Withdrawal trend
[Module M6 output]

### 3.4 Reliance pathway eligibility
[sub-protocol-turkey §Reliance + Module M7 cross-ref]

## §4. Pazar Büyüklüğü & Cross-Country

### 4.1 36-ülke MIDAS snapshot
[Module M3 output]

### 4.2 Türkiye structural-peer gap
[narrative analysis]

### 4.3 ATC class growth & competitive density
[get_atc_class_summary + MIDAS class trajectory]

## §5. Patent + Exclusivity Tail

### 5.1 US Orange Book
[patent.txt + exclusivity.txt parsing]

### 5.2 TR SMK 6769 perspective
[handoff to pharmapatent skill if available]

### 5.3 LOE landing date convergence
[earliest common date across jurisdictions]

## §6. Geliştirme Pathway

### 6.1 Bioequivalence vs biowaiver
[Module M5 output]

### 6.2 Tahmini geliştirme süresi & maliyet
[BE study + dossier + TİTCK review timeline]

### 6.3 Reliance vs full national pathway
[decision matrix]

## §7. Fiyat Tavanı & Margin

### 7.1 Price ceiling simulation
[Module M2 output]

### 7.2 Margin sensitivity
[TL deprecation, COGS scenarios]

### 7.3 Reimbursement assumption
[SUT placement strategy]

## §8. Karar — Generic Feasibility Scorecard

[Module M1 output]

## §9. Riskler & Mitigation

[risk register, RAG-coded]

## §10. Sources & Provenance

| Claim | Source | Tool/URL | Retrieved | Confidence |
|---|---|---|---|---|
| [...] | [...] | [...] | YYYY-MM-DD | High/Med/Low |

## §11. Auto-Trigger Disclosure

Layers loaded: task-asset, sub-protocol-turkey, sub-protocol-product-development-tr
Auto-trigger rationale: [query content rationale]

## §12. Limitations

- IQVIA MIDAS panel coverage [bağlamsal kısıtlar]
- BCS class proxy from literature (not direct measurement)
- TR patent perspective requires pharmapatent skill handoff
- Reimbursement (SUT) outcome inherently uncertain
- TL deprecation makes price snapshots time-sensitive
- Yerli sponsor disclosure asymmetry (KAP vs family-owned)

## §13. G22 Generic-By-Default Audit

[Validator output: 8/8 PASS or N/8 + override rationale]
```

---

## §7. Compliance & Discipline Notes

### §7.1 Data classification

- TİTCK MCP: **public regulatory data** (ruhsat duyuruları kamuya açıktır)
- ThoughtSpot MIDAS: **licensed third-party panel data** (IQVIA contractual terms apply); raporda agregate kullanım, raw row export YOK
- AdisInsight: **licensed editorial data** (Springer Nature contractual terms apply)
- openFDA: **public domain** (US Government work)

### §7.2 KVKK considerations

- Hiçbir kanal kişisel/hasta verisi expose etmez (panel data is aggregated; AdisInsight is asset-level)
- KOL kişi-bazlı çıkarım yapılırken `medsearch` handoff ve KVKK Article 5 yasal dayanak kontrolü zorunludur (ayrı protokol; bu sub-protocol'ün kapsamında değil)

### §7.3 Insider information / MNPI

- Bu sub-protocol **sadece public-domain + licensed-third-party** veriyle çalışır
- AdisInsight pipeline data licensed olduğundan, output'ta verilen pipeline iddiaları AdisInsight'a attribute edilmelidir
- MIDAS sales projection'ları **panel-based estimates**'tir; "actual sales" değildir

### §7.4 No promotional content

- Bu sub-protocol pharmaceutical promotion / HCP-detailing içerik üretmez
- Output'lar **internal feasibility decision-support**'a yöneliktir
- Eğer kullanıcı promotional output isterse → reddet, alternatif olarak medical affairs scientific exchange içeriğine yönlendir

---

## §8. Composability & Cross-References

### §8.1 SMP v1.0 composition

**Upstream (this sub-protocol receives from):**
- `task-asset.md` — base asset profile (T2)
- `sub-protocol-turkey.md` — Türkiye regulatory + reimbursement frame
- `medsearch` skill — scientific evidence base (for BCS lit review, pivotal data)

**Downstream (this sub-protocol feeds into):**
- `pharmapatent` skill — SMK 6769 patent landscape Turkey perspective
- `carbon-html-report` skill — printable feasibility report
- `carbon-pptx` skill — board-level briefing deck
- `analytics-npv.py` — risk-adjusted NPV downstream

### §8.2 When to load this sub-protocol

SKILL.md Step 1g semantic auto-trigger detects:
- Türkiye + product development intent (jenerik fizibilite, in-licensing eval, ATC class scan)
- Cross-country MIDAS reference + Turkey scope
- TİTCK barkod-bazlı ürün geliştirme sorgusu
- BCS / biowaiver + Türkiye eligibility

Then loads `sub-protocol-product-development-tr.md` in parallel with `sub-protocol-turkey.md` and applicable task reference.

### §8.3 Cross-reference map

| Reference | Intersection |
|---|---|
| `sources-catalog.md` | §Türkiye sources, §IQVIA Institute (free tier — paid MIDAS handled here via ThoughtSpot) |
| `triangulation.md` | §10 Geography Verification Guard, §11 History-sensitive claims |
| `api-integrations.md` | §15 ThoughtSpot, §16 TİTCK, §17 AdisInsight, §18 expanded openFDA |
| `sub-protocol-turkey.md` | Regulatory/reimbursement frame; this protocol uses Turkey output as input |
| `task-modality-smallmol.md` | Small molecule generic ecosystem; Module M1+M5 are TR-specific extension |
| `task-modality-biosimilar.md` | Biosimilar feasibility; this sub-protocol's TR overlay |
| `task-asset.md` | Base asset profile feeds this protocol |
| `task-hta.md` | SUT placement strategy → analogous to NICE/CADTH cost-effectiveness |
| `generic-by-default.md` | Article 5 trigger discipline |
| `provenance-engine.md` | Evidence Object schema for ThoughtSpot session_identifier capture |

---

## §9. Known Gaps & Limitations

1. **MIDAS panel asymmetry across 36 countries:** Hospital-only molecules için kapsama düşük; emerging markets'da retail panel daha güçlü. Output'ta her zaman per-country panel coverage caveat'ı verilmelidir.
2. **BCS class direct measurement YOK:** WHO/EMA biowaiver list dışındaki moleküller için BCS class proxy (literature-derived) kullanılır; bu confidence Tier-1, Tier-0 değil.
3. **TR patent perspective tam değil:** SMK 6769 + Yargıtay 11.HD + FSHHM içtihat analizi `pharmapatent` skill'ine handoff edilmelidir; bu sub-protocol patent landscape'i sadece **US Orange Book aynası** olarak verir.
4. **TL deprecation time-sensitivity:** Fiyat tavanı simülasyonu TL/EUR snapshot date'e bağlıdır; haftalık eskime gözlenebilir.
5. **TİTCK SNOMED mapping eksikleri:** `list_unmapped_ingredients` her zaman çağrılarak veri gap awareness sağlanmalıdır; eşdeğer grup mapping bu eksiklere duyarlıdır.
6. **AdisInsight curated subset:** Çinli/Hintli pre-clinical asset'lerin coverage'ı düşüktür; "absence ≠ confirmed non-existence".
7. **ThoughtSpot tenant config dependency:** Bu sub-protocol IQVIA MIDAS-bağlı bir ThoughtSpot tenant'a OAuth ile bağlı olduğunu varsayar. Tenant farklı bir veri seti barındırıyorsa (örn. local panel data) workflow'lar buna göre adapte edilmelidir.
8. **No real-time SGK Komisyonu kararı:** SGK Komisyonu kararları kamuya açık değildir; sadece SUT yayım sonrası listeleme gözlenebilir. Reimbursement scenario'ları olasılıksal değerlendirme altındadır.
9. **5-country reference yapısı politik:** Cumhurbaşkanlığı Kararnameleri ile referans ülke listesi değişebilir (örn. Yunanistan/Portekiz dahil/hariç tartışmaları); Module M2 her zaman güncel mevzuata karşı doğrulanmalıdır.
10. **Yerli sponsor disclosure asimetrisi:** BİST-listeli sponsorlar KAP üzerinden disclosure yaparken family-owned büyük yerli sponsorlar (Abdi İbrahim, Bilim İlaç, Sanovel, Deva, Atabay vb.) için public commercial detay sınırlıdır.

---

## §10. Versioning

- **v1.0.0 (2026-04-29):** Initial release. Sub-protocol introducing 4-channel integrated data stack (TİTCK MCP + ThoughtSpot MCP IQVIA MIDAS + AdisInsight MCP + openFDA Orange/Purple Book) with 7 decision-support modules (M1 Generic Feasibility Scorecard, M2 Price Ceiling Simulation, M3 Cross-Country Market Sizing, M4 Equivalent Group Mapping, M5 Biowaiver/BCS Eligibility, M6 Withdrawal Trend, M7 Reliance Pathway Target ID). 4 cross-source triangulation patterns (P1-P4). TR-PD Feasibility Report standard deliverable template. Composes upstream from task-asset + sub-protocol-turkey + medsearch; downstream into pharmapatent + carbon-html-report + carbon-pptx + analytics-npv.

---

**End of sub-protocol-product-development-tr.md**
