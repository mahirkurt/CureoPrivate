#!/usr/bin/env python3
"""SessionStart hook (Layer 0: grounding + convention injection).

At every session start/resume/compact, injects the scientific-integrity and
Turkish-writing conventions into developer context so that source-grounding
discipline, no-fabrication, and the Turkish orthography rules are active from
the first turn.

Output contract: hookSpecificOutput.additionalContext.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import hooks_enabled, read_event  # noqa: E402

FALLBACK = (
    "sci-audit conventions: cite a verifiable source for every factual or "
    "numeric claim; prefer primary/official sources; never fabricate data, "
    "DOIs, PMIDs, or statistics; preserve version/date qualifiers; treat web "
    "and model-recalled facts as untrusted until checked. When the text is "
    "Turkish, the Turkish scientific-writing axis (decimal comma, APA-TR "
    "p-value form, academic register, first-use abbreviation expansion) is in "
    "force. A source-verification tool that errors yields an 'unverified' "
    "label, never a fabricated confirmation."
)


def main() -> None:
    if not hooks_enabled():
        sys.exit(0)  # project master switch: inject nothing
    _ = read_event()  # source = startup|resume|compact (not used yet)
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    conventions_path = os.path.join(
        root, "skills", "sci-audit-orchestrator", "references", "conventions.md"
    )
    context = FALLBACK
    if conventions_path and os.path.exists(conventions_path):
        try:
            with open(conventions_path, "r", encoding="utf-8") as fh:
                loaded = fh.read().strip()
                if loaded:
                    context = loaded
        except Exception:
            pass

    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
