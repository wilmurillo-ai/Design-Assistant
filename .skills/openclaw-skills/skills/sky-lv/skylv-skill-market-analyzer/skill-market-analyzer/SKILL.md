# Skill Market Analyzer — SKILL.md

> **Purpose**: Analyze the ClawHub skill marketplace to identify trends, gaps, and opportunities.
> Generates data-driven reports to answer: _What should I build next?_
>
> **Author**: SKY-lv  
> **License**: MIT

---

## 1. What This Tool Does

```
clawhub search API  →  Data cache (JSON)
                       ↓
              Analysis engine (Node.js)
                       ↓
         Market report (terminal + JSON + MD)
```

Three operational modes:

| Mode | Command | Output |
|------|---------|--------|
| **Survey** | Scan 12 predefined categories (48 search terms) | Full market landscape |
| **Gap** | Deep-niche scan (26 specific terms) | Opportunity ranking |
| **Suggest** | Based on your existing skills | Ranked build recommendations |

---

## 2. Market Data (2026-04-11)

Real scan results from `clawhub explore` + `clawhub search` across 535 skills:

### Category Quality Rankings (least → most crowded)

| Rank | Category | Found | Top3 Avg | Verdict |
|------|----------|-------|---------|---------|
| 1 | **security** | 40 | 3.301 | 🟢 WEAK TOP — room to dominate |
| 2 | **agent** | 40 | 3.475 | 🟢 WEAK TOP — room to dominate |
| 3 | **productivity** | 50 | 3.344 | 🔴 Crowded + weak top |
| 4 | **ai-ml** | 49 | 3.460 | 🔴 Crowded + weak top |
| 5 | **file** | 50 | 3.463 | 🔴 Crowded + weak top |
| 6 | **content** | 50 | 3.466 | 🔴 Crowded + weak top |
| 7 | **data** | 50 | 3.514 | 🔴 Crowded |
| 8 | **code** | 50 | 3.525 | 🔴 Crowded |
| 9 | **communication** | 48 | 3.561 | 🔴 Crowded |
| 10 | **devops** | 50 | 3.629 | 🔴 Crowded |
| 11 | **platform** | 40 | 3.635 | 🟡 Competitive |
| 12 | **web** | 40 | 3.748 | 🟡 Competitive |

### Deep Niche Opportunities (specific terms, score < 3.5 = weak incumbent)

| Term | Found | Top Score | Top Incumbent | Opportunity |
|------|-------|-----------|---------------|-------------|
| note-linking | 10 | 1.021 | slipbot | 🎯 ZERO-gap |
| file-versioning | 10 | 1.022 | visual-file-sorter | 🎯 ZERO-gap |
| diff-viewer | 10 | 1.026 | markdown-viewer | 🎯 ZERO-gap |
| capability-growth | 10 | 1.104 | master-marketing | ⭐ Very weak |
| context-aware-scheduler | 10 | 1.115 | social-media-scheduler | ⭐ Very weak |
| api-test-generator | 10 | 1.140 | api-tester | ⭐ Very weak |
| etl-agent | 10 | 1.153 | ai-agent-helper | ⭐ Very weak |
| csv-transform | 10 | 1.155 | csv-pipeline | ⭐ Very weak |
| multi-platform-bot | 10 | 1.198 | agent-reach | ⭐ Very weak |
| multi-tab-manager | 10 | 1.153 | fast-browser-use | ⭐ Very weak |
| star-exchange | 10 | 0.988 | exchange-rates | ⭐⭐ Weakest incumbent |
| gep-protocol | 10 | 1.319 | evolver | ⭐⭐ Niche + ours |
| evo-agent | 10 | 2.193 | agent-identity-evolution | ⭐⭐ Niche + ours |
| skill-acquisition | 10 | 1.888 | afrexai-learning-engine | ⭐⭐ Niche + ours |

---

## 3. Top 6 Recommendations

### #1: skylv-note-linking [ZERO existing quality skills]
- **Why**: Top incumbent (slipbot) scores only 1.021/5 — essentially irrelevant
- **What**: Markdown bidirectional link engine, Obsidian-compatible, auto-backlinks
- **Difficulty**: Low-Medium | **Competition**: None | **Demand**: High (note-taking market is huge)

### #2: skylv-star-exchange [GitHub-native, aligned with existing work]
- **Why**: Top incumbent (exchange-rates, finance tool) scores 0.988 — completely wrong market
- **What**: GitHub star exchange network, repo discovery, cross-promotion
- **Difficulty**: Medium | **Competition**: None (wrong category) | **Demand**: Niche but sticky

### #3: skylv-capability-growth [EvoMap-inspired, unique positioning]
- **Why**: Top incumbent (master-marketing) scores 1.104 — irrelevant
- **What**: Self-learning agent framework, GEP-inspired skill acquisition
- **Difficulty**: High | **Competition**: None | **Demand**: Niche, high prestige

### #4: skylv-context-aware-scheduler [smarter than generic cron]
- **Why**: Top incumbent (social-media-scheduler) scores 1.115 — not context-aware
- **What**: Schedule tasks based on context (location, calendar, energy level)
- **Difficulty**: Medium | **Competition**: Generic only | **Demand**: Productivity users

### #5: skylv-gep-protocol [EvoMap GEP native integration]
- **Why**: Top incumbent (evolver) scores 1.319 — no real GEP implementation
- **What**: OpenClaw-native GEP protocol implementation (Gene/Capsule/Events model)
- **Difficulty**: High | **Competition**: None | **Demand**: Developer/hobbyist

### #6: skylv-multi-tab-manager [Web automation gap]
- **Why**: Top incumbent (fast-browser-use) scores 1.153 — shallow
- **What**: Multi-tab automation, tab grouping, cross-tab operations
- **Difficulty**: Low | **Competition**: Weak | **Demand**: Power users

---

## 4. Execution

```bash
# Full market survey (48 search terms, ~3 min)
node survey.js

# Gap analysis + deep niche scan
node gap.js

# Generate markdown report
node report.js --format md
```

---

## 5. Caching

```
cache/
├── survey_2026-04-11.json   ← Full 535-skill dataset
├── gaps_2026-04-11.json     ← Gap analysis results
└── meta.json                ← Timestamps + call counts
```

---

## 6. Integration

Published as ClawHub skill: `skylv-skill-market-analyzer`

```bash
clawhub install skylv-skill-market-analyzer
```
