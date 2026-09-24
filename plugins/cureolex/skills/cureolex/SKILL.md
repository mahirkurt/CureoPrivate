---
name: cureolex
description: >-
  Türkiye sağlık mevzuatı reform protokolü — kanun · CBK · yönetmelik · tebliğ · genelge düzeyinde yeni mevzuat
  üretmek, değiştirmek, yeniden yazmak için 12 mod (DRAFT · AMEND · ANALYZE · COMPLY · OPINE · RIA ·
  COMPARATIVE_LAW · TBMM_KANUN_TEKLIFI/PARLIAMENTARY_BILL · EX_POST_EVALUATION · REGULATORY_MATURITY ·
  TRANSPOSITION · RELIANCE_FRAMEWORK). 4.0: yargı bölgesinden bağımsız ÇEKİRDEK + takılabilir yargı
  bölgesi PAKETİ (jurisdictions/; TR aktif, GB/DE/CH taslak). 5210 Yönetmelik + AYM belirlilik içtihadı +
  OECD Better Regulation + Anayasa Md.17/56/90/5; G0-G11 kapı + no-fabrication (evidence_ledger). Kullan —
  "yönetmelik/tebliğ taslağı hazırla", "şu maddeyi değiştir", "TBMM kanun teklifi", "1219 SK reform", "TİTCK
  yönetmelik", "SUT reform", "ATMP/HTA düzenlemesi", "5210 uyum denetimi", "düzenleyici etki analizi/DEA",
  "karşılaştırmalı analiz / AB karşılığı", "ex post değerlendirme", "WHO GBT olgunluk açığı",
  "AB direktifi aktarım tablosu", "reliance çerçevesi". 21 wire'lı MCP + 3 companion (Yargı ·
  Open Law · Ansvar) tam-filonun zorunlu üyeleri; klinik kanıt → evidentia,
  atıf-adli + Türkçe hukuk dili → sci-audit (kuruluysa ZORUNLU). Şüphede Scope Guard önceliklidir;
  bireysel dava (SGK reddi, AYM başvuru), malpraktis ve promosyon denetimi KAPSAM DIŞIDIR.
version: 4.0.0
---

# Cureolex — Türkiye Sağlık Mevzuatı Reform Protokolü

**Yüzey:** Claude Code ve Cursor `.mcp.json` + Python hook ile çalışır (`doppler run`). claude.ai ve ChatGPT'de MCP **elle connector** eklenir, hook **koşmaz** — G0 kapsam manifestosunu model yazar. Ayrıntı: plugin kökü `CONNECTORS.md`.

Bu yetkinlik, **Türkiye'de sağlık mevzuatının her düzlemde reform, değişiklik ve yeniden yazımı** için tasarlanmış norm-üretim protokolüdür. En temel düzeyden (Anayasal sağlık hakkı) en operasyonel düzeye (tebliğ/genelge) kadar **yeni mevzuat üretir, mevcut mevzuatı değiştirir, gerektiğinde çerçeveyi tamamen yeniden yazar** — **5210 sayılı Yönetmelik** (RG 24/2/2022, 31760), **AYM belirlilik içtihadı**, **OECD Better Regulation**, **Anayasa Md.17/56 + Md.90/5 + ICESCR Md.12** ekseninde ve **savunulabilir, kanıt-temelli** biçimde.

## 0. Nasıl çalışılır (her modda)

1. **Scope Guard'ı önce uygula (§6).** Şüphede yönlendir, çıktı üretme.
2. **Modu ve yargı bölgesi paketini belirle (§1, §1.5).** Kullanıcı komut verdiyse (`/lex-draft` vb.) mod sabittir; serbest metinse tetikleyicilere göre seç. Yargı bölgesi belirtilmemişse varsayılan **TR** paketidir (3.x davranışı); başka bir bölge istendiyse o paketi yükle — paket yoksa uydurma, `manual_required` + mevcut paket listesi.
3. **TAM-FİLO devreye al (§3 — zorunlu, her sorgu).** Wire edilmiş **21 kaynak MCP + 3 companion**'un tamamı her sorguda taranır. Getirimi **≤4 paralel shard**'a böl (TR-çekirdek · karşılaştırmalı · doktrin · klinik), her shard'ı bir distiller alt-ajanına ver; ana bağlama yalnız kompakt `retrieval_distillate` + `coverage` döner. Bağlam ekonomisi ve büyük-veri disiplini **zorunludur** (§3.5) — ham veri ana pencereye girmez. Hiçbir server sessizce atlanmaz.
4. **Üst-norm zincirini kur.** `mcp__mevzuat__get_anayasa` → dayanak kanun/CBK → yönetmelik. Primer arama: anahtar kelime **ve** kanun/mevzuat NUMARASI (`search_mevzuat` `mevzuat_no` veya yalnız-rakam query), `phrase` (bedesten Solr), belge-içi `search_within_mevzuat`. Ayrıntı: `references/07-mevzuat-mcp-workflow.md`. Canlı primer `mevzuat.cureonics.com` **0.15.1+** (HP cutover 2026-08): phrase / `search_within` / bedesten tam gerekçe mevcut — tool listesinde yoksa uydurma; yoklukta ikincil veya `manual_required`.
5. **Klinik boyut varsa → evidentia'ya delege et (§5, her klinik-boyutlu sorguda).** Sağlık mevzuatında bu ≈ daima; klinik-sıfır saf idari normlarda atla ve **kapsam manifestosunda gerekçesiyle beyan et**.
6. **Metni/analizi üret**, ilgili **template**'i kullan (§2, `templates/`).
7. **G0-G11 kapılarından geçir (§4)** — G0 tam-filo kapsamını doğrular; kapı parametreleri (norm hiyerarşisi, dil profili, mahkemeler) aktif paketten okunur. `evidence_ledger` tut (`home_jurisdiction` + yabancı kayıtlarda `jurisdiction_role`).
8. **Çıktıyı sci-audit'e delege et (§5 — her çıktıda)** — atıf-adli + istatistik tutarlılık + Türkçe imla/halüsinasyon taraması.
9. **Kapsam manifestosu + confidence_label ile bitir (§7).** Hook yoksa (claude.ai / ChatGPT) Stop G0 hatırlatması gelmez — manifesto yine zorunludur.

