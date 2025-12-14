# Podcast Generator — Style Guide

## Design Philosophy: "Academic Greenhouse"

A space where knowledge grows organically. Scholarly warmth meets botanical freshness. The interface feels like a cozy study filled with plants and old books — but with modern, clean interactions.

---

## Color Palette

### Primary Colors
| Name | Hex | Usage |
|------|-----|-------|
| **Forest** | `#4A6B5D` | Primary actions, headers, key UI elements |
| **Sage** | `#6B8F7A` | Secondary buttons, hover states, accents |
| **Deep Forest** | `#2C3E35` | Text, dark backgrounds, emphasis |

### Accent Colors
| Name | Hex | Usage |
|------|-----|-------|
| **Parchment Gold** | `#C4A77D` | Highlights, badges, special elements |
| **Warm Amber** | `#D4A853` | Active states, notifications |
| **Terracotta** | `#C17C5E` | Warnings, destructive actions (muted) |

### Neutral Colors
| Name | Hex | Usage |
|------|-----|-------|
| **Cream** | `#F5F2EB` | Main background |
| **Warm White** | `#FAF9F6` | Cards, elevated surfaces |
| **Stone** | `#E8E4DC` | Borders, dividers |
| **Charcoal** | `#3D3D3D` | Body text |
| **Muted** | `#7A7A7A` | Secondary text, placeholders |

---

## Typography

### Font Stack

**Display / Headings**: Fraunces
- A variable serif with organic, quirky character
- Use optical sizing for different scales
- Soft axis for a warmer feel

```css
font-family: 'Fraunces', Georgia, serif;
```

**Body / UI**: Source Serif 4
- Highly readable serif for longer text
- Warm and scholarly without being stuffy

```css
font-family: 'Source Serif 4', Georgia, serif;
```

**Mono / Code**: JetBrains Mono
- For technical details, paper IDs, timestamps

```css
font-family: 'JetBrains Mono', monospace;
```

### Type Scale

| Name | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| Display | 3rem (48px) | 600 | 1.1 | Hero headings |
| H1 | 2.25rem (36px) | 600 | 1.2 | Page titles |
| H2 | 1.75rem (28px) | 500 | 1.25 | Section headers |
| H3 | 1.25rem (20px) | 500 | 1.3 | Card titles |
| Body | 1rem (16px) | 400 | 1.6 | Main content |
| Small | 0.875rem (14px) | 400 | 1.5 | Captions, meta |
| Tiny | 0.75rem (12px) | 500 | 1.4 | Labels, badges |

---

## Spacing System

Based on 4px grid, using powers of 2:

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | 4px | Tight gaps |
| `--space-2` | 8px | Icon padding, small gaps |
| `--space-3` | 12px | Button padding |
| `--space-4` | 16px | Card padding, standard gaps |
| `--space-5` | 24px | Section padding |
| `--space-6` | 32px | Large gaps |
| `--space-8` | 48px | Section margins |
| `--space-10` | 64px | Page sections |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 4px | Buttons, inputs |
| `--radius-md` | 8px | Cards, modals |
| `--radius-lg` | 16px | Large containers |
| `--radius-full` | 9999px | Pills, avatars |

---

## Shadows

Warm, soft shadows with slight green tint:

```css
--shadow-sm: 0 1px 2px rgba(44, 62, 53, 0.06);
--shadow-md: 0 4px 12px rgba(44, 62, 53, 0.08);
--shadow-lg: 0 8px 24px rgba(44, 62, 53, 0.12);
--shadow-xl: 0 16px 48px rgba(44, 62, 53, 0.16);
```

---

## Motion & Animation

### Principles
- Organic, growing movements — not mechanical
- Elements "bloom" into view
- Subtle hover states that feel alive
- Staggered reveals for lists

### Timing
```css
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--duration-fast: 150ms;
--duration-normal: 300ms;
--duration-slow: 500ms;
```

### Key Animations

**Bloom In** — For cards and elements appearing:
```css
@keyframes bloom-in {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
```

**Unfurl** — For expandable content:
```css
@keyframes unfurl {
  from {
    opacity: 0;
    max-height: 0;
    transform: scaleY(0.8);
    transform-origin: top;
  }
  to {
    opacity: 1;
    max-height: 500px;
    transform: scaleY(1);
  }
}
```

**Pulse Grow** — For loading/processing states:
```css
@keyframes pulse-grow {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.05); opacity: 1; }
}
```

---

## Component Patterns

### Buttons

**Primary Button**
- Background: `--color-forest`
- Text: white
- Hover: `--color-sage` with slight scale(1.02)
- Border-radius: `--radius-sm`
- Padding: `12px 24px`

**Secondary Button**
- Background: transparent
- Border: 2px solid `--color-forest`
- Text: `--color-forest`
- Hover: fill with `--color-forest`, text white

**Ghost Button**
- Background: transparent
- Text: `--color-forest`
- Hover: background `--color-stone`

### Cards

- Background: `--color-warm-white`
- Border: 1px solid `--color-stone`
- Border-radius: `--radius-md`
- Shadow: `--shadow-md` on hover
- Padding: `--space-5`

### Inputs

- Background: `--color-warm-white`
- Border: 2px solid `--color-stone`
- Focus: border-color `--color-forest`
- Border-radius: `--radius-sm`
- Padding: `12px 16px`

---

## Textures & Details

### Paper Texture
Subtle noise overlay on backgrounds for warmth:
```css
background-image: url("data:image/svg+xml,..."); /* noise pattern */
background-blend-mode: overlay;
```

### Botanical Accents
- Subtle leaf/vine SVG decorations in corners
- Growing line animations for loading states
- Organic blob shapes for backgrounds

### Grain Overlay
Light grain texture at 3-5% opacity for depth.

---

## Iconography

- Style: Outlined, 1.5px stroke
- Size: 20px default, 24px for emphasis
- Color: Inherit from parent
- Library: Lucide React (recommended)

---

## Responsive Breakpoints

| Name | Width | Usage |
|------|-------|-------|
| Mobile | < 640px | Single column |
| Tablet | 640px - 1024px | Two column |
| Desktop | > 1024px | Full layout |

---

## Accessibility

- Minimum contrast ratio: 4.5:1 for text
- Focus states: 2px solid `--color-parchment-gold` with 2px offset
- Motion: Respect `prefers-reduced-motion`
- Touch targets: Minimum 44x44px

---

## Example CSS Variables

```css
:root {
  /* Colors */
  --color-forest: #4A6B5D;
  --color-sage: #6B8F7A;
  --color-deep-forest: #2C3E35;
  --color-parchment: #C4A77D;
  --color-amber: #D4A853;
  --color-terracotta: #C17C5E;
  --color-cream: #F5F2EB;
  --color-warm-white: #FAF9F6;
  --color-stone: #E8E4DC;
  --color-charcoal: #3D3D3D;
  --color-muted: #7A7A7A;

  /* Typography */
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Source Serif 4', Georgia, serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-8: 48px;
  --space-10: 64px;

  /* Borders */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(44, 62, 53, 0.06);
  --shadow-md: 0 4px 12px rgba(44, 62, 53, 0.08);
  --shadow-lg: 0 8px 24px rgba(44, 62, 53, 0.12);

  /* Motion */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --duration-fast: 150ms;
  --duration-normal: 300ms;
}
```
