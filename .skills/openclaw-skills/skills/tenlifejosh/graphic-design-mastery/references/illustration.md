# Illustration & Iconography Reference

Use this reference for: icon design, icon systems, spot illustrations, editorial illustration, technical
illustration, isometric art, pixel art, vector art, character design, mascot design, emoji/sticker design,
badges, emblems, decorative elements, and any illustrative design work.

---

## TABLE OF CONTENTS
1. Icon Design System
2. Icon Construction (SVG)
3. Illustration Styles & Techniques
4. Isometric Illustration
5. Character & Mascot Design
6. Decorative Elements & Patterns
7. Technical Illustration

---

## 1. ICON DESIGN SYSTEM

### Icon Grid & Keylines

All icons should be built on a consistent grid:

```
Standard sizes: 16×16, 20×20, 24×24, 32×32, 48×48, 64×64
Primary design size: 24×24 (scale up/down from here)
Padding: 2px on all sides (active area = 20×20 in a 24×24 grid)
Stroke weight: 1.5px or 2px (consistent across entire set)
Corner radius: 1px-2px for small corners, match stroke weight
```

### Keyline Shapes (for visual consistency)

```svg
<!-- These shapes define the maximum bounds for different icon types -->
<svg viewBox="0 0 24 24">
  <!-- Square keyline: 18×18 centered -->
  <rect x="3" y="3" width="18" height="18" fill="none" stroke="#ddd"/>

  <!-- Circle keyline: 20×20 centered -->
  <circle cx="12" cy="12" r="10" fill="none" stroke="#ddd"/>

  <!-- Vertical rectangle: 16×20 centered -->
  <rect x="4" y="2" width="16" height="20" fill="none" stroke="#ddd"/>

  <!-- Horizontal rectangle: 20×16 centered -->
  <rect x="2" y="4" width="20" height="16" fill="none" stroke="#ddd"/>
</svg>
```

### Icon Style Categories

**Outlined (Line Icons)**: Clean, modern, minimal. Best for UI.
- Consistent stroke weight throughout the set
- Open endpoints or rounded caps
- No fills (or minimal fills for distinction)

**Filled (Solid Icons)**: Bold, readable at small sizes. Best for navigation, active states.
- Solid shapes with negative-space details
- Better contrast at small sizes
- Use for "selected" state paired with outlined "unselected"

**Duotone**: Two-tone icons with primary fill + lighter secondary fill. Modern, distinctive.
- Primary color for key shape
- 20-30% opacity for secondary/background shape
- Creates depth without complexity

**Glyph/Pictogram**: Ultra-simplified, single-color. Best for wayfinding, universal communication.

### SVG Icon Template

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
  <!-- Icon paths here -->
  <!-- Use currentColor to inherit text color -->
  <!-- stroke-linecap="round" for friendly feel, "square" for technical -->
</svg>
```

### Icon Optical Corrections

- **Circles appear smaller** than squares at the same dimension. Extend circles 1px beyond the grid.
- **Triangles/arrows appear smaller**. Extend pointed shapes ~2px beyond the grid.
- **Horizontal strokes appear thicker** than vertical strokes at the same weight. Optionally thin by 0.25px.
- **Diagonal strokes appear thinner**. Optionally thicken by 0.25px.

---

## 2. ICON CONSTRUCTION PATTERNS

### Arrow
```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
  <line x1="5" y1="12" x2="19" y2="12"/>
  <polyline points="12 5 19 12 12 19"/>
</svg>
```

### Hamburger Menu
```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <line x1="3" y1="6" x2="21" y2="6"/>
  <line x1="3" y1="12" x2="21" y2="12"/>
  <line x1="3" y1="18" x2="21" y2="18"/>
</svg>
```

### Search (Magnifying Glass)
```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
  <circle cx="11" cy="11" r="8"/>
  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>
```

### Complex Icon Construction Approach
For more complex icons, build from primitives:
1. Start with the keyline shape that fits your icon's proportions
2. Build the primary shape (the main recognizable form)
3. Add detail shapes (windows on a house, lines on a document)
4. Apply consistent stroke weight and corner radius
5. Test at 16px, 24px, and 48px — refine at each size if needed
6. Ensure the icon is recognizable in silhouette (squint test)

---

## 3. ILLUSTRATION STYLES & TECHNIQUES

### Flat Illustration
Solid colors, no gradients, minimal shadows. Clean geometric shapes.
```svg
<svg viewBox="0 0 400 300">
  <!-- Build with simple shapes and solid fills -->
  <!-- Use a limited color palette (4-6 colors) -->
  <!-- Layer shapes for depth (back to front) -->
  <!-- Slight overlap between elements creates cohesion -->
