# Md. 21 — Atıf Tekniği (En Hataya Açık Alan)

Atıf kuralları, mevzuat yazımında en sık hata yapılan alandır. Bu dosya, **operasyonel kontrol listesi** niteliğindedir. Her atıf yazılırken bu dosya açılmalı veya kontrol script'i çağrılmalıdır.

## 1. Temel Kural

**Atıf yapılan mevzuatın**:
- **Tarihi** (gün/ay/yıl)
- **Sayısı**
- **Adı**
- **Maddesi / fıkrası / bendi / alt bendi**

**açıkça belirtilir.**

## 2. İlk Atıf vs Sonraki Atıflar

### 2.1. İlk atıf — Kanun
**Format:**
```
14/5/1928 tarihli ve 1262 sayılı İspençiyari ve Tıbbi Müstahzarlar Kanununun
```

**Yanlış:**
- ❌ `1262 sayılı Kanunun` (ilk atıfta eksik)
- ❌ `14.05.1928 tarihli` (nokta yerine eğik çizgi olmalı)
- ❌ `14/05/1928` (soldaki sıfır YASAK)
- ❌ `1262 sayılı İspençiyari Kanunu` (ad eksik)

### 2.2. İlk atıf — Cumhurbaşkanlığı Kararnamesi
**Format:**
```
1 sayılı Cumhurbaşkanlığı Teşkilatı Hakkında Cumhurbaşkanlığı Kararnamesinin
```

Not: CBK'larda **tarih kullanılmaz**, sayı ve ad yeterli.

### 2.3. Sonraki atıflar
**Format:**
```
Aynı Kanunun 5 inci maddesinin
Aynı Yönetmeliğin 12 nci maddesinin (3) numaralı fıkrasının (b) bendinin
Aynı Kararnamenin 508 inci maddesinin
```

## 3. Tarih Formatı

| Doğru | Yanlış | Sebep |
|-------|--------|-------|
| `1/3/2024` | `01/03/2024` | Soldaki sıfır yasak |
| `14/5/1928` | `14.5.1928` | Eğik çizgi zorunlu |
| `2/6/2021` | `2-6-2021` | Tire değil eğik çizgi |
| `11/12/2021` | `11/12/21` | 4 haneli yıl |

## 4. Madde / Fıkra / Bent / Alt Bent Atıfları

### 4.1. Madde — Türkçe ses uyumlu ek
| Madde | Doğru | Yanlış |
|-------|-------|--------|
| 1 | birinci maddesi | 1. maddesi (kesme yok ama "inci" tercih) |
| 4 | 4 üncü maddesi | 4. maddesi |
| 5 | 5 inci maddesi | 5'inci maddesi (kesme YASAK) |
| 12 | 12 nci maddesi | 12 inci maddesi |
| 24 | 24 üncü maddesi | 24 ncü maddesi |
| 100 | 100 üncü maddesi | 100. maddesi |
| 537 | 537 nci maddesi | 537'inci maddesi |

**Genel kural:** Sayıdan sonra **boşluk** + Türkçe ses uyumuna göre ek + **kesme yok**.

Ses uyumu ek tablosu:
- 1, 2, 3, 4, 5, 6, 7 → öncesi ünlüye göre `inci`, `ıncı`, `üncü`, `ünci`, `nci`
- Pratik form: **3 üncü, 4 üncü, 7 nci, 8 inci, 9 uncu, 10 uncu, 12 nci, 15 inci, 20 nci, 23 üncü, 100 üncü, 537 nci**

### 4.2. Fıkra atıfı — Rakam yerine yazı
| Fıkra | Doğru | Yanlış |
|-------|-------|--------|
| (1) | birinci fıkrası | (1) fıkrası |
| (2) | ikinci fıkrası | 2. fıkrası |
| (3) | üçüncü fıkrası | (3) numaralı fıkrası |

