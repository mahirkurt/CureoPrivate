#!/usr/bin/env python3
"""Cureonics filo üreticisi — plugin-agnostik. Kaynak: <plugin>/fleet.yaml.

Üretilenler (hepsi opsiyonel, fleet.yaml neyi bildiriyorsa):
  <plugin>/.mcp.json                    Claude Code MCP wiring
  <plugin>/.codex-plugin/plugin.json    mcpServers bloğu + version (yerinde)
  <plugin>/fleet.lock.json              hook'ların okuduğu stdlib türev
  fleet.yaml `generated_blocks` ile bildirilen ⟨GEN⟩ blokları

Kullanım:
  python3 tools/fleetkit/gen_fleet.py                 tüm plugin'ler
  python3 tools/fleetkit/gen_fleet.py lex-sanitas     tek plugin
  python3 tools/fleetkit/gen_fleet.py --check         yazma; fark varsa exit 1

NEDEN VAR: filo tanımı plugin başına 3-8 yerde elle tutuluyordu. 2026-08-06
denetiminde bunun üç ölü katman (edupedia/maarif-mufredat, evidentia/titck-cache,
vekayinuvis/tavily — hepsi 401), iki tamamen sapmış codex bloğu
(brand-ecosystem-core: 7 gerçek server'ın hiçbiri yok, olmayan 3 tanesi var) ve
beş sürüm sürüklenmesi ürettiği ölçüldü.

Bu betik PyYAML kullanır ve YALNIZ geliştirme zamanında koşar. Hook'lar onu
import ETMEZ — fleet.lock.json'u stdlib json ile okurlar.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
PLUGINS = REPO / "plugins"

# `tier` serbest metindir: her plugin kendi taksonomisini kullanır (lex-sanitas
# primary/comparative/doctrine…, evidentia K/K-epi/O). Sabit bir liste dayatmak
# mevcut sözlükleri yeniden yazmak olurdu — doğrulama yalnız boş-olmama arar.
GATES = {None, "G5", "G6", "G7"}
SERVER_REQUIRED = {"name", "url", "auth_env"}

GEN_WARNING = ("ÜRETİLMİŞ DOSYA — elle düzenlemeyin. "
               "Kaynak: fleet.yaml → python3 tools/fleetkit/gen_fleet.py")


# ── Yükleme / doğrulama ─────────────────────────────────────────────────────

def plugin_dirs(only=None):
    for d in sorted(PLUGINS.iterdir()):
        if not (d / "fleet.yaml").is_file():
            continue
        if only and d.name not in only:
            continue
        yield d


def load_fleet(root: Path) -> dict:
    fleet = yaml.safe_load((root / "fleet.yaml").read_text(encoding="utf-8"))
    validate_fleet(fleet)
    return fleet


def validate_fleet(fleet: dict) -> None:
    """Şema ihlallerinde ValueError — sessiz bozuk üretim olmaz."""
    for key in ("version", "plugin", "plugin_version", "servers"):
        if key not in fleet:
            raise ValueError(f"fleet.yaml: '{key}' alanı eksik")

    seen = set()
    for s in fleet["servers"]:
        missing = SERVER_REQUIRED - set(s)
        if missing:
            raise ValueError(
                f"server {s.get('name')!r}: eksik alan(lar) {sorted(missing)}")
        if s["name"] in seen:
            raise ValueError(f"server adı tekrarlı: {s['name']}")
        seen.add(s["name"])
        if "tier" in s and not str(s["tier"]).strip():
            raise ValueError(f"{s['name']}: tier boş — ya anlamlı değer ver ya alanı sil")
        if s.get("gate") not in GATES:
            raise ValueError(f"{s['name']}: geçersiz gate {s.get('gate')!r}")
        if not str(s["url"]).startswith("http"):
            raise ValueError(f"{s['name']}: url http(s) ile başlamalı")

    comp = {c["name"] for c in fleet.get("companions", [])}
    if seen & comp:
        raise ValueError(f"wire'lı server companion olamaz: {sorted(seen & comp)}")


# ── Türev gövdeler ──────────────────────────────────────────────────────────

def build_lock(fleet: dict) -> dict:
    """Hook'ların okuduğu stdlib türev — role/tools_used/degrade taşımaz."""
    keys = ("name", "url", "tier", "auth_env", "shard", "modes", "gate", "headers")
    servers = [{k: s.get(k) for k in keys if k in s or k in ("auth_env",)}
               for s in fleet["servers"]]
    gated = sum(1 for s in servers if s.get("auth_env"))
    return {
        "_generated": GEN_WARNING,
        "plugin": fleet["plugin"],
        "plugin_version": fleet["plugin_version"],
        "counts": {
            "servers": len(servers),
            "gated": gated,
            "public": len(servers) - gated,
            "companions": len(fleet.get("companions", [])),
            "delegations": len(fleet.get("delegations", [])),
        },
        "servers": servers,
        "companions": fleet.get("companions", []),
        "delegations": fleet.get("delegations", []),
    }


