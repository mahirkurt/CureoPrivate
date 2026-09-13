# edupedia — Paylaşılan Connector Sözleşmesi (CONNECTORS.md)

**Belge sınıfı:** Normatif connector envanteri — plugin-düzeyi tek doğruluk kaynağı
**Sürüm:** 1.3.0
**Kapsam:** `edupedia` plugin'inin paketlediği İKİ MCP connector'ı:
1. **Maarif Modeli MCP** (`maarif-mufredat`) — flagship `carbon-edupedia` skill'inin (ve
   ileride `carbon-html-report` / `carbon-pptx` sibling skill'lerinin) tükettiği kazanım/
   müfredat kaynağı (§0-§6 aşağıda).
2. **Eğitim Kaynak RAG MCP** (`egitim-kaynak`) — açık eğitsel kaynak (OER) getirme katmanı;
   modül üretirken **konu içeriği, açıklayıcı materyal ve (Faz 2'den) kazanıma-hizalı pasaj**
   çeker. Kazanımı `maarif-mufredat` verir, İÇERİĞİ `egitim-kaynak` zenginleştirir (§9 aşağıda).

Plugin **yayınlamaz.** Eski `modul-yayin` / `/edupedia:yayinla` yüzeyi plugin 0.8.0'da
kaldırıldı (§8). Teslim yerel tek-dosya HTML'dir.

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
| **Auth** | **Bearer** — `.mcp.json` `Authorization: Bearer ${MUFREDAT_MCP_API_KEY}` (Doppler `cureohub/dev_personal`). Anahtarsız çağrı 401. |
| **Kapsam (hard)** | **YALNIZ Türkiye MEB / Türkiye Yüzyılı Maarif Modeli (2024).** Yabancı müfredat (IB, Cambridge), üniversite içeriği veya genel konu anlatımı **kapsam dışı** — bunlar için connector çağrılmaz, kullanıcı kaynağı / yerleşik bilgi kullanılır (skill `SKILL.md §7`). |
| **Korpus (introspeksiyon 2026-07-06, BAYAT — güncel değer 2026-09-13 canlı ölçüm)** | `tymm.meb.gov.tr` · corpus_version **1.5** (eski: 1.4) · 60 ders · **4.286** kanonik kazanım (eski introspeksiyon 4.069'du; ham/dedup-öncesi satır sayısı farklı ve daha yüksektir — `search_learning_outcomes`'un `included_fragment_types` zarfıyla karıştırma) · 13 çerçeve (266 madde) · 105 ders kitabı · 157 video · sunucu **21 araç** (eski introspeksiyon dönemindeki sayıdan farklı olabilir). `server_info` ile her zaman doğrula — bu tablo bir anlık görüntüdür. |
| **`search` zarfı (R30, kırıcı değişiklik — mufredat 0.4.x)** | `search` artık düz dizi DEĞİL, `{results, included_outcome_fragment_types}` döner; `search_learning_outcomes` de `{results, included_fragment_types}` zarfına sarılıdır. Bu tablonun altındaki araç satırları bu zarfı varsayar — eski düz-dizi bekleyen bir ayrıştırıcı güncellenmeden kırılır. |

> Ham introspeksiyon çıktısı: `./docs/mcp-introspection-2026-07-06.json` (denetlenebilirlik; BAYAT — 2026-09-13 canlı sayımlarla değiştirilmedi, yeniden introspeksiyon önerilir).

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
- **`search_figures(grade=...)` de aynı `5.Sınıf` biçimini ister** — ama upstream şema
  açıklaması *"Sınıf filtresi, ör. '6'"* diyor ve o örnek **YANLIŞ**: `grade="6"` **0 sonuç**,
  `grade="6.Sınıf"` sonuç döndürür (ölçüldü 2026-07-31). Yanlış biçim hata değil **boş liste**
  verir — sessiz tuzak.
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
| **Tier-2a** (dayanak) | `get_figure(..., include_image=false)` → **metadata**: `caption`, `page_no`, `bbox`, `pdf_url`, kazanım-bağı | **Her zaman kullanılabilir** | Atıf/dayanak güçlendirmesi. Ayrıca `include_image=true` ile görseli **modelin GÖRMESİ** sağlanır; model o orijinale bakarak Tier-1 yazar-SVG'yi çok daha sadık çizer. |
| **Tier-2b** (gerçek gömme) | `pdf_url` + `page_no` + `bbox` → **PDF'ten yeniden çıkarma** → base64 JPEG | **Best-effort, yerel dosya sistemi + Python** | `scripts/fetch_figure.py` yapar (bkz. §3.2). Native yol Claude Code/Cursor'dadır; başka bir hostta ancak script açıkça yerelde çalıştırılabiliyorsa mümkündür. Model `figures` bloğu + `@@FIG:<key>@@` yer tutucusu yazar, script doldurur. Hata/erişilemezlikte yer tutucu **yerinde kalır** ve rapora düşer → Tier-1. claude.ai'de native dosya sistemi yolu olmadığı için **kullanılamaz** — orada Tier-2a + Tier-1 geçerlidir. |

### 3.1 Yetenek-probu (capability probe) — kanonik akış

Introspeksiyon (2026-07-06) `get_figure`'ın **mevcut** olduğunu doğruladı; yine de her koşuda
runtime probu uygulanır (connector kaldırılabilir / kısıtlanabilir):

1. **Araç var mı?** Bağlı araç listesinde `get_figure` yoksa → Tier-2 devre dışı,
   `tier2_status: unavailable`, log: `tier2_unavailable: tool_absent`.
2. **Metadata-first (`include_image=false`):** Hedef figür(ler) için önce
   `search_figures(query, subject)` → aday `figure_id` → `get_figure(figure_id, include_image=false)`.
   Bu **Tier-1 zenginleştirmesidir**: başlık, sayfa, `caption`, `pdf_url`, kazanım-bağı buradan
   gelir (görsel gömülmez, atıf/dayanak güçlenir).
3. **`include_image=true` — ne yapar, ne YAPMAZ (2026-07-31 ampirik):** görseli **MCP
   ImageContent** olarak döndürür. Model onu **GÖRÜR** (bu Tier-2a'nın değeridir: yazar-SVG
   orijinale bakılarak çizilir), ama **base64'ü metin olarak ALMAZ** — harness onu görüntüye
   çevirir ve JSON gövdesinde `data`/`base64` alanı **yoktur**. Binary veri token token yeniden
   üretilemeyeceği için **modelin gömmesi yapısal olarak imkânsızdır**.
   > Bu belge uzun süre "base64'ü çek ve göm" diyerek modelden imkânsız bir şey istedi. Vaat
   > 2026-07-31'de ölçülüp düzeltildi; gerçek gömme yolu §3.2'dir.
4. **Gerçek gömme (Tier-2b, yerel dosya sistemi + Python):** metadata'daki `pdf_url` + `page_no` + `bbox`
   figürü **birebir** yeniden çıkarmaya yeter (doğrulandı: MCP'nin gösterdiği görselin aynısı).
   `scripts/fetch_figure.py` bunu yapar (§3.2). Başarılıysa `tier2_status: embedded`, aksi
   halde `tier2_status: degraded` + Tier-1.

`tier2_status ∈ {unavailable, degraded, embedded}` her koşu için `run_manifest`'e yazılır
(bkz. `shared/run-manifest-schema.json`).

### 3.2 `scripts/fetch_figure.py` — Tier-2b yerel gömme aracı

Model `MODULE_DATA`'ya motorun **görmezden geldiği** bir `figures` bloğu yazar (`curriculum` /
`exam` bloklarıyla aynı desen) ve görselin geleceği yere `@@FIG:<key>@@` yer tutucusunu koyar:

```js
figures:{
  f1:{ figureId:6448, pdfUrl:"https://tymm.meb.gov.tr/upload/kitap/fen_bilimleri_6_1.pdf",
       page:80, bbox:[137.1,325.4,253.0,442.4],
       caption:"Bitki hücresi kesiti (Fen 6, s.80)",
       alt:"Hücre duvarı, çekirdek ve kloroplastları gösteren kesit çizimi" }
},
segments:[
  { type:"teach", id:"t1", visual:{ kind:"svg", ref:"@@FIG:f1@@" } }
]
```

Alanların tamamı `get_figure(figure_id, include_image=false)` çıktısından gelir — **uydurulmaz**.
Sonra:

```bash
python3 scripts/fetch_figure.py <modul.html> --in-place
```

Script PDF'i kitap başına **bir kez** indirir (`/tmp/edupedia-figure-cache`), `bbox`'ı kırpar,
JPEG q85'e sıkıştırır ve yer tutucuyu `role="img"` + `<title>` taşıyan bir
`<svg><image href="data:image/jpeg;base64,…"></svg>` ile değiştirir.

**Ölçüm (Fen 6 s.80, bitki hücresi):** PNG 3x = 171 KB base64 · **JPEG 2x q85 = 15 KB** →
JPEG varsayılan. Gömülü modül tüm kapılardan geçer (`G-SELFCONTAINED` `data:` URI'sine izinli,
`G-SVG` PASS).

**Motor DEĞİŞMEZ:** `visual.kind:"svg"` zaten keyfi SVG kabul eder (`svgFigure(ref)`).

**Degrade:** PDF inilemez / sayfa-bbox tutmaz / anahtar bilinmez → yer tutucu **yerinde kalır**
(sessizce silinmez), rapora düşer, çıkış kodu yine 0. Üretim asla bloke olmaz; o figür Tier-1
yazar-SVG ile doldurulur. PyMuPDF veya Pillow yoksa da aynı degrade.

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

## 8. Yayın yüzeyi — kaldırıldı (plugin 0.8.0)

`modul-yayin` connector'ı, `/edupedia:yayinla` komutu ve `edupedia_publish` /
`POST /api/publish` ajan yolları **plugin'den çıkarıldı.** Modül teslimi yerel
tek-dosya HTML'dir (Claude Code: çıktı dizinine yaz; claude.ai: sohbet artefaktı).
Kalite kapılarının otoritesi yerel `scripts/validate_module.py` (ve PostToolUse
hook'u)dır. Ajan siteye yayınlamaz ve `edupedia_site` deploy etmez.

---

## 9. `egitim-kaynak` connector'ı — açık eğitsel kaynak RAG (içerik zenginleştirme, plugin 0.5.0)

**Rol:** kazanımı `maarif-mufredat` verir; modülün İÇERİĞİNİ (konu anlatımı, açıklayıcı
materyal, pedagojik örnek, ileride etkileşim deseni) `egitim-kaynak` **kaynaklandırılmış,
lisans-etiketli pasajlarla** zenginleştirir. MEB öğretim programının KENDİSİ burada DEĞİL
(o `maarif-mufredat`) — bu connector onu tamamlar, kopyalamaz.

| Alan | Değer |
|---|---|
| **Connector adı** | `egitim-kaynak` (`.mcp.json` iç anahtarı; claude.ai/Gemini/ChatGPT'da görünen display adı **"Eğitim Kaynakları"** = `serverInfo.name`) |
| **Endpoint** | `https://egitim-kaynak.cureonics.com/mcp` |
| **Transport** | `http` (streamable-HTTP MCP, stateless) |
| **Auth** | **OAuth 2.1 + Bearer — keyed (2026-07-19).** Statik bağlantıda `.mcp.json`, `Authorization: Bearer ${EGITIM_KAYNAK_MCP_API_KEY}` kullanır (Doppler `cureohub/dev_personal`); anahtar çözülmezse connector 401 ve SessionStart preflight uyarır. OAuth connector akışında kullanıcı yetkilendirme formuna anahtarı girer; authorization code ve access token **opaque** değerlerdir, `MCP_API_KEY`/statik Bearer anahtarının kendisi değildir. Redirect/CORS/PRM desteği ilgili hostun OAuth connector akışına hizmet eder. Connector public-by-default değildir. |
| **Node** | Pi :8312 (systemd `egitim-kaynak-mcp`); CureoHub `mcp-servers/egitim-kaynak-mcp/`. |
| **Faz** | **Faz 1 (canlı 2026-07-17):** BM25/FTS5 (Türkçe İ/I, ı/i ve diakritik harf katlamalı arama) **+ vektör yedeği** (`@cf/baai/bge-m3`, Cloudflare Workers AI; korpus kapsaması 1.0). Kaynaklar: **124 doğrulanmış müfredat kategorisi** (tüm fen, matematik, sosyal/tarih, coğrafya, Türkçe/edebiyat, felsefe, astronomi, bilişim dalları) + **PhET** (175 Türkçe simülasyon, CC BY-NC 4.0). **Faz 2 (kazanım hizalaması) hâlâ KAPALI, ama Faz 1.5/EK-11 (ikinci dalga) `kb_for_outcome`'u `alignment_not_built`'TEN ÇIKARDI** — hizalama tablosu boşken artık ara mod kazanımın kök metnini `kb_search`'e sorgu verir ve `status:"ok"` (`alignment_kind:"query_time_bm25"`) YALNIZ tam AND ya da terimlerin ≥%40'ını tutan bir gevşetme basamağında döner, aksi hâlde `status:"degraded"`/`reason:"interim_low_relevance"` — saklı bir hizalama hâlâ iddia edilmez. Canlı sayımlar (2026-09-13, BAYAT eski `>6.380/>33.045` yerine): yaklaşık **28.551 belge / 106.107 chunk+vektör** (`kb_server_info`/`kb_sources` ile doğrula — bu tablo değil, sunucu otoritedir; gecelik koşumla değişir). |
| **Getirme** | **BM25 önce, vektör YEDEK — RRF füzyonu YOK** (2026-07-17'de kaldırıldı: ölçüm hibridi 3/8, saf BM25'i 6/8 verdi; RRF *uzlaşmayı* ödüllendirdiği için gürültülü vektör tarafı doğru cevabı boğuyordu). Vektör yalnız BM25 metin kanıtı bulamayınca konuşur. **`retrieval` adını iki AYRI alan taşır:** `kb_server_info`'daki *sunucu modudur* (`bm25+vector-fallback` / `fts5-bm25`); `kb_search` sonucundaki *o sorguda izlenen yoldur* (`fts5-bm25` / `vector-fallback`). Karıştırmayın. |

### 9.1 Araç Envanteri (6 salt-okunur araç)

| Araç | Rol |
|---|---|
| `kb_search` | Eğitsel korpusta arama → **belge başına EN İYİ pasaj** (`top_k` BELGE sayar). Her sonuç `license` + `quote_allowed` + `match_kind` taşır; `match_kind` **üç değerli**: `text` (sözlüksel kanıt) > `title_only` > `semantic` (**vektör tahmini** — gövde sorguyu hiç anmayabilir). Sıralama kademe-birincildir; `score` ikincil anahtar ve listede monoton azalmaz → **`score`'a göre yeniden sıralamayın**. `score_kind` (`bm25`/`cosine`) ile hangi ölçek olduğu bildirilir. |
| `kb_for_outcome` | Bir MEB kazanım koduna hizalanmış pasajlar. **Faz 2 (saklı hizalama) hâlâ kapalı, ama artık ham `alignment_not_built` DÖNMEZ** — ara mod (`alignment_kind:"query_time_bm25"` ya da vektör yedeğiyle `"query_time_vector_fallback"`) kazanımın kendi kök metnini sorgular; `status:"ok"` yalnız tam AND ya da ≥%40 terim-kapsamlı basamakta (`retrieval_tier`, `rung`, `coverage` alanlarıyla), aksi hâlde `status:"degraded"`/`reason:"interim_low_relevance"`. Bilinmeyen kod → `outcome_code_unknown`; kazanım JSONL'i hiç yoksa → `outcome_text_unavailable`. Asla sahte/saklı hizalama iddia edilmez. `degraded` dönerse **`kb_search`'e düşün** (kazanım metnindeki konuyu serbest sorgulayın). |
| `kb_get` | Bir belgenin tam/kısmi metni (bağlam genişletme; `kb_search` bir pasaj döner, gerisini bununla aç). Bilinmeyen `doc_id` → `not_found`. |
| `kb_patterns` | Etkileşim/oyunlaştırma desen kartları (Faz 4; şimdilik boş + caveat). |
| `kb_sources` | Kaynak envanteri: lisans, `quote_allowed`, belge/chunk sayısı. |
| `kb_server_info` | Sürüm, faz, getirme yöntemi, hizalama durumu, korpus sayımları. |

### 9.2 Kullanım akışı (flagship skill için)

Kazanım al (`maarif-mufredat` `list_learning_outcomes`) → **içerik zenginleştir**
(`egitim-kaynak` `kb_for_outcome(kod)` hazırsa, aksi halde `kb_search(konu)`) → modülü yaz.
Her çıktı `mcp_verified:false` + `caveat` taşır. **Lisans disiplini:** `quote_allowed:false`
bir kaynaktan birebir uzun alıntı yapılmaz (yalnız öğrenilir); G-VOICE / lisans
disiplini bunu yerel kapıda denetler.

### 9.3 Fallback / Graceful Degradation

- **Connector kopuk / anahtar yok:** kb_* araçları görünmez → skill yerleşik bilgiyle devam eder,
  kaynak zenginleştirme atlanır (hard-fail yok, asla uydurma kaynak).
- **`kb_for_outcome` degraded (ara mod `interim_low_relevance`/saklı hizalama hâlâ kapalı):** **`kb_search`'e düşün** — kazanım metnindeki konuyu serbest sorgulayın; hizalama iddia edilmez. Bu bir arıza DEĞİL — saklı (Faz 2) hizalama, korpus müfredat konularını kapsayana **ve** insan denetimi geçene kadar bilinçli kapalıdır (ölçüm: kazanım↔pasaj kosinüsleri konuyu değil "ikisi de uzun resmî Türkçe"yi ölçüyor → eşik ayarıyla açılamaz). Ara mod (EK-11, ikinci dalga) `ok` döndüğünde ise `alignment_kind:"query_time_bm25"` etiketiyle GERÇEK, kullanılabilir bir sinyaldir — yalnız saklı/embedding-vetted DEĞİLDİR.
- **Embedding ucu düşük / vektörsüz korpus:** her şey saf FTS5-BM25'e (Faz 0 davranışı) düşer; **arama asla embedding yüzünden başarısız olmaz**.
- **Boş sonuç:** dürüst boş — konunun korpusta yokluğu, konunun yokluğunun kanıtı değildir.