</svg>
```

### Geometric Illustration
Built entirely from basic geometric shapes: circles, rectangles, triangles.
- Consistent corner radius across all elements
- Limited, bold color palette
- Shapes can overlap with transparency for depth
- Works well for abstract concepts, tech, and modern brands

### Line Illustration
Single-weight line art, often monochromatic or duochrome.
- Consistent stroke width (2-3px at standard size)
- Rounded line caps for friendly feel, square for technical
- Can add limited spot color for emphasis
- Excellent for editorial, documentation, and technical contexts

### Textured/Grain Illustration
Flat illustration + noise/grain texture for warmth and tactile quality.

SVG noise texture technique:
```svg
<defs>
  <filter id="grain">
    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
    <feBlend in="SourceGraphic" mode="multiply"/>
  </filter>
</defs>
<!-- Apply: filter="url(#grain)" on a group -->
```

CSS noise overlay:
```css
.textured::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,..."); /* inline SVG noise */
  opacity: 0.15;
  mix-blend-mode: multiply;
  pointer-events: none;
}
```

### Gradient Illustration
Rich gradients replacing flat fills. Creates depth and dimension.
- Use multi-stop gradients for realistic depth
- Combine linear and radial gradients
- Keep gradients within the same color family for cohesion
- Mesh gradient approximation: overlay multiple radial gradients

---

## 4. ISOMETRIC ILLUSTRATION

### Isometric Grid
True isometric: 30° angles from horizontal.

```svg
<!-- Isometric cube construction -->
<svg viewBox="0 0 200 200">
  <g transform="translate(100, 50)">
    <!-- Top face -->
    <polygon points="0,-30 52,-0 0,30 -52,0" fill="#4A90D9"/>
    <!-- Left face -->
    <polygon points="-52,0 0,30 0,90 -52,60" fill="#357ABD"/>
    <!-- Right face -->
    <polygon points="52,0 0,30 0,90 52,60" fill="#2C6AA0"/>
  </g>
</svg>
```

### Isometric Transform (CSS)
```css
.isometric {
  transform: rotateX(55deg) rotateZ(-45deg);
  transform-style: preserve-3d;
}
```

### Isometric Building Blocks
Build complex isometric scenes from these primitives:
- Cube (as shown above)
- Rectangular prism (stretch the cube)
- Cylinder (ellipse top + rectangle side + ellipse bottom)
- Ramp (right triangle side + parallelogram top)
- Steps (stacked narrow prisms)

---

## 5. CHARACTER & MASCOT DESIGN

### Character Construction Principles
- **Silhouette test**: Character should be recognizable as a solid black shape
- **Proportions**: Exaggerate head-to-body ratio for friendly feel (large head = cute)
- **Shape language**:
  - Circles/rounds = friendly, approachable, soft
  - Squares/rectangles = stable, strong, reliable
  - Triangles/angles = dynamic, energetic, edgy
- **Expression**: Eyes are the most important feature. Keep them simple but expressive.
- **Pose**: Even in a static illustration, imply movement or personality through posture.

### Simple SVG Character Template
```svg
<svg viewBox="0 0 200 300">
  <!-- Head (oversized for friendly proportion) -->
  <circle cx="100" cy="80" r="60" fill="#FFD93D"/>

  <!-- Body -->
  <rect x="65" y="130" width="70" height="90" rx="20" fill="#4ECDC4"/>

  <!-- Eyes (the most expressive element) -->
  <circle cx="82" cy="72" r="8" fill="#2C3E50"/>
  <circle cx="118" cy="72" r="8" fill="#2C3E50"/>
  <!-- Eye highlights -->
  <circle cx="85" cy="69" r="3" fill="white"/>
  <circle cx="121" cy="69" r="3" fill="white"/>

  <!-- Mouth -->
  <path d="M 88 95 Q 100 108 112 95" fill="none" stroke="#2C3E50" stroke-width="3"
        stroke-linecap="round"/>

  <!-- Arms -->
  <line x1="65" y1="155" x2="30" y2="185" stroke="#FFD93D" stroke-width="12" stroke-linecap="round"/>
  <line x1="135" y1="155" x2="170" y2="185" stroke="#FFD93D" stroke-width="12" stroke-linecap="round"/>

  <!-- Legs -->
  <line x1="85" y1="220" x2="80" y2="280" stroke="#4ECDC4" stroke-width="14" stroke-linecap="round"/>
  <line x1="115" y1="220" x2="120" y2="280" stroke="#4ECDC4" stroke-width="14" stroke-linecap="round"/>
