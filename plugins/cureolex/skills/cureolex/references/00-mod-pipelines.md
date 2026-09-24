# Mod Pipeline'ları — adım-adım + tam-filo server listesi

> **Tam-filo ilkesi:** Aşağıdaki "load-bearing" ve "çapraz-kontrol" ayrımı **öncelik**tir, aktivasyon kapısı değil. Wire edilmiş 21 MCP + bağlı companion'ların **tamamı her sorguda** `legal-distiller` alt-ajanı tarafından süpürülür ve sonucu kapsam manifestosuna girer. Load-bearing = o modda sentezi taşıyan; çapraz-kontrol = doğrulama/tamamlama için ateşlenen ama sonucu manifestoda "empty/N/A" olabilecek server.

**Bağlam-güvenli dağıtım (zorunlu):** tek bir distiller'a 14+ server vermek onun penceresini de taşırabilir. Bu yüzden süpürme **≤4 paralel shard**'a bölünür (bkz. `references/16-baglamyonetimi-ve-buyuk-veri.md` §B + `shared/context-economy-contract.md` §2):

- **S1 — TR çekirdek** (`legal-distiller`): mevzuat · resmi-gazete · saglikbakanligi · titck · tbmm · detsis · **intl-treaty (Md.90/5)**.
- **S2 — Karşılaştırmalı** (`comparative-law-researcher`): health-policy · german-law · eurlex (G6) · fedlex (CH) · uk-legal · ich-guidelines · intl-treaty · eudamed · oecd (+Open_Law UK · Ansvar, bağlıysa).
- **S3 — Doktrin/içtihat** (`legal-distiller`): yok-akademik · Yarg · YokTez · literatur.
- **S4 — Klinik** (evidentia `evidence-synthesizer`): zenginleştirilmiş sorgu.

Her shard'a verilecek görev şablonu:
> "Konu: <T>. Mod: <MOD>. Shard server'larını **tools_used semantik sırasıyla eksiksiz** süpür (token için kalıcı alt küme bırakma). Tek `retrieval_distillate` (≤15-20 bulgu, identifier/url) + `coverage` (her server hit/empty/degraded/skipped-with-reason). Büyük metinleri sen tüket. **S1:** mevzuat list_types→by_type/search(NUMARA+kelime+`phrase`)→detail→anayasa→semantic_context→mulga→madde_tree/timeline/relations→**search_within_mevzuat**→content→**get_mevzuat_gerekce** (bedesten tam metin; ikincile gövde devretme)→resolve_RG→list_kurumlar; RG rg_info→resolve→search→toc→item→pdf→ocr; sb birimler→kategoriler→belgeler→taslaklar→search→get; TİTCK list_datasets önce (cihaz≠TİTCK); TBMM search_teklif→get(**sira_no**)→locator; DETSİS resolve→kunye→…; **Md.90/5** treaty_status+reservations→coe 164/211→intl_treaty_info→**uhri_search→uhri_fetch_document** (COMPARATIVE/Md.90/ICESCR; yerine geçmez); eurlex browse→search→lookup_celex→…. **S2:** semantic_search→keşif→fetch; german resolve→provision→SONRA EU ailesi (premium case_law çağırma); ich (+M4/M8); eudamed cihaz; oecd GOV_REG+HEA; fedlex search→get_by_sr (+ **RIA:** SR sonrası Vernehmlassung open/search/get — TR DRAFT usulü değil); **uk-legal legislation_search→_get_toc→_get_section**→case/Hansard/bills/votes/committees/OSCOLA (Open Law yalnız çapraz/yedek). Conscious exclude: german premium · ChatGPT search/fetch · ÜTS · fedlex recent+termdat_concept · detsis/yok peripheral — **UHRI ve legislation_* exclude DEĞİL**. S1 S2'yi 'örtmez'."

Ana pencere 4 zarfı tek G0 manifestosunda birleştirir; ham getirim distiller pencerelerinde kalır (Tier 1). Büyük tam-metin → anamnesis (Tier 2). Detay: `references/16`.

---

