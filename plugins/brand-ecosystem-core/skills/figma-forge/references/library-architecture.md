# Library Architecture

Figma libraries can be structured as a single file or split across multiple files with cross-file linking. `figma-forge` defaults to a **4-file architecture** matching modern enterprise DS patterns (Roche RDS, Material 3, Carbon, Polaris), but supports collapse-to-2-file and collapse-to-1-file for smaller systems.

## The 4-file default

```
Foundations  ──┬──→ Components  ──┬──→ Patterns
               │                  │
Icons  ────────┴──────────────────┘
```

| File | Contents | Consumed by |
|---|---|---|
| **Foundations** | Variables (color, dimension, font*, radius, opacity), paint styles, text styles, effect styles, grid styles | Components, Patterns, Icons (typography), product files |
| **Components** | Variant-aware components (Button, Input, Tag, Card, etc.) | Patterns, product files |
| **Patterns** | Compositions (Form, DataTable, EmptyState, OnboardingFlow) | Product files |
| **Icons** | Iconography library (SVG-imported components) | Components, Patterns, product files |

### Why the split

- **Update independence:** updating an icon doesn't trigger a Components-file republish; updating a color variable doesn't force Patterns to republish.
- **Performance:** large monolithic libraries slow Figma's renderer. 4-file split keeps each file under ~5k nodes typically.
- **Permission scoping:** different teams can own different files (foundations team, components team, etc.).
- **Mental model:** designers see clear separation between primitives, primitives-applied (components), and patterns (compositions).

## Smaller variants

### 2-file ("starter")

Used for early-stage products or smaller teams:

```
Foundations  ──→  Components+Patterns
```

Icons are inlined into the Components+Patterns file as a page rather than a separate file.

### 1-file ("micro")

Used for very small DS or prototypes:

```
DesignSystem (everything in one file)
```

Pages within the file: `Cover`, `Foundations`, `Components`, `Patterns`, `Icons`.

## Larger variants

For very large systems, the skill supports adding more files:

```
Foundations  ─→  Components  ─→  Patterns
                      ↓
                Data Visualization (charts, plots, etc.)
                      ↓
                Templates (full-page templates)
```

Roche RDS uses a 5-file split (Foundations / Components / Patterns / Icons / Data Visualization). The skill's `SCAFFOLD` mode supports any of these depths.

## Linking rules

When a downstream file consumes upstream variables/styles/components, the upstream file must be **published** to the team library and **enabled** in the downstream file (Assets panel → toggle library on).

The skill records linking dependencies in `library-registry.json`:

```json
{
  "ds_name": "Hemantix",
  "files": {
    "foundations": {
      "name": "Hemantix — Foundations",
      "file_key": "ABCDEFGHIJKLMNOPQRSTUV",
      "url": "https://www.figma.com/file/ABCDEFGHIJKLMNOPQRSTUV/Hemantix-Foundations",
      "consumes": []
    },
    "components": {
      "name": "Hemantix — Components",
      "file_key": "WXYZABCDEFGHIJKLMNOPQR",
      "url": "https://www.figma.com/file/WXYZABCDEFGHIJKLMNOPQR/Hemantix-Components",
      "consumes": ["foundations", "icons"]
    },
    "patterns": {
      "name": "Hemantix — Patterns",
      "file_key": "STUVWXYZABCDEFGHIJKLMN",
      "url": "https://www.figma.com/file/STUVWXYZABCDEFGHIJKLMN/Hemantix-Patterns",
      "consumes": ["foundations", "components", "icons"]
    },
    "icons": {
      "name": "Hemantix — Icons",
      "file_key": "OPQRSTUVWXYZABCDEFGHIJ",
      "url": "https://www.figma.com/file/OPQRSTUVWXYZABCDEFGHIJ/Hemantix-Icons",
      "consumes": ["foundations"]
    }
  },
  "publish_order": ["icons", "foundations", "components", "patterns"]
}
```

## Page structure within each file

### Foundations file pages

1. `Cover` — DS name, version, contributors, status legend, links
2. `Color` — primitive swatches, semantic swatches (per mode), contrast check matrices
3. `Typography` — type ramp visualized, line-height + tracking annotations
4. `Spacing` — spacing scale visualized as vertical bars
5. `Radius` — radius scale visualized as squares
6. `Elevation` — elevation ramp visualized
7. `Grid` — column grid examples per breakpoint
8. `Variables` — admin-style listing of all variables (auto-organized by collection)

### Components file pages

1. `Cover` — version, status legend, component matrix
2. One page per family: `Actions` (Button, IconButton, Link), `Inputs` (TextInput, Select, Checkbox, Radio, Toggle), `Surfaces` (Card, Modal, Panel, Sheet), `Navigation` (Tabs, Breadcrumb, Pagination, Menu), `Feedback` (Alert, Toast, Tooltip, ProgressBar, Skeleton), `Data Display` (Table, Tag, Badge, Avatar)
3. `Candidates` — components under construction (not published)
4. `Deprecated` — legacy components marked for removal

### Patterns file pages

1. `Cover`
2. One page per pattern category: `Forms`, `Empty States`, `Onboarding`, `Authentication`, `Error Handling`, `Data Density`

### Icons file pages

1. `Cover`
2. `System Icons` (16/20/24/32 grid)
3. `Brand Icons` (logo lockups, marks)
4. `Illustration Spot` (small contextual illustrations)

## Cover page templates

Every file has a Cover page. The skill auto-generates these with:

- DS name + logo (if provided)
- Version + last-updated timestamp
- Status legend: 🟢 Stable · 🟡 Beta · 🔴 Deprecated · 🔵 Candidate
- Library description (~100 words)
- Contributors list (from manifest or input)
- Links to companion documentation site / Storybook
- Code Connect status badge (% of components linked)

## Publish order

When publishing a multi-file library for the first time:

1. **Icons first** — no upstream dependencies; safest to publish.
2. **Foundations next** — depends only on Icons (for icon-set typography swatches).
3. **Components** — depends on Foundations + Icons.
4. **Patterns** — depends on all three.

Subsequent publishes follow the same dependency order. The skill's `library-registry.json` tracks `publish_order` explicitly.

## Anti-patterns to avoid

| Anti-pattern | Why it's bad |
|---|---|
| Variables defined in Components or Patterns files | They can't be consumed elsewhere; defeats the architecture |
| Cross-file component instances embedded in Foundations | Creates circular dependency |
| One mega-file with 10k+ nodes | Slow rendering, hard to publish incrementally |
| Hard-coded colors in components | Components can't follow theme changes |
| Icon SVGs imported as raw nodes, not components | Cannot be swapped via instance-swap |

`PUBLISH_AUDIT` checks for each of these.

---

End of reference.
