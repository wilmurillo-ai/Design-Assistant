# Token Budget Guard 💰

> Stop burning context. Manage your agent's token budget intelligently.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/type-agent--skill-blue)](SKILL.md)

**Why this exists:** The AAI Gateway project proved 99% token savings are possible through progressive disclosure. But that's an external tool. This skill makes token awareness native to every agent workflow — no setup required.

## The Problem

AI agents waste 40-60% of their context window on:
- Full tool schemas when stubs would suffice
- Raw conversation history when summaries work
- Entire files when targeted extraction is enough
- Uncompressed tool outputs that accumulate silently

## Key Insight

```
Context window is a budget, not unlimited storage.
Treat every token like a dollar — spend wisely.
```

## Quick Start

```
# Install as an agent skill
# Claude Code: Copy SKILL.md to .claude/skills/token-budget-guard/
# Cursor: Copy to .cursor/rules/token-budget-guard.mdc
# OpenClaw: Copy to ~/.openclaw/workspace/skills/token-budget-guard/

# Then tell your agent:
"Be token-efficient"
"Reduce my context usage"
"Am I running out of context?"
```

## Core Strategies

### 1. Progressive Disclosure (99% schema savings)
- Level 0: Name only (1-5 tokens)
- Level 1: Summary (10-30 tokens) ← default
- Level 2: Full schema (50-200 tokens) ← only when using tool
- Level 3: Examples (200-500 tokens) ← only when learning tool

### 2. Conversation Compression
- After 5 turns: summarize previous context
- After 10 turns: aggressive summarization
- At 80% capacity: drop everything except current task + summary

### 3. Selective File Operations
- `jq '.dependencies'` > `cat package.json`
- `grep -n "function" file.js` > `cat file.js`
- `head -20 / tail -20` > full file for context

### 4. Budget Monitoring
Track running totals and alert at 60%/80%/90% thresholds.

## Real Impact

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Multi-MCP workflows | 7,500 tokens | 75 tokens | 99% |
| Conversation history | 5,000 tokens | 1,000 tokens | 80% |
| File operations | 2,000 tokens | 600 tokens | 70% |

## Works With

Any AI agent framework. No dependencies.

## License

MIT
