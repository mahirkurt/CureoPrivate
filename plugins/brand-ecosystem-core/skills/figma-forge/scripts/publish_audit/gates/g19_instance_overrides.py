"""Gate 19 — Component instances in publishable pages must have clean
overrides — text and instance-swap overrides allowed, paint/typography
overrides flagged.

A "detached override" is when an INSTANCE node has been modified beyond
the safe overrides (text content, child-instance-swap). Typical bad cases:
  * a Button instance with its fill color hand-overridden to a hex that
    doesn't match any variant's color — implies a missing variant
  * a Card instance with overridden corner radius — implies an off-spec
    usage that should either become a new variant or be reverted

Detection strategy: every INSTANCE has an ``overrides`` field listing
``{id, overriddenFields}``. For each entry, we check whether the
overridden field is in the safe-list. Anything else is reported.
"""

from __future__ import annotations

from ..context import MultiFileFigmaContext
from ..models import GateResult, walk_nodes
from ..gates_registry import get_gate, register_gate


# Field names that are safe to override at instance-use site
SAFE_OVERRIDE_FIELDS = {
    "characters",        # text content
    "componentProperties",  # variant property selection
    "visible",           # show/hide
    "name",              # rename
    # Instance swap properties are exposed via componentProperties; bare
    # ``mainComponent`` overrides on child instances are also allowed.
    "mainComponent",
}


SKIP_PAGES = {"Candidates", "Deprecated", "Playground"}


def _bad_override_fields(overrides: list) -> list[str]:
    """Return the sorted unique list of override fields outside the safe allowlist."""
    bad: list[str] = []
    for override in overrides:
        for f_name in override.get("overriddenFields") or []:
            if f_name not in SAFE_OVERRIDE_FIELDS:
                bad.append(f_name)
    return sorted(set(bad))


def _is_audited_instance(node: dict, page: str) -> bool:
    """True iff ``node`` is an INSTANCE on a page that is not exempt."""
    return node.get("type") == "INSTANCE" and (page or "") not in SKIP_PAGES


@register_gate(19)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Detect instance overrides that touch fields outside the safe-override allowlist."""
    res = GateResult(gate=get_gate(19))
    for role, f in ctx.iter_publishable_files():
        for node, page in walk_nodes(f.document):
            if not _is_audited_instance(node, page):
                continue
            overrides = node.get("overrides") or []
            if not overrides:
                continue
            res.checked_count += 1
            unique_fields = _bad_override_fields(overrides)
            if unique_fields:
                res.add(
                    f"[{role}] {page} → instance {node.get('name', '<unnamed>')!r}: "
                    f"detached override on fields {unique_fields}",
                    role=role
                )
    res.mark_fail()
    return res
