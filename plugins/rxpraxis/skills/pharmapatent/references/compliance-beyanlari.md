# references/compliance-beyanlari.md — Farmasötik Raporlarda Zorunlu Compliance Beyanları

> Farmasötik sektörde her rapor, **birden fazla compliance rejiminin kesişiminde** bulunur. GPP3 (Good Publication Practice) medical affairs yayınları, MDR/IVDR tıbbi cihaz bağlantılı raporlar, KVKK kişisel/sağlık verisi işlemleri, avukat-müvekkil ayrıcalığı hukuki çalışma ürünleri, GDPR AB faaliyetleri, GCP klinik veri kullanımı — bu rejimlerin her biri farklı beyan gerektirir. Bu protokol, her rapor tipi için **zorunlu beyan setini** standartlaştırır, ihlal risklerini tanımlar ve her compliance kategorisi için hazır şablon metinler sunar.

## İlişkili Protokoller

- **`rapor-sablonlari.md`** — Her rapor şablonunun footer'ına eklenecek compliance beyanları bu protokolde tanımlı
- **`gorsel-standartlari.md`** — Görsel compliance (kaynak atıf + disclaimer mini-footer)
- **`ictihat-emsal.md`** — Yargıtay kararlarında avukat-müvekkil ayrıcalığı emsalleri
- **`tibbi-cihaz-uts.md`** — MDR/IVDR uyumlu raporlar

## İçindekiler

1. Compliance rejimleri genel haritası
2. GPP3 (Good Publication Practice) — medical affairs
3. MDR/IVDR — tıbbi cihaz bağlantılı raporlar
4. KVKK — kişisel/sağlık verisi
5. GDPR — AB operasyonları
6. Avukat-müvekkil ayrıcalığı + work product doctrine
7. GCP (Good Clinical Practice) — klinik veri kullanımı
8. FCPA / UK Bribery Act / Türkiye 5607 — kamu görevlisi etkileşimi
9. Çıkar çatışması beyanları
10. Rapor-tip × compliance beyan matrisi
11. Hazır şablon metinler

---

## 1. Compliance rejimleri genel haritası

### Rejim × rapor tipi kesişim

| Rejim | FTO | Invalidity | Landscape | Lifecycle | Regulatory | Litigation | DD | Opposition | Biosimilar |
|---|---|---|---|---|---|---|---|---|---|
| GPP3 | — | — | O | — | — | — | — | — | O |
| MDR/IVDR | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| KVKK | O | O | — | — | ✓ | ✓ | ✓ | — | ✓ |
| GDPR | O | O | — | — | ✓ | ✓ | ✓ | — | ✓ |
| Avukat-müvekkil | ✓ | ✓ | O | O | O | ✓ | ✓ | ✓ | O |
| GCP | — | O | — | — | ✓ | — | O | — | ✓ |
| FCPA / 5607 | — | — | — | — | ✓ | ✓ | ✓ | — | ✓ |

*✓ = Zorunlu beyan; O = Opsiyonel ama önerilen*

### Compliance-first tasarım prensibi

Rapor yazılırken, zorunlu beyanlar **template düzeyinde** eklenmeli — "sonradan ekleyelim" yaklaşımı ihlal riski doğurur. Her rapor şablonunun footer'ı compliance blok'unu içerir.

---

## 2. GPP3 (Good Publication Practice)

### GPP3 nedir?

**Good Publication Practice for Communicating Company-Sponsored Medical Research** — 3. baskı (2015, güncelleme 2022).

**Ne zaman uygulanır**:
- Medical affairs yayınları
- Industry-sponsored klinik araştırma raporları
- Congress sunumları, poster, abstract
- KOL işbirliği yayınları

### Temel ilkeler

1. **Yazarlık kriterleri** (ICMJE uyumlu)
   - Substantive contribution to design/analysis
   - Drafting/critical revision
   - Final approval
   - Accountability

