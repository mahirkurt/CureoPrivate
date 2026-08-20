# canonical-cache-contract.md — evidentia Orkestrasyon Disiplini

> **Normatif.** Süit içindeki skill ve komutların, pahalı/latency'li connector'lardan veriyi
> **tek sefer** çekip **kanonik artefakt** olarak paylaşmasını yönetir. Amaç: çift connector
> sorgusunu, kota tüketimini ve latency yığılmasını engellemek. `CONNECTORS.md` §3 ile birlikte
> okunur.

---

## 1. İlke — Single-Fetch Canonical Artifact

Bir veri parçası **bir kez** çekilir, bir **kanonik artefakta** yazılır, sonraki tüm adımlar
o artefakttan **okur**. Aynı sorgu iki kez yapılmaz. Bu, `medical-research`'ün
"native-MCP-first" merdiveniyle çelişmez — merdiven *hangi kaynaktan* çekileceğini, bu sözleşme
*kaç kez* çekileceğini belirler.

| Kanonik artefakt | Sahibi (ilk çeken) | Okuyanlar |
|---|---|---|
| `evidence_corpus` | İlk akademik tarama (PubMed/EPMC/CT.gov/Consensus) | sentez, KOL, tam-metin, ekseni-özgü adımlar |
| `titck_record` | İlk TİTCK `get_drug`/`search_drugs` | fiyat, biyobenzer, off-label, regülatuar adımlar |
| `regulatory_snapshot` | İlk openfda (self-host) çağrısı (openFDA/ICD-11) | epidemiyoloji, güvenlik, kodlama adımları |
| `terminology_map` | İlk `med-terminologies`/`nlm-rxnorm`/`nih-clinicaltables` | normalizasyon, cross-country eşleme |
| `kol_graph` | İlk OpenAlex/S2/EPMC yazar taraması | KOL haritası, ağ analizi |
| `evidence_index` | İlk anamnesis `ingest_document` — dual-write `collection=evidentia:run:<run_id>` + `doc_id=evrun:<run_id>:<DOI>` (Tier 3 openathens `oa_fetch_fulltext` veya tüketilmiş `oa_fetch_pdf` dosyası · Tier 4 Wiley · Tier 5 annas reader veya tüketilmiş `download_document` dosyası · yüklenen PDF). Kısa-ömürlü resource link değil DOI/MD5 + SHA-256/provenance saklanır. Koşu bitince `forget_collection` — kalıcı kütüphane değil | sentez, tam-metin, scoped `hybrid_query(collection=…)` / önekli `semantic_search` — **ham metin değil, indeks** |
| `working_set_ledger` | PostToolUse `working_set_ledger.py` — P1/P2 search (+ fulltext) sonuçlarından PMID\|DOI\|NCT upsert; yol `.claude/evidentia-run/<run_id>/ledger.json` (+ `hits.jsonl`, `screening_table.jsonl`). **Anamnesis `evidentia-anamnesis-run.json` doc_id ledger'ından ayrı** (münhasırlık bozulmaz). P1: `list_docs` → `reconcile_anamnesis_ledger` (missing_extractions / orphans). P2: `coverage_gate.py` Completeness Gate advisory | Completeness Gate v2 coverage%; P3/P4/P6 status geçişleri; synthesizer `coverage` bloğu (`n_include`/`n_cited`/`n_skipped_reasoned`/`uncovered[]`) |

---

## 2. Connector-Özgü Tek-Sefer Kuralları

- **TİTCK tek-sefer kuralı.** Barcode/ürün çözümü **bir kez** yapılır; sonraki TİTCK
  alt-sorguları (fiyat geçmişi, biyobenzer grup, off-label) çözülen `titck_record`'tan
  ilerler. Aynı ürünü iki kez `search_drugs` ile aramak yasaktır.
- **openfda (self-host, latency-prone).** **Tekil** çağrı (paralel değil) + **1 retry** +
  başarısızsa **skippable** işaretle ve `regulatory_snapshot`'ı kısmî bırak. Asla 2. tam
  deneme yapma; downstream "regülatuar veri kısmî" notuyla devam eder.
- **Tier-K genişletme (×4).** İlk liveness sonrası aynı oturumda yeniden probe edilmez;
  sonuç `terminology_map`'e yazılır.
- **drugddx (self-host, Tier-O canlı).** İlaç çifti normalizasyonu `terminology_map`'ten
  okunur; aynı çift iki kez sorgulanmaz.
- **PopHIVE (Tier-K-epi, US-only · v8.5).** Bir hastalık×yer dilimi **bir kez** çekilir →
  `regulatory_snapshot`'a yazılır; precomputed kanıt **BİREBİR** taşınır (PopHIVE sayıları
  yeniden-türetilMEZ). YALNIZCA ABD — global/Türkiye yük için bu artefakta yazma (belgelenmiş boşluk).
