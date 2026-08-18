# TBMM Kanun Teklifi Şablonu — Mod 8 (TBMM_KANUN_TEKLIFI)

Bu şablon, **Anayasa Md. 88** uyarınca milletvekillerince TBMM Başkanlığına sunulacak kanun tekliflerinin Cureolex v2.6.0 standardına uygun olarak hazırlanması için kullanılır. Şablon, **TBMM İçtüzüğünün 74-91. maddeleri** ile **5210 sayılı Mevzuat Hazırlama Usul ve Esasları Hakkında Yönetmelik** (RG 24/2/2022, 31760) prensiplerini birleştirir.

> **Önemli kapsam notu (5210 Md. 1/3):** TBMM Başkanlığına milletvekillerince sunulan kanun teklifleri, 5210 sayılı Yönetmeliğin kapsamı **dışındadır**. Onlar için **Anayasa Md. 88 + TBMM İçtüzüğü Md. 74-91** esastır. Ancak Cureolex v2.6.0, 5210 Yönetmeliğin maddi-anayasal uygunluk ilkelerinin (Md. 4) ve şekli-tipografik standartlarının (Md. 10-25) ekosistem bütünlüğü için **referans alınmasını** önerir; bu, TBMM Başkanlığının "Anayasa dili ve kanun yazılış tekniği" heyetinin (İçtüz. Md. 85) denetim standardıyla da uyumludur.

---

## Bölüm A — Üst Künye

```
TÜRKİYE BÜYÜK MİLLET MECLİSİ BAŞKANLIĞINA

KONU : {{Teklif edilen kanunun tam adı}} Hakkında Kanun Teklifi
TARİH: {{gün/ay/yıl}}
```

**Atıf notu (TBMM İçtüz. Md. 74):** Kanun teklifleri, **bir veya daha çok imza** ile birlikte gerekçesi ile birlikte TBMM Başkanlığına verilir. Birden fazla teklif sahibi varsa **ilk imza sahibi** birinci sırada, diğerleri tarih/seçim çevresi sırasında yazılır.

---

## Bölüm B — İmza Listesi

```
TEKLİF SAHİBİ MİLLETVEKİLLERİ:

1. {{Ad Soyad}}, {{Şehir}} Milletvekili, {{Parti}}    İmza: __________
2. {{Ad Soyad}}, {{Şehir}} Milletvekili, {{Parti}}    İmza: __________
3. {{Ad Soyad}}, {{Şehir}} Milletvekili, {{Parti}}    İmza: __________
[...]
```

**Not (İçtüz. Md. 74/2):** Komisyonlar, şartlarına uymayan kanun tekliflerini sahiplerine tamamlattırmaya yetkilidirler.

---

## Bölüm C — Genel Gerekçe

```
GENEL GEREKÇE

1. Konunun Önemi ve Düzenleme İhtiyacı
{{Mevcut hukukî durumun tasviri; saptanan sorun/boşluk; düzenleme 
gerekliliğinin somut gerekçesi}}

2. Anayasal Çerçeve
{{Anayasa Md. 17, 56, 60, 73, 90/5 ve diğer ilgili maddelere atıfla, 
düzenlemenin anayasal dayanağı}}

3. Uluslararası Hukukî Çerçeve (Anayasa Md. 90/5 Boyutu)
{{`treaty_status` + `treaty_reservations` (ICESCR Md. 12, CRC Md. 24, CRPD
Md. 25, CEDAW, ICCPR) ve `coe_treaty_signatories` (Oviedo 164, MEDICRIME 211;
snapshot + snapshot_age_days + mcp_verified:false). intl_treaty_info bir kez.
live_coe:false = beyanlı degrade. Andlaşma↔kanun çatışması → md. 90/5 cümlesi;
onay uydurulmaz. Md.90 sonrası uhri_search→uhri_fetch_document. Bkz. references/10}}

4. AB Müktesebatı Uyumu (Varsa)
{{İlgili AB regülasyonları/direktifleri (CELEX referansları) ile 
uyum analizi: MDR, IVDR, CTR, GDPR, 2001/83/EC, Falsified Medicines 
Directive 2011/62/EU, HTA Regulation 2021/2282 vd.}}

5. Karşılaştırmalı Mevzuat İncelemesi
{{En az 2 AB üye devleti + 1 Asya-Pasifik regülatörü emsal incelemesi. 
Bkz. references/12}}

6. Türk Yüksek Yargı İçtihatı
{{AYM sağlık hakkı ve etkili başvuru içtihat sinyali + Danıştay + Yargıtay konu ile ilgili 
içtihatları; AİHM Türkiye kararları (varsa). Bkz. references/13}}

7. Türk Akademik Doktrin
{{YokTez + Türk akademik literatürü temel referansları}}

8. Düzenlemenin Beklenen Etkileri
{{Hastalar, sağlık profesyonelleri, ilaç firmaları, eczaneler, 
hastaneler, kamu kurumları (TİTCK, SGK, SB) üzerindeki etkilerin 
özeti}}

9. Mali Etki Özeti
{{Bütçe etkisi tahmini; gerekirse ayrı BEF (Bütçe Etki Formu) 
eklenir. Bkz. templates/bef-template.md}}

10. Diğer Hususlar
{{Geçiş süresi gerekçesi, ikincil mevzuat çıkarma yetkisi, vd.}}
```

