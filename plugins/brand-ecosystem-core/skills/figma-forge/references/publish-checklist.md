# Publish Checklist — 19 Gates

`PUBLISH_AUDIT` mode runs all 19 gates against a Figma file (or set of files) before recommending publish. Each gate has a severity, a check methodology, and a remediation path.

## Severity legend

- **error** — Must fix before publishing. Library will be unusable or unsafe for consumers.
- **warn** — Should fix; library will work but quality is degraded.
- **info** — Optional improvement; no functional impact.

## The 19 gates

### Gate 1 — All paints come from a variable

**Severity:** error
**Check:** For every fillable node in the file, enumerate `fills[].boundVariables.color`. If `boundVariables.color` is missing on any solid fill outside the Foundations swatch demos, fail.
**Why:** Hard-coded colors break theme support. Consumers cannot switch modes (Light/Dark) reliably.
**Remediation:** Iterate failing nodes; rebind to the appropriate variable. If no variable exists, add one to Foundations first.

### Gate 2 — All text uses a text style

**Severity:** error
**Check:** For every text node, enumerate `textStyleId`. If missing or empty (i.e., detached typography), fail.
**Why:** Detached typography breaks type-ramp consistency and prevents font updates from propagating.
**Remediation:** Apply the appropriate text style. If style missing, create in Foundations first.

### Gate 3 — No orphan styles

**Severity:** warn
**Check:** For every published paint/text/effect style, search the file for at least one reference. If zero references, mark orphan.
**Why:** Orphan styles bloat the published library and confuse consumers who see them in the Assets panel.
**Remediation:** Delete unused styles, or apply them to relevant nodes if intent is to keep them.

### Gate 4 — No missing variable references

**Severity:** error
**Check:** For every variable alias (a variable whose value is `{type: VARIABLE_ALIAS, id: <other_var_id>}`), verify the target variable exists in the file or in linked libraries.
**Why:** Missing alias targets render as the fallback default and quietly degrade the system.
**Remediation:** Either restore the missing target variable, or rebind the alias to an existing variable.

### Gate 5 — All components have descriptions

**Severity:** warn
**Check:** For every component in the Components/Patterns files, verify `description` is non-empty and has at least 30 characters.
**Why:** Descriptions appear in Figma's Assets panel and dev mode; missing descriptions hurt discoverability.
**Remediation:** Author a 1–2 sentence description per component, covering "what it is" and "when to use it".

### Gate 6 — All components have keywords

**Severity:** warn
**Check:** For every component, verify the component's documented keyword list is non-empty.
**Why:** Keywords drive search in the Assets panel; without them, consumers cannot find components.
**Remediation:** Add 4–8 keywords per component (name + synonyms + family + use-case verbs).

### Gate 7 — Every variant axis is fully populated

**Severity:** error
**Check:** For each component set, enumerate variant axes and verify the Cartesian product of values is fully represented as instances (no gaps in the variant matrix).
**Why:** Gaps in the variant matrix mean some consumer-selected combinations resolve to the "next closest" variant unpredictably.
**Remediation:** Add the missing variant instances. If a combination is genuinely invalid, document via `disabledVariants` extension or remove the axis.

### Gate 8 — Component naming follows convention

**Severity:** warn
**Check:** For every component name, verify it matches the convention selected in `library-registry.json` (Carbon/Material/BEM/Custom). Specifically:
- Carbon/Material: `PascalCase` block names, optionally `Family / Block` for grouping
- BEM: `block`, `block__element`, `block__element--modifier`
- Custom: literal match against the source DS naming

**Remediation:** Rename non-conforming components. The skill provides a rename batch script.

### Gate 9 — Variant property naming follows convention

**Severity:** warn
**Check:** Variant property keys are `camelCase`; values are lowercase short kebab or single-word; no mixed casing.
**Remediation:** Rename via Figma's variant editor or Channel 3 plugin.

### Gate 10 — Foundations file has cover page

**Severity:** warn
**Check:** Foundations file has a page named "Cover" with at least one frame containing the DS name and version.
**Why:** Cover pages are the canonical landing zone for documentation; without them, users land in the variable list and feel lost.
**Remediation:** Auto-generate via skill or hand-craft.

