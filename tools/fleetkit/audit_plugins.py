#!/usr/bin/env python3
"""CureoPrivate plugin filosu denetimi — lex-sanitas v3.5.0 denetiminin genellemesi.

Beş eksen:
  [A] CANLI MCP SAĞLIĞI   her uca gerçek `initialize`; auth_missing ≠ unauthorized
  [B] ENV KANONİKLİĞİ     her Bearer env adı Doppler'da var mı
  [C] SÜRÜM SÜRÜKLENMESİ  plugin.json ↔ marketplace.json ↔ codex ↔ SKILL.md
  [D] YAPISAL HİJYEN      çift hooks.json, eksik hook betiği, commit'li __pycache__
  [E] KURULUM DURUMU      enabledPlugins'te var mı

Prob istemcisi lex-sanitas/hooks/scripts/fleet_probe.py ile aynı sertleştirmeleri
taşır (açık UA / 256KB okuma / 12s eşik) — aksi hâlde sağlıklı server'lar sahte
arızalı görünür.
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request


class KeepPost(urllib.request.HTTPRedirectHandler):
    """307/308'i METOT ve GÖVDE korunarak takip eder.

    FastMCP /mcp altına mount edildiğinde bare POST /mcp → 307 /mcp/ döner
    (CLAUDE.md edupedia notu). urllib bunu takip etmez → sağlıklı server sahte
    'error 307' görünür. Bu handler o yanlış-pozitifi kapatır.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (307, 308):
            return urllib.request.Request(
                newurl, data=req.data, headers=req.headers,
                method=req.get_method(), unverifiable=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(KeepPost)
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path("/mnt/thunderbolt/workspaces/CureoPrivate")
USER_AGENT = "cureonics-plugin-audit/1.0 (+https://cureonics.com)"
INIT = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
               "clientInfo": {"name": "audit", "version": "1"}},
}).encode()
TIMEOUT, READ_LIMIT = 12.0, 262144
ENV_RX = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


# ── [A] canlı prob ──────────────────────────────────────────────────────────
def classify(http, body):
    if http in (401, 403):
        return "unauthorized"
    if http is None or http >= 500:
        return "unreachable"
    if http != 200:
        return "error"
    cands = [body] + [l[5:].strip() for l in body.splitlines() if l.startswith("data:")]
    for raw in cands:
        raw = raw.strip()
        if raw.startswith("{"):
            try:
                p = json.loads(raw)
            except ValueError:
                continue
            return "error" if "error" in p else ("ok" if "result" in p else "error")
    return "error"


def probe(target):
    url, env_name, needs_uc = target
    key = os.environ.get(env_name) if env_name else None
    if needs_uc:
        return target, {"status": "user_config", "http": None,
                        "detail": "user_config ile parametrelenmiş (env değil)"}
    if env_name and not key:
        return target, {"status": "auth_missing", "http": None,
                        "detail": f"${env_name} ortamda yok"}
    h = {"Content-Type": "application/json",
         "Accept": "application/json, text/event-stream", "User-Agent": USER_AGENT}
    if key:
        h["Authorization"] = f"Bearer {key}"
    try:
        req = urllib.request.Request(url, data=INIT, headers=h, method="POST")
        with OPENER.open(req, timeout=TIMEOUT) as r:
            b = r.read(READ_LIMIT).decode("utf-8", "replace")
            return target, {"status": classify(r.status, b), "http": r.status, "detail": ""}
    except urllib.error.HTTPError as e:
        try:
            b = e.read(READ_LIMIT).decode("utf-8", "replace")
        except Exception:
            b = ""
        return target, {"status": classify(e.code, b), "http": e.code,
                        "detail": b[:90].replace("\n", " ")}
    except Exception as e:
        return target, {"status": "unreachable", "http": None, "detail": type(e).__name__}


