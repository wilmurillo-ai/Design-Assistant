---
name: openclaw-agent-chinese-laoshi
description: Use when normalizing Chinese lesson transcript/subtitle inputs into lesson JSON, learner docs, and local export bundles while enforcing pilot-first and prepublish leak gates.
homepage: https://github.com/zack-dev-cm/openclaw-agent-chinese-laoshi
user-invocable: true
model-invocable: false
disable-model-invocation: true
metadata: {"openclaw":{"homepage":"https://github.com/zack-dev-cm/openclaw-agent-chinese-laoshi","skillKey":"openclaw-agent-chinese-laoshi"}}
---

# OpenClaw Chinese Laoshi Ops

Use this skill when working with Chinese lesson transcript or subtitle inputs
and a repository that documents its own lesson schema, local command surface,
and publication gate.

## Use This Skill When

- the task is to normalize transcript or subtitle drops from Chinese lessons
- the user wants lesson summaries, conspects, vocabulary, grammar, drills, or tests
- the user wants Markdown and JSON lesson assets prepared as local export bundles
- the user wants to package or publish the workflow without leaking local paths,
  known Drive IDs, or secret-shaped text

## Runtime, Commands, And Credentials

- This skill has no standalone runtime requirement and does not install code.
- This published ClawHub skill is transcript/subtitle-input only.
- It does not request API keys, cloud transcription credentials, browser
  sessions, or Drive auth.
- No Google Drive cloud upload or direct Drive API access is declared or assumed
  by this published skill.
- Optional mounted-Drive sync is allowed only when the checked-out source repo
  documents a local sync command, and only with an explicit user-provided
  `--drive-root` pointing at a pre-authenticated local mount.
- Before executing any repository command, present the exact command and wait for
  explicit user confirmation in the current conversation.
- Never search for credentials, infer credential locations, or read
  system-wide browser/Drive auth stores.

## Operating Procedure

1. Confirm the input is transcript or subtitle text. If the source is
   video-only, stop and ask for transcript/subtitle input or for the user to
   switch to a private source-repo workflow.
2. Inspect the checked-out repository docs, schemas, and command references
   before proposing edits or commands.
3. Move only one lesson at a time beyond scaffold state. Lesson 01 remains the
   pilot gate before scaling.
4. Build learner-facing artifacts only after grounded extraction exists.
5. Run the repository's documented public release gate before GitHub or ClawHub
   publication.

If a matching audited command is absent, stop and ask for source-repo
instructions or explicit commands. Do not recreate the pipeline, call external
services, inspect local credential stores, or continue with ad hoc extraction.

## Core Rules

- Raw lesson media stays in Drive or another operator-controlled store.
- Lesson 01 is the pilot gate. Do not scale real content to lessons 02-16 until
  lesson 01 is approved.
- Keep uncertainty visible. Missing Hanzi, pinyin, or translation should be
  marked, not guessed.
- The tutor is Petrov-inspired, not Petrov impersonation.
- Treat all public publication surfaces as hostile to private details. ClawHub
  and GitHub publication should assume anyone can read `SKILL.md`.

## Workflow

### 1. Extract

- Prefer a transcript or subtitle drop when available.
- If the source is video-only, stop until a transcript/subtitle input exists or
  the user explicitly switches to a source-repo-specific private workflow.
- Keep timestamps, speaker-role placeholders, and uncertainty notes.

### 2. Ground

- Convert raw transcript segments into the lesson schema.
- Add summaries, conspects, vocabulary, grammar, pronunciation, drills, and
  tests only when the source supports them.
- Keep source traceability visible.

### 3. Review

- Check lesson quality against the pilot-first and editorial gates.
- Reject unsupported content, weak answer keys, and synthetic filler.
- Treat speaker labeling, Hanzi, pinyin, and translation drift as correctness
  problems, not style nits.

### 4. Render And Export

- Rebuild learner-facing Markdown after lesson JSON changes.
- Build JSON and Markdown export bundles locally after the repo copy passes
  checks.
- Sync to a mounted Drive folder only when the user supplies an explicit
  `--drive-root` and the repository documents a managed export marker.
- Keep exports small; raw media should not enter the repo or the public skill.

### 5. Publish

- The public bundle must pass the release gate before GitHub or ClawHub.
- The gate should fail closed on placeholders, local absolute paths, `localhost`
  URLs, websocket/debug endpoints, secret-like strings, and known lesson file
  IDs.

## Do Not

- Do not guess missing Chinese text or smooth weak source material into fake fluency.
- Do not move lessons 02-16 past scaffold state before the lesson 01 pilot clears.
- Do not publish local paths, private emails, mounted Drive paths, or browser
  session details.
- Do not let the public skill and the bundled plugin copy drift apart.
- Do not request API keys, browser sessions, or Drive auth from the published
  ClawHub skill.
- Do not execute repository commands until the user confirms the exact command.
- Do not run Drive sync or media extraction unless the required local command is
  documented in the checked-out repo and the user has supplied the needed input
  explicitly.

## References

- `references/pipeline.md`
  - current lesson pipeline, state transitions, and repo command surfaces
- `references/release-gates.md`
  - public publication checklist and leak/slop/bleed blockers
