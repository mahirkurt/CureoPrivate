#!/usr/bin/env python3
"""
favicon_simulator.py — Logo Scalability Verification

Bir logo (SVG veya raster PNG/JPG) dosyasını favicon ve app-icon boyutlarında
(16/32/64/192/512) render eder ve tanınabilirlik kontrol listesini üretir.
Monokrom varyant oluşturur, kontrast testi uygular.

Usage:
    python favicon_simulator.py logo.svg
    python favicon_simulator.py logo.png --output-dir ./favicon-test/
    python favicon_simulator.py logo.svg --sizes 16,32,64,192
    python favicon_simulator.py logo.svg --skip-mono

Dependencies:
    Standart input SVG/PNG için Pillow gerekli. Eğer yoksa, mental-simulation
    checklist moduna düşer (dependency-free).

    pip install Pillow CairoSVG  # SVG render için
    # Veya sadece Pillow (PNG input için)

Çıktılar:
    <output-dir>/
    ├── logo-16.png          (favicon 16×16)
    ├── logo-32.png          (favicon 32×32)
    ├── logo-64.png          (app icon small)
    ├── logo-192.png         (PWA icon)
    ├── logo-512.png         (master)
    ├── logo-16-mono.png     (monokrom varyant)
    ├── logo-32-mono.png
    ├── report.md            (tanınabilirlik raporu)

Test kriterleri:
    - Silhouette tanınabilirliği (16px)
    - Detay korunumu (32px)
    - Stroke kalınlığı (tek-stroke ise < 1.5px 16px'te kaybolur)
    - Monokrom çalışırlık
    - Kenar netliği (aliasing riski)
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

DEFAULT_SIZES = [16, 32, 64, 128, 192, 512]


# ============================================================================
# Dependency detection
# ============================================================================

def has_pillow() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def has_cairosvg() -> bool:
    try:
        import cairosvg  # noqa: F401
        return True
    except ImportError:
        return False


# ============================================================================
# SVG rasterization
# ============================================================================

def rasterize_svg(svg_path: Path, size: int, out_path: Path) -> bool:
    """Render SVG to PNG at given size. Returns success."""
    if has_cairosvg():
        import cairosvg
        try:
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(out_path),
                output_width=size,
                output_height=size,
            )
            return True
        except Exception as e:
            print(f"  [WARN] CairoSVG failed: {e}", file=sys.stderr)

    # Fallback: try rsvg-convert (system binary)
    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        import subprocess
        try:
            subprocess.run(
                [rsvg, "-w", str(size), "-h", str(size),
                 "-o", str(out_path), str(svg_path)],
                check=True, capture_output=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"  [WARN] rsvg-convert failed: {e}", file=sys.stderr)

    # Fallback: try ImageMagick
    magick = shutil.which("magick") or shutil.which("convert")
    if magick:
        import subprocess
        try:
            subprocess.run(
                [magick, "-background", "none", "-density", "300",
                 str(svg_path), "-resize", f"{size}x{size}",
                 str(out_path)],
                check=True, capture_output=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"  [WARN] ImageMagick failed: {e}", file=sys.stderr)

    return False


# ============================================================================
# Raster resampling
# ============================================================================

def resample_raster(in_path: Path, size: int, out_path: Path) -> bool:
    if not has_pillow():
        return False
    from PIL import Image
    try:
        im = Image.open(in_path).convert("RGBA")
        im_resized = im.resize((size, size), Image.LANCZOS)
        im_resized.save(out_path, "PNG")
        return True
    except Exception as e:
        print(f"  [WARN] Pillow resample failed: {e}", file=sys.stderr)
        return False


# ============================================================================
# Monochrome conversion
# ============================================================================

def make_monochrome(in_path: Path, out_path: Path) -> bool:
    if not has_pillow():
        return False
    from PIL import Image
    try:
        im = Image.open(in_path).convert("RGBA")
        # Luminance-based threshold
        grayscale = im.convert("L")
        # Keep alpha channel
        r, g, b, a = im.split() if im.mode == "RGBA" else (None,) * 4
        threshold_applied = grayscale.point(lambda p: 0 if p < 128 else 255)
        mono = Image.new("RGBA", im.size, (0, 0, 0, 0))
        mono_rgb = Image.new("RGB", im.size, (0, 0, 0))
        mono.paste(mono_rgb, mask=threshold_applied.point(lambda p: 255 - p))
        if a:
            mono.putalpha(a)
        mono.save(out_path, "PNG")
        return True
    except Exception as e:
        print(f"  [WARN] Monochrome conversion failed: {e}", file=sys.stderr)
        return False


# ============================================================================
# Report generation
# ============================================================================

MENTAL_SIMULATION_CHECKLIST = """
## Mental Simulation Checklist — brand-visual 5-Test Protocol

