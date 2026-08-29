---
name: Hyper-Refined Modern Builder
colors:
  surface: '#12131a'
  surface-dim: '#12131a'
  surface-bright: '#383941'
  surface-container-lowest: '#0d0e15'
  surface-container-low: '#1a1b22'
  surface-container: '#1e1f26'
  surface-container-high: '#292931'
  surface-container-highest: '#33343c'
  on-surface: '#e3e1ec'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#e3e1ec'
  inverse-on-surface: '#2f3038'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#ca8100'
  on-tertiary-container: '#3e2400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#12131a'
  on-background: '#e3e1ec'
  surface-variant: '#33343c'
typography:
  display:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: 0em
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.02em
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  gutter: 16px
  row-height-compact: 32px
  row-height-standard: 44px
---

## Brand & Style

The design system is engineered for high-performance B2B workflows, prioritizing precision, technical authority, and extreme information density. It targets power users who require speed and clarity when managing complex AI-driven recruitment pipelines.

The aesthetic follows a **Hyper-Refined Modern** approach, drawing inspiration from high-end developer tools and command-line interfaces. Key characteristics include:
- **Precision Craft:** 1px hairline borders and razor-sharp alignment grids.
- **High Density:** Optimized spatial efficiency to reduce scrolling and maximize data visibility.
- **Technical Sophistication:** A blend of geometric sans-serifs with monospaced accents for a "builder" feel.
- **Functional Transparency:** Use of glassmorphism for structural navigation to maintain context while browsing deep data sets.

## Colors

The palette is designed for prolonged professional use, focusing on deep contrast and intentional accentuation.

- **Primary Indigo:** Used exclusively for primary actions, active states, and critical paths.
- **The Obsidian Base:** In dark mode, `#090d16` provides a "true-black" feel that allows card surfaces to pop with subtle elevation.
- **Semantic Status:** Success (Emerald) and Warning (Amber) are used sparingly for status pips and data indicators to maintain the monochrome technical aesthetic.
- **Borders:** Must be 1px. In dark mode, use Slate-800 with 80% opacity to ensure they feel like "hairlines" rather than heavy separators.

## Typography

Typography is the primary driver of hierarchy. 

- **Headlines:** Use Plus Jakarta Sans with tight tracking (`-0.02em`) to create a compact, punchy editorial feel.
- **Body:** Standardized at 13px-14px to support high information density. Inter's tall x-height ensures legibility at these smaller sizes.
- **Technical Data:** Use JetBrains Mono for candidate IDs, skill scores, time stamps, and metadata. This reinforces the "AI-driven" and "precision" nature of the tool.

## Layout & Spacing

This design system utilizes a **Fixed Grid** model for primary dashboard structures and a **Flexible IDE** layout for outreach and management tools.

- **The 4px Rule:** All spacing must be a multiple of 4px. 
- **IDE Layout:** Use a three-pane system (Navigation | Main Feed | Inspector) to keep all tools within reach. Panels should be resizable with 1px dividers.
- **Density:** Table rows should use `row-height-compact` (32px) for data-heavy views.
- **Sticky Glass:** Navigation headers must use a backdrop-blur (minimum 12px) with a semi-transparent background to allow content to bleed through while scrolling.

## Elevation & Depth

Depth is achieved through **Tonal Layering** rather than traditional shadows. 

- **Level 0 (Background):** Obsidian (#090d16).
- **Level 1 (Card/Panel):** Slate-900/Card Surface (#161f33). 
- **Borders:** Instead of large drop shadows, use 1px inner borders (rim lights) and subtle outer borders.
- **Overlays:** Modals and menus use a slightly darker backdrop-blur to isolate the focus area without losing the global context.

## Shapes

The shape language is disciplined and geometric.

- **Cards:** 8px radius provides a modern container feel without becoming "bubbly."
- **Interactive Elements:** Buttons at 6px and smaller elements like Tags or Pips at 4px create a nested visual hierarchy where smaller items appear sharper than their containers.

## Components

- **Segmented Controls:** Used for high-level navigation within panels. These should be flush with the panel header, using a subtle background fill for the active state.
- **Buttons:** 1px border. Primary buttons use the Indigo fill with white text. Secondary buttons are ghost-style with a 1px border that brightens on hover.
- **Input Fields:** Minimalist design with 1px borders. Focus state is indicated by a primary color border glow (no thick rings).
- **Visual Skill Matrix:** A grid-based component using monospaced labels and tiny colored pips (Success/Warning/Neutral) to represent AI-graded skill levels.
- **Vertical Timeline Nodes:** 1px vertical lines connecting small circular nodes (4px) to represent candidate history or pipeline progression.
- **Kanban Pipeline:** High-density cards (no internal padding larger than 12px) with 1px borders, arranged in columns with sticky headers.
- **Tables:** No vertical lines. Only 1px horizontal dividers. On hover, rows should highlight with a subtle shift in surface color.