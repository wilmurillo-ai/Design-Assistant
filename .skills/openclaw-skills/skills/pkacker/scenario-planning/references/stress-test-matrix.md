# Strategy Stress Test & Gap Analysis Templates

## Research Basis

This reference combines the **Gap Analysis** methodology with the stress-testing framework from standard project risk management. The Gap Analysis is the quantitative backbone that gives scenarios financial grounding — without it, scenarios remain abstract.

---

## The Planning Gap Concept 

A **Strategic Gap** = the difference between strategic goals and what each scenario actually produces.

The Gap Analysis answers: "If this scenario unfolds, does our project still achieve its objectives — and by how much does it fall short?"

### Step 1: Define your Key Performance Indicators 

Choose 3–5 measurable project performance indicators. Examples:

| KPI | Planned Target | Measurement Method |
|-----|---------------|-------------------|
| Project completion date | [date] | Schedule tracking |
| Total project cost | [$X] | Budget tracking |
| Scope delivered | [%] or [features] | Scope register |
| Return on Sales  or ROI | [%] | Financial model |
| Stakeholder acceptance score | [score] | Survey / sign-off |
| Strategic objectives achieved | [Y/N per objective] | Objective register |

### Step 2: Calculate Gap per Scenario

For each scenario, estimate what each KPI looks like:

| KPI | Planned Target | Baseline Scenario | Scenario 2 | Scenario 3 | Scenario 4 |
|-----|---------------|-------------------|------------|------------|------------|
| Completion date | Q4 2026 | Q4 2026 | Q1 2027 (+1Q) | Q3 2027 (+3Q) | Q2 2026 (-2Q) |
| Total cost | $2.0M | $2.1M | $2.6M (+30%) | $3.2M (+60%) | $1.9M (-5%) |
| Scope delivered | 100% | 100% | 85% (-15%) | 60% (-40%) | 105% (+5%) |
| ROI | 15% | 14% | 8% (-47%) | 2% (-87%) | 18% (+20%) |

**Threshold for concern:** A KPI change of >50% from plan signals that strategic goals will not be met and the scenario requires a fundamentally different strategic response, not just a tactical adjustment.

---

## Strategy Stress Test Matrix

### Full Matrix Template

Rate each plan element in each scenario:
- ✅ **Stable** — holds with no changes required
- ⚠️ **At Risk** — threatened; contingency needed
- 🔴 **Must Change** — cannot survive this scenario; pivot required
- ➕ **Opportunity** — this scenario actually improves conditions

| Plan Element | Baseline | Scenario 2 | Scenario 3 | Scenario 4 | Pattern |
|---|---|---|---|---|---|
| **SCOPE** | | | | | |
| Core deliverables | ✅ | ✅ | ⚠️ | 🔴 | Vulnerable in 1 |
| Stretch features | ✅ | ⚠️ | 🔴 | ➕ | Mixed |
| Quality standards | ✅ | ✅ | ✅ | ✅ | Robust |
| **TIMELINE** | | | | | |
| Phase 1 deadline | ✅ | ✅ | ⚠️ | ✅ | Mostly stable |
| Phase 2 deadline | ✅ | ⚠️ | 🔴 | ✅ | Vulnerable |
| Final deadline | ✅ | ⚠️ | 🔴 | ➕ | High variance |
| **BUDGET** | | | | | |
| Phase 1 budget | ✅ | ✅ | ⚠️ | ✅ | Stable |
| Phase 2 budget | ✅ | ⚠️ | 🔴 | ➕ | High variance |
| Contingency reserve | ✅ | ⚠️ | 🔴 | ✅ | Under pressure |
| **TEAM & RESOURCES** | | | | | |
| Core team availability | ✅ | ✅ | ⚠️ | ✅ | Watch |
| Vendor/partner reliability | ✅ | ⚠️ | 🔴 | ✅ | Vulnerable |
| Critical skills present | ✅ | ✅ | ⚠️ | ✅ | Watch |
| **STAKEHOLDERS** | | | | | |
| Executive sponsor support | ✅ | ✅ | ⚠️ | ✅ | Watch |
| Client/customer alignment | ✅ | ✅ | 🔴 | ➕ | High variance |
| Cross-functional dependencies | ✅ | ⚠️ | 🔴 | ✅ | Vulnerable |
| **TECHNICAL** | | | | | |
| Core technology/platform | ✅ | ✅ | ⚠️ | ✅ | Mostly stable |
| Integration points | ✅ | ⚠️ | 🔴 | ✅ | Vulnerable |
| Security/compliance | ✅ | ✅ | 🔴 | ✅ | Scenario-specific risk |

**Reading the pattern column:**
- Elements marked 🔴 in 2+ scenarios = **Critical vulnerabilities** — highest priority for action
- Elements marked ✅ across all scenarios = **Robust elements** — protect these
- Elements with ➕ in any scenario = **Strategic opportunities** — build plans to capitalize

---

## Strategy Classification

