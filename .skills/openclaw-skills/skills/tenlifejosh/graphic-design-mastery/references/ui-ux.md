# UI/UX & Digital Product Design Reference

Use this reference for: web design, app design, dashboard design, design systems, component libraries,
wireframes, prototypes, responsive design, dark mode, accessibility, micro-interactions, form design,
landing pages, and any screen-based interface design.

---

## TABLE OF CONTENTS
1. Layout Patterns & Page Architecture
2. Component Design Library
3. Form & Input Design
4. Dashboard Design
5. Responsive Design System
6. Dark Mode Design
7. Micro-Interactions & States
8. Landing Page Design

---

## 1. LAYOUT PATTERNS & PAGE ARCHITECTURE

### The Responsive Container System
```css
.container {
  width: 100%;
  max-width: 1280px;
  margin-inline: auto;
  padding-inline: clamp(1rem, 5vw, 3rem);
}

/* Breakpoint-aware widths */
.container-sm { max-width: 640px; }
.container-md { max-width: 768px; }
.container-lg { max-width: 1024px; }
.container-xl { max-width: 1280px; }
.container-2xl { max-width: 1536px; }
```

### Common Page Layouts

**Holy Grail (Header + Sidebar + Content + Footer)**:
```css
.holy-grail {
  display: grid;
  grid-template: "header header" auto
                 "sidebar main" 1fr
                 "footer footer" auto / 260px 1fr;
  min-height: 100vh;
}
```

**Sidebar + Content (App Shell)**:
```css
.app-shell {
  display: grid;
  grid-template-columns: 260px 1fr;
  height: 100vh;
}
.sidebar { overflow-y: auto; border-right: 1px solid var(--color-border-default); }
.main-content { overflow-y: auto; }
```

**Centered Content (Marketing/Blog)**:
```css
.centered-layout {
  display: grid;
  grid-template-columns: 1fr min(65ch, 100% - 4rem) 1fr;
}
.centered-layout > * { grid-column: 2; }
.centered-layout > .full-bleed { grid-column: 1 / -1; }
```

### Navigation Patterns

**Top Navigation Bar**:
```html
<nav class="navbar">
  <div class="nav-brand"><!-- Logo --></div>
  <div class="nav-links"><!-- Primary links --></div>
  <div class="nav-actions"><!-- CTA, profile, search --></div>
</nav>
```
```css
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  height: 64px;
  border-bottom: 1px solid var(--color-border-default);
  background: var(--color-surface-primary);
  position: sticky;
  top: 0;
  z-index: 100;
}
```

**Sidebar Navigation**:
```css
.sidebar-nav {
  width: 260px;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-default);
}
.nav-item:hover { background: var(--color-surface-secondary); color: var(--color-text-primary); }
.nav-item.active { background: var(--color-brand-primary-light); color: var(--color-brand-primary); font-weight: 500; }
```

---

## 2. COMPONENT DESIGN LIBRARY

### Button System
```css
/* Base button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: 10px 20px;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
  line-height: 1;
}

/* Variants */
.btn-primary {
  background: var(--color-brand-primary);
  color: white;
}
.btn-primary:hover { background: var(--color-brand-primary-hover); transform: translateY(-1px); }
.btn-primary:active { transform: translateY(0); }

.btn-secondary {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-default);
}
.btn-secondary:hover { background: var(--color-surface-tertiary); border-color: var(--color-border-strong); }

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}
.btn-ghost:hover { background: var(--color-surface-secondary); color: var(--color-text-primary); }

.btn-danger {
  background: var(--color-error);
  color: white;
}

/* Sizes */
.btn-sm { padding: 6px 12px; font-size: var(--text-xs); }
.btn-lg { padding: 14px 28px; font-size: var(--text-base); }
```

### Card Component
```css
.card {
  background: var(--color-surface-primary);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--duration-normal) var(--ease-default);
}
.card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-md);
}
.card-header { padding: var(--space-6) var(--space-6) 0; }
.card-body { padding: var(--space-6); }
.card-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border-default);
  background: var(--color-surface-secondary);
}
```

