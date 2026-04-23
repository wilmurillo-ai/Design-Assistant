# Improvement Examples — Real Patterns from Skill Garden

> These are examples of actual improvements the system has made or would make, with the full context of what changed and why.

---

## Example 1: Expanding Coverage (Confidence: 88%)

**Skill:** `github-trending-summary`
**Before description:**
```yaml
description: "Scrape GitHub trending top 5 repos and send summary email."
```
**After description:**
```yaml
description: "Scrape GitHub trending top 5 repos via GitHub Search API (NOT direct page scrape — page is JS-rendered) and send summary email. Use when user says 'github trending', '今日热门项目', '爬 GitHub trending', or 'GitHub trending 总结'. Supports custom language filters and sorting by stars."
```
**Evidence from logs:**
```
## 2026-04-07 10:30
Trigger: github-trending-summary: morning top 5
Outcome: FAIL
Signal: Missing: language filter not implemented
Evidence: User asked for "今日热门项目" but skill didn't know to use "language:python" filter.

## 2026-04-10 09:15
Trigger: github-trending-summary: top JS repos
Outcome: PARTIAL
Signal: Missing: star sort order not configurable
Evidence: Skill always returns by date, user wanted by stars.
```

**What changed:** Description now explicitly mentions it uses Search API (not page scrape), language filters, and star sorting. Also added Chinese trigger phrases since that's what the user actually says.

**Confidence rationale:** 2 [new_trigger] flags → 80–84% confidence. Applying with [experimental] tag since some ambiguity in whether these are truly new use cases vs. phrasings of existing ones.

---

## Example 2: Adding Error Handling (Confidence: 95%)

**Skill:** `banxuebang-helper`
**Before (missing step in SKILL.md):**
```markdown
## Check Unfinished Homework

1. Load token from `.token.json`
2. Call `/homework/unfinished` endpoint
```
**After (with error handling added):**
```markdown
## Check Unfinished Homework

1. Load token from `.token.json`
   - If file missing → run `banxuebang-helper signin` first
2. Call `/homework/unfinished` endpoint
   - If 401 Unauthorized → token expired, run `banxuebang-helper signin`
   - If 429 Rate Limited → wait 60s and retry once
   - If empty array → no unfinished homework (this is a valid OK outcome)
```
**Evidence from logs:**
```
## 2026-04-15 14:20
Trigger: banxuebang-helper: check homework
Outcome: FAIL
Signal: Missing: no handling for 401 expired token
Evidence: API returned {"code": 401, "msg": "token expired"}. No recovery step documented.

## 2026-04-16 08:45
Trigger: banxuebang-helper: check homework
Outcome: FAIL
Signal: Missing: no handling for 429 rate limit
Evidence: API returned 429 after 10 rapid sign-in attempts. Skill hung indefinitely.
```

**What changed:** Added explicit error handling branches for 401 and 429 responses, and noted that empty array is valid (not an error).

**Confidence rationale:** 2 [missing_coverage] + 1 [config_stale] → completeness 80%, currency 70%. Config fix: [config_stale] with exact wrong value identified → 92% confidence. Error handling: 2 [missing_coverage] flags with clear error codes → 88% confidence.

---

## Example 3: Improving Clarity of a Step (Confidence: 76%)

**Skill:** `apple-notes`
**Before step:**
```markdown
### Creating a Note

1. Use the `memo` CLI to create the note
2. Specify the folder with `-f` flag
```
**After step:**
```markdown
### Creating a Note

1. Create the note using `memo new "note title"` (title is required, must be quoted if it contains spaces)
2. Specify the folder with `-f "folder name"` (folder name is optional; if omitted, defaults to first available folder)
3. The note body is entered interactively OR via pipe: `echo "content" | memo new "title"`

⚠️ Common mistake: forgetting to quote the folder name when it contains spaces (`-f "My Folder"` not `-f My Folder`)
```
**Evidence from logs:**
```
## 2026-04-18 16:00
Trigger: apple-notes: create note in Personal
Outcome: FAIL
Signal: Confusing step: -f flag format unclear
Evidence: User tried `-f Personal` without quotes. Command failed. Error: "flag expects quoted string".

## 2026-04-19 10:30
Trigger: apple-notes: new note via pipe
Outcome: FAIL
Signal: Missing coverage: pipe input not documented
Evidence: User tried `echo "hello" | memo new "test"` but it opened interactive mode instead.
```

