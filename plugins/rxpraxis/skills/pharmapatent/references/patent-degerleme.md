# references/patent-degerleme.md — Farmasötik Patent Değerleme Protokolü

> Patent **finansal varlıktır**; M&A, licensing, sermaye tabanı, teminat, vergi ve dava tazminatı kararlarında nicel değer gerektirir. Bu protokol, üç temel değerleme yaklaşımını (cost / market / income) patent özellikleriyle uyumlu metodolojilerle uygular ve Türkiye + uluslararası farmasötik sektörde kabul gören pratik örüntüleri özetler.

## İlişkili Protokoller

- **`ruhsat-veri-imtiyazi.md`** — Pazara giriş tarihi ve veri imtiyazı, patent değerleme için temel gelir süre hesabında belirleyici
- **`fto-invalidity-protokol.md`** — Patent değerinin geçerlilik riski ile düzeltilmesi (hükümsüzlük olasılığı discount)
- **`biyobenzer-yol.md`** — Biyolojik ilaç patent portföyü değerlemede jenerik erozyon modeli
- **`yeni-modaliteler.md`** — ADC, CAR-T, mRNA-LNP için modalite-spesifik değerleme çarpanları
- **`rapor-sablonlari.md §7`** — Due Diligence Raporu şablonu — değerleme çıktısının raporlanma biçimi

## İçindekiler

1. Değerleme metodolojileri genel çerçevesi
2. Cost Approach (maliyet yaklaşımı)
3. Market Approach (piyasa yaklaşımı — comparable transactions)
4. Income Approach (gelir yaklaşımı — DCF + relief-from-royalty)
5. Monte Carlo simülasyonu ve risk ayarlaması
6. Biyolojikler ve yeni modaliteler için değerleme farkı
7. Portföy bazlı değerleme (aile + jurisdiction)
8. Vergi ve Türkiye spesifik hususlar
9. Raporlama ve savunulabilirlik

---

## 1. Değerleme metodolojileri genel çerçevesi

### Üç temel yaklaşım

Uluslararası Değerleme Standartları (IVS 210 — Intangible Assets) ve AICPA Practice Aid çerçevesinde üç temel yaklaşım:

| Yaklaşım | Prensip | Farmasötik patent için uygunluk |
|---|---|---|
| **Cost Approach** | Patentin yerine konulma maliyeti | Erken aşama, ticari gelir öncesi (düşük doğruluk) |
| **Market Approach** | Benzer patent transaksiyonları | Comparable data varsa güçlü (çoğu spesifik ilaç için zor) |
| **Income Approach** | Beklenen gelir akışı DCF | **Primer yaklaşım** — ticari ilaçlar için altın standart |

### Seçim rehberi

- **Geç aşama ürün (Faz III, onaylı, pazarda)**: Income Approach (DCF veya relief-from-royalty)
- **Orta aşama (Faz II tamamlanmış)**: Income Approach + probability adjusted (rNPV)
- **Erken aşama (Faz I, preklinik)**: Market Approach + Cost Approach kombinasyonu
- **Defansif/savunma patentleri (kullanılmayan ama rakibi engelleyen)**: Relief-from-royalty
- **Portföy/platform patentleri**: Scenario-based DCF + Monte Carlo

## 2. Cost Approach (maliyet yaklaşımı)

### Temel formül

```
Patent Değeri = Yerine Koyma Maliyeti (Replacement Cost)
              = Kümüle Ar-Ge + Patent Başvuru + Yıllık Harç + İşlem Maliyeti
              - Amortizasyon (zaman + teknik eskime)
              - Başarısızlık oranı düzeltmesi
```

### Bileşenler

**Ar-Ge maliyeti — keşif + preklinik**:
- Medisinal kimya hedef kimliklendirme: USD 2-5M
- HTS ve lead optimization: USD 15-30M
- Preklinik toksikoloji + farmakoloji: USD 10-25M
- **Toplam erken aşama**: USD 30-60M

