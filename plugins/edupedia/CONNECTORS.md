# edupedia — Paylaşılan Connector Sözleşmesi (CONNECTORS.md)

**Belge sınıfı:** Normatif connector envanteri — plugin-düzeyi tek doğruluk kaynağı
**Sürüm:** 1.2.0
**Kapsam:** `edupedia` plugin'inin paketlediği ÜÇ MCP connector'ı:
1. **Maarif Modeli MCP** (`maarif-mufredat`) — flagship `carbon-edupedia` skill'inin (ve
   ileride `carbon-html-report` / `carbon-pptx` sibling skill'lerinin) tükettiği kazanım/
   müfredat kaynağı (§0-§6 aşağıda, değişmedi).
2. **Eğitim Kaynak RAG MCP** (`egitim-kaynak`) — açık eğitsel kaynak (OER) getirme katmanı;
   modül üretirken **konu içeriği, açıklayıcı materyal ve (Faz 2'den) kazanıma-hizalı pasaj**
   çeker. Kazanımı `maarif-mufredat` verir, İÇERİĞİ `egitim-kaynak` zenginleştirir (§9 aşağıda, yeni).
3. **Modül Yayın MCP** (`modul-yayin`) — `/edupedia:yayinla` komutunun ve claude.ai üretim
   akışının tercih ettiği yayın connector'ı (§8 aşağıda). **Not:** eski adı `edupedia` idi;
   MCP connector'ı plugin adıyla çakışmasın diye `modul-yayin`'e alındı — endpoint/token aynı.

**Birlikte normatif:** `./shared/canonical-cache-contract.md` (tek-sefer disiplini +
`get_figure` yetenek-probu) · `./shared/run-manifest-schema.json` (çift-sorgu denetim kanıtı)

> **Neden bu dosya var.** Standalone `carbon-edupedia` skill'inde connector envanteri +
> kimlik/PDF uyarıları + provenans standardı `references/curriculum-integration.md §2`
> içinde tanımlıydı. Plugin sarmalayıcısı bu *tanımı* tek noktaya çeker; skill artık buraya
> **referans verir** (`../../CONNECTORS.md`), kendi içinde yeniden tanımlamaz. Connector adı /
> parametre / envanter değişikliği yalnızca burada güncellenir. Bu, kullanıcının `rxpraxis`
> 1.7.0 dönüşümündeki felsefeyle aynıdır: *davranış ve kalite kapıları değişmez — yalnız
> sözleşmeler tek noktaya çekilir.*

---

## 0. Connector Kimliği

| Alan | Değer |
|---|---|
| **Connector adı** | `maarif-mufredat` (`.mcp.json`'da bildirilir) |
| **Endpoint** | `https://mufredat.cureonics.com/mcp` |
| **Transport** | `http` (streamable-HTTP MCP) |
| **Auth** | Yok — public read-only (plugin `.mcp.json`'ı header taşımaz) |
| **Kapsam (hard)** | **YALNIZ Türkiye MEB / Türkiye Yüzyılı Maarif Modeli (2024).** Yabancı müfredat (IB, Cambridge), üniversite içeriği veya genel konu anlatımı **kapsam dışı** — bunlar için connector çağrılmaz, kullanıcı kaynağı / yerleşik bilgi kullanılır (skill `SKILL.md §7`). |
| **Korpus (introspeksiyon 2026-07-06)** | `tymm.meb.gov.tr` · corpus_version **1.4** · build 2026-06-14 · 60 ders · 10.855 kazanım (4.069 kanonik) · 13 çerçeve (266 madde) · 105 ders kitabı · 22.414 figür · 157 video |

> Ham introspeksiyon çıktısı: `./docs/mcp-introspection-2026-07-06.json` (denetlenebilirlik).

---

## 1. Araç Envanteri — dört işlevsel küme (canlı doğrulanmış)

Aşağıdaki tablo **canlı `tools/list` introspeksiyonundan** (2026-07-06) türetilmiştir.
Otoritatif araç sayısı **21**'dir (skill v2.7.0 dokümante tabanı "19" der ve `get_figure`'ı
envanterde saymaz; **canlı sunucu `get_figure`'ı DA bildirir** → Tier-2 mevcuttur, §3).

### A · Keşif / navigasyon (hangi ders, hangi sınıf, ne var?)
| Araç | Ne döner | Rol |
|---|---|---|
| `server_info` | Korpus sürümü, build tarihi, sayımlar | **Provenans damgası** için sürüm öğrenme; pre-flight canlılık |
| `list_education_levels` | İki seviye (`temel-egitim`, `ortaogretim`) + ders sayısı | En üst seviye keşif |
| `list_subjects` | 60 ders (slug + ad + seviye + sınıf sayısı); `q` ile isim filtresi | **Ders slug'ını bulma** (kritik ilk adım) |
| `get_subject` | Bir dersin programları, sınıfları, ders kitapları, `outcome_count` | Ders profilini doğrulama |
| `list_curriculum_programs` | Program belgeleri (subject/grade filtreli) | Program belge id'sini bulma |
| `get_curriculum_program` | Program belgesi + hafif sayfa-başlığı içindekiler | Ünite/bölüm yapısını görme |

### B · Kazanım (öğrenme çıktısı) erişimi — **modülün çekirdek kaynağı**
| Araç | Ne döner | Rol |
|---|---|---|
| `list_learning_outcomes` | Bir dersin kazanımları (kod, metin, sınıf, sayfa). `distinct_codes:true` ile kod başına tek kanonik satır | **Birincil çekme** — konu/ünite kazanımları |
| `search_learning_outcomes` | Tam-metin kazanım araması (`q`); ders/sınıf/seviye filtresi. `distinct_codes:true` desteklenir | Konu adından kazanım bulma ("hücre", "kesir") |
| `search` | Birleşik FTS: program sayfaları + çerçeveler + kazanımlar (`kind` filtresi) | Geniş keşif; konunun program metnindeki yeri |

### C · Beceri çerçevesi — **pedagojik haritalama kaynağı**
| Araç | Ne döner | Rol |
|---|---|---|
| `list_frameworks` | 13 çerçeve + madde sayısı (Kavramsal Beceriler, SDÖB, Erdem-Değer, Okuryazarlık...) | Hangi çerçeveler var |
| `get_framework` | Çerçevenin tüm maddeleri (kod, başlık, açıklama). En önemlisi `beceriler/kavramsal-beceriler` (38 madde) | **Beceri kodu (KB2.x) → etkileşim deseni** eşlemesi (skill §4) |

### D · Belge + medya (opsiyonel zenginleştirme)
| Araç | Ne döner | Rol |
|---|---|---|
| `list_document_kinds` | Belge türleri + sayıları | `list_documents` öncesi tür keşfi |
| `list_documents` | Her tür belge (program/textbook/guide/material/differentiation/remedial/report/common) | İlgili materyal bulma |
| `get_document_text` | Belge sayfa metni (`page` / `page_range`, maks 25 sayfa). Endekssiz belge (`page_count=0`) → `pdf_url` notu | Program/kılavuz metnini kaynak olarak çekme |
| `list_textbooks` | Ders kitabı kataloğu (`pdf_url`) | Kaynak ders kitabını **referanslama** (gömülmez) |
| `list_guides` / `list_reports` | Kılavuz / TYMM rapor belgeleri | Pedagojik kılavuz desteği |
| `list_videos` / `get_video` | Eğitim/tanıtım videoları (kategori filtreli; `youtube_url` + açıklama) | Opsiyonel görsel kaynak **atfı** (modüle gömülmez) |

### (Görsel yolu — Tier-2 dayanağı)
| Araç | Ne döner | Rol |
|---|---|---|
| `search_figures` | Ders kitabı görsellerinde semantik arama (VLM caption + etiket + figür-altı FTS; Türkçe diakritik duyarsız). **Görselin kendisini döndürmez** → `figure_id` listesi | Tier-1 zenginleştirme + Tier-2 aday-figür keşfi |
| `get_figure` | Tek figür: `include_image=false` → zengin **metadata** (title, page_no, caption, nearby_text, `pdf_url`, mime, boyut); `include_image=true` → satır-içi görsel (ImageContent, ≤110KB PNG/JPEG) | **Tier-2** görsel yolu — yalnız yetenek-probuyla (§3) |

> **Not (kimlik doğrulama):** `search_figures` `grade` parametresi **sayısal** biçim bekler
> (`'5'`, `'6'`); ancak canlı testte `grade='5'` bazı sorgular için 0 döndü, subject-scoped
> sorgu 3 isabet verdi (5.Sınıf + 6.Sınıf karışık). **Öneri:** figür aramayı ders-scoped yap,
> `grade_or_grades` alanına göre istemci-tarafı filtrele. Kazanım araçlarındaki sınıf etiketi
> ise `5.Sınıf` biçimindedir (bkz. §2).

---

## 2. Kimlik / PDF uyarıları (korunur — boş sonuç tuzakları)

Bu uyarılar `carbon-edupedia/references/curriculum-integration.md §2`'den taşınmıştır ve
**normatiftir**:

- **Ders slug'ını ASLA isimden uydurma.** "Matematik" ortaokulda `ortaokul-matematik-dersi`,
  ilkokulda `ilkokul-matematik-dersi`; "Fen" → `fen-bilimleri-dersi`. Her zaman önce
  `list_subjects(q="…")` ile doğru slug'ı al. *(Canlı doğrulama: `list_subjects(q="fen")` →
  `fen-bilimleri-dersi`.)*
- **Sınıf etiketi `5.Sınıf` biçimindedir** (nokta sonrası boşluk yok, büyük S). `5. Sınıf` /
  `5.sinif` boş sonuç döndürebilir. `get_subject.grades` geçerli etiketleri verir.
  *(`search_figures` için sınıf ayrıdır — bkz. §1 notu.)*
- **Çerçeve slug'ı yol-biçimlidir:** `beceriler/kavramsal-beceriler` (eğik çizgili).
- **`document_id` tamsayıdır**, slug değil (`get_subject`/arama döndürür). *(Canlı doğrulama:
  FB.5.3.1.1 → `document_id: 7`.)*
- **`get_figure.figure_id` tamsayıdır**, `search_figures` döndürür.
- **PDF-türevi kazanım metni temizliği (zorunlu):** kazanım `text` alanları program PDF'inden
  çıkarıldığı için artefakt taşır: tireli satır kırpması ("rasyo- nel" → "rasyonel"), kesik son
  cümle, gömülü "İÇERİK ÇERÇEVESİ / Anahtar Kavramlar / ÖĞRENME KANITLARI" başlıkları. Modüle
  koymadan önce: (1) tireli bölünmeleri birleştir, (2) içerik-çerçevesi kuyruğunu ayrıştır ve
  ilgili teach segmentine kaynak yerleştir, (3) yarım cümleyi **tamamlama** — eksikse atla.

---

## 3. Görüntü-Dayanak Politikası (Tier-1 / Tier-2) — plugin-düzeyi normatif

Bu politika `carbon-edupedia`'nın görsel üretim yolunu plugin düzeyinde sabitler. Skill'in
görsel arketipleri (`svgFigure`, `labeledFigure`, `vizTable`, `numberLine`, `fractionBar`,
`relationFlow`) **değişmez**; bu bölüm yalnız Müfredat MCP kaynaklı görsel dayanağın iki
katmanını netleştirir (skill `references/svg-authoring.md` ile tutarlı).

| Katman | Tanım | Durum | Davranış |
|---|---|---|---|
| **Tier-1** | Kazanım koduna / program metnine izlenebilir olgular + **yazar-üretimli tema-duyarlı SVG** (token-renkli, WCAG 2.1 AA, `role="img"` + başlık/etiket) | **Garanti** | Varsayılan ve zorunlu yol. `validate_module.py` **G-CURRICULUM** + **G-SVG** kapılarıyla denetlenir. MCP'nin görsel çekememesi skill sözleşmesinde **başarısızlık değildir** — Tier-1 tek başına tam işlevseldir. |
| **Tier-2** | `get_figure(..., include_image=true)` → resmî ders-kitabı görselinin **base64 gömülmesi** | **Best-effort, opsiyonel** | Yalnız yetenek-probu geçerse denenir; **herhangi bir hata / `413` / timeout / boş dönüşte sessizce Tier-1'e düşülür**; modül üretimi **asla bloke olmaz**. |

### 3.1 Yetenek-probu (capability probe) — kanonik akış

Introspeksiyon (2026-07-06) `get_figure`'ın **mevcut** olduğunu doğruladı; yine de her koşuda
runtime probu uygulanır (connector kaldırılabilir / kısıtlanabilir):

1. **Araç var mı?** Bağlı araç listesinde `get_figure` yoksa → Tier-2 devre dışı,
   `tier2_status: unavailable`, log: `tier2_unavailable: tool_absent`.
2. **Metadata-first (`include_image=false`):** Hedef figür(ler) için önce
   `search_figures(query, subject)` → aday `figure_id` → `get_figure(figure_id, include_image=false)`.
   Bu **Tier-1 zenginleştirmesidir**: başlık, sayfa, `caption`, `pdf_url`, kazanım-bağı buradan
   gelir (görsel gömülmez, atıf/dayanak güçlenir).
3. **Fırsatçı `include_image=true`:** YALNIZ *fırsatçı* olarak base64'ü çekmeyi dene; başarılıysa
   göm (`tier2_status: embedded`), değilse sessizce Tier-1'de kal ve `tier2_status: degraded`
   + `tier2_degraded: <hata-sınıfı>` logla. `n_bytes` ≤110KB sınırı tool tarafında zorlanır;
   büyük figür → degrade.

`tier2_status ∈ {unavailable, degraded, embedded}` her koşu için `run_manifest`'e yazılır
(bkz. `shared/run-manifest-schema.json`).

---

## 4. Provenans Standardı (G-CURRICULUM)

- Modüldeki **her olgusal iddia** bir kazanım koduna veya çekilen program / ders-kitabı metnine
  **izlenebilir** olmalı. Eksik olgu **uydurulmaz**; yerleşik müfredat bilgisi kullanılıyorsa
  açıkça etiketlenir ve doğrulama istenir (`SKILL.md §7`).
- `meta.sourceCitation` = çekilen kazanım kodları + korpus sürümü (`server_info.corpus_version`
  + `build_date`). Örn: *"MEB Türkiye Yüzyılı Maarif Modeli — Fen Bilimleri (2024), 5. Sınıf,
  3. Ünite. Kazanımlar: FB.5.3.1.1, FB.5.3.1.2. Kaynak: tymm.meb.gov.tr / Maarif MCP
  (corpus v1.4, build 2026-06-14)."*
- `curriculum` bloğu (`MODULE_DATA` uzantısı) her kazanım için `code` + `text` + `skill` (KB2.x)
  + `mappedTo` (segment id'leri) taşır; `validate_module.py` G-CURRICULUM kapısı
  kazanım→segment izlenebilirliğini denetler. Şema:
  `carbon-edupedia/references/curriculum-integration.md §5`.
- Görsel için: Tier-2 gömülürse `meta.sourceCitation`'a figür `pdf_url` + `page_no` eklenir;
  Tier-1'de kalınırsa yazar-üretimli SVG olduğu belirtilir.

---

## 5. Fallback / Graceful Degradation

Müfredat MCP bir **zenginleştirme ve doğrulama katmanıdır**, tek-nokta bağımlılık değildir:

- **MCP erişilemez / araç hata:** Modül üretimi **durmaz**. Kullanıcıya kısaca bildir
  ("Müfredat verisine ulaşılamadı; verdiğiniz içerikle / yerleşik bilgiyle devam ediyorum") →
  **offline** yola dön (kullanıcı kaynağı veya etiketli yerleşik bilgi). `curriculum` bloğu
  kısmi doldurulabilir veya atlanır; mod CURRICULUM yerine MODULE'a düşebilir.
- **Kazanım bulunamadı** (`search_learning_outcomes` boş): sorguyu genişlet (eş anlamlı, kısa
  terim) → gerekirse `list_learning_outcomes(distinct_codes=true)` ile üniteyi tara → hâlâ yoksa
  doğru ders/sınıf/konu sor.
- **Yanlış slug:** `list_subjects` çıktısındaki slug'ı **birebir** kullan; ezberden yazma.
- **Ders kitabı metni boş:** beklenen davranış (`get_document_text` ders kitaplarında `pdf_url`
  döner); program belgesini veya kullanıcı kaynağını kullan.
- **Tier-2 başarısız:** §3.1 → sessizce Tier-1; hard-fail yok.

---

## 6. Pre-flight (ilk çağrıdan önce)

İlk connector kullanımından önce `server_info` (veya `list_subjects`) ile canlılığı doğrula.
Bu, korpus sürümünü de verir (provenans damgası). `/edupedia:durum` komutu bu pre-flight'ı
kullanıcı-yüzeyli çalıştırır (canlılık + araç kümesi + `get_figure` mevcudiyeti + önbellek durumu).

---

## 7. Genişleme Notu (composability kancası)

Bu connector sözleşmesi ileride `edupedia` plugin'ine eklenecek **sibling skill'ler** tarafından
paylaşılabilir:

- `carbon-html-report` — aynı kazanım kaynağından baskıya-hazır **statik** çalışma kâğıdı.
- `carbon-pptx` — aynı kazanım kaynağından **slayt** dizisi.

Bu skill'ler eklendiğinde `maarif-mufredat` envanterini, kimlik/PDF uyarılarını ve provenans
standardını **buradan** tüketir — kendi içlerinde yeniden tanımlamazlar. Bu brief'te **yalnız**
`carbon-edupedia` + `start` paketlenmiştir.

---

## 8. `modul-yayin` connector'ı — yayın (yayın connector'ı, plugin 0.5.0)

> **Yeniden adlandırma (plugin 0.5.0):** bu connector'ın adı `edupedia` → `modul-yayin`
> oldu (MCP connector'ı `edupedia` plugin adıyla çakışmasın diye). **Endpoint, token, araçlar
> ve davranış birebir aynı** — yalnız `.mcp.json` anahtarı ve connector kimliği değişti.
> Araç adları (`edupedia_publish` vb.) sunucu tarafı olduğundan DEĞİŞMEDİ.

| Alan | Değer |
|---|---|
| **Connector adı** | `modul-yayin` (`.mcp.json`'da bildirilir; eski ad `edupedia`) |
| **Endpoint** | `https://edupedia.cureonics.com/mcp` |
| **Transport** | `http` (streamable-HTTP MCP, stateless) |
| **Auth** | Tek-kiracılı OAuth 2.1 (RFC 8414/7591/9728) — sunucunun tek sırrı
  `EDUPEDIA_PUBLISH_TOKEN` hem `/mcp` bearer kapısını hem `/api/publish` REST kapısını
  korur (ayrı bir `AUTH_HMAC_SECRET` YOK — bu servis Python-filo'nun "access_token = master
  key" desenini izler, `mcp-servers/` altındaki Cloud-Run-lineage servislerin çoğuyla aynı).
  Claude Code'da `.mcp.json`'daki `Authorization: Bearer ${EDUPEDIA_PUBLISH_TOKEN}` başlığı
  ortam değişkeninden okunur; claude.ai'de kullanıcı connector ayarlarında OAuth ile bağlanır
  ve token sohbete hiç girmez. |
| **Kapsam** | Yalnız `edupedia.cureonics.com`'da modül yayınlama/listeleme/kaldırma —
  Maarif MCP'nin kazanım/müfredat kapsamıyla ilgisizdir. |
| **Public okuma yolları** | `/`, `/m/<slug>`, `/api/index.json`, `/health` token'sız açık
  (bearer yalnız `/mcp` ve mutasyon REST uçlarına uygulanır). |

### 8.1 Araç Envanteri (4 araç)

| Araç | İmza | Rol |
|---|---|---|
| `edupedia_publish` | `(html, run_id, subject_slug, grade, topic, mode, outcome_codes, subject?, slug?, title?, force?) → JSON` | Modülü yayınla. **Manifest istemci tarafında kurulmaz** — sunucu `run_id`/`requested_scope`'u bu düz alanlardan kendisi kurar. Kalite kapılarını **sunucu** ölçer (istemci beyanı yok sayılır). Başarıda `{slug, version, url, forced, gates}`; kapı FAIL'de (ve `force` yoksa) `{"error": ..., "status_code": 422}` — asla `url` uydurmaz. |
| `edupedia_list` | `(subject?, grade?, mode?, query?) → JSON` | Yayınlanmış modülleri filtreli listele (`/edupedia:durum` ve keşif için). |
| `edupedia_unpublish` | `(slug) → JSON` | Modülü katalogdan gizle (dosyalar diskte kalır — geri döndürülebilir işlem değildir ama veri kaybı da değildir). |
| `edupedia_server_info` | `() → JSON` | `gate_count`, `max_upload_bytes`, `base_url`, `gates_measured_by:"server"` — canlılık + kapasite pre-flight'ı. |

**Araç şeması kısıtı:** grok.com uyumluluğu için `minLength`/`maxLength`/`pattern`/`allOf`
JSON-schema anahtarları KULLANILMAZ (fleet-genel kural, bkz. CureoHub `reference_grok_mcp.md`);
doğrulama yalnız sunucu tarafında (`app/gates.py`, `app/publish.py`) yapılır.

### 8.2 `/edupedia:yayinla` ve claude.ai için tercih sırası

`edupedia_publish` bağlı araç listesinde görünüyorsa **her zaman tercih edilir** —
`../commands/yayinla.md` Yol A. Görünmüyorsa (connector eklenmemiş, tipik Claude Code
oturumu) `../commands/yayinla.md` Yol B'deki REST akışına (`POST /api/publish` +
`EDUPEDIA_PUBLISH_TOKEN`) düşülür. claude.ai'de dosya sistemi yoktur — model HTML'i
`edupedia_publish`'in `html` argümanına doğrudan üretir (`../commands/modul.md` /
`../commands/mufredat.md` "Yayın teklifi" bölümü); bu sürüm hiçbir zaman diske yazılmaz,
kullanıcı modülü yayınlandıktan sonra siteden indirir.

### 8.3 Fallback / Graceful Degradation

- **`edupedia_publish` yok / connector kopuk:** `/edupedia:yayinla` sessizce Yol B'ye düşer;
  hard-fail yok, kullanıcı token'ı zaten Doppler'dan sağlıyorsa akış aynı sonuca ulaşır.
- **Kapı FAIL (422):** her iki yolda da aynı anlam — sunucu ölçtü, düşen kapı adları
  yanıtta gelir, kullanıcı onayı olmadan `force` denenmez.
- **Sunucuya ulaşılamıyor:** yerel HTML dosyasına (varsa) dokunulmaz; kullanıcıya durum
  bildirilir, sonra tekrar denenir.

---

## 9. `egitim-kaynak` connector'ı — açık eğitsel kaynak RAG (içerik zenginleştirme, plugin 0.5.0)

**Rol:** kazanımı `maarif-mufredat` verir; modülün İÇERİĞİNİ (konu anlatımı, açıklayıcı
materyal, pedagojik örnek, ileride etkileşim deseni) `egitim-kaynak` **kaynaklandırılmış,
lisans-etiketli pasajlarla** zenginleştirir. MEB öğretim programının KENDİSİ burada DEĞİL
(o `maarif-mufredat`) — bu connector onu tamamlar, kopyalamaz.

| Alan | Değer |
|---|---|
| **Connector adı** | `egitim-kaynak` (`.mcp.json`'da bildirilir) |
| **Endpoint** | `https://egitim-kaynak.cureonics.com/mcp` |
| **Transport** | `http` (streamable-HTTP MCP, stateless) |
| **Auth** | **YOK — kasıtlı olarak anahtarsız** (2026-07-17). Ne `.mcp.json` başlığı, ne OAuth, ne kullanıcı secret'ı: connector kutudan çıkar çıkmaz çalışır. Gerekçesi `titck-cache-mcp` emsaliyle aynı: altı aracın tamamı salt-okunur ve korpusun tamamı zaten kamuya açık, açık lisanslı içerik (PhET CC BY-NC 4.0 + Vikipedi-TR CC BY-SA 4.0) — yetkilendirilecek bir şey yok. Sunucu tarafında `MCP_API_KEY` yok + `MCP_ALLOW_NO_AUTH=1`; **ikisi birden** şart, çünkü anahtarın yalnızca eksik olması yanlış yapılandırmadır (500) — anahtarı unutmak sunucuyu kazara açmaz. Bu modda server-card dürüstçe `authentication.required=false` der ve OAuth uçları 404 döner (aksi hâlde istemci, imzası tanımsız bir OAuth dansına girerdi). Kıyas: yazma yapan `modul-yayin` anahtarlı KALIR. |
| **Node** | Pi :8312 (systemd `egitim-kaynak-mcp`); CureoHub `mcp-servers/egitim-kaynak-mcp/`. |
| **Faz** | **Faz 0 (canlı 2026-07-16):** yalnız BM25/FTS5 + Vikipedi-TR. Embedding/vektör (Faz 1) ve kazanım hizalaması (Faz 2) YOK. |

### 9.1 Araç Envanteri (6 salt-okunur araç)

| Araç | Rol |
|---|---|
| `kb_search` | Eğitsel korpusta arama → **belge başına EN İYİ pasaj** (`top_k` BELGE sayar). Her sonuç `license` + `quote_allowed` + `match_kind` (`text`/`title_only`) taşır. Sıralama metin-kanıtı önce; `score` ham BM25, listede monoton azalmaz → **yeniden sıralanmaz**. |
| `kb_for_outcome` | Bir MEB kazanım koduna hizalanmış pasajlar. Faz 0'da dürüstçe `degraded/alignment_not_built` (Faz 2'de gerçek pasaj) — asla sahte hizalama. |
| `kb_get` | Bir belgenin tam/kısmi metni (bağlam genişletme; `kb_search` bir pasaj döner, gerisini bununla aç). Bilinmeyen `doc_id` → `not_found`. |
| `kb_patterns` | Etkileşim/oyunlaştırma desen kartları (Faz 4; şimdilik boş + caveat). |
| `kb_sources` | Kaynak envanteri: lisans, `quote_allowed`, belge/chunk sayısı. |
| `kb_server_info` | Sürüm, faz, getirme yöntemi, hizalama durumu, korpus sayımları. |

### 9.2 Kullanım akışı (flagship skill için)

Kazanım al (`maarif-mufredat` `list_learning_outcomes`) → **içerik zenginleştir**
(`egitim-kaynak` `kb_for_outcome(kod)` hazırsa, aksi halde `kb_search(konu)`) → modülü yaz.
Her çıktı `mcp_verified:false` + `caveat` taşır. **Lisans disiplini:** `quote_allowed:false`
bir kaynaktan birebir uzun alıntı yapılmaz (yalnız öğrenilir); yayın kapısı (Faz 4) bunu uygular.

### 9.3 Fallback / Graceful Degradation

- **Connector kopuk / anahtar yok:** kb_* araçları görünmez → skill yerleşik bilgiyle devam eder,
  kaynak zenginleştirme atlanır (hard-fail yok, asla uydurma kaynak).
- **`kb_for_outcome` degraded (Faz 0/1):** `kb_search` ile serbest arama yapılır; hizalama iddia edilmez.
- **Boş sonuç:** dürüst boş — konunun korpusta yokluğu, konunun yokluğunun kanıtı değildir.
