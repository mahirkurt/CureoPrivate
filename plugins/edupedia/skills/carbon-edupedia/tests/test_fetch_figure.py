# tests/test_fetch_figure.py — Tier-2 figür gömücü testleri
#
# Ağ YOK: PDF'ler testin içinde PyMuPDF ile üretilir. Gerçek ders kitabı indirme
# yolu (resolve_pdf) bir seam ile enjekte edilir, böylece kırpma/gömme mantığı
# upstream'e bağımlı olmadan test edilir.
import hashlib
import os
import socket
import stat
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import fetch_figure as ff

import pytest

fitz = pytest.importorskip("fitz", reason="PyMuPDF yok — Tier-2 gömme kullanılamaz")

ALLOWED_PDF_URL = "https://tymm.meb.gov.tr/kitaplar/kitap.pdf"
PUBLIC_IPV4 = "8.8.8.8"


class _FakeResponse:
    def __init__(
        self,
        body=b"%PDF-1.7\nfixture",
        *,
        status=200,
        headers=None,
        fail_after_reads=None,
    ):
        self.status = status
        self.headers = (
            {"Content-Type": "application/pdf"} if headers is None else headers
        )
        self._body = body
        self._offset = 0
        self._reads = 0
        self._fail_after_reads = fail_after_reads
        self.read_sizes = []
        self.closed = False

    def getcode(self):
        return self.status

    def read(self, size=-1):
        self.read_sizes.append(size)
        if self._fail_after_reads is not None and self._reads >= self._fail_after_reads:
            raise OSError("simulated stream failure")
        self._reads += 1
        if size is None or size < 0:
            size = len(self._body) - self._offset
        chunk = self._body[self._offset:self._offset + size]
        self._offset += len(chunk)
        return chunk

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


class _GeneratedPdfResponse(_FakeResponse):
    def __init__(self, byte_count, *, headers=None):
        super().__init__(body=b"", headers=headers)
        self._remaining = byte_count
        self._prefix = b"%PDF-"

    def read(self, size=-1):
        self.read_sizes.append(size)
        if size is None or size < 0:
            size = self._remaining
        if self._remaining <= 0:
            return b""
        amount = min(size, self._remaining)
        self._remaining -= amount
        prefix = self._prefix[:amount]
        self._prefix = self._prefix[len(prefix):]
        return prefix + (b"x" * (amount - len(prefix)))


class _TransportRecorder:
    def __init__(self):
        self.calls = []


class _FakePinnedConnection:
    responses = []
    connections = []
    request_log = []
    opener = None

    def __init__(self, host, address, timeout=None, context=None):
        self.host = host
        self.address = address
        self.timeout = timeout
        self.context = context
        self.closed = False
        type(self).connections.append(self)

    def request(self, method, target, body=None, headers=None):
        type(self).request_log.append(
            {
                "method": method,
                "target": target,
                "host": self.host,
                "address": self.address,
                "timeout": self.timeout,
                "headers": headers or {},
            }
        )
        if type(self).opener is not None:
            type(self).opener.calls.append(
                (f"https://{self.host}{target}", self.timeout)
            )

    def getresponse(self):
        if not type(self).responses:
            raise AssertionError("unexpected pinned HTTPS request")
        response = type(self).responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response

    def close(self):
        self.closed = True


def _install_transport(monkeypatch, *responses):
    opener = _TransportRecorder()
    _FakePinnedConnection.responses = list(responses)
    _FakePinnedConnection.connections = []
    _FakePinnedConnection.request_log = []
    _FakePinnedConnection.opener = opener
    monkeypatch.setattr(
        ff,
        "_PinnedHTTPSConnection",
        _FakePinnedConnection,
        raising=False,
    )
    return opener


def _install_dns(monkeypatch, addresses=(PUBLIC_IPV4,)):
    calls = []

    def fake_getaddrinfo(host, port, *_args, **_kwargs):
        calls.append((host, port))
        rows = []
        for address in addresses:
            if ":" in address:
                rows.append(
                    (socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP, "",
                     (address, port, 0, 0))
                )
            else:
                rows.append(
                    (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "",
                     (address, port))
                )
        return rows

    monkeypatch.setattr(ff.socket, "getaddrinfo", fake_getaddrinfo)
    return calls


def _cache_path(cache_dir, canonical_url):
    digest = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
    return cache_dir / f"{digest}.pdf"


def _sidecar_path(cache_dir, canonical_url):
    digest = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
    return cache_dir / f"{digest}.sha256"


