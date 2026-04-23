# Motion & Animation Reference

Use this reference for: CSS animations, SVG animations, scroll animations, loading animations, page transitions,
micro-interactions, kinetic typography, motion graphics, Lottie-style animations, parallax effects, sprite
animations, and any task involving movement, timing, or animated visual design.

---

## TABLE OF CONTENTS
1. Motion Design Principles
2. Easing & Timing
3. CSS Animation Library
4. SVG Animation (SMIL + CSS)
5. Scroll-Driven Animations
6. Page Transitions
7. Loading & Progress Animations
8. Particle & Physics Animations (JS)
9. Complex Sequenced Animations

---

## 1. MOTION DESIGN PRINCIPLES

### The 12 Principles of Animation (Adapted for UI)

1. **Squash & Stretch**: Elements compress on impact, stretch on release. Use for bouncy buttons, playful UIs.
2. **Anticipation**: A small reverse movement before the main action. Pull back before launching forward.
3. **Staging**: Direct attention through motion. Animate the important thing; keep background still.
4. **Straight-Ahead vs Pose-to-Pose**: CSS keyframes = pose-to-pose. JS physics = straight-ahead.
5. **Follow-Through & Overlapping Action**: Elements don't stop at once. Trailing elements settle after main.
6. **Ease In / Ease Out**: Nothing in nature moves at constant speed. Always ease.
7. **Arcs**: Natural motion follows curved paths, not straight lines. Use for repositioning.
8. **Secondary Action**: Supporting motions that enhance the primary (icon spin while card slides in).
9. **Timing**: Speed communicates meaning. Fast = snappy, decisive. Slow = considered, dramatic.
10. **Exaggeration**: Slightly overshoot, slightly overspin. Makes motion feel alive.
11. **Solid Drawing**: 3D consistency — shadows and transforms should respect a consistent light source.
12. **Appeal**: Motion should feel good. Test by watching it 20 times. Still delightful? Keep it.

### Duration Guidelines

| Action Type | Duration | Use Case |
|-------------|----------|----------|
| Micro | 100-150ms | Button press, toggle, checkbox |
| Fast | 150-250ms | Hover states, small reveals, tooltips |
| Normal | 250-400ms | Modals, dropdowns, card transitions |
| Deliberate | 400-600ms | Page transitions, large reveals |
| Dramatic | 600-1000ms | Hero animations, storytelling moments |
| Cinematic | 1000ms+ | Full-screen transitions, loading sequences |

### When NOT to Animate
- User has `prefers-reduced-motion: reduce` enabled
- The animation adds no meaning (decorative-only motion on functional elements)
- It slows down the user's task completion
- It repeats endlessly and creates visual noise

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 2. EASING & TIMING

### Standard Easing Functions

```css
/* Default — smooth and natural */
--ease-default: cubic-bezier(0.4, 0, 0.2, 1);

/* Ease-out — fast start, gentle landing (entering elements) */
--ease-out: cubic-bezier(0, 0, 0.2, 1);

/* Ease-in — slow start, fast exit (exiting elements) */
--ease-in: cubic-bezier(0.4, 0, 1, 1);

/* Ease-in-out — symmetric, smooth both ends */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* Bounce — overshoots then settles (playful, attention-grabbing) */
--ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);

/* Elastic — pronounced overshoot with oscillation */
--ease-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55);

/* Snappy — quick acceleration, sharp deceleration */
--ease-snappy: cubic-bezier(0.5, 0, 0.1, 1);

/* Heavy — slow, weighted feel */
--ease-heavy: cubic-bezier(0.7, 0, 0.3, 1);

/* Spring-like (for JS implementations) */
/* stiffness: 200, damping: 20, mass: 1 */
```

### Easing Selection Guide
- **Elements entering**: Use ease-out (arrive gently)
- **Elements exiting**: Use ease-in (depart quickly)
- **Elements moving/transforming**: Use ease-in-out or default
- **Bouncy/playful interactions**: Use bounce or elastic
- **Precise/professional tools**: Use snappy or default
- **Heavy/dramatic reveals**: Use heavy

---

## 3. CSS ANIMATION LIBRARY

