#!/usr/bin/env python3
"""lex-sanitas filo üreticisi — fleet.yaml'dan tüm türev artefaktları üretir.

Üretilenler:
  fleet.lock.json                            hook'ların okuduğu stdlib-türev
  .mcp.json                                  Claude Code MCP wiring
  .codex-plugin/plugin.json                  mcpServers bloğu + version (yerinde)
  commands/lex-connectors.md                 ⟨GEN⟩ anahtar tablosu
  agents/*.md                                ⟨GEN⟩ tools: satırı (YAML frontmatter)
  skills/lex-sanitas/references/00-mod-pipelines.md   ⟨GEN⟩ mod×server matrisi

Kullanım:
  python3 tools/gen_fleet.py            üret ve yaz
  python3 tools/gen_fleet.py --check    yazma; fark varsa exit 1 (CI kapısı)

NOT: Bu betik PyYAML kullanır. Hook'lar ASLA bu betiği import etmez — onlar
fleet.lock.json'u stdlib json ile okur, böylece kullanıcı sisteminde PyYAML
olmasa da preflight çalışır.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

TIERS = {"primary", "secondary", "comparative", "support",
         "doctrine", "fulltext", "substrate"}
SHARDS = {"S1", "S2", "S3", "S4", "ALL"}
MODES = {"ALL", "DRAFT", "AMEND", "ANALYZE", "COMPLY", "OPINE", "RIA",
         "COMPARATIVE_LAW", "TBMM_KANUN_TEKLIFI", "EX_POST_EVALUATION"}
GATES = {None, "G5", "G6", "G7"}

SERVER_KEYS = {"name", "url", "tier", "auth_env", "shard", "modes",
               "gate", "tools_used", "role", "degrade"}
COMPANION_KEYS = {"name", "tool_prefixes", "gate", "modes",
                  "manifest_row", "degrade"}
DELEGATION_KEYS = {"name", "plugin_id_prefix", "trigger",
                   "manifest_row", "degrade"}

GEN_WARNING = ("ÜRETİLMİŞ DOSYA — elle düzenlemeyin. "
               "Kaynak: fleet.yaml → python3 tools/gen_fleet.py")

MODE_ORDER = ["DRAFT", "AMEND", "ANALYZE", "COMPLY", "OPINE", "RIA",
              "COMPARATIVE_LAW", "TBMM_KANUN_TEKLIFI", "EX_POST_EVALUATION"]
MODE_ABBR = {"DRAFT": "DRAFT", "AMEND": "AMEND", "ANALYZE": "ANLZ",
             "COMPLY": "CMPLY", "OPINE": "OPINE", "RIA": "RIA",
             "COMPARATIVE_LAW": "COMP", "TBMM_KANUN_TEKLIFI": "TBMM",
             "EX_POST_EVALUATION": "EXPOST"}

# (ajan dosyası, shard'lar, ek yerleşik araçlar, companion önekleri dâhil mi)
AGENT_SHARDS = [
    ("legal-distiller.md", ["S1", "S3"], ["Read", "Grep", "Glob", "WebFetch"], True),
    ("comparative-law-researcher.md", ["S2", "S4"],
     ["Read", "Grep", "Glob", "WebFetch"], True),
    ("compliance-auditor.md", ["S1"], ["Read", "Grep", "Glob"], True),
    ("gerekce-drafter.md", ["S1", "S3"], ["Read", "Grep", "Glob"], True),
]


# ── Yükleme ve doğrulama ────────────────────────────────────────────────────

def load_fleet(root: Path) -> dict:
    """fleet.yaml'ı okur ve şema-doğrular."""
    fleet = yaml.safe_load((root / "fleet.yaml").read_text(encoding="utf-8"))
    validate_fleet(fleet)
    return fleet


def validate_fleet(fleet: dict) -> None:
    """Şema ihlallerinde ValueError fırlatır — sessiz bozuk üretim olmaz."""
    for key in ("version", "plugin", "plugin_version", "servers",
                "companions", "delegations"):
        if key not in fleet:
            raise ValueError(f"fleet.yaml: '{key}' alanı eksik")

    seen = set()
    for s in fleet["servers"]:
        missing = SERVER_KEYS - set(s)
        if missing:
            raise ValueError(
                f"server {s.get('name')!r}: eksik alan(lar) {sorted(missing)}")
        if s["name"] in seen:
            raise ValueError(f"server adı tekrarlı: {s['name']}")
        seen.add(s["name"])
        if s["tier"] not in TIERS:
            raise ValueError(f"{s['name']}: geçersiz tier {s['tier']!r}")
        if s["shard"] not in SHARDS:
            raise ValueError(f"{s['name']}: geçersiz shard {s['shard']!r}")
        if s["gate"] not in GATES:
            raise ValueError(f"{s['name']}: geçersiz gate {s['gate']!r}")
        if not set(s["modes"]) <= MODES:
            raise ValueError(
                f"{s['name']}: geçersiz mod(lar) {sorted(set(s['modes']) - MODES)}")
        if not s["url"].endswith("/mcp"):
            raise ValueError(f"{s['name']}: url '/mcp' ile bitmeli")

    for c in fleet["companions"]:
        missing = COMPANION_KEYS - set(c)
        if missing:
            raise ValueError(
                f"companion {c.get('name')!r}: eksik alan(lar) {sorted(missing)}")
    for d in fleet["delegations"]:
        missing = DELEGATION_KEYS - set(d)
        if missing:
            raise ValueError(
                f"delegation {d.get('name')!r}: eksik alan(lar) {sorted(missing)}")

    comp = {c["name"] for c in fleet["companions"]}
    if seen & comp:
        raise ValueError(f"wire'lı server companion olamaz: {sorted(seen & comp)}")


