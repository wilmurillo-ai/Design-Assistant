---
name: project-kickoff
description: Turn a vague product, webpage, app, workflow, automation, plugin, or skill idea into an actionable kickoff plan. Use when Codex needs to scope a new project from scratch, define the MVP, choose a stack, break work into phases, identify risks, or convert a rough idea into concrete build steps.
---

# Project Kickoff

## Overview

Use this skill to turn an early idea into a buildable plan without forcing the user to already know product, design, or engineering language.

Default to momentum. Make reasonable assumptions, state them, and only stop to ask questions when the answer changes architecture, cost, or delivery risk in a non-obvious way.

## Core Workflow

Follow this order unless the user explicitly asks for only one part.

1. Classify the project.
2. Extract the real goal.
3. Define the smallest valuable version.
4. Choose the delivery shape.
5. Break implementation into phases.
6. Flag risks, unknowns, and decisions.
7. End with the clearest next action.

## 1. Classify The Project

Map the request into one primary type before planning:

- `web-page`: landing page, interactive site, dashboard, mini tool, portfolio
- `web-app`: authenticated app, CRUD product, SaaS, internal tool
- `skill`: reusable Codex skill with workflows, references, or scripts
- `plugin`: Codex plugin or integration surface
- `automation`: recurring task, scheduled workflow, inbox automation
- `script-tool`: CLI helper, local utility, data processor
- `content-system`: CMS-backed site, documentation hub, blog, knowledge base

If the request spans multiple types, choose the build target that delivers the first usable value and mention the other types as later phases.

## 2. Extract The Real Goal

Rewrite the request as a plain-language product goal:

- Who is it for?
- What frustrating job should it solve?
- What should feel better after using it?
- What makes it interesting enough to deserve building?

If the user gives only a theme, infer a likely user and use case. Mark that inference explicitly.

## 3. Define The MVP

Reduce the project to the smallest version that still feels complete.

For the MVP:

- Include only the core loop
- Prefer one polished flow over many partial features
- Remove admin panels, auth, analytics, AI, payments, collaboration, and syncing unless they are central to the first value
- Keep the MVP demonstrable in one sitting

Use this framing:

- `must-have`: required for the first usable version
- `nice-to-have`: useful but safely postponed
- `later`: good future expansions

## 4. Choose The Delivery Shape

Recommend a concrete implementation shape, not a vague tech list.

Cover:

- platform: static page, SPA, full-stack app, local script, skill folder, plugin scaffold
- stack: HTML/CSS/JS, React/Vite, Next.js, Python, Node.js, etc.
- data model: local state, JSON file, localStorage, SQLite, remote DB, or none
- deployment shape: local only, static hosting, server deployment, Codex skill install

Bias toward the lowest-complexity stack that supports the MVP cleanly.

Examples:

- Single interactive webpage -> static HTML/CSS/JS unless complexity clearly needs a framework
- Small internal dashboard -> React + local mock data first
- Reusable Codex planning helper -> skill with `SKILL.md` and optional references
- Scheduled reporting assistant -> automation before full web app

## 5. Break Work Into Phases

Always produce a phased build plan with concrete outputs.

Use this default structure:

### Phase 0

Clarify the concept, constraints, examples, and success criteria.

### Phase 1

Build the MVP shell and the core interaction loop.

### Phase 2

Polish UX, persistence, error states, and useful quality improvements.

### Phase 3

Ship, validate, and add optional stretch features.

For each phase, include:

- objective
- deliverables
- implementation notes
- done-when check

## 6. Flag Risks And Decisions

Separate risk from uncertainty.

Use short bullets for:

- technical risks: stack mismatch, data complexity, auth, performance, API dependency
- product risks: too broad MVP, unclear audience, novelty without utility
- decision points: where one choice affects architecture or long-term cost

When possible, pair each risk with a mitigation.

## 7. End With The Next Move

Always end with the most helpful next action for the current moment.

Choose one:

- write the project scaffold
- generate page structure and component list
- draft the skill files
- propose the database schema
- create the implementation plan
- start building immediately

If the user seems ready to build, do not stop at planning. Transition into execution.

## Output Format

Use this structure unless the user asks for something shorter:

### Project Summary

- one short paragraph

### Users And Goal

- target user
- user problem
- expected outcome

### MVP

- must-have
- nice-to-have
- later

### Recommended Stack

- platform
- tech choices
- persistence or data model
- deployment shape

### Build Plan

- phase 0
- phase 1
- phase 2
- phase 3

### Risks And Decisions

- key risk bullets

### Next Step

- one clear recommended action

## Project-Type Guidance

Read [references/project-patterns.md](references/project-patterns.md) when you need project-specific planning patterns, stack bias, or a sharper MVP cut for one of these types:

- webpage or microsite
- web app or dashboard
- Codex skill
- automation
- script or CLI tool

## Handling Ambiguity

When details are missing:

- infer the simplest sensible audience
- infer the smallest useful scope
- prefer boring technology over ambitious architecture
- surface assumptions in one short block

Ask follow-up questions only when the answer changes:

- hosting or deployment model
- whether user accounts are required
- whether external APIs are mandatory
- whether the work is a local utility or a public product
- whether persistence must survive across devices

## Quality Bar

The plan should be specific enough that another strong builder could start implementation immediately.

Avoid:

- generic advice with no delivery shape
- giant feature dumps
- “it depends” without a recommendation
- recommending frameworks because they are popular rather than necessary
- overcomplicating a one-weekend project

Prefer:

- concrete scope cuts
- named phases
- opinionated but reversible recommendations
- short assumptions
- one decisive next move
