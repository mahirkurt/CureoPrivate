# examples/landscape-ornek-adc-2030.md — Landscape Forecast Report Filled Example

> **Kullanım notu**: Hipotetik vakadır, eğitim amaçlıdır. Gerçek landscape forecast için BERT-tabanlı patent sınıflandırma + zaman serisi modeli + domain uzman validation + comparable transaction verilerinin periyodik güncellemesi gerekir.

---

# Landscape Forecast Report — Antibody-Drug Conjugates (ADC) Solid Tumor, 2025-2030

**Versiyon**: v1.0 — 2026-04-24
**Hazırlayan**: [Strateji + IP Intelligence Ekibi]
**Dağıtım kısıtı**: GİZLİ — İÇ STRATEJİK DEĞERLENDİRME
**Hedef kitle**: Executive (CEO, CFO, Chief Scientific Officer, Board)
**Şablon kaynağı**: `rapor-sablonlari.md` (Landscape Forecast Report — Mod 11)

---

## 1. Yönetici Özeti (BLUF)

**Teknoloji alanı**: Antibody-Drug Conjugates (ADC) — solid tumor endikasyonları odaklı.

**Kapsam**: 2015-2024 retrospektif veri + 2025-2030 öngörü (6 yıllık ileriye dönük).

**Ana bulgular (top 5)**:

1. **Patent başvuru sayısı 2020-2024 arasında 3.2× artmış** (384 → 1,230 yıllık başvuru). Bu hız sürerse 2030'da yıllık 2,500+ başvuru beklenir.

2. **Hedef antijen dominasyonu değişiyor**: HER2 + TROP2 zirveden düşmeye başladı (2022-2024), yerini **CEACAM5, CDH6, Nectin-4, FRα, CLDN18.2** gibi orta-nadir hedefler alıyor.

3. **Yeni payload sınıfları**: Exatecan (DXd) hegemonyasını koruyor ama **camptothecin derivatives, CBI-analogues, PROTAC payloadları** 2025-2027'de büyük artış gösterecek.

4. **Coğrafi kayma**: **Çin patentleri** ilk defa ABD'yi geçti (2024: Çin %34 vs ABD %32). Çin ADC firmalarının ABD/AB lisanslamaları 2024'te $30B+ toplam deal hacmi.

5. **White space tespiti**: TROP2 + ADC'de **yeni epitope + düşük DAR + non-topoisomeraz payload** kombinasyonu rekabet az, yüksek fırsat (patent boşluk).

**Kritik fırsat**: **CLDN18.2 ADC** — mide + pankreas için, şu anda <50 aktif patent, önümüzdeki 3 yılda rekabet yoğunlaşacak. **Erken giriş 12-18 ay içinde şart**.

**Kritik risk**: **HER2 ADC** alanı doygun — yeni giriş için klinik differentiation + patent design-around zorlayıcı; yatırım ROI düşük.

**Stratejik öneri**: 
- **[Firma]** için 3 öncelikli yatırım önerisi: 
  (a) CLDN18.2 ADC preklinik in-license veya JV
  (b) Dual-payload platform partnership (emerging)
  (c) Çin pazar erişimi için Çin ADC firması stratejik ortaklık
- 2025-2027 pencere içinde aksiyon alınması kritik

---

## 2. Teknoloji Alanı Tanımı

### 2.1. Kapsam

**Antibody-Drug Conjugate (ADC)** — şu öğelerin kombinasyonu:
- Targeting antibody (monoclonal antibody veya fragment)
- Linker (cleavable veya non-cleavable)
- Cytotoxic payload (topoisomerase inhibitor, tubulin binder, DNA damage, etc.)

### 2.2. Endikasyon kapsamı

**Solid tumor odaklı**:
- Meme kanseri (HER2+, HER2-low, TNBC)
- Akciğer kanseri (NSCLC)
- Ürotelyal karsinom (UC/bladder)
- Gastric kanseri
- Ovarian kanseri
- Pancreatic + biliary
- Endometrial
- Renal (RCC)
- Prostat

**Hematoloji ADC** ayrı analiz (§hematoloji-ip.md).

