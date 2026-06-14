# Code Connect Patterns

Figma Code Connect bridges design components and code components, enabling code preview directly in Figma's dev mode. `figma-forge`'s `CODE_CONNECT` mode generates stub files that link Figma component variants to their code counterparts.

## What Code Connect provides

- **Dev mode preview** — designers and developers see the exact code snippet that produces a given Figma instance.
- **Round-trip alignment** — when designers change a component variant or property, the linked code preview updates.
- **Property mapping** — Figma component properties (variants, boolean, text, instance-swap) map to code props.

## Supported frameworks

| Framework | Stub extension | Status |
|---|---|---|
| React (JSX/TSX) | `.figma.tsx` | First-class |
| Web Components | `.figma.ts` | First-class |
| HTML | `.figma.html` | First-class |
| Vue | `.figma.vue` | Beta |
| SwiftUI (iOS) | `.figma.swift` | Beta |
| Compose (Android) | `.figma.kt` | Beta |

`figma-forge` ships templates for React, Web Components, and HTML. Beta frameworks are routable but require the user to validate manually.

## React stub template

```tsx
import { figma } from "@figma/code-connect";
import { Button } from "./Button";

figma.connect(Button, "https://www.figma.com/file/<FILE_KEY>/<FILE_NAME>?node-id=<NODE_ID>", {
  props: {
    variant: figma.enum("variant", {
      primary: "primary",
      secondary: "secondary",
      tertiary: "tertiary",
      ghost: "ghost",
      danger: "danger"
    }),
    size: figma.enum("size", {
      sm: "sm",
      md: "md",
      lg: "lg"
    }),
    disabled: figma.boolean("state", {
      disabled: true,
      "*": false
    }),
    iconLeading: figma.boolean("iconLeading"),
    iconTrailing: figma.boolean("iconTrailing"),
    children: figma.string("label")
  },
  example: ({ variant, size, disabled, iconLeading, iconTrailing, children }) => (
    <Button
      variant={variant}
      size={size}
      disabled={disabled}
      iconLeading={iconLeading ? <Icon /> : undefined}
      iconTrailing={iconTrailing ? <Icon /> : undefined}
    >
      {children}
    </Button>
  )
});
```

## Web Components stub template

```typescript
import { figma } from "@figma/code-connect";

figma.connect(
  "https://www.figma.com/file/<FILE_KEY>/<FILE_NAME>?node-id=<NODE_ID>",
  {
    props: {
      variant: figma.enum("variant", {
        primary: "primary",
        secondary: "secondary",
        tertiary: "tertiary",
        ghost: "ghost",
        danger: "danger"
      }),
      size: figma.enum("size", { sm: "sm", md: "md", lg: "lg" }),
      disabled: figma.boolean("state", { disabled: true, "*": false }),
      label: figma.string("label")
    },
    example: ({ variant, size, disabled, label }) =>
      `<my-button variant="${variant}" size="${size}"${disabled ? " disabled" : ""}>
        ${label}
      </my-button>`
  }
);
```

## HTML stub template

```typescript
import { figma } from "@figma/code-connect/html";

figma.connect(
  "https://www.figma.com/file/<FILE_KEY>/<FILE_NAME>?node-id=<NODE_ID>",
  {
    props: {
      variant: figma.enum("variant", { primary: "primary" }),
      label: figma.string("label")
    },
    example: ({ variant, label }) =>
      `<button class="btn btn-${variant}">${label}</button>`
  }
);
```

## Property type mapping

| Figma property type | Code Connect mapper | Notes |
|---|---|---|
| Variant (enum) | `figma.enum(key, mapping)` | One mapping entry per variant value |
| Boolean | `figma.boolean(key)` or `figma.boolean(key, mapping)` | Use mapping to remap multiple values to true/false |
| Text content (instance text override) | `figma.string(layerName)` | Layer name in Figma must match |
| Instance swap (icon, image) | `figma.instance(key)` | Returns the swapped instance for further connection |
| Children | `figma.children(layerName)` | For slots / containers |

## Bulk generation algorithm

For `CODE_CONNECT` mode:

```
1. Read Components Figma file via Figma:get_design_context
2. For each component:
    a. Extract node URL (file_key + node_id)
    b. Extract variant property definitions
    c. Look up code source path (from component spec or by name matching in target repo)
    d. Generate stub from the appropriate template (React/WC/HTML)
    e. Write to target_repo_path/.figma/<component>.figma.tsx
3. Bulk save via Figma:send_code_connect_mappings
```

## Source path resolution

The skill resolves source paths in priority order:

1. Explicit `code_connect.source_path` in the component spec (highest priority)
2. Convention: `src/components/<ComponentName>/<ComponentName>.tsx` (React)
3. Convention: `src/components/<component-name>.ts` (Web Components)
4. Convention: scan target_repo for files matching `<ComponentName>.{tsx,ts,vue,html}` and pick the first
5. If none found: emit stub with placeholder `// TODO: link to actual component` and mark for user review

## Validation

After generating stubs:

| Check | Action |
|---|---|
| Stub file syntactically valid (parses) | Halt and report on error |
| Imported component file exists | Warn if missing |
| Figma URL contains a valid file_key | Halt if missing |
| All variant axes in the spec mapped in stub | Warn per missing axis |

## Round-trip from Figma

In `CODE_CONNECT` interactive mode (when `Figma:get_code_connect_suggestions` is available), the skill queries Figma for AI-suggested mappings, presents them to the user, and applies the accepted ones via `Figma:send_code_connect_mappings`.

```
1. Figma:get_code_connect_suggestions(file_key, repo_path)
   → [{node_id, suggested_component_path, confidence}]

2. Filter to confidence ≥ 0.75 by default; user can adjust threshold.

3. For accepted mappings:
   - Generate stub via templates
   - Write to disk
   - Add mapping via Figma:send_code_connect_mappings
```

## CLI workflow (for users who want to run Code Connect from terminal)

If the user prefers Figma's `code-connect` CLI tool over the in-skill flow:

```bash
# Install
npm install -D @figma/code-connect

# Initialize (creates config + stubs)
npx figma connect create <FIGMA_URL>

# Publish to Figma (so it appears in dev mode)
npx figma connect publish
```

`figma-forge` can output the stub files in CLI-compatible format and let the user run publish themselves.

---

End of reference.
