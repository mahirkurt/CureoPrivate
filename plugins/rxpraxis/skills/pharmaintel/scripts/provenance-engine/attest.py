#!/usr/bin/env python3
"""
attest.py — pharmaintel v5.0.0 Forensic Provenance Layer

L3 attestation layer — content hashes + RFC 3161 Time-Stamp Authority (TSA)
timestamping + sigstore cosign signing.

Three-tier attestation:
  1. Content hashing: SHA-256 (universal) + BLAKE3 (modern parallel) per artifact
  2. RFC 3161 TSA: DigiCert (primary) + FreeTSA (fallback) — proves pre-existence
  3. Sigstore cosign / GPG: keyless OIDC or local key — proves operator identity

External dependencies (optional, graceful degradation):
  - rfc3161ng       → RFC 3161 TSA requests
  - blake3          → BLAKE3 hashing (stdlib SHA-256 always available)
  - cosign binary   → sigstore signing (subprocess call; GPG subprocess fallback)
  - cryptography    → TSR verification

Environment variables:
  - PHARMAINTEL_TSA_PRIMARY   (default: http://timestamp.digicert.com)
  - PHARMAINTEL_TSA_FALLBACK  (default: https://freetsa.org/tsr)
  - PHARMAINTEL_SIGNER_ID     (operator identity for cosign keyless)

Run as module:
  python3 attest.py --hash <file>                      # Print SHA-256 + BLAKE3
  python3 attest.py --attest <evidence_id> --root <dir>  # Full attestation flow
  python3 attest.py --example                           # Dry-run demo

Cross-references:
  - references/provenance-engine.md §3.4 (L3 attestation)
  - references/evidence-object-schema.md §2.2 integrity + custody blocks
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import blake3  # type: ignore

    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False

try:
    import rfc3161ng  # type: ignore

    HAS_RFC3161 = True
except ImportError:
    HAS_RFC3161 = False


TSA_PRIMARY = os.environ.get(
    "PHARMAINTEL_TSA_PRIMARY", "http://timestamp.digicert.com")
TSA_FALLBACK = os.environ.get(
    "PHARMAINTEL_TSA_FALLBACK", "https://freetsa.org/tsr")


# --- Hashing ----------------------------------------------------------------


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    """Compute SHA-256 of file. Streaming (bounded memory)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def blake3_file(path: str | Path, chunk: int = 1 << 20) -> Optional[str]:
    """Compute BLAKE3 of file if available; else None."""
    if not HAS_BLAKE3:
        return None
    h = blake3.blake3()
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- Manifest digest --------------------------------------------------------


