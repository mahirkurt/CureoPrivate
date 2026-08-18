from __future__ import annotations

import importlib.util
import stat
import zipfile
from pathlib import Path

import pytest


PLUGIN = Path(__file__).parents[1]
SCRIPT = PLUGIN / "scripts" / "build_claude_ai_skill.py"
SPEC = importlib.util.spec_from_file_location("build_claude_ai_skill", SCRIPT)
assert SPEC and SPEC.loader
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _frontmatter(*description_lines: str) -> str:
    description = "\n".join(f"  {line}" for line in description_lines)
    return (
        "---\n"
        "name: carbon-edupedia\n"
        "description: >-\n"
        f"{description}\n"
        "---\n"
        "\n"
        "# Fixture skill\n"
    )


@pytest.fixture
def package_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    plugin = tmp_path / "edupedia"
    skill = plugin / "skills" / "carbon-edupedia"
    out_zip = plugin / "dist" / "carbon-edupedia-claude-ai.zip"

    _write(
        skill / "SKILL.md",
        _frontmatter(
            "MEB kazanımlarından erişilebilir, DEHB-dostu etkileşimli öğrenim modülü üretir."
        )
        + "\n"
        + "[Rehber](references/guide.md) · `scripts/validate.py` · "
        + "`docs/CHANGELOG.md` · `../../shared/run-manifest-schema.json`\n",
    )
    _write(skill / "skill-manifest.yaml", "guide: references/guide.md\n")
    _write(skill / "CHANGELOG.md", "# Değişiklik günlüğü\n")
    _write(
        skill / "references" / "guide.md",
        "[Şablon](../assets/template.html)\n"
        "`docs/superpowers/specs/2026-01-01-edupedia-design.md`\n",
    )
    _write(skill / "assets" / "template.html", "<!doctype html><title>Fixture</title>\n")
    _write(skill / "assets" / "authority.json", "{}\n")
    _write(skill / "scripts" / "validate.py", "# assets/authority.json\n")
    _write(skill / "evals" / "README.md", "[Skill](../SKILL.md)\n")
    _write(skill / "evals" / "evals.json", '{"validator": "scripts/validate.py"}\n')

    # Bunlar Claude.ai runtime paketine ait değildir.
    _write(skill / "tests" / "test_runtime.py", "raise AssertionError\n")
    _write(skill / "docs" / "CHANGELOG.md", "# Yinelenen changelog\n")
    _write(skill / "loose-leftover.txt", "paketlenmemeli\n")

    vendor = {
        "CONNECTORS.md": plugin / "CONNECTORS.md",
        "canonical-cache-contract.md": plugin / "shared" / "canonical-cache-contract.md",
        "run-manifest-schema.json": plugin / "shared" / "run-manifest-schema.json",
        "mcp-introspection-2026-07-06.json": (
            plugin / "docs" / "mcp-introspection-2026-07-06.json"
        ),
    }
    for name, path in vendor.items():
        _write(path, "{}\n" if path.suffix == ".json" else f"# {name}\n")

    monkeypatch.setattr(packager, "PLUGIN", plugin)
    monkeypatch.setattr(packager, "SKILL_SRC", skill)
    monkeypatch.setattr(packager, "OUT_DIR", out_zip.parent)
    monkeypatch.setattr(packager, "OUT_ZIP", out_zip)
    monkeypatch.setattr(packager, "VENDOR", vendor)
    return skill, out_zip


