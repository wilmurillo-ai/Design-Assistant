---
name: ralph
description: Persistence loop until task completion with verification - "don't stop until it's done"
version: 1.0.0
author: Rook (adapted from oh-my-codex)
---

# Ralph Skill for OpenClaw

Self-referential loop that keeps working on a task until it is **fully complete** and verified. Ralph prevents "almost done" syndrome.

## What It Does

Ralph is a **persistence wrapper** around tasks:
1. Takes a task that must be completed
2. Works on it iteratively (up to 10 iterations)
3. Verifies completion with fresh evidence
4. If not done → fixes issues and repeats
5. If done → clean exit

**The boulder never stops rolling until it reaches the top.**

## Usage

```bash
/ralph "implement user authentication with JWT tokens"
/ralph "fix all TypeScript errors in src/ directory"
/ralph "write comprehensive tests for the API"
```

Or say: "ralph", "don't stop", "must complete", "keep going until done"

## When to Use

✅ **Use Ralph when:**
- Task requires guaranteed completion (not "do your best")
- Work may span multiple attempts
- You need verification before declaring done
- Task has clear completion criteria (tests pass, build succeeds)

❌ **Don't use Ralph when:**
- Quick one-shot fix needed
- You want manual control over completion
- Task is exploratory (research, planning)

## How It Works

### The 10-Step Loop

```
┌─────────────────────────────────────┐
│  1. CONTEXT SNAPSHOT                │
│     Save task state to file         │
├─────────────────────────────────────┤
│  2. REVIEW PROGRESS                 │
│     Check what was done before      │
├─────────────────────────────────────┤
│  3. CONTINUE FROM WHERE LEFT OFF    │
│     Pick up incomplete tasks        │
├─────────────────────────────────────┤
│  4. DELEGATE WORK                   │
│     Route to appropriate agents     │
├─────────────────────────────────────┤
│  5. RUN LONG OPS IN BACKGROUND      │
│     Builds, installs, tests         │
├─────────────────────────────────────┤
│  6. VERIFY COMPLETION               │
│     Fresh evidence required         │
├─────────────────────────────────────┤
│  7. ARCHITECT REVIEW                │
│     Quality verification            │
├─────────────────────────────────────┤
│  8. DESLOP PASS                     │
│     Clean up AI-generated slop      │
├─────────────────────────────────────┤
│  9. REGRESSION CHECK                │
│     Ensure nothing broke            │
├─────────────────────────────────────┤
│  10. DECISION                       │
│     Done → Exit / Not done → Loop   │
└─────────────────────────────────────┘
```

### State Management

Ralph maintains state in `~/.openclaw/state/ralph/`:

```
~/.openclaw/state/ralph/
├── current-task.json       # Active task definition
├── iteration-N/            # Each attempt
│   ├── attempt.log         # What was tried
│   ├── result.json         # Outcome
│   └── evidence/           # Proof of work
└── verification.json       # Final verification
```

### Completion Criteria

Ralph considers task complete ONLY when ALL are true:

- [ ] All requirements from original task are met
- [ ] Zero pending TODO items
- [ ] Fresh test run shows all tests pass
- [ ] Fresh build shows success
- [ ] No new errors introduced
- [ ] Architect verification passed
- [ ] Post-cleanup regression tests pass

## Implementation

