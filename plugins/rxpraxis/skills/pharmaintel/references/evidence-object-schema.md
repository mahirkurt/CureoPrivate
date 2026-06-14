# evidence-object-schema.md

**Canonical Data Model Reference — Evidence Object Schema (v5.0.0)**

> **Purpose:** Defines the standardized YAML schema for all forensic-grade pharmaceutical intelligence claims. Every provenanced claim produces exactly one Evidence Object conforming to this schema. Consumed by `scripts/provenance-engine/evidence_object.py` for validation + by `carbon-pptx` / `carbon-html-report` rendering pipelines for footnote + appendix integration.
>
> **Architectural context:** Schema reference for `provenance-engine.md` capability framework. Referenced by `sub-protocol-provenance.md` + `sub-protocol-bd-dd.md` workflows. Cross-referenced by `validate-report-discipline.py --mode forensic-grade` gates G51-G60.

---

## §1. Schema Version & Evolution

**Current schema version:** `evidence-object-schema v1.0` (released with pharmaintel v5.0.0)

**Evolution policy:**
- Additive fields → minor version bump (v1.0 → v1.1)
- Required field changes → major version bump (v1.0 → v2.0)
- Schema version declared in each Evidence Object YAML via `schema_version: "1.0"` top-level field
- Parser maintains backward compatibility with all v1.x schemas

---

## §2. Complete Schema Specification

### 2.1 Top-level structure

```yaml
# evidence-object.schema.yaml (v1.0)
schema_version: "1.0"                      # REQUIRED — schema contract version
evidence_id: "ev_<YYYY-MM-DD>_<sha256_8>"  # REQUIRED — deterministic ID
claim_text: <str>                           # REQUIRED — human-readable claim
claim_type: <enum>                          # REQUIRED — see §3.1
claim_domain: <enum>                        # REQUIRED — see §3.2
source: <source_block>                      # REQUIRED — L1 provenance
archive: <archive_block>                    # REQUIRED — L2 temporal attestation
integrity: <integrity_block>                # REQUIRED — L3 content hashes
custody: <custody_block>                    # OPTIONAL — L4 chain-of-custody
cross_refs: <cross_refs_block>              # REQUIRED — report integration
compliance: <compliance_block>              # REQUIRED — GDPR/KVKK
```

### 2.2 Full annotated example

