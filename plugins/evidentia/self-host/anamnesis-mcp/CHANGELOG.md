# Changelog — anamnesis-mcp

Bu dosya 2026-09-07 denetiminde başlatıldı. Öncesindeki sürümler `git log` ve
`package.json`'dan geriye dönük olarak kaydedilmiştir.

Biçim: [Keep a Changelog](https://keepachangelog.com/tr/1.1.0/); sürümleme [SemVer](https://semver.org/lang/tr/).

## [Yayınlanmamış]

### Düzeltildi
- **Tek entegrasyon süiti hiç koşmuyordu.** `vitest.config.ts`'te açık `test.include` yoktu;
  Vitest'in varsayılan globu (`**/*.{test,spec}.*`) `test/collection.eval.ts` ile eşleşmiyordu.
  Çapraz-koleksiyon sızıntısını, `forget_collection` izolasyonunu, re-ingest kuyruk artığını,
  kapsamsız `hybrid_query` hatasını ve graf izolasyonunu doğrulayan **tek** süit sessizce
  atlanıyordu. Ölçüm: düzeltme öncesi 6 dosya / 77 test → sonrası **7 dosya / 82 test**.
  (Denetim bulgusu D1)

- **Uzun belge sessizce kesiliyordu.** 400-pencere kapağı aşılınca belgenin kalanı haber
  verilmeden atılıyordu; Tier-2 sözleşmesi belgeleri buraya tam olarak >30 KB'de yönlendirdiği
  için kesilmesi en olası belgeler, buraya gelmesi zorunlu olanlardı. Kesik belgede yapılan
  sorgu "kanıt yok" diyordu — no-fabrication invaryantının sessiz ihlali. Artık ingest
  `chars_indexed` / `chars_total` / `next_offset` döndürür, `offset` parametresiyle kaldığı
  yerden devam edilir ve kesik sonuç `action_required` ile bunu açıkça bildirir. (A1)
- **Karakter ofsetleri uydurulabiliyordu.** Ofsetler chunk'lama sonrası `text.indexOf()` ile
  geri kurulmaya çalışılıyordu; blok ve pencere birleştirmesi `" "` ile yaptığı için CRLF veya
  çoklu boşluk içeren her kaynakta (yani neredeyse her PDF/OCR çıkarımında) ıskalıyor ve
  gerçeğinden ayırt edilemeyen **sentetik** bir ofset dönüyordu. Ofsetler artık blok → cümle →
  pencere → chunk boyunca taşınır ve inşa gereği doğrudur. (A4)
- **Şema bootstrap'ı her araç çağrısındaydı.** Ölçüm: çağrı başına 24 ifade (7 CREATE, 7 ALTER,
  4 tam-tablo `UPDATE … WHERE collection IS NULL` yazması, 2 `COUNT(*)` taraması) ve
  `hybrid_query` bunu iki kez ödüyordu. Artık isolate başına bir kez, Promise ile memoize
  edilmiş (eşzamanlı istekler yarışmaz, hata durumunda yeniden denenir). (A3)
- **Embedding düşünce arama tamamen çöküyordu.** Sorgu embed çağrısı, leksikal kolun aksine
  sarmalanmamıştı; Workers AI kesintisinde FTS5 tek başına cevaplayabilecekken tüm arama
  fırlatıyordu. Artık leksikal-only'ye degrade eder ve `degraded: "vector_unavailable"` ile
  dürüstçe bildirir. (A6)
- **Çoklu `doc_ids` daraltmasında recall çöküyordu.** Vectorize filtresi yalnız tek `doc_id`
  için kuruluyordu; 2+ belgede filtresiz top-K dönüp D1 çoğunu atıyordu — üstelik plugin
  sözleşmelerinin önerdiği yol tam olarak buydu. Artık `$in` ile daraltma vektör koluna iner. (A5)
- **`ingest_document` başarısızlıkta yıkıcıydı.** `forgetDocument` embed'den önce koşuyordu, bu
  yüzden başarısız bir re-ingest eski belgeyi silip fırlatıyordu. Chunk'lama artık silmeden önce
  yapılır. (A7)
- **`doc_id` uzunluğu doğrulanmıyordu.** Vectorize vektör id'sini 64 byte'ta kesiyor ve id
  `<doc_id>::<idx>`; kısıt yalnız istemci tarafında (marmara-mcp) biliniyordu ve aşıldığında
  A7 ile birleşip veri kaybına yol açıyordu. Artık ingest başında doğrulanır. (A8)
