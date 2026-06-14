"""Gate 18 — The cover page must declare DS version, license, and contact.

Without this metadata block, consumers can't tell:
  * which version of the DS they're consuming (debugging upgrade issues),
  * whether they're licensed to use it (especially for external libraries),
  * who to ping when something breaks.

Depends on G10 — a missing cover page means G18 is automatically skipped.
The cover's text content is concatenated and scanned for three signals:
  1. Version string — typically ``v1.0.0`` or ``Version: 1.2.3``
  2. License declaration — ``License:`` / ``Internal use only`` / ``MIT``
  3. Contact — email-like pattern, Slack handle, or ``Contact:`` keyword
"""

from __future__ import annotations

import re

from ..context import FigmaFile, MultiFileFigmaContext
from ..models import GateResult, collect_text_content, find_page
from ..gates_registry import get_gate, register_gate


VERSION_RE = re.compile(r"\b(?:v|version[:\s]+)\d+\.\d+(?:\.\d+)?\b", re.IGNORECASE)
LICENSE_KEYWORDS = ("license", "lisans", "internal use", "all rights reserved",
                    "mit", "apache", "bsd", "proprietary")
CONTACT_RE = re.compile(
    r"(?:contact[:\s]+|@[\w.-]+|\b[\w.-]+@[\w.-]+\.\w+\b|#[\w-]+)",
    re.IGNORECASE
)


def _check_cover(f: FigmaFile) -> tuple[bool, bool, bool]:
    """Inspect the file's cover page; return (has_version, has_license, has_contact)."""
    for candidate_name in ("Cover", "Overview", "Welcome"):
        page = find_page(f.document, candidate_name)
        if page is not None:
            break
    else:
        return False, False, False
    text = collect_text_content(page)
    text_lower = text.lower()
    return (
        bool(VERSION_RE.search(text)),
        any(kw in text_lower for kw in LICENSE_KEYWORDS),
        bool(CONTACT_RE.search(text))
    )


def _foundations_target(ctx: MultiFileFigmaContext) -> tuple[str, FigmaFile] | None:
    """Return the FigmaFile playing the Foundations role, or None in single-file mode."""
    if ctx.registry is not None:
        f = ctx.get("foundations")
        return ("foundations", f) if f is not None else None
    primary = ctx.primary
    if "foundation" in (primary.name or "").lower():
        return ("primary", primary)
    return None


@register_gate(18)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Verify the Foundations cover page declares version, license, and contact metadata."""
    res = GateResult(gate=get_gate(18))
    target = _foundations_target(ctx)
    if target is None:
        res.status = "n_a"
        res.notes.append("No foundations file resolvable; G18 skipped.")
        return res
    role, f = target
    has_version, has_license, has_contact = _check_cover(f)
    res.checked_count = 1
    missing = []
    if not has_version:
        missing.append("version string (e.g. 'v1.2.3' or 'Version: 1.2.3')")
    if not has_license:
        missing.append("license declaration")
    if not has_contact:
        missing.append("contact (email / Slack handle / 'Contact:')")
    if missing:
        res.add(
            f"[{role}] cover page missing: " + "; ".join(missing),
            role=role
        )
    res.mark_fail()
    return res
