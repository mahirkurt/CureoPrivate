#!/usr/bin/env python3
"""
g_identity.py — G-IDENTITY gate. Every self-host Worker must identify itself
consistently in all four places its name is user-visible.

WHY THIS EXISTS (2026-08-07 audit finding MAJOR-3): `auth.ts` is propagated
between Workers by copy. The copy carried `const REALM = "openfda-mcp"` into
ema/globocan/who-gho and a header comment naming `drugddx-mcp` into five of the
seven. REALM is not cosmetic — it feeds:

  * `resource_name` in the RFC 9728 protected-resource metadata (auth.ts ~L140)
  * the OAuth `client_id` returned by dynamic registration (~L169)
  * the <title>/<h1> of the AUTHORIZE CONSENT PAGE the user reads when adding
    the connector in claude.ai / ChatGPT / grok (~L190/L194)
  * the 401 `WWW-Authenticate: Bearer realm="…"` (~L260)

So three production Workers told users they were `openfda-mcp`, and three
distinct Workers registered under one `client_id` string. Live-verified against
`/.well-known/oauth-protected-resource` before the fix.

The routing/auth suites cannot catch this: each Worker's tests would happily
assert whatever wrong constant is compiled in. Only a CROSS-WORKER comparison
sees it. That is this gate.

Checks, per Worker directory under self-host/:
  1. auth.ts        `const REALM = "<dir>"`
  2. auth.ts        header comment names `<dir>`
  3. package.json   `"name": "<dir>"`
  4. wrangler.jsonc `"name": "<dir>"`

Stdlib only, no network. Exit 0 = consistent, 1 = drift, 2 = setup error.
Usage:  python3 scripts/g_identity.py [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SELF_HOST = Path(__file__).resolve().parent.parent / "self-host"

GREEN, RED, YELLOW, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"

REALM_RE = re.compile(r'^const REALM = "([^"]+)";', re.M)
HEADER_RE = re.compile(r"^ \* auth\.ts .* for the ([A-Za-z0-9-]+) Worker", re.M)
# wrangler.jsonc is JSON-with-comments; a plain regex is safer than a JSONC parser.
WRANGLER_NAME_RE = re.compile(r'^\s*"name":\s*"([^"]+)"', re.M)


def check(worker_dir: Path) -> dict:
    name = worker_dir.name
    row = {"worker": name, "realm": None, "header": None, "package": None,
           "wrangler": None, "problems": []}

    auth = worker_dir / "src" / "auth.ts"
    if auth.exists():
        text = auth.read_text(encoding="utf-8")
        m = REALM_RE.search(text)
        row["realm"] = m.group(1) if m else None
        h = HEADER_RE.search(text)
        row["header"] = h.group(1) if h else None
        if row["realm"] is None:
            row["problems"].append("auth.ts: `const REALM = \"…\"` bulunamadı")
        elif row["realm"] != name:
            row["problems"].append(
                f'auth.ts REALM="{row["realm"]}" ≠ "{name}" — bu değer onay '
                f"sayfasında, client_id'de, PRM resource_name'de ve 401 realm'inde görünür")
        if row["header"] is not None and row["header"] != name:
            row["problems"].append(
                f'auth.ts başlık yorumu "{row["header"]}" diyor, Worker "{name}"')
    else:
        row["problems"].append("src/auth.ts yok")

    pkg = worker_dir / "package.json"
    if pkg.exists():
        try:
            row["package"] = json.loads(pkg.read_text(encoding="utf-8")).get("name")
        except json.JSONDecodeError as e:
            row["problems"].append(f"package.json ayrıştırılamadı: {e}")
        if row["package"] is not None and row["package"] != name:
            row["problems"].append(f'package.json name="{row["package"]}" ≠ "{name}"')
    else:
        row["problems"].append("package.json yok")

    wr = worker_dir / "wrangler.jsonc"
    if wr.exists():
        m = WRANGLER_NAME_RE.search(wr.read_text(encoding="utf-8"))
        row["wrangler"] = m.group(1) if m else None
        if row["wrangler"] is None:
            row["problems"].append("wrangler.jsonc: `\"name\"` bulunamadı")
        elif row["wrangler"] != name:
            row["problems"].append(
                f'wrangler.jsonc name="{row["wrangler"]}" ≠ "{name}" '
                "(deploy hedefi yanlış Worker'a gider)")
    else:
        row["problems"].append("wrangler.jsonc yok")

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="G-IDENTITY — self-host Worker kimlik tutarlılığı")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not SELF_HOST.is_dir():
        print(f"{RED}SETUP ERROR{RESET}: {SELF_HOST} yok")
        return 2

    workers = sorted(d for d in SELF_HOST.iterdir()
                     if d.is_dir() and (d / "package.json").exists())
    if not workers:
        print(f"{RED}SETUP ERROR{RESET}: {SELF_HOST} altında Worker bulunamadı")
        return 2

    rows = [check(w) for w in workers]
    bad = [r for r in rows if r["problems"]]

    if args.json:
        print(json.dumps({"workers": rows, "failed": [r["worker"] for r in bad]},
                         ensure_ascii=False, indent=2))
        return 1 if bad else 0

    print("G-IDENTITY — self-host Worker kimliği (REALM · başlık · package · wrangler)\n")
    for r in rows:
        mark = f"{GREEN}OK  {RESET}" if not r["problems"] else f"{RED}DRIFT{RESET}"
        print(f"  {mark} {r['worker']:20} REALM={str(r['realm']):20} "
              f"pkg={str(r['package']):20} wrangler={r['wrangler']}")
        for p in r["problems"]:
            print(f"        {YELLOW}·{RESET} {p}")

    print(f"\n  {len(rows)} Worker denetlendi · {len(rows) - len(bad)} tutarlı · {len(bad)} sürüklenmiş")
    if bad:
        print(f"\n{RED}IDENTITY DRIFT: {', '.join(r['worker'] for r in bad)}{RESET}")
        print("  → auth.ts kopyalanırken REALM yerelleştirilmemiş olabilir (2026-08-07 MAJOR-3).")
        return 1
    print(f"\n{GREEN}IDENTITY CONSISTENT{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