- **`score` ölçeği belirsizdi.** Rerank başarılıysa cross-encoder, değilse RRF skoru dönüyordu;
  ayırt eden tek şey bir alan içindeki son ekti. Artık `score_kind: "rerank" | "rrf"`. (A11)
- **Girdi boyutu sınırsızdı.** `ingest_document` artık 1 MB byte tavanı uygular. (A12)
- **Kenar ağırlığı tekrarı ölçüyordu.** Aynı üçlünün yeniden yazılması `weight`'i artırıyordu,
  yani ağırlık "kanıt gücü"nü değil "orkestratör kaç kez tekrarladı"yı ölçüyordu ve `graph.ts`'teki
  her `ORDER BY weight DESC` (neighbors, subgraph, edgesByDocs ve dolayısıyla hybrid_query graf
  paketi) bu sapmayı miras alıyordu. `weight` artık **destekleyen farklı belge sayısıdır**;
  tekrar `assert_count`'ta şeffafça durur. Geçiş: `migrations/0002_edge_evidence.sql`. (A10)

### Güvenlik
- **`forget_document` çapraz-kiracı silmeye açıktı.** Araç yalnız `doc_id` alıyor, koleksiyonu
  satırdan çözüp siliyordu; kimliği doğrulanmış herhangi bir çağıran bir id'yi bilirse başka
  kiracının belgesini kalıcı silebiliyordu. Tek engel, claude.ai web connector'ının, ChatGPT'nin,
  Cursor'ın ve düz curl'ün asla çalıştırmadığı fail-open bir Python hook'uydu. Araç artık
  opsiyonel `collection` alır ve **sahiplik uyuşmazlığını reddeder**; re-ingest de aynı kontrolü
  uygular (yalnız `_legacy` satırları usulüne uygun kapsamlı bir ingest tarafından devralınabilir). (B1)
- **`STRICT_COLLECTION` geçiş anahtarı eklendi** (varsayılan `"0"`). Kapalıyken davranış aynı
  kalır ama her kapsamsız çağrı `anamnesis.scope_violation` satırı olarak yapılandırılmış log'a
  düşer (hangi araç, hangi gerekçe). Açıldığında kapsamsız `ingest_document` / `semantic_search` /
  `forget_document` / `upsert_triples` hata döner. Önce kanıt, sonra kırılma. (B2/B3)

### Düzeltildi (çapraz-repo)
- **`marmara` ve `openathens` GEÇERSİZ koleksiyon üretiyordu.** İkisi de çağıran bir `collection`
  vermediğinde `<plugin>:fetch:<sha1-8>` mint ediyordu; ama sözleşmedeki kind kümesi
  `{run, sess, lib}` — `fetch` yok. Ampirik doğrulama: `resolveWriteCollection` bu adı
  `InvalidCollectionError` ile reddediyor → araç `isError` → `AnamnesisClient` `RuntimeError`
  yükseltiyor. Yani **bu iki sunucunun kendi-mint ettiği her ingest sunucuda başarısızdı**, üstelik
  dört plugin'in `ANAMNESIS_FLEET_SCOPE_PREFIXES` listesi bu geçersiz öneki meşru sayıyordu
  (hook ALLOW verirken sunucu reddediyordu). Önek `<plugin>:run:` yapıldı; sözleşme her iki pakette
  yerel bir regresyon testiyle sabitlendi. CureoHub: `marmara-mcp` 271 test, `openathens-mcp` 203
  test yeşil. CureoPrivate: 10 dosya hizalandı, dört plugin'in hook süiti yeşil
  (cureolex 108 · evidentia 132 · vekayinuvis 79 · historia-medicinae 34 · edupedia 45). (C1)
  Not: `marmara:ebsco` bir koleksiyon değil, `access_path` kaynak etiketidir — dokunulmadı.

