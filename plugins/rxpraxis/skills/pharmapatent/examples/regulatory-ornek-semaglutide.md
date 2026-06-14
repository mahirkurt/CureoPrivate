# examples/regulatory-ornek-semaglutide.md — Pazara Giriş Takvimi Filled Example

> **Kullanım notu**: Bu doküman hipotetik bir vakadır, eğitim amaçlıdır. Gerçek patent + ruhsat tarihleri için TÜRKPATENT EPAAT, EMA EPAR, FDA Orange Book'tan güncel veri alınmalıdır. Semaglutide IP peyzajı karmaşık ve dinamiktir; bu örnek 2026-04-23 tarihli kısmi veriye dayanır.

---

# Pazara Giriş Takvimi — Jenerik/Biyobenzer Semaglutide (Türkiye)

**Versiyon**: v1.0 — 2026-04-23
**Hazırlayan**: [Jenerik/Biyobenzer Firma] Strateji Ekibi
**Dağıtım kısıtı**: GİZLİ — TİCARİ KARAR DOKÜMANTASYONU
**Hedef kitle**: Executive (CEO, CFO, Board) + Legal (GC + IP Lead)

---

## 1. Yönetici Özeti (BLUF)

**En erken yasal pazara arz tarihi**: 2032 Q1 (tam patent engelleri + veri imtiyazı dikkate alınarak).
**En erken pratik pazara arz tarihi**: 2032 Q3-Q4 (ruhsat + fiyat + SGK müzakere sonrası).

**Kritik engeller** (önem sırasına göre):
1. **Patent duvarı**: Novo Nordisk'in semaglutide portföyü 2031-2035 aralığında dağılık expiry tarihleri içeriyor (küçük molekül form patenti 2031, formülasyon patenti 2033, injection device patenti 2034)
2. **Veri imtiyazı**: Semaglutide EMA onayı 2017-12-08 → 6 yıllık TR veri imtiyazı 2023-12'de zaten doldu (NOT bir engel)
3. **Cihaz patenti**: FlexTouch/FlexPen oto-enjektör patent duvarı 2032-2034 sonuna kadar → biyobenzer kendi cihazı geliştirmeli
4. **Üretim kapasitesi**: Peptide sentezi + liyofilize üretim için yüksek CAPEX; 18-24 ay ramp-up

**Önerilen zaman çizelgesi**: **2028 Q2**'de biyoeşdeğerlik/karşılaştırılabilirlik başlat (Bolar kapsamında), **2030 Q2**'de ruhsat başvur, **2032 Q3** pazara arz.

**Toplam yatırım tahmini**: USD 45-75M (üretim tesisi + klinik karşılaştırılabilirlik + cihaz geliştirme + registrasyon).

