# Naming Conventions

Consistent naming is the single highest-leverage habit in a design system library — it determines searchability, code-side mapping ease, and long-term maintainability. `figma-forge` supports three industry-standard conventions plus a custom override.

## Three canonical conventions

### Carbon-style (kebab-case tokens, PascalCase components)

```
Tokens (kebab-case, dot-separated semantic):
  color.background
  color.layer-01
  color.text-primary
  color.support-error
  spacing-01
  body-compact-01

Components (PascalCase):
  Button
  TextInput
  StructuredList
  TopBar

Variant properties (camelCase):
  variant: primary | secondary | tertiary
  size: sm | md | lg
  state: default | hover | pressed
```

Recommended when forging Carbon-based or Carbon-inspired systems.

### Material-style (camelCase tokens, PascalCase components)

```
Tokens (camelCase, hierarchical):
  surfaceContainer
  surfaceContainerHigh
  onPrimary
  outlineVariant
  spaceMedium
  cornerLarge

Components (PascalCase):
  FilledButton
  OutlinedButton
  FilledTonalButton
  NavigationBar
  TopAppBar

Variant properties (camelCase):
  variant: filled | tonal | outlined | elevated
  size: small | medium | large
  enabled: true | false
```

Recommended when forging Material 3-based systems.

### BEM-style (block__element--modifier)

Mostly used in tokens; rarely in component names today.

```
Tokens:
  color-button--primary--default
  color-button--primary--hover
  color-button--primary--disabled

  spacing-card__padding
  spacing-card__gap

Components (often kebab or Pascal):
  Button
  Card
  Modal
```

### Custom override

If the user's existing DS uses a different convention, the skill follows it literally — preserving the exact name shape. This is the right choice for legacy DS migrations.

## Variable naming inside Figma

Figma variables use **forward slashes** for hierarchy. `figma-forge` maps DTCG dot-paths to slashes:

| DTCG path | Figma variable name |
|---|---|
| `color.blue.500` | `color/blue/500` |
| `color.action.primary.bg` | `color/action/primary/bg` |
| `dimension.spacing.06` | `dimension/spacing/06` |
| `font.family.sans` | `font/family/sans` |
| `typography.body-01.fontSize` | `typography/body-01/fontSize` (composite leaf) |

The slash hierarchy auto-groups variables in Figma's UI, so following this convention is essential for navigability.

## Mode naming

Figma supports multiple modes per variable collection. The skill normalizes mode names:

| Concept | Mode name |
|---|---|
| Light theme | `Light` |
| Dark theme | `Dark` |
| Default | `Default` |
| High contrast | `High contrast` |
| Reduced motion | `Reduced motion` |
| Brand A vs Brand B | `Brand A` / `Brand B` (literal brand names) |
| Density compact | `Compact` |
| Density comfortable | `Comfortable` |
| RTL | `RTL` |

## Component naming taxonomy

For component name uniqueness across the library, the skill uses a `Family / Component` hierarchy. Family names are normalized:

| Family | Components |
|---|---|
| `Actions` | Button, IconButton, Link, MenuButton, SplitButton, FAB |
| `Inputs` | TextInput, NumberInput, Select, Combobox, Checkbox, Radio, Toggle, Slider, Stepper, ColorPicker, DatePicker, FileUpload |
| `Surfaces` | Card, Modal, Panel, Sheet, Drawer, Popover |
| `Navigation` | Tabs, Breadcrumb, Pagination, Menu, Sidebar, TopBar, Stepper (workflow) |
| `Feedback` | Alert, Toast, Tooltip, ProgressBar, ProgressCircle, Skeleton, Spinner, EmptyState |
| `Data Display` | Table, Tag, Badge, Avatar, List, Tree, Timeline, Stats, Chart |
| `Layout` | Container, Grid, Stack, Divider, AspectRatio |
| `Media` | Image, Video, AudioPlayer, Map |
| `Typography` | Heading, Text, Code, Quote |
| `Brand` | Logo, LogoLockup, BrandMark |

When the user provides a component spec, the skill validates family names. Unknown families generate a warning (not error) — the user may legitimately need a new family.

## File naming

| Pattern | Example |
|---|---|
| `<DS Name> — Foundations` | `Hemantix — Foundations` |
| `<DS Name> — Components` | `Hemantix — Components` |
| `<DS Name> — Patterns` | `Hemantix — Patterns` |
| `<DS Name> — Icons` | `Hemantix — Icons` |

Note: em-dash (—) not hyphen. The em-dash is recognizable and visually distinct from in-file names. The skill always uses em-dash unless the user explicitly requests a different separator.

## Page naming within a file

Use sentence case with spaces:

```
Foundations file:
  - Cover
  - Color
  - Typography
  - Spacing
  - Radius
  - Elevation
  - Grid
  - Variables

Components file:
  - Cover
  - Actions
  - Inputs
  - Surfaces
  - Navigation
  - Feedback
  - Data Display
  - Layout
  - Candidates
  - Deprecated
```

## Layer naming inside components

For nested layers inside a component (for designers exploring the structure):

| Layer purpose | Name |
|---|---|
| Outer auto-layout frame | `Container` |
| Visible background paint | `Background` |
| Border element if separate | `Border` |
| Main text | `Label` |
| Helper or secondary text | `HelperText`, `Description` |
| Icon slot | `Icon`, `LeadingIcon`, `TrailingIcon` |
| Generic content slot | `Slot`, `Slot — Header`, etc. |
| Internal sub-frame | `Group — <purpose>` |

Layer names appear in code via `figma.string(layerName)` so consistency matters.

## Variant property naming

Variant property keys are **camelCase**, values are **lowercase kebab or single-word**:

```
size: sm | md | lg | xl
variant: primary | secondary | tertiary | ghost | danger
state: default | hover | pressed | disabled | focus
iconLeading: true | false
iconTrailing: true | false
fullWidth: true | false
```

Avoid:
- `Size` (capitalized — Figma displays as-is, looks inconsistent)
- `is_disabled` (snake_case — not standard)
- `Variant_Primary` (PascalCase value with prefix — overengineered)

## Description text

Component descriptions appear in Figma's Assets panel and dev mode. Conventions:

- First sentence: what the component is (e.g., "Primary interactive element for triggering actions.").
- Subsequent sentences: when to use, when not to use.
- Plain prose; no markdown formatting that Figma won't render.
- Length target: 60–200 characters.

## Keyword strategy

Component keywords are searched in Figma's Assets panel. Include:

- The component name as a single token (`button`)
- Common synonyms (`cta`, `action`)
- Family name (`actions`)
- Use-case verbs (`click`, `submit`, `confirm`)
- Visual descriptors (`primary`, `rounded`)

The skill auto-generates keywords from family + spec and lets the user augment.

## Convention selection during SCAFFOLD

When `SCAFFOLD` mode begins, the skill asks:

> Which naming convention will this DS use?
> 1. Carbon-style (kebab tokens, PascalCase components)
> 2. Material-style (camelCase tokens, PascalCase components)
> 3. BEM tokens, PascalCase components
> 4. Custom (preserve names from input spec literally)

The selection is recorded in `library-registry.json` and applied to every subsequent mode's outputs.

---

End of reference.
