#!/usr/bin/env python3
"""edupedia yüzey paketlerini tek başlangıç talimatından üretir (spec §9.1–§9.2).

    python3 plugins/edupedia/scripts/build_surfaces.py           # yaz
    python3 plugins/edupedia/scripts/build_surfaces.py --check   # yazma; bayat/beklenmeyen dosya varsa exit 1
    python3 plugins/edupedia/scripts/build_surfaces.py --zip     # yaz + dist/edupedia-claude-ai.zip

Kaynaklar: surfaces/bootstrap.md (model talimatı, ≤ 3.500 karakter) ve fleet.lock.json (sürüm ve
anahtarsız `tedy` ucu; tools/fleetkit/gen_fleet.py fleet.yaml'dan üretir). Yalnız stdlib.

NEDEN TEK GÖVDE: claude.ai, Codex, Grok ve Gemini'de hook, alt-ajan ve komut yoktur; bütün derinlik
ted-mcp'dedir. Yüzeyler arasında talimat farkı, aynı orkestratöre farklı kurallarla gelen istemci demektir.
Kurulum adımları talimata girmez — KURULUM.md'dedir. check_drift [7] bu betiği --check ile koşar.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
BOOTSTRAP = "surfaces/bootstrap.md"
BOOTSTRAP_MAX_CHARS = 3500
PRIMARY_SERVER = "tedy"
SKILL_NAME = "edupedia"
SKILL_DESCRIPTION = (
    "TEDY edupedia — Türkiye Yüzyılı Maarif Modeli'ne hizalı etkileşimli öğrenim modüllerini tedy MCP "
    "orkestratörüyle üretir, derler ve tedy.online aile kataloğunda yayınlar. Modül, quiz, flashcard, "
    "sınav sorusu çözümü, kazanım bulma, modül kataloğu ve ilerleme isteklerinde kullan."
)
ZIP_NAME = "edupedia-claude-ai.zip"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


class SurfaceError(ValueError):
    """Kaynaklar yüzey üretimine uygun değil (talimat bütçesi aşıldı, anahtarsız tedy yok)."""


def _sources(root: Path) -> tuple[str, str, str]:
    body = (root / BOOTSTRAP).read_text(encoding="utf-8")
    if len(body) > BOOTSTRAP_MAX_CHARS:
        raise SurfaceError(f"{BOOTSTRAP}: {len(body)} karakter > {BOOTSTRAP_MAX_CHARS}")
    lock = json.loads((root / "fleet.lock.json").read_text(encoding="utf-8"))
    tedy = next((s for s in lock.get("servers", []) if s.get("name") == PRIMARY_SERVER), None)
    if tedy is None or tedy.get("auth_env") is not None or not tedy.get("url"):
        raise SurfaceError("fleet.lock.json: anahtarsız 'tedy' sunucusu yok")
    return body, lock["plugin_version"], tedy["url"]


def _skill(body: str, version: str) -> str:
    return (
        "---\n"
        f"name: {SKILL_NAME}\n"
        f"description: {json.dumps(SKILL_DESCRIPTION, ensure_ascii=False)}\n"
        "metadata:\n"
        f'  version: "{version}"\n'
        f"  generated_from: {BOOTSTRAP}\n"
        "---\n\n" + body
    )


def _servers(url: str) -> dict:
    return {PRIMARY_SERVER: {"type": "http", "url": url}}


def _codex_plugin(version: str, url: str) -> str:
    manifest = {
        "name": SKILL_NAME,
        "version": version,
        "description": "TEDY edupedia ince istemcisi — tek başlangıç skill'i ve tedy MCP orkestratörü (OAuth).",
        "author": {"name": "Cureonics", "url": "https://cureonics.com"},
        "homepage": "https://cureonics.com",
        "license": "MIT",
        "skills": "./skills/",
        "mcpServers": _servers(url),
        "interface": {
            "displayName": "Edupedia",
            "shortDescription": "Maarif Modeli modüllerini TEDY orkestratörüyle üretip tedy.online'da yayınlar.",
            "developerName": "Cureonics",
            "category": "Education",
            "capabilities": ["Interactive", "Read", "Write"],
            "defaultPrompt": [
                "Işık'ın yaklaşan bir sınavı için QUIZ modunda edupedia modülü hazırla.",
                "5. sınıf Fen Bilimleri maddenin hâlleri kazanımlarını bul.",
            ],
        },
    }
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def render(root: Path = PLUGIN) -> dict[str, str]:
    """Yüzey dosyaları: plugin köküne göre yol → içerik."""
    body, version, url = _sources(root)
    skill = _skill(body, version)
    return {
        "skills/edupedia/SKILL.md": skill,
        "surfaces/claude-ai/edupedia/SKILL.md": skill,
        "surfaces/codex/.codex-plugin/plugin.json": _codex_plugin(version, url),
        "surfaces/codex/skills/edupedia/SKILL.md": skill,
        "surfaces/codex/mcp.json": json.dumps({"mcpServers": _servers(url)}, ensure_ascii=False, indent=2) + "\n",
        "surfaces/grok/grok-workspace.md": body,
        "surfaces/gemini/gemini-gem.md": body,
    }


def _out_of_sync(root: Path, expected: dict[str, str]) -> bool:
    """Yedi paketten biri bile diskteki içerikle uyuşmuyorsa True — parti tek gövde sayılır."""
    return any(
        not (root / rel).is_file() or (root / rel).read_text(encoding="utf-8") != text
        for rel, text in expected.items()
    )


def stale(root: Path = PLUGIN) -> list[str]:
    """Bayat ya da eksik paketler + surfaces/ altında üreticinin tanımadığı dosyalar.

    Yedi paket tek bir türetimin ürünüdür (aynı bootstrap.md + fleet.lock.json): biri bile
    kaynaklarla uyuşmuyorsa parti bütünüyle bayat sayılır — örneğin yalnız bootstrap.md
    düzenlendiğinde codex mcp.json'ın baytları değişmez, ama o da yeniden yazılacak partinin
    parçasıdır.
    """
    expected = render(root)
    out = list(expected) if _out_of_sync(root, expected) else []
    present = {p.relative_to(root).as_posix() for p in (root / "surfaces").rglob("*") if p.is_file()}
    out += [f"{rel} (beklenmeyen)" for rel in sorted(present - set(expected) - {BOOTSTRAP})]
    return out


def write(root: Path = PLUGIN) -> list[str]:
    """Parti kaynaklarla uyuşmuyorsa yedi paketin tümünü yazar (bkz. stale())."""
    expected = render(root)
    if not _out_of_sync(root, expected):
        return []
    for rel, text in expected.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return list(expected)


def build_zip(root: Path = PLUGIN) -> Path:
    """claude.ai skill zip'i: kökte `edupedia/SKILL.md`, sabit zaman damgası → bayt-deterministik."""
    data = render(root)["surfaces/claude-ai/edupedia/SKILL.md"].encode("utf-8")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        info = zipfile.ZipInfo(f"{SKILL_NAME}/SKILL.md", date_time=ZIP_EPOCH)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        zf.writestr(info, data)
    target = root / "dist" / ZIP_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(buf.getvalue())
    return target


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="edupedia yüzey paketi üreticisi")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="yazma; bayat ya da beklenmeyen dosya varsa exit 1")
    mode.add_argument("--zip", action="store_true", help="yaz ve dist/edupedia-claude-ai.zip üret")
    args = ap.parse_args(argv)
    try:
        if args.check:
            problems = stale()
            for line in problems:
                print(line)
            return 1 if problems else 0
        for rel in write():
            print(f"yazıldı: {rel}")
        if args.zip:
            print(f"zip: {build_zip().relative_to(PLUGIN)}")
        return 0
    except (SurfaceError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