**KRİTİK:** Md. 21/9 — **Fıkra, paragraf ve cümlelere atıfta rakam yerine YAZI** kullanılır.

### 4.3. Bent atıfı — Harf ayraç içinde
| Bent | Doğru | Yanlış |
|------|-------|--------|
| a) | (a) bendinin | a bendinin |
| b) | (b) bendinin | (b) bendinin **doğru** |
| ç) | (ç) bendinin | ç) bendinin |

### 4.4. Alt bent atıfı — Numara ayraç içinde
| Alt bent | Doğru |
|----------|-------|
| 1) | (1) numaralı alt bendinin |
| 2) | (2) numaralı alt bendinin |

## 5. Yürürlükten Kaldırma Atıfları

### 5.1. YASAK — Muğlak ifadeler
- ❌ `Bu Yönetmeliğe aykırı hükümler yürürlükten kaldırılmıştır.`
- ❌ `Diğer mevzuatın bu Yönetmeliğe aykırı hükümleri uygulanmaz.`
- ❌ `Aksine düzenlemeler hükümsüzdür.`

**Bu ifadeler Md. 21/8'e aykırıdır ve Danıştay iptal gerekçesidir.**

### 5.2. DOĞRU — Açık yürürlükten kaldırma
- ✅ `26/8/2005 tarihli ve 25919 sayılı Resmî Gazete'de yayımlanan Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği yürürlükten kaldırılmıştır.`
- ✅ `Aynı Kanunun 7 nci maddesinin üçüncü fıkrası yürürlükten kaldırılmıştır.`
- ✅ Birden fazla maddenin yürürlükten kaldırılması durumunda her biri açıkça sayılır.

## 6. Alt Düzeydeki Mevzuata Atıf Yasağı (Md. 21/6)

**Yasak:** Kanun, alt düzey mevzuata **somut atıf yapamaz**.

### 6.1. Yasak örnek
```
Kanun Md. 5 — Ruhsat başvurusu için 11/12/2021 tarihli ve 
31685 sayılı Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliğinde 
belirtilen belgeler eklenir.
```
**Sorun:** Üst (kanun) → alt (yönetmelik) somut atıf var.

### 6.2. Çerçeve atıf (izin verilen)
```
Kanun Md. 5 — Ruhsat başvurusunun usul ve esasları 
yönetmelikle düzenlenir.
```
**Bu OK** — "yönetmelikle düzenlenir" çerçeve atıftır, somut atıf değildir.

## 7. Atıf İçinde Geçmiş Değişiklikler Vurgulanmaz

**Yasak:**
- ❌ `1262 sayılı Kanunun (3/8/2018 tarihli ve 7146 sayılı Kanunla değişik) 4 üncü maddesi`

**Doğru:**
- ✅ `1262 sayılı Kanunun 4 üncü maddesi`

Önceki değişiklik bilgisi atıfta yer almaz; sadece mevcut yürürlükteki ada/sayıya/maddeye atıf yapılır.

## 8. Çoklu Atıf Sıralaması

Birden fazla mevzuata atıf varsa **eski tarihliden yeniye doğru**:

```
14/5/1928 tarihli ve 1262 sayılı İspençiyari ve Tıbbi Müstahzarlar Kanunu,
18/12/1953 tarihli ve 6197 sayılı Eczacılar ve Eczaneler Hakkında Kanun ve
31/5/2006 tarihli ve 5510 sayılı Sosyal Sigortalar ve Genel Sağlık 
Sigortası Kanunu hükümleri uygulanır.
```

## 9. Pratik Atıf Yazımı Örnekleri (Sağlık Mevzuatı)

### 9.1. Beşeri tıbbi ürün ruhsat
```
14/5/1928 tarihli ve 1262 sayılı İspençiyari ve Tıbbi Müstahzarlar 
Kanununun 1 inci maddesi ile 10/7/2018 tarihli ve 30474 sayılı 
Resmî Gazete'de yayımlanan 1 sayılı Cumhurbaşkanlığı Teşkilatı 
Hakkında Cumhurbaşkanlığı Kararnamesinin 508 inci maddesine 
dayanılarak hazırlanmıştır.
```