### Badge / Tag
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  font-size: var(--text-xs);
  font-weight: 500;
  border-radius: var(--radius-full);
  line-height: 1.5;
}
.badge-default { background: var(--color-surface-tertiary); color: var(--color-text-secondary); }
.badge-primary { background: var(--color-brand-primary-light); color: var(--color-brand-primary); }
.badge-success { background: #d1fae5; color: #065f46; }
.badge-warning { background: #fef3c7; color: #92400e; }
.badge-error { background: #fee2e2; color: #991b1b; }
```

### Avatar
```css
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  overflow: hidden;
  background: var(--color-surface-tertiary);
  color: var(--color-text-secondary);
  font-weight: 600;
}
.avatar-sm { width: 32px; height: 32px; font-size: var(--text-xs); }
.avatar-md { width: 40px; height: 40px; font-size: var(--text-sm); }
.avatar-lg { width: 48px; height: 48px; font-size: var(--text-base); }
.avatar-xl { width: 64px; height: 64px; font-size: var(--text-lg); }
```

### Modal / Dialog
```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: var(--color-surface-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: min(500px, 90vw);
  max-height: 85vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border-default);
}
.modal-body { padding: var(--space-6); }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border-default);
}
```

### Toast / Notification
```css
.toast {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--color-surface-primary);
  border: 1px solid var(--color-border-default);
  box-shadow: var(--shadow-lg);
  max-width: 400px;
}
```

---

## 3. FORM & INPUT DESIGN

### Input Field
```css
.input {
  width: 100%;
  padding: 10px 14px;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  background: var(--color-surface-primary);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-default);
  outline: none;
}
.input::placeholder { color: var(--color-text-tertiary); }
.input:hover { border-color: var(--color-border-strong); }
.input:focus {
  border-color: var(--color-brand-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
.input-error {
  border-color: var(--color-error);
}
.input-error:focus {
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}
```

### Form Layout
```css
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  margin-bottom: var(--space-4);
}
.form-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}
.form-hint {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}
.form-error-msg {
  font-size: var(--text-xs);
  color: var(--color-error);
}
```

### Checkbox & Radio
```css
.checkbox {
  width: 18px; height: 18px;
  border: 2px solid var(--color-border-strong);
  border-radius: var(--radius-sm);
  appearance: none;
  cursor: pointer;
  transition: all var(--duration-fast);
}
.checkbox:checked {
  background: var(--color-brand-primary);
  border-color: var(--color-brand-primary);
  /* Add checkmark via background-image SVG */
}
```

---

## 4. DASHBOARD DESIGN

### Dashboard Layout Patterns

**Metric Cards + Table**:
```
┌──────┐┌──────┐┌──────┐┌──────┐
│ KPI  ││ KPI  ││ KPI  ││ KPI  │
│ Card ││ Card ││ Card ││ Card │
└──────┘└──────┘└──────┘└──────┘
┌──────────────────────────────┐
│                              │
│         Chart Area           │
│                              │
└──────────────────────────────┘
┌──────────────────────────────┐
│         Data Table           │
└──────────────────────────────┘
```

**KPI Card Design**:
```css
.kpi-card {
  padding: var(--space-6);
  background: var(--color-surface-primary);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-lg);
}
.kpi-label {
  font-size: var(--text-xs);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-1);
}
.kpi-value {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.1;
}
.kpi-change {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-sm);
  font-weight: 500;
  margin-top: var(--space-2);
}
.kpi-change.positive { color: var(--color-success); }
.kpi-change.negative { color: var(--color-error); }
```

### Data Table Design
```css
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}
.data-table th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  font-weight: 500;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-tertiary);
  border-bottom: 2px solid var(--color-border-default);
  background: var(--color-surface-secondary);
}
.data-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border-default);
  color: var(--color-text-primary);
}
.data-table tr:hover td { background: var(--color-surface-secondary); }
```

---

## 5. RESPONSIVE DESIGN SYSTEM

### Breakpoint Strategy
```css
/* Mobile-first breakpoints */
/* Default: Mobile (0-639px) */
@media (min-width: 640px) { /* sm: Tablet portrait */ }
@media (min-width: 768px) { /* md: Tablet landscape */ }
@media (min-width: 1024px) { /* lg: Desktop */ }
@media (min-width: 1280px) { /* xl: Large desktop */ }
@media (min-width: 1536px) { /* 2xl: Extra large */ }
```

### Responsive Patterns
- **Stack to horizontal**: Columns stack on mobile, go side-by-side on desktop
- **Show/hide**: Sidebar hidden on mobile, visible on desktop (replaced by hamburger)
- **Reorder**: Change element order between breakpoints
- **Simplify**: Reduce complexity on small screens (fewer columns, collapsed sections)
- **Resize**: Fluid scaling between breakpoints using `clamp()`

---

## 6. DARK MODE DESIGN

### Color Strategy
Don't just invert colors. Dark mode needs its own carefully crafted palette:

```css
:root[data-theme="dark"] {
  --color-surface-primary: #1a1a2e;
  --color-surface-secondary: #222236;
  --color-surface-tertiary: #2a2a40;
  --color-surface-elevated: #32324a;

  --color-text-primary: #e8e8f0;
  --color-text-secondary: #a0a0b8;
  --color-text-tertiary: #6a6a82;

  --color-border-default: #32324a;
  --color-border-strong: #4a4a62;

  /* Reduce brand color intensity for dark mode */
  --color-brand-primary: #5b8dee;
  --color-brand-primary-light: rgba(91, 141, 238, 0.15);
}
```

### Dark Mode Principles
1. **Don't use pure black** (#000000). Use very dark grays (#1a1a2e, #121220) for depth.
2. **Don't use pure white text**. Use slightly muted whites (#e8e8f0) to reduce eye strain.
3. **Reduce saturation** of brand colors. Vivid colors glare on dark backgrounds.
4. **Elevate with lightness**, not shadow. Higher surfaces = slightly lighter. (Reverse of light mode.)
5. **Keep contrast in check**. Don't exceed 15:1 contrast for body text (too harsh at night).
6. **Test with real content**. Dark mode issues often only surface with dense text or complex layouts.

---

## 7. MICRO-INTERACTIONS & STATES

### Interactive States (every interactive element needs ALL of these)
```css
.interactive {
  /* Default state */
  transition: all var(--duration-fast) var(--ease-default);
}
.interactive:hover { /* Lighter, elevated, pointer cursor */ }
.interactive:focus-visible {
  outline: 2px solid var(--color-brand-primary);
  outline-offset: 2px;
}
.interactive:active { /* Pressed, slightly darker or depressed */ }
.interactive:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

