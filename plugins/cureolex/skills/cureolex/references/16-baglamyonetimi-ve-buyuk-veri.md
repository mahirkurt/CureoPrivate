# Referans 16 — Bağlam Yönetimi ve Büyük-Veri Operasyonel Protokolü

Bu dosya, `shared/context-economy-contract.md` sözleşmesinin **operasyonel yürütme kılavuzudur** — hangi durumda hangi katmanı, hangi araç parametreleriyle çağıracağını adım adım tanımlar. Tam-filo (21 kaynak MCP her sorguda) çalışırken bağlamı boğmadan **en doğru ve kapsamlı** getirimi sağlar.

## A. Karar ağacı — bir belge geldiğinde

```
Belge/getirim geldi
├─ Küçük (≤6KB) ve tek-mod kullanımı? → ana pencerede kullan (Tier 0), evidence_ledger'a işle
├─ Büyük (>6KB) veya çok-mod/çok-kapı kullanımı?
│   ├─ anamnesis anahtarı VAR? → Tier 2: ingest_document(collection=cureolex:sess:<id>, doc_id=<collection>:<kanonik>) → hybrid_query(collection, doc_ids[]) bounded dilim
│   └─ anamnesis anahtarı YOK? → §C bounded-chunk fallback (madde_tree → hedef chunk)
└─ Çok-server ham süpürme? → Tier 1: sharded distiller (§B), ana pencereye yalnız zarf
```

## B. Sharded tam-filo dağıtımı (paralel distiller)

Her sorguda 4 shard'ı **paralel** dağıt (bağımsız görevler — tek turda). Her shard bağımsız distiller çağrısıdır; ana pencere 4 kompakt zarfı G0 manifestosunda birleştirir.

**S1 — TR çekirdek** (`legal-distiller`):
> "Konu: <T>. Mod: <M>. S1 tools_used semantik sırası eksiksiz (kalıcı alt küme yok): mevzuat list_types→by_type/search_kanun|search_mevzuat→detail→anayasa→semantic_context→mulga/fihrist→madde_tree/timeline/relations→search_within→content/text→gerekçe→resolve_RG→list_kurumlar (+AMEND onceki_metinler/madde_diff); RG rg_info→resolve→search→toc→item→pdf→ocr; TİTCK list_datasets→guidelines→drugs… (cihaz≠TİTCK); TBMM search_teklif→get(sira_no)→search_kanun locator→komisyon/havale→tutanak (DSpace≠GK)→milletvekili→OA; sb server_info→birimler→kategoriler→belgeler/kılavuz/kurul→taslaklar→search→get; detsis resolve→kunye→…; Md.90/5 treaty_status+reservations→coe 164/211→intl_treaty_info; eurlex browse→search→lookup_celex→…. ≤15 bulgu + coverage."

**S2 — Karşılaştırmalı** (`comparative-law-researcher`):
> "Konu: <T>. S2 tam süpürme sırası: health-policy semantic_search→govinfo/congress/FR/japan_search/australia_search/china_recent→*_fetch/ecfr; german search→parse/validate→get_provision→currency→SONRA EU ailesi (premium case_law çağırma); eurlex browse→search→lookup→get/relations/cases; fedlex search(keywords)→get_by_sr(params) (+RIA: open/search/get_consultation); **uk-legal legislation_search→_get_toc→_get_section**→case→judgment→hansard→bills→votes→committees→OSCOLA (Open Law çapraz/yedek); ich_server_info→list→search→get→history (+M4/M8); intl-treaty treaty→coe→info→**uhri_search→uhri_fetch_document**; eudamed (cihaz; ÜTS yok); oecd categories→dataflows→indicators→structure→query→url (**GOV_REG** RIA); Open_Law/Ansvar bağlıysa. Conscious exclude: german premium · ChatGPT alias · ÜTS · fedlex recent+termdat — UHRI/legislation_* exclude DEĞİL. Matris+coverage."

**S3 — Doktrin/içtihat** (`legal-distiller`):
> "Konu: <T>. yok-akademik search→profile/full→publications/projects/theses/collaborators; literatur search→pdf_to_html→references; yoktez search→get_details (G7)→markdown; Yargı (bağlıysa). ≤10 bulgu + coverage."

**S4 — Klinik** (evidentia `evidence-synthesizer` / `/evidentia`): zenginleştirilmiş sorgu (composition-contract §1).

Zarflar geldikten sonra ana pencere yalnız 4 zarf + birleşik G0 manifestosu görür; ham getirim distiller pencerelerinde kalır.

## C. Bounded-chunk fetch (anamnesis yoksa veya hedef madde biliniyorsa)

Büyük mevzuatı **asla** limitsiz `max_chars` ile getirme. Sıra:

