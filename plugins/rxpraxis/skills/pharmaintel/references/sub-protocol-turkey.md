# pharmaintel — Türkiye Sub-Protocol (TİTCK + SGK + SUT Layer)

## Scope

Türkiye, daha önce pharmaintel'in genel global scope'undan deliberately dışlanmıştı. Ancak Türkiye'de operasyon yürüten herhangi bir pharma şirketi (multinational originatör Türkiye operasyonu veya yerli sponsor) için **Türkiye-spesifik regulatuar + reimbursement gerçeği** materyal stratejik önem taşır. Bu sub-protocol Türkiye'yi optional layer olarak adapte eder — **default OFF, explicit invocation ON**.

**Neden ayrı sub-protocol:**

- TİTCK (Türkiye İlaç ve Tıbbi Cihaz Kurumu) regulatuar pathway'i FDA / EMA'dan farklı bir mantık taşır
- SGK (Sosyal Güvenlik Kurumu) geri ödeme kararları SUT (Sağlık Uygulama Tebliği) çerçevesinde işler — diğer HTA framework'lerine (NICE, G-BA, HAS, PBAC) doğrudan tercüme edilemez
- Fiyatlandırma 5-ülke referans pazarlık + KDV + zorunlu indirim + dağıtım marjı şeritleri çok-katmanlıdır
- Türkiye RWE altyapısı bölge-spesifik registries üzerinden işler
- ATÜB-EMA reliance pathway opsiyoneldir ve hâlâ olgunlaşmaktadır

## Trigger logic (v1.7.0 — generic-by-default discipline)

Bu sub-protocol **yalnızca query content**'ine göre tetiklenir. Kullanıcının coğrafi konumu, işvereni, rolü veya uzmanlık alanı **trigger değildir** (bkz. `generic-by-default.md` Article 5). Bu, v1.6.0 production test'inde tespit edilen kritik bug'ın v1.7.0'da düzeltilmesidir.

### (A) Trigger by query keywords (explicit)

Aşağıdaki Türkçe regulatuar / reimbursement terimleri query'de açıkça geçtiğinde tetiklenir:

TİTCK, SGK, SUT, Sağlık Uygulama Tebliği, Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği, Sağlık Bakanlığı, Türk farmasötik fiyatlandırma, KDV indirim, kâr marjı, depocu marjı, eczacı marjı, geri ödeme listesi, EK-4A, EK-4C, EK-4D, kullanım protokolü, reçete kuralı, MEDULA, Reliance Pathway Türkiye, ATÜB, ZSF (zorunlu satış fiyatı), tavan fiyat, eşdeğer ilaç, referans fiyat sistemi, Hızlı Erken Erişim Programı (HEEP), isimsel ithalat, şahsi ithalat, SGK Komisyon kararı, Türk Eczacılar Birliği, AİFD, TİSD, KAP disclosure, reçete renewal Türkiye bağlamında.

### (B) Trigger by query content (semantic — query-based, NOT user-based)

Türkiye sub-protocol'ü ancak query'nin **explicit content'i** Türkiye-spesifik regulatuar / reimbursement / market access soruları içerdiğinde tetiklenir.

**Trigger örnekleri (geçerli):**
- Query'de Türkçe regulatuar terim explicitly geçer ("X ilacının TİTCK durumu", "Y için SGK geri ödemesi")
- Query bir Türk yerli sponsor adını explicitly mention eder ("[Türk sponsor X] pipeline'ı")
- Query Türkiye-spesifik kapsam ifadesi içerir ("Türkiye'de [endikasyon] pazarı", "Türk hekim katılımı [trial]'de")
- Query "Türkiye launch", "Türk hasta erişimi", "Türk RWE registry" gibi açık Türkiye kapsamı çağırır

**Trigger DEĞİLDİR (forbidden — user-identity-based):**
- ❌ Kullanıcının Türkiye'de yaşaması veya çalışması
- ❌ Kullanıcının Türk pharma şirketinde çalışması
- ❌ Kullanıcının uzmanlık alanının Türkiye operasyonunu kapsaması
- ❌ Kullanıcının rolünün medical director / market access / regulatory affairs Türkiye olması
- ❌ Memory'den gelen "user is based in Türkiye" / "user works for [Türkiye'deki şirket]" bilgisi

