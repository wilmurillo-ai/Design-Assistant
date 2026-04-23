# CC-BOS — Classical Chinese Jailbreak Agent Skill

An OpenClaw agent skill implementing the CC-BOS framework from **arXiv:2602.22983** (ICLR 2026 Poster).

> *Obscure but Effective: Classical Chinese Jailbreak Prompt Optimization via Bio-Inspired Search*

## What is CC-BOS?

CC-BOS exploits a blind spot in LLM safety training: classical Chinese (文言文) is massively underrepresented in RLHF/safety fine-tuning data. It uses **fruit fly optimization (FOA)** to automatically generate adversarial prompts across 8 dimensions:

| Dimension | Description |
|-----------|-------------|
| Role | The persona the model is instructed to adopt |
| Behavior | The specific harmful action requested |
| Mechanism | How the action should be performed |
| Metaphor | Classical Chinese analogies to obscure intent |
| Expression | Linguistic style and register |
| Knowledge | Domain knowledge invoked |
| Trigger Pattern | Activation phrases |
| Context | Framing and situational setup |

The optimizer runs three search phases — smell search, visual search, and Cauchy mutation — iteratively refining prompts until they bypass safety constraints.

## Modes

### 1. Attack Mode (Red-teaming / Research)
```bash
uv run --with openai python scripts/attack.py \
  --query "test query" \
  --target-model gpt-4o \
  --iterations 20 \
  --dry-run   # safe mode: no real API calls
```

### 2. Defensive Mode (Prompt Analysis)
```bash
uv run python scripts/defend.py \
  --prompt "your prompt text here"
```
Returns confidence score + which CC-BOS dimensions are detected. Useful for filtering adversarial inputs in production agent systems.

### 3. Research Mode (Results Analysis)
```bash
uv run --with pandas python scripts/research.py \
  --results results/sample_results.jsonl \
  --output report.md
```
Summarises optimization runs — evolved prompt dimensions, attack success rates, English translations.

## Installation

```bash
# Clone
git clone https://github.com/AlexChen31337/cc-bos
cd cc-bos

# Run tests (no API keys needed)
uv run --with pytest --with openai --with anthropic --with pandas --with numpy --with tqdm \
  pytest tests/ -v
# → 90/90 tests pass
```

## Configuration

Edit `config.json` to set your API endpoints, model names, and optimization parameters. All 4 API roles are independently configurable: optimizer, target, judge, translator.

## Architecture

```
scripts/
├── attack.py      # FOA optimization loop — generates CC-BOS prompts
├── defend.py      # Detection engine — regex + LLM-based analysis
├── research.py    # Results summarizer — markdown + dimension heatmap
├── dimensions.py  # 8-dimension definitions + encoding/decoding
├── translate.py   # Classical Chinese ↔ English translation
├── scoring.py     # Consistency + keyword scoring functions
└── setup.py       # Environment setup helper
```

## Tests

90 unit tests covering all components. No API keys required — all LLM calls are mocked.

```
tests/
├── test_dimensions.py   # Dimension encoding/decoding
├── test_defend.py       # Detection accuracy
├── test_translate.py    # Translation wrapper
└── test_scoring.py      # Scoring functions
```

## Defensive Use in Agent Systems

The `defend.py` detector is designed to be called as a pre-filter before any agent acts on external input. Example integration pattern:

```python
from scripts.defend import analyse_prompt

result = analyse_prompt(prompt)
if result.confidence > 0.7 and result.severity == "CRITICAL":
    quarantine(prompt)
```

This is directly applicable to any agent marketplace (like ClawChain's `pallet-service-market`) where adversarial content may be submitted as service requests.

## Reference

```bibtex
@article{huang2026ccbos,
  title={Obscure but Effective: Classical Chinese Jailbreak Prompt Optimization via Bio-Inspired Search},
  author={Xun Huang et al.},
  journal={arXiv:2602.22983},
  year={2026},
  note={ICLR 2026 Poster}
}
```

## Disclaimer

This is a research tool for AI safety, red-teaming, and defensive analysis. Use responsibly.
