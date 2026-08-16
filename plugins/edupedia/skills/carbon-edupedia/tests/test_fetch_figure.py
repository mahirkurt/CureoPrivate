# tests/test_fetch_figure.py — Tier-2 figür gömücü testleri
#
# Ağ YOK: PDF'ler testin içinde PyMuPDF ile üretilir. Gerçek ders kitabı indirme
# yolu (resolve_pdf) bir seam ile enjekte edilir, böylece kırpma/gömme mantığı
# upstream'e bağımlı olmadan test edilir.
import sys, os, base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import fetch_figure as ff

import pytest

fitz = pytest.importorskip("fitz", reason="PyMuPDF yok — Tier-2 gömme kullanılamaz")


def _make_pdf(tmp_path, pages=1):
    """Icinde bilinen bir dikdortgen olan kucuk bir test PDF'i uretir."""
    doc = fitz.open()
    for _ in range(pages):
        page = doc.new_page(width=300, height=400)
        page.draw_rect(fitz.Rect(50, 100, 150, 200), color=(1, 0, 0), fill=(1, 0, 0))
    p = tmp_path / "test.pdf"
    doc.save(str(p))
    return str(p)


HTML_WITH_FIGURES = '''<html lang="tr"><body><script>
const MODULE_DATA = {
  meta: { title: "Test", mode: "CURRICULUM" },
  figures: {
    f1: { figureId: 6448, pdfUrl: "https://example.invalid/kitap.pdf", page: 1,
          bbox: [50, 100, 150, 200],
          caption: "Bitki hucresi kesiti",
          alt: "Hucre duvari, cekirdek ve kloroplastlari gosteren kesit cizimi" }
  },
  segments: [
    { type: "teach", id: "t1", title: "Hucre",
      visual: { kind: "svg", ref: "@@FIG:f1@@" } }
  ]
};
</script></body></html>'''


def test_parse_figures_block_reads_all_fields():
    figs = ff.parse_figures_block(HTML_WITH_FIGURES)
    assert set(figs) == {"f1"}
    f = figs["f1"]
    assert f["figureId"] == 6448
    assert f["page"] == 1
    assert f["bbox"] == [50.0, 100.0, 150.0, 200.0]
    assert f["caption"] == "Bitki hucresi kesiti"
    assert f["alt"].startswith("Hucre duvari")


def test_parse_figures_block_absent_returns_empty():
    assert ff.parse_figures_block("<html><body>hic figures yok</body></html>") == {}


def test_render_figure_produces_jpeg_of_the_clip(tmp_path):
    pdf = _make_pdf(tmp_path)
    data, w, h = ff.render_figure(pdf, page=1, bbox=[50, 100, 150, 200])
    assert data[:2] == b"\xff\xd8", "JPEG SOI imzasi bekleniyor"
    # 100x100 pt kirpim, varsayilan 2x olcek -> ~200x200 px
    assert 150 <= w <= 250 and 150 <= h <= 250, (w, h)


def test_render_figure_rejects_out_of_range_page(tmp_path):
    pdf = _make_pdf(tmp_path, pages=1)
    with pytest.raises(ff.FigureError) as e:
        ff.render_figure(pdf, page=99, bbox=[0, 0, 10, 10])
    assert "sayfa" in str(e.value).lower()


def test_svg_wrapper_is_accessible_and_self_contained():
    svg = ff.svg_wrapper("QUJD", "image/jpeg", 200, 150,
                         caption="Baslik", alt="Erisilebilir aciklama")
    assert 'role="img"' in svg
    assert "<title>Erisilebilir aciklama</title>" in svg
    assert 'href="data:image/jpeg;base64,QUJD"' in svg
    assert 'viewBox="0 0 200 150"' in svg
    # harici bagimlilik yok
    assert "http://" not in svg and "https://" not in svg


def test_svg_wrapper_escapes_alt_text():
    svg = ff.svg_wrapper("QQ==", "image/jpeg", 10, 10, caption="c", alt='a<b>&"x"')
    assert "<b>" not in svg
    assert "&lt;b&gt;" in svg


def test_svg_wrapper_default_alt_is_not_textbook_deixis():
    """Boş alt/caption 'Ders kitabı görseli' yazmamalı — o öğrenci yüzeyine sızan meta-atıftır."""
    svg = ff.svg_wrapper("QQ==", "image/jpeg", 10, 10)
    assert "ders kitab" not in svg.casefold()
    assert "Şekil" in svg


def test_embed_figures_replaces_placeholder(tmp_path):
    pdf = _make_pdf(tmp_path)
    out, report = ff.embed_figures(HTML_WITH_FIGURES, resolve_pdf=lambda url: pdf)
    assert "@@FIG:f1@@" not in out
    assert "data:image/jpeg;base64," in out
    assert report["embedded"] == ["f1"]
    assert report["failed"] == []


def test_embed_figures_is_noop_without_placeholder(tmp_path):
    pdf = _make_pdf(tmp_path)
    html = HTML_WITH_FIGURES.replace('"@@FIG:f1@@"', '"<svg></svg>"')
    out, report = ff.embed_figures(html, resolve_pdf=lambda url: pdf)
    assert out == html
    assert report["embedded"] == []


def test_embed_figures_reports_unknown_key_without_crashing(tmp_path):
    pdf = _make_pdf(tmp_path)
    html = HTML_WITH_FIGURES.replace("@@FIG:f1@@", "@@FIG:yok@@")
    out, report = ff.embed_figures(html, resolve_pdf=lambda url: pdf)
    # yer tutucu YERINDE kalir (sessizce silinmez) ve rapora dusr
    assert "@@FIG:yok@@" in out
    assert report["failed"] and report["failed"][0][0] == "yok"


def test_embed_figures_degrades_when_pdf_unreachable():
    def boom(url):
        raise ff.FigureError("indirilemedi: aglar kapali")
    out, report = ff.embed_figures(HTML_WITH_FIGURES, resolve_pdf=boom)
    # uretim bloke OLMAZ: yer tutucu kalir, hata raporlanir
    assert "@@FIG:f1@@" in out
    assert report["embedded"] == []
    assert report["failed"][0][0] == "f1"
    assert "indirilemedi" in report["failed"][0][1]


def test_embed_figures_downloads_each_pdf_once(tmp_path):
    """Iki figur ayni PDF'ten geliyorsa indirme TEK sefer olmali (19 MB dosya)."""
    pdf = _make_pdf(tmp_path)
    html = HTML_WITH_FIGURES.replace(
        '  segments: [',
        '''  segments2: [],
  segments: [''').replace(
        'f1: { figureId: 6448',
        '''f2: { figureId: 6449, pdfUrl: "https://example.invalid/kitap.pdf", page: 1,
          bbox: [50, 100, 150, 200], caption: "Ikinci", alt: "Ikinci figur" },
    f1: { figureId: 6448''').replace(
        '"@@FIG:f1@@"', '"@@FIG:f1@@ @@FIG:f2@@"')
    calls = []
    def counting(url):
        calls.append(url)
        return pdf
    out, report = ff.embed_figures(html, resolve_pdf=counting)
    assert sorted(report["embedded"]) == ["f1", "f2"]
    assert len(calls) == 1, f"PDF {len(calls)} kez cozuldu; onbellek calismiyor"
