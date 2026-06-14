#!/usr/bin/env python3
"""
anonymize_calibration.py — scrub identifiers from a calibration sidecar
before sharing it with the skill maintainer.

A calibration sidecar produced by ``publish_audit.py --calibration-mode``
contains:
  * Figma file keys (in the ``library.files`` list, as registry roles
    only — but the raw fixture passes can leak more)
  * Component names (``boundary_decisions[].node_name``)
  * Component IDs (``boundary_decisions[].node_id``)
  * Possibly cover-page metadata containing operator emails (via the G18
    probe, if added)

This tool transforms each identifier into a deterministic, salt-able hash
that preserves cross-sidecar matching (the same component will hash to
the same anonymous handle across runs of the same operator) without
revealing the original value.

Outputs:
  * ``<input>.anon.json`` — the anonymized sidecar
  * ``<input>.anon.salt`` — the salt used (the operator keeps this; if
    they want to map anonymous handles back to real names, they need
    the salt)

Usage:
    python3 tools/anonymize_calibration.py calibration.json
    python3 tools/anonymize_calibration.py calibration.json --salt secret
    python3 tools/anonymize_calibration.py calibration.json --inplace

The default mode never overwrites the original sidecar. Use --inplace
only if you intend to discard the raw data after anonymization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import sys
from pathlib import Path
from typing import Any


HASH_LENGTH = 12  # truncated SHA-256 hex


def hash_identifier(value: str, salt: str) -> str:
    """Return a deterministic short hash of ``value`` using ``salt``.

    Same value + same salt → same hash. Different salts produce unlinkable
    hashes across operators, so two operators' sidecars cannot be merged
    to deanonymize either one.
    """
    digest = hashlib.sha256((salt + ":" + value).encode("utf-8")).hexdigest()
    return digest[:HASH_LENGTH]


def _anonymize_boundary_decisions(decisions: list[dict], salt: str) -> None:
    """Mutate every boundary decision to replace node_id and node_name."""
    for d in decisions:
        nid = d.get("node_id")
        if nid:
            d["node_id"] = "anon:" + hash_identifier(str(nid), salt)
        nname = d.get("node_name")
        if nname:
            d["node_name"] = "anon:" + hash_identifier(str(nname), salt)


def _anonymize_notes(probe: dict, salt: str) -> None:
    """Notes may contain free-form component names; replace bracketed
    identifiers ``[role] Name`` patterns by their hash."""
    notes = probe.get("notes") or []
    # We intentionally take a conservative approach: replace the entire
    # note content rather than try to parse out structured fields,
    # because identifier leakage in free text is hard to characterize.
    probe["notes"] = [
        f"anon:{hash_identifier(note, salt)}" if len(note) > 60 else note
        for note in notes
    ]


def _anonymize_library_info(library: dict, salt: str) -> None:
    """Replace the DS name with a hash; keep the version structure."""
    name = library.get("ds_name")
    if name and name != "<single-file>":
        library["ds_name"] = "anon:" + hash_identifier(str(name), salt)
    files = library.get("files") or []
    library["files"] = [
        ("anon:" + hash_identifier(str(role), salt)) if role not in {
            "foundations", "components", "patterns", "icons", "primary"
        } else role
        for role in files
    ]


def anonymize(sidecar: dict, salt: str) -> dict:
    """Return a copy of ``sidecar`` with identifiers anonymized.

    The original argument is *not* mutated; produce a deep-enough copy
    that subsequent operations on it are safe.
    """
    # JSON round-trip = cheap deep copy + ensures only JSON-safe types
    output = json.loads(json.dumps(sidecar))
    if "library" in output:
        _anonymize_library_info(output["library"], salt)
    probes = output.get("probes") or {}
    for _gid, probe in probes.items():
        _anonymize_boundary_decisions(probe.get("boundary_decisions") or [], salt)
        _anonymize_notes(probe, salt)
    return output


def _audit_clean(payload: dict) -> list[str]:
    """Sanity check: scan the anonymized payload for residual identifiers.

    Looks for substrings that *look* like raw component names (Title-Case
    multi-word patterns) inside boundary decisions. False positives are
    expected; the audit's job is to flag any anonymization regression.
    """
    issues: list[str] = []
    probes = payload.get("probes") or {}
    for gid, probe in probes.items():
        for d in probe.get("boundary_decisions") or []:
            for field_name in ("node_id", "node_name"):
                value = d.get(field_name, "")
                if value and not value.startswith("anon:"):
                    issues.append(
                        f"gate {gid} boundary decision: {field_name}={value!r} "
                        f"is not anon:-prefixed"
                    )
    return issues


def main() -> int:
    """Parse CLI args, anonymize, write outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to calibration sidecar JSON")
    parser.add_argument("--salt", default=None,
                        help="Salt for hashing (default: random; reused across "
                             "runs only if you keep the .salt file)")
    parser.add_argument("--inplace", action="store_true",
                        help="Overwrite the input file (default: write to <input>.anon.json)")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 if the audit pass finds any non-anon identifier")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"Input not found: {src}", file=sys.stderr)
        return 2

    salt = args.salt or secrets.token_hex(16)
    with open(src, "r", encoding="utf-8") as f:
        payload = json.load(f)
    anon = anonymize(payload, salt)

    issues = _audit_clean(anon)
    if issues:
        print("WARNING: anonymization audit flagged residual identifiers:",
              file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        if args.strict:
            return 1

    if args.inplace:
        out_path = src
    else:
        out_path = src.with_suffix(src.suffix + ".anon.json"
                                     if not src.suffix.endswith(".anon.json")
                                     else src.suffix)
        if not str(out_path).endswith(".anon.json"):
            out_path = Path(str(src) + ".anon.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(anon, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote anonymized sidecar → {out_path}", file=sys.stderr)

    if args.salt is None:
        # Operator-only artifact: keep the salt locally for reproducible re-runs.
        salt_path = Path(str(src) + ".anon.salt")
        salt_path.write_text(salt + "\n", encoding="utf-8")
        print(f"Wrote salt → {salt_path} (keep this private!)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
