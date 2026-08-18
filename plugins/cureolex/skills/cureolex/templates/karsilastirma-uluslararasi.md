# Uluslararası Karşılaştırmalı Tablo Şablonu

Bu şablon, **DRAFT (Adım 5)**, **AMEND (Adım 6 — AB kaynaklı amendment)**, **ANALYZE (Adım 4 — uyum açığı)**, **OPINE (AB Başkanlığı görüşü)** ve **RIA (Adım 4)** modlarında üretilen karşılaştırmalı tabloların standart formatıdır.

> **Kullanım:** Bu tablo, **Türkiye iç değişiklik** için kullanılan `karsilastirma-cetveli.md` şablonundan **ayrıdır**. Burada yan yana koyulan, Türkçe eski-yeni metin değil; Türk mevzuatı vs. uluslararası karşılıklarıdır.

---

## Bölüm A — Standart Kapsam Tablosu (3 sütun)

En sık kullanılan format. Türk mevzuat hükmü + AB karşılığı + en az bir AB üye devleti / ABD karşılığı.

```
{{KONU/TASLAĞIN ADI}} — KARŞILAŞTIRMALI MEVZUAT TABLOSU
```

| Türk Mevzuatı | AB Müktesebatı | Karşılaştırılan Yargı Bölgesi | Uyum / Sapma Notu |
|---|---|---|---|
| **{{Türk metni — atıf: gün/ay/yıl, sayı, ad, madde}}** <br><br> {{tam hüküm metni}} | **{{CELEX numarası, AB regülasyon/direktif adı, madde no}}** <br><br> {{paralel AB hükmü kısa özet}} | **{{Ülke + ulusal mevzuat + madde}}** <br><br> {{paralel ulusal hüküm kısa özet}} | {{(i) Uyumlu / (ii) Kısmen Uyumlu / (iii) Uyumsuz <br> (iv) Açıklama: hangi açıdan, hangi tanım/eşik/süre farkı}} |

---

## Bölüm B — Genişletilmiş Çok-Yargı Bölgeli Tablo (6 sütun)

RIA modunda kapsamlı benchmark için. Beş yargı bölgesi paralel okuma.

```
{{KONU/TASLAĞIN ADI}} — ÇOK-YARGI BÖLGELİ KARŞILAŞTIRMA
```

| Konu / Tanım | Türkiye | AB (CELEX) | Almanya | ABD | Birleşik Krallık |
|---|---|---|---|---|---|
| **{{Konunun adı / Tanım}}** | {{Türk tanımı + atıf}} | {{AB tanımı + madde}} | {{Alman tanımı + AMG/MPDG madde}} | {{ABD tanımı + eCFR Title.Part.Section}} | {{UK tanımı + UK MDR / NHS Act madde}} |
| **{{Eşik değer / Süre / Prosedür}}** | {{Türk değeri}} | {{AB değeri}} | {{Alman değeri}} | {{ABD değeri}} | {{UK değeri}} |
| **{{Yaptırım / Müeyyide}}** | {{Türk yaptırımı}} | {{AB yaptırımı (varsa)}} | {{Alman yaptırımı}} | {{ABD yaptırımı}} | {{UK yaptırımı}} |

---

## Bölüm C — HTA Karşılaştırma Tablosu (Geri Ödeme / SUT Bağlamı)

```
{{ÜRÜN/ENDIKASYON ADI}} — HTA DEĞERLENDİRMESİ ULUSLARARASI KARŞILAŞTIRMA
```

