---
name: lex-sanitas
description: >-
  Türkiye sağlık mevzuatı reform protokolü — kanun · CBK · yönetmelik · tebliğ · genelge düzeyinde yeni mevzuat
  üretmek, değiştirmek, yeniden yazmak için 9 mod (DRAFT · AMEND · ANALYZE · COMPLY · OPINE · RIA ·
  COMPARATIVE_LAW · TBMM_KANUN_TEKLIFI · EX_POST_EVALUATION). 5210 Yönetmelik + AYM belirlilik içtihadı +
  OECD Better Regulation + Anayasa Md.17/56/90/5; G0-G9 kapı + no-fabrication (evidence_ledger). Kullan —
  "yönetmelik/tebliğ taslağı hazırla", "şu maddeyi değiştir", "TBMM kanun teklifi", "1219 SK reform", "TİTCK
  yönetmelik", "SUT reform", "ATMP/HTA düzenlemesi", "5210 uyum denetimi", "düzenleyici etki analizi/DEA",
  "karşılaştırmalı analiz / AB karşılığı", "ex post değerlendirme". 19 wire'lı MCP + 5 companion (Yargı ·
  Open Law · Ansvar · Fedlex Swiss · Türk Patent) tam-filonun zorunlu üyeleri; klinik kanıt → evidentia,
  atıf-adli + Türkçe hukuk dili → sci-audit (kuruluysa ZORUNLU). Şüphede Scope Guard önceliklidir;
  bireysel dava (SGK reddi, AYM başvuru), malpraktis ve promosyon denetimi KAPSAM DIŞIDIR.
version: 3.5.6
---

# Lex-Sanitas — Türkiye Sağlık Mevzuatı Reform Protokolü

Bu yetkinlik, **Türkiye'de sağlık mevzuatının her düzlemde reform, değişiklik ve yeniden yazımı** için tasarlanmış norm-üretim protokolüdür. En temel düzeyden (Anayasal sağlık hakkı) en operasyonel düzeye (tebliğ/genelge) kadar **yeni mevzuat üretir, mevcut mevzuatı değiştirir, gerektiğinde çerçeveyi tamamen yeniden yazar** — **5210 sayılı Yönetmelik** (RG 24/2/2022, 31760), **AYM belirlilik içtihadı**, **OECD Better Regulation**, **Anayasa Md.17/56 + Md.90/5 + ICESCR Md.12** ekseninde ve **savunulabilir, kanıt-temelli** biçimde.

## 0. Nasıl çalışılır (her modda)

1. **Scope Guard'ı önce uygula (§6).** Şüphede yönlendir, çıktı üretme.
2. **Modu belirle (§1).** Kullanıcı komut verdiyse (`/lex-draft` vb.) mod sabittir; serbest metinse tetikleyicilere göre seç.
3. **TAM-FİLO devreye al (§3 — zorunlu, her sorgu).** Wire edilmiş **19 kaynak MCP + 5 companion**'un tamamı her sorguda taranır. Getirimi **≤4 paralel shard**'a böl (TR-çekirdek · karşılaştırmalı · doktrin · klinik), her shard'ı bir distiller alt-ajanına ver; ana bağlama yalnız kompakt `retrieval_distillate` + `coverage` döner. Bağlam ekonomisi ve büyük-veri disiplini **zorunludur** (§3.5) — ham veri ana pencereye girmez. Hiçbir server sessizce atlanmaz.
4. **Üst-norm zincirini kur.** `mcp__mevzuat__get_anayasa` → dayanak kanun/CBK → yönetmelik. Arama **KEYWORD** tabanlıdır (`"organ ve doku nakli"`, `"3960"` değil). Ayrıntı: `references/07-mevzuat-mcp-workflow.md`.
5. **Klinik boyut varsa → evidentia'ya delege et (§5, her klinik-boyutlu sorguda).** Sağlık mevzuatında bu ≈ daima; klinik-sıfır saf idari normlarda atla ve **kapsam manifestosunda gerekçesiyle beyan et**.
6. **Metni/analizi üret**, ilgili **template**'i kullan (§2, `templates/`).
7. **G0-G9 kapılarından geçir (§4)** — G0 tam-filo kapsamını doğrular. `evidence_ledger` tut.
8. **Çıktıyı sci-audit'e delege et (§5 — her çıktıda)** — atıf-adli + istatistik tutarlılık + Türkçe imla/halüsinasyon taraması.
9. **Kapsam manifestosu + confidence_label ile bitir (§7).**

