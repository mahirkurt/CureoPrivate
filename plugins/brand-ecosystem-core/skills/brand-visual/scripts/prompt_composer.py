#!/usr/bin/env python3
"""
prompt_composer.py — Structured AI Image Generation Prompt Composer

brand-visual skill'in 7-element prompt formülüyle multi-model AI prompt üretir
(Midjourney V7/V8, Niji 7, Flux.1, DALL-E 3, Ideogram).

Usage (CLI arg mode):
    python prompt_composer.py \\
        --subject "letter C formed by two nested arcs suggesting an aperture and curiosity" \\
        --logo-type "minimalist monogram" \\
        --style-anchor "Paul Rand,Sagi Haviv" \\
        --color "deep indigo on pure white" \\
        --sector coffee \\
        --model midjourney

Usage (interactive mode):
    python prompt_composer.py --interactive

Multi-model output:
    python prompt_composer.py [args] --model all

Models:
    midjourney (V7/V8 alpha) — default flagship
    niji (V7) — illustration/character
    flux (Dev/Schnell) — open source
    dalle (3) — best text rendering
    ideogram (2.0) — text-heavy / posters
    all — produce variants for all models

No external dependencies.
"""

import argparse
import sys
from typing import Dict, List, Optional


# ============================================================================
# Base negative prompt (always applied)
# ============================================================================

BASE_NEGATIVES = [
    "text", "typography", "letters", "words", "writing",
    "realistic photo details", "3d render", "3d",
    "gradients", "drop shadows", "glow effect",
    "mockup environments", "product mockup",
    "watermark", "signature",
    "multiple variants in one image", "collage",
    "busy background", "ornaments", "decoration",
    "stock icon look", "generic vector art", "cliche",
]

# ============================================================================
# Sector-specific negatives (red-lines.md synthesis)
# ============================================================================

SECTOR_NEGATIVES: Dict[str, List[str]] = {
    "real-estate": [
        "house silhouette", "roof shape", "key icon",
        "location pin", "skyline", "chimney", "window frame",
    ],
    "fintech": [
        "credit card", "dollar sign", "coin", "vault",
        "blue-green corporate gradient", "safe box",
        "stock chart upward arrow", "currency symbol",
    ],
    "healthcare": [
        "stethoscope", "heart shape", "EKG line",
        "medical cross", "pill", "bandage", "DNA helix",
        "caduceus", "red cross",
    ],
    "pharma": [
        "pill", "tablet", "capsule", "DNA helix",
        "medical cross", "molecule diagram literal",
    ],
    "tech": [
        "circuit board", "gear", "cog", "robot head",
        "brain icon", "cloud silhouette",
        "sparkles", "AI magic emoji", "rocket icon",
        "lightbulb idea",
    ],
    "ai": [
        "robot head", "brain icon", "neural network illustration",
        "sparkles", "magic wand", "AI emoji",
        "circuit board", "gear",
    ],
    "saas": [
        "gear icon", "cloud silhouette",
        "checkmark generic", "speech bubble",
    ],
    "eco": [
        "green leaf", "recycling triangle", "earth globe",
        "tree silhouette", "green gradient",
        "water drop", "sun rays literal",
    ],
    "sustainability": [
        "green leaf", "recycling triangle",
        "earth globe", "tree silhouette",
    ],
    "coffee": [
        "coffee cup", "coffee bean cliche", "mug", "steam spiral",
        "brown palette dominance", "latte art",
    ],
    "education": [
        "graduation cap", "open book", "owl",
        "lightbulb", "apple for teacher",
        "pencil crossed", "diploma scroll",
    ],
    "edtech": [
        "graduation cap", "open book", "owl",
        "lightbulb", "pencil",
    ],
    "restaurant": [
        "crossed fork knife", "chef hat",
        "cursive vintage script badge", "wooden chalk aesthetic",
        "circular emblem badge generic",
    ],
    "beauty": [
        "pastel pink dominant", "gold foil ornament",
        "lipstick silhouette", "mirror form",
        "watercolor splash", "flower wreath",
    ],
    "luxury": [
        "gold foil generic", "ornate flourish",
        "crown generic", "diamond cliche",
    ],
    "construction": [
        "crane", "hard hat yellow", "building silhouette",
        "hammer", "compass and ruler",
    ],
    "automotive": [
        "car silhouette", "speedometer", "wheel",
        "highway literal", "gas pump",
    ],
    "gaming": [
        "pixelated retro", "sword crossed", "neon cyberpunk generic",
        "glitch effect", "aggressive snarl mascot",
    ],
    "pediatrics": [
        "child and balloon", "pacifier", "baby bottle",
        "pastel blue pink gender coded",
        "teddy bear generic", "hand holding child hand",
    ],
}