| HTA Kurumu | Yargı Bölgesi | Karar / Öneri | Karar Tarihi | İlave Kanıt Talebi | Klinik Eşik Kabulü | Maliyet Etkinlik Eşiği | Atıf URL'si |
|---|---|---|---|---|---|---|---|
| **NICE** | UK | {{TA xxx — recommend / optimised / not recommended}} | {{gün/ay/yıl}} | {{örn. erken erişim verisi}} | {{örn. PFS, OS}} | {{£20-30k/QALY}} | {{nice.org.uk/...}} |
| **G-BA / IQWiG** | DE | {{Zusatznutzen: erheblich / beträchtlich / gering / nicht belegt}} | {{tarih}} | {{karşılaştırıcı kabulü}} | {{...}} | (AMNOG sonrası fiyat müzakeresi) | {{g-ba.de/...}} |
| **HAS** | FR | {{SMR: important / modéré / faible — ASMR: I-V}} | {{tarih}} | {{...}} | {{...}} | (Comité Économique fiyat müzakeresi) | {{has-sante.fr/...}} |
| **CADTH** | CA | {{recommend / reimburse with criteria / do not reimburse}} | {{tarih}} | {{...}} | {{...}} | {{CAD$50k/QALY}} | {{cadth.ca/...}} |
| **PBAC** | AU | {{recommend / recommend with restriction / reject}} | {{tarih}} | {{...}} | {{...}} | {{Effectiveness vs cost analizine göre}} | {{pbs.gov.au/...}} |
| **ICER** | US | {{long-term value rating: high / moderate / low}} | {{tarih}} | {{...}} | {{...}} | {{US$100-150k/QALY}} | {{icer.org/...}} |
| **EU JCA** (varsa) | EU | {{JCA report sonucu}} | {{tarih}} | {{...}} | {{...}} | (EU HTA Reg. — JCA tek değerlendirme) | {{hta.europa.eu/...}} |
| **Türkiye** | TR (önerilen) | {{Önerilen SUT durumu}} | {{önerilen yürürlük}} | {{TİTCK öncesi koşul}} | {{...}} | (SGK kamu maliyeti tartışması) | {{ilgili Resmî Gazete}} |

---

## Bölüm D — Düzenleyici Otorite Prosedür Karşılaştırması

```
{{PROSEDÜRÜN ADI — örn. RUHSATLANDIRMA}} — REGÜLATÖR PROSEDÜR KARŞILAŞTIRMASI
```

| Aşama | TİTCK (TR) | EMA (EU centralised) | FDA (US) | MHRA (UK) | Swissmedic (CH) | PMDA (JP) |
|---|---|---|---|---|---|---|
| Başvuru formatı | {{eCTD modulü, dil}} | eCTD, EN | eCTD, EN | eCTD, EN | eCTD, DE/FR/IT/EN | CTD-J, JA |
| Bilimsel danışma | {{TİTCK Bilimsel Danışma}} | EMA Scientific Advice | FDA Pre-IND/Type B/C | MHRA Scientific Advice | Swissmedic Scientific Advice | PMDA Consultation |
| Standart süre (gün) | {{TR süreleri}} | 210 gün (clock-stops ile genelde >12 ay) | 10 ay (standard) / 6 ay (priority) | 150 gün | 330 gün | 12 ay (priority 9 ay) |
| Hızlandırılmış yol | {{örn. Reliance}} | PRIME, Accelerated, Conditional | Breakthrough, Fast Track, Accelerated, Priority | ILAP | (yok — bilateral) | Sakigake |
| Ücret | {{TR Hizmet Bedeli}} | {{€XX,XXX}} | {{$X,XXX,XXX PDUFA}} | {{£XX,XXX}} | {{CHF XX,XXX}} | {{¥X,XXX,XXX}} |
| Yenileme | {{...}} | 5 yıl sonra perpetual | (yok — perpetual) | 5 yıl sonra perpetual | 5 yıl | 5 yıl |

---

## Bölüm E — Anlam Sözlüğü (Glosaryum) Tablosu

Tanım farklılıklarını sistematik izlemek için.

```
{{TASLAK ADI}} — TANIM/SÖZLÜK PARALEL OKUMA
```

