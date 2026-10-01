# Türkiye Katmanı — kapsam ve sınır

Türkiye bağlamı tetiklendiğinde yüklenir.

---

## 1. Bu katman ne yapar, ne yapmaz

Kullanıcı kararı gereği Türkiye **tam kapsam** içindedir: Osmanlı–Türk tıp tarihi bu plugin'de
küresel karşılaştırmanın **bir bölgesi** olarak tam derinlikte yaşar.

**Ama tekrar yazılmaz.** `vekayinuvis` plugin'i Osmanlı–Türk tıp tarihi için 987 satırlık,
doğrulama-statüsü etiketli bir külliyat taşır (`vekayinuvis/skills/vekayinuvis/references/medical-history.md`):
kurumsal kronoloji (1228–1953), mevzuat korpusu (1827–1953), Osmanlı tıp literatürü ve
şahsiyetleri, tıp dergileri ve cemiyetleri, beş arşiv çağrı reçetesi, 1219 sayılı Kanun
aparatı ve dört Türkiye-özgü Quellenkritik filtresi.

| Konu | Nerede |
|---|---|
| Osmanlı–Türk kurumsal kronoloji, mevzuat korpusu, şahsiyet külliyatı, arşiv reçeteleri | **`vekayinuvis`** (kurulu ise çağrılır) |
| Osmanlıca **el yazması** paleografi/HTR, ebced, BOA derin süpürme, belge satın-alma | **`vekayinuvis`** (delegasyon) |
| 1219/1593'ün **yürürlükteki** hâli, AYM/Danıştay içtihadı | **`cureolex`** |
| Türkiye'nin **küresel karşılaştırmadaki yeri**, TR akademik literatürün taranması, TR yasama kaydının tarihsel okunması | **burada** |

---

## 2. Burada yapılan iş

1. **TR akademik tarama** — `literatur` (DergiPark: *Osmanlı Bilimi Araştırmaları*, *Tıp Tarihi
   Araştırmaları*, *Lokman Hekim Dergisi*) + `yoktez` (tıp tarihi ve deontoloji tezleri).
   Bu literatür Batı indekslerinde **büyük ölçüde görünmez**; taranmaması kapsam kaybıdır.
2. **TR yasama kaydının tarihsel okunması** — `mevzuat:search_mulga_mevzuat` +
   `get_mevzuat_gerekce`, `tbmm` zabıtları, `resmigazete` (1920+) yayın kaydı.
   Örnek: 1219 sayılı Tababet ve Şuabatı Sanatlarının Tarzı İcrasına Dair Kanun (1928) ve
   1593 sayılı Umumi Hıfzıssıhha Kanunu (1930) müzakerelerinin **zabıttan** okunması.
3. **Katalog düzeyinde arşiv** — `devlet-arsivleri` ile künye/fon-kutu-gömlek; derin zanaat
   `vekayinuvis`'e devredilir.
4. **Karşılaştırma** — TBMM müzakeresi ↔ Hansard; 1593 ↔ İngiliz Public Health Act'leri;
   Osmanlı karantina rejimi ↔ uluslararası sanitary konvansiyonlar.

---

### 2.1 KAYSİS kurumsal düzenleme katmanı

