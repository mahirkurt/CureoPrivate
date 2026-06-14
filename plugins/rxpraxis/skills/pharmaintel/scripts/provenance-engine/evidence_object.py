#!/usr/bin/env python3
"""
evidence_object.py — pharmaintel v5.0.0 Forensic Provenance Layer

Canonical Evidence Object data model implementing evidence-object-schema.md v1.0.

Provides:
  - EvidenceObject dataclass with schema v1.0 conformance
  - Deterministic evidence_id generation (ev_YYYY-MM-DD_<sha8>)
  - YAML serialization / deserialization (round-trip)
  - Schema validation (baseline + forensic-grade modes)
  - SQLite evidence index interface

Pure stdlib dependencies: hashlib, json, sqlite3, datetime, re, pathlib.
Optional: PyYAML for YAML I/O (stdlib JSON fallback available).

Run as module:
  python3 evidence_object.py --example                    # Print example EO YAML
  python3 evidence_object.py --validate <yaml_path>       # Validate an EO YAML file
  python3 evidence_object.py --validate <yaml_path> --mode forensic-grade
  python3 evidence_object.py --init-db <db_path>          # Create SQLite evidence index

Cross-references:
  - references/evidence-object-schema.md (canonical schema v1.0)
  - references/provenance-engine.md §2 (Evidence Object model)
  - scripts/provenance-engine/capture.py (produces EvidenceObject instances)
  - scripts/provenance-engine/attest.py (adds integrity + custody blocks)
  - scripts/provenance-engine/bundle.py (reads EvidenceObject for bundling)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# --- Constants --------------------------------------------------------------

SCHEMA_VERSION = "1.0"
EVIDENCE_ID_REGEX = re.compile(r"^ev_\d{4}-\d{2}-\d{2}_[a-f0-9]{8}$")
SHA256_REGEX = re.compile(r"^[a-f0-9]{64}$")
ISO_8601_UTC_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")

VALID_CLAIM_TYPES = {
    "beneficial_ownership",
    "sanctions_hit",
    "regulatory_action",
    "deleted_pipeline_claim",
    "historical_label",
    "titck_opponent_claim",
    "litigation_exhibit",
    "commercial_claim",
    "trial_endpoint",
    "guideline_quote",
    "other",
}

PROVENANCE_REQUIRED_CLAIM_TYPES = {
    "beneficial_ownership",
    "sanctions_hit",
    "regulatory_action",
    "deleted_pipeline_claim",
    "historical_label",
    "titck_opponent_claim",
    "litigation_exhibit",
}

VALID_AUTHORITY_TIERS = {
    "T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7",
    "OSINT-T1", "OSINT-T2", "OSINT-T3",
}

P0_AUTHORITY_TIERS = {"T0", "OSINT-T1"}
P1_AUTHORITY_TIERS = {"OSINT-T2"}

VALID_GDPR_BASES = {
    "art_6_1_a_consent",
    "art_6_1_b_contract",
    "art_6_1_c_legal_obligation",
    "art_6_1_d_vital_interests",
    "art_6_1_e_public_task",
    "art_6_1_f_legitimate_interest",
}

VALID_KVKK_ARTICLES = {
    "madde_5_1_acik_riza",
    "madde_5_2_a",
    "madde_5_2_b",
    "madde_5_2_c",
    "madde_5_2_c_meshru_menfaat",
    "madde_5_2_d_veri_sahibi",
    "madde_5_2_e_hukuki_talep",
    "madde_5_2_f",
}


# --- Evidence ID generation -------------------------------------------------


def generate_evidence_id(primary_url: str, retrieved_at: str) -> str:
    """Deterministic evidence_id: ev_YYYY-MM-DD_<sha256(url)[:8]>.

    Idempotent: same URL + same retrieval date → same evidence_id.

    Args:
        primary_url: source URL (http/https)
        retrieved_at: ISO 8601 UTC datetime string

    Returns:
        Evidence ID string conforming to EVIDENCE_ID_REGEX.

    Raises:
        ValueError: if retrieved_at not parseable.
    """
    dt = datetime.fromisoformat(retrieved_at.replace("Z", "+00:00"))
    date_str = dt.date().isoformat()
    url_hash = hashlib.sha256(primary_url.encode("utf-8")).hexdigest()[:8]
    return f"ev_{date_str}_{url_hash}"


# --- Validation -------------------------------------------------------------


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def validate_evidence_object(obj: dict, mode: str = "baseline") -> ValidationResult:
    """Validate Evidence Object dict against schema v1.0.

    Args:
        obj: Evidence Object as dict (parsed YAML/JSON).
        mode: "baseline" (G58 BLOCKER only) or "forensic-grade" (G51-G60 all BLOCKER).

    Returns:
        ValidationResult with errors + warnings.
    """
    r = ValidationResult()

    # Top-level required fields (G52)
    required_top = {
        "schema_version", "evidence_id", "claim_text", "claim_type",
        "claim_domain", "source", "archive", "integrity",
        "cross_refs", "compliance",
    }
    for field_name in required_top:
        if field_name not in obj:
            r.errors.append(f"G52_MISSING_REQUIRED_TOP: {field_name}")

    # Schema version
    if obj.get("schema_version") != SCHEMA_VERSION:
        r.errors.append(f"UNSUPPORTED_SCHEMA_VERSION: {obj.get('schema_version')}")

    # Evidence ID format (G52)
    eid = obj.get("evidence_id", "")
    if not EVIDENCE_ID_REGEX.match(eid):
        r.errors.append(f"G52_INVALID_EVIDENCE_ID_FORMAT: {eid}")

    # Claim type enumeration (G51 implicit — type determines provenance requirement)
    ct = obj.get("claim_type", "")
    if ct not in VALID_CLAIM_TYPES:
        r.errors.append(f"INVALID_CLAIM_TYPE: {ct}")

    # Source block
    src = obj.get("source", {})
    for sf in ["authority_tier", "primary_url", "source_name",
               "retrieved_at", "retriever_agent", "http_status"]:
        if sf not in src:
            r.errors.append(f"G52_MISSING_SOURCE_FIELD: {sf}")

    if src.get("authority_tier") not in VALID_AUTHORITY_TIERS:
        r.errors.append(f"INVALID_AUTHORITY_TIER: {src.get('authority_tier')}")

    # retrieved_at ISO 8601 UTC strict
    ra = src.get("retrieved_at", "")
    if not ISO_8601_UTC_REGEX.match(ra):
        r.errors.append(f"INVALID_RETRIEVED_AT_FORMAT: {ra}")

    # Archive: at least 2 of 3 capture paths (G53/G-PROV-03)
    arc = obj.get("archive", {})
    succeeded = arc.get("capture_paths_succeeded", [])
    if not isinstance(succeeded, list):
        r.errors.append("G53_CAPTURE_PATHS_NOT_LIST")
    elif len(succeeded) < 2:
        r.errors.append(f"G53_INSUFFICIENT_CAPTURE_PATHS: {len(succeeded)}/3")

    # Integrity: content_hash_sha256 (G54/G-PROV-04)
    int_blk = obj.get("integrity", {})
    h = int_blk.get("content_hash_sha256", "")
    if not SHA256_REGEX.match(h):
        r.errors.append(f"G54_INVALID_CONTENT_HASH: {h[:16]}…")

    # Forensic-grade: TSR required (G55/G-PROV-05)
    if mode == "forensic-grade":
        tsa = obj.get("custody", {}).get("timestamp_authority", {}).get("primary", {})
        if not tsa.get("tsr_path") or not tsa.get("tsr_hash_sha256"):
            r.errors.append("G55_MISSING_TSR")

    # UBO claim requires P0/P1 + triangulation (G56/G-PROV-06)
    if ct == "beneficial_ownership":
        tier = src.get("authority_tier", "")
        if tier not in (P0_AUTHORITY_TIERS | P1_AUTHORITY_TIERS):
            r.errors.append(f"G56_UBO_INSUFFICIENT_SOURCE_TIER: {tier}")
        partners = obj.get("cross_refs", {}).get("triangulation_partner_ids", [])
        if not partners:
            r.errors.append("G56_UBO_NO_TRIANGULATION")

    # Capture freshness (G57/G-PROV-07) — WARNING only
    if ra and ISO_8601_UTC_REGEX.match(ra):
        try:
            dt = datetime.fromisoformat(ra.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - dt).days
            if age_days > 7:
                r.warnings.append(f"G57_STALE_CAPTURE: {age_days} days since retrieval")
        except ValueError:
            pass

    # PII + redaction discipline (G58/G-PROV-08) — BLOCKER always
    comp = obj.get("compliance", {})
    if comp.get("contains_personal_data") is True:
        if not comp.get("pii_redaction_applied"):
            r.errors.append("G58_PII_NOT_REDACTED")

    # GDPR/KVKK basis enumerations
    if comp.get("gdpr_lawful_basis") and comp["gdpr_lawful_basis"] not in VALID_GDPR_BASES:
        r.errors.append(f"INVALID_GDPR_BASIS: {comp['gdpr_lawful_basis']}")
    if comp.get("kvkk_article") and comp["kvkk_article"] not in VALID_KVKK_ARTICLES:
        r.errors.append(f"INVALID_KVKK_ARTICLE: {comp['kvkk_article']}")

    return r


# --- Serialization ----------------------------------------------------------


def load_evidence_object(path: str | Path) -> dict:
    """Load Evidence Object from YAML or JSON file."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix in (".yaml", ".yml"):
        if not HAS_YAML:
            raise RuntimeError("PyYAML required to load YAML files")
        return yaml.safe_load(text)
    return json.loads(text)


