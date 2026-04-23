# 3D & WebGL Reference

Use this reference for: Three.js scenes, 3D product renders, 3D typography, WebGL shaders, GLSL,
ray marching, procedural geometry, 3D environments, isometric 3D, low-poly art, voxel art,
and any task requiring 3D rendering or shader-based visual effects.

---

## TABLE OF CONTENTS
1. Three.js Scene Setup
2. Lighting & Materials
3. Geometry & Modeling
4. Camera & Controls
5. Post-Processing Effects
6. Shader Fundamentals (GLSL)
7. Common 3D Compositions
8. Performance Optimization

---

## 1. THREE.JS SCENE SETUP

### Minimal Scene Template
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<canvas id="scene"></canvas>
<script>
// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a1a);

// Camera
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 2, 5);
camera.lookAt(0, 0, 0);

// Renderer
const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById('scene'),
  antialias: true,
  alpha: true,
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;

// Responsive
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  // Update logic here
  renderer.render(scene, camera);
}
animate();
</script>
```

### Scene with OrbitControls Alternative
Since OrbitControls is not available from the r128 CDN, implement basic orbit:
```javascript
// Simple mouse-driven orbit
let mouseX = 0, mouseY = 0;
let targetRotationX = 0, targetRotationY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
  mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
});

function animate() {
  requestAnimationFrame(animate);
  targetRotationY += (mouseX * 0.5 - targetRotationY) * 0.05;
  targetRotationX += (mouseY * 0.3 - targetRotationX) * 0.05;
  camera.position.x = Math.sin(targetRotationY) * 5;
  camera.position.z = Math.cos(targetRotationY) * 5;
  camera.position.y = 2 + targetRotationX * 2;
  camera.lookAt(0, 0, 0);
  renderer.render(scene, camera);
}
```

---

## 2. LIGHTING & MATERIALS

### Three-Point Lighting Setup
```javascript
// Key light (main illumination)
const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
keyLight.position.set(5, 5, 5);
keyLight.castShadow = true;
keyLight.shadow.mapSize.width = 2048;
keyLight.shadow.mapSize.height = 2048;
scene.add(keyLight);

// Fill light (soften shadows)
const fillLight = new THREE.DirectionalLight(0x8888ff, 0.4);
fillLight.position.set(-3, 2, -2);
scene.add(fillLight);

// Rim/back light (edge definition)
const rimLight = new THREE.DirectionalLight(0xffffff, 0.6);
rimLight.position.set(0, 3, -5);
scene.add(rimLight);

// Ambient (base illumination, prevents pure black)
const ambient = new THREE.AmbientLight(0x404040, 0.3);
scene.add(ambient);
```

### Material Types

**MeshStandardMaterial** (PBR - the default choice):
```javascript
const material = new THREE.MeshStandardMaterial({
  color: 0x3b82f6,
  metalness: 0.3,       // 0 = plastic, 1 = metal
  roughness: 0.4,       // 0 = mirror, 1 = chalk
  emissive: 0x000000,   // Self-illumination color
  emissiveIntensity: 0,
});
```

**MeshPhysicalMaterial** (Advanced PBR):
```javascript
const glass = new THREE.MeshPhysicalMaterial({
  color: 0xffffff,
  metalness: 0,
  roughness: 0.05,
  transmission: 0.95,    // Transparency (glass-like)
  thickness: 0.5,        // Refraction depth
  ior: 1.5,              // Index of refraction (glass = 1.5)
  clearcoat: 1.0,
  clearcoatRoughness: 0.1,
});
```

**ShaderMaterial** (Custom):
```javascript
const customMaterial = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uColor: { value: new THREE.Color(0x3b82f6) },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    void main() {
      float wave = sin(vUv.x * 10.0 + uTime) * 0.5 + 0.5;
      gl_FragColor = vec4(uColor * wave, 1.0);
    }
  `,
});
```

---

## 3. GEOMETRY & MODELING

