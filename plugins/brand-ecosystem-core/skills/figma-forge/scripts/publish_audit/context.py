"""
Audit context — encapsulates REST access to one or more Figma files.

Two modes:

1. **Single-file mode** (v0.1.x backward compatibility): the auditor is
   pointed at one ``file_key`` and one PAT. The context exposes a single
   ``FigmaFile`` instance via ``ctx.primary``.

2. **Multi-file mode** (v0.2.0 new): the auditor is pointed at a
   ``LibraryRegistry`` and one PAT. The context fetches every declared
   file in parallel and exposes them via ``ctx.get(role)``.

Both modes share the same ``FigmaFile`` data class — only the orchestration
layer differs. Gates that care about cross-file checks (G10, G11, G18) ask
the context for specific roles. Gates that operate on whatever file they
are given iterate ``ctx.iter_publishable_files()``.
"""

from __future__ import annotations

import concurrent.futures
import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Iterator

from .registry import LibraryRegistry


# ----------------------------------------------------------------------------
# FigmaFile — single-file payload container
# ----------------------------------------------------------------------------

@dataclass
class FigmaFile:
    """Per-file payload fetched from the Figma REST API.

    Attributes are populated in ``fetch()``:
        name                  — Figma file name
        document              — root document node (CANVAS pages as children)
        styles                — declared style metadata (id → {key, name, …})
        components            — declared component metadata
        component_sets        — declared componentSet metadata
        variable_collections  — variable collection metadata (Variables API)
        variables             — variable metadata (Variables API)
        role                  — registry-assigned role ("foundations", etc.);
                                None when the context is single-file mode
    """
    file_key: str
    pat: str
    name: str = ""
    document: dict = field(default_factory=dict)
    styles: dict = field(default_factory=dict)
    components: dict = field(default_factory=dict)
    component_sets: dict = field(default_factory=dict)
    variable_collections: dict = field(default_factory=dict)
    variables: dict = field(default_factory=dict)
    role: str | None = None

    # --- Fetch ---------------------------------------------------------------

    def fetch(self) -> "FigmaFile":
        """Populate all fields via two REST round-trips. Returns self for chaining."""
        self._fetch_document()
        self._fetch_variables()
        return self

    def _request(self, path: str) -> dict:
        url = f"https://api.figma.com{path}"
        req = urllib.request.Request(url, headers={"X-Figma-Token": self.pat})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _fetch_document(self) -> None:
        data = self._request(f"/v1/files/{self.file_key}")
        self.name = data.get("name", "")
        self.document = data.get("document", {})
        self.styles = data.get("styles", {})
        self.components = data.get("components", {})
        self.component_sets = data.get("componentSets", {})

    def _fetch_variables(self) -> None:
        try:
            data = self._request(f"/v1/files/{self.file_key}/variables/local")
            meta = data.get("meta", {})
            self.variable_collections = meta.get("variableCollections", {})
            self.variables = meta.get("variables", {})
        except urllib.error.HTTPError as e:
            # Variables endpoint requires Enterprise; tolerate 403 gracefully.
            if e.code != 403:
                raise

    # --- Convenience constructors -------------------------------------------

    @classmethod
    def from_fixture(cls, fixture: dict, *, file_key: str = "fixture", role: str | None = None) -> "FigmaFile":
        """Build a FigmaFile from a pre-fetched JSON payload (used by tests).

        The fixture dict mirrors the structure of GET /v1/files/:key combined
        with GET /v1/files/:key/variables/local. Missing keys default to
        empty containers.
        """
        f = cls(file_key=file_key, pat="<fixture>", role=role)
        f.name = fixture.get("name", "")
        f.document = fixture.get("document", {})
        f.styles = fixture.get("styles", {})
        f.components = fixture.get("components", {})
        f.component_sets = fixture.get("componentSets", {})
        variables_block = fixture.get("variables_local", {}).get("meta", {})
        f.variable_collections = variables_block.get("variableCollections", {})
        f.variables = variables_block.get("variables", {})
        return f