Türkiye kurum/kamu sağlığı sorusunda `mevzuat:search_all_mevzuat(query="<konu>",
page=1, limit_per_source=10)` ile mevzuat.gov.tr ve
[KAYSİS KMS](https://kms.kaysis.gov.tr/) birlikte taranır. Kurumun yönerge,
genelge veya kararlarını daraltmak için altı yeni aracın akışı şöyledir:

```
list_kaysis_types()
search_kaysis_institutions(query="<kurum adı>")
search_kaysis(query="<konu>", kurum_id=<dönen kurum_id>, yururluk="tumu", page=1)
get_kaysis_detail(belge_id=<sonuçtaki belge_id>)
get_kaysis_text(belge_id=<aynı belge_id>, start_page=1, end_page=3, max_chars=12000)
```

`turler` KAYSİS listesinden seçilir; mevzuat.gov.tr tür kodu kullanılmaz.
Kurum sorgusu 3–160 karakter; `search_kaysis.query` boş veya 3–160 karakterdir.
Numara için `query="", mevzuat_no="<numara>"`; sayfa 1–10000, kaynak sayfa
boyu 50'dir. `yururluk="tumu"|"yururlukte"|"mulga"` filtredir; kaynakta
açık durum etiketi yoksa bilinmiyor kalır. **Bugünkü KAYSİS kaydı tarihsel
yürürlüğü kanıtlamaz.** Dönemin metni ve değişim zinciri RG/zabıt/arşivle teyit
edilir; bugünkü kurumsal düzenleme geçmişe yansıtılmaz.

`kaysis:<belge_id>` ile mevzuat.gov.tr `{tertip}_{tur}_{no}` ayrı kimliklerdir;
aynı başlıklar otomatik birleştirilmez. KAYSİS kaydı `get_mevzuat_*`, madde/graf
ve önceki metin araçlarına verilmez. ChatGPT `search` iki kaynaklıdır;
`limit` toplam sonuç sınırıdır, `limit_per_source` kaynak başınadır.
`fetch(id="kaysis:<belge_id>")` dönen kimlikle çalışır.

Her `coverage` satırının `status`, `diagnostics`, `page`, `retrieved`,
`returned`, `page_truncated`, `total`, `has_more` alanlarını kapsam kaydında
koru. `degraded`/`manual_required`/`error` görünür boşluktur; erişilen kaynakla
devam edilir. `total=null`/`has_more=null` bilinmeyendir; sıfır/false sayılmaz.
Kısa/boş sayfa tarihsel kayıt yokluğu kanıtı değildir. `page_truncated=true`
ise aynı sayfayı native kaynak aramasıyla tamamla; yalnız sonraki sayfaya geçme.

Katalog künyesi tam metin değildir. PDF'de `selected_pages`, `truncated`,
`ocr_required`, `missing_text_pages` ve `diagnostics` korunur; KAYSİS otomatik
OCR yapmaz. Taranmış/eksik metin manuel doğrulama gerektirir.
`truncated=false` yalnız seçilen sayfaların kesilmediğini söyler; belge bütünü
okunmuş sayılmaz. Kaynak/PDF URL'si, `fetched_at`, SHA-256 ve sayfa konumu
atıf kaydına alınır; `fetched_at` tarihsel yürürlük tarihi değildir.

---

## 3. Devlet Arşivleri oturum kuralı

`devlet-arsivleri` **tek-cihaz oturum kilidi** taşır. Her arşiv sorgusundan **önce**
`devarsiv_session_status` çağrılır. `session_required` dönerse:
- kullanıcıya "resmî katalog oturumu düştü, HP noVNC re-login gerekiyor" bildirilir,
- manifestoda `degraded: session_required` yazılır (**skip değil**),
- iş `ottoman-archives` + `yoktez` + `literatur` ile **degrade devam eder**; belge içeriği
  asla uydurulmaz.

---

## 4. Türkiye-özgü Quellenkritik filtreleri

Dört filtre `vekayinuvis` külliyatında ölçülmüş ve belgelenmiştir (erken Cumhuriyet
laik-Batılılaşmacı · 1980 sonrası Türk-İslâm sentezi · salt pozitivist bilimsel-tarih ·
hagiyografik meslekî anı). Burada **tekrarlanmaz**; TR ikincil literatürü değerlendirilirken
o katman çağrılır. `vekayinuvis` kurulu değilse filtre farkındalığı `quellenkritik.md` §7'nin
genel karşılıklarıyla (Whig, kutlama tarihi, büyük adam anlatısı) sürdürülür ve eksiklik
beyan edilir.

---

## 5. Çeviriyazı

Türkçe metinde **TDV İA**, İngilizce metinde **IJMES** — biri seçilir, karıştırılmaz
(`citation-and-transliteration.md` §2). Tarihler çift yazılır: Hicrî/Rumî + Miladî.
