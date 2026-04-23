# Citadel

## Overview

Tower defense against incoming missiles. You control 3 missile silos along the bottom (y=19) of a 30×20 play area, defending 6 cities also at y=19. Incoming missiles rain down from the top (y=0) in waves, arriving in staggered batches of 1-3 every 3 ticks. Fire counter-missiles from your silos to intercept them — counter-missiles explode at their target coordinates with a **radius of 2**, destroying any incoming missiles caught in the blast. If a missile reaches the ground, it destroys the nearest city or silo within **1.5 cells**. **Destroyed silos are repaired between waves** (fully restored with fresh ammo). The game ends when all cities are destroyed or tick reaches 2000.

**Scoring:** +10 per intercept, +5 per multi-kill (extra missile in same explosion), +5 threat priority bonus (intercepting missile near a live city), +3 near-miss bonus (explosion close to but missing a missile), -20 per city destroyed, -10 per silo destroyed. Wave bonus: wave number × 25 + surviving cities × 5 + 10 if accuracy > 50%.

## Waves

Waves get progressively harder. Key breakpoints:

| Wave | Missiles | Speed     | Angle Range  | Ammo/Silo |
| ---- | -------- | --------- | ------------ | --------- |
| 1    | 1        | 1.0       | 0 (straight) | 15        |
| 5    | 15       | 1.5 (cap) | 1            | 12        |
| 10   | 30       | 1.5 (cap) | 2            | 10        |

Between breakpoints values interpolate linearly. Incoming missile speed is **capped at 1.5 cells/tick** (counter-missiles travel at 2 — you are always faster). Missiles arrive in **staggered batches of 1-3** throughout the wave (new batch every 3 ticks), not all at once. Beyond wave 10, missiles scale +1/wave with **no cap** (wave 100 = 120 missiles), ammo -1 per 5 waves (min 5). Explosions last 3 ticks.

## State

```json
{
  "tick": 15,
  "cities": [
    { "x": 2, "y": 19, "alive": true },
    { "x": 7, "y": 19, "alive": true }
  ],
  "silos": [
    { "x": 5, "y": 19, "ammo": 12, "alive": true, "cooldown": 0 },
    { "x": 15, "y": 19, "ammo": 10, "alive": true, "cooldown": 2 },
    { "x": 25, "y": 19, "ammo": 0, "alive": false, "cooldown": 0 }
  ],
  "incomingMissiles": [{ "x": 12, "y": 8, "dx": 0, "dy": 1, "ticksRemaining": 8 }],
  "explosions": [{ "x": 10, "y": 12, "radius": 2, "ticksRemaining": 2 }],
  "counterMissiles": [{ "x": 5, "y": 15, "targetX": 12, "targetY": 8, "ticksRemaining": 4 }],
  "wave": 1,
  "score": 30,
  "status": "playing"
}
```

| Field              | Description                                                                             |
| ------------------ | --------------------------------------------------------------------------------------- |
| `tick`             | Current tick within the wave                                                            |
| `cities`           | 6 cities with position and alive status                                                 |
| `silos`            | 3 silos with position, ammo, alive status, and cooldown timer                           |
| `silos[].alive`    | `true` if silo is intact, `false` if destroyed by incoming missile (repaired next wave) |
| `silos[].cooldown` | Ticks until silo can fire again (0 = ready, 2 after firing)                             |
| `incomingMissiles` | Active threats. `dx`/`dy` = velocity, `ticksRemaining` = ticks to ground                |
| `explosions`       | Active blasts. Anything within `radius` is destroyed                                    |
| `counterMissiles`  | Your in-flight shots heading toward `targetX`/`targetY`                                 |
| `wave`             | Current wave number                                                                     |
| `score`            | Running score                                                                           |
| `status`           | `"playing"`, `"wave_complete"`, or `"game_over"`                                        |

## API

**Create:**

```
POST /games/citadel
```

No request body. Returns `{ "data": { "gameId": "uuid", "state": { ... } } }` (HTTP 201).

**Submit action (each tick):**

Fire a counter-missile:

```
POST /games/{gameId}/action
{
  "action": {
    "action": "FIRE",
    "siloIndex": 0,
    "targetX": 15,
    "targetY": 10
  }
}
```

Or wait (skip this tick):

