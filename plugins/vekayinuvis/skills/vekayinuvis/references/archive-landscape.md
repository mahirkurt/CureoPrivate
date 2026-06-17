# Archive Landscape — Osmanlı/Türk Arşiv Haritası

> Bu dosya `vekayinuvis` skill'inin arşiv-merkezli sorgularında yüklenir.
> Sorgu **BOA, VGM, TKGM, BCA, ATASE, ISAM, Süleymaniye, Topkapı, Millet
> Yazma, IRCICA, Atatürk Kitaplığı, şer'iyye sicili** gibi kurumsal isim
> içerdiğinde veya belirli bir tasnif/fond sorulduğunda zorunlu yüklenir.

## İçindekiler
1. [Türkiye'deki Devlet Arşivleri](#tr-state)
2. [Türkiye'deki Yazma Eser Kütüphaneleri](#tr-yazma)
3. [Türkiye'deki Diğer Araştırma Kurumları](#tr-research)
4. [Türk Dijital Süreli Yayın Koleksiyonları](#tr-periodicals)
5. [Türkçe Akademik Platformlar](#tr-academic)
6. [Uluslararası IIIF Kütüphaneleri](#international-iiif)
7. [Uluslararası Tertier ve Aggregator Kaynaklar](#international-aggr)
8. [Erişim Akış Şemaları](#access-flows)

---

<a id="tr-state"></a>
## 1. Türkiye'deki Devlet Arşivleri

### 1.1 BOA — Cumhurbaşkanlığı Devlet Arşivleri, Osmanlı Arşivi
- **Kayıt id**: `boa-dab`
- **Erişim**: restricted (BETSİS kataloğu açık; belge görüntüleri için
  kayıt + on-site)
- **URL**: <https://katalog.devletarsivleri.gov.tr>
- **Ana fond grupları (özet)**:

| Tasnif/Fond | Açılım | Dönem | İçerik |
|---|---|---|---|
| HAT | Hatt-ı Hümâyûn | ~1750–1846 | Sultan'ın haşiyeli/cevaplı yazışmaları |
| C.* | Cevdet Tasnifi (konu) | 1500–1840 | C.ADL (adliye), C.AS (askerî), C.BLD (belediye), C.DH (dahiliye), C.EV (evkâf), C.HR (hariciye), C.IKTSD (iktisat), C.MF (maarif), C.ML (maliye), C.NF (nâfi'a), C.SH (sıhhiye), C.SM (saray) |
| A.MKT.* | Sadâret Mektubî Kalemi | 1839–1922 | A.MKT (umumi), A.MKT.MHM (mühimme), A.MKT.MVL (Meclis-i Vâlâ), A.MKT.NZD (nezâret) |
| İ.* | İrade | 1839–1922 | İ.DH, İ.HR, İ.HUS, İ.ML, İ.MMS, İ.MVL, İ.AS, İ.MF, İ.PT vb. |
| Y.* | Yıldız | 1876–1909 | Y.A.RES (resmi maruzat), Y.MTV (mütenevvi), Y.PRK (perakende), Y.EE (esas evrak) |
| DH.* | Dahiliye Nezareti | 1839–1922 | DH.MKT (mektubî), DH.İD, DH.EUM (emniyet), DH.ŞFR (şifre), DH.SAİD (Sicill-i Ahval) |
| MV | Meclis-i Vükelâ Mazbataları | 1885–1922 | Bakanlar Kurulu kararları |
| ML.* | Maliye | her dönem | ML.VRD (varidat), MAD (Maliyeden Müdevver), KK (Kamil Kepeci) |
| TT, TD | Tahrir Defterleri | 15–17c. | Mufassal & icmal nüfus/vergi sayımları |
| MD, MHM | Mühimme Defterleri | 16–18c. | En önemli devlet yazışmaları |
| EV.* | Evkâf | her dönem | EV.HMH (Haremeyn Müfettişliği), EV.MKT |
| MF.MKT | Maarif Mektubî | 1869–1922 | Eğitim bürokrasisi |
| ŞD | Şûrâ-yı Devlet | 1868–1922 | Danıştay öncesi |
| BEO | Bâb-ı Âli Evrak Odası | 1892–1922 | Genel evrak akışı |

- **Önemli not**: BOA katalog araması (BETSİS) tam metin değildir; başlık
  + tasvirî özettir. Belge fotokopisi için akademik akreditasyon gerekir.
- **vekayinuvis için yöntem**: `ottoman_get_source(boa-dab)` → erişim
  yolunu kullanıcıya açıklar; ardından **YÖKtez** üzerinden ilgili belgelerin
  transkripsiyonunu içeren tezleri bulur (genellikle yüksek lisans/doktora
  tezleri 50–200 belge transkripsiyonu içerir).

### 1.2 BCA — Cumhurbaşkanlığı Devlet Arşivleri, Cumhuriyet Arşivi (Ankara)
- **Erişim**: restricted; Ankara'da on-site veya BETSİS sınırlı sayfa görüntüleme
- **Ana fondlar**:
  - **030.10**: Başvekâlet/Başbakanlık Muamelat Genel Müdürlüğü
  - **030.18**: Bakanlar Kurulu Kararları
  - **490.1**: CHP (Cumhuriyet Halk Partisi) arşivi
  - **180.9**: Atatürk arşivi (özel evrak)
  - **051.\***: Diyanet İşleri Başkanlığı
  - **180.\***: Cumhurbaşkanlığı evrakları
  - **272.\***: İçişleri Bakanlığı
- Cumhuriyet erken dönemine (1923–1950) dair tüm idari, askerî, eğitim,
  sağlık kararlarının çekirdek kaynağıdır.

### 1.3 TKGM Kuyûd-ı Kadîme Arşivi
- **Kayıt id**: `tkgm-kuyud`
- **Erişim**: restricted, Ankara on-site
- **İçerik**: Mufassal/icmal tahrir defterleri (15–17c.), vakıf defterleri,
  evkâf-ı hümâyûn defterleri, evlad-ı vakıf defterleri, sıvâzâ defterleri
- Demografik/iktisadi tarih için BOA Tahrir Defterleri ile **tamamlayıcı**;
  bazı eyalet defterleri yalnız burada var.

### 1.4 Topkapı Sarayı Müzesi Arşivi (TS.MA)
- **Kayıt id**: `topkapi-arsiv`
- **Erişim**: restricted, on-site, sınırlı dijitalleştirme
- **TS.MA.d**: Defter (yaklaşık 11,000 defter, 14c. başı–19c.)
- **TS.MA.e**: Evrak (yaklaşık 35,000 belge)
- Erken Osmanlı dönemi için (Fatih, II. Bayezid, Yavuz, Kanuni dönemleri)
  **birincil** öneme sahip; saray, hassa, divan ve dış yazışmalar burada.

### 1.5 VGM Arşivi (Vakıflar Genel Müdürlüğü, Ankara)
- **Erişim**: yarı-açık (vakfiye sureti istek üzerine, mikrofilm)
- **İçerik**:
  - **Vakfiyeler**: 11–20c. arası ~30,000 vakfiye
  - **Hurûfat Defterleri**: 18–19c. vakıf görev atamaları
  - **Atik Şikâyet Defterleri**
  - **Mübayeneşin Defterleri**
- Sosyal tarih, mimari tarih ve kent tarihinin omurgası.

### 1.6 ATASE — Genelkurmay Askeri Tarih ve Stratejik Etüt Arşivi
- **Erişim**: restricted, çoğunlukla 60-yıl kuralı
- **İçerik**:
  - BLG (Balkan Harbi), HRP (Birinci Dünya Harbi 1914–18), İSH (İstiklâl
    Harbi 1919–22) ve sonrası TC dönemi askerî evrakları
- Askerî tarih ve Milli Mücadele araştırmaları için zorunlu.

---

<a id="tr-yazma"></a>
## 2. Türkiye'deki Yazma Eser Kütüphaneleri

### 2.1 Süleymaniye Yazma Eser Kütüphanesi (İstanbul)
- **Kayıt id**: `suleymaniye-yazma`
- **Erişim**: yarı-açık; mikrofilm/dijital görüntü talep edilir
- **Katalog**: <https://yazmalar.gov.tr> (union catalogue)
- **İçerik**: ~110,000 yazma; Osmanlı/İslâmî ilim tarihinin **en zengin**
  tekil koleksiyonu (Ayasofya, Carullah, Hâlet Efendi, Esad Efendi, Hekim Ali
  Paşa, Şehit Ali Paşa, Reisülküttab gibi 100+ koleksiyon).

### 2.2 Millet Yazma Eser Kütüphanesi (İstanbul, Ali Emîrî)
- **Kayıt id**: `millet-yazma`
- **İçerik**: Ali Emîrî Efendi'nin (1857–1924) bağışıyla kurulmuş;
  ~20,000 yazma + tarihî matbu + Ali Emîrî kendi belge koleksiyonu.

### 2.3 Nuruosmaniye Yazma Eser Kütüphanesi
- Sultanahmet-Cağaloğlu bölgesinde; ~5,000 yazma, kelâm ve hadis ağırlıklı.

### 2.4 Beyazıt Devlet Kütüphanesi
- **Kayıt id**: `bdk-hakki-tarik-us`
- **Hakkı Tarık Us Süreli Yayınlar Koleksiyonu**: Osmanlı dönemi süreli
  yayınların **en büyük** dijital koleksiyonu (Tokyo Üniversitesi tarafından
  sunulan ASW portalında erişilebilir).

### 2.5 İBB Atatürk Kitaplığı Sayısal Arşivi (Taksim)
- **Kayıt id**: `ibb-ataturk-kitapligi`
- Geç-Osmanlı İstanbul'unun harita, fotoğraf, süreli yayın ve yazmaları.

---

<a id="tr-research"></a>
## 3. Türkiye'deki Diğer Araştırma Kurumları

### 3.1 İSAM (Türkiye Diyanet Vakfı İslâm Araştırmaları Merkezi)
- **Kayıt id**: `isam`
- **Önemli kapasiteler**:
  1. TDV İslâm Ansiklopedisi'nin yayıncısı ve elektronik versiyon sahibi
  2. **Makaleler Veritabanı** — 50,000+ Türkçe akademik makale taraması
     (Osmanlı, İslâmî, Türk tarihi)
  3. **Şer'iyye Sicili Transkripsiyon Projesi** — bazı vilayet sicilleri
     yayımlanmıştır
  4. Türkçe-Arapça-Farsça-Osmanlıca tezler için zengin kütüphane
- Bağlı bulunduğu TDV İA: `ottoman_get_islam_ansiklopedisi` ile programmatik.

### 3.2 IRCICA (Research Centre for Islamic History, Art and Culture)
- **Kayıt id**: `ircica`
- **Önemli koleksiyon**: II. Abdülhamid Fotoğraf Albümleri (914 albüm,
  ~36,000 fotoğraf); pan-İslâmik geç-Osmanlı dokümantasyonu.

### 3.3 TTK (Türk Tarih Kurumu)
- **Kayıt id**: `ttk`
- **Belleten** dergisi (1937–): Türk tarih yazımının amiral gemisi.
- TTK Yayınları: belge edisyonları, monograflar, çeviriler.

### 3.4 TBMM Kütüphanesi ve Arşivi
- **URL**: <https://acikerisim.tbmm.gov.tr> (Açık Erişim Sistemi)
- Meclis-i Mebusan, Meclis-i Âyan, TBMM Zabıt Cerideleri (tam dijital);
  kanun gerekçeleri, lâyihalar, yasama tarihi.
- **Düstûr koleksiyonu (v1.2 — doğrulandı)**: TBMM Açık Erişim, *Düstûr*
  Tertîb-i Sani (II. Tertib, 1908–1920, 12 cilt) ve Tertib 3 (1920+)
  ciltlerini dijital olarak yayınlamaktadır. **Bu, II. Meşrutiyet ve
  erken Cumhuriyet mevzuatı için en kanonik dijital kaynaktır.**
  - II. Tertib c.1 örnek URL: `acikerisim.tbmm.gov.tr/items/8689f0ba-...`
  - Tetkik tarzı: items/ sayfasında PDF download veya sayfa-sayfa
    JS-rendered viewer.

---

<a id="tr-periodicals"></a>
## 4. Türk Dijital Süreli Yayın Koleksiyonları

| Koleksiyon | Erişim | İçerik |
|---|---|---|
| Hakkı Tarık Us (`bdk-hakki-tarik-us`) | open | Tanzimat sonrası ana gazete ve dergiler |
| Müteferriqa (`muteferriqa`) | yarı-açık | Servet-i Fünûn, illüstre dergiler (yüksek kalite tarama) |
| Atatürk Kitaplığı | open | Geç-Osmanlı İstanbul süreli yayınları |
| Internet Archive (`internet_archive`) | open | Düstûr, Takvîm-i Vekayi, Cerîde-i Havâdis gibi temel belgeler |
| **LoC Hamid II Collection** (`loc`) (v1.2 — doğrulandı) | open IIIF | *Düstûr* tam serisi (1863–1960, tüm tertipler); Abdülhamid albümleri; ünik geç-Osmanlı kayıtları |
| **TBMM Açık Erişim Düstûr** (v1.2 — doğrulandı) | open | *Düstûr* Tertîb-i Sani (1908–1920) ve Tertib 3 (1920+) — kanonik dijital |

---

<a id="tr-academic"></a>
## 5. Türkçe Akademik Platformlar

### 5.1 DergiPark
- **Kayıt id**: `dergipark`
- En kritik dergiler:
  - *Belleten* (TTK) — temel referans
  - *OTAM* (Ankara Üniversitesi Osmanlı Tarihi Araştırma ve Uygulama Merkezi)
  - *Osmanlı Araştırmaları* (İSAM)
  - *Cihannüma* — Karadeniz Tarihi
  - *Vakanüvis* — Sakarya Üniversitesi
  - *Tarih Dergisi* (İstanbul Üniversitesi)
  - *Tarih Araştırmaları Dergisi* (Ankara Üniversitesi)
  - *History Studies* (Samsun Üniversitesi)
  - *Tarih Kritik*
  - ***Osmed*** (Osmanlı Bilimi Araştırmaları, İÜEF) (v1.2 — doğrulandı):
    Osmanlı tıp tarihi ve bilim tarihinin **en yetkili hakemli Türkçe
    dergisi**; tıp mevzuatı ve hekimlik tarihi çalışmalarında
    standart referans
  - *Tıp Tarihi Araştırmaları* (TTAD)

### 5.2 TR Dizin (ULAKBİM)
- **Kayıt id**: `tr-dizin`
- Türk akademik atıf indeksi; abstract + metadata aranabilir.

### 5.3 YÖK Ulusal Tez Merkezi (YÖKtez)
- **Kayıt id**: `yoktez`
- **MCP**: `YokTez MCP` (6 tool)
- **Önem**: Binlerce Osmanlıca tahrir/mühimme/şer'iyye sicili transkripsiyon
  tezi açık erişimli PDF olarak indirilebilir.

### 5.4 Resmî Mevzuat Platformları (v1.2 — yeni)

#### 5.4.1 mevzuat.gov.tr
- **URL**: <https://www.mevzuat.gov.tr>
- **Erişim**: tam açık
- **İçerik**: TC mevzuatının resmî konsolide metinleri (Anayasa, kanun,
  CBK, KHK, tüzük, yönetmelik, yönerge). Her belgenin tam tarihçesi:
  RG yayım sayı/tarih + Düstûr tertib/cilt/sayfa + tüm değişiklikler.
- **KANUN_GEREKÇESİ için kritik**: L4 (Erken Cumhuriyet) ve L5 (Modern
  Türkiye) katmanlarının **tek-tıkla konsolide referansı** buradadır.
- **Örnek**: 1219 sayılı Kanun → `www.mevzuat.gov.tr/mevzuatmetin/1.3.1219.pdf`

#### 5.4.2 resmigazete.gov.tr
- **URL**: <https://www.resmigazete.gov.tr>
- **Erişim**: tam açık (PDF tarama)
- **İçerik**: Resmî Gazete tüm sayıları (1921'den günümüze).
- **KANUN_GEREKÇESİ için**: L4 ve L5 katmanlarının **orijinal yayın
  formatında** kontrolü için.

#### 5.4.3 Lexpera
- **URL**: <https://www.lexpera.com.tr>
- **Erişim**: kısmen açık (bazı içerik abonelik gerektirir)
- **İçerik**: Kanun, yönetmelik, içtihat (AYM, Yargıtay, Danıştay)
  konsolide arama.

---

<a id="international-iiif"></a>
## 6. Uluslararası IIIF Kütüphaneleri

| Kayıt id | Kurum | Ülke | Önemli Osmanlı içeriği |
|---|---|---|---|
| `gallica` | BnF | Fransa | Schefer koleksiyonu, geç-Osmanlı periyodikleri, manuscrits turcs |
| `british-library` | British Library | UK | Or. (Oriental) koleksiyonu, Sloane, Royal MSS, fermân koleksiyonu |
| `bsb-munich` | Bayerische Staatsbibliothek | Almanya | Cod. turc, Cod. arab, Cod. pers, oryantal yazmalar |
| `berlin-sbb` | Staatsbibliothek zu Berlin | Almanya | Ottomanica koleksiyonu (Karabacek), Türkische Handschriften |
| `cambridge-digital` | Cambridge University Library | UK | İslâmî yazmalar; E.G. Browne koleksiyonu |
| `princeton-islamic` | Princeton University Library | ABD | Garrett Collection (one of the largest in Americas) |
| `yale-beinecke` | Yale Beinecke | ABD | Landberg Collection, kalligrafi, münşeât |
| `vienna-onb` | ÖNB | Avusturya | Habsburg-Osmanlı diplomatik evrakı, Cod. Vind. turc/ar |
| `walters` | Walters Art Museum | ABD | Aydınlatılmış İslâmî/Osmanlı yazmaları (open license) |
| `qatar-digital-library` | QDL | Katar | India Office Records — Körfez, Hicaz, Arap eyaletleri |
| `loc` | Library of Congress | ABD | Abdülhamid albümleri, Hampson koleksiyonu |
| `nli-israel` | National Library of Israel | İsrail | Filistin/Suriye/Beyrut Osmanlı dönemi |

---

<a id="international-aggr"></a>
## 7. Uluslararası Tertier ve Aggregator Kaynaklar

| Kayıt id | Kurum | Notu |
|---|---|---|
| `internet_archive` | Internet Archive | Düstûr, Takvîm-i Vekayi, salnâmeler, eski tıp kitapları |
| `hathitrust` | HathiTrust | ABD üniversite kütüphanelerinin Osmanlı dijital eserleri |
| `europeana` | Europeana | AB çoklu-kurum aggregatörü |
| `dpla` | DPLA | ABD aggregatör |
| `tdv-islam-ansiklopedisi` | TDV İA | Türkçe en yetkili Osmanlı/İslâmî ansiklopedi |
| `docorpora` | DOCORPORA | Osmanlıca print için referans transkripsiyon korpusu |
| `otap` | OTAP (UW–Bilkent) | Erken DH transkripsiyon korpusu |

---

<a id="access-flows"></a>
## 8. Erişim Akış Şemaları

### 8.1 BOA Belgesi İçin Tam Yol Haritası
```
1. ottoman_get_source(boa-dab) → erişim koşulları
2. Konuya göre fond tahmini (HAT/Cevdet/A.MKT/İrade/Yıldız/DH/MV)
3. https://katalog.devletarsivleri.gov.tr (BETSİS) sorgu önerisi
4. search_yok_tez_detailed(keyword=<konu>) → mevcut transkripsiyon tezleri
5. Tezler içinde aranan belge varsa → o transkripsiyona güvenle atıf
6. Tezde yoksa → kullanıcıya BOA başvuru/akreditasyon talimatı
```

### 8.2 IIIF Manuscript İçin Tam Yol Haritası
```
1. ottoman_search_iiif(query=<konu>, sources=[gallica, ia, princeton, …])
2. Eşleşen manifest_url(s) toplanır
3. ottoman_fetch_iiif_manifest(manifest_url) → metadata + canvas sayısı
4. ottoman_search_within_manifest (varsa) ile içerik araması
5. (opsiyonel) ottoman_escriptorium_import_iiif → HTR pipeline
6. Atıf: kurum + raf no + IIIF manifest URL + erişim tarihi
```

### 8.3 Şer'iyye Sicili İçin Tam Yol Haritası
```
1. ottoman_get_islam_ansiklopedisi("Şer'iyye Sicilleri") → kavram tabanı
2. Bulunduğu vilayet/kaza tespiti
3. İSAM Şer'iyye Sicili Projesi sayfa kontrolü (web_fetch)
4. search_yok_tez_detailed(keyword=<vilayet/kaza> sicili) → transkripsiyon
5. DergiPark araması → mevcut makaleler
6. (Eğer transkripsiyon yoksa) İSAM/Müftülük başvuru talimatı
```

### 8.4 Cumhuriyet Dönemi (BCA) Belgesi
```
1. ottoman_get_source — BCA için kayıt yok; web_search ile fond tablosu
2. Tahmini fond (030.10/030.18/490.1/180.9 vd.) ile sorgu önerisi
3. search_yok_tez_detailed + ottoman_search_dergipark → transkripsiyonu
   olan tezler/makaleler
4. TBMM Zabıt Ceridesi paralel sorgu (eğer yasama bağlamı varsa) →
   tbmm.gov.tr ya da Internet Archive
5. BCA için Ankara on-site veya BETSİS sınırlı erişim talimatı
```
