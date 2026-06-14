#!/usr/bin/env python3
"""
bundle.py — pharmaintel v5.0.0 Forensic Provenance Layer

L4 deliverable layer — Evidence Bundle ZIP builder.

Produces standalone immutable artifact for submission to:
  - TİTCK commission defenses
  - FDA Citizen Petition dockets
  - BD due diligence data rooms
  - Litigation discovery
  - Regulatory audit responses

Bundle structure:
  rpt_<id>_evidence_bundle.zip
  ├── MANIFEST.yaml             # all evidence_ids + hashes + TSRs + metadata
  ├── README.md                 # orientation for recipient
  ├── VERIFICATION.md           # step-by-step verification scripts
  ├── LICENSE                   # bundle usage license
  ├── evidence/
  │   ├── ev_<id>.pdf / .png / .html / .warc.gz / .har / .sig / .tsr
  │   └── ...
  ├── provenance.db.sqlite      # SQLite evidence index (copy)
  └── chain-walk/               # optional UBO investor chain visualizations
      └── chain_<target>.svg / .md

Pure stdlib: zipfile, hashlib, sqlite3, pathlib, datetime.
Optional: PyYAML for MANIFEST.yaml (JSON fallback).

Run as module:
  python3 bundle.py --report-id <id> --evidence-db <db_path> --output <out_path>
  python3 bundle.py --example                                      # Dry-run

Cross-references:
  - references/provenance-engine.md §3.5 (L4 ingestion + bundle)
  - references/sub-protocol-provenance.md §4.3 (output contract)
  - scripts/provenance-engine/evidence_object.py (SQLite schema)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import yaml  # type: ignore

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


PHARMAINTEL_VERSION = "5.0.0"
SCHEMA_VERSION = "1.0"


# --- Manifest construction --------------------------------------------------


def build_manifest(report_id: str, evidence_rows: list[dict],
                   bundle_metadata: dict) -> dict:
    """Build MANIFEST.yaml content from evidence index rows.

    Args:
        report_id: parent report identifier
        evidence_rows: list of dicts from SQLite evidence query
        bundle_metadata: bundle-level metadata (date, operator, mode, etc.)

    Returns:
        Manifest dict suitable for YAML/JSON serialization.
    """
    return {
        "manifest_version": "1.0",
        "pharmaintel_version": PHARMAINTEL_VERSION,
        "evidence_schema_version": SCHEMA_VERSION,
        "bundle_metadata": {
            "report_id": report_id,
            "bundle_built_at": bundle_metadata.get(
                "bundle_built_at",
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            ),
            "operator_identity": bundle_metadata.get("operator_identity"),
            "forensic_grade_mode": bundle_metadata.get("forensic_grade_mode", False),
            "evidence_count": len(evidence_rows),
            "capture_period_start": (
                min((r["retrieved_at"] for r in evidence_rows), default=None)
                if evidence_rows else None
            ),
            "capture_period_end": (
                max((r["retrieved_at"] for r in evidence_rows), default=None)
                if evidence_rows else None
            ),
            "validator_gates_passed": bundle_metadata.get(
                "validator_gates_passed", []),
            "validator_gates_failed": bundle_metadata.get(
                "validator_gates_failed", []),
            "validator_gates_warned": bundle_metadata.get(
                "validator_gates_warned", []),
            "jurisdiction_of_capture": bundle_metadata.get(
                "jurisdiction_of_capture", "TR"),
            "retention_policy": bundle_metadata.get("retention_policy", "7_years"),
        },
        "evidence_index": [
            {
                "evidence_id": r["evidence_id"],
                "claim_text": r["claim_text"],
                "claim_type": r["claim_type"],
                "source_authority_tier": r["source_authority_tier"],
                "primary_url": r["primary_url"],
                "source_name": r["source_name"],
                "retrieved_at": r["retrieved_at"],
                "wayback_url": r.get("wayback_url"),
                "archive_is_url": r.get("archive_is_url"),
                "capture_paths_succeeded":
                    json.loads(r.get("capture_paths_succeeded") or "[]"),
                "content_hash_sha256": r["content_hash_sha256"],
                "tsr_primary_path": r.get("tsr_primary_path"),
                "tsr_primary_hash": r.get("tsr_primary_hash"),
                "tsa_primary_url": r.get("tsa_primary_url"),
                "signing_method": r.get("signing_method"),
                "triangulation_partner_ids":
                    json.loads(r.get("triangulation_partner_ids") or "[]"),
            }
            for r in evidence_rows
        ],
    }


def render_readme(report_id: str, manifest: dict) -> str:
    """Render bundle README.md content."""
    md = manifest["bundle_metadata"]
    return f"""# Evidence Bundle — {report_id}

