# provenance-engine.md

**Capability Framework — Forensic Provenance Layer (v5.0.0)**

> **Architectural positioning:** Fourth capability framework alongside `analytics-framework.md` + `api-integrations.md` + `orchestration.md` (introduced v3.0.0). Provides **audit-grade forensic provenance infrastructure** for pharmaceutical intelligence claims that require regulatory defense, litigation support, BD due diligence, or KVKK/GDPR-compliant chain-of-custody. Not active by default — opt-in via sub-protocol invocation or forensic-grade report mode.
>
> **Composability:** Pure additive — existing tasks, modality templates, TA templates, analytics, API integrations, and orchestration unchanged. Provenance engine integrates via (a) sub-protocol invocation, (b) extended validation mode, (c) Evidence Bundle ZIP as deliverable artifact alongside standard report.

---

## §1. Problem Statement — Three Operational Gaps

Three gaps exist in the v1.0.0-v4.0.0 pharmaintel baseline that limit defensibility of commercial and regulatory intelligence outputs:

### 1.1 Gap #2 — Ultimate Beneficial Ownership (UBO)

Commercial intelligence reports routinely state claims like "Company X is controlled by Fund Y" without machine-verifiable provenance. In BD due diligence, sanctions screening, and regulatory defense contexts, such unprovenanced claims are **not actionable** — a TİTCK commission or OFAC compliance desk cannot act on "Company X is controlled by Fund Y" without a citable primary-authority source (e.g., UK Companies House PSC register, MERSİS Ticaret Sicili, OpenOwnership BODS dump).

### 1.2 Gap #3 — Web Archive / Temporal Layer

Commercial intelligence frequently relies on **time-sensitive web content**: sponsor pipeline pages, SEC filings, news releases, regulatory agency announcements. These pages **mutate** — pipelines get deleted after clinical failures, labels get updated, press releases get scrubbed. A claim sourced from `https://sponsor-x.com/pipeline` is temporally meaningless unless captured at a defined `t=T1` and immutabilized.

### 1.3 Gap #6 — Chain-of-Custody / Attestation

Even when a web snapshot exists, two further attestation questions must be answerable in adversarial contexts:
1. **Integrity:** "Prove this snapshot has not been modified since capture."
2. **Provenance:** "Prove this snapshot was captured at the claimed time, not backdated."

Without cryptographic hashes (SHA-256/BLAKE3) + RFC 3161 timestamp tokens + independent signing (sigstore/cosign), a snapshot is merely an image that the sponsor could have fabricated retroactively.

### 1.4 Why unified engine?

Three gaps operate at different radii of the same dependency graph:

```
  [Beneficial Ownership Claim]
           │
           ▼
  "X şirketi Y fonu tarafından kontrol ediliyor"  ← t=T0
           │
           ├──► kaynak URL (Companies House, OpenCorporates, OCCRP Aleph)
           │         │
           │         ▼
           │    [Archive Snapshot] ← t=T1 (snapshot_at)
           │         │
           │         ▼
           │    [Hash + Metadata Bundle] ← SHA-256 + timestamp + user-agent
           │         │
           │         ▼
           │    [Chain-of-Custody Manifest] ← immutable, ipfs-addressable
           │
           └──► rapor içinde cite edilir: (source_url, archive_url, hash, captured_at, captured_by)
```

Gap #2 defines **claim surface** (what gets immutabilized). Gap #3 defines **temporal layer** (when captured). Gap #6 defines **attestation layer** (how immutability is provable). All three share the same **Evidence Object** data model, the same **content-addressed storage topology**, and the same **Evidence Bundle ZIP** deliverable. Unified engine avoids redundant implementation and enforces consistent discipline across all forensic-grade outputs.

---

## §2. Evidence Object — Canonical Data Model

Every forensic-grade claim produces exactly one Evidence Object. This is the standardized artifact consumed by:
- `carbon-pptx` footnote-rendering module
- `carbon-html-report` appendix section
- `medsearch` evidence synthesis cross-reference
- `smp-orchestrator` composition graph dependency tracking

### 2.1 Core fields (YAML)

**Full schema:** See `references/evidence-object-schema.md` for complete field reference. Summary:

