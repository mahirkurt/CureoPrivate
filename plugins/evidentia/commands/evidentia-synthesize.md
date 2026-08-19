---
description: Graph-temelli derin çıkarım + sentez (P4+P6). Çok kaynaklı tam-metin kanıtı anamnesis'e ingest eder (semantik chunk + bge-m3 + D1 grafiği), ilişki triple'larını çıkarıp grafiğe yazar ve hybrid_query ile context-window'a sığan, provenance-damgalı, çapraz-belge bir kanıt paketinden GRADE-disiplinli sentez üretir. Bağlam-penceresi taşması kaynaklı eksik/tutarsız değerlendirmeyi önler.
argument-hint: <sentez sorusu / konu> [— ingest edilecek DOI'ler veya kaynaklar]
---

# /evidentia-synthesize — Graph-Temelli Derin Çıkarım + Sentez (P4+P6, anamnesis RAG/GraphRAG)

Sentez sorusu / konu: **$ARGUMENTS**

`medical-research` **P4 (çıkarım)** ve **P6 (sentez + GRADE)** fazlarını graph-temelli, bağlam-güvenli
bir kanıt paketiyle yürütür.

> **Ön koşul:** anamnesis self-host Worker deploy edilmiş olmalı (`self-host/anamnesis-mcp/
> BUILD-BRIEF.md`; Vectorize 1024-d + D1). Deploy edilmemişse bu komut **degrade eder**:
> kaynakları getirir, **özetleyerek** (verbatim değil) sentezler ve "anamnesis indeks katmanı
> yok → bağlam-bütünlüğü garanti edilemez" notunu görünür kılar.

Normatif: [`../CONNECTORS.md`](../CONNECTORS.md) (tam-metin zinciri + retrieve-don't-dump),
[`../shared/canonical-cache-contract.md`](../shared/canonical-cache-contract.md) (`evidence_index`).
Flagship: `../skills/medical-research/SKILL.md`.

## Akış (retrieve-don't-dump)

1. **Kaynakları topla.** Soru için P0–P2 akademik tarama + gerekiyorsa `/evidentia-fulltext` ile
   tam metin. Kullanıcı DOI/kaynak verdiyse onları kullan.

2. **İndeksle (ham metin bağlama DÖKÜLMEZ; münhasır çalışma seti).** Her kaynağı **bir kez**
   anamnesis'e ingest et: `ingest_document(text=<tam metin>, collection=evidentia:run:<run_id>,
   doc_id=evrun:<run_id>:<DOI>, title=…, source=…)` → **manifest** döner (dual-write). Aynı önekli
   `doc_id` iki kez ingest edilmez (`evidence_index`).

3. **İlişki çıkar → grafiğe yaz (LLM-in-the-loop).** `semantic_search` veya `hybrid_query` ile
   `collection=evidentia:run:<run_id>`; **sen** (orchestrator) chunk'lardan triple çıkar ve
   `upsert_triples(collection=aynı, [{…, doc_id:"evrun:<run_id>:<DOI>", evidence:"<doc_id::idx>"}])`
   yaz. Kapsamsız hybrid/graph/global search YASAK.

4. **Flagship sorgula.** Çok-yönlü soruyu `queries[]` ile ayır; `hybrid_query(collection=aynı,
   queries=[…])` tek pakette birleştirir. `list_docs(collection=aynı)` seti doğrular.
   Kapsam zayıfsa: daha fazla kaynak ingest et → tekrar sorgula. Graph hop: yalnız
   `graph_neighbors`/`subgraph` **collection veya önekli doc_id ile**.

5. **Sentezle (P6, GRADE-disiplinli).** **YALNIZ** bu koşunun chunk'larından sentez yaz; her
   iddiayı **chunk granülaritesinde** (`doc_id::idx`) atıfla. Çelişen kanıtı işaretle; sonuç-bazlı
   GRADE kesinliği (`references/evidence-grading.md`) ve Summary-of-Findings diline sadık kal.

6. **Temizlik.** P7 bitince veya komut abort olunca SessionEnd / sonraki `/evidentia` kancası
   `forget_collection` tercih eder (yedek: ledger `forget_document`). Elle küresel wipe yok.
   Stop-hook forget yok.

## Sınırlar (dürüst)

- **Paylaşılan korpus yok.** `hybrid_query` / `graph_*` kapsamsız çağrılmaz (hook DENY).
  Global community özeti yok (Microsoft-GraphRAG Leiden katmanı Cloud Run'a ertelendi,
  BUILD-BRIEF §5).
- **Telif:** tam metin yalnız analiz için ingest edilir; chunk'lar sınırlı/provenance'lı; çıktı
  künye + yeniden-ifade + gerekçeli **kısa** alıntı (CC-BY/CC0 değilse verbatim toplu metin yok).
- **No-fabrication:** ingest edilmemiş kaynaktan "hatırlayarak" iddia üretme; her iddia paketteki
  bir chunk'a dayanır. Kapsam yetersizse "VERİ BULUNAMADI" + denenen kaynaklar.
- Klinik karar **üretmez**; kanıt sentezler, belirsizliği işaretler. Devir ana asistana aittir.

## Ne zaman bu komut

Çok kaynaklı, tam-metin yoğun, çapraz-belge ilişki gerektiren **derin** çıkarım+sentezde. Tek makale
özeti veya hızlı sorgu için `/evidentia` yeterli; tam-metin getirme için `/evidentia-fulltext`;
RoB+GRADE değerlendirmesi için `/evidentia-appraise`. Ağır fan-out + bağlam-ekonomisi gerekiyorsa
`evidence-synthesizer` alt-ajanı bu akışı izole bağlamında yürütür.