def dump_evidence_object(obj: dict, path: str | Path) -> None:
    """Write Evidence Object to YAML or JSON file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix in (".yaml", ".yml"):
        if not HAS_YAML:
            raise RuntimeError("PyYAML required to write YAML files")
        p.write_text(
            yaml.safe_dump(obj, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    else:
        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


# --- SQLite evidence index --------------------------------------------------


INDEX_SCHEMA = """
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    claim_text TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    claim_domain TEXT NOT NULL,
    source_authority_tier TEXT NOT NULL,
    primary_url TEXT NOT NULL,
    source_name TEXT NOT NULL,
    retrieved_at TIMESTAMP NOT NULL,
    retriever_agent TEXT NOT NULL,
    http_status INTEGER,
    wayback_url TEXT,
    archive_is_url TEXT,
    fallback_methods TEXT,                  -- JSON array
    capture_paths_succeeded TEXT NOT NULL,  -- JSON array
    content_hash_sha256 TEXT NOT NULL,
    content_hash_blake3 TEXT,
    tsa_primary_url TEXT,
    tsr_primary_path TEXT,
    tsr_primary_hash TEXT,
    signing_method TEXT,
    signer_identity TEXT,
    parent_report_id TEXT,
    triangulation_partner_ids TEXT,         -- JSON array
    gdpr_lawful_basis TEXT,
    kvkk_article TEXT,
    contains_personal_data INTEGER,
    pii_redaction_applied INTEGER,
    retention_until DATE,
    jurisdiction_of_capture TEXT,
    full_yaml TEXT NOT NULL,                -- round-trip preservation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_report ON evidence(parent_report_id);