```yaml
schema_version: "1.0"
evidence_id: "ev_2026-04-16_7f3a2b1e"      # deterministic: date + sha256(primary_url)[0:8]
claim_text: "Company X is ultimately owned by Fund Y via a Luxembourg SCSp vehicle"
claim_type: "beneficial_ownership"
claim_domain: "corporate_structure"

# L1 — Source provenance
source:
  authority_tier: "OSINT-T1"                # see §4.1 for tier definitions
  primary_url: "https://find-and-update.company-information.service.gov.uk/company/12345678/persons-with-significant-control"
  source_name: "UK Companies House PSC Register"
  retrieved_at: "2026-04-16T09:34:22Z"      # ISO 8601 UTC, strict format
  retriever_agent: "pharmaintel-provenance-engine/5.0.0"
  http_status: 200
  content_type: "text/html; charset=utf-8"
  content_length_bytes: 184726
  content_encoding: "gzip"                   # optional
  ssl_fingerprint: "sha256:bf5e..."          # optional — TLS cert fingerprint
  
# L2 — Temporal attestation (Web Archive)
archive:
  wayback_url: "https://web.archive.org/web/20260416093500/https://find-and-update.company-information.service.gov.uk/company/12345678/persons-with-significant-control"
  wayback_timestamp: "20260416093500"        # 14-char Wayback timestamp
  wayback_snapshot_mode: "spn"               # enum: spn | existing | cdx-discovered
  wayback_job_id: "spn2-abc123def456"        # for SPN2 jobs
  archive_is_url: "https://archive.ph/ABc12"
  archive_is_hash: "ABc12"                   # archive.is short hash
  fallback_method: "playwright_fullpage"     # enum: playwright_fullpage | playwright_har | curl_wget | none
  fallback_paths:
    pdf: "evidence/pdf/ev_2026-04-16_7f3a2b1e.pdf"
    png: "evidence/png/ev_2026-04-16_7f3a2b1e.png"
    html: "evidence/html/ev_2026-04-16_7f3a2b1e.html"
    warc: "evidence/warc/ev_2026-04-16_7f3a2b1e.warc.gz"
    har: "evidence/har/ev_2026-04-16_7f3a2b1e.har"
  capture_paths_succeeded: ["wayback", "archive_is", "local"]  # which of 3 succeeded
  capture_paths_failed: []
  capture_duration_seconds: 18.3
  
# L3 — Content attestation
integrity:
  # Per-artifact SHA-256
  content_hash_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # primary HTML
  html_hash_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  pdf_hash_sha256: "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
  png_hash_sha256: "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9"
  warc_hash_sha256: "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
  har_hash_sha256: "0a0a9f2a6772942557ab5355d76af442f8f65e01d1744273278dd16e11f20d4d"
  # BLAKE3 — modern parallel fingerprint
  content_hash_blake3: "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
  # Manifest digest — deterministic CBOR-encoded sorted dict of all hashes
  manifest_digest_sha256: "9a0364b9e99bb480dd25e1f0284c8555e51f2f5dcbc3e8a2b8e3b14fb1eef0d7"
  
# L4 — Chain-of-custody
custody:
  captured_by_identity: "operator@example.org"   # optional; null if skill-autonomous
  capture_environment:
    user_agent: "Mozilla/5.0 (X11; Linux x86_64) pharmaintel-provenance-engine/5.0.0"
    ip_egress_anonymized: true                    # true if no IP logging
    tls_fingerprint: "JA3:e7d705a3286e19ea42f587b344ee6865"
    tls_version: "TLSv1.3"
    platform: "Linux 6.1.0-x86_64"
    playwright_version: "1.41.0"
    chromium_version: "121.0.6167.85"
  signing:
    method: "sigstore_cosign"                     # enum: sigstore_cosign | gpg | none
    signer_identity: "operator@example.org"
    sig_path: "evidence/sig/ev_2026-04-16_7f3a2b1e.sig"
    sig_hash_sha256: "d4a9..."                    # hash of signature file
  timestamp_authority:
    primary:
      protocol: "rfc3161"
      tsa_url: "http://timestamp.digicert.com"
      tsr_path: "evidence/tsr/ev_2026-04-16_7f3a2b1e.tsr"
      tsr_hash_sha256: "9a0364b9..."
      tsa_cert_subject: "DigiCert Timestamp 2024"
      tsa_cert_serial: "0abc123..."
    fallback:                                      # optional secondary TSA
      protocol: "rfc3161"
      tsa_url: "https://freetsa.org/tsr"
      tsr_path: "evidence/tsr/ev_2026-04-16_7f3a2b1e.freetsa.tsr"
      tsr_hash_sha256: "ff12..."

# Report integration
cross_refs:
  parent_report_id: "rpt_glofitamab_titck_v3"
  cited_in_sections: ["§4.2", "§Appendix-B-Evidence-Bundle"]
  triangulation_partner_ids:
    - "ev_2026-04-16_a91b3c4d"                  # second source for triangulation
  skill_composition_chain:
    - "pharmaintel:sub-protocol-bd-dd"
    - "pharmaintel:sub-protocol-provenance"
    - "carbon-pptx:footnote-render"
  evidence_bundle_zip_path: "evidence/bundle/rpt_glofitamab_titck_v3_evidence_bundle.zip"

# Jurisdictional compliance
compliance:
  gdpr_lawful_basis: "art_6_1_f_legitimate_interest"
  kvkk_applies: true
  kvkk_article: "madde_5_2_c"                    # meşru menfaat
  contains_personal_data: false                   # CRITICAL — triggers G58 if true
  pii_redaction_applied: false                    # mandatory true if contains_personal_data
  pii_redaction_method: null                      # e.g. "ner_blackbox", "dom_scrub"
  retention_policy: "7_years"
  retention_until: "2033-04-16"
  jurisdiction_of_capture: "TR"
  lawful_basis_memorandum_ref: "docs/legal/kvkk-mesru-menfaat-memo-2026-q1.pdf"  # optional
```

