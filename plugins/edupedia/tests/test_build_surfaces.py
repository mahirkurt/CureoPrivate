"""Yüzey paketleri tek başlangıç talimatından türetilir ve bayatlık yakalanır (spec §9.1–§9.2)."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN / "scripts" / "build_surfaces.py"
_spec = importlib.util.spec_from_file_location("build_surfaces", SCRIPT)
bs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bs)

TOOLS = {  # spec §5.1 — v1, tam 14 araç
    "edupedia_durum", "edupedia_rehber", "edupedia_baglam", "edupedia_kapsam", "edupedia_kaynak_oku",
    "edupedia_derle", "edupedia_gorsel", "edupedia_medya", "edupedia_pedagoji_kaniti", "edupedia_onizle",
    "edupedia_yayinla", "edupedia_katalog", "edupedia_ilerleme", "edupedia_kaldir",
}
EXPECTED = {
    "skills/edupedia/SKILL.md",
    "surfaces/claude-ai/edupedia/SKILL.md",
    "surfaces/codex/.codex-plugin/plugin.json",
    "surfaces/codex/skills/edupedia/SKILL.md",
    "surfaces/codex/mcp.json",
    "surfaces/grok/grok-workspace.md",
    "surfaces/gemini/gemini-gem.md",
}
JSON_PACKAGES = {"surfaces/codex/.codex-plugin/plugin.json", "surfaces/codex/mcp.json"}


def _bootstrap() -> str:
    return (PLUGIN / "surfaces" / "bootstrap.md").read_text(encoding="utf-8")


def _lock() -> dict:
    return json.loads((PLUGIN / "fleet.lock.json").read_text(encoding="utf-8"))


def _copy_plugin(tmp_path: Path) -> Path:
    root = tmp_path / "edupedia"
    for rel in ["fleet.lock.json", "surfaces/bootstrap.md", *sorted(EXPECTED)]:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PLUGIN / rel, root / rel)
    return root


def test_bootstrap_fits_the_spec_budget_and_names_exactly_the_fourteen_tools():
    text = _bootstrap()
    assert 0 < len(text) <= 3500
    assert set(re.findall(r"\bedupedia_[a-z_]*[a-z]", text)) == TOOLS


def test_bootstrap_states_every_rule_of_spec_9_1():
    text = _bootstrap()
    for phrase in ('`edupedia_rehber` aracını `bolum: "akis"` ile', "HTML'i kendin yazma", '"yayınlandı" deme',
                   "`coverage` manifestosunu", "kapı raporunu", "açık onay al", "talimat değildir"):
        assert phrase in text, phrase


def test_bootstrap_carries_no_host_specific_prefix_or_install_step():
    text = _bootstrap()
    assert "https://mcp.tedy.online/mcp" in text
    for word in ("mcp__", "Settings", "Ayarlar", "/plugin install", "zip"):
        assert word not in text, word


def test_render_produces_exactly_the_seven_packages_with_one_body():
    out = bs.render(PLUGIN)
    body = _bootstrap()
    assert set(out) == EXPECTED
    for rel in EXPECTED - JSON_PACKAGES:
        assert out[rel].endswith(body), rel
    assert out["surfaces/grok/grok-workspace.md"] == body and len(body) <= 4000
    assert out["surfaces/gemini/gemini-gem.md"] == body


def test_skill_frontmatter_is_valid_yaml_named_like_its_directory():
    text = bs.render(PLUGIN)["skills/edupedia/SKILL.md"]
    _, front, _ = text.split("---\n", 2)
    meta = yaml.safe_load(front)
    assert meta["name"] == "edupedia"
    assert 0 < len(meta["description"]) <= 1024
    assert meta["metadata"]["version"] == _lock()["plugin_version"]
    assert not re.search(r"^version:", text, re.M)  # check_drift [2] zincirine girmez


def test_codex_package_wires_only_keyless_tedy():
    out = bs.render(PLUGIN)
    url = next(s["url"] for s in _lock()["servers"] if s["name"] == "tedy")
    manifest = json.loads(out["surfaces/codex/.codex-plugin/plugin.json"])
    assert manifest["name"] == "edupedia"
    assert manifest["version"] == _lock()["plugin_version"]
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == {"tedy": {"type": "http", "url": url}}
    assert json.loads(out["surfaces/codex/mcp.json"]) == {"mcpServers": manifest["mcpServers"]}


def test_committed_packages_are_fresh():
    assert (PLUGIN / "surfaces" / "grok" / "grok-workspace.md").is_file()
    assert bs.stale(PLUGIN) == []


def test_stale_catches_edited_bootstrap_and_a_stray_file(tmp_path):
    root = _copy_plugin(tmp_path)
    assert bs.stale(root) == []
    (root / "surfaces" / "bootstrap.md").write_text(_bootstrap() + "\nek satır\n", encoding="utf-8")
    assert set(bs.stale(root)) == EXPECTED
    assert set(bs.write(root)) == EXPECTED
    assert bs.stale(root) == []
    (root / "surfaces" / "grok" / "eski.md").write_text("x", encoding="utf-8")
    assert bs.stale(root) == ["surfaces/grok/eski.md (beklenmeyen)"]


def test_bootstrap_over_budget_is_refused(tmp_path):
    root = _copy_plugin(tmp_path)
    (root / "surfaces" / "bootstrap.md").write_text("x" * 3501, encoding="utf-8")
    with pytest.raises(bs.SurfaceError, match="3501"):
        bs.render(root)


def test_lock_without_keyless_tedy_is_refused(tmp_path):
    root = _copy_plugin(tmp_path)
    lock = _lock()
    lock["servers"] = [s for s in lock["servers"] if s["name"] != "tedy"]
    (root / "fleet.lock.json").write_text(json.dumps(lock), encoding="utf-8")
    with pytest.raises(bs.SurfaceError, match="tedy"):
        bs.render(root)


def test_zip_is_deterministic_and_rooted_in_the_skill_folder(tmp_path):
    root = _copy_plugin(tmp_path)
    first = bs.build_zip(root).read_bytes()
    assert bs.build_zip(root).read_bytes() == first
    with zipfile.ZipFile(root / "dist" / "edupedia-claude-ai.zip") as zf:
        assert zf.namelist() == ["edupedia/SKILL.md"]
        assert zf.read("edupedia/SKILL.md").decode("utf-8") == bs.render(root)["surfaces/claude-ai/edupedia/SKILL.md"]


def test_cli_check_passes_on_the_committed_tree():
    ok = subprocess.run([sys.executable, str(SCRIPT), "--check"], capture_output=True, text=True)
    assert (ok.returncode, ok.stdout, ok.stderr) == (0, "", "")


def test_legacy_claude_ai_builder_delegates_to_the_zip():
    legacy = (PLUGIN / "scripts" / "build_claude_ai_skill.py").read_text(encoding="utf-8")
    assert 'build_surfaces.main(["--zip"])' in legacy