### Loading States
```css
/* Skeleton screen */
.skeleton {
  background: linear-gradient(90deg,
    var(--color-surface-secondary) 25%,
    var(--color-surface-tertiary) 50%,
    var(--color-surface-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}
@keyframes shimmer { to { background-position: -200% 0; } }

/* Spinner */
.spinner {
  width: 24px; height: 24px;
  border: 3px solid var(--color-border-default);
  border-top-color: var(--color-brand-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
```

---

## 8. LANDING PAGE DESIGN

### Above-the-Fold Anatomy
Every effective landing page hero has:
1. **Headline**: Clear value proposition (what does this do for me?)
2. **Sub-headline**: Supporting detail (how? or for whom?)
3. **CTA**: One primary action (Sign Up, Get Started, Try Free)
4. **Social proof**: Trust signal (logos, testimonials, metrics)
5. **Visual**: Screenshot, illustration, or video that shows the product

### Landing Page Section Order
1. Hero (value proposition + CTA)
2. Social proof bar (logo wall)
3. Feature showcase (3-4 key features)
4. How it works (3 steps)
5. Testimonials
6. Pricing (if applicable)
7. FAQ
8. Final CTA
9. Footer

### Hero Section Pattern
```css
.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-16);
  align-items: center;
  min-height: 80vh;
  padding: var(--space-24) var(--space-8);
}
.hero-content { max-width: 540px; }
.hero-eyebrow {
  font-size: var(--text-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-brand-primary);
  margin-bottom: var(--space-4);
}
.hero-title {
  font-size: var(--text-5xl);
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.03em;
  margin-bottom: var(--space-6);
}
.hero-subtitle {
  font-size: var(--text-xl);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: var(--space-8);
}
```

### Social Proof Bar
```css
.social-proof {
  display: flex;
  align-items: center;
  gap: var(--space-12);
  padding: var(--space-8) 0;
  border-top: 1px solid var(--color-border-default);
  border-bottom: 1px solid var(--color-border-default);
  opacity: 0.5;
  filter: grayscale(100%);
}
```