def _squash(text) -> str:
    return " ".join(str(text).split())


def build_mcp_servers(fleet: dict) -> dict:
    """`.mcp.json` / codex için mcpServers bloğu."""
    out = {}
    for s in fleet["servers"]:
        entry = {"type": s.get("type", "http"), "url": s["url"]}
        if s.get("auth_env"):
            entry["headers"] = {"Authorization": "Bearer ${%s}" % s["auth_env"]}
        elif s.get("headers"):
            entry["headers"] = s["headers"]
        if s.get("tier"):
            entry["_tier"] = s["tier"]
        if s.get("role"):
            entry["_role"] = _squash(s["role"])
        for k, v in (s.get("extra") or {}).items():
            entry[k] = _squash(v) if isinstance(v, str) else v
        out[s["name"]] = entry
    return out


def build_mcp_json(fleet: dict) -> dict:
    c = build_lock(fleet)["counts"]
    note = fleet.get("mcp_comment", "")
    comment = (f"{GEN_WARNING} — {fleet['plugin']} MCP wiring. "
               f"{c['servers']} server ({c['gated']} Bearer-gated, {c['public']} public)"
               + (f", {c['companions']} companion" if c["companions"] else "")
               + ". Auth'lu server'lar Doppler-injected Bearer bekler; anahtar yoksa "
                 "o katman graceful degrade eder (asla uydurma). "
               + (note and f"{_squash(note)} ")).strip()
    return {"_comment": comment, "mcpServers": build_mcp_servers(fleet)}


def replace_gen_block(text: str, name: str, body: str, style: str = "html") -> str:
    """⟨GEN⟩ bloğunun içini değiştirir (html yorumu veya YAML `#` yorumu)."""
    if style == "yaml":
        begin, end = f"# GEN:{name} BEGIN", f"# GEN:{name} END"
    else:
        begin, end = f"<!-- GEN:{name} BEGIN -->", f"<!-- GEN:{name} END -->"
    rx = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)
    if not rx.search(text):
        raise ValueError(f"⟨GEN⟩ bloğu bulunamadı: {name} ({style})")
    return rx.sub(lambda _: f"{begin}\n{body}\n{end}", text, count=1)


# ── ⟨GEN⟩ blok üreticileri ──────────────────────────────────────────────────

def gen_env_table(fleet, _cfg):
    rows = ["| Server | Tier | Env-var (Doppler → Bearer) |", "|---|---|---|"]
    for s in fleet["servers"]:
        env = f"`{s['auth_env']}`" if s.get("auth_env") else "_(public — anahtar yok)_"
        rows.append(f"| `{s['name']}` | {s.get('tier', '—')} | {env} |")
    for c in fleet.get("companions", []):
        rows.append(f"| {c['name']} | companion | "
                    f"_(claude.ai connector — env anahtarı yok)_ |")
    return "\n".join(rows)


