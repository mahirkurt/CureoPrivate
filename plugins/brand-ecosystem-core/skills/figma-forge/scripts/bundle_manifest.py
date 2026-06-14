#!/usr/bin/env python3
"""bundle_manifest.py — generate a SHA-256-hashed file inventory for a library bundle.

Produces a ``manifest.json`` sidecar that lists every file in the bundle
with its size, SHA-256 hash, and category. The manifest is the canonical
input for supply-chain integrity checks, reproducible-build verification,
and the v1.0.0 Sigstore/Cosign attestation pipeline.

Usage::

    python3 scripts/bundle_manifest.py \\
        --library-dir ./dustur-figma-library \\
        --output ./dustur-figma-library/manifest.json

Exit codes::

    0  Manifest written successfully
    1  Validation against an existing manifest failed (with --verify)
    2  Cannot run (missing dir, write error, etc.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.3.0-rc.1"

# Patterns excluded from the manifest (build artefacts, VCS, OS metadata)
DEFAULT_SKIP_DIR_PARTS = frozenset({
    "__pycache__", ".pytest_cache", ".git", "node_modules", ".venv", ".idea",
})
DEFAULT_SKIP_NAMES = frozenset({
    ".DS_Store", ".gitignore", "Thumbs.db", ".coverage",
})
DEFAULT_SKIP_SUFFIX = frozenset({".pyc", ".pyo", ".swp", ".tmp"})

# Categorization rules — first match wins
CATEGORY_RULES: list[tuple[str, str]] = [
    ("tokens/primitives/",         "tokens.primitive"),
    ("tokens/semantic/",           "tokens.semantic"),
    ("tokens/",                    "tokens.merged"),
    ("components/",                "components.spec"),
    ("patterns/",                  "patterns.spec"),
    ("code-connect/",              "code-connect.mapping"),
    ("icons/svg/tier/",            "icons.tier-svg"),
    ("icons/svg/selcuklu-motif/",  "icons.selcuklu-svg"),
    ("icons/svg/document/",        "icons.legal-svg"),
    ("icons/svg/",                 "icons.generic-svg"),
    ("icons/",                     "icons.spec"),
    ("docs/",                      "docs"),
    ("remediations/",              "remediations"),
]


@dataclass
class FileEntry:
    path: str
    size: int
    sha256: str
    category: str


# ---------------------------------------------------------------------------
# Hash computation
# ---------------------------------------------------------------------------

def sha256_of(path: Path, *, chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def categorize(path_str: str) -> str:
    for prefix, category in CATEGORY_RULES:
        if path_str.startswith(prefix):
            return category
    return "root"


def should_skip(path: Path) -> bool:
    if not path.is_file():
        return True
    if any(part in DEFAULT_SKIP_DIR_PARTS for part in path.parts):
        return True
    if path.name in DEFAULT_SKIP_NAMES:
        return True
    if path.suffix in DEFAULT_SKIP_SUFFIX:
        return True
    return False


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def build_manifest(
    library_dir: Path,
    *,
    bundle_name: str | None = None,
    bundle_version: str | None = None,
    source_ds: dict | None = None,
    skip_self: str = "manifest.json",
) -> dict:
    """Compute the full manifest dict for ``library_dir``."""
    files: list[FileEntry] = []
    for p in sorted(library_dir.rglob("*")):
        if should_skip(p):
            continue
        rel = str(p.relative_to(library_dir))
        if rel == skip_self:
            continue  # Exclude the manifest itself
        files.append(FileEntry(
            path=rel,
            size=p.stat().st_size,
            sha256=sha256_of(p),
            category=categorize(rel),
        ))

    categories: dict[str, int] = {}
    for f in files:
        categories[f.category] = categories.get(f.category, 0) + 1

    # Sort summary deterministically
    summary = {k: categories[k] for k in sorted(categories)}

    library_registry: dict | None = None
    reg_path = library_dir / "library-registry.json"
    if reg_path.exists():
        try:
            library_registry = json.loads(reg_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            library_registry = None

    inferred_bundle_name = bundle_name or library_dir.name
    inferred_source: dict = source_ds or {}
    if library_registry:
        inferred_source = {
            "name": library_registry.get("ds_name") or inferred_source.get("name"),
            "version": library_registry.get("ds_version") or inferred_source.get("version"),
            "url": library_registry.get("ds_url") or inferred_source.get("url"),
        }
        # Clear None-valued fields
        inferred_source = {k: v for k, v in inferred_source.items() if v}

    return {
        "$schema": "https://raw.githubusercontent.com/mahirkurt/figma-forge/main/schemas/bundle-manifest.schema.json",
        "bundle_name": inferred_bundle_name,
        "bundle_version": bundle_version or "0.0.0",
        "source_design_system": inferred_source or None,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "generator": {
            "tool": "figma-forge bundle-manifest",
            "version": __version__,
        },
        "file_count": len(files),
        "total_size_bytes": sum(f.size for f in files),
        "summary_by_category": summary,
        "files": [asdict(f) for f in files],
    }


def verify_manifest(
    expected_path: Path,
    library_dir: Path,
) -> tuple[bool, list[str]]:
    """Compare the on-disk manifest against a fresh recomputation.

    Returns ``(ok, issues)``; ``issues`` is a list of human-readable
    diff lines (added / removed / hash-mismatch).
    """
    try:
        on_disk = json.loads(expected_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return False, [f"Cannot read manifest: {e}"]

    fresh = build_manifest(
        library_dir,
        bundle_name=on_disk.get("bundle_name"),
        bundle_version=on_disk.get("bundle_version"),
        source_ds=on_disk.get("source_design_system"),
    )

    on_disk_files = {f["path"]: f["sha256"] for f in on_disk.get("files", [])}
    fresh_files = {f["path"]: f["sha256"] for f in fresh.get("files", [])}

    issues: list[str] = []
    for path in sorted(set(on_disk_files) | set(fresh_files)):
        if path not in on_disk_files:
            issues.append(f"ADDED:    {path}")
        elif path not in fresh_files:
            issues.append(f"REMOVED:  {path}")
        elif on_disk_files[path] != fresh_files[path]:
            issues.append(f"CHANGED:  {path} "
                          f"(was {on_disk_files[path][:12]}…, "
                          f"now {fresh_files[path][:12]}…)")

    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bundle_manifest.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--library-dir", type=Path, required=True,
                   help="Library bundle root.")
    p.add_argument("--output", type=Path, default=None,
                   help="Output path (default: <library-dir>/manifest.json).")
    p.add_argument("--bundle-name", default=None,
                   help="Override bundle name (default: library-dir basename).")
    p.add_argument("--bundle-version", default=None,
                   help="Override bundle version (default: read library-registry, else 0.0.0).")
    p.add_argument("--verify", action="store_true",
                   help="Verify an existing manifest matches the current bundle state.")
    p.add_argument("--quiet", "-q", action="store_true",
                   help="Suppress progress output.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if not args.library_dir.is_dir():
        print(f"❌ Library directory not found: {args.library_dir}", file=sys.stderr)
        return 2

    output = args.output or (args.library_dir / "manifest.json")

    if args.verify:
        if not output.exists():
            print(f"❌ Cannot verify: {output} does not exist.", file=sys.stderr)
            return 2
        ok, issues = verify_manifest(output, args.library_dir)
        if ok:
            if not args.quiet:
                print(f"✓ Manifest matches current bundle state: {output}")
            return 0
        print(f"❌ Manifest verification failed ({len(issues)} issue(s)):", file=sys.stderr)
        for line in issues[:50]:
            print(f"  {line}", file=sys.stderr)
        if len(issues) > 50:
            print(f"  … and {len(issues) - 50} more", file=sys.stderr)
        return 1

    # Build mode
    # Read existing bundle_version from library-registry if not explicit
    bundle_version = args.bundle_version
    if bundle_version is None:
        reg = args.library_dir / "library-registry.json"
        if reg.exists():
            try:
                data = json.loads(reg.read_text(encoding="utf-8"))
                bundle_version = data.get("bundle_version") or data.get("ds_version")
            except json.JSONDecodeError:
                pass
    bundle_version = bundle_version or "0.0.0"

    manifest = build_manifest(
        args.library_dir,
        bundle_name=args.bundle_name,
        bundle_version=bundle_version,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if not args.quiet:
        print(f"✓ Manifest written → {output}")
        print(f"  {manifest['file_count']} file(s), "
              f"{manifest['total_size_bytes']:,} bytes "
              f"({manifest['total_size_bytes']/1024:.1f} KB)")
        cats = manifest["summary_by_category"]
        for cat in sorted(cats):
            print(f"    {cat:30s} {cats[cat]:4d}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
