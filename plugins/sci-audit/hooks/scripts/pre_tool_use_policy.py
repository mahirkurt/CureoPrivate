#!/usr/bin/env python3
"""PreToolUse hook (Layer 1: deterministic gate / universal destructive-command guard).

Catches Bash commands BEFORE they run and denies destructive operations plus
commands that read or exfiltrate credential/environment files. File-tool access
(Read/Grep/Glob/Edit) is additionally controllable via `permissions.deny` in
`.claude/settings.json`; this hook focuses on Bash.

Note: a model can write a script to disk and run it; this hook is a
high-value guardrail, NOT a complete security boundary.

Deny contract: hookSpecificOutput.permissionDecision = "deny".
"""
from __future__ import annotations

import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import hooks_enabled, read_event  # noqa: E402

# Domain-agnostic credential/secret path protection. Study-specific data
# directories are intentionally NOT hardcoded here — projects add their own via
# `.claude/settings.json` permissions.deny.
CREDENTIAL_PATH = (
    r"(^|[\s'\"=])(\.env(?:\.[\w-]+)?|"
    r"[^\s'\";|&]*(credentials|client_secret|service[_-]?account|"
    r"id_rsa|id_ed25519|\.pem|\.p12|\.keystore)[^\s'\";|&]*)"
)

# Each entry: (compiled regex, human reason).
DENY_RULES = [
    # rm with BOTH recursive and force flags targeting an absolute path,
    # home, or glob. Relative paths (e.g. build/) are intentionally allowed.
    (re.compile(r"\brm\s+-\w*[rf]\w*[rf]\w*\b[^|;&\n]*\s+(/[^\s]*|~|\*|\$HOME)(\s|$)"),
     "Recursive force-delete of an absolute/home/glob path"),
    (re.compile(r"\bgit\s+push\b.*--force(?!-with-lease)"), "Non-lease force push"),
    (re.compile(r"\bgit\s+push\b.*\b(main|master|release)\b.*--force"), "Force push to a protected branch"),
    (re.compile(r"\b(DROP|TRUNCATE)\s+TABLE\b", re.IGNORECASE), "Destructive SQL DDL"),
    (re.compile(r"\bDELETE\s+FROM\b(?!.*\bWHERE\b)", re.IGNORECASE), "Unbounded SQL DELETE (no WHERE)"),
    (re.compile(r"\b(mkfs|dd)\b.*\bof=/dev/"), "Raw device write / format"),
    (re.compile(r":\(\)\s*\{\s*:\|:&\s*\}\s*;:"), "Fork bomb"),
    (re.compile(r"\bcurl\b.*\|\s*(sudo\s+)?(bash|sh)\b"), "Piping remote script straight into a shell"),
    (re.compile(r"\bwget\b.*\|\s*(sudo\s+)?(bash|sh)\b"), "Piping remote script straight into a shell"),
    (re.compile(r"\bchmod\s+(-R\s+)?777\b"), "World-writable (777) chmod"),
    (re.compile(r"\bgh\s+repo\s+delete\b"), "GitHub repo deletion"),
    (re.compile(r"\bgit\s+add\s+(\.|-A|--all)(\s|$)"), "Broad staging; stage files by name"),
    (re.compile(rf"\b(cat|head|tail|less|more|sed|awk|grep|rg)\b[^|;&\n]*{CREDENTIAL_PATH}", re.IGNORECASE),
     "Direct shell display/search of credentials or environment files"),
    (re.compile(rf"\b(cp|scp|rsync|tar|zip|7z|gzip|xz|base64)\b[^|;&\n]*{CREDENTIAL_PATH}", re.IGNORECASE),
     "Copy/archive/encode command touches credentials or environment files"),
    (re.compile(rf"\b(python3?|Rscript|R\s+-e|node|ruby|perl)\b[^|;&\n]*{CREDENTIAL_PATH}", re.IGNORECASE),
     "Interpreter command touches credentials or environment files"),
]

# Raw MCP roster listings can echo plaintext tokens embedded in stdio server
# args. Deny the raw form; the redacted roster path is allowed.
RAW_MCP_ROSTER = re.compile(r"\b(codex|claude)\s+mcp\s+list\b")


def extract_command(event: dict) -> str:
    candidates: list[str] = []

    def add(value: object) -> None:
        if isinstance(value, str) and value.strip():
            candidates.append(value)

    for key in ("command", "cmd"):
        add(event.get(key))

    for key in ("tool_input", "input", "params"):
        value = event.get(key)
        if isinstance(value, str):
            add(value)
        elif isinstance(value, dict):
            for nested_key in ("command", "cmd"):
                add(value.get(nested_key))

    return "\n".join(candidates)


def deny(reason: str) -> None:
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def main() -> None:
    if not hooks_enabled():
        sys.exit(0)  # project master switch: allow without policy check
    event = read_event()
    command = extract_command(event)

    if RAW_MCP_ROSTER.search(command) and "roster" not in command:
        deny(
            "Blocked by sci-audit policy: raw `mcp list` can expose plaintext "
            "tokens embedded in stdio server args. Use a redacting roster "
            "wrapper (see governance/mcp-roster.md) instead."
        )

    for rule, reason in DENY_RULES:
        if rule.search(command):
            deny(
                f"Blocked by sci-audit policy: {reason}. "
                "Credentials and secrets must never be displayed, copied, or "
                "piped into the context."
            )
    sys.exit(0)  # allow (exit 0, no output)


if __name__ == "__main__":
    main()