### 9.2. Klinik araştırma
```
13/4/2013 tarihli ve 28617 sayılı Resmî Gazete'de yayımlanan 
Klinik Araştırmalar Hakkında Yönetmeliğin 5 inci maddesinin 
birinci fıkrasının (b) bendi
```

### 9.3. SGK SUT atfı
```
24/3/2013 tarihli ve 28597 sayılı Resmî Gazete'de yayımlanan 
Sosyal Güvenlik Kurumu Sağlık Uygulama Tebliğinin 4.2 numaralı 
maddesinin (B) bendinin (3) numaralı alt bendi
```

### 9.4. KVKK sağlık verisi atfı
```
24/3/2016 tarihli ve 6698 sayılı Kişisel Verilerin Korunması 
Kanununun 6 ncı maddesinin altıncı fıkrası
```

### 9.5. Tıbbi cihaz
```
2/6/2021 tarihli ve 31499 sayılı Resmî Gazete'de yayımlanan 
Tıbbi Cihaz Yönetmeliğinin 4 üncü maddesinin birinci fıkrasının 
(g) bendi
```

## 10. Atıf Format Kontrol Listesi (Pre-Submission Check)

Her atıf için aşağıdaki soruları yanıtlayın:

- [ ] İlk atıfta tarih + sayı + ad var mı?
- [ ] Tarih `gün/ay/yıl` formatında ve soldaki sıfır yok mu?
- [ ] Madde numarası sonrası kesme işareti kullanılmadı mı?
- [ ] Ses uyumlu ek (inci/ıncı/üncü/ünci/nci) doğru mu?
- [ ] Fıkra atfı **rakam yerine yazı** ile mi yapıldı?
- [ ] Bent ve alt bent **ayraç içinde** mi gösterildi?
- [ ] "Aykırı hükümler" gibi muğlak ifade yok mu?
- [ ] Yürürlükten kaldırılan her hüküm açıkça sayıldı mı?
- [ ] Kanunda yönetmeliğe somut atıf yok mu?
- [ ] Geçmiş değişiklik bilgisi atıfa konmadı mı?
- [ ] Çoklu atıfta eski tarihliden yeniye sıra var mı?
- [ ] Sonraki atıflarda "aynı Kanunun/Yönetmeliğin" kısaltması kullanıldı mı?

**MCP doğrulaması:** Her atıfta, mevzuatın güncel adı + sayısı **`get_mevzuat_detail`** ile teyit edilmelidir.

---

## 11. Uluslararası Antlaşma ve Sözleşme Atıfları

Türkiye'nin taraf olduğu uluslararası sözleşmelere yapılan atıflar, **Anayasa Md. 90/5 hükmü** uyarınca **kanun hükmünde** kabul edildiğinden, atıf tekniği özen ister.

### 11.1. Genel Format

```
[İmzalanış tarihi] tarihli ve [Türkiye onay tarihi/sayısı] sayılı 
[Antlaşma adı]'nın [Madde] maddesi
```

### 11.2. BM Sözleşmeleri

**ICESCR (Ekonomik, Sosyal ve Kültürel Haklar):**
```
16/12/1966 tarihli ve 4867 sayılı Kanunla onaylanması uygun bulunan 
Ekonomik, Sosyal ve Kültürel Haklar Uluslararası Sözleşmesinin 
12 nci maddesinin ikinci fıkrasının (d) bendi
```

**CRC (Çocuk Hakları):**
```
20/11/1989 tarihinde imzaya açılan 9/12/1994 tarihli ve 4058 sayılı 
Kanunla onaylanması uygun bulunan Çocuk Haklarına Dair Sözleşmenin 
24 üncü maddesi
```