**Trigger DEĞİLDİR (forbidden — query language, v6.0.0):**
- ❌ Sorgunun Türkçe yazılmış olması. **Sorgu dili kendi başına content trigger değildir** — bkz. `generic-by-default.md` Article 5.3. Bir Türkçe-yazılı sorgu global bir konuyu sorabilir (örn. "T-DXd'nin FDA endikasyonları nedir?"); aynı şekilde bir İngilizce-yazılı sorgu Türkiye-spesifik olabilir (örn. "What's T-DXd's SGK reimbursement status?"). Sadece yukarıdaki (A) veya (B) maddelerinde listelenen **semantic content** trigger'dır — yazım dili değil.
- Bu kural v5.0.0 production test (T-DXd Türkçe sorgu "trastuzumab deruxtecan raporu hazırla") sonrası v6.0.0'da kodifiye edilmiştir. Runtime o testte bu kuralı ihlal ederek `sub-protocol-turkey` fire etmişti; G61 manifest gate v6.0.0'da eklenerek validator seviyesinde pattern detection yapılmaktadır.

Eğer query content Türkiye-bağlamı çağırmıyorsa, sub-protocol-turkey **YÜKLENMEZ**, kullanıcı kim olursa olsun. Bu, bir T-DXd asset profile'ının default olarak Türkiye katmanı içermemesi gerektiği anlamına gelir — ancak query "T-DXd'nin Türkiye'deki SGK geri ödeme durumu" diye sorduysa katman yüklenir.

**Tetiklenmez (default OFF):** Global pipeline / global regulatuar / global commercial / global modality query'lerinde Türkiye katmanı yüklenmez. Query Türkiye'yi açıkça dahil etmediği sürece global scope korunur.

---

## Free-tier access map

| Source | URL pattern | Language | What to fetch |
|---|---|---|---|
| **TİTCK ana web sitesi** | titck.gov.tr | Türkçe | Ruhsat duyuruları, ilaç fiyat listesi, klinik araştırma onayları, GVP/GMP duyuruları, mevzuat |
| **TİTCK ilaç ürün izlem sistemi** | onlineuygulamalar.titck.gov.tr | Türkçe | Ruhsatlı ilaç sorgulaması, ürün takibi, KÜB / KT erişimi |
| **TİTCK KÜB / KT veritabanı** | titck.gov.tr | Türkçe | Kısa Ürün Bilgisi (KÜB; analog FDA Prescribing Information) + Kullanma Talimatı (KT; analog Medication Guide) |
| **SGK SUT** | sgk.gov.tr | Türkçe | Sağlık Uygulama Tebliği güncel metni + güncellemeleri; Bedeli Ödenecek İlaçlar Listesi |
| **SGK Ek listeleri** | sgk.gov.tr | Türkçe | EK-4A (kamuda ödenen ilaçlar), EK-4B (zorunlu indirim oranları), EK-4C (özel hastane ödenenler), EK-4D (kullanım protokolüne tabi ilaçlar) |
| **MEDULA Eczane / Hastane** | medula.sgk.gov.tr | Sınırlı erişim (kullanıcı-başvurulu) | Real-time reçete kuralları, e-reçete operasyonel detay |
| **Resmi Gazete** | resmigazete.gov.tr | Türkçe | TİTCK + SGK kararnamelerinin yasal dayanağı; bakanlık kararları, tarihli mevzuat değişiklikleri |
| **Türk Eczacılar Birliği** | teb.org.tr | Türkçe | Eczacılık piyasası analizleri, dağıtım kanalı verileri (sınırlı kamu erişimi) |
| **AİFD (Araştırmacı İlaç Firmaları Derneği)** | aifd.org.tr | Türkçe | Innovator pharma sektör perspektifi, yıllık değerlendirme raporları, market access pozisyonları |
| **TİSD (Türkiye İlaç Sanayicileri Derneği)** | tisd.org.tr | Türkçe | Yerli üretim odaklı sektör perspektifi, yerli sanayi verileri |
| **İEİS (Türkiye İlaç Endüstrisi İşverenler Sendikası)** | ieis.org.tr | Türkçe | Sektörel istihdam + üretim verisi |
| **KAP (Kamuyu Aydınlatma Platformu)** | kap.org.tr | Türkçe + İngilizce | BİST-listeli yerli pharma şirketleri için zorunlu disclosure (analog SEC EDGAR) |
| **Borsa İstanbul (BİST) ilaç şirketleri** | borsaistanbul.com | Türkçe + İngilizce | Yerli sponsor finansal bildirimleri |
| **TÜİK Sağlık İstatistikleri** | tuik.gov.tr | Türkçe + İngilizce | Sağlık harcamaları, demografik veriler, hastane istatistikleri |
| **Hastalık-spesifik Türk klinisyen dernekleri** (Türk Onkoloji Grubu, Türk Hematoloji Derneği, Türk Kardiyoloji Derneği, Türk Romatoloji Derneği, Türk Nöroloji Derneği, vb.) | sırasıyla turkonkoloji.org, thd.org.tr, tkd.org.tr, romatoloji.org, noroloji.org.tr, vb. | Türkçe (bazıları İngilizce) | Türk klinisyen perspektifi, derneğe özel kılavuzlar, registry datası |

