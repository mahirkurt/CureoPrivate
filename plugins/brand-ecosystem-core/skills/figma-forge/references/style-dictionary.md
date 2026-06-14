# Style Dictionary → DTCG Conversion

Amazon Style Dictionary is a widely-used multi-platform DS tooling system. Its native token format predates the W3C DTCG draft and uses slightly different conventions. `figma-forge` normalizes Style Dictionary exports to DTCG via the bundled `scripts/style_dict_to_dtcg.py` converter.

## Style Dictionary token format

A typical Style Dictionary token file:

```json
{
  "color": {
    "blue": {
      "500": {
        "value": "#0066CC",
        "comment": "Primary blue, mid-tone"
      }
    },
    "action": {
      "primary": {
        "value": "{color.blue.500.value}",
        "comment": "Primary action color"
      }
    }
  }
}
```

## Key differences vs DTCG

| Style Dictionary | DTCG |
|---|---|
| `value` | `$value` |
| `comment` | `$description` |
| (inferred from path or `$type`) | explicit `$type` required at leaf |
| `{color.blue.500.value}` (alias with `.value` suffix) | `{color.blue.500}` (no suffix) |
| Optional `attributes.category` | encoded via group structure |

## Conversion algorithm (`scripts/style_dict_to_dtcg.py`)

```
def style_dict_to_dtcg(node, path=""):
    if "value" in node:
        # leaf — convert
        dtcg = {
            "$value": rewrite_aliases(node["value"]),
            "$type": infer_type(node, path),
        }
        if "comment" in node:
            dtcg["$description"] = node["comment"]
        return dtcg
    # group — recurse
    return {key: style_dict_to_dtcg(child, f"{path}.{key}") for key, child in node.items()}
```

### Type inference

Style Dictionary doesn't require explicit `$type`. The converter infers from:

1. **Path heuristics:** `color.*` → `color`, `size.*` / `spacing.*` / `dimension.*` → `dimension`, `font.family.*` → `fontFamily`, `font.weight.*` → `fontWeight`, `font.size.*` → `dimension`, `font.lineHeight.*` → `dimension`, `font.letterSpacing.*` → `dimension`, `radius.*` → `dimension`, `shadow.*` → `shadow`, `motion.*` → `duration` or `cubicBezier`, etc.
2. **Value heuristics:** values matching `#[0-9A-Fa-f]{3,8}` → `color`. Values like `"16px"` → `dimension`. Numeric weights 100–900 → `fontWeight`.
3. **`attributes.category` / `attributes.type`** if present in source.
4. **User override** if the source DS specifies a `type` field directly.

### Alias rewriting

Style Dictionary aliases are dot-paths ending with `.value` (the legacy `{node.value}` syntax) or without (`.value`-less, newer). The converter strips the trailing `.value`:

```
{color.blue.500.value}    →    {color.blue.500}
```

### Multi-platform exports

If the Style Dictionary input is from a `build/` directory with platform-specific outputs (e.g., `css`, `js`, `json`, `scss`), the converter:

1. Prefers the `json` output if present (raw token data).
2. Falls back to scanning `.scss` and converting Sass variables back to tokens.
3. Asks the user to point at the canonical token source if the build outputs diverge.

## Style Dictionary + DTCG bidirectional bridge

For ecosystems where Style Dictionary remains the source of truth (e.g., a multi-platform DS where Style Dictionary generates iOS, Android, and Web outputs), `figma-forge` can run as a **read-only consumer** — it imports tokens into Figma without claiming ownership. The DS team continues to maintain tokens in Style Dictionary format; `figma-forge` re-imports on each update.

Pattern:

```
1. DS team commits Style Dictionary tokens
2. CI runs: figma-forge in --mode TOKENS_IMPORT --input tokens-build/json/all.json --update-only
3. Figma library is updated; team is notified
```

The `--update-only` flag skips creation of new variables and only updates existing matched-by-name variables. New tokens require an explicit `--allow-new` to prevent accidental library bloat.

## Composite token handling

Style Dictionary expresses composites two ways:

### Implicit (multi-property tokens at one path)

```json
{
  "typography": {
    "body": {
      "value": {
        "fontFamily": "{font.family.sans.value}",
        "fontSize": "{font.size.md.value}",
        "fontWeight": "{font.weight.regular.value}",
        "lineHeight": "{font.lineHeight.md.value}"
      },
      "type": "typography"
    }
  }
}
```

### Explicit (parallel paths)

```json
{
  "typography": {
    "body": {
      "fontFamily": {"value": "{font.family.sans.value}"},
      "fontSize": {"value": "{font.size.md.value}"},
      "fontWeight": {"value": "{font.weight.regular.value}"},
      "lineHeight": {"value": "{font.lineHeight.md.value}"}
    }
  }
}
```

The converter detects both shapes. The implicit shape converts directly to a DTCG composite. The explicit shape is left as-is (it's already DTCG-shaped at the primitive level) and the composite is reconstructed only if a `$type: "typography"` hint or an explicit name like `body.composite` indicates it.

## Conversion gotchas

| Issue | Resolution |
|---|---|
| Style Dict aliases use `.value` suffix | Stripped by converter |
| `attributes` Style Dict metadata block | Ignored unless `attributes.category` aids type inference |
| `transformGroup` references | Not converted — these are platform-specific build configs |
| Token names with reserved DTCG keys (`$value`, `$type`) | Renamed with a prefix; warning logged |
| Numeric values without units | Default unit applied per type (`px` for dimension); warning logged |
| `name` field at non-leaf | Treated as group display name; preserved in `$description` |

## Output

After conversion:

```
tokens-input.json (Style Dictionary)
  ↓ scripts/style_dict_to_dtcg.py
tokens.dtcg.json (canonical DTCG intermediate)
  ↓ figma-forge TOKENS_IMPORT
Figma Variables + styles
```

The DTCG intermediate is preserved in the run output for audit and round-trip purposes.

---

End of reference.
