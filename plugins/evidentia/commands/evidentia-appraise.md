---
description: Yanlılık riski + GRADE değerlendirmesi (P5–P6). Verilen bir çalışma seti için tasarıma göre RoB2/ROBINS-I/QUADAS-2/Newcastle-Ottawa/PROBAST uygular ve sonuç-bazlı GRADE kesinlik + Summary-of-Findings üretir. medical-research P5–P6.
argument-hint: <çalışma seti — DOI/PMID/NCT listesi veya konu>
---

# /evidentia-appraise — Yanlılık Riski + GRADE (P5–P6)

Çalışma seti: **$ARGUMENTS**

`medical-research` **P5** (`references/risk-of-bias.md`) ve **P6** (`references/evidence-grading.md`)
fazlarını yürüt; `rob_assessments` + `grade_sof` üret. İnsan-onay kapısı bağlayıcıdır.

Playbook (`execution-map.md` P5–P6): yeni keşif sunucusu **yok**. Anamnesis korpusu doluysa
**MUST** `hybrid_query(collection=evidentia:run:<run_id>, queries=[methods, randomisation,
blinding, attrition, outcome])` — RoB/GRADE hücreleri `doc_id::idx` provenance taşır.
Kapsamsız hybrid DENY. Korpus boşsa özetten çıkar + `SKIP-REASON` (tam metin yok).
Epi/regülatuar/terminoloji Worker'ları P5/P6'da **OUT**.
