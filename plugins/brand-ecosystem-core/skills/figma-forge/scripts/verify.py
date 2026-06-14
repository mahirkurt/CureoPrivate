#!/usr/bin/env python3
"""verify.py — figma-forge cryptographic supply-chain verification (v1.0.0).

Three-layer verification of a signed bundle manifest:

    1. **Manifest integrity** — re-hash the on-disk manifest; confirm
       it matches the SHA-256 declared in the SLSA provenance subject.

    2. **Bundle integrity** (optional, when --library-dir provided) —
       walk every file in the manifest; recompute SHA-256; confirm
       no file is missing or modified.

    3. **Signature**:
       - sha256-only mode → confirm declared hashes match + identity
       - sigstore-keyless mode → verify Sigstore bundle against
         expected signer identity and OIDC issuer

Usage::

    # Manifest + bundle + signature
    python3 scripts/verify.py \\
        --manifest signed-bundle/manifest.json \\
        --provenance signed-bundle/provenance.json \\
        --signature signed-bundle/signature.sigstore \\
        --library-dir . \\
        --expected-identity 'release-bot@example.com'

    # Manifest-only (quick check)
    python3 scripts/verify.py \\
        --manifest signed-bundle/manifest.json \\
        --provenance signed-bundle/provenance.json

Exit codes::

    0  All checks passed.
    1  One or more checks failed (use --verbose for details).
    2  Cannot run (missing inputs, malformed JSON, etc.).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make figma_forge importable regardless of CWD
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="verify.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--manifest", type=Path, required=True,
                   help="Path to manifest.json")
    p.add_argument("--provenance", type=Path, required=True,
                   help="Path to provenance.json")
    p.add_argument("--signature", type=Path, default=None,
                   help="Path to signature.sigstore (optional)")
    p.add_argument("--library-dir", type=Path, default=None,
                   help="Bundle directory for per-file SHA-256 re-verification")
    p.add_argument("--expected-identity", type=str, default="",
                   help="Expected signer identity (email for Sigstore)")
    p.add_argument("--expected-oidc-issuer", type=str, default="",
                   help="Expected OIDC issuer URL (default: Google)")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Print pass/fail details to stderr")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if not args.manifest.exists():
        print(f"❌ Manifest not found: {args.manifest}", file=sys.stderr)
        return 2
    if not args.provenance.exists():
        print(f"❌ Provenance not found: {args.provenance}", file=sys.stderr)
        return 2

    import figma_forge as ff

    try:
        result = ff.verify_manifest(
            manifest_path=args.manifest,
            provenance_path=args.provenance,
            signature_path=args.signature,
            expected_identity=args.expected_identity,
            expected_oidc_issuer=args.expected_oidc_issuer,
            library_dir=args.library_dir,
        )
    except Exception as e:
        print(f"❌ Verification raised an exception: {e}", file=sys.stderr)
        return 2

    if result.is_valid:
        print(f"✓ All checks passed ({len(result.passed_checks)} checks)")
        if args.verbose:
            for c in result.passed_checks:
                print(f"  ✓ {c}", file=sys.stderr)
        return 0
    else:
        print(
            f"✗ Verification FAILED "
            f"({len(result.failed_checks)} failure(s), "
            f"{len(result.passed_checks)} check(s) passed)"
        )
        for c in result.failed_checks:
            print(f"  ✗ {c}")
        if args.verbose:
            for c in result.passed_checks:
                print(f"  ✓ {c}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