# ── Toplama ─────────────────────────────────────────────────────────────────
def load_plugins():
    mp = {p["name"]: p.get("version")
          for p in json.loads((ROOT / ".claude-plugin" / "marketplace.json")
                              .read_text(encoding="utf-8"))["plugins"]}
    try:
        enabled = json.loads(Path(os.path.expanduser("~/.claude/settings.json"))
                             .read_text(encoding="utf-8")).get("enabledPlugins", {})
    except Exception:
        enabled = {}

    out = []
    for d in sorted((ROOT / "plugins").iterdir()):
        man = d / ".claude-plugin" / "plugin.json"
        if not man.is_file():
            continue
        m = json.loads(man.read_text(encoding="utf-8"))
        name = m["name"]
        servers = {}
        mcp = d / ".mcp.json"
        if mcp.is_file():
            for sn, sv in json.loads(mcp.read_text(encoding="utf-8")).get("mcpServers", {}).items():
                url = sv.get("url")
                auth = sv.get("headers", {}).get("Authorization", "")
                envs = ENV_RX.findall(auth)
                uc = "user_config" in (auth + (url or ""))
                if url and "user_config" in url:
                    uc = True
                servers[sn] = {"url": url, "env": envs[0] if envs else None,
                               "user_config": uc, "has_auth_header": bool(auth)}
        codex = d / ".codex-plugin" / "plugin.json"
        codex_v = (json.loads(codex.read_text(encoding="utf-8")).get("version")
                   if codex.is_file() else None)
        skill_v = None
        for sk in (d / "skills").glob("*/SKILL.md"):
            mt = re.search(r"^version:\s*(\S+)\s*$", sk.read_text(encoding="utf-8"), re.M)
            if mt and sk.parent.name in (name, f"{name}-start"):
                skill_v = mt.group(1)
                if sk.parent.name == name:
                    break
        out.append({
            "name": name, "dir": d, "version": m.get("version"),
            "marketplace": mp.get(name), "codex": codex_v, "skill": skill_v,
            "servers": servers,
            "enabled": enabled.get(f"{name}@cureonics-marketplace"),
        })
    return out


def candidate_keys(server_name, url, dop):
    """Bu server için Doppler'da makul bir Bearer anahtarı var mı?

    Ayrım noktası: anahtar VARSA header'ın eksikliği bir wiring arızasıdır
    (titck/mufredat sınıfı). Anahtar HİÇ yoksa server zaten interaktif OAuth
    ile bağlanıyordur ve 401 beklenen davranıştır.
    """
    if not dop:
        return []
    # 'mcp'/'api' gibi jenerik host etiketleri HER anahtarla eşleşir (mcp.consensus.app
    # → 'mcp' → tüm *_MCP_API_KEY'ler). Bunlar elenmezse heuristik işe yaramaz.
    GENERIC = {"mcp", "api", "www", "app", "com", "net", "org", "io", "dev",
               "connector", "gateway", "server", "cloud", "workers"}
    stems = set()
    host = (url or "").split("//")[-1].split("/")[0]
    for raw in [server_name] + host.split("."):
        s = re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")
        for cand in {s, *(s[: -len(x)] for x in ("_cache", "_mcp", "_origin") if s.endswith(x))}:
            if cand and cand not in GENERIC and len(cand) >= 4:
                stems.add(cand)
    out = []
    for k in dop:
        kl = k.lower()
        if not kl.endswith("_api_key"):
            continue
        if any(st in kl for st in stems):
            out.append(k)
    return sorted(out)


def structural(p):
    d, issues = p["dir"], []
    if (d / "hooks.json").is_file() and (d / "hooks" / "hooks.json").is_file():
        issues.append("çift hooks.json (kök + hooks/)")
    hj = next((x for x in (d / "hooks.json", d / "hooks" / "hooks.json") if x.is_file()), None)
    if hj:
        txt = hj.read_text(encoding="utf-8")
        for m in re.finditer(r"hooks/scripts/([A-Za-z0-9_]+\.py)", txt):
            if not (d / "hooks" / "scripts" / m.group(1)).is_file():
                issues.append(f"hook betiği eksik: {m.group(1)}")
    tracked = subprocess.run(["git", "ls-files", str(d.relative_to(ROOT))],
                             cwd=ROOT, capture_output=True, text=True).stdout
    if "__pycache__" in tracked or ".pyc" in tracked:
        issues.append("commit'li __pycache__/.pyc")
    for sn, sv in p["servers"].items():
        if sv["url"] and not sv["url"].rstrip("/").endswith("/mcp") and "?" not in sv["url"]:
            issues.append(f"{sn}: url '/mcp' ile bitmiyor")
    return issues


