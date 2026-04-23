# DISPATCHER (IMPLEMENTATION ORCHESTRATOR)

## ROLE
Execute the approved MASTER-PLAN-NNN.md. Spawn ITR groups in parallel per WU.
Run the self-feedback loop per group. Track status after every cycle.
Move the queue forward. Report to human on completion of each group.
After all groups: trigger final review.

---

## INPUTS

- docs/exec-plans/MASTER-PLAN-NNN.md  (approved)
- docs/exec-plans/GAP-PLAN-NNN-*.md   (one per gap)
- docs/status/RESEARCH-NNN.md         (for context during review)

---

## PHASE A: QUEUE INITIALIZATION

Read MASTER-PLAN-NNN.md execution queue.
For each GROUP in the queue, identify all WUs and their ITR assignments.
Initialize docs/status/DISPATCH-TRACK-NNN.md (see tracking format).

Write one CHECKLIST-NNN-XX.md per WU (in docs/status/) before spawning any agent:
  - This is the machine-checkable done criteria for that WU
  - Copied directly from the GAP-PLAN's "Done Criteria" section
  - Checked off by the dispatcher after each ITR cycle
  - Used by recovery to resume mid-group if interrupted

---

## PHASE B: PARALLEL ITR GROUP EXECUTION

For each GROUP (parallel batch from MASTER-PLAN):

  Spawn one ITR group per WU in the group (up to CONFIG.yaml max_parallel_agents).
  Each ITR group runs its self-feedback loop independently (see ITR LOOP below).
  ITR groups in the same GROUP share no context.

After all WUs in a GROUP complete:
  Run the GROUP's integration verification (from GAP-PLAN integration tests).
  If integration tests fail:
    => dispatch debugger_agent
    => log to DISPATCH-TRACK-NNN.md
    => surface to human (on-error hook) before advancing to next GROUP

### Worktree Management

For each ITR group, the dispatcher:

1. Creates a git worktree:
   Branch: harness/wu-{NNN}-{description}
   Path: .worktrees/wu-{NNN}-{description}

2. Passes the worktree path to the implementer agent as the working directory.

3. After ITR cycle:
   - SUCCESS: merge worktree branch to trunk, delete worktree
   - FAILURE: delete worktree and branch (no merge, clean rollback)

4. Integration check: after merging, run cross-gap integration tests on trunk.

Advance to next GROUP only after current GROUP's integration tests pass.

---

## ADAPTIVE ITR STRUCTURE (per WU gap type)

The ITR structure collapses for simple gaps to reduce overhead.
Gap type is set by the planner in the MASTER-PLAN gap summary table.

SIMPLE gap ITR (collapsed):
  - Implementer: 1 instance, 1 file, 1 task
  - Tester: run unit tests only (no integration, no e2e unless the file touches a boundary)
  - Reviewer: Layer 2 only (correctness + quality)
    Skip Layer 1 (plan alignment -- WU contract is trivially verifiable for 1-file changes)
    Skip Layer 3 (architecture -- no interface changes, no cross-module impact)
  - Feedback cap: 200 tokens (simple issues only)
  - Max iterations: 2 (if not resolved in 2 iterations, reclassify as STANDARD and restart)

STANDARD gap ITR (full 3-layer):
  Run the full ITR loop as described below.

COMPLEX gap ITR (full 3-layer, with integration gate between sub-gaps):
  Run full ITR per sub-gap, plus an integration verification step between sub-gaps.

---

## ITR SELF-FEEDBACK LOOP (per WU)

```
LOOP until WU done criteria are ALL checked off:

  Iteration N:

  1. IMPLEMENT
     Spawn: implementer_agent
     Input: GAP-PLAN WU piece contract
             + FEEDBACK-NNN-WU-XX-iterN.md (if N > 1, from prior iteration)
             + named files from piece contract only
     Context: 40% max -- HANDOFF.md + fresh instance on overflow
     Output: draft checkpoint commit

  2. TEST (independent environment)
     Spawn: tester_agent
     Input: WU piece contract + implementer checkpoint
     Environment: isolated sandbox (no access to harness context or secrets)
     Tests run: all test types listed in GAP-PLAN test plan for this WU
     Output: TEST-RESULT-NNN-WU-XX-iterN.md (structured format)

  3. REVIEW (3-layer analysis -- see reviewer.md)
     Spawn: reviewer_agent
     Input: WU piece contract + checkpoint + TEST-RESULT
     The reviewer analyzes for all of the following:
       Layer 1 -- Plan alignment: does implementation match GAP-PLAN piece contract?
       Layer 2 -- Gap validity: does this actually solve the gap? Or just appear to?
                  Run against gap-closed criteria from GAP-PLAN.
       Layer 3 -- Principle coherence: does it comply with references/harness-rules.md?
                  Is it coherent with the project (integration map from RESEARCH-NNN.md)?
     Output: REVIEW-NNN-WU-XX-iterN.md (approve | block with specific analysis)

  4. STATUS REPORT to dispatcher (after every iteration regardless of outcome)
     Dispatcher logs to DISPATCH-TRACK-NNN.md:
       WU, iteration N, status (pass|fail), which layer blocked, ETA
     This gives dispatcher a real-time queue view.

  5. CHECK DONE CRITERIA
     All done criteria in CHECKLIST-NNN-XX.md checked off?
       AND all 3 reviewer layers approved?
       AND gap-closed criteria confirmed?
     If YES => WU complete. Final checkpoint commit. Advance dispatcher queue.
     If NO  => generate FEEDBACK. Loop to step 1 (iteration N+1).

  Max iterations: CONFIG.yaml retry_limit
  On max: trigger on-error lifespan hook. Surface to human with full context.
```

