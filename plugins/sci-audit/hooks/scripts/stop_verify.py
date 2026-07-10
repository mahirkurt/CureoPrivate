#!/usr/bin/env python3
"""Stop hook (Layer 0+2: grounding + twin verification gate).

At end of turn, inspects the assistant's last message. Two gates:

  (a) Unsourced quantitative claim: a numeric/quantitative statement with no
      nearby source marker (URL, DOI, PMID, arXiv id, [n], (year), or a repo
      file path) continues the turn and asks for a source.
  (b) Turkish orthography blocker (axis G5): when the message is Turkish (or
      lang: tr in config), an English decimal-dot p-value / decimal-dot stat
      form is a blocker — Turkish scientific prose uses the decimal comma and
      APA-TR p-value form (p<0,001).

Claude Code may not place the last message in the event; it is then read from
the transcript JSONL. Config is read from `.claude/sci-audit.local.md`
frontmatter; safe defaults apply when absent.

Stop contract: {"decision":"block","reason":...} does not reject the turn; it
continues it with the reason. stop_hook_active breaks the loop.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import hooks_enabled, load_local_config, read_event  # noqa: E402

# Domain-agnostic scientific quantitative-claim signal.
NUMERIC_CLAIM = re.compile(
    r"\b\d+(?:[.,]\d+)?\s?%|\b\d{4}\b|\$\s?\d|"
    r"\b(?:n|N)\s?=\s?\d|\b(?:OR|HR|RR|CI|SD|SE|IQR)\b\s?[:=]?\s?\d|"
    r"\b\d+(?:[.,]\d+)?\s?"
    r"(mg|ml|kg|µg|mcg|mmol|nmol|patients|subjects|participants|cases|"
    r"hasta|katilimci|katılımcı|olgu|denek)\b",
    re.IGNORECASE,
)
# Source markers: URL/DOI/PMID/arXiv/[n]/(year) + a traceable repo artefact.
SOURCE_MARKER = re.compile(
    r"https?://|doi\.org|arxiv|\bPMID\b|\bPMCID\b|\[\d+\]|\(20\d\d\)|\(19\d\d\)|"
    r"[\w./~-]+\.(?:md|csv|tsv|py|R|qmd|Rmd|bib|ya?ml|json|toml|pdf|docx|tex)\b|"
    r"`[^`]*[/.][^`]*`",
    re.IGNORECASE,
)
# English decimal-dot p-value in an otherwise-Turkish text (G5 blocker).
TR_PVALUE_DOT = re.compile(r"\bp\s*[<=>]\s*0?\.\d+", re.IGNORECASE)
# Turkish-specific letters, used for lightweight language detection.
TR_CHARS = re.compile(r"[ışğİĞŞçöüÇÖÜ]")


def is_turkish(text: str, config: dict) -> bool:
    lang = (config.get("lang") or "auto").strip().lower()
    if lang == "tr":
        return True
    if lang == "en":
        return False
    # auto: enough Turkish-specific letters relative to length
    hits = len(TR_CHARS.findall(text))
    letters = sum(1 for c in text if c.isalpha())
    return letters > 0 and hits / max(letters, 1) > 0.01 and hits >= 3


def last_assistant_message(event: dict) -> str:
    msg = event.get("last_assistant_message")
    if isinstance(msg, str) and msg.strip():
        return msg
    transcript = event.get("transcript_path") or ""
    if not transcript or not os.path.exists(transcript):
        return ""
    try:
        with open(transcript, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except Exception:
        return ""
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") != "assistant":
            continue
        message = entry.get("message") or {}
        content = message.get("content")
        texts: list[str] = []
        if isinstance(content, str):
            texts.append(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    texts.append(part.get("text") or "")
        joined = "\n".join(t for t in texts if t.strip())
        if joined.strip():
            return joined
    return ""


def main() -> None:
    if not hooks_enabled():
        sys.exit(0)  # project master switch: allow stop without verification
    event = read_event()

    # Loop guard: if we already forced a continue this turn, let it stop.
    if event.get("stop_hook_active"):
        sys.stdout.write(json.dumps({"continue": True}))
        sys.exit(0)

    config = load_local_config()
    gate_unsourced = str(config.get("gate_unsourced_numeric", "true")).lower() != "false"
    gate_tr_pvalue = str(config.get("gate_tr_pvalue_dot", "true")).lower() != "false"

    msg = last_assistant_message(event)
    if not msg.strip():
        sys.stdout.write(json.dumps({"continue": True}))
        sys.exit(0)

    sentences = re.split(r"(?<=[.!?])\s+", msg)

    # Gate (b): Turkish decimal-dot p-value blocker.
    if gate_tr_pvalue and is_turkish(msg, config):
        for sentence in sentences:
            m = TR_PVALUE_DOT.search(sentence)
            if m:
                sys.stdout.write(json.dumps({
                    "decision": "block",
                    "reason": (
                        "sci-audit G5 blocker: Turkish text uses an English "
                        "decimal-dot p-value form — write it with the decimal "
                        f"comma (e.g. p<0,001), not \"{m.group(0)}\"."
                    ),
                }))
                sys.exit(0)

    # Gate (a): unsourced quantitative claim.
    if gate_unsourced:
        unsourced = [
            s for s in sentences
            if NUMERIC_CLAIM.search(s) and not SOURCE_MARKER.search(s)
        ]
        if unsourced:
            preview = unsourced[0][:160]
            sys.stdout.write(json.dumps({
                "decision": "block",
                "reason": (
                    "sci-audit verification gate: the following quantitative "
                    "claim has no source marker — add a primary source, a repo "
                    f"file path, or remove it: \"{preview}\""
                ),
            }))
            sys.exit(0)

    sys.stdout.write(json.dumps({"continue": True}))
    sys.exit(0)


if __name__ == "__main__":
    main()
