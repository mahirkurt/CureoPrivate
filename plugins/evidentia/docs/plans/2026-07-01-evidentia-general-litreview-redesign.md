# evidentia → Genel PRISMA Literatür-İnceleme Aracı — Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** evidentia'yı tedavi-alanı/pazar-istihbaratı motorundan, tüm-tıp genel-amaçlı PRISMA 2020 / PRISMA-ScR sistematik/kapsam derleme aracına yerinde refactor et; hiçbir yeteneği silmeden, tüm domain katmanlarını opsiyonel + bağlam-tetiklemeli zenginleştirme modüllerine çevir.

**Architecture:** `medical-research` skill'inin çekirdeği 10-eksen istihbarat koşumundan P0–P7 PRISMA yaşam döngüsüne yeniden yazılır. Domain katmanları (11 dosya) korunur ama "opsiyonel zenginleştirme modülü"ne yeniden etiketlenir; Adım 0.5 zorunlu eksen-yükleyici → opsiyonel bağlam-sınıflandırıcı olur. `check_integrity.py` deterministik test omurgasıdır ve yeni mimariyi assert edecek şekilde güncellenir.

**Tech Stack:** Markdown skill dosyaları · Python 3 stdlib (`check_integrity.py` integrity gate, PyYAML yok) · JSON (benchmark/eval + `.data.json` sidecar şeması) · YAML (`skill-manifest.yaml`) · plugin.json.

## Global Constraints