---

## §3. Enumeration Specifications

### 3.1 `claim_type` enumeration

Claims are classified by forensic defensibility requirements:

| Value | Use case | Provenance required? | G51-G60 all BLOCKER? |
|---|---|---|---|
| `beneficial_ownership` | UBO claim, parent structure, investor chain | YES | YES |
| `sanctions_hit` | OFAC SDN / EU / UK HMT match | YES | YES |
| `regulatory_action` | FDA 483, Warning Letter, EMA CHMP action | YES | YES |
| `deleted_pipeline_claim` | Sponsor pipeline page since deleted | YES | YES |
| `historical_label` | Prior drug label version (pre-relabeling) | YES | YES |
| `titck_opponent_claim` | Competing sponsor's historical claim for TİTCK defense | YES | YES |
| `litigation_exhibit` | Evidence for patent/IP/product liability litigation | YES | YES |
| `commercial_claim` | Standard market size, sales estimates | NO (baseline) | NO |
| `trial_endpoint` | ClinicalTrials.gov primary endpoint | NO (baseline) | NO |
| `guideline_quote` | NCCN/ESMO/ASCO guideline citation | NO (baseline) | NO |
| `other` | Uncategorized | CASE-BY-CASE | CASE-BY-CASE |

**Claim type → provenance_required mapping** is enforced at G51/G-PROV-01 by validator.

### 3.2 `claim_domain` enumeration

Aligned with existing pharmaintel task taxonomy:

```
corporate_structure      # UBO, parent, subsidiary, JV
sanctions_compliance     # OFAC, EU, UK HMT, UN
regulatory_fda           # FDA 483, WL, Complete Response, approvals
regulatory_ema           # EMA CHMP, PRAC actions
regulatory_titck         # TİTCK commission, ruhsat
regulatory_pmda          # PMDA, MHLW
regulatory_nmpa          # NMPA CDE
regulatory_other         # MHRA, Health Canada, TGA, Swissmedic
clinical_trial           # CT.gov registration, protocols, amendments
clinical_outcome         # publication, press release, ODAC/CHMP readout
label_content            # current or historical FDA label, SmPC, PMDA添付文書
commercial_market        # sales, forecasts, IQVIA
pipeline_asset           # sponsor pipeline page, corporate presentation
deal_transaction         # M&A, licensing, royalty, option
patent_ip                # patent claim, Orange Book, Purple Book, patent dance
litigation_procedural    # docket entry, filing, discovery
ma_due_diligence         # target assessment, risk register
other                    # uncategorized
```

### 3.3 `authority_tier` enumeration

Defines court-defensibility tier. Used for triangulation logic (see `triangulation.md` + `ubo-source-hierarchy.md`):

| Tier | Definition | Examples |
|---|---|---|
| **T0** | Statutory primary (regulatory authority filings, government gazettes) | FDA Drugs@FDA, EMA EPAR, TİTCK commission minutes, Resmi Gazete, SEC EDGAR, Orange/Purple Book |
| **T1** | Peer-reviewed scientific | NEJM, JAMA, Lancet, peer-reviewed journals with impact factor |
| **T2** | Authorized commercial press (primary quotes + attribution) | FiercePharma + BioPharma Dive + Endpoints with direct sponsor attribution |
| **T3** | Sponsor IR material | Corporate press releases, investor presentations, 10-K/20-F |
| **T4** | Authorized aggregators | Evaluate Vantage, IQVIA Institute reports |
| **T5** | Commercial intelligence services | Citeline Pharmaprojects, Cortellis, Pharmaprojects (NOT in free tier) |
| **T6** | Secondary press | Industry blogs, generic news |
| **T7** | Unattributed / anonymous | Reddit, forums, unverified social media |
| **OSINT-T1** | Primary authority public registries | Companies House UK, Handelsregister DE, MERSİS TR, Ticaret Sicili Gazetesi |
| **OSINT-T2** | Authorized aggregators | OpenCorporates, OpenOwnership BODS |
| **OSINT-T3** | Investigative | OCCRP Aleph, ICIJ Offshore Leaks |

