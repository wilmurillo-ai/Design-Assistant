# skylv-agent-evaluator

> AI Agent behavior evaluation engine. Score actions against 5 criteria, provide improvement suggestions.

## Usage

```bash
node agent_evaluator.js evaluate <file>   # Full evaluation
node agent_evaluator.js score <file>      # Quick score only
node agent_evaluator.js criteria          # List criteria
```

## Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Accuracy | 25% | Correctness of information and actions |
| Efficiency | 20% | Time and resource usage |
| Clarity | 15% | Clear communication and reasoning |
| Safety | 20% | No harmful or dangerous actions |
| Helpfulness | 20% | Value provided to user |

## Output

- Score: 0-100
- Grade: A+ to D
- Improvement suggestions for low criteria

## Market Position

Blue ocean category. Top competitor: `eval` (0.734) — weak.

---

*Self-evaluating AI agent.*
