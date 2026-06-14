# Component Spec Templates

For `COMPONENTS_BUILD` mode, `figma-forge` accepts a **component specification JSON** describing each component's structure, variants, slots, and token bindings. This reference documents the schema and provides templates for common component patterns.

## Spec schema

```json
{
  "components": [
    {
      "name": "Button",
      "family": "Actions",
      "description": "Primary interactive element for triggering actions.",
      "keywords": ["button", "action", "cta", "click"],
      "auto_layout": {
        "direction": "horizontal",
        "padding": "{space.component-padding.md}",
        "gap": "{space.gap.sm}",
        "align": "center",
        "fill_container": "hug-contents"
      },
      "variants": {
        "size": ["sm", "md", "lg"],
        "variant": ["primary", "secondary", "tertiary", "ghost", "danger"],
        "state": ["default", "hover", "pressed", "disabled", "focus"],
        "iconLeading": [true, false],
        "iconTrailing": [true, false]
      },
      "token_bindings": {
        "background": "{color.button.{variant}.{state}.bg}",
        "text_color": "{color.button.{variant}.{state}.text}",
        "border": "{color.button.{variant}.{state}.border}",
        "border_width": "{dimension.border.thin}",
        "radius": "{dimension.radius.button.{size}}",
        "typography": "{typography.label.{size}}",
        "padding_x": "{space.button.x.{size}}",
        "padding_y": "{space.button.y.{size}}"
      },
      "slots": [
        {
          "name": "leading_icon",
          "type": "icon",
          "size": "{dimension.icon.{size}}",
          "visible_when": "iconLeading=true"
        },
        {
          "name": "label",
          "type": "text",
          "default_content": "Button"
        },
        {
          "name": "trailing_icon",
          "type": "icon",
          "size": "{dimension.icon.{size}}",
          "visible_when": "iconTrailing=true"
        }
      ],
      "interactions": {
        "hover_from": "default",
        "pressed_from": "hover",
        "disabled_disables_all_other_states": true
      },
      "code_connect": {
        "framework": "react",
        "source_path": "src/components/Button/Button.tsx"
      }
    }
  ]
}
```

## Per-family templates

### Buttons

```json
{
  "name": "Button",
  "family": "Actions",
  "variants": {
    "variant": ["primary", "secondary", "tertiary", "ghost", "danger"],
    "size": ["sm", "md", "lg"],
    "state": ["default", "hover", "pressed", "disabled", "focus"],
    "iconLeading": [true, false],
    "iconTrailing": [true, false]
  }
}
```

