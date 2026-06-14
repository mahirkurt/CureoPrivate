"""
LibraryRegistry — Canonical record of a multi-file Figma DS library.

A Figma DS library typically spans 4 files (Foundations / Components /
Patterns / Icons). The registry tells the audit which file plays which role,
what naming convention to validate against, and in what order files must be
published.

Loaded from a JSON sidecar file authored by the operator. The schema is
intentionally minimal and forward-compatible — extra fields are preserved
under ``extras`` for future capabilities.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


NamingConvention = Literal["carbon", "material", "bem", "custom"]
KNOWN_CONVENTIONS = ("carbon", "material", "bem", "custom")

# Canonical 4-file library roles. Single-file or 2-file collapsed variants
# remain supported — roles that are absent from a registry file just mean
# the audit will skip role-specific gates for them.
CANONICAL_ROLES = ("foundations", "components", "patterns", "icons")


@dataclass
class FileInfo:
    """Per-file entry in the library registry."""
    file_key: str
    role: str
    expected_pages: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, role: str, data: dict) -> "FileInfo":
        if "figma_file_key" not in data:
            raise ValueError(f"file role {role!r}: missing 'figma_file_key'")
        return cls(
            file_key=data["figma_file_key"],
            role=role,
            expected_pages=list(data.get("expected_pages") or [])
        )


@dataclass
class LibraryRegistry:
    """Operator-authored map of a multi-file Figma DS library."""
    ds_name: str
    ds_version: str
    naming_convention: NamingConvention
    files: dict[str, FileInfo]
    publish_order: list[str]
    extras: dict = field(default_factory=dict)

    # --- Lifecycle ----------------------------------------------------------

    @classmethod
    def from_path(cls, path: str | Path) -> "LibraryRegistry":
        """Load a registry from a JSON sidecar file.

        Raises ``FileNotFoundError`` if path missing, ``ValueError`` if the
        schema is invalid (missing required keys, unknown naming convention).
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"library-registry not found: {p}")
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryRegistry":
        """Construct a registry from a parsed JSON dict. Validates required keys."""
        for required in ("ds_name", "ds_version", "files"):
            if required not in data:
                raise ValueError(f"library-registry: missing required key {required!r}")
        convention = data.get("naming_convention", "custom")
        if convention not in KNOWN_CONVENTIONS:
            raise ValueError(
                f"library-registry: naming_convention {convention!r} not in {KNOWN_CONVENTIONS}"
            )
        files = {
            role: FileInfo.from_dict(role, info)
            for role, info in data["files"].items()
        }
        publish_order = data.get("publish_order") or _default_publish_order(files)
        consumed = {"ds_name", "ds_version", "naming_convention", "files", "publish_order"}
        extras = {k: v for k, v in data.items() if k not in consumed}
        return cls(
            ds_name=data["ds_name"],
            ds_version=data["ds_version"],
            naming_convention=convention,  # type: ignore[arg-type]
            files=files,
            publish_order=publish_order,
            extras=extras
        )

    # --- Lookup -------------------------------------------------------------

    def get_file_key(self, role: str) -> str | None:
        """Return the Figma file_key for ``role`` (case-insensitive), or None."""
        info = self.files.get(role.lower())
        return info.file_key if info else None

    def get_file_info(self, role: str) -> FileInfo | None:
        """Return the FileInfo entry for ``role`` (case-insensitive), or None."""
        return self.files.get(role.lower())

    def has_role(self, role: str) -> bool:
        """Cheaper than ``get_file_key`` when the caller only needs a boolean."""
        return role.lower() in self.files

    @property
    def roles(self) -> list[str]:
        """All declared roles in this registry, lowercase, sorted."""
        return sorted(self.files.keys())

    @property
    def is_multi_file(self) -> bool:
        """True when the registry declares ≥2 files (canonical library shape)."""
        return len(self.files) >= 2


def _default_publish_order(files: dict[str, FileInfo]) -> list[str]:
    """Return the canonical Foundations → Components → Patterns → Icons order
    restricted to the roles actually present in ``files``.
    """
    return [r for r in CANONICAL_ROLES if r in files]


# ----------------------------------------------------------------------------
# Schema reference (operator-facing)
# ----------------------------------------------------------------------------

EXAMPLE_REGISTRY_JSON = """\
{
  "ds_name": "Hemantix",
  "ds_version": "1.0.0",
  "naming_convention": "carbon",
  "files": {
    "foundations": {
      "figma_file_key": "abc123FoundationsKey",
      "expected_pages": ["Cover", "Tokens", "Color", "Typography", "Spacing"]
    },
    "components": {
      "figma_file_key": "def456ComponentsKey",
      "expected_pages": ["Cover", "Actions", "Forms", "Data Display", "Feedback"]
    },
    "patterns": {
      "figma_file_key": "ghi789PatternsKey",
      "expected_pages": ["Cover", "Layouts", "Empty States"]
    },
    "icons": {
      "figma_file_key": "jkl012IconsKey",
      "expected_pages": ["Cover", "16px", "20px", "24px"]
    }
  },
  "publish_order": ["icons", "foundations", "components", "patterns"],
  "channel_used": "Channel 2 (REST)",
  "contact": "design-system@hemantix.example"
}
"""
