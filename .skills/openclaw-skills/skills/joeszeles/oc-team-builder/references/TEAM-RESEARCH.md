# Research Lab — Autonomous Experiment Methodology

Adapted from Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) framework. The core idea: set up a measurable experiment, run it in a fixed time budget, keep improvements, discard failures, and loop forever.

This methodology is **not limited to ML training**. It applies to any domain with a measurable metric: image analysis pipelines, prompt engineering, configuration tuning, data processing, performance optimization, and more.

Source reference: `reference/autoresearch-master/program.md` and `reference/autoresearch-master/README.md`

## Core Principles

1. **Fixed time budget** — every experiment runs for exactly the same duration, making results directly comparable
2. **Single metric** — one number that defines success (lower is better or higher is better — pick one)
3. **Keep or discard** — if the metric improved, keep the change; if not, revert
4. **Simplicity bias** — a small improvement that adds ugly complexity is not worth it; removing code for equal results is a win
5. **Never stop** — the loop runs until manually interrupted; the agent is fully autonomous

## The Experiment Loop

```
LOOP FOREVER:
  1. Review current state (baseline metric, recent experiments)
  2. Propose a hypothesis — what change might improve the metric?
  3. Implement the change (modify only the in-scope file/config)
  4. Run the experiment (fixed time budget)
  5. Measure the result
  6. Decision:
     - IMPROVED → keep the change, advance
     - EQUAL/WORSE → revert, try something else
     - CRASHED → fix if trivial, skip if fundamental
  7. Log the result to the experiment ledger
  8. Repeat
```

## Experiment Ledger Format

Log every experiment in a TSV file:

```
commit	val_bpb	memory_gb	status	description
a1b2c3d	0.997900	44.0	keep	baseline
b2c3d4e	0.993200	44.2	keep	increase LR to 0.04
c3d4e5f	1.005000	44.0	discard	switch to GeLU activation
d4e5f6g	0.000000	0.0	crash	double model width (OOM)
```

Columns: experiment ID (or git commit hash), metric value, resource usage, status (keep/discard/crash), short description.

## How autoresearch Works (from Karpathy's repo)

Three files that matter:

- **`prepare.py`** — fixed constants, data prep, runtime utilities (dataloader, evaluation). **Never modified.**
- **`train.py`** — the single file the agent edits. Contains the full model, optimizer, and training loop. Everything is fair game: architecture, hyperparameters, optimizer, batch size, etc.
- **`program.md`** — instructions for the agent. The "research org code" that the human iterates on.

By design, training runs for a **fixed 5-minute time budget** (wall clock, excluding startup/compilation). The metric is **val_bpb** (validation bits per byte) — lower is better, vocab-size-independent so architectural changes are fairly compared.

### The autoresearch Loop (verbatim from program.md)

```
LOOP FOREVER:
  1. Look at the git state: the current branch/commit we're on
  2. Tune train.py with an experimental idea by directly hacking the code
  3. git commit
  4. Run the experiment: uv run train.py > run.log 2>&1
  5. Read out the results: grep "^val_bpb:\|^peak_vram_mb:" run.log
  6. If grep output is empty, the run crashed. Run tail -n 50 run.log for stack trace
  7. Record the results in the TSV
  8. If val_bpb improved (lower), "advance" the branch, keeping the git commit
  9. If val_bpb is equal or worse, git reset back to where you started
```

### Key Rules from autoresearch

- **Only modify the in-scope target** — do not change measurement infrastructure, evaluation metric, or fixed constants
- **No new dependencies** — work within the existing toolset
- **Log everything** — every experiment gets recorded, even crashes
- **Simplicity criterion** — all else being equal, simpler is better. A 0.001 improvement that adds 20 lines of hacky code? Not worth it. A 0.001 improvement from deleting code? Definitely keep.
- **NEVER STOP** — do NOT pause to ask the human. The human might be asleep. You are autonomous. If you run out of ideas, think harder — read papers referenced in the code, re-read in-scope files for new angles, try combining previous near-misses, try more radical changes.
- **Timeout handling** — if an experiment exceeds 2x the time budget, kill it and log as crash

## Applying to Any Domain

The autoresearch pattern works anywhere you have a measurable metric:

### Image Analysis
**Metric**: Detection accuracy, classification confidence, or feature count
**In-scope**: Analysis parameters (thresholds, filters, model settings)
**Fixed budget**: Time per analysis run

```
LOOP:
  1. Load image or image set
  2. Apply current analysis pipeline
  3. Measure quality metric
  4. Modify pipeline parameters
  5. Re-run and compare
  6. Keep improvements, discard regressions
```

### Prompt Engineering
**Metric**: Output quality score (automated evaluation or downstream task performance)
**In-scope**: Prompt structure, wording, examples, system instructions
**Fixed budget**: N generations per prompt variant

```
LOOP:
  1. Current prompt baseline
  2. Modify prompt (add detail, restructure, change examples)
  3. Generate N outputs with new prompt
  4. Score outputs against quality criteria
  5. Keep if average score improved
  6. Log variant and score
```