## Mod 1 — DRAFT (çekirdek)
**Önkoşul (semantik):** belirsiz manzara / "hangi düzey?" sorusu varsa önce Mod 3 ANALYZE distillate'i üret; kör DRAFT yasak.
**Load-bearing:** mevzuat · resmi-gazete · titck · saglikbakanligi · health-policy · german-law · ich-guidelines · intl-treaty · yok-akademik · Yarg · evidentia.
**11 adım:** (0) ANALYZE manzarası hazır değilse kısa landscape distiller; (1) alt-alan kapsamı; (2) üst-norm zinciri (`get_anayasa` → dayanak; primer `phrase`/`search_within`/`get_mevzuat_gerekce`) **+ Md.90/5:** `treaty_status`/`treaty_reservations` → `coe_treaty_signatories`(164/211) → `intl_treaty_info` → **`uhri_search`→`uhri_fetch_document`**; (3) yatay semantik tarama (`build_mevzuat_semantic_context`); (4) mülga (`search_mulga_mevzuat`); (5) AB/uluslararası (≥2 üye + ICH **M4/M8 dosya-yapısıysa** + WHO/BM/CoE — health-policy + german **resolve→EU** + ich + intl-treaty + eurlex G6 + UK `legislation_*`); cihaz→eudamed; (6) içtihat+doktrin (Yarg + yok-akademik + literatur + yoktez); (7) 5210 Md.15 iskelet; (8) Md.4+10-22+25 yaz; (9) yan belgeler (gerekçe Md.23, DEA/BEF, karşılaştırma); (10) kaynakça; (11) R9 dil QC. **Klinik ◆:** evidentia. **Kapılar:** G0-G7.

## Mod 2 — AMEND (çekirdek)
**Load-bearing:** mevzuat (`get_onceki_metinler` kümülatif; `search_within` + `get_mevzuat_gerekce` primer) · resmi-gazete · titck · saglikbakanligi. **Çapraz:** health-policy/german-law (mukayeseli değişiklik gerekçesi) · **intl-treaty (Md.90/5: treaty→coe→info→uhri_*)** · evidentia (bilimsel-temel değişikliği ise).
**8 adım:** hedefi çek (`get_mevzuat_detail`+`search_within`+`content`), `get_onceki_metinler` (kümülatif), değişiklik tipini sınıfla (madde-değişikliği Md.19 tırnak-içi / ibare Md.20 / ek madde Md.16 / geçici Md.16 / ilga Md.21/8), çerçeve-madde yapısı (Md.18 eski→yeni), atıf kuralları (Md.21 `1/3/2024` sıfırsız), karşılaştırma cetveli, madde gerekçesi (`get_mevzuat_gerekce`), R9 QC (+ klasik kanunda Tabaka A/B→C geçişi). **Kapılar:** G0-G7.

## Mod 3 — ANALYZE
**Load-bearing:** mevzuat · Yarg · yok-akademik · health-policy/german-law/eudamed (mukayeseli sapma). **Çapraz:** resmi-gazete · saglikbakanligi · intl-treaty · evidentia (klinik).
**8 adım:** hedef + paralel üst-norm zinciri, **7-boyut uyum denetimi** (üst-norm Md.4/a, amaç-içerik Md.4/b, belirlilik Md.4/e+AYM, atıf Md.21, madde yapısı Md.10-16, yükümlülük kanuniliği Md.24, dil Md.25), AB/uluslararası benchmark sapma analizi, **Türk yargı+doktrin filtresi** (AYM/Danıştay 10&13/Yargıtay 11&13/AİHM/ABAD + yok-akademik), iptal-riski değerlendirmesi, mukayeseli zayıflık haritası, rapor. **Kapılar:** G0-G7.

## Mod 4 — COMPLY
**Load-bearing:** mevzuat · (denetlenen metin). **Çapraz:** resmi-gazete · titck · saglikbakanligi · Yarg · health-policy/german-law · **intl-treaty (K-1 Md.90/5: treaty→coe→info→uhri_*; onay uydurulmaz)** · evidentia (yeni klinik reform ise).
**Süreç:** `references/06b`'deki **21-nokta R6b rubriği** — her kontrol PASS/FAIL/CONDITIONAL/N/A. K-1 (üst-norm) önce; FAIL → dur (kapsamlı revizyon). Eşikler SKILL §4'te. **Kapılar:** G0-G7 + R6b skor-kartı.

