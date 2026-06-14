# pharmaintel — Generic-By-Default Discipline

## Scope

This reference codifies the **non-negotiable separation** between user context (employment, role, employer, geographic location, specialty area) and report content. pharmaintel reports are **evidence inventories** — they must be sponsor-agnostic, audience-neutral, and reusable by any informed scientific reader. User context informs interpretation, NEVER content.

This reference was added in v1.7.0 in response to a controlled production test (T-DXd asset profile, v1.6.0) that surfaced **9 distinct customization leak categories**. Without this discipline, memory-derived user context bleeds into report bodies, frontmatter, executive summaries, intended-use declarations, and auto-trigger rationales — producing reports that read as internal sponsor memoranda rather than competitive intelligence inventories.

---

## Article 1 — User-context vs Query-content separation

The skill operates with two distinct information sources that MUST NOT be conflated:

| Source | Role | Permitted use | Forbidden use |
|---|---|---|---|
| **User context** (memory-derived) — name, employer, role, geographic location, specialty | Interpretation aid for tone/depth calibration ONLY | Adjusting depth (medical-affairs-level vs general-reader); using language register appropriate for query language; offering downstream handoff suggestions in chat | ANY content in report body, frontmatter, executive summary variants, scope notes, auto-trigger rationales, intended-use declarations, audience framing labels |
| **Query content** (user prompt) — explicit asset name, sponsor name, geographic mention, regulatory authority name, indication, modality | Primary trigger for scope, layer activation, depth | All content decisions, all auto-trigger decisions, all framing decisions |

**Rule of thumb:** Before writing any sentence in the report, ask: *"Could this sentence appear identically in a report written for a completely different reader (different employer, different role, different country)?"* If the answer is no, the sentence carries customization leak and must be rewritten.

---

## Article 2 — Forbidden content patterns

The following patterns MUST NOT appear in any pharmaintel report body, frontmatter, or formal disclosure block:

### 2.1 Direct user address
- "Sayın [name]", "Sizin için", "[name] bey/hanım", "Sizin pozisyonunuzda"
- Second-person possessive constructions referring to the reader's organization ("sizin franchise'ınız", "your portfolio")

**Generic alternative:** Direct address belongs in the conversational chat layer, NEVER in the document body.

### 2.2 User-employer strategic action recommendation
- "Stratejik aksiyon sinyali ([Employer X] BU): defensive..."
- "[Employer Y] perspektifinden..."
- "[Employer Z] için defensive niş savunması..."
- "[Employer]'ın [asset] franchise'ı için aşınma analizi..."

**Generic alternative:** Strategic implications must be **multi-stakeholder** ("for incumbents", "for entrants", "for payers"), never sponsor-specific. If a competitive dynamic affects multiple sponsors, name them all symmetrically. If user wants single-sponsor strategic analysis, that is a SEPARATE task type (T6 head-to-head focused on a specific competitive pair) and requires explicit user request naming the sponsor.

### 2.3 User-employer-fitted intended use declaration
- "Intended for internal strategic intelligence use within [Employer] context"
- "...for [Employer] [Department] decision support"
- "...usable in [Employer] internal stakeholder briefing"

**Generic alternative:** "Intended for medical affairs, business development, regulatory intelligence, market access, and academic readers analyzing [asset/modality/topic]."

### 2.4 User-employer internal terminology in audience framing
- "BU senior team, KOL advisory, RWE registry committee" (Roche-internal terminology)
- "[Employer]-internal stakeholder briefing"
- Any acronym or organizational structure name specific to a single company

**Generic alternative:** "medical affairs briefing, business development presentation, KOL advisory board discussion, payer engagement materials"

### 2.5 User-employer competitive scope alignment
- "...özellikle [Employer] portföyüyle ([Product A], [Product B], [Product C]) rekabetçi etkileşim"
- "...with particular attention to [Employer]'s competitive position"
- Scope notes that anchor the analysis around the user's employer's portfolio

**Generic alternative:** Scope notes describe the analytical frame in sponsor-agnostic terms. Competitive interactions are noted symmetrically (e.g., "Competitive position vs incumbent therapies" with all incumbents named, not just the user's employer's products).