This is a **Forensic Provenance Layer** Evidence Bundle produced by
**pharmaintel v{PHARMAINTEL_VERSION}**.

## Bundle metadata

| Field | Value |
|---|---|
| Report ID | `{report_id}` |
| Bundle built at | `{md['bundle_built_at']}` |
| Operator identity | `{md.get('operator_identity') or '(skill-autonomous)'}` |
| Forensic-grade mode | `{md['forensic_grade_mode']}` |
| Evidence count | **{md['evidence_count']}** |
| Capture period | `{md.get('capture_period_start')}` → `{md.get('capture_period_end')}` |
| Jurisdiction of capture | `{md['jurisdiction_of_capture']}` |
| Retention policy | `{md['retention_policy']}` |
| Validator gates passed | {len(md.get('validator_gates_passed', []))}/10 |

## Bundle contents

```
{report_id}_evidence_bundle.zip
├── MANIFEST.yaml           ← machine-readable evidence index + metadata
├── README.md               ← this file
├── VERIFICATION.md         ← step-by-step verification scripts
├── LICENSE                 ← bundle usage terms
├── evidence/               ← all captured artifacts
│   ├── ev_<id>.pdf
│   ├── ev_<id>.png
│   ├── ev_<id>.html
│   ├── ev_<id>.warc.gz     ← WARC (ISO 28500) full HTTP capture
│   ├── ev_<id>.har         ← HTTP Archive (request chain)
│   ├── ev_<id>.sig         ← sigstore/cosign signature (or GPG)
│   ├── ev_<id>.tsr         ← RFC 3161 timestamp token (DigiCert)
│   └── ev_<id>.freetsa.tsr ← RFC 3161 timestamp token (FreeTSA fallback)
└── provenance.db.sqlite    ← SQLite evidence index (copy)
```

## Cryptographic integrity

Each evidence object is attested via three independent layers:

1. **Content hashing** (SHA-256 + BLAKE3) per artifact
2. **RFC 3161 Time-Stamp Authority** (DigiCert primary + FreeTSA fallback)
3. **Sigstore cosign keyless signing** (or GPG fallback)

To verify, see `VERIFICATION.md`.

## Jurisdictional compliance

- **KVKK (6698 SK):** Captures performed under Madde 5/2(ç) meşru menfaat.
  PII content has been redacted where present.
- **GDPR Art. 6(1)(f):** Legitimate interest — regulatory defense + commercial DD.
- **Retention:** {md['retention_policy']} from build date.

## License

This bundle is the work product of pharmaintel v{PHARMAINTEL_VERSION}. Evidence
artifacts are derived from public web sources captured under fair-use research
provisions. See LICENSE file for full terms.

## Support

For verification questions or schema clarifications, see:
- `references/provenance-engine.md` — capability framework
- `references/evidence-object-schema.md` — schema v{SCHEMA_VERSION}
- `references/ubo-source-hierarchy.md` — UBO source tier definitions
"""


def render_verification(report_id: str, manifest: dict) -> str:
    """Render bundle VERIFICATION.md with verification scripts."""
    md = manifest["bundle_metadata"]
    sample_eid = (manifest["evidence_index"][0]["evidence_id"]
                  if manifest["evidence_index"] else "ev_YYYY-MM-DD_xxxxxxxx")
    return f"""# Verification Procedures — {report_id}

This document provides step-by-step instructions to independently verify the
integrity and provenance of evidence objects in this bundle.

## Prerequisites

- `openssl` (for RFC 3161 TSR verification)
- `cosign` (for sigstore signature verification) — install:
  `curl -LO https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64`
- `sha256sum` (or equivalent) for content hash recomputation

## 1. Bundle integrity check

Verify the bundle ZIP itself has not been modified since release:

