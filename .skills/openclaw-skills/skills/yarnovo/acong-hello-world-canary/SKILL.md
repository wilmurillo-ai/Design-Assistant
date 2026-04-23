---
name: acong-hello-world
description: End-to-end smoke test for skill-publish-cli. Published from Hangzhou Acong Intelligent Technology Co., Ltd to verify the full ClawHub + skills.sh release pipeline. Use when demonstrating the minimum viable skill structure (single SKILL.md, no supporting files) or verifying agent skill loader compatibility.
---

# Acong Hello World

Minimal SKILL.md used as a smoke test for [skill-publish-cli](https://github.com/acong-tech/skill-publish-cli)'s 8-step publish flow (validate → creds → repo → copy → commit/push → clawhub publish → skills.sh telemetry → record).

## When to use

- You are curious what a valid minimal SKILL.md looks like
- You are building a skill loader and want the smallest possible test fixture
- You just installed `skill-publish-cli` and want to confirm it works end-to-end

## What this skill does when loaded

Nothing functional. This skill is intentionally empty — it exists only to verify the publish pipeline and the discovery mechanism of ClawHub / skills.sh / compatible agents.

## Provenance

- Published by: [acong-tech](https://github.com/acong-tech) (杭州阿空智能科技有限公司)
- Pipeline: `skill-publish-cli publish fixtures/hello-skill`
- License: MIT-0 (no attribution required)
- Channels: ClawHub (`clawhub install acong-hello-world`) + skills.sh (`npx skills add acong-tech/skill-acong-hello-world`)

## Updates

This skill may be re-published when the underlying `skill-publish-cli` releases a new version, to validate that `publish` remains idempotent and backward-compatible.
