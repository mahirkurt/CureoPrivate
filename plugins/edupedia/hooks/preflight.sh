#!/bin/bash
# Backward-compatibility wrapper -> hooks/scripts/session_start.py
exec python3 "$(dirname "$0")/scripts/session_start.py" "$@"
