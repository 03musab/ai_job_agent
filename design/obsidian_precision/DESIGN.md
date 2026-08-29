---
name: Obsidian Precision
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1c1b1d'
  surface-container: '#201f22'
  surface-container-high: '#2a2a2c'
  surface-container-highest: '#353437'
  on-surface: '#e5e1e4'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#e5e1e4'
  inverse-on-surface: '#313032'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#c8c5ca'
  on-secondary: '#303033'
  secondary-container: '#47464a'
  on-secondary-container: '#b6b4b8'
  tertiary: '#ffb783'
  on-tertiary: '#4f2500'
  tertiary-container: '#d97721'
  on-tertiary-container: '#452000'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#e4e1e6'
  secondary-fixed-dim: '#c8c5ca'
  on-secondary-fixed: '#1b1b1e'
  on-secondary-fixed-variant: '#47464a'
  tertiary-fixed: '#ffdcc5'
  tertiary-fixed-dim: '#ffb783'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#703700'
  background: '#131315'
  on-background: '#e5e1e4'
  surface-variant: '#353437'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
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
  element-gap: 12px
  section-gap: 32px
  grid-columns: '12'
  gutter: 16px
---

## Brand & Style

This design system is built on the philosophy of **Hyper-Refined Modern Functionalism**. It targets a high-end B2B audience where precision, speed, and information density are paramount. The aesthetic rejects decorative trends like gradients or blurs in favor of razor-sharp alignment and structural clarity.

The visual language is defined by a "Deep Obsidian" environment, utilizing a tiered architectural approach to surfaces. High-contrast typography and subtle 1px hairline borders create a sense of mechanical quality and professional reliability. The emotional response is one of total control, sophisticated efficiency, and uncompromising utility.

## Colors

The palette is rooted in a monochromatic "Obsidian" scale to minimize cognitive load and emphasize content hierarchy. 

- **Primary:** Crisp Indigo (#6366f1) is used exclusively for primary actions, active states, and critical highlights.
- **Backgrounds:** The foundation is Deep Obsidian (#09090b).
- **Surfaces:** Use Rich Slate (#18181b) for secondary surfaces like sidebars or headers, and Surface Card (#27272a) for elevated workspace elements.
- **Borders:** A consistent 1px hairline (rgba(255,255,255,0.07)) must be applied to all container edges to define structure against the dark backgrounds.

## Typography

The typographic system balances character with utility. 

- **Headings:** Plus Jakarta Sans provides a modern, geometric feel. Tracking must be set to -0.02em (or -0.04em for larger displays) to maintain a compact, high-end editorial look.
- **Body:** Inter is used for all functional text and UI labels at 13px or 14px to ensure maximum legibility in high-density layouts.
- **Technical/Data:** JetBrains Mono is reserved for metadata, timestamps, code snippets, and status labels. It signals accuracy and a "pro" tool environment.

## Layout & Spacing

This design system employs a **Fixed-Fluid Hybrid Grid**. The workspace utilizes a 12-column grid with narrow 16px gutters to maximize usable area. 

The spacing rhythm is strictly based on a 4px baseline. High information density is prioritized; therefore, vertical padding in lists and tables should remain tight (8px to 12px). All elements must align to the grid to maintain "razor-sharp" visual integrity. Breakpoints occur at 768px (Tablet) and 1280px (Desktop), with the layout expanding to fill the screen while maintaining a maximum content width of 1600px for legibility.

## Elevation & Depth

Depth is achieved through **Tonal Layering** rather than shadows. 

1.  **Level 0 (Base):** Deep Obsidian (#09090b) - Used for the main application background.
2.  **Level 1 (Sub-navigation/Sidebar):** Rich Slate (#18181b) - Anchored surfaces that sit flush against the base.
3.  **Level 2 (Cards/Modals):** Surface Card (#27272a) - Active working areas.

Every elevation change must be reinforced by a 1px hairline border (rgba(255,255,255,0.07)). Shadows are prohibited, except for a single 10% black drop shadow on floating dropdown menus to slightly detach them from the underlying cards.

## Shapes

The shape language is conservative and disciplined. 

- **General UI Elements:** Use a "Soft" 4px to 8px radius.
- **Cards:** Maximum corner radius is 8px.
- **Buttons & Inputs:** Use a 6px radius for buttons and 4px for input fields to create a slightly sharper, more technical appearance compared to the outer containers.
- **Status Indicators:** Use 2px radius (near-sharp) for small status tags to distinguish them from interactive buttons.

## Components

- **Buttons:** Compact height (32px for standard, 40px for large). Primary buttons use Indigo (#6366f1) with white text. Secondary buttons use a transparent fill with a 1px border. No gradients.
- **Inputs:** Background should be Deep Obsidian (#09090b) to "recess" into the Surface Card. Borders brighten to 15% white on focus.
- **Cards:** Defined by Surface Card (#27272a) with a 1px hairline border. Headers within cards should have a subtle bottom border to separate title areas from content.
- **Data Tables:** High density. Row height 36px. Use JetBrains Mono for numeric data. Hover states should use a subtle highlight of Rich Slate (#18181b).
- **Chips/Tags:** Small, rectangular with 2px radius. Backgrounds should be low-opacity versions of the status color (e.g., 10% Indigo) with a solid 1px border.
- **Scrollbars:** Custom slim 4px wide bars, color #3f3f46, no track background.