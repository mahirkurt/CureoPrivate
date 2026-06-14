# sub-protocol-provenance.md

**Sub-Protocol — Forensic Capture Orchestration (v5.0.0)**

> **Purpose:** Direct orchestration sub-protocol for activating the Forensic Provenance Layer. Coordinates L0-L4 workflow (claim identification → source resolution → k-redundant capture → hash + TSA attestation → bundle delivery). Invoked by parent task playbooks (task-company.md, task-asset.md, task-deal.md) or by higher-level sub-protocols (sub-protocol-bd-dd.md, sub-protocol-turkey.md) when forensic-grade evidence required.
>
> **Architectural context:** Extends existing 6 sub-protocols (pmda, sponsor-sweep, label, nmpa, turkey, catalyst-watch). Unique among sub-protocols — produces **two artifacts**: (1) standard pharmaintel report with provenanced footnotes + §Appendix B section, (2) Evidence Bundle ZIP as standalone immutable deliverable.

---

## §1. Activation Triggers

### 1.1 Explicit invocation

User-facing invocations that trigger this sub-protocol:
- "Forensic-grade report on <target>"
- "Kanıt zinciri ile <iddia> belgele"
- "Evidence bundle for TİTCK defense on <asset>"
- "Chain-of-custody documentation for <claim>"
- "UBO walkthrough for <target company>"
- "Provenance-verified analysis of <topic>"

### 1.2 Implicit triggers (claim-content-based)

Parent workflow detects claim types requiring provenance:
```
IF any_claim IN current_report.claims HAS claim_type ∈ {
    "beneficial_ownership",
    "sanctions_hit",
    "regulatory_action",
    "deleted_pipeline_claim",
    "historical_label",
    "titck_opponent_claim",
    "litigation_exhibit"
} THEN activate sub-protocol-provenance
```

### 1.3 Parent sub-protocol chaining

- `sub-protocol-bd-dd.md` → always activates provenance (BD DD is forensic-grade by default)
- `sub-protocol-turkey.md` (TİTCK defense mode) → activates provenance when `mode: "titck-defense"` specified
- `sub-protocol-sponsor-sweep.md` → activates provenance only when sweep output is forensic-grade deliverable

### 1.4 NOT triggered by

- ❌ Standard commercial intelligence reports without regulatory/legal defense context
- ❌ Educational or internal-only research tasks
- ❌ User identity alone (e.g., "Mahir works at Roche, so all reports must be forensic-grade" — NOT valid trigger per `generic-by-default.md` Article 5)

---

## §2. Sub-Protocol Workflow

### 2.1 Step-by-step sequence

```
[INVOCATION — parent task detects provenance trigger]
        ↓
Step 1: Claim Inventory
    └─ Scan report draft for [^prov:...] markup OR auto-detect provenance_required claim types
    └─ Produce claim_list: List[ClaimDraft]
        ↓
Step 2: For each claim in claim_list — parallel-safe:
    ├─ Step 2a: Source Resolution (L1)
    │   └─ Invoke ubo-source-hierarchy.md priority ladder
    │   └─ For UBO: P0 → P1 → P2 → P3 cascade
    │   └─ For other claim types: direct source URL
    │   └─ Produce: primary_url + triangulation_partner_url
    ├─ Step 2b: Capture (L2) — parallel 3-path
    │   ├─ Path A: Wayback Machine SPN2 (if authenticated) or CDX
    │   ├─ Path B: Archive.is submit (Playwright form POST)
    │   └─ Path C: Local Playwright fullpage + WARC + HAR
    │   └─ Produce: wayback_url, archive_is_url, fallback_paths
    ├─ Step 2c: Attestation (L3)
    │   ├─ SHA-256 + BLAKE3 hash all artifacts
    │   ├─ Manifest digest via CBOR
    │   ├─ RFC 3161 TSA (DigiCert primary + FreeTSA fallback)
    │   └─ Sigstore cosign keyless OR GPG fallback
    │   └─ Produce: integrity + custody blocks
    └─ Step 2d: Evidence Object Emission
        └─ Serialize complete YAML per evidence-object-schema.md
        └─ Insert SQLite evidence index row
        └─ Return evidence_id to parent
        ↓
Step 3: Report Integration
    ├─ Replace claim_list markers in report draft with [^prov:ev_<id>] footnotes
    ├─ Append §Appendix B — Evidence Bundle Manifest section
    └─ Generate bundle_manifest.yaml listing all evidence_ids
        ↓
Step 4: Validation
    └─ Invoke validate-report-discipline.py --mode forensic-grade
    └─ Gates G51-G60 must all pass GREEN
    └─ On BLOCKER: halt + return error to parent
        ↓
Step 5: Bundle Delivery (L4)
    ├─ Build Evidence Bundle ZIP:
    │   ├── MANIFEST.yaml (all evidence_ids + hashes + TSRs)
    │   ├── README.md (verification instructions)
    │   ├── evidence/ (all artifact files)
    │   └── VERIFICATION.md (openssl ts -verify + cosign verify scripts)
    ├─ Compute bundle ZIP SHA-256
    ├─ Update parent report footnote with bundle_hash
    └─ Return bundle_path to parent task
        ↓
[RETURN TO PARENT — with evidence_bundle_zip_path + manifest_summary]
```