**Ar-Ge maliyeti — klinik**:
- Faz I: USD 10-30M
- Faz II: USD 30-80M
- Faz III: USD 100-300M (onkoloji Faz III: USD 150-500M)
- **Toplam klinik**: USD 140-410M

**Patent kazanım + korunma**:
- PCT başvuru: USD 5-15K
- Ulusal fazlar (AB, ABD, JP, CN, TR): USD 50-200K
- Yıllık harçlar: USD 500-5K/yıl/ülke × 20 yıl × 30 ülke
- Tescil sürdürme: USD 150-400K / 20 yıl

### Cost Approach sınırlılıkları

- **Geleceği göstermez**: Yüksek Ar-Ge harcamasına rağmen pazarda başarısız olan ilaçlar mevcuttur
- **Fırsat maliyetini ihmal eder**: Portföy içinde spesifik patentin katkısı birebir orantılı değildir
- **Tali birinciliği**: Cost Approach tek başına ticari patent için yetersiz; Income Approach ile kombinasyon önerilir

### Cost Approach kullanımı: erken aşama

Sadece **hiçbir klinik veri bulunmayan** veya **ticari uygulanabilirliği kanıtlanmamış** patentler için birincil yaklaşım. Örnek: platform teknoloji patentleri, yeni modalite araştırma patentleri.

## 3. Market Approach (piyasa yaklaşımı)

### Comparable transactions metodu

Benzer patentlerin gerçek pazar işlemlerinden değer türetilir.

### Karşılaştırılabilirlik kriterleri

Bir transaksiyonun comparable sayılması için:
1. **Terapötik alan** aynı (onkoloji, kardiyoloji, nöroloji vb.)
2. **Modalite** aynı (small molecule, mAb, ADC, CAR-T, gene therapy vb.)
3. **Geliştirme aşaması** benzer (Faz II, Faz III, onaylı)
4. **Pazar büyüklüğü** karşılaştırılabilir (peak sales hedefi aynı büyüklük diliminde)
5. **İşlem tipi** aynı (lisans, iktisap, tek ürün M&A)
6. **Coğrafi kapsam** örtüşür

### Veri kaynakları

| Kaynak | Kapsam | Erişim |
|---|---|---|
| SEC EDGAR 8-K / 10-K | Halka açık M&A + büyük lisanslar | Açık |
| EvaluatePharma dealmaker database | Geniş farmasötik licensing | Abonelik (USD 10-30K/yıl) |
| Cortellis Deals | Merkezi deal database | Abonelik |
| GlobalData Pharma | Pipeline + deals | Abonelik |
| BIO/Ernst & Young raporları | Yıllık trend raporları | Genellikle açık |
| DealForma | Startup + platform deals | Abonelik |

### Tipik işlem değerleri (2020-2025)

**Onkoloji Faz III asset**:
- Upfront: USD 200M - 1.5B
- Milestones: USD 500M - 3B
- Royalty: %10-25

**Faz II asset**:
- Upfront: USD 50-300M
- Milestones: USD 200M - 1.5B
- Royalty: %8-15

**Faz I asset**:
- Upfront: USD 20-100M
- Milestones: USD 100M - 800M
- Royalty: %6-12

**Preklinik platform**:
- Upfront: USD 5-50M
- Milestones: USD 50-500M
- Royalty: %3-8

### Market Approach sınırlılıkları

- **Sınırlı veri**: Birçok lisans anlaşması gizli (şirketlerin yalnız milestone açıkladığı)
- **Heterojenlik**: Hiçbir iki patent tam aynı değildir
- **Survivorship bias**: Başarısız anlaşmalar raporlanmaz
- **Zamanlama**: Piyasa koşulları 2 yılda değişebilir (2020 COVID premium, 2023-2024 biotech düşüşü)

## 4. Income Approach (gelir yaklaşımı)

**En yaygın kullanılan yaklaşım**. İki ana metodu var: DCF ve Relief-from-Royalty.

