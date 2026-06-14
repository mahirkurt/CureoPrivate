# Tailwind CSS (v3 + v4) → DTCG Mapping

Tailwind CSS is a utility-first CSS framework. While not a "design system" in the strict component-library sense, Tailwind's **token scales** (colors, spacing, type, radius) are widely adopted as DS primitives. `figma-forge` includes Tailwind mappers for both v3 (config-based) and v4 (CSS `@theme` based).

## Tailwind v3 vs v4 — what's different

| Aspect | Tailwind v3 | Tailwind v4 |
|---|---|---|
| Configuration | `tailwind.config.js` (CommonJS) | CSS `@theme` directive in `app.css` |
| Color format | hex strings | hex strings + `oklch()` recommended |
| Token reference | `theme('colors.blue.500')` | CSS variables `var(--color-blue-500)` |
| Extension | `extend: { ... }` to add | `@theme { ... }` for full + extend |
| Default theme | spread imports needed | inline defaults; override with `@theme` |

`figma-forge` handles both; the mapper detects which version by source format.

## Color palette

Tailwind ships with a comprehensive default color palette. Representative subset:

```
slate-50  #F8FAFC    slate-500  #64748B    slate-950  #020617
gray-50   #F9FAFB    gray-500   #6B7280    gray-950   #030712
zinc-50   #FAFAFA    zinc-500   #71717A    zinc-950   #09090B
neutral-50 #FAFAFA   neutral-500 #737373   neutral-950 #0A0A0A
stone-50  #FAFAFA    stone-500  #78716C    stone-950  #0C0A09

red-50    #FEF2F2    red-500    #EF4444    red-950    #450A0A
orange-50 #FFF7ED    orange-500 #F97316    orange-950 #431407
amber-50  #FFFBEB    amber-500  #F59E0B    amber-950  #451A03
yellow-50 #FEFCE8    yellow-500 #EAB308    yellow-950 #422006
lime-50   #F7FEE7    lime-500   #84CC16    lime-950   #1A2E05
green-50  #F0FDF4    green-500  #22C55E    green-950  #052E16
emerald-50 #ECFDF5   emerald-500 #10B981   emerald-950 #022C22
teal-50   #F0FDFA    teal-500   #14B8A6    teal-950   #042F2E
cyan-50   #ECFEFF    cyan-500   #06B6D4    cyan-950   #083344
sky-50    #F0F9FF    sky-500    #0EA5E9    sky-950    #082F49
blue-50   #EFF6FF    blue-500   #3B82F6    blue-950   #172554
indigo-50 #EEF2FF    indigo-500 #6366F1    indigo-950 #1E1B4B
violet-50 #F5F3FF    violet-500 #8B5CF6    violet-950 #2E1065
purple-50 #FAF5FF    purple-500 #A855F7    purple-950 #3B0764
fuchsia-50 #FDF4FF   fuchsia-500 #D946EF   fuchsia-950 #4A044E
pink-50   #FDF2F8    pink-500   #EC4899    pink-950   #500724
rose-50   #FFF1F2    rose-500   #F43F5E    rose-950   #4C0519
```

Each hue family has 11 stops: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950. That's 22 hue families × 11 stops + 4 grays × 11 stops = 286 primitive colors.

The mapper emits all of them by default. `--filter` option allows trimming to a smaller subset.

## DTCG output (representative)

```json
{
  "color": {
    "blue": {
      "500": {
        "$value": "#3B82F6",
        "$type": "color"
      }
    }
  }
}
```

## Spacing scale

Tailwind's default spacing:

| Class | Value (rem at default base) | Pixels |
|---|---|---|
| `space-0` | 0 | 0 |
| `space-px` | 1px | 1 |
| `space-0.5` | 0.125rem | 2 |
| `space-1` | 0.25rem | 4 |
| `space-1.5` | 0.375rem | 6 |
| `space-2` | 0.5rem | 8 |
| `space-2.5` | 0.625rem | 10 |
| `space-3` | 0.75rem | 12 |
| `space-3.5` | 0.875rem | 14 |
| `space-4` | 1rem | 16 |
| `space-5` | 1.25rem | 20 |
| `space-6` | 1.5rem | 24 |
| `space-7` | 1.75rem | 28 |
| `space-8` | 2rem | 32 |
| `space-9` | 2.25rem | 36 |
| `space-10` | 2.5rem | 40 |
| `space-11` | 2.75rem | 44 |
| `space-12` | 3rem | 48 |
| `space-14` | 3.5rem | 56 |
| `space-16` | 4rem | 64 |
| `space-20` | 5rem | 80 |
| `space-24` | 6rem | 96 |
| `space-28` | 7rem | 112 |
| `space-32` | 8rem | 128 |
| `space-36` | 9rem | 144 |
| `space-40` | 10rem | 160 |
| `space-44` | 11rem | 176 |
| `space-48` | 12rem | 192 |
| `space-52` | 13rem | 208 |
| `space-56` | 14rem | 224 |
| `space-60` | 15rem | 240 |
| `space-64` | 16rem | 256 |
| `space-72` | 18rem | 288 |
| `space-80` | 20rem | 320 |
| `space-96` | 24rem | 384 |