### 2.2 Failure modes + retry logic

| Failure | Retry? | Fallback action |
|---|---|---|
| Wayback SPN2 rate limit (429) | YES — exp. backoff up to 3× | Fall through to CDX existing-snapshot discovery |
| Wayback rejects via robots directive | NO | Archive.is + local capture only; flag in Evidence Object `capture_paths_failed` |
| Archive.is Cloudflare CAPTCHA | NO | Local Playwright + WARC only (still satisfies G53/G-PROV-03 if 2+ of 3) |
| Local Playwright timeout | YES — 2× with increased timeout | Fall through to `curl_wget` simpler fetch (WARN in EO) |
| All 3 capture paths fail | NO | Halt + return error to parent; emit incident log entry |
| RFC 3161 TSA DigiCert unavailable | YES | Fall through to FreeTSA |
| Both TSAs unavailable | NO | Baseline mode: WARNING + continue; Forensic-grade mode: BLOCKER + halt |
| Sigstore OIDC flow fails | YES | Fall through to GPG local signing if key available; else unsigned (forensic-grade BLOCKER) |
| P0 national registry unavailable | NO | Fall through P1 aggregator per ubo-source-hierarchy.md §1.1 rules |

### 2.3 Parallel-safety annotations

Per `orchestration.md` v3.0.0 parallel-safe sub-protocol framework:

**Parallel-safe** (concurrent across different claims):
- Step 1 (claim inventory)
- Step 2a (source resolution) — independent per claim
- Step 2b (3-path capture) — independent per claim
- Step 2c (attestation) — independent per claim
- Step 2d (evidence object emission) — independent per claim

**Serial-only** (must complete in order):
- Step 3 (report integration) — requires all evidence_ids from Step 2
- Step 4 (validation) — requires complete report + evidence index
- Step 5 (bundle delivery) — requires validated report

**Within Step 2 (single claim), 3-path capture is parallel-safe:**
- Path A (Wayback) + Path B (Archive.is) + Path C (Local Playwright) run concurrently via async task group
- Cache key: `(primary_url, YYYY-MM-DD)` — same URL captured same day deduplicates

---

## §3. Cache Key Taxonomy

Extends `orchestration.md` cache framework for forensic context:

### 3.1 Source resolution cache

```
Key: "ubo:{entity_name}:{jurisdiction}:{sha256(search_params)}"
TTL: 7 days (UBO data lag-acceptable per §9.2 ubo-source-hierarchy.md)
Invalidation: Explicit operator flag or source freshness breach
```

### 3.2 Capture cache

```
Key: "capture:{sha256(primary_url)}:{YYYY-MM-DD}"
TTL: Permanent (once captured, immutable by design)
Invalidation: Never (new capture creates new evidence_id)
```

### 3.3 Hash cache

```
Key: "hash:{artifact_path}:{sha256/blake3}"
TTL: Permanent (deterministic)
Invalidation: Never
```

### 3.4 TSA request cache

```
Key: "tsa:{manifest_digest}:{tsa_url}"
TTL: Permanent (timestamps are immutable once issued)
Invalidation: Never
```

---

## §4. Output Contract

### 4.1 Primary output — Parent report with forensic footnotes

Every provenanced claim in parent report rendered as:

```markdown
<claim text with embedded fact> [^prov:ev_<evidence_id>].

[^prov:ev_<id>]: <claim_text> — Source: <source_name>
    | Retrieved: <ISO 8601 UTC>
    | Archive: <wayback_url OR archive_is_url OR fallback_ref>
    | SHA-256: <content_hash_sha256 first 16 chars>…
    | TSA: <tsa_url>
    | Bundle: <bundle_zip_path>
```

