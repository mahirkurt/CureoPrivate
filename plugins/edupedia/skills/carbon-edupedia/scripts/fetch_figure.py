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
import errno
import hashlib
import html as _html
import http.client
import ipaddress
import io
import json
import math
import os
import re
import secrets
import socket
import ssl
import stat
import sys
import tempfile
import time
import urllib.parse

DEFAULT_SCALE = 2.0
DEFAULT_QUALITY = 85
PLACEHOLDER_RE = re.compile(r"@@FIG:([A-Za-z0-9_-]+)@@")
DOWNLOAD_TIMEOUT = 30
DOWNLOAD_CHUNK_SIZE = 64 * 1024
MAX_DOWNLOAD_BYTES = 32 * 1024 * 1024
MAX_REDIRECTS = 3
MAX_FIGURE_COUNT = 16
MAX_UNIQUE_PDF_URLS = 4
MAX_CUMULATIVE_PDF_BYTES = 64 * 1024 * 1024
MAX_CUMULATIVE_JPEG_BYTES = 24 * 1024 * 1024
MAX_CUMULATIVE_BASE64_BYTES = 32 * 1024 * 1024
MAX_CACHE_BYTES = 256 * 1024 * 1024
STALE_PART_MAX_AGE_SECONDS = 60 * 60
HASH_SIDECAR_MAX_BYTES = 256
ALLOWED_PDF_HOSTS = frozenset({"tymm.meb.gov.tr"})
ALLOWED_PDF_MIME_TYPES = frozenset({"application/pdf", "application/x-pdf"})
PDF_MAGIC = b"%PDF-"
MIN_RENDER_SCALE = 0.25
MAX_RENDER_SCALE = 4.0
MAX_RENDER_PIXELS = 16_000_000
MAX_OUTPUT_BYTES = 8 * 1024 * 1024
MAX_PDF_PAGE_COUNT = 2_000
MIN_JPEG_QUALITY = 1
MAX_JPEG_QUALITY = 95
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_CACHE_DIR_NAME = (
    f"edupedia-figure-cache-v2-{getattr(os, 'getuid', lambda: 'user')()}"
)
# Cloudflare/bot kuralları varsayılan istemci UA'sını 403 ile karşılayabiliyor
# (edupedia yayın istemcilerinde ölçülmüş davranış) — açık UA gönderiyoruz.
USER_AGENT = "edupedia-fetch-figure/1.0 (+https://cureonics.com)"


class FigureError(Exception):
    """Figür çıkarılamadı — çağıran Tier-1'e düşer, üretim bloke olmaz."""


class _BoundedBytesIO(io.BytesIO):
    """Encoder'ın tanımlı çıktı bütçesinden fazla bellek büyütmesini engelle."""

    def __init__(self, limit):
        super().__init__()
        self._limit = limit

    def write(self, data):
        current_size = self.getbuffer().nbytes
        projected_size = max(current_size, self.tell() + len(data))
        if projected_size > self._limit:
            raise FigureError(
                f"JPEG çıktı boyutu güvenli sınırı aşıyor: "
                f"{projected_size} > {self._limit}"
            )
        return super().write(data)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Önceden doğrulanmış IP'ye bağlanırken TLS kimliğini hostname'de tut."""

    def __init__(self, host, address, timeout=DOWNLOAD_TIMEOUT, context=None):
        self._vetted_address = address
        super().__init__(
            host=host,
            port=443,
            timeout=timeout,
            context=context or ssl.create_default_context(),
        )

    def connect(self):
        family, sockaddr, _display_address = self._vetted_address
        raw_socket = socket.socket(family, socket.SOCK_STREAM)
        try:
            raw_socket.settimeout(self.timeout)
            raw_socket.connect(sockaddr)
            self.sock = self._context.wrap_socket(
                raw_socket,
                server_hostname=self.host,
            )
        except Exception:
            raw_socket.close()
            raise


class _ManagedHTTPResponse:
    """HTTP yanıtı kapanınca ona ait pinned bağlantıyı da kapat."""

    def __init__(self, response, connection):
        self._response = response
        self._connection = connection
        self.status = getattr(response, "status", None)
        self.headers = getattr(response, "headers", None)

    def getcode(self):
        getcode = getattr(self._response, "getcode", None)
        return getcode() if callable(getcode) else self.status

    def read(self, size=-1):
        return self._response.read(size)

    def close(self):
        try:
            self._response.close()
        finally:
            self._connection.close()


def _canonicalize_pdf_url(url):
    """PDF URL'sini doğrula ve cache/istek için tek kanonik biçime indir."""
    if not isinstance(url, str) or not url:
        raise FigureError("pdfUrl boş veya metin değil")
    if any(ord(char) <= 32 or ord(char) == 127 for char in url) or "\\" in url:
        raise FigureError("pdfUrl kontrol karakteri, boşluk veya ters eğik çizgi içeriyor")
    if "#" in url:
        raise FigureError("pdfUrl fragment içeremez")

    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError as e:
        raise FigureError(f"pdfUrl ayrıştırılamadı: {e}") from e
    if parts.scheme.casefold() != "https":
        raise FigureError("pdfUrl yalnız HTTPS olabilir")
    if not parts.netloc or not parts.hostname:
        raise FigureError("pdfUrl geçerli bir hostname içermiyor")
    if parts.username is not None or parts.password is not None:
        raise FigureError("pdfUrl userinfo içeremez")

    try:
        host = parts.hostname.encode("idna").decode("ascii").casefold()
    except (UnicodeError, AttributeError) as e:
        raise FigureError("pdfUrl hostname IDNA olarak geçersiz") from e
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise FigureError("pdfUrl IP literal içeremez")
    if host not in ALLOWED_PDF_HOSTS:
        raise FigureError(f"pdfUrl hostname izinli değil: {host}")

    try:
        port = parts.port
    except ValueError as e:
        raise FigureError(f"pdfUrl portu geçersiz: {e}") from e
    if parts.netloc.endswith(":"):
        raise FigureError("pdfUrl boş port içeremez")
    if port not in (None, 443):
        raise FigureError("pdfUrl yalnız varsayılan HTTPS portunu kullanabilir")

    path = parts.path or "/"
    return urllib.parse.urlunsplit(("https", host, path, parts.query, ""))