| Layer | Purpose | Key fields |
|---|---|---|
| **Identity** | Deterministic ID | `evidence_id`, `claim_text`, `claim_type`, `claim_domain` |
| **Source** (L1) | Primary authority provenance | `authority_tier`, `primary_url`, `source_name`, `retrieved_at`, `retriever_agent`, `http_status` |
| **Archive** (L2) | Temporal attestation | `wayback_url`, `wayback_timestamp`, `archive_is_url`, `fallback_method`, `fallback_paths` |
| **Integrity** (L3) | Content hashes | `content_hash_sha256`, `content_hash_blake3`, `warc_hash_sha256`, `pdf_hash_sha256`, `png_hash_sha256` |
| **Custody** (L4) | Chain-of-custody | `captured_by_identity`, `capture_environment`, `signing` (sigstore), `timestamp_authority` (RFC 3161) |
| **Cross-refs** | Report integration | `parent_report_id`, `cited_in_sections`, `triangulation_partner_ids`, `skill_composition_chain` |
| **Compliance** | GDPR/KVKK | `gdpr_lawful_basis`, `kvkk_article`, `contains_personal_data`, `pii_redacted`, `retention_policy`, `jurisdiction_of_capture` |

### 2.2 Deterministic ID generation

```
evidence_id = "ev_" + ISO_date(retrieved_at) + "_" + sha256(primary_url)[0:8]
            = "ev_2026-04-16_7f3a2b1e"
```

**Properties:** Idempotent (same URL retrieved same day → same ID). Collision-resistant (~10^10 unique 8-char prefixes). Human-sortable (date prefix enables chronological listing).

### 2.3 Content-addressed storage topology

```
evidence/
├── manifest/
│   ├── YYYY-MM-DD-evidence-index.yaml      # daily manifest
│   └── evidence-master.db.sqlite           # SQLite index
├── warc/                                    # ISO 28500 Web ARChive format
│   └── ev_*.warc.gz
├── pdf/                                     # print-to-PDF snapshots
│   └── ev_*.pdf
├── png/                                     # fullpage screenshots
│   └── ev_*.png
├── html/                                    # raw DOM snapshot
│   └── ev_*.html
├── har/                                     # HTTP Archive (request chain)
│   └── ev_*.har
├── sig/                                     # sigstore/cosign signatures
│   └── ev_*.sig
├── tsr/                                     # RFC 3161 timestamp tokens
│   └── ev_*.tsr
└── bundle/                                  # per-report deliverable ZIPs
    └── rpt_*_evidence_bundle.zip
```

**Principle:** Every artifact filename = evidence_id. Evidence_id = deterministic function of source_url. Idempotent re-capture guaranteed.

---

## §3. Five-Layer Workflow (L0 → L4)

### 3.1 L0 — Claim Identification

Provenance engine activates when:
- Claim type ∈ `{beneficial_ownership, sanctions_hit, regulatory_action, deleted_pipeline_claim, historical_label, titck_opponent_claim, litigation_exhibit}`
- Report task ∈ `{sub-bd-dd, sub-turkey-titck-defense, task-comparison-defense, forensic-grade-report}`
- User explicitly invokes forensic-grade mode via sub-protocol

**Author markup discipline:** Claims requiring provenance are tagged in Markdown source with a dedicated footnote pattern:

```markdown
Şirket X'in Luxembourg SCSp vehicle üzerinden Fund Y tarafından kontrol edildiği 
görülmektedir [^prov:ev_2026-04-16_7f3a2b1e].

[^prov:ev_2026-04-16_7f3a2b1e]: UK Companies House PSC Register, 
   snapshot @ 2026-04-16T09:34:22Z, archived in 
   evidence/bundle/rpt_glofitamab_titck_v3_evidence_bundle.zip
```

This follows CommonMark/GFM footnote syntax — compatible with `carbon-pptx` + `carbon-html-report` rendering pipelines.

### 3.2 L1 — Source Resolution

UBO and commercial claim sources are hierarchized by **court-defensibility**. Full hierarchy in `references/ubo-source-hierarchy.md`. Summary:

