"""Gate 14 — Icon-shaped nodes must be COMPONENT or INSTANCE, never raw
VECTOR or GROUP.

This is the hardest gate to get right. Figma has no "this is an icon"
marker on a node; we infer iconhood via geometric and contextual heuristics.

Heuristic stack:

1. **Bounding box** — node has a defined absoluteBoundingBox AND:
     * width and height are both in [12, 64] px, AND
     * |width − height| ≤ 2 (approximately square), AND
     * either width or height is in the canonical set {16, 20, 24, 32, 48}
       OR ±1 from it (tolerance for visual rounding).

2. **Type** — node type is VECTOR, GROUP, or BOOLEAN_OPERATION.

3. **Context** — node lives on a page named "Icons", "Icon", "icon", or
   on the Icons file (registry role == "icons").

4. **Negative signals** — node is a child of a frame named like a swatch
   demo, or has a name containing "decorator", "ornament", "background".

Default severity for failures is the gate's declared ``error`` level only
when the icon is in registry role ``icons``; in other contexts (icon-like
nodes on a Components or Foundations page) the gate downgrades to
``warn`` severity via a note — these may be legitimate decorations rather
than reusable icons.

The thresholds and canonical sizes are exposed as module-level constants
so operators can tune them via the future ``--config`` mechanism (v0.3.0).
"""

from __future__ import annotations

from typing import Iterable

from ..calibration import (
    BoundaryDecision,
    CalibrationProbe,
    bucket_canonical,
    register_calibrator,
)
from ..context import FigmaFile, MultiFileFigmaContext
from ..models import GateResult, walk_nodes
from ..gates_registry import get_gate, register_gate


# ----------------------------------------------------------------------------
# Heuristic configuration
# ----------------------------------------------------------------------------

CANONICAL_ICON_SIZES = (16, 20, 24, 32, 48)
ICON_SIZE_TOLERANCE_PX = 1                       # ±1 px around canonical sizes
ICON_BBOX_MIN = 12                               # smallest plausible icon
ICON_BBOX_MAX = 64                               # largest plausible icon
ICON_SQUARENESS_TOLERANCE_PX = 2                 # |w-h| ≤ this is "square enough"

ICON_FRIENDLY_NODE_TYPES = {"VECTOR", "GROUP", "BOOLEAN_OPERATION"}
ICON_PAGE_HINTS = ("icon", "ikon")
DECORATIVE_NAME_HINTS = ("decorator", "ornament", "background", "watermark",
                          "swatch", "demo", "preview")


# ----------------------------------------------------------------------------
# Heuristic functions
# ----------------------------------------------------------------------------

def _bounding_box(node: dict) -> tuple[float, float] | None:
    """Return (width, height) from absoluteBoundingBox, or None if absent."""
    bbox = node.get("absoluteBoundingBox")
    if not isinstance(bbox, dict):
        return None
    w = bbox.get("width")
    h = bbox.get("height")
    if not (isinstance(w, (int, float)) and isinstance(h, (int, float))):
        return None
    return float(w), float(h)


def _is_canonical_icon_dim(dim: float) -> bool:
    """True iff ``dim`` is within ±tolerance of any canonical icon size."""
    return any(abs(dim - canon) <= ICON_SIZE_TOLERANCE_PX
               for canon in CANONICAL_ICON_SIZES)


def _has_iconish_geometry(node: dict) -> bool:
    """Geometric test: bounding box looks like an icon."""
    bbox = _bounding_box(node)
    if bbox is None:
        return False
    w, h = bbox
    if not (ICON_BBOX_MIN <= w <= ICON_BBOX_MAX and ICON_BBOX_MIN <= h <= ICON_BBOX_MAX):
        return False
    if abs(w - h) > ICON_SQUARENESS_TOLERANCE_PX:
        return False
    return _is_canonical_icon_dim(w) or _is_canonical_icon_dim(h)


def _is_on_icon_page(page_name: str | None) -> bool:
    if not page_name:
        return False
    lower = page_name.lower()
    return any(hint in lower for hint in ICON_PAGE_HINTS)


def _has_decorative_name(node: dict) -> bool:
    name = (node.get("name") or "").lower()
    return any(hint in name for hint in DECORATIVE_NAME_HINTS)


