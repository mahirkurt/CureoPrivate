#!/usr/bin/env python3
"""Cureonics marketplace SÖZLEŞME kapısı — AĞ ERİŞİMİ GEREKTİRMEZ, CI'da güvenle koşar.

check_drift.py filonun TÜRETİLMİŞLİĞİNİ denetler (fleet.yaml → .mcp.json/lock,
sürüm zinciri, sunucu kimliği). Bu dosya farklı bir şeyi denetler: paketin
Claude Code marketplace sözleşmesine uyup uymadığını — yani GitHub'dan
`/plugin marketplace add mahirkurt/CureoPrivate` ile kurulduğunda connector,
skill, agent, komut ve hook katmanlarının GERÇEKTEN yüklenip yüklenmeyeceğini.

Altı denetim (hepsi deterministik, hepsi offline):
  [1] Katalog ↔ disk        marketplace.json plugin'leri ↔ plugins/*/ + zorunlu alanlar
  [2] Skill frontmatter     name + description var mı, name == dizin adı mı
  [3] Agent frontmatter     name + description var mı, name == dosya adı mı
  [4] Komut frontmatter     description var mı (yoksa /komut menüde boş görünür)
  [5] Hook sözleşmesi       geçerli olay · betik mevcut · CLAUDE_PLUGIN_ROOT · timeout
  [6] Hook betiği sözdizimi her .py derleniyor mu
  [7] Manifest yolları      plugin.json / .cursor-plugin bildirilen path gerçek ve `..`'suz

NEDEN VAR: bu katmanların hiçbiri türetilmiyor, dolayısıyla check_drift onları
görmüyordu. Bir SKILL.md'nin `name`'i dizin adından saparsa skill sessizce
keşfedilemez; bir hook betiği yeniden adlandırılırsa hook her oturumda sessizce
düşer; bir komutun `description`'ı yoksa /komut menüsünde boş satır çıkar.
Hiçbiri hata vermez — sadece ÇALIŞMAZ. Bu kapı o sessiz sınıf içindir.

Kullanım:
  python3 tools/fleetkit/check_marketplace.py
  python3 tools/fleetkit/check_marketplace.py --quiet
Çıkış: 0 temiz · 1 sözleşme ihlali.
"""
import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
CATALOG = REPO / ".claude-plugin" / "marketplace.json"

# Claude Code'un tanıdığı hook olayları. Listede olmayan bir olay, kaydında
# açıklayıcı bir `_comment` taşıyorsa BİLİNÇLİ ileri-uyum bahsi sayılır
# (bilinmeyen olay zararsızca yoksayılır); taşımıyorsa yazım hatası muamelesi
# görür — çünkü sessizce hiç çalışmayan bir hook, olmayan hooktan beterdir.
VALID_EVENTS = {
    "PreToolUse", "PostToolUse", "Stop", "SubagentStop", "SessionStart",
    "SessionEnd", "UserPromptSubmit", "PreCompact", "Notification",
}
# marketplace.json'da her plugin kaydının taşıması gereken alanlar.
# İKİYE AYRILIR: `strict` bir BOOLEAN'dır ve meşru değeri `false`'tur — varlık
# yerine doğruluk denetlenirse her `strict: false` kaydı yanlış-pozitif verir.
CATALOG_FIELDS_NONEMPTY = ("name", "displayName", "source", "version",
                           "description", "author", "category", "keywords")
CATALOG_FIELDS_PRESENT = ("strict",)


class BadFrontmatter(Exception):
    """Frontmatter GERÇEK bir YAML parser'ından geçmedi."""


