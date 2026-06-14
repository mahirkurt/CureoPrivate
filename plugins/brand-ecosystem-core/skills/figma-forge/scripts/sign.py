#!/usr/bin/env python3
"""sign.py — figma-forge cryptographic supply-chain signing (v1.0.0).

Produces three artifacts in the output directory:

    1. ``manifest.json``     — schema-v1.0 bundle manifest (SHA-256 of each file)
    2. ``provenance.json``   — SLSA v1.0 provenance attestation
    3. ``signature.sigstore``— Sigstore signing bundle (keyless flow)
                                or sha256-only fallback when sigstore absent

Usage::

    # Sigstore keyless (GitHub Actions, OIDC token detected automatically)
    python3 scripts/sign.py \\
        --library-dir . \\
        --output-dir release/ \\
        --identity 'release-bot@example.com' \\
        --source-repository 'https://github.com/org/repo' \\
        --source-commit "$GITHUB_SHA"

    # Air-gapped sha256-only (no Sigstore dependency)
    python3 scripts/sign.py \\
        --library-dir . \\
        --output-dir release/ \\
        --identity 'release@local' \\
        --sign-mode sha256-only

Exit codes::

    0  Signing succeeded; artifacts written.
    1  Signing failed (Sigstore unreachable, OIDC missing, etc.).
    2  Cannot run (library_dir missing, manifest empty, etc.).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Make figma_forge importable regardless of CWD
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sign.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--library-dir", type=Path, required=True,
                   help="Path to the Figma library bundle directory.")
    p.add_argument("--output-dir", type=Path, required=True,
                   help="Directory to write manifest, provenance, signature.")
    p.add_argument("--identity", type=str, required=True,
                   help="Signer identity (email for Sigstore, free-form for sha256).")
    p.add_argument("--sign-mode",
                   choices=("auto", "sigstore-keyless", "sha256-only"),
                   default="auto",
                   help="Signing mode (default: auto — Sigstore if available).")
    p.add_argument("--source-repository", type=str, default="",
                   help="Source git URL for SLSA provenance materials.")
    p.add_argument("--source-commit", type=str, default="",
                   help="Source git commit SHA for SLSA provenance.")
    p.add_argument("--builder-id", type=str,
                   default="figma-forge cli",
                   help="SLSA runDetails.builder.id (workflow ref in CI).")
    p.add_argument("--bundle-name", type=str, default=None,
                   help="Override bundle name (default: library-dir basename).")
    p.add_argument("--bundle-version", type=str, default=None,
                   help="Override bundle version (default: library-registry).")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Print signing summary to stderr.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if not args.library_dir.exists() or not args.library_dir.is_dir():
        print(f"❌ Library dir not found: {args.library_dir}", file=sys.stderr)
        return 2

    import figma_forge as ff

    # Build manifest
    try:
        manifest = ff.build_bundle_manifest(args.library_dir)
    except OSError as e:
        print(f"❌ Cannot build manifest: {e}", file=sys.stderr)
        return 2

    if manifest.file_count == 0:
        print(f"❌ Bundle is empty: {args.library_dir}", file=sys.stderr)
        return 2

    # Capture invocation environment (sanitized — no secrets)
    safe_env_keys = {
        "GITHUB_REPOSITORY", "GITHUB_WORKFLOW", "GITHUB_RUN_ID",
        "GITHUB_RUN_ATTEMPT", "RUNNER_OS", "CI",
        "PYTHON_VERSION", "FIGMA_FORGE_VERSION",
    }
    safe_env = {k: v for k, v in os.environ.items() if k in safe_env_keys}
    safe_env["FIGMA_FORGE_VERSION"] = ff.__version__

    # Sign
    try:
        signed = ff.sign_manifest(
            manifest,
            identity=args.identity,
            source_repository=args.source_repository,
            source_commit=args.source_commit,
            builder_id=args.builder_id,
            invocation_command=" ".join(sys.argv),
            invocation_environment=safe_env,
            sign_mode=args.sign_mode,
        )
    except RuntimeError as e:
        print(f"❌ Signing failed: {e}", file=sys.stderr)
        return 1

    # Write artifacts
    paths = signed.write_artifacts(args.output_dir)

    if args.verbose:
        print(f"  Library:      {args.library_dir}", file=sys.stderr)
        print(f"  Files:        {manifest.file_count}", file=sys.stderr)
        print(f"  Total size:   {manifest.total_size_bytes:,} bytes", file=sys.stderr)
        print(f"  Manifest:     {manifest.manifest_hash()[:24]}…", file=sys.stderr)
        print(f"  Mode:         {signed.signing_mode}", file=sys.stderr)
        print(f"  Identity:     {signed.signer_identity}", file=sys.stderr)
        print(f"  Signed at:    {signed.signed_at}", file=sys.stderr)
        print(file=sys.stderr)
        print(f"  Artifacts:", file=sys.stderr)
        for name, p in paths.items():
            print(f"    {name:12s} {p}  ({p.stat().st_size:,} bytes)",
                  file=sys.stderr)
    else:
        for name, p in paths.items():
            print(f"✓ {name}: {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