### Primitive Geometries
```javascript
// NOTE: Do NOT use CapsuleGeometry (introduced in r142, unavailable in r128)
// Use CylinderGeometry + SphereGeometry as alternatives

new THREE.BoxGeometry(1, 1, 1);                         // width, height, depth
new THREE.SphereGeometry(0.5, 32, 32);                  // radius, widthSeg, heightSeg
new THREE.CylinderGeometry(0.5, 0.5, 1, 32);           // topR, bottomR, height, segments
new THREE.TorusGeometry(0.5, 0.15, 16, 32);             // radius, tube, radialSeg, tubularSeg
new THREE.PlaneGeometry(10, 10);                         // width, height
new THREE.RingGeometry(0.3, 0.5, 32);                   // innerR, outerR, segments
new THREE.IcosahedronGeometry(0.5, 0);                  // radius, detail (0=icosa, higher=sphere)
new THREE.OctahedronGeometry(0.5, 0);                   // radius, detail
new THREE.DodecahedronGeometry(0.5, 0);                 // radius, detail
new THREE.TorusKnotGeometry(0.5, 0.15, 100, 16, 2, 3); // Complex knot shape
new THREE.ConeGeometry(0.5, 1, 32);                     // radius, height, segments
```

### Procedural Geometry (Custom Shapes)
```javascript
const geometry = new THREE.BufferGeometry();
const vertices = new Float32Array([
  // Triangle
  -0.5, -0.5, 0,
   0.5, -0.5, 0,
   0.0,  0.5, 0,
]);
geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
```

### Grouped Objects (Models)
```javascript
const group = new THREE.Group();

const body = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1.5, 0.8),
  new THREE.MeshStandardMaterial({ color: 0x3b82f6 })
);
group.add(body);

const head = new THREE.Mesh(
  new THREE.SphereGeometry(0.4, 32, 32),
  new THREE.MeshStandardMaterial({ color: 0xfbbf24 })
);
head.position.y = 1.2;
group.add(head);

scene.add(group);
```

---

## 4. CAMERA & CONTROLS

### Camera Types
```javascript
// Perspective (natural, depth perception)
const perspCam = new THREE.PerspectiveCamera(
  50,   // FOV (degrees) — 30=telephoto, 50=normal, 90=wide
  aspect,
  0.1,  // Near plane
  1000  // Far plane
);

// Orthographic (flat, architectural, isometric)
const orthoCam = new THREE.OrthographicCamera(
  -5, 5,   // left, right
  5, -5,   // top, bottom
  0.1, 100 // near, far
);
```

### Isometric Camera Setup
```javascript
const d = 5;
const camera = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 0.1, 1000);
camera.position.set(10, 10, 10);
camera.lookAt(0, 0, 0);
// True isometric angle
```

### Smooth Camera Animation
```javascript
function animateCamera(target, duration = 2000) {
  const start = { ...camera.position };
  const startTime = performance.now();

  function update() {
    const elapsed = performance.now() - startTime;
    const t = Math.min(elapsed / duration, 1);
    const eased = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

    camera.position.x = start.x + (target.x - start.x) * eased;
    camera.position.y = start.y + (target.y - start.y) * eased;
    camera.position.z = start.z + (target.z - start.z) * eased;
    camera.lookAt(0, 0, 0);

    if (t < 1) requestAnimationFrame(update);
  }
  update();
}
```

---

## 5. POST-PROCESSING EFFECTS

### Fog (Atmospheric Depth)
```javascript
scene.fog = new THREE.Fog(0x0a0a1a, 5, 20);        // Color, near, far
scene.fog = new THREE.FogExp2(0x0a0a1a, 0.08);      // Exponential fog (more natural)
```

### Custom Bloom Glow (without EffectComposer)
```javascript
// Emissive materials create a glow feel without post-processing
const glowMaterial = new THREE.MeshStandardMaterial({
  color: 0x3b82f6,
  emissive: 0x3b82f6,
  emissiveIntensity: 0.5,
  metalness: 0.5,
  roughness: 0.2,
});

// Combine with a slightly larger transparent clone for fake bloom
const glowHalo = new THREE.Mesh(
  new THREE.SphereGeometry(0.55, 32, 32),
  new THREE.MeshBasicMaterial({
    color: 0x3b82f6,
    transparent: true,
    opacity: 0.15,
  })
);
```

---

## 6. SHADER FUNDAMENTALS (GLSL)

