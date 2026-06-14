# pharmaintel — Report Template (v8.1.0)

This is the canonical markdown skeleton for pharmaintel outputs. Adapt sections per task type (T1–T8). The report is organized in **two layers** per `references/report-presentation.md` (Reader-Facing Clean-Copy Standard):

- **Layer A — okur-yüzlü temiz kopya:** the default, render-visible deliverable. Journal-quality Turkish prose; info boxes; abbreviations glossary; journal-style numbered citations; consolidated Kaynaklar; reader-friendly Yöntem ve Kapsam. **No internal-process machinery in the visible body.**
- **Layer B — iç denetim ve sağlama kaydı:** the gate-mandated machinery (per-claim provenance stamps, Confidence Disclosure Table, Triangulation Notes, G22 audit line, Auto-Trigger / Sponsor Sweep Disclosure), wrapped in render-exclusion sentinels (or a companion file). Present in raw markdown for the validator; **never rendered**.

Keep the **meta-block**, **executive summary**, **abbreviations glossary**, **Yöntem ve Kapsam**, **Sınırlılıklar**, **Kaynaklar** (Layer A) and the **render-excluded audit ledger** (Layer B) regardless of task type.

---

## Meta-block (mandatory, at the top)

```markdown
---
report_type: [T1 Company | T2 Asset | T3 Modality | T4 Deal | T5 Catalyst | T6 Comparison | T7 Reg-status | T8 Pipeline]
subject: [primary subject of the report]
data_cutoff: YYYY-MM-DD
pharmaintel_version: 8.1.0
medsearch_upstream: [yes/no — if a medsearch pass was used upstream]
sources_tier: [T0 only | T0+T1 | T0+T1+T2]
---
```

---

# LAYER A — Okur-yüzlü temiz kopya (render-visible)

This is the journal-article-quality body. Everything in Layer A is written for the reader; no validator/gate/machinery terminology appears here.

## Standard document skeleton (Layer A)

