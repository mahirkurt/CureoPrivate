#!/usr/bin/env python3
"""Cureonics filo prob'u — YALNIZ stdlib, fail-open, 24 saat cache'li.

KANONİK KOPYA: tools/fleetkit/fleet_probe.py. Plugin'lere BİREBİR vendor edilir
(hooks/scripts/fleet_probe.py); `tools/fleetkit/check_drift.py --all` kopyaların
bayt-özdeşliğini doğrular. Plugin içinde düzenlemeyin — burada düzenleyip
`python3 tools/fleetkit/vendor.py` koşun.

NEDEN VAR: env-var varlığına bakmak YETMEZ. 2026-08-02'de TİTCK kapılandı;
lex-sanitas onu "public" saymaya devam etti ve her çağrıda 401 aldı (aynı hata
edupedia/maarif-mufredat, evidentia/titck-cache ve vekayinuvis/tavily'de de
bulundu) — preflight
bunu YAPISAL OLARAK göremedi, çünkü yalnız os.environ'a bakıyordu. Bu modül
gerçek bir MCP `initialize` isteği atar ve iki hâli AYIRIR:

  auth_missing  → anahtar bekleniyor ama ortamda yok (MEŞRU DEGRADE; ağa çıkılmaz)
  unauthorized  → sunucu 401/403 verdi (YAPILANDIRMA ARIZASI — düzeltilebilir)

Bu ayrım olmadan ikisi de "o katman çalışmıyor" diye görünür ve arıza degrade
kılığında sonsuza dek yaşar.

CLI:        python3 fleet_probe.py [--fresh] [--json] [--quiet]
Kütüphane:  cached_probe(root, os.environ)

Bağımlılık notu: bu dosya PyYAML kullanmaz ve gen_fleet'i import etmez —
fleet.lock.json'u stdlib json ile okur, böylece kullanıcı sisteminde PyYAML
kurulu olmasa da preflight çalışır.
"""
import argparse
import hashlib
import hmac
import json
import os
import stat
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

INIT_PAYLOAD = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
               "clientInfo": {"name": "cureonics-preflight", "version": "1.0.0"}},
}).encode("utf-8")

# ÖLÇÜM (2026-08-06, evidentia 20-server filosu): Cloudflare Worker uçlarının
# soğuk başlangıcı 11-12 sn sürüyor (globocan 12.0 · ema 11.8 · drugddx 11.7 ·
# who-gho 11.4 · anamnesis 11.2 · openfda 10.9). Prob 24 saatte bir koştuğu için
# HER ZAMAN soğuk uca çarpar — eşikler bu gerçekliğin üstünde olmalı, yoksa
# sağlıklı server'lar 'unreachable'/'unknown' görünür (prob teşhis ettiği arızayı
# kendisi üretir). Filo TEK dalgada koşar (MAX_WORKERS ≥ en büyük filo) →
# duvar-saati en yavaş server'a eşittir, toplamına değil. Hook fail-open.
PER_ENDPOINT_TIMEOUT = 20.0
TOTAL_DEADLINE = 25.0
MAX_WORKERS = 32
# oecd'nin initialize yanıtı 32 KB (uzun capabilities/instructions). Okuma sınırı
# gövdeyi JSON'un ORTASINDAN keserse ayrıştırma çöker ve sağlıklı server sahte
# 'error' verir — sınır en büyük gerçek yanıtın üstünde olmalı.
READ_LIMIT = 262144
CACHE_TTL = 86400  # 24 saat — her oturumda ağ trafiği olmasın
CACHE_SCHEMA_VERSION = 2
CACHE_MAX_BYTES = 1024 * 1024
CACHE_SALT_NAME = ".credential-salt"

_CACHE_KEYS = {
    "schema_version",
    "roster",
    "auth_presence",
    "credential_fingerprint",
    "ts",
    "results",
}
_CACHE_IDENTITY_KEYS = _CACHE_KEYS - {"ts", "results"}

