#!/usr/bin/env python3
"""
motion_spec_generator.py — Brand Motion Language Spec Generator

Marka arketipi + tonalite girdilerinden **motion personality spec** üretir:
duration ladders, easing curves, animation primitives, Lottie JSON iskeleti.

Marka kılavuzunun motion bölümünü dolduran spec'tir; motion designer'a
brief verir (Bodymovin/LottieFiles plugin export workflow).

Usage:
    python motion_spec_generator.py --archetype Sage --tonality "premium,calm"
    python motion_spec_generator.py --archetype Outlaw --tonality "bold,cesur"
    python motion_spec_generator.py --archetype Hero --format json
    python motion_spec_generator.py --archetype Magician --emit-lottie

Output formats:
    text     — Human-readable motion brief
    markdown — Brand book section ready
    json     — Programmatic spec (motion designer hand-off)

--emit-lottie  — Logo entry animation için stub Lottie JSON üretir
                 (designer After Effects'te detaylandırır, Bodymovin export'lar)

Reference standards:
    Lottie Specification v1.0 (Sept 2024) — github.com/lottie/lottie-spec
    All In Motion (2026) — Motion design in brand guidelines
    Material Design Motion — easing curves vocabulary
"""

import argparse
import json
import sys
from typing import Dict, List, Optional


# ============================================================================
# Archetype → Motion Personality Mapping
# ============================================================================
# Each archetype maps to (a) durations character, (b) easing personality,
# (c) animation primitives that "feel right" for the archetype.