**What changed:** Step rewritten with explicit quoting rules, pipe example, and a warning about the most common mistake. Separated the `-f` flag into its own line with full explanation.

**Confidence rationale:** 2 [confusing_step] flags → 80–84% confidence. Fix addresses both directly.

---

## Example 4: Removing Token Bloat (Confidence: 82%)

**Skill:** `ppt-generator`
**Before (verbose opening section):**
```markdown
# PPT Generator Skill

This skill helps you create beautiful, professional PowerPoint-style HTML presentations
using the latest modern web technologies. Whether you need to present quarterly results,
explain a complex technical concept, or create a stunning visual showcase, this skill
will help you build presentation-ready HTML files that can be opened in any modern browser...

[80 more words of preamble before getting to the actual workflow]
```
**After (condensed opening):**
```markdown
# PPT Generator

Creates minimal, professional, Jobs-style vertical HTML presentations.

**Output:** Single `.html` file, opens in any browser, mobile-optimized.

**When to use:** User says "生成PPT", "演示", "slides", "乔布斯风", or similar.

See workflow below.
```
**Evidence from logs:**
```
## 2026-04-12 11:00
Trigger: ppt-generator: quarterly汇报
Outcome: OK
Signal: Token heavy: verbose intro causes slow first token
Evidence: First meaningful output arrived 8 seconds after skill was invoked.
         Skimmed through 80-word preamble before reaching instructions.

## 2026-04-14 09:30
Trigger: ppt-generator: tech demo slides
Outcome: OK
Signal: Token heavy: same preamble scanned before work started
Evidence: Token count for skill context included 80+ words of intro material
         that provided no procedural value.
```

**What changed:** Replaced verbose intro (80+ words) with a 3-line summary. Moved detail about "how it works" to a footnote reference. No loss of functionality.

**Confidence rationale:** 2 [token_heavy] flags → 81% confidence. Direct trim, no ambiguity.

---

## Example 5: Fixing Stale Configuration (Confidence: 97%)

**Skill:** `banxuebang-helper`
**Before (hardcoded semester):**
```python
CURRENT_SEMESTER = "2024-2025下学期"
```
**After (dynamic detection):**
```python
from datetime import datetime
year = datetime.now().year
month = datetime.now().month
# Academic year: Aug-Jan is "上学期", Feb-Jul is "下学期"
academic_year = year if month >= 8 else year - 1
semester_type = "上学期" if month >= 8 or month <= 1 else "下学期"
CURRENT_SEMESTER = f"{academic_year}-{academic_year+1}{semester_type}"
```
**Evidence from logs:**
```
## 2026-04-07 08:00
Trigger: banxuebang-helper: check homework
Outcome: FAIL
Signal: Config stale: hardcoded semester wrong for current date
Evidence: Config has "2024-2025下学期" but today is 2026-04-07. API returns empty.
         Current actual semester is "2025-2026下学期".

## 2026-04-07 08:05
Trigger: banxuebang-helper: check homework
Outcome: FAIL
Signal: Same issue: stale semester config
Evidence: Same failure, same root cause.
```

**What changed:** Replaced hardcoded string with dynamic calculation based on current date and academic year logic. Skill now always uses the correct semester.

**Confidence rationale:** 2 [config_stale] flags with identical error message, exact wrong value named, correct value identified → 95% confidence. Auto-applied.

---

## Example 6: A Proposal That Stayed a Proposal (Confidence: 63%)

**Skill:** `daily-song-recommender`
**Proposed change:** Add support for genre preference memory (remember what genres user liked before)
**Evidence:**
```
## 2026-04-20 19:00
Trigger: daily-song-recommender: recommend jazz
Outcome: OK
Signal: Missing: no genre preference memory
Evidence: User asked for jazz. Previous 3 sessions also asked for jazz.
         Skill has no mechanism to remember this preference across sessions.
```
**Decision:** Confidence 63% — wrote to proposals file, flagged for user review.
**User decision (hypothetical):** "Yes, add this — it's been frustrating having to repeat my taste every time"

**What would have changed:** SKILL.md gets a new section:
```markdown
## Remembering Preferences

If user mentions a genre preference (e.g., "I like jazz", "偏好古典"),
write it to `memory/song_preferences.md` with timestamp.
On future song requests, check this file first and prioritize the stored preference.
```
