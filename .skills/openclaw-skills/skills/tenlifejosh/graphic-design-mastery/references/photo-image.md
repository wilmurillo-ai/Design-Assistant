# Photo & Image Manipulation Reference

Use this reference for: photo compositing concepts, image manipulation, color grading, retouching concepts,
background removal concepts, image optimization, responsive images, art direction with images, duotone/tritone
effects, and any design work involving photographic or raster image treatment.

---

## TABLE OF CONTENTS
1. Image Treatment Techniques (CSS/SVG)
2. Duotone & Color Effects
3. Image Composition Principles
4. Responsive Image Strategy
5. Image Optimization
6. CSS Image Effects Library
7. SVG Filter Effects
8. Image Masking & Clipping

---

## 1. IMAGE TREATMENT TECHNIQUES (CSS/SVG)

### CSS Filter Effects
```css
/* Grayscale */
.grayscale { filter: grayscale(100%); }
.grayscale:hover { filter: grayscale(0%); transition: filter 0.5s; }

/* Sepia (vintage) */
.sepia { filter: sepia(80%) saturate(120%); }

/* High contrast B&W */
.high-contrast { filter: grayscale(100%) contrast(150%); }

/* Warm tone */
.warm { filter: sepia(20%) saturate(130%) brightness(105%); }

/* Cool tone */
.cool { filter: saturate(80%) brightness(95%) hue-rotate(10deg); }

/* Fade/Muted */
.faded { filter: saturate(60%) contrast(90%) brightness(110%); }

/* Dramatic dark */
.dramatic { filter: contrast(130%) brightness(80%) saturate(120%); }

/* Blur background */
.blur-bg { filter: blur(20px) brightness(70%); }

/* Combined editorial look */
.editorial {
  filter: contrast(105%) saturate(90%) brightness(102%);
  mix-blend-mode: multiply;
}
```

### CSS Blend Modes for Image Overlays
```css
/* Color overlay */
.color-overlay {
  position: relative;
}
.color-overlay::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  mix-blend-mode: multiply;
  opacity: 0.7;
}

/* Available blend modes for design: */
/* multiply — Darkens, good for color overlay on photos */
/* screen — Lightens, good for glow effects */
/* overlay — Increases contrast, good for texture overlay */
/* soft-light — Subtle contrast boost */
/* hard-light — Dramatic contrast */
/* color — Applies hue/saturation while preserving luminance */
/* luminosity — Applies brightness while preserving color */
/* difference — Creates inverted/psychedelic effects */
/* exclusion — Softer version of difference */
```

---

## 2. DUOTONE & COLOR EFFECTS

### CSS Duotone
```css
.duotone {
  position: relative;
  overflow: hidden;
}
.duotone img {
  filter: grayscale(100%) contrast(120%);
  mix-blend-mode: luminosity;
}
.duotone::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1e3a5f 0%, #3b82f6 100%);
  mix-blend-mode: screen;
  z-index: 1;
}
.duotone::after {
  content: '';
  position: absolute;
  inset: 0;
  background: #0f172a;
  mix-blend-mode: multiply;
  z-index: 2;
}
```

### SVG Duotone Filter
```svg
<defs>
  <filter id="duotone">
    <!-- Convert to grayscale -->
    <feColorMatrix type="saturate" values="0"/>
    <!-- Map shadows and highlights to two colors -->
    <feComponentTransfer>
      <!-- Shadow color: dark blue (r=30, g=58, b=95 → 0.118, 0.227, 0.373) -->
      <!-- Highlight color: light blue (r=59, g=130, b=246 → 0.231, 0.510, 0.965) -->
      <feFuncR type="table" tableValues="0.118 0.231"/>
      <feFuncG type="table" tableValues="0.227 0.510"/>
      <feFuncB type="table" tableValues="0.373 0.965"/>
    </feComponentTransfer>
  </filter>
</defs>
<image href="photo.jpg" width="100%" height="100%" filter="url(#duotone)"/>
```

### Tritone Effect
```svg
<filter id="tritone">
  <feColorMatrix type="saturate" values="0"/>
  <feComponentTransfer>
    <!-- Three-stop color map: shadow → midtone → highlight -->
    <feFuncR type="table" tableValues="0.05 0.9 1.0"/>
    <feFuncG type="table" tableValues="0.05 0.4 0.95"/>
    <feFuncB type="table" tableValues="0.2 0.2 0.5"/>
  </feComponentTransfer>
</filter>
```

---

## 3. IMAGE COMPOSITION PRINCIPLES

### Cropping for Impact
- **Tight crop**: Fills the frame, creates intimacy and intensity
- **Loose crop**: Includes context and environment
- **Off-center crop**: Creates dynamic tension, applies rule of thirds
- **Extreme close-up**: Abstract, textural, draws attention to detail

### Image + Text Relationships
1. **Text over low-detail area**: Find naturally "empty" zones in photos
2. **Color overlay**: Semi-transparent color block over image for text contrast
3. **Gradient overlay**: Fade from transparent to solid for text area
4. **Split layout**: Image on one side, text on the other (no overlap)
5. **Text mask**: Photo visible through text cutout (clip-path)

