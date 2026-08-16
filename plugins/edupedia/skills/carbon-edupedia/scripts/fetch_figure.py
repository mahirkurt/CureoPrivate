#!/usr/bin/env python3
"""Tier-2 figür gömücü — ders kitabı görselini modüle base64 olarak yerleştirir.

NEDEN BU SCRIPT VAR (kök neden, 2026-07-31 ampirik olarak ölçüldü)
-------------------------------------------------------------------
`get_figure(figure_id, include_image=true)` görseli **MCP ImageContent** olarak
döndürür. Model o görseli GÖRÜR, ama base64'ünü **metin olarak ALMAZ** — harness
onu bir görüntüye çevirir ve JSON gövdesinde `data`/`base64` alanı yoktur. Binary
veriyi token token yeniden üretmek mümkün olmadığından, **gömmeyi model yapamaz.**

Dokümantasyon uzun süre "Tier-2 = base64 göm" diyerek modelden yapısal olarak
imkânsız bir şey istedi. Gerçek yol şudur: metadata'daki `pdf_url` + `page_no` +
`bbox` üçlüsü figürü **birebir** yeniden çıkarmaya yeter. Bu script onu yapar.

AKIŞ
----
1. Model, MODULE_DATA'ya motorun görmezden geldiği bir `figures` bloğu yazar
   (`curriculum` / `exam` bloklarıyla aynı desen) ve görselin geleceği yere
   `@@FIG:<key>@@` yer tutucusunu koyar:

       figures: {
         f1: { figureId: 6448, pdfUrl: "https://tymm.meb.gov.tr/...pdf", page: 80,
               bbox: [137.1, 325.4, 253.0, 442.4],
               caption: "Bitki hücresi kesiti",
               alt: "Hücre duvarı, çekirdek ve kloroplastları gösteren kesit" } }
       ...
       { type:"teach", id:"t1", visual:{ kind:"svg", ref:"@@FIG:f1@@" } }

2. Bu script PDF'i (kitap başına bir kez) çözer, bbox'ı kırpar, JPEG'e sıkıştırır
   ve yer tutucuyu erişilebilir bir <svg><image href="data:..."></svg> ile değiştirir.

MOTOR DEĞİŞMEZ: `visual.kind:"svg"` zaten keyfi SVG kabul eder (svgFigure(ref)).

DEGRADE SÖZLEŞMESİ: hiçbir hata üretimi bloke etmez. PDF inilemezse, sayfa/bbox
tutmazsa veya anahtar bilinmiyorsa **yer tutucu yerinde kalır** (sessizce silinmez)
ve rapora düşer — Tier-1 yazar-SVG yolu her zaman geçerlidir.

KULLANIM
    python3 fetch_figure.py <modul.html> [--in-place] [--scale 2.0] [--quality 85]
    python3 fetch_figure.py <modul.html> --json     # yalnız rapor
"""
import argparse
import base64
import html as _html
import io
import json
import os
import re
import sys
import tempfile
import urllib.request

DEFAULT_SCALE = 2.0
DEFAULT_QUALITY = 85
PLACEHOLDER_RE = re.compile(r"@@FIG:([A-Za-z0-9_-]+)@@")
DOWNLOAD_TIMEOUT = 180
# Cloudflare/bot kuralları urllib'in varsayılan UA'sını 403 ile karşılayabiliyor
# (edupedia yayın istemcilerinde ölçülmüş davranış) — açık UA gönderiyoruz.
USER_AGENT = "edupedia-fetch-figure/1.0 (+https://cureonics.com)"


class FigureError(Exception):
    """Figür çıkarılamadı — çağıran Tier-1'e düşer, üretim bloke olmaz."""


# ---------------------------------------------------------------- ayrıştırma

def _slice_bracketed(text, start_idx, open_ch="{", close_ch="}"):
    """Eşleşen kapanışa kadar iç dilim. validate_module.py'deki ikizi ile aynı
    sözleşme (string içi parantez sayılmaz — salt-metin heuristiği)."""
    depth = 0
    for i in range(start_idx, len(text)):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                return text[start_idx + 1:i]
    return ""


def _parse_bbox(raw):
    nums = re.findall(r"-?\d+(?:\.\d+)?", raw)
    if len(nums) != 4:
        raise FigureError(f"bbox 4 sayı olmalı, {len(nums)} bulundu: {raw!r}")
    return [float(n) for n in nums]