**Progressive disclosure:** bu gövde load-bearing özet + yönlendirmedir. Her modun tam pipeline'ı, kapı kriterleri ve dil kuralları `references/` altındadır — ilgili modda **o dosyayı oku**.

## 1. On iki mod

| # | Mod | Tetikleyici | Çıktı template | Referans |
|---|---|---|---|---|
| 1 | **DRAFT** (çekirdek) | "yönetmelik/tebliğ taslağı hazırla", "ATMP düzenlemesi", "yeni mevzuat" | `templates/yonetmelik-taslagi.md` · `teblig-taslagi.md` | `references/04`, `01` |
| 2 | **AMEND** (çekirdek) | "şu maddeyi değiştir", "ek/geçici madde", "ibare değişikliği" | `templates/karsilastirma-cetveli.md` | `references/03`, `04` |
| 3 | **ANALYZE** | "şunu incele", "hukuka uygun mu", "sorun var mı" | hiyerarşik bulgu + risk ısı-haritası | `references/06`, `13` |
| 4 | **COMPLY** | "5210 uyumu", "drafting kalite kontrolü", "reform metnini denetle" | 21-nokta rapor + R6b skor-kartı | `references/06b` |
| 5 | **OPINE** | "kurum görüşü", "Md.6 görüşü", "TİTCK/komisyon görüşü", "bilirkişi mütalaası" | `templates/gorus-bildirimi.md` | `references/06`, `13` |
| 6 | **RIA** | "DEA hazırla", "düzenleyici etki analizi", "bütçe etki formu/BEF" | `templates/dea-template.md` · `bef-template.md` | `references/05` |
| 7 | **COMPARATIVE_LAW** | "karşılaştırmalı analiz", "AB karşılığı", "Japonya/PHARMAC nasıl", "reliance benchmark" | `templates/comparative-law-analysis.md` | `references/08`, `12` |
| 8 | **PARLIAMENTARY_BILL** — TR paketinde **TBMM_KANUN_TEKLIFI** (çekirdek, en üst) | "TBMM kanun teklifi", "1219 SK reform", "Anayasa Md.88" | `templates/tbmm-kanun-teklifi.md` (TR paketi) | `references/09` |
| 9 | **EX_POST_EVALUATION** | "ex post değerlendirme", "geriye dönük etki", "12-36 ay etki", "sunset clause" | `templates/ex-post-evaluation.md` | `references/05`, `11` |
| 10 | **REGULATORY_MATURITY** (4.0) | "WHO GBT", "düzenleyici olgunluk", "ML3 açığı", "NRA güçlendirme" | `templates/regulatory-maturity-gbt.md` | `references/11` |
| 11 | **TRANSPOSITION** (4.0) | "direktif aktarımı", "uyum tablosu", "transposition table", "AB müktesebatına uyum" | `templates/transposition-table.md` | `references/08` |
| 12 | **RELIANCE_FRAMEWORK** (4.0) | "reliance", "referans otorite", "kısaltılmış inceleme", "WHO Listed Authorities" | `templates/reliance-framework.md` | `references/11`, `12` |

**Mod adları yargı bölgesinden bağımsızdır.** Mod 8'in kanonik adı `PARLIAMENTARY_BILL`'dir; `TBMM_KANUN_TEKLIFI` TR paketinin `mode_aliases` eşlemesiyle ona çözülür ve 3.x'teki gibi kullanılmaya devam eder (gerileme yok). Mod 10–12 komutları: `/lex-maturity` · `/lex-transpose` · `/lex-reliance`.

**Mod başına pipeline özeti** `references/00-mod-pipelines.md` dosyasındadır; bir moda girdiğinde o dosyanın ilgili bölümünü oku. Çekirdek disiplin: **belirsiz manzarada ANALYZE landscape → sonra DRAFT**; DRAFT üst-norm + yatay semantik tarama + AB/uluslararası (german **resolve→EU**; ich **M4/M8** dosya-yapısıysa; cihaz→**eudamed** not ÜTS/TİTCK) + içtihat/doktrin + 5210 Md.15; AMEND `get_onceki_metinler` + Md.18-21; RIA **OECD GOV_REG zorunlu**; TBMM dayanağı **Anayasa Md.88 + İçtüzük Md.74-91** (5210 yalnız referans). **Mod 8:** `sira_no` onerge + gerekçe gövdesi `get_mevzuat_gerekce`; DSpace≠canlı GK. Conscious excludes: `shared/coverage-manifest.md` + `fleet.yaml` `conscious_excludes`.

## 1.5. Yargı bölgesi paketleri (4.0 — `jurisdictions/`)

4.0'da plugin **yargı bölgesinden bağımsız bir çekirdek** ile **takılıp çıkarılabilir ülke paketlerine** ayrıldı. Çekirdek: mod iskeletleri, kapı mantığı, kanıt defteri, no-fabrication, kapsam manifestosu, bağlam ekonomisi. Paket (`jurisdictions/<kod>/jurisdiction_pack.yaml`): norm hiyerarşisi, bağlayıcılar, yetenek bayrakları, legistik profil, dil profili, kurum haritası (düzenleyici · ödeyici · HTA · yasama · anayasal denetim), kapı parametreleri, mod takma adları, altın/adversarial vakalar.