def _is_inside_component(node_path: Iterable[dict]) -> bool:
    """True if any ancestor is a COMPONENT — icons inside other components
    are part of a larger artwork, not standalone icons that need wrapping."""
    return any(p.get("type") in ("COMPONENT", "COMPONENT_SET", "INSTANCE")
               for p in node_path)


# ----------------------------------------------------------------------------
# Traversal with parent-chain tracking
# ----------------------------------------------------------------------------

def _walk_with_parents(node: dict, parent_page: str | None = None,
                        path: tuple[dict, ...] = ()):
    """Like ``walk_nodes`` but also yields the ancestor chain."""
    if node.get("type") == "CANVAS":
        parent_page = node.get("name", "")
    yield node, parent_page, path
    new_path = path + (node,)
    for child in node.get("children") or []:
        yield from _walk_with_parents(child, parent_page, new_path)


def _iter_icon_candidates(f: FigmaFile, *, role: str) -> Iterable[tuple[dict, str]]:
    """Yield (node, page_name) for each node that *looks like* an icon but
    isn't wrapped as a component."""
    is_icons_file = (role == "icons")
    for node, page, parents in _walk_with_parents(f.document):
        node_type = node.get("type")
        if node_type not in ICON_FRIENDLY_NODE_TYPES:
            continue
        if _has_decorative_name(node):
            continue
        if _is_inside_component(parents):
            continue
        on_icon_page = _is_on_icon_page(page)
        if not (is_icons_file or on_icon_page):
            # The geometric test alone is too permissive outside icon
            # contexts — skip to keep false-positive rate manageable.
            continue
        if not _has_iconish_geometry(node):
            continue
        yield node, page or ""


# ----------------------------------------------------------------------------
# Gate entry
# ----------------------------------------------------------------------------