**Authoritative hierarchy for Türkiye claims:**

1. TİTCK ruhsat duyurusu / KÜB / KT — primary regulatory
2. SGK SUT yürürlükte olan metni + Bedeli Ödenecek İlaçlar Listesi — primary reimbursement
3. Resmi Gazete'de yayımlanmış kararnameler — primary yasal dayanak
4. Sponsor Türkiye iletişim materyali (KAP disclosure for BİST-listeli) — primary sponsor-self-reported
5. AİFD / TİSD / İEİS sektör raporları — secondary aggregate
6. Akademik yayın (Türk dergileri + Türk merkezleri uluslararası yayınları) — secondary topic-specific
7. Sektör medya (PharmaTürkiye, Medimagazin, MedikalAkademi, Tıbbi Türkiye) — tertiary

---

## TİTCK Regulatuar Pathway

### Standart ruhsatlandırma yolu

TİTCK ruhsatlandırma süreci **Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği** çerçevesinde işler (R.G. 19.01.2005 ilk yayım, sonraki güncellemeler).

| Adım | Adı | Süre |
|---|---|---|
| 1 | Ruhsat başvurusu (CTD formatında dosya) | — |
| 2 | TİTCK formal kabul | 30-60 gün |
| 3 | Bilimsel değerlendirme (TİTCK iç komisyonu + dış uzman) | 6-12 ay (standart); 3-6 ay (hızlandırılmış) |
| 4 | Ruhsat onayı | — |
| 5 | KÜB / KT yayımı + fiyat başvurusu | onayı takip eden 30 gün |
| 6 | SGK geri ödeme başvurusu | ruhsat sonrası ayrı süreç |

### Hızlandırılmış pathway'ler

- **Reliance Pathway (ATÜB / EMA reliance):** EMA tarafından zaten onaylı ürünler için reliance prosedürü; başvuru süresi typically 4-6 ay
- **TR Reliance Yönetmeliği (2023+ genişletilmiş):** WHO prequalified, FDA, EMA, PMDA, MHRA, TGA, Health Canada, Swissmedic onaylı ürünler için kısaltılmış ruhsat yolu
- **Hızlı Erken Erişim Programı (HEEP):** Yaşamı tehdit eden ya da ciddi hastalıklar için, TİTCK izni ile ruhsat öncesi şahsi ithalat + hastane bazında compassionate use
- **Şahsi ithalat / İsimsel ithalat:** Ruhsat olmayan ürünlerin TİTCK iznini takiben hasta-bazında ithali; üçüncü kişi reçetesiyle

### Hassas ürün kategorileri için özel kurallar

- **Onkoloji ilaçları:** TİTCK Onkoloji Komisyonu tarafından özel değerlendirme; biyobenzer için ek immunogenicity verisi
- **Biyobenzer:** TİTCK Biyobenzer Yönergesi (EMA biyosimilar yönergesi ile uyumlu)
- **Pediatrik ilaçlar:** Pediatrik Araştırma Planı zorunluluğu (EMA PIP modeline benzer)
- **Yetim ilaçlar (orphan):** Ayrı yetim ilaç düzenlemesi yok; HEEP + isimsel ithalat sıkça kullanılır
- **Gen terapisi + ileri tedavi tıbbi ürünleri (ATMP):** EMA ATMP framework ile uyumlu yönerge; Türkiye'de henüz onaylı ATMP sınırlı

### TİTCK Komisyonu süreci

TİTCK Komisyonları konu-spesifik (Onkoloji, Romatoloji, Kardiyovasküler, Nöroloji, Endokrinoloji, vb.) işler. Sponsor bilimsel değerlendirme dosyasını sunar; tartışma + Q&A; karar üç şekilde olabilir: kabul, revize talebi, ret.

**Tipik defense dosyası bileşenleri** (TİTCK komisyon hazırlığı için):

