# references/biyobenzer-yol.md — Biyobenzer Onay Yolu ve Karşılaştırılabilirlik Protokolü

> Biyobenzer (biosimilar), referans biyolojik ürünün **aynısı değil benzeridir** — canlı hücre kültüründen üretim doğası gereği %100 aynı yapı mümkün değildir. Bu protokol, biyobenzer geliştirme, karşılaştırılabilirlik kanıtı, patent kesişimi, ruhsat rejimi, extrapolation, interchangeability ve pazara giriş stratejisini Türkiye + AB + ABD eksenlerinde yapılandırır.

## İlişkili Protokoller

- **`ruhsat-veri-imtiyazi.md`** — Biyolojik referans ürün için 6 yıllık veri imtiyazı Türkiye'de biyobenzer başvurusunun temel engelidir
- **`fto-invalidity-protokol.md`** — Formülasyon, proses, cihaz patentleri üzerinden biyobenzer FTO + invalidity
- **`patent-degerleme.md`** — Biyobenzer pazar payı + erozyon modelinin NPV üzerindeki etkisi
- **`yeni-modaliteler.md`** — ADC, CAR-T, gene therapy biyobenzer — henüz düzenleyici tanımı yok
- **`tibbi-cihaz-uts.md`** — Biyolojik + enjektör kombinasyon ürünlerde cihaz patenti stratejisi
- **`rapor-sablonlari.md §9`** — Biosimilar Pathway Briefing şablonu

## İçindekiler

1. Biyobenzer tanımı ve farmasötik jenerikle fark
2. Karşılaştırılabilirlik paketi (CQA + analitik + klinik)
3. AB düzenleyici rejim (EMA EPAR)
4. ABD düzenleyici rejim (FDA BPCIA)
5. Türkiye düzenleyici rejim (TİTCK)
6. Veri imtiyazı ve patent kesişimi
7. Extrapolation (endikasyon uzatma)
8. Interchangeability (değiştirilebilirlik)
9. Pazar dinamikleri ve fiyat erozyonu
10. Biyobenzer-spesifik IP stratejileri

---

## 1. Biyobenzer tanımı ve farmasötik jenerikle fark

### Temel tanım

**Biyobenzer (biosimilar)**:
> "Biyolojik referans ürüne yüksek benzerlikte olan; kalite, etkinlik ve güvenlik açısından klinik olarak anlamlı farklılık göstermeyen biyolojik ürün."

**EMA tanımı** (Directive 2001/83/EC Art. 10(4)): "Similar biological medicinal product".

**FDA tanımı** (BPCIA 2010, 42 USC §262(i)(2)): "Biosimilar" veya "highly similar" + "no clinically meaningful differences".

### Jenerik vs biyobenzer — yapısal farklılıklar

| Boyut | Jenerik (küçük molekül) | Biyobenzer |
|---|---|---|
| Yapısal karmaşıklık | <1000 Da, iyi tanımlanabilir | 10,000-150,000 Da, heterojen |
| Üretim | Kimyasal sentez — tekrarlanabilir | Canlı hücre kültürü — lot-to-lot varyasyon |
| "Aynılık" mümkün mü | Evet (kimyasal kimlik) | Hayır — sadece "benzerlik" |
| İmmünojenisite riski | Genellikle düşük | Kritik değerlendirme gerekli |
| Ruhsat maliyeti | USD 1-5M | USD 100-300M |
| Geliştirme süresi | 3-5 yıl | 7-10 yıl |
| Biyoeşdeğerlik çalışması | Küçük Faz I PK (~30 kişi) | Faz I PK + Faz III etkinlik (~300-900 kişi) |
| Formülasyon özgürlüğü | Neredeyse tam | Kısıtlı — referans ile benzer olmalı |
| LOE sonrası erozyon (1 yıl) | %80-90 | %20-40 |
| LOE sonrası erozyon (3 yıl) | %95+ | %40-60 |

## 2. Karşılaştırılabilirlik paketi (comparability package)

### Adım adım karşılaştırılabilirlik

#### 2.1. Critical Quality Attributes (CQA) tespiti