### 4.1. Risk-Adjusted Net Present Value (rNPV) / DCF

**Temel formül**:

```
rNPV = Σ [ (Revenue_t - Cost_t) × Success_Probability × (1-Tax_rate) / (1+r)^t ]
```

**Parametreler**:

**Revenue projection (gelir projeksiyonu)**:
- Peak sales tahmini (USD/yıl, tepe yıl)
- Ramp-up eğrisi (ilk 5-7 yıl)
- Coğrafi yayılım (ABD %40-50, AB %25-30, JP %8-10, RoW %15-20)
- LOE sonrası erosion (small molecule: %80 kayıp ilk yıl; biyobenzer: %30-50 ilk yıl)

**Cost projection**:
- COGS: küçük molekül %10-20; biyolojik %15-30; ADC %30-50
- SG&A: %25-40 of revenue
- Ongoing R&D: %5-15 of revenue
- Royalty burden: varsa

**Probability of Technical and Regulatory Success (PTRS)**:

| Aşama | Küçük molekül | mAb/biyolojik | Gen/hücre terapisi |
|---|---|---|---|
| Preklinik → Faz I | %63 | %70 | %55 |
| Faz I → Faz II | %45 | %55 | %45 |
| Faz II → Faz III | %26 | %35 | %30 |
| Faz III → Onay | %55 | %65 | %60 |
| **Preklinik → Onay** | **%4.1** | **%8.8** | **%4.4** |
| Onay → Peak sales | %95 | %95 | %90 |

*Kaynak: BIO QLS 2023, DiMasi et al., KMR Group*

**Discount rate (r)**:
- Büyük farma (risksiz + risk premium): %8-12
- Mid-cap biotech: %12-18
- Early-stage biotech: %18-30
- Pre-clinical asset: %25-40
- Jurisdiction risk (Turkey): +1-2% ek

### 4.2. Relief-from-Royalty (RFR)

**Temel mantık**: Patent sahibi olmasaydı, aynı teknolojiyi üçüncü taraftan lisansla alacaktı. Kaçınılan royalty → patent değeri.

**Formül**:

```
Patent Değeri = Σ [ Revenue_t × Royalty_Rate × (1-Tax) / (1+r)^t ]
```

**Royalty rate seçimi**:

| Modalite | Tipik royalty | Not |
|---|---|---|
| Küçük molekül onkoloji | %6-12 | Faz III+ |
| mAb onkoloji | %8-15 | Patent kuvveti + platform |
| ADC | %10-20 | Payload + linker + conjugation patentleri |
| CAR-T | %8-15 | Platform teknoloji değeri |
| mRNA-LNP | %10-18 | Moderna + BioNTech portföyü ağır |
| Gene therapy | %10-20 | Viral vektör + transgen |
| Medical device combination | %3-8 | Cihaz düşük |

**Kullanım alanları**:
- Vergi değerlemesi (intercompany transfer pricing)
- Dava tazminat hesaplaması (reasonable royalty)
- Portföy değerlemesi (kümülatif)

### 4.3. Real Options yaklaşımı

Klasik DCF, geleceğe dair esnek kararları (ilerletme, durdurma, genişletme) hesaba katmaz. Real options, Black-Scholes modelini uyarlayarak bu esnekliği değerler.

**Uygunluk**: Yüksek belirsizlik + büyük Ar-Ge harcaması kararları (Faz III go/no-go, yeni endikasyon açma, coğrafi genişleme).

**Karmaşıklık**: Uzmanlık gerekir; basit DCF'den 3-5× daha uzun analiz.

## 5. Monte Carlo simülasyonu ve risk ayarlaması

### Monte Carlo uygulaması

**Parametreler olasılık dağılımı ile tanımlanır**:
- Peak sales: log-normal, mean USD 500M, std USD 200M
- PTRS: beta distribution
- Launch year: triangular (best/likely/worst)
- LOE year: uniform (patent expiry ± 2 yıl)

