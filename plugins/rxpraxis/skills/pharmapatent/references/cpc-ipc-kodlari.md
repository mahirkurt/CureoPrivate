# references/cpc-ipc-kodlari.md — Farmasötik ve Tıbbi Cihaz CPC/IPC Taksonomisi

> İlaç ve tıbbi cihaz patent araştırmalarında taksonomik kilitlerin doğru seçimi, aramanın verimliliğini belirleyen tek en önemli değişkendir. Anahtar kelime ile yakalanamayan patentler, doğru sınıfta kesinlikle yakalanır.

## İlişkili Protokoller

- **`markush-protokol.md`** — C07D (heterosiklik), C07K (peptid), C07H (karbonhidrat) altındaki Markush yoğun istemlerin kimyasal topoloji analizi
- **`veritabani-stratejileri.md`** — CPC kodlarının USPTO `.CPC.` / Espacenet `cpc=` / PATENTSCOPE Boolean sorgusuna dönüşümü
- **`fto-invalidity-protokol.md` §1 Adım 4-5 + §2 Adım 4** — CPC kilit listesi çıkarma ve sınıf tabanlı patent taraması iş akışı
- **`tibbi-cihaz-uts.md`** — A61M/A61B/G16H kodlarının tıbbi cihaz ve SaMD sınıflandırmasıyla kesişimi

## İçindekiler

1. IPC ve CPC arasındaki temel farklar
2. A61K — Tıbbi, dişçilik ve tuvalet preparatları (en kritik ağaç)
3. A61M — Vücuda ilaç/sıvı/gaz uygulama cihazları
4. A61B — Teşhis, cerrahi, tanımlama
5. A61P — Kimyasal bileşiklerin terapötik aktiviteye göre sınıflandırılması
6. B01D — Ayırma prosesleri (saflaştırma)
7. C07 ağacı — Organik kimya (C07D heterosiklik, C07K peptid)
8. C12N — Mikroorganizmalar ve enzimler, genetik mühendislik
9. G16H — Sağlık bilişimi (yapay zeka teşhis sistemleri)
10. TÜRKPATENT 2024 Nice güncellemesi ile etkileşim
11. CPC tabanlı Boolean sorgu örnekleri
12. Sık düşülen taksonomik hatalar

---

## 1. IPC ve CPC arasındaki temel farklar

**IPC (International Patent Classification)** — WIPO tarafından yönetilir, tüm WTO üyesi ülkelerde zorunlu olarak uygulanır. Yaklaşık 72.000 alt-grup. Yıllık güncellenir; 2024 sürümü geçerlidir. Hiyerarşi: **Bölüm → Sınıf → Alt-sınıf → Grup → Alt-grup**. Örnek: `A` (İnsan ihtiyaçları) → `A61` (Tıp / Veterinerlik / Hijyen) → `A61K` (Preparatlar) → `A61K 31/00` (Organik aktif maddeler içeren) → `A61K 31/4985` (Spesifik heterosiklik bileşik alt dalı).

**CPC (Cooperative Patent Classification)** — USPTO + EPO ortaklığı ile geliştirilen genişletilmiş sistem. Yaklaşık 260.000 kod — IPC'nin ~3,6 katı granülerlik. Çin SIPO, Kore KIPO, Rusya Rospatent, Meksika IMPI ve diğerleri tarafından da benimsenir. Her patente birden fazla CPC kodu atanabildiği için "çoklu etiketleme" radarı oluşturur; aynı patent hem `A61K 9/7015` (cilt yapıştırıcısı) hem `A61M 5/145` (pompalı uygulama) hem `A61K 31/4985` (heterosiklik aktif) kodlarını taşıyabilir.

**Türkiye durumu**: TÜRKPATENT hem IPC hem CPC atar (CPC atama 2015 sonrası tutarlı). EPAAT üzerinden her iki kod ile sorgu mümkündür; CPC genellikle daha spesifik sonuç verir.