def _resolve_global_host(host):
    """Hostname'in bütün A/AAAA sonuçlarının public/global olduğunu doğrula."""
    try:
        results = socket.getaddrinfo(
            host,
            443,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
    except (OSError, socket.gaierror) as e:
        raise FigureError(f"PDF hostname çözümlenemedi: {e}") from e
    if not results:
        raise FigureError("PDF hostname için DNS sonucu yok")

    addresses = {}
    for result in results:
        try:
            family = result[0]
            sockaddr = result[4]
            raw_address = result[4][0]
            address = ipaddress.ip_address(str(raw_address).split("%", 1)[0])
        except (IndexError, TypeError, ValueError) as e:
            raise FigureError("DNS yanıtında geçersiz IP adresi var") from e
        if address.version == 6 and address.ipv4_mapped is not None:
            address = address.ipv4_mapped
        if (
            not address.is_global
            or address.is_loopback
            or address.is_private
            or address.is_link_local
            or address.is_multicast
            or address.is_reserved
            or address.is_unspecified
            or getattr(address, "is_site_local", False)
        ):
            raise FigureError(f"DNS global olmayan adres döndürdü: {address}")
        if family not in (socket.AF_INET, socket.AF_INET6):
            raise FigureError("DNS yanıtında desteklenmeyen adres ailesi var")
        key = (address.version, address.packed, family, tuple(sockaddr))
        addresses[key] = (family, tuple(sockaddr), str(address))
    if not addresses:
        raise FigureError("PDF hostname için kullanılabilir global adres yok")
    return tuple(addresses[key] for key in sorted(addresses))


def _response_status(response):
    if response is None:
        raise FigureError("PDF sunucusu yanıt döndürmedi")
    status_code = getattr(response, "status", None)
    if status_code is None:
        getcode = getattr(response, "getcode", None)
        if not callable(getcode):
            raise FigureError("PDF yanıtında HTTP durum kodu yok")
        status_code = getcode()
    try:
        status_code = int(status_code)
    except (TypeError, ValueError) as e:
        raise FigureError("PDF yanıtındaki HTTP durum kodu geçersiz") from e
    if not 100 <= status_code <= 599:
        raise FigureError("PDF yanıtındaki HTTP durum kodu geçersiz")
    return status_code


def _response_header(response, name):
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    getter = getattr(headers, "get", None)
    if callable(getter):
        value = getter(name)
        if value is not None:
            return value
    try:
        for key, value in headers.items():
            if str(key).casefold() == name.casefold():
                return value
    except (AttributeError, TypeError):
        return None
    return None


def _close_response(response):
    close = getattr(response, "close", None)
    if callable(close):
        close()


def _open_pinned_response(canonical_url, vetted_addresses):
    parts = urllib.parse.urlsplit(canonical_url)
    host = parts.hostname
    if host is None:
        raise FigureError("pdfUrl hostname içermiyor")
    target = parts.path or "/"
    if parts.query:
        target = f"{target}?{parts.query}"

    failures = []
    for address in vetted_addresses:
        connection = _PinnedHTTPSConnection(
            host,
            address,
            timeout=DOWNLOAD_TIMEOUT,
        )
        try:
            connection.request(
                "GET",
                target,
                headers={
                    "Host": host,
                    "User-Agent": USER_AGENT,
                    "Accept": "application/pdf, application/x-pdf;q=0.9",
                    "Connection": "close",
                },
            )
            response = connection.getresponse()
            return _ManagedHTTPResponse(response, connection)
        except (OSError, TimeoutError, ssl.SSLError, http.client.HTTPException) as e:
            failures.append(f"{address[2]}: {e}")
            connection.close()
        except Exception as e:
            failures.append(f"{address[2]}: {e}")
            connection.close()
    detail = "; ".join(failures) if failures else "doğrulanmış adres yok"
    raise FigureError(f"PDF pinned HTTPS isteği başarısız: {detail}")


def _validated_content_length(response, max_bytes=MAX_DOWNLOAD_BYTES):
    raw_length = _response_header(response, "Content-Length")
    if raw_length is None:
        return None
    text = str(raw_length).strip()
    if not text.isascii() or not text.isdigit():
        raise FigureError("PDF Content-Length başlığı geçersiz")
    length = int(text)
    if length < len(PDF_MAGIC):
        raise FigureError("PDF Content-Length başlığı geçersiz")
    if length > max_bytes:
        raise FigureError(
            f"PDF Content-Length sınırı aşıyor ({length} > {max_bytes})"
        )
    return length


def _stream_pdf_response(response, output, max_bytes=MAX_DOWNLOAD_BYTES):
    content_type = _response_header(response, "Content-Type")
    if not isinstance(content_type, str):
        raise FigureError("PDF yanıtında Content-Type yok veya geçersiz")
    mime = content_type.split(";", 1)[0].strip().casefold()
    if mime not in ALLOWED_PDF_MIME_TYPES:
        raise FigureError(f"PDF yanıt MIME türü kabul edilmiyor: {mime or 'boş'}")
    declared_length = _validated_content_length(response, max_bytes=max_bytes)

    total = 0
    prefix = bytearray()
    while True:
        try:
            chunk = response.read(DOWNLOAD_CHUNK_SIZE)
        except Exception as e:
            raise FigureError(f"PDF akışı okunamadı: {e}") from e
        if chunk is None:
            raise FigureError("PDF akışı geçersiz boş parça döndürdü")
        if not isinstance(chunk, (bytes, bytearray, memoryview)):
            raise FigureError("PDF akışı bayt döndürmedi")
        if not chunk:
            break
        data = bytes(chunk)
        total += len(data)
        if total > max_bytes:
            raise FigureError(
                f"PDF gerçek bayt sınırı aşıldı ({total} > {max_bytes})"
            )
        if len(prefix) < len(PDF_MAGIC):
            needed = len(PDF_MAGIC) - len(prefix)
            prefix.extend(data[:needed])
            if len(prefix) == len(PDF_MAGIC) and bytes(prefix) != PDF_MAGIC:
                raise FigureError("PDF içeriği %PDF- magic imzası taşımıyor")
        written = output.write(data)
        if written is not None and written != len(data):
            raise FigureError("PDF geçici dosyaya eksik yazıldı")

    if total < len(PDF_MAGIC) or bytes(prefix) != PDF_MAGIC:
        raise FigureError("PDF içeriği %PDF- magic imzası taşımıyor")
    if declared_length is not None and declared_length != total:
        raise FigureError(
            f"PDF Content-Length ile gerçek boyut uyuşmuyor ({declared_length} != {total})"
        )
    return total


def _download_pdf(canonical_url, output, max_bytes=MAX_DOWNLOAD_BYTES):
    current_url = canonical_url
    seen = {canonical_url}
    redirects_followed = 0

    while True:
        # Her istek/redirect hedefi bir kez çözülür ve o sonuçtaki IP'ye pinlenir.
        current_url = _canonicalize_pdf_url(current_url)
        host = urllib.parse.urlsplit(current_url).hostname
        if host is None:
            raise FigureError("pdfUrl hostname içermiyor")
        vetted_addresses = _resolve_global_host(host)
        response = _open_pinned_response(current_url, vetted_addresses)
        try:
            status_code = _response_status(response)
            if status_code in _REDIRECT_STATUSES:
                location = _response_header(response, "Location")
                if not isinstance(location, str) or not location.strip():
                    raise FigureError("PDF redirect yanıtında geçerli Location yok")
                target = urllib.parse.urljoin(current_url, location)
                # Location takip kararı verilmeden önce URL politikasından geçer;
                # bir sonraki döngüde yeniden çözülüp yeni IP'ye pinlenir.
                target = _canonicalize_pdf_url(target)
                if target in seen:
                    raise FigureError("PDF redirect döngüsü algılandı")
                if redirects_followed >= MAX_REDIRECTS:
                    raise FigureError(f"PDF redirect sınırı aşıldı ({MAX_REDIRECTS})")
                seen.add(target)
                redirects_followed += 1
                current_url = target
                continue
            if status_code != 200:
                raise FigureError(f"PDF sunucusu HTTP {status_code} döndürdü")
            total = _stream_pdf_response(response, output, max_bytes=max_bytes)
            return current_url, total
        finally:
            _close_response(response)


def _current_uid():
    getuid = getattr(os, "getuid", None)
    return getuid() if callable(getuid) else None


def _assert_private_cache_dir(cache_dir):
    try:
        info = os.lstat(cache_dir)
    except OSError as e:
        raise FigureError(f"Özel PDF cache dizini incelenemedi: {e}") from e
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise FigureError("PDF cache yolu gerçek bir dizin olmalı; symlink olamaz")
    uid = _current_uid()
    if uid is not None and info.st_uid != uid:
        raise FigureError("PDF cache dizini mevcut kullanıcıya ait değil")
    mode = stat.S_IMODE(info.st_mode)
    if mode & 0o077 or mode & 0o700 != 0o700:
        raise FigureError("PDF cache dizini yalnız sahibi için rwx (0700) olmalı")


def _prepare_cache_dir(cache_dir):
    cache_dir = os.path.abspath(os.fspath(cache_dir))
    try:
        os.mkdir(cache_dir, mode=0o700)
    except FileExistsError:
        pass
    except OSError as e:
        raise FigureError(f"Özel PDF cache dizini oluşturulamadı: {e}") from e
    _assert_private_cache_dir(cache_dir)
    return cache_dir


def _open_private_cache_dir(cache_dir):
    _assert_private_cache_dir(cache_dir)
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(cache_dir, flags)
    except OSError as e:
        if e.errno in (errno.ELOOP, errno.EMLINK):
            raise FigureError("PDF cache dizini symlink olamaz") from e
        raise FigureError(f"PDF cache dizini güvenle açılamadı: {e}") from e
    try:
        opened = os.fstat(descriptor)
        current = os.lstat(cache_dir)
        if not stat.S_ISDIR(opened.st_mode):
            raise FigureError("PDF cache yolu normal dizin değil")
        if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
            raise FigureError("PDF cache dizini açılırken değişti")
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _validate_private_file_descriptor(descriptor, label):
    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode):
        raise FigureError(f"{label} normal dosya değil")
    uid = _current_uid()
    if uid is not None and info.st_uid != uid:
        raise FigureError(f"{label} mevcut kullanıcıya ait değil")
    if info.st_nlink != 1:
        raise FigureError(f"{label} hard-link olamaz")
    if stat.S_IMODE(info.st_mode) != 0o600:
        try:
            os.fchmod(descriptor, 0o600)
        except OSError as e:
            raise FigureError(f"{label} izni 0600 yapılamadı: {e}") from e
    return info


