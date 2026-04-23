# Phase 3: Design

Use this phase when the person needs to make visual design decisions before building.

## Design Principles

Apply these to every recommendation:

1. **Subtraction default.** As little design as possible. If an element doesn't earn its pixels, cut it.
2. **Specificity over vibes.** "Clean, modern UI" is not a design decision. Name the font, the color, the spacing.
3. **Edge cases are user experiences.** 47-char names, zero results, error states — these are features, not afterthoughts.
4. **Hierarchy is service.** What does the user see first, second, third? Respect their time.
5. **Empty states are features.** "No items found." is not a design.
6. **Trust is earned at the pixel level.** Every decision either builds or erodes trust.
7. **AI slop is the enemy.** Generic card grids, purple gradients, 3-column feature sections — if it looks like every other AI-generated site, it fails.

## The 7 Design Passes

### Pass 1: Information Architecture

Does the design define what the user sees first, second, third?

For each screen:
- What is the ONE thing the user must see?
- What is secondary? What is tertiary (can hide)?
- Draw a simple ASCII wireframe.

**Ask:** "If you could only show 3 things on this screen, what would they be?"

### Pass 2: Interaction States

Does the design specify loading, empty, error, success, and partial states?

```
FEATURE    | LOADING | EMPTY     | ERROR    | SUCCESS
-----------|---------|-----------|----------|--------
[feature]  | [spec]  | [spec]    | [spec]   | [spec]
```

Empty states are features. Specify: warmth, a primary action, and context.

### Pass 3: User Journey & Emotional Arc

Design for three time horizons simultaneously:
- **5 seconds:** What is the visceral impression?
- **5 minutes:** What behavior does the design encourage?
- **5 years:** What relationship is this building?

```
STEP | USER DOES        | FEELING    | DESIGN SUPPORT
-----|------------------|------------|----------------
1    | [action]         | [emotion]  | [visual cue]
...  | ...              | ...        | ...
```

### Pass 4: Anti-Slop Check

Flag every instance of these AI-generated patterns:

1. Purple/violet gradient backgrounds
2. The 3-column feature grid (icon + bold title + 2-line description, repeated 3x symmetrically)
3. Icons in colored circles as decoration
4. Centered everything (`text-align: center` on all headings)
5. Uniform bubbly border-radius on every element
6. Decorative blobs, floating circles, wavy SVG dividers
7. Emoji as bullet points or section headers
8. Generic hero copy ("Welcome to...", "Unlock the power of...")
9. Cookie-cutter section rhythm (hero → 3 features → testimonials → pricing)
10. Card grids that aren't about cards-as-interaction

For each flag, rewrite with a specific, intentional alternative.

### Pass 5: Typography & Color

- **Font:** Name a specific typeface. Not "a modern font" — "DM Sans" or "Playfair Display."
- **Size scale:** xs, sm, base, lg, xl, 2xl... with actual values.
- **Color palette:** Define CSS variables. Primary, secondary, accent, background, text — with hex codes.
- **Contrast:** Meet WCAG AA minimum (4.5:1 for text).
- **Dark mode:** Is it supported? How do colors adapt?

### Pass 6: Responsive & Accessibility

- **Mobile:** Intentional rearrangement or just "stacked"?
- **Keyboard navigation:** What is the tab order?
- **Screen readers:** ARIA landmarks? Alt text?
- **Touch targets:** At least 44x44px?
- **Colorblind safety:** Does information rely on color alone?

### Pass 7: Motion & Interaction

- **Hover:** What changes? (Subtle is fine — is it intentional?)
- **Click/tap:** What feedback does the user get?
- **Loading:** Is there a loading indicator?
- **Motion principle:** Motion should clarify hierarchy or communicate state. If it doesn't, remove it.

## Design System Decisions

For multi-screen products:

1. **Spacing scale:** Define the base unit. (e.g., 4px base → 4, 8, 12, 16, 24, 32, 48, 64)
2. **Border radius scale:** none, sm, md, lg, xl, full
3. **Shadow scale:** Define depth levels.
4. **Component vocabulary:** Button, Input, Card, Modal, Toast, Avatar...
5. **Icon style:** Filled or outlined?
6. **Language/tone:** Formal/casual/technical? Give examples.

## Design Specification

```markdown
# Design Specification: [title]

Date: [date]

## Product & Users
- **Product type:** [landing page / app / hybrid]
- **User:** [name the person]
- **Core feeling:** [one emotion the design must evoke]

## Visual System

### Typography
- **Font family:** [name + why]
- **Heading scale:** [sizes]
- **Body scale:** [sizes]

### Color Palette
- **Primary:** [#hex]   **Secondary:** [#hex]
- **Accent:** [#hex]    **Background:** [#hex]
- **Text:** [#hex]      **Error:** [#hex]   **Success:** [#hex]

### Spacing Scale
[Define your 4px-based scale]

### Border Radius
[Define your radius scale]

## Page Structure

### [Page Name]
```
[ASCII wireframe]
```
- **Primary action:** [what]
- **States:** loading / empty / error / success

## Interaction States
[State table]

## Accessibility
- [ ] WCAG AA contrast
- [ ] Keyboard navigation
- [ ] Touch targets ≥44px
- [ ] ARIA landmarks
- [ ] Error states with text labels

## Anti-Slop Checklist
- [ ] No purple gradients
- [ ] No generic 3-column grids
- [ ] No centered everything
- [ ] No decorative blobs
- [ ] No emoji as design
- [ ] No cookie-cutter sections

## Not In Scope
[Explicitly deferred decisions]
```

## Closing

- **The one decision to fight hardest to protect:** The visual element that makes this feel unique
- **The one edge case to add before launch:** The empty state or error message most teams forget
- **The one thing that would make you rethink the design:** The assumption that, if wrong, changes everything