**CEDAW:**
```
18/12/1979 tarihinde imzaya açılan 11/6/1985 tarihli ve 3232 sayılı 
Kanunla onaylanması uygun bulunan Kadınlara Karşı Her Türlü Ayrımcılığın 
Önlenmesi Sözleşmesinin 12 nci maddesi
```

**CRPD (Engelli Hakları):**
```
13/12/2006 tarihinde imzaya açılan 3/12/2008 tarihli ve 5825 sayılı 
Kanunla onaylanması uygun bulunan Engellilerin Haklarına İlişkin 
Sözleşmenin 25 inci maddesi
```

### 11.3. AİHS (Avrupa İnsan Hakları Sözleşmesi)

```
4/11/1950 tarihinde imzalanan 10/3/1954 tarihli ve 6366 sayılı 
Kanunla onaylanması uygun bulunan İnsan Haklarının ve Temel 
Özgürlüklerin Korunmasına İlişkin Sözleşmenin 8 inci maddesi
```

### 11.4. WHO Sözleşmeleri

**IHR 2005 (Uluslararası Sağlık Tüzüğü):**
```
23/5/2005 tarihinde WHA58.3 kararıyla kabul edilen 11/4/2007 tarihli 
ve 5610 sayılı Kanunla onaylanması uygun bulunan Uluslararası Sağlık 
Tüzüğü (2005)'nin 6 ncı maddesi
```

**FCTC (Tütün Kontrol Çerçeve Sözleşmesi):**
```
21/5/2003 tarihinde imzaya açılan 25/11/2004 tarihli ve 5261 sayılı 
Kanunla onaylanması uygun bulunan Dünya Sağlık Örgütü Tütün Kontrolü 
Çerçeve Sözleşmesinin 8 inci maddesi
```

### 11.5. BM Narkotik Üçlü Sözleşmesi

```
30/3/1961 tarihli Tek Sözleşme'nin 21/4/1967 tarihli ve 812 sayılı 
Kanunla onaylanması uygun bulunan metninin 2 nci maddesi
```

### 11.6. AB Müktesebatı Atıfı (CELEX Kodu)

AB regülasyon ve direktiflerine atıf yapılırken **CELEX kodu** zorunludur:

```
21/3/2014 tarihli ve (AB) 536/2014 sayılı Avrupa Parlamentosu ve 
Konseyi Tüzüğünün (CELEX: 32014R0536) 28 inci maddesi
```

**CELEX kod yapısı (mevzuat için):**
- `3` = AB ikincil mevzuatı
- `2014` = yıl
- `R` = Regülasyon (Tüzük) / `L` = Direktif / `D` = Karar
- `0536` = sayı

### 11.7. AB Direktifi Örneği

```
6/11/2001 tarihli ve 2001/83/EC sayılı Avrupa Parlamentosu ve 
Konseyi Direktifinin (CELEX: 32001L0083) 8 inci maddesi
```

### 11.8. Helsinki Bildirgesi ve Soft Law Atıfı

Bağlayıcı olmayan ama bilimsel-etik standart oluşturan belgeler için:

```
Dünya Tabipler Birliği Helsinki Bildirgesi (2024 Revizyonu) — 
İnsanlar Üzerinde Yapılan Tıbbi Araştırmalara İlişkin Etik 
İlkeler'in 22 nci paragrafı
```

```
Dünya Sağlık Örgütü Esansiyel İlaçlar Listesi (24. Baskı, 2025) — 
Madde [ATC kodu]
```

### 11.9. WHA Resolution Atıfı

```
24/5/2014 tarihli ve WHA67.13 sayılı Dünya Sağlık Asamblesi Kararı
```

### 11.10. Anti-Pattern — Uluslararası Atıfta Yapılmaması Gerekenler

