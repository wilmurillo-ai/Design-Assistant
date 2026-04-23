---
name: physics-tutorial-video
version: 1.0.1
displayName: "Physics Tutorial Video Maker — Create Physics Lessons and Experiment Videos"
description: >
  Physics Tutorial Video Maker — Create Physics Lessons and Experiment Videos.
metadata: {"openclaw": {"emoji": "⚛️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Physics Tutorial Video Maker — Physics Lessons and Experiment Videos

The professor wrote F=ma on the board, said "this is intuitive," and moved on — leaving half the lecture hall wondering why a formula that predicts everything from car crashes to rocket launches was supposed to be obvious to someone who last thought about force when they dropped their phone. Physics education on YouTube fills the gap between textbook derivations that assume you already understand the concept and pop-science videos that skip the math entirely, leaving you with a vague sense of wonder but no ability to solve a problem. The channels that genuinely teach physics are the ones that start with the phenomenon (why does a spinning gyroscope resist falling over?), show the math that explains it (angular momentum conservation), and connect it back to something the viewer can test (spin a bicycle wheel and try to tilt it). This tool transforms physics concepts, problem walkthroughs, and experiment demonstrations into polished tutorial videos — animated force diagrams with vectors that scale to magnitude, step-by-step equation derivations where each algebraic move appears sequentially, experiment demonstrations with slow-motion replay and measurement overlays, energy-transfer visualizations showing kinetic and potential as animated bar charts, wave and field animations that make invisible phenomena visible, and the "pause and try it yourself" problem segments that turn passive watching into active learning. Built for physics teachers creating flipped-classroom content, tutors building problem-set video libraries, university lecturers supplementing in-person courses, science communicators making physics accessible, students creating study-group explanation videos, and anyone who believes that physics is beautiful but only after the moment it clicks.

## Example Prompts

### 1. Concept + Problem — Newton's Second Law Applied
"Create an 8-minute video teaching Newton's Second Law through real-world problems. Opening (0-20 sec): a hockey puck sliding on ice, then hit by a stick — it accelerates. 'The puck was moving at a constant velocity. Then a force was applied and the velocity changed. The relationship between force, mass, and acceleration is the most useful equation in classical mechanics.' The law (20-80 sec): F = ma on screen, then expanded: 'The net force on an object equals its mass times its acceleration. Net force — not just any force. If you push a book across a table, friction pushes back. The book accelerates based on the net force, not your push alone.' Animated free-body diagram: a box on a surface with applied force arrow, friction arrow opposing it, normal force up, gravity down. 'Four forces. The vertical ones cancel (normal = gravity on a flat surface). The horizontal net force determines acceleration.' Problem 1 (80-200 sec): 'A 5 kg box is pushed with 30 N of force across a surface with friction coefficient 0.2. Find the acceleration.' Step by step on screen: friction = μ × N = 0.2 × (5 × 9.8) = 9.8 N. Net force = 30 - 9.8 = 20.2 N. Acceleration = F/m = 20.2/5 = 4.04 m/s². Show each step appearing with the algebra highlighted. 'The box accelerates at 4 m/s². Without friction, it would accelerate at 6 m/s². Friction stole one-third of your force.' Problem 2 — inclined plane (200-360 sec): 'A 10 kg block slides down a 30° frictionless ramp. Find the acceleration.' Animated diagram: the block on the ramp, gravity decomposed into parallel (mg sin θ) and perpendicular (mg cos θ) components. 'This decomposition is the key skill. Gravity always points down, but the ramp rotates our coordinate system.' Step by step: a = g sin θ = 9.8 × sin 30° = 9.8 × 0.5 = 4.9 m/s². 'Half of gravitational acceleration. On a steeper ramp, more of gravity's force goes into acceleration. At 90°, you're in free fall.' Problem 3 — Atwood machine (360-440 sec): two masses on a pulley. 'Mass 1 = 8 kg, Mass 2 = 5 kg. Find the acceleration of the system and the tension in the rope.' Free-body diagrams for both masses. Set up equations: for m1 (going down): m1g - T = m1a. For m2 (going up): T - m2g = m2a. Add equations: (m1-m2)g = (m1+m2)a. Solve: a = (3)(9.8)/13 = 2.26 m/s². Tension: T = m2(g+a) = 5(12.06) = 60.3 N. 'Pause here and try it before I show the answer' — 5-second pause with the problem on screen. Closing (440-480 sec): 'F = ma is three letters and it predicts everything from an elevator ride to a satellite orbit. The skill isn't memorizing the formula — it's drawing the free-body diagram correctly. Every physics problem starts with the diagram.'"

### 2. Experiment Demo — Conservation of Energy
"Build a 6-minute energy conservation demonstration with real measurements. Opening: a pendulum — 'I'm going to hold this bowling ball against my nose, release it, and not flinch. The reason I won't flinch is math.' The concept (0-60 sec): animated energy bar chart — 'Energy converts between forms but the total stays constant. When the pendulum is at its highest point: maximum potential energy, zero kinetic. At the lowest point: zero potential, maximum kinetic.' Show the bars trading — PE decreasing as KE increases, total constant. The equation: mgh = ½mv². 'Mass cancels. The speed at the bottom depends only on the height, not the mass.' Demo 1 — pendulum (60-180 sec): real footage of the pendulum swing with measurement overlay. Release height measured: 1.2 m. Predicted speed at bottom: v = √(2gh) = √(2 × 9.8 × 1.2) = 4.85 m/s. Measured speed with a photogate: 4.71 m/s. 'The prediction was 4.85, the measurement was 4.71 — 97% agreement. The missing 3% is air resistance and the string's mass.' The nose test: hold the ball to the nose, release (slow-motion of the ball swinging away and returning, stopping just short). 'It can never swing higher than the release point because that would require more energy than the system has. Physics saves my nose.' Demo 2 — ramp and loop (180-320 sec): a ball rolling down a ramp into a vertical loop. 'What's the minimum height for the ball to complete the loop without falling?' The physics: at the top of the loop, the ball needs minimum centripetal acceleration = g. That means v² = gR at the top. Energy conservation from height h to the top of the loop (height 2R): mgh = mg(2R) + ½mv². Solve: h = 2R + R/2 = 2.5R. 'The release height must be at least 2.5 times the loop radius.' Demo: loop radius = 0.2 m. Minimum height = 0.5 m. Test at 0.45 m — ball falls. Test at 0.5 m — ball barely completes the loop. Test at 0.6 m — comfortable loop. Show each attempt with slow-motion and speed overlay. Closing: 'Energy conservation isn't an abstract rule. It's why the pendulum doesn't hit my nose, why the roller coaster needs the first hill to be the tallest, and why you can predict the outcome of a system with a single equation before running the experiment.'"

### 3. Visual Explainer — How Electromagnetic Waves Work
"Produce a 5-minute visual explainer on electromagnetic waves. Opening: turn on a flashlight — 'The light leaving this flashlight is an electromagnetic wave. It's an electric field and a magnetic field oscillating perpendicular to each other, traveling at 300 million meters per second, and it requires no medium — it works in a vacuum. Let's see what that actually looks like.' The wave (0-80 sec): animated EM wave — electric field oscillating vertically (red), magnetic field oscillating horizontally (blue), propagating forward. 'The electric field creates the magnetic field. The magnetic field creates the electric field. They sustain each other — that's why light travels through empty space. No air needed.' Show the wavelength and frequency labeled. 'Wavelength × frequency = speed of light. Always. Longer wavelength = lower frequency = lower energy.' The spectrum (80-200 sec): animated spectrum expanding from visible light outward. Start with visible (red to violet, 700nm to 400nm). Expand left: infrared (your TV remote), microwaves (your kitchen), radio waves (your phone). 'Radio waves are light. Just light your eyes can't see, with wavelengths measured in meters instead of nanometers.' Expand right: ultraviolet (sunburn), X-rays (hospital), gamma rays (nuclear). 'The only difference between radio waves and gamma rays is wavelength. They're all electromagnetic waves traveling at the same speed.' Each type labeled with wavelength, frequency, and one real-world use. How they're made (200-280 sec): animated — 'Accelerate a charged particle and it emits an electromagnetic wave.' Show an electron oscillating up and down — waves radiating outward. 'In your phone antenna, electrons oscillate billions of times per second, radiating radio waves.' In a light bulb: 'Atoms vibrate from heat, their electrons accelerate, emitting infrared and visible light.' In an X-ray machine: 'Electrons are smashed into a metal target. The sudden deceleration emits high-energy X-rays.' Why the speed is constant (280-340 sec): 'Maxwell's equations predict the speed of electromagnetic waves from two constants: the permittivity and permeability of free space. The result is exactly 299,792,458 m/s. No one told light how fast to go — it emerged from the equations.' Show Maxwell's derivation (simplified): c = 1/√(ε₀μ₀). 'Einstein read this and asked: what if this speed is the same for every observer? That question became special relativity.' Closing: the flashlight again — 'This beam is 10²⁰ photons per second, each an oscillating electromagnetic wave, traveling at the fastest speed the universe allows, generated by electrons in a filament moving less than a millimeter. Physics is not boring.'"

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the physics topic, problems, experiments, and target student level |
| `duration` | string | | Target video length (e.g. "5 min", "6 min", "8 min") |
| `style` | string | | Video style: "concept-problem", "experiment-demo", "visual-explainer", "derivation", "exam-review" |
| `music` | string | | Background audio: "ambient-study", "curious-electronic", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `equations` | boolean | | Show step-by-step equation derivations on screen (default: true) |
| `diagrams` | boolean | | Generate animated free-body diagrams and force vectors (default: true) |

## Workflow

1. **Describe** — Outline the physics concept, problems, experiments, and student level
2. **Upload (optional)** — Add experiment footage, whiteboard recordings, or simulation outputs
3. **Generate** — AI produces the tutorial with equations, diagrams, and experiment overlays
4. **Review** — Verify physics accuracy, equation steps, and unit consistency
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "physics-tutorial-video",
    "prompt": "Create an 8-minute Newton Second Law tutorial: hockey puck opening hook, F=ma with net force emphasis, animated free-body diagram of box on surface, 3 problems with step-by-step algebra (flat surface with friction, inclined plane decomposition, Atwood machine), pause-and-try segment before each solution",
    "duration": "8 min",
    "style": "concept-problem",
    "equations": true,
    "diagrams": true,
    "music": "ambient-study",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Start with the phenomenon, not the equation** — A hockey puck accelerating when hit is interesting; "F=ma" written on a blank screen is not. The AI places your described real-world observation before the mathematical framework.
2. **Show equations appearing step by step** — Each algebraic manipulation appearing sequentially lets viewers follow the logic. The AI animates equation derivations line by line when equations is enabled.
3. **Include "pause and try" moments** — Display the problem for 5 seconds before showing the solution. The AI inserts pause-prompt graphics when you describe try-it-yourself segments.
4. **Use animated free-body diagrams** — Force vectors that scale to magnitude and decompose on inclines make abstract forces visible. The AI generates proportional vector diagrams when diagrams is enabled.
5. **Connect the math back to reality** — "The missing 3% is air resistance" validates both the theory and the real world. The AI highlights theory-vs-measurement comparisons when you describe experimental verification.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube physics tutorial / course content |
| MP4 9:16 | 1080p | TikTok / YouTube Shorts physics fact |
| MP4 1:1 | 1080p | Instagram post / LinkedIn education |
| GIF | 720p | Diagram animation loop / Reddit physics |

## Related Skills

- [chemistry-lesson-video](/skills/chemistry-lesson-video) — Chemistry lesson and reaction videos
- [biology-education-video](/skills/biology-education-video) — Biology and life science education videos
- [science-explainer-video](/skills/science-explainer-video) — Science education and concept videos