**Çıktı**: 10,000+ simülasyon → değer dağılımı (P10, P50, P90)

**Örnek sonuç**:
```
P10 (konservatif): USD 120M
P50 (median):      USD 340M  ← "beklenen değer"
P90 (agresif):     USD 780M
Mean:              USD 410M
```

### Raporlama

Tek bir noktasal değer yerine **değer aralığı** raporlanır. M&A müzakereleri için pazarlık marjı sağlar.

### Araçlar

- Excel + @RISK eklentisi (USD 1500/yıl) — en yaygın
- Python (numpy + matplotlib) — açık kaynak
- Crystal Ball (Oracle)
- ModelRisk (Vose)

## 6. Biyolojikler ve yeni modaliteler için değerleme farkı

### Biyolojik vs küçük molekül

| Boyut | Küçük molekül | Biyolojik |
|---|---|---|
| LOE erozyonu | %80-90 (1 yıl) | %20-40 (1 yıl), %40-60 (3 yıl) |
| COGS | %10-20 | %15-30 |
| Patent kuvveti | Genellikle dar | Daha çok formülasyon/proses |
| Veri imtiyazı (EU) | 8+2+1 yıl | 8+2+1 yıl (benzer) |
| Biyobenzer eşik | Jenerik — kolay | Biyobenzer — zor |

**Değerleme etkisi**: Biyolojikler **daha uzun monetization ömrü** → daha yüksek NPV/terminal value.

### Yeni modaliteler için modifikasyonlar

**ADC**:
- Royalty stack: payload + linker + conjugation + antibody (her biri ayrı)
- Tipik toplam %15-25 royalty burden (net gelir bazlı)
- LOE bulanık — farklı komponenlerin patent süreleri farklı