- ❌ `Helsinki Bildirgesi 22 inci maddesi` (paragraf — madde değil)
- ❌ `IHR Md. 6` (resmî tam ad eksik)
- ❌ `CRC Md. 24` (resmî adı + onay bilgisi eksik)
- ❌ `EU Directive 2001/83` (CELEX kodu eksik + Türkçe terim yok)
- ❌ `WHO EML Madde X` (baskı ve yıl eksik)

---

## 12. Yargı Kararı Atıfları

Mevzuat metni içinde içtihata atıf — gerekçe bölümünde yapılır; ana hüküm metninde **kural olarak içtihat atfı bulunmaz** (modern mevzuat tekniği).

Ancak **gerekçe**, **mütalaa**, **DEA**, **RIA**, **ANALYZE** çıktılarında içtihat atıfı zorunludur.

### 12.1. Türk Yüksek Yargı Atıf Standardı

**Anayasa Mahkemesi — Norm Denetimi:**
```
AYM, E. 2019/103, K. 2021/15, T. 18/2/2021
```

**Anayasa Mahkemesi — Bireysel Başvuru (paragraf eklenir):**
```
AYM, B. No: 2019/12345, T. 18/2/2021, § 42
```

**Anayasa Mahkemesi — Bireysel Başvuru (geleneksel uzun form):**
```
AYM, [Başvurucu Adı] Başvurusu, B. No: 2019/12345, K.T. 18/2/2021, § 42
```

**Danıştay:**
```
Danıştay 10. D., E. 2018/2456, K. 2020/3122, T. 14/9/2020
```

**Danıştay İdari Dava Daireleri Kurulu:**
```
Danıştay İDDK, E. 2020/1234, K. 2022/567, T. 15/3/2022
```

**Yargıtay Hukuk Dairesi:**
```
Yargıtay 11. HD, E. 2017/4521, K. 2019/8765, T. 22/11/2019
```

**Yargıtay Hukuk Genel Kurulu:**
```
Yargıtay HGK, E. 2016/22-789, K. 2019/456, T. 8/4/2019
```

**Yargıtay Ceza Genel Kurulu:**
```
Yargıtay CGK, E. 2018/8-234, K. 2020/89, T. 15/4/2020
```

### 12.2. AİHM Karar Atıfı

**Türkçe metinde:**
```
*Mehmet Şentürk c. Türkiye*, B. No: 13423/09, T. 9/4/2013, § 88
```

**İngilizce metinde:**
```
Mehmet Şentürk and Bekir Şentürk v. Turkey, App. No. 13423/09, 
9 April 2013, § 88
```

**Büyük Daire kararı:**
```
*Vo c. Fransa* [BD], B. No: 53924/00, T. 8/7/2004, § 67
```

### 12.3. ABAD Karar Atıfı

**Çağdaş form (ECLI ile):**
```
ABAD, C-148/15 *Deutsche Parkinson Vereinigung*, T. 19/10/2016, 
ECLI:EU:C:2016:776
```

**ABAD eski form (CELEX kodu ile):**
```
ABAD, C-148/15 *Deutsche Parkinson*, 19/10/2016, AB:C:2016:776
(CELEX: 62015CJ0148)
```

**Genel Mahkeme kararı:**
```
ABAD Genel Mahkeme, T-758/14 *Idorsia Pharmaceuticals*, 12/7/2017, 
ECLI:EU:T:2017:485
```

### 12.4. Yabancı Yüksek Mahkeme Kararı Atıfı

**US Supreme Court:**
```
*Sebelius v. Auburn Reg'l Med. Ctr.*, 568 U.S. 145 (2013)
```

**UK Supreme Court:**
```
*Montgomery v. Lanarkshire Health Board* [2015] UKSC 11
```

**Alman Bundesverfassungsgericht (Anayasa Mahkemesi):**
```
BVerfG, 1 BvR 3215/07, 24/11/2010
```

**Fransız Conseil d'État:**
```
CE, 14/10/2011, Société Pfizer, n° 327050
```

