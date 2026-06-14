"""
VariantMatrixAnalyzer — parse Figma component-set variants and analyse
whether the variant Cartesian product is fully populated.

Figma's variant model:
  * A ComponentSet groups Components that share variant *axes*.
  * Each child Component's ``name`` encodes its variant values via a
    comma-separated key=value notation, e.g.:
        "Type=Primary, Size=Medium, State=Default"
  * Axes are inferred from the union of keys across the set's children.
  * The Cartesian product of all axes' values is the expected matrix;
    any axis combination missing from the children is a "gap".

This module:
  1. Parses Figma's variant-name notation into structured axes.
  2. Computes the expected Cartesian product.
  3. Identifies missing combinations (gaps) and optionally
     intentionally-disabled combinations (via a ``disabledVariants``
     extension or description marker).
  4. Surfaces 64-variant warnings and 256-variant blockers — Figma's
     practical and hard limits respectively.

The analyzer is consumed by both G7 (matrix completeness) and G9
(property-naming validation).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from itertools import product
from typing import Iterable


# Figma variant name format: "Key=Value, Key=Value, ..."
# Each key/value separated by ',' with optional whitespace; key/value
# separated by '='. Spaces inside values are allowed but uncommon.
VARIANT_PAIR_RE = re.compile(r"\s*([^=,]+?)\s*=\s*([^,]+?)\s*(?:,|$)")


# Figma's documented practical limits
SOFT_VARIANT_WARN_THRESHOLD = 64    # editor performance starts to degrade
HARD_VARIANT_FAIL_THRESHOLD = 256   # publish-likely-to-fail ceiling


@dataclass
class VariantMatrix:
    """Structured representation of one ComponentSet's variant geometry."""
    component_set_name: str
    axes: dict[str, list[str]]                       # axis_name → ordered unique values
    actual_variants: set[tuple[str, ...]]            # tuples ordered by sorted axes
    explicitly_disabled: set[tuple[str, ...]] = field(default_factory=set)
    parse_errors: list[str] = field(default_factory=list)

    @property
    def axis_names(self) -> list[str]:
        """Axes in their canonical (sorted) order — drives tuple key ordering."""
        return sorted(self.axes.keys())

    @property
    def expected_combinations(self) -> set[tuple[str, ...]]:
        """The full Cartesian product across all axes."""
        if not self.axes:
            return set()
        keys = self.axis_names
        return {tuple(combo) for combo in product(*(self.axes[k] for k in keys))}

    @property
    def expected_count(self) -> int:
        """Size of the full Cartesian product."""
        if not self.axes:
            return 0
        count = 1
        for values in self.axes.values():
            count *= len(values)
        return count

    @property
    def missing(self) -> set[tuple[str, ...]]:
        """Combinations in the Cartesian product without a matching component,
        excluding those explicitly disabled."""
        return self.expected_combinations - self.actual_variants - self.explicitly_disabled

    @property
    def coverage_ratio(self) -> float:
        """Fraction of expected combinations that have a component (0.0–1.0)."""
        if self.expected_count == 0:
            return 1.0
        covered = self.expected_count - len(self.missing)
        return covered / self.expected_count

    @property
    def is_complete(self) -> bool:
        return not self.missing

    @property
    def exceeds_soft_threshold(self) -> bool:
        return self.expected_count >= SOFT_VARIANT_WARN_THRESHOLD

    @property
    def exceeds_hard_threshold(self) -> bool:
        return self.expected_count >= HARD_VARIANT_FAIL_THRESHOLD


# ----------------------------------------------------------------------------
# Parsing
# ----------------------------------------------------------------------------

def parse_variant_name(component_name: str) -> dict[str, str] | None:
    """Parse a Figma variant component name into ``{axis_key → value}``.

    Returns None when the name doesn't look like a variant-encoded name
    (e.g. has no '=' character). Empty values and malformed pairs are
    silently skipped — callers can detect this by comparing key counts.
    """
    if "=" not in component_name:
        return None
    pairs = {}
    for m in VARIANT_PAIR_RE.finditer(component_name):
        key = m.group(1).strip()
        value = m.group(2).strip()
        if key and value:
            pairs[key] = value
    return pairs if pairs else None


# ----------------------------------------------------------------------------
# Analysis — called from G7
# ----------------------------------------------------------------------------

def analyze_component_set(component_set_id: str, set_meta: dict,
                            children_components: Iterable[dict]) -> VariantMatrix:
    """Inspect a ComponentSet + its children, returning a VariantMatrix.

    Arguments:
        component_set_id    — the set's node-id (used only for error reporting)
        set_meta            — the metadata dict from ``file.componentSets[id]``;
                              we read its ``name`` and ``description``
        children_components — iterable of child component metadata dicts
                              from ``file.components.values()`` filtered by
                              ``componentSetId == component_set_id``
    """
    set_name = set_meta.get("name", component_set_id)
    parsed_children: list[dict[str, str]] = []
    parse_errors: list[str] = []

    for child in children_components:
        name = child.get("name", "")
        pairs = parse_variant_name(name)
        if pairs is None:
            parse_errors.append(f"child {name!r} has no variant-encoded name; skipped")
            continue
        parsed_children.append(pairs)

    # Build axes from union of keys
    axes: dict[str, list[str]] = {}
    for pairs in parsed_children:
        for key, value in pairs.items():
            if key not in axes:
                axes[key] = []
            if value not in axes[key]:
                axes[key].append(value)
    # Sort values within each axis for deterministic Cartesian product
    for key in axes:
        axes[key] = sorted(axes[key])

    # Build actual_variants tuples in canonical key order
    canonical_keys = sorted(axes.keys())
    actual: set[tuple[str, ...]] = set()
    for pairs in parsed_children:
        # Skip children that don't declare all axes (treat as malformed,
        # they don't contribute to coverage of any specific tuple).
        if not all(k in pairs for k in canonical_keys):
            missing_keys = [k for k in canonical_keys if k not in pairs]
            parse_errors.append(
                f"child with axes {sorted(pairs.keys())!r} missing keys "
                f"{missing_keys!r}; not counted toward coverage"
            )
            continue
        tup = tuple(pairs[k] for k in canonical_keys)
        actual.add(tup)

    # Parse explicit disable list from set description (optional)
    explicitly_disabled = _parse_disabled_variants(set_meta.get("description", ""),
                                                     canonical_keys)

    return VariantMatrix(
        component_set_name=set_name,
        axes=axes,
        actual_variants=actual,
        explicitly_disabled=explicitly_disabled,
        parse_errors=parse_errors,
    )


def _parse_disabled_variants(description: str,
                              canonical_keys: list[str]) -> set[tuple[str, ...]]:
    """Look for a ``Disabled:`` block in the component-set description and
    parse comma-separated variant-tuples to exclude from coverage checks.

    Format (intentionally permissive):
        Disabled:
        - Type=Primary, Size=Large, State=Disabled
        - Type=Danger, Size=Small, State=Hover

    Lines not matching variant-pair syntax are silently ignored.
    """
    if "Disabled:" not in description:
        return set()
    disabled: set[tuple[str, ...]] = set()
    after_marker = description.split("Disabled:", 1)[1]
    for line in after_marker.splitlines():
        line = line.strip().lstrip("-").strip()
        if not line or "=" not in line:
            continue
        pairs = parse_variant_name(line)
        if not pairs:
            continue
        if not all(k in pairs for k in canonical_keys):
            continue
        disabled.add(tuple(pairs[k] for k in canonical_keys))
    return disabled
