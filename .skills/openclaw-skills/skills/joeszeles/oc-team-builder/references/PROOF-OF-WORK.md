# Proof of Work — Team Builder Skill

This document demonstrates the Team Builder skill in action, showing the Planner proposing teams for sample tasks that cross roster boundaries.

## Test 1: "Analyze Astronomy Photos for Star Classification"

### Input Task
> Analyze a set of deep-space telescope images. Identify and classify star types by color temperature and luminosity. Generate enhanced images highlighting each classification.

### Planner Output

```
## Team Proposal

### Task
Analyze deep-space telescope images for star classification with enhanced visualization

### Classification
- Domain: Visual Analysis + Research + Creative
- Mode: Sprint
- Estimated effort: 3-5 days

### Proposed Team

| Role | Agent | Roster | Activation Phase |
|------|-------|--------|-----------------|
| Leader | CEO | Core | Phase 1 |
| Scoping | Senior PM | Agency PM | Phase 1 |
| Image Acquisition | Artist | Core | Phase 2 |
| Prompt Engineering | Image Prompt Engineer | Agency Design | Phase 2 |
| Analysis Loop | Research Lab | Research | Phase 2 |
| ML Classification | AI Engineer | Agency Engineering | Phase 2 |
| Data Reporting | Analytics Reporter | Agency Specialized | Phase 3 |
| QA | Evidence Collector | Agency Testing | Phase 3 |
| Gate | Reality Checker | Agency Testing | Phase 3 |

### Execution Plan
1. Senior PM scopes: define classification categories, image set size, accuracy targets
2. Artist + Image Prompt Engineer process raw telescope images (contrast, filtering)
3. Research Lab runs iterative classification loop:
   - Metric: classification accuracy (% correctly typed stars)
   - In-scope: detection thresholds, color temperature bins, luminosity cutoffs
   - Budget: 5-min analysis pass per configuration
   - Loop: adjust parameters → re-classify → compare accuracy → keep/discard
4. AI Engineer tunes the classification model parameters
5. Artist generates enhanced visualization images with classification overlays
6. Analytics Reporter compiles results into a summary report
7. Evidence Collector validates classifications against known catalogs
8. Reality Checker certifies the final output

### Handoff Chain
Senior PM (scope) → Artist + Image Prompt Engineer (image prep) →
Research Lab + AI Engineer (classification loop) → Artist (enhanced visuals) →
Analytics Reporter (report) → Evidence Collector → Reality Checker
```

### Why This Works
- **Three rosters active**: Core (CEO, Artist), Agency (5 specialists from 4 divisions), Research Lab
- **Cross-pollination**: Research methodology applied to image analysis
- **Artist + Design pairing**: Image Prompt Engineer structures prompts for Artist's image generation
- **Evidence-based QA**: Agency Testing division validates before shipping

---

## Test 2: "Optimize a Prompt Engineering Pipeline"

### Input Task
> Our image generation prompts are producing inconsistent quality. Set up an optimization experiment to improve prompt quality scores by tuning prompt structure, detail level, and style descriptors.

### Planner Output

```
## Team Proposal

### Task
Optimize image generation prompts — improve quality score from baseline

### Classification
- Domain: Creative + Research
- Mode: Sprint
- Estimated effort: 1-2 weeks (continuous experiment loops)

### Proposed Team

| Role | Agent | Roster | Activation Phase |
|------|-------|--------|-----------------|
| Leader | CEO | Core | Phase 1 |
| Prompt Craft | Image Prompt Engineer | Agency Design | Phase 1 |
| Experiment Loop | Research Lab | Research | Phase 2 |
| Image Generation | Artist | Core | Phase 2 |
| Quality Eval | Visual Storyteller | Agency Design | Phase 2 |
| Tracking | Experiment Tracker | Agency PM | Phase 2 |
| QA | Evidence Collector | Agency Testing | Phase 3 |

### Execution Plan
1. Image Prompt Engineer establishes baseline prompt structure and scoring criteria
2. Research Lab runs autoresearch loop:
   - Metric: average quality score across N generated images
   - In-scope: prompt structure, detail level, style descriptors, technical terms
   - Budget: 5 generations per prompt variant
   - Loop: modify prompt → generate → score → keep/discard
3. Artist generates images for each prompt variant
4. Visual Storyteller evaluates narrative quality
5. Experiment Tracker logs all variants and scores
6. Evidence Collector validates the winning configuration

### Handoff Chain
Image Prompt Engineer (baseline) → Research Lab + Artist (experiment loop) →
Experiment Tracker (logging) → Evidence Collector (validate)
```

