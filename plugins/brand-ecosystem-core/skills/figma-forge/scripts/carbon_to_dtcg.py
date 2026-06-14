#!/usr/bin/env python3
"""
carbon_to_dtcg.py — Generate W3C DTCG-shaped JSON from the IBM Carbon Design System v11 canonical
token tables.

Usage:
    python3 carbon_to_dtcg.py --theme white --output carbon-white.dtcg.json
    python3 carbon_to_dtcg.py --theme g100 --output carbon-g100.dtcg.json
    python3 carbon_to_dtcg.py --all-themes --output carbon.dtcg.json   # Multi-mode

The "themes" become Figma modes in the Semantic color collection.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


# ----------------------------------------------------------------------------
# Carbon v11 primitive palette (canonical hex values)
# ----------------------------------------------------------------------------

CARBON_PRIMITIVES: dict[str, dict[str, str]] = {
    "gray": {
        "10":  "#F4F4F4", "20":  "#E0E0E0", "30":  "#C6C6C6", "40":  "#A8A8A8",
        "50":  "#8D8D8D", "60":  "#525252", "70":  "#393939", "80":  "#262626",
        "90":  "#161616", "100": "#0B0B0B"
    },
    "blue": {
        "10":  "#EDF5FF", "20":  "#D0E2FF", "30":  "#A6C8FF", "40":  "#78A9FF",
        "50":  "#4589FF", "60":  "#0F62FE", "70":  "#0043CE", "80":  "#002D9C",
        "90":  "#001D6C", "100": "#001141"
    },
    "red": {
        "10":  "#FFF1F1", "20":  "#FFD7D9", "30":  "#FFB3B8", "40":  "#FF8389",
        "50":  "#FA4D56", "60":  "#DA1E28", "70":  "#A2191F", "80":  "#750E13",
        "90":  "#520408", "100": "#2D0709"
    },
    "green": {
        "10":  "#DEFBE6", "20":  "#A7F0BA", "30":  "#6FDC8C", "40":  "#42BE65",
        "50":  "#24A148", "60":  "#198038", "70":  "#0E6027", "80":  "#044317",
        "90":  "#022D0D", "100": "#071908"
    },
    "yellow": {
        "10":  "#FCF4D6", "20":  "#FDDC69", "30":  "#F1C21B", "40":  "#D2A106",
        "50":  "#B28600", "60":  "#8E6A00", "70":  "#684E00", "80":  "#483700",
        "90":  "#302400", "100": "#1C1500"
    },
    "magenta": {
        "10":  "#FFF0F7", "20":  "#FFD6E8", "30":  "#FFAFD2", "40":  "#FF7EB6",
        "50":  "#EE5396", "60":  "#D02670", "70":  "#9F1853", "80":  "#740937",
        "90":  "#510224", "100": "#2A0A18"
    },
    "purple": {
        "10":  "#F6F2FF", "20":  "#E8DAFF", "30":  "#D4BBFF", "40":  "#BE95FF",
        "50":  "#A56EFF", "60":  "#8A3FFC", "70":  "#6929C4", "80":  "#491D8B",
        "90":  "#31135E", "100": "#1C0F30"
    },
    "teal": {
        "10":  "#D9FBFB", "20":  "#9EF0F0", "30":  "#3DDBD9", "40":  "#08BDBA",
        "50":  "#009D9A", "60":  "#007D79", "70":  "#005D5D", "80":  "#004144",
        "90":  "#022B30", "100": "#081A1C"
    },
    "cyan": {
        "10":  "#E5F6FF", "20":  "#BAE6FF", "30":  "#82CFFF", "40":  "#33B1FF",
        "50":  "#1192E8", "60":  "#0072C3", "70":  "#00539A", "80":  "#003A6D",
        "90":  "#012749", "100": "#061727"
    },
}

CONSTANTS = {"white": "#FFFFFF", "black": "#000000"}


# ----------------------------------------------------------------------------
# Carbon semantic role mapping per theme
# Each value is a primitive reference like ("gray", "10")
# ----------------------------------------------------------------------------

SEMANTIC_ROLES: dict[str, dict[str, tuple[str, str] | str]] = {
    "background":            {"white": "white",            "g10": ("gray", "10"), "g90": ("gray", "90"),  "g100": ("gray", "100")},
    "background-hover":      {"white": ("gray", "20"),     "g10": ("gray", "20"), "g90": ("gray", "70"),  "g100": ("gray", "80")},
    "background-active":     {"white": ("gray", "30"),     "g10": ("gray", "30"), "g90": ("gray", "60"),  "g100": ("gray", "70")},
    "layer-01":              {"white": ("gray", "10"),     "g10": "white",        "g90": ("gray", "80"),  "g100": ("gray", "90")},
    "layer-02":              {"white": "white",            "g10": ("gray", "10"), "g90": ("gray", "70"),  "g100": ("gray", "80")},
    "layer-03":              {"white": ("gray", "10"),     "g10": "white",        "g90": ("gray", "60"),  "g100": ("gray", "70")},
    "layer-hover-01":        {"white": ("gray", "20"),     "g10": ("gray", "20"), "g90": ("gray", "70"),  "g100": ("gray", "80")},
    "text-primary":          {"white": ("gray", "100"),    "g10": ("gray", "100"),"g90": ("gray", "10"),  "g100": ("gray", "10")},
    "text-secondary":        {"white": ("gray", "70"),     "g10": ("gray", "70"), "g90": ("gray", "30"),  "g100": ("gray", "30")},
    "text-placeholder":      {"white": ("gray", "40"),     "g10": ("gray", "40"), "g90": ("gray", "60"),  "g100": ("gray", "60")},
    "text-on-color":         {"white": "white",            "g10": "white",        "g90": "white",         "g100": "white"},
    "text-disabled":         {"white": ("gray", "40"),     "g10": ("gray", "40"), "g90": ("gray", "60"),  "g100": ("gray", "60")},
    "icon-primary":          {"white": ("gray", "100"),    "g10": ("gray", "100"),"g90": ("gray", "10"),  "g100": ("gray", "10")},
    "icon-secondary":        {"white": ("gray", "70"),     "g10": ("gray", "70"), "g90": ("gray", "30"),  "g100": ("gray", "30")},
    "interactive":           {"white": ("blue", "60"),     "g10": ("blue", "60"), "g90": ("blue", "50"),  "g100": ("blue", "50")},
    "link-primary":          {"white": ("blue", "60"),     "g10": ("blue", "60"), "g90": ("blue", "40"),  "g100": ("blue", "40")},
    "link-primary-hover":    {"white": ("blue", "70"),     "g10": ("blue", "70"), "g90": ("blue", "30"),  "g100": ("blue", "30")},
    "border-subtle-00":      {"white": ("gray", "20"),     "g10": ("gray", "30"), "g90": ("gray", "80"),  "g100": ("gray", "90")},
    "border-subtle-01":      {"white": ("gray", "20"),     "g10": ("gray", "20"), "g90": ("gray", "70"),  "g100": ("gray", "80")},
    "border-strong-01":      {"white": ("gray", "50"),     "g10": ("gray", "50"), "g90": ("gray", "50"),  "g100": ("gray", "50")},
    "border-interactive":    {"white": ("blue", "60"),     "g10": ("blue", "60"), "g90": ("blue", "50"),  "g100": ("blue", "50")},
    "focus":                 {"white": ("blue", "60"),     "g10": ("blue", "60"), "g90": "white",         "g100": "white"},
    "support-error":         {"white": ("red", "60"),      "g10": ("red", "60"),  "g90": ("red", "50"),   "g100": ("red", "50")},
    "support-warning":       {"white": ("yellow", "30"),   "g10": ("yellow", "30"),"g90": ("yellow", "30")," g100": ("yellow", "30")},
    "support-success":       {"white": ("green", "50"),    "g10": ("green", "50"),"g90": ("green", "40"), "g100": ("green", "40")},
    "support-info":          {"white": ("blue", "70"),     "g10": ("blue", "70"), "g90": ("blue", "50"),  "g100": ("blue", "50")},
    "button-primary":        {"white": ("blue", "60"),     "g10": ("blue", "60"), "g90": ("blue", "60"),  "g100": ("blue", "60")},
    "button-primary-hover":  {"white": ("blue", "70"),     "g10": ("blue", "70"), "g90": ("blue", "70"),  "g100": ("blue", "70")},
    "button-primary-active": {"white": ("blue", "80"),     "g10": ("blue", "80"), "g90": ("blue", "80"),  "g100": ("blue", "80")},
    "button-secondary":      {"white": ("gray", "80"),     "g10": ("gray", "80"), "g90": ("gray", "60"),  "g100": ("gray", "60")},
    "button-danger-primary": {"white": ("red", "60"),      "g10": ("red", "60"),  "g90": ("red", "60"),   "g100": ("red", "60")},
    "button-disabled":       {"white": ("gray", "20"),     "g10": ("gray", "20"), "g90": ("gray", "70"),  "g100": ("gray", "70")},
}


# ----------------------------------------------------------------------------
# Type ramp (canonical Carbon v11)
# ----------------------------------------------------------------------------

TYPE_RAMP: dict[str, dict[str, Any]] = {
    "body-compact-01":   {"size": 14, "lineHeight": 18, "weight": 400, "letterSpacing": 0.16},
    "body-compact-02":   {"size": 16, "lineHeight": 22, "weight": 400, "letterSpacing": 0},
    "body-01":           {"size": 14, "lineHeight": 20, "weight": 400, "letterSpacing": 0.16},
    "body-02":           {"size": 16, "lineHeight": 24, "weight": 400, "letterSpacing": 0},
    "heading-compact-01":{"size": 14, "lineHeight": 18, "weight": 600, "letterSpacing": 0.16},
    "heading-01":        {"size": 14, "lineHeight": 20, "weight": 600, "letterSpacing": 0.16},
    "heading-02":        {"size": 16, "lineHeight": 24, "weight": 600, "letterSpacing": 0},
    "heading-03":        {"size": 20, "lineHeight": 28, "weight": 400, "letterSpacing": 0},
    "heading-04":        {"size": 28, "lineHeight": 36, "weight": 400, "letterSpacing": 0},
    "heading-05":        {"size": 32, "lineHeight": 40, "weight": 400, "letterSpacing": 0},
    "heading-06":        {"size": 42, "lineHeight": 50, "weight": 300, "letterSpacing": 0},
    "heading-07":        {"size": 54, "lineHeight": 64, "weight": 300, "letterSpacing": 0},
    "code-01":           {"size": 12, "lineHeight": 16, "weight": 400, "letterSpacing": 0.32},
    "code-02":           {"size": 14, "lineHeight": 20, "weight": 400, "letterSpacing": 0.32},
    "label-01":          {"size": 12, "lineHeight": 16, "weight": 400, "letterSpacing": 0.32},
    "label-02":          {"size": 14, "lineHeight": 18, "weight": 400, "letterSpacing": 0.16},
}


SPACING_SCALE = {
    "01": "2px",  "02": "4px",  "03": "8px",  "04": "12px",
    "05": "16px", "06": "24px", "07": "32px", "08": "40px",
    "09": "48px", "10": "64px", "11": "80px", "12": "96px", "13": "160px"
}


# ----------------------------------------------------------------------------
# Builders
# ----------------------------------------------------------------------------

def primitive_to_dtcg() -> dict:
    """Emit Carbon's primitive color palette as a DTCG color-token tree.

    Iterates the canonical 10-hue × 10-step swatch grid (CARBON_PRIMITIVES) and
    the constants (white/black), producing one leaf per hex value with
    `$type: color`. Used as the raw layer to which semantic role tokens alias.
    """
    color = {}
    for hue, swatches in CARBON_PRIMITIVES.items():
        color[hue] = {step: {"$value": hex_val, "$type": "color"} for step, hex_val in swatches.items()}
    for name, hex_val in CONSTANTS.items():
        color[name] = {"$value": hex_val, "$type": "color"}
    return color


def semantic_to_dtcg(themes: list[str]) -> dict:
    """Emit Carbon semantic role tokens as DTCG aliases to the primitive layer.

    For each role in SEMANTIC_ROLES (e.g. ``text-primary``, ``layer-01``,
    ``button-primary-hover``), resolves the per-theme primitive target and
    emits either (a) a single-mode alias when ``len(themes) == 1`` or (b) a
    multi-mode dict value keyed by theme name when multiple themes are
    requested. Hyphenated role names are split into nested DTCG paths
    (e.g. ``button-primary-hover`` → ``button/primary/hover``).
    """
    semantic = {}
    for role, theme_map in SEMANTIC_ROLES.items():
        leaf: dict[str, Any] = {"$type": "color"}
        if len(themes) == 1:
            theme = themes[0]
            target = theme_map.get(theme)
            leaf["$value"] = primitive_alias(target) if target else "#000000"
        else:
            leaf["$value"] = {theme: primitive_alias(theme_map.get(theme)) for theme in themes}
        # set into nested dict
        parts = role.split("-")
        node = semantic
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = leaf
    return semantic


def primitive_alias(target: Any) -> str:
    """Build a DTCG curly-brace alias path for a primitive token target.

    Accepts either a string constant key (e.g. ``"white"``) or a (hue, step)
    tuple (e.g. ``("blue", "60")``). Returns the DTCG alias literal that
    references the corresponding primitive token. Falls back to opaque black
    on missing/None target — caller is responsible for surfacing this.
    """
    if target is None:
        return "#000000"
    if isinstance(target, str):
        return "{color.primitive." + target + "}"
    if isinstance(target, tuple):
        hue, step = target
        return "{color.primitive." + hue + "." + step + "}"
    return "#000000"


def typography_to_dtcg() -> dict:
    """Emit Carbon's type ramp as composite DTCG typography tokens.

    Each TYPE_RAMP entry becomes one composite ``$type: typography`` token
    whose ``$value`` is the structural dict (fontFamily/Size/Weight/LineHeight/
    LetterSpacing). Font family is aliased to ``{font.family.sans}`` so the
    same ramp can be re-themed via font-family override (e.g. Roche Sans).
    """
    typo = {}
    for name, params in TYPE_RAMP.items():
        typo[name] = {
            "$type": "typography",
            "$value": {
                "fontFamily":    "{font.family.sans}",
                "fontSize":      f"{params['size']}px",
                "fontWeight":    params["weight"],
                "lineHeight":    f"{params['lineHeight']}px",
                "letterSpacing": f"{params['letterSpacing']}px"
            }
        }
    return typo


def spacing_to_dtcg() -> dict:
    """Emit Carbon's spacing scale (steps 01-13, 2px-160px) as DTCG dimensions."""
    return {step: {"$value": val, "$type": "dimension"} for step, val in SPACING_SCALE.items()}


