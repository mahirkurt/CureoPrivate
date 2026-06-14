#!/usr/bin/env python3
"""
wcag_contrast.py — WCAG + APCA Contrast Calculator

İki renk arası kontrast oranını, hem WCAG 2.x standardı hem de APCA (Accessible
Perceptual Contrast Algorithm, WCAG 3 adayı) ile hesaplar. Her use-case için
pass/fail verdikleri ile birlikte.

Usage:
    python wcag_contrast.py "#5B5BD6" "#FFFFFF"
    python wcag_contrast.py "#5B5BD6" "#FCFCFD"  # brand on subtle bg
    python wcag_contrast.py "#2E2E80" "#F9F9FB" --text-size body
    python wcag_contrast.py "#4747B5" "#FCFCFD" --verbose

Standards:
    WCAG 2.2: Ratio 1:1 to 21:1
      - AA Normal text (body): ≥4.5
      - AA Large text (≥18pt or ≥14pt bold): ≥3.0
      - AA UI components: ≥3.0
      - AAA Normal text: ≥7.0
      - AAA Large text: ≥4.5

    APCA (WCAG 3 draft): Lc -108 to +108
      - Lc 75+: Fluent body text
      - Lc 60+: Comfortable content text (Radix step 11 target)
      - Lc 45+: Large headlines / UI labels
      - Lc 30+: Minimum for non-text / decorative
      - Lc 90+: High-contrast text (Radix step 12 target)

Referans:
    WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum
    APCA: https://git.apcacontrast.com/documentation/APCAeasyIntro
"""

import argparse
import math
import sys
from typing import Tuple


