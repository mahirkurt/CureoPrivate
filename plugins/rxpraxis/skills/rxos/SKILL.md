---
name: rxos
description: |
  rxpraxis süitinin orkestratörü — Türkiye-merkezli farmasötik jenerik/biyobenzer fırsat tarayıcı. Retail/topluluk-eczanesi kanalında oral + topikal küçük molekül ürünleri TÜM terapötik alanlarda tarar (hiçbiri varsayılan değil). Yedi-aşamalı deterministik boru hattı (Aşama 0 brief + 1-6 pipeline) ile dört kaynak-tipi sibling skill'i (medical-research, pharmaintel, pharmapatent, thoughtspot-roche) G0-G6 kalite kapılarıyla orkestre eder. Paylaşılan connector sözleşmesi (../../CONNECTORS.md) ve kanonik-artefakt önbelleği (../../shared/canonical-cache-contract.md) altında çift connector sorgusunu engeller. HOSPITAL/IV SCOPE DIŞI. USE for — jenerik fırsat taraması, Türkiye ürün geliştirme, generic feasibility, gap analysis, Type_A/B/C/D/E typology, 36-ülke MIDAS cross-country sizing, eşdeğer grup, fiyat tavanı, biowaiver, Reliance target, RxOpportunityScanner, rxpraxis-scan. When in doubt USE.
version: 1.7.0
last_updated: 2026-06-14
changelog:
  - "1.7.0 (2026-06-14): rxpraxis PLUGIN ENTEGRASYONU. Standalone rxos v1.6.3'ten plugin-orkestratörüne dönüştürüldü. (a) §0.A Veri Kaynakları Manifesti → plugin-düzeyi ../../CONNECTORS.md'ye taşındı (connector tanımı artık skill içinde tekrarlanmıyor). (b) §0.D MIDAS Veri Sözleşmesi + tek-sefer TİTCK kuralı → ../../shared/canonical-cache-contract.md'ye genelleştirildi (üç kanonik artefakt: titck_canonical + midas_extract + adis_pipeline). (c) Skill çağrıları sibling plugin skill'lerine bağlandı (rxpraxis:medical-research vb.). (d) run_manifest → ../../shared/run-manifest-schema.json + connector_call_ledger (çift-sorgu denetim kanıtı). Davranış/aşama sayıları/kalite kapıları DEĞİŞMEDİ — yalnız sözleşmeler tek noktaya çekildi."
  # NOT: Standalone sürüm geçmişi (1.0.0 → 1.6.3) orijinal rxos CHANGELOG.md dosyasındadır.
---

# rxos — rxpraxis Orkestratörü (Türkiye Jenerik Fırsat Tarayıcı)

**Skill tipi:** Multi-skill orchestration (deterministic pipeline) — plugin flagship
**Süit:** rxpraxis · **Sürüm:** 1.7.0
**Dil:** Türkçe (rapor çıktıları); İngilizce (MCP sorguları)

> **Plugin entegrasyon notu.** Bu skill, rxpraxis süitinin orkestratörüdür. Connector
> envanteri ve fallback'ler için **[../../CONNECTORS.md](../../CONNECTORS.md)**, kanonik
> önbellek ve çift-sorgu disiplini için **[../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md)**
> normatiftir. Bu iki dosya, eski standalone rxos'taki §0.A + §0.D + tek-sefer-TİTCK
> bölümlerinin yerini alır.

---

## Ne Zaman Çağrılır

Türkiye'de **retail/topluluk-eczanesi kanalında** dağıtılan oral/topikal küçük molekül
ürünler için jenerik/biyobenzer fırsat taraması gerektiğinde. Tetikleyiciler: "jenerik
fırsat taraması", "Türkiye ürün geliştirme", "generic feasibility", "gap analysis",
"X indikasyonunda jenerik fırsatı", "36-ülke MIDAS / cross-country sizing", "eşdeğer grup
pazar boyutu", "fiyat tavanı", "Reliance target", "RxOpportunityScanner", "rxpraxis-scan".

**Ayrım (scope guard):** bireysel SGK/dava → onko-erisim; MLR/promosyon → promo-censor;
mevzuat reformu → lex-sanitas; saf klinik kanıt → rxpraxis:medical-research; global pipeline
→ rxpraxis:pharmaintel. Hastane/IV ürünler **kapsam dışıdır**.