```bash
sha256sum <bundle_filename>.zip
# Compare against published SHA-256 in parent report §Appendix B
```

## 2. Per-evidence content hash verification

For each evidence object, recompute the content hash and compare to the
hash recorded in MANIFEST.yaml:

```bash
# Recompute SHA-256 of HTML primary content
sha256sum evidence/{sample_eid}.html

# Compare to MANIFEST.yaml entry:
# evidence_index:
#   - evidence_id: {sample_eid}
#     content_hash_sha256: <expected_hash>
```

## 3. RFC 3161 Time-Stamp verification

The TSR (Time-Stamp Response) proves that the content hash existed at the
recorded timestamp, attested by an independent third-party Time-Stamp
Authority (DigiCert primary + FreeTSA fallback).

### Primary TSA (DigiCert)

```bash
# Compute manifest digest (sha256 of canonical sorted-key hash JSON)
# Or use the manifest_digest_sha256 from the original Evidence Object

openssl ts -verify \\
    -digest <manifest_digest_hex> \\
    -in evidence/{sample_eid}.tsr \\
    -CAfile /path/to/digicert-tsa-ca-bundle.pem
```

### Fallback TSA (FreeTSA)

```bash
openssl ts -verify \\
    -digest <manifest_digest_hex> \\
    -in evidence/{sample_eid}.freetsa.tsr \\
    -CAfile https://freetsa.org/files/cacert.pem
```

Both TSAs should verify successfully — they provide independent attestation
of the same content existing at the recorded time.

## 4. Sigstore cosign signature verification

Verify operator identity attestation via sigstore keyless signature:

```bash
cosign verify-blob \\
    --signature evidence/{sample_eid}.sig \\
    --certificate-identity {md.get('operator_identity') or '<signer_email>'} \\
    --certificate-oidc-issuer https://accounts.google.com \\
    evidence/{sample_eid}.html
```

If GPG was used as fallback (signing.method: "gpg"):

```bash
gpg --verify evidence/{sample_eid}.sig evidence/{sample_eid}.html
```

## 5. SQLite index spot-check

The bundle includes a copy of the SQLite evidence index. Verify consistency:

```bash
sqlite3 provenance.db.sqlite \\
    "SELECT evidence_id, content_hash_sha256, retrieved_at
     FROM evidence WHERE parent_report_id = '{report_id}'"
```

## 6. Triangulation verification

For UBO claims, every evidence object should have at least one
triangulation partner with a distinct source. Verify:

```bash
sqlite3 provenance.db.sqlite \\
    "SELECT evidence_id, claim_type, triangulation_partner_ids
     FROM evidence
     WHERE parent_report_id = '{report_id}'
       AND claim_type IN ('beneficial_ownership', 'sanctions_hit')"
```

## What verification proves

A successful end-to-end verification demonstrates:

1. **Content integrity:** No modification since capture (G54)
2. **Temporal pre-existence:** Content existed at recorded time per
   independent third-party TSA (G55)
3. **Operator attestation:** Capture operator identity bound via PKI
4. **Triangulation:** Multi-source corroboration where required (G56)
5. **k-Redundancy:** ≥2 of 3 capture paths succeeded (G53)

## What verification does NOT prove

- The captured content was **factually accurate** at time of capture (only
  that it was published as captured)
- The source authority itself is **trustworthy** (only that it claimed what
  was captured at the recorded time)
- The claim derived from the evidence is **legally enforceable**
  (depends on jurisdictional rules of evidence)

For substantive evaluation of claims, consult:
- Source authority documentation (Companies House UK, SEC EDGAR, etc.)
- Local counsel in target jurisdiction
- Subject-matter expert review

## Pharmaintel attribution

This Evidence Bundle was produced by **pharmaintel v{PHARMAINTEL_VERSION}**
Forensic Provenance Layer using:
- Evidence Object schema v{SCHEMA_VERSION}
- UBO source hierarchy (P0-P3)
- k-redundant 3-path web archive capture
- RFC 3161 + sigstore dual attestation
- KVKK + GDPR compliance discipline
"""


def render_license() -> str:
    """Render bundle LICENSE content."""
    return f"""Evidence Bundle License — pharmaintel v{PHARMAINTEL_VERSION}

This Evidence Bundle is the work product of pharmaintel Forensic Provenance Layer.

