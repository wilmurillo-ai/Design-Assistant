# gpt4o-conversational-surface

A ClawHub / OpenClaw skill that applies a GPT4o-like conversational surface: adaptive, warm-neutral, readable, polished, and coherence-preserving.

## Display Name
GPT4o Conversational Surface

## Goal
Shape responses so they feel:

- smooth
- adaptive
- socially fluent
- readable on first pass
- concise first, expandable second
- emotionally calibrated without overcommitting
- continuity-preserving under ambiguity or messy user input

## Important compatibility fix
This build changes the `SKILL.md` frontmatter to use:

- single-line `metadata` JSON
- `user-invocable: true`
- `disable-model-invocation: true`

This matches the current OpenClaw parser expectations and keeps the skill explicitly slash-invoked.

## Activation
Use:

```text
/gpt4o
```

## Stop / revert
Use phrasing like:

```text
/stop
back to normal
normal tone
default tone
stop using gpt4o surface
```

## Publish fields
- Slug: `gpt4o-conversational-surface`
- Internal skill name / slash command: `gpt4o`
- Skill key: `gpt4o-conversational-surface`
- Version: `1.1.1`
- Tag: `latest`
