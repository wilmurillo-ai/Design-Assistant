# Skill Authoring Best Practices Reference

> Source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

## Table of Contents

- [1. Conciseness](#1-conciseness)
- [2. Appropriate Freedom](#2-appropriate-freedom)
- [3. YAML Frontmatter](#3-yaml-frontmatter)
- [4. Naming Conventions](#4-naming-conventions)
- [5. Effective Descriptions](#5-effective-descriptions)
- [6. Progressive Disclosure](#6-progressive-disclosure)
- [7. Writing Style](#7-writing-style)
- [8. Workflows and Feedback Loops](#8-workflows-and-feedback-loops)
- [9. Content Guidelines](#9-content-guidelines)
- [10. Common Patterns](#10-common-patterns)
- [11. Executable Code in Skills](#11-executable-code-in-skills)
- [12. Anti-Patterns to Avoid](#12-anti-patterns-to-avoid)
- [13. Evaluation and Iteration](#13-evaluation-and-iteration)

---

## 1. Conciseness

The context window is a shared resource. A skill competes with the system prompt, conversation history, other skill metadata, and the actual request.

**Default assumption: Claude is already very smart.**

Question every piece of information:
- "Does Claude really need this explanation?"
- "Can this be assumed as common knowledge?"
- "Does this content justify its token cost?"

**Good** (~50 tokens):
```markdown
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

**Bad** (~150 tokens) — Explains what PDFs are, what libraries exist, and why pdfplumber is chosen before showing code. Claude already knows all of this.

---

## 2. Appropriate Freedom

Match specificity level to the task's fragility and variability.

| Freedom Level | When to Use | Example |
|---|---|---|
| **High** (text instructions) | Multiple valid approaches; context-dependent decisions | Code review process |
| **Medium** (pseudocode / parameterized scripts) | Preferred patterns exist; some variation allowed | Report generation |
| **Low** (specific scripts, few/no params) | Brittle operations; consistency critical; strict ordering | Database migrations |

**Analogy:** Treat Claude as a robot navigating a path.
- Narrow bridge with cliffs on both sides → precise guardrails (low freedom)
- Open field with no dangers → general direction is enough (high freedom)

---

## 3. YAML Frontmatter

Two required fields in SKILL.md frontmatter:

**`name`:**
- Max 64 characters
- Lowercase letters, digits, and hyphens only
- No XML tags
- No reserved words: "anthropic", "claude"

**`description`:**
- Non-empty
- Max 1024 characters
- No XML tags
- Describes what the skill does AND when to use it

---

## 4. Naming Conventions

Prefer **gerund form** (verb + -ing):
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `testing-code`
- `writing-documentation`

Acceptable alternatives:
- Noun phrases: `pdf-processing`, `spreadsheet-analysis`
- Action-oriented: `process-pdfs`, `analyze-spreadsheets`

Avoid:
- Vague: `helper`, `utils`, `tools`
- Overly generic: `documents`, `data`, `files`
- Reserved: `anthropic-helper`, `claude-tools`

---

## 5. Effective Descriptions

The description field drives skill discovery.

**Always use third person:**
- ✅ "Processes Excel files and generates reports"
- ❌ "I can help you process Excel files"
- ❌ "You can use this to process Excel files"

**Be specific and include key terms:**

Good examples:
```yaml
# PDF Processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# Excel Analysis
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

---

## 6. Progressive Disclosure

Three-level loading system:

1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — loaded when skill triggers (<5k words)
3. **Bundled resources** — loaded as needed by Claude (unlimited*)

*Unlimited because scripts can execute without loading into context.

**Practical guidance:**
- Keep SKILL.md body under 500 lines
- Near the limit → split content into separate files

**Pattern 1: High-level guide + references**
```markdown
## Quick start
[core instructions]

## Advanced features
**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
```

**Pattern 2: Domain-specific organization**
Organize by domain to avoid loading irrelevant context.

**Pattern 3: Conditional detail**
Show basics inline, link to advanced content.

**Avoid deep nesting** — References should be one level deep from SKILL.md.

**Table of contents** — For reference files over 100 lines, include a TOC at the top.

---

## 7. Writing Style

- Use **imperative/infinitive form** (verb-first instructions)
- Avoid second person ("you should")
- Use objective, instructional language
  - ✅ "To accomplish X, do Y"
  - ❌ "You should do X"
  - ❌ "If you need to do X"

---

## 8. Workflows and Feedback Loops

### Complex Task Workflows
Break complex operations into clear sequential steps. For particularly complex workflows, provide a checklist:

```markdown
## Research synthesis workflow

Copy this checklist and track progress:

```
Research Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Verify citations
```
```

### Feedback Loops
The pattern: **run validator → fix errors → repeat**

This pattern significantly improves output quality for any skill that produces verifiable artifacts.

---

## 9. Content Guidelines

### Avoid Time-Sensitive Information
Do not include information that will become outdated. If historical context is necessary, use a "Legacy Notes" section.

### Use Consistent Terminology
Pick one term and use it throughout the entire skill. Do not alternate between synonyms.

---

## 10. Common Patterns

### Template Pattern
Provide templates for output formats. Match strictness to requirements:
- **Strict** (API responses, data formats): exact template structure
- **Flexible** (general guidance): reasonable defaults, adjust as needed

### Example Pattern
When output quality depends on seeing examples, provide input/output pairs.

### Conditional Workflow Pattern
Guide Claude through decision points with clear branching logic.

---

## 11. Executable Code in Skills

### Solve, Don't Punt
Handle errors explicitly instead of deferring to Claude:

```python
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, "w") as f:
            f.write("")
        return ""
```

### Utility Scripts Are Worth It
Even though Claude can write scripts, pre-made scripts provide:
- Higher reliability than generated code
- Token savings
- Time savings
- Cross-use consistency

### Plan-Verify-Execute Pattern
Create a plan in structured format → validate with script → execute. Catches errors early.

### Package Dependencies
- **claude.ai**: Can install from npm/PyPI and pull from GitHub
- **Claude API**: No network access, no runtime package installation

### MCP Tool References
Always use fully qualified tool names: `ServerName:tool_name`

---

## 12. Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|---|---|
| Windows-style paths (`scripts\helper.py`) | Use forward slashes (`scripts/helper.py`) |
| Too many options for one task | Show one recommended approach |
| Assuming tools are installed | Explicitly list dependencies and verify availability |
| "Voodoo constants" in scripts | Document the reasoning for every magic value |
| Deep reference nesting | Keep references one level from SKILL.md |
| Explaining things Claude knows | Remove; assume intelligence |
| Inconsistent terminology | Pick one term, use it everywhere |

---

## 13. Evaluation and Iteration

### Evaluation-Driven Development
1. Identify gaps: Run Claude on representative tasks without the skill. Record specific failures
2. Create evaluations: Build three scenarios testing those gaps
3. Establish baseline: Measure Claude's performance without the skill
4. Write minimal instructions: Create just enough to address gaps and pass evaluations
5. Iterate: Run evaluations, compare with baseline, refine

### Iterating with Claude
1. Complete a task without the skill
2. Identify reusable patterns
3. Have Claude A create the skill
4. Check conciseness
5. Improve information architecture
6. Test on similar tasks
7. Iterate based on observations

### Observe Navigation Patterns
Watch how Claude actually uses the skill in practice. Note which sections it reads, which it skips, and where it gets confused.