CREATE INDEX IF NOT EXISTS idx_claim_type ON evidence(claim_type);
CREATE INDEX IF NOT EXISTS idx_hash ON evidence(content_hash_sha256);
CREATE INDEX IF NOT EXISTS idx_retrieved ON evidence(retrieved_at);
CREATE INDEX IF NOT EXISTS idx_retention ON evidence(retention_until);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity TEXT NOT NULL,       -- INFO | WARNING | ERROR | BLOCKER
    evidence_id TEXT,
    gate_id TEXT,                 -- G51, G52, ...
    description TEXT NOT NULL,
    context_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_incident_ev ON incidents(evidence_id);
"""


def init_index_db(db_path: str | Path) -> None:
    """Create SQLite evidence index database."""
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(p)) as conn:
        conn.executescript(INDEX_SCHEMA)
        conn.commit()


def insert_evidence(db_path: str | Path, obj: dict) -> None:
    """Insert Evidence Object into SQLite index."""
    src = obj.get("source", {})
    arc = obj.get("archive", {})
    int_blk = obj.get("integrity", {})
    cust = obj.get("custody", {}) or {}
    tsa_p = cust.get("timestamp_authority", {}).get("primary", {}) or {}
    sig = cust.get("signing", {}) or {}
    cref = obj.get("cross_refs", {})
    comp = obj.get("compliance", {})

    row = (
        obj["evidence_id"],
        obj.get("schema_version", SCHEMA_VERSION),
        obj["claim_text"],
        obj["claim_type"],
        obj["claim_domain"],
        src["authority_tier"],
        src["primary_url"],
        src["source_name"],
        src["retrieved_at"],
        src["retriever_agent"],
        src.get("http_status"),
        arc.get("wayback_url"),
        arc.get("archive_is_url"),
        json.dumps(arc.get("fallback_paths", {}), sort_keys=True),
        json.dumps(arc.get("capture_paths_succeeded", [])),
        int_blk["content_hash_sha256"],
        int_blk.get("content_hash_blake3"),
        tsa_p.get("tsa_url"),
        tsa_p.get("tsr_path"),
        tsa_p.get("tsr_hash_sha256"),
        sig.get("method"),
        sig.get("signer_identity"),
        cref.get("parent_report_id"),
        json.dumps(cref.get("triangulation_partner_ids", [])),
        comp.get("gdpr_lawful_basis"),
        comp.get("kvkk_article"),
        1 if comp.get("contains_personal_data") else 0,
        1 if comp.get("pii_redaction_applied") else 0,
        comp.get("retention_until"),
        comp.get("jurisdiction_of_capture"),
        (yaml.safe_dump(obj, sort_keys=False, allow_unicode=True) if HAS_YAML
         else json.dumps(obj, indent=2, ensure_ascii=False)),
    )
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO evidence VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
             ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            row,
        )
        conn.commit()


def log_incident(
    db_path: str | Path,
    severity: str,
    description: str,
    evidence_id: Optional[str] = None,
    gate_id: Optional[str] = None,
    context: Optional[dict] = None,
) -> None:
    """Log incident into SQLite incidents table."""
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            "INSERT INTO incidents (severity, evidence_id, gate_id, description, context_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (severity, evidence_id, gate_id, description, json.dumps(context or {})),
        )
        conn.commit()


# --- Example fixture --------------------------------------------------------


def example_evidence_object() -> dict:
    """Return a fully-populated example Evidence Object conforming to schema v1.0."""
    primary_url = (
        "https://find-and-update.company-information.service.gov.uk/"
        "company/12345678/persons-with-significant-control"
    )
    retrieved_at = "2026-04-16T09:34:22Z"
    eid = generate_evidence_id(primary_url, retrieved_at)
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_id": eid,
        "claim_text": (
            "Company X is ultimately owned by Fund Y via a Luxembourg SCSp vehicle"
        ),
        "claim_type": "beneficial_ownership",
        "claim_domain": "corporate_structure",
        "source": {
            "authority_tier": "OSINT-T1",
            "primary_url": primary_url,
            "source_name": "UK Companies House PSC Register",
            "retrieved_at": retrieved_at,
            "retriever_agent": "pharmaintel-provenance-engine/5.0.0",
            "http_status": 200,
            "content_type": "text/html; charset=utf-8",
            "content_length_bytes": 184726,
        },
        "archive": {
            "wayback_url": f"https://web.archive.org/web/20260416093500/{primary_url}",
            "wayback_timestamp": "20260416093500",
            "wayback_snapshot_mode": "spn",
            "archive_is_url": "https://archive.ph/ABc12",
            "archive_is_hash": "ABc12",
            "fallback_method": "playwright_fullpage",
            "fallback_paths": {
                "pdf": f"evidence/pdf/{eid}.pdf",
                "png": f"evidence/png/{eid}.png",
                "html": f"evidence/html/{eid}.html",
                "warc": f"evidence/warc/{eid}.warc.gz",
            },
            "capture_paths_succeeded": ["wayback", "archive_is", "local"],
            "capture_paths_failed": [],
            "capture_duration_seconds": 18.3,
        },
        "integrity": {
            "content_hash_sha256":
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "content_hash_blake3":
                "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262",
            "pdf_hash_sha256":
                "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
            "warc_hash_sha256":
                "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
            "manifest_digest_sha256":
                "9a0364b9e99bb480dd25e1f0284c8555e51f2f5dcbc3e8a2b8e3b14fb1eef0d7",
        },
        "custody": {
            "captured_by_identity": "operator@example.org",
            "capture_environment": {
                "user_agent":
                    "Mozilla/5.0 (X11; Linux x86_64) pharmaintel-provenance-engine/5.0.0",
                "ip_egress_anonymized": True,
                "tls_version": "TLSv1.3",
                "platform": "Linux 6.1.0-x86_64",
            },
            "signing": {
                "method": "sigstore_cosign",
                "signer_identity": "operator@example.org",
                "sig_path": f"evidence/sig/{eid}.sig",
            },
            "timestamp_authority": {
                "primary": {
                    "protocol": "rfc3161",
                    "tsa_url": "http://timestamp.digicert.com",
                    "tsr_path": f"evidence/tsr/{eid}.tsr",
                    "tsr_hash_sha256": "9a0364b9" + "0" * 56,
                },
                "fallback": {
                    "protocol": "rfc3161",
                    "tsa_url": "https://freetsa.org/tsr",
                    "tsr_path": f"evidence/tsr/{eid}.freetsa.tsr",
                    "tsr_hash_sha256": "ff12" + "0" * 60,
                },
            },
        },
        "cross_refs": {
            "parent_report_id": "rpt_example_v1",
            "cited_in_sections": ["§4.2", "§Appendix-B"],
            "triangulation_partner_ids": ["ev_2026-04-16_a91b3c4d"],
            "skill_composition_chain": [
                "pharmaintel:sub-protocol-bd-dd",
                "pharmaintel:sub-protocol-provenance",
                "pharmaintel:provenance-engine",
            ],
            "evidence_bundle_zip_path":
                "evidence/bundle/rpt_example_v1_evidence_bundle.zip",
        },
        "compliance": {
            "gdpr_lawful_basis": "art_6_1_f_legitimate_interest",
            "kvkk_applies": True,
            "kvkk_article": "madde_5_2_c_meshru_menfaat",
            "contains_personal_data": False,
            "pii_redaction_applied": False,
            "retention_policy": "7_years",
            "retention_until": "2033-04-16",
            "jurisdiction_of_capture": "TR",
        },
    }


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="pharmaintel v5.0.0 Evidence Object toolkit (schema v1.0)"
    )
    parser.add_argument("--example", action="store_true",
                        help="Print example Evidence Object YAML")
    parser.add_argument("--validate", metavar="PATH",
                        help="Validate an Evidence Object YAML/JSON file")
    parser.add_argument("--mode", choices=["baseline", "forensic-grade"],
                        default="baseline",
                        help="Validation mode (default: baseline)")
    parser.add_argument("--init-db", metavar="DB_PATH",
                        help="Initialize SQLite evidence index database")
    parser.add_argument("--insert", metavar="PATH",
                        help="Insert EO from YAML file into DB (requires --db)")
    parser.add_argument("--db", metavar="DB_PATH",
                        help="SQLite index path for --insert")
    args = parser.parse_args()

    if args.example:
        obj = example_evidence_object()
        if HAS_YAML:
            print(yaml.safe_dump(obj, sort_keys=False, allow_unicode=True))
        else:
            print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0

    if args.init_db:
        init_index_db(args.init_db)
        print(f"✓ SQLite evidence index initialized at {args.init_db}")
        return 0

    if args.validate:
        obj = load_evidence_object(args.validate)
        result = validate_evidence_object(obj, mode=args.mode)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return 0 if result.passed else 1

    if args.insert:
        if not args.db:
            parser.error("--insert requires --db")
        obj = load_evidence_object(args.insert)
        result = validate_evidence_object(obj, mode=args.mode)
        if not result.passed:
            print("VALIDATION FAILED:", file=sys.stderr)
            print(json.dumps(result.to_dict(), indent=2), file=sys.stderr)
            return 1
        insert_evidence(args.db, obj)
        print(f"✓ Inserted {obj['evidence_id']} into {args.db}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
