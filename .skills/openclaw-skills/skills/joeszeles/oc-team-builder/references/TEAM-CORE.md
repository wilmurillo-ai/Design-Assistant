# Core Team

The permanent OpenClaw agents. These are always running and form the backbone of all operations.

## CEO — Leader & Orchestrator

- **Workspace**: `.openclaw/workspace/`
- **Role**: Leader of the entire OpenClaw network. Manages all subagents, orchestrates workflows, final authority on deliverables.
- **Key files**: `SOUL.md`, `AGENTS.md`

### CEO Capabilities
- Routes tasks to the engineering team pipeline: @planner → @coder → @reviewer → @tester
- Manages all inter-agent communication via `sessions_send`
- Activates specialist teams from the Agency roster when needed
- Final sign-off authority — nothing ships without CEO approval

### CEO as Team Leader
The CEO is the top of the command structure. When a task arrives:
1. CEO receives the request
2. CEO reads `PLANNER.md` (or delegates to @planner) to scope the work
3. CEO selects and activates the right specialists
4. CEO orchestrates execution through the team pipeline
5. CEO runs the review process via `REVIEWER.md` before delivering

## Artist — Visual Creative

- **Workspace**: `.openclaw/workspace-artist/`
- **Role**: Image generation, visual analysis, and creative output using xAI models
- **Key files**: `SOUL.md`, `IDENTITY.md`

### Artist Capabilities
- Image generation via xAI models
- Image analysis via vision models
- Video generation
- Generated images served from `/generated/` directory

### Artist Team Connections
- Works with **Image Prompt Engineer** for structured, professional prompts
- Works with **Visual Storyteller** for narrative-driven visual content
- Works with **Research Lab** for iterative image analysis (astronomy, medical, satellite imagery)
- Works with **Brand Guardian** for brand-consistent visual output

## Routing Rules

| Request Type | Primary Agent | Support Agents |
|-------------|---------------|----------------|
| Image generation / visual | Artist | Image Prompt Engineer |
| Code / engineering tasks | CEO → @planner pipeline | Agency Engineering |
| General management | CEO | As needed |
| Cross-domain projects | CEO (orchestrate) | Mix from all rosters |
| Research / optimization | CEO + Research Lab | Relevant specialists |

## Inter-Agent Communication

Agents communicate through OpenClaw's `sessions_send` mechanism:
- CEO → `@artist` for visual tasks
- CEO → `@planner` / `@coder` / `@reviewer` / `@tester` for engineering pipeline
- Any agent can reference team-builder skill to propose specialist activation