def _seed_cache_entry(cache_dir, canonical_url, data, *, sidecar_hash=None):
    cache_dir.mkdir(mode=0o700, exist_ok=True)
    pdf_path = _cache_path(cache_dir, canonical_url)
    sidecar_path = _sidecar_path(cache_dir, canonical_url)
    pdf_path.write_bytes(data)
    pdf_path.chmod(0o600)
    digest = sidecar_hash or hashlib.sha256(data).hexdigest()
    sidecar_path.write_text(f"{digest} {len(data)}\n", encoding="ascii")
    sidecar_path.chmod(0o600)
    return pdf_path, sidecar_path


def _make_pdf(tmp_path, pages=1, *, width=300, height=400):
    """Icinde bilinen bir dikdortgen olan kucuk bir test PDF'i uretir."""
    doc = fitz.open()
    for _ in range(pages):
        page = doc.new_page(width=width, height=height)
        page.draw_rect(fitz.Rect(50, 100, 150, 200), color=(1, 0, 0), fill=(1, 0, 0))
    p = tmp_path / "test.pdf"
    doc.save(str(p))
    doc.close()
    return str(p)


def _make_pdf_bytes(marker="fixture", *, pages=1):
    doc = fitz.open()
    for index in range(pages):
        page = doc.new_page(width=300, height=400)
        page.insert_text((40, 40), f"{marker}-{index}")
    data = doc.tobytes()
    doc.close()
    return data


def _build_figures_html(urls):
    entries = []
    placeholders = []
    for index, url in enumerate(urls):
        key = f"f{index}"
        entries.append(
            f'{key}: {{ figureId: {index + 1}, pdfUrl: "{url}", '
            'page: 1, bbox: [0, 0, 10, 10], caption: "c", alt: "a" }'
        )
        placeholders.append(f'"@@FIG:{key}@@"')
    return (
        "<script>const MODULE_DATA = { figures: {"
        + ", ".join(entries)
        + "}, segments: ["
        + ", ".join(placeholders)
        + "] };</script>"
    )


