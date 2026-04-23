# Project Patterns

Use this reference when the request is still fuzzy and you need a stronger recommendation for scope, stack, or sequencing.

## 1. Webpage Or Microsite

Best for:

- interactive showcase
- landing page
- small utility with one core flow
- portfolio or single-topic site

Default bias:

- start with static `HTML + CSS + JavaScript`
- use `localStorage` for lightweight persistence
- avoid frameworks unless state or routing complexity is real

MVP checklist:

- one clear page goal
- one primary interaction
- one polished visual direction
- mobile layout
- simple persistence if useful

Common overbuild trap:

- turning a playful single-page idea into a full app too early

## 2. Web App Or Dashboard

Best for:

- repeat use over time
- multi-screen workflows
- data entry, filtering, or tracking
- authenticated or role-based systems

Default bias:

- React or Next.js only if multiple views or substantial state are required
- mock local data before real backend wiring
- add auth only if it changes the real user value

MVP checklist:

- one primary user role
- one core workflow
- one source of truth for data
- clear empty state and error state

Common overbuild trap:

- shipping auth, settings, billing, and notifications before the main job works

## 3. Codex Skill

Best for:

- repeatable planning or execution workflows
- domain guidance Codex should follow consistently
- lightweight procedural knowledge with optional references or scripts

Default bias:

- keep `SKILL.md` lean and procedural
- use `references/` for deeper guidance
- add scripts only when deterministic execution matters

MVP checklist:

- clear trigger description
- one reusable workflow
- one strong output format
- minimal but useful reference material

Common overbuild trap:

- writing a human README instead of an agent-facing skill

## 4. Automation

Best for:

- recurring summaries
- scheduled checks
- inbox-style monitoring
- repetitive status gathering

Default bias:

- define trigger, cadence, workspace, and output first
- keep prompts self-sufficient
- avoid multi-step workflows that need frequent human rescue

MVP checklist:

- one repeated job
- one schedule
- one output destination
- clear skip conditions

Common overbuild trap:

- trying to automate judgment-heavy work with vague prompts

## 5. Script Or CLI Tool

Best for:

- local file transforms
- repetitive developer tasks
- structured data cleanup
- deterministic utility work

Default bias:

- prefer a simple script with clear inputs and outputs
- optimize for repeatability before polish
- write usage examples into the plan

MVP checklist:

- explicit input source
- explicit output destination
- predictable flags or parameters
- basic error handling

Common overbuild trap:

- wrapping a small script in an unnecessary UI

## Decision Heuristics

Choose the simpler option when these are true:

- one user role
- one main workflow
- no cross-device sync required
- no mandatory collaboration
- no complex permissions
- no backend-only dependency

Choose the heavier option only when the MVP truly needs it:

- authenticated data
- multi-user collaboration
- server-side integrations
- long-lived storage beyond the local machine
- complex search, filtering, or data relationships

## Scope-Cutting Prompts

Use one or more of these internally when the user idea is too broad:

- What is the smallest version someone would still finish using?
- What can be removed without breaking the core loop?
- What belongs in version two even if it sounds exciting now?
- What can be mocked locally before building real infrastructure?
- Which feature adds the most complexity per unit of user value?