def _open_cache_member(cache_fd, name, label):
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(name, flags, dir_fd=cache_fd)
    except FileNotFoundError:
        return None
    except OSError as e:
        if e.errno in (errno.ELOOP, errno.EMLINK):
            raise FigureError(f"{label} symlink olamaz") from e
        raise FigureError(f"{label} güvenle açılamadı: {e}") from e
    try:
        _validate_private_file_descriptor(descriptor, label)
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _read_fd_bytes(descriptor, limit, label):
    before = os.fstat(descriptor)
    if before.st_size < 0 or before.st_size > limit:
        raise FigureError(f"{label} boyutu güvenli sınır dışında")
    os.lseek(descriptor, 0, os.SEEK_SET)
    data = bytearray()
    while True:
        chunk = os.read(descriptor, min(DOWNLOAD_CHUNK_SIZE, limit + 1 - len(data)))
        if not chunk:
            break
        data.extend(chunk)
        if len(data) > limit:
            raise FigureError(f"{label} boyutu güvenli sınırı aşıyor")
    after = os.fstat(descriptor)
    identity_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    identity_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    if identity_before != identity_after or len(data) != before.st_size:
        raise FigureError(f"{label} okunurken değişti")
    return bytes(data)


def _validate_pdf_structure(pdf_bytes):
    if not len(PDF_MAGIC) <= len(pdf_bytes) <= MAX_DOWNLOAD_BYTES:
        raise FigureError("PDF boyutu güvenli sınır dışında")
    if not pdf_bytes.startswith(PDF_MAGIC):
        raise FigureError("PDF içeriği %PDF- magic imzası taşımıyor")
    try:
        import fitz
    except ImportError as e:
        raise FigureError(
            "PyMuPDF (fitz) kurulu değil; PDF bütünlüğü doğrulanamaz"
        ) from e
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise FigureError(f"PDF yapısal doğrulamadan geçemedi: {e}") from e
    try:
        if not isinstance(doc.page_count, int) or not (
            1 <= doc.page_count <= MAX_PDF_PAGE_COUNT
        ):
            raise FigureError(
                f"belge sayfa sayısı güvenli aralık dışında: {doc.page_count}"
            )
    finally:
        doc.close()