# ============================================================================
# Model parameter presets
# ============================================================================

MODEL_PARAMS = {
    "midjourney": "--ar 1:1 --s 250 --v 7 --style raw",
    "midjourney-v8": "--ar 1:1 --s 300 --v 8 --style raw",
    "niji": "--ar 1:1 --s 200 --niji 7 --style raw",
    "flux": "",  # Flux uses different interface
    "dalle": "",
    "ideogram": "",
}


# ============================================================================
# Prompt composition
# ============================================================================

def compose_prompt(
    subject: str,
    logo_type: str,
    style_anchor: str,
    color: str,
    technical: Optional[str] = None,
    composition: Optional[str] = None,
    sector: Optional[str] = None,
    extra_negatives: Optional[List[str]] = None,
    model: str = "midjourney",
) -> str:
    """Compose a full structured prompt.

    Args:
        subject: Concrete metaphor ("letter C formed by two arcs...")
        logo_type: Category ("minimalist monogram", "abstract logomark")
        style_anchor: Designer/era refs, comma-sep ("Paul Rand,Sagi Haviv")
        color: Color spec ("deep indigo on pure white")
        technical: Optional override of default technical spec
        composition: Optional override of default composition spec
        sector: Sector key from SECTOR_NEGATIVES (adds negatives)
        extra_negatives: Extra --no items
        model: midjourney / niji / flux / dalle / ideogram

    Returns:
        Final prompt string with parameters and --no negatives.
    """
    # Default technical if none provided
    if technical is None:
        technical = (
            "purely flat 2D vector, single weight stroke, minimum nodes, "
            "SVGO optimized, clever negative space utilizing Gestalt principles"
        )

    # Default composition
    if composition is None:
        composition = (
            "centered, generous breathing room, "
            "isolated composition, scalable to 16px favicon"
        )

    # Anchor — convert comma list to "in the style of X and Y" format
    anchor_names = [s.strip() for s in style_anchor.split(",") if s.strip()]
    if len(anchor_names) == 1:
        anchor_text = f"in the style of {anchor_names[0]}"
    elif len(anchor_names) == 2:
        anchor_text = f"in the modernist tradition of {anchor_names[0]} and {anchor_names[1]}"
    elif len(anchor_names) >= 3:
        anchor_text = (
            f"in the tradition of {', '.join(anchor_names[:-1])}, and {anchor_names[-1]}"
        )
    else:
        anchor_text = "in the Logo Modernism tradition"

    # Compose positive prompt
    parts = [
        f"{logo_type} of {subject}",
        anchor_text,
        technical,
        color,
        composition,
    ]
    positive = ", ".join(parts)

    # Build negatives
    negatives = list(BASE_NEGATIVES)
    if sector:
        sector_key = sector.lower().replace("_", "-")
        if sector_key in SECTOR_NEGATIVES:
            negatives.extend(SECTOR_NEGATIVES[sector_key])
    if extra_negatives:
        negatives.extend(extra_negatives)

    # Dedupe
    negatives = list(dict.fromkeys(negatives))

    # Model-specific formatting
    if model in ("midjourney", "midjourney-v8", "niji"):
        params = MODEL_PARAMS[model]
        neg_str = ", ".join(negatives)
        return f"{positive} {params} --no {neg_str}"

    elif model == "flux":
        # Flux uses natural language + separate negative prompt
        neg_str = ", ".join(negatives)
        return (
            f"POSITIVE: {positive}, flat vector logo, high quality, "
            f"clean professional logo design\n\n"
            f"NEGATIVE: {neg_str}\n\n"
            f"SETTINGS: guidance_scale=3.5, steps=28 (dev) / 4 (schnell), "
            f"width=1024, height=1024"
        )

    elif model == "dalle":
        # DALL-E 3 prefers natural language, no parameters
        neg_description = "Do not include: " + ", ".join(negatives) + "."
        return (
            f"Create a logo design. {positive}. "
            f"The composition should feel like a professional brand identity mark "
            f"suitable for a modern company. {neg_description}"
        )

    elif model == "ideogram":
        # Ideogram is prompt+style-ref based
        neg_str = ", ".join(negatives)
        return (
            f"{positive}\n\n"
            f"Style: professional logo design, flat vector, brand identity\n"
            f"Negative: {neg_str}\n"
            f"Aspect ratio: 1:1"
        )

    else:
        raise ValueError(f"Unknown model: {model}")


