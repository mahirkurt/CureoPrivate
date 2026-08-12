# Atıf ve Çeviriyazı Disiplini

RELATIO ve EDITIO modlarında yüklenir.

---

## 1. Atıf sistemi

**Chicago notes-bibliography** (17./18. baskı) esastır — tıp tarihinin baskın sistemi budur
(*Bull Hist Med*, *Med Hist*, *Soc Hist Med*). Vancouver **kullanılmaz** (klinik literatürün
sistemi).

### Şablonlar

```
Kitap
  Yazar Adı Soyadı, *Eser Adı* (Yer: Yayınevi, Yıl), sayfa.

Makale
  Yazar, "Makale Başlığı," *Dergi* cilt, sayı (Yıl): sayfa aralığı, DOI/PMID.

Kitap bölümü
  Yazar, "Bölüm Başlığı," in *Kitap Adı*, ed. Editör (Yer: Yayınevi, Yıl), sayfa.

Arşiv belgesi
  Kurum, Fon Kodu, Kutu/Gömlek, tarih (özgün takvim / Miladî), belge adı.
  Ör.: BOA, DH.MKT, 1234/56, 15 Ra 1305 (1 Aralık 1887), "…".

IIIF / dijital yazma
  Kurum, Koleksiyon, shelfmark, folio/canvas. Manifest: <URI>. Erişim: <tarih>.
  Ör.: Wellcome Collection, MS.1234, fol. 12r. Manifest:
       https://iiif.wellcomecollection.org/presentation/v2/b3135631x. Erişim: 11 Ağustos 2026.

Meclis zabtı
  Hansard, HC Deb, <tarih>, vol <cilt>, cols <sütun>.
  TBMM, <Dönem>. Dönem, <Yasama Yılı>, <Birleşim>. Birleşim, <tarih>, s. <sayfa>.

Resmî yayın
  Resmî Gazete, sayı <no>, <tarih>.
```

### Sert kurallar

1. **Tanımlayıcı uydurulmaz.** DOI/PMID/manifest URI ancak gerçek bir çağrıdan geldiyse yazılır.
2. **Pre-DOI monograf** için tanımlayıcı **verilmez** — bibliyografik künye yeterlidir ve
   doğrudur. Sahte DOI, eksik künyeden daha kötüdür.
3. **Erişim tarihi** her çevrimiçi kaynakta zorunludur.
4. **Sayfa/konum** verilir; "bkz. eser" tek başına yetmez.
5. Snapshot'tan gelen veri (ör. `intl-treaty` CoE) **snapshot tarihi ve yaşı** ile birlikte
   anılır.

---

## 2. Çeviriyazı

| Dil / yazı | Sistem | Not |
|---|---|---|
| Arapça | **IJMES** | Akademik standart; makale içi tutarlılık şart |
| Farsça | IJMES | — |
| Osmanlı Türkçesi | **TDV İA** (Türkçe metin) veya IJMES (İngilizce metin) | Metnin diline göre **biri** seçilir, karıştırılmaz |
| Yunanca | Latinize (klasikçi konvansiyon) | Özel ad + özgün biçim ilk geçişte |
| Sanskritçe | IAST | — |
| Çince | **Pinyin** (+ gerekirse hanzi) | Wade-Giles yalnız alıntıda korunur |
| Japonca | Hepburn | Uzun ünlü işaretleri korunur |
| Kiril | ALA-LC | — |

**Üçlü kural (ilk geçişte):** *özgün terim* + çeviriyazı + modern/açıklayıcı karşılık.
Örnek: **بيمارستان** *bîmâristân* (hastane).

**Tarihsel terim modern karşılığa çevrilmez.** *Consumption* "tüberküloz" diye yazılmaz;
terim korunur, modern okuma varsa hipotez olarak ayrı belirtilir
(`retrospective-diagnosis.md`).

---

## 3. İsim ve tarih disiplini

- Kişi adları dönemin/bölgenin konvansiyonuyla: *Ibn Sīnā* (Latincesi *Avicenna* parantezde).
  Latinize form **birincil** yapılmaz.
- Tarihler `periodization.md` §3'e tabidir: Miladî olmayan tarih **çift** yazılır; Jülyen
  bağlamında O.S./N.S. belirtilir.
- Kurum adları özgün + çeviri: *Mekteb-i Tıbbiye-i Şâhâne* (Imperial School of Medicine).

---

## 4. Alıntı ve telif

- Tam metin **analiz içindir**; toplu birebir çoğaltma yapılmaz.
- CC-BY içerik serbestçe alıntılanabilir; **CC BY-NC** (ör. Wellcome) atıf zorunlu + ticari
  kullanım yok — lisans **manifestten okunur**, varsayılmaz.
- `annas-reader` (Tier 4) kaynaklı metin çıktıya **gövde olarak kopyalanmaz**.