# ZORUNLU: urllib'in varsayılan 'Python-urllib/x.y' User-Agent'ı Cloudflare bot
# kuralına takılır ve TÜM cureonics.com/workers.dev uçları 403 (error 1010) döner.
# Bu, filonun tamamını sahte 'unauthorized' gösterir — yani prob'un teşhis etmek
# için var olduğu arızanın birebir aynısını ÜRETİR. Açık UA şart.
USER_AGENT = "cureonics-preflight/1.0 (+https://cureonics.com)"

SYMBOL = {"ok": "✓", "auth_missing": "○", "unauthorized": "✗",
          "unreachable": "✗", "error": "!", "unknown": "?", "user_config": "◇"}


class _KeepPost(urllib.request.HTTPRedirectHandler):
    """307/308'i METOT ve GÖVDE korunarak takip eder.

    FastMCP `/mcp` altına mount edildiğinde bare `POST /mcp` → 307 `/mcp/` döner
    (edupedia modul-yayin bunu yapar). urllib POST'ta 307'yi takip etmez → sağlıklı
    server sahte 'error' görünür, yani prob teşhis ettiği arızayı kendisi üretir.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (307, 308):
            return urllib.request.Request(newurl, data=req.data, headers=req.headers,
                                          method=req.get_method(), unverifiable=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_KeepPost)


def load_lock(root):
    """fleet.lock.json'u okur; okunamazsa None (fail-open)."""
    try:
        return json.loads((Path(root) / "fleet.lock.json").read_text(encoding="utf-8"))
    except Exception:
        return None


def _extract_json(body: str):
    """Düz JSON veya SSE (`data: {...}`) gövdesinden ilk JSON nesnesini çıkarır."""
    candidates = [body]
    candidates += [ln[5:].strip() for ln in body.splitlines() if ln.startswith("data:")]
    for raw in candidates:
        raw = raw.strip()
        if raw.startswith("{"):
            try:
                return json.loads(raw)
            except ValueError:
                continue
    return None


def classify(http, body: str) -> str:
    """HTTP kodu + gövdeden durum türetir."""
    if http in (401, 403):
        return "unauthorized"
    if http is None or http >= 500:
        return "unreachable"
    if http != 200:
        return "error"
    payload = _extract_json(body)
    if payload is None:
        return "error"
    if "error" in payload:
        return "error"
    return "ok" if "result" in payload else "error"


def _redact_text(value, sensitive_values) -> str:
    """Hassas değerleri uzunluk/prefix sızdırmayan sabit işaretle değiştirir."""
    try:
        text = str(value)
    except Exception:
        return ""
    secrets = []
    for sensitive in sensitive_values:
        try:
            secret = sensitive if isinstance(sensitive, str) else str(sensitive)
        except Exception:
            continue
        if secret:
            secrets.append(secret)
    for secret in sorted(set(secrets), key=len, reverse=True):
        text = text.replace(secret, "<redacted>")
    return text


def probe_server(server: dict, env, timeout: float = PER_ENDPOINT_TIMEOUT) -> dict:
    """Tek sunucuyu prob eder. Ağ hatası dâhil hiçbir istisna sızmaz."""
    name = server["name"]
    auth_env = server.get("auth_env")
    key = env.get(auth_env) if auth_env else None

    # `${user_config.*}` ile parametrelenmiş server'ı (Claude Code kurulum sırasında
    # doldurur) prob EDEMEYİZ — yer tutucu URL'ye gider ve 401 döner. Bunu
    # 'unauthorized' diye raporlamak sağlıklı bir connector'ı arızalı göstermek
    # olur; dürüst durum 'user_config'tir.
    blob = str(server.get("url", "")) + str(server.get("headers", ""))
    if "${user_config." in blob:
        return {"name": name, "status": "user_config", "http": None,
                "detail": "kurulum sırasında doldurulur (/plugin configure)"}

    if auth_env and not key:
        return {"name": name, "status": "auth_missing", "http": None,
                "detail": "${%s} süreç ortamında yok" % auth_env}

    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream",
               "User-Agent": USER_AGENT}
    if key:
        headers["Authorization"] = "Bearer %s" % key
    req = urllib.request.Request(server["url"], data=INIT_PAYLOAD,
                                 headers=headers, method="POST")
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            body = resp.read(READ_LIMIT).decode("utf-8", "replace")
            return {"name": name, "status": classify(resp.status, body),
                    "http": resp.status, "detail": ""}
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(READ_LIMIT).decode("utf-8", "replace")
        except Exception:
            body = ""
        return {"name": name, "status": classify(exc.code, body),
                "http": exc.code,
                "detail": _redact_text(body, (key,))[:120].replace("\n", " ")}
    except Exception as exc:
        return {"name": name, "status": "unreachable", "http": None,
                "detail": type(exc).__name__}