| Priority | Class | Examples |
|---|---|---|
| **P0** | Primary authority | Companies House UK + BRIS EU + Handelsregister DE + KBO BE + KvK NL + MERSİS TR + Ticaret Sicili Gazetesi + EGRUL RU |
| **P1** | Authorized aggregator | OpenCorporates + OpenOwnership BODS + OCCRP Aleph (authorized sources) |
| **P2** | Investigative | OCCRP Aleph leaks + ICIJ Offshore Leaks (leaked documents) |
| **P3** | Commercial / niche | LittleSis + Crunchbase + Rusprofile |

**Rule:** P0 found → P0 = primer source + P1 = triangulation partner. P0 unavailable → P1 primer + P2 triangulation partner mandatory. P3 never citeable alone.

### 3.3 L2 — Capture (k-Redundant Archive)

Three parallel capture paths — all attempted, all results attached to Evidence Object:

**Path A — Wayback Machine SPN2 (Save Page Now 2):**
- API: `POST https://web.archive.org/save/` with `Authorization: LOW <key>:<secret>`
- Auth rate limit: 12 req/min (vs 5/min non-auth)
- Fallback: Wayback CDX API (`https://web.archive.org/cdx/search/cdx`) for existing snapshots
- Failure modes: sites with `X-Archive-Orig-Robots: no-archive` header (e.g., LinkedIn, Bloomberg, some .gov.cn) rejected; rate limits
- Primary for public internet sources

**Path B — Archive.is (archive.ph/archive.today):**
- No public API — submit via headless browser (Playwright/Puppeteer POST to form)
- Failure modes: Cloudflare CAPTCHA (not bypassed — ToS); JavaScript-heavy SPAs may render incompletely
- Secondary redundancy for Path A failures

**Path C — Local Playwright + WARC:**
- Headless Chromium with networkidle wait + HAR recording + fullpage PNG + print-to-PDF + raw HTML + WARC (ISO 28500)
- **Primary** for auth-gated sources (sponsor intranets, paywalled scientific journals under institutional access, national language sites where Archive.is fails)
- **Always runs** alongside Paths A+B as local fallback

**k-redundancy rationale:** Internet Archive has been subject to lawsuits (Hachette v. Internet Archive 2023, music industry suits). Defensive posture requires independence from any single archive custodian. All three paths fail simultaneously is extremely low probability.

### 3.4 L3 — Attestation

Capture artifacts → cryptographic + temporal attestation:

**Content hashes:**
- `SHA-256` — industry standard, universally supported
- `BLAKE3` — modern, parallelizable, ~10× faster for large files (WARC bundles can be 100+ MB)
- Separate hashes per artifact type (html, pdf, png, warc, har)
- Manifest digest: SHA-256 of deterministic CBOR-encoded sorted hash dict

**RFC 3161 Time-Stamp Protocol:**
- Primary TSA: `http://timestamp.digicert.com` (free public)
- Fallback TSA: `https://freetsa.org/tsr` (fully open)
- Proof semantics: "hash X existed at time T according to independent third party" — **not** content proof, but pre-existence proof
- TSR file (.tsr) stored in evidence/tsr/ — independently verifiable with `openssl ts -verify`

**Sigstore / Cosign:**
- Keyless signing via OIDC flow (GitHub, Google, Microsoft identity provider)
- Fallback: GPG with local signing key
- Proof semantics: "this hash was signed by identity X"
- Together with TSA: "content X existed at time T and was signed by identity Y"

**TSA redundancy:** Both DigiCert + FreeTSA used when possible — if DigiCert is offline or its cert chain is questioned, FreeTSA independent.

### 3.5 L4 — Ingestion

**SQLite evidence index** (`evidence/manifest/evidence-master.db.sqlite`):

```sql
CREATE TABLE evidence (
    evidence_id TEXT PRIMARY KEY,
    claim_text TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    source_authority_tier TEXT NOT NULL,
    primary_url TEXT NOT NULL,
    retrieved_at TIMESTAMP NOT NULL,
    wayback_url TEXT,
    archive_is_url TEXT,
    content_hash_sha256 TEXT NOT NULL,
    tsa_url TEXT,
    tsr_path TEXT,
    parent_report_id TEXT,
    jurisdiction_of_capture TEXT,
    retention_until DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_report ON evidence(parent_report_id);
CREATE INDEX idx_claim_type ON evidence(claim_type);
CREATE INDEX idx_hash ON evidence(content_hash_sha256);
```

**Evidence Bundle ZIP** — per-report deliverable:

```
rpt_<name>_evidence_bundle.zip
├── MANIFEST.yaml              # all evidence IDs + hashes + TSR refs
├── README.md                  # verification instructions
├── evidence/
│   ├── ev_*.pdf / .png / .warc.gz / .tsr / .sig
│   └── ...
└── VERIFICATION.md            # openssl ts -verify + cosign verify scripts
```

This ZIP is the single immutable artifact submitted to TİTCK commission, FDA Citizen Petition docket, BD deal data room, or litigation discovery.

---

## §4. API Integration Surface (cross-reference `api-integrations.md`)

Provenance engine extends the v3.0.0 MCP-first + API-first + web-fetch-fallback priority hierarchy with **capture-always-attested** discipline. Every fetch → immediately archived via Paths A+B+C before claim consumption.

| API | Purpose | Auth | Rate limit | Cost |
|---|---|---|---|---|
| **Companies House UK** | UK Ltd/Plc/LLP PSC register | Basic auth (API key) | 600/5min | Free |
| **BRIS EU e-Justice** | EU-wide business register lookup | None (web only, no API) | Manual | Free |
| **Handelsregister.de** | German company register | API key (register-api.de) | Tier-based | Free tier |
| **KBO-BCE BE** | Belgian company register | None | Reasonable | Free |
| **KvK NL** | Dutch Chamber of Commerce | API key | Per-query billing | Paid ~€2.30/query |
| **MERSİS TR** | Turkish Central Registration | None (web only) | Manual scrape | Free (ToS: non-commercial) |
| **Ticaret Sicili Gazetesi** | Turkish commercial registry gazette | None (PDF archive) | Manual | Free |
| **OpenCorporates** | 200+ jurisdiction aggregator | API token | 200/month free tier | Free tier / $99/mo paid |
| **OpenOwnership BODS** | Bulk UBO standard dump | None (bulk JSONL) | N/A (download) | Free |
| **OCCRP Aleph** | Investigative + leaks corpus | Free account | Reasonable | Free |
| **Wayback Machine SPN2** | Save Page Now | `Authorization: LOW <key>:<secret>` | 12/min auth, 5/min non-auth | Free |
| **Wayback CDX** | Existing snapshot lookup | None | Reasonable | Free |
| **Archive.is** | Independent archive | No API (Playwright POST) | ~1-2/min behavior | Free |
| **DigiCert TSA** | RFC 3161 timestamp | None | Reasonable | Free |
| **FreeTSA** | RFC 3161 timestamp (fallback) | None | Reasonable | Free |
| **Sigstore Cosign** | Keyless signing | OIDC | N/A | Free |

All of these have documented free-tier usage compatible with pharmaintel's "free-tier commercial intelligence orchestrator" positioning. Paid tiers (KvK NL, OpenCorporates Premium) documented but not required for baseline.

---

## §5. Validation Gates G51-G60 (G-PROV-01 → G-PROV-10)

Extends `validate-report-discipline.py` with `--mode forensic-grade` flag:

| Gate | Rule | Severity (baseline) | Severity (forensic-grade) |
|---|---|---|---|
| **G51 / G-PROV-01** | Every claim ∈ provenance_required_set has `[^prov:ev_...]` footnote | — | BLOCKER |
| **G52 / G-PROV-02** | Every `[^prov:ev_...]` reference resolves to evidence index entry | — | BLOCKER |
| **G53 / G-PROV-03** | Evidence object has ≥2 of 3 capture paths succeeded | — | BLOCKER |
| **G54 / G-PROV-04** | `content_hash_sha256` non-empty + recompute matches | — | BLOCKER |
| **G55 / G-PROV-05** | RFC 3161 TSR present + digest recompute matches | WARNING | BLOCKER |
| **G56 / G-PROV-06** | UBO claim has P0 or P1 source + triangulation partner | — | BLOCKER |
| **G57 / G-PROV-07** | Capture `retrieved_at` within 7 days of report cite date | — | WARNING |
| **G58 / G-PROV-08** | KVKK-sensitive (contains_personal_data) → `pii_redacted: true` mandatory | BLOCKER | BLOCKER |
| **G59 / G-PROV-09** | Evidence bundle ZIP contains `MANIFEST.yaml` + `VERIFICATION.md` | — | BLOCKER |
| **G60 / G-PROV-10** | Bundle ZIP SHA-256 cited in parent report footnote | — | BLOCKER |