**Progressive disclosure:** bu gövde load-bearing özet + yönlendirmedir. Her modun tam pipeline'ı, kapı kriterleri ve dil kuralları `references/` altındadır — ilgili modda **o dosyayı oku**.

## 1. Dokuz mod

| # | Mod | Tetikleyici | Çıktı template | Referans |
|---|---|---|---|---|
| 1 | **DRAFT** (çekirdek) | "yönetmelik/tebliğ taslağı hazırla", "ATMP düzenlemesi", "yeni mevzuat" | `templates/yonetmelik-taslagi.md` · `teblig-taslagi.md` | `references/04`, `01` |
| 2 | **AMEND** (çekirdek) | "şu maddeyi değiştir", "ek/geçici madde", "ibare değişikliği" | `templates/karsilastirma-cetveli.md` | `references/03`, `04` |
| 3 | **ANALYZE** | "şunu incele", "hukuka uygun mu", "sorun var mı" | hiyerarşik bulgu + risk ısı-haritası | `references/06`, `13` |
| 4 | **COMPLY** | "5210 uyumu", "drafting kalite kontrolü", "reform metnini denetle" | 21-nokta rapor + R6b skor-kartı | `references/06b` |
| 5 | **OPINE** | "kurum görüşü", "Md.6 görüşü", "TİTCK/komisyon görüşü", "bilirkişi mütalaası" | `templates/gorus-bildirimi.md` | `references/06`, `13` |
| 6 | **RIA** | "DEA hazırla", "düzenleyici etki analizi", "bütçe etki formu/BEF" | `templates/dea-template.md` · `bef-template.md` | `references/05` |
| 7 | **COMPARATIVE_LAW** | "karşılaştırmalı analiz", "AB karşılığı", "Japonya/PHARMAC nasıl", "reliance benchmark" | `templates/comparative-law-analysis.md` | `references/08`, `12` |
| 8 | **TBMM_KANUN_TEKLIFI** (çekirdek, en üst) | "TBMM kanun teklifi", "1219 SK reform", "Anayasa Md.88" | `templates/tbmm-kanun-teklifi.md` | `references/09` |
| 9 | **EX_POST_EVALUATION** | "ex post değerlendirme", "geriye dönük etki", "12-36 ay etki", "sunset clause" | `templates/ex-post-evaluation.md` | `references/05`, `11` |

**Mod başına pipeline özeti** `references/00-mod-pipelines.md` dosyasındadır; bir moda girdiğinde o dosyanın ilgili bölümünü oku. Çekirdek disiplin: DRAFT üst-norm + yatay semantik tarama + AB/uluslararası benchmark + içtihat/doktrin + 5210 Md.15 madde sırası; AMEND `mcp__mevzuat__get_onceki_metinler` (kümülatif) + Md.18-21 değişiklik tekniği; TBMM dayanağı **Anayasa Md.88 + TBMM İçtüzüğü Md.74-91** olup **5210 yalnız referanstır** (Md.1/3 teklifleri hariç tutar — "5210-uyumlu" DENMEZ).

## 2. Şablonlar (`templates/`)

`yonetmelik-taslagi` · `teblig-taslagi` · `karsilastirma-cetveli` (yurtiçi değişiklik) · `karsilastirma-uluslararasi` (3/6-sütun + HTA) · `comparative-law-analysis` (Mod 7, 13-bölüm) · `gorus-bildirimi` (kurum görüşü EK-1) · `genel-gerekce` · `madde-gerekce` (Md.23 tekrar-yok) · `dea-template` (DEA) · `bef-template` (BEF EK-3) · `tbmm-kanun-teklifi` (Mod 8, 9-bölüm) · `ex-post-evaluation` (Mod 9, 14-bölüm).

## 3. MCP filosu — tam-filo aktivasyonu (her sorguda)

