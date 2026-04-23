---
name: kivo
description: "Self-evolving knowledge engine for AI agents that extracts six typed knowledge entries (facts, methodologies, decisions, experiences, intents, meta-cognition) from conversations and documents, manages version history and state transitions, detects contradictions with multi-strategy resolution, discovers knowledge gaps and generates research tasks with budgets, injects ranked context into queries within token budgets, parses Markdown, PDF, and web content with source tracing, and maps entry relationships including supplements, supersedes, conflicts, and dependencies."
version: 1.0.0
author: yuchangxu1989@gmail.com
---

# KIVO

KIVO stands for **Knowledge Iteration and Versioned Operations**.

KIVO is a self-evolving knowledge engine for AI agents. It ingests conversations and documents, turns them into typed knowledge entries, manages lifecycle and versioning, detects gaps, schedules follow-up research, and injects the right context back into future queries.

## What it does

- Extracts structured knowledge from conversations and documents: facts, methodologies, decisions, experiences, intents, and meta-cognition
- Parses Markdown, PDF, and web content with source tracing and segment-level classification
- Stores typed knowledge entries with version history and state transitions
- Finds relationships between entries, including supplements, supersedes, conflicts, and dependencies
- Detects contradictions and resolves them by time priority, source authority, or human arbitration
- Detects knowledge gaps and generates research tasks with goals, scope, strategy, and budgets
- Injects ranked context into future queries within a caller-defined token budget
- Suggests clarification when intent disambiguation confidence is low

## Architecture

Six knowledge types: `fact`, `methodology`, `decision`, `experience`, `intent`, `meta`

Core pipeline: `Intake → Extraction → Classification → Conflict Detection → Resolution → Persistence → Gap Analysis`

## Quick start

```ts
import { Kivo } from '@self-evolving-harness/kivo';

const kivo = new Kivo({
  storage: { provider: 'file', basePath: './knowledge-store' },
  embedding: { provider: 'openai', model: 'text-embedding-3-small' },
});

await kivo.ingest({
  source: { type: 'conversation', id: 'session-001' },
  content: 'User prefers arc42 for architecture docs...',
});

const results = await kivo.query({
  text: 'What architecture template should I use?',
  tokenBudget: 2000,
});
```

## When to use it

Use KIVO when an agent system needs durable memory with versioning, contradiction handling, research backlog generation, and query-time context injection instead of flat note storage.

## License

MIT License. Commercial use and derivative works must include attribution to the original author (yuchangxu1989@gmail.com).
