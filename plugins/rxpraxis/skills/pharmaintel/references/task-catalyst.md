# pharmaintel — T5: Catalyst Watch Playbook

## Scope

Monitoring and analysis of near-term pharma/biotech catalysts: FDA / EMA regulatory decisions, AdComm meetings, clinical readouts, earnings, conference late-breakers, deal flow, IP events (Paragraph IV, PTAB). Can be built as:
- **One-shot snapshot** (current state of pending catalysts on a ticker, asset, or TA)
- **Recurring monitoring** (defined watchlist, weekly/monthly refresh)

## Deliverable structure

### One-shot snapshot

```
# [Watchlist Label] — Catalyst Snapshot, [Date]

## Next 30 days
| Date | Catalyst type | Asset / Company | Significance | Source |

## 30–90 days
| Date | Catalyst type | Asset / Company | Significance | Source |

## 90 days – 12 months
| Date | Catalyst type | Asset / Company | Significance | Source |

## Key uncertainties  (pending / outcome unknown)
  (items known to exist but without specific date, OR PDUFA date has passed without a public outcome announcement)

## Recently resolved (trailing 30 days, outcome known)
  (ONLY catalysts with a confirmed outcome — approval, CRL, withdrawal, readout published)

## Limitations
```

**Table discipline (v1.1.0):**

- "Recently resolved" is for **known outcomes only**. A PDUFA date that has passed without a public announcement → §Key uncertainties, not §Recently resolved.
- Any asset listed in §Recently resolved must have at least one primary regulatory source (fda.gov, EMA, etc.) + one sponsor-primary source cited.
- If the outcome narrative uses words like "presumably," "likely," or "may have been," the item belongs in §Key uncertainties with a specific follow-up action.
- **Window discipline:** every item's date field must fall within the declared query window (plus the 30-day trailing context). An out-of-window item is NOT parked in §Uncertainties; it is either moved to §90 days – 12 months (forward-looking) or removed (past).

### Recurring monitoring

Same structure, with additional "**changes since last refresh**" section at top listing newly added, removed, or resolved catalysts.

---

## Catalyst taxonomy

| Type | Primary source | Typical horizon |
|------|---------------|-----------------|
| PDUFA action date | FDA (published with acceptance notice) + company 8-K | 6-10 months post-acceptance |
| CHMP opinion | EMA CHMP monthly agenda (published ~1mo ahead) | Monthly cycle |
| AdComm meeting | FDA Advisory Committee Calendar | 2-3 months notice |
| Phase 3 readout | ClinicalTrials.gov primary completion date + company guidance | Variable |
| Phase 2 readout | ClinicalTrials.gov PCD + guidance | Variable |
| Earnings release | IR calendar | Quarterly |
| Investor / R&D Day | IR calendar | Annual / semi-annual |
| Conference late-breaker | Conference program + company "upcoming presentations" | 1-3 weeks before presentation |
| Paragraph IV certification | FDA Paragraph IV list + originator response | As filed |
| PTAB IPR institution / decision | PTAB docket | Per docket |
| IRA negotiation event | CMS annual release | Once per year |
| AdComm brief publication | 2 business days before AdComm | 2 days before AdComm |

---

## Phase 2 — Discovery

Depending on the watchlist scope:

### For a single ticker / company

1. **SEC EDGAR 8-K RSS** for the CIK (last 90d + forward calendar from IR)
2. **Company IR "Events" / "Upcoming" page** (Fetch)
3. **ClinicalTrials.gov MCP**: `sponsor=<company>, status IN (ACTIVE_NOT_RECRUITING, RECRUITING), phase=PHASE3, primary_completion_date_from=<today>, primary_completion_date_to=<today+18mo>`
4. **FDA Advisory Committee Calendar** (Fetch) — scan for company/asset names
5. **CHMP agenda** (Fetch) — scan upcoming meeting
6. **Tavily** (news, 30d): `"<company> catalyst OR readout OR PDUFA"`

### For a specific asset

1. **ClinicalTrials.gov MCP**: `intervention=<INN/brand>` active + upcoming
2. **FDA pending PDUFA lists** (Fetch) — if the asset has a pending NDA/BLA, company 8-K usually disclosed acceptance + PDUFA date
3. **EMA pending evaluations** — less directly published; triangulate via company guidance + CHMP agenda look-ahead
4. **Conference programs** for upcoming presentations (sponsor "upcoming presentations")

### For a therapeutic area / modality

