# Safe Outputs - Permission Models for Agent CI

Comprehensive guide to defining what agents are allowed to do in your repository.

## Core Principle

**Agents operate with read-only access by default.** They cannot create issues, open pull requests, or modify content unless explicitly permitted.

This is intentional: agents can fail or behave unexpectedly. Outputs must be sanitized, permissions explicit, and all activity logged. The blast radius is deterministic.

## Safe Output Types

### 1. Pull Requests

**Most common output.** PRs align with how developers already review and reason about change.

**Configuration:**
```yaml
safe-outputs:
  create-pull-request:
    title-prefix: "[auto] "           # Required: mark agent PRs
    branch-prefix: "agent-ci/"        # Optional: organize branches
    base-branch: "main"               # Optional: default PR target
    auto-assign: ["qa-team"]          # Optional: reviewers
    labels: ["agent-generated"]       # Optional: apply labels
    draft: true                       # Optional: create as draft
```

**Constraints:**
- Agents cannot merge PRs (developers retain control)
- Title prefix makes agent PRs instantly recognizable
- Draft mode prevents accidental merges

**Example:**
```yaml
safe-outputs:
  create-pull-request:
    title-prefix: "[docs] "
    branch-prefix: "doc-sync/"
    labels: ["documentation", "auto-fix"]
    draft: false
```

When agent detects doc/code mismatch, it opens:
```
PR: [docs] Fix docstring for calculate_total()
Branch: doc-sync/calculate-total-20260319
Labels: documentation, auto-fix
```

### 2. Issues

**Best for alerts, reports, and findings that don't require immediate code changes.**

**Configuration:**
```yaml
safe-outputs:
  create-issue:
    title-prefix: "[alert] "
    labels: ["agent-report"]
    assign: ["team-lead"]
    close-stale: 7d                   # Auto-close if unaddressed
```

**Use cases:**
- Daily status reports
- Dependency drift alerts
- Performance regression warnings
- Test coverage gaps

**Example:**
```yaml
safe-outputs:
  create-issue:
    title-prefix: "[coverage] "
    labels: ["test-coverage", "agent"]
    assign: ["qa-lead"]
```

Creates:
```
Issue: [coverage] New feature missing E2E tests
Labels: test-coverage, agent
Assigned: qa-lead
```

### 3. Comments

**Contextual feedback on existing PRs or issues.**

**Configuration:**
```yaml
safe-outputs:
  create-comment:
    only-on: pull_request            # Only comment on PRs
    prefix: "🤖 Agent CI:"           # Mark agent comments
    max-per-target: 3                # Prevent spam
```

**Use cases:**
- PR audit results
- Test failure diagnosis
- Code review suggestions

**Constraints:**
- Cannot edit or delete existing comments
- Cannot comment on locked threads
- Rate-limited to prevent spam

**Example:**
```yaml
safe-outputs:
  create-comment:
    only-on: pull_request
    prefix: "🛡️ Sentinel:"
```

Comments on PR:
```
🛡️ Sentinel: Found 2 critical issues:
1. Raw selector in test code (line 45)
2. Missing await on async operation (line 67)
```

### 4. Discussions

**Long-form communication or proposals that don't fit issues/PRs.**

**Configuration:**
```yaml
safe-outputs:
  create-discussion:
    category: "Agent Reports"
    title-prefix: "[weekly] "
```

**Use cases:**
- Weekly activity summaries
- Architectural proposals
- Long-form analysis

**Example:**
```yaml
safe-outputs:
  create-discussion:
    category: "Quality Reports"
    title-prefix: "[analysis] "
```

### 5. File Modifications (High Risk)

**Rarely used.** Most changes should go through PRs.

**Configuration:**
```yaml
safe-outputs:
  modify-files:
    allowed-paths:
      - "docs/**/*.md"
      - "tests/**/*.spec.ts"
    forbidden-paths:
      - "src/**"                      # Never touch source code
      - ".github/**"                  # Never touch CI config
    require-pr: true                  # Force PR even for allowed paths
```