The captured artifacts contained herein are derived from public web sources.
The capture and indexing operation was performed under:

  - GDPR Article 6(1)(f) — legitimate interest (regulatory defense + DD)
  - KVKK 6698 SK Madde 5/2(ç) — meşru menfaat
  - National copyright fair-use research provisions

Use of this bundle is permitted for:

  ✓ Regulatory defense submissions (TİTCK, FDA, EMA, PMDA, NMPA, etc.)
  ✓ Litigation evidence preservation
  ✓ BD/M&A due diligence documentation
  ✓ Compliance audit trail
  ✓ Internal corporate intelligence retention

Use of this bundle is NOT permitted for:

  ✗ Commercial republishing of captured copyrighted content
  ✗ Personal data reidentification beyond purpose limitation
  ✗ Adversarial use against captured data subjects beyond legitimate interest
  ✗ Distribution to third parties without redaction of personal data

Retention of this bundle is governed by the retention_policy field in
MANIFEST.yaml (default 7 years from bundle_built_at).

After retention expiry, the bundle should be cryptographically destroyed
(zero-overwrite or secure erase) per KVKK Madde 7 + GDPR Art. 17 compliance.

For questions regarding bundle usage rights, contact:
- Bundle operator (operator_identity in MANIFEST.yaml)
- pharmaintel skill maintainer
"""


# --- Bundle assembly --------------------------------------------------------


def query_evidence_for_report(db_path: str | Path,
                              report_id: str) -> list[dict]:
    """Query SQLite evidence index for all rows matching parent_report_id."""
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM evidence WHERE parent_report_id = ?",
            (report_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def assemble_bundle(
    report_id: str,
    evidence_db: str | Path,
    evidence_root: str | Path,
    output_dir: str | Path,
    bundle_metadata: Optional[dict] = None,
    chain_walk_dir: Optional[str | Path] = None,
) -> dict:
    """Assemble Evidence Bundle ZIP from SQLite index + evidence artifacts.

    Args:
        report_id: parent report identifier (filter for evidence rows)
        evidence_db: path to SQLite evidence index
        evidence_root: directory containing evidence/<artifact>/ subdirs
        output_dir: directory to write bundle ZIP
        bundle_metadata: optional bundle-level metadata
        chain_walk_dir: optional directory with UBO chain visualizations

    Returns:
        dict with bundle_zip_path + bundle_zip_sha256 + manifest summary
    """
    bundle_metadata = bundle_metadata or {}
    evidence_rows = query_evidence_for_report(evidence_db, report_id)

    if not evidence_rows:
        raise ValueError(f"No evidence found for report_id={report_id}")

    manifest = build_manifest(report_id, evidence_rows, bundle_metadata)
    readme = render_readme(report_id, manifest)
    verification = render_verification(report_id, manifest)
    license_text = render_license()

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / f"{report_id}_evidence_bundle.zip"

    evidence_root_p = Path(evidence_root)
    evidence_db_p = Path(evidence_db)

    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=6) as zf:
        # Manifest
        if HAS_YAML:
            zf.writestr("MANIFEST.yaml",
                        yaml.safe_dump(manifest, sort_keys=False,
                                       allow_unicode=True))
        else:
            zf.writestr("MANIFEST.json",
                        json.dumps(manifest, indent=2, ensure_ascii=False))

        # Documentation
        zf.writestr("README.md", readme)
        zf.writestr("VERIFICATION.md", verification)
        zf.writestr("LICENSE", license_text)

        # Evidence artifacts — copy all artifacts referenced by evidence_ids
        evidence_ids = [r["evidence_id"] for r in evidence_rows]
        for kind in ("pdf", "png", "html", "warc", "har", "sig", "tsr"):
            kind_dir = evidence_root_p / kind
            if not kind_dir.is_dir():
                continue
            for eid in evidence_ids:
                # Match patterns: ev_<id>.pdf, ev_<id>.warc.gz, ev_<id>.freetsa.tsr
                for f in kind_dir.glob(f"{eid}*"):
                    if f.is_file():
                        zf.write(f, f"evidence/{f.name}")

        # SQLite evidence index (filtered copy)
        if evidence_db_p.is_file():
            # Create a filtered copy with only this report's evidence
            tmp_db = out_dir / f".{report_id}_filtered.db"
            try:
                _create_filtered_db(evidence_db_p, tmp_db, report_id)
                zf.write(tmp_db, "provenance.db.sqlite")
            finally:
                tmp_db.unlink(missing_ok=True)

        # Optional chain-walk visualizations
        if chain_walk_dir:
            chain_dir = Path(chain_walk_dir)
            if chain_dir.is_dir():
                for f in chain_dir.iterdir():
                    if f.is_file():
                        zf.write(f, f"chain-walk/{f.name}")

    # Compute bundle ZIP SHA-256
    bundle_hash = _sha256_file(bundle_path)

    return {
        "bundle_zip_path": str(bundle_path),
        "bundle_zip_sha256": bundle_hash,
        "evidence_count": len(evidence_rows),
        "bundle_size_bytes": bundle_path.stat().st_size,
        "manifest_summary": {
            "report_id": report_id,
            "evidence_count": len(evidence_rows),
            "capture_period_start": manifest["bundle_metadata"][
                "capture_period_start"],
            "capture_period_end": manifest["bundle_metadata"][
                "capture_period_end"],
        },
    }


def _create_filtered_db(src_db: Path, dst_db: Path, report_id: str) -> None:
    """Create filtered copy of SQLite DB containing only report's evidence."""
    shutil.copyfile(src_db, dst_db)
    with sqlite3.connect(str(dst_db)) as conn:
        conn.execute(
            "DELETE FROM evidence WHERE parent_report_id != ?",
            (report_id,),
        )
        conn.execute(
            "DELETE FROM incidents WHERE evidence_id NOT IN "
            "(SELECT evidence_id FROM evidence)"
        )
        conn.execute("VACUUM")
        conn.commit()


