"""
Core models for the figma-forge PUBLISH_AUDIT framework.

Defines the data shapes shared by every gate implementation. Kept free of
network I/O — the ``context`` module handles all REST/MCP calls and the
``gates`` modules consume these data classes for their per-gate logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, Literal


Severity = Literal["error", "warn", "info"]
GateStatus = Literal["pass", "fail", "skip", "n_a"]


@dataclass(frozen=True)
class Gate:
    """Static definition of a publish-readiness gate.

    Gates are catalogued in ``gates.GATE_CATALOG`` and consumed by the
    auditor in numeric order. Each gate has a stable integer ID (1..19)
    that survives version bumps; new gates get fresh IDs, never re-use.
    """
    id: int
    name: str
    severity: Severity
    description: str
    remediation: str


@dataclass
class GateResult:
    """Result of running a single gate against the audit target.

    Fields:
        gate          — the static Gate definition
        status        — ``pass`` / ``fail`` / ``skip`` / ``n_a``
        failures      — human-readable lines describing each individual
                        failure (typically ``"<page> → <node name>: reason"``)
        checked_count — how many candidate nodes/styles/components were
                        examined; surfaced in the report for transparency
        notes         — non-failure observations the reviewer should see
                        (e.g. "registry has no Icons role → G14 skipped")
        per_file      — optional map of ``role → list[str]`` for multi-file
                        gates that want to group failures by source file
    """
    gate: Gate
    status: GateStatus = "pass"
    failures: list[str] = field(default_factory=list)
    checked_count: int = 0
    notes: list[str] = field(default_factory=list)
    per_file: dict[str, list[str]] = field(default_factory=dict)

    def mark_fail(self) -> None:
        """Flip status to 'fail' if any failures have accumulated."""
        if self.failures or any(self.per_file.values()):
            self.status = "fail"

    def add(self, message: str, *, role: str | None = None) -> None:
        """Append a failure, optionally tagged with the originating role."""
        self.failures.append(message)
        if role is not None:
            self.per_file.setdefault(role, []).append(message)


# ----------------------------------------------------------------------------
# Walk helpers — these are pure functions over Figma's node-tree shape.
# They operate on the JSON returned by GET /v1/files/:key.
# ----------------------------------------------------------------------------

def walk_nodes(node: dict, parent_page: str | None = None) -> Iterator[tuple[dict, str | None]]:
    """Yield every node in the document tree paired with its containing page.

    The Figma document tree has the shape DOCUMENT → CANVAS (= page) →
    FRAME/COMPONENT/INSTANCE/etc. The first time we encounter a CANVAS, we
    capture its name and propagate it down so downstream gates can attribute
    findings to the correct page.
    """
    if node.get("type") == "CANVAS":
        parent_page = node.get("name", "")
    yield node, parent_page
    for child in node.get("children") or []:
        yield from walk_nodes(child, parent_page)


def iter_pages(document: dict) -> Iterator[dict]:
    """Yield each page (CANVAS node) at the document root."""
    for child in document.get("children") or []:
        if child.get("type") == "CANVAS":
            yield child


def iter_text_nodes(document: dict, *, skip_pages: Iterable[str] = ("Candidates",)) -> Iterator[tuple[dict, str]]:
    """Yield ``(node, page_name)`` for every TEXT node outside the skipped pages."""
    skip_set = set(skip_pages)
    for node, page in walk_nodes(document):
        if node.get("type") == "TEXT" and (page or "") not in skip_set:
            yield node, page or ""


def collect_text_content(node: dict) -> str:
    """Concatenate the ``characters`` field across this node and all descendants.

    Useful for searching a frame's text content for marker strings (e.g.
    "version", "license") without caring about per-node structure.
    """
    parts: list[str] = []
    if node.get("type") == "TEXT" and node.get("characters"):
        parts.append(node["characters"])
    for child in node.get("children") or []:
        parts.append(collect_text_content(child))
    return "\n".join(p for p in parts if p)


def find_page(document: dict, name: str, *, case_insensitive: bool = True) -> dict | None:
    """Return the first page whose name matches ``name``."""
    target = name.lower() if case_insensitive else name
    for page in iter_pages(document):
        page_name = page.get("name", "")
        cand = page_name.lower() if case_insensitive else page_name
        if cand == target:
            return page
    return None