2. **Ghost authorship yasaktır** — medical writer olarak katkıda bulunanlar "acknowledgment" bölümünde ifşa edilmeli

3. **Çıkar beyanı** — her yazar + medical writer

4. **Sponsorluk açık** — pharma sponsorluğu saklanamaz

5. **Veri erişimi** — yazarların tam veriye erişim hakkı

### pharmapatent için uygulama

Bir **Landscape Raporu** (§3) veya **Biosimilar Pathway Briefing** (§9) bir yayına / konferansa dönüştürülecekse:

```
## GPP3 Uyum Beyanı

Bu doküman [Firma] medical affairs ekibi ve [dış patent hukuku firması] 
arasında ortak çalışma ürünüdür. Yayın formatına dönüştürülmesi durumunda 
GPP3 kriterleri uygulanır:

- Tüm katkı sağlayanlar ya yazar ya da acknowledgment olarak ifşa edilir
- [Firma] sponsorluğu açıkça belirtilir
- Yazarlar tam veriye erişime sahiptir
- Tüm yazarlar makalenin nihai halini onaylamıştır
```

### Hazır beyan metni (rapor footer)

> **GPP3 Beyanı**: Bu doküman sponsoralanmış bir çalışma raporu değildir; [Firma] IP stratejisi için iç kullanım hazırlandı. Yayına dönüştürülmesi durumunda GPP3 kriterleri (ICMJE yazarlık + ghost authorship yasağı + tam veri erişimi + çıkar beyanı) zorunlu uygulanacaktır.

---

## 3. MDR / IVDR — Tıbbi Cihaz Bağlantılı Raporlar

### Regülatör çerçevesi

- **MDR (EU 2017/745)** — tıbbi cihazlar, tam yürürlük 26.05.2021
- **IVDR (EU 2017/746)** — in vitro tanı cihazları
- **Türkiye Tıbbi Cihaz Yönetmeliği (2021)** — MDR uyumlu

### Ne zaman uygulanır

- Kombinasyon ürünler (ilaç + cihaz)
- SaMD (Software as Medical Device)
- Yapay zeka diagnostik cihazları
- ADC, CAR-T ile ilgili cihaz bileşenleri
- Prefilled syringe, oto-enjektör, inhaler patent raporları

### Beyan gereklilikleri

1. **Cihaz sınıflandırma atıfı** — raporda Sınıf I/IIa/IIb/III açıkça belirtilir
2. **Klinik değerlendirme durumu** — CER (Clinical Evaluation Report) mevcut / bekleniyor
3. **UDI referansı** — rapor konusu cihaz UDI kodu ile
4. **PMS plan** — post-market surveillance gereklilikleri
5. **EUDAMED status** — AB kayıt durumu

### MDR Article 14 — Satış sonrası surveillance

**PMS raporu** periyodik gerekliliği. Patent raporunda cihaz bileşeni varsa, MDR PMS döngüsüne eklenmelidir.

### Hazır beyan metni

> **MDR/IVDR Uyum Beyanı**: Bu rapor, MDR (EU 2017/745) ve/veya Türkiye Tıbbi Cihaz Yönetmeliği (2021) kapsamında değerlendirilen cihaz bileşeni içermektedir. [Cihaz adı], Sınıf [I/IIa/IIb/III] olarak sınıflandırılmıştır. UDI: [XXXX]. Bu rapor MDR gerekliliklerini yerine getirmek için yeterli değildir; onaylanmış kuruluş denetimi + klinik değerlendirme raporu (CER) ayrıca zorunludur.

---

## 4. KVKK — Kişisel ve Sağlık Verisi

### Çerçeve

**6698 sayılı Kişisel Verilerin Korunması Kanunu** (2016):
- Genel veri işleme ilkeleri (m. 4)
- Özel nitelikli veri — sağlık verisi (m. 6)
- VERBİS kayıt (veri sorumluları sicili)
- İhlal bildirimi: 72 saat
- İdari para cezası: 2025 güncel rakamlar için kvkk.gov.tr

