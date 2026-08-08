# Lex Sanitas — Kompozisyon Sözleşmesi (evidentia + sci-audit + companion connector'lar — bağlam-tetiklemeli ZORUNLU entegrasyon)

Lex Sanitas **bağımsız** bir plugin'dir: hiçbir dış plugin olmadan da 9 modu çalıştırır. Ancak **kurulu/bağlı olan** komşu plugin ve companion connector'lar için entegrasyon **opsiyonel değildir**: bağlam tetiklendiğinde çağrılmaları **zorunludur**; atlanmaları **G0 ihlalidir**. "Yumuşak" olan tek şey *yokluk hâlidir* — plugin/connector gerçekten kurulu/bağlı değilse zarifçe degrade edilir, bu kapsam manifestosunda (G0) gerekçesiyle beyan edilir ve ilgili kalite kapısı CONDITIONAL'a düşer. Hiçbir degrade uydurmaya yol açmaz. (Plugin'ler ayrı marketplace girişi olarak kalır.)

**Karar kuralı (her sorguda):** (1) SessionStart preflight'ın kurulum/bağlantı işaretlerini oku → (2) bağlam tetikleyicisini değerlendir (aşağıdaki matrisler) → (3) tetiklenen HER kurulu/bağlı katmanı çağır → (4) manifestoya satırını yaz. "Çağırmasam da olur" diye bir durum yoktur; yalnız "tetiklenmedi (gerekçe)" veya "kurulu/bağlı değil" vardır.

## 1. evidentia — klinik kanıt katmanı

**Ne zaman:** konu ilaç/cihaz/hastalık/tedavi/klinik-çalışma/geri-ödeme boyutu içerdiğinde. Sağlık mevzuatında bu **≈ daima** vardır → tam-filo ilkesi gereği her klinik-boyutlu sorguda devrede. Klinik-sıfır saf idari norm (ör. bir kurumun iç işleyiş yönetmeliği) → atla + manifestoda `skipped: saf idari norm — klinik-sıfır` beyan et.

**Mod × zorunluluk:**
- **Zorunlu (◆):** DRAFT · ANALYZE · OPINE · RIA · COMPARATIVE_LAW · TBMM (ÇİFT-zorunlu tam §1-20) · EX_POST (`ex_post_metrics` bloğu zorunlu).
- **Koşullu:** AMEND (bilimsel-temel değişikliği ise) · COMPLY (yeni klinik reform metni ise).

**Nasıl çağrılır:**
1. `/evidentia <zenginleştirilmiş sorgu>` komutu **veya** `evidence-synthesizer` alt-ajanı (ağır fan-out bağlam ekonomisi gerektiğinde).
2. **Zenginleştirilmiş sorgu** kur (ham TR soru DEĞİL):
   ```json
   {
     "main_query": "<İngilizce klinik soru>",
     "explicit_layer_request": ["<istenen zenginleştirme modülleri>"],
     "lex_sanitas_legal_context": {
       "turkish_refs": ["<mevzuat/TİTCK referansları>"],
       "anayasa": ["Md.17", "Md.56", "Md.90/5"],
       "treaties": ["ICESCR Md.12", "Oviedo CETS 164"]
     },
     "requested_sections_priority": {"MANDATORY": ["..."], "RECOMMENDED": ["..."], "OPTIONAL": ["..."]},
     "citation_format": "Vancouver",
     "epistemic_dual_label": true
   }
   ```
3. Dönen **sidecar**'da **önce `reverse_signals`** oku (uncertainty_flags → dipnot; out_of_scope_flags → skill öner; retry_triggers → yeniden çağır; alternative_interpretations → executive summary; confidence_breakdown → çift-dürüstlük raporu).
4. Aktarılan **her TR referansı** `mcp__mevzuat__*` / `mcp__Yarg__*` ile **çapraz-doğrula** (evidentia sidecar `mcp_verified` bayrağı ana otorite değil — lex-sanitas kendi doğrulamasını yapar).
5. Çıktıda evidentia bulgularını `[medical-research, §X.Y, tarih]` etiketiyle işaretle.

**Kaynakça ayrımı (asla karıştırma):** 8.1 Türk+uluslararası mevzuat · 8.2 bilimsel (Vancouver) · 8.3 Türk içtihat.

**Çapraz-kapı eşlemesi (G↔M-G):** G2↔M-G3 · G4↔M-G6 · G5↔M-G2+M-G5 · G6↔M-G1+M-G7 · **G7↔M-G8 (ÇİFT-zorunlu — her plugin kendi limitini raporlar, sonra birleştirilir).**