**Use with extreme caution.** Direct file modification bypasses review.

**Safer alternative:** Use `create-pull-request` instead.

## Permission Scopes

Define granular access:

```yaml
permissions:
  read: true                          # Read repo contents
  issues: write                       # Create/edit issues
  pull-requests: write                # Create PRs
  discussions: write                  # Create discussions
  actions: read                       # Read workflow runs
```

**Principle of least privilege:** Grant only what's needed.

### Read-Only (Safest)
```yaml
permissions:
  read: true
safe-outputs:
  create-issue:
    title-prefix: "[report] "
```

Agent can analyze but only report findings via issues.

### PR-Only (Common)
```yaml
permissions:
  read: true
  pull-requests: write
safe-outputs:
  create-pull-request:
    title-prefix: "[auto] "
```

Agent can create PRs for fixes but cannot merge.

### Full Write (Use Sparingly)
```yaml
permissions:
  read: true
  issues: write
  pull-requests: write
  discussions: write
safe-outputs:
  create-pull-request:
    title-prefix: "[auto] "
  create-issue:
    title-prefix: "[alert] "
```

Agent can create multiple artifact types.

## Output Sanitization

All agent outputs must be sanitized before publishing.

### Dangerous Content to Filter

**Secrets/Credentials:**
```yaml
sanitize:
  patterns:
    - regex: "sk-[a-zA-Z0-9]{32}"    # OpenAI keys
    - regex: "ghp_[a-zA-Z0-9]{36}"   # GitHub tokens
    - regex: "AIza[a-zA-Z0-9_-]{35}" # Google API keys
  replace: "[REDACTED]"
```

**Sensitive Paths:**
```yaml
sanitize:
  paths:
    - "/home/user/**"
    - "**/.env"
    - "**/secrets/**"
  action: abort                       # Abort if detected
```

**PII (Personal Identifiable Information):**
```yaml
sanitize:
  pii:
    - emails: true
    - phone-numbers: true
    - ip-addresses: true
```

### Example: Comprehensive Sanitization
```yaml
safe-outputs:
  create-pull-request:
    title-prefix: "[auto] "
    sanitize:
      secrets: true
      pii: true
      paths:
        forbidden: ["**/.env", "**/secrets/**"]
      patterns:
        - regex: "password=.*"
          replace: "password=[REDACTED]"
```

## Audit Trail

Every agent action must be logged for debugging and compliance.

**Minimum log fields:**
- Timestamp
- Agent ID
- Action type (create-pr, create-issue, etc.)
- Target (repo, PR number, etc.)
- Input (what triggered the action)
- Output (what was created/modified)
- Status (success, failed, blocked)

**Example log:**
```json
{
  "timestamp": "2026-03-19T16:30:00Z",
  "agent_id": "doc-sync-agent",
  "action": "create-pull-request",
  "target": "org/repo",
  "input": {
    "trigger": "pull_request",
    "pr_number": 1234,
    "files_changed": ["src/utils.py"]
  },
  "output": {
    "pr_number": 1235,
    "branch": "doc-sync/utils-fix",
    "title": "[docs] Fix docstring for calculate_total()"
  },
  "status": "success"
}
```

**Retention:** Keep logs for at least 90 days for compliance.

## Rate Limiting

Prevent agents from spamming your repository.

### Per-Agent Limits
```yaml
rate-limits:
  agent: doc-sync
  max-prs-per-day: 10
  max-issues-per-day: 5
  max-comments-per-pr: 3
```

### Global Limits
```yaml
rate-limits:
  global:
    max-prs-per-hour: 20
    max-issues-per-hour: 10
```

**Behavior on limit hit:**
- Queue excess actions for next period
- OR abort and log warning
- Never silently drop actions

## Rollback & Emergency Stop

