---
name: literatur
description: DergiPark'ta tam-metin akademik literatür taraması yapar (literatur connector — PDF→HTML + referans) ve tarihyazımı sentezi kurar (HISTORIOGRAPHY modu).
---

`vekayinuvis` skill'ini **HISTORIOGRAPHY** modunda, **`literatur`** (DergiPark) connector'ı
odağıyla çalıştır.

Hedef: kullanıcının belirttiği konu/soru (+ opsiyonel dönem/dizin, örn. "19. yüzyıl Osmanlı
karantina politikaları") için Türk akademik dergi literatürünü tam-metin tara ve ekol/tartışma
haritası kur.

Akış:
1. **`literatur`** — makale arama (yıl/tür/dizin/sıralama filtreli) → **PDF→HTML tam metin** +
   **referans çekme**. ottoman-archives `search_dergipark`'ı (curated OAI-PMH metadata) ile
   birlikte çalıştır (literatur tam-metin ve tüm-dergi kapsamıyla tamamlar).
2. Uluslararası literatür için `paper-search` (Google Scholar/Semantic Scholar/CrossRef) +
   `consensus` + `scholar-gateway` + `exa`; modern uzman/ekol için **`yok-akademik`**.
3. **Bağlam ekonomisi:** büyük tam-metin makaleyi ham işleme —
   `anamnesis.ingest_document(collection=vekayinuvis:run:<12hex>, doc_id=vkrun:<12hex>:doi:…)`
   → `hybrid_query(collection=…, queries=[…])` ile bounded dilim çek; ağır süpürmeyi `arsiv-tarama-distilleri`
   ajanına delege et (${CLAUDE_PLUGIN_ROOT}/shared/context-economy-contract.md).

Çıktı: ekol haritası + ana tartışma eksenleri + dönüm-noktası eserler + son 10 yılın eğilimi;
her iddia hakemli/tam-metin kaynağa bağlı, atıflar DOI/kalıcı URL'li. **TAM-FİLO:** bağlama uygun
tüm akademik server'ları çalıştır ve çıktıya **G0 kapsam manifestosu** ekle (${CLAUDE_PLUGIN_ROOT}/shared/coverage-manifest.md).