### 2.3. Teknoloji stack sınıflandırması

**Hedef antijen kategorileri**:
- Tier A (olgun — 10+ onaylı/klinik): HER2, TROP2, Nectin-4, FRα, BCMA (heme)
- Tier B (gelişmekte — 3-10 klinik): CEACAM5, CDH6, CD166, CLDN18.2, MUC16, LIV-1, AXL
- Tier C (emerging — 1-3 klinik): c-Met, MET, EGFR mutant-specific, FGFR2b, CD228, CEACAM6
- Tier D (preklinik patent): 40+ yeni hedef aktif patent başvurusu

**Payload sınıfları**:
- Tubulin binder: MMAE, MMAF (vedotin sınıfı), maytansinoid (DM1, DM4)
- Topoisomerase I inhibitor: SN-38, exatecan (DXd) — **hegemon**
- Topoisomerase II: PBD, calicheamicin
- DNA damage: Duocarmycin derivatives
- Emerging: PROTAC payloadları, STING agonistleri, TLR agonistleri, immunomodulator payloads

---

## 3. Arama Stratejisi

### 3.1. Patent veri tabanları

- Espacenet (primary) — INPADOC aileleri
- USPTO Patent Public Search
- Google Patents (full-text search)
- PATENTSCOPE (PCT aileleri)
- CAS SciFinder (kimyasal alt-yapı)
- Derwent Innovation (detaylı)

### 3.2. Boolean sorgu stratejisi

```
ANA ADC SORGU:
(CPC = A61K 47/68 OR CPC = C07K 16/00) AND
(CPC = A61P 35/00 OR CPC = A61P 35/04) AND
("antibody-drug conjugate" OR "ADC" OR "immunoconjugate" OR 
 "drug conjugate" OR "targeted therapy conjugate")
```

### 3.3. NLP özellik çıkarımı (BERT-based)

Her patent için BERT embedding + sınıflandırma:
- Hedef antijen tespiti (abstract + claims)
- Payload sınıfı tanıması
- Linker teknolojisi
- Endikasyon
- Manufacturing claim varlığı

**Model**: PubMedBERT fine-tuned on patent corpus (custom 10K training set).

**Doğruluk**: %87 hedef antijen, %92 payload sınıfı, %84 endikasyon.

### 3.4. Sonuç veri seti

- **Toplam patent**: 8,450 (2015-01-01 ~ 2024-12-31)
- **Aktif/granted**: 5,320
- **PCT aktif faz**: 1,890
- **Ulusal faz pending**: 1,240

---

## 4. Yıllık Başvuru Trendi

### 4.1. Yıllık hacim (2015-2024)

```
Yıl    Başvuru sayısı   YoY değişim   Kümülatif
2015   215              -             215
2016   280              +30%          495
2017   360              +29%          855
2018   430              +19%          1,285
2019   528              +23%          1,813
2020   640              +21%          2,453
2021   810              +27%          3,263
2022   975              +20%          4,238
2023   1,100            +13%          5,338
2024   1,230            +12%          6,568
```

### 4.2. CAGR (2015-2024)

**CAGR**: 21.3% — farmasötik patent alanında **en hızlı büyüyen segment**.

### 4.3. 2025-2030 projeksiyon

BERT-tabanlı trend modeli (ARIMA + sentiment indicator):

| Senaryo | 2026 | 2027 | 2028 | 2029 | 2030 |
|---|---|---|---|---|---|
| **Konservatif** (15% CAGR) | 1,415 | 1,627 | 1,871 | 2,152 | 2,475 |
| **Baseline** (18% CAGR) | 1,451 | 1,712 | 2,020 | 2,384 | 2,813 |
| **Agresif** (22% CAGR) | 1,500 | 1,830 | 2,233 | 2,724 | 3,323 |

**Görsel**: `visualize:show_widget(title=adc_filing_trend_2015_2030, ...)` — landscape-filing-trend şablonu + 3 senaryo projeksiyon line'ı.

---

## 5. Assignee + Konsantrasyon Analizi

