#!/usr/bin/env python3
"""edupedia'nın carbon-edupedia skill'ini claude.ai Agent Skill paketine dönüştürür.

    python3 plugins/edupedia/scripts/build_claude_ai_skill.py
    → dist/carbon-edupedia-claude-ai.zip   (Settings → Customize → Skills → Upload)

NEDEN AYRI BİR PAKET: claude.ai'da tek uzantı noktası **Skill**'dir — hook, alt-ajan ve
slash-komut YOKTUR. Plugin'in `hooks/`, `agents/`, `commands/` bileşenleri oraya geçmez;
skill kendi başına yeterli olmak zorundadır. (Sözleşme akışı bu yüzden komutta değil
`references/curriculum-integration.md §3`'te yaşar — claude.ai'ın gördüğü yer orasıdır.)

ZIP YAPISI (spec — yanlışı sessizce reddedilir):
    carbon-edupedia-claude-ai.zip
    └── carbon-edupedia/          ← klasör KÖKTE olmalı
        ├── SKILL.md
        ├── references/*.md
        └── assets/*
SKILL.md'yi zip köküne koymak GEÇERSİZDİR.

DIŞLANANLAR: tests/ docs/ evals/ __pycache__ .pytest_cache — geliştirme yükü (~670KB).
claude.ai'a gitmelerinin faydası yok, 30MB bütçesini ve indirme süresini yer.

`scripts/` DAHİL EDİLİR: claude.ai kod-çalıştırma açıkken script koşturabilir, yani
`validate_module.py` yerel ön-kontrol olarak işe yarar. Ama OTORİTE DEĞİLDİR — kapıları
yayın sunucusu ölçer. Koşmazsa üretim yine çalışır (kapı 422'de görünür).
"""
from __future__ import annotations

import re
import shutil
import sys
import zipfile
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SKILL_SRC = PLUGIN / "skills" / "carbon-edupedia"
SKILL_NAME = "carbon-edupedia"
OUT_DIR = PLUGIN / "dist"
OUT_ZIP = OUT_DIR / f"{SKILL_NAME}-claude-ai.zip"

# claude.ai spec limitleri (ölçülür, varsayılmaz)
MAX_ZIP_BYTES = 30 * 1024 * 1024
MAX_NAME = 64
MAX_DESC = 1024

EXCLUDE_DIRS = {"tests", "docs", "evals", "__pycache__", ".pytest_cache"}
EXCLUDE_SUFFIX = {".pyc", ".pyo"}


def _iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix in EXCLUDE_SUFFIX:
            continue
        yield p


def _check_frontmatter(skill_md: Path) -> list[str]:
    """claude.ai Agent Skill frontmatter kurallarını ÖLÇ (uydurma)."""
    hatalar: list[str] = []
    t = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return ["SKILL.md YAML frontmatter ile başlamıyor"]
    fm = m.group(1)

    nm = re.search(r"^name:\s*(.+?)\s*$", fm, re.M)
    if not nm:
        hatalar.append("frontmatter'da `name` yok (zorunlu)")
    else:
        name = nm.group(1).strip().strip("\"'")
        if len(name) > MAX_NAME:
            hatalar.append(f"name {len(name)} kar. (>{MAX_NAME})")
        if not re.fullmatch(r"[a-z0-9-]+", name):
            hatalar.append(f"name '{name}' — yalnız küçük harf/rakam/tire olmalı")
        if "anthropic" in name.lower() or "claude" in name.lower():
            hatalar.append(f"name '{name}' rezerve kelime içeriyor (anthropic/claude)")

    # description: düz ya da katlanmış (>-) blok olabilir
    dm = re.search(r"^description:\s*(?:>-?\s*\n((?:[ \t]+.*\n?)+)|(.+))", fm, re.M)
    if not dm:
        hatalar.append("frontmatter'da `description` yok (zorunlu — tetikleme SADECE buradan)")
    else:
        desc = (dm.group(1) or dm.group(2) or "").strip()
        if not desc:
            hatalar.append("description boş")
        if len(desc) > MAX_DESC:
            hatalar.append(f"description {len(desc)} kar. (>{MAX_DESC}) — {len(desc)-MAX_DESC} fazla")
        if re.search(r"<[a-zA-Z/][^>]*>", desc):
            hatalar.append("description XML/HTML etiketi içeriyor (yasak)")
    return hatalar


def main() -> int:
    if not (SKILL_SRC / "SKILL.md").is_file():
        print(f"HATA: {SKILL_SRC}/SKILL.md yok", file=sys.stderr)
        return 1

    hatalar = _check_frontmatter(SKILL_SRC / "SKILL.md")
    if hatalar:
        print("✘ claude.ai frontmatter spec ihlali:", file=sys.stderr)
        for h in hatalar:
            print(f"    - {h}", file=sys.stderr)
        return 1
    print("✔ frontmatter: name + description claude.ai spec'ine uygun")

    OUT_DIR.mkdir(exist_ok=True)
    if OUT_ZIP.exists():
        OUT_ZIP.unlink()

    n = 0
    atlanan = 0
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in _iter_files(SKILL_SRC):
            rel = p.relative_to(SKILL_SRC)
            z.write(p, arcname=str(Path(SKILL_NAME) / rel))  # ← klasör KÖKTE
            n += 1
    for p in SKILL_SRC.rglob("*"):
        if p.is_file() and (
            any(part in EXCLUDE_DIRS for part in p.relative_to(SKILL_SRC).parts)
            or p.suffix in EXCLUDE_SUFFIX
        ):
            atlanan += 1

    boyut = OUT_ZIP.stat().st_size
    if boyut > MAX_ZIP_BYTES:
        print(f"✘ zip {boyut/1e6:.1f} MB > 30 MB limiti", file=sys.stderr)
        return 1

    # Yapıyı ZIP'İN KENDİSİNDEN doğrula — niyetten değil.
    with zipfile.ZipFile(OUT_ZIP) as z:
        adlar = z.namelist()
    kok = f"{SKILL_NAME}/SKILL.md"
    if kok not in adlar:
        print(f"✘ zip'te {kok} yok — klasör-kök yapısı bozuk", file=sys.stderr)
        return 1
    if "SKILL.md" in adlar:
        print("✘ SKILL.md zip KÖKÜNDE — spec klasör-kök ister", file=sys.stderr)
        return 1
    sizinti = [a for a in adlar if any(f"/{d}/" in f"/{a}" for d in EXCLUDE_DIRS)]
    if sizinti:
        print(f"✘ dışlanan dizin zip'e sızdı: {sizinti[:3]}", file=sys.stderr)
        return 1

    print(f"✔ yapı    : {kok} (klasör kökte)")
    print(f"✔ içerik  : {n} dosya | {atlanan} geliştirme dosyası dışlandı")
    print(f"✔ boyut   : {boyut/1024:.0f} KB  (limit 30 MB — %{boyut/MAX_ZIP_BYTES*100:.1f})")
    print(f"\n→ {OUT_ZIP}")
    print("  Yükleme: claude.ai → Settings → Customize → Skills → Upload")
    print("  UNUTMA: connector'lar AYRI eklenir (Settings → Customize → Connectors).")
    print("          Skill bir connector'ı talep EDEMEZ — bağımlılık mekanizması yok.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