```markdown
# [Başlık — açık, bilgilendirici, Türkçe]

**Rapor türü:** [T_N — okuyucu-dostu etiket, örn. "Varlık/Molekül Profili"]
**Veri kesim tarihi:** YYYY-AA-GG
**Kapsam:** [tek cümlelik, paydaş-agnostik çerçeve]

---

## Kısaltmalar ve Tanımlar

[Raporda geçen tüm kısaltmalar ve anahtar terimler. Okuyucunun anlamadığı terim kalmamalı.]

| Kısaltma / Terim | Açılım / Tanım |
|---|---|
| [örn. ADC] | [Antikor-ilaç konjugatı (antibody-drug conjugate) — kısa, tam-cümle tanım.] |
| [örn. PFS] | [Progresyonsuz sağkalım (progression-free survival) — ...] |
| [örn. PDUFA] | [ABD FDA karar hedef tarihi — ...] |

---

## Yönetici Özeti

[3–6 tam cümle. Yalnızca bu bölümü okuyan biri şunları öğrenmeli: (1) konu, (2) mevcut durum, (3) en kritik 2–3 bulgu, (4) en önemli belirsizlik/boşluk. Numaralı atıflarla desteklenir.]

**Öne çıkan bulgular:**
- [Bulgu 1 — tam cümle, atıflı]
- [Bulgu 2 — tam cümle, atıflı]
- [Bulgu 3 — tam cümle, atıflı]

[Çok-paydaşlı raporlar için isteğe bağlı üç-mercek özeti — bkz. "Multi-audience executive summary" bölümü, paydaş-agnostik disiplinle.]

---

## Arka Plan ve Bağlam

[Konunun çerçevesi. Okuyucuyu bulgulara hazırlar: endikasyon/modalite tanımı, pazar bağlamı, terminoloji. Karmaşık kavramlar bilgi kutularıyla desteklenir.]

> **Bilgi Kutusu · [İlk geçen anahtar terim]**
>
> [Tanım — tam cümlelerle, okuyucunun bu raporu anlaması için gereken kavramsal arka plan.]

---

## [Göreve özgü bulgu bölümü 1 — lede cümlesiyle açılır]

[Bölümün ana bulgusunu özetleyen açılış cümlesi; ardından kanıt; ardından bağlam. Her maddi iddia numaralı atıfla desteklenir. Kritik sayısal değerler (HR, %95 GA, p, n, tarihler, mali rakamlar) atıf işaretini sayının kendisine taşır.]

[Tablodan önce yönlendirme cümlesi:]
Aşağıdaki tablo, [...] karşılaştırmaktadır.

| [Sütun] | [Sütun] | [Sütun] |
|---|---|---|
| [veri] | [veri] | [veri] |

<!-- VIZ: tip=<grafik-türü>; veri=<bu tablo/değerler>; eksen=<x: ..., y: ...>; vurgu=<...>; not=<tasarımcıya kısa yönlendirme> -->

[Tablodan sonra yorum cümlesi:]
Tablodan görüldüğü üzere [...].

> **Yöntem Notu · [İlgili genel metodolojik nokta]**
>
> [Okuyucu-dostu, genel metodolojik açıklama. İç-makine terimi (validator, gate, rütbe) İÇERMEZ.]

---

## [Göreve özgü bulgu bölümü 2 — köprü cümlesiyle bağlanır]

[Bir önceki bölüme köprü: "Düzenleyici durum bu şekilde netleştikten sonra, klinik kanıt tabanına geçilebilir." Ardından bölümün lede'i ve içeriği.]

...

---

## Sentez ve Çıkarımlar

[Bulgular bir araya getirilir; paydaş-agnostik çıkarımlar (generic-by-default disiplini). Soyut paydaş kategorileri için ("yerleşik oyuncular", "yeni girenler", "ödeyiciler") — asla belirli adlandırılmış bir sponsor için değil (T6-Defense istisnası hariç).]

---

## Sınırlılıklar

**Açık erişim kaynak boşlukları:**
- [örn. "Abonelik gerektiren küresel satış veri tabanlarına erişilememiş → ABD dışı coğrafi satış kırılımı, şirket segment bildirimlerinden yaklaşık olarak türetilmiştir."]
- [Kurumsal pipeline veri tabanları erişilemedi → erken pipeline yalnızca yayımlanmış ön baskılar + patent başvurularıyla sınırlı.]

**Konuya özgü boşluklar:**
- [örn. "Şirket X özeldir; analiz büyük ölçüde basın bültenleri ve patent başvurularına dayanır (tek-kaynak riski)."]

**Veri kesim tarihi:**
- YYYY-AA-GG — bu tarihten sonraki gelişmeler rapora yansıtılmamıştır.

---

## Yöntem ve Kapsam

Bu rapor, birincil ve açık erişimli kaynaklara dayanmaktadır: ABD FDA ve Avrupa İlaç Ajansı (EMA) düzenleyici kayıtları, ClinicalTrials.gov çalışma tescilleri, SEC EDGAR mali bildirimleri ve hakemli literatür. Her maddi bulgu, en az iki bağımsız kaynakla teyit edilmeye çalışılmış; teyit düzeyi farklılık gösteren bulgular metinde açıkça belirtilmiştir. Ticari analiz platformlarına (örneğin abonelik gerektiren küresel satış veri tabanları) erişilememiş; bunun yarattığı boşluklar Sınırlılıklar bölümünde belgelenmiştir.

Bu rapor yatırım tavsiyesi, promosyonel materyal veya profesyonel düzenleyici/klinik/mali danışmanlık yerine geçmez; provenansı belgelenmiş bir kanıt envanteridir.

---

## Kaynaklar

[İlk göründükleri sırada numaralandırılır. Her künye tam atıf sağlar.]

**[1]** [Kaynak adı/türü] — [açıklama/başlık].
- URL/Kimlik: [DOI, NCT ID, 8-K accession, EPAR URL, patent no veya kanonik URL]
- Erişim: YYYY-AA-GG · Kullanıldığı bölümler: §X, §Y

**[2]** [Yazar(lar)] — "[Makale başlığı]".
- Dergi: [ad] ([yıl]) · DOI: [...]
- Erişim: YYYY-AA-GG · Kullanıldığı bölümler: §Z

...
```

---

## Multi-audience executive summary (Layer A — optional, default off; sponsor-agnostic discipline)

For high-stakes reports addressing multiple stakeholder communities (Medical Affairs, Commercial / BU Lead, Payer / HEOR), Claude MAY render **three parallel executive summary variants** in Layer A. Enabled when:

1. User explicitly requests "üç-paydaş özeti", "multi-audience summary", "MA + Commercial + Payer summary"
2. Task is T2 Asset Profile or T3 Modality Landscape with both clinical and commercial dimensions
3. Report scope spans >5 material claims with differential relevance to the three audiences

**Sponsor-neutrality discipline (non-negotiable):** All three variants describe market dynamics, competitive positioning, payer reality, and strategic implications **sponsor-agnostically**. Strategic action recommendations are made for **abstract stakeholder categories** ("for incumbents", "for entrants", "for payers"), NEVER for any specific named sponsor. Incumbents named symmetrically.

A sponsor-specific Commercial variant is appropriate ONLY when: user explicitly names the sponsor AND requests sponsor-specific perspective; OR Task is T6 Head-to-Head naming both products; OR Task is explicit competitive defense analysis. In these cases the sponsor-specific variant runs **in addition to** the generic variants, and the Kapsam note declares it explicitly.

