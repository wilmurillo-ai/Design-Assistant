# Design Systems Reference

Use this reference for: token architecture, component specifications, variant systems, documentation
standards, contribution models, versioning, theming, cross-platform consistency, accessibility at scale,
and building comprehensive design systems for organizations or products.

---

## TABLE OF CONTENTS
1. Design System Architecture
2. Token System Design
3. Component Specification
4. Theming & Multi-Brand
5. Documentation Standards
6. Accessibility at Scale
7. Implementation Patterns

---

## 1. DESIGN SYSTEM ARCHITECTURE

### The Design System Pyramid

```
                    ┌──────────┐
                    │ PATTERNS │  Page layouts, flows, templates
                    ├──────────┤
                 ┌──┤COMPONENTS├──┐  Buttons, cards, modals, forms
                 │  ├──────────┤  │
              ┌──┤  │  TOKENS  │  ├──┐  Colors, spacing, type, motion
              │  │  ├──────────┤  │  │
           ┌──┤  │  │PRINCIPLES│  │  ├──┐  Brand values, design philosophy
           │  │  │  └──────────┘  │  │  │
           └──┴──┴────────────────┴──┴──┘
```

### Design System Scope

A complete design system includes:

1. **Design Principles**: The "why" — guiding philosophy, brand personality, accessibility commitment
2. **Design Tokens**: The "atoms" — colors, typography, spacing, shadows, motion, borders
3. **Components**: The "molecules" — buttons, inputs, cards, modals, navigation, tables
4. **Patterns**: The "organisms" — page layouts, form patterns, navigation patterns, data display
5. **Templates**: The "pages" — complete page compositions for common use cases
6. **Documentation**: The "manual" — usage guidelines, do's and don'ts, code examples
7. **Governance**: The "process" — contribution model, versioning, deprecation, support

---

## 2. TOKEN SYSTEM DESIGN

### Token Hierarchy

```
Global Tokens (raw values)
    ↓
Alias Tokens (semantic meaning)
    ↓
Component Tokens (specific usage)
```

**Example flow**:
```
Global:    --blue-500: #3b82f6
Alias:     --color-action-primary: var(--blue-500)
Component: --button-primary-bg: var(--color-action-primary)
```

### Complete Token Architecture

```css
/* ========================================
   TIER 1: GLOBAL TOKENS (Raw Values)
   ======================================== */

:root {
  /* Colors: Raw palette */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  --gray-950: #030712;

  --blue-50: #eff6ff;
  --blue-100: #dbeafe;
  --blue-500: #3b82f6;
  --blue-600: #2563eb;
  --blue-700: #1d4ed8;

  /* Add complete scales for all brand colors */

  /* Spacing: Raw scale */
  --space-0: 0;
  --space-px: 1px;
  --space-0-5: 2px;
  --space-1: 4px;
  --space-1-5: 6px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;

  /* Typography: Raw values */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  --font-size-5xl: 3rem;
  --font-size-6xl: 3.75rem;

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.15;
  --line-height-snug: 1.3;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* Borders */
  --radius-none: 0;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);

  /* Motion */
  --duration-instant: 100ms;
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --duration-slower: 600ms;
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ========================================
   TIER 2: ALIAS TOKENS (Semantic Meaning)
   ======================================== */

:root {
  /* Surface colors */
  --color-bg-primary: var(--gray-50);
  --color-bg-secondary: var(--gray-100);
  --color-bg-tertiary: var(--gray-200);
  --color-bg-inverse: var(--gray-900);
  --color-bg-brand: var(--blue-500);

  /* Text colors */
  --color-text-primary: var(--gray-900);
  --color-text-secondary: var(--gray-600);
  --color-text-tertiary: var(--gray-400);
  --color-text-inverse: white;
  --color-text-brand: var(--blue-600);
  --color-text-link: var(--blue-600);

  /* Border colors */
  --color-border-default: var(--gray-200);
  --color-border-strong: var(--gray-300);
  --color-border-brand: var(--blue-500);

  /* Action colors */
  --color-action-primary: var(--blue-600);
  --color-action-primary-hover: var(--blue-700);
  --color-action-secondary: var(--gray-100);
  --color-action-secondary-hover: var(--gray-200);
  --color-action-danger: #dc2626;

  /* Status colors */
  --color-status-success: #059669;
  --color-status-warning: #d97706;
  --color-status-error: #dc2626;
  --color-status-info: var(--blue-600);

  /* Semantic spacing */
  --spacing-component-padding: var(--space-4);
  --spacing-section-gap: var(--space-12);
  --spacing-page-margin: var(--space-6);
}

/* ========================================
   TIER 3: COMPONENT TOKENS (Usage-Specific)
   ======================================== */

:root {
  /* Button tokens */
  --button-height-sm: 32px;
  --button-height-md: 40px;
  --button-height-lg: 48px;
  --button-padding-x: var(--space-4);
  --button-border-radius: var(--radius-md);
  --button-font-size: var(--font-size-sm);
  --button-font-weight: var(--font-weight-medium);
  --button-primary-bg: var(--color-action-primary);
  --button-primary-bg-hover: var(--color-action-primary-hover);
  --button-primary-text: var(--color-text-inverse);

  /* Input tokens */
  --input-height: 40px;
  --input-padding-x: var(--space-3);
  --input-border-radius: var(--radius-md);
  --input-border-color: var(--color-border-default);
  --input-border-color-focus: var(--color-border-brand);
  --input-font-size: var(--font-size-sm);

  /* Card tokens */
  --card-padding: var(--space-6);
  --card-border-radius: var(--radius-lg);
  --card-border-color: var(--color-border-default);
  --card-bg: white;
  --card-shadow: var(--shadow-sm);
  --card-shadow-hover: var(--shadow-md);
}
```