</svg>
```

---

## 6. DECORATIVE ELEMENTS & PATTERNS

### SVG Pattern Definitions
```svg
<defs>
  <!-- Dot pattern -->
  <pattern id="dots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
    <circle cx="10" cy="10" r="2" fill="currentColor" opacity="0.15"/>
  </pattern>

  <!-- Diagonal lines -->
  <pattern id="diag-lines" x="0" y="0" width="10" height="10" patternUnits="userSpaceOnUse">
    <line x1="0" y1="10" x2="10" y2="0" stroke="currentColor" stroke-width="1" opacity="0.1"/>
  </pattern>

  <!-- Grid pattern -->
  <pattern id="grid" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M 24 0 L 0 0 0 24" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.08"/>
  </pattern>

  <!-- Cross-hatch -->
  <pattern id="crosshatch" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
    <path d="M 0 0 L 8 8 M 8 0 L 0 8" stroke="currentColor" stroke-width="0.5" opacity="0.1"/>
  </pattern>
</defs>
```

### CSS Patterns
```css
/* Dot grid */
.dots { background: radial-gradient(circle, #000 1px, transparent 1px);
        background-size: 20px 20px; }

/* Diagonal stripes */
.stripes { background: repeating-linear-gradient(
  45deg, transparent, transparent 10px, rgba(0,0,0,0.03) 10px, rgba(0,0,0,0.03) 20px); }

/* Grid */
.grid-bg { background-image:
  linear-gradient(rgba(0,0,0,0.05) 1px, transparent 1px),
  linear-gradient(90deg, rgba(0,0,0,0.05) 1px, transparent 1px);
  background-size: 24px 24px; }
```

### Decorative Dividers
```svg
<!-- Elegant horizontal rule -->
<svg viewBox="0 0 400 20" xmlns="http://www.w3.org/2000/svg">
  <line x1="0" y1="10" x2="170" y2="10" stroke="#d1d5db" stroke-width="1"/>
  <circle cx="200" cy="10" r="4" fill="none" stroke="#d1d5db" stroke-width="1"/>
  <line x1="230" y1="10" x2="400" y2="10" stroke="#d1d5db" stroke-width="1"/>
</svg>
```

---

## 7. TECHNICAL ILLUSTRATION

### Diagram Arrows
```svg
<defs>
  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="currentColor"/>
  </marker>
</defs>
<line x1="10" y1="50" x2="190" y2="50"
      stroke="currentColor" stroke-width="2" marker-end="url(#arrowhead)"/>
```

### Flowchart Nodes
```svg
<!-- Process (rectangle) -->
<rect x="10" y="10" width="120" height="50" rx="4" fill="white" stroke="#374151" stroke-width="1.5"/>

<!-- Decision (diamond) -->
<polygon points="75,10 140,45 75,80 10,45" fill="white" stroke="#374151" stroke-width="1.5"/>

<!-- Terminal (rounded rectangle) -->
<rect x="10" y="10" width="120" height="50" rx="25" fill="white" stroke="#374151" stroke-width="1.5"/>

<!-- Data (parallelogram) -->
<polygon points="20,60 130,60 140,10 30,10" fill="white" stroke="#374151" stroke-width="1.5"/>
```

### Callout / Annotation Pattern
```svg
<g class="annotation">
  <!-- Leader line -->
  <line x1="100" y1="80" x2="200" y2="40" stroke="#6b7280" stroke-width="1" stroke-dasharray="4,3"/>
  <!-- Dot at origin -->
  <circle cx="100" cy="80" r="3" fill="#6b7280"/>
  <!-- Label -->
  <text x="205" y="44" font-size="12" fill="#374151" font-family="sans-serif">Label</text>
</g>
```