# ----------------------------------------------------------------------------
# MultiFileFigmaContext — single source of truth for an audit run
# ----------------------------------------------------------------------------

@dataclass
class MultiFileFigmaContext:
    """Audit context spanning one or many Figma files.

    Use ``single_file`` constructor when running v0.1.x-style one-file audits
    or ``with_registry`` when running a full multi-file library audit.

    Always populate via ``fetch_all()`` (or ``fetch_all_fixtures()`` in tests)
    before passing to gate functions — gates assume payloads are loaded.
    """
    pat: str
    registry: LibraryRegistry | None = None
    files: dict[str, FigmaFile] = field(default_factory=dict)

    # Populated when no registry is provided (single-file mode)
    _primary_role: str = "primary"

    # --- Constructors --------------------------------------------------------

    @classmethod
    def single_file(cls, file_key: str, pat: str) -> "MultiFileFigmaContext":
        """v0.1.x-compatible: one file_key, no registry."""
        ctx = cls(pat=pat)
        ctx.files[ctx._primary_role] = FigmaFile(file_key=file_key, pat=pat, role=None)
        return ctx

    @classmethod
    def with_registry(cls, registry: LibraryRegistry, pat: str) -> "MultiFileFigmaContext":
        """v0.2.0: registry-driven multi-file audit."""
        ctx = cls(pat=pat, registry=registry)
        for role, info in registry.files.items():
            ctx.files[role] = FigmaFile(file_key=info.file_key, pat=pat, role=role)
        return ctx

    # --- Fetch orchestration ------------------------------------------------

    def fetch_all(self, *, max_workers: int = 4) -> None:
        """Populate every FigmaFile in parallel via threaded REST fetches.

        Errors propagate; if any single file fails to fetch, the entire audit
        run is aborted (rather than silently producing a partial report).
        """
        if not self.files:
            return
        if len(self.files) == 1:
            # Avoid thread pool overhead for the common single-file case.
            for f in self.files.values():
                f.fetch()
            return
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(f.fetch): role for role, f in self.files.items()}
            for fut in concurrent.futures.as_completed(futures):
                fut.result()  # re-raises on any error

    def load_fixtures(self, fixtures: dict[str, dict]) -> None:
        """Populate FigmaFile entries from pre-loaded JSON fixtures (test path).

        ``fixtures`` maps role → fixture dict. Roles missing from the input
        are left as un-fetched FigmaFile shells.
        """
        for role, fixture in fixtures.items():
            file_key = self.files[role].file_key if role in self.files else f"fixture_{role}"
            self.files[role] = FigmaFile.from_fixture(fixture, file_key=file_key, role=role)

    # --- Access -------------------------------------------------------------

    @property
    def primary(self) -> FigmaFile:
        """Return the single primary file in single-file mode.

        Raises ``RuntimeError`` if called on a multi-file context — callers in
        that mode should use ``get(role)`` or ``iter_publishable_files()``.
        """
        if self.registry is not None:
            raise RuntimeError(
                "primary file accessor only valid in single-file mode; "
                "use get(role) for registry-backed audits."
            )
        return self.files[self._primary_role]

    def get(self, role: str) -> FigmaFile | None:
        """Look up a file by role (case-insensitive). Returns None if absent."""
        return self.files.get(role.lower())

    def iter_publishable_files(self) -> Iterator[tuple[str, FigmaFile]]:
        """Yield ``(role, FigmaFile)`` for every file the audit should scan.

        In single-file mode this yields one pair with role ``"primary"``.
        In registry mode it yields every declared file in registry's publish
        order (Foundations first, Icons last).
        """
        if self.registry is None:
            yield self._primary_role, self.files[self._primary_role]
            return
        for role in self.registry.publish_order:
            if role in self.files:
                yield role, self.files[role]

    @property
    def is_multi_file(self) -> bool:
        return self.registry is not None and self.registry.is_multi_file
