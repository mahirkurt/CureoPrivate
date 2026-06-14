#!/usr/bin/env python3
"""
palette_generator.py — Radix-Style 12-Step Palette Generator

Bir base HEX renginden, Radix Colors metodolojisine uygun 12-step light + dark mode
paletleri üretir. OKLCH color space (perceptually uniform) kullanır.

Usage:
    python palette_generator.py "#5B5BD6"
    python palette_generator.py "#5B5BD6" --mode light
    python palette_generator.py "#5B5BD6" --mode dark
    python palette_generator.py "#5B5BD6" --mode both
    python palette_generator.py "#5B5BD6" --format css     # default
    python palette_generator.py "#5B5BD6" --format tailwind
    python palette_generator.py "#5B5BD6" --format json
    python palette_generator.py "#5B5BD6" --name "curio-indigo"

Radix 12-step semantic scale:
    1-2: App / subtle backgrounds
    3-5: UI component backgrounds (default / hover / pressed)
    6-8: Borders (subtle / interactive / strong/focus)
    9-10: Solid brand actions (primary / hover)
    11-12: Text (low-contrast / high-contrast)

No external dependencies — pure Python stdlib.

Referans: https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale
"""

import argparse
import colorsys
import json
import math
import sys
from typing import List, Tuple


# ============================================================================
# Color space conversions — HEX ↔ RGB ↔ OKLCH
# ============================================================================

def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """#RRGGBB → (r, g, b) floats 0-1."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return (r, g, b)


def rgb_to_hex(r: float, g: float, b: float) -> str:
    """(r, g, b) floats 0-1 → #RRGGBB."""
    r = max(0.0, min(1.0, r))
    g = max(0.0, min(1.0, g))
    b = max(0.0, min(1.0, b))
    return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"


