#!/usr/bin/env python3
"""Cureonics marketplace SÖZLEŞME kapısı — AĞ ERİŞİMİ GEREKTİRMEZ, CI'da güvenle koşar.

check_drift.py filonun TÜRETİLMİŞLİĞİNİ denetler (fleet.yaml → .mcp.json/lock,
sürüm zinciri, sunucu kimliği). Bu dosya farklı bir şeyi denetler: paketin
Claude Code marketplace sözleşmesine uyup uymadığını — yani GitHub'dan
`/plugin marketplace add mahirkurt/CureoPrivate` ile kurulduğunda connector,
skill, agent, komut ve hook katmanlarının GERÇEKTEN yüklenip yüklenmeyeceğini.

Yedi denetim (hepsi deterministik, hepsi offline):
  [1] Katalog ↔ disk        marketplace.json plugin'leri ↔ plugins/*/ + zorunlu alanlar
  [2] Skill frontmatter     name + description var mı, name == dizin adı mı
  [3] Agent frontmatter     name + description var mı, name == dosya adı mı
  [4] Komut frontmatter     description var mı (yoksa /komut menüde boş görünür)
  [5] Hook sözleşmesi       platform şeması · olay · betik · host root · timeout · çıktı
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
CLAUDE_VALID_EVENTS = {
    "PreToolUse", "PostToolUse", "Stop", "SubagentStop", "SessionStart",
    "SessionEnd", "UserPromptSubmit", "PreCompact", "Notification",
}
CURSOR_VALID_EVENTS = {
    "workspaceOpen", "sessionStart", "sessionEnd", "preToolUse", "postToolUse",
    "postToolUseFailure", "subagentStart", "subagentStop",
    "beforeShellExecution", "afterShellExecution", "beforeMCPExecution",
    "afterMCPExecution", "beforeReadFile", "afterFileEdit",
    "beforeSubmitPrompt", "preCompact", "stop", "afterAgentResponse",
    "afterAgentThought", "beforeTabFileRead", "afterTabFileEdit",
}
CURSOR_COMMAND_RE = re.compile(
    r'^/usr/bin/env python3 "\$\{CURSOR_PLUGIN_ROOT\}/([^"]+)"$'
)
CURSOR_COMMON_FIELDS = {
    "type", "command", "timeout", "matcher", "failClosed", "loop_limit",
}
CURSOR_EVENT_FIELDS = {
    "sessionStart": {"type", "command", "timeout", "failClosed"},
    "postToolUse": {"type", "command", "timeout", "matcher", "failClosed"},
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


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _command_target(root: Path, rel: str, label: str, issues: list[str]) -> Path | None:
    path = Path(rel)
    if path.is_absolute() or ".." in path.parts:
        issues.append(f"{label}: hook betiği yolu mutlak veya `..` içeriyor → {rel}")
        return None
    target = (root / path).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        issues.append(f"{label}: hook betiği plugin kökü dışına çözülüyor → {rel}")
        return None
    if not target.is_file():
        issues.append(f"{label}: hook betiği YOK → {rel}")
        return None
    return target


def _check_claude_hooks(root: Path, path: Path, doc: dict) -> list[str]:
    issues: list[str] = []
    label = _display_path(path)
    events = doc.get("hooks", doc)
    if not isinstance(events, dict):
        return [f"{label}: Claude hooks mapping değil"]

    for event, body in events.items():
        if event.startswith("_"):
            continue
        if event not in CLAUDE_VALID_EVENTS:
            if "_comment" not in json.dumps(body, ensure_ascii=False):
                issues.append(
                    f"{label}: bilinmeyen olay '{event}' "
                    f"(gerekçe `_comment`'i yok — yazım hatası mı?)"
                )
        if not isinstance(body, list):
            issues.append(f"{label}: Claude olayı '{event}' liste değil")
            continue
        for group in body:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                issues.append(
                    f"{label}: Claude olayı '{event}' nested `hooks` listesi taşımıyor"
                )

    for hook in iter_command_hooks(events):
        cmd = hook["command"]
        if not isinstance(cmd, str):
            issues.append(f"{label}: Claude hook command metin değil")
            continue
        if "CLAUDE_PLUGIN_ROOT" not in cmd:
            issues.append(
                f"{label}: taşınabilir değil (CLAUDE_PLUGIN_ROOT yok) → {cmd[:60]}"
            )
        if "timeout" not in hook:
            issues.append(f"{label}: timeout yok → {cmd[:60]}")
        for rel in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)", cmd):
            _command_target(root, rel, label, issues)
    return issues


def _check_cursor_hooks(root: Path, path: Path, doc: dict) -> list[str]:
    issues: list[str] = []
    label = _display_path(path)
    if type(doc.get("version")) is not int or doc.get("version") != 1:
        issues.append(f"{label}: Cursor hook sürümü tam olarak `version: 1` olmalı")

    events = doc.get("hooks")
    if not isinstance(events, dict):
        return issues + [f"{label}: Cursor `hooks` mapping değil"]

    for event, definitions in events.items():
        if event not in CURSOR_VALID_EVENTS:
            issues.append(f"{label}: bilinmeyen Cursor olayı '{event}' (camelCase gerekli)")
        if not isinstance(definitions, list):
            issues.append(f"{label}: Cursor olayı '{event}' liste değil")
            continue

        allowed = CURSOR_EVENT_FIELDS.get(event, CURSOR_COMMON_FIELDS)
        for definition in definitions:
            if not isinstance(definition, dict):
                issues.append(f"{label}: Cursor olayı '{event}' doğrudan tanım değil")
                continue
            if "hooks" in definition:
                issues.append(
                    f"{label}: Cursor olayı '{event}' Claude-style nested `hooks` içeriyor"
                )
            extra = set(definition) - allowed
            if extra:
                issues.append(
                    f"{label}: Cursor olayı '{event}' desteklenmeyen alan(lar) → "
                    + ", ".join(sorted(extra))
                )
            if definition.get("type", "command") != "command":
                issues.append(f"{label}: Cursor olayı '{event}' command hook olmalı")
                continue
            timeout = definition.get("timeout")
            if type(timeout) is not int or timeout <= 0:
                issues.append(f"{label}: Cursor olayı '{event}' pozitif integer timeout ister")
            if not isinstance(definition.get("failClosed"), bool):
                issues.append(f"{label}: Cursor olayı '{event}' boolean failClosed ister")
            if event == "postToolUse" and not isinstance(definition.get("matcher"), str):
                issues.append(f"{label}: Cursor postToolUse metin matcher ister")

            command = definition.get("command")
            if not isinstance(command, str):
                issues.append(f"{label}: Cursor olayı '{event}' command metni taşımıyor")
                continue
            match = CURSOR_COMMAND_RE.fullmatch(command)
            if not match:
                issues.append(
                    f"{label}: Cursor command `/usr/bin/env python3 "
                    f"\"${{CURSOR_PLUGIN_ROOT}}/...\"` biçiminde olmalı → {command[:60]}"
                )
                continue
            rel = match.group(1)
            target = _command_target(root, rel, label, issues)
            if target is None:
                continue
            if Path(rel).parts[:2] != ("hooks", "scripts"):
                issues.append(f"{label}: Cursor hook betiği hooks/scripts altında değil → {rel}")
            try:
                script = target.read_text(encoding="utf-8")
            except OSError as exc:
                issues.append(f"{label}: Cursor hook betiği okunamadı → {rel}: {exc}")
                continue
            for claude_field in ("hookSpecificOutput", "additionalContext"):
                if claude_field in script:
                    issues.append(
                        f"{label}: Cursor wrapper Claude çıktı alanı "
                        f"`{claude_field}` içeriyor → {rel}"
                    )
    return issues


def check_hook_contract(root: Path, path: Path, platform: str) -> list[str]:
    """Bir hook dosyasını onu bildiren host'un gerçek şemasına göre doğrula."""
    label = _display_path(path)
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{label}: BOZUK JSON — {exc}"]
    except OSError as exc:
        return [f"{label}: hook dosyası okunamadı — {exc}"]
    if not isinstance(doc, dict):
        return [f"{label}: hook belgesi mapping değil"]
    if platform == "claude":
        return _check_claude_hooks(root, path, doc)
    if platform == "cursor":
        return _check_cursor_hooks(root, path, doc)
    raise ValueError(f"bilinmeyen hook platformu: {platform}")


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
        issues.extend(check_hook_contract(root, hj, "claude"))

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
            cursor_hooks = cur.get("hooks")
            declared = cursor_hooks if isinstance(cursor_hooks, list) else [cursor_hooks]
            for item in declared:
                if not isinstance(item, str):
                    continue
                hook_path = root / item
                if hook_path == hj:
                    # Geçiş uyumluluğu: Cursor-native dosyası olmayan eski plugin'lerin
                    # Claude ile paylaştığı hooks.json bugün kırılmaz.
                    continue
                if hook_path.is_file():
                    issues.extend(check_hook_contract(root, hook_path, "cursor"))

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
