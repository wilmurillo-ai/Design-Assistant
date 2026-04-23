# Agent CI Examples

Real-world workflow examples from production deployments.

## Example 1: Documentation/Code Alignment

**Problem:** Docstrings drift from implementation as code evolves.

**Traditional approach:** Manual audits (slow, incomplete coverage).

**Agent CI approach:** Continuous validation on every PR.

### Workflow Definition

```yaml
name: Doc/Code Alignment Check
on:
  pull_request:
    paths:
      - 'src/**/*.py'
      - 'lib/**/*.ts'

permissions: read

safe-outputs:
  create-pull-request:
    title-prefix: "[docs] "
    branch-prefix: "doc-fix/"
    labels: ["documentation", "auto-fix"]
    draft: false
```

### Agent Instructions

```markdown
Analyze all modified functions in this PR:

1. Read the function's docstring/comments
2. Read the implementation
3. Identify mismatches:
   - Parameters added/removed but docs unchanged
   - Return type changed but docs unchanged
   - Behavior changed but description stale

For each mismatch:
- Explain the divergence clearly
- Determine if code or docs should change
- Propose a concrete fix

If fixes are needed:
- Create a new PR with corrections
- Link it to the original PR
- Summarize all findings in PR description
```

### Expected Output

**Original PR:** Add caching to `fetch_user_data()`

**Agent-created PR:** `[docs] Update fetch_user_data() docstring for caching`

```diff
def fetch_user_data(user_id: str, use_cache: bool = True) -> User:
    """
-   Fetch user data from the database.
+   Fetch user data from the database with optional caching.
    
    Args:
        user_id: The user's unique identifier
+       use_cache: If True, return cached data when available (default: True)
        
    Returns:
-       User object
+       User object from database or cache
    """
```

**Impact:**
- Time saved: ~30min per PR review
- Coverage: 100% of code changes
- False positive rate: <5%

---

## Example 2: Automated Test Coverage Expansion

**Problem:** Test coverage lags behind feature development.

**Traditional approach:** Manual test writing (slow, inconsistent).

**Agent CI approach:** Daily test generation runs.

### Workflow Definition

```yaml
name: Test Coverage Expansion
on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM daily

permissions: read

safe-outputs:
  create-pull-request:
    title-prefix: "[coverage] "
    branch-prefix: "test-gen/"
    labels: ["test-coverage", "agent-generated"]
    draft: true
```

### Agent Instructions

```markdown
Daily test coverage expansion:

1. Run coverage analysis on main branch
2. Identify files with <80% coverage
3. For the top 3 files by churn (most frequently modified):
   - Analyze uncovered code paths
   - Generate Playwright/Jest tests to cover them
   - Follow existing test patterns (Page Object Model)
   - Include edge cases and error paths

4. Create a single PR with all new tests
5. In PR description:
   - List coverage increase (before/after %)
   - Explain what each test validates
   - Note any assumptions or limitations
```

### Expected Output

**PR:** `[coverage] Add tests for UserProfile.update() - 67% → 91%`

```typescript
// tests/user-profile.spec.ts

describe('UserProfile.update()', () => {
  test('should update email with valid address', async () => {
    const profile = new UserProfile({ email: 'old@example.com' });
    await profile.update({ email: 'new@example.com' });
    expect(profile.email).toBe('new@example.com');
  });

  test('should reject invalid email format', async () => {
    const profile = new UserProfile({ email: 'valid@example.com' });
    await expect(
      profile.update({ email: 'not-an-email' })
    ).rejects.toThrow('Invalid email format');
  });

  test('should preserve unchanged fields', async () => {
    const profile = new UserProfile({ name: 'Alice', email: 'alice@example.com' });
    await profile.update({ email: 'alice2@example.com' });
    expect(profile.name).toBe('Alice');
  });
});
```

**PR Description:**
```
Coverage increased: 67% → 91% (+24%)

Tests added:
- ✅ Valid email update
- ✅ Invalid email rejection
- ✅ Field preservation during partial update

Untested paths remaining:
- Concurrent update handling (race condition, rare)
```

**Impact:**
- Tests written: 1,400+ over 45 days
- Cost: ~$80 total (~$0.06/test)
- Human review time: ~5min per PR
- Coverage growth: 380 → 700+ tests

---

## Example 3: Dependency Drift Detection

**Problem:** Dependencies change behavior without major version bumps.

**Traditional approach:** Discover issues in production.

**Agent CI approach:** Daily dependency monitoring.

### Workflow Definition

