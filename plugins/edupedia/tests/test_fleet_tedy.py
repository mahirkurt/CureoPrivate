"""edupedia 1.0.0 filosu: tedy orkestratörü birincil, interaktif OAuth (Bearer yok)."""
import json
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
TEDY_URL = "https://mcp.tedy.online/mcp"


def _json(rel: str) -> dict:
    return json.loads((PLUGIN / rel).read_text(encoding="utf-8"))


def test_lock_puts_keyless_tedy_first():
    lock = _json("fleet.lock.json")
    assert [s["name"] for s in lock["servers"]] == ["tedy", "maarif-mufredat", "egitim-kaynak"]
    assert lock["servers"][0] == {"name": "tedy", "url": TEDY_URL, "auth_env": None}
    assert lock["counts"] == {"servers": 3, "gated": 2, "public": 1, "companions": 0, "delegations": 0}


def test_every_wiring_sends_tedy_without_an_authorization_header():
    for rel in (".mcp.json", ".cursor-plugin/mcp.json"):
        entry = _json(rel)["mcpServers"]["tedy"]
        assert (entry["type"], entry["url"]) == ("http", TEDY_URL), rel
        assert "headers" not in entry, rel
    codex = _json(".codex-plugin/plugin.json")["mcpServers"]["tedy"]
    assert codex["url"] == TEDY_URL and "headers" not in codex


def test_version_chain_is_one_point_zero():
    marketplace = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    versions = {
        "plugin.json": _json(".claude-plugin/plugin.json")["version"],
        "codex": _json(".codex-plugin/plugin.json")["version"],
        "cursor": _json(".cursor-plugin/plugin.json")["version"],
        "lock": _json("fleet.lock.json")["plugin_version"],
        "marketplace": next(p["version"] for p in marketplace["plugins"] if p["name"] == "edupedia"),
    }
    assert set(versions.values()) == {"1.0.0"}, versions