### 2.6 User-employer in auto-trigger rationale
- "sub-protocol-[X].md (Step 1g — sponsor profile: [Employer] [Role])"
- Auto-trigger rationales that cite the user's employer or role

**Generic alternative:** Auto-trigger rationales cite **query content only** (asset's sponsor, query's geographic mention, query's keyword match). User identity is NOT a valid trigger source.

---

## Article 3 — Audience neutrality default

### 3.1 Default audience

Default audience for all pharmaintel reports: **"informed scientific reader"** — a composite that includes:
- Clinicians (oncologists, hematologists, cardiologists, etc., depending on therapeutic area)
- Academic researchers
- Pharmaceutical industry professionals (medical affairs, regulatory, market access, business development, R&D)
- Healthcare investors and analysts
- Patient advocacy professionals (when applicable)
- Health policy researchers

This composite audience is **sponsor-agnostic and employer-agnostic** by construction.

### 3.2 Multi-audience executive summary variants — disciplined sponsor-neutrality

When multi-audience rendering is invoked (per `report-template.md` Multi-audience executive summary), the three variants MUST follow this discipline:

| Variant | Generic framing (REQUIRED) | Sponsor-specific framing (FORBIDDEN unless explicit user request) |
|---|---|---|
| **Medical Affairs lens** | Clinical impact, label delta, KOL implications, unmet need — discussed sponsor-agnostically | "[Employer]'s competitive medical affairs response" — NO |
| **Commercial / BU lens** | Market sizing, competitive positioning across all incumbents, launch trajectory archetype, analyst consensus — sponsor-agnostic | "Strategic action signal ([Employer] BU): defensive..." — NO |
| **Payer / HEOR lens** | Pricing, cost-effectiveness, access barriers, sequencing implications — generic | "[Employer]'s payer negotiation strategy" — NO |

**Critical:** The Commercial/BU lens is the most prone to sponsor-specific contamination. The discipline: write the Commercial/BU variant as if you do not know which sponsor will read it. Discuss launch trajectory, market share dynamics, competitive threats — but assign no actions to any specific sponsor.

### 3.3 Sponsor-specific variant — opt-in only

A sponsor-specific Commercial variant is appropriate ONLY when:
1. User explicitly names the sponsor in the query ("How does [molecule X] threaten [Sponsor Y]'s [franchise Z]?")
2. The task type is T6 Head-to-Head Comparison with two specific sponsor products
3. The task is explicitly framed as a competitive defense analysis (separate task category, not standard T2/T3)

In these cases, the sponsor-specific lens runs in addition to (not in replacement of) the generic variants, and the document scope note explicitly declares: "This report includes sponsor-specific competitive analysis from [Sponsor]'s perspective per user request."

### 3.4 Formal T6-Defense exception (v1.8.0)

Per `task-comparison-defense.md` v1.8.0+, T6 Head-to-Head Comparison has a single permitted **sub-mode exception** to the audience neutrality default: T6-Defense (sponsor-specific competitive defense framing). This exception is the only formal carve-out from generic-by-default discipline and is governed by the following invariants:

1. **Activation is explicit-only** (per `task-comparison-defense.md` §1) — no semantic auto-trigger, no user-identity inference
2. **Override is selective** — only G22.4 (sponsor-specific strategic action) and G22.7 (scope note alignment) are overridden, and only within designated §10.B / §10.C Strategic Implications sections
3. **Symmetric framing is mandatory** — defense framing for Sponsor X requires parallel offensive framing for Sponsor Z (per `task-comparison-defense.md` §3)
4. **Triple disclosure is mandatory** — Provenance section explicitly declares activation source, sponsor, competitive target, and scope of override (per `task-comparison-defense.md` §6)
5. **G24 gate audit** verifies the exception's well-formedness (6 checks per `task-comparison-defense.md` §7)

All other generic-by-default articles (1, 2, 4, 5, 6, 7) remain in full force during T6-Defense. The exception narrows specific elements within a specific section; it does NOT broadly suspend the discipline.

If T6-Defense is invoked malformed (e.g., missing parallel symmetric section, missing triple disclosure, override applied outside §10.B/§10.C), G24 audit fails and the report cannot be delivered in T6-Defense mode — fall back to standard T6 (sponsor-agnostic).

---

## Article 4 — Coverage anchor symmetry

### 4.1 Positive-list discipline

Coverage statements list what IS in scope, not what is OUT of scope. "Global (US, EU, Japan, China)" is correct; "Global (US, EU, Japan, China) — Türkiye dışlanmıştır" is incorrect because it asymmetrically anchors a specific region as a reference point of exclusion. Asymmetric exclusion is a fingerprint pattern (only readers who would have expected that region get singled out).

### 4.2 Permitted exclusions

Explicit exclusions are permitted ONLY when:
1. User's query explicitly requested exclusion ("global pipeline excluding China")
2. Phase 1 scope decision required boundary documentation due to a methodological reason
3. The exclusion is generic to the analytical category (e.g., "ATMPs excluded from this conventional small-molecule landscape") — methodological, not geographic-bias-driven

Exclusion of a specific region without methodological reason is a fingerprint and forbidden.

### 4.3 Inclusion anchor asymmetry

The inverse fingerprint pattern: scope notes that highlight one region/sponsor with extra emphasis ("özellikle Türkiye pazarı bağlamı", "with particular attention to Roche's portfolio") create the same asymmetry. The fix: if a region or sponsor is materially in scope, treat it symmetrically with comparable analytical depth as other peer entities. If only one region/sponsor warrants depth, explain methodologically (data availability, regulatory significance) — not via emphasis.

---

## Article 5 — Auto-trigger rationale clarity

### 5.1 Valid auto-trigger sources

Each auto-triggered layer's rationale MUST cite one or more of:

| Trigger source | Valid? | Example rationale |
|---|---|---|
| **Asset's actual sponsor (named in query or known asset-sponsor mapping)** | YES | "Daiichi Sankyo + AstraZeneca named as T-DXd's developers" |
| **Query keyword match** | YES | "Query contains 'NICE' explicit keyword → HTA layer" |
| **Asset's modality / indication / cost class characteristic** | YES | "High-cost specialty oncology profile → HTA layer" |
| **Asset's regulatory characteristic** (orphan, breakthrough, conditional, first-in-class) | YES | "First-in-class FDA approval profile → FAERS focus" |
| **Geographic mention in query** | YES | "Query mentions Türk hekim katılımı → Türkiye layer" |
| **User's employer** | NO (forbidden) | ❌ "Sponsor profile: [Employer] [Role]" |
| **User's role / specialty** | NO (forbidden) | ❌ "User is medical director → load X layer" |
| **User's geographic location** | NO (forbidden) | ❌ "User in Türkiye → load Türkiye layer" |
| **User's memory-derived organizational context** | NO (forbidden) | ❌ "User works in hematology BU → emphasize hematology angle" |
| **Query language (writing system / natural language of query)** *(v6.0.0)* | NO (forbidden) | ❌ "Query written in Turkish → load Türkiye layer"; ❌ "Query in Japanese → load PMDA layer"; ❌ "Query in Mandarin → load NMPA layer" |

### 5.2 Auto-trigger disclosure block discipline

The §Auto-Trigger Disclosure block in every report MUST list each loaded layer with a query-content-based rationale. If any layer's rationale is user-context-based, the auto-trigger logic itself is bugged and that load is invalid — Claude MUST NOT load the layer and MUST NOT mention it in disclosure.

**Worked example for T-DXd query:**

| Katman | Tetik tipi | Rationale (CORRECT, query-content-based) |
|---|---|---|
| `task-asset.md` (T2) | Step 1 task classification | "asset profili çıkar" semantic match |
| `sub-protocol-label.md` | Step 1f mandatory | T-DXd onaylı asset (FDA + EMA + multiple regions); label + boxed warning analysis required |
| `sub-protocol-sponsor-sweep.md` | Step 1e mandatory | Daiichi Sankyo + AstraZeneca named (asset's actual sponsors); both Top-30 |
| `task-hta.md` | Step 1g semantic auto-trigger | High-cost specialty oncology (~$190K/yr/patient); NICE TA862 + TA992 already public |
| `sub-protocol-pmda.md` | Step 1g semantic auto-trigger | Daiichi Sankyo is Japanese sponsor (asset's developer, not user's employer); Japan is a primary market |
| `sub-protocol-turkey.md` | NOT TRIGGERED | Query does not mention Türkiye, TİTCK, SGK, or Türkiye-specific market context. User's location/employer is NOT a valid trigger. |

In the T-DXd v1.6.0 production test, sub-protocol-turkey was incorrectly auto-triggered with rationale "Sponsor profile — Roche Türkiye Country Medical Director / BU Lead konumu" — this is a textbook user-identity-based trigger and represents the bug v1.7.0 fixes.

### 5.3 Language vs scope distinction *(v6.0.0)*

**Principle:** The natural language / writing system in which a query is composed is **not a valid trigger source** for any regional sub-protocol. Query language carries no information about query scope. A Turkish-speaking user can ask about French healthcare policy in Turkish; an English-speaking user can ask about TİTCK regulatory decisions in English. The trigger for `sub-protocol-turkey.md` must be explicit Türkiye-scope semantic content (TİTCK, SGK, SUT, EK-4, Türkiye pazarı, yerli sponsor adı, etc.) — **not** the fact that the query itself is written in Turkish.

**Symmetric application across regional sub-protocols:**

| Regional sub-protocol | Language fact (NEVER a trigger) | Valid trigger (content-based) |
|---|---|---|
| `sub-protocol-turkey.md` | ❌ Query written in Turkish (Türkçe) | ✅ Explicit Türkiye-scope: TİTCK, SGK, SUT, EK-4, MEDULA, Türk yerli sponsor adı, "Türkiye'de [endikasyon] pazarı", "Türk hekim katılımı [trial]", "Türkiye launch", "Türk hasta erişimi", "Türk RWE registry", "yerli ilaç" |
| `sub-protocol-pmda.md` | ❌ Query written in Japanese (日本語) | ✅ Explicit Japan-scope: PMDA, MHLW, Chuikyo (中医協), Sakigake, 薬価, 再審査, named Japanese sponsor as asset's developer + Japan regulatory/commercial scope |
| `sub-protocol-nmpa.md` | ❌ Query written in Mandarin (中文) | ✅ Explicit China-scope: NMPA, CDE, NHSA, NRDL (国家医保目录), VBP (集中带量采购), 附条件批准, named Chinese sponsor (BeOne, Innovent, Junshi, Hengrui, etc.) + China regulatory/commercial scope |

**Rationale:** v5.0.0 production test (T-DXd asset profile query "trastuzumab deruxtecan raporu hazırla") revealed that runtime fired `sub-protocol-turkey.md` despite query content containing ZERO Türkiye-specific terminology. Root cause diagnosis: runtime ambiguously interpreted "Turkish query language" as a species of "Geographic mention in query" (Article 5.1 valid row). This conflation is incorrect — the writing system is a property of the *utterance*, not of the *content*. v6.0.0 codifies this distinction.

**Worked counterexamples:**

| Query | Language | Should `sub-protocol-turkey.md` fire? | Rationale |
|---|---|---|---|
| "trastuzumab deruxtecan raporu hazırla" | Turkish | **NO** | Zero Türkiye-scope semantic content — just a Turkish-language request for a generic asset profile |
| "T-DXd'nin TİTCK durumu" | Turkish | **YES** | Explicit TİTCK keyword in query content |
| "T-DXd's regulatory status in Turkey" | English | **YES** | Explicit Türkiye geographic scope in query content |
| "What's T-DXd's US pipeline?" | English | **NO** | Explicit US-scope query; Türkiye not invoked |
| "pembrolizumab 1L NSCLC landscape" | English | **NO** | Global modality/TA query; no regional scope invoked |
| "Enhertu için SGK geri ödemesi nasıl?" | Turkish | **YES** | Explicit SGK keyword in query content |

**Enforcement:** Claude MUST NOT cite "Turkish query language" or "query written in Turkish" (or equivalents for Japanese / Mandarin) as trigger rationale in the §Auto-Trigger Disclosure block. If regional sub-protocol activation would otherwise be contemplated based on query writing system alone, the correct behavior is to **NOT load the sub-protocol** — and the disclosure entry for that sub-protocol must be "NOT TRIGGERED — query language alone is not a valid content trigger (Article 5.3)."

**New manifest gate G61 (v6.0.0):** Validator pattern-matches §Auto-Trigger Disclosure blocks for language-as-trigger rationales. Any occurrence of regex `(turkish|türkçe|japanese|japonca|mandarin|çince|chinese).{0,40}(language|dil|written|yaz[ıi]lm[ıi]ş).{0,40}(trigger|tetik)` in auto-trigger rationale → BLOCKER fail. Report must be revised to remove the offending sub-protocol activation + rationale before delivery.

---

## Article 6 — Generic-By-Default audit (G22)

Before any report is finalized, Claude executes the G22 Generic-By-Default audit with the following 8 checks. Any "yes" answer requires revision before delivery.

| # | Check | Pass criterion |
|---|---|---|
| 1 | Does the document body contain the user's name (memory-derived)? | NO occurrences |
| 2 | Does the document body contain the user's employer name AND that employer is NOT explicitly mentioned in the user query? | NO occurrences |
| 3 | Does any auto-trigger rationale cite "user profile", "sponsor profile" (when "sponsor" actually means user's employer), user role, or user location? | ZERO such rationales |
| 4 | Does any executive summary variant include strategic action recommendation directed at a specific named sponsor (other than mechanically-required incumbent identification)? | ZERO recommendations |
| 5 | Does the intended-use declaration name the user's employer or contain employer-internal terminology? | NO |
| 6 | Does the coverage statement contain region exclusion-as-mention asymmetry, or region/sponsor inclusion anchor asymmetry? | NEITHER |
| 7 | Does the document scope note align analytical frame with user employer's competitive setting? | NO |
| 8 | Do any disclosure blocks (Triangulation Notes, Provenance Disclosure, Confidence Disclosure) contain user-context references beyond what is methodologically required? | NO |

If any check fails: revise the offending content to a generic equivalent, re-run audit. Do NOT deliver until all checks pass.

This audit runs as Step 1h in SKILL.md immediately after Step 1g (Semantic Auto-Trigger evaluation), and again as the final gate before report finalization.

---

## Article 7 — Permitted user-context use (positive examples)

To avoid over-correction, the following uses of user context ARE permitted because they affect tone/depth/format only, not content:

| Use | Permitted? | Rationale |
|---|---|---|
| Writing in Turkish if user's query is in Turkish | YES | Language register matches query, not user identity |
| Calibrating depth to medical-affairs-grade detail when user query indicates clinical sophistication | YES | Depth calibration based on query sophistication, not user role |
| Suggesting downstream handoffs (carbon-html-report, carbon-pptx) in chat after delivering report | YES | Chat suggestion ≠ report content |
| Offering to produce a follow-up T6 head-to-head focused on a specific sponsor when user mentions a sponsor concern in chat | YES | Follow-up offer ≠ unsolicited content insertion |
| Acknowledging user's named employer in chat conversation if user voluntarily disclosed it in current chat session | YES | Conversational acknowledgment ≠ document body content |

The rule: chat layer can be conversational and aware; document layer is sponsor-agnostic and audience-neutral.

---

## Cross-reference

- `SKILL.md §Task Routing — Layer triggers (B) Semantic auto-triggers` — trigger logic must follow Article 1 + Article 5
- `SKILL.md Step 1g` — Semantic auto-trigger evaluation references this discipline
- `SKILL.md Step 1h` — G22 Generic-By-Default audit (added v1.7.0)
- `report-template.md Multi-audience executive summary` — Article 3.2 governs variant discipline
- `triangulation.md §10` — Geography Verification Guard pairs with Article 4 coverage symmetry
- `sub-protocol-turkey.md §Trigger by query content` — Article 5 governs trigger source validity
- `sub-protocol-pmda.md §Trigger by query content` — same discipline
- `sub-protocol-nmpa.md §Trigger by query content` — same discipline
- `scripts/validate-report-discipline.py` — programmatic enforcement of G22 (added v1.7.0)

**When loaded:** This reference is loaded automatically at SKILL.md Step 1 (always, no conditional) because it governs all subsequent skill behavior. It is NOT a conditional layer — it is a foundational discipline.
