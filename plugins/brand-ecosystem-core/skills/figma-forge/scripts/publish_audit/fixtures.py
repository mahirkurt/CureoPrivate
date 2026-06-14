"""
Fixture generators for publish-audit gate testing.

Each generator produces a dict that mirrors the structure of:
  GET /v1/files/:key            (document, styles, components, componentSets)
  GET /v1/files/:key/variables  (variables_local.meta.{variableCollections, variables})

The generated dicts are consumed by ``FigmaFile.from_fixture(...)`` and
exercised against gate checkers in ``tests/test_publish_audit.py``.

Design principles:
  * **Deterministic** — same arguments → same output. No random IDs.
  * **Minimal** — only fields read by the gate under test are populated.
    Other fields are left absent (Figma's actual API is sparse for missing
    data; absent ≠ empty in their schema).
  * **Composable** — high-level helpers (e.g. ``make_foundations_fixture``)
    build on low-level primitives (``make_canvas``, ``make_component``).
"""

from __future__ import annotations

import itertools
from typing import Any


# ----------------------------------------------------------------------------
# ID generator — deterministic, monotone
# ----------------------------------------------------------------------------

_id_counter = itertools.count(start=1)


def fresh_id(prefix: str = "node") -> str:
    """Return a fresh, monotonically increasing node-id-shaped string."""
    n = next(_id_counter)
    return f"{prefix}_{n}"


def reset_id_counter() -> None:
    """Reset the deterministic ID counter — call at the start of each fixture."""
    global _id_counter
    _id_counter = itertools.count(start=1)


# ----------------------------------------------------------------------------
# Low-level primitives
# ----------------------------------------------------------------------------

def make_text_node(*, text: str = "Hello", style_id: str | None = None,
                   name: str | None = None) -> dict:
    """A TEXT node, optionally bound to a text style."""
    node: dict[str, Any] = {
        "id": fresh_id("text"),
        "type": "TEXT",
        "name": name or text[:40],
        "characters": text,
    }
    if style_id:
        node["styles"] = {"text": style_id}
    return node