ARCHETYPE_MOTION: Dict[str, Dict] = {
    "Innocent": {
        "personality": "Naïf, soft, gentle bounce. Optimistic but never frantic.",
        "duration_character": "moderate (250-450ms)",
        "easing_palette": [
            ("primary", "ease-out-soft", "cubic-bezier(0.25, 0.46, 0.45, 0.94)"),
            ("secondary", "ease-in-out-gentle", "cubic-bezier(0.4, 0, 0.2, 1)"),
        ],
        "primitives": ["fade-in-up", "soft-bounce-arrive", "gentle-pulse"],
        "duration_ladder": {
            "micro": "150ms", "ui": "300ms", "logo-stinger": "1.5s",
            "transition": "400ms",
        },
        "no-go": "no overshoot, no spring, no glitch effects",
    },
    "Everyman": {
        "personality": "Direct, honest, no-nonsense. Functional motion.",
        "duration_character": "fast-functional (150-300ms)",
        "easing_palette": [
            ("primary", "ease-out", "cubic-bezier(0, 0, 0.2, 1)"),
            ("secondary", "linear", "linear"),
        ],
        "primitives": ["fade-in", "slide-up-modest", "instant-snap"],
        "duration_ladder": {
            "micro": "100ms", "ui": "200ms", "logo-stinger": "1.0s",
            "transition": "250ms",
        },
        "no-go": "no decorative flourish, no spring, no exaggeration",
    },
    "Hero": {
        "personality": "Cesur, dinamik, decisive. Hareket vurgu = güç vurgu.",
        "duration_character": "snappy with confident weight (180-350ms)",
        "easing_palette": [
            ("primary", "ease-out-decisive", "cubic-bezier(0.16, 1, 0.3, 1)"),
            ("secondary", "ease-in-quart", "cubic-bezier(0.5, 0, 0.75, 0)"),
        ],
        "primitives": ["slam-arrive", "diagonal-stripe-reveal", "scale-up-bold"],
        "duration_ladder": {
            "micro": "120ms", "ui": "250ms", "logo-stinger": "1.2s",
            "transition": "300ms",
        },
        "no-go": "no soft bounce, no slow fade, no apologetic motion",
    },
    "Outlaw": {
        "personality": "Asi, bozuk, kasıtlı tutarsızlık. Glitch ve cut estetiği OK.",
        "duration_character": "abrupt + aggressive (80-200ms primary)",
        "easing_palette": [
            ("primary", "ease-in-cut", "cubic-bezier(0.7, 0, 0.84, 0)"),
            ("secondary", "step-end", "steps(3, end)"),  # cut-style steps
        ],
        "primitives": ["glitch-cut", "harsh-snap", "torn-reveal", "static-buzz"],
        "duration_ladder": {
            "micro": "80ms", "ui": "150ms", "logo-stinger": "0.8s",
            "transition": "180ms",
        },
        "no-go": "no smooth bezier, no gentle ease, no perfectionist polish",
    },
    "Explorer": {
        "personality": "Açık, akan, organic. Doğa ritmi — nehir, rüzgâr.",
        "duration_character": "extended + organic (400-800ms)",
        "easing_palette": [
            ("primary", "ease-out-organic", "cubic-bezier(0.215, 0.61, 0.355, 1)"),
            ("secondary", "ease-in-out-flow", "cubic-bezier(0.645, 0.045, 0.355, 1)"),
        ],
        "primitives": ["horizon-pan", "topographic-reveal", "wind-sway"],
        "duration_ladder": {
            "micro": "200ms", "ui": "400ms", "logo-stinger": "2.0s",
            "transition": "500ms",
        },
        "no-go": "no urban tech glitch, no robotic linear, no aggressive snap",
    },
    "Creator": {
        "personality": "Yaratıcı sürec, hand-drawn rhythm, generative feel.",
        "duration_character": "varied artistic (200-700ms across primitives)",
        "easing_palette": [
            ("primary", "ease-out-artistic", "cubic-bezier(0.34, 1.56, 0.64, 1)"),  # back-out
            ("secondary", "ease-in-out-organic", "cubic-bezier(0.4, 0, 0.2, 1)"),
        ],
        "primitives": ["pen-stroke-build", "modular-assemble", "color-fill-flood"],
        "duration_ladder": {
            "micro": "150ms", "ui": "350ms", "logo-stinger": "1.8s",
            "transition": "400ms",
        },
        "no-go": "no robotic linear, no instant-snap (kills 'made by hand' feel)",
    },
    "Ruler": {
        "personality": "Yetkili, contained, precise. Hiç fazlalık yok.",
        "duration_character": "controlled and exact (200-350ms)",
        "easing_palette": [
            ("primary", "ease-out-precise", "cubic-bezier(0.25, 0.1, 0.25, 1)"),
            ("secondary", "ease-in-quad", "cubic-bezier(0.55, 0.085, 0.68, 0.53)"),
        ],
        "primitives": ["formal-fade", "measured-reveal", "centered-scale"],
        "duration_ladder": {
            "micro": "150ms", "ui": "250ms", "logo-stinger": "1.5s",
            "transition": "300ms",
        },
        "no-go": "no overshoot, no playful bounce, no chaos",
    },
    "Magician": {
        "personality": "Dönüşüm, alchemy, smooth-impossible morphs.",
        "duration_character": "flowing and seamless (300-600ms)",
        "easing_palette": [
            ("primary", "ease-in-out-mystic", "cubic-bezier(0.83, 0, 0.17, 1)"),
            ("secondary", "ease-out-back", "cubic-bezier(0.34, 1.56, 0.64, 1)"),
        ],
        "primitives": ["morph-transform", "particle-coalesce", "alchemy-fade"],
        "duration_ladder": {
            "micro": "200ms", "ui": "400ms", "logo-stinger": "2.5s",
            "transition": "450ms",
        },
        "no-go": "no harsh cuts, no instant snap (breaks the spell)",
    },
    "Lover": {
        "personality": "Romantic, sensual, smooth curves. Velvet motion.",
        "duration_character": "languid (350-700ms)",
        "easing_palette": [
            ("primary", "ease-in-out-romantic", "cubic-bezier(0.77, 0, 0.175, 1)"),
            ("secondary", "ease-out-soft", "cubic-bezier(0.25, 0.46, 0.45, 0.94)"),
        ],
        "primitives": ["velvet-fade", "curve-trace", "soft-bloom"],
        "duration_ladder": {
            "micro": "200ms", "ui": "400ms", "logo-stinger": "2.2s",
            "transition": "500ms",
        },
        "no-go": "no aggressive snap, no robotic linear, no pixelated steps",
    },
    "Jester": {
        "personality": "Playful, bouncy, unexpected. Spring energy.",
        "duration_character": "bouncy with overshoot (250-500ms)",
        "easing_palette": [
            ("primary", "ease-out-back", "cubic-bezier(0.34, 1.56, 0.64, 1)"),
            ("secondary", "ease-elastic", "spring(1, 80, 10, 0)"),  # spring physics
        ],
        "primitives": ["spring-bounce", "wiggle-pulse", "playful-rotate"],
        "duration_ladder": {
            "micro": "150ms", "ui": "350ms", "logo-stinger": "1.5s",
            "transition": "400ms",
        },
        "no-go": "no formal stillness, no muted fade, no corporate stiffness",
    },
    "Caregiver": {
        "personality": "Soft, protective, slow-down. 'Her şey yolunda' hissi.",
        "duration_character": "gentle and unhurried (300-500ms)",
        "easing_palette": [
            ("primary", "ease-out-soft", "cubic-bezier(0.215, 0.61, 0.355, 1)"),
            ("secondary", "ease-in-out-gentle", "cubic-bezier(0.4, 0, 0.2, 1)"),
        ],
        "primitives": ["soft-fade", "embrace-scale", "warm-pulse"],
        "duration_ladder": {
            "micro": "180ms", "ui": "350ms", "logo-stinger": "1.8s",
            "transition": "400ms",
        },
        "no-go": "no harsh cut, no aggressive snap, no anxiety-inducing flicker",
    },
    "Sage": {
        "personality": "Considered, slow, intentional. Akademik dinginlik.",
        "duration_character": "deliberate (300-450ms)",
        "easing_palette": [
            ("primary", "ease-out", "cubic-bezier(0, 0, 0.2, 1)"),
            ("secondary", "linear", "linear"),
        ],
        "primitives": ["measured-fade", "scholarly-reveal", "centered-stillness"],
        "duration_ladder": {
            "micro": "200ms", "ui": "300ms", "logo-stinger": "1.5s",
            "transition": "350ms",
        },
        "no-go": "no playful bounce, no spring, no decorative flourish",
    },
}


