# Citation & Transliteration — Atıf ve Çeviriyazı Standartları

> Bu dosya ACADEMIC_REPORT modu için ve bibliyografya/atıf düzenleme
> sorgularında yüklenir. İki ana standart vardır: IJMES (İngilizce çıktı)
> ve TDV İA (Türkçe çıktı). Bir rapor içinde **tek sistem** seçilir;
> karışım yasaktır.

## İçindekiler
1. [Temel İlke: Tek Sistem](#single-system)
2. [TDV İA Sistemi (Türkçe çıktı)](#tdv)
3. [IJMES Sistemi (İngilizce çıktı)](#ijmes)
4. [Karşılaştırma Tablosu](#comparison)
5. [Tarih Notasyonu](#dates)
6. [Atıf Formatı — Birincil Arşiv](#cite-archive)
7. [Atıf Formatı — Birincil Matbu](#cite-printed)
8. [Atıf Formatı — Modern Akademik](#cite-modern)
9. [Bibliyografya Düzenleme](#bibliography)
10. [Sık Yapılan Hatalar](#errors)

---

<a id="single-system"></a>
## 1. Temel İlke: Tek Sistem

Bir rapor metninde:
- Türkçe akademik çıktı → **TDV İA** transliterasyon sistemi
- İngilizce akademik çıktı → **IJMES** (International Journal of Middle East
  Studies) transliterasyon sistemi
- Almanca/Fransızca akademik çıktı → İlgili dilin yerleşik sistemleri
  (Berlin Akademisi, EAL, GAL vd.); bu skill default olarak IJMES'i kullanır.

**Tek istisna**: Bir birincil belgenin/metnin orijinal okumasına sadakat
gerektiğinde transkripsiyon kuralı geçici olarak değiştirilebilir; bu durum
**dipnotta açıkça not edilir**.

---

<a id="tdv"></a>
## 2. TDV İA Sistemi (Türkçe çıktı için)

### 2.1 Uzun Ünlüler
| Karakter | Kullanım |
|---|---|
| â | Arapça uzun a (â'lim, kâtib, hâtem) |
| î | Arapça uzun i (Selîm, vekîl, fîl) |
| û | Arapça uzun u (Mahmûd, sûre, vücûd) |

### 2.2 Özel Konsonantlar
| Karakter | Yerleşik kullanım |
|---|---|
| ' (apostrof) | Arapça 'ayn (sâ'at, ta'lîk, mâ'rûz) |
| ’ (curly hemze) | Hemze (te’hîr, kazâ’) — bazı yayıncılar düz apostrof kullanır |
| ğ | Arapça gayn (mağrib, lugavî); Türkçe yumuşak g'den ayırt etmek için |
| ḥ vs h | TDV İA genelde **ayırt etmez**, ikisi de "h" yazılır |
| ḳ vs k | Genelde ayırt edilmez; bağlamdan anlaşılır |

### 2.3 Tipik Örnek Cümle
> *Şânîzâde Mehmed Atâullâh Efendi, Mi'yârü'l-Etıbbâ adlı eserinde,
> Mekteb-i Tıbbiye-i Şâhâne'nin 1827'de te'sîsinden önce Tabhâne-i
> Âmire'nin geleneksel tıb eğitimini yürüttüğünü kaydeder.*

### 2.4 Kaynak Standardı
- TDV İslâm Ansiklopedisi'nin kendi madde başlıkları **referans** kabul
  edilir.
- Şüpheli yazımda `ottoman_get_islam_ansiklopedisi(<terim>)` ile madde
  başlığı doğrulanır.

---

<a id="ijmes"></a>
## 3. IJMES Sistemi (İngilizce çıktı için)

### 3.1 Uzun Ünlüler (IJMES "simplified" — diakritiksiz)
- Resmî IJMES Word List'te yer alan kelimeler diakritiksiz yazılır:
  `sultan, vizier, pasha, beg, agha, qadi, ulema, sharia, fatwa,
   waqf, sancak, vilayet, kaza, hatt-i humayun, irade, mecelle,
   meşrutiyet, tanzimat`.
- Word List dışındaki kelimeler için tam IJMES transliterasyonu:

### 3.2 Ünlüler ve Tonlamalar
| IJMES | Arap harfi | Örnek |
|---|---|---|
| ā | ا (long a) | Mahmūd, ʿālim |
| ī | ي (long i) | Selīm, fīl |
| ū | و (long u) | Maḥmūd, sūra |
| a, i, u | kısa ünlüler | qadi, sultan |
| e, o | Türkçe-Osmanlıca ünlüler | mektep, vali, sancakbeyi |
| ö, ü | Türkçe ön ünlüler | Süleymân, müderris |

### 3.3 Ünsüzler
| IJMES | Arap harfi | Notu |
|---|---|---|
| ʾ | ء (hamza) | te'sīs → taʾsīs |
| ʿ | ع (ʿayn) | ʿālim, taʿlīm |
| ḥ | ح | Maḥmūd, Aḥmed |
| kh | خ | khalīfa |
| dh | ذ | dhimmī |
| sh | ش | sharīʿa |
| ṣ | ص | Ṣadr |
| ḍ | ض | qāḍī |
| ṭ | ط | sulṭān, ṭibb |
| ẓ | ظ | naẓīr |
| q | ق | qāḍī (k yerine — Türkçe yazımda da ḳ olarak ayrılır) |
| gh | غ | maghrib |

### 3.4 Tipik Örnek Cümle
> *Şānīzāde Meḥmed Aṭāʾullāh Efendi, in his work Miʿyār al-aṭibbāʾ,
> records that the traditional medical education was conducted by the
> Tabhāne-yi ʿĀmire before the founding of the Mekteb-i Ṭıbbiyye-i
> Şāhāne in 1827.*

### 3.5 Kaynak Standardı
- IJMES Word List (en güncel sürüm): yayıncının web sitesi.
- Anglo-Amerikan Osmanlı çalışmalarında **fiilî standart**dır.

---

<a id="comparison"></a>
## 4. Karşılaştırma Tablosu

| Kavram | TDV İA (Türkçe) | IJMES (İngilizce) |
|---|---|---|
| سلطان | sultân | sulṭān |
| فقيه | fakîh | faqīh |
| قاضى | kadı / kâdî | qāḍī |
| محمد | Mehmed (modern) / Muhammed (klasik) | Meḥmed / Muḥammad |
| عثمانى | Osmânî | ʿOthmānī / ʿUthmānī |
| ملت | millet | millet |
| تنظيمات | Tanzîmât | Tanẓīmāt (or Tanzimat in Word List) |
| شعرية | Şer'iyye | Sharʿiyya |
| وقف | vakıf | waqf |
| مدرسة | medrese | madrasa |
| همايون | hümâyûn | humāyūn |
| دفتر | defter | defter |
| سجل | sicil | sijill |
| فرمان | fermân | fermān |
| برات | berat | berāt |

---

<a id="dates"></a>
## 5. Tarih Notasyonu

### 5.1 Üç Takvim Sistemi
- **Hicrî (H./AH)**: Kameri (ay) takvimi; 622 CE Hicret'ten başlar.
- **Rumî (R./MR)**: Mâlî/Julian-bazlı güneş takvimi; 1840–1925 arası
  Osmanlı resmî takvimi.
- **Miladî (M./CE/AD)**: Gregoryen.

### 5.2 Notasyon Kuralı
**Birincil belge alıntısında orijinal takvim + parantez içinde Miladi**:
- `15 Rebîülevvel 1248 (12 Ağustos 1832)` — hicri öncelikli (klasik)
- `24 Mart 1331 R. (6 Nisan 1915)` — rumi öncelikli (geç-Osmanlı)
- `13 Şubat 1339 (13 Şubat 1923)` — rumi-miladi aynı (1917–1926 geçiş)

**Önemli geçiş tarihleri**:
- 14 Şubat 1331 R. = 27 Şubat 1916 Miladi (Rumi 13 gün geride; 1900–1923)
- 16 Şubat 1332 R. = 1 Mart 1917 (Rumi+Miladi takvim **yıl başlangıcı
  ortaklaştı**; gün sayım hâlâ farklı)
- 1 Kânûn-ı sânî 1342 = 1 Ocak 1926: Türkiye Cumhuriyeti Gregoryen
  takvime tam geçer.

### 5.3 Doğrulama
Her tarih `ottoman_convert_date` ile doğrulanır. Belge üzerinde tam
gün-ay-yıl yazıyorsa zorunlu çift takvim notasyonu uygulanır.

### 5.4 Hicrî Kameri Ayları (kısaltma + tam)
| Kısaltma | Tam ad |
|---|---|
| M | Muharrem |
| S | Safer |
| Rabi I | Rebîülevvel |
| Rabi II | Rebîülâhir |
| Cem I | Cemâziyelevvel |
| Cem II | Cemâziyelâhir |
| Receb | Receb |
| Şaban | Şa'bân |
| Ramazan | Ramazân |
| Şevval | Şevvâl |
| Zilkade | Zilka'de |
| Zilhicce | Zilhicce |

### 5.5 Rumî/Mâlî Ayları
Ocak yerine *Kânûn-ı sânî*, Şubat *Şubat*, Mart *Mart*, Nisan *Nisan*,
Mayıs *Mayıs*, Haziran *Haziran*, Temmuz *Temmuz*, Ağustos *Ağustos*,
Eylül *Eylül*, Ekim *Teşrîn-i evvel*, Kasım *Teşrîn-i sânî*, Aralık
*Kânûn-ı evvel*.

---

<a id="cite-archive"></a>
## 6. Atıf Formatı — Birincil Arşiv

### 6.1 Genel Şablon
```
[Arşiv kısaltması], [Fond/Tasnif], [Defter/Dosya no][/[Belge no]],
[gömlek/sayfa no], [tarih (orijinal takvim + Miladi)].
[Eğer varsa: özet/konu].
```

### 6.2 Örnekler

**BOA HAT**:
*BOA, HAT, 1556/22, 15 Rebîülevvel 1248 (12 Ağustos 1832). "Mekteb-i Tıbbiye'nin
Galatasaray'a nakli hakkında."*

**BOA Cevdet (alt-tasnif belirtmeli)**:
*BOA, C.SH (Cevdet Sıhhiye), 17/823, 7 Zilkade 1255 (12 Ocak 1840).
"Tabhane-i Âmire'de kullanılan ecza hakkında."*

**BOA Mühimme**:
*BOA, MD 5, hk. 1245, 17 Cemâziyelâhir 967 (14 Mart 1560).*

**BOA Tahrir**:
*BOA, TT 387, fol. 23a (Hicri 935 / 1530 — Vilâyet-i Karaman).*

**Şer'iyye Sicili**:
*Bursa Şer'iyye Sicili, no. A 152, varak 47b, h. 1098 (1687). "Hüccet-i şer'iyye
— …" [Eğer transkripsiyon edisyonu varsa: edisyon yazarı, başlığı, sayfa].*

**Topkapı**:
*Topkapı Sarayı Müzesi Arşivi, TS.MA.e, 802/15, [tarih].*

**BCA**:
*BCA, 030.10/57.376.4, 12 Ekim 1928. "Tababet ve Şuabatı Sanatlarının Tarz-ı
İcrasına dair Kanun lâyihasının Heyet-i Vekîle'de müzakeresi."*

**VGM Vakfiye**:
*VGM Arşivi, Vakfiyeler Defteri no. 581, sayfa 134, "Hâcı Mehmed Paşa
Vakfiyesi", 15 Rebîülevvel 985 (2 Haziran 1577).*

### 6.3 Atıf Notu
- Eğer belge **dijital olarak** erişim sağlanmışsa katalog URL'si dipnota eklenir.
  **BOA/BCA için (`devlet-arsivleri` connector):** `devarsiv_get_belge`'den dönen
  `belge_url` (`…BelgeGoster.aspx?ItemId=…`) doğrulanabilir katalog URL'i olarak
  dipnota eklenir ve *"[devlet-arsivleri kataloğundan doğrulandı]"* etiketiyle
  işaretlenir. Örn: `BOA, DH.İ.UM, 22/19, H-27-12-1337. <…ItemId=31664060…>`
  (bkz. `devlet-arsivleri-katalog.md` § 5). Belgenin görüntüsü/OCR/HTR içeriği
  yalnız gerçek araç çıktısı ve provenance ile aktarılır; çekilmediyse yalnız
  katalog kaydı+URL atıflanır, görüntü içeriği uydurulmaz.
- Eğer belge sadece **transkripsiyon edisyonundan** alıntılanmışsa, hem orijinal
  arşiv referansı hem de edisyon referansı verilir (ikili atıf).

---

<a id="cite-printed"></a>
## 7. Atıf Formatı — Birincil Matbu

### 7.1 Genel Şablon
```
[Yazar (eğer varsa)]. [Eser Başlığı (italik)]. [Yer]: [Matbaa], [Tarih (H./R./M.)].
```

### 7.2 Örnekler

**Klasik dönem matbu**:
*Şânîzâde Mehmed Atâullâh. Mi'yârü'l-Etıbbâ. İstanbul: Dârü't-Tıbâ'ati'l-Âmire,
h. 1235 (1820).*

**Salnâme**:
*Salnâme-i Devlet-i Aliyye-i Osmâniye, sene 1304 (1886–87) [54. sene]. İstanbul:
Matba'a-i Âmire, h. 1304.*

*Salnâme-i Nezâret-i Maârif-i Umûmiye, def'a 4 (sene 1319 / 1901–02). İstanbul:
Matba'a-i Âmire, h. 1319.*

**Süreli yayın makalesi**:
*"Tabîb Sâlim Efendi'nin Mahmûd Beyefendi'ye Cevâbı." Mecmûa-i Fünûn, no. 7
(Şâban 1280 / Ocak 1864): 234–242.*

**Düstûr**:
*Düstûr, Birinci Tertip, c. IV. İstanbul: Matba'a-i Âmire, h. 1296 (1879),
ss. 224–229. "Tarz-ı icrâ-yı tababet hakkında nizamnâme."*

**TBMM Zabıt Ceridesi**:
*TBMM Zabıt Ceridesi, devre III, ictima senesi 1, c. 1, 14 Nisan 1928,
ss. 156–172.*

---

<a id="cite-modern"></a>
## 8. Atıf Formatı — Modern Akademik

### 8.1 Chicago Notes-Bibliography Sistemi (Türk tarih yazımı ile uyumlu)

#### A. Kitap
**Dipnot ilk geçiş**:
*Halil İnalcık, Osmanlı İmparatorluğu Klâsik Çağ (1300–1600), çev. Ruşen Sezer
(İstanbul: Yapı Kredi Yayınları, 2003), 145–148.*

**Sonraki geçişler (kısa)**:
*İnalcık, Klâsik Çağ, 167.*

**Bibliyografya**:
*İnalcık, Halil. Osmanlı İmparatorluğu Klâsik Çağ (1300–1600). Çev. Ruşen
Sezer. İstanbul: Yapı Kredi Yayınları, 2003.*

#### B. Makale
**Dipnot**:
*M. Şükrü Hanioğlu, "The Second Constitutional Period, 1908–1918," in The
Cambridge History of Turkey, vol. 4, ed. Reşat Kasaba (Cambridge: Cambridge
University Press, 2008), 62–111.*

**Bibliyografya**:
*Hanioğlu, M. Şükrü. "The Second Constitutional Period, 1908–1918." In The
Cambridge History of Turkey, vol. 4, edited by Reşat Kasaba, 62–111.
Cambridge: Cambridge University Press, 2008.*

#### C. Dergi Makalesi (Türkçe)
*Faroqhi, Suraiya. "16. Yüzyıl Ortalarında Anadolu'da Halı Üretimi." Belleten
44, no. 175 (1980): 539–561.*

DOI varsa eklenir; DergiPark URL'si varsa eklenir.

#### D. Tez
*Demirel, Ömer. "II. Mahmud Devri Yeniçeri Ocağı'nın Kaldırılması Üzerine
Bir Araştırma." Doktora Tezi, Ankara Üniversitesi Sosyal Bilimler Enstitüsü,
1986. [YÖKtez: <https://tez.yok.gov.tr/UlusalTezMerkezi/...>]*

#### E. TDV İA Maddesi
*Akgündüz, Ahmet. "Hatt-ı Hümâyûn." TDV İslâm Ansiklopedisi, c. 16
(İstanbul: TDV İSAM, 1997): 486–488. <https://islamansiklopedisi.org.tr/hatti-humayun>*

### 8.2 IJMES İngilizce Format

*Hanioğlu, M. Şükrü. A Brief History of the Late Ottoman Empire. Princeton:
Princeton University Press, 2008.*

*Quataert, Donald. "Ottoman Manufacturing in the Nineteenth Century." In
Manufacturing in the Ottoman Empire and Turkey, 1500–1950, edited by Donald
Quataert, 87–122. Albany: SUNY Press, 1994.*

---

<a id="bibliography"></a>
## 9. Bibliyografya Düzenleme

Akademik tarih raporlarında bibliyografya **üç bölüme** ayrılır:

### 9.1 Birincil Arşiv Kaynakları (Archival Sources)
Alfabetik arşiv adına göre. Bir arşiv altında fond/tasnif. Tek tek belge
listelenmez (zaten dipnotlarda var); yalnız fondlar.

Örnek:
```
BOA — Devlet Arşivleri Başkanlığı, Osmanlı Arşivi (İstanbul):
   HAT, Hatt-ı Hümâyûn Tasnifi
   C.SH, Cevdet Tasnifi — Sıhhiye
   İ.SH, İrade — Sıhhiye
   DH.MKT, Dahiliye Mektubî Kalemi
   DH.SAİD, Sicill-i Ahval Defterleri

BCA — Devlet Arşivleri Başkanlığı, Cumhuriyet Arşivi (Ankara):
   030.10  Başvekâlet/Başbakanlık Muamelat Genel Müdürlüğü

VGM — Vakıflar Genel Müdürlüğü Arşivi (Ankara)
```

### 9.2 Birincil Matbu Kaynaklar (Printed Primary Sources)
Yayın yılına göre kronolojik veya yazara göre alfabetik.

Örnek:
```
Cevdet, Ahmed Paşa. Târîh-i Cevdet. 12 c. İstanbul: Matba'a-i Âmire,
   h. 1271–1301 (1855–1884).

Düstûr. Birinci Tertip. 8 c. İstanbul: Matba'a-i Âmire, h. 1289–1320
   (1872–1902).

Salnâme-i Devlet-i Aliyye-i Osmâniye. 68 c. İstanbul: Matba'a-i Âmire,
   h. 1263–1334 (1847–1918).

Şânîzâde Mehmed Atâullâh. Mi'yârü'l-Etıbbâ. İstanbul: Dârü't-Tıbâ'ati'l-
   Âmire, h. 1235 (1820).

Takvîm-i Vekayi. İstanbul: 1831–1922 (aralıklı).
```

### 9.3 İkincil Literatür (Secondary Literature)
Yazara göre alfabetik, Chicago bibliyografya formatında.

---

<a id="errors"></a>
## 10. Sık Yapılan Hatalar

### 10.1 Karışık Transliterasyon
> ❌ *"Hatt-ı Humāyūn"* — Türkçe başlık IJMES diakritikli; tutarsız.
> ✅ *"Hatt-ı Hümâyûn"* (TDV) veya *"Hatt-ı Humāyūn"* (IJMES strict) — biri.

### 10.2 Çift Takvim Atlanması
> ❌ *"1248 yılında Mekteb-i Tıbbiye kuruldu."*
> ✅ *"H. 1242 / 1827 yılında Mekteb-i Tıbbiye-i Şâhâne kuruldu."*

### 10.3 Rumi/Miladi Karışması
1916–1926 arası belgelerde Rumi 13 gün geri; "Mart" Rumi'de tipik olarak
Nisan'ı işaret eder.

> ❌ *"31 Mart 1909 Vakası"* notasyonunda bu doğrudur (popüler ad);
> ANCAK belge tarihi olarak ihtiyatla:
> ✅ *"31 Mart 1325 R. (13 Nisan 1909)"*

### 10.4 BOA Tasnif Adı Hataları
- HAT = Hatt-ı Hümâyûn (Cevdet'in eski tasnifinin **devamı değildir**;
  ayrı bir koleksiyon)
- C.SH = Cevdet Sıhhiye; C.S = Cevdet Saray. İkisini karıştırmamak.
- A.MKT.MHM = Sadâret Mühimmesi; MHM (eski) ayrı.

### 10.5 Yazar Adında Karışıklık
- Sicill-i Osmânî'de bir kişi 3 farklı isimle geçebilir (lakap +
  baba adı + memleket). vekayinuvis sözlü/yazılı varyantları normalleştirir.

### 10.6 Atıf Eksik Bilgi
Asla:
> *"BOA, HAT" yetersiz; numara + tarih + Miladi karşılığı şart.*

Her zaman:
> *BOA, HAT, [defter ya da dosya no]/[gömlek/belge no], [tarih H./R.] / [Miladi]*