| Kavram | Türkçe Tanım (taslak madde) | AB Tanımı (CELEX, madde) | Karşılaştırılan Ülke Tanımı | Eşdeğer mi? |
|---|---|---|---|---|
| **{{örn. "Sponsor"}}** | {{Türk yön. madde tanımı}} | {{CTR Art. 2(14)}} | {{AMG § 4 / 21 CFR 312.3}} | {{Evet/Kısmen/Hayır + açıklama}} |
| **{{örn. "Beklenmeyen ciddi advers reaksiyon"}}** | {{Türk tanımı}} | {{Reg. 726/2004 Art. 1}} | {{...}} | {{...}} |

---

## Bölüm F — Uyum Açığı (Compliance Gap) Özeti

Tablo sonuna ekteki özet bölümü:

```markdown
## Uyum Açığı Değerlendirmesi

### 1. Tam Uyumlu Hükümler
- {{Madde no — kısa açıklama}}

### 2. Kısmen Uyumlu Hükümler (Açıklamalı)
- **{{Madde no}}**: AB CELEX [...] ile karşılaştırıldığında [...] farkı vardır. 
  Bu fark **(a) gerekçeli politik tercih / (b) kapatılması gereken uyum açığı**dır 
  çünkü {{neden}}.

### 3. Uyumsuz Hükümler — Risk Değerlendirmesi
- **{{Madde no}}**: AB müktesebatından sapma; AB Komisyonu yıllık ilerleme 
  raporunda [...] eleştirisine maruz kalabilir. Önerilen revizyon: {{...}}

### 4. AB Müktesebatında Karşılığı Olmayan Hükümler
- **{{Madde no}}**: Tamamen ulusal düzlem; AB'de düzenlenmemiştir. 
  Bu hüküm Türkiye'nin {{ulusal sağlık politikası amacı}} ile bağdaşıktır.

### 5. Türk Mevzuatında Karşılığı Olmayıp AB'de Bulunan Hükümler (Eksik)
- **{{Konu}}**: AB CELEX [...] tarafından düzenlenmiş; Türk mevzuatında karşılığı yok.
  Bu eksiklik {{etki}} sonucunu doğurur. Önerilen ek madde: {{...}}
```

---

## Bölüm G — Üst Bilgi Formatı

Resmî sunumda tablonun üst bilgisi:

```
T.C.
{{KURUMUN/BAKANLIĞIN ADI}}
{{İLGİLİ BİRİMİN ADI}}

TASLAK ADI         : {{...}}
KARŞILAŞTIRMA TÜRÜ : [ ] AB Müktesebatı Uyum  [ ] Çok-Yargı Bölgeli Benchmark
                     [ ] HTA Karşılaştırma    [ ] Regülatör Prosedür Karşılaştırma
                     [ ] Tanım/Sözlük Paralel Okuma
DAYANAK            : Md. 4/c (5210 Yönetmeliği — uluslararası kaynak gözetimi)
KAYNAK DOĞRULAMA   : {{tüm uluslararası referanslar Fetch/Tavily/Exa ile teyit edildi tarihi}}
HAZIRLAYAN         : {{birim + uzman}}
TARİH              : {{gün/ay/yıl}}

ULUSLARARASI KARŞILAŞTIRMA TABLOSU
```

---

## Bölüm H — Doğrulama Listesi

- [ ] Her uluslararası referans **Bölüm 5.4 üç doğrulama** kuralından geçti mi? (sürüm tipi, yürürlük, çeviri durumu)
- [ ] AB regülasyonları **konsolide sürümle** alındı mı (CELEX `02xxx...` örüntüsü)?
- [ ] Almanca/Fransızca/İtalyanca metinler **orijinal dil + Türkçe bağlamsal açıklama** çiftli sunum biçiminde mi?
- [ ] HTA tablolarında karar tarihleri tutarlı (önemli karar değişimleri olmuş olabilir) mi?
- [ ] CELEX numaraları geçerli mi (Fetch ile teyit)?
- [ ] FDA Guidance referansları **Guidance Database** kontrolünden geçti mi?
- [ ] Tablo, AB Başkanlığı'nın **Müktesebata Uyum Mevzuat Tablosu** standardıyla uyumlu mu?
- [ ] Uyum açığı bölümü, hükümlerin **(a) gerekçeli sapma vs (b) kapatılacak açık** ayrımını yapıyor mu?