def main():
    plugins = load_plugins()

    targets, who = set(), defaultdict(list)
    for p in plugins:
        for sn, sv in p["servers"].items():
            if not sv["url"]:
                continue
            t = (sv["url"], sv["env"], sv["user_config"])
            targets.add(t)
            who[t].append((p["name"], sn))

    print(f"[A] CANLI PROB — {len(targets)} benzersiz uç, {len(plugins)} plugin\n")
    results = {}
    with ThreadPoolExecutor(max_workers=24) as pool:
        for fut in as_completed([pool.submit(probe, t) for t in targets]):
            t, r = fut.result()
            results[t] = r

    # Doppler secret adları
    try:
        dop = set(json.loads(subprocess.run(
            ["doppler", "secrets", "-p", "cureohub", "-c", "dev_personal",
             "--only-names", "--json"], capture_output=True, text=True, timeout=60).stdout))
    except Exception:
        dop = None

    SYM = {"ok": "✓", "auth_missing": "○", "unauthorized": "✗", "unreachable": "✗",
           "error": "!", "user_config": "◇"}
    findings = defaultdict(list)

    for p in plugins:
        rows, worst = [], []
        for sn, sv in sorted(p["servers"].items()):
            if not sv["url"]:
                rows.append(f"    ?  {sn:22s} (url yok)")
                continue
            r = results[(sv["url"], sv["env"], sv["user_config"])]
            st = r["status"]
            rows.append(f"    {SYM.get(st,'?')} {sn:22s} {st:13s} "
                        f"{str(r['http'] or '-'):>4}  {(r['detail'] or '')[:42]}")
            if st == "unauthorized":
                if sv["has_auth_header"]:
                    worst.append(sn)
                    findings["A-401"].append(
                        f"{p['name']} · {sn} → 401 (header VAR, anahtar geçersiz/emekli)")
                else:
                    cand = candidate_keys(sn, sv["url"], dop)
                    if cand:
                        worst.append(sn)
                        findings["A-401"].append(
                            f"{p['name']} · {sn} → 401, header YOK ama Doppler'da "
                            f"aday anahtar var: {', '.join(cand)}")
                    else:
                        rows[-1] = rows[-1].replace("unauthorized ", "oauth-interakt")
                        findings["A-oauth"].append(
                            f"{p['name']} · {sn} ({sv['url']}) — interaktif OAuth, "
                            f"Bearer env'i yok (beklenen)")
            elif st in ("unreachable", "error"):
                findings["A-down"].append(f"{p['name']} · {sn} → {st}")
            if dop is not None and sv["env"] and sv["env"] not in dop:
                findings["B-env"].append(f"{p['name']} · {sn} → ${sv['env']} Doppler'da YOK")

        vs = {"plugin": p["version"], "marketplace": p["marketplace"]}
        if p["codex"]:
            vs["codex"] = p["codex"]
        if p["skill"]:
            vs["skill"] = p["skill"]
        vmis = len(set(vs.values())) > 1
        if vmis:
            findings["C-ver"].append(f"{p['name']} → {vs}")
        st_issues = structural(p)
        for i in st_issues:
            findings["D-struct"].append(f"{p['name']} → {i}")
        if not p["enabled"]:
            findings["E-inst"].append(f"{p['name']} → kurulu değil")

        flag = "🔴" if worst else ("🟠" if (vmis or st_issues) else "🟢")
        print(f"{flag} {p['name']}  v{p['version']}"
              f"{'  ⚠ sürüm: ' + str(vs) if vmis else ''}"
              f"{'  [kurulu değil]' if not p['enabled'] else ''}")
        for r in rows:
            print(r)
        for i in st_issues:
            print(f"    ⚠ yapısal: {i}")
        print()

    print("=" * 78)
    print("BULGU ÖZETİ")
    labels = {"A-401": "🔴 [A] 401/403 — YAPILANDIRMA ARIZASI (titck sınıfı)",
              "A-oauth": "🔵 [A] interaktif OAuth connector (401 beklenen — arıza DEĞİL)",
              "A-down": "🟠 [A] erişilemez / geçersiz yanıt",
              "B-env": "🔴 [B] env adı Doppler'da yok",
              "C-ver": "🟠 [C] sürüm sürüklenmesi",
              "D-struct": "🟠 [D] yapısal hijyen",
              "E-inst": "🔵 [E] kurulu değil"}
    for k, lab in labels.items():
        if findings[k]:
            print(f"\n{lab}  ({len(findings[k])})")
            for f in findings[k]:
                print(f"   · {f}")
    if not any(findings.values()):
        print("\n  temiz.")


if __name__ == "__main__":
    main()