1. **Bilimsel temellendirme:** Mekanizma + preklinik + klinik kanıt sentezi
2. **Pivotal kanıt:** RCT verisi, peer-reviewed yayın, registry data
3. **Karşılaştırmalı etkililik:** Existing standard of care vs proposed product
4. **Güvenlik profili:** AE rates, boxed warning değerlendirmesi, REMS ihtiyaç
5. **Türkiye-spesifik bağlam:** Türk popülasyonunda kanıt (varsa), Türkiye epidemiyolojisi
6. **Kalite verisi:** GMP belgesi, kararlılık, çok-merkez tutarlılık
7. **Etkililik-maliyet (HEOR):** Eğer payer perspektifi de dahil ediliyorsa

---

## SGK Geri Ödeme Pathway (SUT çerçevesi)

### Ana mekanizma

Sağlık Uygulama Tebliği (SUT) SGK tarafından yıllık olarak güncellenir; her güncelleme Resmi Gazete'de yayımlanır. SUT şunları kodlar:

- **Bedeli ödenecek ilaçlar listesi:** SGK'nın geri ödeme yaptığı tüm ilaçlar
- **Ek-4A:** Kamu sağlık kurumlarında ödenen ilaçlar (devlet hastaneleri, üniversite hastaneleri, eğitim ve araştırma hastaneleri)
- **Ek-4B:** İlaç firma indirimleri tablosu (zorunlu indirim oranları)
- **Ek-4C:** Özel sağlık kuruluşlarında ödenen ilaçlar
- **Ek-4D:** Bedeli ödenmek koşullarına bağlanmış ilaçlar (kullanım protokolüne tabi)
- **Reçete kuralları:** Hangi hekim, hangi tanı kodu (ICD-10), hangi tetkik şartı, hangi süre, hangi prior therapy

### Geri ödeme başvuru süreci

| Adım | Açıklama | Süre |
|---|---|---|
| 1 | TİTCK ruhsatı sonrası SGK'ya başvuru | — |
| 2 | SGK Komisyonu değerlendirme (klinik fayda + farmakoekonomik analiz + bütçe etkisi) | 6-18 ay (typical); bazı agresif vakalarda 3-6 ay |
| 3 | SUT güncellemesinde dahil edilme veya 3 ay geri çekme | — |
| 4 | Ek-4D protokol oluşturma (varsa) | komisyon kararı sonrası 3-6 ay |
| 5 | MEDULA reçete kuralı entegrasyonu | aktivasyondan önce |
| 6 | Hizmet etkin olma | SUT yayım tarihinden 1 ay sonra typical |

### Geri ödeme kategorileri

| Kategori | Mekanizma | Tipik kullanım |
|---|---|---|
| **Tam ödeme (Ek-4A)** | %100 SGK öder, hasta katkı payı yok | Çoğu temel ilaç, kronik hastalık ilaçları |
| **Katkı payı ile ödeme** | Hasta katkı payı %10-20; SGK kalanı öder | Bazı reçeteli ilaçlar |
| **Kullanım protokolü ile ödeme (Ek-4D)** | Belirli endikasyon + tanı kodu + tetkik + süre kısıtı | Yüksek maliyetli onkoloji + biyolojik ilaçlar |
| **İndirimli liste fiyatı (Ek-4B)** | Sponsor zorunlu indirim oranıyla geri öder | Yeni onaylı + yüksek maliyetli ilaçların çoğu |
| **Geri ödeme dışı** | SUT'ta yer almaz; tam self-pay | Ruhsatsız + onaylı ama listeye girmemiş ilaçlar |

### EK-4D Kullanım Protokolleri — anatomi

EK-4D, yüksek maliyetli ilaçlar için Türkiye'nin restrictive prescribing mekanizmasıdır. Tipik bir EK-4D protokolünün bileşenleri:

- **Endikasyon kapsamı:** Hangi ICD-10 kodu, hangi histolojik tip, hangi evre
- **Hasta kriterleri:** Yaş, performans durumu, organ fonksiyonu, prior therapy gereksinimleri
- **Biyomarker kriterleri:** PD-L1 ekspresyonu, mutasyon durumu, HER2 statüsü, vb. — biomarker test gereksinimleri
- **Hekim kriterleri:** Onkoloji uzmanı, hematoloji uzmanı, romatoloji uzmanı, vb.
- **Hastane kriterleri:** Üçüncü basamak hastane, üniversite hastanesi, vb.
- **Tetkik gereksinimleri:** Belirli görüntüleme, biyopsi, lab parametreleri
- **Süre kısıtları:** Maksimum tedavi süresi, response evaluation interval
- **Dur-kuralları:** Progression criteria, toxicity-driven discontinuation
- **Reçete renewal kuralları:** Her N ayda bir SUT komisyonu başvurusu
- **Hasta-başına maliyet üst sınırı:** Bazı protokollerde mevcut

### SUT denetim ve uyum