```
POST /games/{gameId}/action
{ "action": { "action": "WAIT" } }
```

`siloIndex` selects which silo fires (0, 1, or 2). `targetX`/`targetY` is where the counter-missile detonates. All values must be integers within the play area (0-29 for X, 0-19 for Y).

**Errors:** `SILO_DESTROYED` (silo destroyed this wave — it repairs next wave), `SILO_ON_COOLDOWN` (silo fired recently, wait for cooldown), `NO_AMMO` (silo empty), `INVALID_SILO` (bad index), `TARGET_OUT_OF_BOUNDS`, `ONE_ACTION_PER_TICK` (already submitted this tick).

## Strategy tips

- **Protect your silos during the wave.** A destroyed silo can't fire for the rest of the wave (they repair between waves). Prioritize intercepting missiles heading toward silos to maintain firepower.
- **Rotate between silos.** Each silo has a 2-tick cooldown after firing. Fire silo 0, then 1, then 2 — by the time you cycle back, silo 0 is ready. Check `silo.cooldown === 0` and `silo.alive === true` before firing.
- Lead your shots — counter-missiles travel at 2 cells/tick. Predict where incoming missiles will be when your counter-missile arrives.
- Prioritize missiles heading toward surviving cities and silos. Ignore missiles heading toward dead cities.
- Use the explosion radius (2 cells) to intercept multiple missiles with one shot — multi-kills earn +5 bonus per extra missile.
- Target missiles near live cities for the +5 threat priority bonus.
- Wave 1 starts with just 1 missile. Early waves are gentle — conserve ammo for accuracy bonus (+10 if > 50% hit rate).

## Gameplay loop pseudocode

```
// Citadel — gameplay loop with intercept prediction
response = POST /games/citadel
gameId = response.gameId
state = response.state

while state.status != "game_over":
  if state.status == "wave_complete":
    // Any action advances to the next wave
    result = POST /games/{gameId}/action { action: { action: "WAIT" } }
    state = result.state
    continue

  // Find most threatening missile (lowest ticksRemaining, heading toward a live city or silo)
  threats = [m for m in state.incomingMissiles
             where anyCityOrSiloNear(m.x + m.dx * m.ticksRemaining, state.cities, state.silos)]
  sortBy(threats, m.ticksRemaining ascending)

  // Find ready silos: alive, has ammo, off cooldown
  readySilos = [s for s in state.silos where s.alive AND s.ammo > 0 AND s.cooldown == 0]

  if threats is empty or readySilos is empty:
    result = POST /games/{gameId}/action { action: { action: "WAIT" } }
  else:
    target = threats[0]
    // Predict where missile will be when counter-missile arrives
    // Counter-missiles travel at 2 cells/tick from silo to target
    silo = closestSilo(readySilos, target)
    distance = euclidean(silo.x, silo.y, target.x, target.y)
    travelTicks = ceil(distance / 2)
    interceptX = clamp(target.x + target.dx * travelTicks, 0, 29)
    interceptY = clamp(target.y + target.dy * travelTicks, 0, 19)

    result = POST /games/{gameId}/action { action: {
      action: "FIRE", siloIndex: silo.index,
      targetX: round(interceptX), targetY: round(interceptY)
    }}
  state = result.state
```

## Advanced strategy development

- Start with nearest-threat targeting (fire at the closest incoming missile from the nearest **ready** silo — must be alive, have ammo, and cooldown === 0)
- Rotate between silos: each silo has a 2-tick cooldown after firing, so cycle through all 3 to maintain fire rate
- Develop intercept prediction: calculate where a missile will be when your counter-missile arrives, accounting for travel time from the selected silo (counter-missiles travel at 2 cells/tick, incoming missiles are capped at 1.5 cells/tick)
- Optimize multi-missile interception: cluster nearby missiles and target the center of the cluster to destroy multiple threats with one explosion (radius = 2)
- Missiles arrive staggered (batches of 1-3 every 3 ticks) — don't waste ammo on early missiles when later batches may be more dangerous
- Protect your silos: incoming missiles destroy silos on ground impact (within 1.5 cells), losing a silo means no fire from it for the rest of the wave (it repairs between waves)

## Testing your strategy

Test cases to cover:

- Intercept timing at different silo distances
- Multi-missile clustering
- Behavior when all silos are empty
- Wave transition handling
