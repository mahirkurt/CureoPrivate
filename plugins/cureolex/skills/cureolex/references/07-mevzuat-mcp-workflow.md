# Mevzuat MCP İş Akışları (Workflow Patterns)

Bu dosya, Mevzuat MCP'nin tool'larının mod bazlı **somut kullanım örüntülerini** içerir.

**0.15.0 (yerel paket; HP production henüz kesilmedi).** Primer first-party bedesten: `search_mevzuat` boş query + `mevzuat_no` / yalnız-rakam NUMARA lookup + `phrase` (Solr); `search_within_mevzuat` belge-içi AND/OR/NOT (EK/GEÇİCİ ağacı); `get_mevzuat_gerekce` TBMM locator **ve** bedesten `getGerekceContent` tam metin. Playwright clone yok. Canlı `mevzuat.cureonics.com` hâlâ 0.14.x ise phrase / `search_within` / tam gerekçe o uçta **yoktur** — tool listesinde yoksa uydurma; ikincil `mevzuat-bilgisi` (wire'lıysa) veya `manual_required`.

## 1. Mevzuat MCP Tool Envanteri (Yeniden)

| Tool | Parametreler | Çıktı |
|------|--------------|-------|
| `search_mevzuat` | query (boş olabilir), `mevzuat_no`, `phrase` (bedesten Solr), sayfalama | Aday liste (`source`) |
| `search_within_mevzuat` | query (AND/OR/NOT / `"ifade"`), `mevzuat_no` + tür | Belge-içi isabet (primer EK/GEÇİCİ ağacı) |
| `list_mevzuat_types` | — | Tür kod tablosu |
| `list_mevzuat_by_type` | tür kodu, (sayfalama) | Sayfalı liste |
| `search_mevzuat_fihristi` | Kanunlar/CBK fihristi araması | Fihrist sonuçları |
| `get_mevzuat_detail` | mevzuat_id | Metadata + URL'ler |
| `get_mevzuat_content` | iframe URL / madde drill-down | Düz metin + parsed madde |
| `get_mevzuat_text` | mevzuat_id | PDF → düz metin |
| `get_anayasa` | — | 1982 Anayasası tam metin |
| `search_mulga_mevzuat` | query | Mülga mevzuat |
| `get_onceki_metinler` | mevzuat_id | Eski sürümler |
| `download_mevzuat_document` | mevzuat_id | doc/pdf base64 |
| `build_mevzuat_semantic_context` | konu kapsamı | Çok katmanlı bağlam |
| `get_mevzuat_gerekce` | `kanun_no` / `gerekce_id` | TBMM locator + bedesten tam gerekçe metni |

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
get_mevzuat_detail(mevzuat_id=<1262>)
   → metadata + URL
get_mevzuat_content(iframe URL)
   → tam metin, özellikle dayanak maddesi
```

**Adım 3 — Mevcut yatay mevzuat taraması:**
```
search_mevzuat(query="beşeri tıbbi ürün")
search_mevzuat(query="ileri tedavi")
search_mevzuat(query="hücresel terapi")
search_mevzuat(query="ATMP")
```
→ Eğer "0 sonuç" çıkarsa, alanın hiç düzenlenmediği veya farklı bir terimle düzenlendiği anlaşılır.

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
get_mevzuat_detail(mevzuat_id=<Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği>)
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
get_mevzuat_detail(mevzuat_id=<SUT>)
get_mevzuat_content(iframe URL)
```

**Adım 2 — Önceki sürümler:**
```
get_onceki_metinler(mevzuat_id=<SUT>)
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
- Kanun/mevzuat **numarası** biliyorsanız `mevzuat_no` veya yalnız-rakam `query` deneyin (0.15.0; canlı 0.14.x uçta yoksa kelime araması veya ikincil)
- Daha geniş anahtar kelime deneyin
- `phrase=` ile tam ifade (bedesten Solr; canlı 0.14.x uçta yoksa atla)
- Eş anlamlı terim deneyin (örn. "ilaç" yerine "müstahzar", "tıbbi ürün")
- `search_mulga_mevzuat` deneyin (kaldırılmış olabilir)
- Belge içi tarama: `search_within_mevzuat` (canlı 0.14.x uçta yoksa `get_mevzuat_content` / madde_tree)

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