**Pratik kural**: FTO ve invalidity aramalarında önce CPC ile sorgu; Türkiye-spesifik yerel başvurular için IPC doğrulama.

---

## 2. A61K — Tıbbi, dişçilik, tuvalet preparatları

A61K, farmasötik patent dünyasının **en merkezi sınıfıdır**. Tüm formülasyon, dozaj formu, uygulama yolu patentlerinin birinci kodu burada yer alır.

### A61K ana alt-sınıfları

| Kod | Konu |
|---|---|
| A61K 6/00 | Diş hekimliği preparatları |
| A61K 8/00 | Tuvalet/kozmetik preparatları |
| A61K 9/00 | **Dozaj formları** (çok kritik) |
| A61K 31/00 | **Organik aktif bileşenler** (küçük molekül) |
| A61K 33/00 | İnorganik aktif bileşenler |
| A61K 35/00 | Belirlenmemiş yapılı ajanlar (hücre/doku/organ) |
| A61K 36/00 | Bitkisel ajanlar |
| A61K 38/00 | **Peptidler, proteinler, antikorlar** |
| A61K 39/00 | **Antijenler / aşılar / immünoglobulinler** |
| A61K 41/00 | Radyasyonla aktive ajanlar |
| A61K 45/00 | Aktif olmayan taşıyıcı içeren bileşimler |
| A61K 47/00 | Aktif olmayan yardımcı maddeler (eksipiyanlar) |
| A61K 48/00 | **Gen terapi preparatları** (DNA/RNA) |
| A61K 49/00 | Görüntüleme için preparatlar (kontrast ajanları) |
| A61K 51/00 | Radyoaktif preparatlar (radyoilaçlar) |

### A61K 9 — Dozaj formları ağacı (çok yaygın sorgulanır)

| Kod | Konu |
|---|---|
| A61K 9/00 | Tıbbi preparatlar, özel fiziki formdaki |
| A61K 9/06 | Merhem, pomat, krem, jel |
| A61K 9/08 | Solüsyonlar |
| A61K 9/10 | Süspansiyonlar, emülsiyonlar |
| A61K 9/12 | Aerosoller, spreyler |
| A61K 9/14 | Partiküler form (ör. powder) |
| A61K 9/16 | Granüller |
| A61K 9/20 | **Tabletler** |
| A61K 9/22 | Uzatılmış salınım formları (genel) |
| A61K 9/24 | Çok-katmanlı tabletler |
| A61K 9/28 | Kaplanmış tabletler |
| A61K 9/48 | Yumuşak jelatin kapsüller |
| A61K 9/50 | **Mikrokapsül / nanopartikül** — modern iletim sistemlerinin kalbi |
| A61K 9/51 | **Nanopartiküller** (<1000 nm) |
| A61K 9/5115 | Polimerik nanopartiküller |
| A61K 9/5123 | Lipid nanopartikülleri (LNP) — mRNA aşı vektörleri |
| A61K 9/70 | Transdermal yamalar |
| A61K 9/7015 | Cilt adezifleri |
| A61K 9/7023 | Reservuar sistemli yama |

### A61K 31 — Organik aktif bileşenler

Bu alt-sınıf, tüm küçük molekül ilaçların patent kodudur. 2000+ alt-alt kod içerir. En çok sorgulananlar:

