# Multi-Agent Council Pattern

Complete implementation guide for the specialized-agent council approach to quality automation.

## Architecture Overview

The Council pattern uses 6-8 specialized agents orchestrated through distinct phases, with a mandatory quality gate.

```
┌─────────────────────────────────────────┐
│ THE ORCHESTRATOR                        │
│ (Pipeline Manager & Router)             │
└──────────────┬──────────────────────────┘
               │
    ┌──────────▼──────────┐
    │ PHASE 1: ANALYSIS   │
    │ 👔 The Analyst      │
    └──────────┬──────────┘
               │ Feature Design Doc
    ┌──────────▼──────────┐
    │ PHASE 2: PLANNING   │
    │ 🏗️ The Architect    │
    └──────────┬──────────┘
               │ Test Plan (P0/P1/P2)
    ┌──────────▼──────────┐
    │ PHASE 3: GENERATION │
    │ ⚙️ The Engineer     │
    └──────────┬──────────┘
               │ Tests/Code
    ┌──────────▼──────────┐
    │ PHASE 4: AUDIT      │
    │ 🛡️ The Sentinel     │
    │ ★ QUALITY GATE ★   │
    └──────────┬──────────┘
               │ BLOCKS if critical issues
    ┌──────────▼──────────┐
    │ PHASE 5: HEALING    │
    │ 🔧 The Healer       │
    └──────────┬──────────┘
               │ Iterates until passing
    ┌──────────▼──────────┐
    │ PHASE 6: DOCS       │
    │ 📝 The Scribe       │
    └─────────────────────┘

     ┌──────────────┐
     │🔍 Inspector  │
     │ (PR Reviewer)│
     └──────────────┘
```

## Agent Roles

### The Orchestrator
**Responsibility:** Pipeline coordination and routing

**Inputs:** Feature request, repo context

**Outputs:** Routed task to appropriate agent chain

**Decisions:**
- Which variant to test (OSS vs Enterprise)
- Which agents are needed for this task
- Parallel vs sequential execution

**Implementation notes:**
- Stateless; can restart from any phase
- Logs all routing decisions for debugging

### Phase 1: The Analyst
**Responsibility:** Feature understanding and selector extraction

**Inputs:**
- Source code for the feature
- UI component definitions
- Existing tests (for context)

**Outputs:** Feature Design Document including:
- All data-test selectors mapped to components
- User workflows (step-by-step)
- Edge cases and error states
- Dependencies and API calls

**Key behaviors:**
- Reads actual source code, not docs
- Extracts every selector to avoid brittle tests
- Identifies error paths, not just happy paths

**Example output:**
```markdown
# Feature: Alert Destinations

## Selectors
- `[data-test="destination-type-select"]` - Dropdown for destination type
- `[data-test="slack-webhook-input"]` - Slack webhook URL field
- `[data-test="save-destination-btn"]` - Save button

## User Workflows
1. Create new destination: Select type → Fill fields → Save → Verify in list
2. Edit destination: Click edit → Modify → Save → Verify changes
3. Delete destination: Click delete → Confirm → Verify removal

## Edge Cases
- Invalid webhook URL format
- Duplicate destination names
- Network failure during save
```

### Phase 2: The Architect
**Responsibility:** Test planning and prioritization

**Inputs:** Feature Design Document

**Outputs:** Test Plan with priorities:
- **P0** - Critical paths (CRUD operations, happy paths)
- **P1** - Core functionality (error handling, validation)
- **P2** - Edge cases (boundary conditions, race conditions)

**Key behaviors:**
- Balances coverage vs maintenance burden
- Groups related tests for efficiency
- Calls out dependencies between tests

**Example output:**
```markdown
# Test Plan: Alert Destinations

## P0 - Critical Paths
1. Create Slack destination with valid webhook
2. Edit existing destination and save
3. Delete destination
4. List all destinations

## P1 - Core Functionality
5. Validate webhook URL format
6. Handle duplicate destination names
7. Show error on save failure
8. Cancel edit without saving

## P2 - Edge Cases
9. Create destination with special characters in name
10. Rapid create/delete (race condition check)
```