# ── Türev gövdeler ──────────────────────────────────────────────────────────

def build_lock(fleet: dict) -> dict:
    """Hook'ların okuduğu stdlib-türev — role/tools_used/degrade taşımaz."""
    servers = [
        {k: s[k] for k in ("name", "url", "tier", "auth_env", "shard", "modes", "gate")}
        for s in fleet["servers"]
    ]
    gated = sum(1 for s in servers if s["auth_env"])
    return {
        "_generated": GEN_WARNING,
        "plugin_version": fleet["plugin_version"],
        "counts": {
            "servers": len(servers),
            "gated": gated,
            "public": len(servers) - gated,
            "companions": len(fleet["companions"]),
            "delegations": len(fleet["delegations"]),
        },
        "servers": servers,
        "companions": fleet["companions"],
        "delegations": fleet["delegations"],
    }


def _squash(text: str) -> str:
    """YAML katlanmış blokların satır sonlarını tek boşluğa indirger."""
    return " ".join(str(text).split())


def build_mcp_servers(fleet: dict) -> dict:
    """`.mcp.json`/codex için mcpServers bloğu."""
    out = {}
    for s in fleet["servers"]:
        entry = {"type": "http", "url": s["url"]}
        if s["auth_env"]:
            entry["headers"] = {"Authorization": "Bearer ${%s}" % s["auth_env"]}
        entry["_tier"] = s["tier"]
        entry["_role"] = _squash(s["role"])
        out[s["name"]] = entry
    return out


def build_mcp_json(fleet: dict) -> dict:
    c = build_lock(fleet)["counts"]
    comp_names = " / ".join(x["name"] for x in fleet["companions"])
    comment = (
        f"{GEN_WARNING} — lex-sanitas MCP wiring. TAM-FİLO İLKESİ: "
        f"{c['servers']} server'ın TAMAMI her sorguda devreye alınır (G0 kapsam "
        f"kapısı). PRİMER/İKİNCİL etiketi aktivasyon kapısı DEĞİL, sentezde otorite "
        f"önceliğidir — çatışmada primer kazanır ama ikincil/support da çalıştırılır "
        f"ve sonucu kapsam manifestosuna girer. Ağır getirim distiller "
        f"alt-ajanlarında toplanır (retrieve-don't-dump); ana bağlama kompakt "
        f"retrieval_distillate + coverage döner. {c['gated']} server Bearer-gated, "
        f"{c['public']} public. Auth'lu server'lar Doppler-injected Bearer bekler; "
        f"anahtar yoksa SessionStart preflight uyarır ve o katman graceful degrade "
        f"eder (manifestoda 'skipped: anahtar yok'; asla uydurma). "
        f"{c['companions']} companion ({comp_names}) DIŞ connector'dır — kararlı "
        f"self-host URL'leri yok, wire edilemez; claude.ai connector olarak bağlıysa "
        f"skill onları tam-filoya dahil eder (bkz. commands/lex-connectors.md)."
    )
    return {"_comment": comment, "mcpServers": build_mcp_servers(fleet)}


def env_table(fleet: dict) -> str:
    rows = ["| Server | Tier | Env-var (Doppler → Bearer) |", "|---|---|---|"]
    for s in fleet["servers"]:
        env = f"`{s['auth_env']}`" if s["auth_env"] else "_(public — anahtar yok)_"
        rows.append(f"| `{s['name']}` | {s['tier']} | {env} |")
    for c in fleet["companions"]:
        rows.append(f"| {c['name']} | companion | "
                    f"_(claude.ai connector — env anahtarı yok)_ |")
    return "\n".join(rows)


def agent_tools_line(fleet: dict, shards, extra, companions: bool) -> str:
    """Ajan frontmatter'ı için tek satırlık `tools:` ifadesi."""
    names = [s["name"] for s in fleet["servers"]
             if s["shard"] in shards or s["shard"] == "ALL"]
    tools = list(extra) + [f"mcp__{n}__*" for n in names]
    if companions:
        tools += [f"{p}*" for c in fleet["companions"] for p in c["tool_prefixes"]]
    return "tools: " + ", ".join(tools)