Wire edilmiş 19 server **`fleet.yaml`'de tanımlıdır ve `.mcp.json` ondan üretilir** (16'sı Bearer-anahtar-gated; `mevzuat-bilgisi`, `yoktez`, `literatur` public). Filo tanımının tek kaynağı budur — hook anahtar haritası, `/lex-connectors` tablosu, distiller araç kısıtları ve mod×server matrisi hep ondan türer; `tools/fleetkit/check_drift.py` (repo kökü) türetilmiş≠commit'li hâlini yakalar — bu araç **yalnız kaynak depoda vardır, kurulu plugin'de yoktur**; kurulu pakette `fleet.yaml` ve türevleri salt-okunur kanıttır. **Temel kural: hepsi her sorguda devreye alınır.** Primer/ikincil ayrımı artık *aktivasyon kapısı* değil, **sentezde otorite önceliğidir** — çatışmada primer kazanır, ama ikincil/support da **çalıştırılır** ve sonucu kapsam manifestosuna girer. Bir server'ın atlanması yalnız iki halde meşrudur: (a) o server için anahtar yok (SessionStart preflight işaretledi), (b) mod için mantıksal olarak N/A — **her iki hal de manifestoda gerekçesiyle beyan edilir** (sessiz atlama = G0 FAIL).

- **TR primer mevzuat:** `mcp__mevzuat__*` — yapısal yasama-grafı (madde_tree, madde_diff as_of, timeline, ilga_zinciri, relations, gerekçe locator). **İkincil (her sorguda çapraz-kontrol):** `mcp__mevzuat-bilgisi__*` — kanun-NUMARASI lookup + bedesten ikinci korpus.
  - **DEVRALMA KURALI (v3.5.4 — zorunlu).** `mcp__mevzuat__*` **düşükse** (upstream TLS/erişim arızası, origin timeout, boş `items` + dolu `diagnostics`), Türk mevzuatı yükünü `mcp__mevzuat-bilgisi__*` **devralır** — çıktı durmaz. Üç koşul birlikte zorunludur: (a) manifestoda `mevzuat → degraded: <teşhis>` **ve** `mevzuat-bilgisi → hit N (fallback devraldı)`; (b) yedekten gelen her atıf `source: mevzuat_bilgisi_mcp (fallback)` etiketi + birincil-doğrulama açığı notu taşır; (c) birincil ayağa kalkınca **çapraz-doğrulanır**. **Yedek EŞDEĞER DEĞİLDİR:** bedesten kanun-NUMARASIYLA arar (mevzuat.gov.tr araçları kelime-tabanlıdır), AND/OR/NOT desteklemez (`+terim1 +terim2`), ve **`resolve_resmi_gazete` karşılığı YOKTUR** — RG çapa çözümlemesi yalnız birincildedir, bu boşluk yedekle KAPANMAZ (kapatılamıyorsa `manual_required`). **İkisi de düşükse Türk mevzuatı iddiası ÜRETME.** Kayıt: `source_registry.yaml → mcp.mevzuat_bilgisi`.
