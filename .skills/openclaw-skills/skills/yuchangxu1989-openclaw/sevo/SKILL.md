---
name: sevo
description: "Full-lifecycle agent software delivery pipeline covering specification, independent spec review gates, architecture contract design with ADR and arc42, bounded implementation stages, cross-role contract review, code and behavior review, regression testing, deployment artifact generation, verification evidence collection, and delivery ledger closure. Features task-level routing, stage-aware context injection, ambiguity detection with clarification workflow, persistent pipeline engine, pluggable host adapters, and traceable audit trails across all stages."
version: 1.0.0
author: yuchangxu1989@gmail.com
---

# SEVO

SEVO stands for **Spec-Execute-Verify-Operate**.

SEVO is a TypeScript pipeline framework for agent-driven software delivery. It turns specs, review gates, execution records, regression checks, deployment artifacts, verification results, and delivery ledgers into one traceable workflow.

## What it does

- Routes incoming work to the right delivery level, from small fixes to full multi-stage projects
- Writes requirement packages with scope, acceptance criteria, concept architecture, and handoff quality
- Runs an independent spec review gate before architecture and implementation proceed
- Generates architecture contracts, work packages, and execution plans that can be assigned and audited
- Runs contract reviews across product, engineering, and quality before coding starts
- Executes implementation in bounded stages with artifact collection, rules, and traceable history
- Reviews code and behavior independently, then runs regression checks before release
- Produces deployment artifacts, verification evidence, and a final delivery ledger

## Pipeline coverage

SEVO covers the full delivery chain across specification, review gates, contract design, implementation, review, regression, deployment, verification, and ledger closure.

## Quick start

```ts
import { Sevo } from './dist/index.js';

const sevo = new Sevo({
  projectName: 'demo-project',
  stages: [
    'spec',
    'spec-review-gate',
    'contract',
    'contract-review-gate',
    'implement',
    'review',
    'regression',
    'deploy',
    'verify',
    'ledger',
  ],
  rules: [],
  adapter: 'standalone',
});

await sevo.init();
```

## Core modules

```text
src/
├── adapter/            Host adapters for OpenClaw and standalone use
├── clarification/      Ambiguity detection and clarification workflow
├── context-injection/  Stage-aware context injection
├── gate/               Rule engine and built-in quality rules
├── gates/              Spec review and contract review gates
├── ledger/             Delivery ledger and artifact collection
├── orchestrator/       Pipeline coordination and events
├── pipeline/           Persistent pipeline engine and stage transitions
├── router/             Task level routing and stage planning
└── stages/             Spec, contract, implement, review, regression, deploy, verify
```

## When to use it

Use SEVO when the job needs a disciplined software delivery pipeline with explicit gates, auditable artifacts, and a final evidence trail instead of ad hoc agent execution.

## License

MIT License. Commercial use and derivative works must include attribution to the original author (yuchangxu1989@gmail.com).