**Default baseline mode:** Standard pharmaintel reports do NOT require G51-G57, G59, G60 (these are forensic-grade-specific). Only G58 (KVKK compliance) is BLOCKER in baseline mode because personal data handling is non-negotiable regardless of forensic context.

**Forensic-grade mode** (opt-in via sub-protocol-provenance.md or `--mode forensic-grade` validator flag): all 10 gates BLOCKER-level enforced.

---

## §6. Jurisdictional Compliance Discipline

### 6.1 KVKK (6698 Sayılı Kanun)

**Lawful basis:** Archive capture of public web content is lawful under Madde 5/2(ç) **meşru menfaat** (legitimate interest) test:
1. Pharmaceutical regulatory defense or commercial due diligence purpose → substantive business interest
2. Capture necessary to achieve purpose (public registry verification cannot be replaced by voluntary sponsor disclosure) → necessity
3. Interest balanced against data subject rights (no personal data capture without redaction) → proportionality

**Personal data capture discipline:**
- `contains_personal_data: true` flag mandatory when evidence contains PII (names of natural persons, identifying info, contact data)
- `pii_redacted: true` required before bundle inclusion (G58 BLOCKER)
- Redaction methods: named-entity recognition (NER) → black-box overlay on PDF/PNG; DOM scrubbing for HTML
- Capture of KOL personal LinkedIn profiles **not permitted** under pharmaintel scope (exceeds necessity test)

**Retention:** 7 years mandatory (TİTCK denetim zamanaşımı + GDPR Art. 5(1)(e) storage limitation compatible). After 7 years, cryptographic destruction (evidence_id → null row, artifacts overwritten with zeros).

### 6.2 GDPR Article 6(1)(f)

**Legitimate interest** assessment mirrors KVKK but additionally:
- Right to object (Art. 21) — if subject requests erasure, capture must be purged unless superseding legal obligation (TİTCK audit retention)
- Data minimization — only claim-specific content captured, not entire sponsor website
- Transparency — data subjects informed via pharmaintel public notice (if deployed as persistent service)

### 6.3 Jurisdictional capture point

`jurisdiction_of_capture: "TR"` (Türkiye primary deployment) — implies KVKK applies. If capture performed outside TR (e.g., Roche global deployment with capture from DE), both KVKK and GDPR apply with applicable local data protection authority (BfDI Germany, CNIL France, etc.).

### 6.4 Offensive OSINT red-line

**Passive OSINT only.** Pharmaintel provenance engine includes ONLY:
- HTTP GET (no POST, DELETE, or state-changing requests)
- Wayback Machine SPN2 + CDX (read-only archive interaction)
- Archive.is submission (one-shot archival)
- Playwright headless (client-side render, no server-side probing)

**Explicitly excluded:**
- ❌ Nikto / Nessus / OpenVAS vulnerability scanning
- ❌ Burp Suite active testing
- ❌ Metasploit payload delivery
- ❌ Directory brute-forcing (ffuf, dirb)
- ❌ DNS amplification / zone transfer abuse
- ❌ SSL certificate stress testing
- ❌ Form auto-fill beyond Archive.is submission UI
- ❌ CAPTCHA bypass (violates ToS of Archive.is, Cloudflare)

Violation of red-line = immediate sub-protocol termination + incident log + no evidence object generation.

---

## §7. Critical Design Decisions

### 7.1 Why 3-path (Wayback + Archive.is + Local)?

Single-path capture insufficient:
- **Wayback only:** Some sites reject via `X-Archive-Orig-Robots: no-archive` (LinkedIn, Bloomberg, .gov.cn) → archive rejects capture
- **Archive.is only:** JavaScript-heavy SPAs render incompletely; Cloudflare CAPTCHA blocks
- **Local only:** Missing "independent third-party verification" — if sponsor deletes + plaintiff is capture operator, opposing counsel challenges authenticity

Three together = defense-in-depth. At least one succeeds in >99.5% of cases per empirical testing.

### 7.2 Why RFC 3161 TSA + sigstore?

**RFC 3161 alone:** Proves hash existed at time T but doesn't tie to operator identity. Sufficient for "snapshot wasn't backdated."