---

## 0. SCOPE POLİTİKASI — Kanal-Temelli, Terapötik-Alan-Nötr

rxpraxis, retail/topluluk-eczanesi kanalında dağıtılan **oral + topikal küçük molekül**
(ve küçük-molekül-eşdeğeri) ürünleri **TÜM terapötik alanlarda** kapsar. Kapsam bir
**kanal/veri-erişimi kararıyla** belirlenir — terapötik alanla değil. Hiçbir TA (onkoloji
dahil) varsayılan değildir.

**Kapsam dışı (her TA'da):** hastane kanalında uygulanan (IV/infüzyon) ürünler — IV
biyolojikler, IV demir, IV antibiyotik, ADC, CAR-T, bispesifik antikorlar, IV kemoterapi.
Gerekçe: (1) TR IQVIA hospital panel erişimi yok; Aşama 5 ticari modeli (TÜİK + epidemiyoloji
+ MIDAS **retail**) hastane-dağıtımlı ürünler için uygulanamaz. (2) Farklı geri ödeme/dağıtım.

> **Not:** Bu bir **kanal** filtresidir. Oral onkoloji (oral TKI, oral CDK4/6, topikal ajanlar)
> kapsam İÇİNDE; IV immünoloji/romatoloji kapsam DIŞINDA. Ayrım molekülün **dağıtım kanalıdır**.

### 0.A Veri Kaynakları → ../../CONNECTORS.md

Süitin tükettiği TÜM connector'lar, skill-eşlemesi, fallback zincirleri ve provenance
standardı **[../../CONNECTORS.md](../../CONNECTORS.md)** dosyasındadır. Bu skill connector
tanımı **yapmaz**; oraya referans verir.

### 0.B Skill Entegrasyon Sözleşmesi

| Süit skill'i | rxos aşaması | Çağrılan yetenek |
|---|---|---|
| `rxpraxis:medical-research` | Aşama 1 | `landscape_scan` — global onaylı ajan haritası + `adis_pipeline` (kanonik) |
| `rxpraxis:pharmaintel` | Aşama 2 + 5 | Regulatory (üç-otorite) + M4 eşdeğer + M6 withdrawal + M1/M2/M3 commercial + M5/M7 biowaiver/Reliance |
| `rxpraxis:pharmapatent` | Aşama 2 + 4 | Mod 13 `titck_canonical` (kanonik) + Mod 1 FTO + Mod 5 exclusivity + Mod 9 biyobenzer |
| `rxpraxis:thoughtspot-roche` | Aşama 5b | 36-ülke MIDAS `midas_extract` (kanonik) — W1-W6 dalga |

### 0.C TA-Adaptasyon Protokolü

Brief'in `therapeutic_area`'sına göre TA-uygun **epidemiyoloji çapası** / **kılavuz otoritesi**
/ **endpoint** / **treated-population funnel** seçilir:
- **Epidemiyoloji çapası:** onkoloji/heme-malign → GLOBOCAN/IARC; aksi halde IHME GBD +
  hastalık-spesifik registry + WHO GHO. (GLOBOCAN'ı TA-dışı alana taşımak **yasaktır**.)
- **Kılavuz otoritesi:** onkoloji ESMO/NCCN; romatoloji EULAR/ACR; dermatoloji AAD/EADV;
  kardiyoloji ESC/AHA; endokrin ADA/EASD; solunum GINA/GOLD.
- Çıktı: `brief.ta_calibration` (epi_anchor + guideline_authorities + funnel_defaults).

### 0.D MIDAS + Kanonik Önbellek → ../../shared/canonical-cache-contract.md

ThoughtSpot-Roche MIDAS veri sözleşmesi (küp envanteri, ATC1/Product/Country attribute
yüzeyi, kümülatif-CHF annualizasyonu, explicit pencere disiplini, türetilmiş-metrik
istemci-tarafı kuralı, provenance + Roche confidential) ve **tek-sefer TİTCK kuralı** artık
**[../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md)**
dosyasında genelleştirilmiştir (üç kanonik artefakt: `titck_canonical` · `midas_extract` ·
`adis_pipeline`). Aşama 2/4/5 çalıştırılırken bu dosya SKILL.md §3 ile birlikte normatiftir.

---

## 1. Skill Ne Yapar

`rxos` (RxOpportunityScanner), Türkiye retail/topluluk-eczanesi (oral + topikal küçük
molekül) pazarında jenerik geliştirme fırsatlarını **tüm terapötik alanlarda** sistematik
tarayan deterministic bir boru hattıdır. Kullanıcının verdiği terapötik alan briefini alıp
önce §0.C TA-kalibrasyonu yapar, sonra dört sibling skill'i sıralı orkestrasyona alarak,
niceliksel + niteliksel kanıtla desteklenmiş final aday hiyerarşisini üretir.

**Birincil kullanım vektörleri:** single-asset opportunity validation · portfolio gap
scanning · brief-driven scanning · cross-country benchmarking (36-ülke MIDAS) · Reliance
procedure feasibility.

Skill **veri üretmez**; dört sibling skill'i paylaşılan connector sözleşmesi altında çağırır,
her birinden JSON-strict artefakt toplar ve konsolide **Markdown** karar dokümanı üretir.

---

## 2. Mimari

rxos = **7 aşama (Aşama 0 brief + 1-6 pipeline) × 4 sibling skill orkestrasyonu × 7 kalite
kapısı (G0-G6)**. Kanonik artefakt akışı (canonical-cache-contract.md):

```
adis_pipeline   : Aşama 1'de üretilir → Aşama 1, 2, 4 tüketir
titck_canonical : Aşama 2'de üretilir → Aşama 2, 4, 5 tüketir   (TİTCK MCP bir kez)
midas_extract   : Aşama 5b'de üretilir → Aşama 5a, 5c tüketir   (ThoughtSpot + REST)
```

---

## 3. Aşama Aşama Protokol

### Aşama 0 — Brief Standardizasyonu (G0)
Kullanıcının doğal dil briefini deterministic JSON şemasına çevir (`assets/brief-schema.json`).
Zorunlu alanlar: `therapeutic_area` (ICD-10 prefix) · `target_indications[]` (ICD-10 + SNOMED
+ tedavi hattı) · `primary_authorities[]` · `target_launch_year` (≥ current+3) ·
`max_development_months` (vars. 36) · `min_global_sales_usd` (vars. 50M) · `max_complexity` ·
`exclusion_categories[]`.
**G0 — 8 kontrol:** TA↔ICD-10 eşleşti · her indication SNOMED · primary authority ≥1 · launch
year ≥ current+3 · exclusion listelendi · min sales kantitatif · JSON şema PASS · (WARN)
`ta_calibration` üretildi (§0.C).

### Aşama 1 — Tedavi Peyzajı (G1) · rxpraxis:medical-research
`landscape_scan` → global onaylı ajanları haritala. Her aday: INN + brand + originatör +
onaylı endikasyonlar (FDA/EMA/MHRA/PMDA) + pivotal RCT (PMID + NCT) + (kritikse) topikal
bioavailability/PK. Çift-kılavuz kontrolü (§0.C TA-uygun otorite + FDA/EMA etiket).
**Kanonik:** `adis_pipeline` burada üretilir (canonical-cache §5).
**Çıktı:** `treatment_landscape.json`. **G1 — 5 kontrol.**

### Aşama 2 — Regülatuar Matris (G2) · pharmaintel Channel A + M4/M6 + pharmapatent Mod 13
Her ajanı üç-otorite × endikasyon × form matrisine yerleştir; TR pipeline rekabetini ölç;
**TİTCK kanonik dosyayı tek seferde çıkar.**
1. pharmaintel Regulatory → FDA/EMA/MHRA/PMDA fetch.
2. **pharmapatent Mod 13** → `titck_canonical` (master + SNOMED + holder + ATC + first-in-class)
   — **bir kez** (canonical-cache §3). Aşama 4 tekrar sormaz.
3. pharmaintel M4 → eşdeğer grup doygunluğu (`titck_canonical.equivalent_group`'a yazar).
4. pharmaintel M6 → withdrawal trend (TÜFAM).
5. Asimetri katman analizi (yatay otorite×endikasyon + dikey form×pazar + TR pipeline sinyali).
**Çıktı:** `regulatory_matrix.json` + `titck_canonical`. **G2 — 8 kontrol** (G2.7 TİTCK kanonik;
G2.8 M4/M6).

### Aşama 3 — Gap Candidate Ranking (G3)
Atomik kayıtlardan gap candidates türet, tipoloji etiketle, exclusion uygula.
**Tipoloji:** Type_A (saf gap, first-mover) · Type_A_with_pipeline · Type_B (farklı form) ·
Type_C (withdrawn) · Type_D (farklı strength/indikasyon) · **Type_E** (reimbursement-constrained).
Brief eşik kontrolü (global_sales · complexity · development_months · launch_year) + 8-kategori
exclusion + konsolidasyon fırsatı.
**Çıktı:** `gap_candidates.json`. **G3 — 5 kontrol.**

### Aşama 4 — Patent + Teknik Fizibilite (G4) · pharmapatent Mod 13→1→5→9 + pharmaintel M5/M7
0. **pharmapatent Mod 13 (paylaşılan):** `titck_canonical`'ı **okur** (tekrar TİTCK sorma);
   yalnız Türk Patent MCP katmanını (search_patents + EP→TR validation) çalıştırır.
1. **Mod 1 FTO** — compound + formülasyon + use + polimorf/metabolite/process patentleri +
   Rezidüel Risk Beyanı.
2. **Mod 5 Regulatory** — FDA NCE 5y + EMA 8+2 + TR BTÜ-RM 6+2 + Bolar (SMK 6769 m.85) + LOE.
2b. **Mod 9 Biosimilar Pathway** (koşullu — yalnız biyolojik/biyobenzer).
3. **pharmaintel M5 Biowaiver/BCS** — Class I-IV + IVRT/BE pathway.
4. Teknik fizibilite — API tedarik + synthesis route + formülasyon karmaşıklığı.
5. **pharmaintel M7 Reliance** — TR Reliance uygunluk skoru + per-country rollout (MIDAS cross-ref).
6-10. (v1.2.1 katmanı) patent_typology_layer · T-DEATH · Bolar safety · injunction risk · SPC
   advantage · Type_B alt-sınıflandırma (`scripts/` helper'lar).
**Çıktı:** `feasibility_matrix.json`. **G4 — 13 kontrol** (G4.12 mod zinciri; G4.13 M5/M7).

### Aşama 5 — TR Commercial Sizing + 36-Ülke MIDAS + SGK (G5) · pharmaintel M1/M2/M3 + thoughtspot-roche
**Bölüm A (TR-iç):** TÜİK ADNKS + TA-adaptif epidemiyoloji (§0.C) + treated population funnel
(5 adım, TA-spesifik default) + SGK SUT pathway (EK-4/A + geri ödeme skoru).
**Bölüm B (36-ülke MIDAS — W1-W6):** thoughtspot-roche `midas_extract` üretir (canonical-cache §4).
Pre-flight `check_connectivity` zorunlu; Pong yoksa Bölüm B atlanır → degrade. Tüm dalgalar
sabit explicit pencere + annualizasyon.
  - W1 ATC1 baseline · W2 by-country (36) · W3 per-capita (istemci-tarafı) · W4 yapısal-akran
    medyanı + gap · W5 LOE erozyon eğrisi · W6 fiyat koridoru (chf/su).
**Bölüm C:** pharmaintel M2 fiyat tavanı (5-ülke referans + Ek-4B indirim) + M1 scorecard
(7-boyut, **annualize** edilmiş pazar) + revenue model (year-3/5 peak; penetrasyon sensitivity
= peak / annualize edilmiş TR taban).
**Çıktı:** `commercial_opportunity.json` + `midas_extract`. **G5 — 15 kontrol** (G5.12-16 MIDAS;
G5.17 annualizasyon; G5.18 provenance + confidential).

### Aşama 6 — Konsolide Rapor (G6)
Aşama 1-5 JSON artefaktlarından senior-leadership-ready konsolide **Markdown** rapor (downstream
render skill'i gerektirmez). 10-12 bölüm: Kapak + Yönetici Özeti (3-aday tablo) + Pilot Çerçevesi
+ 5 aşama detayı + Strateji Sentezi + Final Ranking + 12-ay Aksiyon Planı + Caveatlar + Provenance.
**G6:** ≥8 `##` başlık · Yönetici Özeti · ≥1 karşılaştırma tablosu · Provenance bölümü · R1-R4
(final ranking 2-5 aday; patent expiry + SGK skoru; caveat fallback'leri).

---

## 4. Quality Gate Matrisi (G0-G6)

| Gate | Aşama | Kontrol | Bloker/WARN |
|---|---|---|---|
| G0 | Brief | 8 (7 BLOKER + 1 WARN) | BLOKER |
| G1 | Landscape | 5 | BLOKER |
| G2 | Regulatory | 8 (6 + 2 WARN) | BLOKER |
| G3 | Gap Ranking | 5 | BLOKER |
| G4 | Patent + Feasibility | 13 (7 + 6 WARN) | BLOKER (PATENT_FTO_FAIL kritik) |
| G5 | Commercial | 15 (8 + 7 WARN) | BLOKER (TR_PROXY_UNFLAGGED kritik) |
| G6 | Rapor | 6 yapı + R1-R4 | yapı BLOKER |

**BLOKER vs WARN:** BLOKER başarısız → boru hattı durur, düzeltme istenir. WARN başarısız →
rapor teslim edilir, kullanıcıya not edilir (düşük-versiyon dependency degrade'ine izin verir).

---

## 5. Orkestrasyon Kayıt Şeması

Her çalıştırma için `run_manifest.json` üretilir — şema:
**[../../shared/run-manifest-schema.json](../../shared/run-manifest-schema.json)**. İçerir:
`skill_invocations` + `quality_gates` + `artifacts` + **`cached_artifacts`** (tek-sefer kanıtı)
+ **`connector_call_ledger`** (`titck_mcp.single_shot_enforced: true` = çift-sorgu yasağı kanıtı).

## 6. Run ID Konvansiyonu
`RxOS-YYYYMMDD-<THERAPEUTIC_AREA>-<SUBTOPIC>-v<N>`. TA kısaltmaları: DERM · ONKO · HEME · IMMUN
· CARDIO · METAB · NEURO · RESP · INFEKT · GI · RENAL · MUSCULO · OPHTH · PSYCH · ENDO. **Hiçbiri
varsayılan değildir.**

## 7. Dosya Yapısı (run çıktısı)
```
<RUN_ID>/
├── brief.json · treatment_landscape.json · regulatory_matrix.json
├── gap_candidates.json · feasibility_matrix.json · commercial_opportunity.json
├── pilot_report.md          # Aşama 6 konsolide Markdown
└── run_manifest.json        # + cached_artifacts + connector_call_ledger
```

## 8. MCP Fallback Protokolü → ../../CONNECTORS.md §6
Tüm fallback zincirleri (Türk Patent / TİTCK / ThoughtSpot / PubMed / Tavily / openFDA) ve
caveat etiketleri CONNECTORS.md §6'dadır. Her fallback `run_manifest.caveats[]` + rapor
§Limitations'a yansır.

## 9. Composability — Pipe Compatibility
**Upstream:** rxpraxis:pharmaintel (cross-country) · rxpraxis:medical-research (landscape) ·
medsearch (KOL/market entry).
**Downstream:** rxpraxis:pharmaintel (Türkiye Ürün Geliştirme onayı) · lex-sanitas (regülatuar
matris → mevzuat boşluk) · carbon-html-report / carbon-pptx (render).

## 10. Referans Dosyalar
- `references/stages.md` — aşama detay protokol genişletmesi (vendored rxos'tan)
- `references/quality-gates.md` — G0-G6 kontrol listesi
- `references/turkey-addendum.md` — TR-spesifik operasyonel kurallar
- `assets/brief-schema.json` — Aşama 0 JSON şeması
- `scripts/g0-runner.py` — quality gate çalıştırıcı
- `scripts/timeseries-sort.py` — MIDAS time-series helper
- **Plugin-düzeyi:** `../../CONNECTORS.md` · `../../shared/canonical-cache-contract.md` ·
  `../../shared/provenance-standard.md` · `../../shared/run-manifest-schema.json`