Footnotes auto-generated from Evidence Objects — no manual authorship.

### 4.2 Primary output — §Appendix B Evidence Bundle Manifest

Structured markdown section appended to every forensic-grade report:

```markdown
## §Appendix B — Evidence Bundle Manifest

Bu raporda cite edilen tüm provenance'lı iddialar bir **Evidence Bundle ZIP** olarak
teslim edilmiştir.

**Bundle dosyası:** `<bundle_path>`
**Bundle SHA-256:** `<bundle_hash>`
**Total evidence objects:** <N>
**Capture period:** <earliest_retrieved_at> → <latest_retrieved_at> (<duration_days> gün)
**Forensic-grade mode:** <baseline | forensic-grade>
**Validator gates passed:** G51-G60 (10/10)

### Doğrulama

Bundle integrity:

    sha256sum <bundle_filename>.zip
    # Beklenen: <bundle_hash>

Her evidence object TSR doğrulama:

    openssl ts -verify -data evidence/pdf/ev_<id>.pdf \
        -in evidence/tsr/ev_<id>.tsr \
        -CAfile tsa-ca-bundle.pem

Sigstore cosign signature verification:

    cosign verify-blob --signature evidence/sig/ev_<id>.sig \
        --certificate-identity <signer_email> \
        --certificate-oidc-issuer <oidc_provider> \
        evidence/<artifact>

### Evidence Index

| Evidence ID | Claim | Tier | Captured | Archive Paths | Hash (SHA-256 head) |
|---|---|---|---|---|---|
| ev_<id_1> | <claim_summary_1> | <tier> | <date> | W+A+L / W+L / A+L | <hash[:16]>… |
| ev_<id_2> | <claim_summary_2> | <tier> | <date> | W+A+L | <hash[:16]>… |
| ... | ... | ... | ... | ... | ... |

### Jurisdictional Compliance

- **KVKK (6698 SK):** Madde 5/2(ç) meşru menfaat temelli capture. Kişisel veri
  içeren iddialar maskelenmiş (N=<pii_redacted_count>).
- **GDPR Art. 6(1)(f):** Legitimate interest — regulatory defense + commercial DD.
- **Retention:** <N> yıl (default 7 — TİTCK denetim zamanaşımı + GDPR storage limit).
```

### 4.3 Standalone output — Evidence Bundle ZIP

```
<report_id>_evidence_bundle.zip
├── MANIFEST.yaml                      # all evidence_ids + metadata + hashes
├── README.md                          # orientation for evidence bundle recipient
├── VERIFICATION.md                    # step-by-step verification scripts
├── LICENSE                            # pharmaintel bundle usage license
├── evidence/
│   ├── ev_YYYY-MM-DD_xxxxxxxx.pdf
│   ├── ev_YYYY-MM-DD_xxxxxxxx.png
│   ├── ev_YYYY-MM-DD_xxxxxxxx.html
│   ├── ev_YYYY-MM-DD_xxxxxxxx.warc.gz
│   ├── ev_YYYY-MM-DD_xxxxxxxx.har
│   ├── ev_YYYY-MM-DD_xxxxxxxx.sig     # sigstore cosign signature
│   ├── ev_YYYY-MM-DD_xxxxxxxx.tsr     # RFC 3161 TSA primary
│   ├── ev_YYYY-MM-DD_xxxxxxxx.freetsa.tsr  # RFC 3161 TSA fallback
│   └── ... (per evidence object)
├── provenance.db.sqlite               # SQLite evidence index (copy)
└── chain-walk/                        # optional — UBO investor chain visualizations
    ├── chain_<target_name>.svg
    └── chain_<target_name>.md
```

### 4.4 Return to parent task

Sub-protocol-provenance returns to parent:

```yaml
return:
  status: "success" | "partial" | "failed"
  evidence_count: <N>
  evidence_bundle_zip_path: "<path>"
  evidence_bundle_zip_sha256: "<hash>"
  validator_result:
    gates_passed: ["G51", "G52", ..., "G60"]
    gates_failed: []
    gates_warned: []
  evidence_ids: ["ev_<id_1>", "ev_<id_2>", ...]
  appendix_b_markdown: "<content>"
  footnote_replacements: {"[^claim_1]": "[^prov:ev_<id_1>]", ...}
  total_duration_seconds: <float>
```

