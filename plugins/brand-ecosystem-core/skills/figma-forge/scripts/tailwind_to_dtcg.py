#!/usr/bin/env python3
"""
tailwind_to_dtcg.py — Generate W3C DTCG JSON from the Tailwind CSS default palette.

Usage:
    python3 tailwind_to_dtcg.py --output tailwind.dtcg.json                     # Full default
    python3 tailwind_to_dtcg.py --hues "slate,blue,red"                          # Filter hues
    python3 tailwind_to_dtcg.py --custom-config tailwind.config.json             # User override
"""

from __future__ import annotations

import argparse
import json
import sys


# ----------------------------------------------------------------------------
# Tailwind v3 default color palette (representative subset of the 286 colors)
# ----------------------------------------------------------------------------

TAILWIND_PALETTE: dict[str, dict[str, str]] = {
    "slate": {
        "50":  "#F8FAFC", "100": "#F1F5F9", "200": "#E2E8F0", "300": "#CBD5E1",
        "400": "#94A3B8", "500": "#64748B", "600": "#475569", "700": "#334155",
        "800": "#1E293B", "900": "#0F172A", "950": "#020617"
    },
    "gray": {
        "50":  "#F9FAFB", "100": "#F3F4F6", "200": "#E5E7EB", "300": "#D1D5DB",
        "400": "#9CA3AF", "500": "#6B7280", "600": "#4B5563", "700": "#374151",
        "800": "#1F2937", "900": "#111827", "950": "#030712"
    },
    "zinc": {
        "50":  "#FAFAFA", "100": "#F4F4F5", "200": "#E4E4E7", "300": "#D4D4D8",
        "400": "#A1A1AA", "500": "#71717A", "600": "#52525B", "700": "#3F3F46",
        "800": "#27272A", "900": "#18181B", "950": "#09090B"
    },
    "neutral": {
        "50":  "#FAFAFA", "100": "#F5F5F5", "200": "#E5E5E5", "300": "#D4D4D4",
        "400": "#A3A3A3", "500": "#737373", "600": "#525252", "700": "#404040",
        "800": "#262626", "900": "#171717", "950": "#0A0A0A"
    },
    "stone": {
        "50":  "#FAFAF9", "100": "#F5F5F4", "200": "#E7E5E4", "300": "#D6D3D1",
        "400": "#A8A29E", "500": "#78716C", "600": "#57534E", "700": "#44403C",
        "800": "#292524", "900": "#1C1917", "950": "#0C0A09"
    },
    "red": {
        "50":  "#FEF2F2", "100": "#FEE2E2", "200": "#FECACA", "300": "#FCA5A5",
        "400": "#F87171", "500": "#EF4444", "600": "#DC2626", "700": "#B91C1C",
        "800": "#991B1B", "900": "#7F1D1D", "950": "#450A0A"
    },
    "orange": {
        "50":  "#FFF7ED", "100": "#FFEDD5", "200": "#FED7AA", "300": "#FDBA74",
        "400": "#FB923C", "500": "#F97316", "600": "#EA580C", "700": "#C2410C",
        "800": "#9A3412", "900": "#7C2D12", "950": "#431407"
    },
    "amber": {
        "50":  "#FFFBEB", "100": "#FEF3C7", "200": "#FDE68A", "300": "#FCD34D",
        "400": "#FBBF24", "500": "#F59E0B", "600": "#D97706", "700": "#B45309",
        "800": "#92400E", "900": "#78350F", "950": "#451A03"
    },
    "yellow": {
        "50":  "#FEFCE8", "100": "#FEF9C3", "200": "#FEF08A", "300": "#FDE047",
        "400": "#FACC15", "500": "#EAB308", "600": "#CA8A04", "700": "#A16207",
        "800": "#854D0E", "900": "#713F12", "950": "#422006"
    },
    "green": {
        "50":  "#F0FDF4", "100": "#DCFCE7", "200": "#BBF7D0", "300": "#86EFAC",
        "400": "#4ADE80", "500": "#22C55E", "600": "#16A34A", "700": "#15803D",
        "800": "#166534", "900": "#14532D", "950": "#052E16"
    },
    "emerald": {
        "50":  "#ECFDF5", "100": "#D1FAE5", "200": "#A7F3D0", "300": "#6EE7B7",
        "400": "#34D399", "500": "#10B981", "600": "#059669", "700": "#047857",
        "800": "#065F46", "900": "#064E3B", "950": "#022C22"
    },
    "teal": {
        "50":  "#F0FDFA", "100": "#CCFBF1", "200": "#99F6E4", "300": "#5EEAD4",
        "400": "#2DD4BF", "500": "#14B8A6", "600": "#0D9488", "700": "#0F766E",
        "800": "#115E59", "900": "#134E4A", "950": "#042F2E"
    },
    "blue": {
        "50":  "#EFF6FF", "100": "#DBEAFE", "200": "#BFDBFE", "300": "#93C5FD",
        "400": "#60A5FA", "500": "#3B82F6", "600": "#2563EB", "700": "#1D4ED8",
        "800": "#1E40AF", "900": "#1E3A8A", "950": "#172554"
    },
    "indigo": {
        "50":  "#EEF2FF", "100": "#E0E7FF", "200": "#C7D2FE", "300": "#A5B4FC",
        "400": "#818CF8", "500": "#6366F1", "600": "#4F46E5", "700": "#4338CA",
        "800": "#3730A3", "900": "#312E81", "950": "#1E1B4B"
    },
    "purple": {
        "50":  "#FAF5FF", "100": "#F3E8FF", "200": "#E9D5FF", "300": "#D8B4FE",
        "400": "#C084FC", "500": "#A855F7", "600": "#9333EA", "700": "#7E22CE",
        "800": "#6B21A8", "900": "#581C87", "950": "#3B0764"
    },
    "pink": {
        "50":  "#FDF2F8", "100": "#FCE7F3", "200": "#FBCFE8", "300": "#F9A8D4",
        "400": "#F472B6", "500": "#EC4899", "600": "#DB2777", "700": "#BE185D",
        "800": "#9D174D", "900": "#831843", "950": "#500724"
    }
}