### Emergency Stop
```yaml
emergency-stop:
  enabled: true
  trigger-file: ".agent-ci-stop"      # Create this file to halt all agents
  webhook: "https://alerts.example.com/agent-stop"
```

When `.agent-ci-stop` exists in repo root, all agents pause immediately.

### Rollback
```yaml
rollback:
  enabled: true
  max-age: 24h                        # Only rollback recent changes
  require-approval: true              # Human must approve rollback
```

Rollback actions:
- Close agent-created PRs
- Delete agent-created issues/discussions
- Revert commits (if any)

## Security Boundaries

### Never Allow

❌ **Merging PRs** - Developers must review and merge

❌ **Deleting branches/tags** - Permanent data loss risk

❌ **Modifying CI/CD config** - Could compromise entire pipeline

❌ **Accessing secrets** - Agents should never read credentials

❌ **Publishing releases** - Human oversight required

❌ **Modifying security settings** - Could weaken protections

### Require Extra Approval

⚠️ **Modifying source code** - Even in PRs, flag for senior review

⚠️ **Changing dependencies** - Security implications

⚠️ **Altering database schemas** - Data integrity risk

⚠️ **Updating documentation in /docs** - Brand/legal implications

## Implementation Examples

### GitHub Actions
```yaml
name: Agent CI - Doc Sync
on: pull_request

jobs:
  doc-sync:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      
    steps:
      - uses: actions/checkout@v3
      
      - name: Run doc-sync agent
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          agent-ci run \
            --agent doc-sync \
            --safe-outputs create-pull-request \
            --title-prefix "[docs] " \
            --sanitize secrets,pii
```

### OpenClaw Cron
```json
{
  "name": "Daily test coverage expansion",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Analyze uncovered code paths, generate tests, open PR with [coverage] prefix."
  },
  "delivery": { "mode": "announce" },
  "sessionTarget": "isolated",
  "safeOutputs": {
    "createPullRequest": {
      "titlePrefix": "[coverage] ",
      "branchPrefix": "test-gen/",
      "labels": ["test-coverage", "agent-generated"],
      "draft": true
    }
  }
}
```

### GitLab CI
```yaml
test-healer:
  stage: test
  script:
    - agent-ci heal-tests --safe-outputs create-merge-request
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
  artifacts:
    reports:
      agent_audit: agent-ci-audit.json
```

## Monitoring & Alerts

Track agent behavior over time:

**Metrics to monitor:**
- PRs/issues created per day
- Merge rate of agent PRs
- Time-to-merge for agent PRs
- Failed sanitization attempts (critical!)
- Rate limit hits
- Emergency stops triggered

**Alert on:**
- Sanitization failures (potential secret leak)
- Sudden spike in agent activity (possible malfunction)
- Repeated PR failures (agent needs tuning)
- Low merge rate (agent output quality issue)

**Dashboard example:**
```
Agent CI Health
├─ Doc Sync Agent
│  ├─ PRs created: 45 (last 7d)
│  ├─ Merge rate: 89%
│  ├─ Avg time-to-merge: 4.2h
│  └─ Rate limits: 0 hits
├─ Test Coverage Agent
│  ├─ PRs created: 12 (last 7d)
│  ├─ Merge rate: 100%
│  ├─ Avg time-to-merge: 2.1h
│  └─ Rate limits: 0 hits
└─ Alerts: 0
```

## Best Practices

✅ **Start restrictive:** Begin with read-only + create-issue, expand as trust builds

✅ **Prefix everything:** Make agent outputs instantly recognizable

✅ **Require review:** Never auto-merge agent PRs

✅ **Sanitize by default:** Assume agents might leak secrets

✅ **Log everything:** Audit trails are critical for debugging

✅ **Rate limit:** Prevent runaway agent behavior

✅ **Test in sandbox:** Validate safe-output configs on test repos first

✅ **Emergency stop:** Always have a kill switch

---

**Remember:** Safe outputs are about trust through constraints. Agents are powerful when bounded by clear, enforceable rules.
