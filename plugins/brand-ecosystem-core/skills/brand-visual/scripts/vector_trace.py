#!/usr/bin/env python3
"""
vector_trace.py — Raster to SVG Conversion Wrapper

AI-generated raster (PNG/JPG) logos veya scanned sketches'i production-ready
SVG'ye çevirir. Multiple backend desteği: VTracer (önerilen), Inkscape Trace
Bitmap, Potrace.

Usage:
    python vector_trace.py logo.png
    python vector_trace.py logo.png --output logo.svg
    python vector_trace.py logo.png --backend vtracer --preset logo-color
    python vector_trace.py logo.png --backend inkscape --preset logo-mono
    python vector_trace.py logo.png --backend potrace --preset bw-clean
    python vector_trace.py logo.png --hierarchical cutout

Backends:
    vtracer (recommended) — Open-source Rust tool, color/spline support, O(n) algorithm
        Install: pip install vtracer  OR  cargo install vtracer
    inkscape — System install, Trace Bitmap dialog (CLI mode)
        Install: apt install inkscape  /  brew install inkscape
    potrace — Classic B/W only, monochrome line art
        Install: apt install potrace  /  brew install potrace
    auto — Otomatik backend seçimi (vtracer öncelikli; yoksa fallback)

Logo Presets:
    logo-color    — Renkli logo, 6-color palette, smooth splines (DEFAULT)
    logo-mono     — Tek-renk monogram, sharp corners
    bw-clean      — Saf siyah-beyaz, ince çizgi, posterized
    pixel-art     — Retro pixel art, sharp corners, integer coords
    sketch        — El-çizimi sketch'i smooth eden preset
    high-detail   — Çok detaylı illustration için, 16+ color palette

Output:
    SVG file + diagnostic report (path count, file size, simplification ratio)
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


# ============================================================================
# Backend detection
# ============================================================================

def detect_vtracer() -> Optional[str]:
    """Find vtracer executable. Returns path or None."""
    # Try Python package first
    try:
        import vtracer  # noqa: F401
        return "python:vtracer"
    except ImportError:
        pass
    # Try system binary
    return shutil.which("vtracer")


def detect_inkscape() -> Optional[str]:
    return shutil.which("inkscape")


def detect_potrace() -> Optional[str]:
    return shutil.which("potrace")


def detect_imagemagick() -> Optional[str]:
    """For pre-processing (PNG → PBM for Potrace)."""
    return shutil.which("magick") or shutil.which("convert")


def select_backend(requested: str) -> str:
    """Resolve 'auto' or validate explicit backend."""
    available = {
        "vtracer": detect_vtracer(),
        "inkscape": detect_inkscape(),
        "potrace": detect_potrace(),
    }
    if requested == "auto":
        for name in ["vtracer", "inkscape", "potrace"]:
            if available[name]:
                return name
        raise RuntimeError(
            "No vector tracing backend found. Install one of: vtracer, inkscape, potrace.\n"
            "  pip install vtracer\n"
            "  apt install inkscape\n"
            "  apt install potrace"
        )
    if not available[requested]:
        raise RuntimeError(
            f"Backend '{requested}' not available. "
            f"Install it or use --backend auto."
        )
    return requested


# ============================================================================
# Logo presets — parameter sets for different image types
# ============================================================================

VTRACER_PRESETS: Dict[str, Dict] = {
    # AI-generated colored logo (Midjourney/Niji output)
    "logo-color": {
        "color_mode": "color",
        "color_precision": 6,           # 6 bits per channel = 64 levels
        "filter_speckle": 4,            # discard tiny patches
        "gradient_step": 16,            # color difference threshold
        "corner_threshold": 60,         # corner detection sensitivity
        "segment_length": 4,            # path simplification
        "splice_threshold": 45,         # spline smoothing
        "hierarchical": "stacked",      # stacked = no holes (cleaner)
        "mode": "spline",
        "path_precision": 2,
    },
    # Single-color monogram, hard edges
    "logo-mono": {
        "color_mode": "binary",
        "filter_speckle": 4,
        "corner_threshold": 90,         # sharper corners
        "segment_length": 4,
        "splice_threshold": 30,
        "mode": "polygon",              # polygon for sharper edges
        "path_precision": 2,
    },
    # Black-white clean linework
    "bw-clean": {
        "color_mode": "binary",
        "filter_speckle": 8,            # more aggressive cleanup
        "corner_threshold": 75,
        "segment_length": 6,
        "splice_threshold": 45,
        "mode": "spline",
        "path_precision": 2,
    },
    # Pixel art preservation
    "pixel-art": {
        "color_mode": "color",
        "color_precision": 8,
        "filter_speckle": 0,            # no filtering (preserve pixels)
        "gradient_step": 0,
        "corner_threshold": 90,         # max corner preservation
        "segment_length": 1,
        "splice_threshold": 1,
        "mode": "pixel",
        "path_precision": 0,            # integer coords
    },
    # Sketch smoothing
    "sketch": {
        "color_mode": "binary",
        "filter_speckle": 2,
        "corner_threshold": 60,
        "segment_length": 8,            # heavier smoothing
        "splice_threshold": 60,
        "mode": "spline",
        "path_precision": 2,
    },
    # High-detail illustration (color mascot)
    "high-detail": {
        "color_mode": "color",
        "color_precision": 8,
        "filter_speckle": 2,
        "gradient_step": 8,             # finer gradient steps
        "corner_threshold": 60,
        "segment_length": 4,
        "splice_threshold": 45,
        "hierarchical": "stacked",
        "mode": "spline",
        "path_precision": 3,
    },
}


# ============================================================================
# VTracer backend
# ============================================================================

def run_vtracer(input_path: Path, output_path: Path, preset: str,
                hierarchical_override: Optional[str] = None) -> int:
    """Invoke vtracer (Python pkg or CLI binary)."""
    if preset not in VTRACER_PRESETS:
        raise ValueError(f"Unknown preset: {preset}. "
                         f"Available: {list(VTRACER_PRESETS.keys())}")
    params = VTRACER_PRESETS[preset].copy()
    if hierarchical_override:
        params["hierarchical"] = hierarchical_override

    # Try Python package first
    try:
        import vtracer
        # Map our preset keys to vtracer Python API param names
        # Real signature: colormode, hierarchical, mode, filter_speckle,
        #   color_precision, layer_difference, corner_threshold,
        #   length_threshold, max_iterations, splice_threshold, path_precision
        param_map = {
            "color_mode": "colormode",
            "color_precision": "color_precision",
            "filter_speckle": "filter_speckle",
            "gradient_step": "layer_difference",
            "corner_threshold": "corner_threshold",
            "segment_length": "length_threshold",
            "splice_threshold": "splice_threshold",
            "hierarchical": "hierarchical",
            "mode": "mode",
            "path_precision": "path_precision",
        }
        py_kwargs = {"image_path": str(input_path), "out_path": str(output_path)}
        for our_key, vt_key in param_map.items():
            if our_key in params:
                v = params[our_key]
                # vtracer wants float for length_threshold; int for others
                if vt_key == "length_threshold":
                    v = float(v)
                py_kwargs[vt_key] = v
        vtracer.convert_image_to_svg_py(**py_kwargs)
        return 0
    except ImportError:
        pass

    # Fall back to CLI binary
    binary = shutil.which("vtracer")
    if not binary:
        raise RuntimeError("vtracer not found")
    cmd = [binary, "--input", str(input_path), "--output", str(output_path)]
    for k, v in params.items():
        if k == "color_mode":
            cmd += ["--colormode", str(v)]
        elif k == "color_precision":
            cmd += ["-p", str(v)]
        elif k == "filter_speckle":
            cmd += ["-f", str(v)]
        elif k == "gradient_step":
            cmd += ["-g", str(v)]
        elif k == "corner_threshold":
            cmd += ["-c", str(v)]
        elif k == "segment_length":
            cmd += ["-l", str(v)]
        elif k == "splice_threshold":
            cmd += ["-s", str(v)]
        elif k == "hierarchical":
            cmd += ["--hierarchical", str(v)]
        elif k == "mode":
            cmd += ["-m", str(v)]
        elif k == "path_precision":
            cmd += ["--path_precision", str(v)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"vtracer stderr: {result.stderr}", file=sys.stderr)
    return result.returncode


# ============================================================================
# Inkscape backend
# ============================================================================

def run_inkscape(input_path: Path, output_path: Path, preset: str) -> int:
    """Invoke Inkscape CLI (Trace Bitmap)."""
    binary = shutil.which("inkscape")
    if not binary:
        raise RuntimeError("inkscape not found")

    # Inkscape CLI tracing requires a script approach.
    # For simplicity, we use the Action System (Inkscape 1.0+).
    actions = [
        f"file-open:{input_path}",
        "select-all",
    ]
    if preset in ("bw-clean", "logo-mono"):
        actions.append("trace-bitmap-brightness")  # B/W threshold
    else:
        actions.append("trace-bitmap-colors:6")     # 6-color tracing
    actions += [
        "delete-original-image",
        f"export-filename:{output_path}",
        "export-do",
    ]
    cmd = [binary, "--actions", ";".join(actions), "--batch-process"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"inkscape stderr: {result.stderr}", file=sys.stderr)
    return result.returncode


# ============================================================================
# Potrace backend
# ============================================================================

def run_potrace(input_path: Path, output_path: Path, preset: str) -> int:
    """Invoke potrace (B/W only — preprocess via ImageMagick)."""
    binary = shutil.which("potrace")
    if not binary:
        raise RuntimeError("potrace not found")
    magick = shutil.which("magick") or shutil.which("convert")
    if not magick:
        raise RuntimeError("ImageMagick required for potrace preprocessing")

    # Convert input to PBM (Portable Bitmap) — potrace's required input
    pbm_path = input_path.with_suffix(".pbm")
    threshold = "50%" if preset == "bw-clean" else "60%"
    pre = subprocess.run(
        [magick, str(input_path), "-colorspace", "Gray",
         "-threshold", threshold, str(pbm_path)],
        capture_output=True, text=True,
    )
    if pre.returncode != 0:
        print(f"ImageMagick preprocessing failed: {pre.stderr}", file=sys.stderr)
        return pre.returncode

    # Potrace parameters (preset-specific)
    if preset == "bw-clean":
        cmd = [binary, "-s", "--turdsize", "8", "--alphamax", "1.0",
               "-o", str(output_path), str(pbm_path)]
    elif preset == "sketch":
        cmd = [binary, "-s", "--turdsize", "2", "--alphamax", "1.3",
               "-o", str(output_path), str(pbm_path)]
    else:  # logo-mono default
        cmd = [binary, "-s", "--turdsize", "4", "--alphamax", "1.0",
               "-o", str(output_path), str(pbm_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    pbm_path.unlink(missing_ok=True)  # cleanup intermediate
    if result.returncode != 0:
        print(f"potrace stderr: {result.stderr}", file=sys.stderr)
    return result.returncode


# ============================================================================
# Diagnostic report
# ============================================================================

def diagnose_svg(svg_path: Path) -> Dict:
    """Quick diagnostic: file size, path count, complexity heuristic."""
    if not svg_path.exists():
        return {"error": "SVG not generated"}

    content = svg_path.read_text(encoding="utf-8", errors="ignore")
    file_size = svg_path.stat().st_size
    path_count = content.count("<path")
    # Estimate node count by counting "M" + "L" + "C" + "Z" commands
    node_count = sum(content.count(c) for c in ["M ", "L ", "C ", "Z"])

    return {
        "file_size_bytes": file_size,
        "file_size_kb": round(file_size / 1024, 1),
        "path_count": path_count,
        "approx_node_count": node_count,
        "complexity": (
            "simple" if node_count < 50
            else "moderate" if node_count < 200
            else "complex" if node_count < 1000
            else "very-complex (consider simplification)"
        ),
    }


def post_process_recommendations(diag: Dict, preset: str) -> List[str]:
    """Generate actionable post-processing recommendations."""
    recs = []
    if diag.get("approx_node_count", 0) > 500:
        recs.append("⚠ High node count — consider running through SVGO "
                    "(`npx svgo file.svg --multipass`)")
    if diag.get("path_count", 0) > 20:
        recs.append("⚠ Many paths — consider Inkscape 'Path > Simplify' "
                    "(Ctrl+L) before final delivery")
    if preset == "logo-color" and diag.get("file_size_kb", 0) > 50:
        recs.append("⚠ Large file size for a logo — likely too many color stops; "
                    "consider --backend vtracer with reduced --color_precision")
    if not recs:
        recs.append("✓ SVG looks clean — proceed to manual cleanup pass in "
                    "Adobe Illustrator or Figma for production refinement")
    recs.append("→ ALWAYS recommend: human designer manual cleanup pass before "
                "production deployment (anchor point optimization, optical "
                "alignment, kerning if logotype)")
    return recs


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Convert raster logo (PNG/JPG) to clean SVG.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", type=Path, help="Input raster file (PNG/JPG)")
    parser.add_argument("--output", "-o", type=Path,
                        help="Output SVG path (default: <input>.svg)")
    parser.add_argument("--backend",
                        choices=["auto", "vtracer", "inkscape", "potrace"],
                        default="auto", help="Tracing backend (default: auto)")
    parser.add_argument("--preset",
                        choices=list(VTRACER_PRESETS.keys()),
                        default="logo-color",
                        help="Logo preset (default: logo-color)")
    parser.add_argument("--hierarchical",
                        choices=["stacked", "cutout"], default=None,
                        help="VTracer hierarchical mode (default: stacked)")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: Input not found: {args.input}", file=sys.stderr)
        return 1

    output = args.output or args.input.with_suffix(".svg")

    try:
        backend = select_backend(args.backend)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"Backend: {backend}")
    print(f"Preset: {args.preset}")
    print(f"Input: {args.input}")
    print(f"Output: {output}")
    print()

    # Run conversion
    if backend == "vtracer":
        rc = run_vtracer(args.input, output, args.preset, args.hierarchical)
    elif backend == "inkscape":
        rc = run_inkscape(args.input, output, args.preset)
    elif backend == "potrace":
        rc = run_potrace(args.input, output, args.preset)
    else:
        print(f"ERROR: Unknown backend: {backend}", file=sys.stderr)
        return 1

    if rc != 0:
        print(f"ERROR: Conversion failed (return code {rc})", file=sys.stderr)
        return rc

    # Diagnose result
    diag = diagnose_svg(output)
    print("=" * 60)
    print("Conversion result:")
    print("=" * 60)
    for k, v in diag.items():
        print(f"  {k}: {v}")
    print()
    print("Post-processing recommendations:")
    for rec in post_process_recommendations(diag, args.preset):
        print(f"  {rec}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