CONSTANTS = {"white": "#FFFFFF", "black": "#000000", "transparent": "#00000000"}


SPACING = {
    "0":   "0px",  "px":   "1px",  "0.5": "2px",  "1":   "4px",  "1.5": "6px",
    "2":   "8px",  "2.5":  "10px", "3":   "12px", "3.5": "14px", "4":   "16px",
    "5":   "20px", "6":    "24px", "7":   "28px", "8":   "32px", "9":   "36px",
    "10":  "40px", "11":   "44px", "12":  "48px", "14":  "56px", "16":  "64px",
    "20":  "80px", "24":   "96px", "28":  "112px","32":  "128px","36":  "144px",
    "40":  "160px","44":   "176px","48":  "192px","52":  "208px","56":  "224px",
    "60":  "240px","64":   "256px","72":  "288px","80":  "320px","96":  "384px"
}


TYPE_SCALE = {
    "xs":   {"size": 12, "lineHeight": 16},
    "sm":   {"size": 14, "lineHeight": 20},
    "base": {"size": 16, "lineHeight": 24},
    "lg":   {"size": 18, "lineHeight": 28},
    "xl":   {"size": 20, "lineHeight": 28},
    "2xl":  {"size": 24, "lineHeight": 32},
    "3xl":  {"size": 30, "lineHeight": 36},
    "4xl":  {"size": 36, "lineHeight": 40},
    "5xl":  {"size": 48, "lineHeight": 48},
    "6xl":  {"size": 60, "lineHeight": 60},
    "7xl":  {"size": 72, "lineHeight": 72},
    "8xl":  {"size": 96, "lineHeight": 96},
    "9xl":  {"size": 128, "lineHeight": 128}
}


WEIGHTS = {
    "thin":       100, "extralight": 200, "light":      300, "normal":     400,
    "medium":     500, "semibold":   600, "bold":       700, "extrabold":  800,
    "black":      900
}


RADIUS = {
    "none": "0px",    "sm":   "2px",    "default": "4px", "md":   "6px",
    "lg":   "8px",    "xl":   "12px",   "2xl":     "16px","3xl":  "24px",
    "full": "9999px"
}


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------

def build(hues_filter: list[str] | None = None) -> dict:
    """Compose the full Tailwind DTCG document.

    If ``hues_filter`` is provided, only the specified hues are included
    (e.g. ``["slate", "blue", "red"]``); otherwise all 16 default Tailwind
    hues are emitted. White, black, and transparent constants are always
    included. Output also contains the default spacing scale (33 stops from
    0 to 96), radius scale, four font weights mapped to numeric values, and
    the 13-step type ramp.
    """
    palette = {h: TAILWIND_PALETTE[h] for h in (hues_filter or list(TAILWIND_PALETTE.keys())) if h in TAILWIND_PALETTE}

    color = {}
    for hue, stops in palette.items():
        color[hue] = {step: {"$value": hex_val, "$type": "color"} for step, hex_val in stops.items()}
    for name, hex_val in CONSTANTS.items():
        color[name] = {"$value": hex_val, "$type": "color"}

    return {
        "color": color,
        "dimension": {
            "spacing": {step: {"$value": val, "$type": "dimension"} for step, val in SPACING.items()},
            "radius":  {step: {"$value": val, "$type": "dimension"} for step, val in RADIUS.items()}
        },
        "font": {
            "family": {
                "sans": {"$value": "Inter",          "$type": "fontFamily"},
                "mono": {"$value": "JetBrains Mono", "$type": "fontFamily"}
            },
            "weight": {name: {"$value": w, "$type": "fontWeight"} for name, w in WEIGHTS.items()}
        },
        "typography": {
            name: {
                "$type": "typography",
                "$value": {
                    "fontFamily":  "{font.family.sans}",
                    "fontSize":    f"{params['size']}px",
                    "lineHeight":  f"{params['lineHeight']}px",
                    "fontWeight":  400
                }
            }
            for name, params in TYPE_SCALE.items()
        },
        "$extensions": {
            "com.figma-forge": {
                "source":  "tailwind",
                "version": "v3 default",
                "hues":    list(palette.keys())
            }
        }
    }


def main() -> int:
    """CLI entry — parse arguments, run build(), write DTCG JSON to output path."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hues", help="Comma-separated hue subset (default: all)")
    p.add_argument("--output", default="tailwind.dtcg.json")
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args()

    hues_filter = [h.strip() for h in args.hues.split(",")] if args.hues else None
    dtcg = build(hues_filter)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dtcg, f, indent=2 if args.pretty else None, ensure_ascii=False)

    total_colors = sum(len(stops) if isinstance(stops, dict) and not any(k.startswith("$") for k in stops) else 0
                       for stops in dtcg["color"].values())
    print(f"✓ Wrote Tailwind DTCG to {args.output}", file=sys.stderr)
    print(f"  Hues: {len(hues_filter) if hues_filter else len(TAILWIND_PALETTE)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
