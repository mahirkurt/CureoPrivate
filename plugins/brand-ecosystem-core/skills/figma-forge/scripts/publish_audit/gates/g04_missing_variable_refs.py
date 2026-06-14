"""Gate 4 — Every variable alias must resolve to an existing target.

Strategy: scan every variable's per-mode values. When the value is a
``VARIABLE_ALIAS`` discriminator, the ``id`` field must reference a
variable that exists either:
  1. In the same file's ``variables`` map (local alias), or
  2. In a linked library (alias has form like "VariableID:1:7" with a
     ``key`` field pointing to an external library — these are accepted
     under the assumption Figma resolves them at consumer-time).

Dangling local aliases are publish blockers. Their consumers see the
fallback default and silently break theming.
"""

from __future__ import annotations

from typing import Iterator

from ..context import FigmaFile, MultiFileFigmaContext
from ..models import GateResult
from ..gates_registry import get_gate, register_gate


def _iter_alias_values(f: FigmaFile) -> Iterator[tuple[str, str, dict]]:
    """Yield ``(var_id, mode_id, alias_value_dict)`` for every alias-typed mode value."""
    for var_id, var in f.variables.items():
        values_by_mode = var.get("valuesByMode") or {}
        for mode_id, value in values_by_mode.items():
            if isinstance(value, dict) and value.get("type") == "VARIABLE_ALIAS":
                yield var_id, mode_id, value


def _is_local_alias(alias: dict) -> bool:
    """True when the alias targets a variable in the same file (no remote ``key`` field)."""
    return "key" not in alias  # ``key`` denotes a library-resolved external alias


@register_gate(4)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Resolve every local VARIABLE_ALIAS and report aliases whose target is missing."""
    res = GateResult(gate=get_gate(4))
    for role, f in ctx.iter_publishable_files():
        if not f.variables:
            continue
        local_var_ids = set(f.variables.keys())
        for var_id, mode_id, alias in _iter_alias_values(f):
            res.checked_count += 1
            if not _is_local_alias(alias):
                continue  # external library aliases trusted at audit-time
            target = alias.get("id")
            if not target or target not in local_var_ids:
                var_name = f.variables[var_id].get("name", var_id)
                res.add(
                    f"[{role}] {var_name} (mode {mode_id}) → broken alias "
                    f"target {target!r}",
                    role=role
                )
    res.mark_fail()
    return res
