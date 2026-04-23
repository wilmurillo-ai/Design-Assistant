# BMad Agent / Workflow Map

Use this file as a **reference map**, not as the primary operating manual.

## Core rule

When the user wants official BMad execution:
- prefer **official agent roles + trigger codes**
- use direct workflows only as a controlled exception or when explicitly requested

## Installed role families

### BMM
- Analyst
- PM
- Architect
- Scrum Master
- Developer
- QA
- UX Designer
- Quick Flow Solo Dev
- Tech Writer

### TEA
- Test Architect

### BMB
- Agent Builder
- Module Builder
- Workflow Builder

### Core
- bmad-help
- party mode
- doc indexing / sharding / reviews

## Most important implementation roles

### Scrum Master
Typical triggers:
- `SP` — Sprint Planning
- `SS` — Sprint Status
- `CS` — Create Story
- `VS` — Validate Story
- `ER` — Retrospective
- `CC` — Correct Course

### Developer
Typical triggers:
- `DS` — Dev Story
- `CR` — Code Review

### PM
Typical triggers:
- `CP` — Create PRD
- `VP` — Validate PRD
- `EP` — Edit PRD
- `CE` — Create Epics and Stories

### Architect
Typical triggers:
- `CA` — Create Architecture
- `IR` — Check Implementation Readiness

### Analyst
Typical triggers:
- `BP` — Brainstorm
- `MR` — Market Research
- `DR` — Domain Research
- `TR` — Technical Research
- `CB` — Create Brief
- `DP` — Document Project
- `GPC` — Generate Project Context

## Standard implementation loop

1. SM → `CS`
2. DEV → `DS`
3. DEV → `CR`
4. Fixes → `DS`
5. Epic complete → SM → `ER`

## Routing rule

- Need official role behavior? → `run_bmad_persona.py`
- Need a direct workflow? → `claude_code_run.py`
- Need a one-shot non-interactive task? → `run_claude_task.sh`

## Where to look next

- full trigger matrix → `bmad-agent-trigger-cheatsheet.md`
- execution rules → `bmad-method-integration.md`
- prompt snippets → `bmad-prompt-templates.md`