| Kod | Konu | Örnek ilaç grubu |
|---|---|---|
| A61K 31/13 | Aminler (aromatik olmayan) | Amfetaminler |
| A61K 31/165 | Karboksamidler | Parasetamol |
| A61K 31/185 | Karboksilik asit ve türevleri | NSAID'ler |
| A61K 31/192 | Fenilasetik asitler | İbuprofen, diklofenak |
| A61K 31/40 | Pirrol halkası içerenler | Atorvastatin |
| A61K 31/404 | İndoller | SSRI grubu |
| A61K 31/415 | 1,2-diazoller (pirazol) | Selekoksib |
| A61K 31/4184 | Bisimidazoller (örn. astım) | — |
| A61K 31/4439 | Pirimidin + heteroaril | Imatinib benzeri |
| A61K 31/4468 | Piperidinler | Risperidon, fentanil |
| A61K 31/47 | Kinolinler | Florokinolonlar |
| A61K 31/498 | Pirazinler | — |
| A61K 31/4985 | Pirazinler + diğer heterosiklik | Moderne kinaz inhibitörleri |
| A61K 31/506 | Pirimidinler + halkalı aminler | Imatinib, kinaz inhibitörleri |
| A61K 31/519 | Pürinler + halka füzyonu | Abakavir, fludarabin |
| A61K 31/52 | Pürin türevleri | — |
| A61K 31/53 | 1,2,4-Triazinler | — |
| A61K 31/5375 | Nonaromatik halkalar | Rapamisin türevleri |
| A61K 31/55 | Yedi üyeli halkalar | — |
| A61K 31/704 | Şekerler + steroidal | Digoksin, glikozidler |
| A61K 31/7088 | Nükleik asitler (RNA/DNA'nın alt parçaları) | — |

### A61K 38 — Peptidler, proteinler, antikorlar

Biyolojik ilaçların kalbi:

| Kod | Konu |
|---|---|
| A61K 38/02 | Peptidler (genel) |
| A61K 38/08 | 5–11 amino asitli peptidler |
| A61K 38/14 | Glikopeptidler (ör. vankomisin) |
| A61K 38/17 | 20'den fazla amino asitli proteinler |
| A61K 38/18 | Büyüme faktörleri |
| A61K 38/19 | Sitokinler (TNF, IFN, IL) |
| A61K 38/21 | İnterferonlar |
| A61K 38/22 | Hormonlar (insülin dahil) |
| A61K 38/27 | Büyüme hormonu |
| A61K 38/28 | İnsülin |
| A61K 38/36 | Koagülasyon faktörleri |
| A61K 38/48 | **Enzim prepararatları** (ör. streptokinaz) |
| A61K 39/395 | **Monoklonal antikorlar** (MAbs) — çok kritik |
| A61K 39/3955 | Anti-kanser antikor-ilaç konjugatları (**ADC**) |

### A61K 48 — Gen terapi (modern modaliteler)

| Kod | Konu |
|---|---|
| A61K 48/00 | Genetik materyalin terapötik kullanımı (genel) |
| A61K 48/005 | Plazmid DNA + doğrudan verme |
| A61K 48/0058 | AAV vektörleri |
| A61K 48/0066 | Retroviral vektörler |
| A61K 48/0075 | Aktive lenfositler (CAR-T kapsamı için) |

---

## 3. A61M — Vücuda ilaç/sıvı/gaz uygulama cihazları

Kombinasyon ürünler (ilaç + cihaz) için A61K ile birlikte çift kodlama yapılır.

| Kod | Konu |
|---|---|
| A61M 1/00 | Vücut sıvılarının emilmesi (ör. diyaliz pompaları) |
| A61M 5/00 | Enjeksiyon cihazları genel |
| A61M 5/142 | Infüzyon pompaları |
| A61M 5/145 | Pompalı uygulama (ör. insülin pompası) |
| A61M 5/158 | **Prefilled syringe / otomatik enjektörler** |
| A61M 5/20 | **Otomatik enjektörler** (EpiPen vs.) |
| A61M 5/24 | İğnesiz enjeksiyon |
| A61M 5/315 | Dozaj ayarlanabilir kalemler (insülin kalemleri) |
| A61M 11/00 | Nebulizer'lar |
| A61M 15/00 | **İnhalerler genel** |
| A61M 15/0003 | Toz inhalerleri (DPI) |
| A61M 15/0065 | Ölçülü dozaj inhalerleri (MDI) |
| A61M 15/0091 | Nefes-aktive inhalerler |
| A61M 16/00 | Solunum sistemleri (anestezi, ventilatör) |
| A61M 25/00 | Kateterler |
| A61M 37/00 | Transdermal uygulama |
| A61M 39/00 | Enjeksiyon portları |

---

## 4. A61B — Teşhis, cerrahi, tanımlama

| Kod | Konu |
|---|---|
| A61B 1/00 | Vücut içi görsel muayene cihazları (endoskoplar) |
| A61B 3/00 | Göz muayene aletleri |
| A61B 5/00 | Teşhis amaçlı ölçüm (EKG, tansiyon, glikoz sensörleri) |
| A61B 5/1473 | Sürekli glukoz monitörleri (CGM) |
| A61B 6/00 | Radyoloji cihazları |
| A61B 8/00 | Ultrason cihazları |
| A61B 17/00 | Cerrahi aletler |
| A61B 18/00 | Elektrocerrahi, lazer |
| A61B 34/00 | **Cerrahi robotlar** (2024 Nice 09. sınıf AI robotu ile kesişir) |
| A61B 90/00 | Cerrahi yardımcı cihazlar |

---

## 5. A61P — Terapötik aktiviteye göre sınıflandırma (ikincil kod)

A61P her zaman A61K ile birlikte atanır; hangi hastalıkta kullanıldığını işaretler.

| Kod | Hastalık alanı |
|---|---|
| A61P 1/00 | Sindirim sistemi |
| A61P 3/00 | Metabolizma (diyabet, obezite) |
| A61P 3/10 | Hiperglisemi / diyabet |
| A61P 5/00 | Endokrin sistem |
| A61P 7/00 | Kan hastalıkları |
| A61P 9/00 | Kardiyovasküler |
| A61P 11/00 | Solunum sistemi |
| A61P 13/00 | Üriner sistem |
| A61P 15/00 | Kadın hastalıkları, doğum kontrolü |
| A61P 17/00 | Dermatolojik |
| A61P 19/00 | İskelet hastalıkları (osteoporoz, artrit) |
| A61P 21/00 | Kas hastalıkları |
| A61P 25/00 | Sinir sistemi (MS, Alzheimer, depresyon) |
| A61P 27/00 | Duyu organları (göz, kulak) |
| A61P 29/00 | Anti-inflamatuar / anti-alerjik |
| A61P 31/00 | Enfeksiyonlar |
| A61P 33/00 | Parazit enfeksiyonları |
| A61P 35/00 | **Anti-neoplastik** (onkoloji) |
| A61P 35/02 | Hematolojik kanserler |
| A61P 37/00 | İmmünomodülatörler (immünosüpresan + immünostimulan) |
| A61P 43/00 | Belirsiz / hedeflenmemiş tedavi amaçlı |

---

## 6. B01D — Ayırma (saflaştırma) prosesleri

Farmasötik üretim usullerinin saflaştırma basamakları:

| Kod | Konu |
|---|---|
| B01D 15/00 | Kromatografi genel |
| B01D 15/08 | Kolon kromatografisi |
| B01D 15/36 | Afinite kromatografisi (protein saflaştırma) |
| B01D 57/00 | Ayırma için elektrik alanları |
| B01D 61/00 | Membran filtrasyonu |
| B01D 61/14 | Ultrafiltrasyon |

---

## 7. C07 — Organik kimya

Küçük molekül sentezi ve yeni kimyasal varlıklar (NCE) patenti.

| Kod | Konu |
|---|---|
| C07C | Asiklik ve karbosiklik bileşikler |
| C07D | **Heterosiklik bileşikler** (küçük moleküllerin çoğu burada) |
| C07D 207 | 5-üyeli halkada bir N (pirrol, pirrolin) |
| C07D 209 | İndol türevleri |
| C07D 211 | Piperidin |
| C07D 213 | Piridin |
| C07D 249 | 1,2,3-Triazoller |
| C07D 403 | 2 ayrı heterosiklik halka içeren füzyon |
| C07D 471 | Halka füzyonlu heterosiklikler |
| C07D 487 | Peri-fused heterosiklikler |
| C07D 519 | Halka füzyonu çok-heterosiklik |
| C07K | Peptidler |
| C07K 16/00 | İmmünoglobulinler (antikorlar) |
| C07K 16/28 | Hayvansal hücreler için antikorlar (anti-CD, anti-HER2 vb.) |
| C07K 16/30 | Tümör hücrelerine karşı antikorlar |
| C07K 19/00 | Hibrid peptidler |

**Pratik not**: Yeni bir NCE için C07 ve A61K birlikte atanır; C07 molekülün kimyasal kimliğini, A61K tıbbi kullanımını belirtir.

---

## 8. C12N — Mikroorganizmalar, enzimler, genetik mühendislik

| Kod | Konu |
|---|---|
| C12N 5/00 | Hücre kültürü, doku |
| C12N 5/0783 | T hücreleri (CAR-T için) |
| C12N 5/0786 | Diğer lökositler |
| C12N 7/00 | Virüsler |
| C12N 7/04 | İnaktive edilmiş virüsler (aşı adayları) |
| C12N 9/00 | Enzimler |
| C12N 15/00 | **Genetik mühendislik — rekombinant DNA** |
| C12N 15/09 | DNA/RNA rekombinantları |
| C12N 15/113 | Antisens / siRNA / shRNA |
| C12N 15/85 | Memeli hücrelerde ifade vektörleri |
| C12N 15/86 | Viral vektörler |

---

## 9. G16H — Sağlık bilişimi / yapay zeka teşhis

2024 Nice güncellemesiyle birleşik öneme sahip:

| Kod | Konu |
|---|---|
| G16H 10/00 | Veri tabanı tasarımı - sağlık |
| G16H 20/00 | Klinik karar destek |
| G16H 30/00 | **Teşhis için görüntü analizi** (AI teşhis) |
| G16H 50/00 | Sağlık predictive analytics |
| G16H 50/20 | Makine öğrenmesi tabanlı teşhis |
| G16H 50/70 | Riski tahmin (önerme modelleri) |

**Pratik not**: Yapay zeka teşhis cihazı için G16H + A61B + 2024 Nice Sınıf 09 (yapay zekalı insansı robotlar) üçlü entegre tescil stratejisi düşünülür.

---

## 10. TÜRKPATENT 2024 Nice güncellemesi — marka sınıflandırma etkileşimi

CPC **patent** sınıflandırmasıdır; Nice ise **marka** sınıflandırması. Farmasötik ürünlerde ikisi paralel çalışır.

2024 itibariyle TÜRKPATENT Nice güncellemeleri:

- **09. sınıf** — Yapay zekalı insansı robotlar, güvenlik ve laboratuvar robotları yeni alt sınıfa ayrıldı. Cerrahi robotlar (A61B 34/00 CPC'si) + AI teşhis yazılımı (G16H CPC'si) artık bu marka sınıfında korunur.
- **39. sınıf** — Sağlık turizmi kapsamında ulaşım ve konaklama ayarlanması hizmetleri eklendi.
- **44. sınıf** — Diş hekimliği hizmetleri ve psikologlara ait hizmetler 44/01 alt sınıfına spesifik olarak eklendi.

**Stratejik önem**: Bir farmasötik firma hem patent (CPC) hem marka (Nice) tescili alır. Yapay zeka teşhis cihazı patenti G16H 50/20 ile korunurken; ürünün markası 09. sınıf yeni alt-sınıfta korunur. Entegre IP portföyü için ikili takip.

---

## 11. CPC tabanlı Boolean sorgu örnekleri

### Örnek 1: Atorvastatin formülasyon FTO taraması

```
USPTO Patent Public Search:
CPC/A61K 31/40 AND CPC/A61K 9/20 AND (atorvastatin OR "4-fluorophenyl")

Espacenet:
cpc=A61K31/40 AND cpc=A61K9/20 AND pa=atorvastatin
```

### Örnek 2: mRNA-LNP aşı landscape

```
USPTO:
(CPC/A61K 39/00 OR CPC/A61K 48/00) AND CPC/A61K 9/5123 AND (mRNA OR "messenger RNA")

Espacenet:
cpc=A61K39/00 AND cpc=A61K9/5123 AND (txt=mRNA OR txt="messenger RNA")
```

### Örnek 3: Anti-HER2 ADC invalidity prior art

```
USPTO:
CPC/A61K 39/3955 AND CPC/C07K 16/32 AND CPC/A61P 35/00 AND (trastuzumab OR HER2 OR ErbB2)

Espacenet:
cpc=A61K39/3955 AND cpc=C07K16/32 AND (txt=trastuzumab OR txt=HER2)
```

### Örnek 4: İnhaler + kortikosteroid kombinasyon FTO

```
USPTO:
CPC/A61K 9/0073 AND CPC/A61M 15/0065 AND CPC/A61K 31/573

Espacenet:
cpc=A61K9/0073 AND cpc=A61M15/0065 AND cpc=A61K31/573
```

### Örnek 5: CAR-T landscape

```
USPTO:
CPC/C12N 5/0783 AND CPC/C07K 19/00 AND CPC/A61K 39/00

Espacenet:
cpc=C12N5/0783 AND cpc=C07K19/00 AND cpc=A61K39/00
```

---

## 12. Sık düşülen taksonomik hatalar

**Hata 1**: A61K 31/00 tek başına sorgulama yapmak. Bu kod çok geniş (yaklaşık 5 milyon kayıt); mutlaka alt-alt koda (örn. A61K 31/506 gibi) kadar indir.

**Hata 2**: Yalnız A61K sorgulamak. Sadece preparatı arar; aktif madde kimyasal yapısı için C07D, biyolojikler için C07K gerekir. Bir ilaç patenti ortalama 3-4 CPC kodu taşır; hepsini birlikte sorgulamak önerilir.

**Hata 3**: Cihaz kombinasyonunda A61M'yi atlamak. Modern preparatlar (prefilled, inhaler, auto-injector) A61M olmaksızın eksik haritalanır. Inhaler kortikosteroidler için A61K 9/0073 (inhalasyon için) + A61M 15/* çift sorgu yapılır.

**Hata 4**: A61P kodunu atlamak. Endikasyon-bazlı sorgulamada A61P, kullanım alanını daraltır ve ikinci tıbbi kullanım patentlerinin bulunmasında kritiktir.

**Hata 5**: IPC eski versiyonunda takılı kalmak. 2024 güncel IPC ve CPC kullanılmalıdır; özellikle mRNA-LNP (A61K 9/5123) ve yapay zeka teşhis (G16H) için son 5 yılda eklenen kodlar kritik.

**Hata 6**: TÜRKPATENT EPAAT'ta CPC aramadığını varsaymak. EPAAT hem IPC hem CPC destekler; ancak arayüz bazen IPC'yi varsayılan gösterir. CPC seçeneği manuel olarak açılmalıdır.

**Hata 7**: USPTO'da `.CPC.` saha kodunu unutarak açık metin sorgulamak. `CPC/A61K31/40` doğru sözdizimidir; yalnız `A61K31/40` yazmak metinde geçen terimi arar, kod eşleştirmesi yapmaz.

---

*Bu doküman; tam alt-kodlar için güncel CPC şemasını (https://www.cooperativepatentclassification.org/) ve TÜRKPATENT 2024 Nice güncellemesini (https://www.turkpatent.gov.tr/) referans alır. Yeni kodlar her 6 ayda bir eklenir; yıllık teyit önerilir.*