| Paket | Durum | Not |
|---|---|---|
| `tr` | **active** (uzman paneli: `grandfathered` — 3.x davranışının birebir tanımı; "panelden geçti" DEĞİL) | Varsayılan. 3.9.0 davranışıyla aynıdır. |
| `gb` · `de` · `ch` | **draft** | Keşif amaçlı. Çıktı en fazla **LOW** (CC-6) + taslak uyarısı. Legistik profil `verified: false`. |

**Paketi kullanma kuralları:**

1. **Kod:** ISO 3166-1 alfa-2 (GB — "UK" değil), alt birim ISO 3166-2 (DE-BY), ulusüstü `ORG:` ad alanı (`ORG:AU` = Afrika Birliği; `AU` = Avustralya). Sözlük: `jurisdictions/_schema/supranational_codes.yaml`.
2. **Yetenek bayrakları → güven tavanı.** Paketin beş bayrağı (`has_consolidated_text` · `has_point_in_time` · `has_explanatory_memoranda` · `has_case_law_api` · `has_authentic_translation`) `jurisdictions/_schema/confidence_ceiling_rules.yaml`'deki CC-1…CC-8 kurallarıyla bir **tavan** üretir; `combined_confidence` bu tavanı **aşamaz** ve `confidence_label.confidence_ceiling` alanına yazılır. Kaynak bir şeyi yayımlamıyorsa ona dayanan iddia yüksek güvenle üretilemez.
3. **Yayım kuralı (pazarlık konusu değil):** wire'lı S1 bağlayıcısı olmayan paket `active` olamaz; uzman paneli değerlendirmesinden geçmemiş paket `active` olamaz. `tests/validate_packs.py` zorlar.
4. **Bağlayıcı sözleşmesi:** her ülke adaptörü `jurisdictions/_schema/connector_contract.yaml`'deki soyut yetenekleri (search · point_in_time_text · timeline · repeal_relations · article_tree · gazette_resolve · explanatory_memorandum · case_law_search · legislative_history) karşılar; düzey A (API/ELI/AKN) · B (yalnız HTML) · C (yalnız PDF gazete).
5. **Evrensel legistik rubrik:** 12 aile (`jurisdictions/_schema/legistic_rubric_families.yaml`); R6b'nin 21 kontrolü ailelere eşlidir. TR'de `gecis_hukumleri` ailesinin rubrik kontrolü **yoktur** — COMPLY bunu "denetlenmedi" diye beyan eder, uydurma kontrol eklenmez.
6. **Çekirdek/paket sınırı ölçülüdür:** `jurisdictions/core_files.yaml` çekirdek dosyalardaki TR kirlenmesini satır sayısıyla kaydeder (en ağır: `references/14`). Fiziksel taşıma Faz 0b'dedir.

## 2. Şablonlar (`templates/`)

`yonetmelik-taslagi` · `teblig-taslagi` · `karsilastirma-cetveli` (yurtiçi değişiklik) · `karsilastirma-uluslararasi` (3/6-sütun + HTA) · `comparative-law-analysis` (Mod 7, 13-bölüm) · `gorus-bildirimi` (kurum görüşü EK-1) · `genel-gerekce` · `madde-gerekce` (Md.23 tekrar-yok) · `dea-template` (DEA) · `bef-template` (BEF EK-3) · `tbmm-kanun-teklifi` (Mod 8, 9-bölüm) · `ex-post-evaluation` (Mod 9, 14-bölüm) · `regulatory-maturity-gbt` (Mod 10) · `transposition-table` (Mod 11) · `reliance-framework` (Mod 12). Mod 10–12 şablonları yargı bölgesinden bağımsız yazıldı; TR'ye özgü şablonlar TR paketinin `owned_files` listesindedir.

## 3. MCP filosu — tam-filo aktivasyonu (her sorguda)

Wire edilmiş 21 server **`fleet.yaml`'de tanımlıdır ve `.mcp.json` ondan üretilir** (20'si Bearer-anahtar-gated; `yoktez` public). Filo tanımının tek kaynağı budur — hook anahtar haritası, `/lex-connectors` tablosu, distiller araç kısıtları ve mod×server matrisi hep ondan türer; `tools/fleetkit/check_drift.py` (repo kökü) türetilmiş≠commit'li hâlini yakalar — bu araç **yalnız kaynak depoda vardır, kurulu plugin'de yoktur**; kurulu pakette `fleet.yaml` ve türevleri salt-okunur kanıttır. **Temel kural: hepsi her sorguda devreye alınır.** Primer/ikincil ayrımı artık *aktivasyon kapısı* değil, **sentezde otorite önceliğidir** — çatışmada primer kazanır, ama ikincil/support da **çalıştırılır** ve sonucu kapsam manifestosuna girer. Bir server'ın atlanması yalnız iki halde meşrudur: (a) o server için anahtar yok (SessionStart preflight işaretledi), (b) mod için mantıksal olarak N/A — **her iki hal de manifestoda gerekçesiyle beyan edilir** (sessiz atlama = G0 FAIL).