### 5.1. Top 15 assignee (2015-2024 kümülatif)

```
Sıra   Şirket                 Ülke   Patentler   Pazar payı
1      Daiichi Sankyo         JP     485         %7.4
2      AstraZeneca             UK    412         %6.3
3      Genentech/Roche         US/CH 388         %5.9
4      Seagen (Pfizer)         US    340         %5.2
5      Kelun Biotech           CN    298         %4.5
6      BioNTech/DualityBio     DE/CN 278         %4.2
7      Regeneron               US    255         %3.9
8      Merck (MSD)             US    242         %3.7
9      Gilead Sciences         US    210         %3.2
10     ImmunoGen (AbbVie)      US    195         %3.0
11     Pfizer (non-Seagen)     US    180         %2.7
12     BeiGene                 CN    168         %2.6
13     Innovent Biologics      CN    162         %2.5
14     Nurix Therapeutics      US    150         %2.3
15     ADC Therapeutics        UK    138         %2.1
```

### 5.2. Konsantrasyon Herfindahl-Hirschman Index (HHI)

**HHI**: 342 — **düşük konsantrasyon**, pazar parçalı.

- Top 5 payı: %29
- Top 15 payı: %59
- Diğer: %41 (400+ firma)

### 5.3. Çin firmalarının yükselişi

**2015 → 2024 değişim**:
- Çin patent sayısı: 38 → 420 (11× artış)
- ABD patent sayısı: 98 → 340 (3.5× artış)
- AB + UK: 62 → 180 (2.9× artış)

**2024 itibarıyla Çin dominasyon noktaları**:
- TROP2 ADC (SKB-264, BL-M02D1, DB-1305)
- HER2 ADC (disitamab vedotin / Aidixi)
- Nektin-4 ADC (pipeline)
- Bispecific ADC — erken aşama

**Deal flow (2023-2024)**:
- Kelun → Merck: $9.3B (2023-12)
- BioNTech → DualityBio: $1.5B (2024-04)
- Sichuan Biokin → BMS: $8.4B (2023-12)
- Hansoh Pharma → GSK: $1.7B (2024-06)
- **Toplam Çin→Batı deal 2023-2024: $30B+**

---

## 6. Coğrafi Dağılım

### 6.1. Ülke bazlı 2024 başvuru

```
Ülke        Yeni başvuru 2024    Pay    Değişim (vs 2023)
Çin         420                  %34    +25%
ABD         395                  %32    +10%
Japonya     165                  %13    +8%
AB (EPO)    130                  %11    +5%
Güney Kore  65                   %5     +15%
UK          30                   %2     +3%
Diğer       25                   %2     —
```

### 6.2. Çin × ABD karşılaştırma