def make_solid_fill(*, variable_id: str | None = None, hex_color: str = "#000000") -> dict:
    """A SOLID fill, optionally bound to a color variable."""
    fill: dict[str, Any] = {"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0, "a": 1}}
    if variable_id:
        fill["boundVariables"] = {"color": {"type": "VARIABLE_ALIAS", "id": variable_id}}
    return fill


def make_rectangle(*, name: str = "rect", fills: list[dict] | None = None) -> dict:
    return {
        "id": fresh_id("rect"),
        "type": "RECTANGLE",
        "name": name,
        "fills": fills or [],
    }


def make_frame(*, name: str = "frame", children: list[dict] | None = None,
                fills: list[dict] | None = None) -> dict:
    return {
        "id": fresh_id("frame"),
        "type": "FRAME",
        "name": name,
        "children": children or [],
        "fills": fills or [],
    }


def make_canvas(*, name: str, children: list[dict] | None = None) -> dict:
    """A CANVAS node (= page) at document root."""
    return {
        "id": fresh_id("canvas"),
        "type": "CANVAS",
        "name": name,
        "children": children or [],
    }


def make_document(*, pages: list[dict]) -> dict:
    return {
        "id": "0:0",
        "type": "DOCUMENT",
        "name": "Document",
        "children": pages,
    }


# ----------------------------------------------------------------------------
# Style + component metadata blocks
# ----------------------------------------------------------------------------

def make_style(*, style_id: str | None = None, name: str = "body-01",
               style_type: str = "TEXT", published: bool = True,
               remote: bool = False) -> tuple[str, dict]:
    """Return ``(style_id, style_metadata_dict)`` ready to insert into ``file.styles``."""
    sid = style_id or fresh_id("style")
    return sid, {
        "key": f"styleKey_{sid}",
        "name": name,
        "styleType": style_type,
        "published": published,
        "remote": remote,
    }


def make_component(*, component_id: str | None = None, name: str = "Component",
                    description: str = "", component_set_id: str | None = None) -> tuple[str, dict]:
    cid = component_id or fresh_id("component")
    meta: dict[str, Any] = {
        "key": f"componentKey_{cid}",
        "name": name,
        "description": description,
    }
    if component_set_id:
        meta["componentSetId"] = component_set_id
    return cid, meta


def make_component_set(*, set_id: str | None = None, name: str = "ComponentSet",
                        description: str = "") -> tuple[str, dict]:
    sid = set_id or fresh_id("compset")
    return sid, {
        "key": f"compsetKey_{sid}",
        "name": name,
        "description": description,
    }


# ----------------------------------------------------------------------------
# Variable metadata block
# ----------------------------------------------------------------------------

def make_variable_collection(*, collection_id: str | None = None,
                              name: str = "Collection",
                              modes: list[dict] | None = None) -> tuple[str, dict]:
    cid = collection_id or fresh_id("varcoll")
    if modes is None:
        modes = [{"modeId": f"{cid}_mode_0", "name": "Default"}]
    return cid, {
        "id": cid,
        "name": name,
        "modes": modes,
    }


def make_variable(*, variable_id: str | None = None, name: str = "var",
                   collection_id: str = "varcoll_1",
                   values_by_mode: dict | None = None,
                   resolved_type: str = "COLOR") -> tuple[str, dict]:
    vid = variable_id or fresh_id("var")
    return vid, {
        "id": vid,
        "name": name,
        "variableCollectionId": collection_id,
        "resolvedType": resolved_type,
        "valuesByMode": values_by_mode or {},
    }


def alias_value(target_var_id: str) -> dict:
    """Return a Figma VARIABLE_ALIAS value dict targeting ``target_var_id``."""
    return {"type": "VARIABLE_ALIAS", "id": target_var_id}


# ----------------------------------------------------------------------------
# High-level fixture builders
# ----------------------------------------------------------------------------

def make_file_fixture(
    *,
    name: str = "Fixture File",
    pages: list[dict] | None = None,
    styles: dict[str, dict] | None = None,
    components: dict[str, dict] | None = None,
    component_sets: dict[str, dict] | None = None,
    variable_collections: dict[str, dict] | None = None,
    variables: dict[str, dict] | None = None,
) -> dict:
    """Compose the full file payload (REST shape) from individual pieces."""
    return {
        "name": name,
        "document": make_document(pages=pages or [make_canvas(name="Page 1")]),
        "styles": styles or {},
        "components": components or {},
        "componentSets": component_sets or {},
        "variables_local": {
            "meta": {
                "variableCollections": variable_collections or {},
                "variables": variables or {},
            }
        },
    }


def make_minimal_valid_foundations() -> dict:
    """A minimal Foundations file that should pass every Sprint-1 gate."""
    reset_id_counter()
    # One color variable in one collection with one mode
    coll_id, coll = make_variable_collection(
        collection_id="varcoll_color",
        name="Color",
        modes=[{"modeId": "mode_default", "name": "Default"}]
    )
    var_id, var = make_variable(
        variable_id="var_primary",
        name="color/primary",
        collection_id=coll_id,
        values_by_mode={"mode_default": {"r": 0, "g": 0.4, "b": 0.8, "a": 1}},
        resolved_type="COLOR"
    )
    # Cover page with complete metadata
    cover = make_canvas(name="Cover", children=[
        make_frame(name="Title", children=[
            make_text_node(text="Hemantix DS", style_id="style_title"),
            make_text_node(text="Version: 1.0.0", style_id="style_body"),
            make_text_node(text="License: Internal use only", style_id="style_body"),
            make_text_node(text="Contact: design-system@hemantix.example",
                            style_id="style_body"),
        ])
    ])
    # Tokens page that uses the variable (so it's not orphaned)
    swatch = make_rectangle(
        name="Primary Swatch",
        fills=[make_solid_fill(variable_id="var_primary")]
    )
    tokens_page = make_canvas(name="Tokens", children=[swatch])
    # Style metadata — text styles used on the Cover page
    _, title_style = make_style(style_id="style_title", name="heading-01",
                                  style_type="TEXT", published=True)
    _, body_style = make_style(style_id="style_body", name="body-01",
                                 style_type="TEXT", published=True)
    return make_file_fixture(
        name="Hemantix Foundations",
        pages=[cover, tokens_page],
        styles={"style_title": title_style, "style_body": body_style},
        variable_collections={coll_id: coll},
        variables={var_id: var},
    )


def make_foundations_no_cover() -> dict:
    """Foundations file missing the Cover page — should fail G10."""
    reset_id_counter()
    page = make_canvas(name="Tokens", children=[])
    return make_file_fixture(name="Foundations No Cover", pages=[page])


def make_foundations_orphan_styles() -> dict:
    """Foundations file with two styles, only one referenced — fails G3."""
    reset_id_counter()
    referenced_sid, ref_style = make_style(style_id="style_used", name="body-01",
                                             style_type="TEXT")
    orphan_sid, orphan_style = make_style(style_id="style_orphan", name="legacy-display",
                                            style_type="TEXT")
    cover = make_canvas(name="Cover", children=[
        make_text_node(text="Brand · Version: 1.0.0 · License: MIT · Contact: a@b.com",
                        style_id=referenced_sid)
    ])
    return make_file_fixture(
        name="Foundations Orphan",
        pages=[cover],
        styles={referenced_sid: ref_style, orphan_sid: orphan_style}
    )


def make_foundations_missing_aliases() -> dict:
    """Foundations file with an unresolved local variable alias — fails G4."""
    reset_id_counter()
    coll_id, coll = make_variable_collection(collection_id="varcoll_color")
    semantic_id, semantic_var = make_variable(
        variable_id="var_semantic",
        name="color/semantic/background",
        collection_id=coll_id,
        values_by_mode={"varcoll_color_mode_0": alias_value("var_NONEXISTENT")},
        resolved_type="COLOR"
    )
    return make_file_fixture(
        name="Foundations Broken Alias",
        variable_collections={coll_id: coll},
        variables={semantic_id: semantic_var},
    )


def make_foundations_unpublished_style() -> dict:
    """Foundations file with an unpublished local style outside Candidates — fails G12."""
    reset_id_counter()
    sid, style = make_style(style_id="style_unpub", name="experimental-display",
                              style_type="TEXT", published=False)
    cover = make_canvas(name="Cover", children=[
        make_text_node(text="DS · v1.0 · MIT · a@b.com", style_id=sid)
    ])
    return make_file_fixture(name="Foundations Unpub", pages=[cover],
                              styles={sid: style})


def make_components_no_cc_badges() -> dict:
    """Components file with components lacking Code Connect badges — fails G17 (info)."""
    reset_id_counter()
    cid, cmeta = make_component(component_id="comp_button", name="Button",
                                 description="A clickable element for primary actions.")
    return make_file_fixture(name="Components", components={cid: cmeta})


def make_components_with_cc_badges() -> dict:
    """Components file with badged descriptions — passes G17."""
    reset_id_counter()
    cid, cmeta = make_component(
        component_id="comp_button",
        name="Button",
        description="🟢 A clickable element for primary actions. Code Connect: linked."
    )
    return make_file_fixture(name="Components Badged", components={cid: cmeta})


def make_minimal_components() -> dict:
    """A minimal Components file with valid components."""
    reset_id_counter()
    cid, cmeta = make_component(
        component_id="comp_btn",
        name="Button",
        description="🟢 Primary action button with size/state variants. Carbon-style API."
    )
    return make_file_fixture(name="Hemantix Components", components={cid: cmeta})


# ----------------------------------------------------------------------------
# Sprint 2: Variant-matrix + naming fixtures
# ----------------------------------------------------------------------------

def make_components_complete_variant_matrix() -> dict:
    """Components file with a fully-populated variant matrix (passes G7)."""
    reset_id_counter()
    set_id, set_meta = make_component_set(
        set_id="set_button",
        name="Button",
        description="Primary action button with type/size variants."
    )
    # 2 × 2 = 4 children, fully covered
    components: dict[str, dict] = {}
    for type_val in ("primary", "secondary"):
        for size_val in ("sm", "md"):
            cid, cmeta = make_component(
                name=f"type={type_val}, size={size_val}",
                component_set_id=set_id,
            )
            components[cid] = cmeta
    return make_file_fixture(
        name="Hemantix Components",
        components=components,
        component_sets={set_id: set_meta}
    )


def make_components_incomplete_variant_matrix() -> dict:
    """Components file missing 1 of 4 combinations (fails G7)."""
    reset_id_counter()
    set_id, set_meta = make_component_set(
        set_id="set_button",
        name="Button",
        description="Button with gap."
    )
    # 3 children — missing (secondary, md)
    components: dict[str, dict] = {}
    for type_val, size_val in [("primary", "sm"), ("primary", "md"), ("secondary", "sm")]:
        cid, cmeta = make_component(
            name=f"type={type_val}, size={size_val}",
            component_set_id=set_id,
        )
        components[cid] = cmeta
    return make_file_fixture(
        name="Hemantix Components Gap",
        components=components,
        component_sets={set_id: set_meta}
    )


def make_components_disabled_marker() -> dict:
    """Components file marking the missing combination as Disabled (passes G7)."""
    reset_id_counter()
    set_id, set_meta = make_component_set(
        set_id="set_button",
        name="Button",
        description="Button.\n\nDisabled:\n- type=secondary, size=md"
    )
    components: dict[str, dict] = {}
    for type_val, size_val in [("primary", "sm"), ("primary", "md"), ("secondary", "sm")]:
        cid, cmeta = make_component(
            name=f"type={type_val}, size={size_val}",
            component_set_id=set_id,
        )
        components[cid] = cmeta
    return make_file_fixture(
        name="Hemantix Components Disabled",
        components=components,
        component_sets={set_id: set_meta}
    )


def make_components_bad_naming_carbon() -> dict:
    """Components file with non-Carbon names (snake_case, lowercase) — fails G8."""
    reset_id_counter()
    cid, cmeta = make_component(
        component_id="comp_btn",
        name="primary_button",   # snake_case — not Carbon PascalCase
        description="🟢 Test."
    )
    return make_file_fixture(
        name="Bad Naming",
        components={cid: cmeta}
    )


def make_components_bad_variant_property_carbon() -> dict:
    """ComponentSet with PascalCase variant key (Carbon expects camelCase) — fails G9."""
    reset_id_counter()
    set_id, set_meta = make_component_set(
        set_id="set_btn",
        name="Button"
    )
    components = {}
    for size_val in ("Small", "Medium"):  # value is PascalCase, not lowercase
        cid, cmeta = make_component(
            name=f"Size={size_val}",        # key is PascalCase, not camelCase
            component_set_id=set_id
        )
        components[cid] = cmeta
    return make_file_fixture(
        name="Bad Variant Naming",
        components=components,
        component_sets={set_id: set_meta}
    )


def make_components_with_section_header() -> dict:
    """A Components page with a section header frame at top (passes G11)."""
    reset_id_counter()
    header = make_frame(name="Section Header", children=[
        make_text_node(text="Actions")
    ])
    actions_page = make_canvas(name="Actions", children=[header])
    return make_file_fixture(name="Comp With Header", pages=[actions_page])


def make_components_no_section_header() -> dict:
    """A Components page with no header (fails G11)."""
    reset_id_counter()
    # A plain frame without header signals
    decoy = make_frame(name="just-a-frame", children=[])
    actions_page = make_canvas(name="Actions", children=[decoy])
    return make_file_fixture(name="Comp No Header", pages=[actions_page])


def make_components_clean_instance() -> dict:
    """Components page with an instance carrying only safe overrides (passes G19)."""
    reset_id_counter()
    instance = {
        "id": fresh_id("instance"),
        "type": "INSTANCE",
        "name": "Button instance",
        "overrides": [
            {"id": "child1", "overriddenFields": ["characters"]},      # text override OK
            {"id": "child2", "overriddenFields": ["componentProperties"]}  # variant pick OK
        ]
    }
    page = make_canvas(name="Examples", children=[instance])
    return make_file_fixture(name="Clean Instance", pages=[page])


def make_components_detached_instance() -> dict:
    """Components page with an instance carrying a paint override (fails G19)."""
    reset_id_counter()
    instance = {
        "id": fresh_id("instance"),
        "type": "INSTANCE",
        "name": "Button hacked",
        "overrides": [
            {"id": "child1", "overriddenFields": ["fills", "strokes"]}  # detached!
        ]
    }
    page = make_canvas(name="Examples", children=[instance])
    return make_file_fixture(name="Detached Instance", pages=[page])


# ----------------------------------------------------------------------------
# Sprint 3: Icons + keywords + effects fixtures
# ----------------------------------------------------------------------------

def _make_icon_node(*, node_type: str, name: str, size: int = 24,
                     non_square: bool = False) -> dict:
    """Build a node with absoluteBoundingBox for icon-geometry testing."""
    h = size + 4 if non_square else size
    return {
        "id": fresh_id(node_type.lower()),
        "type": node_type,
        "name": name,
        "absoluteBoundingBox": {"x": 0, "y": 0, "width": size, "height": h},
    }


def make_icons_all_components() -> dict:
    """Icons file where every icon is a COMPONENT at canonical size (passes G14, G15)."""
    reset_id_counter()
    icons_page = make_canvas(name="Icons", children=[
        _make_icon_node(node_type="COMPONENT", name="Icon / Add", size=24),
        _make_icon_node(node_type="COMPONENT", name="Icon / Close", size=24),
    ])
    # Register the COMPONENT nodes in the components dict too
    components = {}
    for node in icons_page["children"]:
        components[node["id"]] = {
            "key": f"key_{node['id']}",
            "name": node["name"],
            "description": "🟢 Icon. Keywords: icon, add, plus, action, ui",
        }
    return make_file_fixture(
        name="Hemantix Icons",
        pages=[icons_page],
        components=components,
    )


def make_icons_raw_vectors() -> dict:
    """Icons file containing raw VECTOR nodes outside any component (fails G14)."""
    reset_id_counter()
    icons_page = make_canvas(name="Icons", children=[
        _make_icon_node(node_type="VECTOR", name="add-glyph", size=24),
        _make_icon_node(node_type="VECTOR", name="close-glyph", size=24),
    ])
    return make_file_fixture(name="Bad Icons", pages=[icons_page])


def make_icons_wrong_size() -> dict:
    """Icons file with off-grid icon dimensions (fails G15)."""
    reset_id_counter()
    icons_page = make_canvas(name="Icons", children=[
        # 22×22 is off-grid (closest canonical is 20 or 24, beyond ±1 tolerance)
        _make_icon_node(node_type="COMPONENT", name="Icon / Custom", size=22),
    ])
    components = {}
    for node in icons_page["children"]:
        components[node["id"]] = {
            "key": f"key_{node['id']}",
            "name": node["name"],
            "description": "🟢 Custom-size icon. Keywords: icon, custom, off, grid",
        }
    return make_file_fixture(
        name="Off-grid Icons",
        pages=[icons_page],
        components=components,
    )


def make_components_with_keywords() -> dict:
    """Components file where every component declares ≥4 keywords (passes G6)."""
    reset_id_counter()
    cid, cmeta = make_component(
        component_id="comp_btn",
        name="Button",
        description=(
            "🟢 Primary action button with size/state variants.\n"
            "Keywords: button, action, cta, submit, primary"
        )
    )
    return make_file_fixture(name="Comp With Keywords", components={cid: cmeta})


def make_components_no_keywords() -> dict:
    """Components file lacking the Keywords: line (fails G6)."""
    reset_id_counter()
    cid, cmeta = make_component(
        component_id="comp_btn",
        name="Button",
        description="🟢 A clickable element for primary actions. No keyword line."
    )
    return make_file_fixture(name="Comp No Keywords", components={cid: cmeta})


def make_foundations_with_elevation_effects() -> dict:
    """Foundations file with proper elevation-named effect styles (passes G13)."""
    reset_id_counter()
    coll_id, coll = make_variable_collection(collection_id="varcoll_color")
    var_id, var = make_variable(
        variable_id="var_primary",
        name="color/primary",
        collection_id=coll_id,
        values_by_mode={"varcoll_color_mode_0": {"r": 0, "g": 0.4, "b": 0.8, "a": 1}}
    )
    # Effect style with elevation-canonical name
    sid_e1, style_e1 = make_style(
        style_id="style_elev1",
        name="elevation/1",
        style_type="EFFECT",
        published=True,
    )
    # Surface frame that references the effect (so G13's reference check passes)
    surface = {
        "id": fresh_id("frame"),
        "type": "FRAME",
        "name": "Surface",
        "styles": {"effect": "style_elev1"},
    }
    cover = make_canvas(name="Cover", children=[
        make_text_node(text="DS · v1.0.0 · License: MIT · contact: a@b.com"),
        surface
    ])
    return make_file_fixture(
        name="Foundations Elevation",
        pages=[cover],
        styles={"style_elev1": style_e1},
        variable_collections={coll_id: coll},
        variables={var_id: var}
    )


def make_foundations_ambiguous_effects() -> dict:
    """Foundations file with ambiguous effect-style name (fails G13)."""
    reset_id_counter()
    sid, style = make_style(
        style_id="style_shadow1",
        name="shadow-1",        # not elevation-named, not decorative
        style_type="EFFECT",
        published=True,
    )
    cover = make_canvas(name="Cover", children=[
        make_text_node(text="DS · v1.0 · MIT · a@b.com")
    ])
    return make_file_fixture(
        name="Foundations Bad Effects",
        pages=[cover],
        styles={sid: style}
    )


# ----------------------------------------------------------------------------
# Composite "pristine" fixtures — for end-to-end happy-path scenarios
#
# These build on the per-gate base fixtures and add the small extras
# (section headers, component keywords) that the simpler base fixtures
# omit. They exist specifically so test_publish_audit_e2e.py can drive
# a multi-file library where every gate is genuinely green.
# ----------------------------------------------------------------------------

def _attach_section_header(page: dict, *, title: str = "Section",
                            style_id: str = "style_title") -> None:
    """Prepend a header frame to a canvas page's children list (in place).

    The text node receives ``style_id`` so it satisfies G2 (every text
    node references a text style). Callers must ensure that style_id is
    registered in the surrounding fixture's ``styles`` map.
    """
    header = make_frame(name=f"{title} Header", children=[
        make_text_node(text=title, style_id=style_id)
    ])
    page.setdefault("children", []).insert(0, header)


def make_pristine_foundations() -> dict:
    """A Foundations file that passes every gate including G2 (text styles)
    and G11 (section headers).

    Builds on ``make_minimal_valid_foundations`` (which already defines
    ``style_title``) and adds a section-header frame to the Tokens page.
    """
    fixture = make_minimal_valid_foundations()
    # Find the Tokens page and prepend a section header that uses the
    # already-published style_title text style.
    for page in fixture["document"]["children"]:
        if page.get("name") == "Tokens":
            _attach_section_header(page, title="Tokens", style_id="style_title")
    return fixture


def make_pristine_components() -> dict:
    """A Components file that passes every gate including G6 (keywords),
    G2 (text styles), and G11 (section headers).

    Builds a Button component with a Code Connect badge, a keyword line,
    a section header on the canvas it lives on, and the published text
    style the header references. Component is Carbon-PascalCase so G8
    also passes when the registry's naming_convention is ``carbon``.
    """
    reset_id_counter()
    cid, cmeta = make_component(
        component_id="comp_btn",
        name="Button",
        description=(
            "🟢 Primary action button with size and state variants.\n"
            "Keywords: button, action, cta, submit, primary"
        )
    )
    _, header_style = make_style(style_id="style_h2", name="heading-02",
                                  style_type="TEXT", published=True)
    header = make_frame(name="Actions Header", children=[
        make_text_node(text="Actions", style_id="style_h2")
    ])
    actions_page = make_canvas(name="Actions", children=[header])
    return make_file_fixture(
        name="Pristine Components",
        pages=[actions_page],
        components={cid: cmeta},
        styles={"style_h2": header_style},
    )


def make_pristine_patterns() -> dict:
    """A Patterns file that passes every gate. Same shape as components but
    a different file role."""
    reset_id_counter()
    cid, cmeta = make_component(
        component_id="comp_card",
        name="Card",
        description=(
            "🟢 Generic card pattern for content surfaces.\n"
            "Keywords: card, container, surface, panel"
        )
    )
    _, header_style = make_style(style_id="style_h2", name="heading-02",
                                  style_type="TEXT", published=True)
    header = make_frame(name="Patterns Header", children=[
        make_text_node(text="Patterns", style_id="style_h2")
    ])
    page = make_canvas(name="Patterns", children=[header])
    return make_file_fixture(
        name="Pristine Patterns",
        pages=[page],
        components={cid: cmeta},
        styles={"style_h2": header_style},
    )


def make_pristine_icons() -> dict:
    """An Icons file where every icon is a COMPONENT at a canonical size,
    each component declares ≥4 keywords (G6), and the icon canvas has a
    section header so G11 passes too."""
    fixture = make_icons_all_components()
    # Inject the heading style used by the section header.
    _, header_style = make_style(style_id="style_h2", name="heading-02",
                                  style_type="TEXT", published=True)
    fixture.setdefault("styles", {})["style_h2"] = header_style
    for page in fixture["document"]["children"]:
        if page.get("name", "").lower() in ("icons", "icon"):
            _attach_section_header(page, title="Icons", style_id="style_h2")
    # Patch every icon component's description to satisfy G6 (keywords)
    # and G5 (≥30 char description).
    for comp in fixture.get("components", {}).values():
        existing = comp.get("description", "")
        comp["description"] = (
            f"{existing} Icon glyph used throughout the product UI.\n"
            "Keywords: icon, glyph, ui, navigation"
        ).strip()
    return fixture