**evidentia yoksa:** klinik iddialar `unverified` kalır; çıktıda "klinik kanıt katmanı (evidentia) bağlı değil — klinik dayanaklar doğrulanmamıştır" uyarısı + manifestoda `evidentia → skipped: plugin kurulu değil`. Klinik iddia **uydurulmaz**.

## 2. sci-audit — güvenilirlik + dil katmanı

**Ne zaman:** **her lex-sanitas çıktısında** (tam-filo çıktı-QA ayağı). Üretilen metin son hâline geldiğinde.

**Nasıl çağrılır:**
- `/verify-citations <metin>` — atıf-adli (referans bütünlüğü; uydurma/yanlış-atıf/geri-çekilme).
- `/check-stats <metin>` — nicel iddia tutarlılığı (özellikle RIA/DEA/BEF sayıları).
- `/check-turkish <metin>` — Türkçe imla/yazım + halüsinasyon sinyalleri.
- (İsteğe bağlı tam denetim: `/audit <metin>` — yedi-eksen.)

**Rol sınırı (önemli):** sci-audit ekseni **bilimsel-yazım** odaklıdır. **Türk hukuk dili G3/R9'da lex-sanitas'a aittir** (5210 Md.25 + 3 Tabaka + Yılmaz doktrini). sci-audit'i **tamamlayıcı** imla/tutarlılık/atıf-bütünlüğü katmanı olarak kullan — hukuk-dili otoritesi olarak DEĞİL. Çelişki hâlinde lex-sanitas G3 kazanır; sci-audit bulgusu "gözden geçir" sinyali olarak not edilir.

**sci-audit yoksa:** atıf-adli + imla denetimi manuel yapılır (lex-sanitas kendi G3/G7 kapıları zaten çalışır); manifestoda `sci-audit → skipped: plugin kurulu değil`. Çıktı durmaz.

## 3. Companion connector'lar — Yargı · Open Law · Ansvar · Fedlex Swiss · Türk Patent (tam-filonun zorunlu üyeleri)

Bu beşi claude.ai connector'ı olarak bağlanır (`fleet.yaml`/`.mcp.json`'da wire EDİLMEZ — kararlı self-host URL'leri yoktur); **bağlı oldukları her oturumda tam-filonun zorunlu üyeleridir**, manifesto satırları her çıktıda mevcuttur ve kalite kapılarına bağlıdır. `/lex-connectors` durumlarını raporlar. *(Önek notu: connector araç önekleri yüzeye göre `mcp__<Ad>__*` veya `mcp__claude_ai_<Ad>__*` görünebilir — eşleştirmeyi server adına göre yap.)*

