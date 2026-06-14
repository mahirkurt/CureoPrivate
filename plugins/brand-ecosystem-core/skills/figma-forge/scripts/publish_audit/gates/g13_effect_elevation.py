"""Gate 13 — Effect styles used for elevation must name-bind to elevation
tokens.

The design-system contract: shadows that represent UI elevation come from
a canonical elevation scale (typically elevation/1..elevation/N). Hand-
authored drop shadows that don't bind to this scale silently fragment
the elevation language across the library.

Detection strategy:

  1. Locate every published EFFECT style in publishable files
     (``file.styles`` filtered to ``styleType == "EFFECT"``).
  2. Categorize each effect style by name:
     * **Elevation-bound** — name matches ``elevation/...`` pattern
       (case-insensitive). These pass.
     * **Decorative** — name suggests non-elevation purpose (``glow``,
       ``inner shadow``, ``focus ring``, ``card-outline``). These pass
       with a note.
     * **Ambiguous** — names like ``shadow-1``, ``drop-shadow``,
       ``card``, or anything not matching the two categories above.
       These **fail** the gate — they should either rename to the
       elevation scale or move to Candidates.
  3. Cross-check: every elevation-bound style should appear referenced
     by at least one node. Unreferenced elevation styles trigger a note
     (suggesting the token may have been deprecated upstream).

Severity: ``warn`` — non-bound effects don't break publish but degrade
the system's coherence.
"""

from __future__ import annotations

import re

from ..context import FigmaFile, MultiFileFigmaContext
from ..models import GateResult, walk_nodes
from ..gates_registry import get_gate, register_gate


# Pattern for elevation-style names: `elevation/`, `Elevation / `,
# `elev-`, `elev_`, `e1`/`e2`/etc.
ELEVATION_NAME_RE = re.compile(
    r"^\s*(?:elevation|elev)\b[/\s_-]+\w+",
    re.IGNORECASE
)

DECORATIVE_EFFECT_HINTS = (
    "glow", "inner shadow", "focus", "ring", "outline",
    "highlight", "blur", "noise", "gradient overlay"
)


def _classify_effect_style(name: str) -> str:
    """Return one of: 'elevation', 'decorative', 'ambiguous'."""
    if ELEVATION_NAME_RE.match(name or ""):
        return "elevation"
    lower = (name or "").lower()
    if any(hint in lower for hint in DECORATIVE_EFFECT_HINTS):
        return "decorative"
    return "ambiguous"


def _collect_referenced_effect_ids(f: FigmaFile) -> set[str]:
    """Return the set of effect-style IDs referenced anywhere in the doc."""
    refs: set[str] = set()
    for node, _page in walk_nodes(f.document):
        styles = node.get("styles") or {}
        if isinstance(styles, dict):
            sid = styles.get("effect")
            if isinstance(sid, str) and sid:
                refs.add(sid)
        for effect in node.get("effects") or []:
            bound = effect.get("boundStyleId")
            if isinstance(bound, str) and bound:
                refs.add(bound)
    return refs


@register_gate(13)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Classify each effect style as elevation, decorative, or ambiguous; flag ambiguous styles."""
    res = GateResult(gate=get_gate(13))
    any_effects_seen = False
    for role, f in ctx.iter_publishable_files():
        effect_styles = {
            sid: meta for sid, meta in f.styles.items()
            if meta.get("styleType") == "EFFECT"
        }
        if not effect_styles:
            continue
        any_effects_seen = True
        referenced = _collect_referenced_effect_ids(f)
        for sid, meta in effect_styles.items():
            res.checked_count += 1
            name = meta.get("name", sid)
            classification = _classify_effect_style(name)
            if classification == "elevation":
                if sid not in referenced:
                    res.notes.append(
                        f"[{role}] elevation effect {name!r} declared but "
                        f"never referenced — may be deprecated."
                    )
                continue
            if classification == "decorative":
                # Pass with no finding; just note for transparency
                res.notes.append(
                    f"[{role}] decorative effect {name!r} not required to "
                    f"bind to elevation."
                )
                continue
            # Ambiguous → fail
            res.add(
                f"[{role}] effect style {name!r} — name does not match "
                f"the elevation token convention "
                f"(expected pattern: elevation/N or elev-N)",
                role=role
            )
    if not any_effects_seen:
        res.status = "n_a"
        res.notes.append(
            "No EFFECT styles declared in any publishable file; G13 skipped."
        )
        return res
    res.mark_fail()
    return res


# ----------------------------------------------------------------------------
# Calibration probe — v0.2.1
# ----------------------------------------------------------------------------

from ..calibration import (
    BoundaryDecision,
    CalibrationProbe,
    register_calibrator,
)


def _name_distance_to_elevation(name: str) -> int | None:
    """Return how many edits the name is from matching ELEVATION_NAME_RE.

    Used to flag near-misses: a style named ``elevation1`` (missing
    separator) or ``elev/1`` (passing) versus ``Shadow/1`` (ambiguous).
    Returns ``None`` when no elevation root token is present.
    """
    lower = (name or "").lower()
    if "elevation" in lower:
        if ELEVATION_NAME_RE.match(name):
            return 0
        return 1  # has the root but missing separator/scale
    if "elev" in lower:
        if ELEVATION_NAME_RE.match(name):
            return 0
        return 1
    return None


def _probe_effect_style(probe: CalibrationProbe, sid: str, meta: dict,
                          referenced: set, role: str) -> None:
    """Record per-effect-style probe data: classification, references,
    near-miss boundary, and decorative-hint matching.
    """
    probe.nodes_scanned += 1
    probe.candidates_filtered += 1
    probe.decisions_made += 1
    name = meta.get("name", sid)
    classification = _classify_effect_style(name)
    probe.increment_histogram("classification", classification)
    if classification == "elevation":
        probe.increment_histogram(
            "elevation_referenced", "yes" if sid in referenced else "no"
        )
    distance = _name_distance_to_elevation(name)
    if distance is not None and distance > 0:
        probe.add_boundary(BoundaryDecision(
            node_id=str(sid),
            node_name=str(name),
            feature_name="elevation_regex_distance",
            feature_value=float(distance),
            threshold=0.0,
            verdict=classification,
            would_flip_at=0.0,
            gate_role=role,
        ))
    lower = (name or "").lower()
    for hint in DECORATIVE_EFFECT_HINTS:
        if hint in lower:
            probe.increment_histogram("decorative_hint_matched", hint)
            break


@register_calibrator(13)
def calibrate(ctx: MultiFileFigmaContext) -> CalibrationProbe:
    """Capture the classification distribution across effect styles and
    record near-misses where the name contains an elevation root token
    but fails the strict regex (most common cause: missing separator)."""
    probe = CalibrationProbe(gate_id=13)
    for role, f in ctx.iter_publishable_files():
        effect_styles = {
            sid: meta for sid, meta in f.styles.items()
            if meta.get("styleType") == "EFFECT"
        }
        if not effect_styles:
            probe.increment_skip("no_effect_styles_in_file")
            continue
        referenced = _collect_referenced_effect_ids(f)
        for sid, meta in effect_styles.items():
            _probe_effect_style(probe, sid, meta, referenced, role)
    if probe.candidates_filtered == 0:
        probe.notes.append("No effect styles evaluated. G13 calibration unavailable.")
    return probe
