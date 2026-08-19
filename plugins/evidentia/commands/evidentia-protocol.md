---
description: PRISMA protokol + arama stratejisi yazımı (P0–P1). Bir araştırma sorusunu soru-tipine sınıflar, PICO/PECO + uygunluk kriterleri üretir ve veritabanı-başına MeSH/Emtree arama stratejisini raporlanabilir dizeyle yazar. medical-research P0–P1.
argument-hint: <araştırma sorusu>
---

# /evidentia-protocol — PRISMA Protokol + Arama Stratejisi (P0–P1)

Soru: **$ARGUMENTS**

`medical-research` **P0** (`references/prisma-protocol.md`) ve **P1** (`references/search-strategy.md`)
fazlarını yürüt; `protocol` + `search_strategy` artefaktlarını üret. İnsan-onayına sun.

**P1 sıra bağlayıcı** (`references/execution-map.md`): `openalex_resolve_name` →
`pubmed_lookup_mesh` + `pubmed_search_articles` + `pubmed_europepmc_search` →
`semantic-scholar.search_papers` → Clinical Trials `search_trials` (companion) →
bioRxiv `search_preprints` → Consensus/Paper Search → YÖK Tez. Atlanan MUST/SHOULD
rung = `SKIP-REASON` (sessiz atlama yok). `evidentia-kb.kb_search` P0 booster (SHOULD).