5 × 3 × 5 × 2 × 2 = 300 variants. **Warning trigger**: this exceeds the 256-variant practical threshold. The skill warns and asks the user to either:
- Collapse the `state` axis (default + hover + disabled only = 3 → 180 variants)
- Or move `state` to interactive overlays via component properties (Figma's "interactive component" feature)

### Inputs

```json
{
  "name": "TextInput",
  "family": "Inputs",
  "variants": {
    "size": ["sm", "md", "lg"],
    "state": ["default", "hover", "focus", "filled", "error", "disabled"],
    "hasLabel": [true, false],
    "hasHelperText": [true, false],
    "hasErrorText": [true, false]
  },
  "slots": [
    {"name": "label", "type": "text", "default_content": "Label"},
    {"name": "input", "type": "input_frame", "placeholder": "Placeholder"},
    {"name": "helper_text", "type": "text", "visible_when": "hasHelperText=true"},
    {"name": "error_text", "type": "text", "visible_when": "state=error AND hasErrorText=true"}
  ]
}
```

### Surfaces (Card, Modal)

```json
{
  "name": "Card",
  "family": "Surfaces",
  "variants": {
    "variant": ["filled", "outlined", "elevated"],
    "interactive": [true, false],
    "hasHeader": [true, false],
    "hasFooter": [true, false]
  },
  "auto_layout": {
    "direction": "vertical",
    "padding": "{space.component-padding.lg}",
    "gap": "{space.gap.md}"
  },
  "slots": [
    {"name": "header", "type": "slot", "visible_when": "hasHeader=true"},
    {"name": "body", "type": "slot"},
    {"name": "footer", "type": "slot", "visible_when": "hasFooter=true"}
  ]
}
```

### Tags / Badges

```json
{
  "name": "Tag",
  "family": "Data Display",
  "variants": {
    "color": ["gray", "blue", "red", "green", "yellow", "purple"],
    "size": ["sm", "md"],
    "filled": [true, false],
    "removable": [true, false]
  }
}
```

### Tooltips

```json
{
  "name": "Tooltip",
  "family": "Feedback",
  "variants": {
    "position": ["top", "right", "bottom", "left"],
    "hasArrow": [true, false]
  }
}
```

## Slot types

| Slot type | Behavior in Figma |
|---|---|
| `text` | Text node; supports default content; text override available at instance level |
| `icon` | Instance of an icon from the Icons library; instance-swap property exposed |
| `slot` | Generic placeholder accepting any frame/component; instance-swap on parent |
| `input_frame` | A child frame styled as an input area (border, padding) — typically used inside TextInput |

## Token-binding placeholder syntax

The component spec uses `{token.path}` for direct bindings and `{token.path.{variant}.{state}}` for variant-aware bindings:

- `{color.action.primary.bg}` → direct binding
- `{color.button.{variant}.{state}.bg}` → resolves to e.g. `color.button.primary.hover.bg` for that variant combination

If the resolved path doesn't exist in the loaded variable set, the skill:

1. Logs a missing-token warning in the run report.
2. Falls back to a sensible default (often the `default` state's token, or a primitive gray).
3. Records the gap so the user can add the missing tokens to the source spec.

## Built-in component sets

For `COMPONENTS_BUILD` with a built-in DS source, the skill ships pre-built component spec JSON in `templates/component-specs/`:

| File | DS source |
|---|---|
| `carbon-v11-components.json` | Carbon v11 components (~60 items) |
| `material3-components.json` | Material 3 components (~75 items) |
| `tailwind-default-components.json` | Generic Tailwind-styled components (~35 items, shadcn-flavored) |

For custom DS, the user provides their own component spec JSON. The skill validates against the schema above before processing.

## Auto-layout patterns

Each component uses Figma's auto-layout. The spec's `auto_layout` field captures the high-level intent; the skill expands it into Figma's per-axis settings:

| Spec field | Figma auto-layout property |
|---|---|
| `direction: horizontal` | `layoutMode: HORIZONTAL` |
| `direction: vertical` | `layoutMode: VERTICAL` |
| `padding: {token}` | `paddingLeft/Right/Top/Bottom` from token, equal on all sides unless `padding_x`/`padding_y` provided |
| `gap: {token}` | `itemSpacing` from token |
| `align: center` | `primaryAxisAlignItems: CENTER`, `counterAxisAlignItems: CENTER` |
| `align: start` | `primaryAxisAlignItems: MIN`, `counterAxisAlignItems: MIN` |
| `align: space-between` | `primaryAxisAlignItems: SPACE_BETWEEN` |
| `fill_container: fill-container` | `layoutAlign: STRETCH` on parent, `STRETCH` on children |
| `fill_container: hug-contents` | `layoutSizingHorizontal: HUG`, `layoutSizingVertical: HUG` |

## Variant generation

Given the variant axes, the skill generates one base component per Cartesian product combination, then groups them into a component set via `figma.combineAsVariants` (plugin) or `use_figma` (MCP).

For interactivity (hover, pressed states as live interactions), the skill emits Figma "Interactive Components" wiring where supported.

## Code Connect linkage

Each component spec optionally includes `code_connect` metadata pointing to a code source path. The skill uses this in `CODE_CONNECT` mode to emit the Code Connect stubs (see `code-connect-patterns.md`).

## Validation gates

Before pushing components, the skill validates:

| Gate | Failure action |
|---|---|
| Every variant axis has at least 2 values | Halt; ask user to remove single-value axes (they're not variants, they're descriptions) |
| Total variant count ≤ 256 | Warn at 64, error at 256 — propose axis collapsing |
| Every `token_bindings` value resolves to a token in the loaded set | Warn per gap; suggest token additions |
| Slot names are unique within a component | Halt |
| Component name is unique within its family | Halt |
| Family name is from the canonical set (Actions, Inputs, Surfaces, Navigation, Feedback, Data Display) — or explicitly allowed | Warn |

---

End of reference.