HTML_WITH_FIGURES = '''<html lang="tr"><body><script>
const MODULE_DATA = {
  meta: { title: "Test", mode: "CURRICULUM" },
  figures: {
    f1: { figureId: 6448, pdfUrl: "https://tymm.meb.gov.tr/kitaplar/kitap.pdf", page: 1,
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


def test_render_figure_accepts_exact_pdf_bytes_without_reopening_path():
    pdf_bytes = _make_pdf_bytes("render-bytes")

    data, w, h = ff.render_figure(
        pdf_bytes,
        page=1,
        bbox=[50, 100, 150, 200],
    )

    assert data.startswith(b"\xff\xd8")
    assert 150 <= w <= 250 and 150 <= h <= 250


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
        '''f2: { figureId: 6449, pdfUrl: "https://tymm.meb.gov.tr/kitaplar/kitap.pdf", page: 1,
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


def test_embed_figures_rejects_figure_count_before_resolver_work(monkeypatch):
    monkeypatch.setattr(ff, "MAX_FIGURE_COUNT", 2, raising=False)
    html = _build_figures_html([ALLOWED_PDF_URL] * 3)
    calls = []

    def should_not_resolve(url):
        calls.append(url)
        raise AssertionError("figure-count budget must fail before resolver work")

    out, report = ff.embed_figures(html, resolve_pdf=should_not_resolve)

    assert out == html
    assert calls == []
    assert report["embedded"] == []
    assert len(report["failed"]) == 3
    assert all("figür" in reason.casefold() and "sınır" in reason.casefold()
               for _key, reason in report["failed"])


def test_embed_figures_rejects_unique_pdf_limit_before_resolver_work(monkeypatch):
    monkeypatch.setattr(ff, "MAX_UNIQUE_PDF_URLS", 2, raising=False)
    urls = [f"https://tymm.meb.gov.tr/kitaplar/{index}.pdf" for index in range(3)]
    html = _build_figures_html(urls)
    calls = []

    def should_not_resolve(url):
        calls.append(url)
        raise AssertionError("unique-PDF budget must fail before resolver work")

    out, report = ff.embed_figures(html, resolve_pdf=should_not_resolve)

    assert out == html
    assert calls == []
    assert report["embedded"] == []
    assert len(report["failed"]) == 3
    assert all("benzersiz pdf" in reason.casefold()
               for _key, reason in report["failed"])


def test_embed_figures_passes_remaining_cumulative_pdf_budget(monkeypatch):
    payload = b"%PDF-abc"
    monkeypatch.setattr(
        ff,
        "MAX_CUMULATIVE_PDF_BYTES",
        len(payload) + len(ff.PDF_MAGIC),
        raising=False,
    )
    html = _build_figures_html(
        [
            "https://tymm.meb.gov.tr/kitaplar/a.pdf",
            "https://tymm.meb.gov.tr/kitaplar/b.pdf",
        ]
    )
    limits = []

    def bounded_resolver(_url, *, max_bytes):
        limits.append(max_bytes)
        if len(payload) > max_bytes:
            raise ff.FigureError("kümülatif PDF sınırı")
        return payload

    bounded_resolver._edupedia_accepts_max_bytes = True
    monkeypatch.setattr(
        ff,
        "render_figure",
        lambda *_args, **_kwargs: (b"\xff\xd8ok", 10, 10),
    )

    _out, report = ff.embed_figures(html, resolve_pdf=bounded_resolver)

    assert report["embedded"] == ["f0"]
    assert report["failed"][0][0] == "f1"
    assert limits == [len(payload) + len(ff.PDF_MAGIC), len(ff.PDF_MAGIC)]


def test_embed_figures_enforces_cumulative_jpeg_budget_per_render(monkeypatch):
    monkeypatch.setattr(ff, "MAX_CUMULATIVE_JPEG_BYTES", 10, raising=False)
    html = _build_figures_html([ALLOWED_PDF_URL] * 3)
    limits = []

    def bounded_render(*_args, max_output_bytes, **_kwargs):
        limits.append(max_output_bytes)
        if max_output_bytes < 6:
            raise ff.FigureError("kümülatif JPEG sınırı")
        return b"\xff\xd8jpeg", 10, 10

    monkeypatch.setattr(ff, "render_figure", bounded_render)
    _out, report = ff.embed_figures(
        html,
        resolve_pdf=lambda _url: b"%PDF-test",
    )

    assert report["embedded"] == ["f0"]
    assert [key for key, _reason in report["failed"]] == ["f1", "f2"]
    assert limits == [10, 4, 4]


def test_embed_figures_checks_base64_budget_before_encoding(monkeypatch):
    monkeypatch.setattr(ff, "MAX_CUMULATIVE_BASE64_BYTES", 8, raising=False)
    html = _build_figures_html([ALLOWED_PDF_URL] * 2)
    monkeypatch.setattr(
        ff,
        "render_figure",
        lambda *_args, **_kwargs: (b"\xff\xd8xx", 10, 10),
    )
    real_b64encode = ff.base64.b64encode
    encoded_inputs = []

    def recording_b64encode(data):
        encoded_inputs.append(data)
        return real_b64encode(data)

    monkeypatch.setattr(ff.base64, "b64encode", recording_b64encode)

    _out, report = ff.embed_figures(
        html,
        resolve_pdf=lambda _url: b"%PDF-test",
    )

    assert report["embedded"] == ["f0"]
    assert report["failed"][0][0] == "f1"
    assert encoded_inputs == [b"\xff\xd8xx"]


@pytest.mark.parametrize(
    "url",
    [
        "http://tymm.meb.gov.tr/kitap.pdf",
        "https://tymm.meb.gov.tr.evil.example/kitap.pdf",
        "https://evil-tymm.meb.gov.tr/kitap.pdf",
        "https://user@tymm.meb.gov.tr/kitap.pdf",
        "https://tymm.meb.gov.tr:444/kitap.pdf",
        "https://tymm.meb.gov.tr/kitap.pdf#page=1",
        "https://127.0.0.1/kitap.pdf",
        "https://[::1]/kitap.pdf",
        "file:///tmp/kitap.pdf",
    ],
)
def test_default_resolver_rejects_non_allowlisted_urls_without_request(
    tmp_path, monkeypatch, url
):
    _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch, _FakeResponse())
    resolve = ff._default_resolver(str(tmp_path / "cache"))

    with pytest.raises(ff.FigureError):
        resolve(url)

    assert opener.calls == []