### Gate 11 — Each component family has a section header

**Severity:** warn
**Check:** Within Components/Patterns files, every page has a heading frame at the top with the family name.
**Remediation:** Add a heading frame using the H2 text style at the top of each page.

### Gate 12 — No unpublished local styles in a publishable file

**Severity:** warn
**Check:** For each style in the file, verify `published === true` (i.e., the style is exposed when the library publishes). Exceptions: styles in the `Candidates` page are allowed to be unpublished.
**Remediation:** Publish the style, or move it to the Candidates page.

### Gate 13 — Effect styles are bound to elevation tokens

**Severity:** warn
**Check:** For every effect style used on a Surface (Card, Modal, Panel), verify its name matches an `elevation/*` token and its color/blur/offset values match the token definition.
**Remediation:** Rebind to the proper elevation effect style, or create the missing elevation style.

### Gate 14 — All icons are components

**Severity:** error
**Check:** For every icon-like node (raster or vector), verify it is a `COMPONENT` or `INSTANCE` of a component from the Icons library. Raw SVG vectors fail.
**Why:** Raw SVG cannot be instance-swapped; consumers cannot pick a different icon at use site.
**Remediation:** Wrap each icon as a Figma component (or import via the Icons library workflow).

### Gate 15 — All icons follow size/grid convention

**Severity:** warn
**Check:** Icon components have a square bounding box at one of `{16, 20, 24, 32, 48}` px and a consistent inner grid (typically a 2px stroke offset).
**Remediation:** Resize and align icons to the convention. Provide multiple sizes as separate variants when needed.

### Gate 16 — Library has at least one mode (Light) defined per collection

**Severity:** error
**Check:** Every variable collection has at least one mode named `Light` or `Default`. Dark/other modes are optional.
**Why:** Without a baseline mode, consumers cannot resolve variable values at all.
**Remediation:** Add the missing mode and populate values.

### Gate 17 — Component descriptions reference Code Connect status

**Severity:** info
**Check:** Component descriptions optionally include a Code Connect status badge: 🟢 (linked), 🟡 (partial), ⚪ (unlinked).
**Why:** Helps designers know which components have ready-to-use code.
**Remediation:** Run `CODE_CONNECT` mode to link, or add status badges manually.

### Gate 18 — License/version/contact metadata present in cover page

**Severity:** warn
**Check:** Cover page contains a text frame with: DS version string, license (or "Internal use only"), contact (team email or Slack channel).
**Remediation:** Add the metadata block to the cover.

### Gate 19 — No detached instance overrides outside the candidate page

**Severity:** warn
**Check:** Every component instance in published pages (not Candidates/Deprecated) has clean overrides: text + instance-swap allowed; paint/typography overrides flagged.
**Why:** Detached overrides indicate either a missing variant or an off-spec usage; both should be resolved before publish.
**Remediation:** Add the missing variant if the override is a legitimate need; otherwise revert the override.

---

## Audit report format

When `PUBLISH_AUDIT` runs, the output is a Markdown report:

```
# figma-forge Publish Audit — <DS Name>

Audit run: <ISO timestamp>
Files audited: 4 (Foundations, Components, Patterns, Icons)
Total checks: 19
Errors: 0
Warnings: 3
Info: 1

## Gate-by-gate results

### Gate 1 — All paints come from a variable
Status: ✓ Pass
Nodes checked: 1,247
Failures: 0

### Gate 5 — All components have descriptions
Status: ⚠ Warn (4 of 47 components fail)
Failures:
  - Components / Surfaces / Modal — empty description
  - Components / Feedback / Toast — empty description
  - Components / Data Display / Tag — empty description
  - Components / Data Display / Avatar — empty description

Remediation: Author 1–2 sentence descriptions covering "what it is" and "when to use it".

...
```

## Audit invocation

```python
python3 scripts/publish_audit.py \
    --library-registry library-registry.json \
    --figma-pat "$FIGMA_PAT" \
    --output publish-audit.md \
    --strict   # exit code 1 on any error-severity gate
```

The `--strict` flag is intended for CI gates blocking merges.

## Recommended pre-publish workflow

