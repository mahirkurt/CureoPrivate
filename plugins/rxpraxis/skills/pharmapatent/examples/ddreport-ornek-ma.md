# examples/ddreport-ornek-ma.md — M&A Due Diligence Report Filled Example

> **Kullanım notu**: Hipotetik bir vakadır, eğitim amaçlıdır. Gerçek bir M&A DD süreci için tam teknik + finansal + hukuki + regülatör DD koordinasyonu + dış hukuk müşaviri + bankacı ekip zorunludur. Burada yöntem + raporlama çerçevesi + karar matrisi gösterilmektedir.

---

# Due Diligence Report — "OncoGenesis Biotech" Anti-PSMA ADC Akuistisyon Değerlendirmesi

**Versiyon**: v1.0 — 2026-04-24
**Hazırlayan**: [Acquirer] Corporate Development + IP + Klinik + Finans Ekipleri
**Dağıtım kısıtı**: GİZLİ — AVUKAT-MÜVEKKİL AYRICALIĞI + WORK PRODUCT
**Hedef kitle**: Executive (CEO, CFO, CSO, Board) + Legal (GC)
**Şablon kaynağı**: `rapor-sablonlari.md` §7 (M&A Due Diligence)
**Deal tip**: AKUISTİSYON (Acquirer perspektifi)
**Target**: OncoGenesis Biotech, Inc. (hipotetik, Faz II preklinik + klinik varlıklı)

---

## 1. Yönetici Özeti (BLUF)

**Deal özeti**: OncoGenesis Biotech'in tam akuistisyonu. Ana varlık: **OG-PSMA-777**, anti-PSMA (Prostate-Specific Membrane Antigen) antibody-drug conjugate (ADC), Faz II metastatik kastrasyon-rezistan prostat kanseri (mCRPC) endikasyonunda.

**Target profili**:
- Kuruluş: 2017 (Boston, ABD)
- Çalışan: 85 (48 R&D, 22 klinik, 15 idari)
- Finansman: Series C ($180M), toplam toplanan $340M
- Mevcut değerleme (Series C 2024): $900M post-money
- Nakit: $120M (18 aylık runway)

**Teklif edilen deal yapısı**:
- **Upfront**: USD 650M (hisse + nakit karışımı)
- **CVR (Contingent Value Rights)**: USD 400M ek — Faz III başarı + onay + satış milestone'lara bağlı
- **Total enterprise value**: USD 1.05B
- **Premium**: Series C valuation üzerinden %16

**Finansal özet**:
- NPV (probability-weighted, 12% discount): **USD +850M**
- IRR: ~22%
- Monte Carlo P10/P50/P90: -$200M / +$750M / +$1.8B
- Peak sales tahmini (2031-2033): USD 1.4-1.8B

**3 ana bulgu**:

1. **IP portföyü güçlü** — 6 patent ailesi, 4'ü granted (US + EP), TR dahil geniş coğrafi koruma, expiry 2039-2043 arası. FTO temiz (Progenics/Lantheus PSMA patentleri farklı epitope).

2. **Faz II verisi ümit verici ama eksik** — PSA50 %48 (%95 CI: 38-58), median rPFS 9.2 ay, OR 41% (CI: 31-51). Mikrotubul ağırlıklı payload nedeniyle **%22 Grade 3+ neuropati** — red flag.

3. **Rekabet yoğun** — 4 aktif Faz III anti-PSMA ADC (Bayer, Novartis, J&J, ITM) + 3 radioligand therapy (Pluvicto dominant, ~$5B 2026). Erken pazara giriş için hızlı Faz III başlatma kritik.

**Öneri**: **ŞARTLI DEVAM** — aşağıdaki kırmızı çizgilerle müzakere:
- Neuropati güvenlik datası tam şeffaflık + Grade 4-5 vakalarının reddedilmesi
- CVR'nin Faz III kayıt yıla bağlanması (18 ay içinde)
- Anahtar personel (CSO + Clinical Head) 3-yıl retention anlaşması
- Regulatory milestone'lar için FDA Type B meeting öncesi hold

**Alternatif senaryolar**:
- **A (Baseline)**: Deal kapanır, Faz III 2025 Q4 başlar, 2029 FDA onay, 2031 Türkiye launch
- **B (Downside)**: Neuropati sorunu Faz III'te kötüleşir, program durdurulur → -$450M loss
- **C (Upside)**: Payload switch başarılı (DXd-based yeni formülasyon), hızlı Faz III, 2028 onay → +$2B NPV