1. **ClinicalTrials.gov MCP**: filter on condition + phase=PHASE3 + PCD next 12mo
2. **FDA AdComm Calendar** scan for TA
3. **CHMP agenda** scan
4. **Conference programs** (ASCO / ASH / ESMO / AHA / EHA / EASD — major TA conferences)
5. **Tavily** domain-scoped to pharma media

### For a broader watchlist (e.g., whole pipeline)

Use a combination of the above + systematic sponsor IR page polling.

---

## Phase 3 — Validation (converting signals to confirmed dated catalysts)

For each identified potential catalyst:

1. **Date-anchor primary source:**
   - PDUFA dates: company 8-K disclosing FDA acceptance letter (contains PDUFA action date)
   - CHMP: listed on CHMP agenda PDF
   - AdComm: FDA calendar
   - Clinical readout: company guidance in earnings call or press release (ClinicalTrials.gov PCD is a study-level estimate; company guidance is usually more current)
   - Earnings: IR calendar
2. **Cross-check freshness:** company guidance updates during earnings calls; read the most recent transcript
3. **Assess significance:**
   - First approval in a class → high
   - Label expansion → medium
   - Phase 3 primary endpoint readout for single-asset biotech → critical
   - Phase 2 readout for single-asset biotech → high
   - Phase 2 subgroup readout at conference → medium
4. **Source-stamp** per triangulation protocol

---

## Phase 4 — Triangulation

- **Date confirmation** requires at least 2 sources: primary regulatory calendar + company guidance
- **Readout date confirmation**: ClinicalTrials.gov PCD + company IR guidance
- Flag any date that rests on single source as Medium confidence

## Phase 5 — Report

Tabular output. Every row stamped with source + date accessed. A "Data cutoff" line at top.

---

## Operational notes

### PDUFA specifically

- **Sponsor 8-K** upon NDA/BLA acceptance is the **authoritative** disclosure of the action date — always check first
- **SEC 10-K / 10-Q forward guidance:** if an 8-K cannot be located, the sponsor's latest 10-K often carries language such as "accelerated approval in the first half of 2026" or "expected PDUFA action date in Q2 2026" in the Business / Pipeline section. This is corporate-guidance-level precision (quarterly, not daily) but is authoritative at that resolution and carries statutory weight.
- **Class discipline:** Class I resubmission = 2mo review; Class II = 6mo; standard NDA = 10mo
- Priority Review shortens standard to 6mo
- Major Amendment (e.g., late CMC submission) can extend review by 3mo — sponsor must disclose via 8-K
- "Approximately [month]" guidance in a press release means a +/- 30-day window is reasonable
- **Inferred PDUFA dates** (sponsor-acceptance + 6mo standard Priority Review calculation without an explicit date disclosure) are **Medium confidence**, never High. Flag the inference in the provenance stamp.

### PDUFA lookup chain — in order
1. Sponsor 8-K (primary) via SEC EDGAR full-text search or sponsor IR page
2. Sponsor 10-K / 10-Q forward guidance (statutory filing fallback)
3. Sponsor press release (primary but less formal)
4. FDA acceptance announcement (if a public AdComm or drug approval listing exists)
5. Industry media aggregations (tertiary — cap Medium confidence)

### CHMP

- CHMP meets monthly (~5 days)
- Agenda published typically the week before
- Opinion does not equal Commission decision; Commission ~67 days later, rarely diverges
- Positive/negative/withdrawn opinions published in "Highlights" within 48 hours of meeting close

### AdComm

- Briefing documents published **2 business days** before the meeting
- This is a catalyst in itself — briefing documents can move markets more than the AdComm vote
- Public voting after 8 CFR Part 14 procedure; webcast available

### Conference late-breakers

- ASCO: late-breakers announced ~2-3 weeks pre-meeting in press release
- ASH: similar timeline
- ESMO: similar
- Oral presentations at major sessions often more impactful than posters
- Company "upcoming presentations" on IR page is a reliable forward indicator

### Earnings

- Calendar set quarterly; guidance may shift by 1-2 weeks
- Pre-announcement common for large misses
- Guidance issued during call on: next readout timing, new trial starts, PDUFA expectation

### Paragraph IV

- FDA publishes list; originator has 45 days to file infringement suit to trigger 30mo stay
- Exchange between company 8-K and list update

---

## Watchlist maintenance (recurring mode)

