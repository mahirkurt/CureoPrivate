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
        ├── plugin-context/*      ← VENDOR: plugin kökündeki normatif belgeler
        └── assets/*
SKILL.md'yi zip köküne koymak GEÇERSİZDİR.

VENDOR — NEDEN VAR (2026-07-17): skill, plugin düzeninde `../../../CONNECTORS.md` gibi
paket-DIŞI yollara referans verir. Bu yollar Claude Code'da DOĞRUdur (plugin ağacı oradadır)
ama zip'in kökü `carbon-edupedia/` olduğu için claude.ai'da hepsi kırık bağlantıya dönüşür —
üstelik biri connector envanterinin "tek doğruluk kaynağı" ilan edilen CONNECTORS.md'dir.
Kaynak yanlış değil, PAKETLEYİCİ eksikti. Çözüm: normatif belgeler `plugin-context/`e
vendor'lanır ve bağlantılar derinlik-duyarlı olarak yeniden yazılır.

`commands/*.md` VENDOR'LANMAZ: claude.ai'da komut diye bir şey yok. O bağlantılar, taşıdıkları
tek anlam olan komut ADINA indirgenir (`../commands/modul.md` → `/edupedia:modul`).

KAPI: paket kurulduktan sonra ZIP'İN İÇİNDEN doğrulanır — paketlenmiş her .md'deki `../`
ile kaçan her .md/.json bağlantısı zip üyesi olmak ZORUNDA. Değilse build DURUR. Bu kapı
niyeti değil ARTEFAKTI ölçer: yeni bir paket-dışı referans eklenirse sessizce sızamaz.

DIŞLANANLAR: tests/ docs/ evals/ __pycache__ .pytest_cache — geliştirme yükü (~670KB).
(docs/ dışlanır ama denetlenebilirlik kanıtı olan MCP introspeksiyon çıktısı vendor'lanır.)

`scripts/` DAHİL EDİLİR: claude.ai kod-çalıştırma açıkken script koşturabilir, yani
`validate_module.py` kalite kapısı olarak işe yarar. Koşmazsa üretim yine çalışır;
kapıları "PASS" diye beyan etmeyin.
"""
from __future__ import annotations

import posixpath
import re
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

# Paket-dışı normatif belgeler → zip içinde bu dizine taşınır.
VENDOR_DIR = "plugin-context"
VENDOR: dict[str, Path] = {
    "CONNECTORS.md": PLUGIN / "CONNECTORS.md",
    "canonical-cache-contract.md": PLUGIN / "shared" / "canonical-cache-contract.md",
    "run-manifest-schema.json": PLUGIN / "shared" / "run-manifest-schema.json",
    "mcp-introspection-2026-07-06.json": PLUGIN / "docs" / "mcp-introspection-2026-07-06.json",
}

# `../commands/modul.md` → `/edupedia:modul` (claude.ai'da dosya yok, komut adı var)
CMD_RE = re.compile(r"(?:\.{1,2}/)+commands/([a-z][a-z0-9-]*)\.md")
# `../../../CONNECTORS.md`, `./shared/run-manifest-schema.json`, … → plugin-context/<ad>
VENDOR_RE = re.compile(
    r"(?:\.{1,2}/)+(?:[A-Za-z0-9_.-]+/)*(" + "|".join(re.escape(b) for b in VENDOR) + r")"
)
# Kapı: `../` ile paket kökünden kaçan .md/.json bağlantıları
ESCAPE_RE = re.compile(r"(?<![\w-])((?:\.\./)+[A-Za-z0-9_./-]*\.(?:md|json))")

# Rewrite + kapı bu uzantılara uygulanır. YAML dâhil: skill-manifest.yaml'ın `read_when`
# metinleri de modelin okuduğu navigasyondur ve o da `../../CONNECTORS.md` diyordu.
TEXT_SUFFIX = {".md", ".yaml"}


def _iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix in EXCLUDE_SUFFIX:
            continue
        yield p


def _rewrite(text: str, pkg_rel: str) -> str:
    """Paket-dışı bağlantıları paket-içi gerçeğe çevir. pkg_rel = zip içindeki yol."""
    here = posixpath.dirname(pkg_rel)

    def _vendor_sub(m: re.Match[str]) -> str:
        return posixpath.relpath(f"{VENDOR_DIR}/{m.group(1)}", here or ".")

    text = CMD_RE.sub(lambda m: f"/edupedia:{m.group(1)}", text)
    return VENDOR_RE.sub(_vendor_sub, text)


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


def _gate_links(zip_path: Path) -> list[str]:
    """ZIP'İN İÇİNDEN ölç: kaçan her bağlantı gerçekten pakette mi?"""
    ihlaller: list[str] = []
    with zipfile.ZipFile(zip_path) as z:
        uyeler = set(z.namelist())
        for ad in sorted(uyeler):
            if not any(ad.endswith(s) for s in TEXT_SUFFIX):
                continue
            metin = z.read(ad).decode("utf-8")
            govde = posixpath.relpath(ad, SKILL_NAME)  # SKILL.md, references/x.md, …
            here = posixpath.dirname(govde)
            for link in ESCAPE_RE.findall(metin):
                hedef = posixpath.normpath(posixpath.join(here, link))
                if hedef.startswith(".."):
                    ihlaller.append(f"{govde}: `{link}` → paket KÖKÜNÜN dışına çıkıyor")
                elif f"{SKILL_NAME}/{hedef}" not in uyeler:
                    ihlaller.append(f"{govde}: `{link}` → `{hedef}` zip'te YOK")
    return ihlaller


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

    eksik = [f"{ad} ({yol})" for ad, yol in VENDOR.items() if not yol.is_file()]
    if eksik:
        print("✘ vendor kaynağı yok:", file=sys.stderr)
        for e in eksik:
            print(f"    - {e}", file=sys.stderr)
        return 1

    # Paket içeriğini kur: zip yolu → bayt
    icerik: dict[str, bytes] = {}
    for p in _iter_files(SKILL_SRC):
        rel = p.relative_to(SKILL_SRC).as_posix()
        if p.suffix in TEXT_SUFFIX:
            icerik[rel] = _rewrite(p.read_text(encoding="utf-8"), rel).encode("utf-8")
        else:
            icerik[rel] = p.read_bytes()
    for ad, yol in VENDOR.items():
        rel = f"{VENDOR_DIR}/{ad}"
        if yol.suffix in TEXT_SUFFIX:
            icerik[rel] = _rewrite(yol.read_text(encoding="utf-8"), rel).encode("utf-8")
        else:
            icerik[rel] = yol.read_bytes()

    atlanan = sum(
        1
        for p in SKILL_SRC.rglob("*")
        if p.is_file()
        and (
            any(part in EXCLUDE_DIRS for part in p.relative_to(SKILL_SRC).parts)
            or p.suffix in EXCLUDE_SUFFIX
        )
    )

    OUT_DIR.mkdir(exist_ok=True)
    if OUT_ZIP.exists():
        OUT_ZIP.unlink()
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, veri in sorted(icerik.items()):
            z.writestr(f"{SKILL_NAME}/{rel}", veri)  # ← klasör KÖKTE

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

    kirik = _gate_links(OUT_ZIP)
    if kirik:
        print(f"✘ KIRIK BAĞLANTI KAPISI — {len(kirik)} paket-dışı referans:", file=sys.stderr)
        for k in kirik:
            print(f"    - {k}", file=sys.stderr)
        print(
            "\n  Çözüm: normatif bir belgeyse VENDOR'a ekleyin; Claude Code'a özgü bir\n"
            "  yüzeyse (komut/hook/ajan) kaynakta dosya bağlantısı yerine ADINI yazın.",
            file=sys.stderr,
        )
        return 1

    vendor_uye = sum(1 for a in adlar if f"/{VENDOR_DIR}/" in a)
    print(f"✔ yapı    : {kok} (klasör kökte)")
    print(f"✔ vendor  : {vendor_uye} normatif belge → {VENDOR_DIR}/ (bağlantılar yeniden yazıldı)")
    print("✔ bağlantı: paket-dışı kırık referans yok (zip'ten ölçüldü)")
    print(f"✔ içerik  : {len(adlar)} dosya | {atlanan} geliştirme dosyası dışlandı")
    print(f"✔ boyut   : {boyut/1024:.0f} KB  (limit 30 MB — %{boyut/MAX_ZIP_BYTES*100:.1f})")
    print(f"\n→ {OUT_ZIP}")
    print("  Yükleme: claude.ai → Settings → Customize → Skills → Upload")
    print("  UNUTMA: connector'lar AYRI eklenir (Settings → Customize → Connectors).")
    print("          Skill bir connector'ı talep EDEMEZ — bağımlılık mekanizması yok.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
