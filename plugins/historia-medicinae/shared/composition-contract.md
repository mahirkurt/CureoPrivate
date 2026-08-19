# Kompozisyon Sözleşmesi — historia-medicinae

Bu plugin **tek başına çalışır**, ama kurulu olan komşu katmanları **atlamaz**. Aşağıdaki
matris hangi katmanın ne zaman ZORUNLU, ne zaman opsiyonel olduğunu ve yokluğunda dürüst
degradenin ne olduğunu bağlar.

---

## §1 Teslim (compose) — çıktı nereye gider

| Hedef | Ne zaman | Arayüz |
|---|---|---|
| **`carbon-html-report`** | RELATIO modunun **her dosya-tabanlı** çıktısı | Tek temiz-kopya `.md` → tek `.html`. `<!-- VIZ: … -->` ve `<!-- OPS: … -->` yorumlarını **tüketip siler**. İçerik-bütünlüğü bijektiftir: kaynak metindeki hiçbir sayı/tarih/çekince düşürülemez |
| **`carbon-quarto-scientific`** | Girdi `.qmd`/`.Rmd` ise, veya çıktı istatistik/tablo taşıyorsa (tarihsel mortalite serisi, nicel bibliyometri) | Quarto şablonu + `qmd2carbon.py`; token'ları carbon-html-report'tan miras alır |
| **`dataviz`** | **Her** grafik/çizelge öncesi — kronoloji şeridi, salgın eğrisi, kurum soyağacı, atıf grafiği | Grafik kodunun **ilk satırından önce** okunur |
| **`artifact-diagramming`** | Mekanizma şeması — bulaş zinciri, humoral→hücresel patoloji geçişi, kurumsal silsile | Inline SVG, iki temada okunur |

**Kural:** çıktı bir dosya raporuysa temiz-kopya doktrini uygulanır (bkz. §6).

---

## §2 Delegasyon — hangi işi kime devrederiz