def parse_figures_block(html):
    """MODULE_DATA'daki `figures` bloğunu {key: {...}} sözlüğüne çevirir.

    Salt-metin ayrıştırma (JS nesnesi parse EDİLMEZ) — validate_module.py'nin
    kapılarıyla aynı sınır. Blok yoksa boş sözlük döner.
    """
    m = re.search(r"\bfigures\s*:\s*\{", html)
    if not m:
        return {}
    block = _slice_bracketed(html, m.end() - 1)
    out = {}
    for em in re.finditer(r"([A-Za-z0-9_-]+)\s*:\s*\{", block):
        key = em.group(1)
        entry = _slice_bracketed(block, em.end() - 1)
        if not entry:
            continue
        rec = {}
        fid = re.search(r"\bfigureId\s*:\s*(\d+)", entry)
        page = re.search(r"\bpage\s*:\s*(\d+)", entry)
        url = re.search(r"\bpdfUrl\s*:\s*[\"']([^\"']+)[\"']", entry)
        bbox = re.search(r"\bbbox\s*:\s*\[([^\]]*)\]", entry)
        # Sonlandırıcı ARANMAZ: `_slice_bracketed` kapanış `}`'yi dilimin dışında
        # bıraktığı için, girdinin SON alanının ardında ne virgül ne süslü parantez
        # kalır — sonlandırıcı arayan bir desen o alanı sessizce ıskalar (alt için
        # ölçüldü). Non-greedy grup zaten ilk kapanış tırnağında durur.
        cap = re.search(r"\bcaption\s*:\s*[\"'](.*?)[\"']", entry, re.S)
        alt = re.search(r"\balt\s*:\s*[\"'](.*?)[\"']", entry, re.S)
        if fid:
            rec["figureId"] = int(fid.group(1))
        if page:
            rec["page"] = int(page.group(1))
        if url:
            rec["pdfUrl"] = url.group(1)
        if bbox:
            try:
                rec["bbox"] = _parse_bbox(bbox.group(1))
            except FigureError:
                pass
        rec["caption"] = cap.group(1) if cap else ""
        rec["alt"] = alt.group(1) if alt else rec.get("caption", "")
        out[key] = rec
    return out


# ------------------------------------------------------------------ çıkarma