- **Resmî metin/yürürlük:** `mcp__resmi-gazete__*`. **İkincil mevzuat/soft-law:** `mcp__saglikbakanligi__*`. **İlaç/cihaz reg:** `mcp__titck__*`. **Yasama tarihçesi:** `mcp__tbmm__*`. **Kurumsal atıf:** `mcp__detsis__*`.
- **Karşılaştırmalı:** `mcp__health-policy__*` (yabancı ülke resmî-metin — US/CA/JP/AU/ES/IE/CN/MX), `mcp__german-law__*` (DE/AB), `mcp__ich-guidelines__*`, `mcp__intl-treaty__*` (Md.90/5), `mcp__eudamed__*` (AB cihaz), `mcp__oecd__*` (RIA nicel).
  - **Doğal-dil giriş kapısı (health-policy semantik arama):** yabancı sağlık-hukuku için önce `mcp__health-policy__semantic_search` (Türkçe/İngilizce serbest soru → çok-dilli planner native sorgu üretir [JP için Japonca vb.], aranabilir portallarda **US/JP/AU/CN** fan-out + bge-m3 rerank ile soruna göre sıralı sonuç; ID-only yargılar **ES/MX/CA/IE** `excluded_sources`'ta raporlanır → onlar için doğrudan fetch araçlarına düş). Çıktı `mcp_verified:false` + `_caveat` (sezgisel sıralama; yokluk ispat değil). Bir metnin **tam gövdesi/point-in-time hâli** gerekince anahtar-kelime/fetch araçlarına geç (`federal_register_search`, `ecfr_get`, `japan_elaws_fetch`, `australia_legislation_fetch`, `canada_justicelaws_fetch`, `spain_boe_fetch`, `mexico_dof_nota`, `china_law_detail`, `ireland_eisb_fetch`). Semantik arama **keşif**, fetch **doğrulama** katmanıdır.
- **Doktrin (üç katman, üçü de wire'lı):** `mcp__yok-akademik__*` **metadata** (akademisyen profili, yayın listesi, danışmanlık) · `mcp__yoktez__*` **tez tam-metni** (YÖK Ulusal Tez Merkezi; arama + sayfa-sayfa Markdown) · `mcp__literatur__*` **makale tam-metni** (DergiPark; `search_articles` → `pdf_to_html` → `get_article_references`). **v3.5.0 değişikliği:** yoktez artık companion değil, first-class wire'lıdır — dolayısıyla **G7'deki YÖK-Tez atıf doğrulaması kullanıcı aksiyonuna bağlı değildir** (tez no/başlık/yazar `get_yok_tez_thesis_details` ile teyit edilir → uydurma tez atfı deterministik yakalanır). literatur, doktrin katmanının tek *okunabilir* TR kaynağıdır: yok-akademik yalnız künye verir, gerekçede alıntılanabilir metin buradan gelir.
- **Tam-metin şelalesi (yabancı hukuk doktrini — Mod 7/ANALYZE/RIA/OPINE/EX_POST):** `mcp__openathens__*` **Tier 3 lisanslı** (Millet Kütüphanesi/OpenAthens SAML, 309 veritabanı; paywall'lı monograf/hakemli makaleye yasal erişim) → yalnız o denendikten sonra `mcp__annas-reader__*` **Tier 4 son çare**. **Şelale disiplini zorunludur:** openathens'in erişilemez olması annas-reader'ı *otomatik açmaz* — son çare açık gerekçeyle kullanılır ve **YALNIZ ANALİZ içindir** (getirilen tam metin çıktıya gövde olarak kopyalanmaz, yeniden yayımlanmaz; yalnız atıf + damıtılmış bulgu üretir). Bu katman **birincil norm metni değildir** — o health-policy/german-law/Open Law'dadır; buradan gelen yalnız doktrin desteğidir.
- **Companion (dış connector — tam-filonun ZORUNLU üyeleri; bkz. `/lex-connectors`):** Yargı içtihat (`mcp__Yarg__*`), Open Law (UK+EU, `mcp__Open_Law__*`), Ansvar (300+ reg korpus, `mcp__Ansvar__*`), Fedlex Swiss (CH federal hukuk, `mcp__Fedlex_Swiss__*`), Türk Patent (TR sınai mülkiyet, `mcp__T_rk_Patent__*`). Bunlar kararlı self-host URL'si olmadığı için wire EDİLEMEZ; claude.ai connector ayarlarından bağlanır. *(Önek notu: claude.ai connector'larının araç öneki yüzeye göre `mcp__Yarg__*` ya da `mcp__claude_ai_Yarg__*` biçiminde görünebilir — eşleştirmeyi server ADINA göre yap, önek biçimine göre değil; gerekirse ToolSearch ile çöz.)* Bunlar "bağlıysa opsiyonel" DEĞİLDİR — bağlı oldukları her oturumda, bağlam tetiklendiğinde **çağrılmaları zorunludur**, manifesto satırları her çıktıda mevcuttur ve kalite kapılarına bağlanmışlardır:
  - **Yargı ↔ G5:** içtihat zinciri (AYM belirlilik/iptal emsali, Danıştay idari-işlem, Yargıtay) HER modda `mcp__Yarg__*` ile taranır (ANALYZE 7-boyut, gerekçe dayanağı, COMPLY K-2/K-17, OPINE mütalaa, TBMM genel gerekçe). Yargı bağlı değilse **G5 tam PASS olamaz → CONDITIONAL** + kullanıcıya connector'ı bağlaması önerilir.
  - **Open Law ↔ G6:** CELEX/EUR-Lex konsolide doğrulama (`fetch_eurlex`) + UK karşılaştırması (Mod 7) + AB müktesebat uyum satırı. Open Law bağlı değilse CELEX doğrulaması german-law `get_eu_basis`/WebFetch'e degrade eder ve **G6 CONDITIONAL** işaretlenir.
  - **Ansvar ↔ Mod 7 + yatay çerçeveler:** CH/FR/IT/NL/SE/DK/FI/AT/PL + 58-yargı korpusu ve yatay çerçeve/standart sorguları (GDPR/NIS2/veri, `search(jurisdictions=…)` + `get_provision`) Ansvar'a gider. Bu yargılardan biri karşılaştırma kapsamındayken Ansvar atlanamaz; bağlı değilse o yargı satırı `manual_required` + kapsam boşluğu beyanı. **CH istisnası:** İsviçre federal mevzuatının *birincil metni* için bağlıysa **Fedlex Swiss** önceliklidir (aşağıda); Ansvar CH satırında çerçeve/yatay-tarama katmanı olarak kalır — çatışmada resmî portal (Fedlex) kazanır.
  - **Fedlex Swiss ↔ Mod 7 CH satırı:** `mcp__Fedlex_Swiss__*` — İsviçre federal hukuku resmî portalı (SR-numaralı: `search_by_title` → `get_law_text`/`get_article` → `list_amendments`). Karşılaştırma kapsamına **CH** girdiğinde birincil-metin kaynağı (Swissmedic/HMG-ilaç, KVG-sigorta, HFG-araştırma rejimleri); CH-dışı sorgularda satır `skipped: mod için N/A` yazılır. Bağlı değilse CH birincil-metin satırı Ansvar çerçeve-taramasına degrade + `manual_required` (Fedlex portal deep-link).
  - **Türk Patent ↔ IP-boyutlu reform:** `mcp__T_rk_Patent__*` (patent/marka/tasarım arama + detay) — konu sınai-mülkiyet kesişimliyse (ilaç patenti, SPC/veri imtiyazı, patent linkage, biyobenzer lansmanı, 6769 SMK kesişimi) DRAFT/RIA/COMPARATIVE'de destek katmanı; IP-boyutsuz sorgularda satır `skipped: mod için N/A` yazılır. Bağlı değilse IP satırı `manual_required` (TÜRKPATENT portal deep-link).

**Nasıl tam-filo tarama yapılır (retrieve-don't-dump ile):** getirimi **≤4 paralel shard**'a böl (§3.5) ve her shard'ı bir distiller alt-ajanına **tek görevde** ver; alt-ajanlar server'ları paralel süpürür, ham çıktıyı kendi bağlamlarında tüketir, ana bağlama yalnız kompakt `retrieval_distillate` zarfı (~15-20 bulgu, her biri identifier/url'li) + **`coverage` bloğu** (her server: hit/empty/degraded/skipped-with-reason) döner. Zarfın bağlayıcı biçimi: `schemas/retrieval_distillate.schema.json` (v1.1) — şemaya uymayan zarf kabul edilmez. Bu, "hepsi çalışsın" ile "bağlamı boğma"yı uzlaştırır: tüm araçlar ateşlenir, ana pencereye yalnız damıtılmış sonuç + kapsam kanıtı gelir. Bir server yoksa/boşsa → **veri boşluğu** olarak işaretle, doldurma; `degrade_and_label` (fetch fallback + `mcp_verified=false`).

## 3.5. Bağlam ekonomisi ve büyük-veri (zorunlu)

Tam-filo, ham hâliyle onlarca büyük belge (tam kanun metni, madde ağacı, RG OCR, yabancı statute, tam gerekçe) üretir. Bunları ana pencerede akıl yürütmek pencereyi taşırır → eksik/tutarsız norm. **Üç-katmanlı ekonomi zorunludur** (tam sözleşme: `shared/context-economy-contract.md`, operasyon: `references/16-baglamyonetimi-ve-buyuk-veri.md`):

- **Tier 0 — Ana pencere (kıt):** yalnız talep · mod planı · G0 manifesto · damıtılmış zarflar · `evidence_ledger` · nihai metin. **Ham araç çıktısı ASLA girmez.**
- **Tier 1 — Distiller alt-ajanları (izole):** `legal-distiller` (S1 TR-çekirdek, S3 doktrin) · `comparative-law-researcher` (S2) · `evidence-synthesizer` (S4 klinik) · `gerekce-drafter` · `compliance-auditor` — ham getirimi kendi pencerelerinde tüketir, kompakt zarf döner. Sharding, tek bir distiller'ın da taşmasını önler.
- **Tier 2 — RAG substratı (`anamnesis`):** büyük tam-metin `ingest_document(doc_id=<kanonik id: mevzuat_no/CELEX/ECLI>)` ile **bir kez** indekslenir → `hybrid_query(queries[])` ile sınırlı, provenance-damgalı **dilim** çekilir. Aynı doc_id iki kez ingest edilmez (**kanonik cache** — belge mod/kapı tekrarında yeniden getirilmez).

**Büyük belge disiplini:** kör getirme yok — önce yapısal navigasyon (`get_mevzuat_madde_tree`/`timeline`/`relations`) ile hedefi lokalize et → yalnız hedef chunk'ı çek (`madde_acikla` / `get_mevzuat_text` `chunk_index`/`start_page`-`end_page`/`max_chars` / `download_mevzuat_document(include_base64=false)`) → tam-metin gerekiyorsa anamnesis'e ingest. **Devre-kesici:** tek çıktı >6KB → PostToolUse hook uyarır, ham işleme; distiller/anamnesis'e yönlen. **Extract-then-evict:** her faz sonu ara getirimleri `evidence_ledger`'a çök, ham izi at. anamnesis anahtarı yoksa → bounded-chunk fallback'e degrade, manifestoda beyan et — asla ham döküm.

## 4. Kalite kapıları (G0-G9)

Her mod **G0-G7'den geçer**; G8/G9 moda bağlıdır. Kriterler `references/06b-compliance-executable-rubric.md` ve `references/09` içindedir.

| Kapı | Ad | PASS kriteri |
|---|---|---|
| **G0** | Tam-filo kapsam (§3) | Wire edilmiş 19 MCP + **5 companion (Yarg/Open_Law/Ansvar/Fedlex_Swiss/Turk_Patent — zorunlu satırlar)** + evidentia (klinik-boyut varsa) + sci-audit **tamamı** ateşlenmiş; her biri kapsam manifestosunda hit/empty/degraded/skipped-with-reason olarak görünür. Companion/plugin `skipped` yalnız gerçek yoklukta meşrudur ve ilgili kapıyı (G5/G6) CONDITIONAL'a düşürür. **Sessiz atlama = FAIL.** |
| **G1** | 5210 şekli uyum (Md.10-22) | Madde başlık formatı, fıkra-bent hiyerarşisi, Md.21 atıf (ses uyumu, sıfırsız tarih), ek/geçici madde kuralları |
| **G2** | 5210 maddi-anayasal uyum (Md.4-9) | Üst-norm uygunluğu, AYM belirlilik, AB müktesebatı, kazanılmış hak, geriye yürümezlik |
| **G3** | Türk hukuk dili (R9, 15-nokta) | Tabaka seçimi, Md.25 kuralları, yabancı sözcük yok, kısa cümle, ses-uyumu ekleri, anti-pattern temiz |
| **G4** | Anti-pattern denetimi | §7 yasak kalıpların hiçbiri yok + `references/09-turk-hukuk-dili-ve-uslubu.md` anti-pattern bölümü (çok-anlamlı terim · anti-pattern toplaması · Md.11 kontrol listesi md.11) temiz. **Sayı iddiası yok:** kapı, kanonik listenin O ANKİ uzunluğuna göre ölçülür — v3.5.5'e kadar "27 kalem" deniyordu ama 27 maddelik numaralı liste hiçbir dosyada yoktu (2026-08-07 denetimi, Ö-7); sayıyı tutturmak için liste uydurmak yerine iddia kaldırıldı. |
| **G5** | İçtihat + doktrin (R13) | AYM/Danıştay/Yargıtay/AİHM/ABAD zinciri (**Yargı companion `mcp__Yarg__*` ile taranmış**) + Türk doktrin **üç wire'lı katmandan** atıflı: yok-akademik (künye) + yoktez (tez tam-metni) + literatur (DergiPark makale tam-metni). Yargı bağlı değil → en fazla CONDITIONAL |
| **G6** | Uluslararası kaynak teyidi (R8/10/11/12) | CELEX konsolide doğrulanmış (**birincil araç: Open Law `fetch_eurlex`**; degrade: german-law `get_eu_basis`→WebFetch + CONDITIONAL); WHO/ICH/PIC/S/IMDRF güncel; ICESCR 12+AAAQ kontrol |
| **G7** | Epistemik dürüstlük | Uydurma kanun/CELEX/AYM/Yargıtay/YÖK-Tez yok; her atıf MCP- veya primer-kaynak-doğrulanmış. **YÖK-Tez atıfları wire'lı `mcp__yoktez__get_yok_tez_thesis_details` ile doğrulanır** (tez no/başlık/yazar) — companion'a bağlı değil, **hard PASS** (v3.5.0). Doğrulanamayan tez atfı `illustrative_placeholder_not_verified` → KULLANILMAZ |
| **G8** | TBMM kapsam (Mod 8) | 5210 Md.1/3 kapsam-dışı notu; İçtüzük Md.74-91 primer; 9-bölüm iskelet tam |
| **G9** | Ex-post kapsam (Mod 9) | 5 OECD kriteri hükme bağlanmış; ex-ante↔ex-post tablo; K-1/2/3 kararı; 14-bölüm iskelet |

**G-Reverse:** evidentia sidecar `reverse_signals` doluysa Executive Summary'de görünür kılınmalı. **R6b eşikleri (Mod 4):** tümü PASS/N-A & CONDITIONAL≤3, FAIL=0 → YAYINA HAZIR; 1 yüksek-risk FAIL → düzeltme zorunlu; FAIL≥2 → kapsamlı revizyon; FAIL≥5 veya K-1/K-17 FAIL → tasarımı yeniden gözden geçir. K-1 (üst-norm) önce test edilir; FAIL ise dur.

## 5. Zorunlu delegasyon — evidentia + sci-audit (bağlam-tetiklemeli)

Bu plugin **bağımsızdır** (ikisi de yokken 9 mod çalışır); ancak bu iki plugin **kuruluysa çağrılmaları opsiyonel DEĞİL, zorunludur** — bağlam tetiklendiğinde atlanmaları **G0 ihlalidir**. Degrade yalnız plugin'in gerçekten kurulu olmadığı durumda meşrudur ("veri boşluğu" işaretiyle, asla uydurmadan) ve manifestoda beyan edilir; SessionStart preflight kurulum durumunu oturum başında işaretler. Tam sözleşme: `shared/composition-contract.md`.

- **Klinik kanıt → evidentia (her klinik-boyutlu sorguda).** Konu ilaç/cihaz/hastalık/tedavi/klinik-çalışma/geri-ödeme içeriyorsa **daima** devrede (DRAFT/ANALYZE/OPINE/RIA/COMPARATIVE/TBMM/EX_POST zorunlu; AMEND/COMPLY koşullu — ama sağlık mevzuatında klinik-boyut ≈ daima vardır). Klinik-sıfır saf idari norm → atla + manifestoda beyan et. **Zenginleştirilmiş sorgu** kur (ham değil): `main_query` (İngilizce) + `explicit_layer_request` + `lex_sanitas_legal_context` (TR referanslar + Anayasa + antlaşmalar) + `requested_sections_priority` + `citation_format:Vancouver` + `epistemic_dual_label:true`. `/evidentia` komutuna veya `evidence-synthesizer` alt-ajanına delege et; dönen sidecar'da **önce `reverse_signals`** oku. Aktarılan her TR referansı `mcp__mevzuat__*`/`mcp__Yarg__*` ile çapraz-doğrula. Kaynakça **asla karıştırma**: 8.1 Türk+uluslararası mevzuat / 8.2 bilimsel (Vancouver) / 8.3 Türk içtihat.
- **Güvenilirlik + dil → sci-audit (her çıktıda).** Üretilen metnin atıflarını `/verify-citations`, istatistik/nicel iddialarını `/check-stats`, halüsinasyon sinyallerini ve Türkçe yazımı `/check-turkish` ile **her çıktıda** denetlet (bu, tam-filo ilkesinin çıktı-QA ayağıdır). sci-audit ekseni bilimsel-yazım odaklıdır; **hukuk dili G3/R9'da lex-sanitas'a aittir** — sci-audit'i tamamlayıcı imla/tutarlılık/atıf-bütünlüğü katmanı olarak kullan, hukuk-dili otoritesi olarak değil.

**Çift epistemik-dürüstlük etiketi** klinik çıktıda zorunludur: klinik kanıtta evidentia, hukuki bağlayıcılıkta lex-sanitas otoritedir. **İnsan denetimi her zaman gereklidir.**

## 6. Scope Guard — kapsam sınırı

**Bağlam karar verir, terim değil.** KAPSAM İÇİ = mevzuat *reformu* (9 mod). YÖNLENDİR:

| Konu | Yönlendir |
|---|---|
| Bireysel SGK ödeme reddi davası · AYM bireysel başvuru (sağlık) · kompasyonel kullanım talebi · hekim malpraktis savunması | `saglik-sigorta` / `onko-erisim` skill'leri |
| Promosyonel materyal denetimi (detail aid, leave-behind, MLR, speaker bureau, CME) | `promo-censor` skill'i |

Şüphede **yönlendir, çıktı üretme**. İçtihat kaynakları reform-**gerekçe** sinyalidir; dava dilekçesi üretimi için DEĞİL.

## 7. Çıktı sözleşmesi — kapsam manifestosu + no-fabrication + confidence_label

- **Kapsam manifestosu (G0, zorunlu — çıktı başında veya sonunda):** tam-filonun kanıtı. Her wire'lı MCP + bağlı companion + evidentia + sci-audit için tek satır: `server → durum (hit N kayıt / empty / degraded / skipped: <gerekçe>)`. Bu blok, "hepsi her sorguda çalıştı" iddiasının doğrulanabilir kanıtıdır; eksik satır = G0 FAIL. Örnek biçim `shared/coverage-manifest.md`'de.
- **No-fabrication (G7):** kanun maddesi, CELEX, AYM/Yargıtay/YÖK-Tez, PMID, NCT, NICE-TA, FDA-Guidance başlığı **asla uydurma**. Her referans MCP- veya primer-kaynak-doğrulanmış (YÖK-Tez atıfları **wire'lı `mcp__yoktez__*`** ile — tez no/başlık/yazar — doğrulanır; bu artık companion'a bağlı değildir). Doğrulanamayan → `illustrative_placeholder_not_verified` etiketle, kullanma. Doğrulanamayan referans varsa → **"MCP üzerinden doğrulanamayan referans"** notu.
- **evidence_ledger:** her somut bilimsel/hukuki iddia → bir `E###` kaydı (kaynak, GRADE, `mcp_verified` bayrağı, desteklenen bölümler, Vancouver atıf). `status=verified` yalnız `mcp_verified=true` ise. Şema: `schemas/evidence_ledger.schema.json`. Kanıt işaretleri `[E1]/[E2]…` sıralı.
- **confidence_label (zorunlu, çıktı sonu):** mod + `combined_confidence` (HIGH/MODERATE/LOW) + `human_review_required:true` + çift öz-beyan (lex-sanitas MCP-erişilemezliği & belirsiz yorumlar; evidentia bilgi-boşlukları & tek-kaynak bulgular) + `scope_disclaimer`. Şema: `schemas/confidence_label.schema.json`.
- **Temiz-kopya doktrini:** nihai metin, süreç gürültüsünden (araç çağrıları, ham getirim) arınmış olmalı.

## 8. Referans haritası (`references/`)

**Efsane:** kapılarda geçen `R##` = `references/##` dosyası (R9 = `09-…`, R6b = `06b-…`, R8/10/11/12 = ilgili numaralı dosyalar).

`00-mod-pipelines` (mod-başına adım-adım) · `01-cerceve-5210` · `02-saglik-mevzuat-haritasi` · `03-atif-teknigi` (Md.21) · `04-madde-yapisi` (Md.10-22) · `05-dea-bef` · `06-compliance-checklist` · `06b-compliance-executable-rubric` (R6b) · `07-mevzuat-mcp-workflow` · `08-uluslararasi-kaynaklar` · `09-turk-hukuk-dili-ve-uslubu` (3 Tabaka + 15-nokta QC) · `10-bm-uluslararasi-saglik-hukuku` · `11-who-derinlemesine-rejim` · `12-gelismis-ulke-rejimleri-derin` · `13-icthat-doktrin-akademik-katman` · `14-medical-research-entegrasyon-katmani` · `14b-medical-research-operational-integration` · `15-programatik-veri-kaynaklari` · `16-baglamyonetimi-ve-buyuk-veri` (bağlam ekonomisi + büyük-veri operasyon protokolü).

> Not: `references/14`/`14b` "medical-research v7.1" adını taşır; canlı entegrasyon hedefi **evidentia plugin** (skill `medical-research`, komut `/evidentia`, alt-ajan `evidence-synthesizer`). İçerik (§×mod matrisi, sidecar şeması, reverse-channel) geçerlidir; yalnız çağrı yüzeyi evidentia'dır.
