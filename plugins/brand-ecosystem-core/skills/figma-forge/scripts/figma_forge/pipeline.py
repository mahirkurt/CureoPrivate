"""figma-forge ``run_pipeline`` — v1.1.0-alpha.

High-level entry point that drives the transport layer end-to-end
for a library bundle. Given a ``library_dir`` containing the
canonical bundle structure (tokens, components, patterns, icons,
code-connect, library-registry), this function:

1. Walks the bundle and emits the appropriate transport operations
2. Routes each operation through a :class:`TransportRouter`
3. Returns a :class:`PipelineResult` summarizing what happened

v1.1.0-alpha implements the **foundations channel** end-to-end
(variable collection + variables + alias rebinding from the merged
DTCG token file) and stubs the remainder. v1.1.0 GA will fill in
icons + components + patterns + code-connect.
"""

from __future__ import annotations

import itertools
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .transport.errors import CapabilityUnsupportedError, TransportError
from .transport.concurrency import ConcurrencyReport, check_concurrency
from .transport.plugin_capture import PluginCaptureTransport
from .transport.protocol import (
    CodeConnectMapping,
    CollectionRef,
    ComponentGeometry,
    ComponentRef,
    PageRef,
    SessionResult,
    TransportAdapter,
    VariableType,
    VariantSpec,
)
from .transport.rest import RestTransport
from .transport.router import TransportRouter
from .transport.stub import StubTransport

logger = logging.getLogger("figma_forge.pipeline")


@dataclass
class PipelineResult:
    """Outcome of a pipeline run."""
    stages_completed: list[str] = field(default_factory=list)
    stages_failed: list[str] = field(default_factory=list)
    operations_attempted: int = 0
    operations_succeeded: int = 0
    session_results: dict[str, SessionResult] = field(default_factory=dict)
    fallback_warnings: list[str] = field(default_factory=list)
    concurrency_report: "ConcurrencyReport | None" = None

    @property
    def is_success(self) -> bool:
        return not self.stages_failed


