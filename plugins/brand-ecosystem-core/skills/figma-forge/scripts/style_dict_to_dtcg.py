#!/usr/bin/env python3
"""
style_dict_to_dtcg.py — Convert Amazon Style Dictionary token JSON to W3C DTCG-shaped JSON.

Style Dictionary uses:  { "value": "...", "comment": "...", "attributes": {...} }
DTCG uses:              { "$value": "...", "$type": "...", "$description": "..." }

This script does the structural conversion + type inference.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


# Type inference heuristics
TYPE_BY_PATH_PREFIX = [
    ("color", "color"),
    ("colour", "color"),
    ("size", "dimension"),
    ("spacing", "dimension"),
    ("space", "dimension"),
    ("dimension", "dimension"),
    ("padding", "dimension"),
    ("margin", "dimension"),
    ("radius", "dimension"),
    ("border-radius", "dimension"),
    ("font.family", "fontFamily"),
    ("fontFamily", "fontFamily"),
    ("font.weight", "fontWeight"),
    ("fontWeight", "fontWeight"),
    ("font.size", "dimension"),
    ("fontSize", "dimension"),
    ("font.lineHeight", "dimension"),
    ("lineHeight", "dimension"),
    ("font.letterSpacing", "dimension"),
    ("letterSpacing", "dimension"),
    ("opacity", "number"),
    ("shadow", "shadow"),
    ("boxShadow", "shadow"),
    ("motion.duration", "duration"),
    ("duration", "duration"),
    ("motion.curve", "cubicBezier"),
    ("cubicBezier", "cubicBezier"),
    ("z-index", "number"),
    ("zIndex", "number"),
    ("border", "border"),
    ("typography", "typography"),
    ("gradient", "gradient"),
]


HEX_RE = re.compile(r"^#[0-9A-Fa-f]{3,8}$")
RGB_RE = re.compile(r"^rgb\(", re.IGNORECASE)
DIM_RE = re.compile(r"^(-?[\d.]+)(px|rem|em|%)?$")


CATEGORY_TO_DTCG = {"color": "color", "size": "dimension", "time": "duration", "asset": "asset"}


def _from_explicit(node: dict) -> str | None:
    """Return the $type if the source already declares one explicitly (DTCG or SD form)."""
    if "$type" in node:
        return node["$type"]
    if "type" in node and isinstance(node["type"], str):
        return node["type"]
    return None


def _from_attributes(node: dict) -> str | None:
    """Return the $type implied by Style Dictionary ``attributes.category`` (color/size/time/asset)."""
    attrs = node.get("attributes", {})
    if not isinstance(attrs, dict):
        return None
    cat = attrs.get("category", "").lower()
    return CATEGORY_TO_DTCG.get(cat) if cat else None


def _from_path(path: str) -> str | None:
    """Return the $type implied by the token path (e.g. ``font.weight`` → ``fontWeight``)."""
    path_lower = path.lower()
    for prefix, t in TYPE_BY_PATH_PREFIX:
        if prefix in path_lower:
            return t
    return None


def _from_value_shape(val: Any) -> str:
    """Return the $type implied by the leaf value's runtime shape. Default: ``string``."""
    if isinstance(val, bool):
        return "boolean"
    if isinstance(val, (int, float)):
        return "number"
    if isinstance(val, str):
        if HEX_RE.match(val) or RGB_RE.match(val):
            return "color"
        if DIM_RE.match(val):
            return "dimension"
    return "string"


def infer_type(node: dict, path: str) -> str:
    """Infer DTCG ``$type`` from explicit declaration → attributes → path → value shape.

    Decision chain (first non-None wins):
        1. Explicit ``$type`` or Style Dictionary ``type`` field on the node
        2. Style Dictionary ``attributes.category`` (mapped via ``CATEGORY_TO_DTCG``)
        3. Path-prefix scan against ``TYPE_BY_PATH_PREFIX``
        4. Runtime value shape (hex/dim regex + isinstance check)
    """
    for inferrer in (_from_explicit, _from_attributes):
        result = inferrer(node)
        if result is not None:
            return result
    path_result = _from_path(path)
    if path_result is not None:
        return path_result
    return _from_value_shape(node.get("value"))


def rewrite_aliases(value: Any) -> Any:
    """
    Style Dictionary aliases:  {token.path.value}  or  {token.path}
    DTCG aliases:              {token.path}
    Strip the trailing .value if present.
    """
    if isinstance(value, str):
        return re.sub(r"\{([\w.\-]+)\.value\}", r"{\1}", value)
    if isinstance(value, dict):
        return {k: rewrite_aliases(v) for k, v in value.items()}
    if isinstance(value, list):
        return [rewrite_aliases(v) for v in value]
    return value


def is_sd_leaf(node: Any) -> bool:
    """A leaf has a 'value' key directly (Style Dictionary)."""
    return isinstance(node, dict) and "value" in node


def convert_node(node: Any, path: str = "") -> Any:
    """Recursively convert a Style Dictionary token tree to DTCG."""
    if is_sd_leaf(node):
        dtcg_node: dict[str, Any] = {
            "$value": rewrite_aliases(node["value"]),
            "$type": infer_type(node, path),
        }
        if "comment" in node and node["comment"]:
            dtcg_node["$description"] = node["comment"]
        # Preserve any Style Dictionary attributes as extension metadata
        if "attributes" in node:
            dtcg_node["$extensions"] = {
                "com.amazon.style-dictionary": {"attributes": node["attributes"]}
            }
        return dtcg_node
    if isinstance(node, dict):
        result = {}
        for key, child in node.items():
            if key in ("type", "category"):
                continue  # Style Dict metadata; absorbed into $type
            child_path = f"{path}.{key}" if path else key
            result[key] = convert_node(child, child_path)
        return result
    return node


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="Style Dictionary JSON input file")
    p.add_argument("--output", default="tokens.dtcg.json", help="Output DTCG JSON file")
    p.add_argument("--pretty", action="store_true", help="Pretty-print")
    args = p.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        sd = json.load(f)

    dtcg = convert_node(sd)

    # Add extension stamp
    dtcg.setdefault("$extensions", {})
    dtcg["$extensions"]["com.figma-forge"] = {
        "version": "0.1.0",
        "convertedFrom": "style-dictionary",
        "convertedAt": "<runtime ISO timestamp>"
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dtcg, f, indent=2 if args.pretty else None, ensure_ascii=False)

    print(f"✓ Converted Style Dictionary → DTCG: {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