Her render'ı görsel olarak incele ve bu 5 testten geçip geçmediğini işaretle:

### Test 1: 16px Silhouette Recognition
- [ ] 16×16 rendere bak — logonun **silhouette'i tanınabilir** mi?
- [ ] Detaylar kaybolsa bile ana form korunuyor mu?
- [ ] **FAIL**: Logo 16px'te tanınmıyor → simplify et (düğüm azalt / tek-renk yap)

### Test 2: 32px Detail Preservation
- [ ] 32×32 rendere bak — detaylar **ayırt edilebilir** mi?
- [ ] İnce strokelar kaybolmuş mu?
- [ ] **FAIL**: Stroke kalınlığı orantısız → stroke weight artır

### Test 3: Monochrome Viability
- [ ] Monokrom siyah-beyaz varyant güçlü mü?
- [ ] Ters (beyaz-on-siyah) de çalışıyor mu?
- [ ] **FAIL**: Renk olmadan yapı çökmüş → logo renge bağımlı, form yeniden düşün

### Test 4: Rotational Balance (opsiyonel)
- [ ] 90°/180° döndürsek hâlâ balanced mi?
- [ ] (Zorunlu değil; bazı logoları "directional" olmalı — ama test bilgi verir)

### Test 5: Phone Call Test
- [ ] Birisine telefonla tarif etsen çizebilir mi? (Nike swoosh testi)
- [ ] **FAIL**: Tarif edilmiyor → çok karmaşık, bir öz formu var mı?

### Test 6 (Bonus): 5-Second Memory Test
- [ ] 5 saniye bak, 1 dakika beklet, tekrar çiz. **Çizilebilir mi?**
- [ ] **FAIL**: Memorability zayıf → ikonik bir element mi eksik?