---

## Bölüm I — Kullanım Sırası (İş Akışı)

1. **Konuyu netleştirin** ve hangi sütunların gerekli olduğuna karar verin (3-sütun mu, çok-yargı bölgeli 6-sütun mu, HTA 8-sütun mu).
2. **Türkçe metni Mevzuat MCP'den** çekin (`get_mevzuat_content`).
3. **AB karşılığını EUR-Lex'ten** Fetch ile çekin (konsolide sürüm).
4. **Ulusal düzlemleri** sırayla — Almanya (gesetze-im-internet.de), Fransa (legifrance.gouv.fr), gerekirse İtalya/İspanya/UK/CH.
5. **HTA boyutu varsa** dörtlü-yedili HTA tablosunu paralel doldurun.
6. **Tanım farklılıklarını ayrı** glosaryum tablosunda izleyin (Bölüm E).
7. **Uyum açığı özetini** Bölüm F formatında yazın.
8. **Üst bilgiyi** Bölüm G'den ekleyin, doğrulama listesini Bölüm H'den geçirin.
9. **Çıktıyı** ana RIA / DEA / OPINE belgesine ek olarak veya bağımsız "Karşılaştırmalı Tablo" çıktısı olarak teslim edin.

---

## Bölüm J — Örnek (Kısaltılmış): MDR Madde 5 — Tıbbi Cihaz Tanımı

| Türk Mevzuatı | AB Müktesebatı | Almanya | Uyum Notu |
|---|---|---|---|
| **Tıbbi Cihaz Yönetmeliği (2/6/2021, 31499) Md. 4(1)(s)** <br><br> Tıbbi cihaz: insanlarda hastalık, yaralanma veya engellilik durumunda tanı, izleme, tedavi, hafifletme amacıyla kullanılan, mekanik etki ile çalışan ve farmakolojik/immünolojik/metabolik etkiyi temel etki olarak kullanmayan alet, cihaz, donanım, yazılım vb. | **Regulation (EU) 2017/745 Article 2(1) — "medical device"** <br><br> any instrument, apparatus, appliance, software, implant, reagent, material... intended by the manufacturer to be used... in humans for one of more of the following specific medical purposes... and which does not achieve its principal intended action by pharmacological, immunological or metabolic means, in or on the human body... | **MPDG § 3 Nr. 1 (Begriffsbestimmungen)** <br><br> "Medizinprodukt: ein Medizinprodukt im Sinne des Artikels 2 Nummer 1 der Verordnung (EU) 2017/745" <br><br> (MPDG, MDR Art. 2(1)'e doğrudan atıf yapar — bağımsız tanım yok) | **(i) Tam uyumlu.** Türk tanımı MDR Art. 2(1) tercümesi olup tüm temel öğeleri içerir; Alman MPDG'de bağımsız tanım yerine doğrudan AB atfı vardır — yapısal seçim farkı olup içerik aynıdır. <br> **(ii) Önemli not:** "Yazılım" (software) hem Türk metninde hem MDR'de açıkça sayılır — SaMD (Software as a Medical Device) rejimi paralel uygulanır. <br> **(iii) Kaynak doğrulama:** EUR-Lex `02017R0745-[konsolide tarih]` ile teyit edildi; gesetze-im-internet.de `mpdg/__3.html` ile teyit edildi. |

---

> **Bu şablon, AB Başkanlığı'nın "Müktesebata Uyum Mevzuat Tablosu" geleneği ile uyumlu olacak şekilde, Cureolex protokolünün karşılaştırmalı katmanını standartlaştırır.**