- **TR primer mevzuat:** `mcp__mevzuat__*` — semantik sıra: `list_mevzuat_types`→`list_mevzuat_by_type`/`search_*`→`get_mevzuat_detail`→yapısal graf→`search_within`→content→`get_mevzuat_gerekce`→`resolve_resmi_gazete`→`list_kurumlar`. Yapısal graf + bedesten (NUMARA, `phrase`, `search_within`, gerekçe).
  - **Canlı uç (zorunlu):** `mevzuat.cureonics.com` HP production **0.15.1+** (2026-08 cutover). Primer first-party bedesten: NUMARA lookup, `phrase`, `search_within_mevzuat`, `get_mevzuat_gerekce` tam metin (`content_source=bedesten` / `tbmm_locator+bedesten`; bedesten `gerekceId` yoksa locator-only dürüst kalır). Tool listesinde yoksa varmış gibi yazma.
  - **PRİMER DÜŞERSE YEDEK YOKTUR (v3.5.5 — 2026-09-12).** `mcp__mevzuat__*` **düşükse** (upstream TLS/erişim arızası, origin timeout, boş `items` + dolu `diagnostics`) Türk mevzuatı yükünü devralacak ikinci bir sunucu **yoktur**: ikincil ayna `mevzuat-bilgisi` kaldırıldı (aynı upstream'i farklı bir uygulamayla okuyordu, yani veri değil yalnız çapraz-kontrol sağlıyordu, ve upstream'i kalıcı kapalıydı). **Eski DEVRALMA KURALI geçersizdir — var olmayan bir sunucuya devretmeyi emrediyordu.** Bunun yerine ÇIKTI DÜRÜSTÇE DURUR: (a) manifestoya `mevzuat → degraded: <teşhis>` yazılır ve İKİNCİ bir satır aranmaz; (b) TR-mevzuat iddiası ÜRETİLMEZ — `manual_required` (mevzuat.gov.tr derin-bağlantısı + sorgu yankısı); (c) primer ayağa kalkınca sorgu tekrarlanır. `resolve_resmi_gazete`, yapısal graf (`madde_tree`/`madde_diff`/`timeline`/`relations`/`ilga`) ve `get_mevzuat_gerekce` zaten YALNIZ primerdeydi; TBMM yasama tarihçesi yalnız `mcp__tbmm__*`'tedir. Boşluğu doldurmak için model belleğinden mevzuat metni yazmak G0 + no-fabrication ihlalidir.
