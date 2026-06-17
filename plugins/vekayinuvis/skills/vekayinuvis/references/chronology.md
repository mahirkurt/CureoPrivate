# Chronology — Osmanlı/Türk Kronoloji ve Takvim Çevirimi

> Bu dosya tarih dönüşümü, ebced, kronogram (tarih düşürme) ve hicri/rumi/
> miladi takvim sorgularında yüklenir. Otomatik kalkış için
> `ottoman_convert_date`, `ottoman_parse_ottoman_date`, `ottoman_calc_ebced`,
> `ottoman_tarih_dusur` araçları kullanılır.

## İçindekiler
1. [Üç Takvim Sistemi](#three-calendars)
2. [Hicrî Takvim — Detay](#hicri)
3. [Rumî/Mâlî Takvim — Detay](#rumi)
4. [Geçiş Dönemleri (1840–1926)](#transitions)
5. [Sultanlar Kronolojisi](#sultans)
6. [Önemli Dönüm Noktaları (Olay Atlas)](#milestones)
7. [Ebced Hesabı (Tarih Düşürme)](#ebced)
8. [MCP Kullanımı](#mcp-usage)
9. [Pratik Örnekler](#examples)

---

<a id="three-calendars"></a>
## 1. Üç Takvim Sistemi

Osmanlı bürokrasisi farklı dönemlerde **üç ayrı takvim** kullanmıştır.
Tarihçi yazarken hangi takvimle yazıldığını **belge üzerinden** doğrulamalı,
çeviri yaparken `ottoman_convert_date` ile teyit etmelidir.

| Takvim | Türü | Resmî Kullanım | Yıl Başı |
|---|---|---|---|
| Hicrî (Kameri) | Ay-bazlı | Klasik dönem geneli; din-resmî olayları için her zaman | 1 Muharrem |
| Rumî (Mâlî, Julian-bazlı) | Güneş-bazlı | 1840–1925 resmî mâlî | 1 Mart (1840–1916), 1 Ocak (1917–1925) |
| Miladî (Gregoryen) | Güneş-bazlı | 1 Ocak 1926'dan itibaren tek resmî | 1 Ocak |

> Kameri yıl, Şemsi yıldan yaklaşık **11 gün** kısadır; bu yüzden Hicri ve
> Miladi yıllar yaklaşık her **33 yılda** 1 yıl kayar.

---

<a id="hicri"></a>
## 2. Hicrî Takvim — Detay

### 2.1 Aylar (gün sayısı yaklaşık)
1. Muharrem (29/30)
2. Safer (29)
3. Rebîülevvel (30)
4. Rebîülâhir (29)
5. Cemâziyelevvel (30)
6. Cemâziyelâhir (29)
7. Receb (30)
8. Şa'bân (29)
9. Ramazân (30)
10. Şevvâl (29)
11. Zilka'de (30)
12. Zilhicce (29 veya 30)

Toplam: 354 veya 355 gün.

### 2.2 Hicri Yıl ↔ Miladi Yıl Yaklaşık Formül
```
Miladi ≈ Hicri × (33/34) + 622
```
**Bu formül kesin değildir**; tek-gün dönüşümü için her zaman
`ottoman_convert_date` kullanın. Manüel hesap için yaklaşık aralık verir:

| Hicri | Miladi yaklaşık |
|---|---|
| 700 | 1300–1301 |
| 900 | 1495–1496 |
| 1000 | 1591–1592 |
| 1100 | 1688–1689 |
| 1200 | 1785–1786 |
| 1250 | 1834–1835 |
| 1300 | 1882–1883 |
| 1320 | 1902–1903 |
| 1340 | 1921–1922 |

### 2.3 Kısaltma Konvansiyonu
- **H.** veya **h.** = Hicri yıl
- **AH** = Anno Hegirae (İngilizce kaynaklar)
- *"h. 1242"* ya da *"AH 1242"*

---

<a id="rumi"></a>
## 3. Rumî/Mâlî Takvim — Detay

### 3.1 Tarihçe
- **1677 (h. 1088)**: Osmanlı mâlî yönetimi vergi tahsilatını şemsi yıla
  bağlamak için *mâlî takvim* tarafından sayılmaya başlar.
- **1840 (h. 1256)**: Tanzimat sonrası Rumî takvim **resmî bürokratik
  takvim** olarak ilan edilir; Hicri 1256 = Rumi 1256 olarak başlatılır;
  ancak şemsi yıl olduğu için aralık zamanla farklılaşır.
- **1916 sonu**: Yıl başı 1 Mart'tan 1 Ocak'a kaydırılır; **1 Mart 1333
  R.** ile **1 Ocak 1333 R.** arasındaki on ay (Mart–Aralık 1917) hem
  Rumi hem Miladi takvimde *aynı yıl içinde* sayılır.
- **26 Aralık 1925** (Tarih ve Saat Kanunu 698 sayılı): 1 Ocak 1926'dan
  itibaren Türkiye Cumhuriyeti tek resmî takvim olarak Gregoryen'i kabul
  eder; Rumi yıl 1341 atlanarak Hicri-bazlı yıl sayımı bırakılır.

### 3.2 Rumî - Miladî Gün Farkı
- Rumi (Julian) takvim, Miladi'ye göre:
  - **1700–1800**: 11 gün geri
  - **1800–1900**: 12 gün geri
  - **1900–1916**: 13 gün geri
  - **1916 sonu sonrası**: yıl başı düzeltmesiyle gün farkı sabit 13 gün

### 3.3 Rumî Yıl ↔ Miladi Yıl
**1840–1916 dönemi**:
```
Miladi ≈ Rumî + 584 (ama sadece Ocak–Şubat sonu yıldönümünde geçerli;
   Mart başı sonrası Miladi - Rumî = 584 değil, 584-1 = 583 kadar)
```

Pratik kural:
- Eğer Rumî tarihi **1 Mart 1331** ise → Miladi **14 Mart 1915**
- Eğer Rumî tarihi **14 Ocak 1331** ise → Miladi **27 Ocak 1916** (bu durumda
  Rumi yıl 1331'in Ocak ayı, Miladi'de 1916'ya denk gelir çünkü Rumi yılbaşı
  Mart'tır)

> Bu yıl-başı kayması en sık karıştırılan noktadır. `ottoman_convert_date`
> bu kaymayı otomatik düzeltir.

### 3.4 1917 Geçiş
- 16 Şubat 1332 R. → 1 Mart 1917 M.: Rumi yıl 1332 (Mart 1916 – Şubat 1917)
- 1 Mart 1333 R. başlangıcı ile 1 Ocak 1333 R. yeni başlangıç arasında
  geçen Mart–Aralık 1917, Rumi'de **1333**, Miladi'de **1917**.
- Bu süre boyunca Rumi-Miladi yıl numarası ortak: ikisi de "1333/1917"
  gözükse de gün farkı 13 gün korunur.

### 3.5 Sembolik Şubat 1332/1916
- *31 Mart Vakası* (1909): Rumi 31 Mart 1325 = Miladi 13 Nisan 1909.
- *14 Mart Tıp Bayramı*: Mekteb-i Tıbbiye-i Şâhâne'nin kuruluş yıldönümü
  Rumi 14 Mart 1248 (Cuma) — Miladi 26 Mart 1832. Modern kutlamada 14 Mart
  Miladi olarak alınır; tarihsel doğrulukta Rumi orijinal tarih önemlidir.

### 3.6 Kısaltma Konvansiyonu
- **R.** veya **MR** (Mâlî Rumî): Rumi yıl
- Aralık 1916 öncesi: belirsizse Mart-Şubat sınırını dikkatle kontrol et.

---

<a id="transitions"></a>
## 4. Geçiş Dönemleri (1840–1926)

Bu dönem belge ile uğraşırken kritik:

### 4.1 1840 (h. 1256) Öncesi
- Tüm resmî belgeler hicri.
- Bazı mâlî defterler mâlî yıl kullanır ama yıl numarası hicri ile aynı.

### 4.2 1840–1916
- Çoğu belge **çift tarih**: hicri (sağ üstte) + rumi (sol üstte).
- Hicri ve Rumi yıllar **aynı numara** ile başlasa da zamanla ayrılır
  (kameri ve şemsi farkı nedeniyle).
- Bazı belgeler sadece rumi; bazıları sadece hicri.

### 4.3 1917–1925
- Yıl başı 1 Mart'tan 1 Ocak'a kaydı.
- Hicri tarih dini belgelerde devam eder; rumi mâli ve siyasi belgelerde
  devam eder.

### 4.4 1 Ocak 1926'dan İtibaren
- TC tek takvim Miladi.
- Hicri tarih bazı dini metinlerde paralel verilir ama resmî yok.

---

<a id="sultans"></a>
## 5. Sultanlar Kronolojisi

Osmanlı padişah saltanat dönemleri tarih düşürme ve dönem belirleme için
zorunlu bilgidir:

| No | Sultan | Saltanat (Miladi) | Saltanat (Hicri) |
|---|---|---|---|
| I | Osman Gazi | ?-1324 | ?-724 |
| II | Orhan Gazi | 1324–1362 | 724–763 |
| III | I. Murad | 1362–1389 | 763–791 |
| IV | I. Bayezid (Yıldırım) | 1389–1402 | 791–805 |
| – | Fetret Devri | 1402–1413 | 805–816 |
| V | I. Mehmed (Çelebi) | 1413–1421 | 816–824 |
| VI | II. Murad | 1421–1444, 1446–1451 | 824–848, 850–855 |
| VII | II. Mehmed (Fatih) | 1444–1446, 1451–1481 | 848–850, 855–886 |
| VIII | II. Bayezid | 1481–1512 | 886–918 |
| IX | I. Selim (Yavuz) | 1512–1520 | 918–926 |
| X | I. Süleyman (Kanunî) | 1520–1566 | 926–974 |
| XI | II. Selim | 1566–1574 | 974–982 |
| XII | III. Murad | 1574–1595 | 982–1003 |
| XIII | III. Mehmed | 1595–1603 | 1003–1012 |
| XIV | I. Ahmed | 1603–1617 | 1012–1026 |
| XV | I. Mustafa | 1617–1618, 1622–1623 | 1026–1027, 1031–1032 |
| XVI | II. Osman (Genç) | 1618–1622 | 1027–1031 |
| XVII | IV. Murad | 1623–1640 | 1032–1049 |
| XVIII | İbrahim | 1640–1648 | 1049–1058 |
| XIX | IV. Mehmed | 1648–1687 | 1058–1099 |
| XX | II. Süleyman | 1687–1691 | 1099–1102 |
| XXI | II. Ahmed | 1691–1695 | 1102–1106 |
| XXII | II. Mustafa | 1695–1703 | 1106–1115 |
| XXIII | III. Ahmed | 1703–1730 | 1115–1143 |
| XXIV | I. Mahmud | 1730–1754 | 1143–1168 |
| XXV | III. Osman | 1754–1757 | 1168–1171 |
| XXVI | III. Mustafa | 1757–1774 | 1171–1187 |
| XXVII | I. Abdülhamid | 1774–1789 | 1187–1203 |
| XXVIII | III. Selim | 1789–1807 | 1203–1222 |
| XXIX | IV. Mustafa | 1807–1808 | 1222–1223 |
| XXX | II. Mahmud | 1808–1839 | 1223–1255 |
| XXXI | Abdülmecid | 1839–1861 | 1255–1277 |
| XXXII | Abdülaziz | 1861–1876 | 1277–1293 |
| XXXIII | V. Murad | 1876 (Mayıs–Ağustos) | 1293 (üç ay) |
| XXXIV | II. Abdülhamid | 1876–1909 | 1293–1327 |
| XXXV | V. Mehmed (Reşad) | 1909–1918 | 1327–1336 |
| XXXVI | VI. Mehmed (Vahdeddin) | 1918–1922 | 1336–1341 |
| – | Halîfe Abdülmecid | 1922–1924 (yalnız halife) | 1341–1342 |

---

<a id="milestones"></a>
## 6. Önemli Dönüm Noktaları (Olay Atlas)

### Klasik Dönem
- **1453** (h. 857): İstanbul'un fethi.
- **1517** (h. 923): Mısır'ın fethi; hilafet Osmanlı'ya.
- **1571** (h. 979): İnebahtı (Lepanto) deniz savaşı.
- **1683** (h. 1094–1095): II. Viyana Kuşatması.
- **1699** (h. 1110–1111): Karlofça Antlaşması.

### Reform Dönemi
- **1718** (h. 1130): Pasarofça; Lâle Devri başlangıcı.
- **1727** (h. 1140): İlk Türkçe matbaa (İbrahim Müteferrika).
- **1774** (h. 1187–1188): Küçük Kaynarca; Rusya ile.
- **1789–1807**: III. Selim, Nizâm-ı Cedîd.
- **1808**: Sened-i İttifak.
- **1826** (h. 1241): Yeniçeri Ocağı'nın kaldırılması.
- **3 Kasım 1839** (Rumi 26 Şaban 1255 / 7 Şaban 1255 H.): Tanzimat
  Fermanı / Gülhane Hatt-ı Hümâyûnu.
- **18 Şubat 1856** (h. 11 Cemâziyelâhir 1272): Islahat Fermanı.

### Tıp Tarihi (Mahir Bey için özel)
- **14 Mart 1827** (R. 14 Mart 1243 / h. 14 Şâban 1242): Mekteb-i
  Tıbbiye-i Şâhâne'nin kuruluşu (modern Türk tıp eğitiminin başlangıcı).
- **17 Şubat 1839**: Tıbbiye, Galatasaray'da Mekteb-i Tıbbiye-i Adliye-i
  Şâhâne adıyla yeniden açılır.
- **9 Mart 1867** (h. 3 Zilka'de 1283): Mekteb-i Tıbbiye-i Mülkiye kurulur.
- **23 Eylül 1908**: Mekteb-i Tıbbiye-i Şâhâne, Dârülfünûn-ı Osmânî
  bünyesine geçer; *Tıb Fakültesi* adını alır.
- **14 Nisan 1928** (TC): **1219 sayılı Tababet ve Şuabatı San'atlarının
  Tarz-ı İcrâsına Dair Kanun** yürürlüğe girer.
- **23 Ocak 1953**: 6023 sayılı Türk Tabipleri Birliği Kanunu.

### II. Meşrutiyet ve Sonrası
- **23 Aralık 1876**: Kanun-ı Esasî.
- **14 Şubat 1878**: I. Meşrutiyet'in askıya alınması.
- **24 Temmuz 1908**: II. Meşrutiyet'in ilanı.
- **13 Nisan 1909** (R. 31 Mart 1325): *31 Mart Vakası*.
- **27 Nisan 1909**: II. Abdülhamid'in tahttan indirilmesi.
- **3 Mart 1924**: Hilafetin kaldırılması (TC Kanun no. 431).
- **1 Ocak 1926**: Gregoryen takvime tam geçiş.

---

<a id="ebced"></a>
## 7. Ebced Hesabı (Tarih Düşürme — Chronograms)

### 7.1 Ebced-i Kebîr Sistemi
Arap alfabesinin her harfine bir sayı değeri atanır:

| Harf | Değer | Harf | Değer | Harf | Değer | Harf | Değer |
|---|---|---|---|---|---|---|---|
| ا | 1 | ي | 10 | ق | 100 | غ | 1000 |
| ب | 2 | ك | 20 | ر | 200 | | |
| ج | 3 | ل | 30 | ش | 300 | | |
| د | 4 | م | 40 | ت | 400 | | |
| ه | 5 | ن | 50 | ث | 500 | | |
| و | 6 | س | 60 | خ | 600 | | |
| ز | 7 | ع | 70 | ذ | 700 | | |
| ح | 8 | ف | 80 | ض | 800 | | |
| ط | 9 | ص | 90 | ظ | 900 | | |

### 7.2 Tarih Düşürme (Ta'rîh-i Lafzî)
Bir bina, eser ya da olay için yazılan beyit/mısranın ebced toplamı **o
olayın hicri tarihine** denk getirilir. Tarihçi okur, ebced toplamını
hesaplar, hicri yılı bulur.

**Örnek**: Bir caminin tarih kitabesinde *"İdüb tahsîn bu cây-ı bî-bedele"*
yazıyorsa, mısranın ebced toplamı (örneğin 1184) o caminin inşa edildiği
hicri yıldır → Miladi ~1770.

### 7.3 MCP Kullanımı
- `ottoman_calc_ebced(text=<mısra>)` → toplam değer
- `ottoman_tarih_dusur(text=<beyit>)` → ebced çözümü + yıl tahmini

### 7.4 Ebced Türleri
- **Ebced-i Kebîr**: yukarıdaki tablo, en yaygın
- **Ebced-i Sagîr**: harf-bazlı küçük değerler (örn. 1-9, 10-90 aralığı
  daraltılmış) — daha az kullanılır
- **Tâm tarih**: tüm beyit ebced'i = yıl
- **Mu'cem tarih**: yalnız noktalı harfler sayılır
- **Mühmel tarih**: yalnız noktasız harfler sayılır

---

<a id="mcp-usage"></a>
## 8. MCP Kullanımı

### 8.1 ottoman_convert_date
**Girdi**: tek tarih, takvim sistemi belirtilir.
**Çıktı**: üç-takvim eş değerleri + gün adı.

Pratik örnek:
```
ottoman_convert_date(
   date="15 Rebîülevvel 1248",
   from_calendar="hicri"
)
```
Beklenen çıktı: H. 15 Rebîülevvel 1248 / R. 30 Temmuz 1248 / M. 12 Ağustos 1832 / Pazartesi.

### 8.2 ottoman_parse_ottoman_date
**Girdi**: serbest metin (örn. "fî 17 muharrem sene 1290").
**Çıktı**: yapılandırılmış JSON (gün, ay numarası, yıl, takvim tahmini).

### 8.3 ottoman_parse_number
**Girdi**: Arapça-Hint rakamı (٠-٩), Doğu-Arap (۰-۹), Roma, Latin.
**Çıktı**: tek sayı.

### 8.4 ottoman_calc_ebced / ottoman_tarih_dusur
**Girdi**: Arapça harfli mısra/beyit.
**Çıktı**: ebced toplamı; tarih düşürme aday yılı.

---

<a id="examples"></a>
## 9. Pratik Örnekler

### 9.1 Tek Tarih Dönüşümü
**Soru**: "BOA HAT 1556/22'nin tarihi 15 Rebîülevvel 1248. Miladi nedir?"

Adımlar:
1. `ottoman_convert_date(date="15 Rebîülevvel 1248", from_calendar="hicri")`
2. Sonuç → 12 Ağustos 1832, Pazartesi.
3. Bağlamda **II. Mahmud dönemi**, yeniçeri-sonrası reform yılları.

### 9.2 Rumi-Miladi Karışıklığı
**Soru**: "Belgede '14 Nisan 1325' yazıyor. Bu hangi olay?"

Adımlar:
1. `ottoman_convert_date(date="14 Nisan 1325", from_calendar="rumi")`
2. Sonuç → 27 Nisan 1909 Miladi.
3. Bağlam → 31 Mart Vakası sonrası, II. Abdülhamid'in **tahttan indirildiği gün**.

### 9.3 Mekteb-i Tıbbiye Kuruluş Tarihi
**Soru**: "14 Mart 1827 hangi takvim?"

Adımlar:
1. Tıp Bayramı'nın resmî tarihi 14 Mart'tır.
2. Orijinal kuruluş Rumi 14 Mart 1243 = Miladi 26 Mart 1827.
3. *Veya*: Hicri 14 Şâban 1242 (eğer 14 Mart 1827 Miladi alınırsa, Rumi
   karşılığı 2 Mart 1243).
4. **Notasyon kuralı**: Akademik metinde *"14 Mart 1827 (R. 1243; H. Şâban
   1242)"* veya *"26 Mart 1827 (R. 14 Mart 1243; H. 27 Şâban 1242)"* —
   hangisi orijinal arşiv kaynağındaki tarihse o öncelikli, parantezde
   karşılıkları.

### 9.4 Tarih Düşürme Çözümü
**Soru**: Bir kitabede *"Yapdı bu mâbedi pâdişah"* mısrası var. Ebced'i?

Adımlar:
1. `ottoman_tarih_dusur(text="يپدى بو معبدى پادشاه")`
2. Beklenen çıktı: harf-bazlı ebced + toplam + Miladi yıl tahmini.
3. Tarih kitabesi şiir/edebi disiplin gerektirir; tahmin için bağlam (bina
   tipi, padişah dönemi) doğrulama sağlar.