### Sonuç
- **6 testten ≥5'i PASS** → Logo production'a uygun
- **4 ya da daha az PASS** → iterasyon gerekli, Adım 3'e veya Adım 4'e geri dön
"""


def generate_report(
    logo_path: Path,
    out_dir: Path,
    sizes: List[int],
    has_rendered: List[int],
    has_mono: bool,
) -> str:
    """Build a markdown report."""
    lines = [
        f"# Favicon & App-Icon Scalability Test Report",
        f"",
        f"**Source**: `{logo_path.name}`",
        f"**Output directory**: `{out_dir}`",
        f"",
        f"## Rendered Sizes",
        f"",
        f"| Size | Render File | Use Case |",
        f"|------|-------------|----------|",
    ]

    use_cases = {
        16: "Browser tab favicon",
        32: "Retina favicon / shortcut icon",
        64: "Mac Dock small / Windows task bar",
        128: "Chrome extension icon",
        192: "PWA home screen icon (Android)",
        512: "PWA splash master / app icon master",
    }

    for size in sizes:
        if size in has_rendered:
            filename = f"{logo_path.stem}-{size}.png"
            use = use_cases.get(size, f"{size}px use")
            lines.append(f"| {size}×{size} | `{filename}` | {use} |")
        else:
            use = use_cases.get(size, f"{size}px use")
            lines.append(f"| {size}×{size} | ⚠ NOT RENDERED | {use} |")

    lines.append("")

    if has_mono:
        lines.append("## Monochrome Variants")
        lines.append("")
        lines.append("| Size | File |")
        lines.append("|------|------|")
        for size in sizes:
            if size in has_rendered:
                filename = f"{logo_path.stem}-{size}-mono.png"
                lines.append(f"| {size}×{size} | `{filename}` |")
        lines.append("")

    lines.append(MENTAL_SIMULATION_CHECKLIST)

    lines.append("")
    lines.append("## External Validation Tools (Recommended)")
    lines.append("")
    lines.append(
        "- **Real Favicon Generator** — https://realfavicongenerator.net "
        "(tüm platform varyasyonları + PWA manifest)"
    )
    lines.append(
        "- **Favicon Checker** — https://www.favicon-checker.com "
        "(browser tab render preview)"
    )
    lines.append(
        "- **Maskable.app Editor** — https://maskable.app/editor "
        "(Android adaptive icon safe area test)"
    )
    lines.append(
        "- **App Icon Preview (iOS)** — https://appicon.co "
        "(iOS icon grid ve dock preview)"
    )

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Render logo at favicon/app-icon sizes and generate test report.",
    )
    parser.add_argument("logo", type=Path, nargs="?", help="Source logo file (SVG/PNG/JPG)")
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=None,
        help="Output directory (default: ./<logo-name>-favicon-test/)",
    )
    parser.add_argument(
        "--sizes",
        type=lambda s: [int(x) for x in s.split(",")],
        default=DEFAULT_SIZES,
        help="Comma-separated sizes (default: 16,32,64,128,192,512)",
    )
    parser.add_argument(
        "--skip-mono",
        action="store_true",
        help="Skip monochrome variant generation",
    )
    parser.add_argument(
        "--checklist-only",
        action="store_true",
        help="Skip rendering, just output the mental-simulation checklist",
    )

    args = parser.parse_args()

    if args.checklist_only:
        print(MENTAL_SIMULATION_CHECKLIST)
        return 0

    if args.logo is None:
        print("ERROR: logo argument required (or use --checklist-only)", file=sys.stderr)
        return 1

    if not args.logo.exists():
        print(f"ERROR: Logo file not found: {args.logo}", file=sys.stderr)
        return 1

    out_dir = args.output_dir or Path(f"./{args.logo.stem}-favicon-test")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Source: {args.logo}")
    print(f"Output: {out_dir}")
    print(f"Sizes: {args.sizes}")
    print()

    # Determine rendering strategy
    is_svg = args.logo.suffix.lower() == ".svg"
    is_raster = args.logo.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")

    if is_svg and not (has_cairosvg() or shutil.which("rsvg-convert") or shutil.which("magick")):
        print(
            "[INFO] No SVG renderer available. Falling back to checklist-only.\n"
            "       Install one of:\n"
            "         pip install cairosvg\n"
            "         apt install librsvg2-bin  (rsvg-convert)\n"
            "         apt install imagemagick\n",
            file=sys.stderr,
        )
        print(MENTAL_SIMULATION_CHECKLIST)
        # Write just the checklist as a report
        (out_dir / "report.md").write_text(
            generate_report(args.logo, out_dir, args.sizes, [], False)
        )
        return 0

    if is_raster and not has_pillow():
        print(
            "[INFO] Pillow not installed. Falling back to checklist-only.\n"
            "       Install: pip install Pillow\n",
            file=sys.stderr,
        )
        print(MENTAL_SIMULATION_CHECKLIST)
        (out_dir / "report.md").write_text(
            generate_report(args.logo, out_dir, args.sizes, [], False)
        )
        return 0

    # Render each size
    rendered_sizes = []
    for size in args.sizes:
        out_path = out_dir / f"{args.logo.stem}-{size}.png"
        print(f"  Rendering {size}×{size}... ", end="", flush=True)
        ok = False
        if is_svg:
            ok = rasterize_svg(args.logo, size, out_path)
        elif is_raster:
            ok = resample_raster(args.logo, size, out_path)
        if ok:
            rendered_sizes.append(size)
            print("✓")
        else:
            print("✗")

    # Monochrome variants
    mono_rendered = False
    if not args.skip_mono and has_pillow():
        print()
        print("Generating monochrome variants...")
        for size in rendered_sizes:
            src = out_dir / f"{args.logo.stem}-{size}.png"
            dst = out_dir / f"{args.logo.stem}-{size}-mono.png"
            print(f"  Mono {size}×{size}... ", end="", flush=True)
            if make_monochrome(src, dst):
                print("✓")
                mono_rendered = True
            else:
                print("✗")

    # Report
    report = generate_report(args.logo, out_dir, args.sizes, rendered_sizes, mono_rendered)
    report_path = out_dir / "report.md"
    report_path.write_text(report)

    print()
    print("=" * 60)
    print(f"  Report written: {report_path}")
    print(f"  Rendered sizes: {rendered_sizes}")
    print("=" * 60)
    print()
    print("Next step: open report.md and walk through the 5-Test Protocol.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