---

## §5. Integration Points

### 5.1 With `provenance-engine.md` capability framework

Sub-protocol-provenance is the **invocation surface** for the provenance-engine capability. Capability framework defines **what**; sub-protocol defines **when + how to orchestrate**.

### 5.2 With `evidence-object-schema.md`

Each Step 2d emission produces exactly one Evidence Object conforming to schema v1.0. Schema violation → Step 4 validator halt.

### 5.3 With `ubo-source-hierarchy.md`

Step 2a invokes the P0→P3 ladder per source hierarchy priority. Triangulation enforcement at G56/G-PROV-06.

### 5.4 With existing sub-protocols

| Existing sub-protocol | Integration |
|---|---|
| `sub-protocol-pmda.md` | PMDA filing snapshots trigger provenance when historical label context required |
| `sub-protocol-sponsor-sweep.md` | Sweep outputs trigger provenance when findings used for BD/regulatory purposes |
| `sub-protocol-label.md` | Historical label reconstruction triggers provenance (deleted_pipeline_claim or historical_label) |
| `sub-protocol-nmpa.md` | NMPA CDE filing snapshots, especially when contested |
| `sub-protocol-turkey.md` | TİTCK defense mode triggers provenance automatically |
| `sub-protocol-catalyst-watch.md` | Catalyst readout snapshots for post-readout commercial analysis |
| `sub-protocol-bd-dd.md` (v5.0.0 new) | Every BD DD triggers full provenance workflow |

### 5.5 With capability frameworks

| Capability framework | Integration |
|---|---|
| `analytics-framework.md` | Confidence stamping downgrade when inputs lack provenance; forensic-grade claims marked HIGH confidence |
| `api-integrations.md` | L2 capture extends priority hierarchy — every fetch in forensic mode triggers 3-path attestation |
| `orchestration.md` | Parallel-safe annotations for Step 2a-2d; serial execution Steps 3-5 |
| `provenance-engine.md` (v5.0.0 new) | This sub-protocol is primary invocation of provenance-engine capability |

### 5.6 With report rendering

- **carbon-pptx:** §Appendix B rendered as terminal slide appendix with footnote-reference slides
- **carbon-html-report:** §Appendix B rendered as distinct HTML section with expandable evidence entries + bundle ZIP download button
- **markdown-only:** §Appendix B preserved as standard Markdown for email/document distribution

---

## §6. Invocation Examples

### 6.1 Direct user invocation

```
User: "Forensic-grade report on Company X UBO + sanctions check before Roche BD meeting"

Task routing:
  → task-company.md (primary task)
  → sub-protocol-bd-dd.md (BD DD context detected)
  → sub-protocol-provenance.md (auto-activated by sub-protocol-bd-dd)
  → provenance-engine + 3-path capture + attestation + bundle

Output:
  → report.md (standard pharmaintel report with [^prov:...] footnotes + §Appendix B)
  → rpt_company_x_ubo_evidence_bundle.zip (standalone deliverable)
```

### 6.2 Parent task explicit invocation

```yaml
# In task-company.md execution context:
invoke_sub_protocol:
  name: "sub-protocol-provenance"
  mode: "forensic-grade"
  claim_filter: ["beneficial_ownership", "sanctions_hit", "litigation_exhibit"]
  output:
    evidence_bundle_zip: true
    appendix_b_section: true
    footnote_replacement: true
```

### 6.3 Implicit chaining via sub-protocol-turkey TİTCK defense mode

```yaml
# sub-protocol-turkey.md activates with:
mode: "titck-defense"
→ Automatically chains sub-protocol-provenance with forensic-grade
→ Historical opponent claims → deleted_pipeline_claim → provenance required
→ Bundle delivered alongside TİTCK commission presentation
```

---

## §7. Operational Discipline

### 7.1 Minimum viable invocation

Every provenance sub-protocol invocation MUST produce at least:
1. ≥1 Evidence Object fully conforming to schema v1.0
2. ≥2 of 3 capture paths succeeded per Evidence Object
3. SHA-256 content hash computed + stored
4. SQLite evidence index row inserted
5. §Appendix B section rendered
6. Evidence Bundle ZIP emitted with MANIFEST.yaml + README.md

### 7.2 Forensic-grade additional requirements

