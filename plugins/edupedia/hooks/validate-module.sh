#!/bin/bash
set -e
# hook stdin JSON'undan dosya yolunu çek (tool_input.file_path)
FILE=$(cat | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || true)
[ -z "$FILE" ] && exit 0
case "$FILE" in *.html) ;; *) exit 0;; esac
grep -q "MODULE_DATA" "$FILE" 2>/dev/null || exit 0
V="${CLAUDE_PLUGIN_ROOT}/skills/carbon-edupedia/scripts/validate_module.py"
python3 "$V" "$FILE" || echo "Edupedia doğrulama: yukarıdaki kapı ihlallerini gözden geçirin (bloke etmez)."
exit 0
