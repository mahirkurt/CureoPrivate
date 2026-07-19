# Changelog — Vekayinüvis Plugin

Bu plugin [Semantic Versioning](https://semver.org/lang/tr/) kullanır.
Flagship skill kendi sürüm geçmişini `skills/vekayinuvis/SKILL.md` frontmatter
`changelog` alanında tutar.

## [3.2.0] — 2026-07-19

### Eklendi

- **Devlet Arşivleri kapsamlı süpürme + yerel store entegrasyonu (22→27 araç, 7. grup "süpürme").**
  Canlı MCP'nin dört yeni aracı plugin doktrinine wire edildi:
  - **`devarsiv_deep_search`** (`[_RW]`) — kapsamlı erişimin **birincil** yolu artık otomatik:
    konuyu arşiv×üst-fon×tarih kovalarına böler, `capped` her kovayı böler, yerel store'a yazar,
    `job_id` döner (idempotent; `arsiv` boş→dört arşiv birden; `ust_fon` `arsiv` gerektirir; store
    yoksa `store_required`). Manuel `list_fon_categories`+`detailed_search` enumerasyonu artık
    yalnız store kapalıyken/dar hedefte yedek yol.
  - **`devarsiv_deep_result`** (`[_RO]`) — süpürmenin **kapsam manifestosu** (`coverage.archives[]`
    arşiv-başına status); `complete=true` yalnız 6 koşul + tüm arşiv `completed`; **`complete=false`
    → boş sonuç "yok" DEĞİL**; tamlık yalnız süpürülen `year_bounds`/`fon_bounds` içinde. Async
    sözleşme OCR K4 ile aynı (deep_search→deep_result poll).
  - **`devarsiv_coverage`** (`[_RO]`) — **STORE-FIRST epistemolojisi**: boş sonuçtan "arşivde yok"
    sonucuna varmadan önce hasat defterine bak — kova defterde yoksa cevap "bilmiyoruz/hasat
    edilmedi", "yok" değil (no-fabrication invaryantı). `capped:true` kova 1000 tavanına vurmuş.
  - **`devarsiv_rebuild_archive`** (`[_RW]`) — satın-alınanları yerel 300 DPI PDF arşivine
    kurar/günceller (eSatış ZIP→kayıpsız PDF); viewer temsilî-tek-sayfa sınırını aşan **tek**
    tam-belge yolu; `session_required` korumalı, ödeme YAPMAZ. arsiv-oku/toplu-okuma önkoşulu.
- **`devarsiv_ocr_image`** CONNECTORS.md'ye eklendi (OCR entegrasyonunda atlanmıştı) — Belge grubu 3→4.

### Değiştirildi

- **Kapsamlı-erişim doktrini deep_search-birincil'e yükseltildi** — flagship §3.1.b tool tablosu
  (+4 satır, Süpürme grubu), araç-seçim rehberi, katalog referansı §2/§2b (§2b.1 async + §2b.2
  manuel yedek), §3 no-fabrication (store-first), kaynak-avi/arsiv-dalis/olay/boa-katalog skill'leri,
  arsiv-tarama-distilleri ajanı, session_start CONVENTIONS (1a), context-economy S1 shard,
  CONNECTORS.md (yetenek katmanı + SOURCE_HUNT/ARCHIVE_DEEP_DIVE/EVENT_RECONSTRUCTION mod setleri).
- **Envanter kontrolü 6→7 araç grubu** (süpürme grubu eklendi) — `vekayinuvis_doctor.py` + start/durum.
  Grup-kapsamı yaklaşımı korundu (magic-number yok); deep_search grubunun tümüyle yokluğu drift sinyali.
- **Araç sayısı sabitleri 22→27** güncellendi (plugin.json ×2 description/longDescription/_role,
  flagship + katalog + CONNECTORS başlıkları) — "kesin sayı deploy'a göre değişir" notuyla.

### Not

- HP-tarafı altyapı (serverInfo rename "Devlet Arşivleri", systemd sertleştirme, oturum alarmı,
  store yedekliliği) plugin değişikliği gerektirmez — server ID `devlet-arsivleri` + tool namespace
  değişmedi. Store dayanıklılığı (mcp-backup + off-site + wal_checkpoint) store-first doktrinini doğrular.

## [3.1.0] — 2026-07-19

### Eklendi

- **`/vekayinuvis:olay` komutu (EVENT_RECONSTRUCTION).** 9 moddan biri olan olay-kurgulaması
  artık kendi komut girişine sahip (önceden yalnız flagship auto-mode ile erişilebiliyordu):
  gün-gün birincil-kaynak kronolojisi + olay örgüsü, çift-tarih + fon/kutu/gömlek künyeli.

### Değiştirildi

- **`devlet-arsivleri` envanter kontrolü magic-number'dan grup-kapsamına geçti.** `start`
  preflight'ı ve `vekayinuvis_doctor.py` artık sabit "22 araç" beklemiyor — 6 araç grubunun
  (arama/belge/sepet/arşiv/OCR/durum) her birinden en az bir araç arar. OCR sisteminin
  `devarsiv_ocr_image`'ı gibi eklemeler artık yanlış-DRIFT üretmez; yalnız bir grubun tümüyle
  yokluğu cache/drift sinyalidir.
- **`start` karşılaması v3.0 filoyu yansıtacak biçimde tazelendi** (v1.2.0→v3.1.0): yasama/
  mevzuat katmanı (Resmî Gazete/mevzuat/TBMM/DETSİS), tam-metin şelalesi (OpenAthens/Anna's),
  anamnesis substratı ve Transleyt iki-okuyucu OCR doktrini karşılama metnine eklendi.
- **Web katmanı host-bağımlı olarak yeniden çerçevelendi.** `web_search`/`web_fetch` artık
  "her zaman mevcut" değil; bundled `exa`/`tavily` birincil web yüzeyi olarak öne çıkarıldı
  (claude.ai custom connector'da host web araçları bulunmayabilir).

### Düzeltildi

- **Var olmayan `carbon-pptx` skill atıfları temizlendi** (4 dosya) → gerçek `carbon-html-report`
  (A4 baskı/sunum-hazır) + `carbon-quarto-scientific` (bilimsel format).
- **No-op `context: fork` frontmatter alanı 3 skill'den kaldırıldı** (kaynak-avi/arsiv-dalis/
  rapor); bağlam ekonomisi artık açık `arsiv-tarama-distilleri` delegasyonuyla (Claude Code) veya
  claude.ai'de doğrudan Tier-2 anamnesis degrade'iyle belgelendi.
- **`stop_coverage` metin-yedeği meta-tur baskılayıcısı (F9).** Transkript-yok yolunda filo/mod
  adlarını ANAN ama araç ÇAĞIRMAYAN turlar (mimari inceleme, dokümantasyon, hook'un kendi kodu)
  yanlış G0-manifesto uyarısı üretiyordu; artık plugin-iç öz-referans veya ≥3-mod-künyesiz
  imzası susturuluyor (transkript-var yolu değişmedi — orada araç-çağrısı kesinliği geçerli).
- **`citation_discipline` kasıtlı arşiv-kapsamı belgelendi.** Yasama (mevzuat/tbmm/resmigazete)
  ve saf-akademik atıflar bilerek dışarıda — arşiv çift-tarih/BOA-künye disiplini Cumhuriyet
  mevzuatına dayatılmaz; yasama-atıf disiplini (kanun no + madde + RG) KANUN_GEREKÇESİ modunun
  prose sorumluluğu. G0 kapsam tarafı `FLEET_DATA_TOOL` ile tüm filoyu zaten kapsıyor.

## [3.0.1] — 2026-07-14

### Düzeltildi

- **Stop hook kapısı isim-geçişinden kayıt-yerine daraltıldı.** `citation_discipline` +
  `stop_coverage` artık yalnız somut bir kayıt yeri (fon/kutu/gömlek örüntüsü, katalog URL'i,
  gerçek `devarsiv_*` araç izi) varsa ateşlenir — MCP'nin kendi kodu üzerinde çalışmak (araç
  adları, şema tartışması) artık yanlış-pozitif üretmez. Bkz. `hooks/scripts/_signals.py`
  `has_record_locator`.
- **Bu sürüm bump'ı daha önce yalnız `.claude-plugin/plugin.json`'a işlenmişti**; codex
  manifesti, flagship skill frontmatter'ı ve README ile bu changelog girdisine geriye dönük
  yayıldı (sürüm ıraksaması onarımı).

## [3.0.0] — 2026-07-12

### BREAKING — commands→skills göçü

Slash komutları artık önek almadan doğrudan skill adıyla çağrılır:
`commands/` dizini kaldırıldı, 10 komut `skills/<ad>/SKILL.md`'e taşındı.

| Eski | Yeni |
|---|---|
| `/vekayinuvis:vekayinuvis-durum` | `/vekayinuvis:durum` |
| `/vekayinuvis:vekayinuvis-arsiv-dalis` | `/vekayinuvis:arsiv-dalis` |
| `/vekayinuvis:vekayinuvis-boa-katalog` | `/vekayinuvis:boa-katalog` |
| `/vekayinuvis:vekayinuvis-kanun-gerekce` | `/vekayinuvis:kanun-gerekce` |
| `/vekayinuvis:vekayinuvis-kaynak-avi` | `/vekayinuvis:kaynak-avi` |
| `/vekayinuvis:vekayinuvis-kronoloji` | `/vekayinuvis:kronoloji` |
| `/vekayinuvis:vekayinuvis-literatur` | `/vekayinuvis:literatur` |
| `/vekayinuvis:vekayinuvis-prosopografi` | `/vekayinuvis:prosopografi` |
| `/vekayinuvis:vekayinuvis-rapor` | `/vekayinuvis:rapor` |
| `/vekayinuvis:vekayinuvis-transkripsiyon` | `/vekayinuvis:transkripsiyon` |

`transkripsiyon` skill'i ayrıca üç-sütun HTR protokolüne kavuştu (Sütun 1
Görü — birincil, çelişkide kazanır — | Sütun 2 Transkribus | Sütun 3
eScriptorium; gürültülü sütun "kullanılmadı (gürültülü)" olarak işaretlenir,
boş bırakılmaz) ve K3 Transkribus model seçim tablosuna (aşağıda).

### Eklendi — devlet-arsivleri 10→22 araç (sepet→noVNC→arşiv→çift-motor OCR→async)

- **eSatış sepeti 4'lüsü** `[_RW/_RO/_DESTRUCTIVE]`: `devarsiv_add_to_cart`
  (1-tabanlı sayfa seçimi, örn. "1,3-5"; boş=tümü), `devarsiv_list_cart`
  (kalemler + **bağlayıcı Tutar**), `devarsiv_remove_from_cart` (satır
  sil/boşalt), `devarsiv_checkout_cart` (ödeme **YAPMAZ** — yalnız noVNC
  URL + sepet döner; ödeme **DAİMA insan/noVNC**, asla otonom).
- **Satın-alınmış/yerel-arşiv 6'lısı**: `devarsiv_list_purchased`
  (SatinAldiklarim t/hash listesi), `devarsiv_ocr_belge_pages` (viewer
  temsilî-sayfa sınırlı), `devarsiv_list_archive` (BOA-kodlu yerel PDF
  arşivi — code/yer/tarih/özet/sayfa), **`devarsiv_get_archive_page`**
  (**300 DPI ImageContent — arşiv-öncelikli okuma**), `devarsiv_ocr_archive_pages`
  (sync OCR, ≤5 sayfa), `devarsiv_get_archive_pdf` (künye + sınırlı base64
  PDF).
- **Async OCR 2'lisi** `[_RW/_RO]`: `devarsiv_ocr_submit` (idempotent,
  job_id döner) + `devarsiv_ocr_result` (queued/running/done/error/**stale**).
- **`engine` parametresi** tüm OCR araçlarında: `auto|both|transkribus|
  escriptorium|tesseract`. Osmanlı varsayılanı `both` — Transkribus PyLaia
  (el yazması) + eScriptorium Kraken (basılı) PARALEL, iki transkripsiyon
  `transcriptions` altında yan yana + tesseract damga katmanı; düşen motor
  dürüst `unavailable` nedeni taşır. Latin arşivler daima `tesseract`. Görü
  birincil, HTR yardımcı — Transkribus taşra-kâtibi ellerinde gürültülü
  olabilir (2026-07-09 canlı gözlem).
- **Yeni okuma-önceliği kuralı**: satın-alınmış belgede okuma DAİMA yerel
  arşivden başlar; katalog önizlemesi yalnız satın-alınmamış belgeler
  içindir.
- **Sync/async karar kuralı (K4)**: ≤5 sayfa VE tek motor → sync
  `devarsiv_ocr_archive_pages`; >5 sayfa VEYA `both` tam belge → async
  `devarsiv_ocr_submit` → `devarsiv_ocr_result(include_text=false)` poll →
  `done`'da tek-sefer `include_text=true` → anamnesis `ingest_document` →
  sonraki sorgular `hybrid_query`. `stale` → aynı parametrelerle resubmit.
- **§6.5 "Kanıt Disiplini (Murzi Kalıpları)"** — altı-maddelik prosopografik/
  toponimik kanıt disiplini: iki-seviye kanıt (toponim eşleşmesi ≠ kişi
  belgesi), katalog-token ≠ doğrulanmış içerik, çift-tarih yeniden-teyit
  (`ottoman_convert_date`), tarihsiz kayıt kronolojik kanıt değildir, ham
  HTR alıntılanmaz (görüyle doğrulanmış okuma alıntılanır), katalog imlâsı
  ile toponimik/tarihsel yorum ayrı sütunlarda.
- **Transkribus model seçim tablosu (K3)**: **56496** OttomanTurkish_generic
  (el yazması genel divani/rika, CER ~%12, üretim varsayılanı) ·
  **169801** Ottoman Fatwa Manuscript (fetva/ilmiye el yazması, %5.94) ·
  **52502** OttomanTurkish_Print_1 (matbu salname/gazete/nizamname, %7.2).

### Eklendi — üç yeni akış-skill'i

- **`/vekayinuvis:satinalma`** — eSatış sepet + noVNC satın-alma: karar
  matrisi → sepet → metin-onay kapısı → noVNC (`https://devarsiv-vnc.
  cureonics.com/vnc.html`; tek-cihaz uyarısı: "Kendi cihazınızdan kataloğa
  GİRMEYİN — tek-cihaz kilidi HP oturumunu düşürür."). Ödeme **DAİMA
  insan**; fiyat dili "~0,50 TL/sayfa TAHMİNDİR; bağlayıcı tutar
  `devarsiv_list_cart` çıktısındaki Tutar sütunudur."
- **`/vekayinuvis:arsiv-oku`** — satın-alınmış belgeyi yerel BOA-kodlu
  arşivden 300 DPI görüyle, sayfa-sayfa okuma (arşiv-öncelikli).
- **`/vekayinuvis:toplu-okuma`** — çok-sayfalı satın-alınmış belgede async
  çift-motor OCR + anamnesis ingest (K4 kararına göre).

### Eklendi — filo genişlemesi 13→17 server (yasama/mevzuat + destekleyici)

| Server | Rol |
|---|---|
| `resmigazete` | Erken-Cumhuriyet Resmî Gazete arşivi (`/eskiler/` 1920+) — tarih-bazlı ilan/kanun kaydı + `rg_search`/`rg_list_recent`; taranmış sayfa rg-ocr çift-motor async kuyruk. KANUN_GEREKÇESİ L4/L5, EVENT_RECONSTRUCTION |
| `mevzuat` | mevzuat.gov.tr — `search_mulga_mevzuat` (mülga kanun/KHK/CBK) + `get_mevzuat_gerekce` (madde gerekçesi) + `resolve_resmi_gazete` (RG çapraz-referans). KANUN_GEREKÇESİ antecedant-mevzuat zinciri |
| `tbmm` | TBMM yasama tarihçesi — kanun teklifi→komisyon raporu→kabul edilmiş kanun soyağacı + Açık Erişim DSpace (geç-Osmanlı/erken-Cumhuriyet zabıt). KANUN_GEREKÇESİ L3/L4, SOURCE_HUNT |
| `detsis` | DETSİS kurumsal prosopografi (`detsis_resolve_birim`→`detsis_get_gecmis_birim`→`detsis_list_milestones`→`detsis_get_mevzuatlar`). PROSOPOGRAPHY — **Cumhuriyet-sınırlı: Osmanlı teşkilatına inmez** |

**Dürüst not: `marmara-mcp` v3.1'e ERTELENDİ.** Turcademy/hukuk tam-metin
Tier-3b companion olarak tasarlanmıştı (spec §4.4); 2026-07-12 canlı-probede
`marmara.cureonics.com` üç bağımsız çözümleyiciyle **NXDOMAIN** doğrulandı
(DNS kaydı henüz yayınlanmamış) → bu turda wire edilmedi. HISTORIOGRAPHY
tam-metin şelalesi şimdilik `openathens→annas-reader` (2 katman) olarak
kalır; DNS/tunnel yayınlandığında `openathens→marmara→annas-reader`'a
genişletilecek.

### Değiştirildi — hook katmanı

- **SessionStart 'clear' BUG düzeltildi**: matcher `"startup|resume|compact"`
  → `"startup|resume|clear|compact"` (oturum `/clear` ile başlatıldığında
  connector preflight hiç çalışmıyordu).
- **`devarsiv_degrade` hook'u (yeni)**: `PostToolUse` + `PostToolUseFailure`
  üzerinde `devarsiv_*` araç yanıtında `session_required`/
  `viewer_runtime_error` görürse K5 re-login runbook'unun kompakt 6-satırlık
  hâlini `additionalContext` olarak enjekte eder.
- **`retrieve_dont_dump`**: `BIG_OUTPUT_TOOLS`'a `devarsiv_ocr_belge_pages`,
  `devarsiv_ocr_archive_pages`, `devarsiv_get_archive_pdf`,
  `devarsiv_ocr_result` eklendi; `devarsiv_get_archive_page` bilinçli
  istisna (görüntü ana pencerede görüyle okunur, dump edilmez).
- **`citation_discipline`**: provenance regex'i async/arşiv araçlarını da
  tanır (`ocr_archive_pages|ocr_submit|ocr_result|job_id|get_archive_page|
  get_archive_pdf`); çift-motor kullanıldıysa iki motorun çıktısının **ayrı
  raporlanması** zorunlu (tek birleşik metin yasak).
- Kök `plugins/vekayinuvis/hooks.json` inert kopyası silindi — tek doğruluk
  kaynağı artık `hooks/hooks.json`.

### Değiştirildi — doctor v3

- `scripts/vekayinuvis_doctor.py`: filo listesi 17 server'a genişledi,
  `clientInfo` sürümü `3.0.0`'a güncellendi.
- `--live` modu üç yeni bölüm kazandı: `[envanter]` (`devarsiv_server_info`
  tool-count'un 22'ye göre drift kontrolü — eksikse claude.ai connector'ını
  yeniden bağlama uyarısı), `[engines]` (Transkribus/eScriptorium motor
  durumu), `[vnc]` (noVNC Access-gate HEAD probu — 302=OK).
- Manifest çıktı ev dizini artık `CLAUDE_PLUGIN_DATA` env var'ını onurlandırır
  (yoksa geriye-uyumlu `cwd()` davranışı korunur).

### Değiştirildi — userConfig + hijyen

- **`userConfig`'e 6 yeni alan**: `devarsiv_api_key`, `ottoman_api_key`,
  `yok_akademik_api_key`, `openathens_api_key`, `annas_api_key`,
  `anamnesis_api_key` (hepsi `sensitive:true`, `required:false`). **Önemli
  sınır**: host'ta `userConfig`→`.mcp.json` header enjeksiyon fallback
  sözdizimi (`${user_config.field:-${ENV}}` gibi) belgelenmemiş olduğu
  doğrulandı (code.claude.com/docs) → bu alanlar `.mcp.json` header'larını
  OTOMATİK beslemez; buraya değer girilirse AYNI ZAMANDA ilgili ortam
  değişkeni de (Doppler/secrets.env) dışa aktarılmalıdır — description'lar
  bu şartı açıkça belirtir. Keychain bütçesi ölçüldü: 6 anahtarın toplamı
  374 bayt (≪1800 bayt eşiği) — kesinti gerekmedi, 6 alanın tamamı kaldı.
- **Hijyen**: `plugin.json`'dan default'u tekrarlayan `"agents": "./agents"`
  ve `"skills": "./skills"` alanları silindi (auto-discovery zaten aynı
  yolu tarar); `agents/openai.yaml` → `.codex-plugin/openai.yaml` taşındı;
  hook/script `.py` dosyaları `755`'e normalize edildi; `marketplace.json`
  vekayinuvis girdisindeki `"strict": false` kaldırıldı.
- **`arsiv-tarama-distilleri` alt-ajanı**: `disallowedTools`'a sepet-mutasyon
  araçları eklendi (`devarsiv_add_to_cart`/`devarsiv_remove_from_cart`/
  `devarsiv_checkout_cart`) + açık invariant: "Bu alt-ajan SEPETE DOKUNMAZ —
  add_to_cart/remove_from_cart/checkout_cart çağırmaz; satın-alma kararı ve
  mutasyonu ana asistanda, kullanıcı onayıyla." Zarf çıktısına `access`
  zenginleştirmesi eklendi ("purchased→`/vekayinuvis:arsiv-oku` ile okunur"
  / "purchasable: N sayfa ≈ X TL sepet adayı").

### Değiştirildi — SKILL çekirdeği

- Flagship `vekayinuvis` SKILL.md **v2.5.0 → v3.0.0**: §3.1.b devarsiv araç
  tablosu 10→22 araca genişledi (6 grup: Arama/Belge/Sepet/Arşiv/Async/
  Durum); motor konvansiyonu (K2) ve sync/async karar kuralı (K4)
  belgelendi; EVENT_RECONSTRUCTION modu devarsiv (`semantic_search` +
  `detailed_search` tarih-aralığı) ile birincil katman olarak güçlendirildi.
  Mod sayısı (9) korundu.
- `references/devlet-arsivleri-katalog.md`: 22-araç envanteri + K5 re-login
  runbook + Transkribus model tablosu + çift-motor güvenilirlik şerhleri
  güncellendi.
- `plugin.json` (Claude + Codex) `version` → `3.0.0`, description v3
  içeriğiyle yeniden yazıldı, `keywords`'e 7 yeni terim eklendi
  (`esatis-sepet`, `novnc-satinalma`, `cift-motor-ocr`, `escriptorium-kraken`,
  `async-ocr`, `resmigazete`, `mulga-mevzuat`).

## [2.5.0] — 2026-07-09

### Eklendi
- **Marketplace-portable doctor:** `/vekayinuvis-durum` komutu ve
  `scripts/vekayinuvis_doctor.py`. Script `.mcp.json` tam-filo wiring'ini,
  env/userConfig/OAuth preflight durumunu ve 13 server satırlı G0 kapsam
  manifestosu iskeletini üretir; belge görüntüsü, OCR/HTR veya tam-metin çekmez.
- **Canlı `devlet-arsivleri` oturum probe'u:** doctor `--live` modunda streamable
  HTTP MCP initialize → initialized → `devarsiv_session_status` zincirini çalıştırır;
  `/vekayinuvis-durum` artık `session alive` ise satırı `hit 1`, oturum düşmüşse
  `degraded: session_required` olarak yazar.

### Değiştirildi
- **G0 hook sıkılaştırıldı:** `stop_coverage.py` artık yalnız çekirdek dört satırı
  değil, 13 server'ın tamamını `hit/empty/degraded/skipped` durum satırıyla arar.
- **Atıf hook'u güçlendirildi:** görüntü/OCR/HTR iddiası varsa gerçek araç adı
  (`devarsiv_get_belge_image`, `devarsiv_ocr_belge`, `devarsiv_ocr_belge_pages`)
  ve sayfa/model/engine/confidence provenance'ı ister.
- **No-fabrication metinleri hizalandı:** eski "belge görüntüsü üretilemez"
  ifadeleri, "yalnız gerçek araçla çekildiyse aktar; çekilmediyse katalog düzeyinde
  kal" disiplinine güncellendi.
- **Claude marketplace metadata:** `.claude-plugin/plugin.json` component path'leri
  (`commands`, `agents`, `skills`, `hooks`, `mcpServers`) açık yazıldı.

## [2.4.0] — 2026-07-08

### Eklendi (çok-sayfa erişim)
- **Derin sayfalara erişim** (satın-alınmış belgeler). devlet-arsivleri MCP 10→**12 araç**:
  `devarsiv_list_purchased` (SatinAldiklarim → {t,hash,ozet,sayfa}) + `devarsiv_ocr_belge_pages`
  (t,hash,arsiv,pages? → eSatış doküman-viewer'dan tam PDF → pdftoppm → her sayfa arşive-duyarlı
  OCR/HTR: Osmanlı→Transkribus PyLaia, Latin→tesseract). 49-görüntülük dosyada eşleşme sayfasına
  ulaşmanın yolu. `references/devlet-arsivleri-katalog.md` §8. MCP CureoHub `e78a8c1e`.
- **Dürüst sınır:** çok-sayfa TAM erişim **yalnız satın-alınmış** belgelerde. Satın-alınmamışta
  katalog yalnız 1 önizleme (sample_picture) sunar; 2..N sayfa satın-alma kapısında (5 açıdan
  doğrulandı: Mi paginate etmez, per-page handler yok, seçim modalı yalnız checkbox) → **uydurulmaz**.

## [2.3.0] — 2026-07-08

### Eklendi (Transkribus Osmanlıca HTR CANLI)
- **El yazması Osmanlıca artık deterministik olarak çeviriyazılıyor.** `devarsiv_ocr_belge` arsiv=2'de
  **Transkribus PyLaia + model 56496 (`OttomanTurkish_generic`)** ile HTR yapıyor (legacy TrpServer
  REST akışı; upload→HTR→export; ~50s, ~1 kredi/sayfa; IJMES-diakritikli transliterasyon). Uçtan uca
  canlı doğrulandı (CureoHub `445db4ab`). ⇒ el yazması için **birincil deterministik yol
  `devarsiv_ocr_belge`**; `devarsiv_get_belge_image` + asistan görüsü tamamlayıcı (düşük-kalite/
  çapraz-doğrulama). Çıktı insan doğrulamasına tabidir (CER ~%12).
- **Teşhis düzeltmesi:** önceki "kredi-kapılı (401)" tanısı yanlıştı — sorun kredi değil YANLIŞ API'ydi
  (hesabın token audience'ı `TrpServer` → Metagrapho processing/v1→401 yerine legacy TrpServer REST).
  §7 tablosu + notu güncellendi.

## [2.2.3] — 2026-07-08

### Düzeltildi
- **"Runtime Error" ayrımı düzeltildi** (§3): katalog kimlik-korumalı sayfalarda 'Runtime Error'
  (500) = büyük olasılıkla **oturum süresi doldu → re-login** (önceki 2.2.2'deki "upstream, re-login
  çözmez" yanlıştı). 2026-07-08 ampirik: başka hesap çalışırken bizim expired oturum bu 500'ü aldı,
  noVNC re-login çözdü. MCP tarafı `status: session_required` + `reason: runtime_error` döner
  (CureoHub `d2b30dcf`).

## [2.2.2] — 2026-07-08

### Değiştirildi
- **`upstream_error` ≠ `session_required` ayrımı** (references §3): katalog backend'i sunucu-tarafı
  "Runtime Error" (Server Error in '/' Application) verirse `upstream_error` döner — oturum değil,
  upstream kesinti; **noVNC re-login çözmez**, bir süre sonra tekrar denenir. (MCP-tarafı tespit
  CureoHub `a8f80a8c`'de; önceden yanlışlıkla alive:true + boş/timeout dönüyordu.)

## [2.2.1] — 2026-07-08

### Değiştirildi (OCR sonrası ince ayar)
- **retrieve-don't-dump hook** artık `devarsiv_ocr_belge`'yi de tanıyor (büyük OCR/HTR metni →
  Tier-1 distiller / Tier-2 anamnesis'e yönlendirilir). `devarsiv_get_belge_image` **kasıtlı
  olarak hariç** — o bir görüntüdür, asistan görüsüyle okunur, dump edilmez.
- **Transkribus HTR durumu netleştirildi** (`devlet-arsivleri-katalog.md` §7): model
  `OttomanTurkish_generic` sunucuda yapılandırıldı ama **kredi-kapılı** (READ Coop kredisi
  gerekir); kredisizken el yazması Osmanlıca için **birincil yol `devarsiv_get_belge_image` +
  asistan görüsü**; kredi eklendiğinde `ocr_belge` gerçek HTR döner.

## [2.2.0] — 2026-07-08

### Eklendi (belge okuma — OCR/HTR + görsel)
- **devlet-arsivleri MCP artık belge sayfa taramasını okuyor** (5→8→**10 araç**). BelgeGoster
  full-res sayfa taramasını `<img id="sample_picture">`'da sunar — **satın-alma durumundan
  BAĞIMSIZ** (satın alınmamış önizlemeler de okunur; ampirik doğrulandı 2026-07-08).
  - **`devarsiv_get_belge_image`** — sayfa taraması ImageContent olarak → asistan **el yazması
    Osmanlıca'yı doğrudan görüsüyle okur** (BOA el yazması için pratikteki en iyi tam-okuma).
  - **`devarsiv_ocr_belge`** — deterministik OCR/HTR: Latin/Cumhuriyet tam-metin · Osmanlı basılı
    damga+arşiv referans kodu (tesseract `tur+eng+ara`) · el yazması Arap-harfli gövde → Transkribus
    HTR (creds-gated, SOTA) veya görsel-okuma. `mean_confidence`+`note`; no-fabrication.

### Değiştirildi
- **No-fabrication güncellendi:** belge görüntüsü artık **çekilir (gerçek tarama, uydurulmaz)** ve
  OCR/görü ile okunur; OCR düşük-güvende dürüstçe raporlanır; el yazması transkripsiyon insan
  doğrulamasına tabi; yalnız çok-sayfalı tam satın-alma seti (eSatış *SatinAldiklarim*) + diğer
  kısıtlı arşivler erişim-kapısında kalır. SKILL §3.1.b (10 araç) + §1.2, ARCHIVE_DEEP_DIVE /
  MANUSCRIPT_TRANSCRIBE / PROSOPOGRAPHY belge-okuma adımı, references/devlet-arsivleri-katalog.md §7
  (motor tablosu + kanonik akış), CONNECTORS §2, boa-katalog + transkripsiyon komutları,
  session_start hook konvansiyonu güncellendi.
- Osmanlıca en iyi okuma iki yol: **asistan görüsü** (self-contained, hesap gerektirmez) +
  **Transkribus HTR** (READ Coop hesabıyla deterministik SOTA); tesseract el yazmasını okumaz
  (basılı+Latin okur) — bu sınır dürüstçe belgelenir.
- Flagship skill **v2.1.0 → v2.2.0**. Davranış/mod sayısı (9) korundu.

## [2.1.0] — 2026-07-08

### Eklendi (devlet-arsivleri derin araç wire)
- **`devarsiv_semantic_search`** — diakronik/semantik katalog araması wire edildi: modern
  sorguyu Osmanlıca eşdeğerlerine genişletir (karantina→tahaffuzhane/sıhhiye/kordon;
  göçmen→muhacir/mülteci) + Workers AI **bge-m3** rerank; `matched_variants` şeffaflığı.
  SOURCE_HUNT/ARCHIVE_DEEP_DIVE modlarında modern-terim **birincil** arama aracı.
- **`devarsiv_detailed_search`** + **`devarsiv_list_fon_categories`** — **1000-tavan aşan
  kapsamlı erişim**: `list_fon_categories` (üst-fon ekseni) → her fon için `detailed_search`
  (arşiv × üst-fon × tarih-penceresi × özet) → `item_id` union. Katalog sayfalama-yok 1000
  satır render ettiği için `capped:true` = *daha fazlası var*; bu enumerasyon her belgeye
  ulaşmanın tek yolu. Ağır fan-out `arsiv-tarama-distilleri` ajanına delege edilir.

### Değiştirildi
- Bu 3 araç şuralara işlendi: SKILL §3.1.b tablosu (5→8 araç) + §5.1/§5.2 mod akışları +
  araç-seçim rehberi; `references/devlet-arsivleri-katalog.md` §2 (8 araç) + yeni §2b (kapsamlı
  erişim enumerasyonu) + §2c (semantik/diakronik); `agents/arsiv-tarama-distilleri.md` (araç
  seçimi + enumerasyon + `kapsam` çıktı alanı); `CONNECTORS.md` §2 + §7; `commands/vekayinuvis-
  boa-katalog.md` + `vekayinuvis-arsiv-dalis.md`; `hooks/scripts/retrieve_dont_dump.py`
  (semantic/detailed büyük-çıktı yönlendirmesi).
- **11→13 server sayım kayması düzeltildi**: `openathens`+`annas-reader` v2.0.0'da eklendiği hâlde
  bazı sayaçlar 11'de kalmıştı → SKILL §3.5/§10, `skills/start`, `session_start.py`,
  `stop_coverage.py` (gerekçe listesine iki tam-metin server'ı eklendi), `hooks.json`, `CONNECTORS.md`
  hepsi 13'e hizalandı; `context-economy-contract.md` sharding tablosuna **fulltext katmanı** (S3) eklendi.
- Flagship skill **v2.0.0 → v2.1.0**. Davranış/mod sayısı (9) korundu.

## [2.0.0] — 2026-07-07

### Eklendi
- **`devlet-arsivleri` çekirdek connector** (`https://devarsiv.cureonics.com/mcp`):
  resmî Devlet Arşivleri kataloğunda (Osmanlı/BOA · Cumhuriyet/BCA · Diplomatik ·
  Askeri) doğrudan **fon/kutu/gömlek araması** + belge künyesi. `archive-landscape.md`
  §1.1/§8.1/§8.4'teki "BETSİS sorgu önerisi / BCA için kayıt yok" boşluğunu kapatır.
  Yeni referans: `references/devlet-arsivleri-katalog.md`.
- **`literatur` (DergiPark) companion**: tam-metin (PDF→HTML) makale + referans;
  ottoman `search_dergipark`'ı tamamlar. Hazır remote (`literatur-mcp.surucu.dev`, authless).
- **`yok-akademik` destekleyici companion**: YÖK Akademik profilleri (modern prosopografi + ekol haritası).
- **Kitap+makale tam-metin şelalesi**: `openathens` (Tier 3 lisanslı — Millet Kütüphanesi /
  OpenAthens SAML, 309 DB; paywall'lı monograf/makale) → `annas-reader` (Tier 4 son-çare —
  Anna's Archive efemer-RAG; out-of-print Osmanlı çalışmaları; yalnız analiz). Getirilen tam-metin
  → anamnesis'e ingest. Böylece kitap ve makaleye tam-metin erişim tamamlandı.
- **`anamnesis` substrat**: büyük-veri RAG/GraphRAG bağlam-ekonomisi altyapısı
  (ingest→bounded query; kişi↔görev↔belge / olay↔tarih↔kaynak grafiği).
- **`arsiv-tarama-distilleri` alt-ajanı** (`agents/`): ağır çok-connector arşiv
  taramasını izole eder → tek `arsiv_distillate` zarfı (retrieve-don't-dump).
- **4 hook** (`hooks/hooks.json` + `hooks/scripts/`): SessionStart connector-preflight
  + tam-filo/bağlam-ekonomisi konvansiyonları; PostToolUse retrieve-don't-dump
  (büyük gövde → Tier-1 distiller / Tier-2 anamnesis); Stop stop_coverage (G0 kapsam
  manifestosu) + Stop citation_discipline (fon/kutu/gömlek + Hicrî/Miladî çift-tarih + katalog URL).
- **Bağlam ekonomisi + tam-filo sözleşmeleri** (`shared/`): `context-economy-contract.md`
  (Tier 0/1/2, sharding, kanonik cache, kör-getirme-yok chunking, devre-kesici) +
  `coverage-manifest.md` (G0 manifesto biçimi + örnek).
- **2 yeni komut**: `vekayinuvis-boa-katalog` (resmî katalog araması+künye) +
  `vekayinuvis-literatur` (DergiPark tam-metin derin literatür).
- **`userConfig`** (`plugin.json`): paper-search Smithery key'i enable-time'da (opsiyonel; girilmezse degrade).

### Değiştirildi
- **TAM-FİLO**: `.mcp.json` artık **11 server** bundle eder (çekirdek + akademik companion +
  yok-akademik + anamnesis, `_tier`/`_role` annotasyonlu) — bağlama uygun her araç her koşumda
  çalışır; iki-katmanlı "companion bundle edilmez" tasarımı full-fleet'e terfi etti.
- Flagship skill **v1.3.0 → v2.0.0**: §1.2 restricted-kaynak notu (katalog araması artık doğrudan;
  belge görüntüleri o sürümde kısıtlıydı; güncel davranış için 2.5.0 no-fabrication notuna bakın),
  §3.1.b F. Resmî Katalog katmanı, §3.2 literatur+yok-akademik,
  §3.5 Tam-Filo ve Bağlam Ekonomisi, §5 mod güncellemeleri (SOURCE_HUNT/ARCHIVE_DEEP_DIVE/
  PROSOPOGRAPHY/HISTORIOGRAPHY/KANUN_GEREKÇESİ), §6.3 katalog URL atfı, §8 G0 kapsam manifestosu,
  §10 shared referanslar.
- CONNECTORS.md: §1 full-fleet, §2 devlet-arsivleri çekirdek + F. Resmî Katalog, §3 literatur/
  yok-akademik/anamnesis + tam-filo notu, §6 auth, §7 mod-map, §8 preflight + güncellenmiş
  restricted-kaynak kuralı. start/SKILL.md: connector kadrosu + tam-filo + anamnesis + degrade notları.

### Not
- **No-fabrication korunur**: resmî katalog kaydı (fon/kutu/gömlek + künye) doğrudan; belge
  **görüntüleri/tam-metni** hâlâ eSatış/on-site/transkripsiyon-tezi kapısında — asla uydurma.
  `devlet-arsivleri` **tek-cihaz oturum kilitli** (HP kalıcı authenticated tarayıcı); oturum düşükse
  `session_required` → re-login yol haritası + degrade.

## [1.0.0] — 2026-06-17

### Eklendi
- **Plugin paketlemesi**: standalone `vekayinuvis` user-skill'i, Claude Code
  plugin formatına (`.claude-plugin/plugin.json`) dönüştürüldü.
- **Çekirdek MCP transport** (`.mcp.json`): `ottoman-archives` (Cloud Run) +
  `yoktez` (FastMCP) uzak HTTP sunucuları bundle edildi.
- **Oryantasyon skill'i** (`skills/start/SKILL.md`): connector preflight +
  9-mod yönlendirme + scope guard.
- **7 slash komutu** (`commands/`): kaynak-avi, arsiv-dalis, transkripsiyon,
  prosopografi, kronoloji, rapor, kanun-gerekce.
- **CONNECTORS.md**: connector envanteri için tek doğruluk kaynağı — çekirdek
  vs. tamamlayıcı katman ayrımı, kimlik doğrulama modeli (OAuth vs. userConfig),
  mod → connector eşlemesi, fallback zincirleri, restricted-kaynak disiplini.
- **Tam orkestrasyon `.mcp.json` snippet'i + `userConfig` bloğu**: tamamlayıcı
  akademik katmanı (paper-search/consensus/scholar-gateway/exa/tavily) bundle
  etmek isteyenler için CONNECTORS.md § 4–5'te dokümante edildi.

### Değiştirildi
- Flagship skill **v1.2 → v1.3.0**: connector envanteri ve transport için
  plugin-düzeyi `../../CONNECTORS.md` + `../../.mcp.json` normatif kaynak olarak
  işaretlendi; § 3 connector tabloları pedagojik referans olarak korundu (skill
  standalone da çalışır). **Davranış / mod sayıları / kalite kapıları
  DEĞİŞMEDİ.**

### Korundu (v1.2 davranışı)
- 9 çalışma modu, G0–G6 kalite kapıları, IJMES/TDV İA çeviriyazı disiplini,
  çift/üçlü tarih notasyonu, restricted-kaynak içerik-üretmeme kuralı, 8
  referans dosyası (archive-landscape, source-typology, citation-and-
  transliteration, chronology, htr-workflow, kanun-gerekcesi-workflow,
  medical-history, report-template).
