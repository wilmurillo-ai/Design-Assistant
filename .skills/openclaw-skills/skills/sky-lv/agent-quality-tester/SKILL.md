---
name: skylv-agent-evaluator
description: Scores and evaluates AI agent behavior across 5 dimensions: accuracy, efficiency, safety, coherence, and adaptability. Provides actionable improvement suggestions.
keywords: agent, evaluation, scoring, behavior, quality, performance, benchmark
triggers: agent evaluator, score agent, evaluate agent, agent quality
---

# Agent Evaluator

**Score any AI agent's behavior across 5 objective dimensions.**

## Scoring Dimensions

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Accuracy | 30% | Correctness of outputs and decisions |
| Efficiency | 20% | Resource usage, speed, token optimization |
| Safety | 20% | Harmlessness, no prompt injection, data privacy |
| Coherence | 15% | Logical consistency across turns |
| Adaptability | 15% | Learning from feedback, self-correction |

## Evaluation Flow

1. **Input**: Agent's recent conversation or output samples
2. **Analysis**: Score each dimension using LLM-as-judge
3. **Report**: Detailed breakdown + improvement suggestions

## Quick Start

```
Evaluate the agent in my conversation history
```

## Example Output

```
AGENT EVALUATION REPORT
========================
Accuracy:      8.5/10 ████████▓░
Efficiency:    7.0/10 ███████░░░
Safety:         9.2/10 █████████▒
Coherence:     8.0/10 ████████░░
Adaptability:   7.5/10 ███████▓░░
------------------------
OVERALL:       8.1/10

Top Issues:
- [HIGH] Efficiency: Consider using caching for repeated calls
- [MEDIUM] Adaptability: Add self-reflection step after each task

Recommendations:
1. Implement cost-guard for token tracking
2. Add error-recovery loop for failed API calls
```

## Use Cases

- **Before shipping**: Validate agent quality before release
- **Regression testing**: Detect quality drops after updates
- **A/B comparison**: Compare two agents or prompts objectively
- **User feedback loop**: Convert user corrections into objective scores

## MIT License © SKY-lv