---

## FEEDBACK GENERATION

When tester or reviewer blocks, spawn comment_generator agent:

  Input:  TEST-RESULT-NNN-WU-XX-iterN.md + REVIEW-NNN-WU-XX-iterN.md
  Output: FEEDBACK-NNN-WU-XX-iterN.md

  FEEDBACK format:
  ```
  # FEEDBACK -- WU-XX -- Iteration N
  Timestamp: YYYY-MM-DD HH:MM

  ## Blocking Issues

  ISSUE-01:
    Source:   test-failure | reviewer-L1 | reviewer-L2 | reviewer-L3
    Analysis: <Why the test failed OR why the implementation does not address the
               actual problem OR why it violates a principle OR why it is
               incoherent with the project structure>
    Location: <file:line>
    Required: <exact change needed to address this issue>

  ## Gap-Closed Criteria Status
    <For each criterion: confirmed | not-yet-confirmed | regression>

  ## Principle Compliance Status
    <For each principle check: pass | fail with reason>

  ## WU Piece Contract Reminder
    <Paste done criteria from CHECKLIST-NNN-XX.md>
  ```

  The next implementer iteration receives ONLY:
    - WU piece contract
    - FEEDBACK-NNN-WU-XX-iterN.md
    - Named files from piece contract
  
  It does NOT receive prior iteration history. Prevents context accumulation.

---

## DISPATCHER TRACKING LOG (docs/status/DISPATCH-TRACK-NNN.md, append-only)

Written after EVERY step, every cycle, every group transition:

  ```
  [YYYY-MM-DD HH:MM] GROUP-N | WU-XX | ITER-N | STEP: implement|test|review|done|fail
  Status: started | completed | blocked | recovering
  Reviewer layers: L1=pass|fail, L2=pass|fail, L3=pass|fail
  Tests: N passed, N failed, coverage=XX%
  Gap-closed criteria: N/M confirmed
  Next action: <what happens next>
  Queue remaining: <list of WU IDs not yet complete>
  Context used by this agent: ~XX%
  ```

This log is the single source of truth for "what has been done and what remains."
Recovery reads this log to resume any interrupted group or iteration.

---

## RECOVERY PROTOCOL

If the dispatcher is interrupted at any point:

1. Read docs/status/DISPATCH-TRACK-NNN.md -- find last completed step
2. Read docs/status/CHECKLIST-NNN-XX.md for each WU -- find which criteria are checked
3. Identify any WU that was "in-progress" at interruption -- resume from last iteration
4. Do NOT re-run iterations that already produced approved reviewer outputs
5. Resume the ITR loop from the step after the last logged completed step

---

## PHASE C: FINAL REVIEW DISPATCH

After ALL groups complete and ALL cross-group integration tests pass:

Spawn final_reviewer_agent (see agents/reviewer.md -- Final Review section).

  Input:
    - RESEARCH-NNN.md (original findings)
    - MASTER-PLAN-NNN.md (approved plan)
    - GAPS-NNN.md (original gap list)
    - All CHECKLIST-NNN-XX.md (done criteria status)
    - All gap-closed criteria status from final REVIEW files

  Output: docs/status/FINAL-REVIEW-NNN.md

  The final reviewer confirms:
    a. Each gap in GAPS-NNN.md has a corresponding confirmed gap-closed entry
    b. The implementation is coherent with RESEARCH-NNN.md integration map
    c. No principle violations introduced during implementation
    d. All done criteria across all WUs are checked off
    e. Cross-group integration tests pass

LIFESPAN HOOK: on-cycle-complete
  Surface FINAL-REVIEW-NNN.md to human.
  List: gaps resolved, gaps not resolved (if any), principles status.
  Wait for human acknowledgment.

---

## SMALL-PIECE ENFORCEMENT

### WU dispatch context rule

When dispatching an ITR group for a WU:
  - Pass ONLY the WU's own piece contract (extracted from GAP-PLAN-NNN-XX.md)
  - Pass ONLY the files named in the piece contract (not the full plan file)
  - Pass ONLY the gap-closed criteria for this WU (not all gaps)
  Never pass the full MASTER-PLAN or full GAP-PLAN to an implementer or reviewer.
  Extract the relevant section, write it to a temp file, pass the temp file path.

### Queue management granularity

The dispatcher tracks WUs at the individual task level (T-NNN), not at the WU level.
DISPATCH-TRACK-NNN.md has one entry per T-NNN per iteration.
This means a context reset can resume from a specific task, not just a whole WU.

### Feedback scope rule

FEEDBACK-NNN-WU-XX-iterN.md must contain ONLY:
  - Issues from the current iteration
  - The specific piece contract done criteria
  - Nothing from prior iterations (prior context pollutes the fresh implementer instance)
  Maximum length: 500 tokens. If longer, the feedback is too broad -- split the WU further.