# Tonality modifiers — adjust archetype defaults
TONALITY_MODIFIERS: Dict[str, Dict] = {
    "premium": {"slowdown_factor": 1.15, "easing_bias": "more curve"},
    "luxury": {"slowdown_factor": 1.25, "easing_bias": "more curve"},
    "fast":  {"slowdown_factor": 0.75, "easing_bias": "snappier"},
    "snappy": {"slowdown_factor": 0.80, "easing_bias": "snappier"},
    "calm":   {"slowdown_factor": 1.20, "easing_bias": "more linear"},
    "minimal": {"slowdown_factor": 1.00, "easing_bias": "more linear"},
    "bold":   {"slowdown_factor": 0.85, "easing_bias": "snappier"},
    "cesur":  {"slowdown_factor": 0.85, "easing_bias": "snappier"},
    "sıcak":  {"slowdown_factor": 1.10, "easing_bias": "more curve"},
    "soğuk":  {"slowdown_factor": 1.00, "easing_bias": "more linear"},
}


def apply_tonality(spec: Dict, tonalities: List[str]) -> Dict:
    """Apply tonality modifiers to base archetype motion spec."""
    spec = json.loads(json.dumps(spec))  # deep copy
    factor_acc = 1.0
    bias_notes = []
    for t in tonalities:
        t_lower = t.lower().strip()
        if t_lower in TONALITY_MODIFIERS:
            mod = TONALITY_MODIFIERS[t_lower]
            factor_acc *= mod["slowdown_factor"]
            bias_notes.append(f"{t}→{mod['easing_bias']}")

    # Apply slowdown to all durations in ladder
    for k, v in spec["duration_ladder"].items():
        if v.endswith("ms"):
            ms = int(v.replace("ms", ""))
            spec["duration_ladder"][k] = f"{int(ms * factor_acc)}ms"
        elif v.endswith("s"):
            s = float(v.replace("s", ""))
            spec["duration_ladder"][k] = f"{s * factor_acc:.1f}s"

    spec["tonality_applied"] = tonalities
    spec["tonality_factor"] = round(factor_acc, 2)
    spec["tonality_bias"] = bias_notes
    return spec


# ============================================================================
# Lottie skeleton generation
# ============================================================================
# A minimal Lottie 5.7 JSON for a logo entry animation.
# Designer fills in actual shape layers via Bodymovin/LottieFiles export.