### Vertex Shader Template
```glsl
uniform float uTime;
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);
  vPosition = position;

  // Deformation example
  vec3 pos = position;
  pos.z += sin(pos.x * 3.0 + uTime) * 0.2;

  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
```

### Fragment Shader Template
```glsl
uniform float uTime;
uniform vec2 uResolution;
varying vec2 vUv;
varying vec3 vNormal;

void main() {
  // Gradient based on UV
  vec3 color = mix(vec3(0.2, 0.4, 0.9), vec3(0.9, 0.3, 0.5), vUv.y);

  // Simple rim lighting
  float rim = 1.0 - dot(vNormal, vec3(0.0, 0.0, 1.0));
  rim = pow(rim, 3.0);
  color += vec3(0.3, 0.5, 1.0) * rim;

  gl_FragColor = vec4(color, 1.0);
}
```

### Common GLSL Patterns

**Noise (Simplex approximation)**:
```glsl
float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
    mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
    f.y
  );
}
```

**SDF Circle**:
```glsl
float sdCircle(vec2 p, float r) {
  return length(p) - r;
}
```

**Color palette function**:
```glsl
vec3 palette(float t) {
  vec3 a = vec3(0.5); vec3 b = vec3(0.5);
  vec3 c = vec3(1.0); vec3 d = vec3(0.263, 0.416, 0.557);
  return a + b * cos(6.28318 * (c * t + d));
}
```

---

## 7. COMMON 3D COMPOSITIONS

### Floating Objects Scene
```javascript
// Create multiple objects floating in space
const objects = [];
for (let i = 0; i < 20; i++) {
  const geometry = [
    new THREE.BoxGeometry(0.5, 0.5, 0.5),
    new THREE.SphereGeometry(0.3, 16, 16),
    new THREE.OctahedronGeometry(0.3),
    new THREE.TorusGeometry(0.3, 0.1, 8, 16),
  ][Math.floor(Math.random() * 4)];

  const material = new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(Math.random() * 0.1 + 0.55, 0.7, 0.6),
    metalness: 0.3,
    roughness: 0.4,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(
    (Math.random() - 0.5) * 8,
    (Math.random() - 0.5) * 8,
    (Math.random() - 0.5) * 8
  );
  mesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
  mesh.userData.rotSpeed = (Math.random() - 0.5) * 0.02;
  mesh.userData.floatSpeed = Math.random() * 0.002 + 0.001;
  mesh.userData.floatOffset = Math.random() * Math.PI * 2;

  scene.add(mesh);
  objects.push(mesh);
}

// Animate
function animate() {
  requestAnimationFrame(animate);
  const time = performance.now() * 0.001;
  objects.forEach(obj => {
    obj.rotation.y += obj.userData.rotSpeed;
    obj.position.y += Math.sin(time + obj.userData.floatOffset) * obj.userData.floatSpeed;
  });
  renderer.render(scene, camera);
}
```

### Ground Plane with Grid
```javascript
// Ground plane
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(50, 50),
  new THREE.MeshStandardMaterial({ color: 0x1a1a2e })
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

// Grid helper
const grid = new THREE.GridHelper(50, 50, 0x333366, 0x222244);
grid.material.opacity = 0.3;
grid.material.transparent = true;
scene.add(grid);
```

---

## 8. PERFORMANCE OPTIMIZATION

### Geometry
- Reuse geometries: Don't create new geometry for identical shapes
- Use `InstancedMesh` for many identical objects
- Lower segment counts for objects far from camera
- Merge static geometries with `BufferGeometryUtils.mergeBufferGeometries`

### Materials
- Reuse materials across similar objects
- Use `MeshBasicMaterial` for unlit objects (no lighting calculation)
- Limit transparent objects (they prevent depth sorting optimization)

### Rendering
- Set `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))` — cap at 2x
- Use `renderer.info` to monitor draw calls, triangles, textures
- Frustum culling is automatic — position off-screen objects outside the view
- For static scenes, render once and stop the animation loop

### Shadow Optimization
- Only enable `castShadow` on objects that need it
- Keep `shadow.mapSize` reasonable (1024 is usually fine)
- Use `shadow.camera` frustum to tightly bound the shadow area