### Patent raporlarında KVKK

**Kişisel veri içeren senaryolar**:
- Bilirkişi raporu atıfları (isim + meslek)
- Patent mucitleri (full name)
- Hasta verisi (klinik çalışma sonuçları)
- KOL bilgileri
- Telefon görüşmesi içerikleri (dava hazırlığı)

### Açık rıza gerekliliği

Sağlık verisi işleme için **açık rıza** (m. 6(3)) — klinik çalışma verileri, biyoeşdeğerlik datası.

**İstisnalar** (m. 6(4)):
- Tıbbi teşhis, tedavi (sağlık profesyonelleri tarafından)
- Kamu sağlığı
- Koruyucu hekimlik

Patent stratejisi için sağlık verisi işleme **açık rıza veya anonim** olmalı.

### Veri aktarımı (sınır ötesi)

**m. 9**: KVKK Kurulu izni olmaksızın yurt dışına veri aktarımı yasak. Ancak:
- Taahhütname ile (Kurul onayı sonrası)
- Bağlı şirketler arası BCR (Binding Corporate Rules)
- Açık rıza

**Pharma grup içi DD**: KVKK uyumlu intra-group data transfer agreement zorunlu.

### Hazır beyan metni

> **KVKK Uyum Beyanı**: Bu rapor, 6698 sayılı Kişisel Verilerin Korunması Kanunu kapsamında **[kişisel / özel nitelikli / anonimleştirilmiş / kişisel veri içermez]** veri işlemiştir. Kişisel veri işleme söz konusu olduğunda, açık rıza veya KVKK m. 5-6'daki istisnalar (kanuni yükümlülük, meşru menfaat, sözleşme ifası) esas alınmıştır. Yurt dışı aktarım için KVKK Kurulu onaylı taahhütname mevcuttur. Sağlık verisi ( m. 6) işleme, yalnız anonim/agrege formda yapılmıştır.

### İhlal durumu