Referans ürünün **kritik kalite özellikleri** tanımlanır:
- Primer yapı: amino asit sekansı, disülfid köprüleri
- İkincil/üçüncül yapı: alpha-helix / beta-sheet oranı
- Kuaterner yapı: monomer vs dimer vs agregat
- Post-translational modifications: glikozilasyon, oksidasyon, deamidasyon
- Yükler: pI, yüzey yükü dağılımı
- Hidrofobisite
- Biyolojik aktivite (target binding, potency)
- Immünojenisite potansiyeli
- Viskozite (yüksek konsantrasyon formülasyonu)

#### 2.2. Analitik karşılaştırma

**Mandatory metodlar**:
| Metod | Ölçüm |
|---|---|
| LC-MS (peptid haritalama) | Primer yapı |
| SEC-HPLC | Monomer vs agregat |
| CE-SDS / cIEF | Yük varyantları |
| Capillary Electrophoresis | Heterojenlik |
| N-Glycan analizi (HPAEC-PAD, LC-MS) | Glikan paterni |
| CD spektroskopisi | İkincil yapı |
| DSC | Termal stabilite |
| FTIR / Raman | Üçüncül yapı |
| SPR / ForteBio BLI | Target binding kinetiği |
| Cell-based potency assay | Biyolojik aktivite |

**Spesifikasyon penceresi**: Her CQA için referans ürünün lot-to-lot varyasyon aralığı (tipik olarak 10-30 lot) × 2 std sapma → biyobenzer hedef aralık.

#### 2.3. Non-klinik karşılaştırma

- In vitro: reseptör bağlanma (HER2, VEGF, TNF-α vs.) + efektör fonksiyonlar (ADCC, CDC, ADCP)
- In vivo (gerekliyse): PK + PD hayvan modeli

#### 2.4. Klinik karşılaştırma

**Faz I** — Single-dose PK (~30-60 sağlıklı gönüllü veya hasta):
- Primary: AUC, Cmax (equivalence limit ±20%)
- Secondary: clearance, half-life, immünojenisite

**Faz III** — Confirmatory efficacy trial:
- En duyarlı endikasyonda (genellikle referans ürünün onay aldığı ilk endikasyon)
- Randomize, paralel gruplar, çift-kör
- Equivalence hypothesis (non-inferiority alone yeterli değil — "too good" da yanlış)
- Örnek boyutu: 200-900 hasta (endikasyona göre)

**İmmünojenisite**:
- ADA (anti-drug antibody) oluşumu %
- Neutralizing antibody oluşumu %
- Switching study (randomize) — referans'tan biyobenzere geçiş immünojenisite

## 3. AB düzenleyici rejim (EMA EPAR)

### Başvuru çerçevesi

**Directive 2001/83/EC Article 10(4)** — "similar biological medicinal product" başvurusu.

### Prosedür

1. **Scientific advice** (CHMP SAWP) — başvuru öncesi EMA ile istişare (önerilir)
2. **MAA submission** — Modül 1-5 CTD formatı
3. **CHMP assessment** — 210 gün değerlendirme + clock stops
4. **Opinion + Commission Decision** — tipik toplam 12-18 ay
5. **Post-approval** — PSUR + PASS (Post-Authorisation Safety Study) sıklıkla gerekir

### İlk biyobenzer (2006)

