# W3C Design Tokens Community Group (DTCG) Schema

The W3C Design Tokens Community Group (DTCG) draft specification is the **canonical interchange format** for design tokens across tooling. `figma-forge` normalizes every input (Style Dictionary export, Carbon/Material/Tailwind mappers, ad-hoc JSON) into DTCG-shaped JSON before pushing to Figma.

Reference draft: [W3C DTCG draft](https://design-tokens.github.io/community-group/format/)

## Core concepts

### Token shape

Every leaf node is an object with at minimum:

```json
{
  "$value": "<value>",
  "$type": "<type-name>",
  "$description": "<optional explanatory text>"
}
```

### Token tree

Tokens are nested under semantic group keys. Group keys are not significant to the schema — only `$value`, `$type`, and `$description` are reserved keys (prefixed with `$`).

```json
{
  "color": {
    "blue": {
      "500": {
        "$value": "#0066CC",
        "$type": "color",
        "$description": "Primary blue, mid-tone"
      },
      "600": {
        "$value": "#0052A3",
        "$type": "color"
      }
    }
  }
}
```

### Aliases

A token can reference another token by curly-brace path:

```json
{
  "action": {
    "primary": {
      "$value": "{color.blue.500}",
      "$type": "color"
    }
  }
}
```

Aliases are resolved at token-system build time. `figma-forge` performs a **topological sort** before pushing so all target tokens are created before their aliases.

When emitted to the Figma REST API, an alias becomes a `VARIABLE_ALIAS` value object:

```json
{
  "variableId": "VariableID:1:42",
  "modeId": "1:0",
  "value": { "type": "VARIABLE_ALIAS", "id": "VariableID:1:7" }
}
```

The `VARIABLE_ALIAS` discriminator tells Figma the variable's value at that mode is a reference, not a literal. The Channel 3 plugin equivalent is `figma.variables.createVariableAlias(targetVariable)`.

## Reserved $types used by figma-forge

| `$type` | Value shape | Figma mapping |
|---|---|---|
| `color` | hex `#RRGGBB`/`#RRGGBBAA` or `rgb()` or `rgba()` or `hsl()` | Color Variable + paint style |
| `dimension` | `{ value: 16, unit: "px" }` or string `"16px"` / `"1rem"` | Float Variable |
| `fontFamily` | string or array of strings (fallback stack) | String Variable; first family used as Figma `fontName.family` |
| `fontWeight` | number (100–900) or string (`"regular"`, `"bold"`) | Float Variable |
| `duration` | `{ value: 200, unit: "ms" }` | Metadata only (Figma has no motion variables) |
| `cubicBezier` | `[0.4, 0.0, 0.2, 1.0]` | Metadata only |
| `number` | number | Float Variable |
| `string` | string | String Variable |
| `boolean` | true/false | Boolean Variable |
| `typography` | composite — see below | Text style |
| `shadow` | composite — see below | Effect style |
| `gradient` | composite — see below | Paint style |
| `border` | composite — see below | Component-level stroke binding |
| `transition` | composite of duration + cubicBezier | Metadata only |

### Composite types

#### `typography`

```json
{
  "$type": "typography",
  "$value": {
    "fontFamily": "{font.family.sans}",
    "fontWeight": "{font.weight.regular}",
    "fontSize": "{dimension.body.md}",
    "lineHeight": "{dimension.body.lineHeight}",
    "letterSpacing": "{dimension.body.tracking}"
  }
}
```

Maps to a Figma text style with each sub-field bound to the resolved variable (where Figma supports the binding).

#### `shadow`

```json
{
  "$type": "shadow",
  "$value": [
    {
      "color": "#0000001A",
      "offsetX": "0px",
      "offsetY": "1px",
      "blur": "3px",
      "spread": "0px"
    },
    {
      "color": "#0000000F",
      "offsetX": "0px",
      "offsetY": "1px",
      "blur": "2px",
      "spread": "0px"
    }
  ]
}
```

Array support → multi-shadow effect style.

#### `gradient`

```json
{
  "$type": "gradient",
  "$value": {
    "stops": [
      {"color": "#0066CC", "position": 0.0},
      {"color": "#0052A3", "position": 1.0}
    ],
    "angle": 90
  }
}
```

Maps to a Figma gradient paint (linear if `angle` provided, radial if `center` + `radius`).

#### `border`

```json
{
  "$type": "border",
  "$value": {
    "color": "{color.border.subtle}",
    "width": "{dimension.border.thin}",
    "style": "solid"
  }
}
```

Border tokens don't have a direct Figma counterpart; they're stored as metadata and applied at component-build time as stroke + strokeWeight.

## Collection structure

`figma-forge` maps DTCG token groups onto Figma's collection-and-mode hierarchy:

| DTCG group at top-level | Figma collection | Modes |
|---|---|---|
| `color.primitive.*` (primitives) | `Primitives — Color` | one default mode |
| `color.semantic.*` (aliases to primitives) | `Semantic — Color` | Light, Dark (if input has theme variants) |
| `color.component.*` (component-specific) | `Component — Color` | inherits Light/Dark |
| `dimension.*` | `Primitives — Dimension` | optionally Density: Compact/Comfortable |
| `font.*` | `Primitives — Typography` | one default mode |
| Composite tokens (typography, shadow, gradient) | not stored as variables — emitted as styles |

If the input DTCG doesn't use this layering convention, `figma-forge` infers groupings heuristically: anything with a literal value goes to `Primitives`, anything aliased to a primitive goes to `Semantic`.

## Mode detection

Multi-theme tokens use the DTCG `$extensions.com.figma-forge.modes` field or follow this convention:

```json
{
  "color": {
    "background": {
      "$type": "color",
      "$value": {
        "light": "#FFFFFF",
        "dark": "#000000"
      }
    }
  }
}
```

The skill recognizes both standard DTCG (`$value` as object with mode keys) and the figma-forge extension format. Mode names are normalized: `light` → `Light`, `dark` → `Dark`, `default` → `Default`.

## Validation

Before pushing tokens, `figma-forge` runs schema validation:

| Check | Action on failure |
|---|---|
| Every leaf has `$value` and `$type` | Halt; report path of offending node |
| Aliases form a DAG (no cycles) | Halt; report cycle path |
| Alias targets exist | Halt; report broken alias path |
| Color values are valid CSS color strings | Coerce or halt |
| Dimension values have units | Default `px` with warning |
| Font families resolve to installable fonts | Warn; proceed |

## Round-tripping

After import, `figma-forge` can re-export DTCG JSON from Figma (Channel 1 read + serialization) to verify round-trip fidelity. The canonical DTCG intermediate is always saved alongside the import for this purpose.

---

## Reference quote summary (paraphrased from DTCG draft)

The Design Tokens Community Group draft specifies that tokens are structured JSON with reserved `$`-prefixed keys for type and value information. Group nesting is open-ended and not semantically constrained. Composite types (typography, shadow, gradient, border, transition) have specified sub-schemas. Aliases use brace-delimited dot-paths to other tokens in the same file. The draft also specifies an `$extensions` key for tool-specific extensions.

Citation: Design Tokens Community Group draft, [https://design-tokens.github.io/community-group/format/](https://design-tokens.github.io/community-group/format/).

---

End of reference. For Style Dictionary conversion: see `style-dictionary.md`. For DS-specific mappers: see `carbon-mapping.md`, `material3-mapping.md`, `tailwind-mapping.md`.