@register_gate(14)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Detect icon-shaped raw VECTOR/GROUP nodes outside any component wrapper."""
    res = GateResult(gate=get_gate(14))
    for role, f in ctx.iter_publishable_files():
        for node, page in _iter_icon_candidates(f, role=role):
            res.checked_count += 1
            res.add(
                f"[{role}] {page} → {node.get('type')} {node.get('name', '<unnamed>')!r}: "
                f"icon-shaped node is not a COMPONENT/INSTANCE",
                role=role
            )
    if res.checked_count == 0:
        res.notes.append(
            "No icon-shaped candidates found. If you expected icons, "
            "verify the registry declares an 'icons' role or the page is "
            "named 'Icons'."
        )
    res.mark_fail()
    return res


# ----------------------------------------------------------------------------
# Calibration probe — v0.2.1
# ----------------------------------------------------------------------------
#
# G14's heuristic stack has the highest false-positive risk in the gate
# catalog: seven signals (node type, page name, decorative-name filter,
# inside-component check, bounding box presence, size range, squareness,
# canonical-size proximity) combine to produce one binary verdict. The
# calibrator walks the document once and emits the full feature
# distribution plus every borderline decision — so the maintainer can
# inspect, across real libraries, which thresholds are operating near
# their edges.

def _classify_node_context(node: dict, parents: tuple,
                             page: str, on_icons_file: bool) -> str:
    """Return context-based skip reason ("" if not skipped).

    Checks the four contextual filters before any geometric tests:
    node type, decorative name pattern, component nesting, and
    icon-scope page. Geometric classification lives in
    ``_classify_node_geometry``.
    """
    if node.get("type") not in ICON_FRIENDLY_NODE_TYPES:
        return "wrong_type"
    if _has_decorative_name(node):
        return "decorative_name"
    if _is_inside_component(parents):
        return "inside_component"
    if not (on_icons_file or _is_on_icon_page(page)):
        return "out_of_icon_scope"
    return ""


def _classify_node_geometry(node: dict) -> str:
    """Return geometric skip reason ("" if all geometry checks pass)."""
    bbox = _bounding_box(node)
    if bbox is None:
        return "no_bbox"
    w, h = bbox
    if not (ICON_BBOX_MIN <= w <= ICON_BBOX_MAX
            and ICON_BBOX_MIN <= h <= ICON_BBOX_MAX):
        return "bbox_out_of_range"
    if abs(w - h) > ICON_SQUARENESS_TOLERANCE_PX:
        return "not_square"
    if not (_is_canonical_icon_dim(w) or _is_canonical_icon_dim(h)):
        return "not_canonical_size"
    return ""


def _classify_for_calibration(node: dict, parents: tuple,
                                page: str, on_icons_file: bool) -> tuple[str, bool]:
    """Return ``(skip_reason, would_be_flagged)`` for a single node.

    Dispatches to context and geometry classifiers, short-circuiting
    on the first non-empty skip reason. ``would_be_flagged`` is True
    iff the candidate would have been added to GateResult.failures.
    """
    skip = _classify_node_context(node, parents, page, on_icons_file)
    if skip:
        return skip, False
    skip = _classify_node_geometry(node)
    if skip:
        return skip, False
    return "", True


def _record_boundary_signals(probe: CalibrationProbe, node: dict,
                              role: str, bbox: tuple[float, float] | None) -> None:
    """Append BoundaryDecision entries for any threshold within 1 unit of value."""
    if bbox is None:
        return
    w, h = bbox
    squareness = abs(w - h)
    nid = str(node.get("id", "<no-id>"))
    nname = str(node.get("name", "<unnamed>"))
    # Boundary for squareness: tolerance is 2 px; flag values 2-4 px
    # since these would flip if the threshold moved to 1, 3, or 4.
    if 1 <= squareness <= ICON_SQUARENESS_TOLERANCE_PX + 2:
        verdict = "candidate" if squareness <= ICON_SQUARENESS_TOLERANCE_PX else "not_icon"
        probe.add_boundary(BoundaryDecision(
            node_id=nid,
            node_name=nname,
            feature_name="squareness_pixels",
            feature_value=squareness,
            threshold=ICON_SQUARENESS_TOLERANCE_PX,
            verdict=verdict,
            would_flip_at=squareness if verdict == "not_icon" else ICON_SQUARENESS_TOLERANCE_PX - 1,
            gate_role=role,
        ))
    # Boundary for canonical-size: a dim that is ±2 px from a canonical
    # value but outside the current ±1 tolerance is a borderline case.
    for dim_name, dim_value in (("width", w), ("height", h)):
        for canon in CANONICAL_ICON_SIZES:
            delta = abs(dim_value - canon)
            if ICON_SIZE_TOLERANCE_PX < delta <= ICON_SIZE_TOLERANCE_PX + 1:
                probe.add_boundary(BoundaryDecision(
                    node_id=nid,
                    node_name=nname,
                    feature_name=f"{dim_name}_near_canonical_{canon}",
                    feature_value=dim_value,
                    threshold=float(canon),
                    verdict="not_canonical",
                    would_flip_at=float(canon) + ICON_SIZE_TOLERANCE_PX + 1,
                    gate_role=role,
                ))
                break  # at most one canonical-size boundary per dimension


@register_calibrator(14)
def calibrate(ctx: MultiFileFigmaContext) -> CalibrationProbe:
    """Walk every node once, recording feature distributions, skip
    reasons, and threshold-boundary decisions for icon classification.

    The probe distinguishes "scanned" (walked at all) from "candidates"
    (reached the geometric tests) from "decisions" (received a final
    verdict). The skip_reasons histogram explains attrition at each
    filter stage.
    """
    probe = CalibrationProbe(gate_id=14)
    for role, f in ctx.iter_publishable_files():
        on_icons_file = (role == "icons")
        for node, page, parents in _walk_with_parents(f.document):
            probe.nodes_scanned += 1
            skip_reason, would_flag = _classify_for_calibration(
                node, parents, page or "", on_icons_file
            )
            if skip_reason:
                probe.increment_skip(skip_reason)
                continue
            probe.candidates_filtered += 1
            probe.decisions_made += 1
            bbox = _bounding_box(node)
            if bbox is not None:
                w, h = bbox
                probe.increment_histogram(
                    "width_buckets",
                    bucket_canonical(w, CANONICAL_ICON_SIZES, ICON_SIZE_TOLERANCE_PX)
                )
                probe.increment_histogram(
                    "squareness_pixels", str(int(abs(w - h)))
                )
            probe.increment_histogram(
                "verdict", "icon" if would_flag else "not_icon"
            )
            _record_boundary_signals(probe, node, role, bbox)
    if probe.candidates_filtered == 0:
        probe.notes.append(
            "No icon candidates evaluated. "
            "Calibration data for G14 is unavailable on this library."
        )
    return probe