def _sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


# --- Example fixture --------------------------------------------------------


def example_bundle_summary() -> dict:
    """Return example bundle summary (no I/O)."""
    return {
        "bundle_zip_path": (
            "evidence/bundle/rpt_glofitamab_titck_v3_evidence_bundle.zip"),
        "bundle_zip_sha256":
            "a4f1b8c9d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8e92b",
        "evidence_count": 17,
        "bundle_size_bytes": 247_829_456,
        "manifest_summary": {
            "report_id": "rpt_glofitamab_titck_v3",
            "evidence_count": 17,
            "capture_period_start": "2026-04-09T08:12:11Z",
            "capture_period_end": "2026-04-16T17:43:55Z",
        },
        "validator_gates_passed":
            ["G51", "G52", "G53", "G54", "G55", "G56", "G58", "G59", "G60"],
        "validator_gates_warned": ["G57"],
        "validator_gates_failed": [],
    }


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=("pharmaintel v5.0.0 Forensic Provenance Layer — "
                     "Evidence Bundle ZIP builder"))
    parser.add_argument("--report-id",
                        help="Parent report identifier")
    parser.add_argument("--evidence-db", default="evidence/manifest/evidence-master.db.sqlite",
                        help="SQLite evidence index path")
    parser.add_argument("--evidence-root", default="evidence",
                        help="Evidence root directory containing artifact subdirs")
    parser.add_argument("--output", default="evidence/bundle",
                        help="Output directory for bundle ZIP")
    parser.add_argument("--operator", help="Operator identity for bundle metadata")
    parser.add_argument("--forensic-grade", action="store_true",
                        help="Mark bundle as forensic-grade mode")
    parser.add_argument("--chain-walk-dir",
                        help="Optional UBO chain visualization directory")
    parser.add_argument("--example", action="store_true",
                        help="Print example bundle summary (no I/O)")
    args = parser.parse_args()

    if args.example:
        print(json.dumps(example_bundle_summary(), indent=2, ensure_ascii=False))
        return 0

    if not args.report_id:
        parser.error("--report-id required (or use --example)")

    metadata = {
        "operator_identity": args.operator,
        "forensic_grade_mode": args.forensic_grade,
        "bundle_built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    summary = assemble_bundle(
        report_id=args.report_id,
        evidence_db=args.evidence_db,
        evidence_root=args.evidence_root,
        output_dir=args.output,
        bundle_metadata=metadata,
        chain_walk_dir=args.chain_walk_dir,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
