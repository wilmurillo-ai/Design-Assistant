# Generative & Creative Coding Reference

Use this reference for: algorithmic art, creative coding, p5.js, Canvas API, noise fields, particle systems,
L-systems, fractals, reaction-diffusion, cellular automata, flow fields, computational geometry, shader art,
and any task involving procedurally generated visual art.

---

## TABLE OF CONTENTS
1. Creative Coding Philosophy
2. p5.js Patterns
3. Canvas API Patterns
4. Noise & Randomness
5. Particle Systems
6. Flow Fields
7. L-Systems & Fractals
8. Cellular Automata
9. Geometric Patterns
10. Color in Generative Art

---

## 1. CREATIVE CODING PHILOSOPHY

Generative art lives at the intersection of control and chaos. The artist defines the rules; the algorithm
discovers the beauty within those rules.

### Key Principles
- **Emergent complexity**: Simple rules → complex behavior. Don't over-engineer.
- **Seeded randomness**: Always use seeds for reproducibility. Same seed = same output.
- **Parameter space**: Design for exploration. Every magic number should be a parameter.
- **Process over product**: The algorithm IS the art. Each run is a unique expression.
- **Happy accidents**: Bugs and unexpected behaviors are creative gifts. Explore them.

---

## 2. P5.JS PATTERNS

### Setup Template
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
<script>
let seed = 42;
let params = {
  count: 500,
  scale: 0.005,
  speed: 0.5,
};

function setup() {
  createCanvas(windowWidth, windowHeight);
  randomSeed(seed);
  noiseSeed(seed);
  // pixelDensity(2); // For high-DPI if needed
}

function draw() {
  // Your generative algorithm here
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}
</script>
```

### Common p5.js Techniques

**Point Cloud**:
```javascript
function draw() {
  background(10, 10, 30);
  for (let i = 0; i < params.count; i++) {
    let x = noise(i * 0.1, frameCount * 0.005) * width;
    let y = noise(i * 0.1 + 1000, frameCount * 0.005) * height;
    let s = noise(i * 0.1 + 2000) * 5;
    fill(200, 220, 255, 150);
    noStroke();
    ellipse(x, y, s);
  }
}
```

**Trail Drawing**:
```javascript
function draw() {
  // Semi-transparent background for trails
  background(10, 10, 30, 15); // Alpha = trail length

  for (let agent of agents) {
    agent.update();
    agent.draw();
  }
}
```

---

## 3. CANVAS API PATTERNS

### Setup Template
```html
<canvas id="canvas"></canvas>
<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

function animate() {
  requestAnimationFrame(animate);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  // Draw here
}
animate();
</script>
```

### Canvas Drawing Essentials
```javascript
// Line
ctx.beginPath();
ctx.moveTo(x1, y1);
ctx.lineTo(x2, y2);
ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
ctx.lineWidth = 1;
ctx.stroke();

// Circle
ctx.beginPath();
ctx.arc(x, y, radius, 0, Math.PI * 2);
ctx.fillStyle = 'hsla(210, 70%, 60%, 0.8)';
ctx.fill();

// Bezier curve
ctx.beginPath();
ctx.moveTo(x1, y1);
ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x2, y2);
ctx.stroke();

// Gradient
const grad = ctx.createRadialGradient(x, y, 0, x, y, radius);
grad.addColorStop(0, 'rgba(59, 130, 246, 0.8)');
grad.addColorStop(1, 'rgba(59, 130, 246, 0)');
ctx.fillStyle = grad;

// Composite operations
ctx.globalCompositeOperation = 'lighter'; // Additive blending
ctx.globalCompositeOperation = 'multiply';
ctx.globalCompositeOperation = 'screen';

// Transform
ctx.save();
ctx.translate(x, y);
ctx.rotate(angle);
ctx.scale(sx, sy);
// Draw at origin
ctx.restore();
```

---

## 4. NOISE & RANDOMNESS

### Perlin/Simplex Noise (p5.js)
```javascript
// 1D noise (smooth random over time)
let value = noise(frameCount * 0.01);

// 2D noise (terrain, textures)
for (let x = 0; x < width; x++) {
  for (let y = 0; y < height; y++) {
    let n = noise(x * 0.01, y * 0.01);
    // n is 0-1, use for height, color, density...
  }
}