def _zip_with_members(path: Path, members: list[tuple[zipfile.ZipInfo | str, str]]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in members:
            archive.writestr(name, data)


def test_claude_ai_description_limit_is_200() -> None:
    assert packager.MAX_DESC == 200


def test_folded_description_at_200_characters_passes(tmp_path: Path) -> None:
    skill_md = tmp_path / "SKILL.md"
    _write(skill_md, _frontmatter("a" * 100, "b" * 99))

    assert packager._check_frontmatter(skill_md) == []


def test_folded_description_over_200_characters_fails(tmp_path: Path) -> None:
    skill_md = tmp_path / "SKILL.md"
    _write(skill_md, _frontmatter("a" * 100, "b" * 100))

    errors = packager._check_frontmatter(skill_md)

    assert any("201" in error and ">200" in error for error in errors)


def test_real_skill_description_is_publishable() -> None:
    assert packager._check_frontmatter(PLUGIN / "skills" / "carbon-edupedia" / "SKILL.md") == []


def test_build_uses_explicit_runtime_map_and_ships_changelog_and_evals(
    package_tree: tuple[Path, Path],
) -> None:
    _, out_zip = package_tree

    assert packager.main() == 0

    with zipfile.ZipFile(out_zip) as archive:
        names = archive.namelist()

    required = {
        "carbon-edupedia/SKILL.md",
        "carbon-edupedia/skill-manifest.yaml",
        "carbon-edupedia/CHANGELOG.md",
        "carbon-edupedia/references/guide.md",
        "carbon-edupedia/assets/template.html",
        "carbon-edupedia/assets/authority.json",
        "carbon-edupedia/scripts/validate.py",
        "carbon-edupedia/evals/README.md",
        "carbon-edupedia/evals/evals.json",
    }
    assert required <= set(names)
    assert "carbon-edupedia/loose-leftover.txt" not in names
    assert not any("/tests/" in name or "/docs/" in name for name in names)


def test_build_is_deterministic_in_order_and_timestamp(
    package_tree: tuple[Path, Path],
) -> None:
    _, out_zip = package_tree

    assert packager.main() == 0

    with zipfile.ZipFile(out_zip) as archive:
        infos = archive.infolist()
    assert [info.filename for info in infos] == sorted(info.filename for info in infos)
    assert {info.date_time for info in infos} == {(1980, 1, 1, 0, 0, 0)}


def test_source_symlink_is_rejected(
    package_tree: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    skill, out_zip = package_tree
    outside = tmp_path / "outside.py"
    _write(outside, "print('outside')\n")
    (skill / "scripts" / "symlink.py").symlink_to(outside)

    assert packager.main() == 1
    assert not out_zip.exists()


def test_zip_gate_rejects_absolute_traversal_duplicate_and_non_regular_members(
    tmp_path: Path,
) -> None:
    zip_path = tmp_path / "unsafe.zip"
    symlink = zipfile.ZipInfo("carbon-edupedia/scripts/link.py")
    symlink.create_system = 3
    symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
    members: list[tuple[zipfile.ZipInfo | str, str]] = [
        ("/absolute.md", ""),
        ("carbon-edupedia/../escape.md", ""),
        ("carbon-edupedia/SKILL.md", "first"),
        ("carbon-edupedia/SKILL.md", "second"),
        (symlink, "target.py"),
    ]
    with pytest.warns(UserWarning, match="Duplicate name"):
        _zip_with_members(zip_path, members)

    violations = packager._gate_links(zip_path)

    assert any("/absolute.md" in violation for violation in violations)
    assert any("carbon-edupedia/../escape.md" in violation for violation in violations)
    assert any("carbon-edupedia/SKILL.md" in violation for violation in violations)
    assert any("carbon-edupedia/scripts/link.py" in violation for violation in violations)


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("carbon-edupedia/guide.md", "[Kırık](references/missing.md)\n"),
        ("carbon-edupedia/manifest.yaml", "guide: references/missing.md\n"),
        ("carbon-edupedia/data.json", '{"guide": "references/missing.md"}\n'),
        ("carbon-edupedia/tool.py", "# references/missing.md\n"),
        ("carbon-edupedia/template.html", "<!-- references/missing.md -->\n"),
    ],
)
def test_link_gate_checks_every_packaged_text_suffix(
    tmp_path: Path,
    name: str,
    text: str,
) -> None:
    zip_path = tmp_path / "broken-link.zip"
    _zip_with_members(
        zip_path,
        [
            ("carbon-edupedia/SKILL.md", _frontmatter("Kısa açıklama")),
            (name, text),
        ],
    )

    violations = packager._gate_links(zip_path)

    assert any("references/missing.md" in violation for violation in violations)


def test_markdown_link_parser_ignores_javascript_inside_inline_code() -> None:
    text = "`SIM_PRESETS[simType](svgEl, values, labels)` çağrılır.\n"

    assert packager._relative_references(text, ".md", "references/guide.md") == set()


def test_development_spec_path_is_demoted_to_offline_identifier() -> None:
    source = "`docs/superpowers/specs/2026-01-01-edupedia-design.md`"

    rewritten = packager._rewrite(source, "references/guide.md")

    assert "docs/superpowers/specs/" not in rewritten
    assert "2026-01-01-edupedia-design" in rewritten


def test_size_gate_rejects_oversized_zip(
    package_tree: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, out_zip = package_tree
    monkeypatch.setattr(packager, "MAX_ZIP_BYTES", 64)

    assert packager.main() == 1
    assert not out_zip.exists()