def _parse_hash_sidecar(sidecar_bytes):
    try:
        text = sidecar_bytes.decode("ascii")
    except UnicodeDecodeError:
        return None
    match = re.fullmatch(r"([0-9a-f]{64}) ([0-9]+)\n", text)
    if match is None:
        return None
    size = int(match.group(2))
    if not len(PDF_MAGIC) <= size <= MAX_DOWNLOAD_BYTES:
        return None
    return match.group(1), size


def _read_cache_entry(cache_fd, pdf_name, sidecar_name):
    pdf_fd = _open_cache_member(cache_fd, pdf_name, "PDF cache dosyası")
    if pdf_fd is None:
        return None
    sidecar_fd = None
    try:
        # İki pathname de önce nofollow fd olarak açılır; bundan sonraki bütün
        # doğrulama, yarışla değiştirilemeyen bu iki inode üzerinde yapılır.
        sidecar_fd = _open_cache_member(
            cache_fd,
            sidecar_name,
            "PDF cache hash sidecar",
        )
        if sidecar_fd is None:
            return None
        try:
            pdf_bytes = _read_fd_bytes(
                pdf_fd,
                MAX_DOWNLOAD_BYTES,
                "PDF cache dosyası",
            )
            sidecar_bytes = _read_fd_bytes(
                sidecar_fd,
                256,
                "PDF cache hash sidecar",
            )
        except FigureError:
            return None
        expected = _parse_hash_sidecar(sidecar_bytes)
        if expected is None:
            return None
        expected_hash, expected_size = expected
        if expected_size != len(pdf_bytes):
            return None
        if hashlib.sha256(pdf_bytes).hexdigest() != expected_hash:
            return None
        try:
            _validate_pdf_structure(pdf_bytes)
        except FigureError:
            return None
        return pdf_bytes
    finally:
        if sidecar_fd is not None:
            os.close(sidecar_fd)
        os.close(pdf_fd)