def srgb_to_linear(c: float) -> float:
    """sRGB gamma correction → linear."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    """Linear → sRGB gamma correction."""
    return c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def rgb_to_oklab(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """sRGB → OKLab (perceptually uniform).

    Reference: Björn Ottosson, https://bottosson.github.io/posts/oklab/
    """
    # 1. sRGB → linear
    lr, lg, lb = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    # 2. Linear RGB → LMS
    l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
    m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
    s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb
    # 3. LMS → LMS^1/3
    l_, m_, s_ = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    # 4. LMS^1/3 → OKLab
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_out = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return (L, a, b_out)


def oklab_to_rgb(L: float, a: float, b: float) -> Tuple[float, float, float]:
    """OKLab → sRGB (reverse)."""
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3
    lr = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    lg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    lb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    r = linear_to_srgb(lr)
    g = linear_to_srgb(lg)
    b_out = linear_to_srgb(lb)
    return (r, g, b_out)


def rgb_to_oklch(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """sRGB → OKLCH (L=lightness, C=chroma, H=hue degrees)."""
    L, a, b_val = rgb_to_oklab(r, g, b)
    C = math.sqrt(a * a + b_val * b_val)
    H = math.degrees(math.atan2(b_val, a)) % 360.0
    return (L, C, H)


def oklch_to_rgb(L: float, C: float, H: float) -> Tuple[float, float, float]:
    """OKLCH → sRGB."""
    H_rad = math.radians(H)
    a = C * math.cos(H_rad)
    b_val = C * math.sin(H_rad)
    return oklab_to_rgb(L, a, b_val)


# ============================================================================
# Radix-style 12-step scale generation
# ============================================================================

# Lightness curve for light mode (L values 0-1 in OKLab)
# Reverse-engineered from Radix Colors observation:
#   Step 1: L ≈ 0.995 (nearly white tinted)
#   Step 2: L ≈ 0.985
#   Step 3: L ≈ 0.960
#   Step 4: L ≈ 0.930
#   Step 5: L ≈ 0.895
#   Step 6: L ≈ 0.850
#   Step 7: L ≈ 0.790
#   Step 8: L ≈ 0.715
#   Step 9: brand — keep at source L  (anchor)
#   Step 10: L reduced by ~0.08 (hover darker)
#   Step 11: L ≈ 0.50 (low-contrast text, target APCA Lc 60)
#   Step 12: L ≈ 0.25 (high-contrast text, target APCA Lc 90)

LIGHT_MODE_L_CURVE = [
    0.995,  # 1
    0.980,  # 2
    0.958,  # 3
    0.928,  # 4
    0.893,  # 5
    0.848,  # 6
    0.788,  # 7
    0.712,  # 8
    None,   # 9 = base color L anchor
    None,   # 10 = base L - 0.08
    0.500,  # 11
    0.260,  # 12
]

# Chroma curve (light mode). Low-step chroma very small (near-gray),
# step 9 peaks, steps 11-12 reduced chroma for readability.
LIGHT_MODE_C_CURVE = [
    0.005,  # 1
    0.010,  # 2
    0.020,  # 3
    0.035,  # 4
    0.050,  # 5
    0.070,  # 6
    0.090,  # 7
    0.120,  # 8
    None,   # 9 = base chroma (peak)
    None,   # 10 = base chroma slightly reduced
    0.160,  # 11
    0.110,  # 12
]

# Dark mode — invert the L curve, raise chroma slightly (dark mode needs
# brighter/more chromatic colors to maintain perceived brand feel).
DARK_MODE_L_CURVE = [
    0.120,  # 1  (deepest bg)
    0.155,  # 2
    0.205,  # 3
    0.250,  # 4
    0.300,  # 5
    0.365,  # 6
    0.440,  # 7
    0.535,  # 8
    None,   # 9 = base L + 0.05 (brighter in dark mode)
    None,   # 10 = base L + 0.10
    0.770,  # 11
    0.920,  # 12
]

DARK_MODE_C_CURVE = [
    0.015,  # 1
    0.020,  # 2
    0.040,  # 3
    0.055,  # 4
    0.075,  # 5
    0.100,  # 6
    0.130,  # 7
    0.165,  # 8
    None,   # 9 = base C + 0.02
    None,   # 10 = base C + 0.02
    0.190,  # 11
    0.080,  # 12
]


def generate_scale(base_hex: str, mode: str = "light") -> List[str]:
    """Generate 12-step Radix-style scale from base color.

    Args:
        base_hex: Base color hex (will be anchored at step 9)
        mode: 'light' or 'dark'

    Returns:
        List of 12 hex strings (step 1 → step 12)
    """
    r, g, b = hex_to_rgb(base_hex)
    base_L, base_C, base_H = rgb_to_oklch(r, g, b)

    if mode == "light":
        l_curve = LIGHT_MODE_L_CURVE.copy()
        c_curve = LIGHT_MODE_C_CURVE.copy()
        # Step 9 = base
        l_curve[8] = base_L
        c_curve[8] = base_C
        # Step 10 = darker hover
        l_curve[9] = max(0.15, base_L - 0.08)
        c_curve[9] = base_C * 0.95
    elif mode == "dark":
        l_curve = DARK_MODE_L_CURVE.copy()
        c_curve = DARK_MODE_C_CURVE.copy()
        # Step 9 = brighter in dark mode
        l_curve[8] = min(0.85, base_L + 0.05)
        c_curve[8] = base_C + 0.02
        # Step 10 = even brighter
        l_curve[9] = min(0.90, base_L + 0.10)
        c_curve[9] = base_C + 0.02
    else:
        raise ValueError(f"Invalid mode: {mode}")

    scale = []
    for L, C in zip(l_curve, c_curve):
        rgb = oklch_to_rgb(L, C, base_H)
        # Gamut clip — OKLCH can produce out-of-gamut sRGB
        rgb = tuple(max(0.0, min(1.0, c)) for c in rgb)
        scale.append(rgb_to_hex(*rgb))
    return scale


# ============================================================================
# Use case labels (Radix semantic)
# ============================================================================

USE_CASES = [
    ("1", "App background"),
    ("2", "Subtle background"),
    ("3", "UI element background"),
    ("4", "UI element bg (hover)"),
    ("5", "UI element bg (pressed/selected)"),
    ("6", "Subtle border (non-interactive)"),
    ("7", "Subtle border (interactive)"),
    ("8", "Strong border / focus ring"),
    ("9", "Solid action (PRIMARY)"),
    ("10", "Solid hover"),
    ("11", "Low-contrast text (APCA Lc 60)"),
    ("12", "High-contrast text (APCA Lc 90)"),
]


# ============================================================================
# Output formatters
# ============================================================================

def format_css(scale_light: List[str], scale_dark: List[str], name: str) -> str:
    """CSS custom properties format."""
    lines = [f"/* === {name.upper()} — Radix-Style 12-Step Scale === */\n"]
    lines.append(":root {")
    for i, hex_val in enumerate(scale_light, 1):
        _, use = USE_CASES[i - 1]
        lines.append(f"  --{name}-{i}: {hex_val}; /* {use} */")
    lines.append("}")
    lines.append("")
    lines.append('[data-theme="dark"] {')
    for i, hex_val in enumerate(scale_dark, 1):
        lines.append(f"  --{name}-{i}: {hex_val};")
    lines.append("}")
    return "\n".join(lines)


def format_tailwind(scale_light: List[str], scale_dark: List[str], name: str) -> str:
    """Tailwind config snippet."""
    lines = [
        f"// === {name} — Radix-Style 12-Step Scale ===",
        "// Add to tailwind.config.js theme.extend.colors",
        "",
        f"{name}: {{",
    ]
    for i, hex_val in enumerate(scale_light, 1):
        lines.append(f"  {i}: 'var(--{name}-{i})',")
    lines.append("},")
    lines.append("")
    lines.append("// Also define CSS variables per mode (see CSS output):")
    lines.append(format_css(scale_light, scale_dark, name))
    return "\n".join(lines)


def format_json(scale_light: List[str], scale_dark: List[str], name: str) -> str:
    """W3C Design Tokens JSON format."""
    tokens = {"color": {name: {}}}
    for i, hex_val in enumerate(scale_light, 1):
        _, use = USE_CASES[i - 1]
        tokens["color"][name][str(i)] = {
            "value": hex_val,
            "type": "color",
            "description": use,
        }
    tokens["color"][f"{name}-dark"] = {}
    for i, hex_val in enumerate(scale_dark, 1):
        tokens["color"][f"{name}-dark"][str(i)] = {
            "value": hex_val,
            "type": "color",
        }
    return json.dumps(tokens, indent=2)


def format_table(scale_light: List[str], scale_dark: List[str], name: str) -> str:
    """Human-readable markdown table."""
    lines = [f"# {name.upper()} — 12-Step Palette\n"]
    lines.append("## Light Mode Scale")
    lines.append("| Step | HEX | Use Case |")
    lines.append("|------|-----|----------|")
    for i, hex_val in enumerate(scale_light, 1):
        _, use = USE_CASES[i - 1]
        lines.append(f"| {i} | `{hex_val}` | {use} |")
    lines.append("")
    lines.append("## Dark Mode Scale")
    lines.append("| Step | HEX | Use Case |")
    lines.append("|------|-----|----------|")
    for i, hex_val in enumerate(scale_dark, 1):
        _, use = USE_CASES[i - 1]
        lines.append(f"| {i} | `{hex_val}` | {use} |")
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate Radix-style 12-step color palette from a base color.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("base_color", help="Base color hex (e.g. '#5B5BD6')")
    parser.add_argument(
        "--mode",
        choices=["light", "dark", "both"],
        default="both",
        help="Which mode(s) to output (default: both)",
    )
    parser.add_argument(
        "--format",
        choices=["css", "tailwind", "json", "table"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--name",
        default="brand",
        help="Color token name (default: 'brand')",
    )

    args = parser.parse_args()

    try:
        scale_light = generate_scale(args.base_color, "light")
        scale_dark = generate_scale(args.base_color, "dark")
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Emit base color info
    r, g, b = hex_to_rgb(args.base_color)
    L, C, H = rgb_to_oklch(r, g, b)
    print(f"# Base color: {args.base_color}", file=sys.stderr)
    print(f"# OKLCH: L={L:.3f} C={C:.3f} H={H:.1f}°", file=sys.stderr)
    print(f"# Token name: --{args.name}-[1..12]", file=sys.stderr)
    print("", file=sys.stderr)

    # Output
    if args.format == "css":
        print(format_css(scale_light, scale_dark, args.name))
    elif args.format == "tailwind":
        print(format_tailwind(scale_light, scale_dark, args.name))
    elif args.format == "json":
        print(format_json(scale_light, scale_dark, args.name))
    else:  # table
        print(format_table(scale_light, scale_dark, args.name))


if __name__ == "__main__":
    main()
