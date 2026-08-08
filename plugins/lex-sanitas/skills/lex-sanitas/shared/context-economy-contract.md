# Lex Sanitas — Bağlam Ekonomisi ve Büyük-Veri Sözleşmesi

**Problem:** lex-sanitas **tam-filo** çalışır — 20 kaynak MCP + companion + evidentia her sorguda ateşlenir. Bu, ham hâliyle **onlarca büyük belge** (tam kanun metinleri, madde ağaçları, RG OCR, yabancı statute'lar, tam gerekçeler) üretir; hepsini ana bağlam penceresine dökmek pencereyi taşırır ve **eksik/tutarsız** norm-üretimine yol açar. Bu sözleşme, "hepsi çalışsın" ile "bağlamı boğma"yı uzlaştıran **zorunlu** disiplindir.

**Değişmez:** ana pencere yalnız (a) kullanıcı talebi, (b) mod planı, (c) G0 kapsam manifestosu, (d) damıtılmış zarflar (`retrieval_distillate`), (e) `evidence_ledger`, (f) nihai artefakt tutar. **Ham araç çıktısı ana pencerede ASLA akıl yürütülmez.**

---

## 1. Üç-katmanlı bağlam ekonomisi

| Katman | Ne | Kapasite | Kural |
|---|---|---|---|
| **Tier 0 — Ana pencere** (kıt) | Talep · mod planı · G0 manifesto · damıtılmış zarflar · evidence_ledger · nihai metin | En değerli; korunur | Ham getirim **girmez**. Yalnız ≤~20 bulguluk zarflar + kanonik atıflar. |
| **Tier 1 — Distiller alt-ajanları** (izole) | `legal-distiller` · `comparative-law-researcher` · `gerekce-drafter` · `compliance-auditor` (+ evidentia `evidence-synthesizer`) | Kendi bağlam pencereleri | Ham MCP çıktısını KENDİ penceresinde tüketir; ana pencereye yalnız kompakt zarf + `coverage` döner. |
| **Tier 2 — RAG substratı** (sınırsız, harici) | `anamnesis` (Vectorize RAG + D1 GraphRAG) | Pencere-dışı; kalıcı | Büyük tam-metin buraya **ingest** edilir; ana pencere yalnız sınırlı, provenance-damgalı **dilim** çeker. |

**Akış:** MCP ham çıktı → Tier 1 (distiller) VEYA Tier 2 (anamnesis) → ana pencereye yalnız damıtılmış sonuç. Ham veri hiçbir zaman Tier 0'ı geçmez.

## 2. Tam-filo'yu sharding ile taşımadan çalıştırma

Tek bir `legal-distiller`'a 14+ server vermek onun KENDİ penceresini de taşırabilir. Bu yüzden tam-filo süpürme **≤4 paralel shard**'a bölünür; her shard bağımsız distiller çağrısıdır, her biri kompakt zarf + kısmi `coverage` döner; ana pencere bunları tek G0 manifestosunda birleştirir:

Shard kümeleri **`fleet.yaml`'ın `shard:` alanından türer** — bu tablo onun
düzyazı yansımasıdır, bağımsız bir liste DEĞİLDİR. Sapma olursa doğruluk
kaynağı `fleet.yaml`'dır (`tests/run_suites.py` ve `check_drift` sapmayı yakalar).

| Shard | Server kümesi (fleet.yaml `shard:`) | Distiller |
|---|---|---|
| **S1 — TR çekirdek** | mevzuat · mevzuat-bilgisi · resmi-gazete · titck · tbmm · saglikbakanligi · detsis | `legal-distiller` · `compliance-auditor` · `gerekce-drafter` |
| **S2 — Karşılaştırmalı** | health-policy · german-law · ich-guidelines · intl-treaty · eudamed · oecd (+Open Law · Ansvar · Fedlex Swiss companion) | `comparative-law-researcher` |
| **S3 — Doktrin** | yok-akademik · yoktez · **literatur** (+Yargı · Türk Patent companion) | `legal-distiller` · `gerekce-drafter` |
| **S4 — Tam-metin şelalesi** | **openathens** (Tier 3 lisanslı) → **annas-reader** (Tier 4 son çare) | `comparative-law-researcher` |
| **ALL** | anamnesis (Tier 2 substrat — her shard'da erişilebilir) | tümü |

> **S4 bir KLİNİK shard'ı DEĞİLDİR.** Klinik kanıt bir shard değil bir
> **delegasyondur**: `evidentia` plugin'ine (`evidence-synthesizer`) gider ve
> kendi bağlam penceresinde koşar; `fleet.lock.json`'da `delegations` altında
> durur, `servers` altında değil. v3.5.5'e kadar bu tablo S4'ü "Klinik →
> evidentia" diye etiketliyordu; sonuç olarak `openathens`, `annas-reader` ve
> `literatur` **hiçbir distiller'a atanmamış** görünüyordu (2026-08-07 denetimi,
> Ö-3). Etiket düzeltildi — üçü de artık sahipli.

Shard'lar **paralel** dağıtılır (bağımsız görevler). Böylece tüm server'lar ateşlenir (tam-filo korunur) AMA hiçbir distiller penceresi taşmaz ve ana pencere yalnız 4 kompakt zarf görür.

## 3. Kanonik artefakt cache (bir-kez-getir)

Bir belge (kanun/yönetmelik/CELEX/ECLI/yabancı statute) **kararlı kimliğiyle** (mevzuat_no+tur+tertip · CELEX · ECLI · ELI) bir kez getirildiğinde, oturum-kapsamlı kanonik cache'e yazılır (distillate + varsa anamnesis doc_id). Sonraki modlar/kapılar (G1 → G5 → gerekçe → COMPLY) **aynı belgeyi yeniden getirmez**; cache'lenen distillate/ingest'e atıfla çalışır. Bu, 9-mod × G0-G9 boyunca aynı 300KB kanun metninin N kez getirilmesini önler.

**Cache anahtarı:** `{kaynak}:{kanonik_id}` (ör. `mevzuat:3960/7/…`, `celex:32007R1394`, `ecli:ECLI:TR:AYM:…`). Cache girişi: `{distillate_ref, anamnesis_doc_id?, as_of, fetched_at}`.

## 4. Chunking ve navigasyon disiplini (büyük belgeyi kör getirme)

Büyük bir belgeyi **asla** kör (`max_chars` limitsiz / tam PDF) getirme. Protokol:

1. **Önce yapısal navigasyon** (hafif): `get_mevzuat_madde_tree` / `get_mevzuat_timeline` / `get_mevzuat_relations` ile hedef maddeyi/bölümü LOKALİZE et.
2. **Yalnız hedef parçayı çek:** `madde_acikla(madde_no)` drill-down · `get_mevzuat_text(start_page,end_page / chunk_index,chunk_size / max_chars)` · `download_mevzuat_document(include_base64=false)` (yalnız URL — bağlam taşması yok).
3. **Tam-metin gerekiyorsa** (karşılaştırma, gerekçe, ex-post trend): Tier 2 anamnesis'e ingest → bounded query. Yabancı hukukta programatik kimlik (CELEX/ECLI/AKN section) + bölüm-düzeyi fetch; tam konsolide metni ana pencereye çekme.
4. **RG OCR / taranmış PDF:** `rg_ocr_submit` → `rg_ocr_result` (async); sonucu > eşik ise anamnesis'e ingest.

## 5. Bağlam bütçesi + devre-kesici

- **Mod-başına yumuşak bütçe:** ana pencerede damıtılmış getirim ≤ ~25-30K karakter. Aşıldıysa → daha agresif damıtma, en eski ham izleri evict et.
- **Devre-kesici (sert):** tek bir araç çıktısı > eşik (PostToolUse `retrieve_dont_dump` hook 6KB'de tetikler) → o çıktı **ham işlenmez**; zorunlu olarak distiller/anamnesis'e yönlenir.
- **Aşamalı özetleme (extract-then-evict):** her mod fazından sonra ara getirimleri kompakt `evidence_ledger` kayıtlarına çök, ham izi evict et. Bir sonraki faz yalnız ledger'ı görür.
- **Companion/anahtar-yok degrade:** anamnesis anahtarı yoksa → §4 bounded-chunk fetch'e degrade (madde_tree navigasyonu + `max_chars`), asla ham tam-metin dökümü. Manifestoda `anamnesis → skipped: anahtar yok (bounded-chunk fallback)`.

## 6. evidence_index (anamnesis) çağrı disiplini

```
# Büyük belge geldi (> eşik):
anamnesis.ingest_document(doc_id="mevzuat:3960/7", text=<tam metin>, metadata={tur, rg, as_of})
# Sınırlı, çok-sorgulu getirim (ana pencereye yalnız bunlar gelir):
anamnesis.hybrid_query(doc_scope="mevzuat:3960/7", queries=["organ nakli tanım", "yaptırım hükmü", "yürürlük"])
# İlişki grafiği (madde↔dayanak↔ilga):
anamnesis.graph_neighbors(node="madde:5", rel="dayanak")
```

Aynı `doc_id` iki kez ingest edilmez (kanonik cache §3). Getirim daima provenance-damgalı (doc_id + madde/sayfa) döner → `evidence_ledger` `E###` kaydına bağlanır.

## 7. Özet — beş değişmez

1. **Ham veri Tier 0'ı geçmez** — distiller (Tier 1) veya anamnesis (Tier 2) üzerinden.
2. **Tam-filo sharding ile** — ≤4 paralel distiller, her biri bounded zarf.
3. **Bir-kez-getir** — kanonik cache, mod/kapı tekrarında yeniden getirme yok.
4. **Kör getirme yok** — yapısal navigasyon → hedef chunk → gerekirse anamnesis.
5. **Devre-kesici + evict** — büyük çıktı zorunlu damıtılır; faz sonu ham iz atılır.

Hepsi **fail-safe**: bir katman yoksa (anamnesis anahtarı yok, companion bağlı değil) daha düşük katmana degrade eder ve manifestoda beyan eder — asla ham döküm, asla uydurma.