### Why This Works
- **Research Lab + Creative pairing**: autoresearch methodology applied to prompt optimization
- **Measurable metric**: quality score makes keep/discard decisions objective
- **Iterative**: 12 experiments/hour, overnight yields ~100 prompt variants tested

---

## Test 3: "Build a Portfolio Dashboard"

### Input Task
> Create a new Portfolio tab with pie charts showing asset allocation and a rebalancing interface.

### Planner Output

```
## Team Proposal

### Task
New Portfolio tab with pie charts and rebalancing

### Classification
- Domain: Engineering
- Mode: Micro
- Estimated effort: 2-3 days

### Proposed Team

| Role | Agent | Roster | Activation Phase |
|------|-------|--------|-----------------|
| Leader | CEO | Core | Phase 1 |
| Frontend Build | Frontend Developer | Agency Engineering | Phase 2 |
| UX Design | UI Designer | Agency Design | Phase 2 |
| QA | Evidence Collector | Agency Testing | Phase 3 |

### Execution Plan
1. CEO scopes requirements via existing dashboard patterns
2. UI Designer creates component layout and interaction flow
3. Frontend Developer builds the Portfolio tab using existing charting libraries
4. Evidence Collector screenshots desktop/tablet/mobile viewports

### Handoff Chain
CEO (scope) → UI Designer (layout) → Frontend Developer (build) → Evidence Collector (validate)
```

### Why This Works
- **Micro mode**: Small team, fast execution, right-sized for the task
- **No over-engineering**: Only 4 agents, no Research Lab needed for a UI feature
- **Existing patterns**: Leverages dashboard's existing tab system and charting

---

## Test 4: "Autonomous LLM Training Optimization" (Research Lab Example)

### Input Task
> Use the autoresearch framework to optimize a small language model overnight. Run autonomous experiments on train.py, measuring val_bpb.

### Planner Output

```
## Team Proposal

### Task
Autonomous LLM training optimization using autoresearch

### Classification
- Domain: Research + AI
- Mode: Sprint (autonomous overnight)
- Estimated effort: 8-12 hours autonomous

### Proposed Team

| Role | Agent | Roster | Activation Phase |
|------|-------|--------|-----------------|
| Leader | CEO | Core | Phase 1 |
| Experiment Loop | Research Lab | Research | Phase 2 |
| ML Expertise | AI Engineer | Agency Engineering | Phase 2 |
| Tracking | Experiment Tracker | Agency PM | Phase 2 |
| QA | Reality Checker | Agency Testing | Phase 3 |

### Execution Plan
1. CEO sets up the autoresearch repo (uv sync, uv run prepare.py)
2. Research Lab runs the autoresearch loop on train.py:
   - Metric: val_bpb (lower is better)
   - In-scope: train.py (model, optimizer, hyperparameters)
   - Budget: 5 minutes per experiment
   - Loop: modify → train → measure → keep/discard (NEVER STOP)
3. AI Engineer provides architecture suggestions when the loop stalls
4. Experiment Tracker maintains the results.tsv ledger
5. Reality Checker reviews the final best configuration

### Key: AUTONOMOUS LOOP
The Research Lab agent runs INDEFINITELY until manually stopped.
Expect ~12 experiments/hour, ~100 experiments overnight.
```

---

## Summary

| Test | Rosters Used | Agents | Mode | Key Cross-Team Integration |
|------|-------------|--------|------|---------------------------|
| Astronomy Photo Analysis | Core + Agency + Research | 9 | Sprint | Research loops on image analysis, Artist + Image Prompt Engineer |
| Prompt Optimization | Core + Agency + Research | 7 | Sprint | autoresearch loop on prompt variants |
| Portfolio Dashboard | Core + Agency | 4 | Micro | Frontend Developer + UI Designer |
| LLM Training | Core + Agency + Research | 5 | Sprint | autoresearch loop on train.py |

The Planner correctly:
1. Classified each task's domain
2. Selected the right mode (Micro/Sprint/Full) based on complexity
3. Composed teams from multiple rosters where beneficial
4. Defined clear activation phases and handoff chains
5. Included QA agents (Evidence Collector / Reality Checker) in every proposal
6. Leveraged cross-roster integration (Research + Artist, Research + AI Engineer, etc.)