**CAR-T**:
- Manufacturing complexity → COGS %40-50 (NPV'de ciddi)
- Platform teknoloji patentleri (Jurik, Juno, Kite) lisans gerekliliği
- Once-per-patient → volume düşük ama fiyat çok yüksek (USD 400K+)
- Patent kuvveti modalite bazlı

**mRNA-LNP**:
- Alnylam/Moderna/BioNTech cross-licensing zorunluluğu
- LNP formülasyon patenti kritik (Acuitas patent portföyü Moderna/BioNTech/Alnylam'a lisanslandı)
- Tipik royalty stack %15-25

**Gene therapy**:
- AAV manufacturing maliyeti çok yüksek
- One-shot tedavi — LTV hesabı farklı
- Durability belirsizliği → revenue projection yüksek varyans

## 7. Portföy bazlı değerleme

### Patent ailesi (INPADOC) değerleme

Bir ilaç için tipik olarak **5-50 patent** bulunur (birincil madde + formülasyon + polimorf + cihaz + kombinasyon + ikinci tıbbi kullanım).

**Yaklaşım**:
1. Portföy haritası (hangi patent hangi ülke)
2. Her bir patentin kapsam değeri (primer/sekonder)
3. Coverage overlap analizi (gereksiz tekrar)
4. En zayıf halka testi (blok edilen pazar girişi için hangisi kritik)

### Coğrafi ağırlıklandırma

**ABD**: Toplam ilaç pazarı %40-45 → patentin USD değerinin %45'i
**AB (EPO + ulusal)**: %25-30
**Japonya**: %8-10
**Çin**: %10-15 (hızla artıyor)
**Türkiye**: %0.5-1 (küresel pazara göre küçük ama stratejik orta doğu kapısı)

### Portföy sinerjisi

Tek bir patentin değeri ile portföy toplam değeri arasında nonlinear ilişki:
- **Single patent**: Değer = X
- **Patent family + divisionals + continuations**: Değer = 2-4X (sinerjik)
- **Cross-licensing + defensive use**: Değer = 3-5X (ekosistem etkisi)

## 8. Vergi ve Türkiye spesifik hususlar

### Türkiye Ar-Ge teşviki

- Ar-Ge merkezi yasası (5746) kapsamında patent başvurusu Ar-Ge harcaması olarak sayılır
- Gelir vergisi indirimi %100
- Patent tescili → **patent box rejimi** (5520 sayılı Kurumlar Vergisi Kanunu m. 32/B): patent gelirine %50 kurumlar vergisi indirimi

### Transfer pricing (grup içi lisans)

- Türkiye'de ilişkili taraflarla patent lisansı BEPS Action 8-10 uyumlu emsal fiyata uygun olmalı
- Relief-from-royalty yaygın kullanılır
- Maliye Bakanlığı doğrulamada comparable transactions araması yapar
- Mükellef ispat yükümlülüğü (burden of proof)

### Dava tazminatı

SMK m. 151 kapsamında patent tecavüz tazminatı üç yönteden **en yüksek olanı**:
1. Fiili zarar + yoksun kalınan kâr
2. Tecavüz edenin net kârı (disgorgement)
3. Lisans analojisi (reasonable royalty — relief-from-royalty metodolojisi)

Yöntem 3 için RFR metodolojisi direkt uygulanır; bilirkişi raporuyla savunulur.

### SGK ve fiyatlandırma etkisi

Türkiye'de referans ülke en düşük fiyat mantığı → patent ömrü boyunca revenue tepe noktasında bile Batı'dan düşük. Bu NPV'de %20-40 indirim etkisi yaratır.

## 9. Raporlama ve savunulabilirlik

### Değerleme raporunun zorunlu bileşenleri

IVS 210 ve IFRS 3 uyumlu değerleme raporu:

1. **Kapsam beyanı**
   - Değerleme amacı (M&A / vergi / dava / sermaye)
   - Değerleme tarihi
   - Değerleme standardı (IVS / USPAP / AICPA)

2. **Varsayımlar ve sınırlar**
   - Açık varsayımlar (peak sales, PTRS, discount rate)
   - Sınırlar (erişilemeyen veriler, tarihsel belirsizlik)

3. **Metodoloji seçimi**
   - Hangi yaklaşım birincil, hangisi destekleyici
   - Neden diğer yaklaşımların uygun olmadığı

4. **Girdilerin kaynakları**
   - Market data → kaynak + erişim tarihi
   - Industry benchmarks → rapor + sayfa no
   - Şirket içi data → dahili dokümantasyon referansı

5. **Duyarlılık analizi**
   - Her kritik parametre için ±20% senaryosu
   - Tornado chart

6. **Monte Carlo dağılımı** (varsa)
   - P10/P50/P90
   - Mean ± std

7. **Sonuç**
   - Değer aralığı (genellikle P20-P80)
   - Punti değer (eğer gerekiyorsa)

8. **Yazar sorumluluğu**
   - CVA (Chartered Valuation Analyst) / ASA / RICS üyeliği
   - Çıkar çatışması beyanı
   - Sign-off

### Savunulabilirlik

**Vergi denetimi**: Maliye Bakanlığı değerleme raporuna itiraz ederse, metodoloji + parametre seçimi savunulabilmelidir. IVS + AICPA Practice Aid atıflı metodoloji güvenilirdir.

**Dava**: Bilirkişi karşı rapor verirse, her parametre için alternatif yaklaşım tartışılmalı ve neden seçilen parametrenin üstün olduğu açıklanmalıdır.

**M&A due diligence**: Karşı taraf kendi bağımsız değerleme yapar. Aradaki fark genellikle %20-40 — müzakere alanı burada.

---

*Patent değerleme, hukukla beraber maliye, ekonometri ve stratejik yönetim kesişim noktasıdır. Bu protokol genel çerçeve sunar; her somut vaka için sertifikalı bir değerleme uzmanı (CVA/ASA/RICS) ile koordinasyon zorunludur. Nihai değer aralığı hukuki + vergisel savunma dokümantasyonu içinde raporlanır.*