### Phase 3: The Engineer
**Responsibility:** Test code generation

**Inputs:**
- Feature Design Document (selectors)
- Test Plan (what to test)
- Page Object Model patterns (framework)

**Outputs:** Playwright test code following project conventions

**Key behaviors:**
- Uses ONLY selectors from Analyst (no raw selectors)
- Follows Page Object Model for maintainability
- Includes assertions for every expected outcome
- Groups tests logically

**Example output:**
```typescript
test.describe('Alert Destinations', () => {
  test('should create Slack destination', async ({ page }) => {
    const destPage = new DestinationsPage(page);
    await destPage.clickCreateNew();
    await destPage.selectType('Slack');
    await destPage.fillWebhook('https://hooks.slack.com/...');
    await destPage.clickSave();
    await expect(destPage.successMessage).toBeVisible();
    await expect(destPage.destinationList).toContainText('My Slack');
  });
});
```

### Phase 4: The Sentinel (Quality Gate)
**Responsibility:** Code audit and blocking enforcement

**Inputs:** Generated test code

**Outputs:**
- **PASS** → continue to Healer
- **BLOCK** → critical issues found, pipeline stops

**Audit checks:**
1. **Framework violations**
   - Raw selectors in test code (must use Page Objects)
   - Missing awaits on async operations
   - Hardcoded credentials or secrets