# ============================================================================
# Interactive mode
# ============================================================================

def interactive_prompt() -> Dict[str, str]:
    """Guide user through prompt composition."""
    print("=" * 70)
    print(" brand-visual — Interactive Prompt Composer")
    print("=" * 70)
    print()

    def ask(question: str, default: Optional[str] = None) -> str:
        if default:
            prompt = f"{question}\n  [default: {default}]\n  > "
        else:
            prompt = f"{question}\n  > "
        response = input(prompt).strip()
        if not response and default:
            return default
        return response

    subject = ask(
        "1. SUBJECT/METAPHOR — Concrete visual metaphor\n"
        "   (e.g. 'letter C formed by two nested arcs suggesting curiosity')",
    )
    logo_type = ask(
        "2. LOGO TYPE — Category",
        default="minimalist abstract logomark",
    )
    style_anchor = ask(
        "3. STYLE ANCHOR — Designer/era refs (comma-separated)\n"
        "   (e.g. 'Paul Rand,Sagi Haviv,Swiss design tradition')",
        default="Paul Rand,Sagi Haviv",
    )
    color = ask(
        "4. COLOR — Palette spec",
        default="solid deep indigo on pure white background",
    )
    sector = ask(
        "5. SECTOR (optional) — Adds sector-specific negatives\n"
        "   (fintech/healthcare/tech/ai/coffee/education/real-estate/...)",
    )
    model = ask(
        "6. MODEL — midjourney / niji / flux / dalle / ideogram / all",
        default="midjourney",
    )
    print()

    return {
        "subject": subject,
        "logo_type": logo_type,
        "style_anchor": style_anchor,
        "color": color,
        "sector": sector or None,
        "model": model,
    }


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Compose AI image generation prompts for logo design.",
    )
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--subject", help="Subject/metaphor")
    parser.add_argument("--logo-type", default="minimalist abstract logomark")
    parser.add_argument("--style-anchor", default="Paul Rand,Sagi Haviv")
    parser.add_argument("--color", default="solid deep indigo on pure white background")
    parser.add_argument("--technical", default=None)
    parser.add_argument("--composition", default=None)
    parser.add_argument("--sector", default=None, help="Sector key for red-line negatives")
    parser.add_argument("--extra-negatives", nargs="*", help="Additional --no items")
    parser.add_argument(
        "--model",
        choices=["midjourney", "midjourney-v8", "niji", "flux", "dalle", "ideogram", "all"],
        default="midjourney",
    )

    args = parser.parse_args()

    if args.interactive:
        params = interactive_prompt()
        args.subject = params["subject"]
        args.logo_type = params["logo_type"]
        args.style_anchor = params["style_anchor"]
        args.color = params["color"]
        args.sector = params["sector"]
        args.model = params["model"]

    if not args.subject:
        print("ERROR: --subject is required (or use --interactive)", file=sys.stderr)
        sys.exit(1)

    # Generate for requested model(s)
    if args.model == "all":
        models = ["midjourney", "niji", "flux", "dalle", "ideogram"]
    else:
        models = [args.model]

    for i, model in enumerate(models):
        if i > 0:
            print("\n" + "=" * 70 + "\n")
        print(f"### {model.upper()} PROMPT\n")
        prompt = compose_prompt(
            subject=args.subject,
            logo_type=args.logo_type,
            style_anchor=args.style_anchor,
            color=args.color,
            technical=args.technical,
            composition=args.composition,
            sector=args.sector,
            extra_negatives=args.extra_negatives,
            model=model,
        )
        print(prompt)


if __name__ == "__main__":
    main()