- **SKILL.md < 500 satır** (EKLENTİ-GELİŞTİRME-GENEL-TALİMATI §3.2.1 ZORUNLU) — sabit tavan.
- **skill `description` ≤ 1024 karakter**, ne+ne-zaman+tetikleyici içerir (§3.2.2).
- **Tam-nitelikli MCP araç adları** korunur (`Sunucu:arac`), §3.2.4.
- **No-fabrication:** kaynak yoksa "VERİ BULUNAMADI"; iddia-düzeyi Vancouver atıf; uydurma atıf YASAK (§4.3).
- **Hiçbir dosya silinmez.** 11 domain katmanı korunur; yalnız çerçeve/tetikleme dili değişir.
- **Self-host worker kodu değişmez / redeploy yok.** `self-host/*/` dokunulmaz; mevcut `auth.test.ts` yeşil kalmalı.
- **ADR-05:** skill adı `medical-research` korunur.
- **Sürüm:** plugin `2.0.0`, skill `9.0.0`.
- **Repo/dal:** `CureoPrivate`, dal `feat/evidentia-litreview-redesign` (spec bu dalda commit'li).
- **Çalışma dizini:** tüm göreli yollar `CureoPrivate/plugins/evidentia/` köküne göredir. Integrity gate: `cd plugins/evidentia/skills/medical-research && python3 evals/check_integrity.py`.

## Plan konvansiyonu (no-placeholder uyumu)

Bu refactor markdown-ağırlıklıdır. Deterministik artefaktlar (integrity-gate Python'u, `plugin.json`/manifest alanları, benchmark JSON, `description` metni) her adımda **tam** verilir. Nesir referans dosyaları için her görev **kesin bir bölüm-şeması + zorunlu-içerik maddeleri (must-include) + çalıştırılabilir kabul kapısı** verir; nihai nesir bu şemaya göre execution'da yazılır (kabul = ilgili gate yeşil). Bu bir placeholder değil, teslimatın kesin spesifikasyonudur.

## Referans dosya yapısı (kim neyden sorumlu)

**Yeni (6, P-fazları):**
- `references/prisma-protocol.md` — P0: soru-tipi sınıflaması, PICO/PECO, uygunluk kriterleri, derleme tipi.
- `references/search-strategy.md` — P1: MeSH/Emtree eşleme, veritabanı-başına sorgu çevirisi, arama-dizesi raporu.
- `references/screening.md` — P3: başlık/özet + tam-metin tarama, dahil/hariç gerekçe, insan-onay kapısı.
- `references/data-extraction.md` — P4: çalışma-tipine göre çıkarım şablonları, anamnesis-RAG çıkarım akışı.
- `references/risk-of-bias.md` — P5: RoB2/ROBINS-I/QUADAS-2/Newcastle-Ottawa/PROBAST/AMSTAR-2 seçim ve uygulama.
- `references/prisma-reporting.md` — P7: PRISMA 2020 + PRISMA-ScR akış diyagramı + kontrol listesi + SoF tablosu.

**Yeniden yazılan/çerçevelenen:** `SKILL.md` (P0–P7 + opsiyonel sınıflandırıcı) · `references/knowledge-map.md` (modül-indeksi) · `references/connector-registry.md` (roster) · `references/output-templates.md` + `references/report-presentation.md` (SR raporu) · `references/evidence-grading.md` (GRADE+SoF) · `skill-manifest.yaml` · `evals/check_integrity.py` (yeni gate'ler) · `evals/benchmark-queries.json`.

**Yeniden etiketlenen (opsiyonel modül):** `references/{oncology,hematology,immunology,neurology,rare-disease,drug-intelligence,regulatory-intelligence,regulatory-science,hta,medaffairs-ops,turkiye}-layer.md` (bazıları `-layer` bazıları `-intelligence`/`-science` adlı).

**Plugin düzeyi:** `commands/*.md` (5 reframe + 2 yeni) · `agents/evidence-synthesizer.md` · `.claude-plugin/plugin.json` · `README.md` · `docs/EVIDENTIA-CALISMA-SISTEMATIGI.md` · `CONNECTORS.md`.

---

## Task 1: Additive integrity gates (G-SIZE + G-DESC) — test-first backbone

**Files:**
- Modify: `skills/medical-research/evals/check_integrity.py`

**Interfaces:**
- Consumes: existing `_read`, `SKILL_MD`, `GATES`, `_ok/_fail/_warn`.
- Produces: `gate_size()`, `gate_desc()`; new `GATES` entries `"size"`(blocking), `"desc"`(blocking). Constants `SKILL_MAX_LINES=500`, `DESC_MAX_CHARS=1024`, `FORBIDDEN_DESC_TRIGGERS`, `REQUIRED_DESC_TRIGGERS`.

- [ ] **Step 1: Write the gates (they will fail against current content — that is the red test)**

Add near the other `gate_*` functions in `check_integrity.py`:

```python
SKILL_MAX_LINES = 500
DESC_MAX_CHARS = 1024
# therapeutic-area / commercial triggers that must NOT dominate the general description
FORBIDDEN_DESC_TRIGGERS = [
    "CAR-T", "bispecific", "myeloma", "JAK", " MS,", "SMA", "Alzheimer", "ADC",
    "BTK", "MRD", "PDUFA", "biosimilar", "SGK", "SUT", "biyobenzer",
]
# general systematic-review triggers that MUST appear
REQUIRED_DESC_TRIGGERS = ["systematic", "PRISMA", "PICO"]


def _skill_description() -> str:
    """Extract the YAML frontmatter `description:` block value from SKILL.md."""
    text = _read(SKILL_MD)
    m = re.search(r"^description:\s*>?\s*\n((?:[ \t]+.*\n)+)", text, re.MULTILINE)
    if m:
        return " ".join(l.strip() for l in m.group(1).splitlines())
    m2 = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    return m2.group(1).strip() if m2 else ""


def gate_size() -> bool:
    """G-SIZE: SKILL.md body < 500 lines (Talimatname §3.2.1)."""
    print("G-SIZE  SKILL.md line budget")
    n = len(_read(SKILL_MD).splitlines())
    if n < SKILL_MAX_LINES:
        _ok(f"SKILL.md {n} lines (< {SKILL_MAX_LINES})")
        return True
    _fail(f"SKILL.md {n} lines (>= {SKILL_MAX_LINES}) — split into references/")
    return False


def gate_desc() -> bool:
    """G-DESC: description <=1024 chars, general PRISMA triggers present, no
    therapeutic-area/commercial trigger domination (de-skew invariant)."""
    print("G-DESC  skill description hygiene (de-skew)")
    desc = _skill_description()
    ok = True
    if not desc:
        _fail("no description: block parsed from SKILL.md frontmatter")
        return False
    if len(desc) <= DESC_MAX_CHARS:
        _ok(f"description {len(desc)} chars (<= {DESC_MAX_CHARS})")
    else:
        _fail(f"description {len(desc)} chars (> {DESC_MAX_CHARS})")
        ok = False
    missing = [t for t in REQUIRED_DESC_TRIGGERS if t.lower() not in desc.lower()]
    if missing:
        _fail(f"description missing required general trigger(s): {', '.join(missing)}")
        ok = False
    else:
        _ok(f"required general triggers present: {', '.join(REQUIRED_DESC_TRIGGERS)}")
    leaked = [t for t in FORBIDDEN_DESC_TRIGGERS if t.lower() in desc.lower()]
    if leaked:
        _fail(f"therapeutic-area/commercial trigger(s) dominate description: {', '.join(leaked)}")
        ok = False
    else:
        _ok("no therapeutic-area/commercial trigger domination")
    return ok
```

Register in the `GATES` dict (add two entries):

```python
GATES = {
    "refs": ("G-REF", gate_refs, True),
    "always-load": ("G-ALWAYS", gate_always_load, True),
    "connectors": ("G-CONN", gate_connectors, True),
    "version": ("G-VERSION", gate_version, False),
    "coverage": ("G-COVERAGE", gate_coverage, True),
    "probe": ("G-PROBE", gate_probe, True),
    "xval": ("G-XVAL", gate_xval, True),
    "whitelist": ("G-WHITELIST", gate_whitelist, True),
    "size": ("G-SIZE", gate_size, True),
    "desc": ("G-DESC", gate_desc, True),
}
```

- [ ] **Step 2: Run the new gates to verify they FAIL against current content**

Run: `cd skills/medical-research && python3 evals/check_integrity.py --size --desc`
Expected: FAIL — `G-SIZE` reports ≥507 lines; `G-DESC` reports missing `systematic/PRISMA/PICO` + leaked `CAR-T/myeloma/JAK/...`.

- [ ] **Step 3: Commit the gate scaffolding (red gates are intentional — they define the target)**

```bash
git add skills/medical-research/evals/check_integrity.py
git commit -m "test(evidentia): add G-SIZE + G-DESC integrity gates (de-skew, <500-line target)"
```

---

## Task 2: `prisma-protocol.md` (P0)

**Files:**
- Create: `skills/medical-research/references/prisma-protocol.md`
- Modify: `skills/medical-research/references/knowledge-map.md` (add forward-map entry)

**Interfaces:**
- Produces: reference file cited by SKILL.md P0; forward-map entry so G-COVERAGE(1) passes.

- [ ] **Step 1: Author `prisma-protocol.md` to this exact section schema (must-include)**

Sections + must-include content:
1. **Soru-tipi sınıflaması** — tedavi / tanı (diagnostic accuracy) / prognoz / etiyoloji-zarar / önleme / kapsam(scoping); her tip için uygun çalışma tasarımı hiyerarşisi (ör. tedavi→RKÇ; tanı→cross-sectional accuracy; prognoz→kohort).
2. **PICO/PECO/PICOTS** şablonu — Population, Intervention/Exposure, Comparator, Outcome (primary/secondary), Timeframe, Setting; kapsam derlemesi için PCC (Population-Concept-Context).
3. **Uygunluk kriterleri** — dahil/hariç matrisi (tasarım, popülasyon, dil, yıl, yayın tipi); önceden-belirtme zorunluluğu.
4. **Derleme tipi seçimi** — sistematik / kapsam(scoping, PRISMA-ScR) / hızlı(rapid); her birinin farkı ve ne zaman.
5. **Protokol çıktısı** — makine-okur `protocol` bloğu (PICO alanları + eligibility + review_type) → `.data.json` `eligibility_criteria` alanına beslenir; no-fabrication notu.
6. **Sonraki faz** — P1 `search-strategy.md`'ye devir.

- [ ] **Step 2: Add the forward-map entry to `knowledge-map.md`**

Under `## Forward Map`, add:

```markdown
### prisma-protocol.md  — [PHASE P0]
- Sections: §1 Soru-tipi sınıflaması, §2 PICO/PECO/PICOTS, §3 Uygunluk kriterleri, §4 Derleme tipi (sistematik/kapsam/hızlı), §5 Protokol çıktısı, §6 P1 devir
- Concepts: PICO, PECO, PCC, eligibility criteria, question type (therapy/diagnosis/prognosis/etiology/prevention), scoping review, PRISMA-ScR, protocol pre-specification
- Synonyms: protokol, soru çerçevesi, dahil hariç kriterleri, araştırma sorusu, review protocol
- Cross-links: search-strategy.md (P1); screening.md (eligibility → screening); prisma-reporting.md (protocol → checklist)
```

- [ ] **Step 3: Run coverage gate to verify the file is covered**

Run: `cd skills/medical-research && python3 evals/check_integrity.py --coverage`
Expected: `forward-map covers prisma-protocol.md` PASS. (Axis checks may still reference old axes — acceptable until Task 8/9.)

- [ ] **Step 4: Commit**

```bash
git add skills/medical-research/references/prisma-protocol.md skills/medical-research/references/knowledge-map.md
git commit -m "feat(evidentia): add prisma-protocol.md (P0) + knowledge-map entry"
```

---

## Task 3: `search-strategy.md` (P1)

**Files:**
- Create: `skills/medical-research/references/search-strategy.md`
- Modify: `skills/medical-research/references/knowledge-map.md`

**Interfaces:** Consumes P0 `protocol` block. Produces per-database search-strategy artifact for P2 retrieval.

- [ ] **Step 1: Author `search-strategy.md` (must-include)**

1. **Kavram→kontrollü sözcük eşleme** — PICO kavramları → MeSH (PubMed) + Emtree (Embase, native-yoksa dürüst boşluk) + serbest-metin eşanlamlılar; wildcard/truncation.
2. **Boole yapısı** — kavram-içi OR, kavramlar-arası AND; alan etiketleri (`[tiab]`, `[mesh]`).
3. **Veritabanı-başına sorgu çevirisi** — PubMed/EPMC · Europe PMC · ClinicalTrials · OpenAlex · Semantic Scholar · Consensus · bioRxiv/medRxiv · Paper Search · YÖK Tez; her connector için tam-nitelikli araç adı (`Sunucu:arac`) ve sorgu-DSL notu.
4. **Duyarlılık/özgüllük filtreleri** — çalışma-tasarımı filtreleri (RCT/SR); PubMed Clinical Queries eşdeğeri; gri-literatür + kayıt (CT.gov) kapsamı.
5. **Raporlanabilir arama dizesi** — her veritabanı için birebir sorgu + tarih + sonuç-sayısı `search_strategy` artefaktına (`.data.json`) yazılır (PRISMA madde 7).
6. **Sınır dürüstlüğü** — Cochrane/Embase native-API yok → boşluk not edilir; connector toplam-sayı döndürmüyorsa akış-sayısı sınırı P7'de işaretlenir.

- [ ] **Step 2: Add forward-map entry to `knowledge-map.md`**

```markdown
### search-strategy.md  — [PHASE P1]
- Sections: §1 Kavram→MeSH/Emtree eşleme, §2 Boole yapısı, §3 Veritabanı-başına sorgu çevirisi, §4 Duyarlılık/özgüllük filtreleri, §5 Raporlanabilir arama dizesi, §6 Sınır dürüstlüğü
- Concepts: MeSH, Emtree, controlled vocabulary, Boolean, field tags, search filters, sensitivity/precision, grey literature, reproducible search string, PRISMA item 7
- Synonyms: arama stratejisi, sorgu çevirisi, anahtar kelime eşleme, search string, database query
- Cross-links: prisma-protocol.md (PICO→concepts); connector-registry.md (per-database tool names); prisma-reporting.md (search string reporting)
```

- [ ] **Step 3: Run coverage gate** — `python3 evals/check_integrity.py --coverage` → `forward-map covers search-strategy.md` PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/medical-research/references/search-strategy.md skills/medical-research/references/knowledge-map.md
git commit -m "feat(evidentia): add search-strategy.md (P1) + knowledge-map entry"
```

---

## Task 4: `screening.md` (P3)

**Files:** Create `skills/medical-research/references/screening.md`; Modify `knowledge-map.md`.

**Interfaces:** Consumes P2 deduped record set + P0 eligibility. Produces `screening_log` (include/exclude+reason) for P4 + P7 flow counts.

- [ ] **Step 1: Author `screening.md` (must-include)**

1. **İki-aşamalı tarama** — başlık/özet → tam-metin; her aşama uygunluk kriterlerine karşı.
2. **Parti-parti işleme** — kayıtlar N'li partiler hâlinde; her kayıt: `include|exclude|maybe` + **gerekçe** (hariç nedeni PRISMA kategorisiyle: yanlış popülasyon/tasarım/karşılaştırıcı/sonuç/dil).
3. **İnsan-onay kapısı (ZORUNLU)** — tool öneri üretir; nihai dahil/hariç kullanıcı onayıyla kesinleşir (savunulabilir derleme normu); belirsizde `maybe`→tam-metin.
4. **İkili tarama notu** — tekil-eleştirmen sınırı dürüstçe belirtilir (ideali çift-eleştirmen).
5. **Sayı defteri** — `screening_log`: tanımlanan / tekilleştirilen / başlık-özet-taranan / hariç(gerekçe) / tam-metin-değerlendirilen / dahil → P7 PRISMA akışına birebir.

- [ ] **Step 2: Add forward-map entry**

```markdown
### screening.md  — [PHASE P3]
- Sections: §1 İki-aşamalı tarama, §2 Parti-parti include/exclude+gerekçe, §3 İnsan-onay kapısı, §4 İkili tarama notu, §5 Sayı defteri (screening_log)
- Concepts: title/abstract screening, full-text screening, eligibility application, exclusion reasons, human-in-the-loop, dual screening, PRISMA flow counts
- Synonyms: tarama, eleme, dahil hariç, screening, study selection
- Cross-links: prisma-protocol.md (eligibility); data-extraction.md (included → extraction); prisma-reporting.md (flow counts)
```

- [ ] **Step 3: Run coverage gate** → `forward-map covers screening.md` PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/medical-research/references/screening.md skills/medical-research/references/knowledge-map.md
git commit -m "feat(evidentia): add screening.md (P3) + knowledge-map entry"
```

---

## Task 5: `data-extraction.md` (P4)

**Files:** Create `skills/medical-research/references/data-extraction.md`; Modify `knowledge-map.md`.

**Interfaces:** Consumes included studies (P3) + `fulltext-retrieval.md` cascade + anamnesis RAG. Produces `evidence_table` rows for P6/P7.

- [ ] **Step 1: Author `data-extraction.md` (must-include)**

1. **Çıkarım şablonu (çalışma-tipine göre)** — RKÇ / kohort / olgu-kontrol / tanısal-doğruluk / kesitsel; alanlar: künye (yazar/yıl/PMID/DOI/NCT), tasarım, N, popülasyon, müdahale/karşılaştırıcı, sonuç ölçütleri, etki büyüklüğü + %95 GA, izlem, fon/çıkar-çatışması.
2. **Tam-metin akışı** — `fulltext-retrieval.md` merdiveni → anamnesis `ingest_document` → `semantic_search`/`hybrid_query` ile provenance-damgalı dilim (retrieve-don't-dump; ham metin bağlama dökülmez).
3. **Sonuç-bazlı toplama** — her sonuç için çalışmalar-arası satırlar → `evidence_table`; birim/tanım uyumu.
4. **İnsan-onay + doğrulama** — çıkarılan sayısal değerler kaynağa karşı doğrulanır; belirsiz değer "VERİ BULUNAMADI" (uydurma yok).
5. **Sidecar** — `evidence_table` şeması (`.data.json`).

- [ ] **Step 2: Add forward-map entry**

```markdown
### data-extraction.md  — [PHASE P4]
- Sections: §1 Çıkarım şablonu (çalışma-tipine göre), §2 Tam-metin akışı (anamnesis RAG), §3 Sonuç-bazlı toplama, §4 İnsan-onay + doğrulama, §5 evidence_table sidecar
- Concepts: data extraction, evidence table, effect size, 95% CI, study characteristics, full-text retrieval, retrieve-don't-dump, anamnesis ingest, per-outcome aggregation
- Synonyms: veri çıkarımı, kanıt tablosu, ekstraksiyon, data charting, extraction form
- Cross-links: screening.md (included studies); fulltext-retrieval.md (cascade); evidence-grading.md (GRADE input); risk-of-bias.md (per-study RoB); prisma-reporting.md (evidence table)
```

- [ ] **Step 3: Run coverage gate** → `forward-map covers data-extraction.md` PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/medical-research/references/data-extraction.md skills/medical-research/references/knowledge-map.md
git commit -m "feat(evidentia): add data-extraction.md (P4) + knowledge-map entry"
```

---

## Task 6: `risk-of-bias.md` (P5)

**Files:** Create `skills/medical-research/references/risk-of-bias.md`; Modify `knowledge-map.md`.

**Interfaces:** Consumes included studies + design (P4). Produces `rob_assessments` per study for P6/P7.

- [ ] **Step 1: Author `risk-of-bias.md` (must-include)**

1. **Araç seçim matrisi (tasarım→araç)** — RKÇ→**RoB2** (5 alan); randomize-olmayan müdahale→**ROBINS-I** (7 alan); tanısal-doğruluk→**QUADAS-2**; gözlemsel (kohort/olgu-kontrol)→**Newcastle-Ottawa**; tahmin-modeli→**PROBAST**; dahil edilen derlemeler→**AMSTAR-2**.
2. **Her araç için alan-alan sorular + yargı seviyeleri** (low / some concerns / high; NOS için yıldız).
3. **İnsan-onay kapısı (ZORUNLU)** — tool alan-alan taslak yargı üretir; nihai yargı kullanıcı onayıyla.
4. **Özet gösterim** — çalışma×alan RoB ısı-tablosu / trafik-ışığı; `rob_assessments` sidecar.
5. **GRADE'e devir** — RoB, P6 GRADE "risk of bias" düşürme alanını besler.

- [ ] **Step 2: Add forward-map entry**

```markdown
### risk-of-bias.md  — [PHASE P5]
- Sections: §1 Araç seçim matrisi (RoB2/ROBINS-I/QUADAS-2/Newcastle-Ottawa/PROBAST/AMSTAR-2), §2 Alan-alan sorular + yargı, §3 İnsan-onay kapısı, §4 Özet gösterim, §5 GRADE'e devir
- Concepts: risk of bias, RoB2, ROBINS-I, QUADAS-2, Newcastle-Ottawa, PROBAST, AMSTAR-2, traffic-light plot, domain judgement, bias downgrade
- Synonyms: yanlılık riski, önyargı değerlendirmesi, bias assessment, quality appraisal
- Cross-links: data-extraction.md (study design); evidence-grading.md (GRADE bias domain); prisma-reporting.md (RoB summary figure)
```

- [ ] **Step 3: Run coverage gate** → `forward-map covers risk-of-bias.md` PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/medical-research/references/risk-of-bias.md skills/medical-research/references/knowledge-map.md
git commit -m "feat(evidentia): add risk-of-bias.md (P5) + knowledge-map entry"
```

---

## Task 7: `prisma-reporting.md` (P7)

**Files:** Create `skills/medical-research/references/prisma-reporting.md`; Modify `knowledge-map.md`.

**Interfaces:** Consumes screening_log + evidence_table + rob_assessments + grade_sof. Produces the reader-facing PRISMA artifacts.

- [ ] **Step 1: Author `prisma-reporting.md` (must-include)**

1. **PRISMA 2020 akış diyagramı** — kutu-kutu şablon (Identification: kayıt sayısı, kayıt+kayıt-dışı kaynak; Screening: taranan, hariç[gerekçe]; Eligibility: tam-metin, hariç[gerekçe]; Included: dahil) + `screening_log`'dan gerçek sayı; **kapsam-derlemesinde PRISMA-ScR** varyantı.
2. **PRISMA 2020 / PRISMA-ScR kontrol listesi** — 27-madde (SR) / PRISMA-ScR-22 (kapsam) eşleme; her maddenin raporun hangi bölümünde karşılandığı.
3. **Çalışma-özellikleri tablosu** — evidence_table → okur-yüzü tablo.
4. **RoB özet figürü** — rob_assessments → trafik-ışığı.
5. **Summary-of-Findings (GRADE) tablosu** — sonuç × (çalışma/katılımcı sayısı, etki, kesinlik, önem).
6. **Sınır dürüstlüğü** — connector toplam-sayı vermiyorsa akış sayısının sınırı dürüstçe not edilir (no-fabrication).

- [ ] **Step 2: Add forward-map entry**

```markdown
### prisma-reporting.md  — [PHASE P7]
- Sections: §1 PRISMA 2020 akış diyagramı (+PRISMA-ScR), §2 PRISMA/PRISMA-ScR kontrol listesi, §3 Çalışma-özellikleri tablosu, §4 RoB özet figürü, §5 Summary-of-Findings (GRADE) tablosu, §6 Sınır dürüstlüğü
- Concepts: PRISMA 2020, PRISMA-ScR, flow diagram, checklist, study characteristics table, traffic-light plot, Summary of Findings, GRADE certainty, count honesty
- Synonyms: PRISMA akış, akış diyagramı, kontrol listesi, SoF tablosu, reporting standard
- Cross-links: screening.md (flow counts); data-extraction.md (evidence table); risk-of-bias.md (RoB summary); evidence-grading.md (GRADE SoF); output-templates.md (report structure); report-presentation.md (clean copy)
```

- [ ] **Step 3: Run coverage gate** → `forward-map covers prisma-reporting.md` PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/medical-research/references/prisma-reporting.md skills/medical-research/references/knowledge-map.md
git commit -m "feat(evidentia): add prisma-reporting.md (P7) + knowledge-map entry"
```

---

## Task 8: Rewrite `SKILL.md` core → P0–P7 + optional-enrichment classifier

**Files:**
- Modify: `skills/medical-research/SKILL.md` (frontmatter description + Adım 0.5 → optional classifier + Adım 1/3 → P0–P7 + Adım 2/5 preserved-reframed)

**Interfaces:**
- Produces: frontmatter `description` satisfying G-DESC; phase markers `P0`..`P7`; always-load list; `version: 9.0.0`; NO mandatory domain-layer loading in the default path (de-skew invariant).

- [ ] **Step 1: Rewrite the frontmatter `description` (exact text)**

Replace the `description:` block value with:

```yaml
description: >
  General-purpose medical literature review engine. Runs an end-to-end PRISMA 2020 /
  PRISMA-ScR systematic or scoping review across all of medicine and every question type
  (therapy, diagnosis, prognosis, etiology, prevention): protocol + PICO/PECO, search
  strategy (MeSH/Emtree), comprehensive retrieval + dedup, title/abstract + full-text
  screening, data extraction, risk of bias (RoB2/ROBINS-I/QUADAS-2/Newcastle-Ottawa),
  GRADE certainty, and a clean Turkish report with a PRISMA flow diagram + Summary-of-
  Findings table. Optional, context-triggered enrichment modules (therapeutic-area,
  drug/regulatory, HTA, Türkiye market, KOL, epidemiology) load only when the question's
  context calls for them; they never drive the default. Pure structured-authoritative
  evidence; no web/OSINT tier; no fabrication. Use for ANY literature-review, systematic
  review, scoping review, evidence-synthesis, meta-analysis-prep, PICO, or "what does the
  evidence say" request. Triggers: literatür derleme, sistematik derleme, kapsam derleme,
  literature review, systematic review, PRISMA, PICO, PECO, screening, risk of bias,
  GRADE, evidence synthesis, kanıt sentezi, meta-analiz, tarama, dahil hariç kriterleri.
```

Verify length ≤ 1024 chars in Step 4 (G-DESC).

- [ ] **Step 2: Rewrite the body — replace Adım 0.5 (10-Axis) and Adım 1/3 with the P0–P7 spine**

Author the body so it contains, in order (keep it LEAN — detail lives in the phase reference files; target < 400 lines total):

- **Adım 0 — Mandatory Loading:** always-load = `knowledge-map.md`, `connector-registry.md`, `evidence-grading.md`, `output-templates.md`, `report-presentation.md`, `prisma-reporting.md`. (Phase files P0/P1/P3/P4/P5 loaded per-phase = progressive disclosure.)
- **Adım 0.1 — Project Settings** (keep existing `.claude/evidentia.local.md` override logic; replace `default_axis` with `default_modules`).
- **Adım 0.4 — Semantic Scope Scan:** reads `knowledge-map.md` to route the question to PHASE files + OPTIONAL modules (module-index).
- **Adım 0.5 — Optional Enrichment Classifier (NON-mandatory):** a context scan that MAY activate enrichment modules; **the default review path loads NO domain layer.** Explicit statement: "No enrichment module is mandatory or always-on; the core PRISMA pipeline runs regardless."
- **P0–P7 phases:** each = 2–5 lines: what it does + `view references/<file>.md` pointer + human-approval note for P3/P5. (Content lives in the reference files from Tasks 2–7 + evidence-grading for P6.)
- **Adım 2 — Generosity Principle:** preserved (uncapped depth), reframed to "depth across phases."
- **Adım 3 — Output Contract:** replaced by pointer to `output-templates.md` SR structure (Task 13) — no inline §1–21 scaffold.
- **Adım 5 — Clean-Copy Doctrine:** preserved; pointer to `report-presentation.md`.
- **Version History:** add `v9.0.0` line.
- Update frontmatter `version: 9.0.0`.

Keep the Extended-Tier cross-validation recipe block (needed by G-XVAL) but move it under P4/enrichment as "when an optional drug/terminology module fires."

- [ ] **Step 3: Verify line budget + phase markers**

Run: `cd skills/medical-research && python3 evals/check_integrity.py --size --desc`
Expected: `G-SIZE` PASS (< 500 lines); `G-DESC` PASS (≤1024, required triggers present, no leaked triggers).

- [ ] **Step 4: Commit**

```bash
git add skills/medical-research/SKILL.md
git commit -m "feat(evidentia)!: rewrite SKILL.md core to P0-P7 PRISMA pipeline + optional enrichment classifier (skill 9.0.0)"
```

---

## Task 9: Update integrity gates to the new architecture (coverage/phases/always-load) → full gate green

**Files:**
- Modify: `skills/medical-research/evals/check_integrity.py`

**Interfaces:**
- Consumes: SKILL.md P0–P7 (Task 8), new always-load set.
- Produces: `gate_phases()` (`"phases"` blocking); updated `ALWAYS_LOAD`; `gate_coverage` axis-check → phase/module check; `gate_deskew()` (`"deskew"` blocking) asserting no mandatory domain-layer load in the default path.

- [ ] **Step 1: Update `ALWAYS_LOAD` constant**

```python
ALWAYS_LOAD = [
    "knowledge-map.md", "connector-registry.md", "evidence-grading.md",
    "output-templates.md", "report-presentation.md", "prisma-reporting.md",
]
```

- [ ] **Step 2: Replace the axis-id check in `gate_coverage` with a phase/module check**

In `gate_coverage`, replace the block that scans `0\.5\.[A-K]` (check (2)) with:

```python
    # (2) every PRISMA phase marker P0..P7 in SKILL.md appears in the map
    skill_text = _read(SKILL_MD)
    phases = sorted(set(re.findall(r"\bP[0-7]\b", skill_text)))
    for ph in phases:
        if ph in map_text:
            _ok(f"map covers phase {ph}")
        else:
            _fail(f"map omits phase {ph}")
            ok = False
```

- [ ] **Step 3: Add `gate_phases` and `gate_deskew`**

```python
PHASE_FILES = {
    "P0": "prisma-protocol.md", "P1": "search-strategy.md", "P3": "screening.md",
    "P4": "data-extraction.md", "P5": "risk-of-bias.md", "P7": "prisma-reporting.md",
}
DOMAIN_LAYERS = [
    "oncology-layer.md", "hematology-layer.md", "immunology-layer.md",
    "neurology-layer.md", "rare-disease-layer.md", "drug-intelligence-layer.md",
    "regulatory-intelligence.md", "regulatory-science-layer.md", "hta-layer.md",
    "medaffairs-ops-layer.md", "turkiye-layer.md",
]


def gate_phases() -> bool:
    """G-PHASES: SKILL.md declares P0..P7 and points each defined phase at its reference file."""
    print("G-PHASES  PRISMA pipeline phases present")
    skill = _read(SKILL_MD)
    ok = True
    for ph in ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"]:
        if re.search(r"\b" + ph + r"\b", skill):
            _ok(f"phase {ph} declared")
        else:
            _fail(f"phase {ph} missing from SKILL.md")
            ok = False
    for ph, fname in PHASE_FILES.items():
        if fname in skill:
            _ok(f"{ph} points at {fname}")
        else:
            _fail(f"{ph} does not point at {fname}")
            ok = False
    return ok


def gate_deskew() -> bool:
    """G-DESKEW: no domain layer is mandatorily loaded in the default path. Every domain
    layer reference in SKILL.md sits under the optional/enrichment framing, never an
    'always'/'mandatorily loaded' directive."""
    print("G-DESKEW  domain layers are optional (de-skew invariant)")
    skill = _read(SKILL_MD)
    ok = True
    for layer in DOMAIN_LAYERS:
        for m in re.finditer(re.escape(layer), skill):
            # inspect the line containing this mention
            line_start = skill.rfind("\n", 0, m.start()) + 1
            line_end = skill.find("\n", m.start())
            line = skill[line_start: line_end if line_end > 0 else len(skill)].lower()
            if "mandator" in line or "always-load" in line or "always load" in line or "zorunlu" in line:
                _fail(f"{layer} referenced as mandatory/always: '{line.strip()[:80]}'")
                ok = False
    if ok:
        _ok(f"all {len(DOMAIN_LAYERS)} domain layers referenced as optional/enrichment")
    return ok
```

Register in `GATES`:

```python
    "phases": ("G-PHASES", gate_phases, True),
    "deskew": ("G-DESKEW", gate_deskew, True),
```

- [ ] **Step 4: Run the FULL gate**

Run: `cd skills/medical-research && python3 evals/check_integrity.py`
Expected: ALL RUN GATES PASSED (G-REF, G-ALWAYS, G-CONN, G-VERSION, G-COVERAGE, G-PROBE, G-XVAL, G-WHITELIST, G-SIZE, G-DESC, G-PHASES, G-DESKEW). If G-PROBE/G-XVAL/G-WHITELIST fail, they depend on connector-registry (Task 14) — note and proceed; re-run green after Task 14.

- [ ] **Step 5: Commit**

```bash
git add skills/medical-research/evals/check_integrity.py
git commit -m "test(evidentia): retarget integrity gates to P0-P7 (G-PHASES, G-DESKEW, phase coverage, always-load)"
```

---

## Task 10: Relabel the 5 therapeutic-area layers → optional enrichment modules

**Files:**
- Modify: `references/oncology-layer.md`, `references/hematology-layer.md`, `references/immunology-layer.md`, `references/neurology-layer.md`, `references/rare-disease-layer.md`

**Interfaces:** Consumes G-DESKEW (must not read as mandatory). Produces optional-module framing + SR-appendix output pointer.

- [ ] **Step 1: In each of the 5 files, replace the loading header + output pointer**

For each file, change the top line from the axis form:
`**Loaded:** when axis 0.5.X fires. **Adım 1 package:** §1.Y.`
to:
`**Optional enrichment module** — loaded only when the question's context enters {domain}. NOT mandatory; the core PRISMA pipeline runs without it. Output → clearly-labelled enrichment appendix (not the core SR report).`

And change any `## N. Output → §1.F / §9 / §19` (or §1.G etc.) line to:
`## N. Output → enrichment appendix (domain-specific guideline placement / pipeline note), never the core SR sections`

Keep all clinical body content (guideline authorities, appraisal checklists) verbatim.

- [ ] **Step 2: Run de-skew gate**

Run: `cd skills/medical-research && python3 evals/check_integrity.py --deskew --coverage`
Expected: G-DESKEW PASS; G-COVERAGE still covers the 5 files.

- [ ] **Step 3: Commit**

```bash
git add skills/medical-research/references/oncology-layer.md skills/medical-research/references/hematology-layer.md skills/medical-research/references/immunology-layer.md skills/medical-research/references/neurology-layer.md skills/medical-research/references/rare-disease-layer.md
git commit -m "refactor(evidentia): relabel 5 therapeutic-area layers as optional enrichment modules"
```

---

## Task 11: Relabel the 6 cross-cutting layers → optional enrichment modules

**Files:**
- Modify: `references/drug-intelligence-layer.md`, `references/regulatory-intelligence.md`, `references/regulatory-science-layer.md`, `references/hta-layer.md`, `references/medaffairs-ops-layer.md`, `references/turkiye-layer.md`

**Interfaces:** Same optional-module framing as Task 10.

- [ ] **Step 1: In each file, replace mandatory/axis framing with optional-enrichment framing**

Change any "**Loaded:** when …", "mandatorily loaded", "Türkiye Dörtlüsü is mandatory", "zorunlu" directive at the top into:
`**Optional enrichment module** — loaded only when the question's context calls for {drug-intelligence / regulatory / HTA / KOL / Türkiye-market} data. NOT mandatory; the core PRISMA pipeline runs without it. Output → enrichment appendix.`

For `turkiye-layer.md` specifically: remove any "MANDATORY / Türkiye Dörtlüsü zorunlu" language; make TR retrieval a context-triggered appendix (TR-specific question OR user-requested).

Keep the clinical/data body verbatim.

- [ ] **Step 2: Run gates**

Run: `cd skills/medical-research && python3 evals/check_integrity.py --deskew --coverage --xval`
Expected: G-DESKEW PASS; G-COVERAGE covers all 6; G-XVAL still finds the cross-validation recipes (they live in SKILL.md/connector-registry, unaffected).

- [ ] **Step 3: Commit**

```bash
git add skills/medical-research/references/drug-intelligence-layer.md skills/medical-research/references/regulatory-intelligence.md skills/medical-research/references/regulatory-science-layer.md skills/medical-research/references/hta-layer.md skills/medical-research/references/medaffairs-ops-layer.md skills/medical-research/references/turkiye-layer.md
git commit -m "refactor(evidentia): relabel 6 cross-cutting layers as optional enrichment modules"
```

---

## Task 12: Rewrite `knowledge-map.md` header → module-index + PICO/question-type taxonomy

**Files:**
- Modify: `references/knowledge-map.md` (header + SKILL.md entry + the 11 layer entries' `[axis 0.5.X]` tags)

**Interfaces:** Consumes G-COVERAGE (phase check from Task 9). Produces module-index framing (axis tags → module tags) + question-type routing.

- [ ] **Step 1: Rewrite the map header + SKILL.md entry**

Replace the top `> Axis IDs covered: 0.5.A …` line and the SKILL.md forward-map entry's axis-table bullet with:
- Header: `> Adım 0.4 reads this to route the question to PRISMA PHASE files (P0–P7) + OPTIONAL enrichment MODULES by meaning. G-COVERAGE asserts exhaustiveness. Phases covered: P0 P1 P2 P3 P4 P5 P6 P7.`
- Add a **Question-Type → PICO taxonomy** block: therapy→PICO/RCT; diagnosis→PICO(index/reference test)/QUADAS; prognosis→PECO/cohort; etiology→PECO; prevention→PICO; scoping→PCC/PRISMA-ScR.

- [ ] **Step 2: Change the 11 layer entries' tags**

Change each `### <layer>.md  — [axis 0.5.X]` to `### <layer>.md  — [OPTIONAL MODULE: <domain>]` and update their `Cross-links` to reference the phase files where relevant. Keep concepts/synonyms.

- [ ] **Step 3: Run coverage gate (full)**

Run: `cd skills/medical-research && python3 evals/check_integrity.py --coverage`
Expected: PASS — all reference files covered, all phases P0–P7 covered, 0 dangling.

- [ ] **Step 4: Commit**

```bash
git add skills/medical-research/references/knowledge-map.md
git commit -m "refactor(evidentia): knowledge-map → module-index + question-type/PICO taxonomy"
```

---

## Task 13: Rewrite output/presentation/grading to SR-report + PRISMA artifacts

**Files:**
- Modify: `references/output-templates.md` (SR report structure + sidecar schema)
- Modify: `references/report-presentation.md` (clean-copy → SR sections)
- Modify: `references/evidence-grading.md` (GRADE + SoF central; keep Tier hierarchy)

**Interfaces:** Consumes phase artifacts. Produces the reader-facing SR report contract + `.data.json` schema used by Task 18 eval.

- [ ] **Step 1: Replace the §1–21 scaffold in `output-templates.md` with the SR report structure**

Reader-facing SR sections (must-include): ① Arka plan ② Amaç + PICO/PECO + derleme tipi ③ Yöntem (uygunluk · kaynaklar · arama stratejisi · seçim · çıkarım · RoB · sentez · GRADE · veri-kesim) ④ PRISMA akış diyagramı ⑤ Bulgular (çalışma-özellikleri tablosu · RoB özeti · sonuç-bazlı) ⑥ Summary-of-Findings/GRADE tablosu ⑦ Tartışma · kısıtlılıklar · sonuç ⑧ Kaynaklar (Vancouver+PMID/DOI/NCT) + dahil/dışlanan listeler. **Opsiyonel enrichment ekleri** ayrı, işaretli appendix.

Replace the `.data.json` sidecar schema with:
```
prisma_flow_counts · eligibility_criteria · search_strategy · screening_log ·
evidence_table · rob_assessments · grade_sof · enrichment_payloads{therapeutic|drug|
regulatory|hta|turkiye|kol|epidemiology}(only if fired) · sources_summary
```

- [ ] **Step 2: Update `report-presentation.md` scaffold→clean-copy mapping**

Replace the §1–21 heading map with the ①–⑧ SR heading map. Keep the six binding clean-copy principles + VIZ/OPS comment isolation + the finalization gate (repurpose "finalization gate" to include a PRISMA-checklist completeness pass).

- [ ] **Step 3: Make GRADE + SoF central in `evidence-grading.md`**

Keep §1 Tier hierarchy + §2 GRADE. Add/strengthen: per-outcome GRADE domains (RoB, inconsistency, indirectness, imprecision, publication bias) explicitly fed by `risk-of-bias.md`; add a **Summary-of-Findings table spec** consumed by `prisma-reporting.md`.

- [ ] **Step 4: Run gates**

Run: `cd skills/medical-research && python3 evals/check_integrity.py --refs --coverage`
Expected: PASS (files still cited + covered).

- [ ] **Step 5: Commit**

```bash
git add skills/medical-research/references/output-templates.md skills/medical-research/references/report-presentation.md skills/medical-research/references/evidence-grading.md
git commit -m "refactor(evidentia): output/presentation/grading → SR report + PRISMA + SoF"
```

---

## Task 14: Reframe connector roster (bibliographic-core primary; domain optional)

**Files:**
- Modify: `references/connector-registry.md` (roster tiers + §8 Probe Log + §2.6 whitelist preserved)
- Modify: `CONNECTORS.md` (§1 tiers, §2 ladders → PRISMA phases, §7 scope note)

**Interfaces:** Consumes G-CONN/G-PROBE/G-XVAL/G-WHITELIST. Produces reframed roster where bibliographic core is primary and domain connectors are optional-module-gated.

- [ ] **Step 1: Reframe `connector-registry.md`**

- Promote a **Bibliographic Core** tier (PubMed/EPMC, Europe PMC, OpenAlex, Semantic Scholar, Consensus, ClinicalTrials, bioRxiv/medRxiv, Paper Search, YÖK Tez) + full-text (annas-reader, Unpaywall) + RAG (anamnesis, evidentia-kb) as the always-on retrieval set.
- Mark TİTCK/Mevzuat/TÜRKPATENT, openFDA/ICD-11, AdisInsight/ChEMBL/GtoPdb, PopHIVE, med-terminologies/RxNorm/nih-clinicaltables, drugddx, NPI/YÖK-Akademik as **optional (enrichment-module-gated)**.
- **Preserve** §8 Probe Log WIRE rows for `med-terminologies, nih-clinicaltables, nlm-rxnorm, iuphar-gtopdb, drugddx, PopHIVE` (G-PROBE) and the §2.6 whitelist without pipeworx-generic tools (G-WHITELIST) and the Extended-Tier cross-validation cues (G-XVAL).

- [ ] **Step 2: Reframe `CONNECTORS.md`**

- §1 tiers: bibliographic-core primary; domain optional. §2 resolution ladders re-expressed per PRISMA phase (P1 search / P2 retrieval / P4 full-text). §7 scope note: reinforce that optional TR/regulatory/drug modules are evidence-context enrichment, NOT commercial intelligence (commercial → pharmaintel, etc.).

- [ ] **Step 3: Run the connector-dependent gates**

Run: `cd skills/medical-research && python3 evals/check_integrity.py --connectors --probe --xval --whitelist`
Expected: ALL PASS (core connectors resolve; WIRE rows present; cross-validation cues present; no pipeworx-generic leak).

- [ ] **Step 4: Commit**

```bash
git add skills/medical-research/references/connector-registry.md CONNECTORS.md
git commit -m "refactor(evidentia): reframe roster — bibliographic core primary, domain connectors optional"
```

---

## Task 15: Update `skill-manifest.yaml` (version, description, tags, always_load, classification)

**Files:**
- Modify: `skills/medical-research/skill-manifest.yaml`

**Interfaces:** Consumes G-VERSION, G-ALWAYS. Produces manifest agreeing with SKILL.md (version 9.0.0, always_load).

- [ ] **Step 1: Update identity + classification + always_load**

- `skill.version: "9.0.0"`; `skill.title: "General Medical Literature-Review Engine (PRISMA)"`; rewrite `skill.description` to the PRISMA identity (systematic/scoping review, all-of-medicine, optional enrichment).
- `classification.primary_category: "medical-evidence-synthesis"`; `secondary_categories: ["systematic-review", "document-generation"]`; `tags: [systematic-review, prisma, prisma-scr, literature-review, scoping-review, risk-of-bias, grade, screening, evidence-synthesis]`.
- Update the `always_load: [...]` list to the 6 from Task 9's `ALWAYS_LOAD`.
- Keep `runtime.mcp_servers` block intact (G-CONN).

- [ ] **Step 2: Run version + always-load gates**

Run: `cd skills/medical-research && python3 evals/check_integrity.py --version --always-load`
Expected: G-VERSION agrees on base `9.0`; G-ALWAYS all 6 present.

- [ ] **Step 3: Commit**

```bash
git add skills/medical-research/skill-manifest.yaml
git commit -m "chore(evidentia): manifest → 9.0.0, PRISMA identity, always_load, tags"
```

---

## Task 16: Reframe commands + agent + plugin.json

**Files:**
- Modify: `commands/evidentia.md`, `commands/evidentia-fulltext.md`, `commands/evidentia-synthesize.md`, `commands/evidentia-connectors.md`, `commands/evidentia-kol.md`
- Create: `commands/evidentia-protocol.md`, `commands/evidentia-appraise.md`
- Modify: `agents/evidence-synthesizer.md`
- Modify: `.claude-plugin/plugin.json`

**Interfaces:** Produces the PRISMA-framed command surface + plugin 2.0.0 metadata.

- [ ] **Step 1: Reframe the 5 existing commands**

- `evidentia.md`: description → "Uçtan uca PRISMA sistematik/kapsam derleme koşumu (P0→P7, insan-onay kapılı)"; body → run `medical-research` P0–P7.
- `evidentia-fulltext.md`: keep (P4 full-text); note it feeds data-extraction.
- `evidentia-synthesize.md`: reframe to P4+P6 (extraction+synthesis via anamnesis).
- `evidentia-connectors.md`: keep (preflight; roster reframed).
- `evidentia-kol.md`: mark as **optional enrichment** (KOL when context calls); description updated.

- [ ] **Step 2: Create the 2 new phase commands**

`commands/evidentia-protocol.md`:
```markdown
---
description: PRISMA protokol + arama stratejisi yazımı (P0–P1). Bir araştırma sorusunu soru-tipine sınıflar, PICO/PECO + uygunluk kriterleri üretir ve veritabanı-başına MeSH/Emtree arama stratejisini raporlanabilir dizeyle yazar. medical-research P0–P1.
argument-hint: <araştırma sorusu>
---

# /evidentia-protocol — PRISMA Protokol + Arama Stratejisi (P0–P1)

Soru: **$ARGUMENTS**

`medical-research` **P0** (`references/prisma-protocol.md`) ve **P1** (`references/search-strategy.md`) fazlarını yürüt; `protocol` + `search_strategy` artefaktlarını üret. İnsan-onayına sun.
```

`commands/evidentia-appraise.md`:
```markdown
---
description: Yanlılık riski + GRADE değerlendirmesi (P5–P6). Verilen bir çalışma seti için tasarıma göre RoB2/ROBINS-I/QUADAS-2/Newcastle-Ottawa/PROBAST uygular ve sonuç-bazlı GRADE kesinlik + Summary-of-Findings üretir. medical-research P5–P6.
argument-hint: <çalışma seti — DOI/PMID/NCT listesi veya konu>
---

# /evidentia-appraise — Yanlılık Riski + GRADE (P5–P6)

Çalışma seti: **$ARGUMENTS**

`medical-research` **P5** (`references/risk-of-bias.md`) ve **P6** (`references/evidence-grading.md`) fazlarını yürüt; `rob_assessments` + `grade_sof` üret. İnsan-onay kapısı bağlayıcıdır.
```

- [ ] **Step 3: Update the agent + plugin.json**

- `agents/evidence-synthesizer.md`: reframe description to isolate heavy P2–P6 fan-out (search→screen→extract→appraise); returns distilled summary.
- `.claude-plugin/plugin.json`: `version: "2.0.0"`; rewrite `description` (PRISMA identity, ≤ a reasonable length); `keywords`: put `["systematic-review","prisma","prisma-scr","literature-review","scoping-review","meta-analysis","risk-of-bias","grade","screening","evidence-synthesis", ... existing domain keywords kept secondary ...]`.

- [ ] **Step 4: Validate JSON + command frontmatter**

Run: `cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins/evidentia && python3 -c "import json;json.load(open('.claude-plugin/plugin.json'));print('plugin.json OK')"`
Expected: `plugin.json OK`. Also confirm the 7 command files exist: `ls commands/ | wc -l` → `7`.

- [ ] **Step 5: Commit**

```bash
git add commands/ agents/evidence-synthesizer.md .claude-plugin/plugin.json
git commit -m "feat(evidentia)!: PRISMA command surface (+protocol/+appraise), agent + plugin 2.0.0"
```

---

## Task 17: Rewrite `README.md` + `docs/EVIDENTIA-CALISMA-SISTEMATIGI.md` identity/architecture

**Files:**
- Modify: `README.md`
- Modify: `docs/EVIDENTIA-CALISMA-SISTEMATIGI.md`

**Interfaces:** Human-facing docs; no gate, but must match the new identity (grep check).

- [ ] **Step 1: Rewrite README "Ne sağlar" + identity**

Replace "Çok-kaynaklı … Türkiye-pazarı araştırma motoru" identity with "Genel-amaçlı PRISMA tıbbi literatür inceleme aracı"; describe P0–P7; list 5+2 commands; state optional enrichment modules; version 2.0.0 / skill 9.0.0.

- [ ] **Step 2: Rewrite the methodology doc**

Rewrite `EVIDENTIA-CALISMA-SISTEMATIGI.md` §0 (bir bakışta) + §1 (mimari — three-layer → PRISMA pipeline P0–P7 + optional modules). Update the ASCII architecture diagram (Adım 0–5 → P0–P7). Keep the CureoSuite boundary (§ scope note).

- [ ] **Step 3: Verify no stale skew language in headline docs**

Run: `cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins/evidentia && grep -niE "istihbarat motoru|pazar(ı| ) araştırma motoru|10 uzmanlık ekseni|10-Axis" README.md docs/EVIDENTIA-CALISMA-SISTEMATIGI.md || echo "no stale skew headline language"`
Expected: `no stale skew headline language`.

- [ ] **Step 4: Commit**

```bash
git add README.md docs/EVIDENTIA-CALISMA-SISTEMATIGI.md
git commit -m "docs(evidentia): README + methodology → PRISMA identity"
```

---

## Task 18: Eval queries (PRISMA + de-skew regression) + final full-gate green

**Files:**
- Modify: `skills/medical-research/evals/benchmark-queries.json`

**Interfaces:** Consumes the whole refactor. Produces PRISMA workflow + de-skew regression eval cases; final green.

- [ ] **Step 1: Replace the axis-oriented benchmark queries with PRISMA + de-skew cases**

Set `version` to `"9.0.0"` and replace `queries` with entries of this exact shape (author ≥6: general therapy, diagnosis, prognosis, scoping, + de-skew regression + one enrichment-fires case):

```json
{
  "id": "Q01-therapy-general",
  "query": "Adults with type 2 diabetes: SGLT2 inhibitors vs placebo for cardiovascular mortality — systematic review",
  "expected_phases": ["P0","P1","P2","P3","P4","P5","P6","P7"],
  "must_produce": ["PICO", "search_strategy", "screening_log", "evidence_table", "rob_assessments(RoB2)", "grade_sof", "prisma_flow_counts"],
  "must_not_fire": ["oncology-layer","hematology-layer","turkiye-layer","drug-intelligence-layer"],
  "regression_if": "any domain enrichment module loaded without an in-question trigger, OR PRISMA flow counts fabricated, OR RoB tool mismatched to design"
},
{
  "id": "Q02-diagnosis",
  "query": "Diagnostic accuracy of point-of-care ultrasound for pediatric appendicitis — scoping review",
  "expected_phases": ["P0","P1","P2","P3","P4","P5","P6","P7"],
  "must_produce": ["PICO(index/reference test)", "PRISMA-ScR flow", "rob_assessments(QUADAS-2)"],
  "must_not_fire": ["oncology-layer","drug-intelligence-layer"],
  "regression_if": "QUADAS-2 not selected for a diagnostic-accuracy question OR PRISMA-ScR variant not used for scoping"
},
{
  "id": "Q03-deskew-regression",
  "query": "Physiotherapy vs corticosteroid injection for lateral epicondylitis — what does the evidence say",
  "expected_phases": ["P0","P1","P2","P3","P4","P5","P6","P7"],
  "must_produce": ["PICO", "grade_sof", "prisma_flow_counts"],
  "must_not_fire": ["oncology-layer","hematology-layer","immunology-layer","neurology-layer","rare-disease-layer","drug-intelligence-layer","regulatory-intelligence","hta-layer","medaffairs-ops-layer","turkiye-layer"],
  "regression_if": "ANY domain enrichment module loads for this domain-neutral question (de-skew failure)"
},
{
  "id": "Q04-enrichment-fires",
  "query": "Trastuzumab deruxtecan in HER2-low breast cancer — systematic review with Türkiye reimbursement context",
  "expected_phases": ["P0","P1","P2","P3","P4","P5","P6","P7"],
  "must_produce": ["PICO", "grade_sof", "prisma_flow_counts", "enrichment_appendix(oncology)", "enrichment_appendix(turkiye)"],
  "may_fire": ["oncology-layer","turkiye-layer","drug-intelligence-layer"],
  "regression_if": "enrichment appears in the CORE SR sections instead of a labelled appendix"
}
```

Update the top-level `description` to explain the phase/de-skew regression semantics.

- [ ] **Step 2: Validate JSON**

Run: `cd skills/medical-research && python3 -c "import json;d=json.load(open('evals/benchmark-queries.json'));print(len(d['queries']),'queries OK')"`
Expected: `4 queries OK` (or more).

- [ ] **Step 3: Run the FULL integrity gate (all gates green)**

Run: `cd skills/medical-research && python3 evals/check_integrity.py`
Expected: `ALL RUN GATES PASSED` (G-REF, G-ALWAYS, G-CONN, G-VERSION, G-COVERAGE, G-PROBE, G-XVAL, G-WHITELIST, G-SIZE, G-DESC, G-PHASES, G-DESKEW).

- [ ] **Step 4: Regression — self-host worker tests still green (no worker code changed)**

Run: `cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins/evidentia/self-host/anamnesis-mcp && npx vitest run test/auth.test.ts 2>&1 | tail -3`
Expected: `15 passed`.

- [ ] **Step 5: G-BUNDLE — roster ↔ .mcp.json consistency (if a bundle checker exists)**

Run: `cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins/evidentia && ls scripts/g_bundle.py && python3 scripts/g_bundle.py 2>&1 | tail -5 || echo "g_bundle not runnable standalone — verify .mcp.json ↔ CONNECTORS.md manually"`
Expected: bundle check passes OR the manual-verify note.

- [ ] **Step 6: Final commit**

```bash
git add skills/medical-research/evals/benchmark-queries.json
git commit -m "test(evidentia): PRISMA + de-skew regression benchmark queries; full gate green (9.0.0)"
```

---

## Self-Review (planned; run before execution handoff)

- **Spec coverage:** F1(Tasks 2–7) · F2(8–9) · F3(10–12) · F4(13–15) · F5(16) · F6(17) · F7(1,18). §9 conformance: G-SIZE(§3.2.1), G-DESC(§3.2.2), progressive disclosure (per-phase loading), grounding/no-fabrication (Task 13/18), eval/CI gate (Task 1/9/18). All spec sections have tasks.
- **Type/name consistency:** phase files named identically across Tasks 2–9 (`prisma-protocol.md`, `search-strategy.md`, `screening.md`, `data-extraction.md`, `risk-of-bias.md`, `prisma-reporting.md`); sidecar keys identical across Task 13/18 (`prisma_flow_counts`, `screening_log`, `evidence_table`, `rob_assessments`, `grade_sof`, `eligibility_criteria`, `search_strategy`); gate names stable (`gate_size/desc/phases/deskew`).
- **Open risk:** G-PROBE/G-XVAL/G-WHITELIST depend on connector-registry edits (Task 14); Task 9 Step 4 notes they go green after Task 14 — sequence honored.
```
