# Vekayinüvis — Bağlam Ekonomisi ve Büyük-Veri Sözleşmesi

**Problem:** vekayinüvis **tam-filo** çalışır — çekirdek (ottoman-archives · devlet-arsivleri · yoktez) + akademik companion (literatur · consensus · scholar-gateway · exa · tavily · paper-search) + destekleyici (yok-akademik) bağlama uygun her sorguda ateşlenir. Bu, ham hâliyle **onlarca büyük belge** (belge transkripsiyonları, tez PDF'leri, DergiPark tam-metin makaleler, IIIF manifest/within-manifest blokları, İА maddeleri, katalog sonuç sayfaları) üretir; hepsini ana bağlam penceresine dökmek pencereyi taşırır ve **detay atlar / tutarsız** sentez üretir. Bu sözleşme, "hepsi çalışsın + hiçbir detay atlanmasın" ile "bağlamı boğma"yı uzlaştıran **zorunlu** disiplindir.

**Değişmez:** ana pencere yalnız (a) kullanıcı talebi, (b) mod planı, (c) G0 kapsam manifestosu, (d) damıtılmış zarflar (`arsiv_distillate`), (e) `evidence_ledger` (E### atıflar), (f) nihai artefakt tutar. **Ham araç çıktısı ana pencerede ASLA akıl yürütülmez.**

---

## 1. Üç-katmanlı bağlam ekonomisi

| Katman | Ne | Kapasite | Kural |
|---|---|---|---|
| **Tier 0 — Ana pencere** (kıt) | Talep · mod planı · G0 manifesto · `arsiv_distillate` zarfları · evidence_ledger · nihai metin | En değerli; korunur | Ham getirim **girmez**. Yalnız ≤~20 bulguluk zarflar + kanonik atıflar (fon/kutu/gömlek, tez-no, DOI). |
| **Tier 1 — Distiller alt-ajanı** (izole) | `arsiv-tarama-distilleri` (+ istenirse paralel shard'lar) | Kendi bağlam penceresi | Ham MCP çıktısını KENDİ penceresinde tüketir; ana pencereye yalnız kompakt `arsiv_distillate` + `coverage` döner. |
| **Tier 2 — RAG substratı** (sınırsız, harici) | `anamnesis` (Vectorize RAG + D1 GraphRAG) | Pencere-dışı; kalıcı | Büyük tam-metin buraya **ingest** edilir; ana pencere yalnız sınırlı, provenance-damgalı **dilim** çeker. |

**Akış:** MCP ham çıktı → Tier 1 (distiller) VEYA Tier 2 (anamnesis) → ana pencereye yalnız damıtılmış sonuç. Ham veri hiçbir zaman Tier 0'ı geçmez. Böylece **tüm araçlar her koşumda çalışır** (detay atlanmaz) ama pencere taşmaz.

## 2. Tam-filo'yu sharding ile taşımadan çalıştırma

Tek bir distiller'a tüm fleet'i vermek onun KENDİ penceresini de taşırabilir. Geniş süpürme **≤4 paralel shard**'a bölünür; her shard bağımsız `arsiv-tarama-distilleri` çağrısıdır, her biri kompakt zarf + kısmi `coverage` döner; ana pencere bunları tek G0 manifestosunda birleştirir:

| Shard | Server kümesi | Odağı |
|---|---|---|
| **S1 — Resmî katalog** | devlet-arsivleri (arsiv=1/2/3/4; search / semantic_search / list_fon_categories→detailed_search enumerasyon) | fon/kutu/gömlek + künye + 1000-tavan aşımı |
| **S2 — Keşif + IIIF + takvim** | ottoman-archives (registry, IIIF, İА, convert_date, HTR) | dijital nüsha + kavram tabanı |
| **S3 — Tez + literatür + tam-metin** | yoktez + literatur (DergiPark tam-metin) + openathens (lisanslı) + annas-reader (son çare) | transkripsiyon + hakemli makale + kitap/makale tam-metin şelalesi |
| **S4 — Akademik/doktrin** | consensus · scholar-gateway · exa · tavily · paper-search · yok-akademik | tarihyazımı + uzman/ekol |

Shard'lar **paralel** dağıtılır. Tüm server'lar ateşlenir (tam-filo korunur) AMA hiçbir distiller penceresi taşmaz ve ana pencere yalnız ≤4 kompakt zarf görür.

## 3. Kanonik artefakt cache (bir-kez-getir)

Bir belge/kaynak **kararlı kimliğiyle** (fon/kutu/gömlek+item_id · tez-no · DOI · IIIF manifest URL · İА madde) bir kez getirildiğinde, oturum-kapsamlı kanonik cache'e yazılır (distillate + varsa `anamnesis doc_id`). Sonraki modlar (SOURCE_HUNT → ARCHIVE_DEEP_DIVE → ACADEMIC_REPORT) **aynı belgeyi yeniden getirmez**; cache'lenen distillate/ingest'e atıfla çalışır.

**Cache anahtarı:** `{kaynak}:{kanonik_id}` (ör. `devarsiv:2/DH.İ.UM/22-19/31664060`, `yoktez:<tez-no>`, `doi:<...>`, `iiif:<manifest-url>`). Cache girişi: `{distillate_ref, anamnesis_doc_id?, as_of, fetched_at}`.

## 4. Chunking ve navigasyon disiplini (büyük belgeyi kör getirme)

Büyük bir belgeyi **asla** kör (`max_chars` limitsiz / tam PDF) getirme. Protokol:

1. **Önce yapısal navigasyon** (hafif): katalog araması (`devarsiv_search` → künye), IIIF manifest metadata (`ottoman_fetch_iiif_manifest` → canvas listesi), tez sayfa dizini (`get_yok_tez_thesis_details`) ile hedefi LOKALİZE et.
2. **Yalnız hedef parçayı çek:** `ottoman_search_within_manifest` (belge içi arama) · `get_yok_tez_document_markdown(page)` (sayfa-bazlı) · DergiPark makalesinin ilgili bölümü. Belge_url yalnız referans olarak taşınır — tam görüntü/PDF ana pencereye çekilmez.
3. **Tam-metin gerekiyorsa** (transkripsiyon analizi, tarihyazımı sentezi, tam rapor): Tier 2 `anamnesis`'e ingest → bounded query. Kanonik doc_id ile bölüm-düzeyi getirim; tam konsolide metni ana pencereye çekme.
4. **Taranmış/OCR gerektiren nüsha:** IIIF görüntü → (opt-in) eScriptorium HTR → çıktı > eşik ise anamnesis'e ingest.

## 5. Bağlam bütçesi + devre-kesici

- **Mod-başına yumuşak bütçe:** ana pencerede damıtılmış getirim ≤ ~25-30K karakter. Aşıldıysa → daha agresif damıtma, en eski ham izleri evict et.
- **Devre-kesici (sert):** tek bir araç çıktısı > ~6KB → o çıktı **ham işlenmez**; zorunlu olarak `arsiv-tarama-distilleri` / `anamnesis`'e yönlenir.
- **Aşamalı özetleme (extract-then-evict):** her mod fazından sonra ara getirimleri kompakt `evidence_ledger` (E###: kaynak + fon/kutu/gömlek/DOI + dilim) kayıtlarına çök, ham izi evict et. Bir sonraki faz yalnız ledger'ı görür.
- **Anahtar-yok / oturum-yok degrade:** `anamnesis` anahtarı yoksa → §4 bounded-chunk fetch (within-manifest + tez sayfa). `devlet-arsivleri` oturumu düşükse → `session_required` beyan + ottoman/yoktez/literatur ile degrade. Manifestoda dürüstçe yaz; asla ham döküm, asla uydurma.

## 6. anamnesis çağrı disiplini (evidence_index)

```
# Büyük belge/tam-metin geldi (> eşik):
anamnesis.ingest_document(doc_id="yoktez:0123456", text=<tez tam-metni>, metadata={anabilim, yil, ilgili_belge})
anamnesis.ingest_document(doc_id="devarsiv:2/DH.İ.UM/22-19", text=<transkripsiyon/özet>, metadata={fon, kutu, gomlek, tarih_H})
# Sınırlı, çok-sorgulu getirim (ana pencereye yalnız bunlar gelir):
anamnesis.hybrid_query(doc_scope="yoktez:0123456", queries=["veba tahaffuzhane tedbir", "İzmir liman karantina", "tarih"])
# İlişki grafiği (prosopografi/kronoloji):
anamnesis.upsert_triples(triples=[["Mustafa Behçet","görev","Hekimbaşı"], ["olay:31 Mart","tarih","H-1327"]])
anamnesis.graph_neighbors(node="kişi:Mustafa Behçet", rel="görev")
```

Aynı `doc_id` iki kez ingest edilmez (kanonik cache §3). Getirim daima provenance-damgalı (doc_id + fon/kutu/gömlek/sayfa) döner → `evidence_ledger` `E###` kaydına bağlanır → atıf disiplinine (fon/kutu/gömlek + çift-tarih) beslenir.

**Devarsiv async-OCR + arşiv-sayfa disiplini** (`skills/toplu-okuma`, `skills/arsiv-oku`):
Async OCR sonucu: `ocr_result(include_text=true)` TEK SEFER okunur → anamnesis `ingest_document(doc_id='devarsiv:<code>')` → ham metin ana pencereden düşürülür; izleyen erişim `hybrid_query`. `get_archive_page` görüntüleri ana pencerede sayfa-sayfa tüketilir (distiller'a gönderilmez — görü ana asistanda).

## 7. Özet — beş değişmez

1. **Ham veri Tier 0'ı geçmez** — distiller (Tier 1) veya anamnesis (Tier 2) üzerinden.
2. **Tam-filo sharding ile** — ≤4 paralel distiller, her biri bounded zarf; tüm server'lar çalışır, hiçbiri sessizce atlanmaz.
3. **Bir-kez-getir** — kanonik cache, mod tekrarında yeniden getirme yok.
4. **Kör getirme yok** — yapısal navigasyon → hedef chunk → gerekirse anamnesis.
5. **Devre-kesici + evict** — büyük çıktı zorunlu damıtılır; faz sonu ham iz atılır.

Hepsi **fail-safe**: bir katman yoksa (anamnesis anahtarı yok, oturum düşük, companion bağlı değil) daha düşük katmana degrade eder ve **coverage manifestosunda beyan eder** — asla ham döküm, asla uydurma, asla sessiz atlama.