def build(themes: list[str]) -> dict:
    """Compose the full Carbon DTCG document for the requested theme set.

    Top-level shape: ``color/primitive``, ``color/semantic`` (multi-mode if
    more than one theme), ``dimension/spacing``, ``dimension/radius``,
    ``font/family``, ``font/weight``, ``typography``. A ``$extensions`` block
    records the source DS, version, and active theme list for downstream
    skill consumers.
    """
    return {
        "color": {
            "primitive": primitive_to_dtcg(),
            "semantic": semantic_to_dtcg(themes)
        },
        "dimension": {
            "spacing": spacing_to_dtcg(),
            "radius": {
                "none": {"$value": "0px", "$type": "dimension"},
                "default": {"$value": "0px", "$type": "dimension"},  # Carbon defaults to 0 radius
                "interactive": {"$value": "4px", "$type": "dimension"},
                "round": {"$value": "9999px", "$type": "dimension"}
            }
        },
        "font": {
            "family": {
                "sans":  {"$value": "IBM Plex Sans",  "$type": "fontFamily"},
                "serif": {"$value": "IBM Plex Serif", "$type": "fontFamily"},
                "mono":  {"$value": "IBM Plex Mono",  "$type": "fontFamily"}
            },
            "weight": {
                "light":    {"$value": 300, "$type": "fontWeight"},
                "regular":  {"$value": 400, "$type": "fontWeight"},
                "semibold": {"$value": 600, "$type": "fontWeight"}
            }
        },
        "typography": typography_to_dtcg(),
        "$extensions": {
            "com.figma-forge": {
                "source": "carbon",
                "version": "v11",
                "themes": themes
            }
        }
    }


def main() -> int:
    """CLI entry point — parse arguments, run build(), write output JSON."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--theme", choices=["white", "g10", "g90", "g100"], help="Single theme")
    p.add_argument("--all-themes", action="store_true", help="Include all four themes as modes")
    p.add_argument("--output", default="carbon.dtcg.json")
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args()

    if args.all_themes:
        themes = ["white", "g10", "g90", "g100"]
    elif args.theme:
        themes = [args.theme]
    else:
        themes = ["white"]

    dtcg = build(themes)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dtcg, f, indent=2 if args.pretty else None, ensure_ascii=False)

    print(f"✓ Wrote Carbon v11 DTCG to {args.output} (themes: {', '.join(themes)})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