### Eklendi
- `CHANGELOG.md` (bu dosya). (Denetim bulgusu D4)
- `migrations/0002_edge_evidence.sql` — `edges.doc_ids` + `edges.assert_count`.
- Test kapsamı 6 dosya / 77 testten **13 dosya / 109 teste** çıktı; yeni süitler:
  `offsets`, `ingest`, `retrieval`, `schema`, `graph-weight`, `tool-surface`
  (sonuncusu gerçek MCP handler'ı üzerinden uçtan uca `tools/list` + `tools/call`).

### Düzeltildi (canlı sevkiyatta ortaya çıktı — 2026-09-07)
- **Toplu vektör silme Vectorize sınırını aşıyordu.** `deleteVectors` 1000'lik gruplar
  gönderiyordu, ama Vectorize bir silme yükünde en fazla **100** id kabul ediyor
  (`VECTOR_DELETE_ERROR 40007`). Yani `forget_document`, `forget_collection` **ve yeni gecelik
  reaper**, 100 chunk'tan büyük her çalışma setinde — yani tam olarak bu substratın taşımak için
  var olduğu büyük korpuslarda — hata veriyordu. Üretim indeksinde 178 chunk'lık bir doğrulama
  koleksiyonu silinirken ölçüldü. Grup boyutu 100'e indirildi; `MockVectorize` de artık aynı
  sınırı uyguluyor (yoksa harness var olmayan bir API'yi modelliyordu).
- **`truncated` yanlış pozitif veriyordu.** Pencere kapağı `units.length >= maxWindows` anında
  tetiklendiği için, kapak **son** pencerede dolduğunda ve geriye hiçbir şey kalmadığında da
  `truncated:true` + dolu `next_offset` dönüyordu; çağıran boş bir devam çağrısı yapmak zorunda
  kalıyor ve daha kötüsü, eksik içerik olmadığı hâlde "eksik" bilgisi alıyordu. `truncated` artık
  "geriye **indekslenmemiş içerik kaldı**" demektir. 126 KB'lık canlı belgede ölçüldü: 4 çağrı → 3.

### Operasyon
- **Süresi dolan scratch artık gerçekten toplanıyor.** `expires_at` ingest'te yazılıp okumada
  filtreleniyordu ama hiçbir şey satırı silmiyordu: cron tetikleyici yoktu, `scheduled()` handler
  yoktu. İki sonucu vardı ve ikisi de sessizdi — D1 sınırsız büyüyordu ve daha kötüsü **Vectorize
  hiç TTL filtrelenmiyordu**: ölü vektörler indekste yer tutmaya ve `topK` aday havuzunda (30-80)
  dönmeye devam ediyor, D1 post-filter onları atınca canlı sonuçlardan aday yeri çalıyorlardı.
  Yani indeks cesetle doldukça recall eriyordu. Artık gecelik cron (`10 4 * * *`) →
  `src/reaper.ts`. Hook temizliği fail-open olduğu için reaper ayrıca **TTL'siz kalmış scratch'i**
  de 14 günden sonra süpürür (son savunma hattı). `lib` asla süpürülmez. (A2)
- **Derin sağlık kontrolü.** `/health` (public, ucuz) aynı kaldı; `/health?deep=1` (Bearer'lı) D1,
  Vectorize ve Workers AI'yı ayrı ayrı yoklar ve düşen bileşeni **adıyla** bildirir — yeşil bir
  liveness probe'u getirim gerçekten çalışıyor mu sorusuna cevap vermiyordu. `smoke_oauth_public.sh`
  bunu kontrol eder.
- **`_legacy` kirliliği görünür oldu.** Global `corpus_stats` artık `legacy_docs` döndürür ve
  sıfırdan büyükse `note` bunu kapsam ihlali göstergesi olarak açıkça beyan eder. (B3)

### Düzeltildi (devam)
- **`subgraph` induced kenarları kaybediyordu.** Induced testi ("her iki uç da istenen kümede")
  `ORDER BY weight DESC LIMIT 500` ön-kesitinden SONRA uygulanıyordu; tohum kümesine 500'den fazla
  kenar değdiğinde induced-olmayan komşular gerçek induced kenarları dışarı itiyor ve araç kenar
  apaçık varken **boş** dönüyordu. Sessiz yanlış-negatif ve tam olarak `lib` korpuslarına
  ölçeklenen şekil. Induced yüklem SQL'e indirildi; 510 kenarlık gerçek bir regresyon testiyle
  sabitlendi. (A9)

### Test
- 6 dosya / 77 test → **18 dosya / 139 test**. Yeni kapsam: reranker yanıt-şekli toleransı
  (`response`/`result`/çıplak dizi) ve bozuk reranker'da RRF sırasına düşme; TTL'nin **okuma
  anında** filtrelenmesi (reaper koşmadan önce); graf gezinmesi (çok-hop BFS, induced subgraph,
  belge-kaynaklı kenarlar); cron reaper'ın uçtan uca tetiklenmesi; derin sağlık kontrolünün
  kapılanması ve düşen bileşeni adıyla bildirmesi.