def test_default_resolver_accepts_exact_host_and_canonicalizes_url(tmp_path, monkeypatch):
    body = _make_pdf_bytes("allowed")
    response = _FakeResponse(
        body,
        headers={
            "Content-Type": "application/pdf; charset=binary",
            "Content-Length": str(len(body)),
        },
    )
    dns_calls = _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch, response)
    cache_dir = tmp_path / "cache"
    resolve = ff._default_resolver(str(cache_dir))

    result = resolve("HTTPS://TYMM.MEB.GOV.TR:443/kitaplar/kitap.pdf")

    canonical = "https://tymm.meb.gov.tr/kitaplar/kitap.pdf"
    assert result == body
    assert _cache_path(cache_dir, canonical).read_bytes() == body
    sidecar = _sidecar_path(cache_dir, canonical)
    assert sidecar.read_text(encoding="ascii") == (
        f"{hashlib.sha256(body).hexdigest()} {len(body)}\n"
    )
    assert opener.calls == [(canonical, ff.DOWNLOAD_TIMEOUT)]
    assert dns_calls == [("tymm.meb.gov.tr", 443)]
    assert len(_FakePinnedConnection.connections) == 1
    assert PUBLIC_IPV4 in repr(_FakePinnedConnection.connections[0].address)
    assert _FakePinnedConnection.connections[0].host == "tymm.meb.gov.tr"
    assert stat.S_IMODE(cache_dir.stat().st_mode) == 0o700
    assert stat.S_IMODE(_cache_path(cache_dir, canonical).stat().st_mode) == 0o600
    assert stat.S_IMODE(sidecar.stat().st_mode) == 0o600
    assert response.read_sizes
    assert all(0 < size <= ff.DOWNLOAD_CHUNK_SIZE for size in response.read_sizes)


@pytest.mark.parametrize(
    "address",
    [
        (socket.AF_INET, (PUBLIC_IPV4, 443), PUBLIC_IPV4),
        (
            socket.AF_INET6,
            ("2606:4700:4700::1111", 443, 0, 0),
            "2606:4700:4700::1111",
        ),
    ],
)
def test_pinned_https_connection_uses_vetted_ip_with_allowlisted_sni(
    monkeypatch, address
):
    if not hasattr(ff, "_PinnedHTTPSConnection"):
        pytest.fail("manual pinned HTTPS transport is missing")

    events = {}

    class FakeRawSocket:
        def settimeout(self, timeout):
            events["timeout"] = timeout

        def connect(self, sockaddr):
            events["connect"] = sockaddr

        def close(self):
            events["raw_closed"] = True

    class FakeContext:
        check_hostname = True

        def wrap_socket(self, raw_socket, *, server_hostname):
            events["wrapped"] = raw_socket
            events["server_hostname"] = server_hostname
            return object()

    raw_socket = FakeRawSocket()
    monkeypatch.setattr(ff.socket, "socket", lambda *_args, **_kwargs: raw_socket)
    connection = ff._PinnedHTTPSConnection(
        "tymm.meb.gov.tr",
        address,
        timeout=7,
        context=FakeContext(),
    )

    connection.connect()

    assert events["connect"] == address[1]
    assert events["server_hostname"] == "tymm.meb.gov.tr"
    assert events["wrapped"] is raw_socket


def test_default_resolver_pins_first_vetted_address_across_dns_rebind(
    tmp_path, monkeypatch
):
    dns_calls = []

    def rebinding_getaddrinfo(host, port, *_args, **_kwargs):
        dns_calls.append((host, port))
        address = PUBLIC_IPV4 if len(dns_calls) == 1 else "127.0.0.1"
        return [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "",
             (address, port))
        ]

    monkeypatch.setattr(ff.socket, "getaddrinfo", rebinding_getaddrinfo)
    body = _make_pdf_bytes("pinned")
    _install_transport(monkeypatch, _FakeResponse(body))
    resolve = ff._default_resolver(str(tmp_path / "cache"))

    result = resolve(ALLOWED_PDF_URL)

    assert _cache_path(tmp_path / "cache", ALLOWED_PDF_URL).read_bytes() == body
    assert result == body
    assert dns_calls == [("tymm.meb.gov.tr", 443)]
    assert len(_FakePinnedConnection.connections) == 1
    connection = _FakePinnedConnection.connections[0]
    assert PUBLIC_IPV4 in repr(connection.address)
    assert connection.host == "tymm.meb.gov.tr"