- **anamnesis `evidence_index` (self-host) — retrieve-don't-dump + münhasır scratch.** Tam-metin
  makale/kitap veya büyük araç çıktısı **asla ham olarak bağlama dökülmez** (eşik: fulltext
  ≥3 KB / bulk ≥8 KB → **sentez yasağı**; yalnız ingest + `hybrid_query` / PICO kartı). Dual-write: bir
  belge **bir kez** `ingest_document(collection=evidentia:run:<run_id>, doc_id=evrun:<run_id>:<PMID|DOI>)`
  ile yazılır. Flagship: `hybrid_query(collection=aynı, queries[])`. `semantic_search` collection
  ve/veya önekli `doc_id` / `doc_ids[]` ile de ALLOW. Kapsamsız hybrid/graph/global search
  PreToolUse DENY (canlı unscoped `semantic_search` compat için durur). Aynı önekli `doc_id` iki
  kez ingest edilmez. Varlık/ilişki çıkarımı orchestrator'dadır → `upsert_triples` (collection
  veya her triple.`doc_id` önekli); Worker yalnız depolar. `nodeKey`/`edgeId` collection içerir.
- **`working_set_ledger` (bibliyografik kapsam).** Alanlar: `id`, `title`, `sources[]`,
  `phase_seen`, `status` ∈ {identified\|screened\|included\|extracted\|cited\|skipped},
  `skip_reason`, `anamnesis_doc_id?`, `cited_chunks[]`, `extraction_gap?`. Completeness Gate v2:
  `coverage = cited_or_skipped_with_reason / include_set` (standard floor **0.90**).
  Synthesizer dönüşü: `{n_include, n_cited, n_skipped_reasoned, coverage, uncovered[]}`.
  Anamnesis doc_id ledger ile **birleştirilmez**; `reconcile_anamnesis_ledger` yalnız bağlar (per-hit title; `ebsco_get` LWW; bare DOI/PMID/NCT/`record_id` ↔ `anamnesis_doc_id`).
  **P3 ölçüm (eval-only):** `skills/medical-research/evals/context_economy_synth.py` —
  sentetik 40 makale; doğru ledger kullanımında `skip_silent_rate=0`; coverage_gate
  uncovered ID'leri listeler (`CONTEXT-ECONOMY-P3.md`).
- **anamnesis korpusu KOŞU-İÇİ doldurulur — boş-set guard'ı (D9).** anamnesis kalıcı bir kütüphane
  DEĞİLDİR. `corpus_stats` **küresel gözlemdir**; `docs > 0` bu koşunun çalışma seti demek DEĞİLDİR.
  Çalışma seti = `list_docs(collection=evidentia:run:<run_id>)` / ledger. Öneksiz + koleksiyonsuz
  `semantic_search` PreToolUse'da DENY edilir. 0 hit (doğru collection ile) "kanıt yok" değil
  → ingest et veya RAG adımını atlandı işaretle.
- **Temizlik — `forget_collection` tercih, ledger `forget_document` yedek.** SessionEnd ve yeni
  `/evidentia` kancası bu koşunun koleksiyonunu siler (idempotent). Stop-hook forget YOK.
  Öneksiz / başka koşunun id'si veya koleksiyonu guard'da DENY. Küresel wipe yok.
  `forget_by_prefix` API değildir.
- **RECALL — çok-sorgulu ayrıştırma (v1.6.0 + P1 enforce, "hiçbir detayı atlamama").** Karmaşık/
  çok-yönlü sentezde TEK `query` ile çağırılMAZ (`queries[]` ≥2 zorunlu; PreToolUse advisory).
  Soruyu ayrı **alt-yönlere + eşanlamlı/terminoloji varyantlarına** ayır ve hepsini
  `hybrid_query(collection=evidentia:run:<run_id>, queries:[...])` veya scoped
  `semantic_search`'e geçir. Yalnız bu chunk'lardan sentezle; `doc_id::idx` cite.

---

## 3. Atlama (Skip) Sözleşmesi

Bir connector latency/kota/auth nedeniyle başarısız olursa: (a) **graceful skip**, (b) kanonik
artefaktı **kısmî** işaretle, (c) çıktıda **açıkça not düş** ("openfda stall → regülatuar/epidemiyoloji
katmanı kısmî; denenen: openfda_search[FAERS] · PopHIVE[US]"). Sessiz atlama **yasaktır** — temiz-kopya doktrini
(VIZ/OPS yorum izolasyonu) ihlal edilmez; boşluk görünür kalır.

---

## 4. Süit-İçi Devir

`start` → niyet yönlendirme; `evidentia` komutu → tam araştırma koşumu (kanonik artefaktları
üretir); `evidence-synthesizer` alt-ajanı → ağır fan-out koşumunu izole eder ve **yalnız
damıtılmış kanonik artefaktları** ana bağlama döndürür (ham connector gürültüsü ana pencereye
sızmaz). Bu, bağlam-pencere ekonomisi + temiz-kopya doktriniyle hizalıdır.
