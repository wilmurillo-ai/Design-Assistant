---
name: skill-release-guard
description: Validate a local skill folder before publishing or sharing it. Use when Codex is about to release a skill, publish to ClawHub, audit SKILL.md quality, check naming/frontmatter/resource hygiene, or generate a release checklist for a skill package.
---

# Skill Release Guard

Use this skill right before packaging or publishing a skill.

## Workflow

1. Inspect the target skill directory.
2. Confirm `SKILL.md` exists and frontmatter has only `name` and `description`.
3. Check naming convention, folder layout, and presence of obvious clutter files.
4. Run `scripts/check_skill_release.js` to generate a compact release checklist.
5. Fix guard failures before publishing.

## Script

```bash
node skills/skill-release-guard/scripts/check_skill_release.js \
  --skill skills/my-skill \
  --out out/my-skill-release-check.json
```

## Guardrails

- Fail if the folder name and frontmatter name diverge.
- Flag clutter docs like README/CHANGELOG/INSTALL guides.
- Flag missing description or overly vague description.
- Treat script syntax failures as release blockers.