- **MEDULA** sistemi tüm reçeteleri otomatik olarak SUT kurallarına karşı denetler
- Kural-dışı reçeteler eczanenin SGK ödemesinden mahrum bırakılır
- Hekimin "off-label" reçete yazması mümkün ama SGK bunu ödemez
- SGK denetimleri retrospektif fault detection mekanizması ile çalışır

### SGK Komisyonu karar parametreleri

Türkiye'de NICE / G-BA gibi tek-bir-yıllık-pazarlık döngüsü yoktur — bunun yerine **rolling SGK Komisyonu kararları** ile her ürün için ayrı pazarlık yapılır. Komisyon değerlendirme parametreleri:

- **Klinik fayda:** Pivotal trial + Türkiye RWE
- **Karşılaştırmalı etkililik:** Mevcut SUT alternatiflerine kıyasla
- **Maliyet-etkililik:** Sponsor sunduğu farmakoekonomik dosya
- **Bütçe etkisi:** SGK toplam bütçesi üzerinde tahmin edilen etki
- **Uluslararası fiyat referansı:** 5-ülke baz; sponsor indirim teklifi
- **Kullanım protokolü kapsamı:** Restrictive prescribing kuralları, biomarker, ICD-10

### Sponsor stratejik seçenekler

1. **Tam liste fiyatı + tüm endikasyon** — düşük olasılık (yüksek maliyetli orijinatör için)
2. **İndirimli fiyat + tüm endikasyon** — typical karar
3. **Tam fiyat + restrictive Ek-4D protokol** — bazı durumlarda kabul edilir
4. **Hızlı onay + 2-3 yıl sonra renegotiation** — yeni-onaylı ürünler için
5. **HEEP / şahsi ithalat** — uzun süreli SGK pazarlık beklemesinde alternatif

---

## Türkiye Pricing & Reimbursement Mekanizması

### Referans fiyat sistemi

Türkiye'de ilaç fiyatlandırması **5 ülke referans sistemine** bağlıdır:
- Fransa
- İspanya
- İtalya
- Yunanistan
- Portekiz

İmalatçı fiyatı (depocu fiyatı), bu 5 ülkenin en düşük fabrika satış fiyatı baz alınarak belirlenir. Sponsor en düşük 5-ülke fiyatına eşit veya daha düşük teklif sunmak zorundadır.

### Fiyat zinciri

| Adım | Mark-up / İndirim |
|---|---|
| 1. Fabrika çıkış fiyatı (sponsor → depocu) | Referans baz |
| 2. Depocu marjı | %4-9 (ilaç bedeline göre azalan ölçek) |
| 3. Eczacı marjı | %12-25 (ilaç bedeline göre azalan ölçek) |
| 4. KDV (%8 ilaç ürünleri için) | %8 ekleme |
| 5. Sponsor zorunlu indirimi (Ek-4B) | %4-41 (orijinal vs jenerik vs kategorisine göre) |

Bu çok-katmanlı mark-up yapısı, fabrika fiyatı + son tüketici fiyatı arasında **2-2.5x fark** yaratabilir.

### TL paritesi etkisi

Türkiye'nin TL bazlı fiyatlandırması, döviz kuru oynaklığında reel fiyat erozyonuna yol açar. **TL deprecation periodlarında** sponsor fiyat artışı talep edebilir; ancak SGK fiyat artışlarını kısıtlar (yıllık 2 kez ayarlama; sınırlı yüzde). Bu yapı, multinational pharma için Türkiye operasyonunun **revenue erozyon riski** taşır.

### Yeni ürün fiyatlandırması

- **Yeni onaylı orijinal ürünler:** TİTCK fiyat onayı sonrası SGK pazarlığı; SGK %20-40 indirim talep eder typical
- **Yeni jenerik:** Originatör fiyatına göre %30-40 indirimli
- **Yeni biyobenzer:** Originatör fiyatına göre %25-35 indirimli (Türkiye biyobenzer pazarı hızla büyüyor)

---

## Reliance Pathway Türkiye (2023+)

2023 sonrasında genişletilmiş Reliance Pathway, EMA + FDA + diğer "stringent regulatory authority" onaylı ürünler için kısaltılmış TİTCK ruhsatlandırma sağlar.

### Eligibility

- WHO listed prequalified veya FDA + EMA + PMDA + MHRA + TGA + Health Canada + Swissmedic onaylı
- Aynı endikasyon + aynı popülasyon + aynı dozaj
- Türkiye-spesifik klinik araştırma şart değil (Türk popülasyon kanıtı bonus ama mandatory değil)