def emit_lottie_skeleton(archetype: str, motion_spec: Dict,
                         logo_dimensions=(1024, 1024)) -> Dict:
    """Generate stub Lottie JSON — designer fills shape data in After Effects."""
    duration_str = motion_spec["duration_ladder"]["logo-stinger"]
    if duration_str.endswith("s"):
        duration_seconds = float(duration_str.replace("s", ""))
    else:
        duration_seconds = float(duration_str.replace("ms", "")) / 1000.0
    fps = 60
    out_frame = int(duration_seconds * fps)

    primary_easing = motion_spec["easing_palette"][0]
    primary_curve = primary_easing[2]

    return {
        "v": "5.7.0",
        "fr": fps,
        "ip": 0,
        "op": out_frame,
        "w": logo_dimensions[0],
        "h": logo_dimensions[1],
        "nm": f"{archetype} Brand Logo Stinger",
        "ddd": 0,
        "assets": [],
        "layers": [
            {
                "ddd": 0,
                "ind": 1,
                "ty": 4,  # shape layer
                "nm": "LOGO_PLACEHOLDER",
                "sr": 1,
                "ks": {  # transform
                    "o": {  # opacity
                        "a": 1,
                        "k": [
                            {"i": {"x": [0.667], "y": [1]},
                             "o": {"x": [0.333], "y": [0]},
                             "t": 0, "s": [0]},
                            {"t": out_frame * 0.6, "s": [100]}
                        ]
                    },
                    "p": {  # position
                        "a": 0,
                        "k": [logo_dimensions[0] / 2, logo_dimensions[1] / 2, 0]
                    },
                    "s": {  # scale
                        "a": 1,
                        "k": [
                            {"i": {"x": [0.667, 0.667], "y": [1, 1]},
                             "o": {"x": [0.333, 0.333], "y": [0, 0]},
                             "t": 0, "s": [80, 80]},
                            {"t": out_frame, "s": [100, 100]}
                        ]
                    },
                    "r": {"a": 0, "k": 0},  # rotation
                },
                "ao": 0,
                "shapes": [
                    {
                        "ty": "gr",  # group placeholder
                        "it": [
                            {
                                "ty": "rc",  # rectangle placeholder
                                "d": 1,
                                "s": {"a": 0, "k": [400, 400]},
                                "p": {"a": 0, "k": [0, 0]},
                                "r": {"a": 0, "k": 0},
                                "nm": "Replace with logo paths in After Effects",
                            },
                            {
                                "ty": "fl",
                                "c": {"a": 0, "k": [0.357, 0.357, 0.839, 1]},
                                "o": {"a": 0, "k": 100},
                                "nm": "Brand color fill",
                            },
                            {
                                "ty": "tr",
                                "p": {"a": 0, "k": [0, 0]},
                                "a": {"a": 0, "k": [0, 0]},
                                "s": {"a": 0, "k": [100, 100]},
                                "r": {"a": 0, "k": 0},
                                "o": {"a": 0, "k": 100},
                            }
                        ]
                    }
                ],
                "ip": 0,
                "op": out_frame,
                "st": 0,
                "bm": 0,
            }
        ],
        "markers": [],
        "_brand_visual_meta": {
            "archetype": archetype,
            "primary_easing_curve": primary_curve,
            "duration_ladder": motion_spec["duration_ladder"],
            "instructions": (
                "Replace LOGO_PLACEHOLDER shape group with your actual brand "
                "logo paths in After Effects. Apply the primary easing curve "
                f"({primary_curve}) to all keyframes. Export via Bodymovin/"
                "LottieFiles plugin to maintain Lottie compatibility."
            ),
        }
    }


# ============================================================================
# Output formatters
# ============================================================================

def format_text(archetype: str, spec: Dict) -> str:
    lines = [
        f"Brand Motion Specification — {archetype} Archetype",
        "=" * 60,
        f"",
        f"Personality: {spec['personality']}",
        f"Duration character: {spec['duration_character']}",
        f"",
        f"DURATION LADDER (millisecond targets):",
    ]
    for k, v in spec["duration_ladder"].items():
        lines.append(f"  {k:18s}  {v}")
    lines += [
        "",
        "EASING PALETTE:",
    ]
    for role, name, curve in spec["easing_palette"]:
        lines.append(f"  {role}: {name}")
        lines.append(f"      → {curve}")
    lines += [
        "",
        "ANIMATION PRIMITIVES (logo entry / interaction options):",
    ]
    for p in spec["primitives"]:
        lines.append(f"  • {p}")
    lines += [
        "",
        f"NO-GO ZONE: {spec['no-go']}",
    ]
    if "tonality_applied" in spec:
        lines += [
            "",
            f"Tonality modifiers applied: {', '.join(spec['tonality_applied'])}",
            f"  Slowdown factor: ×{spec['tonality_factor']}",
            f"  Bias adjustments: {', '.join(spec['tonality_bias'])}",
        ]
    return "\n".join(lines)