If the user asks for a recurring catalyst watch:
1. Persist the watchlist definition (asset list or ticker list)
2. At each refresh, rerun Phase 2 discovery
3. Compare to prior snapshot
4. Surface: new additions, date changes, resolved catalysts + outcome
5. Refresh the Data cutoff line

### Suggested refresh cadence

- Daily: not practical at pharmaintel scope; agent-automated monitoring appropriate
- Weekly: fits most use cases (covers Monday-Friday 8-K filings + IR updates)
- Monthly: fits strategic reviews

---

## Significance rating rubric

When ranking catalysts by significance for the user:

| Rating | Criteria |
|--------|----------|
| Critical | First-in-class FDA approval; registrational Ph3 primary endpoint readout for single-asset company; AdComm with known split view |
| High | Label expansion for major product; Ph3 primary endpoint readout in competitive class; M&A announcement |
| Medium | Ph2 primary endpoint readout; routine PDUFA extension; conference late-breaker in non-pivotal trial |
| Low | Investigator-initiated trial readout; subgroup analysis of already-reported data; non-consequential regulatory housekeeping |

Stamp each row with a significance rating in the table.

---

## Limitations

- Not all catalysts have publicly-disclosed dates ("H2 2026" guidance is common)
- Private companies — IR page is not mandatory; visibility limited
- Company guidance is not a commitment — slip risk is real
- Regulatory surprise exists — e.g., an out-of-cycle FDA safety action
- Conference late-breakers may be under embargo

---

## Protocol compliance checklist (self-audit before handing off)

Before finalizing any T5 catalyst watch report, Claude runs through this list. If any answer is "no," the report is marked draft-only and the relevant remediation is performed.

| # | Check | Remediation if fail |
|---|---|---|
| 1 | Was `tool_search` invoked for Clinical Trials + PubMed + Fetch + (Paper Search if pivotal-backed) before Phase 2? | Run activations now; re-execute Phase 2 with MCP-native fetches |
| 2 | For each pivotal-readout-backed catalyst, has a `Paper Search:search_pubmed` or `Consensus:search` query been run to check for peer-reviewed publication? | Run it; if publication exists, rewrite the stamp and numbers per triangulation.md §6.1 |
| 3 | For each PDUFA entry, has at least one attempt been made to retrieve the sponsor 8-K / 10-K via SEC EDGAR or sponsor IR? | Run it; downgrade to Medium if only industry media can be cited |
| 4 | Every entry in §Recently resolved has a known outcome with a primary regulatory source (fda.gov, EMA, etc.)? | Move unknown-outcome entries to §Key uncertainties |
| 5 | Every entry's date field falls within the declared query window (plus trailing-30d context)? | Remove out-of-window entries; do NOT park in §Uncertainties |
| 6 | For any Türkiye-context claim, have the pivotal trial's ClinicalTrials.gov locations been checked for Turkish sites? | Run `get_trial_details`; revise geographic reach claims based on actual site list |
| 7 | Every p-value and 95% CI stamped at High is from a peer-reviewed publication, not a PR? | Downgrade to Medium + flag "peer-review pending" |
| 8 | Out-of-window items (past or beyond horizon): removed, or correctly placed in §90d–12mo (forward) / §Context (past trailing-30d only)? | Re-sort; drop truly out-of-scope items |

A report that passes 8/8 is production-grade. A report that fails ≥2 is returned to discovery phase, not shipped.

---

## Geography verification (useful for Türkiye-context users and any non-US layer)

When a user asks for catalyst analysis *with a regional interpretation layer* (Türkiye strategic implications, EU pricing layer, APAC access, etc.), Claude MUST verify the geographic claim against the pivotal trial's actual ClinicalTrials.gov `locations` field before asserting any regional interpretation.

Common failure mode: generic statements like "Türkiye için erken erişim paterni beklenir" written for a trial that had zero Turkish sites. The fix is one `get_trial_details` call.

Suggested phrasing templates:
- **Türk merkezi olan çalışma:** "[Trial] programına Türkiye [N] merkezle katıldı ([merkez isimleri])"
- **Türk merkezi olmayan çalışma:** "[Trial] çalışmasında Türk klinik merkezi yer almadı; Türkiye'ye erişim baştan planlanmayı gerektirir"
- **Tek-bölgeli çalışma:** "[Trial] X-only (N site); ex-X erişim post-approval mekanizmalara bağımlıdır"

These templates are not mandatory but they reflect a verification pattern that the T5 correction cycle showed is material.

Surface these in §Limitations explicitly.