1. **Yapı:** `get_mevzuat_madde_tree(mevzuat_no, tur, tertip)` → madde başlıkları + numaraları (hafif).
2. **Zaman/ilişki:** gerekirse `get_mevzuat_timeline` (yürürlük) · `get_mevzuat_relations` / `ilga_zinciri` (dayanak/ilga kenarları).
3. **Belge-içi arama (0.15+):** `search_within_mevzuat` ile hedef madde/EK/GEÇİCİ'yi lokalize et (`mevzuat_tur` INTEGER).
4. **Hedef chunk:** `madde_acikla(madde_no)` VEYA `get_mevzuat_content(madde_no)` / `get_mevzuat_text(chunk_index=i, chunk_size=n)` / `(start_page, end_page)` / `(max_chars=<makul>)`.
5. **Gerekçe:** `get_mevzuat_gerekce` — bedesten tam metin (`content_source=bedesten`); `gerekceId` yoksa locator-only. Playwright PDF-markdown uydurma.
6. **İndirme:** `download_mevzuat_document(include_base64=false)` → yalnız URL (base64 gövdesini ana pencereye çekme).

Parametre notu: `mevzuat_no`/`mevzuat_tertip` INTEGER. as_of tarihli geçmiş sürüm için `get_mevzuat_madde_tree(as_of_date=...)`.

## D. anamnesis (Tier 2) tam çağrı örneği

`doc_scope` **yoktur**. Collection + önekli `doc_id` (insan kuyruğu `mevzuat:`/`celex:`/`ecli:`/`rg:` korunur). G0–G9 aynı `cureolex:sess:<id>`.

```text
# 1) Bir kez ingest (collection + önekli kanonik id — ikinci kez ingest edilmez):
anamnesis.ingest_document(
  collection="cureolex:sess:<id>",
  doc_id="cureolex:sess:<id>:mevzuat:1219/1",
  text=<tam kanun metni>,
  metadata={"tur":"kanun","rg":"1219","as_of":"2026-07-05"}
)
# 2) Çok-sorgulu, sınırlı, provenance-damgalı getirim (ana pencereye YALNIZ bunlar):
anamnesis.hybrid_query(
  collection="cureolex:sess:<id>",
  doc_ids=["cureolex:sess:<id>:mevzuat:1219/1"],
  queries=["tabiplik yetkisi tanım", "diploma tescil", "yaptırım", "yürürlük hükmü"]
)
# 3) İlişki grafiği — aynı collection (kapsamsız graph_* DENY):
anamnesis.graph_neighbors(
  collection="cureolex:sess:<id>",
  node="cureolex:sess:<id>:mevzuat:1219/1:madde:8",
  rel="degisiklik"
)
anamnesis.subgraph(collection="cureolex:sess:<id>", seed="cureolex:sess:<id>:mevzuat:1219/1", depth=1)
```

Getirim hep `{doc_id, idx, madde/sayfa, snippet}` döner → atıf `doc_id::idx` → `evidence_ledger` `E###`. RG OCR aynı disipline tabi: `rg_ocr_result` > eşik → ingest. `corpus_stats` çalışma seti değildir. `lib` kullanma.

## E. Yabancı hukuk büyük-metin (karşılaştırmalı)

- **Kimlik-öncelikli:** CELEX (`32007R1394`), ECLI, ELI, Akoma Ntoso section id ile **bölüm-düzeyi** fetch; tam konsolide statute'u ana pencereye çekme.
- **Tam-metin karşılaştırma** gerekiyorsa → anamnesis'e ingest (`doc_id=cureolex:sess:<id>:celex:32007R1394`) → sadece karşılaştırılan maddeleri query et.
- `comparative-law-researcher` bu işi kendi penceresinde yapar; ana pencereye yalnız mukayese matrisi (hücre başına identifier) döner.

## F. Bütçe izleme ve evict

- Her mod fazı sonunda: ara getirimleri `evidence_ledger` kayıtlarına çök (extract), ham izleri **evict** et. Sonraki faz yalnız ledger + kanonik cache'i görür.
- Ana pencere damıtılmış getirimi ~25-30K karakteri aşarsa: en eski ham/uzun izleri at, distillate'leri daha da sıkıştır.
- Devre-kesici: PostToolUse `retrieve_dont_dump` hook'u 6KB üstü hukuk-metni çıktısında ingest/distiller yönlendirmesi enjekte eder — bu uyarıyı **uygula**, ham işleme geçme.

## G. Kapsam manifestosunda büyük-veri satırı

anamnesis kullanıldığında G0 manifestosuna ekle:
```
Substrat
  anamnesis            → collection=cureolex:sess:<id> · ingest 3 belge (mevzuat:1219/1, celex:32007R1394, rg:33686) · 11 bounded query
```
Kullanılmadıysa (küçük getirim) veya anahtar yoksa:
```
  anamnesis            → skipped: gerekmedi (küçük getirim)   |   skipped: anahtar yok (bounded-chunk fallback)
```

Bu protokol, "tüm araçlar her sorguda çalışsın" talebini **bağlam-güvenli** kılar: hepsi ateşlenir, ham veri Tier 1/Tier 2'de tüketilir, ana pencere yalnız damıtılmış kanıt + kapsam kanıtı taşır.
