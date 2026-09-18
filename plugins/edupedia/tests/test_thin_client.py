"""edupedia 1.0.0 ince istemci: yerel yazım yığını yok, tek kaynak TED ted-mcp (spec §9.3)."""
import json
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {"__pycache__", ".pytest_cache", "dist"}
EXPECTED_FILES = {
    ".claude-plugin/plugin.json",
    ".codex-plugin/openai.yaml",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/mcp.json",
    ".cursor-plugin/plugin.json",
    ".mcp.json",
    "CLAUDE-AI-KURULUM.md",
    "CONNECTORS.md",
    "KURULUM.md",
    "README.md",
    "commands/durum.md",
    "commands/kazanim-bul.md",
    "commands/modul.md",
    "commands/mufredat.md",
    "commands/soru.md",
    "fleet.lock.json",
    "fleet.yaml",
    "hooks/hooks-cursor.json",
    "hooks/hooks.json",
    "hooks/preflight.sh",
    "hooks/scripts/cursor_session_start.py",
    "hooks/scripts/fleet_probe.py",
    "hooks/scripts/hook_core.py",
    "hooks/scripts/session_start.py",
    "hooks/test_hooks.py",
    "scripts/build_claude_ai_skill.py",
    "scripts/build_surfaces.py",
    "skills/edupedia/SKILL.md",
    "skills/start/SKILL.md",
    "surfaces/bootstrap.md",
    "surfaces/claude-ai/edupedia/SKILL.md",
    "surfaces/codex/.codex-plugin/plugin.json",
    "surfaces/codex/mcp.json",
    "surfaces/codex/skills/edupedia/SKILL.md",
    "surfaces/gemini/gemini-gem.md",
    "surfaces/grok/grok-workspace.md",
    "tests/test_build_surfaces.py",
    "tests/test_fleet_tedy.py",
    "tests/test_thin_client.py",
}


def tree() -> set[str]:
    return {
        p.relative_to(PLUGIN).as_posix()
        for p in PLUGIN.rglob("*")
        if p.is_file() and not IGNORED_PARTS & set(p.relative_to(PLUGIN).parts)
    }


def _json(rel: str) -> dict:
    return json.loads((PLUGIN / rel).read_text(encoding="utf-8"))


def test_plugin_tree_is_exactly_the_thin_client():
    files = tree()
    assert {"skills/edupedia/SKILL.md", "skills/start/SKILL.md", "hooks/scripts/session_start.py"} <= files
    assert files == EXPECTED_FILES, {"fazla": sorted(files - EXPECTED_FILES), "eksik": sorted(EXPECTED_FILES - files)}


def test_manifests_declare_no_agent_and_only_session_start_hooks():
    claude = _json(".claude-plugin/plugin.json")
    cursor = _json(".cursor-plugin/plugin.json")
    assert (claude["skills"], claude["commands"], claude["hooks"]) == ("./skills", "./commands", "./hooks/hooks.json")
    assert cursor["hooks"] == "./hooks/hooks-cursor.json"
    assert "agents" not in claude and "agents" not in cursor
    assert list(_json("hooks/hooks.json")["hooks"]) == ["SessionStart"]
    assert list(_json("hooks/hooks-cursor.json")["hooks"]) == ["sessionStart"]


BANNED = ("validate_module", "module-auditor", "carbon-edupedia", "canonical-cache-contract", "fetch_figure",
          "references/", "16 kalite", "yerel tek-dosya", "plugin yayınlamaz")


def test_no_file_points_at_the_removed_local_authoring_stack():
    scanned = sorted(tree() - {"tests/test_thin_client.py"})
    assert "README.md" in scanned and "commands/modul.md" in scanned  # the surface exists before the absence claim
    offenders = [f"{rel}: {word}" for rel in scanned for word in BANNED
                 if word in (PLUGIN / rel).read_text(encoding="utf-8")]
    assert offenders == []


def test_every_command_routes_through_the_orchestrator():
    commands = sorted(r for r in tree() if r.startswith("commands/"))
    assert len(commands) == 5
    for rel in commands:
        text = (PLUGIN / rel).read_text(encoding="utf-8")
        assert text.startswith("---\ndescription: "), rel
        assert "edupedia_" in text, rel
    soru = (PLUGIN / "commands" / "soru.md").read_text(encoding="utf-8")
    assert "EXAM" in soru and "yayınlanmaz" in soru
    assert "Modül üretme" in (PLUGIN / "commands" / "kazanim-bul.md").read_text(encoding="utf-8")