### Süreç

- Reliance dossier ile başvuru
- TİTCK doğrulama: Stringent authority kararı + uyum + Türkiye'ye uygunluk
- 4-6 ay tipik süre (vs standart 12 ay)

### Stratejik anlam

Reliance pathway, EMA / FDA-onaylı yeni moleküllerin Türkiye'ye **6-12 ay daha hızlı** giriş yapabilmesini sağlar. Launch sequencing + revenue acceleration + competitive lead time için materyal mekanizma.

---

## Türkiye RWE Altyapısı — discovery methodology

Türkiye, Türk hastalık-spesifik registries üzerinden global pivotal trial dışı RWE üretir. Bu registries Türk hekimlerin günlük klinik pratiğini reflect eder ve Türk hasta popülasyonunda gerçek-dünya outcome verisi üretir.

### Registry discovery yaklaşımı (sponsor- ve hastalık-agnostik)

Belirli bir terapötik alan için Türk registry varlığını araştırmak için aşağıdaki primary discovery sequence kullanılır:

1. **İlgili Türk uzmanlık derneği web sitesi** — örn: onkoloji için turkonkoloji.org, hematoloji için thd.org.tr, kardiyoloji için tkd.org.tr, nöroloji için noroloji.org.tr, romatoloji için romatoloji.org. Tam dernek listesi için TÜBA (Türkiye Bilimler Akademisi) ve Türk Tabipleri Birliği uzmanlık dernekleri kataloğu kullanılır.
2. **PubMed Türk merkezleri yayın taraması** — `(Turkey[Affiliation] OR Türk*[Affiliation]) AND <indication>` query'si Türk merkezleri yayınlarını yüzeye çıkarır; registry referansları yayın içinde dokümante edilir.
3. **Resmi Gazete + Sağlık Bakanlığı duyuruları** — kamu-fonlu registries (BAP, TÜSEB destekli) Resmi Gazete'de duyurulur.
4. **TİTCK Klinik Araştırmalar Daire Başkanlığı duyuruları** — observational study + non-interventional registry başvuruları kamuya açık registry'de listelenir.

### Türk registry tipolojisi

Türk RWE registries genellikle şu üç tipoloji altında dağılır:

- **Dernek-yürütücü registries** — uzmanlık derneği bir hastalık alanını sistematik takip eder; çok-merkez katılım; akademik publication-driven
- **Sponsor-fonlu observational study'ler** — multinational originatör'ün post-marketing efficacy / safety verisi için Türk merkezlerinde yürüttüğü; SGK geri ödeme dosyası destekleyici materyal
- **Devlet / TÜSEB destekli sağlık çıktı registries** — kamu sağlık sistemi-wide veri toplama; epidemiyoloji ve sağlık politikası odaklı

**Methodological caveat:** Bir terapötik alan için "Türk registry var mı?" sorusu her zaman live discovery gerektirir; sub-protocol bu sorunun cevabını önceden encode etmez. Önemli olanlar yıldan yıla evrilir; yeni registries başlatılır, eskiler kapanır veya akademik konsorsiyuma devredilir.

### Strateji açısı (sponsor-agnostic)

Yeni onaylı bir orijinatör için, Türkiye-spesifik RWE çalışması (Türk registry içinde) genellikle SGK geri ödeme başvuru dosyasının güçlü bir unsuru olur — local efficacy + safety verisi gösterir. Bu, Türkiye'de operasyon yürüten herhangi bir sponsor için (multinational veya yerli) geçerli bir genel bulgu'dur.

---

## Yerli Sponsor Pipeline Analysis — discovery methodology

Türk yerli ilaç firmaları geniş ve dinamik bir ekosistem oluşturur. Bu sub-protocol, **exhaustive sponsor listesi** sağlamak yerine **discovery + classification framework** sağlar; spesifik sponsor analizi her query için live primary source fetch gerektirir.

### Yerli sponsor sınıflandırma çerçevesi (genel)

Türk yerli pharma şirketleri analiz amacıyla aşağıdaki dimensional framework altında sınıflandırılır:

| Dimension | Kategoriler |
|---|---|
| **Public disclosure** | BİST-listeli (KAP zorunlu disclosure) / family-owned (sınırlı public disclosure) / özel sermaye-fonlu / academic spin-off |
| **Modality scope** | Multi-modality / jenerik-odaklı / biyobenzer-odaklı / specialty (örn: onkoloji odaklı) / CDMO (contract manufacturing) |
| **Sponsor scale** | Büyük (>$100M revenue) / mid-cap / niş / start-up |
| **Channel concentration** | Hastane kanalı dominant / retail eczane kanalı / kamu ihale dominant / ihracat dominant |
| **Innovation depth** | Pure jenerik / value-added formulation / biyosimilar / orijinal R&D |