---

## 2. Target Şirket Profili

### 2.1. Kuruluş ve Tarih

**OncoGenesis Biotech, Inc.**:
- Kuruluş: 2017-03, Boston MA, ABD
- Kurucular: Dr. Michael Chen (CSO, ADC formülasyon) + Dr. Laura Rodriguez (CMO, ürolojik onkolog)
- Yönetim: Alexander Park (CEO, BMS'den 2020), CFO Diana Walsh (2022)

### 2.2. Finansman geçmişi

| Round | Tarih | Miktar | Valuation | Lead investor |
|---|---|---|---|---|
| Seed | 2017-Q4 | $8M | $24M | Atlas Venture |
| Series A | 2019-Q1 | $35M | $110M | ARCH Venture |
| Series B | 2021-Q2 | $90M | $380M | BlackRock Life |
| Series C | 2024-Q1 | $180M | $900M | RA Capital |

### 2.3. Organizasyon

**R&D yapısı**:
- Chemistry (12 kişi): linker-payload
- Biology (18 kişi): antikor engineering + in vivo model
- CMC (10 kişi): conjugation + formülasyon
- Preclinical (8 kişi): tox + PK

**Klinik yapısı**:
- Clinical development (12 kişi)
- Regulatory affairs (5 kişi)
- Clinical operations (5 kişi)

### 2.4. IP + teknoloji varlıkları

- **Ana asset**: OG-PSMA-777 (Faz II)
- **Backup**: OG-PSMA-888 (preklinik, next-gen formülasyon)
- **Discovery platform**: Anti-solid-tumor conjugation platform (lisanslı Abzena'dan 2018)

---

## 3. Asset Envanteri — OG-PSMA-777 Derinlik

### 3.1. Molekül profili

| Özellik | Değer |
|---|---|
| Tip | Antibody-Drug Conjugate |
| Hedef | PSMA (FOLH1) |
| Antikor | Humanized IgG1 (novel epitope, extracellular domain 2) |
| Payload | MMAE (tubulin binder) |
| Linker | Cleavable valin-sitrülin dipeptide |
| DAR | 4 (site-spesifik konjugasyon — cysteine engineering) |
| Molekül ağırlığı | ~155 kDa |
| Formülasyon | Liyofilize, 50 mg vial |

### 3.2. Klinik program

**Faz I tamamlandı** (2021-2023):
- 48 hasta mCRPC
- Dose escalation → RP2D 2.4 mg/kg q3w
- MTD: Grade 3 neuropati dose-limiting
- PK tam karakterize edildi

**Faz II aktif** (2023-2025):
- 120 hasta mCRPC (post-2 abiraterone/enzalutamide + taxane başarısız)
- Primary endpoint: rPFS
- Ön sonuçlar (2024 Q4):
  - PSA50: %48 (n=95, 6-ay minimum follow-up)
  - rPFS median: 9.2 ay (historical comparator 4.5 ay)
  - OR: 41% (CI: 31-51)
  - Güvenlik: Grade 3+ neuropati %22, infusion reactions %12, nötropeni %18

**Faz III planlama** (2025-2029):
- Pivotal SPECTRUM trial — 650 hasta, 3-kollu (OG-PSMA-777 vs Pluvicto vs chemo)
- Regulatory strateji: FDA Type B meeting 2025 Q2, Faz III başlama 2025 Q4

### 3.3. Rekabet peyzajı

**Onaylı mCRPC tedaviler**:
- Enzalutamide, abiraterone (hormone)
- Docetaxel, cabazitaxel (chemo)
- Olaparib, rucaparib, talazoparib (PARP — BRCA+)
- **177Lu-PSMA-617 (Pluvicto, Novartis)** — radioligand therapy, 2022 FDA

**Pipeline anti-PSMA ADC (Faz III)**:
- **Bayer BAY 2287411** — MMAE payload, Faz III
- **Novartis NVP-PSMA-DM4** — DM4 payload, Faz III
- **J&J psntCADt** (eski Ambrx partnership) — Faz II/III
- **ITM-AS-101** — radionuclide-ADC hybrid, Faz II/III

**Pazar projeksiyon**:
- mCRPC toplam pazar 2024: $14B
- 2028'e kadar: $20B+ (Pluvicto + yeni ADC'ler)
- OG-PSMA-777 peak sales senaryolar:
  - Baseline: $1.4B (2033)
  - Downside: $600M
  - Upside: $2.2B (neuropati çözülürse)

---

## 4. Patent Portföy Kuvveti

### 4.1. IP aileleri (6 toplam)

| Aile | Konu | Priority | Expiry (TR) | Durum | Güç |
|---|---|---|---|---|---|
| F1 | Antikor kompozisyonu (yeni epitope) | 2019-05-12 | 2039-05-12 | US granted, EP granted, TR granted, JP granted, CN granted | ⭐⭐⭐⭐⭐ |
| F2 | Linker-payload bileşimi | 2020-08-20 | 2040-08-20 | US granted, EP pending, TR pending, JP granted | ⭐⭐⭐⭐ |
| F3 | Conjugation process (site-specific) | 2021-03-15 | 2041-03-15 | US granted, EP pending, TR pending | ⭐⭐⭐ |
| F4 | Formülasyon (liyofilize) | 2022-06-10 | 2042-06-10 | PCT pending, national phase 2024 | ⭐⭐⭐ |
| F5 | mCRPC endikasyonu (kullanım) | 2023-01-20 | 2043-01-20 | PCT pending | ⭐⭐ |
| F6 | Backup molekül OG-PSMA-888 | 2024-04-15 | 2044-04-15 | US provisional | ⭐⭐ |

**Görsel**: `fto-patent-country-heatmap` şablonu ile 6 aile × 7 ülke coverage matrix.

### 4.2. FTO analizi

**Blocker patent taraması**:

**PC1 — Progenics/Lantheus PSMA binders (US 9,XXX,XXX)**:
- Anti-PSMA antikor farklı epitope (extracellular domain 1)
- OG-PSMA-777'nin epitope 2 hedeflemesi → **FTO temiz**

**PC2 — Seagen (Pfizer) ADC platform patents**:
- vedotin + cleavable linker genel
- Seagen ile cross-license olmadan potansiyel ihlal
- **Çözüm**: Seagen ADC platform lisansı ($50-80M upfront + %3-5 royalty)

**PC3 — Daiichi Sankyo DXd linker patent**:
- OG-PSMA-777 DXd kullanmıyor (MMAE) → FTO temiz

**PC4 — İki radioligand PSMA şirketi (Novartis Pluvicto, POINT Biopharma)**:
- Radyoizotop farklı modalite — FTO temiz

**Sonuç**: FTO temiz, sadece **Seagen ADC platform lisansı zorunlu** (deal öncesi tamamlanmalı).

### 4.3. Patent sürdürülebilirlik (invalidation riski)

OG-PSMA-777 patent aileleri için invalidation riski analizi:

- F1 (antikor) — NOVELTY high confidence (yeni epitope kanıtlanmış X-ray kristal yapı)
- F2 (linker-payload) — INVENTIVE STEP moderate (valin-sitrülin dipeptide common in ADC)
- F3 (conjugation) — NOVELTY strong (cysteine engineering yaklaşımı farklı)
- F4 (formülasyon) — moderate risk (lyo formülasyon common)

**Risk düşürme stratejisi**: F2 + F4 için backup kontinuasyon aileleri + dar istem stratejisi.

---

## 5. Klinik Veri Değerlendirmesi

### 5.1. Faz II veri kalitesi

**Güçlü noktalar**:
- Randomize değil ama single-arm OBJECTIVE endpoints (PSA50, rPFS, OR)
- IRC (Independent Review Committee) imaging assessment
- Central lab
- Primary endpoint achieve edildi

**Zayıf noktalar**:
- Comparator yok (historical)
- Short follow-up (median 8 ay)
- %18 hastada dose reduction (tolerabilite endişesi)

### 5.2. Güvenlik profili — Grade 3+ AEs

| AE | Oran | Karşılaştırma (Pluvicto) |
|---|---|---|
| Peripheral neuropati | **%22** | %4-6 |
| Nötropeni | %18 | %8 |
| İnfüzyon reaksiyonu | %12 | %3 |
| Görme bozukluğu | %8 | %2 |
| Thrombocytopenia | %6 | %10 (Pluvicto lehine) |

**Kritik endişe**: Neuropati oranı Pluvicto'dan 3-5× yüksek. Bu mCRPC popülasyonu için kabul edilebilir olmayabilir.

### 5.3. Klinik risk senaryolar

**Scenario A — Baseline (60% probability)**:
- Faz III primary endpoint (rPFS) başarılı
- Neuropati Grade 3+ Faz III'te %18'e düşer (dose optimization)
- 2029 FDA onay, 2030 AB, 2031 TR

**Scenario B — Neuropati kötüleşme (15%)**:
- Faz III'te neuropati %30+ olur → çalışma hold veya terminate
- Alternatif payload gerekli (DXd-based OG-PSMA-888)

**Scenario C — Efficacy win big (15%)**:
- Neuropati yönetilir + PSA50 %55+ → birinci basamak genişleme
- Upside: $2B+ peak sales

**Scenario D — Pipeline rekabet kaybeder (10%)**:
- Bayer veya Novartis daha iyi profil gösterir → pazar payı kısıtlı
- Peak sales $600-800M

---

## 6. Regülatör Yol Durumu

### 6.1. FDA

- Faz I IND aktif (2020-03 onay)
- Faz II protokolü onaylı
- **Fast Track designation** alındı (2023-11)
- **Breakthrough Therapy** başvurusu 2025 Q1 planlı (Faz II tam veri sonrası)
- Beklenen BLA filing: 2028 Q2
- Beklenen FDA onay: 2029 Q1

### 6.2. EMA

- Orphan Designation reddedildi (mCRPC'nin prevalans üzeri)
- PRIME designation adayı — 2025 Q2 başvuru
- Beklenen EMA onay: 2030 Q1

### 6.3. TİTCK

- Türkiye'de klinik çalışma IND onayı henüz yok (Faz III'te beklenir)
- Beklenen TR onay: 2031-2032
- SGK geri ödeme: metastatik CRPC için yüksek öncelik, beklenen pozitif

### 6.4. Çin

- NMPA bildirimi henüz yok
- Faz III'e Çin siteleri eklenebilir (2026+)

---

## 7. Finansal Değerleme

### 7.1. Revenue projeksiyonu (risk-adjusted)

| Yıl | Bölge | Launch | Peak sales | PTRS | Risk-adj peak |
|---|---|---|---|---|---|
| 2029 | ABD | 2029 Q2 | $600M | %60 | $360M |
| 2030 | AB | 2030 Q1 | $350M | %55 | $193M |
| 2031 | Türkiye | 2031 Q3 | $30M | %50 | $15M |
| 2031 | Japonya | 2031 Q1 | $100M | %60 | $60M |
| 2031 | Çin | 2031 Q4 | $200M | %45 | $90M |

**Risk-adjusted toplam peak**: ~$720M
**Nominal peak (Faz III başarı)**: $1.4-1.8B

### 7.2. Cash flow modeli (acquirer perspektifi)

Horizon 15 yıl, discount rate %12:

```
Yıl 0 (2026):     Deal closing             -$650M (upfront)
                   Seagen ADC lisans        -$70M
                   Integration costs        -$30M
Yıl 1-2:          Faz III yürütme          -$200M
Yıl 3 (2029):     FDA onay + launch        +$50M (initial)
Yıl 3-4:          CVR payments             -$200M (part 1 + part 2)
Yıl 4-8:          Revenue ramp-up          $100M → $1.2B
Yıl 7:            CVR final                -$200M (sales-based)
Yıl 8-12:         Peak revenue             $1.2-1.4B/yıl
Yıl 12-15:        Patent expiry + erosion  revenue decline
```

### 7.3. NPV + IRR

**Base case (60% probability)**:
- NPV: +$1.1B
- IRR: ~24%
- Payback: Year 7

**Probability-weighted NPV**: +$850M
**Monte Carlo (10,000 simulations)**:
- P10 (pessimistic): -$200M
- P50 (median): +$750M
- P90 (optimistic): +$1.8B

**Görsel**: `dd-montecarlo` şablonu ile NPV dağılımı.

---

## 8. Monte Carlo Risk Analizi

### 8.1. Simülasyon parametreleri

- Simülasyon sayısı: 10,000
- Bağımsız değişkenler: PTRS, peak sales, discount rate, clinical timeline, competition
- Her değişken için üçgen dağılım (min, baseline, max)

### 8.2. Sensitivity rankings (NPV etkisi)

**Görsel**: `dd-tornado` şablonu ile 6 parametre duyarlılık analizi.

| Parametre | -1σ NPV etkisi | +1σ NPV etkisi |
|---|---|---|
| Peak sales | -$400M | +$500M |
| PTRS (Phase III başarı) | -$350M | +$280M |
| Timeline (launch delay 1 yıl) | -$180M | +$150M |
| Discount rate | -$150M | +$130M |
| Competitive entry (Bayer/Novartis) | -$120M | +$90M |
| Seagen royalty burden | -$80M | +$60M |

### 8.3. Senaryo matrisi

| Senaryo | Probability | NPV | Aksiyon |
|---|---|---|---|
| Base case | 60% | +$1.1B | Deal devam |
| Upside (CVR tetikleniyor) | 15% | +$2.3B | Mükemmel ROI |
| Downside (Faz III başarısız) | 15% | -$450M | Impairment |
| Edge cases | 10% | varies | — |

---

## 9. Hukuki Riskler + Litigation Exposure

### 9.1. Aktif davalar — yok

OncoGenesis Biotech şu anda aktif patent davası, ürün sorumluluk, veya ticari anlaşmazlık davasına taraf değil.

### 9.2. Potansiyel gelecek davalar

**R1 — Seagen patent ihlali (potansiyel)**:
- ADC platform patentleri (MMAE + cleavable linker)
- Deal öncesi Seagen lisansı alınması zorunlu
- Tahmini lisans maliyeti: $50-80M upfront + %3-5 royalty

**R2 — Daiichi Sankyo FTO tarama**:
- DXd linker-payload patentleri
- OG-PSMA-777 MMAE kullandığı için risk düşük
- OG-PSMA-888 DXd kullanırsa → yeni lisans gereksinimi

**R3 — Employment claims**:
- Kurucu Dr. Chen'in eski işvereni (BMS) stok haklarının temizlenmesi gerekir
- Ek 3 araştırmacının önceki akademik kurumlarıyla IP ownership dispute potansiyeli

### 9.3. Regulatory compliance

**FDA 483 veya warning letter**:
- GMP inceleme 2023 — 3 minör bulgu, kapatıldı
- CMC durumu temiz

**CTA (Clinical Trial Agreement) portföyü**:
- 18 klinik çalışma sitesi (ABD + AB)
- Tüm CTA'lar reviewed, standard clauses

### 9.4. Veri koruma

- HIPAA compliance — OK
- GDPR (AB siteleri) — OK
- KVKK uygulanabilir değil (Türkiye siteleri yok)

---

## 10. Deal Önerisi + Stratejik Kırmızı Çizgiler

### 10.1. Önerilen deal yapısı (finalize)

**Structure A — Hibrit upfront + CVR (TERCİH EDİLEN)**:
- Upfront: **USD 550M** (nakit + hisse karışımı)
- Stok hissesi: acquirer shares, 18-ay lock-up
- CVR Tranche 1 ($150M): Faz III rPFS primary endpoint başarısı
- CVR Tranche 2 ($150M): FDA onay
- CVR Tranche 3 ($200M): İlk yıl satış >$500M
- **Total maximum**: USD 1.05B
- Acquirer NPV: +$850M

**Structure B — All-upfront alternatif** (yedek):
- Upfront only: $750M
- Acquirer risk yüksek

**Structure C — Earnout heavy** (target lehine):
- Upfront: $400M
- CVR: $800M maksimum
- Target lehine, acquirer'da düşük commitment

### 10.2. Stratejik kırmızı çizgiler

1. **Neuropati şeffaflık**: Tüm Grade 3-5 nöropati vakalarının bağımsız nörolojik inceleme sonrası retrospektif audit. Grade 4-5 vaka sayısı ≥3 ise deal iptal.

2. **CVR tetikleme şartları kesin**: Faz III dosyalama tarihi 2026 Q2'e kadar garanti; yoksa CVR tranche 1 iptal.

3. **Anahtar personel retention**: CSO (Dr. Chen) + CMO (Dr. Rodriguez) + Clinical Head 3-yıllık retention + değer-yaratıcı bonus planı.

4. **Seagen lisansı ön-tamamlama**: Deal signing öncesi Seagen ile lisans term sheet imzalı olmalı.

5. **FDA Type B meeting öncesi hold**: Deal closing 2025 Q3'te planlanıyorsa, Type B meeting sonucu pozitif olmazsa 90-gün bekleme + MAC clause.

6. **IP teminatı**: Tüm 6 patent ailesi için sahiplik zincirinin temiz olduğunu garanti + representation & warranty indemnification (3 yıl, %100 tavan upfront).

7. **Change-of-control**: Kurucular veya kilit yönetim deal signing sonrasında 6 ay içinde toplu istifa durumunda, CVR tranche 1'in %50'si cancel.

### 10.3. Müzakere takvimi

| Hafta | Aktivite | Hedef |
|---|---|---|
| 1-2 | Term sheet exchange + non-binding offer | $550M upfront + CVR |
| 3-4 | Due diligence derinleştirme (access to full Faz II data) | Neuropati analysis |
| 5-8 | Seagen lisans müzakeresi (paralel) | Term sheet imzalı |
| 9-12 | Main merger agreement drafting | Legal + tax optimization |
| 13-16 | SEC/antitrust filing (HSR Act) | Clearance |
| 17-20 | Shareholder approval (target side) | >%80 onay |
| 21-24 | Closing + integration başlangıç | Day 1 integration |

### 10.4. Post-deal entegrasyon planı

**Day 1 - 30**:
- Kilit personel retention bildirimleri
- Klinik program status review
- Seagen lisans finalize

**Day 30 - 90**:
- Faz III planlama konsolidasyonu
- Acquirer infrastructure entegrasyonu (reg affairs, manufacturing)
- İleri backup asset (OG-PSMA-888) road-mapping

**Day 90 - 365**:
- FDA Type B meeting
- Faz III başlatma
- Global launch planning (AB + Asya + TR)

---

## 11. Compliance Beyanları

### Avukat-Müvekkil Ayrıcalığı

Bu rapor 1136 sayılı Avukatlık Kanunu m. 36 + HMK m. 219/3 + ABA Model Rules + UK LPP kapsamında **avukat-müvekkil ayrıcalığı + work product doctrine** altındadır.

### Çıkar çatışması

Rapor hazırlayıcıları [Acquirer]'ın tam zamanlı çalışanları veya sözleşmeli dış müşavirleridir. OncoGenesis Biotech ile aktif veya geçmiş 3 yılda profesyonel ilişki açıklanmıştır (yok).

### Veri kaynakları

- Target veri odası (electronic data room) — 2026-04-01 ile 2026-04-23 arası erişim
- SEC EDGAR public filings
- Clinical trial registries (ClinicalTrials.gov, EudraCT)
- Patent databases (EPAAT, USPTO, Espacenet)
- Commercial databases (Evaluate Pharma, IQVIA)

### Finansal modelleme sınırlılıkları

- Monte Carlo baz parametreleri tahmin — risk tahminleri belirsizliklidir
- Regulatory timeline assumptions FDA/EMA historical pattern'a dayalıdır
- Competitive dynamics projeksiyonu 3-5 yıl ötesine dair belirsiz

### KVKK + GDPR

Target çalışan verileri DD sırasında yalnız aggregate olarak analiz edildi; kişisel veri işleme GDPR Art. 6(1)(f) meşru menfaat kapsamında.

### FCPA + Anti-Bribery

Deal süreci boyunca FCPA + UK Bribery Act + TR 5607 uyumu tam; target'ın tüm ticari anlaşmaları review edildi, kırmızı bayrak yok.

### Compliance detay: `../references/compliance-beyanlari.md §10 M&A DD`

---

*Hazırlayan: [İsim], VP Corporate Development, [Tarih] — [İmza]*
*IP inceleme: [İsim], Head of IP, [Tarih] — [İmza]*
*Klinik inceleme: [İsim], Chief Medical Officer, [Tarih] — [İmza]*
*Finansal inceleme: [İsim], VP Finance + Strategy, [Tarih] — [İmza]*
*Hukuki inceleme: [İsim], General Counsel, [Tarih] — [İmza]*
*Executive onay: [İsim], CEO, [Tarih]*
*Board onayı: [Tarih, Board Resolution No]*
