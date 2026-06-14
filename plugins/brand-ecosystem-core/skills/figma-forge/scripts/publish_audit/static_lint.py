"""publish_audit static-only lint (v0.3.0-rc).

Closes Düstur build lesson L4: bundle-level integrity checks that do
not require a live Figma file_key or PAT. Suitable for CI runs without
secrets, pre-publish gates, and offline validation.

The nine lint dimensions:

    L1  JSON validity — every *.json file parses cleanly
    L2  Primitive token count — color family × LCH step count
    L3  Alias resolvability — every DTCG alias resolves against the path index
    L4  Component spec schema — required fields + variants.expected_count present
    L5  Pattern → component reference consistency — uses_components targets exist
    L6  SVG validity — every SVG has <svg>…</svg> + viewBox
    L7  Code Connect completeness — one mapping per component spec
    L8  Manifest completeness — manifest.json files set == on-disk files set
    L9  Accessibility coverage — WCAG target + APCA + diacritic audit declared

Each check maps to a synthetic gate id (L1→100, …, L9→108) so the JSON
audit report can carry static-lint findings in the same schema v1.0
shape as live gates.

Public API:
    run_static_lint(library_dir) → list[GateResult]
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .models import Gate, GateResult


# ---------------------------------------------------------------------------
# Synthetic gate catalogue
# ---------------------------------------------------------------------------

_STATIC_GATE_BASE = 100  # Static lint gates use IDs 100..108

_STATIC_GATES = [
    Gate(
        id=100, name="JSON validity", severity="error",
        description="Every *.json file in the bundle parses cleanly.",
        remediation="Run `python -m json.tool` on each failure; fix syntax.",
    ),
    Gate(
        id=101, name="Primitive token count", severity="error",
        description="Each declared color family has the expected number of LCH steps "
                    "(default: 12 per family, 6 families).",
        remediation="Either complete the family or declare a partial step set in "
                    "library-registry.color_families[].expected_steps.",
    ),
    Gate(
        id=102, name="DTCG alias resolvability", severity="error",
        description="Every DTCG alias literal resolves against the merged path index.",
        remediation="Use auto_remediate G13 to rewrite alias paths.",
    ),
    Gate(
        id=103, name="Component spec schema", severity="error",
        description="Each component spec carries the required fields and a coherent "
                    "variants block.",
        remediation="Use auto_remediate G07 to populate variants.expected_count.",
    ),
    Gate(
        id=104, name="Pattern → component referential integrity", severity="warn",
        description="Every component named in a pattern's uses_components actually "
                    "exists as a component spec.",
        remediation="Either add the missing component spec or rename the reference.",
    ),
    Gate(
        id=105, name="SVG validity", severity="error",
        description="Every SVG file has a well-formed <svg>…</svg> with a viewBox attribute.",
        remediation="Use auto_remediate G14 to inject viewBox + <title>.",
    ),
    Gate(
        id=106, name="Code Connect completeness", severity="warn",
        description="Every component spec has a corresponding code-connect/<id>.json mapping.",
        remediation="Use auto_remediate G17 to synthesize missing mappings.",
    ),
    Gate(
        id=107, name="Manifest completeness", severity="warn",
        description="manifest.json lists exactly the on-disk files (no additions, no removals).",
        remediation="Re-run `bundle_manifest.py` to refresh.",
    ),
    Gate(
        id=108, name="Accessibility coverage declaration", severity="warn",
        description="library-registry.json declares WCAG target, APCA enablement, "
                    "and TR diacritic audit set.",
        remediation="Add the accessibility block to library-registry.json.",
    ),
]
_GATE_BY_ID = {g.id: g for g in _STATIC_GATES}


# ---------------------------------------------------------------------------
# Per-check implementations
# ---------------------------------------------------------------------------

def _find_merged_dtcg(library_dir: Path) -> Path | None:
    """Locate the merged DTCG token file in a bundle.

    Resolution order:
    1. ``library-registry.json``'s ``merged_dtcg`` field (explicit)
    2. ``library-registry.json``'s ``ds_name`` lowercased + ".tokens.json"
    3. Common conventional locations: ``tokens/*.tokens.json`` (first match)

    Returns ``None`` if no merged DTCG can be located.
    """
    reg = library_dir / "library-registry.json"
    if reg.exists():
        try:
            data = json.loads(reg.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        merged = data.get("merged_dtcg")
        if isinstance(merged, str):
            cand = library_dir / merged
            if cand.exists():
                return cand
        ds_name = data.get("ds_name")
        if isinstance(ds_name, str):
            # Slugify: lowercase, remove non-alphanumeric except hyphens
            slug = re.sub(r"[^a-z0-9-]+", "", ds_name.lower().replace(" ", "-"))
            cand = library_dir / "tokens" / f"{slug}.tokens.json"
            if cand.exists():
                return cand

    # Last resort: pick the first *.tokens.json under tokens/
    tokens_dir = library_dir / "tokens"
    if tokens_dir.exists():
        candidates = sorted(tokens_dir.glob("*.tokens.json"))
        if candidates:
            return candidates[0]
    return None


def run_static_lint(library_dir: Path) -> list[GateResult]:
    """Run all nine static lint dimensions against ``library_dir``."""
    merged_dtcg = _find_merged_dtcg(library_dir)
    results: list[GateResult] = []
    results.append(_l1_json_validity(library_dir))
    results.append(_l2_primitive_token_count(library_dir, merged_dtcg))
    results.append(_l3_alias_resolvability(library_dir, merged_dtcg))
    results.append(_l4_component_spec_schema(library_dir))
    results.append(_l5_pattern_reference_integrity(library_dir))
    results.append(_l6_svg_validity(library_dir))
    results.append(_l7_code_connect_completeness(library_dir))
    results.append(_l8_manifest_completeness(library_dir))
    results.append(_l9_accessibility_coverage(library_dir))
    for r in results:
        r.mark_fail()
    return results


def _l1_json_validity(library_dir: Path) -> GateResult:
    r = GateResult(gate=_GATE_BY_ID[100])
    files = sorted(library_dir.rglob("*.json"))
    r.checked_count = len(files)
    for p in files:
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            r.add(f"{p.relative_to(library_dir)} — parse error: {e}")
    return r


def _l2_primitive_token_count(library_dir: Path, merged_dtcg: Path | None) -> GateResult:
    r = GateResult(gate=_GATE_BY_ID[101])
    if merged_dtcg is None or not merged_dtcg.exists():
        r.notes.append("No merged DTCG token file found (skipping)")
        return r
    try:
        tokens = json.loads(merged_dtcg.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return r

    color = tokens.get("color")
    if not isinstance(color, dict):
        r.notes.append("No 'color' branch in merged DTCG (skipping)")
        return r

    # Read per-family expected_steps from library-registry.
    # When color_families is declared, ONLY those families are checked
    # (alias dives like ``color.semantic`` are correctly skipped).
    # When color_families is absent, fall back to scanning every
    # immediate child of ``color`` against the default expected_steps.
    reg = library_dir / "library-registry.json"
    family_expected: dict[str, int] = {}
    default_expected = 12
    color_families_declared = False
    if reg.exists():
        try:
            reg_data = json.loads(reg.read_text(encoding="utf-8"))
            families = reg_data.get("color_families")
            # Two coexisting registry shapes:
            #
            # 1. List-of-dicts (Material 3, Carbon convention):
            #    "color_families": [{"name": "gray", "expected_steps": 10}]
            #    → Enables the L2 allow-list because the count expectation
            #      is explicit per family.
            #
            # 2. Dict-keyed (Düstur Tasarım Sistemi convention):
            #    "color_families": {"tbk": {"name": "TBK (Türk...)", ...}}
            #    → Carries no per-family expected_steps; the L2 gate falls
            #      back to "scan every family" mode below. This is correct:
            #      Düstur's metadata describes families for documentation,
            #      not for count-budget assertions, and the test fixture
            #      ships with all primitive scales filled in.
            if isinstance(families, list):
                color_families_declared = True
                for entry in families:
                    if isinstance(entry, dict) and "name" in entry and "expected_steps" in entry:
                        family_expected[str(entry["name"])] = int(entry["expected_steps"])
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    families_checked = 0
    for family_name, family in color.items():
        if family_name.startswith("$") or not isinstance(family, dict):
            continue
        # When color_families is declared, treat it as an allow-list:
        # families absent from the list are alias dives or semantic
        # branches — not primitives — and must not be counted.
        if color_families_declared and family_name not in family_expected:
            continue
        leaves = [k for k, v in family.items()
                  if isinstance(v, dict) and "$value" in v]
        if not leaves:
            continue
        families_checked += 1
        expected = family_expected.get(family_name, default_expected)
        if len(leaves) != expected:
            r.add(f"color.{family_name}: {len(leaves)} steps "
                  f"(expected {expected})")
    r.checked_count = families_checked
    if families_checked == 0:
        r.notes.append("No primitive color families detected — skipping count check")
    return r


def _l3_alias_resolvability(library_dir: Path, merged_dtcg: Path | None) -> GateResult:
    r = GateResult(gate=_GATE_BY_ID[102])
    if merged_dtcg is None or not merged_dtcg.exists():
        r.notes.append("No merged DTCG token file found (skipping)")
        return r
    try:
        tokens = json.loads(merged_dtcg.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return r

    paths: set[str] = set()
    _walk_paths(tokens, "", paths)

    alias_re = re.compile(r"^\{([^}]+)\}$")
    total = unresolved = 0

    def _scan(node, prefix=""):
        nonlocal total, unresolved
        if isinstance(node, dict):
            if "$value" in node and isinstance(node["$value"], str):
                m = alias_re.match(node["$value"])
                if m:
                    total += 1
                    if m.group(1) not in paths:
                        unresolved += 1
                        r.add(f"{prefix} → unresolved alias {{{m.group(1)}}}")
            else:
                for k, v in node.items():
                    if k.startswith("$"):
                        continue
                    _scan(v, f"{prefix}.{k}" if prefix else k)

    _scan(tokens)
    r.checked_count = total
    if total > 0 and unresolved == 0:
        r.notes.append(f"All {total} aliases resolve cleanly")
    return r


def _l4_component_spec_schema(library_dir: Path) -> GateResult:
    r = GateResult(gate=_GATE_BY_ID[103])
    comp_dir = library_dir / "components"
    if not comp_dir.exists():
        r.notes.append("components/ directory not present (skipping)")
        return r
    specs = sorted(comp_dir.glob("*.json"))
    r.checked_count = len(specs)
    required = {"$schema", "component", "variants"}
    for p in specs:
        try:
            spec = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            r.add(f"{p.name}: invalid JSON")
            continue
        missing = required - set(spec.keys())
        if missing:
            r.add(f"{p.name}: missing fields {sorted(missing)}")
        if isinstance(spec.get("variants"), dict) and "expected_count" not in spec["variants"]:
            r.add(f"{p.name}: variants.expected_count missing")
    return r


def _l5_pattern_reference_integrity(library_dir: Path) -> GateResult:
    r = GateResult(gate=_GATE_BY_ID[104])
    comp_dir = library_dir / "components"
    pat_dir = library_dir / "patterns"
    if not comp_dir.exists() or not pat_dir.exists():
        r.notes.append("components/ or patterns/ not present (skipping)")
        return r
    component_names: set[str] = set()
    for p in comp_dir.glob("*.json"):
        try:
            spec = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        carbon = spec.get("component", {}).get("name_carbon")
        if carbon:
            component_names.add(carbon)

    patterns = sorted(pat_dir.glob("*.json"))
    r.checked_count = len(patterns)
    for p in patterns:
        try:
            spec = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        used = spec.get("composition", {}).get("uses_components", []) or []
        for c in used:
            if c not in component_names:
                r.add(f"{p.name}: references unknown component {c!r}")
    return r


def _l6_svg_validity(library_dir: Path) -> GateResult:
    r = GateResult(gate=_GATE_BY_ID[105])
    svg_dir = library_dir / "icons" / "svg"
    if not svg_dir.exists():
        r.notes.append("icons/svg/ not present (skipping)")
        return r
    svgs = sorted(svg_dir.rglob("*.svg"))
    r.checked_count = len(svgs)
    for p in svgs:
        text = p.read_text(encoding="utf-8")
        if not (text.lstrip().startswith("<svg") and text.rstrip().endswith("</svg>")):
            r.add(f"{p.relative_to(library_dir)}: not a valid SVG envelope")
            continue
        if "viewBox" not in text:
            r.add(f"{p.relative_to(library_dir)}: missing viewBox attribute")
    return r


def _l7_code_connect_completeness(library_dir: Path) -> GateResult:
    r = GateResult(gate=_GATE_BY_ID[106])
    comp_dir = library_dir / "components"
    cc_dir = library_dir / "code-connect"
    if not comp_dir.exists():
        r.notes.append("components/ not present (skipping)")
        return r
    if not cc_dir.exists():
        r.add("code-connect/ directory missing entirely")
        return r
    cc_ids = {p.stem for p in cc_dir.glob("*.json")}
    expected_ids = set()
    for p in comp_dir.glob("*.json"):
        # spec stem like "01-yuzey-badge" → component id "yuzey-badge"
        stem = re.sub(r"^\d+-", "", p.stem)
        expected_ids.add(stem)
    r.checked_count = len(expected_ids)
    missing = expected_ids - cc_ids
    for cid in sorted(missing):
        r.add(f"Missing Code Connect mapping: code-connect/{cid}.json")
    return r


def _l8_manifest_completeness(library_dir: Path) -> GateResult:
    r = GateResult(gate=_GATE_BY_ID[107])
    manifest_path = library_dir / "manifest.json"
    if not manifest_path.exists():
        r.notes.append("manifest.json not present (skipping)")
        return r
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        r.add("manifest.json fails JSON parse")
        return r
    manifest_files = {f["path"] for f in manifest.get("files", [])}
    actual_files: set[str] = set()
    for p in library_dir.rglob("*"):
        if not p.is_file() or p.name.startswith("."):
            continue
        if p.name == "manifest.json":
            continue
        if any(part in {"__pycache__", ".git", "node_modules"} for part in p.parts):
            continue
        actual_files.add(str(p.relative_to(library_dir)))
    r.checked_count = max(len(manifest_files), len(actual_files))
    for added in sorted(actual_files - manifest_files):
        r.add(f"Not in manifest: {added}")
    for removed in sorted(manifest_files - actual_files):
        r.add(f"Listed in manifest but missing on disk: {removed}")
    return r


def _l9_accessibility_coverage(library_dir: Path) -> GateResult:
    r = GateResult(gate=_GATE_BY_ID[108])
    reg = library_dir / "library-registry.json"
    if not reg.exists():
        r.notes.append("library-registry.json not present (skipping)")
        return r
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        r.add("library-registry.json fails JSON parse")
        return r
    a11y = data.get("accessibility")
    if not isinstance(a11y, dict):
        r.add("library-registry.accessibility block missing")
        return r
    if not a11y.get("wcag_target"):
        r.add("accessibility.wcag_target missing")
    if "apca_enabled" not in a11y:
        r.add("accessibility.apca_enabled missing")
    diac = a11y.get("tr_diacritics_audit") or []
    if set(diac) != {"Ç", "Ğ", "İ", "Ö", "Ş", "Ü"}:
        r.add(f"accessibility.tr_diacritics_audit incomplete: {diac}")
    r.checked_count = 3  # Three sub-checks above
    return r


# ---------------------------------------------------------------------------
# Path walker
# ---------------------------------------------------------------------------

def _walk_paths(node, prefix: str, out: set[str]) -> None:
    if isinstance(node, dict):
        if "$value" in node:
            out.add(prefix)
        else:
            for k, v in node.items():
                if k.startswith("$"):
                    continue
                p = f"{prefix}.{k}" if prefix else k
                _walk_paths(v, p, out)
