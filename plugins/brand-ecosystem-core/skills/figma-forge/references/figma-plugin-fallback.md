# Figma Plugin Fallback (Channel 3)

The plugin fallback is the most reliable path for writing Figma Variables on non-Enterprise plans, and the only path for some advanced operations (Variable creation, complex variant generation, library publish on Starter plan).

## When Channel 3 is invoked

The skill switches to Channel 3 when any of these conditions is true:

1. User is on Free / Starter / Professional plan and `TOKENS_IMPORT` requires Variables write.
2. Channel 1 (`use_figma`) reported a failure that the skill cannot work around.
3. Component spec has variant explosion >256 unique variants.
4. User explicitly requests "use the plugin path" (e.g., for sandboxed environments where REST PAT cannot be issued).

## What the user gets

`figma-forge` produces a complete plugin bundle:

```
figma-forge-plugin/
├── manifest.json              ← Plugin manifest (Figma Plugin API spec)
├── code.ts                    ← Compiled plugin logic
├── code.js                    ← (alternative: pre-compiled JS for users without TS toolchain)
├── ui.html                    ← Plugin UI (file picker + status display)
├── tokens.dtcg.json           ← The actual tokens to import (auto-embedded)
└── README.md                  ← Step-by-step import instructions for the user
```

The user runs these steps once:

1. Save the bundle locally (`figma-forge-plugin/` directory).
2. In Figma desktop app, open the target file.
3. Menu: **Plugins → Development → Import plugin from manifest**.
4. Select `figma-forge-plugin/manifest.json`.
5. Run the plugin: **Plugins → Development → figma-forge importer**.
6. Plugin reads `tokens.dtcg.json` (auto-embedded) and writes to Figma.
7. Plugin reports a summary in its UI panel; user closes the plugin.

Subsequent runs on the same file: simply update `tokens.dtcg.json` in the bundle, re-run the plugin.

## Plugin Manifest

The bundled `manifest.json`:

```json
{
  "name": "figma-forge importer",
  "id": "com.figma-forge.importer",
  "api": "1.0.0",
  "main": "code.js",
  "ui": "ui.html",
  "editorType": ["figma"],
  "permissions": ["currentuser"],
  "documentAccess": "dynamic-page",
  "networkAccess": {
    "allowedDomains": ["none"]
  }
}
```

Key notes:

- `documentAccess: dynamic-page` is required for files with >1k nodes (large libraries).
- `networkAccess: none` — the plugin never phones home. All token data is bundled in.
- `permissions: currentuser` — only used to record who ran the import in metadata.

## Plugin Code (code.ts) — primary operations

### Create a variable collection with modes

```typescript
const collection = figma.variables.createVariableCollection("Primitives");
const defaultModeId = collection.modes[0].modeId;
const darkModeId = collection.addMode("Dark");
```

### Create a color variable

```typescript
const colorVar = figma.variables.createVariable(
  "color/blue/500",
  collection,
  "COLOR"
);
colorVar.setValueForMode(defaultModeId, { r: 0.0, g: 0.4, b: 0.8, a: 1.0 });
colorVar.setValueForMode(darkModeId, { r: 0.2, g: 0.5, b: 0.9, a: 1.0 });
```

### Create an aliased variable

```typescript
const semanticVar = figma.variables.createVariable(
  "color/action/primary",
  semanticCollection,
  "COLOR"
);
semanticVar.setValueForMode(defaultModeId, {
  type: "VARIABLE_ALIAS",
  id: colorVar.id
});
```

### Create a paint style bound to a variable

```typescript
const style = figma.createPaintStyle();
style.name = "color/action/primary";
const paint = figma.util.solidPaint("#0066CC");
style.paints = [paint];
// Bind the paint's color to the variable:
const boundPaint = figma.variables.setBoundVariableForPaint(
  paint,
  "color",
  semanticVar
);
style.paints = [boundPaint];
```

### Create a text style with variable bindings

```typescript
await figma.loadFontAsync({ family: "IBM Plex Sans", style: "Regular" });
const textStyle = figma.createTextStyle();
textStyle.name = "typography/body/medium";
textStyle.fontName = { family: "IBM Plex Sans", style: "Regular" };
textStyle.fontSize = 14;
textStyle.lineHeight = { value: 20, unit: "PIXELS" };
textStyle.letterSpacing = { value: 0, unit: "PIXELS" };
// Bind to variables where available:
textStyle.setBoundVariable("fontSize", fontSizeVar);
textStyle.setBoundVariable("lineHeight", lineHeightVar);
```

### Create a variant component set

```typescript
// Create base instances for each variant combination
const baseNodes: ComponentNode[] = [];
for (const { size, state, variant } of variantCombinations) {
  const node = figma.createComponent();
  node.name = `size=${size}, state=${state}, variant=${variant}`;
  // Configure auto-layout, paints, etc.
  baseNodes.push(node);
}

// Combine into a component set
const componentSet = figma.combineAsVariants(baseNodes, figma.currentPage);
componentSet.name = "Button";
```

## Plugin UI (ui.html)

A minimal UI panel that:

- Shows the import progress (collection X of N, variable Y of M).
- Reports any errors per variable (e.g., "font not installed", "alias target not found").
- Provides a "Run again" button after completion.
- Includes a "Download log" button to save the run report.

The UI communicates with the plugin sandbox via `parent.postMessage` and `window.onmessage`.

## Local-bundled token data

To avoid network calls, `tokens.dtcg.json` is bundled into the plugin directory. The plugin reads it via the Figma `fetch` polyfill — but `networkAccess: none` blocks network requests, so the skill embeds the JSON directly in `code.js`:

```typescript
const TOKENS_JSON = /* ⟵ embedded by figma-forge at build time */;
const tokens = JSON.parse(TOKENS_JSON);
```

For very large token sets (>500 KB), the skill splits into multiple plugin bundles or instructs the user to use Channel 2.

## Plugin output

When the plugin completes, it displays:

```
✓ Created 3 variable collections (Primitives, Semantic, Component)
✓ Created 2 modes per collection (Light, Dark)
✓ Created 247 primitive color variables
✓ Created 78 semantic color variables (aliased)
✓ Created 24 typography size variables
✓ Created 12 font weight variables
✓ Created 8 radius variables
✓ Created 32 spacing variables
✓ Created 14 text styles bound to variables
✓ Created 12 effect styles
✓ Created 48 paint styles bound to variables

⚠ 2 fonts not installed: "Roche Sans", "IBM Plex Sans Hebrew"
   → These styles will fall back; install the fonts and re-run for full fidelity.

Total: 458 entities created. Plugin run completed in 18.3s.
```

The user is asked to **publish the library** manually (Figma menu: Assets → Publish Library) — this is intentionally a human-in-the-loop step because publishing is irreversible and may notify consumers.

## Cleanup

Plugins imported via "Plugins → Development → Import" are local to the user's machine and not shared. The user can delete the plugin at any time via **Plugins → Development → Manage plugins → Remove**. The skill includes this in the README.

---

End of reference. For Channel 1 (MCP): see `figma-mcp-cookbook.md`. For Channel 2 (REST): see `figma-rest-api.md`.
