---
name: skylv-commit-linter
slug: skylv-commit-linter
version: 1.0.0
description: "Validates git commit messages against conventional commits format. Triggers: commit lint, conventional commits, commit format."
author: SKY-lv
license: MIT
tags: [automation, tools]
keywords: [automation, tools]
triggers: commit-linter
---

# Commit Linter

## Overview
Validates commit messages and enforces conventional commits format.

## Conventional Commit Format

type(scope): description

Types: feat, fix, docs, style, refactor, perf, test, chore

## Valid Examples
feat(auth): add password reset
fix(api): handle null response
docs(readme): update install

## Rules
- Subject line max 72 characters
- Use imperative mood ("add" not "added")
- No period at end of subject
- Separate subject from body with blank line

## Validate
git log --oneline -20