| Hedef | Tetikleyici | Yokluğunda degrade |
|---|---|---|
| **`vekayinuvis`** | Osmanlıca **el yazması** paleografi/HTR · BOA/BCA fon-kutu-gömlek düzeyinde kapsamlı süpürme · belge satın-alma + 300 DPI arşiv okuma · ebced/kronogram çözümü · Hicrî-Rumî çeviri gerektiren derin arşiv işi | Osmanlıca el yazması **transkripsiyonu YAPILMAZ**; katalog künyesi düzeyinde kalınır, kullanıcıya vekayinuvis kurulum önerisi verilir. Metin **asla uydurulmaz** |
| **`evidentia`** | Soru tarihten **çağdaş kanıta** kaydığında — "bu tarihsel tedavi bugün etkili mi", "paleopatolojik bulgunun modern karşılığı", retrospektif tanının klinik geçerliliği | Çağdaş klinik iddia **UNVERIFIED** bırakılır; PRISMA/GRADE düzeyinde kanıt üretilmez ve bu çıktıda beyan edilir |
| **`sci-audit`** | **Her RELATIO çıktısı** — atıf-adli (A ekseni), iddia temellendirme (B), Türkçe bilimsel dil (G) | Bağımsız QA uygulanmaz; çıktıda "bağımsız atıf ve dil denetimi yapılmadı" olarak **açıkça beyan edilir** |
| **`cureolex`** | Tarihsel bir normun **yürürlükteki** hâli sorulduğunda (1219 s.K.'nın bugünkü metni, AYM/Danıştay içtihadı) | Çağdaş norm durumu verilmez; tarihsel katmanla sınırlı kalınır |
| **Distiller alt-ajanları** | Ham MCP gövdesi > 6 KB (bkz. context-economy-contract §1) | Ana bağlamda sınırlı-parça getirime düşülür |

**Rol sınırı (önemli).** `sci-audit` genel bilimsel-metin denetçisidir; **tıp tarihi çeviriyazı,
periyodizasyon ve retrospektif-tanı otoritesi `historia-medicinae`'de kalır.** sci-audit
tamamlayıcıdır, üstün değildir; çakışmada bu plugin'in disiplin kuralı geçerlidir.

---

## §3 Degrade matrisi — meşru degrade ile G0 ihlali farkı

| Durum | Meşru mu | Manifesto satırı |
|---|---|---|
| Plugin **kurulu değil** | ✅ meşru | `skipped: plugin kurulu değil` |
| Connector **anahtarsız** | ✅ meşru | `skipped: anahtar yok` |
| Upstream **oturumu düşük** (devarsiv) | ✅ meşru degrade | `degraded: session_required` |
| Upstream **bloklu** (LoC 403, NLM bot kapısı) | ✅ meşru degrade | `degraded: upstream blocked (erişim yol haritası verildi)` |
| Mod için **gerçekten ilgisiz** | ✅ meşru | `skipped: mod için N/A` + gerekçe |
| **Kurulu/bağlı ama çağrılmadı** | ❌ **G0 FAIL** | — bu satır yazılamaz |

---

## §4 Paylaşılan anamnesis substratı

`anamnesis` paylaşılan RAG/GraphRAG substratı. Tenancy **collection** ile ayrılır
(`{plugin}:{kind}:{id}`; kind ∈ {run, sess, lib} — **lib varsayılan değildir**).
`doc_scope` **yoktur**. Kapsamsız `hybrid_query` / `graph_*` DENY (veya Worker MCP error).

| Plugin | collection | doc_id |
|---|---|---|
| **evidentia** | `evidentia:run:<12hex>` **scratch** | `evrun:<12hex>:<PMID\|DOI>` — koşu bitince forget; kalıcı kütüphane değil |
| cureolex | `cureolex:sess:<session>` | insan-okunur `mevzuat:` / `celex:` / `ecli:` / `rg:` soneki |
| **historia-medicinae** | **`histmed:run:<12hex>`** | **`hmrun:<12hex>:<kanonik>`** (kanonik: `doi/…` · `pmid/…` · `wellcome/…` · `devarsiv/…`) |

Ön-eksiz / collectionsuz ingest yasaktır: bir plugin'in belgesi diğerinin sorgusuna sızar.
Cevap yalnız dönen chunk'lardan; atıf **`doc_id::idx`**. `corpus_stats` küresel gözlemdir,
bu koşunun çalışma seti değildir. Stop'ta silinmez; SessionEnd / startup yalnız kendi
collection'ını `forget_collection` ile temizler.

---

## §5 Companion connector'lar (claude.ai yüzeyi)

`PubMed`, `Paper Search`, `Elicit` claude.ai connector'ları **bağlıysa** kullanılır ve
manifestoda satır alır; bağlı değilse wire'lı karşılıkları (pubmed-epmc, paper-search) işi taşır
ve kayıp olmaz. Companion satırının **hiç yazılmaması** G0 ihlalidir; `skipped: bağlı değil`
yazılır.

---

## §6 Temiz-kopya doktrini (RELATIO)

Dosya-tabanlı her rapor **iki katmanlıdır**:

- **Katman A — Temiz kopya (görünür):** bitmiş, okuyucuya dönük akademik makale. Tam cümleler,
  bilimsel register, açık atıflar (Chicago notes-bibliography; PMID/DOI/arşiv künyesi + erişim
  tarihi), yönetici özeti, kısaltmalar dizini, okuyucuya dönük Yöntem ve Sınırlılıklar bölümü.
- **Katman B/C — Viz + Ops (görünmez):** yalnız `<!-- VIZ: … -->` ve `<!-- OPS: … -->` HTML
  yorumları içinde taşınır; hiçbir zaman render edilmez.

**Sızıntı yasağı:** connector/araç adları, MCP, mod kodları, shard adları, çağrı sayıları,
kapsam manifestosu ve telemetri **görünür gövdeye giremez**. Yöntem bölümü yalnız **kamuya açık
veritabanı ve arşiv adlarını** anar (PubMed, Wellcome Collection, Hansard, BOA) — araç günlüğünü
değil.

Kapsam manifestosu (G0) `<!-- OPS: … -->` bloğunun içinde yaşar; kısa etkileşimli yanıtlarda
görünür olabilir.