- Somatropin (Omnitrope, Sandoz) — 2006-04
- 2023 itibarıyla AB'de 80+ biyobenzer onaylı
- Biyobenzer penetrasyon oranı: %30-50 (TNF-α inhibitörleri için %70-80'e kadar)

### Veri imtiyazı (AB)

**Referans biyolojik için**: 8 yıl reg. münhasırlık + 2 yıl pazar münhasırlık + 1 yıl yeni endikasyon (8+2+1 toplam 11 yıl).

Biyobenzer başvurusu 8. yıl sonunda kabul edilir; pazara arz 10 yıl sonra.

### Extrapolation

AB bir endikasyonda biyobenzerlik kanıtlanmışsa, **bilimsel gerekçe ile** diğer endikasyonlara uzatılabilir. Örnek: infliksimab biyobenzeri (Remsima) romatoid artritte kanıtlanıp Crohn + ülseratif kolit + ankilozan spondilit + psöriyazis + psöriyatrik artrit gibi 5+ endikasyona uzatıldı.

### Interchangeability (AB, 2022'den sonra)

EMA + HMA ortak açıklama (2022): Biyobenzerler ve referans ürünler Avrupa Birliği genelinde **karşılıklı değiştirilebilir** olarak kabul edilir. Fakat **eczane değişimi** üye ülke hukukuna göre değişir:
- Almanya, Fransa — eczacı değişimi mümkün ama kısıtlı
- İngiltere — NHS tender bazlı
- Türkiye (ilgili değil ama karşılaştırma için) — SGK ihalesi bazlı

## 4. ABD düzenleyici rejim (FDA BPCIA)

### BPCIA (Biologics Price Competition and Innovation Act, 2010)

**42 USC §262(k)** — biyobenzer başvurusu için 351(k) pathway.

### Başvuru kategorileri

**Biosimilar (351(k))**:
- Faz III klinik çalışma gerekli
- Interchangeability ayrıca talep edilebilir (ek veri gerekir)

**Interchangeable biosimilar (351(k) + switching studies)**:
- Switching study (3+ switch döngüsü) gerekli
- Eczacı değişimi için özel yetki (Purple Book "I" işareti)

### Süreç

1. **BPD meeting** (Biosimilar Product Development) — FDA ile erken iletişim
2. **IND submission** — klinik geliştirme başlar
3. **351(k) application** — kapsamlı dosya
4. **FDA review** — 10 ay hedef
5. **Approval + Purple Book listing**

### İlk biyobenzer (2015)

- Filgrastim-sndz (Zarxio, Sandoz) — 2015-03
- 2024 itibarıyla ABD'de 50+ biyobenzer onaylı
- Interchangeable biosimilar sayısı 8-10 (2024 sonuçları)

### Veri imtiyazı (ABD)

**Referans biyolojik**: **12 yıl** regülatör münhasırlık + 4 yıl data exclusivity başlangıç (toplam 12 yıl).

Biyobenzer başvurusu 4. yıldan itibaren FDA'ya sunulabilir; onay 12 yıldan önce verilmez.

**Not**: ABD'de biyolojik için 12 yıl, AB'nin 10 yılından (8+2) uzun — bu neden büyük farma biyolojiklerde ABD'ye daha fazla yatırır.

### Patent dance (BPCIA §262(l))

Biyobenzer başvurusu kabul edildikten sonra referans ürün üreticisi ile "patent dance" süreç:
- 20 gün: biyobenzer firma patent + 351(k) dosyası kopyalarını referansa gönderir
- 60 gün: referans firma ilgili patentler listesi
- 60 gün: biyobenzer firma claim-by-claim analizi
- 60 gün: referans firma karşı analiz
- Taraf anlaşır → patent dava stratejisi
- Anlaşamaz → dava

### Interchangeability ABD'de

Eczacının direk değişim yapabilmesi için FDA interchangeable statüsü gerekli. Kısıtlar:
- 3 switch döngüsü çalışma
- İmmünojenisite benzerliği
- Sağlık sonucu farkı yok

2023'den itibaren FDA interchangeability için gereklilikleri hafiflettiğini açıkladı → biyobenzer ile interchangeable arasındaki fark azalıyor.

## 5. Türkiye düzenleyici rejim (TİTCK)

### Yasal çerçeve

- Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği (2022 revizyonu)
- Article 10(4) benzer biyolojik ürün başvurusu
- TİTCK Biyobenzer Kılavuzu (2013, güncellemeler)

### Başvuru tipi

**Benzer biyolojik ürün (similar biological medicinal product)** — TİTCK terminolojisinde resmi ad.

### Veri paketi

AB EMA ile yüksek oranda uyumlu:
- Kalite karşılaştırması (full)
- Nonklinik karşılaştırma
- Klinik karşılaştırma (faz I PK + faz III etkinlik)
- İmmünojenisite

### Ek Türkiye-spesifik gereklilikler

- Türk popülasyonunda klinik veri (gerekirse; genellikle pivotal çalışma içinde 20-40 Türk hasta yeterli)
- TİTCK'nın Avrupa Farmakopesi uyumlu kalite standartları
- GMP denetimi Türkiye tesisi için

### Veri imtiyazı (Türkiye)

**6 yıl** (biyolojik ve küçük molekül için aynı — farklı değil). Gümrük Birliği alanında ilk ruhsat tarihi baz alınır.

### Onay süresi

- Tipik: 18-30 ay
- Eksiklik döngüsü 2-3 tur olabilir

### İlk biyobenzer (Türkiye)

- Filgrastim biyobenzeri (2011) — TİTCK ilk benzer biyolojik
- 2024 itibarıyla Türkiye'de 40+ biyobenzer onaylı

### SGK geri ödeme

Tüm biyobenzerler referans ürünle aynı endikasyon kodunda geri ödeme alır. SGK ihalesinde en ucuz teklif kazanır; ihale periyodik (genellikle 6-12 ay).

### Pazar dinamikleri (Türkiye)

- Biyobenzer penetrasyon %40-60 (TNF-α inhibitörleri)
- Fiyat erozyonu: ilk yıl %30-40, 3 yıl sonra %50-70
- SGK ihale kazanan biyobenzer geçici tekel yaşar (6-12 ay)

## 6. Veri imtiyazı ve patent kesişimi

### Üç katmanlı koruma

Referans biyolojik üreticisinin "koruma tuvali":

1. **Primer patent** — molekül veya sekans (en değerli)
2. **Üretim proses patentleri** — hücre hattı, kültür koşulları, saflaştırma
3. **Formülasyon patentleri** — tampon + eksipiyan + pH + stabilizatörler
4. **Cihaz patentleri** — prefilled syringe, oto-enjektör, pen
5. **Endikasyon patentleri** — her endikasyon ayrı ikinci tıbbi kullanım
6. **Dozaj rejim patentleri** — spesifik dozaj + sıklık
7. **Veri imtiyazı** — regülatör koruma (patentten bağımsız)

### Biyobenzer FTO sorunları

Biyobenzer firmanın tipik FTO haritası:
- Sekans: genellikle patent süresi dolmuş (molekül eski)
- Üretim proses: kendi farklı hücre hattı (CHO vs NS0 vs yeast) ile aşılır
- Formülasyon: orijinal formülasyondan farklı tampon/pH ile aşılabilir
- Cihaz: üçüncü taraf tedarikçi (Ypsomed, SHL, BD) veya kendi geliştirme
- Endikasyon: patent süresi dolmuşsa veya skinny label

### Patent duvarı takvimi (örnek: adalimumab)

Adalimumab (Humira, AbbVie) için:
- Molekül patenti: 2016 (ABD), 2018 (AB)
- Formülasyon patenti: 2022 (yüksek konsantrasyonlu)
- Cihaz patenti: 2024
- Üretim patenti: 2030

**Pratik pazara giriş**:
- AB: 2018 (ilk biyobenzer dalga: Amgevita, Hyrimoz, Imraldi)
- ABD: 2023 (patent settlements ile geciktirildi; 2016 molekül patenti sonrası 7 yıl patent savunma ile uzatıldı)

## 7. Extrapolation (endikasyon uzatma)

### Temel ilke

Biyobenzerlik **en duyarlı endikasyonda** klinik olarak kanıtlandıysa, bilimsel gerekçe ile diğer endikasyonlara uzatılabilir — **her endikasyon için ayrı Faz III gerekmez**.

### En duyarlı endikasyon seçimi

Mekanizma-bazlı değerlendirme:
- Etki büyüklüğü en büyük (treatment effect size büyük → küçük farklar tespit edilir)
- Örnek boyutu en küçük (maliyet + süre tasarrufu)
- Popülasyon homojen

### Extrapolation edilebilir endikasyonlar

**Infliksimab biyobenzer (örnek)**:
- Pivotal çalışma: Romatoid artrit (Faz III, 600 hasta)
- Extrapolation: Crohn, ülseratif kolit, ankilozan spondilit, psöriyazis, psöriyatrik artrit
- **Toplam 6 endikasyon tek pivotal çalışma ile**

### Extrapolation reddedildiği durumlar

- Farklı immün mekanizmalar (otoimmün vs onkolojik hedefleme)
- Farklı Fc efektör fonksiyonları (ADCC vs CDC-bağımlı)
- Farklı farmakokinetik davranış

**Tarihsel örnek**: Trastuzumab biyobenzer (Amgen'in Kanjinti), meme kanserinde kanıtlandı → mide kanseri için ek Faz III istenmedi (mekanizma aynı — HER2 inhibition).

## 8. Interchangeability (değiştirilebilirlik)

### Üç kavram ayrımı

| Kavram | Anlam |
|---|---|
| **Biosimilarity** | Biyobenzer onay — referansla yüksek benzer + klinik anlamlı fark yok |
| **Switchability** | Doktor değişimi güvenli — tüm biyobenzerler bu kategoride |
| **Interchangeability** | Eczacı değişimi güvenli — ek kanıt gerekli (ABD spesifik) |

### AB'de interchangeability

EMA 2022 ortak açıklama: Biyobenzer = interchangeable (üye ülke hukukuna göre eczacı değişimi değişir).

### ABD'de interchangeability

FDA Purple Book'ta "I" işareti. Ek kanıt:
- 3 switch döngüsü switching çalışması
- İmmünojenisite fark yok
- PK eşdeğerlik sürer

### Türkiye'de interchangeability

Resmi bir kavram yok. Pratikte:
- SGK ihale kazanan biyobenzer hastanelerde otomatik kullanılır
- Doktor "tedavi değişikliği" talep ederse geri ödeme sorunu
- Eczacı değişimi formel olarak tanımlı değil

## 9. Pazar dinamikleri ve fiyat erozyonu

### Biyobenzer erozyon eğrileri

| Süre | Küçük molekül jenerik | Biyobenzer |
|---|---|---|
| 1 yıl sonra | %70-80 fiyat erozyon, %80-90 hacim kaybı | %20-30 fiyat erozyon, %30-50 hacim kaybı |
| 3 yıl sonra | %90+ | %40-60 |
| 5 yıl sonra | %95+ | %60-80 |

### Neden biyobenzer daha yavaş penetre eder?

- Doktorların konservatifliği (tanıdık biyolojik ilacı değiştirmek istememe)
- Hasta immünojenisite endişesi
- Hastane formuler bariyerleri
- Biyobenzer üretim maliyeti yüksek → fiyat indirimi limit
- Referans ürün firması tipik olarak aggressive defense (rebate'ler, contracts)

### İlk-girmenin değeri

AB pazarında ilk biyobenzer:
- İlk 6-12 ay tekel (ikinci biyobenzer gelene kadar)
- Pazar payı: referans ürünün %30-50'si
- Sonra fragmente (3-5 biyobenzer rekabet)

**Stratejik tavsiye**: **Hızlı ikinci** biyobenzer ol — ilk biyobenzer patent lawsuit yüküyle karşılaşır; ikinci, riski alır ama settlement alan ile pazara girer.

## 10. Biyobenzer-spesifik IP stratejileri

### Savunma IP (biyobenzer tarafı)

1. **Kendi formülasyon patentleri** — biyobenzer firmasının kendi stabilize formülasyonu
2. **Kendi üretim proses patentleri** — orijinal üreticiden farklı CHO hattı, farklı medium, farklı saflaştırma
3. **Kendi cihaz patentleri** (varsa) — veya üçüncü taraf lisans
4. **Defensive publication** — rakibin patent alamaması için açık yayım

### Saldırı IP (biyobenzer tarafı)

1. **Hükümsüzlük davaları** — referans ürünün zayıf patentleri hedef
2. **Üçüncü kişi görüşü** — TÜRKPATENT, EPO yayımlanmış başvurulara
3. **EPO opposition** — 9 aylık pencere
4. **Declaratory judgment** (ABD) — "patent ihlali yok" ön tespit davası

### Settlement dinamikleri

ABD'de "pay-for-delay" anlaşmaları FTC incelemesine tabi. AB + Türkiye'de daha rahat. Tipik settlement:
- Referans: patent savunma
- Biyobenzer: belirli tarihe kadar pazara girmeme + ek ödeme

---

*Biyobenzer geliştirme en yüksek riskli ve en yüksek maliyetli jenerik kategorisidir. Patent + veri imtiyazı + klinik geliştirme + cihaz stratejisi entegre karar gerektirir. Bu protokol genel çerçeve sunar; her spesifik biyobenzer için uzman regülatör danışmanı + patent vekili ile koordinasyon zorunludur. Türkiye'de TİTCK Biyobenzer Kılavuzu güncellemelerinin takibi kritiktir.*