### 3.4 `wayback_snapshot_mode` enumeration

| Value | Meaning |
|---|---|
| `spn` | Save Page Now 2 — new capture requested on-demand |
| `existing` | Already existing Wayback snapshot (closest in time) |
| `cdx-discovered` | Discovered via CDX API query for historical snapshot |

### 3.5 `fallback_method` enumeration

| Value | Meaning |
|---|---|
| `playwright_fullpage` | Chromium headless fullpage (PDF+PNG+HTML+WARC+HAR) |
| `playwright_har` | Chromium headless with HAR recording only |
| `curl_wget` | Command-line fetch (no JS rendering — last resort for non-JS content) |
| `none` | No fallback attempted (Wayback+Archive.is both succeeded) |

### 3.6 `signing.method` enumeration

| Value | Description | Trust model |
|---|---|---|
| `sigstore_cosign` | Keyless signing via OIDC (GitHub/Google/Microsoft) | PKI + OIDC identity provider |
| `gpg` | Traditional GPG with local signing key | Web of trust |
| `hsm_pkcs11` | Hardware Security Module via PKCS#11 | Hardware root of trust |
| `none` | Unsigned | No operator identity attestation |

### 3.7 `timestamp_authority.protocol` enumeration

| Value | Standard |
|---|---|
| `rfc3161` | IETF RFC 3161 Time-Stamp Protocol |
| `rfc5816` | IETF RFC 5816 ESSCertIDv2 update |
| `none` | No TSA attestation |

### 3.8 `compliance.gdpr_lawful_basis` enumeration

Per GDPR Article 6(1):

| Value | Article |
|---|---|
| `art_6_1_a_consent` | (a) Consent |
| `art_6_1_b_contract` | (b) Contract performance |
| `art_6_1_c_legal_obligation` | (c) Legal obligation |
| `art_6_1_d_vital_interests` | (d) Vital interests |
| `art_6_1_e_public_task` | (e) Public task |
| `art_6_1_f_legitimate_interest` | (f) Legitimate interest (primary for pharmaintel) |

### 3.9 `compliance.kvkk_article` enumeration

Per KVKK 6698 Sayılı Kanun Madde 5(2):

| Value | Article |
|---|---|
| `madde_5_1_acik_riza` | Madde 5/1 — Açık rıza |
| `madde_5_2_a` | (a) Kanunlarda açıkça öngörülmesi |
| `madde_5_2_b` | (b) Fiili imkansızlık |
| `madde_5_2_c` | (c) Sözleşmenin kurulması / ifası |
| `madde_5_2_c_meshru_menfaat` | (ç) Meşru menfaat (primary for pharmaintel forensic capture) |
| `madde_5_2_d_veri_sahibi` | (d) Veri sahibinin kendi verisini alenileştirmesi |
| `madde_5_2_e_hukuki_talep` | (e) Hakkın tesisi / kullanılması / korunması |
| `madde_5_2_f` | (f) Temel hakların korunması |

---

## §4. Field-Level Constraints

### 4.1 `evidence_id` format

- Regex: `^ev_\d{4}-\d{2}-\d{2}_[a-f0-9]{8}$`
- Length: exactly 22 characters
- Deterministic generation: `"ev_" + date(retrieved_at).isoformat() + "_" + sha256(primary_url).hexdigest()[:8]`
- **Idempotency:** Same primary_url + same retrieval date → same evidence_id (no duplicate artifacts)

### 4.2 `retrieved_at` format

- ISO 8601 UTC: `YYYY-MM-DDTHH:MM:SSZ`
- Strict Z suffix (no `+00:00` alternative)
- Millisecond precision optional but permitted: `YYYY-MM-DDTHH:MM:SS.sssZ`
- Timezone MUST be UTC — no local time zones

