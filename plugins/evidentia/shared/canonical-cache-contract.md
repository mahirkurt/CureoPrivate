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
| `regulatory_snapshot` | İlk RegulatoryMCP çağrısı (openFDA/ICD-11/WHO GHO) | epidemiyoloji, güvenlik, kodlama adımları |
| `terminology_map` | İlk `med-terminologies`/`nlm-rxnorm`/`nih-clinicaltables` | normalizasyon, cross-country eşleme |
| `kol_graph` | İlk OpenAlex/S2/EPMC yazar taraması | KOL haritası, ağ analizi |
| `evidence_index` | İlk anamnesis `ingest_document` (tam-metin/büyük çıktı indekslemesi) | sentez, tam-metin, `hybrid_query` çeken tüm adımlar — **ham metin değil, indeks** |

---

## 2. Connector-Özgü Tek-Sefer Kuralları

- **TİTCK tek-sefer kuralı.** Barcode/ürün çözümü **bir kez** yapılır; sonraki TİTCK
  alt-sorguları (fiyat geçmişi, biyobenzer grup, off-label) çözülen `titck_record`'tan
  ilerler. Aynı ürünü iki kez `search_drugs` ile aramak yasaktır.
- **RegulatoryMCP (latency-prone 180s).** **Tekil** çağrı (paralel değil) + **1 retry** +
  başarısızsa **skippable** işaretle ve `regulatory_snapshot`'ı kısmî bırak. Asla 2. tam
  deneme yapma; downstream "regülatuar veri kısmî" notuyla devam eder.
- **Tier-K genişletme (×4).** İlk liveness sonrası aynı oturumda yeniden probe edilmez;
  sonuç `terminology_map`'e yazılır.
- **drugddx (self-host, deploy sonrası).** İlaç çifti normalizasyonu `terminology_map`'ten
  okunur; aynı çift iki kez sorgulanmaz.
- **anamnesis `evidence_index` (self-host, deploy sonrası) — retrieve-don't-dump.** Tam-metin
  makale/kitap veya büyük araç çıktısı **asla ham olarak bağlama dökülmez**; bir `doc_id`
  (DOI vb.) **bir kez** `ingest_document` ile indekslenir (semantik chunk + bge-m3 embed +
  D1 grafiği). Sonraki sorgular `semantic_search`/`hybrid_query` ile indeksten **sınırlı,
  provenance-damgalı** dilim çeker — aynı `doc_id` iki kez ingest edilmez. Bu, context-window
  taşması nedeniyle eksik/tutarsız değerlendirmeyi önleyen çekirdek kuraldır. Varlık/ilişki
  **çıkarımı orchestrator (Claude) tarafından** yapılır → `upsert_triples` (LLM-in-the-loop
  GraphRAG); Worker yalnız depolar+gezer.
- **anamnesis korpusu OTURUM-İÇİ doldurulur — boş-korpus guard'ı (D9).** anamnesis kalıcı bir
  korpus DEĞİLDİR; her oturumda `ingest_document` ile doldurulur. `semantic_search`/`hybrid_query`
  çağırmadan ÖNCE **zorunlu `corpus_stats` kontrolü**: `docs == 0` ise önce ilgili tam-metni
  `ingest_document` ile indeksle. Boş korpusta 0 hit dönmesi **bir hata değildir** (RAG substratı
  çalışıyor, içerik yok) → 0 hit'i "kanıt yok" diye raporlama; önce ingest et veya RAG adımını
  atlandı olarak işaretle. (Vectorize indeksleme ~saniye gecikmeli; ingest'ten hemen sonraki
  `semantic_search` geçici 0 dönebilir → kısa bekle/yeniden dene.)

---

## 3. Atlama (Skip) Sözleşmesi

Bir connector latency/kota/auth nedeniyle başarısız olursa: (a) **graceful skip**, (b) kanonik
artefaktı **kısmî** işaretle, (c) çıktıda **açıkça not düş** ("RegulatoryMCP stall → epidemiyoloji
katmanı kısmî; denenen: who_gho_query[TUR]"). Sessiz atlama **yasaktır** — temiz-kopya doktrini
(VIZ/OPS yorum izolasyonu) ihlal edilmez; boşluk görünür kalır.

---

## 4. Süit-İçi Devir

`start` → niyet yönlendirme; `evidentia` komutu → tam araştırma koşumu (kanonik artefaktları
üretir); `evidence-synthesizer` alt-ajanı → ağır fan-out koşumunu izole eder ve **yalnız
damıtılmış kanonik artefaktları** ana bağlama döndürür (ham connector gürültüsü ana pencereye
sızmaz). Bu, bağlam-pencere ekonomisi + temiz-kopya doktriniyle hizalıdır.
