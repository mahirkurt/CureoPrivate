#!/usr/bin/env bash
# tests/check_engine.sh — motor inline script'ini çıkarıp node --check
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="${1:-$SCRIPT_DIR/../assets/module-template.html}"
tmp=$(mktemp "${TMPDIR:-/tmp}/edupedia_engine.XXXXXX.js")
trap 'rm -f "$tmp"' EXIT
python3 - "$T" > "$tmp" <<'PY'
import sys,re
h=open(sys.argv[1],encoding='utf-8').read()
for m in re.finditer(r'<script>(.*?)</script>', h, re.S): sys.stdout.write(m.group(1)+"\n")
PY
node --check "$tmp" && echo "ENGINE SYNTAX OK"