After completing the matrix, classify each potential strategic response:

### No-Regret Moves
Actions that create value or reduce risk **in every scenario**. Execute immediately regardless of which scenario unfolds.

| Action | Why Robust Across All Scenarios | Effort | Priority |
|--------|--------------------------------|--------|----------|
| Document all key assumptions explicitly | Reduces confusion in any scenario | Low | High |
| Build slack into first milestone | Preserves optionality | Low | High |
| Establish fast escalation path | Speeds response in any scenario | Low | High |
| Cross-train on critical tasks | Reduces key-person risk | Medium | High |
| Create prioritized scope backlog | Enables rapid descoping | Low | High |
| Strengthen vendor contracts (exit clauses) | Useful in disrupted scenarios | Medium | Medium |
| Pre-align stakeholders on scope trade-offs | Speeds decision in adversity | Low | High |

### Robust Strategies
These work **reasonably well across multiple scenarios**, even if not optimal in any single one:
- Modular delivery (allows scope adjustment without full redesign)
- Phased investment (avoids large upfront commitment under uncertainty)
- Cross-functional collaboration infrastructure (accelerates pivots)

### Scenario-Specific Strategies
These only work if their scenario is confirmed. Define the activation trigger:

| Strategy | Works In | Activation Trigger | Risk if Wrong |
|----------|----------|--------------------|---------------|
| Accelerate investment in [area] | Scenario 4  | Scenario 4 activation threshold confirmed | Overspend if wrong scenario |
| Descope to MVP | Scenario 3  | Scenario 3 activation threshold confirmed | Under-delivers if wrong scenario |

### Hedging Strategies
Moderately suboptimal in every scenario but protect against the worst outcomes:
- Maintaining a larger contingency reserve than baseline requires
- Running two parallel technical approaches until one is confirmed
- Keeping vendor relationships warm even when they are not needed immediately

---

## Pre-authorized Decision Gates Register

Pre-authorizing decisions now prevents paralysis when a scenario activates. For each critical decision:

| Gate # | Gate Name | Tied to Milestone/Date | Decision Required | Authority | Options | Signals to Read | Default if Ambiguous |
|--------|-----------|----------------------|-------------------|-----------|---------|-----------------|----------------------|
| G1 | Discovery Checkpoint | End of Phase 1 | Proceed / Pivot scope / Pause | PM + Sponsor | A: Full scope / B: Reduced scope / C: Pause | [early warning indicators] | Option A  |
| G2 | Mid-Project Review | [milestone] | Maintain timeline / Extend | PM + Sponsor | A: Hold deadline / B: Extend by [X] | [indicators] | Option A |
| G3 | Budget Gate | Q3 review | Maintain / Reduce / Accelerate | Steering Committee | A: Hold budget / B: Cut $Xk / C: Add $Xk | [indicators] | Option A |

**Design principles for good gates:**
- Tie to natural project events (milestone completions, phase transitions, budget reviews) — not arbitrary dates
- Pre-define what "ambiguous signals" means so the default is not debated under pressure
- Authority must be named — not "management" but a specific person or committee
- The decision must be binary or have clear enumerated options — "review the situation" is not a gate decision

---

## Robustness Assessment 

After completing the matrix, answer:

**1. Which plan elements are vulnerable in 2 or more scenarios?**
*(These are your highest-priority risks — regardless of which scenario unfolds, these elements need reinforcement)*

**2. Which scenario represents the most fundamental departure from the current plan?**
*(The scenario with the most 🔴 ratings requires the most advance preparation and the most pre-authorized decisions)*

**3. What load-bearing assumptions in the current plan break down under adverse scenarios?**
*(These become your primary early warning indicators — monitor them first)*

**4. What is the Minimum Viable Project if the most adverse scenario unfolds?**
*(Define this explicitly now so the team can act without debate if conditions deteriorate)*

**5. What capabilities or resources are missing from the current plan that would be needed in a disrupted scenario?**
*(Build a capability gap list — either acquire these now or identify how to access them quickly)*

---

## Sensitivity Analysis for Quantifiable Projects (PMT/LP elements)

When project performance is measurable (budget, revenue, schedule), apply sensitivity analysis to confirm which variables matter most:

**Method :**
1. Identify all variables that affect your key KPI (e.g., EBT, ROI, timeline)
2. Apply a **uniform 10% negative change** to each variable
3. Measure the impact on the KPI
4. Rank variables by impact magnitude
5. Variables where a 10% change produces **>50% change in the KPI** are your **critical sensitivity factors** — these are the highest-priority Scenario Drivers

**Interpretation:**
- If sales volume produces a 370% decline in EBT for a 10% change → sales volume is your #1 Scenario Driver
- If energy costs produce only 52% change → important but secondary
- If depreciation produces 11% change → background noise for scenario purposes

This analysis prevents the common mistake of building scenarios around the *most dramatic-sounding* uncertainties rather than the *most financially consequential* ones.