### Yerli sponsor discovery sequence

Belirli bir Türk pharma sponsorunun analizi için primary discovery sequence:

1. **AİFD ve TİSD üye listeleri** — innovator-focused (AİFD) ve general industry (TİSD) sponsor kataloğu; sektörel pozisyonu hızlıca lokalize eder
2. **KAP disclosure sorgusu (BİST-listeli için)** — sponsor adıyla KAP'ta zorunlu finansal disclosure'lar, faaliyet raporları, özel durum açıklamaları
3. **Sponsor kurumsal web sitesi** — pipeline + ürün portföyü + ortaklıklar
4. **Türkiye İlaç Endüstrisi İşverenler Sendikası (İEİS)** — istihdam ve üretim verileri
5. **Resmi Gazete Ek-4B yayımları** — sponsor-spesifik zorunlu indirim oranları (originatör vs jenerik vs biyobenzer kategorisinin sponsor için pratik etkisi)
6. **Kamu ihale platformu (EKAP)** — kamu sağlık kuruluşları ihalelerindeki sponsor pozisyonu

### Yerli sponsor ekosisteminin sektörel dinamikleri (sponsor-agnostik)

- Jenerik + biyobenzer üretim Türkiye'de hızla büyüyor
- "Yerli Üretim" politikası kamu ihalelerinde yerli üretim öncelik mekanizması sağlıyor
- Multinational + yerli partnership modelleri (lisanslama, co-marketing, contract manufacturing) yaygın
- Yerli sponsorlar off-patent + biyobenzer pazarda multinational orijinatörlerle direkt rekabet
- TL paritesi erozyonu yerli üretim göreceli avantajı yaratabilir (import cost rising)

**Methodological caveat:** Türk pharma sektörü hızla evrim geçiriyor; M&A, yeni sponsor girişi, partnership değişiklikleri her yıl materyal. Spesifik sponsor profili için her zaman güncel KAP / sponsor IR / sektör derneği fetch'i zorunludur. Sub-protocol önceden hazırlanmış sponsor profilleri tutmaz.

---

## Türkiye İçin Hassas Stratejik Konular (sektör genelinde)

Bu konular, Türkiye-bazlı pharma executive tarafından sıklıkla sorulan ve pharmaintel'in adresleyebileceği soru tipleridir:

### Launch sequencing soruları

- "X molekülü EMA onayından kaç ay sonra TİTCK ruhsatı alır?"
- "Y reliance pathway eligibility'si var mı?"
- "Z için Türkiye launch'u global launch sequence'de hangi pozisyonda olur?"

### Reimbursement timing soruları

- "X için SGK Komisyonu kararı tahmini ne zaman?"
- "Y için Ek-4D kullanım protokolü pattern'i ne olabilir?"
- "Z için sponsor pazarlık stratejisi (tam fiyat vs indirimli vs restricted) ne olmalı?"

### Pricing soruları

- "X için 5-ülke referans fiyat hesaplaması ne sonuç verir?"
- "Y biyobenzer Türkiye fiyatı pazara ne etki yapar?"
- "Z için yıllık tedavi maliyeti TL bazında ne kadar?"

### Pipeline + competitive intelligence soruları

- "X terapötik alanında Türkiye'de aktif olan tüm sponsorlar (multinational + yerli)?"
- "Y indikasyon için Türkiye geri ödenen alternatifler?"
- "Z'nin Türkiye'deki en yakın rakipleri (yerli + multinational) hangileri?"

### Yerli sponsor analizi

- "X yerli sponsor pipeline'ı?"
- "Y Türk biyobenzer pazarı (rekabet, fiyat, üretim)?"
- "Z için lisanslama partner aday'ları (Türk yerli)?"

### Defense + medical affairs soruları

- "X için TİTCK Komisyonu defense dosyası içeriği ne olmalı?"
- "Y için Türkiye RWE çalışma stratejisi?"
- "Z için Türk KOL haritası?"

---

## Output template (when Türkiye layer included in larger report)

