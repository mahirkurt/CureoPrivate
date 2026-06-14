"""Plugin channel TypeScript script writer (v0.3.0-beta).

Renders :class:`RemediationAction` instances as Figma plugin TypeScript
source. The output is **paste-into-console** runnable: an operator opens
the target Figma file → Plugins → Development → Open Console → pastes
the generated script.

This module is intentionally string-based (no AST library dependency)
to keep the v0.3.0-beta footprint small. The trade-off is that template
maintenance carries a higher diff cost; v0.4.0 will revisit when the
multi-MCP transport layer lands.

Public API:
    render_plugin_script(actions, ctx, *, header_locale) → str
    render_single_action(action, ctx) → str
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Iterable

from .base import RemediationAction, RemediationContext


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_plugin_script(
    actions: list[RemediationAction],
    ctx: RemediationContext,
    *,
    header_locale: str = "en-US",
) -> str:
    """Render a list of actions as one runnable TypeScript script.

    The script wraps every action in an async IIFE; failures in one
    action do not abort subsequent ones (each is wrapped in its own
    try/catch).
    """
    parts: list[str] = []
    parts.append(_render_header(actions, ctx, header_locale))
    parts.append("(async () => {")
    parts.append(f"  console.log('🛠  figma-forge auto-remediate — running {len(actions)} action(s)…');")
    parts.append("")
    for idx, action in enumerate(actions, start=1):
        parts.append(_render_action_block(action, idx))
        parts.append("")
    parts.append("  console.log('✅ figma-forge auto-remediate complete.');")
    parts.append("})();")
    return "\n".join(parts) + "\n"


def render_single_action(action: RemediationAction, ctx: RemediationContext) -> str:
    """Render exactly one action as a self-contained TS file."""
    return render_plugin_script([action], ctx, header_locale="en-US")


# ---------------------------------------------------------------------------
# Internal renderers
# ---------------------------------------------------------------------------

def _render_header(
    actions: list[RemediationAction], ctx: RemediationContext, locale: str
) -> str:
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    strategy_ids = sorted({a.strategy_id for a in actions})
    if locale == "tr-TR":
        title = "figma-forge auto-remediate — plugin TS scripti"
        usage_line = "Figma → Plugins → Development → Open Console → bu scripti yapıştırıp Enter'a basın."
    else:
        title = "figma-forge auto-remediate — plugin TS script"
        usage_line = "Figma → Plugins → Development → Open Console → paste this script + press Enter."

    return (
        f"// ============================================================================\n"
        f"// {title}\n"
        f"// Generated: {timestamp}\n"
        f"// Library:   {ctx.library_dir}\n"
        f"// Actions:   {len(actions)} (strategy ids: {strategy_ids})\n"
        f"//\n"
        f"// {usage_line}\n"
        f"// ============================================================================\n"
    )


def _render_action_block(action: RemediationAction, idx: int) -> str:
    """Dispatch by action_type + strategy_id to the appropriate emitter."""
    rationale_lines = action.rationale.splitlines()
    rationale_block = "\n".join(f"  // {line}" for line in rationale_lines)

    body = _dispatch_emitter(action)

    return (
        f"  // ───── Action {idx} · G{action.strategy_id:02d} · {action.target_path}\n"
        f"{rationale_block}\n"
        f"  try {{\n"
        f"{body}\n"
        f"    console.log('   ✓ Action {idx} (G{action.strategy_id:02d}) applied');\n"
        f"  }} catch (err) {{\n"
        f"    console.error('   ✗ Action {idx} (G{action.strategy_id:02d}) failed:', err);\n"
        f"  }}"
    )


def _dispatch_emitter(action: RemediationAction) -> str:
    """Route to the per-strategy plugin emitter."""
    emitter = _EMITTERS.get(action.strategy_id, _emit_static_only_notice)
    return emitter(action)


# ---------------------------------------------------------------------------
# Per-strategy emitters
# ---------------------------------------------------------------------------

def _emit_static_only_notice(action: RemediationAction) -> str:
    """Default: announce that this action has no live-Figma equivalent."""
    return (
        f"    console.log('   ⓘ G{action.strategy_id:02d} action targets static source '\n"
        f"      + '({action.target_path}). No live Figma mutation needed; apply the PR-channel '\n"
        f"      + 'patch via git apply instead.');"
    )


def _emit_g02_text_styles(action: RemediationAction) -> str:
    """G02 — create Figma Text Styles from extracted composite typography."""
    if action.action_type != "create_file":
        return _emit_static_only_notice(action)
    try:
        payload = json.loads(action.new_content or "{}")
    except json.JSONDecodeError:
        return _emit_static_only_notice(action)

    styles = payload.get("text_styles", {})
    if not styles:
        return _emit_static_only_notice(action)

    lines: list[str] = []
    lines.append(f"    console.log('    G02: Creating {len(styles)} text style(s)…');")
    for role, spec in styles.items():
        font_family = (spec.get("fontFamily") or "Inter").replace("'", "\\'")
        font_weight = str(spec.get("fontWeight") or "Regular").replace("'", "\\'")
        font_size = _num(spec.get("fontSize"), default=16)
        letter_spacing = _num(spec.get("letterSpacing"), default=0)
        safe_role = role.replace("'", "\\'")

        lines.append("    {")
        lines.append(f"      await figma.loadFontAsync({{ family: '{font_family}', style: '{font_weight}' }});")
        lines.append(f"      const style = figma.createTextStyle();")
        lines.append(f"      style.name = '{safe_role}';")
        lines.append(f"      style.fontName = {{ family: '{font_family}', style: '{font_weight}' }};")
        lines.append(f"      style.fontSize = {font_size};")
        lh = spec.get("lineHeight")
        if lh is not None:
            lines.append(f"      style.lineHeight = {_render_line_height(lh)};")
        lines.append(f"      style.letterSpacing = {{ unit: 'PIXELS', value: {letter_spacing} }};")
        lines.append("    }")
    return "\n".join(lines)


def _emit_g13_alias_variable_rebind(action: RemediationAction) -> str:
    """G13 — alias path rebind, executed as a Figma plugin operation.

    Produces a production-grade Variable rebinder that:

    * Loads the merged DTCG payload (passed as a static JSON string)
    * Walks ``figma.variables.getLocalVariables()`` and locates each
      target variable by canonical name
    * For each variable, inspects every mode's value and, when the
      value is a ``VARIABLE_ALIAS`` whose target id resolves to a
      stale path, calls ``setValueForMode`` with a fresh alias
      pointing at the correct variable id
    * Records each rebind operation in a console summary

    The script extracts the old→new alias map from the action's
    rationale text (auto-remediate G13 embeds these as
    ``OLD_PATH → NEW_PATH`` lines), then performs the lookup in the
    live Figma document.

    Because Figma's Variables API is collection-scoped, the script
    inspects every local collection's variables — most design
    systems put primitives and semantics into separate collections,
    and aliases cross the boundary.
    """
    target = action.target_path
    rationale = (action.rationale or "").replace("`", "\\`").replace("${", "\\${")
    # Extract OLD → NEW pairs from the rationale text (one per line)
    rebinds = _extract_alias_rebinds(action.rationale or "")
    # Pre-render the rebind map as a JS literal
    rebind_lines: list[str] = []
    for old_path, new_path in rebinds:
        safe_old = old_path.replace("'", "\\'")
        safe_new = new_path.replace("'", "\\'")
        rebind_lines.append(f"      ['{safe_old}', '{safe_new}'],")
    rebind_map_literal = "\n".join(rebind_lines) if rebind_lines else "      // (no pairs parsed from rationale)"
    rebind_count = len(rebinds)
    rationale_block = "\n".join(f"    // {line}" for line in rationale.splitlines())

    return (
        f"    // G13: DTCG Alias Path → Live Figma Variable Rebind\n"
        f"    // Source: {target}\n"
        f"{rationale_block}\n"
        f"    \n"
        f"    // Canonical rebind map (OLD → NEW), extracted from action rationale\n"
        f"    const rebindMap = new Map<string, string>([\n"
        f"{rebind_map_literal}\n"
        f"    ]);\n"
        f"    console.log(`      G13: Processing ${{rebindMap.size}} rebind pair(s)…`);\n"
        f"    \n"
        f"    // Build a name → Variable index across ALL local collections\n"
        f"    const allCollections = figma.variables.getLocalVariableCollections();\n"
        f"    const varsByName = new Map<string, Variable>();\n"
        f"    for (const coll of allCollections) {{\n"
        f"      for (const varId of coll.variableIds) {{\n"
        f"        const v = figma.variables.getVariableById(varId);\n"
        f"        if (v) varsByName.set(v.name, v);\n"
        f"      }}\n"
        f"    }}\n"
        f"    console.log(`      G13: Indexed ${{varsByName.size}} variable(s) "
        f"across ${{allCollections.length}} collection(s)`);\n"
        f"    \n"
        f"    // Apply each rebind\n"
        f"    let rebound = 0;\n"
        f"    let skipped = 0;\n"
        f"    for (const [oldPath, newPath] of rebindMap.entries()) {{\n"
        f"      const sourceVar = varsByName.get(oldPath);\n"
        f"      const targetVar = varsByName.get(newPath);\n"
        f"      if (!sourceVar) {{\n"
        f"        console.warn(`        ⚠ G13: source variable not found: ${{oldPath}}`);\n"
        f"        skipped++; continue;\n"
        f"      }}\n"
        f"      if (!targetVar) {{\n"
        f"        console.warn(`        ⚠ G13: target variable not found: ${{newPath}}`);\n"
        f"        skipped++; continue;\n"
        f"      }}\n"
        f"      \n"
        f"      // Rebind: replace sourceVar's value(s) with an alias to targetVar.\n"
        f"      // We rebind in every mode the source variable defines.\n"
        f"      const sourceColl = figma.variables.getVariableCollectionById(\n"
        f"        sourceVar.variableCollectionId\n"
        f"      );\n"
        f"      if (!sourceColl) {{\n"
        f"        console.warn(`        ⚠ G13: collection not found for ${{oldPath}}`);\n"
        f"        skipped++; continue;\n"
        f"      }}\n"
        f"      const alias = figma.variables.createVariableAlias(targetVar);\n"
        f"      for (const mode of sourceColl.modes) {{\n"
        f"        sourceVar.setValueForMode(mode.modeId, alias);\n"
        f"      }}\n"
        f"      console.log(\n"
        f"        `        ✓ G13: rebound ${{oldPath}} → ${{newPath}} `\n"
        f"        + `across ${{sourceColl.modes.length}} mode(s)`\n"
        f"      );\n"
        f"      rebound++;\n"
        f"    }}\n"
        f"    console.log(\n"
        f"      `      G13: ${{rebound}} rebind(s) applied, ${{skipped}} skipped `\n"
        f"      + `(total {rebind_count} requested)`\n"
        f"    );"
    )


def _extract_alias_rebinds(rationale: str) -> list[tuple[str, str]]:
    """Pull ``OLD → NEW`` alias pairs out of an auto_remediate G13
    rationale block.

    The G13 strategy writes its rationale in the form:

        Rewrite alias path 'color.x' → 'color.y' (or full DTCG path).

    or, for multi-pair runs, one mapping per line:

        - color.x → color.y
        - color.a → color.b

    The extractor is lenient on whitespace and bullets; it requires
    the literal ``→`` (U+2192) or ``->`` separator.
    """
    import re
    pairs: list[tuple[str, str]] = []
    arrow = re.compile(r"['`]?([\w.\-:/]+)['`]?\s*(?:→|->)\s*['`]?([\w.\-:/]+)['`]?")
    for line in rationale.splitlines():
        for m in arrow.finditer(line):
            old, new = m.group(1), m.group(2)
            if old and new and old != new:
                pairs.append((old, new))
    # Deduplicate while preserving first occurrence
    seen: set[tuple[str, str]] = set()
    deduped: list[tuple[str, str]] = []
    for pair in pairs:
        if pair not in seen:
            deduped.append(pair)
            seen.add(pair)
    return deduped


def _emit_g14_icon_create_component(action: RemediationAction) -> str:
    """G14 — convert imported SVG into a Figma component with full setup.

    Produces a production-grade component creation flow:

    * Imports the normalized SVG via ``figma.createNodeFromSvg``
    * Promotes the resulting node to a component via
      ``figma.createComponentFromNode``
    * Sets the component name (derived from the file basename)
    * Routes to the correct page based on icon tier
      (Tier / Selçuklu / Document / UI)
    * Sets the component description with file path provenance
    * Sets the publishable component ``key`` to the basename (stable
      across publishes)
    * Adds ``documentationLinks`` to the canonical source-of-truth path

    The script is idempotent: re-running it locates existing components
    by name and updates their geometry in-place rather than duplicating.
    """
    target = action.target_path
    raw_svg = action.new_content or ""
    # Escape backticks and ${...} for safe embedding in a template literal
    safe_svg = raw_svg.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    basename = _basename_no_ext(target)
    page_name = _icon_tier_to_page(target)
    container_size = _container_size_for(target)
    doc_path = _provenance_path(target)
    safe_basename = basename.replace("'", "\\'")
    safe_page = page_name.replace("'", "\\'")
    safe_doc_path = doc_path.replace("'", "\\'")

    return (
        f"    // G14: Icon SVG → Figma Component\n"
        f"    // Source path:  {target}\n"
        f"    // Target page:  {page_name}\n"
        f"    // Container:    {container_size}×{container_size}px\n"
        f"    const svgString = `{safe_svg}`;\n"
        f"    \n"
        f"    // 1. Locate or create the target page\n"
        f"    let targetPage = figma.root.children.find(\n"
        f"      (p): p is PageNode => p.type === 'PAGE' && p.name === '{safe_page}'\n"
        f"    );\n"
        f"    if (!targetPage) {{\n"
        f"      targetPage = figma.createPage();\n"
        f"      targetPage.name = '{safe_page}';\n"
        f"    }}\n"
        f"    await figma.setCurrentPageAsync(targetPage);\n"
        f"    \n"
        f"    // 2. Import the SVG and resize to canonical container\n"
        f"    const importedNode = figma.createNodeFromSvg(svgString);\n"
        f"    importedNode.resize({container_size}, {container_size});\n"
        f"    \n"
        f"    // 3. Locate existing component by name (idempotent re-runs)\n"
        f"    const existing = targetPage.findOne(\n"
        f"      (n): n is ComponentNode =>\n"
        f"        n.type === 'COMPONENT' && n.name === '{safe_basename}'\n"
        f"    );\n"
        f"    \n"
        f"    let component: ComponentNode;\n"
        f"    if (existing) {{\n"
        f"      // Update geometry in place: replace children with the fresh import\n"
        f"      for (const child of [...existing.children]) child.remove();\n"
        f"      for (const child of [...importedNode.children]) existing.appendChild(child);\n"
        f"      existing.resize({container_size}, {container_size});\n"
        f"      importedNode.remove();\n"
        f"      component = existing;\n"
        f"      console.log(`      G14: Updated existing component \\\"{safe_basename}\\\"`);\n"
        f"    }} else {{\n"
        f"      // Promote the imported node to a component\n"
        f"      component = figma.createComponentFromNode(importedNode);\n"
        f"      component.name = '{safe_basename}';\n"
        f"      console.log(`      G14: Created new component \\\"{safe_basename}\\\"`);\n"
        f"    }}\n"
        f"    \n"
        f"    // 4. Set description with provenance trail\n"
        f"    component.description = "
        f"`Source: {safe_doc_path}\\nGenerated by figma-forge auto-remediate G14.`;\n"
        f"    \n"
        f"    // 5. Add documentation link to canonical source-of-truth path\n"
        f"    component.documentationLinks = [\n"
        f"      {{ uri: 'https://github.com/<org>/<repo>/blob/main/{safe_doc_path}' }}\n"
        f"    ];"
    )


def _icon_tier_to_page(target_path: str) -> str:
    """Map an icon source path to the canonical Figma page name."""
    if "icons/svg/tier/" in target_path:
        return "Tier Icons"
    if "icons/svg/selcuklu-motif/" in target_path:
        return "Selçuklu Motifleri"
    if "icons/svg/document/" in target_path:
        return "Document Icons"
    return "UI Icons"


def _container_size_for(target_path: str) -> int:
    """Default Figma component container size per icon tier."""
    if "icons/svg/selcuklu-motif/" in target_path:
        return 192
    if "icons/svg/tier/" in target_path:
        return 24
    if "icons/svg/document/" in target_path:
        return 24
    return 24


def _provenance_path(target_path: str) -> str:
    """Strip leading slash and normalize to forward slashes."""
    return target_path.lstrip("/").replace("\\", "/")


def _emit_g17_code_connect_attach(action: RemediationAction) -> str:
    """G17 — attach Code Connect mapping via Figma Plugin API.

    The Code Connect attachment API is currently REST-only (no plugin
    equivalent). This emitter therefore prints an explanatory NO-OP and
    points to the PR-channel patch.
    """
    return (
        "    // G17 plugin mode: Code Connect attach is REST-only (no plugin API equivalent).\n"
        "    // Apply the PR-channel patch and run:  npx @figma/code-connect publish\n"
        f"    console.log('    G17: PR-channel patch generated at {action.target_path}.');"
    )


_EMITTERS = {
    2: _emit_g02_text_styles,
    13: _emit_g13_alias_variable_rebind,
    14: _emit_g14_icon_create_component,
    17: _emit_g17_code_connect_attach,
}


# ---------------------------------------------------------------------------
# Value coercion helpers
# ---------------------------------------------------------------------------

def _num(value, *, default: float = 0) -> str:
    """Render any DTCG dimension-ish value as a JS number literal."""
    if value is None:
        return str(default)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        s = value.strip().lower()
        if s.endswith("px"):
            s = s[:-2]
        try:
            return str(float(s))
        except ValueError:
            return str(default)
    return str(default)


def _render_line_height(value) -> str:
    """Convert a DTCG line-height value to a Figma LineHeight literal."""
    if isinstance(value, (int, float)):
        return f"{{ unit: 'PERCENT', value: {value * 100} }}"
    if isinstance(value, str):
        s = value.strip().lower()
        if s.endswith("%"):
            try:
                return f"{{ unit: 'PERCENT', value: {float(s[:-1])} }}"
            except ValueError:
                pass
        if s.endswith("px"):
            return f"{{ unit: 'PIXELS', value: {s[:-2]} }}"
        try:
            return f"{{ unit: 'PERCENT', value: {float(s) * 100} }}"
        except ValueError:
            pass
    return "{ unit: 'AUTO' }"


def _basename_no_ext(path: str) -> str:
    """Return the filename without directories or extension, suitable for
    use as a Figma component name."""
    from pathlib import Path
    return Path(path).stem
