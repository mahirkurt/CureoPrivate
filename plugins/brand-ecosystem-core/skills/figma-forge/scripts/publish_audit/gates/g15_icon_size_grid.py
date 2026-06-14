"""Gate 15 — All icon COMPONENTS must follow the size/grid convention.

Where G14 checks that icon-shaped nodes are wrapped as components, G15
checks that those components have **canonical** dimensions:
  * Bounding box width × height ∈ {16×16, 20×20, 24×24, 32×32, 48×48}
    (±1 px tolerance for snap/rounding artifacts).
  * Square geometry (|w − h| ≤ 1).

G15 only runs against icon components — components living in the Icons
file (registry mode) or on a page named "Icons" (single-file mode). This
keeps the gate from flagging non-icon components with small bounding
boxes (e.g. a Badge component).

This gate is **warn**-severity: non-canonical icons still render but
break the spacing system and signal an icon authoring mistake that the
team should resolve before publish.
"""

from __future__ import annotations

from ..calibration import (
    BoundaryDecision,
    CalibrationProbe,
    bucket_canonical,
    register_calibrator,
)
from ..context import FigmaFile, MultiFileFigmaContext
from ..models import GateResult, walk_nodes
from ..gates_registry import get_gate, register_gate
from .g14_icons_are_components import (
    CANONICAL_ICON_SIZES,
    ICON_SIZE_TOLERANCE_PX,
    ICON_SQUARENESS_TOLERANCE_PX,
    _bounding_box,
    _is_on_icon_page,
)


def _is_icon_component(component_meta: dict, *, on_icons_file: bool) -> bool:
    """Heuristic: this component is an icon if either we're in the Icons
    file, or its name suggests it's an icon."""
    if on_icons_file:
        return True
    name = (component_meta.get("name") or "").lower()
    return name.startswith("icon") or "/icon" in name or " icon" in name


def _find_component_node(document: dict, component_id: str) -> tuple[dict, str | None] | None:
    """Walk the document to locate the COMPONENT node matching ``component_id``."""
    for node, page in walk_nodes(document):
        if node.get("type") == "COMPONENT" and node.get("id") == component_id:
            return node, page
    return None


def _check_icon_dimensions(node: dict) -> tuple[bool, str]:
    """Return ``(ok, reason)`` for an icon node."""
    bbox = _bounding_box(node)
    if bbox is None:
        return False, "no bounding box (cannot verify size)"
    w, h = bbox
    if abs(w - h) > ICON_SQUARENESS_TOLERANCE_PX:
        return False, f"non-square geometry ({w:.1f} × {h:.1f} px)"
    matched = None
    for canon in CANONICAL_ICON_SIZES:
        if abs(w - canon) <= ICON_SIZE_TOLERANCE_PX:
            matched = canon
            break
    if matched is None:
        return (
            False,
            f"size {w:.1f}×{h:.1f} not in canonical set "
            f"{CANONICAL_ICON_SIZES} (±{ICON_SIZE_TOLERANCE_PX}px tolerance)"
        )
    return True, ""


def _publishable_role_is_icons(ctx: MultiFileFigmaContext, role: str) -> bool:
    if ctx.registry is None:
        return False
    return role == "icons"


def _file_has_icons_page(f: FigmaFile) -> bool:
    for node, page in walk_nodes(f.document):
        if node.get("type") == "CANVAS" and _is_on_icon_page(node.get("name")):
            return True
    return False


def _file_yields_icon_checks(ctx: MultiFileFigmaContext, role: str, f) -> bool:
    """Decide whether this publishable file should be scanned for icons."""
    return _publishable_role_is_icons(ctx, role) or _file_has_icons_page(f)


def _iter_icon_components(ctx: MultiFileFigmaContext, role: str, f):
    """Yield (component_id, comp_meta, node, on_icons_file) for each
    icon-like component on this file. Filters out variants and
    non-Icons-page nodes in single-file mode."""
    on_icons_file = _publishable_role_is_icons(ctx, role)
    for cid, comp in f.components.items():
        if comp.get("componentSetId"):
            continue  # variant children handled via parent set
        if not _is_icon_component(comp, on_icons_file=on_icons_file):
            continue
        located = _find_component_node(f.document, cid)
        if located is None:
            continue
        node, page = located
        if not on_icons_file and not _is_on_icon_page(page):
            continue
        yield cid, comp, node, on_icons_file


@register_gate(15)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Verify every icon component has a square canonical bounding box."""
    res = GateResult(gate=get_gate(15))
    any_icons_seen = False
    for role, f in ctx.iter_publishable_files():
        if not _file_yields_icon_checks(ctx, role, f):
            continue
        for cid, comp, node, _on_icons_file in _iter_icon_components(ctx, role, f):
            any_icons_seen = True
            res.checked_count += 1
            ok, reason = _check_icon_dimensions(node)
            if not ok:
                res.add(f"[{role}] {comp.get('name', cid)} — {reason}", role=role)
    if not any_icons_seen:
        res.status = "n_a"
        res.notes.append(
            "No icon components located (no 'icons' registry role and no "
            "page named 'Icons'); G15 skipped."
        )
        return res
    res.mark_fail()
    return res


# ----------------------------------------------------------------------------
# Calibration probe — v0.2.1
# ----------------------------------------------------------------------------

@register_calibrator(15)
def calibrate(ctx: MultiFileFigmaContext) -> CalibrationProbe:
    """Capture size + squareness distributions for every icon component
    examined, plus boundary decisions where the bounding box is just
    outside the canonical-size tolerance.
    """
    probe = CalibrationProbe(gate_id=15)
    for role, f in ctx.iter_publishable_files():
        if not _file_yields_icon_checks(ctx, role, f):
            probe.increment_skip("no_icon_scope_for_file")
            continue
        for cid, comp, node, _on_icons_file in _iter_icon_components(ctx, role, f):
            probe.nodes_scanned += 1
            probe.candidates_filtered += 1
            bbox = _bounding_box(node)
            if bbox is None:
                probe.increment_skip("no_bbox")
                continue
            w, h = bbox
            probe.decisions_made += 1
            probe.increment_histogram(
                "width_buckets",
                bucket_canonical(w, CANONICAL_ICON_SIZES, ICON_SIZE_TOLERANCE_PX)
            )
            probe.increment_histogram(
                "height_buckets",
                bucket_canonical(h, CANONICAL_ICON_SIZES, ICON_SIZE_TOLERANCE_PX)
            )
            squareness = abs(w - h)
            probe.increment_histogram(
                "squareness_pixels", str(int(squareness))
            )
            ok, _reason = _check_icon_dimensions(node)
            probe.increment_histogram("verdict", "pass" if ok else "fail")
            # Boundary capture: just-outside canonical-size tolerance
            for dim_name, dim_value in (("width", w), ("height", h)):
                for canon in CANONICAL_ICON_SIZES:
                    delta = abs(dim_value - canon)
                    if ICON_SIZE_TOLERANCE_PX < delta <= ICON_SIZE_TOLERANCE_PX + 2:
                        probe.add_boundary(BoundaryDecision(
                            node_id=str(cid),
                            node_name=str(comp.get("name", "<unnamed>")),
                            feature_name=f"{dim_name}_distance_to_canonical_{canon}",
                            feature_value=delta,
                            threshold=float(ICON_SIZE_TOLERANCE_PX),
                            verdict="fail" if not ok else "pass",
                            would_flip_at=delta - 0.5,
                            gate_role=role,
                        ))
                        break
    if probe.candidates_filtered == 0:
        probe.notes.append(
            "No icon components evaluated. Calibration for G15 unavailable."
        )
    return probe
