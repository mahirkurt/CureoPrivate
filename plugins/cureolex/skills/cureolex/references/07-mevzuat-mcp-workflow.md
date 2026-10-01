# Mevzuat MCP İş Akışları (Workflow Patterns)

Bu dosya, Mevzuat MCP'nin tool'larının mod bazlı **somut kullanım örüntülerini** içerir.

**0.15.1+ (HP production `mevzuat.cureonics.com`, 2026-08 cutover).** Primer first-party bedesten: `search_mevzuat` boş query + `mevzuat_no` / yalnız-rakam NUMARA lookup + `phrase` (Solr); `search_within_mevzuat` belge-içi AND/OR/NOT (EK/GEÇİCİ ağacı; `mevzuat_tur` INTEGER); `get_mevzuat_gerekce` TBMM locator **ve** bedesten `getGerekceContent` tam metin (`gerekceId` yoksa locator-only dürüst). Playwright clone yok. Tool listesinde yoksa uydurma → `manual_required` (ikincil ayna yoktur; 2026-09-12'de kaldırıldı).

## 1. Mevzuat MCP Tool Envanteri (Yeniden)

| Tool | Parametreler | Çıktı |
|------|--------------|-------|
| `search_mevzuat` | query (boş olabilir), `mevzuat_no`, `phrase` (bedesten Solr), sayfalama | Aday liste (`source`) |
| `search_within_mevzuat` | query (AND/OR/NOT / `"ifade"`), `mevzuat_no` + tür | Belge-içi isabet (primer EK/GEÇİCİ ağacı) |
| `list_mevzuat_types` | — | Tür kod tablosu |
| `list_mevzuat_by_type` | tür kodu, (sayfalama) | Sayfalı liste |
| `search_mevzuat_fihristi` | Kanunlar/CBK fihristi araması | Fihrist sonuçları |
| `get_mevzuat_detail` | `mevzuat_no`, `mevzuat_tur`, `mevzuat_tertip?` | Metadata + URL'ler |
| `get_mevzuat_content` | Aynı mevzuat üçlüsü, `madde_no?`, `max_chars` | Düz metin + parsed madde |
| `get_mevzuat_text` | Aynı mevzuat üçlüsü, sayfa/karakter sınırı | PDF → düz metin |
| `get_anayasa` | — | 1982 Anayasası tam metin |
| `search_mulga_mevzuat` | query | Mülga mevzuat |
| `get_onceki_metinler` | Aynı mevzuat üçlüsü | Eski sürümler |
| `download_mevzuat_document` | Aynı mevzuat üçlüsü, `format`, `include_base64` | doc/pdf URL veya base64 |
| `build_mevzuat_semantic_context` | konu kapsamı | Çok katmanlı bağlam |
| `get_mevzuat_gerekce` | `kanun_no` / `gerekce_id` | TBMM locator + bedesten tam gerekçe metni |
| `list_kaysis_types` | — | KAYSİS'e özgü tür kodları |
| `search_kaysis_institutions` | `query` (3–160 karakter) | Kurum adı + `kurum_id` |
| `search_kaysis` | `query`, `kurum_id?`, `turler?`, `mevzuat_no?`, `yururluk`, `page` | KAYSİS katalog kayıtları + kapsam/diagnostics |
| `get_kaysis_detail` | `belge_id` | Künye, açık yürürlük etiketi, PDF erişim durumu |
| `get_kaysis_text` | `belge_id`, `start_page`, `end_page?`, `max_chars` | PDF metni + provenance, OCR/kesilme durumu |
| `search_all_mevzuat` | `query`, `page`, `limit_per_source` (1–50) | İki kaynaktan sonuçlar + `coverage` |

### 1.1. İki kaynaklı keşif ve kaynak kimliği

Konu taramasında `search_all_mevzuat(query="<konu>", page=1,
limit_per_source=10)` ile mevzuat.gov.tr ve [KAYSİS KMS](https://kms.kaysis.gov.tr/)
birlikte taranır. Kurumun yönerge/genelge/karar kataloğu için:

```
list_kaysis_types()
search_kaysis_institutions(query="<kurum adı>")
search_kaysis(query="<konu>", kurum_id=<dönen kurum_id>, yururluk="tumu", page=1)
get_kaysis_detail(belge_id=<sonuçtaki belge_id>)
get_kaysis_text(belge_id=<aynı belge_id>, start_page=1, end_page=3, max_chars=12000)
```

`turler` yalnız `list_kaysis_types` kodlarından seçilir; mevzuat.gov.tr tür kodları
aktarılmaz. `search_kaysis` metin sorgusu boş veya 3–160 karakterdir; numara
aranıyorsa `query="", mevzuat_no="<numara>"` kullanılır. Sayfa 1–10000, kaynak
sayfa boyu 50'dir. `yururluk="tumu"|"yururlukte"|"mulga"` arama filtresidir;
kaynaktaki açık etiket yoksa kayıt durumu **bilinmiyor** kalır.

- **Kimlik:** `kaysis:<belge_id>` ile mevzuat.gov.tr `{tertip}_{tur}_{no}` ayrıdır.
  Aynı başlıklı kayıtlar otomatik birleştirilmez; KAYSİS `belge_id` değeri
  `get_mevzuat_*` veya madde/graf/tarihçe araçlarına gönderilmez. Bu araçlar ve
  `build_mevzuat_semantic_context` mevzuat.gov.tr kapsamındadır.
- **Kapsam:** Her kaynağın `coverage` içindeki `status`, `diagnostics`,
  `page`, `retrieved`, `returned`, `page_truncated`, `total`, `has_more` alanları
  G0 kaydına taşınır. `degraded`/`manual_required`/`error` görünür boşluktur;
  sağlıklı kaynakla devam edilir. `total=null` veya `has_more=null` bilinmeyendir;
  sıfır/false yapılmaz. Kısa sayfa veya limitli sonuç, taramanın tamamlandığı ya da
  mevzuat bulunmadığı anlamına gelmez. `page_truncated=true` ise aynı kaynak
  sayfasını native arama aracıyla tam incele; yalnız sonraki sayfaya geçmek kalan
  kayıtları atlar.
- **Metin ve atıf:** Katalog künyesi tam metin değildir. `selected_pages`,
  `truncated`, `ocr_required`, `missing_text_pages`, `diagnostics` korunur.
  KAYSİS otomatik OCR yapmaz; taranmış/boş metin katmanı veya eksik PDF için
  manuel doğrulama gerekir. `truncated=false`, yalnız seçilen sayfaların
  kesilmediğini gösterir; tüm belgenin okunduğu söylenmez. Kaynak/PDF URL'si,
  `fetched_at`, SHA-256 ve sayfa konumu atıf kaydına alınır; `fetched_at`
  yürürlük tarihi sayılmaz. Bugünkü kayıt belirli bir tarihteki yürürlüğü kanıtlamaz.
- **ChatGPT yüzeyi:** `search` iki kaynaklıdır; `limit` toplam sonuç sınırıdır,
  `search_all_mevzuat.limit_per_source` ise kaynak başınadır. Dönen kimlik aynen
  `fetch(id="kaysis:<belge_id>")` veya `fetch(id="<tertip>_<tur>_<no>")` ile
  kullanılır; native araçlar varsa yukarıdaki ayrıntılı akış tercih edilir.

## 2. Mod Bazlı İş Akışları

### 2.1. DRAFT Modu — Tipik İş Akışı

**Senaryo:** Kullanıcı "ATMP (ileri tedavi tıbbi ürünler) için yeni yönetmelik taslağı hazırla" istiyor.

**Adım 1 — Üst hukuk normu zinciri:**
```
get_anayasa()
   → Md. 17, 56, 73, 124 alın
```

**Adım 2 — Dayanak kanun:**
```
search_mevzuat(query="beşeri tıbbi ürün ruhsat")
   → 1262 sayılı Kanun + 1 sayılı CBK md. 508 vd.
get_mevzuat_detail(mevzuat_no=<sonuçtaki no>, mevzuat_tur=<tür>, mevzuat_tertip=<tertip>)
   → metadata + URL
get_mevzuat_content(mevzuat_no=<aynı no>, mevzuat_tur=<tür>, mevzuat_tertip=<tertip>)
   → tam metin, özellikle dayanak maddesi
```

**Adım 3 — Mevcut yatay mevzuat taraması:**
```
search_all_mevzuat(query="beşeri tıbbi ürün")
search_all_mevzuat(query="ileri tedavi")
search_all_mevzuat(query="hücresel terapi")
search_all_mevzuat(query="ATMP")
```
→ Kurum düzenlemeleri §1.1 ile ayrıca daraltılır. "0 sonuç" yokluk kanıtı değildir;
kaynak erişimi, sayfalama ve alternatif terimler kontrol edilerek kapsam boşluğu yazılır.

**Adım 4 — Mülga / önceki düzenlemeler:**
```
search_mulga_mevzuat(query="hücresel terapi")
search_mulga_mevzuat(query="genetik tedavi")
```
→ Tarihsel arka plan; daha önce neden kaldırıldı?

**Adım 5 — Semantik kapsam:**
```
build_mevzuat_semantic_context(konu="beşeri tıbbi ürün ruhsatlandırma + ATMP")
```
→ Eğer bu tool desteklerse, tüm ana türlerde çoklu katman bağlam.

**Adım 6 — Benzer yönetmelik analizi (model):**
```
get_mevzuat_detail(mevzuat_no=<bulunan yönetmelik no>, mevzuat_tur=<tür>, mevzuat_tertip=<tertip>)
get_mevzuat_content(...)
```
→ Mevcut "klasik" ruhsat yönetmeliğini iskelet olarak alın; ATMP-spesifik adaptasyon yapın.

**Adım 7 — AB müktesebatı kontrolü (manuel — Mevzuat MCP'de yok):**
- EUR-Lex'te Regulation (EC) 1394/2007 (ATMPs)
- (Bu adım için web_fetch veya manuel referans kullanılır)

**Adım 8 — Taslak iskeleti kurma + Md. 15 sıralaması.**

**Adım 9 — Md. 4 + 10-22 + 25 kontrolleri ile yazım.**

**Adım 10 — DEA + BEF + Genel/madde gerekçe üretimi.**

---

### 2.2. AMEND Modu — Tipik İş Akışı

**Senaryo:** "SUT'un 4.2.27.A.2 numaralı maddesinde yer alan onkoloji ilacı ödeme kriterlerinde değişiklik yap."

**Adım 1 — Hedef mevzuatı çek:**
```
search_mevzuat(query="sağlık uygulama tebliği SUT")
get_mevzuat_detail(mevzuat_no=<bulunan SUT no>, mevzuat_tur=<tür>, mevzuat_tertip=<tertip>)
get_mevzuat_content(mevzuat_no=<aynı no>, mevzuat_tur=<tür>, mevzuat_tertip=<tertip>)
```

**Adım 2 — Önceki sürümler:**
```
get_onceki_metinler(mevzuat_no=<aynı no>, mevzuat_tur=<tür>, mevzuat_tertip=<tertip>)
```
→ SUT yıllık değişikliklerle güncellenir; en son onaylı metni teyit edin.

**Adım 3 — İlgili maddenin **tam** metnini çekin** (çoğu zaman uzun, alt bentleri olan bir madde).

**Adım 4 — Md. 18-19 değişiklik kurallarına göre çerçeve madde yazımı:**
```
MADDE 1- 24/3/2013 tarihli ve 28597 sayılı Resmî Gazete'de 
yayımlanan Sosyal Güvenlik Kurumu Sağlık Uygulama Tebliğinin 
4.2.27.A.2 numaralı maddesi aşağıdaki şekilde değiştirilmiştir.

"4.2.27.A.2 — [Yeni metin tırnak içinde, satırbaşı yapılmadan]"
```

**Adım 5 — Karşılaştırma cetveli üretimi (eski metin yanına yeni metin).**

**Adım 6 — Madde gerekçesi (Md. 23 — tekrar yasağı):**
```
MADDE 1 Gerekçesi:
Madde, oral onkoloji tedavisinde son üç yılda yayımlanan 
NCCN ve ESMO kılavuzlarındaki güncellemeler doğrultusunda, 
hastaların kanıta dayalı tedaviye daha hızlı erişebilmesini 
sağlamak amacıyla değiştirilmektedir. Eski metinde yer 
alan [şu] kriter, [bu] gerekçeyle kaldırılmakta; yeni eklenen 
[şu] kriter, [bu] amaçla getirilmektedir. ...
```

---

### 2.3. ANALYZE Modu — Tipik İş Akışı

**Senaryo:** "Bu yönetmelik taslağında hukuka aykırılık var mı?"

**Adım 1 — Hedef mevzuatı tam çek:**
```
get_mevzuat_detail + get_mevzuat_content veya get_mevzuat_text
```

**Adım 2 — Hedef taslağın atıflarını çıkarın:**
- Manuel olarak metinden her atıfı liste.
- Her atfedilen mevzuat için ayrı `get_mevzuat_detail + get_mevzuat_content`.

**Adım 3 — Anayasa çek:**
```
get_anayasa()
```

**Adım 4 — Yedi boyutlu uygunluk denetimi (`references/06`).**

**Adım 5 — Risk değerlendirmesi:**
- Danıştay 10. Daire içtihadı (sağlık)
- AYM içtihadı (belirlilik)
- AİHM içtihadı (öngörülebilirlik)

**Adım 6 — Rapor yazımı.**

---

### 2.4. COMPLY Modu — Tipik İş Akışı

Bu mod ANALYZE'a göre **daha sistematik** ve **kontrol listesi tabanlı**. 19 noktanın her birine `PASS / FAIL / N/A`.

**MCP kullanımı:**
- `get_mevzuat_detail + get_mevzuat_content` — hedef taslak + üst normlar
- `get_anayasa()` — Anayasa kontrolü için
- `search_mevzuat` — örtüşen/çakışan mevzuat tespiti için

**Çıktı:** `references/06-compliance-checklist.md` formatında 19-puanlı rapor.

---

### 2.5. OPINE Modu — Tipik İş Akışı

**Senaryo:** "TİTCK olarak SGK'nın bir SUT değişiklik taslağına resmi görüş hazırla."

**Adım 1 — Görüş bildirilecek taslağı + ek belgeleri al** (kullanıcı sağlar).

**Adım 2 — Arka planda COMPLY:**
```
[19 noktayı uygula]
```

**Adım 3 — Görüş veren kurumun (TİTCK) perspektifinden ek değerlendirme:**
- Bu taslak TİTCK'nın yetki alanına giriyor mu?
- Bu taslak TİTCK'nın ruhsatlandırma kararlarıyla çelişiyor mu?
- ÜTS entegrasyonu nasıl etkilenir?
- Farmakovijilans yükümlülüğü nasıl etkilenir?
- AB CTR ve MDR ile uyum nasıl?

**Adım 4 — İlgili mevzuat çapraz çekimi:**
```
search_mevzuat(query="TİTCK ruhsat")
search_mevzuat(query="Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği")
```

**Adım 5 — EK-1 formatına uygun yapılandırılmış görüş:**
```
T.C.
SAĞLIK BAKANLIĞI
Türkiye İlaç ve Tıbbi Cihaz Kurumu

Sayı: 
Konu: [Taslak Adı] hk. görüşümüz

T.C.
[Görüş İsteyen Kurum]

İlgi: ...
Görüşü istenen taslakla ilgili Kurumumuz değerlendirmesi 
aşağıda sunulmuştur.

1. [Bulgu 1]
2. [Bulgu 2]
...

Yukarıdaki hususlar değerlendirilmek üzere arz/rica olunur.

[İmza]
Kurum Başkanı/Yetkili
```

---

### 2.6. RIA Modu — Tipik İş Akışı

**Senaryo:** "Yeni klinik araştırma yönetmeliği taslağı için DEA + BEF hazırla."

**Adım 1 — Taslağı + hedefini analiz et.**

**Adım 2 — Benchmark araması:**
```
search_mevzuat(query="klinik araştırma")
search_mulga_mevzuat(query="klinik araştırma")
list_mevzuat_by_type(<yönetmelik>)
```
→ AB CTR'a uyum derecesi: ne kadarı uyum, ne kadar boşluk?

**Adım 3 — Etki haritası:**
- TİTCK personel kaynak ihtiyacı (örn. ek 50 uzman)
- Etik kurul yapı değişimi
- Sponsor (firma) maliyet etkisi
- Hastalara erişim etkisi
- Türkiye'nin uluslararası klinik araştırma pazarındaki konumu

**Adım 4 — Senaryo analizi:**
- Baz senaryo: Mevcut sistem devam
- Optimist: Yeni sistem 12 ayda tam uygulama
- Pessimist: 36 ayda kısmi uygulama

**Adım 5 — Bilimsel/Epidemiyolojik Destek Katmanı:**
"Türkiye'de klinik araştırma sayısı son 10 yılda nasıl evrilmiş? Avrupa karşılaştırması nedir?" sorusu için PubMed + ClinicalTrials.gov + Tavily (ECDC + EU Clinical Trials Information System) + Scholar Gateway gibi bilimsel destek MCP'leri kullanılır. Bu çağrı **sadece bilimsel/epidemiyolojik kanıt** için yapılır; mevzuat yazımı cureolex protokolünde kalır.

**Adım 6 — DEA raporu + BEF formu.**

## 3. Sık Karşılaşılan Sorunlar ve Çözümler

### 3.1. `search_mevzuat` 0 sonuç veriyor
- `search_all_mevzuat` ile kaynakları ayrı raporlayın; kurum mevzuatı için §1.1'deki KAYSİS zincirini uygulayın
- Kanun/mevzuat **numarası** biliyorsanız `mevzuat_no` veya yalnız-rakam `query` deneyin (0.15+)
- Daha geniş anahtar kelime deneyin
- `phrase=` ile tam ifade (bedesten Solr)
- Eş anlamlı terim deneyin (örn. "ilaç" yerine "müstahzar", "tıbbi ürün")
- `search_mulga_mevzuat` deneyin (kaldırılmış olabilir)
- Belge içi tarama: `search_within_mevzuat` (`mevzuat_tur` INTEGER; yoksa `get_mevzuat_content` / madde_tree)

### 3.2. `get_mevzuat_content` çok uzun metin
- İlgili maddeleri sentaktik olarak izole edin (Madde N başlığı + sonraki Madde'ye kadar)
- Sadece dayanak maddesi + yetkilendirme + kapsam maddelerini analiz edin

### 3.3. Birden fazla atıf çakışıyor
- Eski tarihliden yeniye sıralayın
- `get_onceki_metinler` ile çakışma sürecini izleyin

### 3.4. Atıf yapacağınız mevzuat henüz çıkmamış
- "Tasarlanmakta olan" ifadesi kullanmayın
- Şu anda yürürlükteki en yakın benzer mevzuata atıf yapın
- Geçici maddede gelecek düzenlemeye atıf yapılabilir

### 3.5. Kullanıcı PDF olarak mevzuat veriyor
- `download_mevzuat_document` ile resmi versiyonu indirin
- PDF içerik tutarsızsa MCP içeriğini öncelikli alın

## 4. MCP Atıf Doğrulama Protokolü

**KRİTİK:** Her atıf yapmadan önce şu doğrulama yapılır:

Mevzuat.gov.tr kimlikleri için aşağıdaki beş adım uygulanır. KAYSİS kimlikleri
için §1.1'deki `get_kaysis_detail` → `get_kaysis_text` ve kaynak yürürlük/provenance
kontrolü uygulanır; KAYSİS'e mevzuat.gov.tr sürüm/tarihçe kapsamı atfedilmez.

```
1. Mevzuatın adı doğru mu?           → get_mevzuat_detail
2. Mevzuatın sayısı doğru mu?         → get_mevzuat_detail
3. Mevzuatın RG tarihi/sayısı doğru mu? → get_mevzuat_detail
4. Atfedilen madde hala yürürlükte mi? → get_mevzuat_content (madde metni)
5. Madde değiştirilmiş mi?           → get_onceki_metinler
```

Bu beş adımdan herhangi biri eksik kalırsa, **atıf yapma**. "MCP üzerinden doğrulanamayan referans" notunu düşün.

## 5. Performans İpuçları

- Aynı oturum içinde aynı mevzuatı tekrar çekmeyin (önce çıkardığınız metni saklı tutun).
- `build_mevzuat_semantic_context` pahalı bir çağrı olabilir; sadece kapsamlı DRAFT veya derin ANALYZE durumlarında kullanın.
- `download_mevzuat_document` sadece OPINE/resmi dosya gerektiren durumlarda.
- Tekrarlı `search_mevzuat` yerine **tek sefer geniş arama + filtreleme** stratejisi daha verimli.