```markdown
### Türkiye (TİTCK + SGK) regulatuar ve geri ödeme statüsü

> Agency: TİTCK + SGK · Karar tarihi: YYYY-MM-DD · Confidence: [H/M/L]
> Source: TİTCK ruhsat duyurusu / KÜB — URL
> SGK statüsü: [Ek-4A tam ödeme / Ek-4D kullanım protokolü / Liste dışı / Henüz başvuru aşamasında]

- **Ürün adı:** [marka, INN]
- **Ruhsat sahibi:** [MAH şirket adı]
- **Ruhsat numarası:** [TR ruhsat no]
- **Onay tarihi:** YYYY-MM-DD
- **Onay yolu:** [Standart / Reliance pathway / HEEP / Şahsi ithalat]
- **Endikasyon (KÜB'e göre):** [tam KÜB endikasyon metni]
- **SGK statüsü:** [kategori + EK-4D kapsam varsa açıklama]
- **EK-4D protokol özeti (varsa):** [endikasyon kapsamı, biomarker, hekim/hastane kriteri, süre kısıtı]
- **Liste fiyatı:** [TL bazında; KDV dahil son tüketici]
- **5-ülke referans:** [hangi ülke baz alındı]
- **Sponsor zorunlu indirimi (EK-4B):** [%]
- **Türk klinik araştırma site katılımı:** [pivotal trial'lerde Türkiye var mı; varsa hangi merkezler]
- **Türkiye RWE varlığı:** [registry datası varsa]

[If sources are mixed-language, explicit §Translation notes paragraph follows:]

> **Çeviri notu:** Türkçe regulatuar ifadelerin İngilizce karşılıkları için [spesifik terimler] kullanıldı. Off-label kullanım veya nüanslı ifadeler için yerel regulatuar uzman görüşü önerilir.
```

---

## Known gaps and limitations

1. **MEDULA erişim sınırlı:** Real-time reçete kuralları + e-reçete operasyonel detayı kullanıcı-başvurulu erişim gerektirir; pharmaintel free-tier bu detaya doğrudan erişemez.
2. **SGK Komisyonu kararları opak:** Komisyonun spesifik karar gerekçeleri kamuya açık değildir; sadece sonuç (SUT'ta listeleme veya listelenmeme) gözlenir.
3. **Yerli sponsor disclosure asimetrisi:** BİST-listeli yerli sponsorlar KAP üzerinden zorunlu disclosure yaparken, family-owned büyük yerli sponsorlar (Abdi İbrahim, Bilim İlaç gibi) için public disclosure çok sınırlıdır.
4. **Provincial / regional varyans:** Türkiye'de provincial reimbursement varyansı yoktur (SGK ulusal); ancak hastane-bazlı protokol farklılıkları (özellikle özel hastaneler için) olabilir.
5. **Türkçe regulatuar terminoloji nüansları:** Bazı terimler (örn: "kullanım protokolü", "geri ödeme dışı", "off-label") İngilizce karşılıklarıyla tam örtüşmez; çeviri yapılırken nüans korunmalı.
6. **TL fiyatlandırma snapshot eskime hızı:** TL deprecation periodlarında fiyat verileri haftalık eskir; rapor data cutoff tarihi bu açıdan kritiktir.
7. **Türk klinik araştırma site katılım datası ClinicalTrials.gov'da:** Türk merkezleri pivotal global çalışmalara nadir-orta sıklıkta katılır; site katılım listesi kontrol edilmeden Türkiye-bağlam çıkarımı yapılmamalı (geography verification guard tetiklenmeli — bkz. triangulation.md §10).
8. **Sub-protocol bilingual interpreter substitute değildir:** Yüksek-stake regulatuar / reimbursement kararları için Türk ruhsatlandırma + market access uzmanı görüşü zorunludur.

---

## Cross-reference

- `sources-catalog.md §Türkiye sources` — URL kataloğu
- `triangulation.md §10` — Geography Verification Guard (Türk merkezi pivotal trial katılım doğrulama)
- `task-asset.md §Regional regulatory layer` — asset-level integration point
- `task-modality.md §8.7 Launch sequence` — Türkiye launch timing dahil
- `task-catalyst.md` — TİTCK / SGK kararları catalyst olarak
- `task-hta.md` — SGK SUT framework HTA logic'in Türk paralelidir; doğrudan tercüme edilemez ama paralel mantık kullanılır
- `sub-protocol-pmda.md`, `sub-protocol-nmpa.md` — diğer regional regulatory sub-protocol'leri; aynı translation-fidelity discipline uygular

**When to load this sub-protocol:** SKILL.md Step 1g (semantic auto-trigger) detects "Türkiye operasyon analizi", "TİTCK", "SGK", "SUT", "yerli pharma sponsor", "Türk RWE" content veya explicit Türkiye layer talebi → loads `sub-protocol-turkey.md` in parallel with task-specific reference. Bu opt-in bir layer'dır; default global scope korunur.