## Mod 5 — OPINE
**Load-bearing:** mevzuat · Yarg · yok-akademik · (görüş veren kurum perspektifi: titck/saglikbakanligi/detsis). **Çapraz:** health-policy/german-law · intl-treaty · oecd · evidentia (klinik).
**7 adım:** taslağı+ekleri oku, arka planda COMPLY, içtihat+doktrin filtresi, görüş-veren kurum perspektifinden değerlendir (TİTCK/SGK-politika/Hazine/AB Başkanlığı/KVKK/TBMM Sağlık Komisyonu — komisyon yüzeyi `tbmm_search_komisyon_raporu`/`tbmm_get_komisyon_raporu` + `tbmm_list_komisyon_havale` query'siz deep-link), EK-1 yapılı görüş üret, karşılaştırma tablosu, Md.7 15-günlük zımni-onay hatırlatması. **Kapılar:** G0-G7.

## Mod 6 — RIA (DEA/BEF)
**Load-bearing:** mevzuat · oecd · health-policy · german-law · eudamed · titck · evidentia (ICER/BIA/MEA). **Çapraz:** resmi-gazete · intl-treaty · Yarg · Ansvar · fedlex (CH SR + Vernehmlassung).
**8 adım:** hedefleri netleştir (Md.26) → etkilenen aktörler (detsis) → yurtiçi benchmark (`list_mevzuat_types`→`list_mevzuat_by_type`) → uluslararası (health-policy semantic→fetch; german resolve→EU; eurlex; cihaz→eudamed; **fedlex:** search_laws→get_law_by_sr → **paydaş/alternatif bölümünde** `fedlex_get_open_consultations`→`fedlex_search_consultations`→`fedlex_get_consultation` — CH ön-parlamento manzarası; TR 5210 görüş/DRAFT usulü diye aktarma) → **OECD: get_categories→list/search_dataflows→…→query_data; GOV_REG alias ZORUNLU** + HEA → içtihat+doktrin → maliyet-fayda → risk senaryoları → çıktı. **Klinik ◆:** evidentia ICER/BIA/MEA/SGK. **Kapılar:** G0-G7.

## Mod 7 — COMPARATIVE_LAW
**Load-bearing:** health-policy · german-law · eurlex (G6) · ich-guidelines · intl-treaty · eudamed · uk-legal · fedlex · oecd · Open_Law (UK, bağlıysa) · Ansvar (58-yargı). **Çapraz:** mevzuat · Yarg · evidentia.
**8 adım:** soru tipi → yargı seçimi → TR Tabaka → **semantic_search önce** → yabancı metinler (CELLAR/eCFR; **UK `legislation_search`→`_get_toc`→`_get_section`** (Open Law yalnız çapraz/yedek); german **resolve→EU**; ich **+M4/M8**; cihaz→eudamed not ÜTS; fedlex SR) → **Md.90/5 ateş:** treaty→coe→info→**uhri_search→uhri_fetch_document** → matris → gap → politika → rapor. **Kapılar:** G0-G7 (+ koşullu G8/G9).

## Mod 8 — PARLIAMENTARY_BILL · TR paketinde TBMM_KANUN_TEKLIFI (çekirdek, en üst)
**Load-bearing:** tbmm · mevzuat · resmi-gazete · Yarg · yok-akademik · health-policy/german-law · evidentia (ÇİFT-zorunlu). **Çapraz:** titck · saglikbakanligi · detsis · intl-treaty · oecd · eudamed · Ansvar.
**Dayanak:** Anayasa Md.88 + TBMM İçtüzüğü Md.74-91 (**5210 yalnız referans**). **10 adım:** (1) `tbmm_search_kanun_teklifi`→`tbmm_get_kanun_teklifi(sira_no)`+`tbmm_get_milletvekili`; (2) ihtiyaç; (3) Tabaka; (4) genel gerekçe — locator `tbmm_search_kanun`, **gövde** primer `get_mevzuat_gerekce` (bedesten; ikincile gövde devretme yok); **Md.90/5** treaty→coe→info→uhri_*; (5) 6-bölüm teklif (tam metin mevzuat + `search_within`/`phrase`); (6) madde gerekçeleri; (7) tutanak (DSpace≠canlı GK); (8) komisyon+havale; (9) OA ekler; (10) kapılar. **Kapılar:** tümü + G8.

## Mod 9 — EX_POST_EVALUATION
**Load-bearing:** mevzuat · resmi-gazete · titck · saglikbakanligi · oecd (GOV_REG + HEA) · Yarg · health-policy · evidentia. **Çapraz:** tbmm · intl-treaty · eudamed · yok-akademik.
**10 adım:** kapsam+dönem → ex-ante → uygulama verisi → **5 OECD kriteri** → yargı → paydaş → mukayese → K-1/2/3 → yol haritası → EDR. **Kapılar:** tümü + G9.

---

> **Mod 10–12 (4.0) yargı bölgesinden bağımsızdır.** "Load-bearing S1" = **aktif paketin** `connectors[role=primary_legislation]` bağlayıcısıdır (TR paketinde `mevzuat`; GB'de `uk-legal`; CH'de `fedlex`; DE'de `german-law`). Aşağıdaki sunucu adları TR paketiyle yazılmıştır; başka pakette paketin bağlayıcısı yerine geçer. Her üç mod G10 + G11'den geçer ve `evidence_ledger.home_jurisdiction` ister.

## Mod 10 — REGULATORY_MATURITY (WHO GBT açık analizi)
**Load-bearing:** paket S1 (TR: mevzuat · resmi-gazete · saglikbakanligi · titck) · intl-treaty · oecd · openathens (GBT yöntem literatürü). **Çapraz:** Yarg · eurlex · health-policy · evidentia (erişim/kapasite verisi).
**7 adım:** (1) paket + ürün sınıfı + referans tarihi; (2) GBT çerçevesi yalnız doğrulanmış yapıyla (RS + MA/VL/MC/LI/RI/LT/CT/LR; düzey 1–4, hedef düzey 3) — **gösterge kimliği/metni bellekten yazılmaz**; (3) işlev başına dayanak norm (S1; as-of G10); (4) açık sözlüğü (yetki · usul · yaptırım · şeffaflık · bağımsızlık · kaynak) + "mevzuat dışı" kapasite açıklarının ayrı sütunu; (5) reliance kullanımı → Mod 12'ye köprü; (6) mevzuat yol haritası (paketin norm hiyerarşisiyle); (7) sınırlar: resmî GBT değerlendirmesi değil, düzey ataması yok. **Kapılar:** G0, G2, G5, G6, G7, G10, G11.

## Mod 11 — TRANSPOSITION (aktarım / uyum tablosu)
**Load-bearing:** eurlex (G6: `eurlex_lookup_celex` → `eurlex_get_relations` → `eurlex_get_document`) · paket S1 · intl-treaty (andlaşma kaynağıysa). **Çapraz:** german-law (`get_german_implementations` — üye devlet emsali) · fedlex (CH özerk uyum) · Ansvar (bağlıysa; üye devlet uygulamaları) · Yarg.
**7 adım:** (1) **G11 önce** — kaynak normun ev bölgesindeki rolü (`binding` / `transposition_source` / `comparative_benchmark` / `treaty_obligation`; paketin `gate_params.G11`) deftere; (2) kaynak normun konsolide hâli + değişiklik zinciri (G6 + G10); (3) madde-madde ulusal karşılık (S1, as-of); (4) karşılama sözlüğü: Tam · Kısmi · Yok · Aşan · Uygulanmaz; (5) tanım uyumu (çok dilli pakette her geçerli dil ayrı); (6) açık → öneri (norm düzeyi G2); (7) rol `comparative_benchmark` ise "aktarım yükümlülüğü" dili YASAK. **Kapılar:** G0, G1, G2, G6, G7, G10, G11.

## Mod 12 — RELIANCE_FRAMEWORK (reliance çerçevesi taslağı)
**Load-bearing:** paket S1 · uk-legal / fedlex / eurlex / health-policy (referans otorite mevzuatı — her biri `comparative_benchmark`) · intl-treaty (tanıma → andlaşma). **Çapraz:** Yarg · openathens · evidentia (erişim süresi kanıtı).
**7 adım:** (1) **yetki analizi önce (G2)** — karar yetkisini veren norm reliance'a izin veriyor mu, gereken norm düzeyi; (2) reliance ↔ tanıma ayrımı (tanıma = andlaşma/anlaşma); (3) referans otorite **ölçütleri** (liste uydurulmaz; kullanıcıdan veya künyeli belgeden); (4) 9 maddelik iskelet — "ulusal karar yetkisinin korunması" atlanamaz; (5) gerekçe (kamu sağlığı kanıtı + egemenlik + karşılaştırmalı emsal G11 rolüyle); (6) risk tablosu; (7) geçiş hükümleri — pakette `coverage_gap` ise beyan. **Kapılar:** G0, G1, G2, G5, G6, G7, G10, G11.

## Mod × server matrisi (üretilmiş — kaynak: `fleet.yaml`)

Bu matris, bir companion/server satırının hangi modda `skipped: mod için N/A` yazılacağını **düzyazıdan değil veriden** belirler.

<!-- GEN:mode-server-matrix BEGIN -->
| Server | DRAFT | AMEND | ANLZ | CMPLY | OPINE | RIA | COMP | TBMM | EXPOST | GBT | TRNSP | RELY |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `mevzuat` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `resmi-gazete` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `titck` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `tbmm` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `saglikbakanligi` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `detsis` (support) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `health-policy` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `german-law` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ich-guidelines` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `intl-treaty` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `eudamed` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `oecd` (support) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `yok-akademik` (doctrine) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `yoktez` (doctrine) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `literatur` (doctrine) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `openathens` (fulltext) | · | · | ✓ | · | ✓ | ✓ | ✓ | · | ✓ | ✓ | · | ✓ |
| `annas-reader` (fulltext) | · | · | ✓ | · | · | · | ✓ | · | · | · | · | · |
| `eurlex` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `fedlex` (comparative) | ✓ | · | · | · | · | ✓ | ✓ | · | · | · | ✓ | ✓ |
| `uk-legal` (comparative) | · | · | ✓ | · | ✓ | · | ✓ | · | · | · | · | ✓ |
| `anamnesis` (substrate) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Yargı** (companion) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Open Law** (companion) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Ansvar** (companion) | · | · | ✓ | · | · | ✓ | ✓ | · | · | · | ✓ | · |

> `✓` = bu modda taranır · `·` = bu modda **mantıksal olarak N/A** → manifestoda `skipped: mod için N/A` yazılır (satır atlanamaz).
<!-- GEN:mode-server-matrix END -->
