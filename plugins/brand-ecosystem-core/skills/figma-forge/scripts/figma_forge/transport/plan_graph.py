"""figma-forge plan dependency layering — v1.6.0-alpha.2.

Computes a topological layering of an MCP plan's steps for
plan-aware concurrent execution. Steps within a layer have no
inter-dependencies and may be dispatched in parallel; layers are
ordered so that every step's dependencies complete before it starts.

Dependency model
-----------------

The dependency edges mirror the validator's ordering heuristic
(``transport.plan_validation``). Three entity classes, each with a
producer operation and one or more consumer operations:

- **Collection** — produced by ``create_variable_collection``
  (identified by ``collection_id``); consumed by ``create_variable``,
  ``update_variable``, ``create_alias_reference`` (via
  ``collection_id``).
- **Page** — produced by ``create_page`` (identified by ``name``);
  consumed by ``create_component``, ``create_component_set``,
  ``import_svg_as_component`` (via ``page_name``).
- **Component** — produced by ``create_component`` /
  ``create_component_set`` (identified by ``name``); consumed by
  ``place_instance`` (via ``parent_name``).

A step that both consumes one entity and produces another (e.g.
``create_component`` consumes a page and produces a component)
creates transitive chains: ``create_page`` → ``create_component``
→ ``place_instance`` land in three successive layers.

Layering algorithm
-------------------

A Kahn-style longest-path layering:

1. Build a producer map: ``entity_key → first step number that
   produces it``.
2. For each step, compute its dependency set: the producer step of
   every entity it references (skipping references with no in-plan
   producer — those are satisfied by prior state or by hand, and
   impose no ordering constraint here).
3. Assign each step to ``layer = 1 + max(layer of its deps)``, or
   layer 0 if it has no in-plan deps. Steps are processed in
   dependency order; a step waits until all its dependencies have a
   layer.
4. **Cycle tolerance**: if a cycle (which a well-formed plan never
   contains) leaves steps unassignable, the remaining steps are
   appended as singleton layers in plan order — degrading
   gracefully to sequential rather than raising.

The result preserves plan order within each layer (steps are listed
by ascending step number), so a concurrent runner produces
deterministic, plan-ordered results regardless of completion order.
"""

from __future__ import annotations

import json
from typing import Any

# Mirror the validator's dependency-defining operation sets. Kept in
# sync with transport.plan_validation; duplicated here rather than
# imported to keep this module's dependency surface minimal and to
# let the two evolve independently if their needs diverge.
_PRODUCES_COLLECTION = "create_variable_collection"
_PRODUCES_PAGE = "create_page"
_PRODUCES_COMPONENT = ("create_component", "create_component_set")

_NEEDS_COLLECTION = ("create_variable", "update_variable",
                     "create_alias_reference")
_NEEDS_PARENT_COMPONENT = ("place_instance",)
_NEEDS_PAGE = ("create_component", "create_component_set",
               "import_svg_as_component")


def _entity_keys_produced(op: str, args: dict) -> list[tuple[str, str]]:
    """Entity keys a step produces, as (class, identifier) tuples."""
    produced: list[tuple[str, str]] = []
    if op == _PRODUCES_COLLECTION:
        cid = args.get("collection_id")
        if cid:
            produced.append(("collection", str(cid)))
    elif op == _PRODUCES_PAGE:
        name = args.get("name")
        if name:
            produced.append(("page", str(name)))
    if op in _PRODUCES_COMPONENT:
        name = args.get("name")
        if name:
            produced.append(("component", str(name)))
    return produced


def _entity_keys_referenced(op: str, args: dict) -> list[tuple[str, str]]:
    """Entity keys a step references, as (class, identifier) tuples."""
    refs: list[tuple[str, str]] = []
    if op in _NEEDS_COLLECTION:
        cid = args.get("collection_id")
        if cid:
            refs.append(("collection", str(cid)))
    if op in _NEEDS_PARENT_COMPONENT:
        parent = args.get("parent_name")
        if parent:
            refs.append(("component", str(parent)))
    if op in _NEEDS_PAGE:
        page = args.get("page_name")
        if page:
            refs.append(("page", str(page)))
    return refs


def plan_execution_layers(plan: str | dict[str, Any]) -> list[list[int]]:
    """Return a topological layering of the plan's steps.

    Each inner list contains the (1-indexed) step numbers of steps
    that may be dispatched in parallel; the outer list is ordered so
    that every layer's dependencies complete in an earlier layer.
    Step numbers within a layer are sorted ascending (plan order).

    A plan with no dependencies collapses to a single layer
    containing every step. A fully-chained plan (each step depends
    on the previous) expands to one step per layer. Most real plans
    fall between: a few wide layers (many independent collections /
    pages) followed by narrower dependent layers.

    Parameters
    ----------
    plan:
        The MCP plan envelope as a JSON string or pre-parsed dict.

    Returns
    -------
    list[list[int]]:
        Topological layers of step numbers. Empty list for a plan
        with no steps.
    """
    if isinstance(plan, str):
        plan_obj = json.loads(plan)
    else:
        plan_obj = plan
    if not isinstance(plan_obj, dict):
        return []
    steps = plan_obj.get("steps", [])
    if not isinstance(steps, list) or not steps:
        return []

    # Normalize step records: (step_num, op, args)
    records: list[tuple[int, str, dict]] = []
    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            continue
        op = step.get("operation", "")
        args = step.get("arguments", {}) if isinstance(
            step.get("arguments"), dict
        ) else {}
        step_num = step.get("step") if isinstance(step.get("step"), int) else idx
        records.append((step_num, op, args))

    # Producer map: entity key → first step that produces it.
    producer: dict[tuple[str, str], int] = {}
    for step_num, op, args in records:
        for key in _entity_keys_produced(op, args):
            producer.setdefault(key, step_num)

    # Dependency set for each step: producer steps of referenced
    # entities (excluding self-references and entities with no
    # in-plan producer).
    deps: dict[int, set[int]] = {}
    for step_num, op, args in records:
        d: set[int] = set()
        for key in _entity_keys_referenced(op, args):
            p = producer.get(key)
            if p is not None and p != step_num:
                d.add(p)
        deps[step_num] = d

    # Longest-path layering. Iterate until all steps assigned; detect
    # stalls (cycles) and degrade gracefully.
    layer_of: dict[int, int] = {}
    all_steps = [r[0] for r in records]
    remaining = set(all_steps)
    while remaining:
        progressed = False
        for step_num in sorted(remaining):
            step_deps = deps[step_num]
            if all(d in layer_of for d in step_deps):
                layer_of[step_num] = (
                    1 + max(layer_of[d] for d in step_deps)
                    if step_deps else 0
                )
                remaining.discard(step_num)
                progressed = True
        if not progressed:
            # Cycle (well-formed plans never hit this). Degrade: assign
            # each remaining step its own successive layer in plan order.
            base = (max(layer_of.values()) + 1) if layer_of else 0
            for offset, step_num in enumerate(sorted(remaining)):
                layer_of[step_num] = base + offset
            remaining.clear()

    # Group step numbers by layer, preserving plan order within each.
    max_layer = max(layer_of.values()) if layer_of else -1
    layers: list[list[int]] = [[] for _ in range(max_layer + 1)]
    for step_num in sorted(all_steps):
        layers[layer_of[step_num]].append(step_num)
    # Drop any empty layers (shouldn't occur, but defensive).
    return [layer for layer in layers if layer]


__all__ = ["plan_execution_layers"]
