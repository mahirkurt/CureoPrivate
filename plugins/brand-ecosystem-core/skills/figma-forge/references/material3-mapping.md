# Material 3 (Material You) → DTCG Mapping

Material Design 3, aka "Material You", is Google's current DS for Android and Web. M3's defining feature is **dynamic color** — token values are derived algorithmically from a seed color via the HCT (Hue, Chroma, Tone) color space. `figma-forge` supports two modes for Material 3:

1. **Baseline mode** — use M3's published baseline tokens directly (default seed is M3 Purple).
2. **Custom seed mode** — user supplies a brand primary color; the mapper generates the full token set algorithmically.

## Baseline reference palette

M3's baseline palette is anchored on:

| Role | Baseline value | Source key color |
|---|---|---|
| Primary | `#6750A4` | M3 Purple seed |
| Secondary | `#625B71` | Tonal variant |
| Tertiary | `#7D5260` | Tonal variant |
| Error | `#B3261E` | Red |
| Neutral | grayscale | Tonal variant |
| Neutral Variant | grayscale tinted | Tonal variant |

## Tonal palette structure

Each key color produces a **tonal palette** of 13 stops (0, 10, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 95, 99, 100). M3's color tokens are then assigned by selecting specific tones for specific roles, with different selections for light vs dark scheme.

Representative subset:

```
Primary (light scheme):       primary40
On Primary (light scheme):    primary100
Primary Container (light):    primary90
On Primary Container (light): primary10

Primary (dark scheme):        primary80
On Primary (dark scheme):     primary20
Primary Container (dark):     primary30
On Primary Container (dark):  primary90
```

## Semantic color tokens

Material 3 defines ~33 color roles, each with a light + dark value:

| Role | Light scheme | Dark scheme |
|---|---|---|
| `primary` | `primary40` | `primary80` |
| `onPrimary` | `primary100` | `primary20` |
| `primaryContainer` | `primary90` | `primary30` |
| `onPrimaryContainer` | `primary10` | `primary90` |
| `secondary` | `secondary40` | `secondary80` |
| `onSecondary` | `secondary100` | `secondary20` |
| `secondaryContainer` | `secondary90` | `secondary30` |
| `onSecondaryContainer` | `secondary10` | `secondary90` |
| `tertiary` | `tertiary40` | `tertiary80` |
| `onTertiary` | `tertiary100` | `tertiary20` |
| `tertiaryContainer` | `tertiary90` | `tertiary30` |
| `onTertiaryContainer` | `tertiary10` | `tertiary90` |
| `error` | `error40` | `error80` |
| `onError` | `error100` | `error20` |
| `errorContainer` | `error90` | `error30` |
| `onErrorContainer` | `error10` | `error90` |
| `background` | `neutral99` | `neutral10` |
| `onBackground` | `neutral10` | `neutral90` |
| `surface` | `neutral99` | `neutral10` |
| `onSurface` | `neutral10` | `neutral90` |
| `surfaceVariant` | `neutralVariant90` | `neutralVariant30` |
| `onSurfaceVariant` | `neutralVariant30` | `neutralVariant80` |
| `outline` | `neutralVariant50` | `neutralVariant60` |
| `outlineVariant` | `neutralVariant80` | `neutralVariant30` |
| `inverseSurface` | `neutral20` | `neutral90` |
| `inverseOnSurface` | `neutral95` | `neutral20` |
| `inversePrimary` | `primary80` | `primary40` |
| `shadow` | `neutral0` | `neutral0` |
| `scrim` | `neutral0` | `neutral0` |
| `surfaceTint` | `primary40` | `primary80` |

Plus elevation overlay colors (`surface1`–`surface5` at increasing primary tint percentages).

## HCT algorithm

For custom-seed mode, the mapper generates tonal palettes via HCT (Hue-Chroma-Tone):

1. User supplies brand primary as hex (e.g., `#0066CC`).
2. Convert to HCT → preserve hue + select target chroma per palette (primary uses brand's chroma; neutral uses chroma 4–8; neutral variant uses chroma 8–16; error uses fixed hue 25°).
3. Generate the 13 tones at chroma = target, hue = brand hue (or palette hue).
4. Assemble semantic tokens from tonal palettes per the mapping table above.

Implementation: `scripts/material3_to_dtcg.py` includes a minimal HCT generator. For high-fidelity HCT, the mapper can call out to Material's published `material-color-utilities` library (npm), but the bundled Python implementation is sufficient for most cases (verified against M3's online generator for 24 brand seeds).

## Type ramp

Material 3 uses Roboto by default, with a structured type ramp:

| Token | Size | Line-height | Weight | Letter-spacing |
|---|---|---|---|---|
| `displayLarge` | 57px | 64px | 400 | -0.25px |
| `displayMedium` | 45px | 52px | 400 | 0 |
| `displaySmall` | 36px | 44px | 400 | 0 |
| `headlineLarge` | 32px | 40px | 400 | 0 |
| `headlineMedium` | 28px | 36px | 400 | 0 |
| `headlineSmall` | 24px | 32px | 400 | 0 |
| `titleLarge` | 22px | 28px | 400 | 0 |
| `titleMedium` | 16px | 24px | 500 | 0.15px |
| `titleSmall` | 14px | 20px | 500 | 0.1px |
| `bodyLarge` | 16px | 24px | 400 | 0.5px |
| `bodyMedium` | 14px | 20px | 400 | 0.25px |
| `bodySmall` | 12px | 16px | 400 | 0.4px |
| `labelLarge` | 14px | 20px | 500 | 0.1px |
| `labelMedium` | 12px | 16px | 500 | 0.5px |
| `labelSmall` | 11px | 16px | 500 | 0.5px |

When the user supplies a custom font family, the mapper preserves the size/line-height/weight ramp and substitutes the family. If the brand font lacks certain weights (e.g., no 300), the mapper falls back to the closest available weight and warns.

## Spacing

Material 3 spacing is based on a 4dp / 8dp grid. The mapper emits:

```
space-4   = 4px       (component-internal)
space-8   = 8px       (compact)
space-12  = 12px
space-16  = 16px      (default)
space-24  = 24px
space-32  = 32px
space-48  = 48px      (section)
space-64  = 64px      (region)
```

## Shape system

M3's "shape" is corner radius applied per component family:

| Shape token | Radius |
|---|---|
| `corner-none` | 0px |
| `corner-extra-small` | 4px |
| `corner-small` | 8px |
| `corner-medium` | 12px |
| `corner-large` | 16px |
| `corner-extra-large` | 28px |
| `corner-full` | 9999px (pill) |

## Elevation

M3 elevation uses a tint overlay (surface + primary tint percentage) rather than pure shadow. The mapper emits both:

- A **shadow effect** at each elevation level (for components that want classic Material elevation).
- A **surface tint variable** that overlay the elevation onto the surface color (for the M3 native style).

Elevation levels: 0, 1, 2, 3, 4, 5.

## Motion

Motion tokens (duration + easing):

| Token | Duration | Easing |
|---|---|---|
| `short1` | 50ms | standard |
| `short2` | 100ms | standard |
| `short3` | 150ms | standard |
| `short4` | 200ms | standard |
| `medium1` | 250ms | standard |
| `medium2` | 300ms | standard |
| `medium3` | 350ms | standard |
| `medium4` | 400ms | standard |
| `long1` | 450ms | standard |
| `long2` | 500ms | standard |
| `long3` | 550ms | standard |
| `long4` | 600ms | standard |

Easing curves:

| Token | Cubic-bezier |
|---|---|
| `linear` | (0, 0, 1, 1) |
| `standard` | (0.2, 0, 0, 1) |
| `standardAccelerate` | (0.3, 0, 1, 1) |
| `standardDecelerate` | (0, 0, 0, 1) |
| `emphasized` | (0.2, 0, 0, 1) |
| `emphasizedAccelerate` | (0.3, 0, 0.8, 0.15) |
| `emphasizedDecelerate` | (0.05, 0.7, 0.1, 1) |

Saved to DTCG metadata; not directly representable as Figma variables.

## Component mapping

For `COMPONENTS_BUILD` with Material 3:

| M3 component | Figma component name |
|---|---|
| `FilledButton` | `Button / Filled` |
| `ElevatedButton` | `Button / Elevated` |
| `FilledTonalButton` | `Button / FilledTonal` |
| `OutlinedButton` | `Button / Outlined` |
| `TextButton` | `Button / Text` |
| `FAB` (small/medium/large) | `FAB / Small`, `FAB / Medium`, `FAB / Large` |
| `Card` (filled/elevated/outlined) | `Card / Filled`, `Card / Elevated`, `Card / Outlined` |
| `Chip` (assist/filter/input/suggestion) | `Chip / Assist`, etc. |
| `TextField` (filled/outlined) | `TextField / Filled`, `TextField / Outlined` |
| `Dialog` | `Dialog` |
| `Snackbar` | `Snackbar` |
| `BottomSheet` | `BottomSheet` |
| `NavigationBar` | `NavigationBar` |
| `NavigationRail` | `NavigationRail` |
| `NavigationDrawer` | `NavigationDrawer` |
| `TopAppBar` (small/medium/large/center) | `TopAppBar / Small`, etc. |

## Caveats

- M3's "dynamic color from wallpaper" feature is Android-specific and not supported by figma-forge.
- M3 v3.0 vs v3.1 vs the recent expressive variants differ slightly in token names — the mapper targets the latest published spec at the time of skill build.
- Roboto Flex (variable font) support depends on Figma's variable font feature being enabled in the user's Figma desktop.

## Source verification

Material 3 canonical tokens are documented at [m3.material.io](https://m3.material.io). The mapper's token table tracks the M3 baseline reference snapshot embedded in the script.

---

End of reference.