For Figma, the mapper converts rem→px using a configurable base (default 16px = 1rem).

## Type scale

| Class | Size (rem) | Pixels | Line-height (rem) |
|---|---|---|---|
| `text-xs` | 0.75rem | 12 | 1rem (16) |
| `text-sm` | 0.875rem | 14 | 1.25rem (20) |
| `text-base` | 1rem | 16 | 1.5rem (24) |
| `text-lg` | 1.125rem | 18 | 1.75rem (28) |
| `text-xl` | 1.25rem | 20 | 1.75rem (28) |
| `text-2xl` | 1.5rem | 24 | 2rem (32) |
| `text-3xl` | 1.875rem | 30 | 2.25rem (36) |
| `text-4xl` | 2.25rem | 36 | 2.5rem (40) |
| `text-5xl` | 3rem | 48 | 1 (line-height = font-size) |
| `text-6xl` | 3.75rem | 60 | 1 |
| `text-7xl` | 4.5rem | 72 | 1 |
| `text-8xl` | 6rem | 96 | 1 |
| `text-9xl` | 8rem | 128 | 1 |

Font family: default is system-ui stack; Tailwind v4 uses CSS variables for this. Mapper picks the first family from the stack for Figma (e.g., `system-ui` → `Inter` as a common practical substitute).

## Font weights

| Class | Weight |
|---|---|
| `font-thin` | 100 |
| `font-extralight` | 200 |
| `font-light` | 300 |
| `font-normal` | 400 |
| `font-medium` | 500 |
| `font-semibold` | 600 |
| `font-bold` | 700 |
| `font-extrabold` | 800 |
| `font-black` | 900 |

## Radius

| Class | Value |
|---|---|
| `rounded-none` | 0 |
| `rounded-sm` | 0.125rem (2px) |
| `rounded` (default) | 0.25rem (4px) |
| `rounded-md` | 0.375rem (6px) |
| `rounded-lg` | 0.5rem (8px) |
| `rounded-xl` | 0.75rem (12px) |
| `rounded-2xl` | 1rem (16px) |
| `rounded-3xl` | 1.5rem (24px) |
| `rounded-full` | 9999px |

## Shadows

```
shadow-sm:   0 1px 2px 0 rgb(0 0 0 / 0.05)
shadow:      0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)
shadow-md:   0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)
shadow-lg:   0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)
shadow-xl:   0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)
shadow-2xl:  0 25px 50px -12px rgb(0 0 0 / 0.25)
shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05)
shadow-none: 0 0 #0000
```

Multi-shadow specifications map to multi-shadow effect styles in Figma.

## Reading Tailwind v3 config

The mapper's `--input tailwind.config.js` flag triggers v3 parsing:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#EFF6FF',
          500: '#0066CC',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    }
  }
}
```

The mapper:
1. Executes the config in a sandboxed Node.js subprocess.
2. Resolves the full theme by merging default + extend.
3. Walks the resolved object and converts each leaf to a DTCG token.

## Reading Tailwind v4 `@theme`

```css
@theme {
  --color-brand-50: oklch(0.971 0.013 244);
  --color-brand-500: oklch(0.546 0.219 244);

  --font-sans: 'Inter Variable', system-ui, sans-serif;

  --radius-md: 0.5rem;
}
```

The mapper parses the CSS, extracts `--*` declarations, converts `oklch()` to hex via a CSS Color Module 4 converter (built-in), and emits DTCG.

## Composite components

Tailwind itself doesn't ship components — only utilities. For `COMPONENTS_BUILD` mode with Tailwind as source, `figma-forge` builds a **default component set** using Tailwind tokens, following a generic "tailwind-styled" component spec inspired by `shadcn/ui`'s patterns (rounded-md, shadow-sm, border, etc.).

The user can override the default component set by providing a custom spec JSON.

## Caveats

- Tailwind's `arbitrary` utilities (`text-[24px]`, `bg-[#FF0000]`) cannot be modeled as tokens; they're per-instance overrides.
- The default Tailwind palette is opinionated; many teams customize it heavily. The mapper handles customized configs but the result depends on what the team retained vs replaced.
- Tailwind v4's `@theme` allows mid-document `--*` overrides; the mapper takes a snapshot of the resolved theme at parse time.

---

End of reference.