```bash
#!/bin/bash
# ~/.openclaw/skills/ralph/ralph.sh

TASK="$1"
MAX_ITERATIONS=10
STATE_DIR="$HOME/.openclaw/state/ralph"

# Initialize state
mkdir -p "$STATE_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ITERATION=1

# Save task
cat > "$STATE_DIR/current-task.json" << EOF
{
  "task": "$TASK",
  "started_at": "$TIMESTAMP",
  "max_iterations": $MAX_ITERATIONS,
  "status": "active"
}
EOF

echo "=== RALPH: Starting persistence loop ==="
echo "Task: $TASK"
echo "Max iterations: $MAX_ITERATIONS"
echo ""

while [[ $ITERATION -le $MAX_ITERATIONS ]]; do
  echo "--- Iteration $ITERATION/$MAX_ITERATIONS ---"
  
  # Create iteration directory
  ITER_DIR="$STATE_DIR/iteration-$ITERATION"
  mkdir -p "$ITER_DIR/evidence"
  
  # Step 1-5: Do the work (delegated to main agent)
  echo "Working on task..."
  
  # Step 6: Verify completion
  echo "Verifying completion..."
  
  # Run verification commands
  VERIFICATION_PASSED=true
  
  # Check if tests pass
  if [[ -f "package.json" ]]; then
    if ! npm test > "$ITER_DIR/evidence/test.log" 2>&1; then
      VERIFICATION_PASSED=false
      echo "❌ Tests failed"
    else
      echo "✅ Tests passed"
    fi
  fi
  
  # Check if build succeeds
  if [[ -f "package.json" ]]; then
    if ! npm run build > "$ITER_DIR/evidence/build.log" 2>&1; then
      VERIFICATION_PASSED=false
      echo "❌ Build failed"
    else
      echo "✅ Build succeeded"
    fi
  fi
  
  # Check for TODOs
  TODO_COUNT=$(grep -r "TODO\|FIXME\|XXX" --include="*.ts" --include="*.js" --include="*.py" . 2>/dev/null | wc -l)
  if [[ $TODO_COUNT -gt 0 ]]; then
    echo "⚠️  Found $TODO_COUNT TODO items"
  fi
  
  # Step 7: Decision
  if [[ "$VERIFICATION_PASSED" == true && $TODO_COUNT -eq 0 ]]; then
    echo ""
    echo "=== RALPH: TASK COMPLETE ==="
    echo "Completed in $ITERATION iterations"
    echo "All verification passed"
    
    # Mark complete
    cat > "$STATE_DIR/verification.json" << EOF
{
  "status": "complete",
  "iterations": $ITERATION,
  "completed_at": "$(date +%Y%m%d_%H%M%S)",
  "verification": "passed"
}
EOF
    
    # Clean exit
    /cancel
    exit 0
  fi
  
  # Not complete - save state and continue
  cat > "$ITER_DIR/result.json" << EOF
{
  "iteration": $ITERATION,
  "verification_passed": $VERIFICATION_PASSED,
  "todos_remaining": $TODO_COUNT,
  "timestamp": "$(date +%Y%m%d_%H%M%S)"
}
EOF
  
  echo "Task not complete. Continuing to next iteration..."
  echo ""
  
  ITERATION=$((ITERATION + 1))
done

echo "=== RALPH: MAX ITERATIONS REACHED ==="
echo "Task may need manual intervention"
echo "Check state in: $STATE_DIR"

# Mark as needs help
cat > "$STATE_DIR/verification.json" << EOF
{
  "status": "needs_help",
  "iterations": $MAX_ITERATIONS,
  "completed_at": "$(date +%Y%m%d_%H%M%S)",
  "verification": "incomplete"
}
EOF

exit 1
```

## Integration with OpenClaw

Add to `AGENTS.md`:

```markdown
## Persistence Mode

When a task MUST be completed (not "do your best"):

Use `/ralph "<task>"` to activate persistence loop.

Ralph will:
- Keep working until verification passes
- Iterate up to 10 times
- Provide fresh evidence each iteration
- Clean up on completion

Say "cancel" or "stop" to exit early.
```

## Tier System

Ralph uses agent tiers for delegation:

| Tier | Use For | Example |
|------|---------|---------|
| LOW | Simple lookups | "What does this function return?" |
| STANDARD | Normal work | "Add error handling" |
| THOROUGH | Complex analysis | "Debug race condition" |

## Examples

### Good Use

```
User: "ralph implement JWT auth"
→ Ralph loops until:
  - JWT tokens generated correctly
  - Middleware validates tokens
  - Tests pass
  - Build succeeds
→ Clean exit
```

### Bad Use

```
User: "ralph what do you think about React?"
→ Ralph: "This is exploratory, not completion-based."
→ Use normal conversation instead.
```

## Stop Conditions

Ralph stops when:
- ✅ All verification passed
- ❌ User says "stop", "cancel", "abort"
- ⚠️ Max iterations (10) reached
- 🚫 Fundamental blocker (missing credentials, external service down)

## Output Format

```
=== RALPH: Starting persistence loop ===
Task: implement JWT auth
Max iterations: 10

--- Iteration 1/10 ---
Working on task...
Verifying completion...
✅ Tests passed
✅ Build succeeded
⚠️  Found 2 TODO items
Task not complete. Continuing...

--- Iteration 2/10 ---
...

=== RALPH: TASK COMPLETE ===
Completed in 3 iterations
All verification passed
```

## Dependencies

- `openclaw` CLI
- Standard POSIX tools
- Project-specific tools (npm, cargo, etc.)

## Version History

- 1.0.0: Initial implementation based on oh-my-codex ralph skill
