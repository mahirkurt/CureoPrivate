#!/usr/bin/env python3
"""Mevcut `.mcp.json`'dan `fleet.yaml` üretir — tek seferlik geçiş aracı.

Elle yazılmış `_role`/`_tier`/`_probe`/`_trust`/`_scope` notları KORUNUR; bunlar
yıllar içinde birikmiş gerçek bilgidir ve yeniden yazılmaz. Geçişten sonra
kaynak fleet.yaml'dir; `.mcp.json` ondan üretilir.

Kullanım:
  python3 tools/fleetkit/bootstrap_fleet.py <plugin> [<plugin> …]
  python3 tools/fleetkit/bootstrap_fleet.py --all --force
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PLUGINS = REPO / "plugins"
ENV_RX = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

# Tarihsel tier kodları (evidentia'nın K/K-epi/O taksonomisi gibi) AYNEN korunur —
# plugin'in kendi sözlüğünü yeniden yazmak bilgi kaybıdır. Tier'ı olmayan server
# için de tier UYDURULMAZ; alan yazılmaz.


def yaml_block(text: str, indent: int = 6) -> str:
    """Uzun düzyazıyı katlanmış YAML bloğu olarak yazar (alıntı kaçışı derdi yok)."""
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 92 - indent:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    pad = " " * indent
    return ">-\n" + "\n".join(pad + ln for ln in lines)


def build(plugin: str) -> str:
    d = PLUGINS / plugin
    mcp = json.loads((d / ".mcp.json").read_text(encoding="utf-8"))
    man = json.loads((d / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))

    out = [
        f"# {plugin} MCP filosunun TEK GERÇEK KAYNAĞI.",
        "#",
        "# Şu dosyalar BURADAN ÜRETİLİR — onları elle düzenlemeyin:",
        "#   .mcp.json · .codex-plugin/plugin.json (mcpServers+version) · fleet.lock.json",
        "#",
        "# Değişiklik yolu:  bu dosyayı düzenle → `python3 tools/fleetkit/gen_fleet.py`",
        "# Denetim:          `python3 tools/fleetkit/check_drift.py --all` (ağ gerektirmez)",
        "# Canlı sağlık:     `python3 tools/fleetkit/audit_plugins.py`",
        "",
        "version: 2",
        f"plugin: {plugin}",
        f'plugin_version: "{man["version"]}"',
        "",
        "servers:",
    ]

    for name, sv in mcp.get("mcpServers", {}).items():
        auth = (sv.get("headers") or {}).get("Authorization", "")
        envs = ENV_RX.findall(auth)
        tier = sv.get("_tier")
        role = sv.get("_role")

        out.append(f"  - name: {name}")
        stype = sv.get("type", "http")
        if stype == "stdio":
            out.append("    type: stdio")
            out.append(f"    command: {sv['command']}")
            if sv.get("args"):
                out.append(f"    args: {json.dumps(sv['args'], ensure_ascii=False)}")
        else:
            out.append(f"    url: {sv['url']}")
            if stype != "http":
                out.append(f"    type: {stype}")
        if tier:
            out.append(f"    tier: {tier}")
        if envs:
            out.append(f"    auth_env: {envs[0]}")
        elif auth:
            # ${VAR} olmayan header (örn. user_config parametresi) — aynen taşı.
            out.append("    auth_env: null")
            out.append(f"    headers: {json.dumps(sv['headers'], ensure_ascii=False)}")
        else:
            out.append("    auth_env: null")
        if role:
            out.append("    role: " + yaml_block(role))

        extra = {k: v for k, v in sv.items()
                 if k.startswith("_") and k not in ("_tier", "_role")}
        if extra:
            out.append("    extra:")
            for k, v in extra.items():
                if isinstance(v, str):
                    out.append(f"      {k}: " + yaml_block(v, indent=8))
                else:
                    out.append(f"      {k}: {json.dumps(v, ensure_ascii=False)}")
        out.append("")

    return "\n".join(out).rstrip("\n") + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="fleet.yaml bootstrap")
    ap.add_argument("plugins", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true", help="mevcut fleet.yaml'i ez")
    a = ap.parse_args(argv)

    if a.all and a.force:
        ap.error("--all ile --force birlikte kullanılamaz: elle yazılmış bir "
                 "fleet.yaml'i sessizce ezer (cureolex'ta bir kez oldu). "
                 "Ezmek istediğiniz plugin'i ADIYLA verin.")
    names = ([p.name for p in sorted(PLUGINS.iterdir())
              if (p / ".mcp.json").is_file()] if a.all else a.plugins)
    if not names:
        ap.error("plugin adı ya da --all gerekli")

    for n in names:
        target = PLUGINS / n / "fleet.yaml"
        if target.exists() and not a.force:
            print(f"  ⏭  {n}: fleet.yaml zaten var (--force ile ez)")
            continue
        target.write_text(build(n), encoding="utf-8")
        import yaml
        f = yaml.safe_load(target.read_text(encoding="utf-8"))
        print(f"  ✓  {n}: {len(f['servers'])} server → fleet.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