**Stratejik tavsiye**: ŞARTLI DEVAM — yüksek IP riski, yüksek yatırım; pazar büyüklüğü (Türkiye'de GLP-1 pazarı ~USD 120M ve büyüyor) ve uzun vadeli stratejik değer justifikasyonu sağlıyor. Ancak patent çürütme şansı aranmalı (paralel invalidity davaları).

## 2. Ürün Profili ve Ruhsat Stratejisi

| Özellik | Değer |
|---|---|
| INN | Semaglutide |
| Aktif madde tipi | GLP-1 analoğu (modifiye peptid, 31 amino asit) |
| Molekül ağırlığı | 4114 Da |
| Dozaj formları hedef | Injectable (SC, oto-enjektör pen), oral tablet |
| Endikasyonlar | Tip 2 diyabet, obezite, kardiyovasküler risk azaltma |
| Başvuru tipi | **Biyobenzer** (Art. 10(4) hybrid uygulaması) |
| Referans ürün | Ozempic® (subkutan), Rybelsus® (oral), Wegovy® (obezite) |
| Hedef pazar | Türkiye (birincil), MENA (ikincil), AB (çok-ülke) |
| Beklenen pazar payı (3 yıl) | %12-18 (ilk biyobenzer olarak) |

## 3. Patent Durumu Özeti

### 3.1. Novo Nordisk semaglutide portföyü — kritik patentler (hipotetik özetler)

| Patent No | Konu | Başvuru | Expiry | TR Durum | Aşılma stratejisi |
|---|---|---|---|---|---|
| EP1996220 | Semaglutide base compound | 2005-05-23 | **2025-05-23** | Aktif | Sona erince çözüm |
| EP2390264 | Sustained release formulation | 2010-02-12 | **2030-02-12** | Aktif | Formülasyon alternatifi |
| EP2925298 | Oral semaglutide formulation (SNAC) | 2013-03-11 | **2033-03-11** | Aktif | Oral ürün için engel |
| EP2874633 | Semaglutide salt + stabilizer | 2013-09-26 | **2033-09-26** | Aktif | Farklı tuz formu |
| EP3456789 | FlexTouch injection device | 2014-11-03 | **2034-11-03** | Aktif | Kendi cihaz geliştir |
| EP3234567 | Cardiovascular use of semaglutide | 2015-06-20 | **2035-06-20** | Aktif | Label carve-out |

*Tablo kısaltılmıştır — Novo Nordisk semaglutide için 40+ aktif patent aileye sahip.*

### 3.2. Patent çürütme / hükümsüzlük olasılıkları

Aşağıdaki patentler için invalidity analizi yapılmalı (ayrı briefing — `invalidity-ornek-*.md` ile):

- **EP2390264 (SR formülasyon)**: WO2003/055522 (Novo'nun kendi eski patenti) prior art adayı olabilir — kısmi hükümsüzlük olası
- **EP2925298 (Oral SNAC)**: SNAC (Sodium N-Caproyl Alanine) Emisphere 2001 patentinde kapsamlı açıklanmış — bağımsızlık iddiası zayıflayabilir
- **EP3234567 (CV use)**: SUSTAIN-6 trial 2016'da yayımlandı; 2015 başvurusu için önceki teknik var mı?

**Stratejik tavsiye**: Kritik patentlerden EP2390264 ve EP2925298 için **invalidity briefing** hazırlansın (ayrı dava).

## 4. Veri İmtiyazı Hesabı

### Ozempic (subkutan semaglutide)

**Temel formül**:
```
Erişim tarihi = MAX(
    Gümrük Birliği alanında ilk ruhsat + 6 yıl,
    Türkiye patent süresi
)
```

- **Gümrük Birliği alanında ilk ruhsat**: 2018-02-08 (EMA merkezi, EPAR referansı)
- **6 yıl eklendiğinde**: 2024-02-08 (✓ GEÇMİŞ)
- **Türkiye patent süresi**: EP1996220 → 2025-05-23 (ana molekül)

**Hesaplanan erişim tarihi**: **2025-05-23** (patent süresi veri imtiyazından geç).

**⚠️ Kritik**: Veri imtiyazı artık bir engel değil. Patent duvarı belirleyici.

### Rybelsus (oral semaglutide)

- **Gümrük Birliği alanında ilk ruhsat**: 2020-04-03 (EMA)
- **6 yıl eklendiğinde**: 2026-04-03 (✓ GEÇMEK ÜZERE)
- **Türkiye patent süresi**: EP2925298 → 2033-03-11 (SNAC oral formülasyon)

**Hesaplanan erişim tarihi**: **2033-03-11** (patent süresi belirleyici).

### Wegovy (obezite endikasyonlu semaglutide 2.4mg)

- Aynı molekül, farklı dozaj ve endikasyon
- Yeni endikasyon için Türkiye'de ayrı veri imtiyazı uzatması YOK
- Erişim tarihi Ozempic ile aynı: **2025-05-23**

### Net sonuç: her 3 ürün için gerçek engel

| Ürün | Veri imtiyazı engeli | Patent engeli | Belirleyici |
|---|---|---|---|
| Ozempic (SC injection) | 2024-02-08 (geçti) | 2030-02 formülasyon + 2034-11 cihaz | **Cihaz patenti** |
| Rybelsus (oral tablet) | 2026-04-03 (geçmek üzere) | 2033-03 SNAC formülasyon | **Formülasyon patenti** |
| Wegovy (obezite) | 2024-02-08 (geçti) | aynı + 2035-06 CV use (endikasyon) | **Cihaz + endikasyon** |

## 5. Bolar İstisnası Takvimi

**Bolar Kural** (SMK m. 85/3): Ruhsatlandırma için gerekli çalışmalar patent tecavüzü oluşturmaz. Bu kural biyobenzer için çok önemli çünkü karşılaştırılabilirlik paketi 3-4 yıl sürer.

### Önerilen aktivite takvimi

| Yıl | Aktivite | Bolar kapsamı |
|---|---|---|
| 2028 Q2 | Peptid sentez süreci + reference standard characterization | ✓ Bolar |
| 2028 Q3-Q4 | Analitik karakterizasyon (HPLC, MS, CD, DSC) — 3 ticari parti | ✓ Bolar |
| 2029 Q1-Q2 | Nonklinik PK/PD hayvan modeli | ✓ Bolar |
| 2029 Q3-Q4 | Faz I karşılaştırmalı PK (~30 subject) | ✓ Bolar |
| 2030 Q1-Q2 | Faz III karşılaştırmalı etkinlik (T2DM, ~900 subject) | ✓ Bolar |
| 2030 Q3 | İmmünojenisite + uzun vadeli stabilite | ✓ Bolar |
| 2030 Q4 | Ruhsat dosyası hazırlık | ✓ Bolar |
| 2031 Q1 | **TİTCK ruhsat başvurusu** | İdari süreç başlar |
| 2031 Q1-2032 Q4 | Ruhsat değerlendirme (eksiklik döngüsü) | İdari süreç |
| 2032 Q2 | Ruhsat alınır | — |
| 2032 Q2-Q3 | Fiyat onayı + SGK müzakere | İdari süreç |
| 2032 Q4 | **Pazara arz** (patent expiry sonrası) | — |

**Kritik kısıtlama**: Üretim ticari ölçekte **sadece patent expiry sonrası** başlayabilir (Bolar dışı).

## 6. Pediatrik / Orphan Etkileşimi

**Türkiye**: Pediatrik veya orphan uzatma yok → N/A.

**AB**: Semaglutide obezite endikasyonunda (Wegovy) pediatrik PIP kapsamında — AB'de 6 ay uzatma olasılığı (AB pazarları için ayrı zamanlama). TR için etkisi yok.

## 7. Cihaz Entegrasyonu — KRİTİK

**FlexTouch® injection device patenti (EP3456789)** — Novo Nordisk'in premium cihaz portföyü.

### Biyobenzer firma opsiyonları

**Opsiyon A: Kendi oto-enjektör cihazını geliştir**
- Mühendislik süreci: 18-24 ay
- CE işaretleme süreci: Sınıf IIb (ilaç salan aktif cihaz)
- Onaylanmış kuruluş denetimi: 6-12 ay
- ÜTS kaydı + UDI + GMP validation: 3-6 ay
- **Toplam**: 24-36 ay
- **Patent FTO**: Ayrı bir FTO çalışması gerekir — Becton Dickinson, Ypsomed, SHL Group patent portföyleri

**Opsiyon B: Üçüncü taraf cihaz tedarikçisi (Ypsomed, SHL Group, Becton Dickinson)**
- Ypsomed YpsoMate®, SHL Molly® vb. beyaz etiketli cihazlar
- Süre: 12-18 ay (integrasyon + validasyon)
- Maliyet: Daha yüksek COGS (lisans ücreti)
- IP FTO: Tedarikçi tarafından yönetilir

**Opsiyon C: Önce prefilled syringe ile gir, oto-enjektöre geçiş daha sonra**
- Prefilled syringe: daha basit, Sınıf IIa, 12-18 ay
- Konfor seviyesi düşük → pazar payı sınırlı
- Geçiş ürünü stratejisi

**Stratejik öneri**: **Opsiyon B** — üçüncü taraf tedarikçi. Time-to-market kritik; kendi cihaz geliştirme maliyeti biyobenzer marjları için ekonomik değil.

### Cihaz patenti etkileşimi

Cihaz patenti (EP3456789) 2034-11'de sona eriyor. Biyobenzer 2032 Q4'te pazara girerse:
- Pfizer gibi rakipler de aynı anda girebilir (her biri kendi cihazı ile)
- Ypsomed tabanlı biyobenzer vs kendi cihaz geliştiren Novo'nun sonraki nesil cihazı
- Fiyat rekabeti: biyobenzer %20-40 indirim

## 8. Risk Değerlendirmesi

### 8.1. İhtiyati Tedbir (HMK m. 389) ihtimali

Novo Nordisk tedbir talebinde bulunabilir mi?

**Yargıtay eğilimi**: İlaç patent tedbirlerinde 2015 sonrası dikkatli tutum. Prima facie geçerlilik + yaklaşık ispat + teminat gerekliliği.

**Değerlendirme**:
- Novo'nun tedbir şansı ORTA — patent portföyü güçlü ancak biyobenzer zaten kendi formülasyon + cihazı ile gelirse tecavüz doğrudan değil
- Biyobenzer firma tarafı: Bolar + farklı formülasyon/cihaz savunması güçlü
- **Tahmini tedbir teminatı**: USD 5-10M (yıllık Türkiye cirosunun %20-30'u)

### 8.2. Patent hükümsüzlük paralel dava

**Önerilen**: EP2390264 (SR formülasyon) için 2028'den itibaren paralel invalidity davası açılsın. Eğer kazanılırsa:
- Formülasyon engeli kalkar
- Pazara giriş 2030'a çekilebilir (24 ay erken)

**Maliyet**: USD 200-350K
**Şans**: MODERATE (prior art adayları mevcut)

### 8.3. Label carve-out (CV endikasyonu)

EP3234567 (CV kullanım) → biyobenzer label'ından CV endikasyonu çıkarılabilir ("Diabetes + weight management only"). Ancak:
- Off-label reçetelenir — firma sorumluluğu değil
- Pazar payı sınırlı etkilenir (CV endikasyonu küçük bir alt segment)

## 9. Zaman Çizelgesi (Gantt)

```
               2028  2029  2030  2031  2032  2033  2034  2035
                |     |     |     |     |     |     |     |
Bolar aktiviteler [=====]                                    
Faz I/III         [===========]                              
Cihaz geliştirme     [==============]                        
Formülasyon patent expiry                     X              
Ruhsat başvurusu             [====]                          
Ruhsat değerlendirme             [==========]                
Cihaz patent expiry                           X              
Fiyat + SGK                          [==]                   
Pazara arz                              [=================>
```

**Pazara arz**: 2032 Q3-Q4 (patent duvarı + regülatör süreç dikkate alınarak).

## 10. Öneriler

### Kısa vadeli (2026-2027)

1. Semaglutide IP peyzajı detaylı FTO çalışması (ayrı `fto-ornek-*.md` briefing formatı)
2. EP2390264 ve EP2925298 için invalidity feasibility çalışması
3. Cihaz tedarikçisi due diligence (Ypsomed, SHL, Becton Dickinson)
4. Üretim tesisi CAPEX komiteye sunulsun (USD 35-50M)

### Orta vadeli (2028-2030)

1. Bolar kapsamında peptide sentez + karakterizasyon başla
2. Faz I/III klinik çalışmalar
3. Paralel invalidity davası (EP2390264)
4. Cihaz CE sertifikasyonu

### Uzun vadeli (2030-2032)

1. Ruhsat başvurusu + fiyat + SGK müzakere
2. Ticari üretim partileri (patent expiry sonrası)
3. Launch readiness

### Stratejik kırmızı çizgiler

- Patent duvarı 2030'dan daha erken aşılamazsa proje durdurulsun
- Üretim CAPEX USD 75M'yi aşarsa ROI tekrar değerlendirilsin
- Cihaz tedarikçisi bulunmazsa Opsiyon C'ye (prefilled syringe) geçilsin

## 11. Hukuki Sorumluluk Notu

Bu takvim bilgilendirme amaçlıdır. Patent sürelerinde TÜRKPATENT EPAAT güncel veriye göre sürekli doğrulama gerekir. Novo Nordisk aktif portföy genişletme yapmaktadır; yeni başvurular pazara giriş tarihini geciktirebilir. Stratejik karar öncesi dış hukuk müşaviri + patent vekili ile koordinasyon zorunludur. Bu doküman mahkeme sürecinde delil olarak kullanılabilir hukuki çalışma ürünüdür.

---

*Hazırlayan: [İsim], Stratejik Planlama Direktörü*
*Gözden geçiren: [İsim], IP Lead + Regulatory Director*
*Onaylayan: [İsim], CEO*
*Finans onayı: [İsim], CFO*

---

## Not: Bu rapor ile bağlantılı diğer briefing önerileri

- **FTO Raporu**: Semaglutide formülasyonun + cihaz seçiminin detaylı FTO analizi (`fto-ornek-*.md` formatında)
- **Invalidity Briefing**: EP2390264 ve EP2925298 için hükümsüzlük argümanları (`invalidity-ornek-*.md` formatında)
- **Litigation Readiness**: İhtiyati tedbir savunma dosyası + acil durum karar ağacı
- **Lifecycle Yol Haritası**: Biyobenzer pazara girdikten sonra orta vadeli genişleme (CV endikasyonu, obezite endikasyonu, pediatrik)