KVKK'nın kritik verisine raporda yer veriliyorsa ve rapor sızarsa:
- 72 saat içinde ihlal bildirimi (KVKK Kurulu'na)
- Veri sahiplerine ihlal bildirimi
- İdari para cezası: güncel tarifeye göre

---

## 5. GDPR — AB Operasyonları

### Ne zaman uygulanır

- Raporun AB veri sahibi verisini işlemesi
- AB'deki tesislere ait bilgi
- AB pazarına yönelik patent stratejisi

### KVKK ile farklar

| Konu | KVKK | GDPR |
|---|---|---|
| Coğrafi kapsam | Türkiye | AB territoriality + extraterritorial |
| Rıza geri çekme | Kabul edilir | Kabul edilir — süre kısıtlaması yok |
| DPIA | Opsiyonel | Zorunlu (high-risk processing) |
| DPO | Zorunlu durumlar sınırlı | Zorunlu (genellikle) |
| İhlal bildirim süresi | 72 saat | 72 saat |
| Max cezai tarife | KVKK tarifesi | €20M veya küresel cironun %4'ü |

### Hazır beyan metni

> **GDPR Uyum Beyanı** (AB işlemleri için): Bu rapor, GDPR (EU 2016/679) kapsamında veri işlemektedir. Legal basis: [GDPR Art. 6(1)(a/b/c/d/e/f)]. Data Protection Impact Assessment (DPIA) tamamlanmıştır / N/A. Data Protection Officer (DPO) onayı alınmıştır. Veri sahiplerine ilgili haklar (m. 15-22) bildirilmiştir.

---

## 6. Avukat-Müvekkil Ayrıcalığı + Work Product Doctrine

### Türk hukukunda avukat-müvekkil ilişkisi

**1136 sayılı Avukatlık Kanunu m. 36**:
> "Avukatların, kendilerine tevdi edilen veya gerek avukatlık görevi, gerekse Türkiye Barolar Birliği ve barolar organlarındaki görevleri dolayısıyla öğrendikleri hususları açığa vurmaları yasaktır."

### Çalışma ürünü koruması

**HMK m. 219/3** (2011):
> "Avukatın müvekkili için hazırladığı belgeler tanıklık konusu olamaz."

**Yargıtay 11. HD 2015/11456 E.** — Avukat-müvekkil iletişimi, dava stratejisi belgeleri, hukuki görüş raporları **üçüncü kişilere karşı gizlilik** sağlar.

### Hazır çalışma ürünü işaretlemesi

Her IP rapor başında:

```
[GİZLİ — HUKUKİ ÇALIŞMA ÜRÜNÜ]
[PRIVILEGED AND CONFIDENTIAL — ATTORNEY WORK PRODUCT]

Bu belge, HMK m. 219/3 ve Av.K m. 36 kapsamında avukat-müvekkil 
iletişimi olarak hazırlanmıştır. Avukat-müvekkil ayrıcalığı 
kapsamındadır ve üçüncü taraflarla paylaşım yapılamaz.
```

### Ayrıcalık kaybı riskleri

Ayrıcalık **aşağıdaki durumlarda kaybedilir**:
- Üçüncü tarafla paylaşım (tedarikçi, consultant, üniversite)
- İnternal leak (ihlal, whistleblower)
- Yönetim kurulu / CEO dosyalarına ekleme — bazı jurisdictionsda
- E-posta CC'leri sürerken

**Koruma için**:
- Bağımsız dış avukatla compartmentalization
- NDA + avukat-müvekkil ilişki sözleşmesi
- Shared drive erişim kısıtlaması
- Dosya watermark ("PRIVILEGED")

### Ortak savunma ayrıcalığı (common interest privilege)

İki firma ortak dava savunması için bilgi paylaşırsa (ör. ortak opposition), tipik olarak ayrıcalık sürer **ancak** Türkiye'de henüz spesifik içtihat oluşmamış — formal Common Interest Agreement (CIA) önerilir.

### Hazır beyan metni

> **Avukat-Müvekkil Ayrıcalığı**: Bu doküman, 1136 sayılı Avukatlık Kanunu m. 36 ve 6100 sayılı HMK m. 219/3 kapsamında "avukat-müvekkil ayrıcalığı" ve "çalışma ürünü" statüsündedir. Yalnızca yetkili hukuk müşavirleri ve onaylanmış iç paydaşlar erişebilir. Üçüncü taraflarla paylaşım, avukatın yazılı izni olmaksızın yasaktır. İhlali 1136 sayılı Kanun m. 36 ve TCK m. 239 kapsamında suç teşkil eder.

---

## 7. GCP (Good Clinical Practice)

### ICH E6(R2)/(R3)

**ICH GCP** — klinik çalışma etik + metodoloji standartı. Türkiye'de TİTCK Klinik Araştırmalar Yönetmeliği (2015, güncellemeler).

### Patent raporlarında uygulama

- Klinik çalışma verisi prior art olarak kullanılıyorsa: GCP uyumlu mu?
- Biyobenzer karşılaştırılabilirlik çalışmaları GCP zorunlu
- Bilirkişi raporlarında klinik data analizi GCP atıfları

### Hazır beyan metni

> **GCP Uyum Beyanı**: Bu raporda atıf yapılan klinik çalışma verileri, ICH-GCP E6(R2)/(R3) uyumlu olarak yürütülmüş / [kaynak] çalışmalardan elde edilmiştir. Verilerin GCP uyumluluk statüsü her kaynak için ayrıca doğrulanmıştır.

---

## 8. FCPA / UK Bribery Act / Türkiye 5607 — Kamu Görevlisi Etkileşimi

### Çerçeve

- **FCPA** (ABD, 1977) — extraterritorial — yabancı kamu görevlisine rüşvet yasağı
- **UK Bribery Act** (2010) — yabancı kamu görevlisi + özel sektör dahil
- **5607 sayılı Rüşvet ve Yolsuzluk İle Mücadele Kanunu** (Türkiye)
- **5237 TCK m. 252** — rüşvet suçu

### Kimler kamu görevlisi sayılır?

- TİTCK çalışanları
- SGK personeli
- Üniversite öğretim üyeleri (devlet üniversiteleri)
- Devlet hastanesi doktorları
- TÜRKPATENT personeli

### Patent raporlarında riskler

- Ruhsat/patent prosedürlerinde "facilitation payment" (hızlandırma bahşişi) yasak
- KOL ödemeleri "fair market value" olmalı (gerçek değer)
- Hospitality standartları (USA $50/kişi gibi katı limitler)
- Pharma-HCP etkileşimi EFPIA + IFPMA codes

### Hazır beyan metni

> **Anti-Bribery Uyum Beyanı**: Bu raporun hazırlanma sürecinde veya atıf yapılan etkileşimlerde FCPA (US), UK Bribery Act, Türkiye 5607 sayılı Kanun ve EFPIA/IFPMA codes ihlali yapılmamıştır. KOL ödemeleri fair market value standardında + usulüne uygun sözleşme + transparency raporlaması ile gerçekleştirilmiştir.

---

## 9. Çıkar Çatışması Beyanları

### Zorunlu ifşalar

Her rapor yazarı/katkıcısı:
- Finansal ilişkiler (shareholdings, consulting)
- İlgili firmalara ait patent buluşları
- Son 3 yıl içinde benzer konuda alınan ücretler
- Aile/akraba bağlantıları

### Dış hukuk müşaviri özel

- Rakip firmalara aktif hizmet var mı
- Chinese wall uygulaması
- Geçici / kalıcı danışmanlık

### Hazır beyan metni

> **Çıkar Çatışması Beyanı**: Bu rapor, [Firma] IP stratejisi için hazırlanmıştır. Rapor hazırlayıcıları [Firma] personelidir veya sözleşmeli dış danışmandır; rakip pharma firmalarla aktif profesyonel ilişkileri bulunmamaktadır / mevcut ilişkiler Chinese Wall uygulaması ile ayrıştırılmıştır. Finansal çıkar/hissedarlık beyanı: [Yok / spesifik beyan].

---

## 10. Rapor-tip × compliance beyan matrisi

### §1 FTO Raporu

**Zorunlu**:
- Avukat-müvekkil ayrıcalığı
- MDR/IVDR (cihaz bileşeni varsa)
- Çıkar çatışması

**Önerilen**: KVKK (bilirkişi isimleri varsa)

### §2 Invalidity Briefing

**Zorunlu**:
- Avukat-müvekkil ayrıcalığı
- Çıkar çatışması

**Önerilen**: MDR/IVDR (cihaz patent iptalinde), KVKK (prior art müelliflerinde isim)

### §3 Landscape Raporu

**Zorunlu**:
- Çıkar çatışması

**Önerilen**: GPP3 (yayın dönüşümüne hazırlık), avukat-müvekkil

### §4 Lifecycle Yol Haritası

**Zorunlu**:
- Avukat-müvekkil ayrıcalığı
- Çıkar çatışması

**Önerilen**: MDR/IVDR (cihaz katmanları için)

### §5 Pazara Giriş Takvimi

**Zorunlu**:
- Avukat-müvekkil ayrıcalığı
- KVKK (hasta verisi içerirse)
- FCPA / 5607 (TİTCK/SGK müzakereleri)
- Çıkar çatışması

**Önerilen**: MDR/IVDR, GCP

### §6 Litigation Briefing

**Zorunlu**:
- Avukat-müvekkil ayrıcalığı (en kritik rapor bu)
- KVKK (dava tarafı + tanık verileri)
- Çıkar çatışması

**Önerilen**: FCPA (tazminat hesaplamada)

### §7 Due Diligence Report

**Zorunlu**:
- Avukat-müvekkil ayrıcalığı
- KVKK + GDPR (target çalışan verisi)
- Çıkar çatışması
- FCPA (target firma anti-bribery compliance)

**Önerilen**: MDR/IVDR, GCP

### §8 Opposition Briefing

**Zorunlu**:
- Avukat-müvekkil ayrıcalığı
- Çıkar çatışması

### §9 Biosimilar Pathway Briefing

**Zorunlu**:
- Avukat-müvekkil ayrıcalığı
- MDR/IVDR (cihaz entegrasyonu)
- KVKK (karşılaştırılabilirlik klinik datası)
- GCP
- FCPA / 5607 (TİTCK/SGK/KOL müzakeresi)
- Çıkar çatışması

**Önerilen**: GPP3 (yayın dönüşümü)

---

## 11. Hazır şablon metinler

### Raporların standart footer compliance blok'u

Aşağıdaki blok her rapor şablonuna **varsayılan olarak** eklenir:

```markdown
---

## Compliance Beyanları

### Avukat-Müvekkil Ayrıcalığı
Bu doküman 1136 sayılı Avukatlık Kanunu m. 36 ve HMK m. 219/3 kapsamında 
"avukat-müvekkil ayrıcalığı" ve "çalışma ürünü" statüsündedir. Yalnızca 
yetkili hukuk müşavirleri ve onaylanmış iç paydaşlar erişebilir.

### Veri Koruma
KVKK (6698 sayılı Kanun) ve GDPR (EU 2016/679) kapsamında: 
[Kişisel veri içermez / Anonimleştirilmiş / Açık rıza ile işlenmiştir]

### Çıkar Çatışması
Rapor hazırlayıcılarının [Firma] ile istihdam ilişkisi dışında ilgili 
taraflarda finansal çıkarı bulunmamaktadır.

### Anti-Bribery
FCPA (US), UK Bribery Act, Türkiye 5607 sayılı Kanun ve EFPIA/IFPMA 
codes uyumluluğu sağlanmıştır.

### Hukuki Sorumluluk
Bu rapor bilgilendirme amaçlıdır. Nihai karar için yetkili patent vekili 
(TÜRKPATENT/EPO akreditasyonlu) + uzman hukuk müşaviri ile koordinasyon 
zorunludur.

---

*Hazırlayan: [İsim], [Unvan], [Tarih] — [İmza]*  
*Gözden geçiren: [İsim], [Unvan], [Tarih] — [İmza]*  
*Onaylayan: [İsim], [Unvan], [Tarih] — [İmza]*
```

### Duruma özgü ek beyanlar

**Cihaz içerikli rapor**:
```
### MDR/IVDR
[Cihaz adı], Sınıf [X] — MDR (EU 2017/745) / Türkiye Tıbbi Cihaz 
Yönetmeliği (2021). UDI: [XXXX]. Klinik değerlendirme raporu: 
[Mevcut / Bekleniyor / N/A].
```

**Klinik veri atıflı rapor**:
```
### GCP
Klinik veriler ICH-GCP E6(R2)/(R3) uyumlu yürütülen çalışmalardan 
alınmıştır.
```

**Yayına dönüşecek rapor**:
```
### GPP3
Yayın formatına dönüştürülmesi durumunda GPP3 (2015, güncelleme 2022) 
kriterleri uygulanacaktır: ICMJE yazarlık + ghost authorship yasağı + 
tam veri erişimi + çıkar beyanı.
```

---

*Compliance manzarası dinamiktir: KVKK ikincil mevzuat, AI Act (EU 2024/1689), DMA/DSA, Chips Act gibi yeni rejimler yıllık eklenir. Bu protokol 2026-04-23 itibarıyla geçerli durumu yansıtır. Yıllık güncelleme zorunludur. Spesifik bir rapor için compliance check-list için uzman hukuk müşaviri ile koordinasyon gereklidir.*
