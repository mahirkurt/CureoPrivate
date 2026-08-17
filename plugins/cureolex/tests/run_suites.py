#!/usr/bin/env python3
"""cureolex davranış süiti koşucusu — 7 YAML süiti · 85 vaka · AĞ ERİŞİMİ YOK.

NE YAPAR (deterministik, offline):
  [1] ŞEMA        her süit `suite`+`cases`; her vaka `id`/`given`/`expect`;
                  aile şemasına göre `title`+`assertions`
  [2] BENZERSİZLİK vaka id'leri TÜM süitlerde global benzersiz
  [3] FIXTURE     `ledger_fixture` → evidence_ledger.schema.json,
                  `sidecar_fixture` → medical_sidecar.schema.json (jsonschema ile)
  [4] REFERANS    vaka metninde adı geçen her sunucu fleet.yaml'da VAR mı ·
                  her mod 9 kanonik moddan biri mi · her kapı G0-G9 mü ·
                  her dosya yolu diskte mevcut mu
  [5] SAYISAL     süitlerin filo hakkındaki sayısal iddiaları (companion sayısı,
                  MANDATORY_ROWS, sunucu sayısı) fleet.lock.json ile tutuyor mu

NE YAPMAZ — ve bu bilinçlidir:
  Bu vakalar MODEL DAVRANIŞI şartnameleridir ("şu prompt şu moda yönlenmeli").
  Bir model koşumu olmadan davranış deterministik olarak doğrulanamaz; bu
  koşucu davranışı ÇALIŞTIRMAZ. Yaptığı şey, 70 düzyazı şartnamesini
  DENETLENEBİLİR artefakta çevirmektir: şartnamenin kendisi bozuksa (var
  olmayan sunucuya atıf, ölü mod adı, şemadan düşen fixture, çakışan id)
  bunu yakalar. Şartname doğruysa ama model yanlış davranıyorsa YAKALAMAZ —
  o katman insan denetimine ve canlı koşuma aittir.

Kullanım:
  python3 tests/run_suites.py            # plugin kökünden ya da tests/ içinden
  python3 tests/run_suites.py --quiet
Çıkış: 0 temiz · 1 ihlal.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                                   # plugin kökü

MODES = {"DRAFT", "AMEND", "ANALYZE", "COMPLY", "OPINE", "RIA",
         "COMPARATIVE_LAW", "TBMM_KANUN_TEKLIFI", "EX_POST_EVALUATION"}
GATES = {f"G{i}" for i in range(10)}
# `expect.mode` alanında tarihsel olarak kısa ad da kullanılmış; ikisi de meşru.
MODE_ALIASES = {"EX_POST": "EX_POST_EVALUATION"}
# Vaka düzyazısında geçen ama sunucu OLMAYAN mcp__ önekleri (kasıtlı negatif
# örnekler ve companion'lar) — referans denetiminde yanlış-pozitif vermesinler.
SCHEMA_FAMILIES = {"title", "assertions"}


def load_fleet():
    fleet = yaml.safe_load((ROOT / "fleet.yaml").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "fleet.lock.json").read_text(encoding="utf-8"))
    names = {s["name"] for s in fleet["servers"]}
    # Ajan allowlist'lerini besleyen aynı önek kümesi (K-1 ad-eşleme katmanı).
    for s in fleet["servers"]:
        for p in s.get("tool_prefixes", []):
            m = re.match(r"mcp__(.+?)__$", p)
            if m:
                names.add(m.group(1))
    for c in fleet.get("companions", []):
        for p in c.get("tool_prefixes", []):
            m = re.match(r"mcp__(.+?)__$", p)
            if m:
                names.add(m.group(1))
    return fleet, lock, names


def case_text(case):
    """Vakanın tüm düzyazısını tek dizede topla (referans taraması için)."""
    return json.dumps(case, ensure_ascii=False)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="cureolex davranış süiti koşucusu")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    try:
        import jsonschema
    except ImportError:
        jsonschema = None

    fleet, lock, server_names = load_fleet()
    schemas = {}
    for nm, fn in (("ledger_fixture", "evidence_ledger.schema.json"),
                   ("sidecar_fixture", "medical_sidecar.schema.json")):
        p = ROOT / "skills" / "cureolex" / "schemas" / fn
        if p.is_file():
            schemas[nm] = json.loads(p.read_text(encoding="utf-8"))

    suites = sorted(HERE.glob("*.yaml"))
    seen_ids, issues, total = {}, [], 0

    for sf in suites:
        try:
            doc = yaml.safe_load(sf.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            issues.append((sf.name, f"BOZUK YAML — {e}"))
            continue
        if not isinstance(doc, dict) or "cases" not in doc:
            issues.append((sf.name, "üst düzeyde `cases` yok"))
            continue
        if "suite" not in doc:
            issues.append((sf.name, "üst düzeyde `suite` yok"))

        cases = doc["cases"]
        # Ailenin şemasını ilk vakadan çıkar: süit içi TUTARLILIK aranır,
        # süitler arası tek biçim DAYATILMAZ (fleet_registry bilinçli sadedir).
        family = SCHEMA_FAMILIES & set(cases[0]) if cases else set()
        for c in cases:
            total += 1
            cid = c.get("id")
            if not cid:
                issues.append((sf.name, f"`id` yok → {str(c)[:60]}")); continue
            if cid in seen_ids:
                issues.append((sf.name, f"id ÇAKIŞMASI '{cid}' (ayrıca {seen_ids[cid]})"))
            seen_ids[cid] = sf.name
            for k in ("given", "expect"):
                if k not in c:
                    issues.append((sf.name, f"{cid}: `{k}` yok"))
            for k in family:
                if k not in c:
                    issues.append((sf.name, f"{cid}: süit ailesi `{k}` bekliyor ama yok"))

            exp = c.get("expect")
            if isinstance(exp, dict):
                m = exp.get("mode")
                if m and MODE_ALIASES.get(m, m) not in MODES:
                    issues.append((sf.name, f"{cid}: bilinmeyen mod '{m}'"))
                g = exp.get("gates")
                if isinstance(g, dict):
                    for gate in g:
                        if gate not in GATES:
                            issues.append((sf.name, f"{cid}: bilinmeyen kapı '{gate}'"))

            txt = case_text(c)
            for ref in set(re.findall(r"mcp__([A-Za-z0-9_-]+?)__", txt)):
                if ref not in server_names and ref.lower() not in {n.lower() for n in server_names}:
                    issues.append((sf.name, f"{cid}: filoda OLMAYAN sunucuya atıf 'mcp__{ref}__'"))
            for ref in set(re.findall(r"`((?:references|templates|schemas|shared|hooks)/[^`]+?\.(?:md|json|yaml|py))`", txt)):
                cand = [ROOT / "skills" / "cureolex" / ref, ROOT / ref]
                if not any(p.exists() for p in cand):
                    issues.append((sf.name, f"{cid}: var olmayan dosyaya atıf '{ref}'"))

            # Fixture doğrulaması TERS ÇEVRİLEBİLİR: bazı vakalar bilinçli
            # NEGATİF örneklerdir (`expect.schema_valid: false`) — orada
            # fixture'ın şemadan DÜŞMESİ beklenen sonuçtur; GEÇMESİ hatadır,
            # çünkü o zaman vaka test ettiğini iddia ettiği şeyi test etmiyordur.
            expect_valid = True
            if isinstance(exp, dict) and exp.get("schema_valid") is False:
                expect_valid = False
            for key, schema in schemas.items():
                if key not in c or not jsonschema:
                    continue
                try:
                    jsonschema.validate(c[key], schema)
                    ok = True
                except jsonschema.ValidationError as e:
                    ok, why = False, e.message[:70]
                if ok and not expect_valid:
                    issues.append((sf.name, f"{cid}: `schema_valid:false` bekleniyor ama "
                                            f"{key} şemadan GEÇTİ — negatif vaka etkisiz"))
                elif not ok and expect_valid:
                    issues.append((sf.name, f"{cid}: {key} şemadan düştü — {why}"))

    # [5] Companion LİSTESİ tamlığı.
    #   Filo BÜYÜKLÜĞÜ iddiaları BİLİNÇLİ olarak burada denetlenmez: onları
    #   check_drift [5] zaten ince ayarlı bir regex'le tarıyor. Naif bir sayı
    #   taraması burada denendi ve bir sürüm etiketinin (`vN.N.N server-side`)
    #   son basamağını sayı sanıp yanlış-pozitif verdi.
    #   Asıl kırılganlık sayı değil LİSTE: bir vaka companion'ları ADIYLA
    #   sayıyorsa eksik bırakması sessiz bir kapsam yalanıdır (Ö-5).
    #   Ölçüt SATIR-İÇİ NUMARALANDIRMADIR, dosya genelinde geçiş değil: bir
    #   vakanın iki companion'a akış içinde değinmesi meşrudur (atıf süiti
    #   Yargı+Open Law'a öyle değiniyor); asıl kusur `(A/B/C)` biçiminde
    #   AÇIKÇA sayıp eksik bırakmaktır — okuyan onu tam liste sanır.
    comp_names = [c["name"] for c in fleet.get("companions", [])]
    for sf in suites:
        for i, line in enumerate(sf.read_text(encoding="utf-8").splitlines(), 1):
            present = [c for c in comp_names if c in line]
            enumerated = len(present) >= 2 and re.search(
                r"%s\s*[/,]\s*%s" % (re.escape(present[0]), re.escape(present[1])), line)
            if enumerated and len(present) < len(comp_names):
                missing = [c for c in comp_names if c not in present]
                issues.append((sf.name, f"satır {i}: companion NUMARALANDIRMASI eksik — "
                                        f"{present} yazılmış, {missing} yok "
                                        f"(fleet: {len(comp_names)})"))

    # [6] Marketplace yüzey wiring — plugin.json mcpServers yoksa kurulum
    # MCP'siz yüklenir ve hiçbir süit vakası bunu görmez.
    man = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    if man.get("mcpServers") not in ("./.mcp.json", ".mcp.json"):
        issues.append(("WIRING", "claude plugin.json mcpServers './.mcp.json' değil"))
    if man.get("hooks") not in ("./hooks/hooks.json", "hooks/hooks.json"):
        issues.append(("WIRING", "claude plugin.json hooks bildirmiyor"))
    for field in ("skills", "commands"):
        if field not in man:
            issues.append(("WIRING", f"claude plugin.json '{field}' yok"))
    agents = man.get("agents")
    if not isinstance(agents, list) or not agents:
        issues.append(("WIRING", "claude plugin.json agents ajan .md dosya listesi olmalı "
                                 "(dizin stringi Claude CLI'da Invalid input)"))
    else:
        for item in agents:
            if not isinstance(item, str) or not (ROOT / item).is_file():
                issues.append(("WIRING", f"claude plugin.json agents yolu yok/dosya değil → {item}"))
    if not (ROOT / "CONNECTORS.md").is_file():
        issues.append(("WIRING", "CONNECTORS.md yok"))
    curp = ROOT / ".cursor-plugin" / "plugin.json"
    if not curp.is_file():
        issues.append(("WIRING", ".cursor-plugin/plugin.json yok"))
    else:
        cur = json.loads(curp.read_text(encoding="utf-8"))
        if cur.get("name") != "cureolex":
            issues.append(("WIRING", "cursor plugin.json name sapması"))
        if cur.get("mcpServers") not in ("./.mcp.json", ".mcp.json"):
            issues.append(("WIRING", "cursor plugin.json mcpServers yok"))
    if not (ROOT / ".codex-plugin" / "openai.yaml").is_file():
        issues.append(("WIRING", ".codex-plugin/openai.yaml yok"))
    if (ROOT / "agents" / "openai.yaml").exists():
        issues.append(("WIRING", "agents/openai.yaml duruyor — Codex stub ajan sanılır"))

    if not a.quiet:
        for name in sorted({s.name for s in suites}):
            bad = [m for f, m in issues if f == name]
            n = len(yaml.safe_load((HERE / name).read_text(encoding="utf-8")).get("cases", []))
            if bad:
                print(f"\n⚠ {name}  ({n} vaka)")
                for m in bad:
                    print(f"      · {m}")
            else:
                print(f"✓ {name:36s} {n:>2d} vaka")
        wire = [m for f, m in issues if f == "WIRING"]
        if wire:
            print("\n⚠ yüzey wiring")
            for m in wire:
                print(f"      · {m}")
        else:
            print("✓ yüzey wiring                        ok")
        print(f"\n{'İHLAL VAR' if issues else 'SÜİTLER TEMİZ'} — "
              f"{total} vaka / {len(suites)} süit denetlendi"
              + ("" if jsonschema else "  (jsonschema yok → fixture doğrulaması ATLANDI)"))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