def frontmatter(path: Path):
    """Frontmatter'ı GERÇEK YAML parser'ıyla ayrıştır.

    Önceki uygulama satır-bazlı bir regex kullanıyordu ve bu yüzden 2026-08-07
    denetiminin K-4 bulgusunu KAÇIRDI: `description:` değeri tırnaksız düz
    skalar içinde `": "` taşıyorsa (`… Yabancı ülke mevzuatı: health-policy …`)
    YAML bunu iç içe mapping sanar ve **tüm frontmatter düşer** — komut
    keşfedilemez hâle gelir. Regex böyle bir satırı sorunsuz okuyup "geçerli"
    raporluyordu. Artık gerçek parser koşuyor; PyYAML neyi reddediyorsa Claude
    Code da onu reddedecektir.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError as e:
        raise BadFrontmatter(str(e).splitlines()[0]) from None
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise BadFrontmatter(f"frontmatter mapping değil ({type(data).__name__})")
    return {k: (" ".join(str(v).split()) if isinstance(v, str) else v)
            for k, v in data.items()}


def iter_command_hooks(node):
    """hooks.json ağacındaki her {type: command} düğümünü yüzeye çıkar."""
    if isinstance(node, dict):
        if node.get("type") == "command" and "command" in node:
            yield node
        for v in node.values():
            yield from iter_command_hooks(v)
    elif isinstance(node, list):
        for v in node:
            yield from iter_command_hooks(v)


def check_catalog(catalog):
    issues = []
    on_disk = {p.name for p in (REPO / "plugins").iterdir() if p.is_dir()}
    listed = {p["name"] for p in catalog["plugins"]}
    for miss in sorted(listed - on_disk):
        issues.append(f"katalogda var, diskte YOK: {miss}")
    for miss in sorted(on_disk - listed):
        issues.append(f"diskte var, katalogda YOK (kurulamaz): {miss}")
    for p in catalog["plugins"]:
        for f in CATALOG_FIELDS_NONEMPTY:
            if not p.get(f):
                issues.append(f"{p.get('name', '?')}: katalog alanı eksik '{f}'")
        for f in CATALOG_FIELDS_PRESENT:
            if f not in p:
                issues.append(f"{p.get('name', '?')}: katalog alanı eksik '{f}' "
                              f"(boolean — değeri false olabilir, ama BULUNMALI)")
        src = REPO / p.get("source", "").lstrip("./")
        if p.get("source") and not (src / ".claude-plugin" / "plugin.json").is_file():
            issues.append(f"{p['name']}: source → {p['source']} altında plugin.json yok")
    return issues


def _declared_path_ok(root: Path, rel: str, field: str, value, issues: list) -> None:
    """Manifestteki bileşen yolu plugin dizini içinde ve gerçekten var mı?"""
    paths = value if isinstance(value, list) else [value]
    for item in paths:
        if not isinstance(item, str):
            continue
        p = Path(item)
        if p.is_absolute() or ".." in p.parts:
            issues.append(f"{rel}: {field} mutlak veya `..` içeriyor → {item}")
            continue
        target = root / item
        if not target.exists():
            issues.append(f"{rel}: {field} yolu yok → {item}")


def check_plugin(root: Path):
    """Bir plugin dizininin bileşen sözleşmesini denetle."""
    issues = []

    for sk in sorted(root.glob("skills/*/SKILL.md")):
        rel = sk.relative_to(REPO)
        try:
            d = frontmatter(sk)
        except BadFrontmatter as e:
            issues.append(f"{rel}: GEÇERSİZ YAML frontmatter — {e}"); continue
        if d is None:
            issues.append(f"{rel}: frontmatter YOK — skill keşfedilemez")
            continue
        for f in ("name", "description"):
            if not d.get(f):
                issues.append(f"{rel}: frontmatter '{f}' eksik")
        if d.get("name") and d["name"] != sk.parent.name:
            issues.append(f"{rel}: name='{d['name']}' ≠ dizin '{sk.parent.name}'")

    for ag in sorted(root.glob("agents/*.md")):
        rel = ag.relative_to(REPO)
        try:
            d = frontmatter(ag)
        except BadFrontmatter as e:
            issues.append(f"{rel}: GEÇERSİZ YAML frontmatter — {e}"); continue
        if d is None:
            issues.append(f"{rel}: frontmatter YOK — agent kaydedilmez")
            continue
        for f in ("name", "description"):
            if not d.get(f):
                issues.append(f"{rel}: frontmatter '{f}' eksik")
        if d.get("name") and d["name"] != ag.stem:
            issues.append(f"{rel}: name='{d['name']}' ≠ dosya '{ag.stem}'")

    for cm in sorted(root.glob("commands/*.md")):
        rel = cm.relative_to(REPO)
        try:
            d = frontmatter(cm)
        except BadFrontmatter as e:
            issues.append(f"{rel}: GEÇERSİZ YAML frontmatter — {e} "
                          f"(komut keşfedilemez hâle gelir)"); continue
        if d is None or not d.get("description"):
            issues.append(f"{rel}: 'description' eksik — /komut menüsünde boş görünür")

    hj = root / "hooks" / "hooks.json"
    if hj.is_file():
        try:
            doc = json.loads(hj.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            return issues + [f"{hj.relative_to(REPO)}: BOZUK JSON — {e}"]
        events = doc.get("hooks", doc)
        for ev, body in events.items():
            if ev.startswith("_") or ev in VALID_EVENTS:
                continue
            if "_comment" not in json.dumps(body, ensure_ascii=False):
                issues.append(f"{hj.relative_to(REPO)}: bilinmeyen olay '{ev}' "
                              f"(gerekçe `_comment`'i yok — yazım hatası mı?)")
        for hook in iter_command_hooks(events):
            cmd = hook["command"]
            if "CLAUDE_PLUGIN_ROOT" not in cmd:
                issues.append(f"{hj.relative_to(REPO)}: taşınabilir değil "
                              f"(CLAUDE_PLUGIN_ROOT yok) → {cmd[:60]}")
            if "timeout" not in hook:
                issues.append(f"{hj.relative_to(REPO)}: timeout yok → {cmd[:60]}")
            for m in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)", cmd):
                if not (root / m).exists():
                    issues.append(f"{hj.relative_to(REPO)}: hook betiği YOK → {m}")

    for py in sorted(root.glob("hooks/scripts/*.py")):
        try:
            compile(py.read_text(encoding="utf-8"), str(py), "exec")
        except SyntaxError as e:
            issues.append(f"{py.relative_to(REPO)}:{e.lineno}: sözdizimi hatası — {e.msg}")

    man_path = root / ".claude-plugin" / "plugin.json"
    if man_path.is_file():
        try:
            man = json.loads(man_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            issues.append(f"{man_path.relative_to(REPO)}: BOZUK JSON — {e}")
            man = None
        if isinstance(man, dict):
            rel = str(man_path.relative_to(REPO))
            for field in ("mcpServers", "hooks", "skills", "commands", "agents"):
                if field in man:
                    _declared_path_ok(root, rel, field, man[field], issues)

    cursor_path = root / ".cursor-plugin" / "plugin.json"
    if cursor_path.is_file():
        rel = str(cursor_path.relative_to(REPO))
        try:
            cur = json.loads(cursor_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            issues.append(f"{rel}: BOZUK JSON — {e}")
            cur = None
        if isinstance(cur, dict):
            if not cur.get("name"):
                issues.append(f"{rel}: 'name' eksik — Cursor plugin keşfedilemez")
            for field in ("mcpServers", "hooks", "skills", "commands", "agents", "rules"):
                if field in cur:
                    _declared_path_ok(root, rel, field, cur[field], issues)

    return issues


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cureonics marketplace sözleşme kapısı")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    failed = False

    cat_issues = check_catalog(catalog)
    if cat_issues:
        failed = True
        if not a.quiet:
            print("\n⚠ katalog (.claude-plugin/marketplace.json)")
            for i in cat_issues:
                print(f"      · {i}")
    elif not a.quiet:
        print(f"✓ katalog                {len(catalog['plugins'])} plugin, alanlar tam")

    for p in sorted(catalog["plugins"], key=lambda x: x["name"]):
        root = REPO / p["source"].lstrip("./")
        if not root.is_dir():
            continue
        issues = check_plugin(root)
        counts = (len(list(root.glob("skills/*/SKILL.md"))),
                  len(list(root.glob("agents/*.md"))),
                  len(list(root.glob("commands/*.md"))),
                  len(list(root.glob("hooks/scripts/*.py"))))
        if issues:
            failed = True
            if not a.quiet:
                print(f"\n⚠ {p['name']}")
                for i in issues:
                    print(f"      · {i}")
        elif not a.quiet:
            print(f"✓ {p['name']:22s} {counts[0]:>2d} skill · {counts[1]:>2d} agent · "
                  f"{counts[2]:>2d} komut · {counts[3]:>2d} hook betiği")

    if not a.quiet:
        print(f"\n{'SÖZLEŞME İHLALİ' if failed else 'MARKETPLACE SÖZLEŞMESİ TEMİZ'} — "
              f"{len(catalog['plugins'])} plugin denetlendi")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