```yaml
name: Dependency Drift Detector
on:
  schedule:
    - cron: '0 10 * * *'  # 10 AM daily

permissions: read

safe-outputs:
  create-issue:
    title-prefix: "[deps] "
    labels: ["dependencies", "drift-alert"]
```

### Agent Instructions

```markdown
Daily dependency drift check:

1. Install current dependencies from package.json/requirements.txt
2. For each CLI dependency:
   - Run `<tool> --help`
   - Save output to `.agent-ci/help-snapshots/<tool>.txt`
   - Diff against yesterday's snapshot
3. For each library dependency:
   - Compare exported APIs against previous version
   - Check for new methods/options
4. If changes detected:
   - Document the diff
   - Assess impact (breaking, new feature, safe)
   - Create issue with findings
```

### Expected Output

**Issue:** `[deps] @aws-sdk/client-s3 added new --metadata-directive option`

```markdown
## Dependency Drift Detected

**Package:** @aws-sdk/client-s3
**Old version:** 3.4.1
**New version:** 3.4.2
**Change type:** New feature

### What changed

New CLI option added:
```
--metadata-directive <COPY|REPLACE>
  Specifies whether to copy metadata from source or replace with new values
  (default: COPY)
```

### Impact Assessment

✅ **Safe**: Backward compatible (default preserves existing behavior)

💡 **Opportunity**: We could use REPLACE in `s3-sync.ts` to fix stale metadata issue (#1234)

### Recommendation

Consider updating `uploadWithMetadata()` to use `--metadata-directive REPLACE`.
```

**Impact:**
- Catches undocumented changes
- Prevents silent failures
- Identifies optimization opportunities

---

## Example 4: Performance Regression Detection

**Problem:** Code changes introduce subtle performance issues.

**Traditional approach:** Profiling after user complaints.

**Agent CI approach:** Continuous performance analysis.

### Workflow Definition

```yaml
name: Performance Guardian
on:
  pull_request:
    paths:
      - 'src/**/*.py'

permissions: read

safe-outputs:
  create-comment:
    only-on: pull_request
    prefix: "⚡ Performance:"
```

### Agent Instructions

```markdown
Analyze PR for performance regressions:

1. Read all modified functions
2. Check for anti-patterns:
   - Regex compiled inside loops
   - Database queries in loops (N+1)
   - Synchronous I/O in async contexts
   - Large lists copied unnecessarily
   - String concatenation in loops (use join())

3. For each issue found:
   - Quote the problematic code
   - Explain the performance impact
   - Suggest optimized alternative
   - Estimate magnitude (minor/moderate/severe)

4. Comment on PR with findings
```

### Expected Output

**Comment on PR:**

```markdown
⚡ Performance: Found 2 potential regressions

### Issue 1: Regex compiled in loop (Moderate)

**Location:** `src/parser.py:45`

```python
for line in lines:
    if re.match(r'\d{4}-\d{2}-\d{2}', line):  # ⚠️ Compiled on every iteration
        dates.append(line)
```

**Impact:** For 10,000 lines, regex compiles 10,000 times instead of once.

**Fix:**
```python
date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')  # Compile once
for line in lines:
    if date_pattern.match(line):
        dates.append(line)
```

### Issue 2: N+1 query pattern (Severe)

**Location:** `src/users.py:78`

```python
users = User.query.all()
for user in users:
    user.profile = Profile.query.filter_by(user_id=user.id).first()  # ⚠️ Query per user
```

**Impact:** For 100 users, executes 101 queries (1 + 100).

**Fix:**
```python
users = User.query.all()
profiles = {p.user_id: p for p in Profile.query.filter(
    Profile.user_id.in_([u.id for u in users])
).all()}  # Single query
for user in users:
    user.profile = profiles.get(user.id)
```
```

**Impact:**
- Catches 85% of common performance issues
- Provides fix suggestions, not just alerts
- Educates team on best practices

---

## Example 5: Translation/Localization Updates

**Problem:** English text changes, translations fall behind.

**Traditional approach:** Batch updates before releases.

**Agent CI approach:** Continuous translation PRs.

### Workflow Definition

```yaml
name: Auto-Translate on Content Change
on:
  push:
    paths:
      - 'locales/en/**/*.json'

permissions: read

safe-outputs:
  create-pull-request:
    title-prefix: "[i18n] "
    branch-prefix: "translations/"
    labels: ["localization", "auto-generated"]
```

### Agent Instructions