Forensic-grade mode (vs baseline) additionally requires:
1. RFC 3161 TSR file present for every Evidence Object
2. Sigstore cosign signature (or GPG fallback)
3. All 10 gates G51-G60 BLOCKER-level enforced
4. Bundle ZIP SHA-256 cited in parent report (G60)
5. KVKK meşru menfaat memorandum reference (if KVKK applies)

### 7.3 Failure escalation

When BLOCKER-level gate fails in forensic-grade mode:
1. **Halt sub-protocol immediately** — do not produce partial bundle
2. **Log incident** in `evidence/manifest/incidents.log` with timestamp + failure reason + context
3. **Return to parent** with `status: "failed"` + `blocking_gate: "G<NN>"` + remediation suggestion
4. **Operator action required** — parent task informs user that forensic-grade deliverable requires operator intervention

### 7.4 KVKK/GDPR compliance discipline

Per `provenance-engine.md` §6:
- Every Evidence Object with `contains_personal_data: true` MUST have `pii_redaction_applied: true` (G58)
- Capture of kişisel veri içerir sayfa (e.g., KOL personal LinkedIn) **not permitted** under pharmaintel scope
- Retention 7 years + cryptographic destruction at expiry
- `jurisdiction_of_capture: "TR"` → KVKK applies; additional jurisdictions trigger GDPR + local DPA framework

### 7.5 Red-line: Passive OSINT only

Sub-protocol-provenance permits ONLY:
- HTTP GET requests (no state-changing methods)
- Wayback Machine SPN2 + CDX (read-only archive)
- Archive.is submission (one-shot)
- Playwright headless (client-side render, no probing)

Excluded: vulnerability scanning, CAPTCHA bypass, credential stuffing, zone transfer abuse, active form submission beyond Archive.is.

Violation → immediate sub-protocol termination + incident log + no evidence emission.

---

## §8. Pricing Reality Discipline

Free tier operational envelope (within single BD DD engagement):
- Wayback SPN2: 12 req/min × 60 min × 24 hr = 17,280 captures/day (practical ceiling ~1,000/day per IP)
- Archive.is: ~1-2 submissions/min practical
- Local Playwright: limited by operator CPU (typical 500-1,000 captures/day)
- DigiCert TSA: no documented rate limit; reasonable use
- FreeTSA: no documented rate limit; reasonable use
- Companies House UK: 600/5min = ~170K/day practical
- OpenCorporates free: 200/month (quickly exhausted for BD DD)

**Practical daily throughput per DD engagement:** ~50-200 evidence objects for typical target company investigation. Higher volumes require:
- OpenCorporates paid tier ($99/mo)
- KvK NL paid per-query (if Netherlands exposure)
- Prioritized P0 captures with lower-priority P1-P3 batched

---

## §9. Versioning & Changelog

- **v5.0.0 (2026-04-16):** Initial release. Sub-protocol-provenance establishes direct orchestration surface for Forensic Provenance Layer. Parallel-safe 5-step workflow (claim inventory → source resolution → k-redundant capture → attestation → bundle delivery). Per-step failure modes + retry logic (Wayback rate limit + Archive.is CAPTCHA + Playwright timeout + TSA unavailability + sigstore OIDC fail). Parallel-safety annotations per orchestration.md v3.0.0 framework — Step 2a/2b/2c/2d per-claim parallel; Steps 3-5 serial. Cache key taxonomy (source resolution TTL 7d + capture permanent + hash permanent + TSA permanent). Output contract — primary parent report with forensic footnotes + §Appendix B Evidence Bundle Manifest section + standalone Evidence Bundle ZIP deliverable with MANIFEST.yaml + README.md + VERIFICATION.md + complete evidence/ directory + optional chain-walk visualizations. Integration with existing 6 sub-protocols (pmda + sponsor-sweep + label + nmpa + turkey + catalyst-watch) + new sub-protocol-bd-dd (v5.0.0). Invocation examples (direct user + parent task + implicit chaining). Operational discipline (minimum viable invocation + forensic-grade additional requirements + failure escalation halt-and-log + KVKK/GDPR compliance + passive OSINT red-line). Pricing reality (~50-200 evidence objects/day typical DD throughput within free-tier envelope). Cross-references: provenance-engine.md (capability framework), evidence-object-schema.md (schema conformance), ubo-source-hierarchy.md (L1 source ladder), validate-report-discipline.py (G51-G60 gates), scripts/provenance-engine/ (runtime module).