def _create_cache_part(cache_fd, digest, kind):
    flags = (
        os.O_RDWR
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    for _attempt in range(16):
        name = f".{digest}.{kind}.{secrets.token_hex(8)}.part"
        try:
            descriptor = os.open(name, flags, 0o600, dir_fd=cache_fd)
        except FileExistsError:
            continue
        except OSError as e:
            raise FigureError(f"PDF cache geçici dosyası oluşturulamadı: {e}") from e
        os.fchmod(descriptor, 0o600)
        return descriptor, name
    raise FigureError("PDF cache için benzersiz geçici dosya oluşturulamadı")


def _write_all(descriptor, data, label):
    view = memoryview(data)
    written = 0
    while written < len(view):
        count = os.write(descriptor, view[written:])
        if count <= 0:
            raise FigureError(f"{label} eksik yazıldı")
        written += count


def _cleanup_stale_parts(cache_fd):
    cutoff = time.time() - STALE_PART_MAX_AGE_SECONDS
    uid = _current_uid()
    for name in os.listdir(cache_fd):
        if not (
            isinstance(name, str)
            and name.startswith(".")
            and name.endswith(".part")
        ):
            continue
        try:
            info = os.stat(name, dir_fd=cache_fd, follow_symlinks=False)
        except FileNotFoundError:
            continue
        except OSError:
            continue
        if (
            not stat.S_ISREG(info.st_mode)
            or (uid is not None and info.st_uid != uid)
            or info.st_nlink != 1
            or info.st_mtime > cutoff
        ):
            continue
        try:
            os.unlink(name, dir_fd=cache_fd)
        except FileNotFoundError:
            continue
        except OSError:
            continue


def _cache_usage(cache_fd, excluded_names=()):
    excluded = set(excluded_names)
    total = 0
    for name in os.listdir(cache_fd):
        if name in excluded:
            continue
        try:
            info = os.stat(name, dir_fd=cache_fd, follow_symlinks=False)
        except FileNotFoundError:
            continue
        except OSError as e:
            raise FigureError(f"PDF cache kotası ölçülemedi: {e}") from e
        if stat.S_ISREG(info.st_mode):
            total += info.st_size
            if total > MAX_CACHE_BYTES:
                break
    return total


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

def _validate_render_parameters(page, bbox, scale, quality):
    if isinstance(page, bool) or not isinstance(page, int) or page < 1:
        raise FigureError("sayfa numarası 1-tabanlı pozitif tamsayı olmalı")
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        raise FigureError("bbox tam olarak 4 sayı içermeli")
    normalized_bbox = []
    for value in bbox:
        if isinstance(value, bool):
            raise FigureError("bbox yalnız sonlu sayılar içermeli")
        try:
            numeric = float(value)
        except (TypeError, ValueError) as e:
            raise FigureError("bbox yalnız sonlu sayılar içermeli") from e
        if not math.isfinite(numeric):
            raise FigureError("bbox yalnız sonlu sayılar içermeli")
        normalized_bbox.append(numeric)
    x0, y0, x1, y1 = normalized_bbox
    if x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0:
        raise FigureError(f"bbox pozitif alanlı olmalı: {normalized_bbox}")

    if isinstance(scale, bool):
        raise FigureError("render ölçeği sonlu bir sayı olmalı")
    try:
        normalized_scale = float(scale)
    except (TypeError, ValueError) as e:
        raise FigureError("render ölçeği sonlu bir sayı olmalı") from e
    if (
        not math.isfinite(normalized_scale)
        or not MIN_RENDER_SCALE <= normalized_scale <= MAX_RENDER_SCALE
    ):
        raise FigureError(
            f"render ölçeği {MIN_RENDER_SCALE}–{MAX_RENDER_SCALE} aralığında olmalı"
        )
    if isinstance(quality, bool) or not isinstance(quality, int):
        raise FigureError("JPEG kalitesi tamsayı olmalı")
    if not MIN_JPEG_QUALITY <= quality <= MAX_JPEG_QUALITY:
        raise FigureError(
            f"JPEG kalitesi {MIN_JPEG_QUALITY}–{MAX_JPEG_QUALITY} aralığında olmalı"
        )
    return page, normalized_bbox, normalized_scale, quality


def render_figure(
    pdf_path,
    page,
    bbox,
    scale=DEFAULT_SCALE,
    quality=DEFAULT_QUALITY,
    max_output_bytes=MAX_OUTPUT_BYTES,
):
    """PDF'in `page` sayfasından `bbox` bölgesini kırpıp JPEG bayt döndürür.

    Döndürür: (jpeg_bytes, width_px, height_px). `page` 1-tabanlıdır
    (get_figure'ın page_no alanıyla aynı taban).

    JPEG tercihi ölçümle geldi: aynı figür PNG 3x'te 171 KB base64, JPEG 2x q85'te
    15 KB — modül dosyası tek-dosya olduğu için bu fark belirleyicidir.
    """
    page, bbox, scale, quality = _validate_render_parameters(
        page, bbox, scale, quality
    )
    if (
        isinstance(max_output_bytes, bool)
        or not isinstance(max_output_bytes, int)
        or not 1 <= max_output_bytes <= MAX_OUTPUT_BYTES
    ):
        raise FigureError(
            f"JPEG çıktı bütçesi 1–{MAX_OUTPUT_BYTES} bayt aralığında olmalı"
        )
    pdf_bytes = None
    local_path = None
    if isinstance(pdf_path, (bytes, bytearray, memoryview)):
        pdf_bytes = bytes(pdf_path)
    else:
        try:
            local_path = os.fspath(pdf_path)
        except TypeError as e:
            raise FigureError(
                "PDF kaynağı bayt veya yerel dosya yolu olmalı"
            ) from e
        if isinstance(local_path, str):
            path_scheme = urllib.parse.urlsplit(local_path).scheme.casefold()
            if path_scheme in {"file", "http", "https"}:
                raise FigureError(
                    "render_figure yerel URL kabul etmez; dosya yolu gerekir"
                )

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
        if pdf_bytes is not None:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        else:
            doc = fitz.open(local_path)
    except Exception as e:
        raise FigureError(f"PDF açılamadı: {e}") from e
    try:
        if not isinstance(doc.page_count, int) or not (
            1 <= doc.page_count <= MAX_PDF_PAGE_COUNT
        ):
            raise FigureError(
                f"belge sayfa sayısı güvenli aralık dışında: {doc.page_count}"
            )
        if page > doc.page_count:
            raise FigureError(
                f"sayfa {page} aralık dışı (belge {doc.page_count} sayfa)")
        source_page = doc[page - 1]
        page_rect = source_page.rect
        page_bounds = (
            float(page_rect.x0),
            float(page_rect.y0),
            float(page_rect.x1),
            float(page_rect.y1),
        )
        if not all(math.isfinite(value) for value in page_bounds):
            raise FigureError("PDF sayfa sınırları sonlu değil")
        x0, y0, x1, y1 = bbox
        if (
            x0 < page_bounds[0]
            or y0 < page_bounds[1]
            or x1 > page_bounds[2]
            or y1 > page_bounds[3]
        ):
            raise FigureError(f"bbox sayfa sınırları dışında: {bbox}")
        width_px = math.ceil((x1 - x0) * scale)
        height_px = math.ceil((y1 - y0) * scale)
        estimated_area = width_px * height_px
        if width_px <= 0 or height_px <= 0 or estimated_area > MAX_RENDER_PIXELS:
            raise FigureError(
                f"render piksel alanı güvenli sınırı aşıyor: "
                f"{width_px}x{height_px} > {MAX_RENDER_PIXELS}"
            )
        rect = fitz.Rect(*bbox)
        if rect.is_empty or rect.is_infinite:
            raise FigureError(f"bbox geçersiz/boş: {bbox}")
        try:
            pix = source_page.get_pixmap(
                clip=rect,
                matrix=fitz.Matrix(scale, scale),
            )
        except Exception as e:
            raise FigureError(f"PDF kırpımı render edilemedi: {e}") from e
        if not pix.width or not pix.height:
            raise FigureError("kırpım boş piksel üretti (bbox sayfa dışında olabilir)")
        if pix.width * pix.height > MAX_RENDER_PIXELS:
            raise FigureError(
                f"render gerçek piksel alanı güvenli sınırı aşıyor: "
                f"{pix.width}x{pix.height}"
            )
        try:
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            buf = _BoundedBytesIO(max_output_bytes)
            img.save(buf, "JPEG", quality=quality, optimize=True)
            data = buf.getvalue()
        except FigureError:
            raise
        except Exception as e:
            raise FigureError(f"JPEG kodlanamadı: {e}") from e
        if not data or len(data) > max_output_bytes:
            raise FigureError(
                f"JPEG çıktı boyutu güvenli sınırı aşıyor: "
                f"{len(data)} > {max_output_bytes}"
            )
        if not data.startswith(b"\xff\xd8"):
            raise FigureError("JPEG çıktı magic imzası taşımıyor")
        return data, pix.width, pix.height
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
    """URL → doğrulanmış PDF baytları; cache pathname'i render'a sızdırılmaz."""
    cache_dir = cache_dir or os.path.join(
        tempfile.gettempdir(), _CACHE_DIR_NAME)
    cache_dir = _prepare_cache_dir(cache_dir)
    initial_cache_fd = _open_private_cache_dir(cache_dir)
    try:
        _cleanup_stale_parts(initial_cache_fd)
    finally:
        os.close(initial_cache_fd)

    def resolve(url, *, max_bytes=MAX_DOWNLOAD_BYTES):
        if (
            isinstance(max_bytes, bool)
            or not isinstance(max_bytes, int)
            or max_bytes < len(PDF_MAGIC)
        ):
            raise FigureError("PDF indirme bütçesi geçersiz veya tükenmiş")
        max_bytes = min(max_bytes, MAX_DOWNLOAD_BYTES)
        canonical_url = _canonicalize_pdf_url(url)
        digest = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
        pdf_name = f"{digest}.pdf"
        sidecar_name = f"{digest}.sha256"
        cache_fd = _open_private_cache_dir(cache_dir)
        pdf_fd = None
        sidecar_fd = None
        pdf_part = None
        sidecar_part = None
        try:
            _cleanup_stale_parts(cache_fd)
            cached = _read_cache_entry(cache_fd, pdf_name, sidecar_name)
            if cached is not None:
                if len(cached) > max_bytes:
                    raise FigureError(
                        f"kümülatif PDF sınırı aşılıyor "
                        f"({len(cached)} > {max_bytes})"
                    )
                return cached

            base_usage = _cache_usage(
                cache_fd,
                excluded_names=(pdf_name, sidecar_name),
            )
            if base_usage + max_bytes + HASH_SIDECAR_MAX_BYTES > MAX_CACHE_BYTES:
                raise FigureError(
                    f"PDF cache kotası yeni indirmeden önce aşılacak "
                    f"({base_usage} + {max_bytes} > {MAX_CACHE_BYTES})"
                )
            pdf_fd, pdf_part = _create_cache_part(cache_fd, digest, "pdf")
            stream = os.fdopen(os.dup(pdf_fd), "wb")
            with stream:
                _download_pdf(canonical_url, stream, max_bytes=max_bytes)
                stream.flush()
                os.fsync(stream.fileno())
            pdf_bytes = _read_fd_bytes(
                pdf_fd,
                max_bytes,
                "indirilen PDF",
            )
            _validate_pdf_structure(pdf_bytes)
            pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
            sidecar_data = f"{pdf_hash} {len(pdf_bytes)}\n".encode("ascii")

            sidecar_fd, sidecar_part = _create_cache_part(
                cache_fd,
                digest,
                "sha256",
            )
            _write_all(sidecar_fd, sidecar_data, "PDF hash sidecar")
            quota_usage = _cache_usage(
                cache_fd,
                excluded_names=(
                    pdf_name,
                    sidecar_name,
                    pdf_part,
                    sidecar_part,
                ),
            )
            if quota_usage + len(pdf_bytes) + len(sidecar_data) > MAX_CACHE_BYTES:
                raise FigureError(
                    f"PDF cache kotası aşılıyor "
                    f"({quota_usage + len(pdf_bytes) + len(sidecar_data)} "
                    f"> {MAX_CACHE_BYTES})"
                )
            os.fsync(pdf_fd)
            os.fsync(sidecar_fd)
            os.replace(
                pdf_part,
                pdf_name,
                src_dir_fd=cache_fd,
                dst_dir_fd=cache_fd,
            )
            pdf_part = None
            os.replace(
                sidecar_part,
                sidecar_name,
                src_dir_fd=cache_fd,
                dst_dir_fd=cache_fd,
            )
            sidecar_part = None
            os.fsync(cache_fd)
            return pdf_bytes
        except FigureError:
            raise
        except Exception as e:
            raise FigureError(f"PDF güvenli biçimde indirilemedi: {e}") from e
        finally:
            if sidecar_fd is not None:
                os.close(sidecar_fd)
            if pdf_fd is not None:
                os.close(pdf_fd)
            for part_name in (sidecar_part, pdf_part):
                if part_name is None:
                    continue
                try:
                    os.unlink(part_name, dir_fd=cache_fd)
                except FileNotFoundError:
                    pass
                except OSError:
                    pass
            os.close(cache_fd)

    resolve._edupedia_accepts_max_bytes = True
    return resolve


# -------------------------------------------------------------------- gömme

def _pdf_payload_size(payload):
    if isinstance(payload, (bytes, bytearray, memoryview)):
        return len(payload)
    try:
        local_path = os.fspath(payload)
        return os.stat(local_path).st_size
    except (TypeError, OSError) as e:
        raise FigureError(f"PDF kaynağı boyutu ölçülemedi: {e}") from e


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
    ordered_keys = list(dict.fromkeys(keys))
    if len(keys) > MAX_FIGURE_COUNT:
        reason = (
            f"figür sayısı güvenli sınırı aşıyor "
            f"({len(keys)} > {MAX_FIGURE_COUNT})"
        )
        report["failed"].extend((key, reason) for key in ordered_keys)
        return html, report

    figures = parse_figures_block(html)
    prepared = {}
    for key in ordered_keys:
        spec = figures.get(key)
        if not spec:
            report["failed"].append((key, "figures bloğunda böyle bir anahtar yok"))
            continue
        missing = [f for f in ("pdfUrl", "page", "bbox") if f not in spec]
        if missing:
            report["failed"].append((key, "eksik alan: " + ", ".join(missing)))
            continue
        try:
            page, bbox, render_scale, render_quality = _validate_render_parameters(
                spec["page"],
                spec["bbox"],
                scale,
                quality,
            )
            url = _canonicalize_pdf_url(spec["pdfUrl"])
            prepared[key] = (
                spec,
                page,
                bbox,
                render_scale,
                render_quality,
                url,
            )
        except FigureError as e:
            report["failed"].append((key, str(e)))

    unique_urls = set(item[5] for item in prepared.values())
    if len(unique_urls) > MAX_UNIQUE_PDF_URLS:
        reason = (
            f"benzersiz PDF sayısı güvenli sınırı aşıyor "
            f"({len(unique_urls)} > {MAX_UNIQUE_PDF_URLS})"
        )
        report["failed"].extend((key, reason) for key in prepared)
        return html, report

    if resolve_pdf is None:
        try:
            resolve_pdf = _default_resolver()
        except FigureError as resolver_error:
            def resolve_pdf(_url, error=resolver_error):
                raise error
    pdf_cache = {}
    rendered = {}
    cumulative_pdf_bytes = 0
    cumulative_jpeg_bytes = 0
    cumulative_base64_bytes = 0

    for key in ordered_keys:
        item = prepared.get(key)
        if item is None:
            continue
        spec, page, bbox, render_scale, render_quality, url = item
        try:
            if url not in pdf_cache:
                remaining_pdf = (
                    MAX_CUMULATIVE_PDF_BYTES - cumulative_pdf_bytes
                )
                if remaining_pdf < len(PDF_MAGIC):
                    raise FigureError("kümülatif PDF bayt bütçesi tükendi")
                if getattr(
                    resolve_pdf,
                    "_edupedia_accepts_max_bytes",
                    False,
                ):
                    payload = resolve_pdf(url, max_bytes=remaining_pdf)
                else:
                    payload = resolve_pdf(url)
                payload_size = _pdf_payload_size(payload)
                if payload_size > remaining_pdf:
                    raise FigureError(
                        f"kümülatif PDF sınırı aşılıyor "
                        f"({cumulative_pdf_bytes + payload_size} "
                        f"> {MAX_CUMULATIVE_PDF_BYTES})"
                    )
                cumulative_pdf_bytes += payload_size
                pdf_cache[url] = payload

            remaining_jpeg = (
                MAX_CUMULATIVE_JPEG_BYTES - cumulative_jpeg_bytes
            )
            if remaining_jpeg <= 0:
                raise FigureError("kümülatif JPEG bayt bütçesi tükendi")
            data, w, h = render_figure(
                pdf_cache[url],
                page,
                bbox,
                scale=render_scale,
                quality=render_quality,
                max_output_bytes=min(MAX_OUTPUT_BYTES, remaining_jpeg),
            )
            if len(data) > remaining_jpeg:
                raise FigureError(
                    f"kümülatif JPEG sınırı aşılıyor "
                    f"({cumulative_jpeg_bytes + len(data)} "
                    f"> {MAX_CUMULATIVE_JPEG_BYTES})"
                )
            cumulative_jpeg_bytes += len(data)
            encoded_size = 4 * ((len(data) + 2) // 3)
            occurrence_count = keys.count(key)
            output_size = encoded_size * occurrence_count
            if (
                cumulative_base64_bytes + output_size
                > MAX_CUMULATIVE_BASE64_BYTES
            ):
                raise FigureError(
                    f"kümülatif base64 sınırı aşılıyor "
                    f"({cumulative_base64_bytes + output_size} "
                    f"> {MAX_CUMULATIVE_BASE64_BYTES})"
                )
            b64 = base64.b64encode(data).decode("ascii")
            if len(b64) != encoded_size:
                raise FigureError("base64 çıktı boyutu beklenmeyen değerde")
            cumulative_base64_bytes += output_size
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
