# Lex Sanitas — Kompozisyon Sözleşmesi (evidentia + sci-audit yumuşak delegasyon)

Lex Sanitas **bağımsız** bir plugin'dir: hiçbir dış plugin olmadan da 9 modu çalıştırır. Ancak iki komşu plugin ile **yumuşak delegasyon** (soft delegation) yoluyla birlikte çalışır — **varsa** çağrılır, **yoksa** zarifçe degrade eder ve bunu kapsam manifestosunda (G0) beyan eder. Bu, ekosistemin kanıtlanmış desenidir (üç plugin ayrı marketplace girişi olarak kalır).

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

## 3. Degrade matrisi (özet)

| Durum | Davranış | Manifesto satırı |
|---|---|---|
| evidentia + sci-audit ikisi de kurulu | Tam kompozisyon | `evidentia → hit` · `sci-audit → hit` |
| yalnız evidentia | Klinik tam, dil-QA manuel | `sci-audit → skipped: plugin kurulu değil` |
| yalnız sci-audit | Dil-QA tam, klinik `unverified` uyarısı | `evidentia → skipped: plugin kurulu değil` |
| ikisi de yok | lex-sanitas tek başına (9 mod çalışır) | her ikisi `skipped: plugin kurulu değil` |

**Değişmez:** hiçbir degrade durumu **uydurmaya** yol açmaz. Eksik katman = dürüst `unverified`/`skipped` beyanı, asla fabrikasyon. İnsan denetimi her hâlde zorunludur.

## 4. Paylaşılan büyük-veri substratı (anamnesis)

lex-sanitas ve evidentia **aynı `anamnesis` RAG/GraphRAG substratını** evidence_index olarak paylaşır (bkz. `context-economy-contract.md` Tier 2). İkisi de büyük tam-metni `ingest_document(doc_id=<kanonik id>)` ile indeksler ve `hybrid_query` ile bounded dilim çeker. **doc_id ad-uzayı ayrımı** çakışmayı önler: lex-sanitas hukuk belgelerini `mevzuat:…`/`celex:…`/`ecli:…`/`rg:…` önekleriyle, evidentia bilimsel belgeleri DOI/PMID ile indeksler. Kanonik cache oturum-kapsamlıdır; bir belge bir kez ingest edilir, iki plugin de aynı doc_id'ye query atabilir. anamnesis anahtarı yoksa her iki plugin de kendi bounded-chunk fallback'ine degrade eder.
