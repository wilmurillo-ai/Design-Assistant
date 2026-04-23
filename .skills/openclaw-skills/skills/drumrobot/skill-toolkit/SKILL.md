---
name: skill-toolkit
description: Claude Code skill management. writer - create new skills [writer.md], lint - validate and fix frontmatter [lint.md], merge - combine related skills [merge.md], dedup - find duplicate skills [dedup.md], convert - convert agents to skills [convert.md], architecture - multi-topic skill structure [architecture.md], upgrade - enhance existing skills, add topics [upgrade.md], route - recommend topic placement [route.md]. Use when "skill writer", "skill lint", "skill merge", "skill dedup", "create skill", "frontmatter fix", "combine skills", "multi-topic skill", "agent to skill", "convert agent", "skill improve", "skill upgrade", "add topic", "topic routing", "topic placement", "where to put", "topic route".
---

# Skill Manager

Comprehensive toolkit for managing Claude Code skills - create, validate, merge, convert, and deduplicate.

## Topics

| Topic | Description | Guide |
|-------|-------------|-------|
| architecture | Multi-topic skill directory structure and templates | [architecture.md](./architecture.md) |
| convert | Convert agent (.md) to skill structure | [convert.md](./convert.md) |
| dedup | Find and clean up duplicate skills between user and plugins | [dedup.md](./dedup.md) |
| lint | Validate and fix SKILL.md frontmatter issues | [lint.md](./lint.md) |
| merge | Combine multiple related skills into one | [merge.md](./merge.md) |
| route | Topic description → scan existing skills → recommend placement | [route.md](./route.md) |
| upgrade | Enhance existing skills: add topics, improve frontmatter, restructure scripts | [upgrade.md](./upgrade.md) |
| writer | Create new Agent Skills with proper structure and frontmatter | [writer.md](./writer.md) |

## Quick Reference

### Writer (Create Skills)

```bash
/skill-manager writer              # Interactive skill creation
```

Key steps:
1. Determine scope and location
2. Create directory structure
3. Write SKILL.md with proper frontmatter
4. Add supporting files if needed
5. Validate and test

[Detailed guide](./writer.md)

### Lint (Validate/Fix)

```bash
/skill-manager lint                # Scan all skills for issues
/skill-manager lint --fix          # Auto-fix common issues
```

Checks for:
- Missing `name:` or `description:` fields
- Invalid fields (`triggers:` → description, `tools:` → `allowed-tools:`)
- Frontmatter position errors

[Detailed guide](./lint.md)

### Merge (Combine Skills)

```bash
/skill-manager merge skill-a skill-b    # Merge two skills
```

Creates unified skill with topic files:
```
new-skill/
├── SKILL.md
├── topic-a.md
└── topic-b.md
```

[Detailed guide](./merge.md)

### Dedup (Find Duplicates)

```bash
/skill-manager dedup               # Find user skills that duplicate plugins
```

Compares:
- `~/.claude/skills/` (user skills)
- `~/.claude/plugins/*/skills/` (plugin skills)

[Detailed guide](./dedup.md)

### Convert (Agent → Skill)

```bash
/skill-manager convert <agent-name>   # Convert agent to skill
```

Converts:
- Agent frontmatter → Skill frontmatter
- External scripts → `scripts/` folder
- Removes `-resolver`, `-agent` suffixes

[Detailed guide](./convert.md)

### Upgrade (Enhance Skills)

```bash
/skill-manager upgrade <skill-name>    # Enhance existing skill
/skill-manager upgrade                 # Enhance current skill
```

Improvement types:
- Add new topics
- Add trigger keywords to frontmatter description
- Restructure into scripts/ folder

[Detailed guide](./upgrade.md)

### Route (Topic Placement)

```bash
/skill-manager route "Helm chart lint"    # Recommend where to place a topic
```

Verdict types:
- Add topic to existing skill → chains to `upgrade`
- Add section to existing topic → direct Edit
- Create new skill → chains to `writer`

[Detailed guide](./route.md)

### Architecture (Multi-Topic Structure)

For skills with multiple related topics:

```
skill-name/
├── SKILL.md          # Entry point with frontmatter
├── topic1.md         # Topic content (no frontmatter)
└── topic2.md
```

[Detailed guide](./architecture.md)

## Skill Locations

| Location | Purpose |
|----------|---------|
| `~/.claude/skills/` | Personal skills |
| `.claude/skills/` | Project skills (committed to git) |
| `~/.claude/plugins/*/skills/` | Plugin skills |

## Frontmatter Reference

```yaml
---
name: skill-name           # Required: lowercase, hyphens, max 64 chars
description: ...           # Required: what + when + triggers, max 1024 chars
allowed-tools: [...]       # Optional: restrict tool access
model: claude-sonnet-4-... # Optional: specific model
context: fork              # Optional: context handling
depends-on: [skill-a]     # Optional: dependent skills
---
```

## Safe Delete (Required Rule)

When removing or replacing skills under `.claude`, **always** move to a root `.bak` folder:

```bash
mkdir -p ~/.claude/.bak
mv ~/.claude/skills/{old-skill} ~/.claude/.bak/
```

**Never** add `.bak` suffix in the same directory:
```bash
# Bad — Claude Code loads .bak folders as skills
mv ~/.claude/skills/old-skill ~/.claude/skills/old-skill.bak

# Good
mv ~/.claude/skills/old-skill ~/.claude/.bak/
```

Add timestamp on name conflicts:
```bash
mv ~/.claude/skills/{old-skill} ~/.claude/.bak/{old-skill}_$(date +%Y%m%d_%H%M%S)
```

## Notes

- Always backup before merging: `~/.claude/.bak/` (NOT `skills/.bak/`)
- Restart Claude Code after skill changes
- Use `claude --debug` for troubleshooting