### Fade In Variants
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes fadeInScale {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

### Slide Variants
```css
@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
@keyframes slideInBottom {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
@keyframes slideOutLeft {
  from { transform: translateX(0); }
  to { transform: translateX(-100%); }
}
```

### Scale & Pop
```css
@keyframes scaleIn {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
@keyframes popIn {
  0% { transform: scale(0); opacity: 0; }
  70% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  14% { transform: scale(1.1); }
  28% { transform: scale(1); }
  42% { transform: scale(1.1); }
}
```

### Rotation
```css
@keyframes spin {
  to { transform: rotate(360deg); }
}
@keyframes spinReverse {
  to { transform: rotate(-360deg); }
}
@keyframes wiggle {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(5deg); }
  75% { transform: rotate(-5deg); }
}
@keyframes swing {
  0%, 100% { transform: rotate(0deg); transform-origin: top center; }
  20% { transform: rotate(15deg); }
  40% { transform: rotate(-10deg); }
  60% { transform: rotate(5deg); }
  80% { transform: rotate(-5deg); }
}
```

### Attention
```css
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); animation-timing-function: cubic-bezier(0.8, 0, 1, 1); }
  50% { transform: translateY(-25%); animation-timing-function: cubic-bezier(0, 0, 0.2, 1); }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
@keyframes glow {
  0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.3); }
  50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); }
}
```

### Staggered Entry (CSS-only)
```css
.stagger-list > * {
  opacity: 0;
  animation: fadeInUp 0.5s var(--ease-out) forwards;
}
.stagger-list > *:nth-child(1) { animation-delay: 0.0s; }
.stagger-list > *:nth-child(2) { animation-delay: 0.08s; }
.stagger-list > *:nth-child(3) { animation-delay: 0.16s; }
.stagger-list > *:nth-child(4) { animation-delay: 0.24s; }
.stagger-list > *:nth-child(5) { animation-delay: 0.32s; }
.stagger-list > *:nth-child(6) { animation-delay: 0.40s; }
.stagger-list > *:nth-child(7) { animation-delay: 0.48s; }
.stagger-list > *:nth-child(8) { animation-delay: 0.56s; }
/* Pattern: n × 80ms for smooth stagger */
```

---

## 4. SVG ANIMATION

### CSS-Based SVG Animation
```css
/* Stroke drawing (line drawing effect) */
.draw-path {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: drawLine 2s ease-out forwards;
}
@keyframes drawLine {
  to { stroke-dashoffset: 0; }
}

/* Morphing (between simple shapes) */
@keyframes morph {
  0% { d: path('M 10 80 C 40 10, 65 10, 95 80'); }
  50% { d: path('M 10 80 C 40 80, 65 80, 95 80'); }
  100% { d: path('M 10 80 C 40 10, 65 10, 95 80'); }
}

/* SVG group animation */
.svg-group {
  transform-origin: center;
  transform-box: fill-box; /* CRITICAL for SVG transform-origin */
}
```

### SMIL Animation (inline SVG)
```svg
<!-- Animate attribute over time -->
<circle cx="50" cy="50" r="20" fill="#3b82f6">
  <animate attributeName="r" values="20;30;20" dur="2s" repeatCount="indefinite"/>
  <animate attributeName="fill-opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
</circle>

<!-- Animate along a path -->
<circle r="5" fill="#3b82f6">
  <animateMotion dur="3s" repeatCount="indefinite">
    <mpath href="#motionPath"/>
  </animateMotion>
</circle>

<!-- Animate transform -->
<g>
  <animateTransform attributeName="transform" type="rotate"
    from="0 50 50" to="360 50 50" dur="4s" repeatCount="indefinite"/>
</g>
```

### SVG Line Drawing Effect
```javascript
// Calculate total path length, then animate stroke-dashoffset
function animatePath(pathElement, duration = 2000) {
  const length = pathElement.getTotalLength();
  pathElement.style.strokeDasharray = length;
  pathElement.style.strokeDashoffset = length;
  pathElement.style.transition = `stroke-dashoffset ${duration}ms ease-out`;
  // Trigger
  requestAnimationFrame(() => {
    pathElement.style.strokeDashoffset = '0';
  });
}
```

---

## 5. SCROLL-DRIVEN ANIMATIONS

### Intersection Observer (JS)
```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      observer.unobserve(entry.target); // Animate once
    }
  });
}, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
```

```css
.animate-on-scroll {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s var(--ease-out), transform 0.6s var(--ease-out);
}
.animate-on-scroll.in-view {
  opacity: 1;
  transform: translateY(0);
}
/* Stagger children */
.animate-on-scroll.in-view > *:nth-child(1) { transition-delay: 0s; }
.animate-on-scroll.in-view > *:nth-child(2) { transition-delay: 0.1s; }
.animate-on-scroll.in-view > *:nth-child(3) { transition-delay: 0.2s; }
```

### CSS Scroll-Driven Animations (Modern Browsers)
```css
@keyframes parallax {
  from { transform: translateY(50px); }
  to { transform: translateY(-50px); }
}
.parallax-element {
  animation: parallax linear;
  animation-timeline: view();
  animation-range: entry 0% exit 100%;
}
```

### Parallax (JS Fallback)
```javascript
window.addEventListener('scroll', () => {
  const scrolled = window.scrollY;
  document.querySelectorAll('.parallax').forEach(el => {
    const speed = parseFloat(el.dataset.speed || 0.5);
    el.style.transform = `translateY(${scrolled * speed}px)`;
  });
}, { passive: true });
```

---

## 6. PAGE TRANSITIONS

### Fade Transition
```css
.page-enter { opacity: 0; }
.page-enter-active {
  opacity: 1;
  transition: opacity 300ms var(--ease-out);
}
.page-exit { opacity: 1; }
.page-exit-active {
  opacity: 0;
  transition: opacity 200ms var(--ease-in);
}
```

### Slide Transition
```css
.page-enter { transform: translateX(100%); }
.page-enter-active {
  transform: translateX(0);
  transition: transform 400ms var(--ease-out);
}
.page-exit { transform: translateX(0); }
.page-exit-active {
  transform: translateX(-30%);
  opacity: 0.5;
  transition: all 400ms var(--ease-in);
}
```

### Shared Element Transition (View Transitions API)
```css
/* Assign transition names to elements */
.card-image { view-transition-name: hero-image; }

::view-transition-old(hero-image) {
  animation: fadeOut 300ms ease-in;
}
::view-transition-new(hero-image) {
  animation: fadeIn 300ms ease-out;
}
```

---

## 7. LOADING & PROGRESS ANIMATIONS

### Spinner Variants
```css
/* Simple ring spinner */
.spinner-ring {
  width: 40px; height: 40px;
  border: 3px solid var(--color-border-default);
  border-top-color: var(--color-brand-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* Three-dot bounce */
.dots-loader { display: flex; gap: 6px; }
.dots-loader span {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--color-brand-primary);
  animation: dotBounce 1.2s ease-in-out infinite;
}
.dots-loader span:nth-child(2) { animation-delay: 0.15s; }
.dots-loader span:nth-child(3) { animation-delay: 0.3s; }
@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* Bar loader */
.bar-loader {
  width: 100%; height: 3px;
  background: var(--color-surface-tertiary);
  overflow: hidden;
  border-radius: 2px;
}
.bar-loader::after {
  content: '';
  display: block;
  width: 40%; height: 100%;
  background: var(--color-brand-primary);
  border-radius: 2px;
  animation: barSlide 1.5s ease-in-out infinite;
}
@keyframes barSlide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(350%); }
}
```

### Progress Bar
```css
.progress-bar {
  width: 100%; height: 8px;
  background: var(--color-surface-tertiary);
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: var(--color-brand-primary);
  border-radius: 4px;
  transition: width 0.4s var(--ease-default);
}
```

### Skeleton Screens
```css
.skeleton-line {
  height: 1em;
  background: linear-gradient(90deg,
    var(--color-surface-secondary) 25%,
    var(--color-surface-tertiary) 50%,
    var(--color-surface-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
}
.skeleton-line:nth-child(odd) { width: 90%; }
.skeleton-line:nth-child(even) { width: 70%; }
.skeleton-circle {
  width: 48px; height: 48px;
  border-radius: 50%;
  background: inherit; /* Same shimmer */
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## 8. PARTICLE & PHYSICS ANIMATIONS (JS)

### Simple Particle System (Canvas)
```javascript
class Particle {
  constructor(x, y) {
    this.x = x; this.y = y;
    this.vx = (Math.random() - 0.5) * 4;
    this.vy = (Math.random() - 0.5) * 4;
    this.life = 1;
    this.decay = 0.01 + Math.random() * 0.02;
    this.size = 2 + Math.random() * 4;
    this.color = `hsla(${200 + Math.random() * 40}, 70%, 60%, `;
  }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vy += 0.05; // gravity
    this.life -= this.decay;
  }
  draw(ctx) {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size * this.life, 0, Math.PI * 2);
    ctx.fillStyle = this.color + this.life + ')';
    ctx.fill();
  }
}
```

### Spring Physics
```javascript
function spring(current, target, velocity, stiffness = 200, damping = 20) {
  const force = stiffness * (target - current);
  const dampingForce = damping * velocity;
  const acceleration = force - dampingForce;
  const newVelocity = velocity + acceleration * 0.001; // dt
  const newPosition = current + newVelocity * 0.001;
  return { position: newPosition, velocity: newVelocity };
}
```

---

## 9. COMPLEX SEQUENCED ANIMATIONS

### CSS Timeline with Custom Properties
```css
.sequence {
  --step: 0;
  animation-delay: calc(var(--step) * 100ms);
}
.sequence:nth-child(1) { --step: 0; }
.sequence:nth-child(2) { --step: 1; }
.sequence:nth-child(3) { --step: 2; }
/* etc. */
```

### Multi-Phase Animation
```css
@keyframes heroEntrance {
  0% { opacity: 0; transform: translateY(40px) scale(0.98); filter: blur(4px); }
  40% { opacity: 1; filter: blur(0); }
  70% { transform: translateY(-5px) scale(1.01); }
  100% { transform: translateY(0) scale(1); }
}
.hero-element {
  animation: heroEntrance 0.8s var(--ease-bounce) forwards;
}
```

### Orchestrated Page Load
```css
.page-load .logo { animation: fadeInScale 0.5s 0.1s var(--ease-bounce) both; }
.page-load .nav-links { animation: fadeInDown 0.4s 0.3s var(--ease-out) both; }
.page-load .hero-title { animation: fadeInUp 0.6s 0.4s var(--ease-out) both; }
.page-load .hero-subtitle { animation: fadeInUp 0.5s 0.55s var(--ease-out) both; }
.page-load .hero-cta { animation: fadeInUp 0.5s 0.7s var(--ease-out) both; }
.page-load .hero-image { animation: fadeInScale 0.7s 0.5s var(--ease-out) both; }
```

### Morphing Gradient Background
```css
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.animated-gradient {
  background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}
```
