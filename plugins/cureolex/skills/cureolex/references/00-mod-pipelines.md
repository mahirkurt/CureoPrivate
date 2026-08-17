# Mod Pipeline'ları — adım-adım + tam-filo server listesi

> **Tam-filo ilkesi:** Aşağıdaki "load-bearing" ve "çapraz-kontrol" ayrımı **öncelik**tir, aktivasyon kapısı değil. Wire edilmiş 22 MCP + bağlı companion'ların **tamamı her sorguda** `legal-distiller` alt-ajanı tarafından süpürülür ve sonucu kapsam manifestosuna girer. Load-bearing = o modda sentezi taşıyan; çapraz-kontrol = doğrulama/tamamlama için ateşlenen ama sonucu manifestoda "empty/N/A" olabilecek server.

**Bağlam-güvenli dağıtım (zorunlu):** tek bir distiller'a 14+ server vermek onun penceresini de taşırabilir. Bu yüzden süpürme **≤4 paralel shard**'a bölünür (bkz. `references/16-baglamyonetimi-ve-buyuk-veri.md` §B + `shared/context-economy-contract.md` §2):

- **S1 — TR çekirdek** (`legal-distiller`): mevzuat · mevzuat-bilgisi · resmi-gazete · saglikbakanligi · titck · tbmm · detsis · **intl-treaty (Md.90/5)**.
- **S2 — Karşılaştırmalı** (`comparative-law-researcher`): health-policy · german-law · eurlex (G6) · fedlex (CH) · uk-legal · ich-guidelines · intl-treaty · eudamed · oecd (+Open_Law UK · Ansvar, bağlıysa).
- **S3 — Doktrin/içtihat** (`legal-distiller`): yok-akademik · Yarg · YokTez · literatur.
- **S4 — Klinik** (evidentia `evidence-synthesizer`): zenginleştirilmiş sorgu.

Her shard'a verilecek görev şablonu:
> "Konu: <T>. Mod: <MOD>. Shard server'larını süpür, tek `retrieval_distillate` (≤15-20 bulgu, her biri identifier/url) + `coverage` (her server hit/empty/degraded/skipped-with-reason) döndür. Büyük metinleri sen tüket (Tier 1); ana pencereye ham döküm verme. TR-mevzuatta primer: kelime + NUMARA lookup (`mevzuat_no` / yalnız-rakam) + `phrase` + `search_within_mevzuat`; gerekçe tam metin `get_mevzuat_gerekce`. **Md.90/5 (S1+S2, atlama yok):** `treaty_status` + `treaty_reservations` (ICESCR IV-3, ICCPR, CEDAW, CRC, CRPD + adlandırılan chapter-IV alias); `coe_treaty_signatories` (Oviedo 164, MEDICRIME 211 — snapshot + `snapshot_age_days` + `mcp_verified:false`); `intl_treaty_info` bir kez. `live_coe:false` = `degraded: snapshot`, skip-without-reason değil. UHRI `tools_used` dışı. Onay/çekince uydurulmaz. **TBMM (S1, atlama yok):** Mod 8/teklif → `tbmm_search_kanun_teklifi` sonra `tbmm_get_kanun_teklifi(sira_no)` (önerge+imza); gerekçe locator `tbmm_search_kanun` (gövde mevzuat); komisyon search/get + `tbmm_list_komisyon_havale`; tutanak search/get — SPA `related_acik_erisim` kütüphane zabıtıdır, canlı Genel Kurul değildir; milletvekili `tbmm_get_milletvekili`; OA `tbmm_list_acik_erisim_collections` + `tbmm_search_acik_erisim(page/year/collection)`. Canlı HP 0.15.0 kesilene kadar phrase/search_within/tam gerekçe production uçta olmayabilir — tool yoksa uydurma. İkincil mevzuat-bilgisi wire'lıysa çapraz; çatışmada primer. Kanonik id'leri not et. Büyük tam-metin gerekiyorsa anamnesis'e ingest önerisi ekle."

Ana pencere 4 zarfı tek G0 manifestosunda birleştirir; ham getirim distiller pencerelerinde kalır (Tier 1). Büyük tam-metin → anamnesis (Tier 2). Detay: `references/16`.

---