2. **Anti-patterns**
   - Brittle locators (CSS selectors instead of data-test)
   - Missing assertions (test runs but doesn't verify)
   - Sleep/waits instead of proper waitFor

3. **Security issues**
   - API keys in code
   - Sensitive data in test fixtures

**Key behaviors:**
- Hard gate: if critical issues found, BLOCKS the entire pipeline
- No compromises on security or framework violations
- Provides actionable feedback for fixes

**Why it matters:**
Early enforcement of quality standards prevents tech debt. The friction creates long-term quality.

### Phase 5: The Healer
**Responsibility:** Test execution and self-repair

**Inputs:**
- Test code from Engineer
- Audit results from Sentinel

**Outputs:**
- Passing tests
- Failure diagnosis and fixes

**Key behaviors:**
- Runs tests and captures failures
- Analyzes root cause (selector changed? timing issue? logic bug?)
- Applies fixes:
  - Update selectors if UI changed
  - Add explicit waits for timing issues
  - Fix logic errors in test code
- Iterates up to 5 times
- If still failing after 5 iterations, escalates to human

**Example healing:**
```
Iteration 1: Test fails - "Timeout waiting for [data-test=save-btn]"
Diagnosis: Selector not found in DOM
Fix: Check actual DOM, find selector is now [data-test=destination-save]
Update test code
Iteration 2: Test passes ✓
```

**Why iteration matters:**
Tests rarely pass on first try. Selectors change, APIs evolve, timing issues emerge. A system that gives up after one failure isn't autonomous.

### Phase 6: The Scribe
**Responsibility:** Documentation and audit trail

**Inputs:**
- Feature Design Document
- Test Plan
- Final passing test code
- Healing history

**Outputs:**
- Test case documentation in test management system
- Execution summary
- Known issues or limitations

**Key behaviors:**
- Links tests to features for traceability
- Documents any deviations from original plan
- Records healing iterations for debugging

### The Inspector (Independent)
**Responsibility:** PR review for test changes

**Inputs:** GitHub PR with E2E test modifications

**Outputs:** PR comments with audit results

**Key behaviors:**
- Runs same audit rules as Sentinel
- Flags violations in existing tests
- Suggests improvements
- Does NOT block merge (informational only)

**Why separate from pipeline:**
Provides continuous quality feedback on human-written tests, not just agent-generated ones.

## Context Chaining

Each agent receives rich context from prior phases. This is critical for intelligent decisions.

**Example:**
- Engineer sees Analyst's feature doc AND Architect's test plan
- Healer sees test code AND failure logs AND Sentinel's audit
- Scribe sees entire pipeline history

**Implementation:**
Pass artifacts between phases as structured data (JSON/YAML) or markdown documents. Avoid forcing agents to re-discover information.

## Workflow States

```
PENDING → ANALYZING → PLANNING → GENERATING → AUDITING → HEALING → DOCUMENTING → COMPLETE

Possible transitions:
- AUDITING → BLOCKED (critical issues)
- HEALING → ESCALATED (failed after 5 iterations)
- Any phase → FAILED (unrecoverable error)
```

## Iteration Limits

To prevent infinite loops:
- Healer: max 5 iterations
- If Healer fails, escalate to human (don't retry Architect/Engineer)
- Orchestrator can restart from ANALYZING if feature definition was wrong

## Real-World Lessons

### Quality Gate Changed Everything
The Sentinel blocking the pipeline for critical issues was controversial initially ("What if it's wrong?"). But the hard gate forced better practices: improved Page Object Model, standardized patterns, clearer prompts. The friction created long-term quality.

### Specialization > Generalization
Early attempts used one "super agent" to do everything. It failed. Bounded agents with clear roles work infinitely better. The Analyst focuses solely on feature analysis, Sentinel only audits, Healer only debugs.

### The Inspector Caught Production Bugs
While generating tests for a ServiceNow integration, the Healer found a bug in the edit flow—URL parsing logic that failed silently in production. No customer had reported it yet. The test automation caught it first.

**Insight:** Comprehensive test coverage + diagnostic capabilities = quality amplifier.

## Cost Management

From production deployment (380 → 700+ tests):
- Total cost: ~$80 worth of tokens
- Duration: 45 days
- Average per test: ~$0.11

**Cost control strategies:**
- Use cheaper models for Analyst/Architect/Scribe (GPT-4o-mini)
- Use premium models for Healer (requires strong reasoning)
- Cache Feature Design Documents for related tests
- Batch test generation by feature area

## Integration Points

### With CI/CD
```yaml
# GitHub Actions example
on:
  pull_request:
    types: [labeled]

jobs:
  council:
    if: contains(github.event.pull_request.labels.*.name, 'needs-e2e')
    runs-on: ubuntu-latest
    steps:
      - name: Run QA Council
        run: |
          council orchestrate \
            --feature "${{ github.event.pull_request.title }}" \
            --branch "${{ github.head_ref }}" \
            --output-pr
```

### With Test Management
The Scribe integrates with tools like TestRail, Jira Test, or custom systems via API:

```python
# Example: Update test case in TestRail
scribe.document(
    feature="Alert Destinations",
    test_plan=test_plan,
    test_code=test_code,
    test_mgmt_api="https://testrail.example.com/api/v2"
)
```

## Adapting the Pattern

The Council pattern is flexible. Adjust based on needs:

**Minimal Council (3 agents):**
- Analyst → Engineer → Healer
- Skip Architect if test plan is obvious
- Skip Scribe if no test management system

**Extended Council (9+ agents):**
- Add Performance Auditor (check for slow tests)
- Add Accessibility Auditor (a11y violations)
- Add Visual Regression Agent (screenshot comparison)

**Domain-Specific:**
- API testing: Analyst extracts endpoints, Engineer generates API tests
- Security testing: Sentinel focuses on auth/injection vulnerabilities
- Mobile testing: Analyst identifies platform-specific selectors

## Success Metrics

Track these to measure impact:

**Speed:**
- Time from feature merge to test PR open
- Average healing iterations needed
- Pipeline throughput (tests/day)

**Quality:**
- Flaky test rate
- Sentinel block rate (should decrease over time)
- Production bugs caught during test generation

**Coverage:**
- Total test count growth
- Feature coverage %
- Edge cases identified by Analyst

**Cost:**
- Token spend per test
- Human review time saved
- ROI (cost vs bugs prevented)

---

**Bottom line:** The Council pattern works because specialization, iteration, and quality gates create a system that doesn't just automate—it improves quality systematically.