### Creating Depth with Images
- **Parallax layers**: Foreground moves faster than background on scroll
- **Blur depth-of-field**: Blur background, sharp foreground (or vice versa)
- **Scale**: Larger = closer, smaller = further
- **Overlap**: Elements overlapping images create depth
- **Shadow**: Drop shadows on floating elements over images

---

## 4. RESPONSIVE IMAGE STRATEGY

### Art Direction
Different crops for different screen sizes:
```html
<picture>
  <source media="(min-width: 1024px)" srcset="hero-wide.jpg">
  <source media="(min-width: 640px)" srcset="hero-medium.jpg">
  <img src="hero-mobile.jpg" alt="Description">
</picture>
```

### CSS Object-Fit
```css
.image-container img {
  width: 100%;
  height: 300px;
  object-fit: cover;    /* Fills container, crops as needed (most common) */
  object-position: center 30%; /* Adjust focal point */
}

/* Other object-fit values: */
/* contain — Shows entire image, may letterbox */
/* fill — Stretches to fill (distorts!) */
/* scale-down — Smaller of contain or none */
```

### Aspect Ratio Control
```css
.image-wrapper {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  border-radius: var(--radius-lg);
}
.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

---

## 5. IMAGE OPTIMIZATION

### Format Selection
| Format | Best For | Transparency | Animation |
|--------|----------|-------------|-----------|
| **WebP** | General web use, best compression | Yes | Yes |
| **AVIF** | Next-gen, best quality/size ratio | Yes | Yes |
| **JPEG** | Photos, complex images | No | No |
| **PNG** | Screenshots, graphics with transparency | Yes | No |
| **SVG** | Icons, logos, illustrations | Yes | CSS/SMIL |
| **GIF** | Simple animations | 1-bit | Yes |

### Optimization Guidelines
- Photos: WebP at 80-85% quality (or JPEG at 82-85%)
- Icons/logos: SVG always (unless photo-realistic)
- Large hero images: Max 200KB after compression
- Thumbnails: Max 30KB
- Use `loading="lazy"` for below-fold images
- Provide `width` and `height` attributes to prevent layout shift

---

## 6. CSS IMAGE EFFECTS LIBRARY

### Vignette
```css
.vignette {
  position: relative;
}
.vignette::after {
  content: '';
  position: absolute;
  inset: 0;
  box-shadow: inset 0 0 100px rgba(0, 0, 0, 0.5);
  pointer-events: none;
}
```

### Film Grain Overlay
```css
.grain::after {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.07;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  mix-blend-mode: overlay;
  pointer-events: none;
}
```

### Parallax Zoom on Hover
```css
.zoom-container {
  overflow: hidden;
  border-radius: var(--radius-lg);
}
.zoom-container img {
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.zoom-container:hover img {
  transform: scale(1.08);
}
```

### Image Reveal on Scroll
```css
.image-reveal {
  clip-path: inset(100% 0 0 0);
  transition: clip-path 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.image-reveal.in-view {
  clip-path: inset(0 0 0 0);
}
```

---

## 7. SVG FILTER EFFECTS

### Sophisticated SVG Filters
```svg
<defs>
  <!-- Gaussian blur -->
  <filter id="blur">
    <feGaussianBlur stdDeviation="5"/>
  </filter>

  <!-- Drop shadow -->
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="2" dy="4" stdDeviation="4" flood-color="rgba(0,0,0,0.2)"/>
  </filter>

  <!-- Noise texture -->
  <filter id="noise">
    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3"/>
    <feColorMatrix type="saturate" values="0"/>
    <feBlend in="SourceGraphic" mode="multiply"/>
  </filter>

  <!-- Glow -->
  <filter id="glow">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>

  <!-- Displacement (warping) -->
  <filter id="warp">
    <feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="3" result="noise"/>
    <feDisplacementMap in="SourceGraphic" in2="noise" scale="15" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</defs>
```

---

## 8. IMAGE MASKING & CLIPPING

### CSS Clip Paths
```css
/* Circle mask */
.circle-mask { clip-path: circle(50% at 50% 50%); }

/* Rounded rectangle */
.rounded-mask { clip-path: inset(0 round 20px); }

/* Polygon shapes */
.diamond { clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%); }
.hexagon { clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); }
.arrow-right { clip-path: polygon(0% 0%, 75% 0%, 100% 50%, 75% 100%, 0% 100%); }

/* Animated clip-path reveal */
.clip-reveal {
  clip-path: circle(0% at 50% 50%);
  transition: clip-path 0.8s ease-out;
}
.clip-reveal.active {
  clip-path: circle(75% at 50% 50%);
}
```

### SVG Masks
```svg
<defs>
  <!-- Text mask (photo visible through text) -->
  <mask id="text-mask">
    <rect width="100%" height="100%" fill="black"/>
    <text x="50%" y="55%" text-anchor="middle" font-size="120" font-weight="900" fill="white">
      DESIGN
    </text>
  </mask>
</defs>
<image href="photo.jpg" width="800" height="400" mask="url(#text-mask)"/>
```

### Gradient Mask (Fade to Transparent)
```css
.fade-mask {
  -webkit-mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
  mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
}
```
