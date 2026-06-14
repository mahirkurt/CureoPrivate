"""
Naming convention validators — strategy pattern for G8 and G9.

Each convention exposes the same three-method interface:
  * validate_component(name)              — component / component-set name
  * validate_variant_property_key(key)    — variant axis name (e.g. "size")
  * validate_variant_property_value(val)  — value within an axis (e.g. "md")

Each method returns a ``ValidationResult`` with ``ok`` boolean and an
optional reason string suitable for embedding in a finding message.

Conventions supported:
  * **Carbon** — PascalCase component names, optionally hierarchical via
    " / " separators (``Components / Actions / Button``). Variant keys
    camelCase; variant values lowercase short tokens or kebab-case.
  * **Material** — Same as Carbon but allows verb-prefix names
    (``ButtonOutlined``, ``FabExtended``).
  * **BEM** — ``block``, ``block__element``, ``block__element--modifier``;
    lowercase + underscores + double-dashes.
  * **Custom** — All names pass. Used when the registry declares a
    bespoke convention; G8/G9 effectively become observation-only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of a single naming check."""
    ok: bool
    reason: str = ""

    @classmethod
    def pass_(cls) -> "ValidationResult":
        """Construct a passing result."""
        return cls(ok=True)

    @classmethod
    def fail(cls, reason: str) -> "ValidationResult":
        """Construct a failing result with ``reason`` describing the violation."""
        return cls(ok=False, reason=reason)


class NamingValidator(Protocol):
    """Strategy interface — implement per naming convention."""

    @property
    def convention_name(self) -> str:
        """Human-readable convention identifier (e.g. "carbon")."""
        ...
    def validate_component(self, name: str) -> ValidationResult:
        """Validate a component or component-set name."""
        ...
    def validate_variant_property_key(self, key: str) -> ValidationResult:
        """Validate a variant axis key."""
        ...
    def validate_variant_property_value(self, value: str) -> ValidationResult:
        """Validate a variant axis value."""
        ...


# ----------------------------------------------------------------------------
# Carbon — PascalCase, hierarchical via " / "
# ----------------------------------------------------------------------------

_CARBON_SEG_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
_CAMEL_KEY_RE = re.compile(r"^[a-z][a-zA-Z0-9]*$")
_LOWERCASE_VALUE_RE = re.compile(r"^[a-z][a-z0-9-]*$")


class CarbonNamingValidator:
    """IBM Carbon convention: PascalCase segments separated by ``/``, camelCase variant keys, lowercase-short values."""
    convention_name = "carbon"

    def validate_component(self, name: str) -> ValidationResult:
        """Validate a component or component-set name against this convention."""
        if not name:
            return ValidationResult.fail("empty name")
        segments = [s.strip() for s in name.split("/")]
        for seg in segments:
            if not _CARBON_SEG_RE.match(seg):
                return ValidationResult.fail(
                    f"segment {seg!r} not PascalCase (expected ^[A-Z][a-zA-Z0-9]*$)"
                )
        return ValidationResult.pass_()

    def validate_variant_property_key(self, key: str) -> ValidationResult:
        """Validate a variant property key (axis name)."""
        if not _CAMEL_KEY_RE.match(key):
            return ValidationResult.fail(
                f"property key {key!r} not camelCase"
            )
        return ValidationResult.pass_()

    def validate_variant_property_value(self, value: str) -> ValidationResult:
        """Validate a variant property value (an enumerated option)."""
        if not _LOWERCASE_VALUE_RE.match(value):
            return ValidationResult.fail(
                f"variant value {value!r} not lowercase short (expected ^[a-z][a-z0-9-]*$)"
            )
        return ValidationResult.pass_()


# ----------------------------------------------------------------------------
# Material 3 — PascalCase, optional verb suffix (Outlined, Filled, Elevated)
# ----------------------------------------------------------------------------

_MATERIAL_SUFFIX_HINTS = ("Outlined", "Filled", "Elevated", "Tonal", "Extended")
_MATERIAL_SEG_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")