- **Resmî metin/yürürlük:** `mcp__resmi-gazete__*`. **İkincil mevzuat/soft-law:** `mcp__saglikbakanligi__*`. **Beşeri tıbbi ürün/ruhsat (cihaz/ÜTS değil):** `mcp__titck__*`. **Yasama tarihçesi (tbmm-mcp 0.2.1 — çağır, atlama yok):** `mcp__tbmm__*` Mod 8 load-bearing, diğer modlarda çapraz. Rota: (1) teklif `tbmm_search_kanun_teklifi` → `tbmm_get_kanun_teklifi(sira_no)` özet+imza+komisyon aşaması; `kanun_no` yalnız `kanunlar.durumu` locator (`rg_sayisi`/`donem` pin). (2) Gerekçe **gövdesi** `mcp__mevzuat__get_mevzuat_gerekce`; TBMM locator `tbmm_search_kanun`. (3) Komisyon `tbmm_search_komisyon_raporu` → `tbmm_get_komisyon_raporu`; havale `tbmm_list_komisyon_havale` (query'siz deep-link). (4) Tutanak `tbmm_search_tutanak` → `tbmm_get_tutanak` (bilinen id/PDF); SPA `manual_required` iken `related_acik_erisim` **kütüphane zabıtıdır**, canlı Genel Kurul DEĞİLDİR. (5) Sponsor `tbmm_get_milletvekili` (güncel dönem; `donem_filter_ignored`). (6) Tarihsel OA `tbmm_list_acik_erisim_collections` → `tbmm_search_acik_erisim(page/year/collection)` → `tbmm_get_acik_erisim_document`. `tasari_teklif_sd.onerge` 302→anasayfa, kullanılmaz. Tam kanun metni `mcp__mevzuat__*`. **Kurumsal atıf:** `mcp__detsis__*`.
- **Karşılaştırmalı:** `mcp__health-policy__*` (semantic→govinfo/congress/…→fetch; ChatGPT search/fetch tools_used dışı), `mcp__german-law__*` (**resolve→provision→SONRA EU ailesi**; premium case_law conscious exclude), `mcp__eurlex__*` (browse→search→`eurlex_lookup_celex` G6), `mcp__uk-legal__*` (`legislation_search`→`_get_toc`→`_get_section` + case/Hansard), `mcp__fedlex__*` (params+search-before-get; **RIA:** SR get sonrası Vernehmlassung open/search/get — TR DRAFT usulü değil), `mcp__ich-guidelines__*` (**M4/M8 dosya-yapısı zorunlu**), `mcp__intl-treaty__*` (Md.90/5), `mcp__eudamed__*` (**cihaz; ÜTS/TİTCK değil**), `mcp__oecd__*` (9 araç; **RIA GOV_REG zorunlu** + HEA).
  - **Doğal-dil giriş kapısı:** önce `semantic_search`; keşif sonrası `govinfo_search`/`congress_search`/`japan_elaws_search`/`australia_legislation_search`/`china_law_recent`/`ecfr_versions` + ilgili fetch. Semantik = keşif, fetch = doğrulama.

### Anayasa Md. 90/5 — intl-treaty ateş listesi (zorunlu)

COMPARATIVE_LAW, DRAFT/AMEND gerekçe (üst-norm), COMPLY (K-1) ve TBMM teklifi **atlanamaz**. Distiller (`legal-distiller` S1, `comparative-law-researcher` S2, `gerekce-drafter`, `compliance-auditor`) şu araçları **ateşler**:

- `treaty_status` + `treaty_reservations` — ICESCR (IV-3), ICCPR, CEDAW, CRC, CRPD ve dosyanın adlandırdığı chapter-IV alias (onay/çekince/itiraz; `mcp_verified:false`).
- `coe_treaty_signatories` — Oviedo CETS 164 ve MEDICRIME CETS 211 (9 CETS anlık görüntü; `snapshot_age_days`; `mcp_verified:false`). `live_coe:false` kapsam satırında **beyanlı degrade** (`degraded: snapshot`), skip-without-reason değil.
- `intl_treaty_info` — dosya başına bir kez (coverage manifesto: `live_coe:false`, `relay_inert:true`).
- UHRI `uhri_search` / `uhri_fetch_document` **tools_used** (2026-08-18): HP
  sağlık-hakları indexer; COMPARATIVE / Md.90/5 / ICESCR dosyalarında
  treaty+coe+info **SONRASI zorunlu** (yerine geçmez). `mcp_verified:false`;
  boş ≠ yokluk. Dump Worker'a GET edilmez.
- Andlaşma↔kanun çatışması → gerekçede Anayasa md. 90/5 cümlesi; onay/çekince **uydurulmaz**. Oviedo TR taraf statüsü `coe_treaty_signatories` snapshot'ından okunur (stale "imzalamadı" yazılmaz).

- **Doktrin (üç katman, üçü de wire'lı):** `mcp__yok-akademik__*` **metadata** (akademisyen profili, yayın listesi, danışmanlık) · `mcp__yoktez__*` **tez tam-metni** (YÖK Ulusal Tez Merkezi; arama + sayfa-sayfa Markdown) · `mcp__literatur__*` **makale tam-metni** (DergiPark; `search_articles` → `pdf_to_html` → `get_article_references`). **v3.5.0 değişikliği:** yoktez artık companion değil, first-class wire'lıdır — dolayısıyla **G7'deki YÖK-Tez atıf doğrulaması kullanıcı aksiyonuna bağlı değildir** (tez no/başlık/yazar `get_yok_tez_thesis_details` ile teyit edilir → uydurma tez atfı deterministik yakalanır). literatur, doktrin katmanının tek *okunabilir* TR kaynağıdır: yok-akademik yalnız künye verir, gerekçede alıntılanabilir metin buradan gelir.
- **Tam-metin şelalesi (yabancı hukuk doktrini — Mod 7/ANALYZE/RIA/OPINE/EX_POST):** `mcp__openathens__*` **Tier 3 lisanslı** (Millet Kütüphanesi/OpenAthens SAML; paywall'lı monograf/hakemli makaleye yasal erişim) → yalnız o denendikten sonra `mcp__annas-reader__*` **Tier 4 son çare**. OpenAthens'te doktrin metni/RAG için `oa_fetch_fulltext`, orijinal sağlayıcı PDF'i için provider-nötr `oa_fetch_pdf(doi|url)`; Anna's bandında bounded reader akışı veya orijinal PDF/EPUB/etc. için `download_document(id=<DOI|32-hex MD5>)` kullanılır. Dosya araçları kısa-ömürlü opaque `resource_link` + SHA-256/provenance döndürür: link derhal tüketilir, kalıcı URL diye cache'lenmez ve evidence_ledger'a DOI/MD5 + checksum yazılır. **Şelale disiplini zorunludur:** openathens'in erişilemez olması annas-reader'ı *otomatik açmaz* — son çare açık gerekçeyle kullanılır ve **YALNIZ ANALİZ içindir**. Bu katman **birincil norm metni değildir**; yalnız doktrin desteğidir.
- **Companion (dış connector — tam-filonun ZORUNLU üyeleri; bkz. `/lex-connectors`):** yalnız **üç** tanedir: Yargı içtihat (`mcp__Yarg__*`), Open Law (UK **çapraz/HUDOC + yedek**; statute birincil = wire `uk-legal` `legislation_*`, `mcp__Open_Law__*`), Ansvar (58-yargı tarama, `mcp__Ansvar__*`). Kararlı self-host URL'leri yoktur; claude.ai/Cursor connector ayarlarından bağlanır. **Fedlex 2026-08-08'de wire edildi** (`mcp__fedlex__*`) — companion DEĞİLDİR. Türk Patent wire'ı 2026-08-17'de emekli edildi (ölü Capsolver upstream). *(Önek notu: claude.ai connector öneki yüzeye göre `mcp__Yarg__*` ya da `mcp__claude_ai_Yarg__*` görünebilir — eşleştirmeyi server ADINA göre yap.)* Bağlı companion "opsiyonel" DEĞİLDİR — tetiklenmiş bağlamda çağrılmaları zorunludur:
  - **Yargı ↔ G5:** içtihat zinciri (AYM belirlilik/iptal emsali, Danıştay idari-işlem, Yargıtay) HER modda `mcp__Yarg__*` ile taranır. Yargı bağlı değilse **G5 tam PASS olamaz → CONDITIONAL**.
  - **Open Law ↔ UK (G6 DEĞİL):** UK çapraz + HUDOC. Statute birincil yolu `mcp__uk-legal__legislation_*`. **G6 CELEX wire'lı `mcp__eurlex__eurlex_lookup_celex`'tedir**. Open Law bağlı değilse / origin fail → `ep.legislation_uk`; G6'yı düşürmez. "UK statute yalnız Open Law" YASAK. german-law `get_eu_basis` CELEX üretmez — G6 yedeği değildir.
  - **Ansvar ↔ Mod 7 + yatay çerçeveler:** CH/FR/IT/NL/SE/DK/FI/AT/PL + 58-yargı tarama + GDPR/NIS2. CH **birincil metni** wire'lı `mcp__fedlex__*`'tedir (Ansvar = çerçeve-teyit; çatışmada Fedlex kazanır). Bağlı değilse o yargı satırı `manual_required` — tablodan silinmez.

**Nasıl tam-filo tarama yapılır (retrieve-don't-dump ile):** getirimi **≤4 paralel shard**'a böl (§3.5) ve her shard'ı bir distiller alt-ajanına **tek görevde** ver; alt-ajanlar server'ları paralel süpürür, ham çıktıyı kendi bağlamlarında tüketir, ana bağlama yalnız kompakt `retrieval_distillate` zarfı (~15-20 bulgu, her biri identifier/url'li) + **`coverage` bloğu** (her server: hit/empty/degraded/skipped-with-reason) döner. Zarfın bağlayıcı biçimi: `schemas/retrieval_distillate.schema.json` (v1.2 — 4.0: `jurisdiction` ISO/ORG: deseni, `id_kind` += akn · ecli · urn-lex · x-<ad>) — şemaya uymayan zarf kabul edilmez. Bu, "hepsi çalışsın" ile "bağlamı boğma"yı uzlaştırır: tüm araçlar ateşlenir, ana pencereye yalnız damıtılmış sonuç + kapsam kanıtı gelir. Bir server yoksa/boşsa → **veri boşluğu** olarak işaretle, doldurma; `degrade_and_label` (fetch fallback + `mcp_verified=false`).

## 3.5. Bağlam ekonomisi ve büyük-veri (zorunlu)

Tam-filo, ham hâliyle onlarca büyük belge (tam kanun metni, madde ağacı, RG OCR, yabancı statute, tam gerekçe) üretir. Bunları ana pencerede akıl yürütmek pencereyi taşırır → eksik/tutarsız norm. **Üç-katmanlı ekonomi zorunludur** (tam sözleşme: `shared/context-economy-contract.md`, operasyon: `references/16-baglamyonetimi-ve-buyuk-veri.md`):

- **Tier 0 — Ana pencere (kıt):** yalnız talep · mod planı · G0 manifesto · damıtılmış zarflar · `evidence_ledger` · nihai metin. **Ham araç çıktısı ASLA girmez.**
- **Tier 1 — Distiller alt-ajanları (izole):** `legal-distiller` (S1 TR-çekirdek, S3 doktrin) · `comparative-law-researcher` (S2) · `evidence-synthesizer` (S4 klinik) · `gerekce-drafter` · `compliance-auditor` — ham getirimi kendi pencerelerinde tüketir, kompakt zarf döner. Sharding, tek bir distiller'ın da taşmasını önler.
- **Tier 2 — RAG substratı (`anamnesis`):** büyük tam-metin `ingest_document(collection='cureolex:sess:<id>', doc_id='cureolex:sess:<id>:mevzuat:…')` ile **bir kez** indekslenir → `hybrid_query(collection=…, doc_ids=[…], queries[])` ile sınırlı, provenance-damgalı **dilim** çekilir (`doc_id::idx`). **`doc_scope` yoktur.** Aynı önekli doc_id iki kez ingest edilmez (**kanonik cache**, G0–G11 aynı sess). `lib` varsayılan değil.

**Büyük belge disiplini:** kör getirme yok — önce yapısal navigasyon (`get_mevzuat_madde_tree`/`timeline`/`relations`) ile hedefi lokalize et → yalnız hedef chunk'ı çek (`madde_acikla` / `get_mevzuat_text` `chunk_index`/`start_page`-`end_page`/`max_chars` / `download_mevzuat_document(include_base64=false)`) → tam-metin gerekiyorsa anamnesis'e ingest. **Devre-kesici:** tek çıktı >6KB → PostToolUse hook uyarır, ham işleme; distiller/anamnesis'e yönlen. **Extract-then-evict:** her faz sonu ara getirimleri `evidence_ledger`'a çök, ham izi at. anamnesis anahtarı yoksa → bounded-chunk fallback'e degrade, manifestoda beyan et — asla ham döküm.

## 4. Kalite kapıları (G0-G11)

Her mod **G0-G7'den geçer**; G8/G9 moda bağlıdır; **G10 ve G11 (4.0) her modda** çalışır. Kriterler `references/06b-compliance-executable-rubric.md` ve `references/09` içindedir. **Parametreler paketten gelir:** G1 legistik profili, G2 norm hiyerarşisi ve anayasal denetim merciileri, G3/G4 dil profili, G5 mahkeme listesi, G8 parlamento usulü, G10 belirli-tarih araçları, G11 ev bölgesi konumu — aktif paketin `gate_params` alanında. Aşağıdaki tablo TR paketinin değerleriyle yazılmıştır.

| Kapı | Ad | PASS kriteri |
|---|---|---|
| **G0** | Tam-filo kapsam (§3) | Wire edilmiş 21 MCP + **3 companion (Yarg/Open_Law/Ansvar — zorunlu satırlar)** + evidentia (klinik-boyut varsa) + sci-audit **tamamı** ateşlenmiş; her biri kapsam manifestosunda hit/empty/degraded/skipped-with-reason olarak görünür. Companion/plugin `skipped` yalnız gerçek yoklukta meşrudur ve ilgili kapıyı (G5/G6) CONDITIONAL'a düşürür. intl-treaty `live_coe:false` **beyanlı degrade** (`degraded: snapshot`) — sessiz atlama = FAIL. |
| **G1** | 5210 şekli uyum (Md.10-22) | Madde başlık formatı, fıkra-bent hiyerarşisi, Md.21 atıf (ses uyumu, sıfırsız tarih), ek/geçici madde kuralları |
| **G2** | 5210 maddi-anayasal uyum (Md.4-9) | Üst-norm uygunluğu, AYM belirlilik, AB müktesebatı, kazanılmış hak, geriye yürümezlik |
| **G3** | Türk hukuk dili (R9, 15-nokta) | Tabaka seçimi, Md.25 kuralları, yabancı sözcük yok, kısa cümle, ses-uyumu ekleri, anti-pattern temiz |
| **G4** | Anti-pattern denetimi | §7 yasak kalıpların hiçbiri yok + `references/09-turk-hukuk-dili-ve-uslubu.md` anti-pattern bölümü (çok-anlamlı terim · anti-pattern toplaması · Md.11 kontrol listesi md.11) temiz. **Sayı iddiası yok:** kapı, kanonik listenin O ANKİ uzunluğuna göre ölçülür — v3.5.5'e kadar "27 kalem" deniyordu ama 27 maddelik numaralı liste hiçbir dosyada yoktu (2026-08-07 denetimi, Ö-7); sayıyı tutturmak için liste uydurmak yerine iddia kaldırıldı. |
| **G5** | İçtihat + doktrin (R13) | AYM/Danıştay/Yargıtay/AİHM/ABAD zinciri (**Yargı companion `mcp__Yarg__*` ile taranmış**) + Türk doktrin **üç wire'lı katmandan** atıflı: yok-akademik (künye) + yoktez (tez tam-metni) + literatur (DergiPark makale tam-metni). Yargı bağlı değil → en fazla CONDITIONAL |
| **G6** | Uluslararası kaynak teyidi (R8/10/11/12) | CELEX konsolide doğrulanmış (**birincil araç: wire'lı `mcp__eurlex__eurlex_lookup_celex`**; degrade: `ep.eurlex_sparql` + CONDITIONAL — german-law `get_eu_basis` CELEX üretmez); WHO/ICH/PIC/S/IMDRF güncel; **Md.90/5:** `treaty_status`/`treaty_reservations` (ICESCR 12+AAAQ + ICCPR/CEDAW/CRC/CRPD) ve `coe_treaty_signatories` (Oviedo 164 / MEDICRIME 211, snapshot) — onay uydurulmaz |
| **G7** | Epistemik dürüstlük | Uydurma kanun/CELEX/AYM/Yargıtay/YÖK-Tez yok; her atıf MCP- veya primer-kaynak-doğrulanmış. **YÖK-Tez atıfları wire'lı `mcp__yoktez__get_yok_tez_thesis_details` ile doğrulanır** (tez no/başlık/yazar) — companion'a bağlı değil, **hard PASS** (v3.5.0). Doğrulanamayan tez atfı `illustrative_placeholder_not_verified` → KULLANILMAZ |
| **G8** | TBMM kapsam (Mod 8) | 5210 Md.1/3 kapsam-dışı notu; İçtüzük Md.74-91 primer; 9-bölüm iskelet tam; `tbmm_get_kanun_teklifi(sira_no)` veya dürüst `manual_required`; DSpace zabıt ≠ canlı tutanak |
| **G9** | Ex-post kapsam (Mod 9) | 5 OECD kriteri hükme bağlanmış; ex-ante↔ex-post tablo; K-1/2/3 kararı; 14-bölüm iskelet |
| **G10** | Güncellik / belirli-tarihte yürürlük (4.0) | Dayanak yapılan her norm referans tarihinde **yürürlükte** (defter: `as_of_date` + `in_force_status`); `repealed` hüküm yürürlükteki dayanak olarak kullanılmamış. TR: `get_onceki_metinler` + `get_mevzuat_timeline` + `get_mevzuat_relations`/`search_mulga_mevzuat` + RG çözümü. Paket `has_point_in_time: false` ise en fazla **CONDITIONAL** (CC-2) |
| **G11** | Yargı bölgesi tutarlılığı (4.0) | Defter `home_jurisdiction` taşır; farklı bölgeden gelen her kanıt `jurisdiction` + `jurisdiction_role` (binding · transposition_source · comparative_benchmark · persuasive · treaty_obligation) beyan eder. **Yabancı norm `binding` olamaz** (istisna: paket AB üyeliğini beyan ediyorsa AB normu). Alt birim normu üst birim normu gibi sunulmaz; paketin dil/legistik profili başka bölgenin çıktısına uygulanmaz. Statik denetim: `tests/validate_packs.py::g11_ihlalleri` |

**G-Reverse:** evidentia sidecar `reverse_signals` doluysa Executive Summary'de görünür kılınmalı. **R6b eşikleri (Mod 4):** tümü PASS/N-A & CONDITIONAL≤3, FAIL=0 → YAYINA HAZIR; 1 yüksek-risk FAIL → düzeltme zorunlu; FAIL≥2 → kapsamlı revizyon; FAIL≥5 veya K-1/K-17 FAIL → tasarımı yeniden gözden geçir. K-1 (üst-norm) önce test edilir; FAIL ise dur.

## 5. Zorunlu delegasyon — evidentia + sci-audit (bağlam-tetiklemeli)

Bu plugin **bağımsızdır** (ikisi de yokken 12 mod çalışır); ancak bu iki plugin **kuruluysa çağrılmaları opsiyonel DEĞİL, zorunludur** — bağlam tetiklendiğinde atlanmaları **G0 ihlalidir**. Degrade yalnız plugin'in gerçekten kurulu olmadığı durumda meşrudur ("veri boşluğu" işaretiyle, asla uydurmadan) ve manifestoda beyan edilir; SessionStart preflight kurulum durumunu oturum başında işaretler. Tam sözleşme: `shared/composition-contract.md`.

- **Klinik kanıt → evidentia (her klinik-boyutlu sorguda).** Konu ilaç/cihaz/hastalık/tedavi/klinik-çalışma/geri-ödeme içeriyorsa **daima** devrede (DRAFT/ANALYZE/OPINE/RIA/COMPARATIVE/TBMM/EX_POST zorunlu; AMEND/COMPLY koşullu — ama sağlık mevzuatında klinik-boyut ≈ daima vardır). Klinik-sıfır saf idari norm → atla + manifestoda beyan et. **Zenginleştirilmiş sorgu** kur (ham değil): `main_query` (İngilizce) + `explicit_layer_request` + `cureolex_legal_context` (TR referanslar + Anayasa + antlaşmalar) + `requested_sections_priority` + `citation_format:Vancouver` + `epistemic_dual_label:true`. `/evidentia` komutuna veya `evidence-synthesizer` alt-ajanına delege et; dönen sidecar'da **önce `reverse_signals`** oku. Aktarılan her TR referansı `mcp__mevzuat__*`/`mcp__Yarg__*` ile çapraz-doğrula. Kaynakça **asla karıştırma**: 8.1 Türk+uluslararası mevzuat / 8.2 bilimsel (Vancouver) / 8.3 Türk içtihat.
- **Güvenilirlik + dil → sci-audit (her çıktıda).** Üretilen metnin atıflarını `/verify-citations`, istatistik/nicel iddialarını `/check-stats`, halüsinasyon sinyallerini ve Türkçe yazımı `/check-turkish` ile **her çıktıda** denetlet (bu, tam-filo ilkesinin çıktı-QA ayağıdır). sci-audit ekseni bilimsel-yazım odaklıdır; **hukuk dili G3/R9'da cureolex'a aittir** — sci-audit'i tamamlayıcı imla/tutarlılık/atıf-bütünlüğü katmanı olarak kullan, hukuk-dili otoritesi olarak değil.

**Çift epistemik-dürüstlük etiketi** klinik çıktıda zorunludur: klinik kanıtta evidentia, hukuki bağlayıcılıkta cureolex otoritedir. **İnsan denetimi her zaman gereklidir.**

## 6. Scope Guard — kapsam sınırı

**Bağlam karar verir, terim değil.** KAPSAM İÇİ = mevzuat *reformu* (12 mod). YÖNLENDİR:

| Konu | Yönlendir |
|---|---|
| Bireysel SGK ödeme reddi davası · AYM bireysel başvuru (sağlık) · kompasyonel kullanım talebi · hekim malpraktis savunması | `saglik-sigorta` / `onko-erisim` skill'leri |
| Promosyonel materyal denetimi (detail aid, leave-behind, MLR, speaker bureau, CME) | `promo-censor` skill'i |

Şüphede **yönlendir, çıktı üretme**. İçtihat kaynakları reform-**gerekçe** sinyalidir; dava dilekçesi üretimi için DEĞİL.

## 7. Çıktı sözleşmesi — kapsam manifestosu + no-fabrication + confidence_label

- **Kapsam manifestosu (G0, zorunlu — çıktı başında veya sonunda):** tam-filonun kanıtı. Her wire'lı MCP + bağlı companion + evidentia + sci-audit için tek satır: `server → durum (hit N kayıt / empty / degraded / skipped: <gerekçe>)`. Bu blok, "hepsi her sorguda çalıştı" iddiasının doğrulanabilir kanıtıdır; eksik satır = G0 FAIL. Örnek biçim `shared/coverage-manifest.md`'de.
- **No-fabrication (G7):** kanun maddesi, CELEX, AYM/Yargıtay/YÖK-Tez, PMID, NCT, NICE-TA, FDA-Guidance başlığı **asla uydurma**. Her referans MCP- veya primer-kaynak-doğrulanmış (YÖK-Tez atıfları **wire'lı `mcp__yoktez__*`** ile — tez no/başlık/yazar — doğrulanır; bu artık companion'a bağlı değildir). Doğrulanamayan → `illustrative_placeholder_not_verified` etiketle, kullanma. Doğrulanamayan referans varsa → **"MCP üzerinden doğrulanamayan referans"** notu.
- **evidence_ledger:** her somut bilimsel/hukuki iddia → bir `E###` kaydı (kaynak, GRADE, `mcp_verified` bayrağı, desteklenen bölümler, Vancouver atıf). `status=verified` yalnız `mcp_verified=true` ise. Şema: `schemas/evidence_ledger.schema.json`. Kanıt işaretleri `[E1]/[E2]…` sıralı.
- **confidence_label (zorunlu, çıktı sonu):** mod + `jurisdiction_pack` (kod · sürüm · durum) + `confidence_ceiling` (tavan + uygulanan CC kuralları) + `combined_confidence` (HIGH/MODERATE/LOW — tavanı aşamaz) + `human_review_required:true` + çift öz-beyan (cureolex MCP-erişilemezliği & belirsiz yorumlar; evidentia bilgi-boşlukları & tek-kaynak bulgular) + `scope_disclaimer`. Şema: `schemas/confidence_label.schema.json`.
- **Temiz-kopya doktrini:** nihai metin, süreç gürültüsünden (araç çağrıları, ham getirim) arınmış olmalı.

## 8. Referans haritası (`references/`)

**Efsane:** kapılarda geçen `R##` = `references/##` dosyası (R9 = `09-…`, R6b = `06b-…`, R8/10/11/12 = ilgili numaralı dosyalar).

`00-mod-pipelines` (mod-başına adım-adım) · `01-cerceve-5210` · `02-saglik-mevzuat-haritasi` · `03-atif-teknigi` (Md.21) · `04-madde-yapisi` (Md.10-22) · `05-dea-bef` · `06-compliance-checklist` · `06b-compliance-executable-rubric` (R6b) · `07-mevzuat-mcp-workflow` · `08-uluslararasi-kaynaklar` · `09-turk-hukuk-dili-ve-uslubu` (3 Tabaka + 15-nokta QC) · `10-bm-uluslararasi-saglik-hukuku` · `11-who-derinlemesine-rejim` · `12-gelismis-ulke-rejimleri-derin` · `13-icthat-doktrin-akademik-katman` · `14-medical-research-entegrasyon-katmani` · `14b-medical-research-operational-integration` · `15-programatik-veri-kaynaklari` · `16-baglamyonetimi-ve-buyuk-veri` (bağlam ekonomisi + büyük-veri operasyon protokolü).

> Not: `references/14`/`14b` "medical-research v7.1" adını taşır; canlı entegrasyon hedefi **evidentia plugin** (skill `medical-research`, komut `/evidentia`, alt-ajan `evidence-synthesizer`). İçerik (§×mod matrisi, sidecar şeması, reverse-channel) geçerlidir; yalnız çağrı yüzeyi evidentia'dır.
