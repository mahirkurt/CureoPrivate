# examples/fto-ornek-atorvastatin.md — FTO Raporu Filled Example

> **Kullanım notu**: Bu doküman hipotetik bir vakadır, eğitim amaçlıdır. Atorvastatin patent süresi 2010-2012 yılları arasında çeşitli ülkelerde dolmuş, günümüzde jenerik pazardadır — gerçek bir FTO çalışması için esas alınmamalıdır. Burada yöntem ve format gösterilmektedir. Gerçek bir FTO çalışması için güncel TÜRKPATENT EPAAT + Espacenet + Orange Book verileri zorunludur.

---

# Faaliyet Serbestisi (FTO) Raporu — NovaStat 40mg Tablet

**Versiyon**: v1.0 — 2026-04-23
**Hazırlayan**: Patent Strateji Birimi, [Firma]
**Dağıtım kısıtı**: GİZLİ — HUKUKİ ÇALIŞMA ÜRÜNÜ
**Hedef kitle**: Technical (R&D, patent vekili, bilirkişi)

---

## 1. Yönetici Özeti

[Firma]'nın planladığı **atorvastatin kalsiyum 40mg tablet** (ticari ad: NovaStat) ürünü için yürütülen FTO çalışması sonucunda **18 aktif patent** tespit edilmiş, bunlardan **3'ü Orta-Yüksek risk**, **5'i Düşük-Orta risk** seviyesinde olarak değerlendirilmiştir. Temel molekül patenti (Pfizer, EP0409281) 2012 yılında sona ermiş olup, kalan patentler formülasyon + polimorf + kombinasyon alanındadır.

**Genel sonuç**: KISMEN RİSKLİ — 3 kritik patent için design-around veya lisans müzakeresi gerekmektedir.

