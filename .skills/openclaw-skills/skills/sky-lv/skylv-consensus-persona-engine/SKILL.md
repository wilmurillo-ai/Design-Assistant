---
description: Builds consensus-driven AI personas from multiple perspectives
keywords: openclaw, skill, automation, ai-agent
name: skylv-consensus-persona-engine
triggers: consensus persona engine
---

# skylv-consensus-persona-engine

> Multi-Agent personality consensus engine. Align multiple agents through voting and weighted decision-making.

## Problem

When multiple AI agents collaborate, how do you ensure consistent behavior? Each agent might have different "personalities" — tone, risk tolerance, autonomy level.

## Solution

**Consensus Persona Engine** — agents vote on personality dimensions, and a consensus personality is calculated.

## Usage

```bash
# Cast votes
node consensus_persona_engine.js vote tone friendly
node consensus_persona_engine.js vote autonomy proactive

# Calculate consensus
node consensus_persona_engine.js consensus

# List dimensions
node consensus_persona_engine.js dimensions
```

## Personality Dimensions (6)

| Dimension | Description | Options |
|-----------|-------------|---------|
| tone | Communication style | formal, casual, friendly, professional, neutral |
| verbosity | Response detail level | concise, moderate, detailed, exhaustive |
| risk_tolerance | Risk acceptance | conservative, balanced, aggressive |
| autonomy | Decision independence | passive, suggestive, proactive, autonomous |
| safety_level | Security strictness | minimal, standard, strict, paranoid |
| creativity | Innovation level | factual, balanced, creative, experimental |

## Output

- **Consensus personality** with confidence scores
- **Generated rules** based on consensus
- **JSON config** for agent initialization

## Market Data

Blue ocean: `consensus-persona-engine` scores **0.713** — minimal competition.

---

*Enabling multi-agent harmony.*

## Install

```bash
openclaw skills install skylv-consensus-persona-engine
```