def run_pipeline(
    library_dir: Path,
    *,
    transport: TransportAdapter | TransportRouter | None = None,
    file_key: str = "",
    stages: list[str] | None = None,
    detect_concurrency: bool = False,
) -> PipelineResult:
    """Drive the figma-forge build pipeline against a library bundle.

    Parameters
    ----------
    library_dir:
        Path to the canonical bundle directory. Must contain at
        minimum a ``library-registry.json`` and a ``tokens/`` subtree.
    transport:
        Either a single :class:`TransportAdapter` (e.g.
        ``ff.PluginCaptureTransport()``) or a :class:`TransportRouter`
        for multi-adapter strategies. When ``None`` (default), uses
        a router preferring REST → PluginCapture → Stub.
    file_key:
        The Figma file key for the target Foundations file. When
        empty (default), the pipeline operates against a placeholder
        key — useful for dry-runs and tests.
    stages:
        Optional subset of stages to execute. When ``None``, runs
        the full v1.1.0-alpha-supported pipeline. Stage names match
        the orchestrate manifest's ``mode`` field.

    Returns
    -------
    PipelineResult
        Summary including stages completed/failed, operation counts,
        session artifacts, and any router fallback warnings.

    Notes
    -----
    v1.1.0-alpha implements the **FOUNDATIONS_BUILD** stage end-to-end
    through the transport layer. Other stages
    (COMPONENTS_BUILD, ICONS_BUILD, PATTERNS_BUILD, CODE_CONNECT,
    PUBLISH) are recognized but defer their actual work to v1.1.0 GA.
    """
    library_dir = Path(library_dir)
    if not library_dir.exists():
        raise FileNotFoundError(library_dir)

    # Resolve transport: accept either router or single adapter
    if transport is None:
        router = _default_router()
    elif isinstance(transport, TransportRouter):
        router = transport
    else:
        # Single adapter wrapped in a router with stub fallback
        adapters = {transport.adapter_id(): transport}
        if "stub" not in adapters:
            adapters["stub"] = StubTransport()
        router = TransportRouter(
            adapters=adapters,
            preferences=[transport.adapter_id(), "stub"],
        )

    stages_to_run = stages or [
        "FOUNDATIONS_BUILD", "ICONS_BUILD",
        "COMPONENTS_BUILD", "PATTERNS_BUILD", "CODE_CONNECT",
    ]
    result = PipelineResult()

    # Concurrency detection: snapshot the file's last_modified before
    # the build so we can detect edits made by another editor during
    # the run. Best-effort — capture-mode adapters can't read live
    # state, in which case the baseline is empty and the post-build
    # check reports checked=False.
    baseline_modified = ""
    if detect_concurrency and file_key:
        baseline_modified = _concurrency_baseline(router, file_key)

    if "FOUNDATIONS_BUILD" in stages_to_run:
        _run_foundations(library_dir, router, result, file_key)

    if "ICONS_BUILD" in stages_to_run:
        _run_icons(library_dir, router, result, file_key)

    if "COMPONENTS_BUILD" in stages_to_run:
        _run_components(library_dir, router, result, file_key)

    if "PATTERNS_BUILD" in stages_to_run:
        _run_patterns(library_dir, router, result, file_key)

    if "CODE_CONNECT" in stages_to_run:
        _run_code_connect(library_dir, router, result, file_key)

    # Any stage not yet implemented is recorded as deferred
    known = {
        "FOUNDATIONS_BUILD", "ICONS_BUILD", "COMPONENTS_BUILD",
        "PATTERNS_BUILD", "CODE_CONNECT",
    }
    for stage in stages_to_run:
        if stage not in known:
            result.stages_completed.append(f"{stage} (deferred-v1.2)")

    result.fallback_warnings = list(router.fallback_warnings)

    # Post-build concurrency check: compare current last_modified to
    # the baseline captured before the build.
    if detect_concurrency and file_key:
        report = check_concurrency(
            router.select("get_file"), file_key=file_key,
            baseline_modified=baseline_modified,
        )
        result.concurrency_report = report
        if report.has_concurrent_edit:
            result.fallback_warnings.append(report.detail)

    return result


def _concurrency_baseline(router: TransportRouter, file_key: str) -> str:
    """Capture the file's last_modified before a build (best-effort)."""
    try:
        return router.select("get_file").get_file(
            key=file_key
        ).last_modified
    except TransportError:
        return ""


# ---------------------------------------------------------------------------
# Stage runners — one per orchestrate mode
# ---------------------------------------------------------------------------