def format_markdown(archetype: str, spec: Dict) -> str:
    lines = [
        f"## Brand Motion Specification — {archetype}",
        "",
        f"**Personality**: {spec['personality']}",
        f"**Duration character**: {spec['duration_character']}",
        "",
        "### Duration Ladder",
        "",
        "| Context | Duration |",
        "|---------|----------|",
    ]
    for k, v in spec["duration_ladder"].items():
        lines.append(f"| {k} | `{v}` |")

    lines += [
        "",
        "### Easing Palette",
        "",
        "| Role | Name | CSS / cubic-bezier |",
        "|------|------|---------------------|",
    ]
    for role, name, curve in spec["easing_palette"]:
        lines.append(f"| {role} | {name} | `{curve}` |")

    lines += [
        "",
        "### Animation Primitives",
        "",
    ]
    for p in spec["primitives"]:
        lines.append(f"- **{p}**")

    lines += [
        "",
        f"### No-Go Zone",
        "",
        f"> {spec['no-go']}",
    ]

    if "tonality_applied" in spec:
        lines += [
            "",
            "### Tonality Adjustments Applied",
            "",
            f"- Modifiers: `{', '.join(spec['tonality_applied'])}`",
            f"- Duration slowdown factor: ×{spec['tonality_factor']}",
            f"- Easing bias: {', '.join(spec['tonality_bias'])}",
        ]

    lines += [
        "",
        "### Hand-off Standards",
        "",
        "- **Source format**: Adobe After Effects project (.aep)",
        "- **Web/mobile delivery**: Lottie JSON (via Bodymovin or LottieFiles plugin)",
        "- **Video delivery**: MP4 ProRes 4444 (transparent background) for editing",
        "- **Cinema/marketing**: 1920×1080 master, then crop variants per platform",
        "- **Logo stinger ceiling**: 2.5 seconds max in enterprise contexts (All In Motion 2026)",
        "- **Light + dark mode variants**: REQUIRED — animation behavior may differ on dark backgrounds",
        "",
    ]
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate brand motion language spec from archetype + tonality.",
    )
    parser.add_argument("--archetype",
                        choices=list(ARCHETYPE_MOTION.keys()),
                        required=True, help="Brand archetype (Pearson & Mark)")
    parser.add_argument("--tonality", default="",
                        help="Comma-separated tonality modifiers "
                             "(e.g. 'premium,calm' or 'bold,cesur')")
    parser.add_argument("--format", choices=["text", "markdown", "json"],
                        default="markdown", help="Output format")
    parser.add_argument("--emit-lottie", action="store_true",
                        help="Also emit Lottie JSON skeleton stub")
    parser.add_argument("--lottie-output", type=str, default=None,
                        help="Path to write Lottie JSON skeleton")
    parser.add_argument("--logo-w", type=int, default=1024,
                        help="Logo width for Lottie composition (default: 1024)")
    parser.add_argument("--logo-h", type=int, default=1024,
                        help="Logo height for Lottie composition (default: 1024)")

    args = parser.parse_args()

    base_spec = ARCHETYPE_MOTION[args.archetype]
    tonalities = [t.strip() for t in args.tonality.split(",") if t.strip()]
    spec = apply_tonality(base_spec, tonalities) if tonalities else base_spec

    if args.format == "json":
        print(json.dumps(spec, indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        print(format_markdown(args.archetype, spec))
    else:
        print(format_text(args.archetype, spec))

    if args.emit_lottie:
        lottie = emit_lottie_skeleton(args.archetype, spec,
                                       (args.logo_w, args.logo_h))
        out_path = args.lottie_output or f"{args.archetype.lower()}-stinger-skeleton.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(lottie, f, indent=2, ensure_ascii=False)
        print(f"\n[Lottie skeleton written to: {out_path}]", file=sys.stderr)


if __name__ == "__main__":
    main()