```markdown
When English locale files change:

1. Identify changed text keys
2. For each supported language (es, fr, de, ja, zh):
   - Translate the new/changed text
   - Preserve placeholders ({{name}}, %s, etc.)
   - Match tone and formality of existing translations
3. Create a single PR with all translations
4. In PR description:
   - List all changed keys
   - Note any translation challenges
   - Flag anything needing human review (idioms, brand terms)
```

### Expected Output

**Trigger:** Push changing `locales/en/app.json`

**PR:** `[i18n] Update translations for welcome message`

```diff
// locales/es/app.json
{
-  "welcome": "Bienvenido a nuestra aplicación"
+  "welcome": "Bienvenido a nuestra plataforma"
}

// locales/fr/app.json
{
-  "welcome": "Bienvenue dans notre application"
+  "welcome": "Bienvenue sur notre plateforme"
}
```

**PR Description:**
```
Automated translations for updated English text.

Changed keys:
- `welcome`: "app" → "platform"

Translation notes:
- Spanish: "aplicación" → "plataforma" (standard)
- French: "application" → "plateforme" (standard)
- German: "Anwendung" → "Plattform" (standard)
- Japanese: Kept respectful form (です/ます)
- Chinese: Simplified variant, formal tone

⚠️ Human review recommended for:
- Marketing pages (brand voice)
```

**Impact:**
- Translation lag: days → hours
- Coverage: 100% of text changes
- Human review for nuance, not typing

---

## Example 6: Interactive UI Testing

**Problem:** UX regressions only appear during actual interaction.

**Traditional approach:** Manual QA testing.

**Agent CI approach:** Agents as deterministic play-testers.

### Workflow Definition

```yaml
name: Onboarding Flow Regression Test
on:
  pull_request:
    paths:
      - 'src/onboarding/**'

permissions: read

safe-outputs:
  create-comment:
    only-on: pull_request
    prefix: "🎮 UX Regression:"
```

### Agent Instructions

```markdown
Test onboarding flow 100 times:

1. Start at /signup
2. Fill form with random (valid) data
3. Submit and track:
   - Steps to completion
   - Error messages encountered
   - Time to first success
   - Drop-off points
4. Compare against baseline (previous 100 runs)
5. If regressions detected:
   - Higher error rate (>10% increase)
   - New error types
   - Slower completion time (>20% increase)
   - Comment on PR with details
```

### Expected Output

**Comment on PR:**

```markdown
🎮 UX Regression: Onboarding flow degraded

### Regression Summary

Ran 100 automated user flows. Detected 2 regressions compared to baseline:

| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Success rate | 94% | 87% | -7% ⚠️ |
| Avg completion time | 42s | 38s | -4s ✅ |
| Error: "Email required" | 3% | 3% | 0% |
| Error: "Invalid password" | 2% | 9% | +7% ⚠️ |

### Issue Details

**New validation bug: Password field**

Reproduced 9/100 runs. The password field now rejects valid passwords containing special characters.

**Example failing input:**
```
Email: test@example.com
Password: SecureP@ss123!
Error: "Invalid password format"
```

**Impact:** This blocks ~9% of signups with valid passwords.

**Suggested fix:** Review password validation regex in `src/onboarding/validate.ts:23`
```

**Impact:**
- Catches interaction bugs before production
- Quantifies UX degradation
- Provides reproduction cases

---

## Lessons from Production

### What Works

✅ **Small, focused workflows** - Single-purpose agents outperform multi-taskers

✅ **Iteration limits** - Cap retries (e.g., 5x) to prevent infinite loops

✅ **Quality gates** - Hard blocks on critical issues enforce standards

✅ **Rich context** - Pass artifacts between phases for intelligent decisions

✅ **Progressive rollout** - Start with low-risk paths (docs, tests) before touching source code

### What Doesn't Work

❌ **Vague instructions** - "Make it better" fails; be specific

❌ **No human review** - Always require approval, never auto-merge

❌ **One mega-agent** - Specialization beats generalization

❌ **Ignoring cost** - Monitor token usage to avoid runaway spend

❌ **Blind trust** - Audit agent outputs, especially early on

### Cost Benchmarks

From real deployments:

| Workflow | Runs/day | Tokens/run | Cost/day |
|----------|----------|-----------|---------|
| Doc sync | 15 PRs | 5K | $0.15 |
| Test gen | 1 run | 50K | $1.50 |
| Dep drift | 1 run | 8K | $0.08 |
| Perf check | 20 PRs | 3K | $0.60 |

**Total:** ~$2.33/day (~$70/month) for continuous quality automation.

---

**Bottom line:** Start with one high-value workflow, validate it works, then expand. Don't try to automate everything at once.