**Çin'in avantajı**:
- Hızlı klinik translasyon (Faz I'e geçiş süresi Çin 2.5 yıl vs ABD 3.8 yıl)
- State-backed R&D finansmanı
- Lokal klinik çalışma havuzu (hasta hacmi)

**ABD'nin avantajı**:
- Patent kuvveti (ABD USPTO daha strict examination)
- Global pazar kapsama (çoklu jurisdiksiyonda başvuru)
- Yüksek ROI fiyat pazarı

---

## 7. White Space (Boş Alan) Analizi

### 7.1. Matrix: Hedef × Payload × Linker kombinasyonları

Aşağıdaki kombinasyonlar için patent yoğunluğu (düşük = white space):

| Hedef       | Topo-I (DXd) | Tubulin (MMAE) | PBD | Duocarmycin | STING | PROTAC |
|---|---|---|---|---|---|---|
| HER2        | 🔴🔴🔴 High | 🔴🔴🔴 High | 🟡 Med | 🟢 Low | 🟢 Low | 🟢 Low |
| TROP2       | 🔴🔴 High | 🟡 Med | 🟢 Low | 🟢 Low | 🟢 Low | 🟢 Low |
| Nectin-4    | 🟡 Med | 🔴🔴 High | 🟢 Low | 🟢 Low | 🟢 Low | 🟢 Low |
| **CLDN18.2** | 🟡 Med | 🟢 Low | 🟢 **WHITE** | 🟢 **WHITE** | 🟢 **WHITE** | 🟢 **WHITE** |
| **CEACAM5**  | 🟡 Med | 🟢 Low | 🟢 Low | 🟢 **WHITE** | 🟢 **WHITE** | 🟢 **WHITE** |
| **CDH6**     | 🟢 Low | 🟢 Low | 🟢 **WHITE** | 🟢 **WHITE** | 🟢 **WHITE** | 🟢 **WHITE** |
| **MET mutant** | 🟢 Low | 🟢 Low | 🟢 **WHITE** | 🟢 **WHITE** | 🟢 **WHITE** | 🟢 **WHITE** |
| **CLL-1**    | 🟢 **WHITE** | 🟢 Low | 🟢 **WHITE** | 🟢 **WHITE** | 🟢 **WHITE** | 🟢 **WHITE** |

### 7.2. Top fırsat matrisi

**Yüksek fırsat** (düşük patent yoğunluğu + klinik potansiyel):

1. **CLDN18.2 + DXd** — Claudin 18.2 gastric/pancreatic için; Astellas'ın zolbetuximab'ı + BMS Bemo (gastric) klinik verisi güçleniyor. ADC formülasyonu: erken aşama.

2. **CEACAM5 + yeni payload (non-DXd)** — Sanofi'nin tusamitamab ravtansine Faz III durduruldu (2024); yeniden değerlendirme + yeni payload fırsatı var.

3. **PROTAC payload ADC** — BCL-XL, BRD4, AR PROTAC'lar. Nurix + Arvinas partnership pazarı açmakta.

4. **Dual-payload ADC** — iki farklı cytotoxic payload + aynı antikor; yeni konsept, 10'dan az patent.

5. **Non-internalizing ADC** — extracellular matrix degradation için; yaklaşık 5 aktif patent.

---

## 8. Rakip Portföy Derinliği

### 8.1. Top 5 rakibin 2024 strateji skoru

| Şirket | Toplam portföy | Yeni hedef çeşitliliği | Platform genişliği | Stratejik skor |
|---|---|---|---|---|
| **Daiichi Sankyo** | 485 | 12 hedef | DXd platform+ | 9.5/10 |
| **AstraZeneca** | 412 | 10 hedef | Çoklu platform | 9.2/10 |
| **Genentech/Roche** | 388 | 8 hedef | ADC + bispecific ADC | 8.7/10 |
| **Seagen (Pfizer)** | 340 | 7 hedef | MMAE + yeni payload | 8.5/10 |
| **Merck (MSD)** | 242 | 15 hedef (Kelun DSA ile) | Çin partnership | 9.0/10 |

### 8.2. Roche ADC strateji analizi (Mahir kontekst)

**Roche ADC portföyü 2024**:
- Trastuzumab emtansine (Kadcyla) — HER2+ meme (olgun)
- Polatuzumab vedotin (Polivy) — DLBCL
- Crovalimab (PiaSky) — anti-C5 (PNH — ADC değil ama heme)
- ADC pipeline: HER2-low yeni nesil + TROP2 (Daiichi partnership dışı)

**Roche'un ADC rekabetçi boşluğu**:
- Daiichi + AstraZeneca ortaklığına (T-DXd + Dato-DXd) karşı Roche kendi platformu sınırlı
- 2025-2027: **Roche için stratejik in-license veya Çin partnership önerisi**

### 8.3. 2024-2030 öngörülen pazar dinamiği

**2025**:
- Dato-DXd NSCLC birinci basamak onayı
- Enhertu HER2-ultra-low onay

**2026**:
- CEACAM5 ADC yeniden değerlendirme onayları
- Yeni TROP2 ADC onayları (3-4 ürün)

**2027**:
- CLDN18.2 ADC ilk onayı (Astellas veya Çin firma)
- Dual-payload ilk Faz II positive results

**2028-2030**:
- PROTAC payload ADC ilk FDA onayı
- Çin ADC firmalarının ABD pazar girişi ciddileşir

---

## 9. Emerging Signals + Forecast

### 9.1. BERT-tabanlı emerging signals tespiti

Yıllık yeni patent başvurularında ortaya çıkan semantik gruplar:

**2022-2024 arası en hızlı büyüyen alt-alanlar**:

1. **Conditional activation ADC** — tümör mikroçevresinde etkinleşen (+340% 3 yılda)
2. **Probody (masked antibody)** — CytomX platform + rakipler (+240%)
3. **Bispecific ADC** — 2 farklı tümör antijeni + payload (+200%)
4. **Intracellular target ADC** — membrane olmayan hedefler için (+180%)
5. **PROTAC payload** — BCL-XL, BRD4, KRAS degrader (+150%)
6. **STING agonist payload** — immune-activating (+120%)
7. **Conditional linker cleavage** — pH-, redox-, hypoxia-responsive (+100%)

### 9.2. 5 yıllık öngörü (Baseline senaryo)

**2030'da beklenen ADC pazar durumu**:
- Küresel pazar: $65-85B (vs 2024 $13B → 5-7× büyüme)
- Onaylı ürün sayısı: 35-45 (vs 2024 13)
- Klinik Faz III asset: 80-100
- Çin pazar payı: %25-30 (vs 2024 %10)

### 9.3. Wildcard scenarios

**Upside (%20 probability)**:
- PROTAC-ADC paradigma değişimi — yeni sınıf
- CRISPR+ADC kombinasyon tedavileri

**Downside (%15 probability)**:
- Major güvenlik sorunları (ILD, neuropati) → sınıf-level regülatör geri çekilme
- Çin pazarı ABD/AB engellemeleri (geopolitical)

---

## 10. Stratejik Öneriler

### 10.1. Kısa vadeli (2025-2026)

**Önerilir**:
- **CLDN18.2 ADC** preklinik varlık in-license veya JV ($50-100M upfront)
- Çin ADC firma ile stratejik ortaklık (regional — TR + AB için özel lisans)
- Conditional activation teknolojisi platform lisansı

**Önerilmez**:
- Yeni HER2 ADC yatırımı (doygun)
- Olgun hedeflerle me-too ADC geliştirme

### 10.2. Orta vadeli (2026-2028)

**Önerilir**:
- Dual-payload platform R&D veya partnership
- CEACAM5 yeniden değerlendirme (Sanofi sonrası fırsat)
- PROTAC-ADC erken giriş — Nurix, Arvinas collaborations

### 10.3. Uzun vadeli (2028-2030)

**Önerilir**:
- İmmün-onkoloji + ADC kombinasyon portföyü
- Türkiye ADC yerli üretim kapasitesi hazırlığı (conjugation GMP)
- Biosimilar ADC regülatör yol hazırlığı (ilk biosimilar Kadcyla 2028-2030)

---

## 11. Compliance Beyanları

### Avukat-Müvekkil Ayrıcalığı
Bu rapor 1136 sayılı Avukatlık Kanunu m. 36 + HMK m. 219/3 kapsamında avukat-müvekkil ayrıcalığı + work product statüsündedir.

### Veri kaynağı
- Public patent database (Espacenet, USPTO, PATENTSCOPE) — 2026-04-20 itibarıyla
- Commercial deal database (SEC EDGAR, Evaluate Pharma) — 2026-04-20
- BERT model fine-tuned on internal patent corpus

### NLP model sınırlılıkları
- BERT embedding accuracy %84-92 — kritik kararlar için manuel review
- Emerging signals detection: false positive %5-8
- Forecast modelleri — geçmiş veriye dayalı, paradigma değişimi tahmin edilemez

### Çıkar çatışması
Rapor hazırlayıcıları [Firma] çalışanları/sözleşmeli müşavirleridir. Rekabetçi firmalar ile aktif ilişki açıklanmıştır.

### Compliance detay: `../references/compliance-beyanlari.md`

---

*Hazırlayan: [İsim], Head of IP Intelligence, [Tarih]*
*İnceleyen: [İsim], Chief Strategy Officer, [Tarih]*
*Onaylayan: [İsim], CEO, [Tarih]*