def test_default_resolver_tries_vetted_ipv4_and_ipv6_deterministically(
    tmp_path, monkeypatch
):
    ipv6 = "2606:4700:4700::1111"

    def mixed_getaddrinfo(_host, port, *_args, **_kwargs):
        return [
            (
                socket.AF_INET6,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                (ipv6, port, 0, 0),
            ),
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                (PUBLIC_IPV4, port),
            ),
        ]

    monkeypatch.setattr(ff.socket, "getaddrinfo", mixed_getaddrinfo)
    body = _make_pdf_bytes("address-fallback")
    _install_transport(
        monkeypatch,
        OSError("first vetted address unavailable"),
        _FakeResponse(body),
    )
    resolve = ff._default_resolver(str(tmp_path / "cache"))

    result = resolve(ALLOWED_PDF_URL)

    assert result == body
    assert len(_FakePinnedConnection.connections) == 2
    assert PUBLIC_IPV4 in repr(_FakePinnedConnection.connections[0].address)
    assert ipv6 in repr(_FakePinnedConnection.connections[1].address)


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "10.0.0.1",
        "172.16.0.1",
        "192.168.1.1",
        "169.254.1.1",
        "0.0.0.0",
        "192.0.2.1",
        "224.0.0.1",
        "::1",
        "fe80::1",
        "fc00::1",
        "fec0::1",
        "2001:db8::1",
        "ff02::1",
    ],
)
def test_default_resolver_rejects_every_non_global_dns_result(
    tmp_path, monkeypatch, address
):
    _install_dns(monkeypatch, (address,))
    opener = _install_transport(monkeypatch, _FakeResponse())
    resolve = ff._default_resolver(str(tmp_path / "cache"))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert opener.calls == []


def test_default_resolver_rejects_mixed_public_and_private_dns(tmp_path, monkeypatch):
    _install_dns(monkeypatch, (PUBLIC_IPV4, "10.0.0.9"))
    opener = _install_transport(monkeypatch, _FakeResponse())
    resolve = ff._default_resolver(str(tmp_path / "cache"))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert opener.calls == []


def test_default_resolver_validates_redirect_dns_before_following(tmp_path, monkeypatch):
    dns_answers = iter(((PUBLIC_IPV4,), ("127.0.0.1",)))

    def fake_getaddrinfo(host, port, *_args, **_kwargs):
        address = next(dns_answers)[0]
        return [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "",
             (address, port))
        ]

    monkeypatch.setattr(ff.socket, "getaddrinfo", fake_getaddrinfo)
    redirect = _FakeResponse(
        b"",
        status=302,
        headers={"Location": "/kitaplar/final.pdf"},
    )
    opener = _install_transport(monkeypatch, redirect, _FakeResponse())
    resolve = ff._default_resolver(str(tmp_path / "cache"))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert [url for url, _timeout in opener.calls] == [ALLOWED_PDF_URL]