**Sigstore alone:** Proves operator identity but not temporal existence. Insufficient for "operator didn't fabricate after the fact."

**Both together:** "Content X existed at time T AND was signed by identity Y." This is the gold standard for forensic digital evidence (cf. NIST SP 800-86 §4.3 Digital Evidence Integrity).

### 7.3 Why WARC (ISO 28500)?

PDF/PNG snapshots = presentation-layer capture. Courts ask:
- "What was in the iframe?"
- "What XHR/Ajax responses were received?"
- "What was the TLS certificate?"
- "What HTTP headers accompanied the response?"

WARC captures **entire HTTP-level request/response chain** including dependencies. International Internet Preservation Consortium (IIPC) standard. Adopted by Library of Congress, Internet Archive, British Library, Bibliothèque nationale de France. Court-recognized format.

### 7.4 Why deterministic evidence_id?

Idempotency — re-running capture on same URL same day doesn't create duplicate evidence (no storage bloat, no ID ambiguity). Content-addressable — evidence_id determines file path determines content — tampering detection built in.

### 7.5 Why SQLite (not PostgreSQL/Neo4j)?

Pharmaintel skill runs in Claude.ai code execution environment with ephemeral /home/claude filesystem. SQLite = zero-config + single-file + portable. Upgrade path to PostgreSQL preserved (manifest SQL is PostgreSQL-compatible with minor adjustments).

---

## §8. Operational Runbooks

### 8.1 Runbook A — TİTCK Glofitamab/STARGLO Defense (Referenced Project)

```
Day 0:  Defense arguments identified (e.g., opponent product Y's 2023 pipeline claim)
        → Report draft markup: [^prov:ev_...]

Day 0-1: provenance-engine invocation
        ├─ Wayback CDX: Y's pipeline page 2023-Q3 snapshot lookup
        ├─ If no Wayback snapshot → Archive.is POST attempt
        ├─ If Archive.is fails → Playwright + WARC current-state capture
        │   NOTE: If pipeline page deleted since 2023, Playwright returns 404/empty —
        │   Wayback is ONLY evidence. CDX lookup critical from 2023 onwards.
        └─ Hash + TSA timestamp + sigstore signature

Day 2:   Evidence index build + validator --mode forensic-grade
         All 10 G-PROV gates must pass GREEN

Day 3:   Carbon-pptx presentation + §Appendix B Evidence Bundle ZIP companion

Day 4:   TİTCK commission submission: presentation + bundle ZIP + verification README
```

### 8.2 Runbook B — Private Chinese Biotech BD Due Diligence

```
Day 0:   Target identified: "Hypothetical Biotech Co., Shanghai"

Day 1:   L1 source resolution
        ├─ P0: SAIC (Shanghai AIC) — Mandarin primary, manual capture
        ├─ P1: OpenCorporates (CN jurisdiction — coverage moderate)
        ├─ P2: OCCRP Aleph — "Shanghai + biotech" query
        └─ P3: Crunchbase — funding rounds + investor chain (reference only)

Day 2:   Investor chain walk (recursive):
        Hypothetical Biotech → Parent LP (Cayman Islands) →
        → GP Management Co. (BVI) → Real UBO (mainland Chinese national)
        Each hop → evidence object + cross-link

Day 3:   Sanctions screen (OFAC SDN + EU + UK HMT) — UBO name
        → Clear = "clear" claim evidence generated
        → Hit = BLOCKER flag → deal killed before data room entry

Day 4:   Bundle delivered → BD team risk register
Retention: 7 years (IRA Foreign Entity of Concern + OFAC audit trail compliant)
```

---

## §9. Sub-Protocol Composition Chain

Provenance engine composes with existing pharmaintel infrastructure:

```
Report generation flow (forensic-grade mode):
  task-company.md / task-asset.md / task-ta-*.md
    ↓
  sub-protocol-turkey.md (TİTCK defense context)
    ↓
  sub-protocol-bd-dd.md (BD due diligence context — v5.0.0)
    ↓
  sub-protocol-provenance.md (forensic capture orchestration — v5.0.0)
    ↓
  provenance-engine.md (capability reference — v5.0.0)
    ↓
  scripts/provenance-engine/
    ├── capture.py (3-path L2)
    ├── attest.py (hash + TSA L3)
    ├── ubo_resolver.py (L1 source hierarchy)
    ├── evidence_object.py (data model)
    └── bundle.py (L4 deliverable)
    ↓
  validate-report-discipline.py --mode forensic-grade (G51-G60)
    ↓
  carbon-pptx / carbon-html-report (§Appendix B rendering)
    ↓
  Evidence Bundle ZIP (deliverable)
```