### Performance Optimization
**Metric**: Response time, throughput, memory usage
**In-scope**: Configuration, algorithm choice, caching strategy
**Fixed budget**: Fixed benchmark duration

```
LOOP:
  1. Run benchmark with current configuration
  2. Propose optimization (caching, batching, algorithm swap)
  3. Implement change
  4. Re-run benchmark
  5. Keep if metric improved without regressions
```

### Configuration Tuning
**Metric**: Any measurable outcome (accuracy, speed, quality score)
**In-scope**: Configuration parameters
**Fixed budget**: Time per configuration test

```
LOOP:
  1. Read current config baseline
  2. Propose parameter change
  3. Run with modified parameters
  4. Compare to baseline
  5. Keep if improved, revert if not
  6. Log to experiment ledger
```

## Constraints

- **Only modify the in-scope target** — do not change the measurement infrastructure, the evaluation metric, or the fixed constants
- **No new dependencies** — work within the existing toolset
- **Log everything** — every experiment gets recorded, even crashes
- **Simplicity criterion** — all else being equal, simpler is better
- **Timeout handling** — if an experiment exceeds 2x the time budget, kill it and log as crash

## Combining with Agency Specialists

Research loops benefit from domain experts:

| Domain | Research Role | Agency Specialist |
|--------|--------------|-------------------|
| UI performance | Load time optimization | Performance Benchmarker (measurement) |
| Image quality | Generation parameter tuning | Image Prompt Engineer (prompt structure) |
| API efficiency | Response time optimization | API Tester (validation) |
| Content quality | Prompt refinement | Content Creator (evaluation criteria) |
| Architecture | Config optimization | Backend Architect (system constraints) |
| ML training | Model/hyperparameter tuning | AI Engineer (architecture decisions) |

The Research Lab provides the experiment loop; the specialist provides domain expertise and evaluation criteria.

## Working Example: LLM Training Optimization Trial

This example shows the autoresearch loop applied to optimizing a small language model using the actual autoresearch codebase. The agent runs autonomously, modifying `train.py` and measuring `val_bpb`.

### Setup
```bash
# Clone the autoresearch repo
git clone https://github.com/karpathy/autoresearch
cd autoresearch

# Install dependencies (requires uv package manager)
uv sync

# Prepare data (one-time, ~2 min — downloads data shards, trains BPE tokenizer)
uv run prepare.py

# Create experiment branch
git checkout -b autoresearch/trial-1

# Run baseline (5 minutes fixed budget)
uv run train.py > run.log 2>&1
grep "^val_bpb:" run.log
# val_bpb: 0.997900

# Initialize ledger (TSV — tab-separated, NOT comma-separated)
echo -e "commit\tval_bpb\tmemory_gb\tstatus\tdescription" > results.tsv
echo -e "a1b2c3d\t0.997900\t44.0\tkeep\tbaseline" >> results.tsv
```

### Trial Run (3 experiments)

**Experiment 1: Increase learning rate**
```
Hypothesis: Higher LR may converge faster in 5-min budget
Change: LR 0.03 → 0.04 in train.py
Run: uv run train.py > run.log 2>&1
Result: val_bpb 0.9932 (improved from 0.9979)
Decision: KEEP — 0.0047 improvement, no added complexity
Action: git commit, advance branch
```

**Experiment 2: Switch activation function**
```
Hypothesis: GeLU might outperform ReLU²
Change: F.relu(x).square() → F.gelu(x) in MLP.forward()
Run: uv run train.py > run.log 2>&1
Result: val_bpb 1.0050 (worse than 0.9932)
Decision: DISCARD — regression, reverted
Action: git reset --hard HEAD~1
```

**Experiment 3: Reduce model depth, increase width**
```
Hypothesis: Wider-shallower model may train faster in 5 min
Change: DEPTH 8→6, n_embd 768→896 in train.py
Run: uv run train.py > run.log 2>&1
Result: OOM crash — grep output empty, tail shows CUDA OOM
Decision: CRASH — too much VRAM, reverted
Action: git reset --hard HEAD~1
```

### Final Ledger
```
commit	val_bpb	memory_gb	status	description
a1b2c3d	0.997900	44.0	keep	baseline
b2c3d4e	0.993200	44.2	keep	increase LR to 0.04
c3d4e5f	1.005000	44.0	discard	switch to GeLU activation
d4e5f6g	0.000000	0.0	crash	reduce depth increase width (OOM)
```

The agent improved val_bpb from 0.9979 → 0.9932 in 3 experiments (~15 minutes). At 12 experiments/hour, an overnight run of ~100 experiments explores the parameter space extensively. The user wakes up to a TSV of results and a branch with the best configuration.

### Output Format (from train.py)

Each run prints a summary block:
```
---
val_bpb:          0.997900
training_seconds: 300.1
total_seconds:    325.9
peak_vram_mb:     45060.2
mfu_percent:      39.80
total_tokens_M:   499.6
num_steps:        953
num_params_M:     50.3
depth:            8
```

Extract the key metric: `grep "^val_bpb:" run.log`
Extract memory: `grep "^peak_vram_mb:" run.log`