**Önemli kural (5210 Md. 23 paralel):** Genel gerekçe, **madde metninin tekrarı şeklinde olamaz**. Düzenlemenin **nedenleri, amaçları, beklenen sonuçları** ve **politika seçenekleri arasındaki tercihin gerekçesi** açıklanır.

---

## Bölüm D — Kanun Teklifi Metni

```
{{TEKLIFIN TAM ADI BÜYÜK HARF KALIN}}
KANUN TEKLİFİ

BİRİNCİ BÖLÜM
Amaç, Kapsam, Dayanak ve Tanımlar

Amaç
MADDE 1- (1) Bu Kanunun amacı; {{düzenlemenin somut hedefi}}.

Kapsam
MADDE 2- (1) Bu Kanun; {{kimleri ve neyi kapsadığı, tereddütsüz}}.

Dayanak
MADDE 3- (1) Bu Kanun; Anayasanın {{ilgili maddeler}} maddelerine 
dayanılarak hazırlanmıştır.

Tanımlar
MADDE 4- (1) Bu Kanunda geçen;
a) {{Tanım — alfabetik sırada}}: {{...}},
b) {{Tanım}}: {{...}},
...
ifade eder.

İKİNCİ BÖLÜM
{{Esas Hükümler Başlığı}}

MADDE 5- (1) {{...}}
...

ÜÇÜNCÜ BÖLÜM
{{Cezaî Hükümler / Düzenleyici İşlemler / vd.}}

MADDE N- (1) {{...}}
...

DÖRDÜNCÜ BÖLÜM
Değiştirilen ve Kaldırılan Hükümler

MADDE [X]- {{Değiştirilen mevzuat ve değişiklik metni — 5210 Md. 18-19 uyumu}}

MADDE [X+1]- {{Yürürlükten kaldırılan hükümler — Md. 21/8 uyarınca 
açıkça sayılır; "aykırı hükümler yürürlükten kaldırılmıştır" muğlaklığı 
yasak}}

BEŞİNCİ BÖLÜM
Geçici Hükümler

GEÇİCİ MADDE 1- (1) {{Geçiş süresi düzenlemesi — 5210 Md. 16/3 uyumu}}
...

ALTINCI BÖLÜM
Son Hükümler

Yürürlük
MADDE [Y]- (1) Bu Kanunun {{tarih/durum}} yürürlüğe girer.

Yürütme
MADDE [Y+1]- (1) Bu Kanun hükümlerini Cumhurbaşkanı yürütür.
```

**Kritik uyarılar:**
- **5210 Md. 24 + Anayasa Md. 7 uyumu:** Kanun teklifi yetki devri yapıyorsa, devredilen yetkinin sınırları açıkça çizilmelidir.
- **5210 Md. 21 atıf formatı:** Tarih `gün/ay/yıl` (sıfırsız), ses uyumu ekleri doğru (5 inci, 12 nci, 100 üncü).
- **Madde başlıkları:** Md. 14 uyarınca kalın, sadece ilk kelimenin baş harfi büyük, sonunda noktalama yok.
- **R9 Bölüm 9 dil kontrolü:** Tüm madde metinleri 15-noktalı kontrol listesinden geçirilir.

---

## Bölüm E — Madde Gerekçeleri

```
MADDE GEREKÇELERİ

MADDE 1- {{Amaç maddesinin gerekçesi — düzenlemenin somut hedefi 
neden seçildi}}

MADDE 2- {{Kapsam maddesinin gerekçesi — kapsam kararı neden}}

MADDE 3- {{Dayanak maddesinin gerekçesi — Anayasa atfı detayı}}

MADDE 4- {{Tanımların gerekçesi — her tanım neden bu şekilde 
formüle edildi; AB/uluslararası emsal varsa atıf}}

...

MADDE [N]- {{Her esas hüküm için ayrı gerekçe — madde metninin 
tekrarı yasak; sorun-çözüm-emsal-içtihat-doktrin sentezi}}
```

**5210 Md. 23 uyumu:** Madde gerekçesi, **madde metninin tekrarı şeklinde olamaz**. Her madde için:
- Düzenlenen sorun ne?
- Neden bu çözüm seçildi?
- Karşılaştırmalı emsaller (AB, ABD, Japonya, vd.) neyi gösteriyor?
- Türk yüksek yargı içtihatı + akademik doktrin nasıl destekliyor?

---

## Bölüm F — TBMM İçtüzüğü Md. 81 Görüşme Usulü Notu

