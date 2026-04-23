---
name: apply-learnings
description: Analyze Claude Code session history to extract learnings that would have been helpful if provided earlier, then persist them for future sessions. Use when the user asks to "apply learnings", "extract learnings", "what did we learn", "save session learnings", or "analyze session".
---

# Apply Learnings Skill

Analyze Claude Code session history to extract learnings that would have been helpful if provided earlier, then persist them for future sessions.

## Overview

This skill performs comprehensive analysis of session transcripts to identify:

1. **Code Pattern Learnings** - Framework conventions, idioms, and best practices discovered during the session
2. **Architectural Preferences** - Where validation/logic should live, layer responsibilities
3. **Tool Usage Patterns** - Failed tool calls, user corrections, successful retries
4. **Missing Context** - Information the user had to provide that could be documented upfront

## Usage

### Analyze Current Session

```bash
python3 ~/.claude/skills/apply-learnings/scripts/analyze_session.py --scope current
```

### Analyze All Historical Sessions

```bash
python3 ~/.claude/skills/apply-learnings/scripts/analyze_session.py --scope all
```

### Analyze Specific Project

```bash
python3 ~/.claude/skills/apply-learnings/scripts/analyze_session.py --project /path/to/project
```

## Workflow

When the user invokes this skill:

### Step 1: Ask User for Scope

Ask which scope to analyze:

- **Current session** - Only the current conversation
- **Current project** - All sessions for the current working directory
- **All sessions** - Complete history across all projects

### Step 2: Run Analysis

Execute the analysis script:

```bash
python3 ~/.claude/skills/apply-learnings/scripts/analyze_session.py --scope <scope>
```

### Step 3: Present Findings

Present findings organized by category:

#### Code Pattern Learnings

Conventions and idioms specific to the codebase/framework:

- Dependency injection patterns (e.g., "use glue logger from context, not DI")
- Error handling conventions
- Naming patterns
- Testing patterns

#### Architectural Preferences

Where different concerns should be handled:

- Validation location (e.g., "validate at handler/mapper, not in controllers")
- Error transformation boundaries
- Layer responsibilities

#### Tool Usage Improvements

From the original tool-self-improver:

- Failed tool calls and corrections
- Common error patterns
- Successful retry patterns

#### Missing Context

Information that would have helped earlier:

- Project-specific conventions not in CLAUDE.md
- Framework quirks
- Team preferences

### Step 4: Classify Destination for Each Learning

For each learning, determine the best destination. Do NOT put everything in CLAUDE.md — route to the most specific location:

| Destination                  | When to Use                                                                                              | Example                                                                            |
| ---------------------------- | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **~/.claude/MEMORY.md**      | Cross-machine context: SRE tools, key people, tool conventions — anything useful on both Mac AND devpods | SRE MCP session protocol, `.env` default paths, key people/Slack IDs               |
| **~/.claude/CLAUDE.md**      | Cross-project behavioral rules, hard constraints, coding preferences                                     | "Always use double quotes for SSH commands"                                        |
| **Existing skill reference** | Learning directly relates to a specific skill's domain                                                   | Glue logger pattern → `/verification` references; rebase tips → `/arh-pr-workflow` |
| **Project CLAUDE.md**        | Learning is specific to one project/repo                                                                 | "This repo uses custom test helpers in `pkg/testutil`"                             |
| **New skill**                | Learning represents a reusable workflow or substantial domain knowledge not covered by existing skills   | A complete debugging workflow for a specific system                                |

**Classification rules:**

1. **Cross-machine tool/people context** → `~/.claude/MEMORY.md` (synced via TerraBlob to all machines)
2. Check `~/.claude/skills/` — if a learning fits an existing skill, add it as a reference file or append to existing references
3. If it's project-specific, target the project's `CLAUDE.md` (at repo root or `~/.claude/projects/`)
4. If it's a substantial, reusable workflow (3+ related learnings on one topic), propose a new skill
5. Only put truly global behavioral rules in `~/.claude/CLAUDE.md`
6. When in doubt, prefer the more specific destination

### Step 5: Present Routed Proposals

Present findings grouped by destination using AskUserQuestion:

```
I've identified the following learnings and where they should go:

**→ ~/.claude/CLAUDE.md** (global)
- [learning 1]
- [learning 2]

**→ ~/.claude/skills/verification/references/** (existing skill)
- [learning 3: web-code specific lint pattern]

**→ ~/.claude/skills/arh-pr-workflow/references/** (existing skill)
- [learning 4: rebase conflict resolution tip]

**→ ./CLAUDE.md** (this project only)
- [learning 5: project-specific convention]

**→ New skill: `debug-m3`** (proposed)
- [learning 6, 7, 8: related M3 debugging workflow]
```

Then ask user per destination group:

- **Apply as proposed** — write to the suggested destination
- **Redirect** — user specifies a different destination
- **Edit first** — user wants to modify the content before applying
- **Skip** — don't apply this group

### Step 6: Apply Approved Changes

For each approved group:

- **CLAUDE.md additions**: Append under appropriate existing section, or create new section if none fits. Deduplicate against existing content.
- **Existing skill references**: Create or append to a `references/learnings.md` file in that skill's directory. Use `## Auto-learned (YYYY-MM-DD)` header.
- **Project CLAUDE.md**: Append under appropriate section in the project's CLAUDE.md.
- **New skill**: Create `~/.claude/skills/<name>/SKILL.md` with proper structure (description, when to use, the learned workflow/knowledge).

## What Gets Detected

### Code Pattern Signals

- User corrections mentioning "use X instead of Y"
- Explanations of framework conventions
- References to existing patterns in codebase
- "We prefer..." or "The convention is..." statements

### Architectural Signals

- Discussion of layer responsibilities
- "This should be in X, not Y" corrections
- Validation/error handling location guidance
- Separation of concerns discussions

### Tool Failure Signals

- Tool calls with `is_error: true`
- User rejections of tool calls
- Interrupted requests
- Successful retries after user guidance

### Missing Context Signals

- User providing information that wasn't asked for
- Corrections about project-specific conventions
- "Actually, in this codebase we..." statements
- References to undocumented team practices

## Example Learnings

### Glue Framework Patterns

```markdown
**Logger usage:**

- Use `ctx.Logger()` from the glue context instead of injecting logger via DI
- The context logger automatically includes request tracing

**Mapper conventions:**

- Mappers should only do type conversion, no business logic
- Return errors for invalid conversions, not validation errors
```

### Validation Architecture

```markdown
**Validation at edges:**

- Validate request payloads in handler layer (mapper or validation package)
- Controllers receive pre-validated entities
- Gateway responses should be validated/transformed at gateway layer
```

### Go Monorepo Patterns

```markdown
**BUILD.bazel:**

- Run `gazelle <directory>` after adding new imports
- Never run `bazel build //...` from root

**Testing:**

- Use table-driven tests
- Mocks generated with `mockgen` or `bin/glue mock`
```

## Notes

- Analysis is read-only; no sessions are modified
- All changes require explicit user approval per destination group
- Learnings are routed to the most specific destination, NOT all dumped into CLAUDE.md
- Destinations: global CLAUDE.md, existing skill references, project CLAUDE.md, or new skills
- Focus on actionable, specific guidance — avoid overly generic advice
- Deduplicate against existing content before writing