class MaterialNamingValidator:
    """Material 3 convention: PascalCase + optional verb-suffix hints (Outlined/Filled/Elevated)."""
    convention_name = "material"

    def validate_component(self, name: str) -> ValidationResult:
        """Validate a component or component-set name against this convention."""
        if not name:
            return ValidationResult.fail("empty name")
        # Material allows " / " hierarchical grouping like Carbon
        segments = [s.strip() for s in name.split("/")]
        for seg in segments:
            if not _MATERIAL_SEG_RE.match(seg):
                return ValidationResult.fail(
                    f"segment {seg!r} not PascalCase"
                )
        return ValidationResult.pass_()

    def validate_variant_property_key(self, key: str) -> ValidationResult:
        """Validate a variant property key (axis name)."""
        if not _CAMEL_KEY_RE.match(key):
            return ValidationResult.fail(f"property key {key!r} not camelCase")
        return ValidationResult.pass_()

    def validate_variant_property_value(self, value: str) -> ValidationResult:
        """Validate a variant property value (an enumerated option)."""
        if not _LOWERCASE_VALUE_RE.match(value):
            return ValidationResult.fail(
                f"variant value {value!r} not lowercase short"
            )
        return ValidationResult.pass_()


# ----------------------------------------------------------------------------
# BEM — block, block__element, block__element--modifier
# ----------------------------------------------------------------------------

_BEM_BLOCK_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_BEM_FULL_RE = re.compile(
    r"^[a-z][a-z0-9-]*"             # block
    r"(?:__[a-z][a-z0-9-]*)?"        # optional element
    r"(?:--[a-z][a-z0-9-]*)?$"       # optional modifier
)


class BEMNamingValidator:
    """BEM convention: ``block`` / ``block__element`` / ``block__element--modifier`` patterns."""
    convention_name = "bem"

    def validate_component(self, name: str) -> ValidationResult:
        """Validate a component or component-set name against this convention."""
        if not name:
            return ValidationResult.fail("empty name")
        # BEM allows hierarchical via " / " or just by being one block
        segments = [s.strip() for s in name.split("/")]
        for seg in segments:
            if not _BEM_FULL_RE.match(seg):
                return ValidationResult.fail(
                    f"segment {seg!r} not BEM "
                    f"(expected block | block__element | block__element--modifier)"
                )
        return ValidationResult.pass_()

    def validate_variant_property_key(self, key: str) -> ValidationResult:
        """Validate a variant property key (axis name)."""
        if not _BEM_BLOCK_RE.match(key):
            return ValidationResult.fail(
                f"property key {key!r} not BEM lowercase-kebab"
            )
        return ValidationResult.pass_()

    def validate_variant_property_value(self, value: str) -> ValidationResult:
        """Validate a variant property value (an enumerated option)."""
        if not _BEM_BLOCK_RE.match(value):
            return ValidationResult.fail(
                f"variant value {value!r} not BEM lowercase-kebab"
            )
        return ValidationResult.pass_()


# ----------------------------------------------------------------------------
# Custom — pass-everything fallback
# ----------------------------------------------------------------------------

class CustomNamingValidator:
    """No-op validator — when the registry declares ``custom``, naming gates
    pass every input. Used when the operator deliberately opts out of
    automated naming checks.
    """
    convention_name = "custom"

    def validate_component(self, name: str) -> ValidationResult:
        """Validate a component or component-set name against this convention."""
        return ValidationResult.pass_() if name else ValidationResult.fail("empty name")

    def validate_variant_property_key(self, key: str) -> ValidationResult:
        """Validate a variant property key (axis name)."""
        return ValidationResult.pass_() if key else ValidationResult.fail("empty key")

    def validate_variant_property_value(self, value: str) -> ValidationResult:
        """Validate a variant property value (an enumerated option)."""
        return ValidationResult.pass_() if value else ValidationResult.fail("empty value")


# ----------------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------------

_VALIDATORS: dict[str, type[NamingValidator]] = {
    "carbon":   CarbonNamingValidator,
    "material": MaterialNamingValidator,
    "bem":      BEMNamingValidator,
    "custom":   CustomNamingValidator,
}


def get_validator(convention: str) -> NamingValidator:
    """Return a validator instance for the named convention.

    Falls back to ``CustomNamingValidator`` (which passes everything) when
    the convention isn't recognized, with the assumption that the audit
    will surface this as a finding via a separate check.
    """
    cls = _VALIDATORS.get(convention.lower(), CustomNamingValidator)
    return cls()