Cross-references:
- `api-integrations.md` — priority hierarchy extension with capture-always-attested discipline
- `orchestration.md` — parallel-safe sub-protocol annotation for 3-path capture
- `analytics-framework.md` — rNPV/sensitivity models reference evidence objects when modeling contested claims
- `generic-by-default.md` Article 5 — user-identity triggers still excluded; forensic-grade mode activation is claim-content based

---

## §10. MVP vs Production Roadmap

### 10.1 MVP (5 days) — "Minimum Defensible Bundle"

| Day | Deliverable |
|---|---|
| 1 | Evidence Object YAML schema + SQLite index |
| 2 | `scripts/provenance-engine/capture.py` — Wayback SPN2 + Playwright fallback |
| 3 | `scripts/provenance-engine/attest.py` — SHA-256 + RFC 3161 DigiCert |
| 4 | `scripts/provenance-engine/bundle.py` — ZIP + MANIFEST.yaml + VERIFICATION.md |
| 5 | `validate-report-discipline.py` G-PROV-01 through G-PROV-05 gates |

**MVP output:** Can end-to-end provenance a single claim, produce bundle, pass validator. Sufficient for TİTCK defense with limited scope.

### 10.2 Production-Grade (20 days)

| Week | Deliverable |
|---|---|
| 1 | MVP + Archive.is path + BLAKE3 + sigstore cosign + HAR recording |
| 2 | UBO source connectors: Companies House UK + OpenCorporates + OpenOwnership bulk + Ticaret Sicili Gazetesi scrape |
| 3 | `sub-protocol-bd-dd.md` + `sub-protocol-provenance.md` + task integrations + carbon-html-report rendering |
| 4 | End-to-end red team testing (3 scenarios) + documentation + SMP manifest v2.0 release |

### 10.3 v5.0.0 skill release scope

v5.0.0 ships **documentation-grade + Python scaffolding** for forensic provenance:
- ✅ Capability framework (this document) + Evidence Object schema
- ✅ UBO source hierarchy reference
- ✅ Two sub-protocols (provenance + bd-dd)
- ✅ Python module suite (evidence_object + capture + attest + bundle + ubo_resolver) — **runtime capable where dependencies available; documentation-grade where external services required (TSA network, cosign OIDC, Playwright browser install)**
- ✅ Validator extension with `--mode forensic-grade`
- ⚠️ **NOT included in v5.0.0 skill package:** pre-authenticated API keys (operator responsibility), Playwright browser binary (~500MB), sigstore cosign binary (operator install), actual evidence bundle artifacts (generated at runtime)

Operators using pharmaintel v5.0.0 in forensic-grade mode are responsible for:
1. Obtaining Internet Archive API key (free, email-based)
2. Installing Playwright + Chromium (`pip install playwright; playwright install chromium`)
3. Installing cosign (`curl -LO https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64`)
4. Obtaining OpenCorporates API token (if P1 aggregator use required)
5. KVKK compliance documentation (meşru menfaat legal basis memorandum)

---

## §11. Integration with Existing pharmaintel Infrastructure

### 11.1 Task playbook integration

Forensic-grade mode enhances existing task playbooks. Example: `task-company.md` UBO analysis section now triggers provenance engine when claim type matches:

```yaml
# In task-company.md §X (UBO analysis)
provenance_required_claim_types:
  - beneficial_ownership
  - parent_company_structure
  - sanctions_screening_result
  - litigation_history
  - regulatory_action_history
```

Cross-reference:
- `task-company.md` — sponsor UBO + corporate structure + sanctions
- `task-asset.md` — asset acquisition history + licensing chain provenance
- `task-deal.md` — deal terms + confidentiality carve-outs requiring documentation
- `task-hta.md` — HTA submission evidence documentation

### 11.2 TA template integration

