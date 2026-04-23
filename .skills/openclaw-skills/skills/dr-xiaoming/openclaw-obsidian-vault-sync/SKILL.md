---
name: obsidian-openclaw-sync
description: Connect an OpenClaw workspace to an Obsidian vault and maintain a structured knowledge sync workflow. Use when setting up Obsidian integration, linking a vault into the workspace, organizing notes into reusable folders, syncing user, profile, org, methodology, and journal content into markdown files, or teaching other OpenClaw agents how to persist working context into Obsidian. Covers symlink-based vault connection, note placement rules, daily journal sync, and mirroring OpenClaw self-knowledge into Obsidian.
---

# Obsidian and OpenClaw Sync

Use this skill to connect OpenClaw with an Obsidian vault and keep knowledge organized as markdown files that humans and agents can both reuse.

## Core pattern

Treat `obsidian/` in the workspace as the vault entrypoint.

Preferred setup on macOS:

```bash
ln -s "/absolute/path/to/your/Obsidian/Vault" ./obsidian
```

This keeps OpenClaw operating inside the workspace while writing directly into the real vault.

## What to store where

Use a stable folder taxonomy. Current proven structure:

- `00-人物/` — people profiles, role cards, relationship context, resume variants
- `10-组织/` — org structures, team maps, stakeholder context
- `20-方法论/` — reusable frameworks, SOPs, evaluation logic, decision rules
- `30-日志/` — daily journals and chronological work summaries
- `90-OpenClaw/` — mirrored agent operating context (`AGENTS.md`, `USER.md`, `MEMORY.md`, etc.)

Do not dump everything into one folder. Prefer one note = one durable topic.

## Writing rules

1. Distill first, then write.
2. Prefer structured markdown over raw chat transcripts.
3. Create overview pages when details begin to scatter.
4. Separate raw daily logs from long-term reusable knowledge.
5. When a note reflects evolving judgment, write the current best understanding instead of preserving every conversational twist.

## Recommended note types

### 1. Person notes

Use for:
- user profile
- leaders / collaborators / stakeholders
- role positioning
- performance goals
- relationship context

Typical examples:
- `00-人物/佘金明.md`
- `00-人物/章东丞.md`
- `00-人物/佘金明-工作画像.md`

### 2. Org notes

Use for:
- team structure
- reporting lines
- collaboration topology
- account/project organization

Typical example:
- `10-组织/BlueFocus-宁德时代项目组.md`

### 3. Methodology notes

Use for:
- frameworks that will be reused
- evaluation models
- operating principles
- AI workflow / SOP abstractions

Typical examples:
- `20-方法论/AI助理-评估与运营改进框架.md`
- `20-方法论/AI助理运营阶段性汇报-3月9日上线至今.md`

### 4. Daily journal notes

Use for:
- what was done today
- outputs created
- stage results
- next-step suggestions

Typical example:
- `30-日志/YYYY-MM-DD.md`

### 5. OpenClaw mirror notes

Mirror key workspace files into `90-OpenClaw/` when you want the Obsidian vault to contain the agent's operating context.

Typical files:
- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `MEMORY.md`
- `TOOLS.md`
- `HEARTBEAT.md`

## Workflow: convert chat work into Obsidian knowledge

### A. Identify the knowledge type

Ask:
- Is this about a person?
- Is this about an org/team?
- Is this a reusable method?
- Is this just today’s progress?
- Is this agent self-context that should be mirrored?

### B. Choose the destination note

- Append to an existing note if the topic already exists.
- Create a new note if the content would otherwise make an unrelated note bloated.
- Create an overview note when several related notes need a summary layer.

### C. Rewrite into durable markdown

Prefer sections like:
- 基本信息
- 当前理解
- 核心职责
- 协作关系
- 方法论
- 今日完成
- 下一步建议

### D. Keep logs and knowledge separate

- Put “today what happened” in `30-日志/`
- Put reusable conclusions in `00-人物/`, `10-组织/`, `20-方法论/`

## Workflow: daily journal sync

When asked to write a daily journal:

1. Summarize the day’s actual completed work.
2. List key files/outputs created.
3. Capture stage-level outcomes, not just actions.
4. Add recommended next steps if useful.
5. Save to `30-日志/YYYY-MM-DD.md`.

## Workflow: mirror OpenClaw context into Obsidian

Use when you want the vault to preserve the agent’s own operating documents.

Mirror from workspace root into `obsidian/90-OpenClaw/`:
- `AGENTS.md`
- `BOOTSTRAP.md` if still relevant
- `IDENTITY.md`
- `SOUL.md`
- `USER.md`
- `MEMORY.md`
- `TOOLS.md`
- `HEARTBEAT.md`

This is useful for:
- letting humans inspect agent context in Obsidian
- keeping system memory visible and editable
- preserving operational continuity in the vault

## Practical rules for other agents

- Respect privacy: do not export sensitive material to shared vaults unless explicitly intended.
- Prefer incremental updates over large rewrites.
- If content comes from screenshots or docs, convert it into structured text before storing.
- If multiple notes are created in one task, also create or update one summary/overview note when helpful.
- Do not assume Obsidian plugins or APIs are available; plain markdown file operations are sufficient.

## Verification checklist

After setup or sync, verify:

```bash
ls -la ./obsidian
find -L ./obsidian -maxdepth 3 -type f | sort | sed -n '1,50p'
```

Confirm:
- `obsidian/` exists and points to the real vault or is a real folder
- target markdown files were created in the intended category
- note names are human-readable
- content is structured enough for future reuse

## Bundled references

- Folder structure and note placement: `references/structure.md`
- Reusable operating workflow: `references/workflow.md`
- Example vault patterns from current usage: `references/examples.md`