### 12.5. Yargı Kararı Atıflarında Anti-Pattern

- ❌ `AYM 2021/15 sayılı karar` (esas + tarih eksik)
- ❌ `Danıştay sağlık kararı` (somut karar verisi yok)
- ❌ `Yargıtay yerleşik içtihatı` (en az 2-3 somut karar sayılmalı)
- ❌ `AİHM Mehmet Şentürk` (başvuru no + tarih eksik)
- ❌ `ABAD Deutsche Parkinson davası` (dava numarası + ECLI eksik)

### 12.6. Yerleşik İçtihat Atıfı

Aynı yönde birden fazla karar varsa "yerleşik içtihat" ifadesi şu standartta kullanılır:

```
Bu yönde yerleşik içtihat:
- Yargıtay 13. HD, E. 2018/5421, K. 2020/3120, T. 10/3/2020
- Yargıtay 13. HD, E. 2019/7842, K. 2021/2456, T. 8/4/2021
- Yargıtay 13. HD, E. 2020/9876, K. 2022/4321, T. 12/5/2022
(bkz. ayrıca Yargıtay HGK, E. 2019/13-456, K. 2021/789, T. 15/9/2021)
```

### 12.7. İçtihat MCP Doğrulaması

Her yargı kararı atfında, kararın **mevcut ve doğru** olduğu Hukuki Veritabanları MCP üzerinden teyit edilmelidir. Şüphe durumunda:

- AYM: `kararlarbilgibankasi.anayasa.gov.tr` (Bireysel Başvuru + Norm Denetimi ayrı arama)
- Danıştay: `karararama.danistay.gov.tr`
- Yargıtay: `karararama.yargitay.gov.tr`
- AİHM: `hudoc.echr.coe.int`
- ABAD: `curia.europa.eu` veya `eur-lex.europa.eu`

**Asla yapmayın:** Hayalî esas/karar numarası, uydurma tarih, var olmayan başvuru numarası. R13 (İçtihat-Doktrin-Akademik Katman) Bölüm 12 — Bilgi Sınırı Uyarısı bağlayıcıdır.

---

## 13. Atıf Bütünlük Kontrol Listesi v2.0

R3 v2.0 (bu sürüm) ile genişletilen kontrol listesi:

**Türk mevzuatı atıfı:**
- [ ] İlk atıfta tarih + sayı + ad var mı?
- [ ] Tarih formatı `gün/ay/yıl` ve sıfır yok mu?
- [ ] Madde ses uyumlu ek doğru mu? (5 inci, 12 nci vd.)
- [ ] Fıkra **yazıyla** mı? (birinci/ikinci/üçüncü)
- [ ] Bent + alt bent ayraç içinde mi?
- [ ] Sonraki atıflarda "aynı Kanunun" kısaltması kullanıldı mı?

**Uluslararası antlaşma atıfı:**
- [ ] Resmî tam ad + Türkiye onay tarihi/sayısı var mı?
- [ ] CELEX kodu (AB için) eklendi mi?
- [ ] Helsinki/Oviedo/IHR vd. için tam yazılış kullanıldı mı?

**Yargı kararı atıfı:**
- [ ] Mahkeme adı + daire + E. + K. + T. tam mı?
- [ ] AYM bireysel başvuruda B. No + paragraf var mı?
- [ ] AİHM kararında başvuru no + tarih + paragraf var mı?
- [ ] ABAD kararında dava no + ECLI var mı?
- [ ] Yerleşik içtihat için 2-3 somut karar sayıldı mı?

**Bütünleyici kontroller:**
- [ ] Soft law referansı için kaynak + sürüm bilgisi var mı?
- [ ] WHO/CIOMS rehberi atfında baskı yılı + sürüm belirtildi mi?
- [ ] Hukuki Veritabanları MCP veya Mevzuat MCP ile teyit yapıldı mı?