Kanun teklifinin Genel Kurul'da görüşülmesi şu sıralamayla yapılır (İçtüz. Md. 81):

1. **Teklifin tümü hakkında görüşme açılır** — siyasi parti grupları ve komisyon adına 20 dk, üyeler 10 dk
2. **Komisyonla 20 dk soru ve cevap işlemi** — maddelerde bu süre 10 dk
3. **Maddelere geçilmesi oylanır**
4. **Teklifin maddeleri görüşülür** — madde başlıklı oylama
5. **Teklifin tümü oylanır**

**Açık oy talebi:** Anayasa değişiklikleri hariç, **en az 20 milletvekilinin talebi** ile açık oylama; aksi takdirde işaret oyuyla yapılır.

**Temel kanun özel yöntemi (İçtüz. Md. 91):** Temel kanun niteliğindeki teklifler için, **bölümler hâlinde** (her bölüm en çok 30 madde) görüşme yapılabilir; Danışma Kurulu oybirliği önerisi + Genel Kurul kararı gerekir.

**Değişiklik önergesi türleri (İçtüz. Md. 87):**
- Bir maddenin reddi önergesi
- Tümünün/maddenin komisyona iadesi önergesi
- Madde değiştirilmesi önergesi
- Ek madde önergesi
- Geçici madde önergesi

---

## Bölüm G — Komisyon Havalesi Önerisi

```
İLGİLİ KOMİSYON HAVALESİ ÖNERİSİ:

ESAS KOMİSYON   : Sağlık, Aile, Çalışma ve Sosyal İşler Komisyonu
TALİ KOMİSYONLAR: 
  - Adalet Komisyonu (cezaî hükümler varsa)
  - Plan ve Bütçe Komisyonu (mali yük varsa)
  - Avrupa Birliği Uyum Komisyonu (AB müktesebatı uyumu boyutu varsa)
  - Anayasa Komisyonu (anayasal denetim boyutu yoğun ise)
  - Dilekçe Komisyonu (vatandaş dilekçesi temelli ise)
```

**İçtüz. Md. 23 atfı:** TBMM ihtisas komisyonları listesi referansı.

---

## Bölüm H — Ekler

```
EKLER:
1. Karşılaştırma Cetveli (eğer mevcut kanun değişiyorsa — Md. 18-19)
   → templates/karsilastirma-cetveli.md
2. Karşılaştırmalı Uluslararası Mevzuat Tablosu
   → templates/karsilastirma-uluslararasi.md
3. Düzenleyici Etki Analizi (DEA) — TBMM komisyonu talep ederse 
   (Md. 26/2 uyarınca SBB koordinasyonunda)
   → templates/dea-template.md
4. Bütçe Etki Formu (BEF) — mali yük varsa
   → templates/bef-template.md
5. Türk Yargı İçtihatı Atıfları Tablosu (AYM, Danıştay, Yargıtay, 
   AİHM, ABAD)
6. Türk Akademik Doktrin Atıfları
7. AB Müktesebatı Uyum Tablosu (CELEX numaraları ile)
8. Uluslararası İnsan Hakları Sözleşmeleri Uyum Notu (Anayasa 
   Md. 90/5 boyutu)
```

---

## Bölüm I — Cureolex v2.6.0 Kalite Kontrol Notu

Bu kanun teklifi, Cureolex v2.6.0 protokolü uyarınca aşağıdaki kalite kapılarından geçirilmiştir:

```
☐ R9 Bölüm 9 — 15-noktalı dil kontrolü (PASS)
☐ R9 Bölüm 6.bis — TMK 4721 gerekçesi terim modernizasyonu kontrolü (PASS)
☐ R9 Bölüm 6.quinquies — HMK gerekçesi kurumsal terim koruma kontrolü (PASS)
☐ Compliance 21-noktalı denetim (SKILL.md Bölüm 6.4) (PASS)
☐ İçtihat + Doktrin temellendirmesi (R13) (PASS)
☐ Karşılaştırmalı uluslararası emsal (R8 + R12) (PASS)
☐ Anayasa Md. 90/5 + uluslararası sözleşmeler uyumu (R10 + R11) (PASS)
☐ Epistemik dürüstlük ilkesi (SKILL.md Bölüm 12) (PASS)
```

**Bilgi sınırı uyarısı:** Bu şablon, cureolex v2.6.0'in **standalone protokolü** olarak hazırlanmıştır. TBMM Başkanlığına fiilî sunum öncesinde, **Anayasa Dili ve Kanun Yazılış Tekniği Heyeti'nin** (İçtüz. Md. 85) önerebileceği şekli düzeltmeler dikkate alınmalıdır.

---

**Bu şablon, Cureolex v2.6.0'in TBMM Kanun Teklifi modunun (Mod 8) operasyonel iskeletidir. Kullanım için Mod 8 protokolüne (SKILL.md Bölüm 6.8) başvurun.**