def mode_matrix(fleet: dict) -> str:
    """Mod × server matrisi — hangi satırın hangi modda N/A olduğu VERİDEN gelir."""
    head = "| Server | " + " | ".join(MODE_ABBR[m] for m in MODE_ORDER) + " |"
    sep = "|---|" + "---|" * len(MODE_ORDER)
    rows = [head, sep]
    for s in fleet["servers"]:
        active = s.get("modes", ["ALL"])
        cells = ["✓" if ("ALL" in active or m in active) else "·" for m in MODE_ORDER]
        rows.append(f"| `{s['name']}` ({s['tier']}) | " + " | ".join(cells) + " |")
    for c in fleet["companions"]:
        active = c.get("modes", ["ALL"])
        cells = ["✓" if ("ALL" in active or m in active) else "·" for m in MODE_ORDER]
        rows.append(f"| **{c['name']}** (companion) | " + " | ".join(cells) + " |")
    rows.append("")
    rows.append("> `✓` = bu modda taranır · `·` = bu modda **mantıksal olarak N/A** "
                "→ manifestoda `skipped: mod için N/A` yazılır (satır atlanamaz).")
    return "\n".join(rows)


# ── Yazma ───────────────────────────────────────────────────────────────────

def replace_gen_block(text: str, name: str, body: str,
                      comment_style: str = "html") -> str:
    """⟨GEN⟩ bloğunun içini değiştirir.

    comment_style='html'  → <!-- GEN:name BEGIN --> … <!-- GEN:name END -->
    comment_style='yaml'  → # GEN:name BEGIN … # GEN:name END
    (YAML frontmatter'da HTML yorumu geçersizdir; ajan dosyaları 'yaml' kullanır.)
    """
    if comment_style == "yaml":
        begin, end = f"# GEN:{name} BEGIN", f"# GEN:{name} END"
    else:
        begin, end = f"<!-- GEN:{name} BEGIN -->", f"<!-- GEN:{name} END -->"
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"⟨GEN⟩ bloğu bulunamadı: {name} ({comment_style})")
    return pattern.sub(lambda _: f"{begin}\n{body}\n{end}", text, count=1)


def _write(path: Path, content: str, check: bool, changed: list) -> None:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return
    changed.append(str(path.name if path.parent.name == "" else path))
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _json_text(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def write_all(root: Path, fleet: dict, check: bool = False) -> list:
    """Tüm türev artefaktları yazar (check modunda yalnız farkı toplar)."""
    changed = []

    _write(root / "fleet.lock.json", _json_text(build_lock(fleet)), check, changed)
    _write(root / ".mcp.json", _json_text(build_mcp_json(fleet)), check, changed)

    codex_path = root / ".codex-plugin" / "plugin.json"
    codex = json.loads(codex_path.read_text(encoding="utf-8"))
    codex["version"] = fleet["plugin_version"]
    codex["mcpServers"] = build_mcp_servers(fleet)
    _write(codex_path, _json_text(codex), check, changed)

    conn = root / "commands" / "lex-connectors.md"
    _write(conn, replace_gen_block(conn.read_text(encoding="utf-8"),
                                   "fleet-env-table", env_table(fleet)),
           check, changed)

    for agent, shards, extra, comps in AGENT_SHARDS:
        path = root / "agents" / agent
        _write(path,
               replace_gen_block(path.read_text(encoding="utf-8"), "agent-tools",
                                 agent_tools_line(fleet, shards, extra, comps),
                                 comment_style="yaml"),
               check, changed)

    pipe = root / "skills" / "lex-sanitas" / "references" / "00-mod-pipelines.md"
    _write(pipe, replace_gen_block(pipe.read_text(encoding="utf-8"),
                                   "mode-server-matrix", mode_matrix(fleet)),
           check, changed)

    return changed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="lex-sanitas filo üreticisi")
    ap.add_argument("--check", action="store_true",
                    help="yazma; fark varsa exit 1 (CI kapısı)")
    args = ap.parse_args(argv)

    root = Path(__file__).resolve().parent.parent
    fleet = load_fleet(root)
    changed = write_all(root, fleet, check=args.check)

    if args.check and changed:
        print("SÜRÜKLENME — türetilmiş dosyalar güncel değil:", file=sys.stderr)
        for c in changed:
            print(f"  · {c}", file=sys.stderr)
        print("  Çözüm: python3 tools/gen_fleet.py", file=sys.stderr)
        return 1

    c = build_lock(fleet)["counts"]
    for path in changed:
        print(f"yazıldı: {path}")
    print(f"filo: {c['servers']} server ({c['gated']} gated / {c['public']} public), "
          f"{c['companions']} companion, {c['delegations']} delegasyon")
    return 0


if __name__ == "__main__":
    sys.exit(main())