def server_prefixes(s, plugin=None):
    """Bir sunucunun araç önekleri — AYNI sunucu yüzeye göre ÜÇ farklı adla yüklenir.

    1. **Plugin'e paketli (Claude Code, KANONİK yol).** Plugin'in `.mcp.json`'ı
       yüklendiğinde önek plugin adıyla NAMESPACE'LENİR:
       `mcp__plugin_<plugin>_<server>__`. 2026-08-07 oturumunda dokuz sunucuda
       ölçüldü (lex-sanitas/edupedia/vekayinuvis/rxpraxis/sci-audit) — kural
       dokuzunda da tuttu. Plugin kurulu olduğunda GERÇEKTE yüklenen budur.
    2. **Kullanıcı düzeyi `.mcp.json`** (plugin dışı, `~/.claude.json` vb.) →
       çıplak `mcp__<server>__`.
    3. **claude.ai/Cowork connector'ı** → `mcp__claude_ai_<Görünen_Ad>__`;
       boşluk `_` olur, ASCII-dışı harf düşer ya da `_` olur (ölçülen:
       "TİTCK Data"→T_TCK_Data, "Yargı"→Yarg, "Türk Patent"→T_rk_Patent).
       Görünen ad bir İNSAN TERCİHİ olduğu için mekanik türetilemez → ampirik
       olarak gözlenmiş adlar fleet.yaml'da `tool_prefixes` ile AÇIKÇA yazılır.

    Bu ayrım kritik: ajanların `tools:` frontmatter'ı SERT bir allowlist'tir —
    model öneki yorumla kapatamaz. Önek eşleşmezse sunucu ajan için YOKTUR.
    Üçünü birden yaymak ucuzdur: tutan çalışır, tutmayan zararsızca boşta kalır.

    `tool_prefixes` verilse bile plugin-kapsamlı biçim DAİMA eklenir — o
    kullanıcı tercihine değil, kurulum mekaniğine bağlıdır.
    """
    n = s["name"]
    out = []
    if plugin:
        out.append(f"mcp__plugin_{plugin}_{n}__")
    if s.get("tool_prefixes"):
        out += [p for p in s["tool_prefixes"] if p not in out]
        return out
    out += [f"mcp__{n}__", f"mcp__claude_ai_{n}__"]
    title = "_".join(w.capitalize() for w in re.split(r"[-_ ]+", n) if w)
    if title != n:
        out.append(f"mcp__claude_ai_{title}__")
    return out


def gen_agent_tools(fleet, cfg):
    shards = cfg.get("shards", [])

    def in_shard(s):
        """`shard` tek değer VEYA liste olabilir.

        Bir sunucu gerçekten iki shard'a ait olabilir — turk-patent hem TR
        çekirdeğidir (S1: TÜRKPATENT Türkiye'nin kendi sicili) hem de
        karşılaştırmalı çalışmada IP-kesişimi katmanıdır (S2, mod matrisinde
        COMPARATIVE_LAW'a atanmış). Tek değere zorlanınca ya S2 distiller'ı onu
        çağıramaz (ajan `tools:` KATI allowlist'tir → IP katmanı sessizce düşer)
        ya da `ALL` yazılıp substrat gibi gösterilir. Liste ikisini de önler.
        """
        sh = s.get("shard")
        vals = sh if isinstance(sh, list) else [sh]
        return (not shards) or "ALL" in vals or any(v in shards for v in vals)

    picked = [s for s in fleet["servers"] if in_shard(s)]
    tools = list(cfg.get("extra", []))
    plug = fleet.get("plugin")
    tools += [f"{p}*" for s in picked for p in server_prefixes(s, plug)]
    if cfg.get("companions"):
        tools += [f"{p}*" for c in fleet.get("companions", [])
                  for p in c.get("tool_prefixes", [])]
    return "tools: " + ", ".join(tools)