def _run_foundations(
    library_dir: Path,
    router: TransportRouter,
    result: PipelineResult,
    file_key: str,
) -> None:
    """Convert merged DTCG → Variable collection + Variables + aliases."""
    from publish_audit.static_lint import _find_merged_dtcg
    merged = _find_merged_dtcg(library_dir)
    if merged is None or not merged.exists():
        result.stages_failed.append("FOUNDATIONS_BUILD: no merged DTCG found")
        return

    try:
        tokens = json.loads(merged.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        result.stages_failed.append(f"FOUNDATIONS_BUILD: token parse: {e}")
        return

    file_key = file_key or "placeholder-file"
    color = tokens.get("color")
    if not isinstance(color, dict):
        result.stages_failed.append("FOUNDATIONS_BUILD: no 'color' branch")
        return

    # 1. Create the Renkler / Colors collection
    coll_adapter = router.select("create_variable_collection")
    coll_token = coll_adapter.begin_session()
    try:
        collection = coll_adapter.create_variable_collection(
            file_key=file_key,
            name="Renkler",  # Düstur convention
            modes=["Aydınlık", "Karanlık"],
        )
        result.operations_attempted += 1
        result.operations_succeeded += 1
    except TransportError as e:
        result.stages_failed.append(f"FOUNDATIONS_BUILD: collection: {e}")
        return

    # 2. Create primitives — one variable per leaf in declared
    #    color_families. Aliases (e.g. color.semantic.*) are deferred
    #    to step 3.
    family_list = _color_families_for(library_dir)
    aliases_to_create: list[tuple[str, str]] = []
    primitive_vars: dict[str, Any] = {}  # path → VariableRef

    var_adapter = router.select("create_variable")

    for family_name in family_list:
        family = color.get(family_name)
        if not isinstance(family, dict):
            continue
        for step_name, step in family.items():
            if step_name.startswith("$"):
                continue
            if not (isinstance(step, dict) and "$value" in step):
                continue
            value = step["$value"]
            full_path = f"color.{family_name}.{step_name}"
            try:
                ref = var_adapter.create_variable(
                    collection_ref=collection,
                    name=full_path,
                    type="COLOR",
                    values_per_mode={
                        "Aydınlık": value,
                        "Karanlık": value,
                    },
                )
                primitive_vars[full_path] = ref
                result.operations_attempted += 1
                result.operations_succeeded += 1
            except TransportError as e:
                result.operations_attempted += 1
                logger.warning("variable %s failed: %s", full_path, e)

    # 3. Walk semantic / alias branches; queue aliases
    def _walk(node, prefix):
        if not isinstance(node, dict):
            return
        if "$value" in node and isinstance(node["$value"], str):
            v = node["$value"]
            if v.startswith("{") and v.endswith("}"):
                aliases_to_create.append((prefix, v[1:-1]))
            return
        for k, sub in node.items():
            if k.startswith("$"):
                continue
            _walk(sub, f"{prefix}.{k}" if prefix else k)

    _walk(tokens, "")

    alias_adapter = router.select("create_alias_reference")
    for source_path, target_path in aliases_to_create:
        source_ref = primitive_vars.get(source_path)
        target_ref = primitive_vars.get(target_path)
        if source_ref is None or target_ref is None:
            continue
        try:
            alias_adapter.create_alias_reference(
                source_var=source_ref,
                target_var=target_ref,
                mode_id="Aydınlık",
            )
            result.operations_attempted += 1
            result.operations_succeeded += 1
        except TransportError as e:
            result.operations_attempted += 1
            logger.warning("alias %s → %s failed: %s",
                           source_path, target_path, e)

    # Commit the session — for capture adapters this materializes the
    # TS script; for REST it would flush the queue; for stub it's a no-op.
    commit_result = coll_adapter.commit_session(coll_token)
    result.session_results[coll_adapter.adapter_id()] = commit_result
    result.stages_completed.append("FOUNDATIONS_BUILD")


def _run_icons(
    library_dir: Path,
    router: TransportRouter,
    result: PipelineResult,
    file_key: str,
) -> None:
    """Import every SVG in ``icons/svg/`` as a Figma component.

    Walks ``icons/svg/<category>/<name>.svg`` recursively. For each
    SVG file:

    1. Reads the raw SVG source
    2. Routes ``create_page`` once per category (idempotent by name)
    3. Routes ``import_svg_as_component`` once per SVG, with the file
       basename (sans extension) as the component name and a
       canonical 24×24 size (Düstur convention; overridable when
       per-category sizing metadata exists in the future)

    Stages a single session per category so the captured TS or
    queued REST batch lands as a coherent unit per page.
    """
    icons_dir = library_dir / "icons" / "svg"
    if not icons_dir.exists():
        # No icons in this bundle — skip without failing
        result.stages_completed.append("ICONS_BUILD (no icons/svg directory)")
        return

    file_key = file_key or "placeholder-icons-file"
    page_adapter = router.select("create_page")
    svg_adapter = router.select("import_svg_as_component")

    # Open a session on the adapter that will handle the SVGs
    svg_session = svg_adapter.begin_session()

    categories = sorted(
        d for d in icons_dir.iterdir() if d.is_dir()
    )
    total_imported = 0

    for cat_dir in categories:
        category = cat_dir.name
        # Create (or reuse) a page named after the category
        try:
            page_ref = page_adapter.create_page(
                file_key=file_key,
                name=f"Icons / {category}",
            )
            result.operations_attempted += 1
            result.operations_succeeded += 1
        except TransportError as e:
            result.operations_attempted += 1
            logger.warning("create_page(%s) failed: %s", category, e)
            continue

        # Walk every .svg in the category
        svgs = sorted(cat_dir.rglob("*.svg"))
        for svg_path in svgs:
            icon_name = svg_path.stem
            try:
                svg_source = svg_path.read_text(encoding="utf-8")
            except OSError as e:
                logger.warning("read %s failed: %s", svg_path, e)
                continue

            try:
                svg_adapter.import_svg_as_component(
                    page_ref=page_ref,
                    name=icon_name,
                    svg_source=svg_source,
                    canonical_size=(24, 24),
                )
                result.operations_attempted += 1
                result.operations_succeeded += 1
                total_imported += 1
            except TransportError as e:
                result.operations_attempted += 1
                logger.warning("import_svg(%s) failed: %s", icon_name, e)

    commit_result = svg_adapter.commit_session(svg_session)
    # Don't overwrite the foundations session if same adapter handles both
    key = svg_adapter.adapter_id()
    if key in result.session_results:
        # Merge artifacts under a stage-specific key
        result.session_results[f"{key}::icons"] = commit_result
    else:
        result.session_results[key] = commit_result

    result.stages_completed.append(
        f"ICONS_BUILD ({total_imported} icons across "
        f"{len(categories)} categories)"
    )


def _run_components(
    library_dir: Path,
    router: TransportRouter,
    result: PipelineResult,
    file_key: str,
) -> None:
    """Build variant-aware components from ``components/*.json`` specs.

    Each spec declares ``variants.axes`` — a dict of axis name → list
    of values (e.g. ``{"Variant": ["Primary", "Secondary"], "Size":
    ["sm", "md", "lg"]}``). The Cartesian product of the axes forms
    the variant set, minus any ``variants.disabled_combinations``.

    For specs with one or more axes, a ComponentSet is created with
    the full variant matrix. For specs with no axes, a single
    Component is created. The component's ``description`` is attached
    via ``update_component_description``.
    """
    components_dir = library_dir / "components"
    if not components_dir.exists():
        result.stages_completed.append("COMPONENTS_BUILD (no components directory)")
        return

    file_key = file_key or "placeholder-components-file"
    page_adapter = router.select("create_page")
    set_adapter = router.select("create_component_set")
    comp_adapter = router.select("create_component")
    desc_adapter = router.select("update_component_description")

    session_adapter = set_adapter  # the adapter that does the heavy lifting
    session = session_adapter.begin_session()

    # One page holds all base components
    try:
        page_ref = page_adapter.create_page(
            file_key=file_key, name="Components",
        )
        result.operations_attempted += 1
        result.operations_succeeded += 1
    except TransportError as e:
        result.stages_failed.append(f"COMPONENTS_BUILD: page: {e}")
        return

    specs = sorted(components_dir.glob("*.json"))
    components_built = 0
    variants_built = 0

    for spec_path in specs:
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            logger.warning("component spec %s parse: %s", spec_path.name, e)
            continue

        comp_meta = spec.get("component", {})
        name = comp_meta.get("name")
        if not name:
            continue
        description = comp_meta.get("description", "")

        axes = (spec.get("variants") or {}).get("axes") or {}
        disabled = set(
            (spec.get("variants") or {}).get("disabled_combinations") or []
        )

        if axes:
            # Build the Cartesian product of all axes into VariantSpecs
            variant_specs = _variant_specs_from_axes(axes, disabled)
            try:
                set_ref = set_adapter.create_component_set(
                    page_ref=page_ref,
                    name=name,
                    variants=variant_specs,
                )
                result.operations_attempted += 1
                result.operations_succeeded += 1
                components_built += 1
                variants_built += len(variant_specs)
                # Attach description to the set
                if description:
                    try:
                        desc_adapter.update_component_description(
                            component_ref=ComponentRef(
                                file_key=file_key,
                                node_id=set_ref.node_id,
                                name=name,
                            ),
                            description=description,
                            doc_links=[],
                        )
                        result.operations_attempted += 1
                        result.operations_succeeded += 1
                    except TransportError:
                        result.operations_attempted += 1
            except TransportError as e:
                result.operations_attempted += 1
                logger.warning("component_set %s failed: %s", name, e)
        else:
            # Single component, no variants
            try:
                comp_ref = comp_adapter.create_component(
                    page_ref=page_ref,
                    name=name,
                    geometry=ComponentGeometry(width=200, height=48),
                )
                result.operations_attempted += 1
                result.operations_succeeded += 1
                components_built += 1
                if description:
                    try:
                        desc_adapter.update_component_description(
                            component_ref=comp_ref,
                            description=description,
                            doc_links=[],
                        )
                        result.operations_attempted += 1
                        result.operations_succeeded += 1
                    except TransportError:
                        result.operations_attempted += 1
            except TransportError as e:
                result.operations_attempted += 1
                logger.warning("component %s failed: %s", name, e)

    commit_result = session_adapter.commit_session(session)
    key = session_adapter.adapter_id()
    result.session_results[
        f"{key}::components" if key in result.session_results else key
    ] = commit_result

    result.stages_completed.append(
        f"COMPONENTS_BUILD ({components_built} components, "
        f"{variants_built} variants)"
    )


def _run_patterns(
    library_dir: Path,
    router: TransportRouter,
    result: PipelineResult,
    file_key: str,
) -> None:
    """Build composite patterns from ``patterns/*.json`` specs.

    Patterns are compositional — they reference base components via
    ``composition.uses_components``. Each pattern is created as a
    Component on a Patterns page; then, when the selected adapter
    supports instance placement, each referenced component is placed
    as a real nested instance inside the pattern frame via
    ``place_instance`` (v1.2.0). When the adapter cannot place
    instances (e.g. the REST channel), the pattern still carries its
    composition metadata in the description for documentation, and the
    instance placements are skipped with a recorded count.
    """
    patterns_dir = library_dir / "patterns"
    if not patterns_dir.exists():
        result.stages_completed.append("PATTERNS_BUILD (no patterns directory)")
        return

    file_key = file_key or "placeholder-patterns-file"
    page_adapter = router.select("create_page")
    comp_adapter = router.select("create_component")
    desc_adapter = router.select("update_component_description")

    # Instance composition uses the same adapter that built the
    # pattern frame, to keep all nodes in one session. Only attempt it
    # when that adapter actually supports place_instance.
    can_compose = comp_adapter.supports("place_instance")

    session = comp_adapter.begin_session()

    try:
        page_ref = page_adapter.create_page(
            file_key=file_key, name="Patterns",
        )
        result.operations_attempted += 1
        result.operations_succeeded += 1
    except TransportError as e:
        result.stages_failed.append(f"PATTERNS_BUILD: page: {e}")
        return

    specs = sorted(patterns_dir.glob("*.json"))
    patterns_built = 0
    instances_placed = 0

    for spec_path in specs:
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            logger.warning("pattern spec %s parse: %s", spec_path.name, e)
            continue

        pat_meta = spec.get("pattern", {})
        name = pat_meta.get("name")
        if not name:
            continue

        description = pat_meta.get("description", "")
        composition = spec.get("composition", {})
        uses = composition.get("uses_components", []) or []
        regions = composition.get("regions", {}) or {}

        # Enrich the description with composition metadata for docs
        comp_doc = description
        if uses:
            comp_doc += f"\n\nUses components: {', '.join(uses)}."
        if regions:
            comp_doc += f"\nRegions: {', '.join(regions.keys())}."

        try:
            comp_ref = comp_adapter.create_component(
                page_ref=page_ref,
                name=name,
                geometry=ComponentGeometry(width=1440, height=900),
            )
            result.operations_attempted += 1
            result.operations_succeeded += 1
            patterns_built += 1
            if comp_doc:
                try:
                    desc_adapter.update_component_description(
                        component_ref=comp_ref,
                        description=comp_doc,
                        doc_links=[],
                    )
                    result.operations_attempted += 1
                    result.operations_succeeded += 1
                except TransportError:
                    result.operations_attempted += 1

            # v1.2: place real nested instances of referenced components
            if can_compose and uses:
                instances_placed += _compose_pattern_instances(
                    comp_adapter, comp_ref, uses, result,
                )
        except TransportError as e:
            result.operations_attempted += 1
            logger.warning("pattern %s failed: %s", name, e)

    commit_result = comp_adapter.commit_session(session)
    key = comp_adapter.adapter_id()
    result.session_results[
        f"{key}::patterns" if key in result.session_results else key
    ] = commit_result

    if can_compose and instances_placed:
        result.stages_completed.append(
            f"PATTERNS_BUILD ({patterns_built} patterns, "
            f"{instances_placed} nested instances)"
        )
    else:
        suffix = " (composition skipped — adapter lacks place_instance)" \
            if (not can_compose) else ""
        result.stages_completed.append(
            f"PATTERNS_BUILD ({patterns_built} patterns){suffix}"
        )


def _compose_pattern_instances(
    adapter: TransportAdapter,
    pattern_ref: ComponentRef,
    uses_components: list[str],
    result: PipelineResult,
) -> int:
    """Place each referenced component as a nested instance.

    For each entry in ``uses_components``, synthesize a
    :class:`ComponentRef` (by name) for the main component and place
    an instance inside ``pattern_ref`` via ``place_instance``,
    stacking instances vertically. Returns the number of instances
    successfully placed.

    A ``uses_components`` entry may carry a parenthetical variant hint
    (e.g. ``"YuzeyBadge (Solid, Kanun)"``); the bare component name
    before the parenthesis is used for the reference, and the parsed
    variant pairs are applied via ``set_instance_property``.
    """
    placed = 0
    y_cursor = 0
    y_step = 80
    for entry in uses_components:
        comp_name, variant_props = _parse_component_reference(entry)
        comp_ref = ComponentRef(
            file_key=pattern_ref.file_key,
            node_id=f"main-for-{comp_name}",
            name=comp_name,
        )
        try:
            inst_ref = adapter.place_instance(
                parent_ref=pattern_ref,
                component_ref=comp_ref,
                position=(0, y_cursor),
            )
            result.operations_attempted += 1
            result.operations_succeeded += 1
            placed += 1
            y_cursor += y_step
            # Apply any parsed variant properties to the instance
            for key, value in variant_props.items():
                try:
                    adapter.set_instance_property(
                        instance_ref=inst_ref, key=key, value=value,
                    )
                    result.operations_attempted += 1
                    result.operations_succeeded += 1
                except TransportError:
                    result.operations_attempted += 1
        except TransportError as e:
            result.operations_attempted += 1
            logger.warning("place_instance %s failed: %s", comp_name, e)
    return placed


def _parse_component_reference(entry: str) -> tuple[str, dict[str, str]]:
    """Split ``"Name (V1, V2)"`` into ``("Name", {"prop0": "V1", ...})``.

    The bare name (text before the first parenthesis) is the component
    name. Parenthetical tokens are treated as positional variant
    values and keyed ``prop0``, ``prop1``, … (the spec doesn't name
    the axes inline, so positional keys are a faithful, lossless
    capture for the instance property descriptor). Entries without a
    parenthesis yield an empty property dict.
    """
    entry = entry.strip()
    if "(" not in entry:
        return entry, {}
    name = entry.split("(", 1)[0].strip()
    inside = entry[entry.index("(") + 1:]
    inside = inside.rsplit(")", 1)[0]
    props: dict[str, str] = {}
    for i, tok in enumerate(t.strip() for t in inside.split(",")):
        if tok:
            props[f"prop{i}"] = tok
    return name, props


def _run_code_connect(
    library_dir: Path,
    router: TransportRouter,
    result: PipelineResult,
    file_key: str,
) -> None:
    """Attach Code Connect mappings from ``code-connect/*.json`` specs.

    Each spec declares a ``react`` block (``import_statement``,
    ``code_example``, ``props``) and optional ``web_components`` /
    other framework blocks. v1.1 attaches the React mapping via
    ``attach_code_connect``. Because Code Connect is REST-only (the
    plugin runtime can't attach mappings), this stage routes to the
    REST adapter; when no REST credentials are present, the router
    falls back to the stub and the stage records a warning rather
    than failing.
    """
    cc_dir = library_dir / "code-connect"
    if not cc_dir.exists():
        result.stages_completed.append("CODE_CONNECT (no code-connect directory)")
        return

    file_key = file_key or "placeholder-cc-file"
    cc_adapter = router.select("attach_code_connect")

    session = cc_adapter.begin_session()

    specs = sorted(cc_dir.glob("*.json"))
    mappings_attached = 0
    mappings_skipped = 0

    for spec_path in specs:
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            logger.warning("code-connect spec %s parse: %s", spec_path.name, e)
            continue

        figma_name = spec.get("figma_component_name") or spec.get("component_id")
        react = spec.get("react", {})
        if not figma_name or not react:
            continue

        mapping = CodeConnectMapping(
            framework="react",
            import_statement=react.get("import_statement", ""),
            code_example=react.get("code_example", ""),
            props_mapping={
                k: {"kind": "enum", "values": str(v)}
                for k, v in (react.get("props", {}) or {}).items()
            },
        )
        comp_ref = ComponentRef(
            file_key=file_key,
            node_id=f"node-for-{spec.get('component_id', figma_name)}",
            name=figma_name,
        )
        try:
            cc_adapter.attach_code_connect(
                component_ref=comp_ref, mapping=mapping,
            )
            result.operations_attempted += 1
            result.operations_succeeded += 1
            mappings_attached += 1
        except CapabilityUnsupportedError:
            # Adapter can't attach (e.g. fell through to plugin-capture
            # which doesn't support Code Connect) — count as skipped
            result.operations_attempted += 1
            mappings_skipped += 1
        except TransportError as e:
            result.operations_attempted += 1
            logger.warning("code_connect %s failed: %s", figma_name, e)

    commit_result = cc_adapter.commit_session(session)
    key = cc_adapter.adapter_id()
    result.session_results[
        f"{key}::code_connect" if key in result.session_results else key
    ] = commit_result

    suffix = f", {mappings_skipped} skipped" if mappings_skipped else ""
    result.stages_completed.append(
        f"CODE_CONNECT ({mappings_attached} mappings attached{suffix})"
    )


def _variant_specs_from_axes(
    axes: dict[str, list[str]],
    disabled: set[str],
) -> list[VariantSpec]:
    """Expand variant axes into the Cartesian product of VariantSpecs.

    ``axes`` maps axis name → list of values. The Cartesian product
    of all axis values forms the variant matrix. Each combination is
    checked against ``disabled`` (a set of human-readable combination
    descriptors like ``"Variant=Ghost, State=Hover"``); matching
    combinations are excluded.

    Returns one :class:`VariantSpec` per surviving combination, with
    its ``properties`` dict mapping axis name → chosen value and a
    canonical name like ``"Variant=Primary, Size=md, State=Default"``.
    """
    axis_names = list(axes.keys())
    axis_values = [axes[name] for name in axis_names]

    specs: list[VariantSpec] = []
    for combo in itertools.product(*axis_values):
        props = dict(zip(axis_names, combo))
        descriptor = ", ".join(f"{k}={v}" for k, v in props.items())
        # Exclude disabled combinations — match if every k=v in a
        # disabled descriptor is present in this combo
        if _is_disabled(props, disabled):
            continue
        specs.append(VariantSpec(
            name=descriptor,
            properties=props,
            geometry=ComponentGeometry(width=120, height=40),
        ))
    return specs


def _is_disabled(props: dict[str, str], disabled: set[str]) -> bool:
    """Return True if ``props`` matches any disabled-combination clause.

    A disabled descriptor like ``"Variant=Ghost, State=Hover (uses ...)"``
    is parsed for its ``key=value`` pairs; if every parsed pair is
    present in ``props``, the combination is disabled. Trailing prose
    after the pairs (in parentheses) is ignored.
    """
    for clause in disabled:
        # Extract key=value tokens from the clause prefix
        head = clause.split("(")[0]
        pairs = {}
        for token in head.split(","):
            token = token.strip()
            if "=" in token:
                k, v = token.split("=", 1)
                pairs[k.strip()] = v.strip()
        if pairs and all(props.get(k) == v for k, v in pairs.items()):
            return True
    return False


def _color_families_for(library_dir: Path) -> list[str]:
    """Read declared color family names from ``library-registry.json``.

    Two registry shapes coexist in the figma-forge ecosystem:

    1. **List-of-dicts shape** (Material 3 stub, IBM Carbon stub)::

           "color_families": [
             {"name": "gray", "expected_steps": 10},
             {"name": "blue", "expected_steps": 10}
           ]

    2. **Dict-keyed shape** (Düstur Tasarım Sistemi and other
       semantically-named systems)::

           "color_families": {
             "tbk":      {"name": "TBK (Türk Bayrağı Kırmızısı)", ...},
             "lacivert": {"name": "Cumhuriyet Lacivert",          ...},
             ...
           }

    For the dict-keyed shape, the **dict keys** (``tbk``,
    ``lacivert``, …) are returned because those are the prefixes used
    in the merged DTCG token tree (``color.tbk.9``, etc.), not the
    human-readable display name in the value's ``name`` field.

    Returns an empty list when the registry is missing, malformed, or
    declares no color families.
    """
    reg = library_dir / "library-registry.json"
    if not reg.exists():
        return []
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    families = data.get("color_families")
    if isinstance(families, dict):
        # Dict-keyed shape (Düstur convention) — keys are the DTCG
        # token-tree prefixes; values carry metadata for documentation.
        return [str(k) for k in families.keys()]
    if isinstance(families, list):
        # List-of-dicts shape (Material 3 / Carbon convention) —
        # each entry's ``name`` field is the token-tree prefix.
        return [
            str(f["name"])
            for f in families
            if isinstance(f, dict) and "name" in f
        ]
    return []


def _default_router() -> TransportRouter:
    """Construct the default router (REST → PluginCapture → Stub).

    ``McpCursorTransport`` is intentionally **not** in the default
    chain. It assumes an MCP-capable agent context (its
    ``authentication_required`` reports ``ambient-mcp``), and adding it
    to the default would cause it to silently emit a tool-call plan in
    environments where no agent executes it. To use MCP dispatch, build
    a router explicitly with ``McpCursorTransport`` in the preference
    list — e.g. ``preferences=["rest-v1", "mcp-cursor", "stub"]`` so
    that MCP becomes the credential-free fallback for Code Connect when
    no REST PAT is present.
    """
    return TransportRouter(
        adapters={
            "stub": StubTransport(),
            "plugin-capture": PluginCaptureTransport(),
            "rest-v1": RestTransport(),
        },
        preferences=["rest-v1", "plugin-capture", "stub"],
    )


__all__ = ["PipelineResult", "run_pipeline"]