### 4.3 Hash format constraints

| Field | Algorithm | Length | Format |
|---|---|---|---|
| `content_hash_sha256` | SHA-256 | 64 hex | lowercase hex |
| `content_hash_blake3` | BLAKE3 | 64 hex | lowercase hex |
| `manifest_digest_sha256` | SHA-256 | 64 hex | lowercase hex |
| `tsr_hash_sha256` | SHA-256 | 64 hex | lowercase hex |

### 4.4 Path format constraints

All file paths (in `fallback_paths`, `sig_path`, `tsr_path`, `evidence_bundle_zip_path`) MUST be:
- Relative to evidence_root (default: `evidence/`)
- POSIX-style forward slashes
- No `..` or `~` references (directory traversal prevention)
- Lowercase filenames matching `ev_*` pattern

### 4.5 URL format constraints

- MUST be HTTPS (HTTP permitted only for TSA endpoints where RFC 3161 standard doesn't require TLS)
- MUST pass URL validation (no javascript: / data: / file: schemes)
- MUST NOT contain query string tokens with authentication material (API keys, session tokens)

---

## §5. Required vs Optional Fields

### 5.1 REQUIRED (G52/G-PROV-02 BLOCKER on missing)

Top-level:
- `schema_version`
- `evidence_id`
- `claim_text`
- `claim_type`
- `claim_domain`
- `source`
- `archive`
- `integrity`
- `cross_refs`
- `compliance`

Inside `source`:
- `authority_tier`, `primary_url`, `source_name`, `retrieved_at`, `retriever_agent`, `http_status`

Inside `archive`:
- At least 2 of `{wayback_url, archive_is_url, fallback_paths}` populated (G53/G-PROV-03 BLOCKER)
- `capture_paths_succeeded` + `capture_paths_failed` always populated

Inside `integrity`:
- `content_hash_sha256` (G54/G-PROV-04 BLOCKER on empty or recompute mismatch)

Inside `cross_refs`:
- `parent_report_id`, `cited_in_sections`, `triangulation_partner_ids` (non-empty for forensic-grade UBO)

Inside `compliance`:
- All fields required for forensic-grade; `contains_personal_data` must be explicit boolean (not null)

### 5.2 OPTIONAL (nullable)

- `custody` block entirely optional in baseline mode; REQUIRED in forensic-grade mode (G55/G-PROV-05 BLOCKER without TSR)
- `source.content_encoding`, `source.ssl_fingerprint` — forensic hygiene, not mandatory
- `custody.captured_by_identity` — can be null for skill-autonomous captures (operator identity asserted via sigstore signing)
- `compliance.lawful_basis_memorandum_ref` — optional pointer to formal legal memorandum
- `archive.wayback_job_id` — only present for SPN2 newly-requested captures

---

## §6. Schema Validation Pseudocode

```python
def validate_evidence_object(obj: dict, mode: str = "baseline") -> ValidationResult:
    errors = []
    warnings = []
    
    # Top-level required fields
    required_top = {"schema_version", "evidence_id", "claim_text", "claim_type",
                    "claim_domain", "source", "archive", "integrity",
                    "cross_refs", "compliance"}
    for field in required_top:
        if field not in obj:
            errors.append(f"MISSING_REQUIRED_TOP: {field}")
    
    # Evidence ID format
    if not re.match(r"^ev_\d{4}-\d{2}-\d{2}_[a-f0-9]{8}$", obj.get("evidence_id", "")):
        errors.append("INVALID_EVIDENCE_ID_FORMAT")
    
    # Claim type enumeration
    valid_claim_types = {"beneficial_ownership", "sanctions_hit", "regulatory_action",
                        "deleted_pipeline_claim", "historical_label",
                        "titck_opponent_claim", "litigation_exhibit",
                        "commercial_claim", "trial_endpoint",
                        "guideline_quote", "other"}
    if obj.get("claim_type") not in valid_claim_types:
        errors.append(f"INVALID_CLAIM_TYPE: {obj.get('claim_type')}")
    
    # Source required subfields
    src = obj.get("source", {})
    for sf in ["authority_tier", "primary_url", "source_name", "retrieved_at",
               "retriever_agent", "http_status"]:
        if sf not in src:
            errors.append(f"MISSING_SOURCE_FIELD: {sf}")
    
    # retrieved_at ISO 8601 strict
    try:
        datetime.fromisoformat(src.get("retrieved_at", "").replace("Z", "+00:00"))
    except ValueError:
        errors.append("INVALID_RETRIEVED_AT_FORMAT")
    
    # Archive: at least 2 of 3 capture paths
    arc = obj.get("archive", {})
    path_count = sum(1 for k in ["wayback_url", "archive_is_url"] 
                     if arc.get(k))
    if arc.get("fallback_paths"):
        path_count += 1
    if path_count < 2:
        errors.append("G53_INSUFFICIENT_CAPTURE_PATHS")  # G-PROV-03 BLOCKER
    
    # Integrity: content_hash_sha256 required, 64-hex lowercase
    int_blk = obj.get("integrity", {})
    h = int_blk.get("content_hash_sha256", "")
    if not re.match(r"^[a-f0-9]{64}$", h):
        errors.append("G54_INVALID_CONTENT_HASH")  # G-PROV-04 BLOCKER
    
    # Forensic-grade mode: TSR required
    if mode == "forensic-grade":
        tsa = obj.get("custody", {}).get("timestamp_authority", {}).get("primary", {})
        if not tsa.get("tsr_path") or not tsa.get("tsr_hash_sha256"):
            errors.append("G55_MISSING_TSR")  # G-PROV-05 BLOCKER in forensic-grade
    
    # Compliance: PII requires redaction
    comp = obj.get("compliance", {})
    if comp.get("contains_personal_data") is True:
        if not comp.get("pii_redaction_applied"):
            errors.append("G58_PII_NOT_REDACTED")  # G-PROV-08 BLOCKER always
    
    # UBO claim: P0 or P1 + triangulation
    if obj.get("claim_type") == "beneficial_ownership":
        if src.get("authority_tier") not in ["OSINT-T1", "OSINT-T2", "T0"]:
            errors.append("G56_UBO_NON_PRIMARY_SOURCE")  # G-PROV-06 BLOCKER
        if not obj.get("cross_refs", {}).get("triangulation_partner_ids"):
            errors.append("G56_UBO_NO_TRIANGULATION")  # G-PROV-06 BLOCKER
    
    return ValidationResult(errors=errors, warnings=warnings)
```

Full implementation in `scripts/provenance-engine/evidence_object.py` (v5.0.0 Aşama 7).

---

## §7. Schema Conformance Test Cases

### 7.1 Test case 1 — UBO claim (UK Companies House)

**Expected:** PASS in both baseline and forensic-grade modes.

Fields: all REQUIRED populated; `authority_tier: "OSINT-T1"`; 3 of 3 capture paths succeeded; TSR present from both DigiCert + FreeTSA; `contains_personal_data: false` (PSC register is corporate data); triangulation partner `ev_...` pointing to OpenCorporates P1 corroboration.

### 7.2 Test case 2 — Sanctions hit (OFAC SDN)

**Expected:** PASS in forensic-grade mode.

Fields: `claim_type: "sanctions_hit"`; `authority_tier: "T0"` (OFAC is statutory primary); Wayback capture + local Playwright; `contains_personal_data: true` (SDN entry includes individual name); `pii_redaction_applied: true` (named individual redacted in bundle PDF if not essential; unredacted if essential for compliance check).

### 7.3 Test case 3 — Invalid (missing triangulation partner)

**Expected:** FAIL G56/G-PROV-06 in all modes for beneficial_ownership claim_type.

Fields: `claim_type: "beneficial_ownership"` + `triangulation_partner_ids: []` (empty) → BLOCKER.

### 7.4 Test case 4 — Invalid (PII without redaction)

**Expected:** FAIL G58/G-PROV-08 always, regardless of mode.

Fields: `contains_personal_data: true` + `pii_redaction_applied: false` → BLOCKER.

### 7.5 Test case 5 — Baseline-mode-only valid (no TSR)

**Expected:** PASS baseline; FAIL G55/G-PROV-05 in forensic-grade.

Fields: all basic fields valid; `custody.timestamp_authority` empty → baseline WARNING, forensic-grade BLOCKER.

---

## §8. Schema Integration with pharmaintel Infrastructure

### 8.1 Footnote rendering (carbon-pptx, carbon-html-report)

Evidence Object consumed via Markdown footnote syntax:
```markdown
Şirket X'in UBO'su Fund Y'dir [^prov:ev_2026-04-16_7f3a2b1e].

[^prov:ev_2026-04-16_7f3a2b1e]: {claim_text} — Source: {source.source_name}
    | Retrieved: {source.retrieved_at} | Archive: {archive.wayback_url}
    | SHA-256: {integrity.content_hash_sha256}
    | TSA: {custody.timestamp_authority.primary.tsa_url}
    | Bundle: {cross_refs.evidence_bundle_zip_path}
```

Renderer expands these fields from the Evidence Object.

### 8.2 Composition chain annotation

Every evidence object logs its skill composition chain for smp-orchestrator tracking:
```yaml
cross_refs:
  skill_composition_chain:
    - "pharmaintel:sub-protocol-bd-dd"       # invoker
    - "pharmaintel:sub-protocol-provenance"  # orchestration
    - "pharmaintel:provenance-engine"        # capture layer
    - "carbon-pptx:footnote-render"          # downstream consumer
```

### 8.3 SQLite index schema

The manifest SQL in `provenance-engine.md` §3.5 derives from this YAML schema:
```sql
-- Primary fields mapped to columns
evidence_id           → evidence_id TEXT PRIMARY KEY
claim_text            → claim_text TEXT NOT NULL
claim_type            → claim_type TEXT NOT NULL
source.authority_tier → source_authority_tier TEXT NOT NULL
source.primary_url    → primary_url TEXT NOT NULL
source.retrieved_at   → retrieved_at TIMESTAMP NOT NULL
archive.wayback_url   → wayback_url TEXT
integrity.content_hash_sha256 → content_hash_sha256 TEXT NOT NULL
custody.timestamp_authority.primary.tsa_url → tsa_url TEXT
custody.timestamp_authority.primary.tsr_path → tsr_path TEXT
cross_refs.parent_report_id → parent_report_id TEXT
compliance.jurisdiction_of_capture → jurisdiction_of_capture TEXT
compliance.retention_until → retention_until DATE
```

Non-indexed YAML fields preserved as serialized `full_yaml TEXT` column for round-trip fidelity.

---

## §9. Versioning & Changelog

- **v1.0 (v5.0.0 pharmaintel release, 2026-04-16):** Initial schema specification. Seven-block structure (identity + source L1 + archive L2 + integrity L3 + custody L4 + cross_refs + compliance). Deterministic evidence_id format `ev_YYYY-MM-DD_<sha8>`. Complete enumerations for claim_type, claim_domain, authority_tier (T0-T7 + OSINT-T1-T3), wayback_snapshot_mode, fallback_method, signing.method, timestamp_authority.protocol, gdpr_lawful_basis, kvkk_article. Field-level constraints (regex patterns, ISO 8601 strict, hash length, URL validation). Required vs optional field specification with mode-dependent severity (baseline vs forensic-grade). Validation pseudocode referenced in scripts/provenance-engine/evidence_object.py. Five conformance test cases. Integration specifications for carbon-pptx footnote rendering, smp-orchestrator composition chain tracking, SQLite index schema mapping. Referenced by: provenance-engine.md (capability framework), sub-protocol-provenance.md (direct invocation), sub-protocol-bd-dd.md (BD DD wrapper), validate-report-discipline.py (G51-G60 gates), scripts/provenance-engine/evidence_object.py (runtime validation).