def render_figure(pdf_path, page, bbox, scale=DEFAULT_SCALE, quality=DEFAULT_QUALITY):
    """PDF'in `page` sayfasından `bbox` bölgesini kırpıp JPEG bayt döndürür.

    Döndürür: (jpeg_bytes, width_px, height_px). `page` 1-tabanlıdır
    (get_figure'ın page_no alanıyla aynı taban).

    JPEG tercihi ölçümle geldi: aynı figür PNG 3x'te 171 KB base64, JPEG 2x q85'te
    15 KB — modül dosyası tek-dosya olduğu için bu fark belirleyicidir.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise FigureError(
            "PyMuPDF (fitz) kurulu değil; Tier-2 gömme yapılamaz → Tier-1'de kalın"
        ) from e
    try:
        from PIL import Image
    except ImportError as e:
        raise FigureError("Pillow kurulu değil; JPEG sıkıştırma yapılamaz") from e

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise FigureError(f"PDF açılamadı: {e}") from e
    try:
        if not (1 <= page <= doc.page_count):
            raise FigureError(
                f"sayfa {page} aralık dışı (belge {doc.page_count} sayfa)")
        rect = fitz.Rect(*bbox)
        if rect.is_empty or rect.is_infinite:
            raise FigureError(f"bbox geçersiz/boş: {bbox}")
        pix = doc[page - 1].get_pixmap(clip=rect, matrix=fitz.Matrix(scale, scale))
        if not pix.width or not pix.height:
            raise FigureError("kırpım boş piksel üretti (bbox sayfa dışında olabilir)")
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=quality, optimize=True)
        return buf.getvalue(), pix.width, pix.height
    finally:
        doc.close()


def svg_wrapper(b64, mime, width, height, caption="", alt=""):
    """base64 görseli erişilebilir, tema-nötr bir SVG'ye sarar.

    role="img" + <title> G-SVG'nin erişilebilirlik koşulunu karşılar. Token
    renk yoktur (raster görselin rengi kendisindedir) — G-SVG bunu WARN olarak
    bildirir, FAIL değil.
    """
    title = _html.escape(alt or caption or "Şekil", quote=True)
    return (
        f'<svg class="viz-figure" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{title}" preserveAspectRatio="xMidYMid meet">'
        f"<title>{title}</title>"
        f'<image href="data:{mime};base64,{b64}" '
        f'width="{width}" height="{height}"/>'
        f"</svg>"
    )


def _default_resolver(cache_dir=None):
    """URL → yerel PDF yolu; kitap başına BİR kez indirir (dosyalar ~20 MB)."""
    cache_dir = cache_dir or os.path.join(
        tempfile.gettempdir(), "edupedia-figure-cache")
    os.makedirs(cache_dir, exist_ok=True)

    def resolve(url):
        name = re.sub(r"[^A-Za-z0-9._-]", "_", url.split("/")[-1]) or "kitap.pdf"
        path = os.path.join(cache_dir, name)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as r, \
                    open(path, "wb") as f:
                f.write(r.read())
        except Exception as e:
            if os.path.exists(path):
                os.unlink(path)
            raise FigureError(f"PDF indirilemedi ({url}): {e}") from e
        return path

    return resolve


# -------------------------------------------------------------------- gömme

def embed_figures(html, resolve_pdf=None, scale=DEFAULT_SCALE,
                  quality=DEFAULT_QUALITY):
    """`@@FIG:<key>@@` yer tutucularını gömülü görselle değiştirir.

    Döndürür: (yeni_html, rapor). Rapor: {"embedded": [key...],
    "failed": [(key, sebep)...], "bytes": {key: base64_uzunluk}}.

    Hiçbir hata istisna fırlatmaz — başarısız yer tutucu **yerinde bırakılır**
    (sessiz silme yok) ve rapora düşer. Üretim asla bloke olmaz.
    """
    report = {"embedded": [], "failed": [], "bytes": {}}
    keys = PLACEHOLDER_RE.findall(html)
    if not keys:
        return html, report

    figures = parse_figures_block(html)
    resolve_pdf = resolve_pdf or _default_resolver()
    pdf_cache = {}
    rendered = {}

    for key in dict.fromkeys(keys):          # sıra korunur, tekrar elenir
        spec = figures.get(key)
        if not spec:
            report["failed"].append((key, "figures bloğunda böyle bir anahtar yok"))
            continue
        missing = [f for f in ("pdfUrl", "page", "bbox") if f not in spec]
        if missing:
            report["failed"].append((key, "eksik alan: " + ", ".join(missing)))
            continue
        try:
            url = spec["pdfUrl"]
            if url not in pdf_cache:
                pdf_cache[url] = resolve_pdf(url)
            data, w, h = render_figure(pdf_cache[url], spec["page"], spec["bbox"],
                                       scale=scale, quality=quality)
            b64 = base64.b64encode(data).decode("ascii")
            rendered[key] = svg_wrapper(b64, "image/jpeg", w, h,
                                        caption=spec.get("caption", ""),
                                        alt=spec.get("alt", ""))
            report["embedded"].append(key)
            report["bytes"][key] = len(b64)
        except FigureError as e:
            report["failed"].append((key, str(e)))
        except Exception as e:                # beklenmedik — yine degrade et
            report["failed"].append((key, f"beklenmedik hata: {e}"))

    if rendered:
        html = PLACEHOLDER_RE.sub(
            lambda m: rendered.get(m.group(1), m.group(0)), html)
    return html, report


def main():
    ap = argparse.ArgumentParser(
        description="Tier-2 ders kitabı figürünü modüle gömer "
                    "(@@FIG:<key>@@ yer tutucuları)")
    ap.add_argument("html", help="modül HTML dosyası")
    ap.add_argument("--in-place", action="store_true",
                    help="dosyayı yerinde güncelle (yoksa stdout'a yazar)")
    ap.add_argument("--scale", type=float, default=DEFAULT_SCALE,
                    help=f"kırpım ölçeği (varsayılan {DEFAULT_SCALE})")
    ap.add_argument("--quality", type=int, default=DEFAULT_QUALITY,
                    help=f"JPEG kalitesi (varsayılan {DEFAULT_QUALITY})")
    ap.add_argument("--json", action="store_true",
                    help="stdout'a yalnız rapor JSON'u bas (HTML yazma)")
    args = ap.parse_args()

    try:
        src = open(args.html, encoding="utf-8").read()
    except OSError as e:
        print(json.dumps({"error": f"Dosya okunamadı: {e}"}, ensure_ascii=False)
              if args.json else f"Dosya okunamadı: {e}", file=sys.stderr)
        sys.exit(2)

    out, report = embed_figures(src, scale=args.scale, quality=args.quality)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.in_place:
        open(args.html, "w", encoding="utf-8").write(out)
        n_kb = sum(report["bytes"].values()) // 1024
        print(f"Gömülen: {len(report['embedded'])} figür (~{n_kb} KB base64)")
        for key, why in report["failed"]:
            print(f"  ATLANDI {key}: {why} — yer tutucu yerinde bırakıldı "
                  "(Tier-1 yazar-SVG ile doldurun)")
    else:
        sys.stdout.write(out)

    # Başarısız figür üretimi bloke ETMEZ; çıkış kodu yine 0.
    sys.exit(0)


if __name__ == "__main__":
    main()