**Three-variant template (Layer A):**

```markdown
## Yönetici Özeti — Medical Affairs merceği
**(Klinik etki, etiket farkı, karşılanmamış ihtiyaç, KOL çıkarımları)**

[3–5 cümle: pivotal klinik sonuçlar (etki büyüklükleri, istatistiksel anlamlılık), etiket/SmPC farkı, hasta popülasyonu kısıtları, karşılanmamış ihtiyaç, beklenen KOL pozisyonu ve açık klinik sorular. Paydaş-agnostik.]

---

## Yönetici Özeti — Ticari / BU merceği
**(Pazar büyüklüğü, rekabetçi konum, lansman trajektörisi, yatırım sinyalleri)**

[3–5 cümle: modalite/TA pazar büyüklüğü ve yön, bu varlığın yerleşik oyunculara karşı konumu (tüm yerleşikler simetrik adlandırılır), lansman trajektörisi arketipi, analist zirve satış konsensüsü + yönetim rehberliği, soyut paydaş kategorileri için stratejik çıkarımlar. Paydaş-agnostik.]

**YASAK desenler (generic-by-default.md):**
- ❌ Belirli adlandırılmış sponsora yönelik stratejik aksiyon önerisi (açık kullanıcı talebi olmadan)
- ❌ Kullanıcı/işveren-kimliği teması

---

## Yönetici Özeti — Ödeyici / HEOR merceği
**(Fiyatlandırma, maliyet-etkililik, erişim engelleri, sıralama çıkarımları)**

[3–5 cümle: liste fiyatı beklentisi + benzer molekül fiyat referansları, maliyet-etkililik sinyali (HTA ajansı ICER bantları, biliniyorsa), beklenen ödeyici kısıtları, temsili ulusal sağlık sistemi için bütçe etkisi, tedavi yolağındaki sıralama. Paydaş-agnostik.]
```

**Disclosure (Layer B):** When multi-audience rendering is used, the §Auto-Trigger Disclosure (Layer B) notes the audiences rendered and confirms sponsor-agnostic framing.

---

# LAYER B — İç denetim ve sağlama kaydı (render-excluded)

> **CRITICAL:** Layer B is wrapped in render-exclusion sentinels (or emitted as a companion `*-denetim-kaydi.md` file). It is present in the raw markdown so the validator scans it and the disclosure-block headings remain findable, but it is **stripped before the rendered clean copy** is produced. The disclosure-block headings below MUST stay as real `##` headings (`##?\s*Provenance\s+Disclosure` etc.) for validator Check 8/9 compatibility — do NOT bury them in HTML comments or demote to `###`.

```markdown
<!-- RENDER:EXCLUDE-FROM-HERE -->

## Ek — İç Denetim ve Sağlama Kaydı (render dışı)

> Bu ek, raporun bütünlük denetimi ve provenans kaydı içindir; okur-yüzlü nihai üründe yer almaz.

## Provenance Disclosure

This report was produced by the pharmaintel skill, v8.1.0, using:
- Free-tier regulatory sources (FDA Drugs@FDA, EMA EPAR, ClinicalTrials.gov, DailyMed, FDA Warning Letters / FAERS as applicable)
- Free-tier financial filings (SEC EDGAR)
- Peer-reviewed literature via PubMed + Paper Search + Scholar Gateway MCPs
- Free-tier industry media (FiercePharma, BioPharma Dive, Endpoints free, Evaluate Vantage free)
- Semantic web retrieval via Exa; real-time news via Tavily

Enterprise sources (Bloomberg, Cortellis, Citeline, Evaluate Premium, IQVIA MIDAS, Patsnap, AlphaSense, STAT Plus, Endpoints Premium) were not used. Material gaps documented in §Sınırlılıklar (Layer A).

**Per-claim provenance stamps (4-part):**

[Claim 1 summary]
— Source: [type — Primary Regulatory / Peer-Reviewed / Statutory Filing / Industry Media / Analyst / IR Statement]
— ID/URL: [DOI, NCT ID, 8-K accession, EPAR URL, patent number, canonical URL]
— Accessed: YYYY-MM-DD
— Confidence: [High | Medium | Low | Unknown]

[Claim 2 summary]
— Source: ...
— ID/URL: ...
— Accessed: YYYY-MM-DD
— Confidence: ...

**Intended audience (sponsor-agnostic per generic-by-default.md):** medical affairs, business development, regulatory intelligence, market access, and academic readers analyzing this asset/modality/topic. The report does NOT name a specific employer or organizational context as its intended audience.

> **Yöntem Notu·** Audience framing must stay sponsor-agnostic. Do not scope the intended audience to any single employer or internal organizational context, do not address the reader in the second person by name, and do not use employer-internal vocabulary when describing who the report is for. (Phrased abstractly here so this guidance line itself remains leak-free under the generic-by-default validator.)

## Confidence Disclosure

| Confidence | Material claims | Proportion | Representative examples |
|---|---|---|---|
| **High** | [N] | [X%] | [1–2 brief representative claim summaries] |
| **Medium** | [N] | [X%] | [...] |
| **Low** | [N] | [X%] | [...] |
| **Unknown** | [N] | [X%] | [...] |
| **Total** | [N] | 100% | — |

**Interpretation:** [One sentence on what the distribution means for usability.]
**Caps applied (if any):** [List any confidence-capped claims per triangulation.md §6.]

## Triangulation Notes

[Summarise conflicts and resolution per §3 hierarchy. E.g.:]
> **Conflict resolved:** Sales figure disclosed as $1.2B in press release, $1.18B in 10-K segment disclosure. 10-K preferred per hierarchy rank 3 > rank 6. Reported: $1.18B.

[If none: "No material source conflicts arose during this analysis."]

## Auto-Trigger Disclosure

[List auto-triggered layers + rationale (query-content-based per generic-by-default.md Article 5; NEVER user-identity or query-language based). If multi-audience rendered: list audiences + confirm sponsor-agnostic framing.]

G22 Generic-By-Default audit (forward + backward) sonucu: Tüm 8 kontrol PASS (validator: scripts/validate-report-discipline.py invocation YYYY-MM-DD).

<!-- RENDER:EXCLUDE-TO-HERE -->
```