---

## 3. COMPONENT SPECIFICATION

### Component Specification Template

For each component, document:

```
COMPONENT: [Name]

DESCRIPTION:
[What it does, when to use it]

ANATOMY:
[Visual breakdown of sub-elements]

VARIANTS:
- Primary / Secondary / Ghost / Danger
- Small / Medium / Large
- With icon / Without icon

STATES:
- Default / Hover / Focus / Active / Disabled / Loading / Error

PROPS (for code):
- variant: 'primary' | 'secondary' | 'ghost' | 'danger'
- size: 'sm' | 'md' | 'lg'
- disabled: boolean
- loading: boolean
- icon: ReactNode (optional)
- children: ReactNode

ACCESSIBILITY:
- ARIA roles and attributes
- Keyboard interactions
- Focus management
- Screen reader behavior

DO:
- [Best practices]

DON'T:
- [Anti-patterns]
```

---

## 4. THEMING & MULTI-BRAND

### Theme Switching with CSS Custom Properties

```css
/* Light theme (default) */
:root, [data-theme="light"] {
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f9fafb;
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  --color-border-default: #e5e7eb;
  --color-action-primary: #2563eb;
}

/* Dark theme */
[data-theme="dark"] {
  --color-bg-primary: #111827;
  --color-bg-secondary: #1f2937;
  --color-text-primary: #f9fafb;
  --color-text-secondary: #9ca3af;
  --color-border-default: #374151;
  --color-action-primary: #60a5fa;
}

/* Brand A */
[data-brand="brand-a"] {
  --color-action-primary: #7c3aed;
  --color-action-primary-hover: #6d28d9;
  --font-display: 'Playfair Display', serif;
}

/* Brand B */
[data-brand="brand-b"] {
  --color-action-primary: #059669;
  --color-action-primary-hover: #047857;
  --font-display: 'Space Grotesk', sans-serif;
}
```

### Theme Toggle (JS)
```javascript
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

// Respect system preference
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const saved = localStorage.getItem('theme');
setTheme(saved || (prefersDark ? 'dark' : 'light'));
```

---

## 5. DOCUMENTATION STANDARDS

### Component Documentation Structure
1. **Overview**: What, why, when to use
2. **Live Examples**: Interactive demos of all variants
3. **API Reference**: Props, events, slots
4. **Design Guidelines**: Do's, don'ts, best practices
5. **Accessibility**: ARIA, keyboard, screen reader
6. **Code Examples**: Copy-paste ready snippets
7. **Related Components**: Links to related or alternative components
8. **Changelog**: Version history of changes

### Writing Style for Documentation
- Use imperative tone: "Use this component when..." not "This component can be used when..."
- Show, don't tell: Include visual examples for every guideline
- Be specific about anti-patterns: "Don't use more than 3 action buttons" not "Don't use too many buttons"
- Include real-world context: "For a settings page with many toggles, use the compact variant"

---

## 6. ACCESSIBILITY AT SCALE

### Accessibility Token Layer
```css
:root {
  /* Focus ring */
  --focus-ring-color: var(--color-action-primary);
  --focus-ring-width: 2px;
  --focus-ring-offset: 2px;
  --focus-ring: var(--focus-ring-width) solid var(--focus-ring-color);

  /* Minimum touch target */
  --touch-target-min: 44px;

  /* Motion preference */
  --animation-duration: var(--duration-normal);
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --animation-duration: 0.01ms;
  }
}

/* Focus visible utility */
:focus-visible {
  outline: var(--focus-ring);
  outline-offset: var(--focus-ring-offset);
}
```

### Color Contrast Verification
For every text/background combination in the token system, verify:
- Normal text: ≥ 4.5:1 contrast ratio
- Large text (18px+ bold or 24px+): ≥ 3:1
- UI components: ≥ 3:1
- Document exceptions where intentional (decorative text, disabled states)

---

## 7. IMPLEMENTATION PATTERNS

### CSS Architecture for Design Systems

```css
/* 1. Reset / Normalize */
/* 2. Token definitions (custom properties) */
/* 3. Base styles (typography, links, lists) */
/* 4. Utility classes (spacing, typography, color) */
/* 5. Component styles (scoped to component class) */
/* 6. Pattern/layout styles */
/* 7. Page-specific overrides (minimize these) */
```

### Utility-First Pattern
```css
/* Spacing utilities */
.mt-0 { margin-top: 0; }
.mt-1 { margin-top: var(--space-1); }
.mt-2 { margin-top: var(--space-2); }
.mt-4 { margin-top: var(--space-4); }
.mt-6 { margin-top: var(--space-6); }
.mt-8 { margin-top: var(--space-8); }

/* Typography utilities */
.text-xs { font-size: var(--font-size-xs); }
.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.text-lg { font-size: var(--font-size-lg); }
.font-medium { font-weight: var(--font-weight-medium); }
.font-semibold { font-weight: var(--font-weight-semibold); }
.font-bold { font-weight: var(--font-weight-bold); }

/* Color utilities */
.text-primary { color: var(--color-text-primary); }
.text-secondary { color: var(--color-text-secondary); }
.bg-primary { background: var(--color-bg-primary); }
.bg-secondary { background: var(--color-bg-secondary); }
```

### Component Class Pattern
```css
/* BEM-inspired component classes */
.card { /* Block */ }
.card__header { /* Element */ }
.card__body { /* Element */ }
.card__footer { /* Element */ }
.card--elevated { /* Modifier */ }
.card--compact { /* Modifier */ }
```