def probe_fleet(lock: dict, env, deadline: float = TOTAL_DEADLINE) -> dict:
    """Tüm filoyu paralel prob eder; bütçe dolarsa kalanlar 'unknown' kalır."""
    servers = lock.get("servers", [])
    results = {s["name"]: {"name": s["name"], "status": "unknown",
                           "http": None, "detail": "bütçe doldu"} for s in servers}
    if not servers:
        return results
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(probe_server, s, env) for s in servers]
        try:
            for fut in as_completed(futures, timeout=deadline):
                try:
                    r = fut.result()
                    results[r["name"]] = r
                except Exception:
                    pass
        except TimeoutError:
            pass          # bütçe doldu → kalanlar 'unknown'
        except Exception:
            pass
        for fut in futures:
            fut.cancel()
    return results


def _cache_path(plugin: str = "") -> Path:
    """Cache plugin adına göre ayrışır — iki plugin birbirinin sonucunu ezmez."""
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    label = plugin or "default"
    if label in (".", "..") or not all(ch.isalnum() or ch in "._-" for ch in label):
        raise ValueError("güvensiz plugin cache kimliği")
    return Path(base) / "cureonics-fleet" / f"{label}.json"


def _owned_by_current_user(st) -> bool:
    geteuid = getattr(os, "geteuid", None)
    return bool(geteuid is not None and st.st_uid == geteuid())


def _ensure_private_cache_dir(path) -> bool:
    """Yalnız ayrılmış 0700 dizini kabul eder; üst/ortak dizinleri chmod etmez."""
    path = Path(path)
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        try:
            os.mkdir(path, 0o700)
            st = os.lstat(path)
        except FileExistsError:
            try:
                st = os.lstat(path)
            except Exception:
                return False
        except Exception:
            return False
    except Exception:
        return False
    return (
        stat.S_ISDIR(st.st_mode)
        and not stat.S_ISLNK(st.st_mode)
        and _owned_by_current_user(st)
        and stat.S_IMODE(st.st_mode) == 0o700
    )


def _secure_open_flags(base: int):
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        return None
    return base | nofollow | getattr(os, "O_CLOEXEC", 0)


def _read_private_file(path, max_bytes: int, exact_bytes=None):
    """0600, owner-owned, tek-link regular dosyayı O_NOFOLLOW ile sınırlı okur."""
    flags = _secure_open_flags(os.O_RDONLY)
    if flags is None:
        return None
    fd = None
    try:
        fd = os.open(Path(path), flags)
        st = os.fstat(fd)
        if not (
            stat.S_ISREG(st.st_mode)
            and _owned_by_current_user(st)
            and stat.S_IMODE(st.st_mode) == 0o600
            and st.st_nlink == 1
            and st.st_size <= max_bytes
        ):
            return None
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, max_bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > max_bytes:
                return None
        raw = b"".join(chunks)
        if exact_bytes is not None and len(raw) != exact_bytes:
            return None
        return raw
    except Exception:
        return None
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass


