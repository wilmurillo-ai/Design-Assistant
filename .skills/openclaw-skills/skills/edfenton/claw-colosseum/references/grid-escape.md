# Grid Escape

## Overview

Navigate a maze from a start position to an exit. The grid contains walls and open paths. Fog of war limits your visibility to a radius around your position (except on easy, where the full grid is visible). Robbers roam the maze on medium and hard — they patrol randomly until they spot you through a clear line of sight, then chase you aggressively. **Colliding with a robber is instant death — score is set to 0 and the game ends immediately.** Your goal is to reach the exit in as few turns as possible while avoiding all robbers.

**Scoring:** Points accumulate during gameplay: +2 × multiplier per step closer to the exit, +1 per new cell discovered (fog maps only), -1 per wall bump. On reaching the exit, a completion bonus of `max(0, (baseTurns - turnsUsed) × multiplier)` is added. On loss (robber collision or exceeding maxTurns), score is 0.

## Difficulty

| Difficulty | Grid  | Visibility | Robbers | Base Turns | Max Turns | Score Multiplier |
| ---------- | ----- | ---------- | ------- | ---------- | --------- | ---------------- |
| `easy`     | 11×11 | Full       | 0       | 100        | 200       | 1×               |
| `medium`   | 21×21 | 5-cell     | 2       | 300        | 500       | 2×               |
| `hard`     | 41×41 | 3-cell     | 5       | 1000       | 1000      | 5×               |

Robber speed: robbers move **every turn** on both medium and hard — they are just as fast as you. On easy, there are no robbers. Your visibility uses Chebyshev distance (square radius around you). Robbers use Bresenham line-of-sight — they can only see you through clear corridors (walls block their vision). When a robber spots you, it switches to chase mode and pursues you aggressively. When it loses sight, it returns to exploring the maze. Robber vision range matches your visibility radius per difficulty.

## State

Each action response and game state query returns:

```json
{
  "grid": [[0, 1, -1, ...], ...],
  "playerPos": { "x": 1, "y": 1 },
  "exitPos": { "x": 9, "y": 9 },
  "robbers": [{ "x": 5, "y": 3 }],
  "turnCount": 12,
  "maxTurns": 200,
  "status": "playing",
  "score": 0,
  "difficulty": "easy"
}
```

| Field       | Description                                                   |
| ----------- | ------------------------------------------------------------- |
| `grid`      | 2D array. `0` = path, `1` = wall, `-1` = unknown (fog of war) |
| `playerPos` | Your current `{x, y}` position                                |
| `exitPos`   | Exit `{x, y}`, or `null` if outside your visibility radius    |
| `robbers`   | Array of visible robber positions (empty if none visible)     |
| `turnCount` | Turns used so far                                             |
| `maxTurns`  | Turn limit (game lost if exceeded)                            |
| `status`    | `"playing"`, `"won"`, or `"lost"`                             |
| `score`     | Current score (calculated at game end)                        |

## API

**Create:**

```
POST /games/grid-escape
{ "difficulty": "easy" }
```

Returns `{ "data": { "gameId": "uuid", "state": { ... } } }` (HTTP 201).

**Submit action:**

```
POST /games/{gameId}/action
{ "action": "UP" }
```

Actions: `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"`

## Strategy tips

- On easy, you can see the whole maze — use BFS/A\* to find the shortest path.
- On medium/hard, explore efficiently. Track visited cells and prefer unexplored paths.
- Robbers have two modes: **explore** (random patrol, no knowledge of your position) and **chase** (pursues you aggressively when they have line of sight through clear corridors).
- Corridors are dangerous — robbers can see down them. Use corners and walls to break line of sight.
- **Robber collision is instant death (score = 0).** Never let a robber touch you. On hard mode with 5 robbers moving every turn, evasion is critical.
- Minimize total turns — the completion bonus is remaining turns × multiplier, added to your accumulated progress score.

## Gameplay loop pseudocode

```
// Grid Escape — gameplay loop with adaptive pathfinding
response = POST /games/grid-escape { difficulty: "easy" }
gameId = response.gameId
state = response.state
visited = set()
knownGrid = empty 2D map   // tracks revealed cells across turns

while state.status == "playing":
  updateKnownGrid(knownGrid, state.grid)   // merge newly visible cells
  visited.add(state.playerPos)

  if state.exitPos is not null:
    // Exit is visible — pathfind directly (BFS or A* on knownGrid)
    path = shortestPath(knownGrid, state.playerPos, state.exitPos, avoid: state.robbers)
    nextMove = path[0]
  else:
    // Exit not visible — explore: pick nearest unvisited reachable cell
    frontier = [pos for pos in neighbors(state.playerPos)
                where knownGrid[pos] == 0 and pos not in visited]
    if frontier is empty:
      frontier = bfsToNearestUnvisited(knownGrid, state.playerPos, visited)
    nextMove = directionTo(state.playerPos, frontier[0])

  // Robber avoidance: robbers chase when they have line of sight
  // Stay behind corners/walls to avoid detection
  // CRITICAL: robber collision = instant death (score 0). NEVER move into a robber.
  if any robber adjacent to nextMove destination:
    nextMove = safestAlternative(state.playerPos, knownGrid, state.robbers)
    if no safe move exists:
      // All neighbors blocked — pick least risky direction (maximize distance from robbers)
      nextMove = maxDistanceFromRobbers(state.playerPos, knownGrid, state.robbers)

  result = POST /games/{gameId}/action { action: nextMove }
  state = result.state
```

## Advanced strategy development

- Start with BFS to find the shortest path (works on easy)
- Graduate to A\* with Manhattan or Chebyshev distance heuristics
- Add robber prediction: model their movement patterns, avoid likely future positions
- Build fog-of-war memory: maintain a persistent map of revealed cells across turns, track which areas are unexplored, and bias exploration toward the most promising regions

## Testing your strategy

Test cases to cover:

- Pathfinding with walls
- Dead-end recovery
- Robber avoidance when robber blocks the shortest path
- Fog-of-war map merging with contradictory data
