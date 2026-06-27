---
description: Graph-temelli derin sentez. Çok kaynaklı tam-metin kanıtı anamnesis'e ingest eder (semantik chunk + bge-m3 + D1 grafiği), ilişki triple'larını çıkarıp grafiğe yazar ve hybrid_query ile context-window'a sığan, provenance-damgalı, çapraz-belge bir kanıt paketinden sentez üretir. Bağlam-penceresi taşması kaynaklı eksik/tutarsız değerlendirmeyi önler.
argument-hint: <sentez sorusu / konu> [— ingest edilecek DOI'ler veya kaynaklar]
---

# /evidentia-synthesize — Graph-Temelli Derin Sentez (anamnesis RAG/GraphRAG)

Sentez sorusu / konu: **$ARGUMENTS**

> **Ön koşul:** anamnesis self-host Worker deploy edilmiş olmalı (`self-host/anamnesis-mcp/
> BUILD-BRIEF.md`; Vectorize 1024-d + D1). Deploy edilmemişse bu komut **degrade eder**:
> kaynakları getirir, **özetleyerek** (verbatim değil) sentezler ve "anamnesis indeks katmanı
> yok → bağlam-bütünlüğü garanti edilemez" notunu görünür kılar.

Normatif: [`../CONNECTORS.md`](../CONNECTORS.md) §2-§3 (tam-metin zinciri + retrieve-don't-dump),
[`../shared/canonical-cache-contract.md`](../shared/canonical-cache-contract.md) (`evidence_index`).
Flagship: `../skills/medical-research/SKILL.md`.

## Akış (retrieve-don't-dump)

1. **Kaynakları topla.** Soru için akademik tarama (medical-research Adım 0–2) + gerekiyorsa
   `/evidentia-fulltext` ile tam metin. Kullanıcı DOI/kaynak verdiyse onları kullan.

2. **İndeksle (ham metin bağlama DÖKÜLMEZ).** Her kaynağı **bir kez** anamnesis'e ingest et:
   `ingest_document(text=<tam metin>, doc_id=<DOI/stabil id>, title=…, source=…)` → **manifest**
   döner (chunk sayısı + token tahmini + 160-karakter önizleme). Aynı `doc_id` iki kez ingest
   edilmez (`evidence_index`). Çok uzun girdiler için `max_tokens`/`break_threshold` ayarlanabilir.

3. **İlişki çıkar → grafiğe yaz (LLM-in-the-loop GraphRAG).** Önce `semantic_search` ile ilgili
   chunk'ları çek; **sen** (orchestrator) bu chunk'lardan varlık-ilişki triple'ları çıkar ve
   `upsert_triples([{subject, predicate, object, doc_id, evidence:"<doc_id::idx>"}, …])` ile D1
   grafiğine yaz. Predicate'ler kısa olsun (`inhibits`, `treats`, `associated_with`, `increases`).
   Çıkarımı **Worker yapmaz** — sen yaparsın; kalite buradan gelir.

4. **Hybrid sorgula (çekirdek).** `hybrid_query(query=<soru>, k=8, seed_entities=[<ana
   kavramlar>], hops=1)` → vektör top-k chunk **∪** çapraz-belge graph kenarları **∪** seed-varlık
   genişletmesi = **sınırlı, provenance-damgalı kanıt paketi** (`approx_token_budget` ile bağlam
   ekonomisi). Kapsam zayıfsa: daha fazla kaynak ingest et → tekrar sorgula.

5. **Sentezle.** **YALNIZ** dönen chunk'lar + ilişkilerden sentez yaz; her iddiayı **chunk
   granülaritesinde** (`doc_id::idx`) atıfla. Çelişen kanıtı işaretle; GRADE/kanıt-kalitesi
   diline sadık kal (medical-research çıktı sözleşmesi). Graf, çok-hop akıl yürütmeyi (ör.
   ilaç → hedef → yolak → endikasyon) **tutarlı** kılar: aynı ilişkiler her sorguda döner.

## Sınırlar (dürüst)

- **Global community özeti yok** (Microsoft-GraphRAG Leiden katmanı Cloud Run'a ertelendi,
  BUILD-BRIEF §5). Bu komut **yerel** (entity-merkezli) graph + vektör hibridi yürütür.
- **Telif:** tam metin yalnız analiz için ingest edilir; chunk'lar sınırlı/provenance'lı; çıktı
  künye + yeniden-ifade + gerekçeli **kısa** alıntı (CC-BY/CC0 değilse verbatim toplu metin yok).
- **No-fabrication:** ingest edilmemiş kaynaktan "hatırlayarak" iddia üretme; her iddia paketteki
  bir chunk'a dayanır. Kapsam yetersizse "VERİ BULUNAMADI" + denenen kaynaklar.
- Klinik karar **üretmez**; kanıt sentezler, belirsizliği işaretler. SGK/dava→ius-salutis;
  MLR→promo-censor; ticari→pharmaintel devri **ana asistana** aittir.

## Ne zaman bu komut

Çok kaynaklı, tam-metin yoğun, çapraz-belge ilişki gerektiren **derin** sentezde. Tek makale
özeti veya hızlı sorgu için `/evidentia` yeterli; tam-metin getirme için `/evidentia-fulltext`.
Ağır fan-out + bağlam-ekonomisi gerekiyorsa `evidence-synthesizer` alt-ajanı bu akışı izole
bağlamında yürütür.