def test_default_resolver_rejects_redirect_to_disallowed_host(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    redirect = _FakeResponse(
        b"",
        status=302,
        headers={"Location": "https://evil.example/kitap.pdf"},
    )
    opener = _install_transport(monkeypatch, redirect, _FakeResponse())
    resolve = ff._default_resolver(str(tmp_path / "cache"))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert len(opener.calls) == 1


def test_default_resolver_rejects_redirect_loop(tmp_path, monkeypatch):
    dns_calls = _install_dns(monkeypatch)
    redirect = _FakeResponse(
        b"",
        status=302,
        headers={"Location": ALLOWED_PDF_URL},
    )
    opener = _install_transport(monkeypatch, redirect)
    resolve = ff._default_resolver(str(tmp_path / "cache"))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert len(opener.calls) == 1
    assert len(dns_calls) >= 1


def test_default_resolver_follows_at_most_configured_redirects(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    redirects = [
        _FakeResponse(b"", status=302, headers={"Location": f"/r{i}.pdf"})
        for i in range(ff.MAX_REDIRECTS + 1)
    ]
    opener = _install_transport(monkeypatch, *redirects)
    resolve = ff._default_resolver(str(tmp_path / "cache"))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert len(opener.calls) == ff.MAX_REDIRECTS + 1


def test_default_resolver_rejects_oversized_content_length(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    response = _FakeResponse(
        headers={
            "Content-Type": "application/pdf",
            "Content-Length": str(ff.MAX_DOWNLOAD_BYTES + 1),
        }
    )
    _install_transport(monkeypatch, response)
    cache_dir = tmp_path / "cache"
    resolve = ff._default_resolver(str(cache_dir))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert response.read_sizes == []
    assert list(cache_dir.iterdir()) == []


def test_default_resolver_enforces_remaining_pdf_budget_before_body_read(
    tmp_path, monkeypatch
):
    _install_dns(monkeypatch)
    body = _make_pdf_bytes("remaining-budget")
    response = _FakeResponse(
        body,
        headers={
            "Content-Type": "application/pdf",
            "Content-Length": str(len(body)),
        },
    )
    _install_transport(monkeypatch, response)
    cache_dir = tmp_path / "cache"
    resolve = ff._default_resolver(str(cache_dir))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL, max_bytes=len(ff.PDF_MAGIC))

    assert response.read_sizes == []
    assert list(cache_dir.iterdir()) == []


def test_default_resolver_rejects_chunked_body_over_actual_byte_cap(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    response = _GeneratedPdfResponse(ff.MAX_DOWNLOAD_BYTES + 1)
    _install_transport(monkeypatch, response)
    cache_dir = tmp_path / "cache"
    resolve = ff._default_resolver(str(cache_dir))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert response.read_sizes
    assert all(size == ff.DOWNLOAD_CHUNK_SIZE for size in response.read_sizes)
    assert list(cache_dir.iterdir()) == []


@pytest.mark.parametrize("content_type", [None, "text/html", "application/octet-stream"])
def test_default_resolver_rejects_missing_or_non_pdf_mime(
    tmp_path, monkeypatch, content_type
):
    _install_dns(monkeypatch)
    headers = {} if content_type is None else {"Content-Type": content_type}
    response = _FakeResponse(b"%PDF-1.7\nfixture", headers=headers)
    _install_transport(monkeypatch, response)
    cache_dir = tmp_path / "cache"
    resolve = ff._default_resolver(str(cache_dir))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert list(cache_dir.iterdir()) == []


def test_default_resolver_requires_pdf_magic_even_with_pdf_mime(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    response = _FakeResponse(b"<html>not a pdf</html>")
    _install_transport(monkeypatch, response)
    cache_dir = tmp_path / "cache"
    resolve = ff._default_resolver(str(cache_dir))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert list(cache_dir.iterdir()) == []


def test_default_resolver_hashes_canonical_url_not_basename(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    first = _make_pdf_bytes("first")
    second = _make_pdf_bytes("second")
    opener = _install_transport(
        monkeypatch,
        _FakeResponse(first),
        _FakeResponse(second, headers={"Content-Type": "application/x-pdf"}),
    )
    cache_dir = tmp_path / "cache"
    resolve = ff._default_resolver(str(cache_dir))
    url_a = "https://tymm.meb.gov.tr/a/kitap.pdf"
    url_b = "https://tymm.meb.gov.tr/b/kitap.pdf"

    data_a = resolve(url_a)
    data_b = resolve(url_b)

    assert data_a == first
    assert data_b == second
    path_a = _cache_path(cache_dir, url_a)
    path_b = _cache_path(cache_dir, url_b)
    assert path_a != path_b
    assert path_a.name == hashlib.sha256(url_a.encode()).hexdigest() + ".pdf"
    assert path_b.name == hashlib.sha256(url_b.encode()).hexdigest() + ".pdf"
    assert path_a.read_bytes() == first
    assert path_b.read_bytes() == second
    assert len(opener.calls) == 2


def test_default_resolver_does_not_reuse_corrupt_cache(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(mode=0o700)
    cached = _cache_path(cache_dir, ALLOWED_PDF_URL)
    cached.write_bytes(b"corrupt-but-nonempty")
    cached.chmod(0o600)
    fresh = _make_pdf_bytes("fresh")
    opener = _install_transport(monkeypatch, _FakeResponse(fresh))
    resolve = ff._default_resolver(str(cache_dir))

    result = resolve(ALLOWED_PDF_URL)

    assert result == fresh
    assert cached.read_bytes() == fresh
    assert len(opener.calls) == 1


def test_default_resolver_reuses_only_hash_verified_structural_cache(
    tmp_path, monkeypatch
):
    body = _make_pdf_bytes("cached")
    cache_dir = tmp_path / "cache"
    _seed_cache_entry(cache_dir, ALLOWED_PDF_URL, body)
    _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch)
    resolve = ff._default_resolver(str(cache_dir))

    result = resolve(ALLOWED_PDF_URL)

    assert result == body
    assert opener.calls == []


def test_default_resolver_replaces_matching_hash_but_structurally_invalid_pdf(
    tmp_path, monkeypatch
):
    cache_dir = tmp_path / "cache"
    corrupt = b"%PDF-1.7\ntruncated-but-magic-present"
    _seed_cache_entry(cache_dir, ALLOWED_PDF_URL, corrupt)
    fresh = _make_pdf_bytes("structural-replacement")
    _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch, _FakeResponse(fresh))
    resolve = ff._default_resolver(str(cache_dir))

    result = resolve(ALLOWED_PDF_URL)

    assert result == fresh
    assert _cache_path(cache_dir, ALLOWED_PDF_URL).read_bytes() == fresh
    assert len(opener.calls) == 1


def test_default_resolver_replaces_bit_corrupt_cache_with_stale_sidecar(
    tmp_path, monkeypatch
):
    original = _make_pdf_bytes("original")
    cache_dir = tmp_path / "cache"
    cached, _sidecar = _seed_cache_entry(cache_dir, ALLOWED_PDF_URL, original)
    corrupted = bytearray(original)
    corrupted[len(corrupted) // 2] ^= 0x01
    cached.write_bytes(corrupted)
    cached.chmod(0o600)
    fresh = _make_pdf_bytes("bit-replacement")
    _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch, _FakeResponse(fresh))
    resolve = ff._default_resolver(str(cache_dir))

    result = resolve(ALLOWED_PDF_URL)

    assert result == fresh
    assert len(opener.calls) == 1


def test_default_resolver_consumes_opened_cache_inode_during_path_replacement(
    tmp_path, monkeypatch
):
    original = _make_pdf_bytes("opened-inode")
    replacement = _make_pdf_bytes("replacement-path")
    cache_dir = tmp_path / "cache"
    cached, sidecar = _seed_cache_entry(cache_dir, ALLOWED_PDF_URL, original)
    replacement_path = tmp_path / "replacement.pdf"
    replacement_path.write_bytes(replacement)
    replacement_path.chmod(0o600)
    _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch)
    real_open = os.open
    replaced = False

    def racing_open(path, flags, *args, **kwargs):
        nonlocal replaced
        descriptor = real_open(path, flags, *args, **kwargs)
        if not replaced and os.fspath(path).endswith(sidecar.name):
            os.replace(replacement_path, cached)
            replaced = True
        return descriptor

    monkeypatch.setattr(ff.os, "open", racing_open)
    resolve = ff._default_resolver(str(cache_dir))

    result = resolve(ALLOWED_PDF_URL)

    assert replaced is True
    assert result == original
    assert cached.read_bytes() == replacement
    assert opener.calls == []


def test_default_resolver_cleans_unique_partial_after_stream_error(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    response = _FakeResponse(
        b"%PDF-" + (b"x" * ff.DOWNLOAD_CHUNK_SIZE),
        fail_after_reads=1,
    )
    _install_transport(monkeypatch, response)
    cache_dir = tmp_path / "cache"
    resolve = ff._default_resolver(str(cache_dir))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert list(cache_dir.iterdir()) == []


def test_default_resolver_rejects_download_before_cache_quota_overflow(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(ff, "MAX_CACHE_BYTES", 100, raising=False)
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(mode=0o700)
    keep = cache_dir / "keep.pdf"
    keep.write_bytes(b"k" * 90)
    keep.chmod(0o600)
    _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch)
    resolve = ff._default_resolver(str(cache_dir))

    with pytest.raises(ff.FigureError) as exc:
        resolve(ALLOWED_PDF_URL)

    assert "cache" in str(exc.value).casefold()
    assert "kota" in str(exc.value).casefold()
    assert opener.calls == []
    assert keep.read_bytes() == b"k" * 90


def test_default_resolver_cleans_only_stale_owned_part_files(tmp_path, monkeypatch):
    monkeypatch.setattr(ff, "STALE_PART_MAX_AGE_SECONDS", 60, raising=False)
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(mode=0o700)
    stale = cache_dir / ".old.part"
    stale.write_bytes(b"old")
    stale.chmod(0o600)
    os.utime(stale, (1, 1))
    fresh = cache_dir / ".fresh.part"
    fresh.write_bytes(b"fresh")
    fresh.chmod(0o600)
    valid_pdf = cache_dir / "keep.pdf"
    valid_pdf.write_bytes(b"valid")
    valid_pdf.chmod(0o600)
    valid_sidecar = cache_dir / "keep.sha256"
    valid_sidecar.write_bytes(b"sidecar")
    valid_sidecar.chmod(0o600)
    outside = tmp_path / "outside"
    outside.write_bytes(b"outside")
    symlink_part = cache_dir / ".link.part"
    symlink_part.symlink_to(outside)

    ff._default_resolver(str(cache_dir))

    assert not stale.exists()
    assert fresh.read_bytes() == b"fresh"
    assert valid_pdf.read_bytes() == b"valid"
    assert valid_sidecar.read_bytes() == b"sidecar"
    assert symlink_part.is_symlink()
    assert outside.read_bytes() == b"outside"


def test_default_resolver_rejects_symlink_cache_directory(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch, _FakeResponse())
    real_cache = tmp_path / "real-cache"
    real_cache.mkdir(mode=0o700)
    cache_link = tmp_path / "cache-link"
    cache_link.symlink_to(real_cache, target_is_directory=True)

    with pytest.raises(ff.FigureError):
        ff._default_resolver(str(cache_link))

    assert opener.calls == []


def test_default_resolver_rejects_symlink_cache_file(tmp_path, monkeypatch):
    _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch, _FakeResponse())
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(mode=0o700)
    target = tmp_path / "target.pdf"
    target.write_bytes(b"%PDF-1.7\noutside")
    cached = _cache_path(cache_dir, ALLOWED_PDF_URL)
    cached.symlink_to(target)
    resolve = ff._default_resolver(str(cache_dir))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert opener.calls == []
    assert target.read_bytes() == b"%PDF-1.7\noutside"


def test_default_resolver_rejects_symlink_hash_sidecar(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    body = _make_pdf_bytes("sidecar-symlink")
    cached = _cache_path(cache_dir, ALLOWED_PDF_URL)
    cache_dir.mkdir(mode=0o700)
    cached.write_bytes(body)
    cached.chmod(0o600)
    outside = tmp_path / "outside.sha256"
    outside.write_text(
        f"{hashlib.sha256(body).hexdigest()} {len(body)}\n",
        encoding="ascii",
    )
    sidecar = _sidecar_path(cache_dir, ALLOWED_PDF_URL)
    sidecar.symlink_to(outside)
    _install_dns(monkeypatch)
    opener = _install_transport(monkeypatch)
    resolve = ff._default_resolver(str(cache_dir))

    with pytest.raises(ff.FigureError):
        resolve(ALLOWED_PDF_URL)

    assert opener.calls == []
    assert sidecar.is_symlink()
    assert outside.exists()


def test_embed_figures_rejects_local_file_url_before_injected_resolver():
    html = HTML_WITH_FIGURES.replace(
        ALLOWED_PDF_URL,
        "file:///etc/passwd",
    )
    calls = []

    def should_not_run(url):
        calls.append(url)
        return "/etc/passwd"

    out, report = ff.embed_figures(html, resolve_pdf=should_not_run)

    assert "@@FIG:f1@@" in out
    assert report["embedded"] == []
    assert report["failed"][0][0] == "f1"
    assert calls == []


@pytest.mark.parametrize(
    "bbox",
    [
        [float("nan"), 0, 10, 10],
        [0, 0, float("inf"), 10],
        [10, 0, 0, 10],
        [0, 10, 10, 0],
        [-1, 0, 10, 10],
        [0, 0, 301, 10],
        [0, 0, 10, 401],
    ],
)
def test_render_figure_rejects_nonfinite_nonpositive_or_out_of_page_bbox(
    tmp_path, bbox
):
    pdf = _make_pdf(tmp_path)

    with pytest.raises(ff.FigureError):
        ff.render_figure(pdf, page=1, bbox=bbox)


@pytest.mark.parametrize("page", [True, 0, -1, 1.5, 2])
def test_render_figure_rejects_invalid_page_values(tmp_path, page):
    pdf = _make_pdf(tmp_path)

    with pytest.raises(ff.FigureError):
        ff.render_figure(pdf, page=page, bbox=[0, 0, 10, 10])


@pytest.mark.parametrize("scale", [0, -1, float("nan"), float("inf"), 4.01])
def test_render_figure_rejects_unbounded_scale(tmp_path, scale):
    pdf = _make_pdf(tmp_path)

    with pytest.raises(ff.FigureError):
        ff.render_figure(pdf, page=1, bbox=[0, 0, 10, 10], scale=scale)


def test_render_figure_rejects_huge_crop_before_rasterization(tmp_path):
    pdf = _make_pdf(tmp_path, width=5000, height=5000)

    with pytest.raises(ff.FigureError) as exc:
        ff.render_figure(pdf, page=1, bbox=[0, 0, 5000, 5000], scale=2)

    assert "piksel" in str(exc.value).casefold()


def test_render_figure_rejects_oversized_encoded_output(tmp_path, monkeypatch):
    from PIL import Image

    pdf = _make_pdf(tmp_path)

    def oversized_save(_self, stream, *_args, **_kwargs):
        stream.write(b"x" * (ff.MAX_OUTPUT_BYTES + 1))

    monkeypatch.setattr(Image.Image, "save", oversized_save)

    with pytest.raises(ff.FigureError):
        ff.render_figure(pdf, page=1, bbox=[50, 100, 150, 200])