---

## Adaptation by task type

### T1 Company Deep-Dive
Sections per `task-company.md`; heavy use of IR + 10-K + 10-Q. Layer A narrative; Layer B ledger.

### T2 Asset / Molecule Profile
Sections per `task-asset.md`; label + pivotal trial + current development tables in Layer A.

### T3 Modality Landscape
Sections per `task-modality.md`; heavy use of tables (approved, late-stage, early pipeline). VIZ directives next to each major table.

### T4 Deal / M&A
Sections per `task-deal.md`; structure + rationale + valuation are the heart.

### T5 Catalyst Watch
Tabular; time-bucketed (next 30 / 30–90 / 90d–12mo); minimal narrative. When sub-protocol-catalyst-watch.md loaded, calendar follows §7 rules. Each catalyst row classified by type. VIZ directive: `tip=timeline`.

### T6 Head-to-Head
Side-by-side tables throughout; differentiation summary at end. VIZ directive: `tip=comparison-table`.

### T7 Regulatory Status Snapshot
Short — the inline handler in SKILL.md §T7. Single table + confidence in Layer B.

### T8 Pipeline Inventory
Tabular; grouped by therapeutic area or phase.

---

## Formatting guidelines (Layer A)

- Use Markdown tables for structured comparisons; precede with a framing sentence, follow with an interpretive sentence.
- Prefer bullet lists for short claim enumerations; prose for contextualisation. Bullets carry at least one complete sentence.
- **No per-claim provenance blockquotes in the visible body** — those live in Layer B. The visible body uses journal-style numbered citations `[n]`.
- Info boxes via standardized bold-lead blockquotes (`**Bilgi Kutusu · ...**`, `**Yöntem Notu · ...**`, `**Dikkat · ...**`).
- Visualization directives as HTML comments (`<!-- VIZ: ... -->` / `<!-- VIZ-BLOCK ... -->`) adjacent to data; never echoed in visible prose.
- Include clickable URLs in Kaynaklar.
- Cap section prose at ~8 paragraphs; if longer, subdivide.
- Dates in ISO 8601 (YYYY-AA-GG); amounts with explicit currency.
- "Veriler ... göstermektedir" type objective phrasing; "biz inanıyoruz" is not used (evidence inventory, not opinion).

## Downstream handoff (render-pipeline contract)

If the user requests:
- **Publication-grade HTML / PDF:** hand this markdown to `carbon-html-report`
- **Briefing deck (PPTX):** hand this markdown to `carbon-pptx`

Both downstream skills MUST, per `references/report-presentation.md` §8:
1. Process and **remove** all `<!-- VIZ: ... -->` / `<!-- VIZ-BLOCK ... -->` comments (after generating the corresponding charts/diagrams).
2. **Remove** the render-excluded Layer B between `<!-- RENDER:EXCLUDE-FROM-HERE -->` and `<!-- RENDER:EXCLUDE-TO-HERE -->`.
3. Upgrade `Bilgi Kutusu` / `Yöntem Notu` / `Dikkat` blockquotes to design-system callout components.
4. Preserve numbered citations and the Kaynaklar section.

Defense-in-depth: even if a downstream skill is unaware of this contract, HTML comments do not render — so the reader-facing output stays clean.