**Ana bulgular**:
- Polimorf patenti EP1235764 (Pfizer, sonlanış 2024) planlanan formülasyonun Form I kristal yapısını kapsamaktadır
- Mikrokapsül formülasyon patenti EP2876108 (Teva, 2029'a kadar) özgül eksipiyan kombinasyonunu korumaktadır
- Amlodipine kombinasyon patenti (AstraZeneca) monoterapi kullanımını etkilememektedir

**Kritik öneri**: Form II veya Form IV kristal polimorfuna geçilmeli; Teva mikrokapsül patentinden uzaklaşan klasik tablet compression uygulanmalıdır.

## 2. Ürün Teknik Özeti

| Özellik | Değer |
|---|---|
| INN | Atorvastatin kalsiyum |
| CAS | 134523-03-8 (kalsiyum tuzu) |
| SMILES | `CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccc(F)cc2)n(CC[C@@H](O)C[C@@H](O)CC(=O)[O-])c1-c1ccccc1.[Ca+2]` |
| Dozaj formu | Tablet, film kaplı |
| Konsantrasyon | 40 mg atorvastatin bazı |
| Eksipiyanlar | Laktoz monohidrat, MCC, kroskarmeloz Na, Mg stearat, film (Opadry II) |
| Kristal form | **Form IV** (design-around seçim) |
| Hedef pazar | Türkiye (birincil), AB (ikincil) |
| Pazara giriş tarihi | Q3 2026 |
| Aktif patent durumu | Molekül patenti (EP0409281) 2012'de sona erdi |

## 3. Araştırma Metodolojisi

**Tarih aralığı**: 2005-01-01 → 2026-04-23 (öncelik tarihi)
**Veri tabanları**: TÜRKPATENT EPAAT, Espacenet (global), USPTO Patent Public Search, Orange Book, WIPO PATENTSCOPE, SureChEMBL (kimyasal yapısal arama)

**Öncül Boolean sorgular**:
```
USPTO: (atorvastatin OR "4-fluorophenyl-hydroxy-calcium") AND CPC/A61K9/20
Espacenet: ta="atorvastatin" AND cpc=A61K9/20 AND pd>20050101
EPAAT: atorvastatin (başlık + özet + istem)
```

**CPC kilit kodları** (çekirdek setten çıkarıldı):
- A61K 31/40 — pirrol halkalı aktifler (atorvastatinin çekirdeği)
- A61K 9/20 — katı oral dozaj formları
- A61K 9/28 — film kaplı
- A61K 31/401 — pirrolidin türevleri
- C07D 207/34 — hedef molekül sentezi

**Kimyasal yapısal arama**: SureChEMBL, 80% benzerlik; 2-amino-4-fenil-3-hidroksi-pentanoik asit çekirdeği; 312 doküman, 47 patent.

**Epistemik sınırlar** (rezidüel risk bkz. §7):
- STN SciFinder erişimi olmadığı için Markush analizi manuel yapıldı
- Son 18 ay içinde TÜRKPATENT EPAAT'ta pending başvurular yayımlanmamış olabilir
- Tayland, Hindistan, Brezilya gibi RoW ülkeleri tarama kapsamı dışında

## 4. Tespit Edilen Aktif Patentler

| Patent No | Başvuru Sahibi | Başlık (kısa) | Öncelik | Expiry | TR Durum | Risk |
|---|---|---|---|---|---|---|
| EP0409281 | Pfizer | Atorvastatin base compound | 1989-07-21 | **Sona erdi** | Sona erdi | TEMİZ |
| EP1235764 | Pfizer | Crystalline Form I atorvastatin Ca | 1997-07-17 | 2024-07 | Aktif | **ORTA-YÜKSEK** |
| EP2876108 | Teva | Stabilized microencapsulated formulation | 2009-03-12 | 2029-03 | Aktif | **YÜKSEK** |
| EP1889827 | Pfizer | Amlodipine + atorvastatin FDC | 2002-05-14 | 2022-05 | Sona erdi | TEMİZ |
| EP3012345 | Watson | Amorphous atorvastatin formulation | 2012-08-03 | 2032-08 | Aktif | ORTA |
| TR2015/12345 | Abdi İbrahim | Direct compression process | 2015-06-20 | 2035-06 | Aktif | DÜŞÜK |
| EP1876543 | Sandoz | Atorvastatin + ezetimibe combination | 2007-04-11 | 2027-04 | Aktif | TEMİZ (monoterapi için) |
| EP2345678 | Ranbaxy | Co-crystal atorvastatin-nicotinamide | 2010-12-01 | 2030-12 | Aktif | ORTA |

*Tablo kısaltılmıştır — tam liste için §9 Ek.*

## 5. İstem-Bazlı Analiz

### Patent 1: EP1235764 (Pfizer) — Form I Crystal Polymorph

**Bağımsız İstem 1**:
> "Crystalline Form I of atorvastatin calcium characterized by X-ray powder diffraction peaks at 2θ = 9.1°, 9.5°, 10.3°, 21.6°, 23.4° (± 0.2°)."

**Özellik-özellik eşleştirme**:

| Özellik | İstem | NovaStat (design-around) | Eşleşme |
|---|---|---|---|
| F1 Molekül | Atorvastatin Ca | Atorvastatin Ca | EVET |
| F2 Kristal form | Form I (2θ: 9.1, 9.5, 10.3, 21.6, 23.4°) | **Form IV** (2θ: 8.4, 12.1, 16.8, 22.3°) | **HAYIR** |
| F3 XRPD pattern | Belirtilmiş | Farklı pattern | HAYIR |

**Literal ihlal**: YOK — Form I'e özgü XRPD pikleri NovaStat'ın Form IV'ünde yoktur.

**Doktrinel eşdeğer**: Polimorf istemlerinde EPO doktrini (T 777/08) dar yorum gerektirir; farklı XRPD imzası farklı bileşik sayılır. Form IV doktrinel eşdeğer değildir.

**Risk seviyesi**: DÜŞÜK (design-around koşuluyla).

**Kritik koşul**: NovaStat üretiminde kristalleşme prosesinin Form IV'ü stabilize ettiği ve Form I kontaminasyonunun <3% kaldığı GMP'de doğrulanmalıdır.

### Patent 2: EP2876108 (Teva) — Stabilized Microencapsulated Formulation

**Bağımsız İstem 1**:
> "A pharmaceutical formulation comprising atorvastatin calcium (20-50% w/w) encapsulated within microspheres of ethyl cellulose (5-15% w/w) and PVP K30 (3-8% w/w), dispersed in an excipient matrix comprising lactose (30-60% w/w), wherein the formulation exhibits dissolution >85% at 30 minutes in pH 6.8 buffer."

**Özellik-özellik eşleştirme**:

| Özellik | İstem | NovaStat | Eşleşme |
|---|---|---|---|
| F1 Atorv Ca | %20-50 | %26 (40mg / 152mg tablet) | EVET |
| F2 Mikrokapsülleme | Ethyl cellulose mikroküre | **YOK** (direkt kompresyon) | HAYIR |
| F3 PVP K30 | %3-8 | %0 | HAYIR |
| F4 Laktoz matris | %30-60 | %52 | EVET |
| F5 Dissolüsyon profili | >%85 / 30 dk | %94 / 30 dk | EVET |

**Literal ihlal**: YOK — F2 ve F3 NovaStat'ta yok (mikrokapsülleme kullanılmamakta).

**Doktrinel eşdeğer**: Mikrokapsül + PVP kombinasyonu Teva'nın spesifik teknolojisidir; direkt kompresyon farklı bir proses ve farklı fizikokimyasal özellik sergiler. Dosya geçmişinde Teva, mikrokapsüllemeyi "kritik özellik" olarak vurgulamıştır (FYP limitation).

**Risk seviyesi**: DÜŞÜK.

### Patent 3: EP3012345 (Watson) — Amorphous Formulation

**Bağımsız İstem 1**:
> "An amorphous atorvastatin calcium composition, wherein the amorphous content is ≥95% as determined by XRPD."

**Özellik-özellik eşleştirme**:

| Özellik | İstem | NovaStat | Eşleşme |
|---|---|---|---|
| F1 Atorv Ca | Var | Var | EVET |
| F2 Amorf form | ≥%95 amorf | **Kristalin Form IV** | HAYIR |

**Literal ihlal**: YOK — NovaStat kristalin bir üründür, amorf değildir.

**Risk seviyesi**: DÜŞÜK-ORTA (üretim kararlılığı sırasında amorfizasyon olursa risk doğar; stabilite çalışmaları kritik).

### Patent 4: EP2345678 (Ranbaxy) — Co-crystal Atorvastatin-Nicotinamide

**Bağımsız İstem 1**:
> "A co-crystal of atorvastatin calcium and nicotinamide in a molar ratio of 1:1 to 1:2."

**Özellik-özellik eşleştirme**: NovaStat nicotinamide içermemekte; co-crystal değildir.

**Risk seviyesi**: TEMİZ.

## 6. Design-Around Önerileri

Yukarıdaki analizde **tek kritik engel** EP1235764 Form I polimorf patentidir. Önerilen design-around:

### Önerilen yaklaşım: Form IV kristal polimorfuna geçiş

**Teknik yol**:
1. Atorvastatin kalsiyum hammadde üretiminde Form IV kristalleşmesini sağlayan solvent sistemi: metanol-aseton 3:1, 0-5°C çökelme
2. GMP validasyon serileri: 3 ticari ölçek parti × tam XRPD + DSC analizi
3. Stabilite: ICH Q1A(R2) uzun süreli (25°C/60%RH) + hızlandırılmış (40°C/75%RH) 12 ay

**Biyoeşdeğerlik etkisi**: Form IV biyoyararlanımı Form I'den farklı olabilir. Referans ilacın (Lipitor® — Form I) biyoeşdeğerliğinin sağlanması için in vitro dissolüsyon + pilot PK çalışması zorunludur. Mümkün risk: farklı biyoeşdeğerlik → yeni Phase I gerekliliği (ek 6-9 ay).

**Yeni FTO sorunu yaratıyor mu?**: Form IV için 2 başvuru sahibi (Nicox 2015, Torrent 2018) ancak istem kapsamı dar (spesifik solvat form). Hibrid form IV-anhidrat NovaStat'ın kullandığı formla örtüşmemektedir.

**Tahmini süreç**: 9-12 ay (formülasyon yeniden geliştirme + biyoeşdeğerlik + ruhsat güncelleme).

**Maliyet tahmini**: USD 850,000 - 1,200,000 (formülasyon geliştirme + biyoeşdeğerlik × 2 + validasyon).

### Alternatif 1: Lisans müzakeresi (Pfizer, EP1235764)

Pfizer, patent 2024'te sonlanmakta. 2024'e kadar 3 yıllık lisans müzakere edilebilir. Pfizer tipik royalty: net satışın %8-12'si + milestone. Tahmini pazara giriş: 2026 Q3 (original plan) vs 2024 Q3 (lisansla).

### Alternatif 2: Pazara girişi 2024 Q3'e erteleme

EP1235764 sonlanışı sonrası (2024-07) serbest Form I kullanımı. Yeni formülasyon geliştirme gerektirmez. Ancak 2 yıllık pazar kaybı + jenerik rakipler (muhtemelen 5+ firma 2024'te girecek).

**Öneri matrisi**:

| Kriter | Form IV design-around | Pfizer lisans | 2024'e erteleme |
|---|---|---|---|
| Zaman | +9-12 ay | +0 ay | +24 ay |
| Maliyet | ~USD 1M | USD ~5M (3 yıl royalty) | 0 (ancak pazar kaybı) |
| Pazar pozisyonu | İlk jenerik | 2. jenerik | Rekabetçi sonrası |
| Uzun vadeli bağımsızlık | YÜKSEK | DÜŞÜK | ORTA |

**Stratejik tavsiye**: **Form IV design-around** — uzun vadeli bağımsızlık + erken giriş kombinasyonu.

## 7. Rezidüel Risk Beyanı

Aşağıdaki riskler tespit edilemedi ancak mevcut olabilir:

1. **Pending başvurular** — Son 18 ay içinde TÜRKPATENT / EPO'ya verilmiş ama henüz yayımlanmamış başvurular tanımsızdır. Özellikle Teva ve Pfizer devam eden portföy genişletmesine sahip olabilir.

2. **Markush kapsam riski** — Paid STN SciFinder erişimi olmadığı için, daha geniş statin sınıfı Markush formülleri (örn. HMG-CoA reduktaz inhibitörleri için genel formüller) tam taranmamıştır. SureChEMBL ile kısmi tarama yapılmış olup, daralan kapsamda 4 potansiyel Markush adayı incelenmiştir.

3. **Co-crystal / solvat varyantları** — Atorvastatinin 50+ bilinen solvat/co-crystal formu vardır. NovaStat'ın Form IV'ü üretim sırasında solvat oluşturursa, 3-5 solvat patentinin kapsamına girebilir (spesifik doğrulama GMP sonrası yapılmalıdır).

4. **Coğrafi kapsam** — Bu rapor TR + AB odaklıdır. ABD, Japonya, RoW pazarları için ayrı FTO gereklidir.

5. **Tıbbi cihaz bileşen riski** — NovaStat bir tablet ürünüdür; cihaz komponenti yoktur. Ancak ambalaj (blister + çocuk kilidi) için potansiyel tasarım patent/tasarım tescili riski incelenmemiştir.

## 8. Genel Sonuç ve Öneriler

### Stratejik değerlendirme

NovaStat, **uygun design-around ile FTO açısından pazara girişe hazır** konumdadır. 3 kritik patentten (EP1235764, EP2876108, EP3012345) tümü için teknik çözüm mevcuttur; Form IV kristal polimorfu birincil öneridir.

### Sonraki adımlar (Gantt önerisi)

| Ay | Aksiyon | Sorumlu |
|---|---|---|
| 1-2 | Form IV kristalleşme prosesi validasyonu | R&D + CMC |
| 2-4 | Pilot ölçek üretim (3 parti) + XRPD | CMC |
| 3-5 | In vitro dissolüsyon karşılaştırma | QC |
| 4-6 | Bolar istisnası kapsamında biyoeşdeğerlik | Klinik |
| 6-8 | TİTCK ruhsat başvurusu | Regulatory |
| 8-10 | Eksiklik cevapları | Regulatory |
| 10-14 | Pazara arz (ruhsat + fiyat + SGK) | Commercial |

### Hukuki güvence önerileri

- Form IV üretim prosesi için **3. kişi görüşü** (TÜRKPATENT) başvurusu — EP1235764'e karşı preemptive savunma pozisyonu
- Patent izleme servisine kayıt — Pfizer + Teva + Watson portföy genişletme uyarısı
- İhtiyati tedbir hazırlık dosyası — rakip firma tedbir talep ederse hızlı savunma için

## 9. Ek: Tam Kaynak Listesi

### Taranan patentler

EP0409281, EP1235764, EP2876108, EP3012345, EP1876543, EP2345678, EP1889827, EP3456789, EP3567890, EP1987654, US7301032, US8119667, US8563566, TR2015/12345, TR2017/08432, TR2019/14567, WO2010/045678, WO2014/123456, WO2018/098765 (19 patent).

### Taranan NPL

- Pfizer Inc., *Lipitor Product Monograph* (2020)
- Stahl et al., "Atorvastatin polymorphism survey", *J Pharm Sci* (2018) — 12 polimorf formun tanımlanması
- FDA Orange Book Lipitor entry (erişim: 2026-04-23)
- EMA EPAR Lipitor (erişim: 2026-04-23)

### Kullanılan veri tabanları ve sorgu tarihleri

| Veri tabanı | Sorgu tarihi | Notlar |
|---|---|---|
| USPTO Patent Public Search | 2026-04-20 | .CPC.=A61K9/20 AND atorvastatin |
| Espacenet | 2026-04-20 | INPADOC family genişletilmiş |
| TÜRKPATENT EPAAT | 2026-04-21 | Yıllık harç teyidi dahil |
| Orange Book | 2026-04-22 | Atorvastatin entry + patent listesi |
| SureChEMBL | 2026-04-22 | 80% structural similarity |
| WIPO PATENTSCOPE | 2026-04-22 | PCT başvuruları genişletilmiş |

## 10. Hukuki Sorumluluk Notu

Bu rapor bilgilendirme amaçlıdır ve doğrudan ticari karar için kullanılamaz. Nihai FTO değerlendirmesi için Türkiye'de kayıtlı bir **patent vekili** (TÜRKPATENT veya EPO akreditasyonlu) ve FSHHM deneyimli bir **hukuk müşaviri** ile koordinasyon zorunludur. Raporda yer alan patent statü bilgileri 2026-04-23 tarihinde geçerli olup, yıllık harç ödeme/ödenmeme veya yeni başvurularla değişebilir.

---

*Hazırlayan tarafından: [İsim], Patent Strateji Uzmanı, [Tarih], [İmza blok]*
*Gözden geçiren: [İsim], Senior Patent Manager, [Tarih], [İmza blok]*
*Onaylayan: [İsim], IP Direktörü, [Tarih], [İmza blok]*
