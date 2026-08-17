#!/bin/bash
# Backward-compatibility wrapper -> hooks/scripts/validate_module_hook.py
exec python3 "$(dirname "$0")/scripts/validate_module_hook.py" "$@"
