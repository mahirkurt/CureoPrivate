"""Shared helpers for sci-audit Claude Code hooks.

Claude Code passes one JSON object on stdin to every command hook. Common
fields: session_id, transcript_path, cwd, hook_event_name. Event-specific
fields: tool_name/tool_input/tool_response (PreToolUse/PostToolUse),
prompt (UserPromptSubmit), stop_hook_active (Stop).

Blocking conventions:
  - exit(2) + message on stderr  -> universal "block / feedback" signal
  - JSON on stdout               -> richer, event-specific decisions
    (hookSpecificOutput.permissionDecision, decision/reason, additionalContext)

This module is domain-agnostic: it carries no project-specific paths, names,
or whitelists. All configurable behaviour is read from
`.claude/sci-audit.local.md` (YAML frontmatter) at the project root, with safe
defaults when that file is absent.
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

# High-precision secret patterns (low false-positive). Shared by the
# UserPromptSubmit gate and the PostToolUse output review.
SECRET_PATTERNS: List[Tuple[str, str]] = [
    (r"sk-(?:proj|svcacct)-[A-Za-z0-9_\-]{20,}", "OpenAI project/service account key"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style secret key"),
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic API key"),
    (r"xai-[A-Za-z0-9]{20,}", "xAI (Grok) API key"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}", "GitHub token"),
    (r"github_pat_[A-Za-z0-9_]{40,}", "GitHub fine-grained personal access token"),
    (r"AIza[0-9A-Za-z_\-]{35}", "Google API key"),
    (r"sbp_[A-Za-z0-9]{40,}", "Supabase access token"),
    (r"(?:sk|rk)_live_[A-Za-z0-9]{20,}", "Stripe live key"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private key block"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}", "JWT"),
]


def read_event() -> Dict[str, Any]:
    """Parse the single JSON object Claude Code writes to stdin. Fail-open."""
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Never hard-crash a hook on malformed input: that would block the
        # loop for the wrong reason. Emit nothing and let the session continue.
        return {}


def project_dir() -> str:
    """Best-effort project root. Claude Code exports CLAUDE_PROJECT_DIR."""
    return os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def emit_json(obj: Dict[str, Any]) -> None:
    """Write a JSON decision to stdout and exit 0."""
    sys.stdout.write(json.dumps(obj))
    sys.exit(0)


def block(reason: str) -> None:
    """Universal block: exit code 2 with reason on stderr."""
    sys.stderr.write(reason)
    sys.exit(2)


def allow() -> None:
    sys.exit(0)


# --- Local config (.claude/sci-audit.local.md) -----------------------------

def _parse_frontmatter(text: str) -> Dict[str, Any]:
    """Parse a minimal YAML frontmatter block into a dict.

    Supports flat `key: value` pairs and `key:` followed by `- item` lists.
    Intentionally dependency-free (no PyYAML): the config surface is small and
    stdlib-only is a hard constraint. Unknown structure degrades to {}.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[3:end].strip("\n")
    result: Dict[str, Any] = {}
    current_key: str | None = None
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        list_match = re.match(r"^\s*-\s+(.*)$", line)
        if list_match and current_key is not None:
            val = list_match.group(1).strip().strip('"').strip("'")
            result.setdefault(current_key, [])
            if isinstance(result[current_key], list):
                result[current_key].append(val)
            continue
        kv = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if val == "":
                current_key = key
                result[key] = []
            else:
                current_key = None
                result[key] = val.strip('"').strip("'")
    return result


def load_local_config() -> Dict[str, Any]:
    """Read `.claude/sci-audit.local.md` frontmatter. Missing file -> {}."""
    path = os.path.join(project_dir(), ".claude", "sci-audit.local.md")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return _parse_frontmatter(fh.read())
    except Exception:
        return {}
