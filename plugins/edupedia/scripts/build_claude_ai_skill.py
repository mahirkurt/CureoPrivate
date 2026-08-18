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
        ├── skill-manifest.yaml
        ├── CHANGELOG.md
        ├── references/*.md
        ├── scripts/*.py
        ├── evals/{README.md,evals.json}
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
Repo-kökü `docs/superpowers/specs/*.md` yolları da runtime bağımlılığı değil geliştirme
provenansıdır; paket metninde kararlı kayıt kimliğine indirgenir, dosya olarak vendor'lanmaz.

KAPI: paket kurulduktan sonra ZIP'İN İÇİNDEN doğrulanır — paketlenmiş her .md'deki `../`
ile kaçan veya göreli hedef gösteren her metin bağlantısı zip üyesi olmak ZORUNDA.
Mutlak/traversal/yinelenen üye adları ve düzenli dosya olmayan üyeler de reddedilir.
Bu kapı niyeti değil ARTEFAKTI ölçer: yeni bir paket-dışı referans sessizce sızamaz.

PAKET HARİTASI AÇIKTIR: yalnız SKILL/manifest/CHANGELOG, runtime references/assets/scripts,
minimal eval sözleşmesi ve VENDOR girer. tests/ ile yinelenen docs/CHANGELOG.md girmez;
denetlenebilirlik kanıtı olan MCP introspeksiyon çıktısı ayrıca vendor'lanır.

`scripts/` DAHİL EDİLİR: claude.ai kod-çalıştırma açıkken script koşturabilir, yani
`validate_module.py` kalite kapısı olarak işe yarar. Koşmazsa üretim yine çalışır;
kapıları "PASS" diye beyan etmeyin.
"""
from __future__ import annotations

import os
import posixpath
import re
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

PLUGIN = Path(__file__).resolve().parent.parent
SKILL_SRC = PLUGIN / "skills" / "carbon-edupedia"
SKILL_NAME = "carbon-edupedia"
OUT_DIR = PLUGIN / "dist"
OUT_ZIP = OUT_DIR / f"{SKILL_NAME}-claude-ai.zip"

# claude.ai spec limitleri (ölçülür, varsayılmaz)
MAX_ZIP_BYTES = 30 * 1024 * 1024
MAX_NAME = 64
MAX_DESC = 200

# Claude.ai için gerekli runtime ağacı. Yeni bir üst-düzey dosya kendiliğinden pakete girmez.
PACKAGE_FILES = (
    "SKILL.md",
    "skill-manifest.yaml",
    "CHANGELOG.md",
    "evals/README.md",
    "evals/evals.json",
)
PACKAGE_TREES: dict[str, frozenset[str]] = {
    "references": frozenset({".md"}),
    "assets": frozenset({".html", ".json"}),
    "scripts": frozenset({".py"}),
}
GENERATED_DIRS = frozenset({"__pycache__", ".pytest_cache"})
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

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
# Paket yüzeyinde yinelenen docs changelog yerine kökteki kanonik kopya kullanılır.
DOC_CHANGELOG_RE = re.compile(r"(?<![A-Za-z0-9_.-])(?:\./)?docs/CHANGELOG\.md")
# Repo-kökü tasarım kayıtları runtime girdisi değildir; pakette yol değil kimlik kalır.
DEV_SPEC_RE = re.compile(r"docs/superpowers/specs/([A-Za-z0-9_.-]+)\.md")

# Rewrite + kapı, pakete alınan bütün metin türlerinde uygulanır.
TEXT_SUFFIX = frozenset({".md", ".yaml", ".yml", ".json", ".py", ".html", ".sh", ".txt"})
TEXT_EXTENSIONS_RE = r"(?:md|yaml|yml|json|py|html|sh|txt)"
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
FENCED_CODE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
RELATIVE_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_:/.-])("
    r"(?:(?:\.{1,2}/)+|(?:references|assets|scripts|evals|plugin-context|docs)/)"
    r"[A-Za-z0-9_.@%+/-]+\."
    + TEXT_EXTENSIONS_RE
    + r"(?:#[A-Za-z0-9_.:%+/-]+)?"
    r")"
)
ROOT_RELATIVE_PREFIXES = tuple(f"{name}/" for name in (*PACKAGE_TREES, "evals", VENDOR_DIR, "docs"))


class PackageError(ValueError):
    """Paket sözleşmesi ihlal edildiğinde kullanıcıya gösterilecek hata."""


def _path_issue(name: str) -> str | None:
    """ZIP üye yolunun taşınabilir ve kök-içi olup olmadığını açıkla."""
    if not name:
        return "boş üye adı"
    if "\x00" in name:
        return "NUL içeren üye adı"
    if "\\" in name:
        return "ters eğik çizgi içeren üye adı"
    if name.startswith("/") or PurePosixPath(name).is_absolute() or re.match(r"^[A-Za-z]:", name):
        return "mutlak üye yolu"
    parts = name.split("/")
    if any(part == ".." for part in parts):
        return "`..` traversal"
    if any(part in {"", "."} for part in parts):
        return "boş veya `.` yol bileşeni"
    if posixpath.normpath(name) != name:
        return "normalize olmayan üye yolu"
    return None


def _require_regular(path: Path, label: str) -> None:
    """Symlink/FIFO/socket/device dâhil düzenli olmayan kaynakları reddet."""
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise PackageError(f"{label} okunamadı: {path} ({exc})") from exc
    if not stat.S_ISREG(mode):
        raise PackageError(f"{label} düzenli dosya değil: {path}")


def _iter_files(root: Path):
    """Açık Claude.ai paket haritasındaki kaynak dosyalarını deterministik sırayla ver."""
    for rel in PACKAGE_FILES:
        issue = _path_issue(rel)
        if issue:
            raise PackageError(f"paket haritasında güvensiz yol `{rel}`: {issue}")
        path = root / rel
        _require_regular(path, "zorunlu paket kaynağı")
        yield path

    for dirname, suffixes in PACKAGE_TREES.items():
        tree = root / dirname
        try:
            tree_mode = tree.lstat().st_mode
        except OSError as exc:
            raise PackageError(f"zorunlu paket dizini okunamadı: {tree} ({exc})") from exc
        if not stat.S_ISDIR(tree_mode):
            raise PackageError(f"zorunlu paket dizini gerçek dizin değil: {tree}")

        for path in sorted(tree.rglob("*")):
            rel_parts = path.relative_to(root).parts
            if any(part in GENERATED_DIRS for part in rel_parts):
                continue
            try:
                mode = path.lstat().st_mode
            except OSError as exc:
                raise PackageError(f"paket kaynağı okunamadı: {path} ({exc})") from exc
            if stat.S_ISDIR(mode):
                continue
            if not stat.S_ISREG(mode):
                raise PackageError(f"paket kaynağı düzenli dosya değil: {path}")
            if path.suffix.lower() not in suffixes:
                allowed = ", ".join(sorted(suffixes))
                raise PackageError(
                    f"açık paket haritası `{path.relative_to(root)}` uzantısını kabul etmiyor "
                    f"(izinli: {allowed})"
                )
            yield path


def _rewrite(text: str, pkg_rel: str) -> str:
    """Paket-dışı bağlantıları paket-içi gerçeğe çevir. pkg_rel = zip içindeki yol."""
    here = posixpath.dirname(pkg_rel)

    def _vendor_sub(m: re.Match[str]) -> str:
        return posixpath.relpath(f"{VENDOR_DIR}/{m.group(1)}", here or ".")

    def _changelog_sub(_: re.Match[str]) -> str:
        return posixpath.relpath("CHANGELOG.md", here or ".")

    def _dev_spec_sub(match: re.Match[str]) -> str:
        return f"geliştirme-tasarım-kaydı:{match.group(1)}"

    text = CMD_RE.sub(lambda m: f"/edupedia:{m.group(1)}", text)
    text = VENDOR_RE.sub(_vendor_sub, text)
    text = DOC_CHANGELOG_RE.sub(_changelog_sub, text)
    return DEV_SPEC_RE.sub(_dev_spec_sub, text)


def _description_value(frontmatter: str) -> str | None:
    """Description YAML skalerini, özellikle `>-` katlamasını semantik olarak oku."""
    match = re.search(
        r"^description:\s*(?:(?P<style>[>|])-?\s*\n"
        r"(?P<block>(?:[ \t]+.*(?:\n|$))+)|(?P<plain>[^\n]+))",
        frontmatter,
        re.M,
    )
    if not match:
        return None
    plain = match.group("plain")
    if plain is not None:
        return plain.strip().strip("\"'")

    lines = [line.strip() for line in (match.group("block") or "").splitlines()]
    if match.group("style") == "|":
        return "\n".join(lines).strip()

    paragraphs: list[str] = []
    current: list[str] = []
    for line in lines:
        if line:
            current.append(line)
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return "\n".join(paragraphs).strip()


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

    desc = _description_value(fm)
    if desc is None:
        hatalar.append("frontmatter'da `description` yok (zorunlu — tetikleme SADECE buradan)")
    else:
        if not desc:
            hatalar.append("description boş")
        if len(desc) > MAX_DESC:
            hatalar.append(f"description {len(desc)} kar. (>{MAX_DESC}) — {len(desc)-MAX_DESC} fazla")
        if re.search(r"<[a-zA-Z/][^>]*>", desc):
            hatalar.append("description XML/HTML etiketi içeriyor (yasak)")
    return hatalar


def _markdown_target(raw: str) -> str:
    """Markdown hedefinden opsiyonel başlığı ayır."""
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split(maxsplit=1)[0]


def _relative_references(text: str, suffix: str, body_name: str) -> set[str]:
    """Paket metnindeki göreli dosya navigasyonlarını çıkar."""
    refs: set[str] = set()
    if suffix == ".md":
        prose = FENCED_CODE_RE.sub("", text)
        prose = INLINE_CODE_RE.sub("", prose)
        refs.update(_markdown_target(raw) for raw in MARKDOWN_LINK_RE.findall(prose))
        # CHANGELOG tarihsel geliştirme yolları taşır; yalnız gerçek Markdown linkleri navigasyondur.
        if body_name == "CHANGELOG.md":
            return refs
    refs.update(RELATIVE_REF_RE.findall(text))
    return refs


def _resolve_reference(body_name: str, raw: str) -> tuple[str | None, str | None]:
    """Bir metin bağlantısını skill-köküne göre çöz; (hedef, hata) döndür."""
    ref = raw.strip().strip("<>")
    if not ref or ref.startswith("#"):
        return None, None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", ref) or ref.startswith("//"):
        return None, None
    ref = ref.split("#", 1)[0].split("?", 1)[0]
    if not ref:
        return None, None
    issue = _path_issue(ref)
    if issue and not ref.startswith(("./", "../")):
        return None, issue

    if ref.startswith(ROOT_RELATIVE_PREFIXES):
        target = posixpath.normpath(ref)
    else:
        target = posixpath.normpath(posixpath.join(posixpath.dirname(body_name), ref))
    if target == ".." or target.startswith("../") or target.startswith("/"):
        return None, "paket kökünün dışına çıkıyor"
    target_issue = _path_issue(target)
    if target_issue:
        return None, target_issue
    return target, None


def _gate_links(zip_path: Path) -> list[str]:
    """ZIP güvenliğini ve bütün göreli metin bağlantılarını artefaktın içinden ölç."""
    ihlaller: list[str] = []
    with zipfile.ZipFile(zip_path) as archive:
        infos = archive.infolist()
        counts: dict[str, int] = {}
        unsafe: set[str] = set()
        prefix = f"{SKILL_NAME}/"

        for info in infos:
            name = info.filename
            counts[name] = counts.get(name, 0) + 1
            issue = _path_issue(name)
            if issue:
                ihlaller.append(f"ZIP üyesi `{name}` güvensiz: {issue}")
                unsafe.add(name)
            if not name.startswith(prefix):
                ihlaller.append(f"ZIP üyesi `{name}` `{prefix}` kökü altında değil")
                unsafe.add(name)

            mode = (info.external_attr >> 16) & 0xFFFF
            file_type = stat.S_IFMT(mode)
            if info.is_dir() or file_type not in {0, stat.S_IFREG}:
                ihlaller.append(f"ZIP üyesi `{name}` düzenli dosya değil")
                unsafe.add(name)

        for name, count in counts.items():
            if count > 1:
                ihlaller.append(f"ZIP üyesi `{name}` {count} kez yineleniyor")
                unsafe.add(name)

        members = set(counts)
        for info in infos:
            name = info.filename
            if name in unsafe or counts[name] > 1:
                continue
            suffix = PurePosixPath(name).suffix.lower()
            if suffix not in TEXT_SUFFIX:
                continue
            try:
                text = archive.open(info).read().decode("utf-8")
            except UnicodeDecodeError:
                ihlaller.append(f"ZIP üyesi `{name}` {suffix} olmasına rağmen UTF-8 değil")
                continue

            body_name = name[len(prefix) :]
            for ref in sorted(_relative_references(text, suffix, body_name)):
                target, error = _resolve_reference(body_name, ref)
                if error:
                    ihlaller.append(f"{body_name}: `{ref}` → {error}")
                elif target is not None and f"{prefix}{target}" not in members:
                    ihlaller.append(f"{body_name}: `{ref}` → `{target}` zip'te YOK")
    return ihlaller


def _add_content(
    content: dict[str, bytes],
    casefolded: dict[str, str],
    rel: str,
    data: bytes,
) -> None:
    """Güvenli ve benzersiz bir paket üyesi ekle."""
    issue = _path_issue(rel)
    if issue:
        raise PackageError(f"güvensiz paket yolu `{rel}`: {issue}")
    if rel in content:
        raise PackageError(f"yinelenen paket üyesi: {rel}")
    folded = rel.casefold()
    if folded in casefolded:
        raise PackageError(f"büyük/küçük harf çakışmalı paket üyeleri: {casefolded[folded]} / {rel}")
    content[rel] = data
    casefolded[folded] = rel


def _read_package_source(path: Path, rel: str) -> bytes:
    """Düzenli kaynak dosyasını oku; metin yollarını paket yüzeyine yeniden yaz."""
    _require_regular(path, "paket kaynağı")
    if path.suffix.lower() in TEXT_SUFFIX:
        return _rewrite(path.read_text(encoding="utf-8"), rel).encode("utf-8")
    return path.read_bytes()


def _collect_content() -> dict[str, bytes]:
    """Açık include haritası + vendor kaynaklarından zip gövdesini kur."""
    content: dict[str, bytes] = {}
    casefolded: dict[str, str] = {}
    for path in _iter_files(SKILL_SRC):
        rel = path.relative_to(SKILL_SRC).as_posix()
        _add_content(content, casefolded, rel, _read_package_source(path, rel))
    for name, path in sorted(VENDOR.items()):
        rel = f"{VENDOR_DIR}/{name}"
        _add_content(content, casefolded, rel, _read_package_source(path, rel))
    return content


def _write_zip(zip_path: Path, content: dict[str, bytes]) -> None:
    """Sabit sıra, zaman damgası ve Unix regular-file modu ile zip yaz."""
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for rel, data in sorted(content.items()):
            info = zipfile.ZipInfo(f"{SKILL_NAME}/{rel}", date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> int:
    skill_md = SKILL_SRC / "SKILL.md"
    try:
        _require_regular(skill_md, "SKILL.md")
    except PackageError as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1

    hatalar = _check_frontmatter(skill_md)
    if hatalar:
        print("✘ claude.ai frontmatter spec ihlali:", file=sys.stderr)
        for h in hatalar:
            print(f"    - {h}", file=sys.stderr)
        return 1
    print("✔ frontmatter: name + description claude.ai spec'ine uygun")

    try:
        content = _collect_content()
    except (OSError, UnicodeError, PackageError) as exc:
        print(f"✘ paket kaynağı reddedildi: {exc}", file=sys.stderr)
        return 1

    temp_zip: Path | None = None
    try:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f".{OUT_ZIP.name}.",
            suffix=".tmp",
            dir=OUT_DIR,
        )
        os.close(descriptor)
        temp_zip = Path(temp_name)
        _write_zip(temp_zip, content)

        size = temp_zip.stat().st_size
        if size > MAX_ZIP_BYTES:
            print(
                f"✘ zip {size / 1024 / 1024:.1f} MB > "
                f"{MAX_ZIP_BYTES / 1024 / 1024:.0f} MB limiti",
                file=sys.stderr,
            )
            return 1

        violations = _gate_links(temp_zip)
        if violations:
            print(
                f"✘ ZIP GÜVENLİK/BAĞLANTI KAPISI — {len(violations)} ihlal:",
                file=sys.stderr,
            )
            for violation in violations:
                print(f"    - {violation}", file=sys.stderr)
            print(
                "\n  Çözüm: runtime bağımlılığını açık paket haritasına/VENDOR'a ekleyin;\n"
                "  Claude Code'a özgü yüzeyse dosya bağlantısı yerine yalnız adını yazın.",
                file=sys.stderr,
            )
            return 1

        with zipfile.ZipFile(temp_zip) as archive:
            names = archive.namelist()
        root_skill = f"{SKILL_NAME}/SKILL.md"
        if root_skill not in names or "SKILL.md" in names:
            print(f"✘ zip klasör-kök yapısı bozuk: {root_skill}", file=sys.stderr)
            return 1

        temp_zip.replace(OUT_ZIP)
        temp_zip = None
    except (OSError, zipfile.BadZipFile, PackageError) as exc:
        print(f"✘ zip üretilemedi: {exc}", file=sys.stderr)
        return 1
    finally:
        if temp_zip is not None:
            temp_zip.unlink(missing_ok=True)

    vendor_uye = sum(1 for name in names if f"/{VENDOR_DIR}/" in name)
    print(f"✔ yapı    : {root_skill} (klasör kökte)")
    print(f"✔ vendor  : {vendor_uye} normatif belge → {VENDOR_DIR}/ (bağlantılar yeniden yazıldı)")
    print("✔ güvenlik: yol/üye türü/yineleme ve göreli bağlantılar zip'ten doğrulandı")
    print(f"✔ içerik  : {len(names)} dosya | açık runtime + eval + vendor haritası")
    print(f"✔ boyut   : {size / 1024:.0f} KB  (limit 30 MB — %{size / MAX_ZIP_BYTES * 100:.1f})")
    print(f"\n→ {OUT_ZIP}")
    print("  Yükleme: claude.ai → Settings → Customize → Skills → Upload")
    print("  UNUTMA: connector'lar AYRI eklenir (Settings → Customize → Connectors).")
    print("          Skill bir connector'ı talep EDEMEZ — bağımlılık mekanizması yok.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