## Mod 1 — DRAFT (çekirdek)
**Load-bearing:** mevzuat · resmi-gazete · titck · saglikbakanligi · health-policy · german-law · ich-guidelines · intl-treaty · yok-akademik · Yarg · evidentia.
**11 adım:** (1) alt-alan kapsamı; (2) üst-norm zinciri (`get_anayasa` → dayanak kanun/CBK) **+ Md.90/5:** `treaty_status`/`treaty_reservations` (ICESCR/ICCPR/CEDAW/CRC/CRPD) + `coe_treaty_signatories`(164/211) + `intl_treaty_info` bir kez; (3) yatay semantik tarama (`build_mevzuat_semantic_context`); (4) mülga taraması (`search_mulga_mevzuat`); (5) AB müktesebatı + uluslararası benchmark (≥2 AB üyesi, ICH/PIC/S/IMDRF, WHO, BM/CoE — health-policy + german-law + ich + intl-treaty); (6) içtihat + doktrin (Yarg + yok-akademik — zorunlu); (7) 5210 Md.15 madde sırası iskeleti (Amaç→Kapsam→Dayanak→Tanımlar→Esas→Cezaî→Değiştirilen/Kaldırılan→Geçici→Yürürlük→Yürütme→Ekler); (8) Md.4+10-22+25'e göre yaz; (9) yan belgeler (genel gerekçe, madde gerekçeleri [Md.23 tekrar-yok], karşılaştırma tablo, DEA, BEF); (10) kaynaklı kaynakça (ayrı alt-başlık); (11) R9 15-nokta dil QC. **Klinik ◆:** evidentia §4,5,7,9. **Kapılar:** G0-G7.

## Mod 2 — AMEND (çekirdek)
**Load-bearing:** mevzuat (`get_onceki_metinler` kümülatif) · resmi-gazete · titck · saglikbakanligi. **Çapraz:** health-policy/german-law (mukayeseli değişiklik gerekçesi) · **intl-treaty (Md.90/5 ateş: `treaty_status`/`treaty_reservations` + `coe_treaty_signatories` 164/211 + `intl_treaty_info`)** · evidentia (bilimsel-temel değişikliği ise).
**8 adım:** hedefi çek (`get_mevzuat_detail`+`content`), `get_onceki_metinler` (kümülatif), değişiklik tipini sınıfla (madde-değişikliği Md.19 tırnak-içi / ibare Md.20 / ek madde Md.16 / geçici Md.16 / ilga Md.21/8), çerçeve-madde yapısı (Md.18 eski→yeni), atıf kuralları (Md.21 `1/3/2024` sıfırsız), karşılaştırma cetveli, madde gerekçesi, R9 QC (+ klasik kanunda Tabaka A/B→C geçişi). **Kapılar:** G0-G7.

## Mod 3 — ANALYZE
**Load-bearing:** mevzuat · Yarg · yok-akademik · health-policy/german-law/eudamed (mukayeseli sapma). **Çapraz:** resmi-gazete · saglikbakanligi · intl-treaty · evidentia (klinik).
**8 adım:** hedef + paralel üst-norm zinciri, **7-boyut uyum denetimi** (üst-norm Md.4/a, amaç-içerik Md.4/b, belirlilik Md.4/e+AYM, atıf Md.21, madde yapısı Md.10-16, yükümlülük kanuniliği Md.24, dil Md.25), AB/uluslararası benchmark sapma analizi, **Türk yargı+doktrin filtresi** (AYM/Danıştay 10&13/Yargıtay 11&13/AİHM/ABAD + yok-akademik), iptal-riski değerlendirmesi, mukayeseli zayıflık haritası, rapor. **Kapılar:** G0-G7.

## Mod 4 — COMPLY
**Load-bearing:** mevzuat · (denetlenen metin). **Çapraz:** resmi-gazete · titck · saglikbakanligi · Yarg · health-policy/german-law · **intl-treaty (K-1 Md.90/5: `treaty_status`/`treaty_reservations` + `coe_treaty_signatories` 164/211 + `intl_treaty_info`; onay uydurulmaz)** · evidentia (yeni klinik reform ise).
**Süreç:** `references/06b`'deki **21-nokta R6b rubriği** — her kontrol PASS/FAIL/CONDITIONAL/N/A. K-1 (üst-norm) önce; FAIL → dur (kapsamlı revizyon). Eşikler SKILL §4'te. **Kapılar:** G0-G7 + R6b skor-kartı.