// 3D noise (animated 2D textures)
let n = noise(x * 0.01, y * 0.01, frameCount * 0.005);

// Multi-octave (fractal) noise for more detail
noiseDetail(4, 0.5); // octaves, falloff
```

### Noise Without p5.js (Pure JS)
```javascript
// Simple value noise
class SimplexNoise {
  constructor(seed = 0) {
    this.perm = new Uint8Array(512);
    const p = new Uint8Array(256);
    for (let i = 0; i < 256; i++) p[i] = i;
    // Fisher-Yates shuffle with seed
    let s = seed;
    for (let i = 255; i > 0; i--) {
      s = (s * 16807) % 2147483647;
      const j = s % (i + 1);
      [p[i], p[j]] = [p[j], p[i]];
    }
    for (let i = 0; i < 512; i++) this.perm[i] = p[i & 255];
  }

  noise2D(x, y) {
    // Simplified 2D noise implementation
    const xi = Math.floor(x) & 255;
    const yi = Math.floor(y) & 255;
    const xf = x - Math.floor(x);
    const yf = y - Math.floor(y);
    const u = xf * xf * (3 - 2 * xf);
    const v = yf * yf * (3 - 2 * yf);

    const aa = this.perm[this.perm[xi] + yi];
    const ab = this.perm[this.perm[xi] + yi + 1];
    const ba = this.perm[this.perm[xi + 1] + yi];
    const bb = this.perm[this.perm[xi + 1] + yi + 1];

    const x1 = this.lerp(this.grad(aa, xf, yf), this.grad(ba, xf - 1, yf), u);
    const x2 = this.lerp(this.grad(ab, xf, yf - 1), this.grad(bb, xf - 1, yf - 1), u);
    return (this.lerp(x1, x2, v) + 1) / 2;
  }