def _new_private_temp(root, stem):
    flags = _secure_open_flags(os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    if flags is None:
        return None, None
    for _ in range(32):
        name = f".{stem}.{os.getpid()}.{os.urandom(12).hex()}.tmp"
        path = Path(root) / name
        try:
            return path, os.open(path, flags, 0o600)
        except FileExistsError:
            continue
        except Exception:
            return None, None
    return None, None


def _write_all(fd, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("cache temp write failed")
        view = view[written:]


def _fsync_dir(path) -> None:
    flags = _secure_open_flags(os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    if flags is None:
        return
    fd = None
    try:
        fd = os.open(Path(path), flags)
        os.fsync(fd)
    except Exception:
        pass
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass


def _load_or_create_salt(cache_root):
    """Atomik oluşturulmuş 32-byte yerel HMAC salt'ını döner; güvensizde None."""
    root = Path(cache_root)
    if not _ensure_private_cache_dir(root):
        return None
    salt_path = root / CACHE_SALT_NAME
    try:
        os.lstat(salt_path)
    except FileNotFoundError:
        temp_path, fd = _new_private_temp(root, "salt")
        if temp_path is None or fd is None:
            return None
        linked = False
        try:
            salt = os.urandom(32)
            _write_all(fd, salt)
            os.fsync(fd)
            os.close(fd)
            fd = None
            try:
                os.link(temp_path, salt_path, follow_symlinks=False)
                linked = True
            except FileExistsError:
                pass
            if linked:
                _fsync_dir(root)
        except Exception:
            return None
        finally:
            if fd is not None:
                try:
                    os.close(fd)
                except Exception:
                    pass
            try:
                os.unlink(temp_path)
            except Exception:
                pass
    except Exception:
        return None
    return _read_private_file(salt_path, 32, exact_bytes=32)


def _replace_target_is_safe(path) -> bool:
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return True
    except Exception:
        return False
    return stat.S_ISREG(st.st_mode) and _owned_by_current_user(st)


def _atomic_write_private(path, payload: bytes) -> bool:
    """Benzersiz 0600 temp + replace; symlink/özel dosya hedefini reddeder."""
    path = Path(path)
    root = path.parent
    if not _ensure_private_cache_dir(root) or not _replace_target_is_safe(path):
        return False
    temp_path, fd = _new_private_temp(root, path.name)
    if temp_path is None or fd is None:
        return False
    try:
        _write_all(fd, payload)
        os.fsync(fd)
        os.close(fd)
        fd = None
        if not _replace_target_is_safe(path):
            return False
        os.replace(temp_path, path)
        _fsync_dir(root)
        return True
    except Exception:
        return False
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
        except Exception:
            pass


def _is_request_roster_field(name) -> bool:
    normalized = str(name).lower().replace("-", "_")
    return (
        normalized in {"name", "url", "type"}
        or "auth" in normalized
        or "header" in normalized
    )


def _request_roster_rows(lock):
    rows = []
    for server in (lock or {}).get("servers") or []:
        row = {
            "name": server.get("name"),
            "url": server.get("url"),
            "auth_env": server.get("auth_env"),
        }
        for key, value in server.items():
            if _is_request_roster_field(key):
                row[str(key)] = value
        encoded = json.dumps(
            row,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        rows.append((encoded, server))
    rows.sort(key=lambda item: item[0])
    return rows


def roster_fingerprint(lock, salt=None) -> str:
    """Filo kimliğinin kararlı damgası.

    Yaş tek başına yetmez: 2026-08-08'de cache, `openalex`/`pubmed-epmc` için
    taşınmadan önceki HTTP 530'u 24 saat boyunca 'degraded' diye raporladı.
    İstek-yüzeyi alanları değişince damga değişir → cache ölür. Cache'e yazılan
    biçim salt'lı HMAC'tir; saltsız çağrı yalnız geriye-uyumlu karşılaştırma/test
    yardımcısıdır ve credential içermez.
    """
    blob = ("[" + ",".join(row for row, _server in _request_roster_rows(lock)) + "]")
    raw = blob.encode("utf-8")
    if salt is not None:
        return hmac.new(
            bytes(salt),
            b"cureonics-fleet/roster/v2\0" + raw,
            hashlib.sha256,
        ).hexdigest()
    return hashlib.sha256(raw).hexdigest()


def _hmac_frame(mac, value: bytes) -> None:
    mac.update(len(value).to_bytes(8, "big"))
    mac.update(value)


def cache_identity(lock, env, salt) -> dict:
    """Roster + aynı probe env'inden presence/HMAC credential kimliği üretir."""
    if not isinstance(salt, (bytes, bytearray)) or len(salt) != 32:
        raise ValueError("cache salt unavailable")
    mac = hmac.new(
        bytes(salt),
        b"cureonics-fleet/credentials/v2\0",
        hashlib.sha256,
    )
    presence = []
    for row, server in _request_roster_rows(lock):
        auth_env = server.get("auth_env")
        value = env.get(auth_env) if auth_env else None
        present = bool(value)
        presence.append(present)
        _hmac_frame(mac, row.encode("utf-8"))
        _hmac_frame(mac, str(auth_env or "").encode("utf-8"))
        mac.update(b"\x01" if present else b"\x00")
        if present:
            try:
                raw_value = value.encode("utf-8") if isinstance(value, str) else str(value).encode("utf-8")
            except Exception:
                raw_value = b""
            _hmac_frame(mac, raw_value)
    return {
        "schema_version": CACHE_SCHEMA_VERSION,
        "roster": roster_fingerprint(lock, salt=salt),
        "auth_presence": presence,
        "credential_fingerprint": mac.hexdigest(),
    }


def _compat_identity(roster, salt) -> dict:
    """Eski doğrudan read/write_cache çağrıları için secretsiz şemalı kimlik."""
    roster_raw = str(roster or "").encode("utf-8")
    return {
        "schema_version": CACHE_SCHEMA_VERSION,
        "roster": hmac.new(
            bytes(salt),
            b"cureonics-fleet/compat-roster/v2\0" + roster_raw,
            hashlib.sha256,
        ).hexdigest(),
        "auth_presence": [],
        "credential_fingerprint": hmac.new(
            bytes(salt),
            b"cureonics-fleet/compat-credentials/v2\0",
            hashlib.sha256,
        ).hexdigest(),
    }


def _identity_matches(data, expected) -> bool:
    try:
        if set(data) != _CACHE_KEYS or set(expected) != _CACHE_IDENTITY_KEYS:
            return False
        if data["schema_version"] != CACHE_SCHEMA_VERSION:
            return False
        if data["schema_version"] != expected["schema_version"]:
            return False
        if data["auth_presence"] != expected["auth_presence"]:
            return False
        return (
            hmac.compare_digest(str(data["roster"]), str(expected["roster"]))
            and hmac.compare_digest(
                str(data["credential_fingerprint"]),
                str(expected["credential_fingerprint"]),
            )
        )
    except Exception:
        return False


def read_cache(path, ttl: int = CACHE_TTL, roster=None, *, identity=None):
    """Güvenli/taze/kimliği eşleşen cache'i döner; aksi durumda None.

    Legacy şema/fingerprint dosyaları, symlink/özel dosyalar ve boyut sınırını
    aşan içerik JSON ayrıştırılmadan reddedilir.
    """
    try:
        path = Path(path)
        salt = _load_or_create_salt(path.parent)
        if salt is None:
            return None
        expected = identity if identity is not None else _compat_identity(roster, salt)
        raw = _read_private_file(path, CACHE_MAX_BYTES)
        if raw is None:
            return None
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict) or not _identity_matches(data, expected):
            return None
        if time.time() - float(data["ts"]) > ttl:
            return None
        if not isinstance(data["results"], dict):
            return None
        return data["results"]
    except Exception:
        return None


def _redact_cache_value(value, sensitive_values):
    if isinstance(value, str):
        return _redact_text(value, sensitive_values)
    if isinstance(value, dict):
        return {
            _redact_text(key, sensitive_values): _redact_cache_value(item, sensitive_values)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_cache_value(item, sensitive_values) for item in value]
    if isinstance(value, tuple):
        return [_redact_cache_value(item, sensitive_values) for item in value]
    return value


def write_cache(path, results: dict, roster=None, *, identity=None,
                sensitive_values=()) -> None:
    try:
        path = Path(path)
        salt = _load_or_create_salt(path.parent)
        if salt is None:
            return
        cache_id = identity if identity is not None else _compat_identity(roster, salt)
        if set(cache_id) != _CACHE_IDENTITY_KEYS:
            return
        payload = {
            "schema_version": cache_id["schema_version"],
            "roster": cache_id["roster"],
            "auth_presence": cache_id["auth_presence"],
            "credential_fingerprint": cache_id["credential_fingerprint"],
            "ts": time.time(),
            "results": _redact_cache_value(results, sensitive_values),
        }
        raw = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(raw) > CACHE_MAX_BYTES:
            return
        _atomic_write_private(path, raw)
    except Exception:
        pass  # cache yazılamaması asla akışı bozmaz


def _credential_values(lock, env):
    values = []
    for _row, server in _request_roster_rows(lock):
        auth_env = server.get("auth_env")
        value = env.get(auth_env) if auth_env else None
        if not value:
            continue
        try:
            text = value if isinstance(value, str) else str(value)
        except Exception:
            continue
        if text:
            values.append(text)
    return tuple(values)


def cached_probe(root, env, ttl: int = CACHE_TTL, fresh: bool = False) -> dict:
    """Cache'li prob. Lock yoksa veya her şey çökerse boş dict (fail-open)."""
    try:
        lock = load_lock(root)
        if not lock:
            return {}
        path = None
        identity = None
        try:
            path = _cache_path((lock or {}).get("plugin", ""))
            salt = _load_or_create_salt(path.parent)
            if salt is not None:
                identity = cache_identity(lock, env, salt)
        except Exception:
            path = None
            identity = None
        if not fresh and path is not None and identity is not None:
            cached = read_cache(path, ttl, identity=identity)
            if cached is not None:
                return cached
        results = probe_fleet(lock, env)
        if path is not None and identity is not None:
            write_cache(
                path,
                results,
                identity=identity,
                sensitive_values=_credential_values(lock, env),
            )
        return results
    except Exception:
        return {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cureonics canlı filo prob'u")
    ap.add_argument("--fresh", action="store_true", help="cache'i atla")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--root", help="plugin kökü (kanonik kopyadan koşarken zorunlu)")
    args = ap.parse_args(argv)

    here = Path(__file__).resolve()
    # Vendor edilmiş kopya: <plugin>/hooks/scripts/ → kök 2 üstte.
    # Kanonik kopya: <repo>/tools/fleetkit/ → --root ile plugin verilmeli.
    root = Path(args.root).resolve() if args.root else here.parent.parent.parent
    results = cached_probe(root, os.environ, fresh=args.fresh)

    if args.as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif not args.quiet:
        if not results:
            print("prob çalıştırılamadı (lock yok veya ağ kapalı) — "
                  "preflight env-only moda düşer", file=sys.stderr)
        for name in sorted(results):
            r = results[name]
            http = r.get("http") or "-"
            print("%s %-18s %-14s %4s %s" % (
                SYMBOL.get(r["status"], "?"), name, r["status"], http,
                (r.get("detail") or "")[:60]))
        tally = {}
        for r in results.values():
            tally[r["status"]] = tally.get(r["status"], 0) + 1
        print("— " + " · ".join(f"{k}: {v}" for k, v in sorted(tally.items())))
    return 0  # HER ZAMAN 0 — fail-open, oturumu asla bloklamaz


if __name__ == "__main__":
    sys.exit(main())