| Companion | Araç yüzeyi | Zorunlu tetik (bağlam) | Bağlı kapı | Bağlı değilse |
|---|---|---|---|---|
| **Yargı** | `mcp__Yarg__search_anayasa_unified` · `search_bedesten_unified` · `search_emsal_detailed_decisions` · `get_*_markdown` | İçtihat zinciri gereken HER an: ANALYZE 7-boyut iptal-riski · DRAFT/AMEND gerekçe dayanağı · COMPLY K-2 (AYM belirlilik)/K-17 · OPINE mütalaa · TBMM genel gerekçe · EX_POST yargı-pratiği | **G5** | G5 en fazla CONDITIONAL; kullanıcıya "Yargı connector'ını bağla" önerisi; içtihat iddiası `unverified` etiketli, asla uydurma |
| **Open Law** | `mcp__Open_Law__fetch_eurlex` · `lookup_statute` · `legislation_toc` · `search_caselaw` · `fetch_hudoc` | CELEX/EUR-Lex **konsolide doğrulama** (G6'nın birincil aracı) · Mod 7 UK satırı · AB müktesebat uyum tablosu · AİHM (HUDOC) içtihadı | **G6** | CELEX doğrulaması german-law `get_eu_basis` → WebFetch'e degrade + G6 CONDITIONAL; manifesto beyanı |
| **Ansvar** | `mcp__Ansvar__search(jurisdictions=…)` · `get_provision` · `list_coverage` · `validate_citation` | Mod 7'de CH/FR/IT/NL/SE/DK/FI/AT/PL veya diğer 58-yargı korpusu kapsamındaki ülke satırı · yatay çerçeve/standart (GDPR/NIS2/veri güvenliği) sorguları | Mod 7 kapsam bütünlüğü | O yargı satırı `manual_required` + kapsam-boşluğu beyanı; satır tablodan SİLİNMEZ |
| **Fedlex Swiss** | `mcp__Fedlex_Swiss__search_by_title` · `get_law_text` · `get_article` · `list_amendments` | Mod 7 karşılaştırma kapsamına **CH** girdiğinde İsviçre federal mevzuatının birincil metni (SR-numaralı; HMG/KVG/HFG rejimleri); CH-dışı sorguda satır `skipped: mod için N/A` | CH birincil-metin satırı Ansvar çerçeve-taramasına degrade + `manual_required` (Fedlex portal deep-link) |
| **Türk Patent** | `mcp__turk-patent__search_patents` · `get_patent_details` · `search_trademarks` · `search_designs` | Konu sınai-mülkiyet kesişimliyse: ilaç patenti · SPC/veri imtiyazı · patent linkage · biyobenzer lansmanı · 6769 SMK kesişimi (DRAFT/RIA/COMPARATIVE); IP-boyutsuz sorguda satır `skipped: mod için N/A` | IP-boyutlu satır `manual_required` (TÜRKPATENT portal deep-link) |

> **v3.5.0 — companion'dan wire'a terfi:** `yoktez` artık companion DEĞİL, `fleet.yaml`'de first-class wire'lıdır (`mcp__yoktez__*`, authless). Sonuç: **G7 YÖK-Tez atıf doğrulaması kullanıcının connector bağlamasına bağlı değildir** — tez no/başlık/yazar `get_yok_tez_thesis_details` ile teyit edilir, uydurma tez atfı deterministik yakalanır (hard PASS). Aynı sürümde `literatur` (DergiPark makale tam-metni), `openathens` (Tier 3 lisanslı) ve `annas-reader` (Tier 4 son çare, yalnız analiz) de wire edildi. Şelale disiplini: openathens'in erişilemez olması annas-reader'ı OTOMATİK AÇMAZ.

**Sorumluluk sınırı:** Türkiye içtihadında otorite Yargı'dır; UK+EU resmî metinde Open Law; **CH birincil metinde Fedlex Swiss**; Ansvar çok-yargı *tarama* katmanıdır — çatışmada ülkenin resmî portalı (health-policy/german-law/Open Law/Fedlex) kazanır, Ansvar bulgusu ikincil teyit olarak not edilir.

## 4. Degrade matrisi (özet)

| Durum | Davranış | Manifesto satırı |
|---|---|---|
| evidentia + sci-audit kurulu, 4 companion bağlı | Tam kompozisyon | hepsi `hit`/`empty` (bağlam-dışı companion `skipped: mod için N/A`) |
| evidentia kurulu ama klinik-boyutlu sorguda ÇAĞRILMADI | **G0 FAIL — meşru degrade değil** | Stop hook tamamlatır |
| sci-audit kurulu ama çıktı denetimsiz teslim edildi | **G0 FAIL — meşru degrade değil** | Stop hook tamamlatır |
| yalnız evidentia kurulu | Klinik tam, dil-QA manuel | `sci-audit → skipped: plugin kurulu değil` |
| yalnız sci-audit kurulu | Dil-QA tam, klinik `unverified` uyarısı | `evidentia → skipped: plugin kurulu değil` |
| companion bağlı değil | İlgili kapı CONDITIONAL / satır `manual_required`-degrade + kullanıcıya bağlama önerisi | `Yarg/Open_Law/Ansvar/Fedlex_Swiss/Turk_Patent → skipped: companion bağlı değil ⇒ <kapı/satır etkisi>` |
| ikisi de yok, companion'lar yok | lex-sanitas tek başına (9 mod çalışır; G5/G6 CONDITIONAL) | tümü `skipped` + gerekçe |

**Değişmez:** hiçbir degrade durumu **uydurmaya** yol açmaz. Eksik katman = dürüst `unverified`/`skipped` beyanı, asla fabrikasyon. `skipped` yalnız (a) gerçek yokluk, (b) gerekçeli bağlam-dışılık ile meşrudur — kurulu/bağlı bir katmanın tetiklenmiş bağlamda atlanması her zaman ihlaldir. İnsan denetimi her hâlde zorunludur.

## 5. Paylaşılan büyük-veri substratı (anamnesis)

lex-sanitas ve evidentia **aynı `anamnesis` RAG/GraphRAG substratını** evidence_index olarak paylaşır (bkz. `context-economy-contract.md` Tier 2). İkisi de büyük tam-metni `ingest_document(doc_id=<kanonik id>)` ile indeksler ve `hybrid_query` ile bounded dilim çeker. **doc_id ad-uzayı ayrımı** çakışmayı önler: lex-sanitas hukuk belgelerini `mevzuat:…`/`celex:…`/`ecli:…`/`rg:…` önekleriyle, evidentia bilimsel belgeleri DOI/PMID ile indeksler. Kanonik cache oturum-kapsamlıdır; bir belge bir kez ingest edilir, iki plugin de aynı doc_id'ye query atabilir. anamnesis anahtarı yoksa her iki plugin de kendi bounded-chunk fallback'ine degrade eder.
