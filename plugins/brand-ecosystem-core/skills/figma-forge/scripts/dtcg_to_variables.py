#!/usr/bin/env python3
"""
dtcg_to_variables.py — Convert W3C DTCG token JSON into a Figma Variables REST API payload.

Usage:
    python3 dtcg_to_variables.py --input tokens.dtcg.json --output variables-payload.json

The output JSON is ready to POST to:
    POST https://api.figma.com/v1/files/:file_key/variables
with header  X-Figma-Token: <PAT>

This script ONLY produces the payload. The actual POST is performed by figma-forge's
REST client (Channel 2) or via a one-off curl.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from typing import Any


# ----------------------------------------------------------------------------
# Type mapping
# ----------------------------------------------------------------------------

DTCG_TO_FIGMA_TYPE: dict[str, str] = {
    "color":      "COLOR",
    "dimension":  "FLOAT",
    "number":     "FLOAT",
    "fontWeight": "FLOAT",
    "fontFamily": "STRING",
    "string":     "STRING",
    "boolean":    "BOOLEAN",
}

# Types that can't be expressed as Figma Variables (saved as metadata)
UNSUPPORTED_TYPES = {"shadow", "typography", "gradient", "duration",
                     "cubicBezier", "transition", "border"}


# ----------------------------------------------------------------------------
# Color helpers
# ----------------------------------------------------------------------------

HEX_RE = re.compile(r"^#([0-9A-Fa-f]{3,8})$")


def hex_to_rgba(hex_str: str) -> dict[str, float]:
    """Convert hex color to {r, g, b, a} with 0-1 floats."""
    m = HEX_RE.match(hex_str.strip())
    if not m:
        raise ValueError(f"Not a hex color: {hex_str!r}")
    h = m.group(1)
    if len(h) == 3:
        r, g, b, a = int(h[0]*2, 16), int(h[1]*2, 16), int(h[2]*2, 16), 255
    elif len(h) == 6:
        r, g, b, a = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255
    elif len(h) == 8:
        r, g, b, a = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16)
    else:
        raise ValueError(f"Hex color must be 3/6/8 chars after #: {hex_str!r}")
    return {"r": r/255, "g": g/255, "b": b/255, "a": a/255}


# ----------------------------------------------------------------------------
# Dimension helpers
# ----------------------------------------------------------------------------

DIM_RE = re.compile(r"^(-?[\d.]+)(px|rem|em)?$")

# Unit → multiplier resolver (rem/em normalize against rem_base; px is identity)
_UNIT_MULT = {"px": 1.0, "rem": None, "em": None}  # None = use rem_base


def _apply_unit(n: float, unit: str | None, rem_base: float) -> float:
    """Convert a numeric value + CSS-unit string into pixels."""
    if unit in (None, "px"):
        return n
    if unit in ("rem", "em"):
        return n * rem_base
    return n


def _parse_dim_dict(val: dict, rem_base: float) -> float:
    """Parse a Style Dictionary–style ``{value, unit}`` dimension dict."""
    return _apply_unit(float(val["value"]), val.get("unit", "px"), rem_base)


def _parse_dim_string(val: str, rem_base: float) -> float | None:
    """Parse a ``"16px"`` / ``"1rem"`` / ``"24"`` string. Returns None if not a dimension literal."""
    m = DIM_RE.match(val.strip())
    if not m:
        return None
    return _apply_unit(float(m.group(1)), m.group(2), rem_base)


def parse_dimension(val: Any, rem_base: float = 16.0) -> float:
    """Parse a dimension value to its pixel float representation.

    Accepts: numeric literals, ``{value, unit}`` dicts (Style Dictionary
    shape), or strings like ``"16px"`` / ``"1rem"`` / ``"24"``. Unit
    conversion is delegated to ``_apply_unit`` (rem/em both normalized
    against ``rem_base``, default 16). Raises ``ValueError`` on unparseable
    input.
    """
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, dict) and "value" in val:
        return _parse_dim_dict(val, rem_base)
    if isinstance(val, str):
        result = _parse_dim_string(val, rem_base)
        if result is not None:
            return result
    raise ValueError(f"Cannot parse dimension: {val!r}")


# ----------------------------------------------------------------------------
# Tree walking
# ----------------------------------------------------------------------------

def is_leaf(node: Any) -> bool:
    return isinstance(node, dict) and "$value" in node


def walk_tokens(tree: Any, prefix: str = "") -> list[tuple[str, dict]]:
    """Walk DTCG tree, returning [(path, leaf_dict)]."""
    leaves = []
    if is_leaf(tree):
        return [(prefix, tree)]
    if isinstance(tree, dict):
        for key, child in tree.items():
            if key.startswith("$"):
                continue
            child_path = f"{prefix}.{key}" if prefix else key
            leaves.extend(walk_tokens(child, child_path))
    return leaves


# ----------------------------------------------------------------------------
# Collection grouping
# ----------------------------------------------------------------------------

def infer_collection(path: str) -> str:
    """Determine the Figma collection name from the token path."""
    if path.startswith("color.primitive"):
        return "Primitives — Color"
    if path.startswith("color.semantic") or path.startswith("color.component"):
        return "Semantic — Color"
    if path.startswith("color."):
        return "Primitives — Color"
    if path.startswith("dimension."):
        return "Primitives — Dimension"
    if path.startswith("font."):
        return "Primitives — Typography"
    if path.startswith("opacity") or path.startswith("z-index"):
        return "Primitives — Misc"
    return "Primitives — Other"


def has_mode_object(leaf: dict) -> bool:
    """
    Detect if leaf's $value is a multi-mode dict.

    For COLOR-type leaves, a dict $value indicates multiple modes (each key is a mode name).
    For COMPOSITE types (typography, shadow, gradient, border), $value is also a dict but
    represents the composite structure — NOT modes — so we exclude them.
    """
    v = leaf.get("$value")
    t = leaf.get("$type")
    if not isinstance(v, dict):
        return False
    # Composites use dict $value for structure, not modes
    if t in ("typography", "shadow", "gradient", "border", "transition"):
        return False
    # Otherwise — color, dimension, etc. — dict $value means modes
    return True


# ----------------------------------------------------------------------------
# Payload builder
# ----------------------------------------------------------------------------

def build_payload(dtcg: dict) -> dict:
    """Build Figma Variables API batch payload from a DTCG document.

    Four-pass pipeline (each pass is a small helper):
        1. ``_discover_collections``  — walk leaves, group by collection, register modes
        2. ``_emit_collections``      — produce ``variableCollections`` + ``variableModes`` ops
        3. ``_emit_variables``        — produce ``variables`` ops, populate ``name_to_temp_id``
        4. ``_emit_mode_values``      — produce ``variableModeValues`` ops with alias resolution

    Returns ``{payload, warnings, collections_created}``. The payload is ready
    to POST to Figma's Variables API; the warnings list captures unresolved
    aliases and unsupported $types.
    """
    leaves = walk_tokens(dtcg)
    payload = {
        "variableCollections": [],
        "variableModes": [],
        "variables": [],
        "variableModeValues": []
    }
    name_to_temp_id: dict[str, str] = {}
    warnings: list[str] = []

    collections = _discover_collections(leaves, warnings)
    _emit_collections(collections, payload)
    _emit_variables(leaves, collections, name_to_temp_id, payload)
    _emit_mode_values(leaves, collections, name_to_temp_id, payload, warnings)

    return {"payload": payload, "warnings": warnings, "collections_created": list(collections.keys())}


def _discover_collections(leaves: list[tuple[str, dict]], warnings: list[str]) -> dict[str, dict]:
    """Pass 1: scan all leaves, return ``{collection_name → {temp_id, modes, needs_modes}}``.

    Side effect: appends a warning to ``warnings`` for any leaf with an
    unsupported ``$type``.
    """
    collections: dict[str, dict] = {}
    for path, leaf in leaves:
        dtcg_type = leaf.get("$type")
        if dtcg_type in UNSUPPORTED_TYPES:
            continue
        if dtcg_type not in DTCG_TO_FIGMA_TYPE:
            warnings.append(f"Unknown type {dtcg_type!r} for token {path}; skipped.")
            continue
        coll_name = infer_collection(path)
        if coll_name not in collections:
            collections[coll_name] = {
                "temp_id": f"tmpcoll_{uuid.uuid4().hex[:8]}",
                "modes": {},
                "needs_modes": False
            }
        if has_mode_object(leaf):
            collections[coll_name]["needs_modes"] = True
            for mode_key in leaf["$value"].keys():
                mode_norm = mode_key.capitalize()
                if mode_norm not in collections[coll_name]["modes"]:
                    collections[coll_name]["modes"][mode_norm] = f"tmpmode_{uuid.uuid4().hex[:8]}"
    return collections


def _emit_collections(collections: dict[str, dict], payload: dict) -> None:
    """Pass 2: append ``variableCollections`` + ``variableModes`` ops to payload.

    Mutates ``collections`` by stamping ``initial_mode_id`` and
    ``initial_mode_name`` on each collection info dict (needed by passes 3-4).
    """
    for coll_name, info in collections.items():
        coll_op = {
            "action": "CREATE",
            "id": info["temp_id"],
            "name": coll_name,
            "initialModeId": "tmpmode_" + uuid.uuid4().hex[:8]
        }
        if info["needs_modes"]:
            first_mode = next(iter(info["modes"].keys())) if info["modes"] else "Light"
            first_mode_id = info["modes"][first_mode] if first_mode in info["modes"] else coll_op["initialModeId"]
            coll_op["initialModeId"] = first_mode_id
            info["initial_mode_id"] = first_mode_id
            info["initial_mode_name"] = first_mode
            for mode_name, mode_id in info["modes"].items():
                action = "UPDATE" if mode_id == first_mode_id else "CREATE"
                payload["variableModes"].append({
                    "action": action,
                    "id": mode_id,
                    "name": mode_name,
                    "variableCollectionId": info["temp_id"]
                })
        else:
            info["initial_mode_id"] = coll_op["initialModeId"]
            info["initial_mode_name"] = "Default"
            payload["variableModes"].append({
                "action": "UPDATE",
                "id": coll_op["initialModeId"],
                "name": "Default",
                "variableCollectionId": info["temp_id"]
            })
        payload["variableCollections"].append(coll_op)


def _emit_variables(leaves: list[tuple[str, dict]], collections: dict[str, dict],
                    name_to_temp_id: dict[str, str], payload: dict) -> None:
    """Pass 3: append ``variables`` create ops; populate ``name_to_temp_id`` for alias resolution."""
    for path, leaf in leaves:
        dtcg_type = leaf.get("$type")
        if dtcg_type in UNSUPPORTED_TYPES or dtcg_type not in DTCG_TO_FIGMA_TYPE:
            continue
        coll_info = collections[infer_collection(path)]
        var_temp_id = f"tmpvar_{uuid.uuid4().hex[:8]}"
        name_to_temp_id[path] = var_temp_id
        var_op = {
            "action": "CREATE",
            "id": var_temp_id,
            "name": path.replace(".", "/"),
            "variableCollectionId": coll_info["temp_id"],
            "resolvedType": DTCG_TO_FIGMA_TYPE[dtcg_type]
        }
        if leaf.get("$description"):
            var_op["description"] = leaf["$description"]
        payload["variables"].append(var_op)


def _emit_mode_values(leaves: list[tuple[str, dict]], collections: dict[str, dict],
                      name_to_temp_id: dict[str, str], payload: dict,
                      warnings: list[str]) -> None:
    """Pass 4: append ``variableModeValues`` ops, resolving aliases against ``name_to_temp_id``."""
    for path, leaf in leaves:
        dtcg_type = leaf.get("$type")
        if dtcg_type in UNSUPPORTED_TYPES or dtcg_type not in DTCG_TO_FIGMA_TYPE:
            continue
        if path not in name_to_temp_id:
            continue
        var_id = name_to_temp_id[path]
        coll_info = collections[infer_collection(path)]
        raw = leaf["$value"]
        if has_mode_object(leaf):
            for mode_key, mode_val in raw.items():
                mode_id = coll_info["modes"][mode_key.capitalize()]
                resolved = resolve_token_value(mode_val, dtcg_type, name_to_temp_id, warnings)
                payload["variableModeValues"].append({
                    "variableId": var_id, "modeId": mode_id, "value": resolved
                })
        else:
            resolved = resolve_token_value(raw, dtcg_type, name_to_temp_id, warnings)
            payload["variableModeValues"].append({
                "variableId": var_id, "modeId": coll_info["initial_mode_id"], "value": resolved
            })


_ALIAS_RE = re.compile(r"^\{([\w.\-]+)\}$")


def _try_alias(raw: Any, name_to_id: dict[str, str], warnings: list[str]) -> Any | None:
    """If ``raw`` is a DTCG alias literal ``{path.to.token}``, resolve it.

    Returns the Figma ``VARIABLE_ALIAS`` value object on hit, ``None`` if
    ``raw`` is not an alias string at all. Records a warning for aliases
    that don't resolve to a known target (and returns the literal as a
    fallback signal).
    """
    if not isinstance(raw, str):
        return None
    m = _ALIAS_RE.match(raw)
    if not m:
        return None
    target = m.group(1)
    if target in name_to_id:
        return {"type": "VARIABLE_ALIAS", "id": name_to_id[target]}
    warnings.append(f"Unresolved alias target {target!r}; falling back to literal.")
    return raw


def _resolve_color(raw: Any) -> Any:
    """Convert hex strings to RGBA dicts; pass through other shapes."""
    if isinstance(raw, str) and raw.startswith("#"):
        return hex_to_rgba(raw)
    return raw


def _resolve_numeric(raw: Any, dtcg_type: str, warnings: list[str]) -> Any:
    """Parse dimension/number/fontWeight via ``parse_dimension``, warning on failure."""
    try:
        return parse_dimension(raw)
    except (TypeError, ValueError):
        warnings.append(f"Could not parse {dtcg_type} value: {raw!r}; treated as literal.")
        return raw


def _resolve_font_family(raw: Any) -> str:
    """Pick the first family from a fallback list; stringify scalars."""
    if isinstance(raw, list):
        return raw[0] if raw else ""
    return str(raw)


# Dispatch: dtcg_type → resolver
_NUMERIC_TYPES = {"dimension", "number", "fontWeight"}


def resolve_token_value(raw: Any, dtcg_type: str, name_to_id: dict[str, str], warnings: list[str]) -> Any:
    """Resolve a DTCG token value into a Figma API-ready value.

    First attempts alias resolution (any ``$type`` may carry an alias
    literal). If not an alias, dispatches on ``dtcg_type`` to the
    appropriate type-specific resolver. Unknown types pass through
    unchanged so the caller can still emit them as literals.
    """
    aliased = _try_alias(raw, name_to_id, warnings)
    if aliased is not None:
        return aliased
    if dtcg_type == "color":
        return _resolve_color(raw)
    if dtcg_type in _NUMERIC_TYPES:
        return _resolve_numeric(raw, dtcg_type, warnings)
    if dtcg_type == "fontFamily":
        return _resolve_font_family(raw)
    if dtcg_type == "boolean":
        return bool(raw)
    return raw


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="DTCG JSON input file")
    p.add_argument("--output", default="variables-payload.json", help="Output payload file")
    p.add_argument("--pretty", action="store_true", help="Pretty-print output")
    args = p.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        dtcg = json.load(f)

    result = build_payload(dtcg)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result["payload"], f, indent=2 if args.pretty else None, ensure_ascii=False)

    print(f"✓ Wrote {args.output}", file=sys.stderr)
    print(f"  Collections: {len(result['collections_created'])}", file=sys.stderr)
    print(f"  Variables: {len(result['payload']['variables'])}", file=sys.stderr)
    print(f"  Mode values: {len(result['payload']['variableModeValues'])}", file=sys.stderr)
    if result["warnings"]:
        print(f"  Warnings: {len(result['warnings'])}", file=sys.stderr)
        for w in result["warnings"][:5]:
            print(f"    · {w}", file=sys.stderr)
        if len(result["warnings"]) > 5:
            print(f"    · ... and {len(result['warnings']) - 5} more", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