  grad(hash, x, y) {
    const h = hash & 3;
    return (h === 0 ? x + y : h === 1 ? -x + y : h === 2 ? x - y : -x - y);
  }
  lerp(a, b, t) { return a + t * (b - a); }
}
```

### Seeded Random
```javascript
// Mulberry32 PRNG
function mulberry32(seed) {
  return function() {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const random = mulberry32(42); // Always produces the same sequence
```

---

## 5. PARTICLE SYSTEMS

### Basic Particle Class
```javascript
class Particle {
  constructor(x, y, options = {}) {
    this.x = x;
    this.y = y;
    this.vx = options.vx || (Math.random() - 0.5) * 2;
    this.vy = options.vy || (Math.random() - 0.5) * 2;
    this.life = options.life || 1;
    this.decay = options.decay || 0.005;
    this.size = options.size || 3;
    this.hue = options.hue || 210;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.life -= this.decay;
    // Add forces: gravity, friction, noise
    this.vy += 0.02; // gravity
    this.vx *= 0.99; // friction
    this.vy *= 0.99;
  }

  draw(ctx) {
    if (this.life <= 0) return;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size * this.life, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(${this.hue}, 70%, 60%, ${this.life})`;
    ctx.fill();
  }

  isDead() { return this.life <= 0; }
}
```

### Particle System Manager
```javascript
class ParticleSystem {
  constructor() {
    this.particles = [];
  }

  emit(x, y, count = 10, options = {}) {
    for (let i = 0; i < count; i++) {
      this.particles.push(new Particle(x, y, {
        vx: (Math.random() - 0.5) * 4,
        vy: (Math.random() - 0.5) * 4 - 2,
        size: 2 + Math.random() * 4,
        hue: 200 + Math.random() * 40,
        ...options,
      }));
    }
  }

  update() {
    this.particles.forEach(p => p.update());
    this.particles = this.particles.filter(p => !p.isDead());
  }

  draw(ctx) {
    this.particles.forEach(p => p.draw(ctx));
  }
}
```

---

## 6. FLOW FIELDS

### Noise-Based Flow Field
```javascript
class FlowField {
  constructor(resolution, noiseScale) {
    this.resolution = resolution;
    this.noiseScale = noiseScale;
    this.cols = Math.ceil(width / resolution);
    this.rows = Math.ceil(height / resolution);
    this.field = [];
  }

  update(time) {
    this.field = [];
    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        const angle = noise(x * this.noiseScale, y * this.noiseScale, time) * TWO_PI * 2;
        this.field.push(p5.Vector.fromAngle(angle));
      }
    }
  }

  lookup(x, y) {
    const col = Math.floor(constrain(x / this.resolution, 0, this.cols - 1));
    const row = Math.floor(constrain(y / this.resolution, 0, this.rows - 1));
    return this.field[row * this.cols + col];
  }
}

// Agent that follows the flow field
class FlowAgent {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = createVector(0, 0);
    this.prevPos = this.pos.copy();
    this.maxSpeed = 2;
  }

  follow(flowField) {
    const force = flowField.lookup(this.pos.x, this.pos.y);
    this.vel.add(force);
    this.vel.limit(this.maxSpeed);
  }

  update() {
    this.prevPos = this.pos.copy();
    this.pos.add(this.vel);
    this.edges(); // Wrap around
  }

  draw() {
    stroke(255, 255, 255, 5);
    strokeWeight(1);
    line(this.prevPos.x, this.prevPos.y, this.pos.x, this.pos.y);
  }

  edges() {
    if (this.pos.x > width) { this.pos.x = 0; this.prevPos.x = 0; }
    if (this.pos.x < 0) { this.pos.x = width; this.prevPos.x = width; }
    if (this.pos.y > height) { this.pos.y = 0; this.prevPos.y = 0; }
    if (this.pos.y < 0) { this.pos.y = height; this.prevPos.y = height; }
  }
}
```

---

## 7. L-SYSTEMS & FRACTALS

### L-System Renderer
```javascript
class LSystem {
  constructor(axiom, rules, angle, length) {
    this.sentence = axiom;
    this.rules = rules;    // { 'F': 'F+F-F-F+F' }
    this.angle = angle;    // Rotation angle in degrees
    this.length = length;  // Step length
  }

  generate(iterations) {
    for (let i = 0; i < iterations; i++) {
      let next = '';
      for (const char of this.sentence) {
        next += this.rules[char] || char;
      }
      this.sentence = next;
    }
  }

  draw(ctx, startX, startY) {
    const stack = [];
    let x = startX, y = startY;
    let currentAngle = -Math.PI / 2; // Start pointing up

    ctx.beginPath();
    ctx.moveTo(x, y);

    for (const char of this.sentence) {
      switch (char) {
        case 'F': // Move forward and draw
          x += Math.cos(currentAngle) * this.length;
          y += Math.sin(currentAngle) * this.length;
          ctx.lineTo(x, y);
          break;
        case '+': // Turn right
          currentAngle += this.angle * Math.PI / 180;
          break;
        case '-': // Turn left
          currentAngle -= this.angle * Math.PI / 180;
          break;
        case '[': // Save state
          stack.push({ x, y, angle: currentAngle });
          break;
        case ']': // Restore state
          const state = stack.pop();
          x = state.x; y = state.y; currentAngle = state.angle;
          ctx.moveTo(x, y);
          break;
      }
    }
    ctx.stroke();
  }
}

// Classic L-system plants:
// Koch snowflake: axiom='F', rules={'F':'F+F-F-F+F'}, angle=90, iterations=4
// Plant: axiom='X', rules={'X':'F+[[X]-X]-F[-FX]+X', 'F':'FF'}, angle=25, iterations=5
// Sierpinski: axiom='F-G-G', rules={'F':'F-G+F+G-F', 'G':'GG'}, angle=120, iterations=6
```

### Recursive Fractal Tree
```javascript
function drawTree(ctx, x, y, length, angle, depth, maxDepth) {
  if (depth > maxDepth) return;

  const endX = x + Math.cos(angle) * length;
  const endY = y + Math.sin(angle) * length;

  const alpha = 1 - depth / maxDepth;
  ctx.strokeStyle = `hsla(${100 + depth * 15}, 50%, ${30 + depth * 5}%, ${alpha})`;
  ctx.lineWidth = Math.max(1, (maxDepth - depth) * 1.5);

  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(endX, endY);
  ctx.stroke();

  const newLength = length * 0.72;
  const spread = 0.4 + Math.random() * 0.2;

  drawTree(ctx, endX, endY, newLength, angle - spread, depth + 1, maxDepth);
  drawTree(ctx, endX, endY, newLength, angle + spread, depth + 1, maxDepth);
}
```

---

## 8. CELLULAR AUTOMATA

### Conway's Game of Life
```javascript
class GameOfLife {
  constructor(cols, rows) {
    this.cols = cols;
    this.rows = rows;
    this.grid = this.createGrid();
    this.randomize();
  }

  createGrid() {
    return Array(this.rows).fill().map(() => Array(this.cols).fill(0));
  }

  randomize(density = 0.3) {
    for (let y = 0; y < this.rows; y++)
      for (let x = 0; x < this.cols; x++)
        this.grid[y][x] = Math.random() < density ? 1 : 0;
  }

  step() {
    const next = this.createGrid();
    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        const neighbors = this.countNeighbors(x, y);
        if (this.grid[y][x] === 1) {
          next[y][x] = (neighbors === 2 || neighbors === 3) ? 1 : 0;
        } else {
          next[y][x] = (neighbors === 3) ? 1 : 0;
        }
      }
    }
    this.grid = next;
  }

  countNeighbors(x, y) {
    let count = 0;
    for (let dy = -1; dy <= 1; dy++)
      for (let dx = -1; dx <= 1; dx++) {
        if (dx === 0 && dy === 0) continue;
        const nx = (x + dx + this.cols) % this.cols;
        const ny = (y + dy + this.rows) % this.rows;
        count += this.grid[ny][nx];
      }
    return count;
  }
}
```

---

## 9. GEOMETRIC PATTERNS

### Circle Packing
```javascript
function circlePacking(maxAttempts = 10000, minR = 2, maxR = 50) {
  const circles = [];

  for (let i = 0; i < maxAttempts; i++) {
    const x = Math.random() * width;
    const y = Math.random() * height;
    let r = maxR;

    // Shrink to fit
    let valid = true;
    for (const c of circles) {
      const d = Math.hypot(x - c.x, y - c.y);
      if (d < c.r + r) {
        r = d - c.r;
        if (r < minR) { valid = false; break; }
      }
    }

    if (valid && r >= minR) {
      circles.push({ x, y, r });
    }
  }
  return circles;
}
```

### Voronoi-Style Tessellation
```javascript
// Simple distance-based Voronoi
function drawVoronoi(ctx, points, width, height) {
  const imageData = ctx.createImageData(width, height);
  const colors = points.map(() => [
    Math.floor(Math.random() * 200 + 55),
    Math.floor(Math.random() * 200 + 55),
    Math.floor(Math.random() * 200 + 55),
  ]);

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      let minDist = Infinity, closest = 0;
      for (let i = 0; i < points.length; i++) {
        const d = Math.hypot(x - points[i].x, y - points[i].y);
        if (d < minDist) { minDist = d; closest = i; }
      }
      const idx = (y * width + x) * 4;
      imageData.data[idx] = colors[closest][0];
      imageData.data[idx + 1] = colors[closest][1];
      imageData.data[idx + 2] = colors[closest][2];
      imageData.data[idx + 3] = 255;
    }
  }
  ctx.putImageData(imageData, 0, 0);
}
```

---

## 10. COLOR IN GENERATIVE ART

### Palette Generation Strategies

**Noise-Driven Color**:
```javascript
const hue = noise(x * 0.01, y * 0.01) * 60 + 180; // Range: 180-240 (blues)
const sat = 60 + noise(x * 0.02) * 30;
const light = 40 + noise(y * 0.02) * 30;
fill(`hsl(${hue}, ${sat}%, ${light}%)`);
```

**Velocity-Driven Color** (for particles):
```javascript
const speed = Math.hypot(p.vx, p.vy);
const hue = map(speed, 0, maxSpeed, 200, 360); // Slow=blue, fast=red
```

**Age-Driven Color** (fade over lifetime):
```javascript
const alpha = p.life; // 1 → 0
const hue = 200 + (1 - p.life) * 60; // Blue → purple as it ages
fill(`hsla(${hue}, 70%, 60%, ${alpha})`);
```

**Curated Palette with Random Selection**:
```javascript
const palette = ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51'];
const color = palette[Math.floor(random() * palette.length)];
```
