#!/usr/bin/env python3
"""Evidence ledger — content-hashed provenance for sci-audit findings (P5).

Stdlib-only (hashlib/json). Records each verified claim/citation together with
the SHA-256 hash of the exact source text it was checked against, so an audit is
defensible and reproducible: a reviewer can confirm the source content has not
changed since the audit. Mirrors the provenance-ledger pattern used by
citable-source connectors.

The ledger stores DERIVED metadata + hashes only — never the raw source body or
any PII. Two uses:
  * `hash` a snippet to stamp a finding.
  * `add` / `verify` entries in a JSONL ledger at the project root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def content_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_entry(claim: str, source_id: str, source_excerpt: str,
               verdict: str, checked_via: str, ts: str | None = None) -> dict:
    """Build one ledger entry. `ts` (ISO-8601) is passed in — this module never
    reads the wall clock, so results are reproducible in tests/CI."""
    return {
        "ts": ts or "",
        "claim": claim.strip()[:300],
        "source_id": source_id.strip()[:120],
        "checked_via": checked_via.strip()[:60],  # e.g. "pubmed-epmc fulltext", "abstract", "crossref"
        "verdict": verdict.strip()[:40],          # grounded | contradicted | unverified | verified | ...
        "source_content_hash": content_hash(source_excerpt),
        "source_excerpt_len": len(source_excerpt),
    }


def verify_entry(entry: dict, current_source_text: str) -> bool:
    """True iff the current source text still hashes to the ledgered value."""
    return entry.get("source_content_hash") == content_hash(current_source_text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="sci-audit evidence ledger (content-hashed provenance).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("hash", help="Hash a snippet (stdin or --text).")
    h.add_argument("--text")

    a = sub.add_parser("add", help="Append an entry to a JSONL ledger.")
    a.add_argument("--ledger", type=Path, required=True)
    a.add_argument("--claim", required=True)
    a.add_argument("--source-id", required=True)
    a.add_argument("--excerpt", required=True, help="Exact source text the claim was checked against.")
    a.add_argument("--verdict", required=True)
    a.add_argument("--checked-via", default="unspecified")
    a.add_argument("--ts", default="", help="ISO-8601 timestamp (caller-supplied; module never reads the clock).")

    v = sub.add_parser("verify", help="Verify a ledger entry against current source text.")
    v.add_argument("--ledger", type=Path, required=True)
    v.add_argument("--index", type=int, required=True)
    v.add_argument("--current", required=True, help="Current source text to re-hash.")

    args = parser.parse_args(argv or sys.argv[1:])

    if args.cmd == "hash":
        text = args.text if args.text is not None else sys.stdin.read()
        print(content_hash(text))
        return 0

    if args.cmd == "add":
        entry = make_entry(args.claim, args.source_id, args.excerpt,
                           args.verdict, args.checked_via, args.ts or None)
        args.ledger.parent.mkdir(parents=True, exist_ok=True)
        with open(args.ledger, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(json.dumps(entry, ensure_ascii=False))
        return 0

    if args.cmd == "verify":
        lines = args.ledger.read_text(encoding="utf-8").splitlines()
        if not (0 <= args.index < len(lines)):
            print("index out of range", file=sys.stderr)
            return 2
        entry = json.loads(lines[args.index])
        ok = verify_entry(entry, args.current)
        print(json.dumps({"index": args.index, "unchanged": ok,
                          "ledgered_hash": entry.get("source_content_hash"),
                          "current_hash": content_hash(args.current)}))
        return 0 if ok else 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