def gen_mode_matrix(fleet, cfg):
    modes = cfg.get("modes") or []
    if not modes:
        return "_(mod tanımlı değil)_"
    abbr = cfg.get("abbr", {})
    rows = ["| Server | " + " | ".join(abbr.get(m, m[:6]) for m in modes) + " |",
            "|---|" + "---|" * len(modes)]
    for s in fleet["servers"]:
        act = s.get("modes", ["ALL"])
        cells = ["✓" if ("ALL" in act or m in act) else "·" for m in modes]
        rows.append(f"| `{s['name']}` ({s.get('tier', '—')}) | " + " | ".join(cells) + " |")
    for c in fleet.get("companions", []):
        act = c.get("modes", ["ALL"])
        cells = ["✓" if ("ALL" in act or m in act) else "·" for m in modes]
        rows.append(f"| **{c['name']}** (companion) | " + " | ".join(cells) + " |")
    rows += ["", "> `✓` = bu modda taranır · `·` = bu modda **mantıksal olarak N/A** "
                 "→ manifestoda `skipped: mod için N/A` yazılır (satır atlanamaz)."]
    return "\n".join(rows)


GENERATORS = {"env_table": gen_env_table, "agent_tools": gen_agent_tools,
              "mode_matrix": gen_mode_matrix}


# ── Yazma ───────────────────────────────────────────────────────────────────

def _write(path: Path, content: str, check: bool, changed: list) -> None:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return
    changed.append(str(path.relative_to(REPO)))
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _json_text(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def write_all(root: Path, fleet: dict, check: bool = False) -> list:
    changed = []
    _write(root / "fleet.lock.json", _json_text(build_lock(fleet)), check, changed)
    _write(root / ".mcp.json", _json_text(build_mcp_json(fleet)), check, changed)

    codex = root / ".codex-plugin" / "plugin.json"
    if codex.is_file():
        d = json.loads(codex.read_text(encoding="utf-8"))
        d["version"] = fleet["plugin_version"]
        d["mcpServers"] = build_mcp_servers(fleet)
        _write(codex, _json_text(d), check, changed)

    for blk in fleet.get("generated_blocks", []):
        path = root / blk["file"]
        if not path.is_file():
            raise ValueError(f"{fleet['plugin']}: ⟨GEN⟩ hedefi yok: {blk['file']}")
        body = GENERATORS[blk["generator"]](fleet, blk.get("config", {}))
        _write(path, replace_gen_block(path.read_text(encoding="utf-8"),
                                       blk["name"], body,
                                       blk.get("style", "html")),
               check, changed)
    return changed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cureonics filo üreticisi")
    ap.add_argument("plugins", nargs="*", help="plugin adları (boş = hepsi)")
    ap.add_argument("--check", action="store_true", help="yazma; fark varsa exit 1")
    args = ap.parse_args(argv)

    all_changed, total = [], 0
    for d in plugin_dirs(args.plugins or None):
        fleet = load_fleet(d)
        ch = write_all(d, fleet, check=args.check)
        all_changed += ch
        c = build_lock(fleet)["counts"]
        total += 1
        if not args.check:
            print(f"{d.name:22s} {c['servers']:>3d} server "
                  f"({c['gated']} gated / {c['public']} public)"
                  + (f", {c['companions']} companion" if c["companions"] else "")
                  + (f"  → {len(ch)} dosya" if ch else "  → güncel"))

    if args.check and all_changed:
        print("SÜRÜKLENME — türetilmiş dosyalar güncel değil:", file=sys.stderr)
        for c in all_changed:
            print(f"  · {c}", file=sys.stderr)
        print("  Çözüm: python3 tools/fleetkit/gen_fleet.py", file=sys.stderr)
        return 1
    if not args.check:
        print(f"— {total} plugin işlendi, {len(all_changed)} dosya yazıldı")
    return 0


if __name__ == "__main__":
    sys.exit(main())