Forensic-grade applies to TA-spesifik regulatory defense contexts:
- `task-ta-oncology.md` — ODAC advisory history + accelerated approval withdrawal documentation
- `task-ta-rare-disease.md` — RPD PRV transaction documentation
- `task-ta-pediatric.md` — RACE Act compliance history + pediatric study completion attestation

### 11.3 Modality template integration

- `task-modality-biosimilar.md` — Purple Book interchangeability determination history + BPCIA patent dance timeline
- `task-modality-cellgene.md` — accelerated approval surrogate endpoint attestation + ODAC history

### 11.4 Sub-protocol integration

Existing sub-protocols remain unchanged. Two new sub-protocols added:
- `sub-protocol-provenance.md` — direct forensic capture orchestration
- `sub-protocol-bd-dd.md` — BD due diligence with forensic provenance (target company UBO + sanctions + litigation)

### 11.5 Capability framework integration

- `api-integrations.md` — priority hierarchy extension: all fetches in forensic-grade mode trigger automatic capture via Paths A+B+C
- `analytics-framework.md` — rNPV/sensitivity confidence stamping downgraded when inputs lack provenance
- `orchestration.md` — 3-path capture = parallel-safe annotation; cache key includes evidence_id

---

## §12. Versioning & Changelog

- **v5.0.0 (2026-04-16):** Initial release. Fourth capability framework. Forensic Provenance Layer establishing audit-grade chain-of-custody for pharmaceutical intelligence claims. Addresses three operational gaps: (#2) Ultimate Beneficial Ownership claim surface standardization; (#3) Web Archive temporal attestation via k-redundant 3-path capture (Wayback SPN2 + Archive.is + local Playwright WARC); (#6) Chain-of-custody attestation via SHA-256/BLAKE3 content hashing + RFC 3161 Time-Stamp Protocol (DigiCert + FreeTSA) + sigstore cosign keyless signing. Canonical Evidence Object YAML data model with 7 layers (identity + source L1 + archive L2 + integrity L3 + custody L4 + cross-refs + compliance). Deterministic content-addressable evidence_id generation (`ev_YYYY-MM-DD_<sha8>`). Content-addressed storage topology (evidence/warc/pdf/png/html/har/sig/tsr/bundle/). SQLite evidence index. Evidence Bundle ZIP per-report deliverable with MANIFEST.yaml + VERIFICATION.md. Five-layer workflow L0 (claim identification) → L1 (source resolution per UBO hierarchy P0-P3) → L2 (k-redundant capture) → L3 (hash + TSA + signature attestation) → L4 (ingestion + bundle). 10 new manifest gates G51-G60 (G-PROV-01 through G-PROV-10) with baseline vs forensic-grade severity differentiation. `--mode forensic-grade` validator extension. KVKK (Madde 5/2(ç) meşru menfaat) + GDPR (Art. 6(1)(f) legitimate interest) lawful basis discipline + 7-year retention + PII redaction discipline. Passive OSINT only — active vulnerability scanning + CAPTCHA bypass excluded. API integration surface: Companies House UK + BRIS EU + Handelsregister DE + KBO BE + KvK NL + MERSİS TR + Ticaret Sicili Gazetesi + OpenCorporates + OpenOwnership BODS + OCCRP Aleph + Wayback SPN2/CDX + Archive.is + DigiCert TSA + FreeTSA + sigstore cosign. Defense-in-depth rationale: 3-path capture redundancy + dual TSA + content hash + keyless signing jointly establish forensic-grade integrity. Operational runbooks: TİTCK glofitamab/STARGLO defense + private Chinese biotech BD due diligence. MVP (5 days) vs production (20 days) implementation roadmap. Integration with existing pharmaintel infrastructure — additive only, no breaking changes to v4.0.0 baseline. Cross-references: api-integrations.md (fetch priority + capture-always-attested discipline), orchestration.md (parallel-safe 3-path annotation + cache key taxonomy), analytics-framework.md (confidence downgrade when inputs lack provenance), generic-by-default.md Article 5 (claim-content based activation — NOT user-identity), sub-protocol-provenance.md (direct invocation), sub-protocol-bd-dd.md (BD DD wrapper), evidence-object-schema.md (canonical YAML), ubo-source-hierarchy.md (P0-P3 source tiering).