1. Run `PUBLISH_AUDIT --strict`.
2. Fix all error-severity issues.
3. Run `PUBLISH_AUDIT` again (without `--strict`).
4. Review warnings; fix the high-impact ones.
5. Re-run audit once more for clean report.
6. Manually publish via Figma menu: Assets → Publish Library.
7. Notify consumers via team channel.

---

## Implementation status (v0.2.0)

As of figma-forge v0.2.0, every gate in the catalog has a registered
checker implementation backed by integration tests against synthetic
fixtures. The audit runner (`scripts/publish_audit.py`) consumes the
package `scripts/publish_audit/` and emits a Markdown report whose
shape is backward-compatible with v0.1.x consumers.

| Gate | Severity | Module | Since | Notes |
|------|----------|--------|-------|-------|
| G1 | error | `gates/g01_paint_bindings.py` | v0.1.0 | Refactored to package in v0.2.0 |
| G2 | error | `gates/g02_text_styles.py` | v0.1.0 | Refactored to package in v0.2.0 |
| G3 | warn | `gates/g03_orphan_styles.py` | v0.2.0 | Walks document for style refs |
| G4 | error | `gates/g04_missing_variable_refs.py` | v0.2.0 | Local-alias resolution |
| G5 | warn | `gates/g05_component_descriptions.py` | v0.1.0 | Refactored to package in v0.2.0 |
| G6 | warn | `gates/g06_component_keywords.py` | v0.2.0 | `Keywords:` line + ≥4 tokens |
| G7 | error | `gates/g07_variant_matrix.py` | v0.2.0 | Cartesian-product gap detection |
| G8 | warn | `gates/g08_component_naming.py` | v0.2.0 | Registry-driven convention check |
| G9 | warn | `gates/g09_variant_property_naming.py` | v0.2.0 | Axis keys + values |
| G10 | warn | `gates/g10_foundations_cover.py` | v0.2.0 | Multi-file aware |
| G11 | warn | `gates/g11_section_headers.py` | v0.2.0 | Top-of-page heading heuristic |
| G12 | warn | `gates/g12_published_styles.py` | v0.2.0 | Candidates page exemption |
| G13 | warn | `gates/g13_effect_elevation.py` | v0.2.0 | Elevation / decorative / ambiguous classifier |
| G14 | error | `gates/g14_icons_are_components.py` | v0.2.0 | Heuristic stack: geometry + context |
| G15 | warn | `gates/g15_icon_size_grid.py` | v0.2.0 | {16,20,24,32,48} ±1 px |
| G16 | error | `gates/g16_modes_per_collection.py` | v0.1.0 | Refactored to package in v0.2.0 |
| G17 | info | `gates/g17_code_connect_badges.py` | v0.2.0 | 🟢/🟡/⚪/🔵 + textual synonyms |
| G18 | warn | `gates/g18_cover_metadata.py` | v0.2.0 | Version regex + license keywords + contact |
| G19 | warn | `gates/g19_instance_overrides.py` | v0.2.0 | Safe-field allowlist |

### Cross-cutting infrastructure

| Module | Purpose |
|--------|---------|
| `publish_audit/registry.py` | `LibraryRegistry` + `FileInfo` — multi-file library schema |
| `publish_audit/context.py` | `MultiFileFigmaContext` + `FigmaFile` — REST orchestration |
| `publish_audit/models.py` | `Gate`, `GateResult`, severity types, document iterators |
| `publish_audit/gates_registry.py` | Catalog + `@register_gate` dispatch |
| `publish_audit/naming.py` | `NamingValidator` protocol + Carbon/Material/BEM/Custom |
| `publish_audit/variants.py` | `VariantMatrixAnalyzer` — variant Cartesian product analysis |
| `publish_audit/reporting.py` | Markdown audit report rendering (v0.1.x-compatible) |
| `publish_audit/fixtures.py` | Deterministic fixture generators for test harness |

### Test coverage

The integration runner `tests/test_publish_audit.py` covers all 19 gates
with 37 test cases (pass + fail + n/a scenarios). Runs in <3 seconds
without a live Figma connection. The skill-level self-validation
(`tests/run_tests.py`) continues to enforce 8 quality gates over the
skill artifacts (file integrity, content validation, anti-pattern
detection, etc.).

---

End of reference.