## Mod 5 — OPINE
**Load-bearing:** mevzuat · Yarg · yok-akademik · (görüş veren kurum perspektifi: titck/saglikbakanligi/detsis). **Çapraz:** health-policy/german-law · intl-treaty · oecd · evidentia (klinik).
**7 adım:** taslağı+ekleri oku, arka planda COMPLY, içtihat+doktrin filtresi, görüş-veren kurum perspektifinden değerlendir (TİTCK/SGK-politika/Hazine/AB Başkanlığı/KVKK/TBMM Sağlık Komisyonu — komisyon yüzeyi `tbmm_search_komisyon_raporu`/`tbmm_get_komisyon_raporu` + `tbmm_list_komisyon_havale` query'siz deep-link), EK-1 yapılı görüş üret, karşılaştırma tablosu, Md.7 15-günlük zımni-onay hatırlatması. **Kapılar:** G0-G7.

## Mod 6 — RIA (DEA/BEF)
**Load-bearing:** mevzuat · oecd · health-policy · german-law · eudamed · titck · evidentia (ICER/BIA/MEA). **Çapraz:** resmi-gazete · intl-treaty · Yarg · Ansvar.
**8 adım:** hedefleri netleştir (Md.26), etkilenen aktörleri haritala, yurtiçi benchmark (`list_mevzuat_by_type`), uluslararası benchmark (AB + üye devletler + US eCFR/FedReg via health-policy + Asya-Pasifik + HTA dörtlüsü + OECD.Stat), içtihat+doktrin, maliyet-fayda (uygunsa JCA), risk-belirsizlik senaryoları (iyimser/baz/kötümser), çıktı. **Klinik ◆:** evidentia §14.c ICER, §14.d BIA, §14.e MEA, §14.f SGK. **Kapılar:** G0-G7.

## Mod 7 — COMPARATIVE_LAW
**Load-bearing:** health-policy (US/CA/JP/AU/ES/IE/CN/MX) · german-law (DE/AB) · ich-guidelines · intl-treaty · eudamed · Open_Law (UK+EU) · Ansvar (58-yargı) · Fedlex_Swiss (CH birincil metin) · oecd. **Çapraz:** mevzuat (TR karşı-taraf) · Yarg · evidentia · Turk_Patent (IP kesişimi).
**8 adım:** soruyu netleştir (benchmark/gap/policy/case-law tipi), yargı bölgelerini seç (R12 §9), TR-metin Tabaka tespiti (tarihsel-paralel vs akran-mukayese), yabancı metinleri çek (**programatik: CELLAR/legislation.gov.uk AKN/eCFR/DPD; ECLI tercih**) **+ Md.90/5 ateş:** `treaty_status`/`treaty_reservations` + `coe_treaty_signatories`(Oviedo 164, MEDICRIME 211) + `intl_treaty_info` bir kez (`live_coe:false` beyanlı degrade), mukayese matrisi, gap analizi (usuli/maddi/kurumsal/şeffaflık), politika önerisi (4-boyut uyum + geçiş — tip C için zorunlu), rapor. **Kapılar:** G0-G7 (+ template'in koşullu G8/G9 notu).

## Mod 8 — TBMM_KANUN_TEKLIFI (çekirdek, en üst)
**Load-bearing:** tbmm · mevzuat · resmi-gazete · Yarg · yok-akademik · health-policy/german-law · evidentia (ÇİFT-zorunlu tam §1-20). **Çapraz:** titck · saglikbakanligi · detsis · intl-treaty · oecd · eudamed · Ansvar.
**Dayanak:** Anayasa Md.88 + TBMM İçtüzüğü Md.74-91 (**5210 yalnız referans** — Md.1/3 teklifleri hariç; "5210-uyumlu" DENMEZ). **10 adım (tbmm-mcp 0.2.1 — çağır):** (1) teklif imzaları — `tbmm_search_kanun_teklifi` → `tbmm_get_kanun_teklifi(sira_no)` özet+imza (`onerge`); sponsor `tbmm_get_milletvekili` (güncel dönem); (2) ihtiyacı netleştir; (3) Tabaka tespiti; (4) genel gerekçe (10 alt-başlık) — locator `tbmm_search_kanun`/`kanunlar.durumu`, **gövde** `get_mevzuat_gerekce`; **uluslararası çerçeve:** `treaty_status`/`treaty_reservations` + `coe_treaty_signatories`(164/211) + `intl_treaty_info`; andlaşma↔kanun çatışması → Anayasa md. 90/5 cümlesi, onay uydurulmaz; (5) 6-bölüm teklif metni (tam kanun metni mevzuat-mcp); (6) madde gerekçeleri; (7) İçtüzük Md.81 görüşme-usulü notu — tutanak `tbmm_search_tutanak`/`tbmm_get_tutanak`; SPA ise `related_acik_erisim` kütüphane zabıtıdır, canlı Genel Kurul DEĞİLDİR; (8) komisyon havalesi (esas = Sağlık/Aile/Çalışma ve Sosyal İşler) — `tbmm_search_komisyon_raporu`/`tbmm_get_komisyon_raporu` + `tbmm_list_komisyon_havale` (query'siz deep-link); (9) ekler — tarihsel OA `tbmm_list_acik_erisim_collections` + `tbmm_search_acik_erisim(page/year/collection)`; (10) kalite kapıları. **Kapılar:** tümü + G8.

## Mod 9 — EX_POST_EVALUATION
**Load-bearing:** mevzuat (yürürlük tarihçesi) · resmi-gazete · titck · saglikbakanligi · oecd · Yarg · health-policy (programatik zaman-serisi) · evidentia (§ + `ex_post_metrics`). **Çapraz:** tbmm (`tbmm_search_kanun` locator + tutanak; SPA DSpace zabıt ≠ canlı Genel Kurul) · intl-treaty · eudamed · yok-akademik.
**Süre:** yürürlükten 12-36 ay sonra geriye dönük. **10 adım:** kapsam+dönem+değerlendirme-tipi, ex-ante varsayımları derle (Mod 6 DEA/BEF), gerçek uygulama verisi (ÜTS/MIDAS/MEDULA/RWE/paydaş + programatik zaman-serisi), **5 OECD kriteri** karşısında ölç (Etkililik/Verimlilik/Tutarlılık/İlgililik/AB-değeri), yargısal-denetim derlemesi, paydaş-geri-bildirim haritası, mukayeseli ex-post, bütüncül hüküm → **karar (K-1 Koru / K-2 Revize→AMEND / K-3 Sunset/İlga)**, düzeltici yol haritası, EDR. **Klinik ◆:** evidentia §5,7,13.c,14.d,19 + `ex_post_metrics` zorunlu. **Kapılar:** tümü + G9.

## Mod × server matrisi (üretilmiş — kaynak: `fleet.yaml`)

Bu matris, bir companion/server satırının hangi modda `skipped: mod için N/A` yazılacağını **düzyazıdan değil veriden** belirler.

<!-- GEN:mode-server-matrix BEGIN -->
| Server | DRAFT | AMEND | ANLZ | CMPLY | OPINE | RIA | COMP | TBMM | EXPOST |
|---|---|---|---|---|---|---|---|---|---|
| `mevzuat` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `mevzuat-bilgisi` (secondary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `resmi-gazete` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `titck` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `tbmm` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `saglikbakanligi` (primary) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `detsis` (support) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `health-policy` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `german-law` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ich-guidelines` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `intl-treaty` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `eudamed` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `oecd` (support) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `yok-akademik` (doctrine) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `yoktez` (doctrine) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `literatur` (doctrine) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `openathens` (fulltext) | · | · | ✓ | · | ✓ | ✓ | ✓ | · | ✓ |
| `annas-reader` (fulltext) | · | · | ✓ | · | · | · | ✓ | · | · |
| `eurlex` (comparative) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `fedlex` (comparative) | ✓ | · | · | · | · | ✓ | ✓ | · | · |
| `uk-legal` (comparative) | · | · | ✓ | · | ✓ | · | ✓ | · | · |
| `anamnesis` (substrate) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Yargı** (companion) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Open Law** (companion) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Ansvar** (companion) | · | · | ✓ | · | · | ✓ | ✓ | · | · |

> `✓` = bu modda taranır · `·` = bu modda **mantıksal olarak N/A** → manifestoda `skipped: mod için N/A` yazılır (satır atlanamaz).
<!-- GEN:mode-server-matrix END -->