def compute_manifest_digest(hashes: dict[str, str]) -> str:
    """Deterministic manifest digest: SHA-256 of sorted-key JSON of hash dict.

    Why not CBOR? CBOR avoids whitespace ambiguity but adds dependency.
    JSON with sort_keys=True + separators=(',',':') is equivalently deterministic
    and stdlib-only.

    Args:
        hashes: dict of {artifact_name: hex_hash}

    Returns:
        SHA-256 hex of canonical JSON serialization.
    """
    canonical = json.dumps(hashes, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return sha256_bytes(canonical)


# --- RFC 3161 TSA timestamping ----------------------------------------------


def tsa_request(digest_hex: str, tsa_url: str,
                timeout: int = 30) -> tuple[Optional[bytes], Optional[str]]:
    """Request RFC 3161 timestamp for a SHA-256 digest.

    Args:
        digest_hex: hex-encoded SHA-256 digest
        tsa_url: TSA endpoint URL
        timeout: request timeout seconds

    Returns:
        (tsr_bytes, error_message). One of them is None.
    """
    if not HAS_RFC3161:
        return None, "rfc3161ng not installed"

    try:
        digest_bytes = bytes.fromhex(digest_hex)
        tsa = rfc3161ng.RemoteTimestamper(tsa_url, hashname="sha256",
                                         timeout=timeout)
        tsr = tsa.timestamp(data=digest_bytes)
        return tsr, None
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def attest_with_tsa(digest_hex: str, tsr_out_dir: str | Path,
                    evidence_id: str) -> dict:
    """Request timestamp from primary TSA with fallback.

    Returns:
        dict with primary + fallback TSA results for custody block.
    """
    out_dir = Path(tsr_out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    result = {"primary": None, "fallback": None}

    # Primary TSA
    tsr, err = tsa_request(digest_hex, TSA_PRIMARY)
    if tsr:
        tsr_path = out_dir / f"{evidence_id}.tsr"
        tsr_path.write_bytes(tsr)
        result["primary"] = {
            "protocol": "rfc3161",
            "tsa_url": TSA_PRIMARY,
            "tsr_path": str(tsr_path),
            "tsr_hash_sha256": sha256_bytes(tsr),
        }
    else:
        result["primary_error"] = err

    # Fallback TSA (always attempted — dual attestation)
    tsr_f, err_f = tsa_request(digest_hex, TSA_FALLBACK)
    if tsr_f:
        tsr_path_f = out_dir / f"{evidence_id}.freetsa.tsr"
        tsr_path_f.write_bytes(tsr_f)
        result["fallback"] = {
            "protocol": "rfc3161",
            "tsa_url": TSA_FALLBACK,
            "tsr_path": str(tsr_path_f),
            "tsr_hash_sha256": sha256_bytes(tsr_f),
        }
    else:
        result["fallback_error"] = err_f

    return result


# --- Sigstore cosign / GPG --------------------------------------------------


def cosign_sign_blob(blob_path: str | Path,
                      sig_out: str | Path) -> tuple[bool, Optional[str]]:
    """Sign blob with cosign keyless OIDC flow. Requires `cosign` CLI."""
    try:
        result = subprocess.run(
            ["cosign", "sign-blob", "--yes", "--output-signature",
             str(sig_out), str(blob_path)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return False, f"cosign failed: {result.stderr}"
        return True, None
    except FileNotFoundError:
        return False, "cosign binary not found"
    except subprocess.TimeoutExpired:
        return False, "cosign timeout (120s) — OIDC flow may have hung"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def gpg_sign_blob(blob_path: str | Path,
                   sig_out: str | Path,
                   signer_email: str) -> tuple[bool, Optional[str]]:
    """Sign blob with GPG. Requires gpg CLI + local signing key."""
    try:
        result = subprocess.run(
            ["gpg", "--batch", "--yes", "--armor", "--detach-sign",
             "--local-user", signer_email,
             "--output", str(sig_out), str(blob_path)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return False, f"gpg failed: {result.stderr}"
        return True, None
    except FileNotFoundError:
        return False, "gpg binary not found"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def attest_with_signature(blob_path: str | Path,
                          sig_out_dir: str | Path,
                          evidence_id: str,
                          signer_identity: Optional[str] = None) -> dict:
    """Attempt cosign keyless → GPG fallback → unsigned."""
    sig_dir = Path(sig_out_dir)
    sig_dir.mkdir(parents=True, exist_ok=True)
    sig_path = sig_dir / f"{evidence_id}.sig"

    # Try cosign keyless
    ok, err = cosign_sign_blob(blob_path, sig_path)
    if ok:
        return {
            "method": "sigstore_cosign",
            "signer_identity": signer_identity,
            "sig_path": str(sig_path),
            "sig_hash_sha256": sha256_file(sig_path),
        }

    # Fall back to GPG
    if signer_identity:
        ok, err = gpg_sign_blob(blob_path, sig_path, signer_identity)
        if ok:
            return {
                "method": "gpg",
                "signer_identity": signer_identity,
                "sig_path": str(sig_path),
                "sig_hash_sha256": sha256_file(sig_path),
            }

    return {"method": "none", "error": err or "no signing method available"}


# --- Full attestation flow --------------------------------------------------


@dataclass
class AttestationResult:
    evidence_id: str
    integrity_block: dict = field(default_factory=dict)
    custody_block: dict = field(default_factory=dict)
    manifest_digest_sha256: Optional[str] = None


def attest_evidence(evidence_id: str, evidence_root: str | Path,
                    artifact_paths: dict[str, str],
                    signer_identity: Optional[str] = None) -> AttestationResult:
    """Full L3 attestation: hash → manifest digest → TSA → signature.

    Args:
        evidence_id: Evidence Object ID
        evidence_root: evidence directory root
        artifact_paths: {artifact_type: file_path} e.g. {"pdf": "…", "warc": "…"}
        signer_identity: operator identity for cosign/GPG

    Returns:
        AttestationResult with integrity + custody blocks populated.
    """
    root = Path(evidence_root)

    # 1. Hash every artifact
    hashes: dict[str, str] = {}
    integrity = {}
    for kind, path in artifact_paths.items():
        if not Path(path).is_file():
            continue
        h_sha = sha256_file(path)
        integrity[f"{kind}_hash_sha256"] = h_sha
        hashes[kind] = h_sha
        # BLAKE3 on HTML primary content
        if kind == "html":
            b3 = blake3_file(path)
            if b3:
                integrity["content_hash_blake3"] = b3

    # Primary content hash = HTML hash (by convention)
    if "html" in hashes:
        integrity["content_hash_sha256"] = hashes["html"]

    # 2. Manifest digest
    manifest_digest = compute_manifest_digest(hashes)
    integrity["manifest_digest_sha256"] = manifest_digest

    # 3. TSA timestamp
    tsa_block = attest_with_tsa(manifest_digest, root / "tsr", evidence_id)

    # 4. Signature (sign the manifest digest for integrity binding)
    # Create ephemeral file with manifest digest for signing
    sign_target = root / "tsr" / f"{evidence_id}.manifest"
    sign_target.parent.mkdir(parents=True, exist_ok=True)
    sign_target.write_text(manifest_digest, encoding="utf-8")
    sig_block = attest_with_signature(sign_target, root / "sig",
                                       evidence_id, signer_identity)

    custody_block = {
        "captured_by_identity": signer_identity,
        "capture_environment": {
            "user_agent": f"pharmaintel-provenance-engine/5.0.0",
            "platform": os.uname().sysname + "-" + os.uname().machine,
        },
        "signing": sig_block,
        "timestamp_authority": {
            k: v for k, v in tsa_block.items()
            if k in ("primary", "fallback") and v is not None
        },
    }

    return AttestationResult(
        evidence_id=evidence_id,
        integrity_block=integrity,
        custody_block=custody_block,
        manifest_digest_sha256=manifest_digest,
    )


# --- Example ----------------------------------------------------------------


def example_attestation_result() -> dict:
    """Return example integrity + custody blocks (for dry-run / documentation)."""
    eid = "ev_2026-04-16_7f3a2b1e"
    return {
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
                "user_agent": "pharmaintel-provenance-engine/5.0.0",
                "platform": "Linux-x86_64",
            },
            "signing": {
                "method": "sigstore_cosign",
                "signer_identity": "operator@example.org",
                "sig_path": f"evidence/sig/{eid}.sig",
            },
            "timestamp_authority": {
                "primary": {
                    "protocol": "rfc3161",
                    "tsa_url": TSA_PRIMARY,
                    "tsr_path": f"evidence/tsr/{eid}.tsr",
                    "tsr_hash_sha256": "9a0364b9" + "0" * 56,
                },
                "fallback": {
                    "protocol": "rfc3161",
                    "tsa_url": TSA_FALLBACK,
                    "tsr_path": f"evidence/tsr/{eid}.freetsa.tsr",
                    "tsr_hash_sha256": "ff12" + "0" * 60,
                },
            },
        },
    }


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="pharmaintel v5.0.0 Forensic Provenance Layer — L3 attestation"
    )
    parser.add_argument("--hash", metavar="PATH",
                        help="Compute + print SHA-256 + BLAKE3 of file")
    parser.add_argument("--attest", metavar="EVIDENCE_ID",
                        help="Full attestation flow for evidence_id")
    parser.add_argument("--root", metavar="DIR", default="evidence",
                        help="Evidence root directory")
    parser.add_argument("--artifacts", metavar="JSON",
                        help="JSON dict {artifact_type: path}")
    parser.add_argument("--signer", metavar="EMAIL",
                        help="Signer identity (for cosign/GPG)")
    parser.add_argument("--example", action="store_true",
                        help="Print example attestation result (no network/signing)")
    parser.add_argument("--verify-tsr", metavar="TSR_PATH",
                        help="Verify TSR file (requires openssl)")
    parser.add_argument("--data", metavar="DIGEST_HEX",
                        help="Digest hex to verify against TSR (with --verify-tsr)")
    args = parser.parse_args()

    if args.example:
        print(json.dumps(example_attestation_result(), indent=2, ensure_ascii=False))
        print(f"\nDependencies — blake3: {HAS_BLAKE3}, rfc3161ng: {HAS_RFC3161}",
              file=sys.stderr)
        return 0

    if args.hash:
        sha = sha256_file(args.hash)
        b3 = blake3_file(args.hash)
        print(json.dumps({
            "path": args.hash,
            "sha256": sha,
            "blake3": b3 or "(blake3 module unavailable)",
        }, indent=2))
        return 0

    if args.attest:
        if not args.artifacts:
            parser.error("--attest requires --artifacts JSON")
        artifacts = json.loads(args.artifacts)
        result = attest_evidence(args.attest, args.root, artifacts, args.signer)
        print(json.dumps({
            "evidence_id": result.evidence_id,
            "manifest_digest_sha256": result.manifest_digest_sha256,
            "integrity": result.integrity_block,
            "custody": result.custody_block,
        }, indent=2, ensure_ascii=False))
        return 0

    if args.verify_tsr:
        if not args.data:
            parser.error("--verify-tsr requires --data DIGEST_HEX")
        # openssl ts -verify semantics
        print(f"Run: openssl ts -verify -digest {args.data} "
              f"-in {args.verify_tsr} -CAfile tsa-ca-bundle.pem",
              file=sys.stderr)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