# ============================================================================
# WCAG 2.x Contrast (relative luminance ratio)
# ============================================================================

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def srgb_to_linear(c: float) -> float:
    """sRGB channel (0-1) → linear luminance component."""
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(r: int, g: int, b: int) -> float:
    """WCAG relative luminance.

    https://www.w3.org/TR/WCAG22/#dfn-relative-luminance
    """
    r_lin = srgb_to_linear(r / 255.0)
    g_lin = srgb_to_linear(g / 255.0)
    b_lin = srgb_to_linear(b / 255.0)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def wcag_contrast_ratio(color1: str, color2: str) -> float:
    """WCAG 2.2 contrast ratio, 1:1 to 21:1.

    https://www.w3.org/TR/WCAG22/#contrast-minimum
    """
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    l1 = relative_luminance(r1, g1, b1)
    l2 = relative_luminance(r2, g2, b2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ============================================================================
# APCA (WCAG 3 draft) — Lc value, perceptually-based
# ============================================================================

# APCA exponents + coefficients (v0.98G-4g, locked 2022-04)
# https://github.com/Myndex/SAPC-APCA
APCA_NORM_TEXT = 0.57
APCA_REV_TEXT = 0.62
APCA_NORM_BG = 0.56
APCA_REV_BG = 0.65
APCA_BLK_THRS = 0.022
APCA_BLK_CLMP = 1.414
APCA_SCALE_BOW = 1.14
APCA_SCALE_WOB = 1.14
APCA_LOW_BOW = 0.001
APCA_LOW_WOB = 0.001
APCA_LOW_OFFSET = 0.027


def apca_luminance(r: int, g: int, b: int) -> float:
    """APCA sRGB-Y luminance (not same as WCAG)."""
    r_norm = (r / 255.0) ** 2.4
    g_norm = (g / 255.0) ** 2.4
    b_norm = (b / 255.0) ** 2.4
    return 0.2126729 * r_norm + 0.7151522 * g_norm + 0.0721750 * b_norm


def apca_contrast_lc(text_hex: str, bg_hex: str) -> float:
    """APCA Lc contrast value.

    Positive = dark text on light bg (BoW — black on white)
    Negative = light text on dark bg (WoB — white on black)

    Returns float Lc, typical range -108 to +108. Absolute values matter
    for accessibility decisions.
    """
    r_t, g_t, b_t = hex_to_rgb(text_hex)
    r_b, g_b, b_b = hex_to_rgb(bg_hex)

    y_text = apca_luminance(r_t, g_t, b_t)
    y_bg = apca_luminance(r_b, g_b, b_b)

    # Soft clamp black levels
    if y_text < APCA_BLK_THRS:
        y_text = y_text + (APCA_BLK_THRS - y_text) ** APCA_BLK_CLMP
    if y_bg < APCA_BLK_THRS:
        y_bg = y_bg + (APCA_BLK_THRS - y_bg) ** APCA_BLK_CLMP

    # Tolerance for insignificant differences
    if abs(y_bg - y_text) < 0.0005:
        return 0.0

    if y_bg > y_text:
        # BoW — dark text on light bg (positive Lc)
        sapc = (y_bg ** APCA_NORM_BG - y_text ** APCA_NORM_TEXT) * APCA_SCALE_BOW
        if sapc < APCA_LOW_BOW:
            return 0.0
        lc = (sapc - APCA_LOW_OFFSET) * 100.0
    else:
        # WoB — light text on dark bg (negative Lc)
        sapc = (y_bg ** APCA_REV_BG - y_text ** APCA_REV_TEXT) * APCA_SCALE_WOB
        if sapc > -APCA_LOW_WOB:
            return 0.0
        lc = (sapc + APCA_LOW_OFFSET) * 100.0

    return lc


# ============================================================================
# Compliance evaluation
# ============================================================================

WCAG_THRESHOLDS = {
    "AA_normal": 4.5,
    "AA_large": 3.0,
    "AA_ui": 3.0,
    "AAA_normal": 7.0,
    "AAA_large": 4.5,
}

APCA_THRESHOLDS = {
    "body_fluent": 75,  # Fluent body text
    "body_comfortable": 60,  # Comfortable content (Radix step 11)
    "headline_large": 45,  # Large headlines, UI labels
    "non_text": 30,  # Minimum for non-text content
    "high_contrast": 90,  # AAA-equivalent high contrast (Radix step 12)
}


def evaluate_wcag(ratio: float) -> dict:
    return {
        "AA Normal text (body ≥16px)": "✓ PASS" if ratio >= 4.5 else "✗ FAIL",
        "AA Large text (≥18pt, 14pt+bold)": "✓ PASS" if ratio >= 3.0 else "✗ FAIL",
        "AA UI components / graphics": "✓ PASS" if ratio >= 3.0 else "✗ FAIL",
        "AAA Normal text": "✓ PASS" if ratio >= 7.0 else "✗ FAIL",
        "AAA Large text": "✓ PASS" if ratio >= 4.5 else "✗ FAIL",
    }


def evaluate_apca(lc_abs: float) -> dict:
    return {
        "Fluent body text (Lc 75+)": "✓ PASS" if lc_abs >= 75 else "✗ FAIL",
        "Comfortable content text (Lc 60+)": "✓ PASS" if lc_abs >= 60 else "✗ FAIL",
        "Large headlines / UI labels (Lc 45+)": "✓ PASS" if lc_abs >= 45 else "✗ FAIL",
        "Non-text / graphic (Lc 30+)": "✓ PASS" if lc_abs >= 30 else "✗ FAIL",
        "High-contrast text (Lc 90+)": "✓ PASS" if lc_abs >= 90 else "✗ FAIL",
    }


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="WCAG 2.x + APCA contrast calculator for brand color pairs.",
    )
    parser.add_argument("text_color", help="Text/foreground hex (e.g. '#5B5BD6')")
    parser.add_argument("bg_color", help="Background hex (e.g. '#FFFFFF')")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Detailed per-threshold breakdown",
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()

    try:
        ratio = wcag_contrast_ratio(args.text_color, args.bg_color)
        lc = apca_contrast_lc(args.text_color, args.bg_color)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    lc_abs = abs(lc)
    polarity = "BoW (dark-on-light)" if lc > 0 else "WoB (light-on-dark)" if lc < 0 else "equal luminance"

    if args.format == "markdown":
        print(f"## Contrast Analysis\n")
        print(f"- **Text**: `{args.text_color}`")
        print(f"- **Background**: `{args.bg_color}`")
        print(f"- **Polarity**: {polarity}")
        print(f"- **WCAG 2.x Ratio**: {ratio:.2f}:1")
        print(f"- **APCA Lc**: {lc:.1f}\n")

        print("### WCAG 2.x")
        print("| Use Case | Status |")
        print("|----------|--------|")
        for case, status in evaluate_wcag(ratio).items():
            print(f"| {case} | {status} |")

        print("\n### APCA (WCAG 3 draft)")
        print("| Use Case | Status |")
        print("|----------|--------|")
        for case, status in evaluate_apca(lc_abs).items():
            print(f"| {case} | {status} |")
    else:
        print(f"TEXT:         {args.text_color}")
        print(f"BACKGROUND:   {args.bg_color}")
        print(f"POLARITY:     {polarity}")
        print()
        print(f"WCAG 2.x ratio: {ratio:.2f}:1")
        print(f"APCA Lc:        {lc:+.1f}  (absolute: {lc_abs:.1f})")
        print()

        if args.verbose:
            print("--- WCAG 2.x compliance ---")
            for case, status in evaluate_wcag(ratio).items():
                print(f"  {status}  {case}")
            print()
            print("--- APCA compliance ---")
            for case, status in evaluate_apca(lc_abs).items():
                print(f"  {status}  {case}")
        else:
            # Quick summary
            aa_normal = "PASS" if ratio >= 4.5 else "FAIL"
            aaa_normal = "PASS" if ratio >= 7.0 else "FAIL"
            apca_body = "PASS" if lc_abs >= 60 else "FAIL"
            apca_high = "PASS" if lc_abs >= 90 else "FAIL"
            print(f"WCAG AA body:   {aa_normal} (need ≥4.5)")
            print(f"WCAG AAA body:  {aaa_normal} (need ≥7.0)")
            print(f"APCA body:      {apca_body} (need Lc 60+)")
            print(f"APCA high-contrast: {apca_high} (need Lc 90+)")


if __name__ == "__main__":
    main()
