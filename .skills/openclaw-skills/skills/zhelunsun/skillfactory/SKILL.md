---
name: skill-factory
version: "2.2.1"
description: >
  A meta-skill for creating, iterating, and publishing OpenClaw skills from scratch.
  Use this skill when the user wants to: build a new skill from an idea or URL, upgrade
  an existing skill with new sources, prepare a skill for GitHub publishing, or design
  a skill's repo structure. Triggers include: "新 skill", "做一个skill", "build a skill",
  "create skill", "skill制作", "把这个做成skill", "帮我把...打包成skill", "skill升级",
  "skill发行", "skill factory", "制造skill", "skill工厂", "skill from scratch",
  "我有个skill想法", "skill迭代", "skill打磨", "做一个关于...的skill",
  "skill版本管理", "skill如何发行", "skill如何升级", "skill生产", "skill自动化".
---

# Skill Factory — The Meta-Skill for Making Skills

> "The first industrial revolution was marked by using machines to make machines.
> Skill Factory is the machine that makes skills."

## Purpose

Skill Factory provides a **repeatable, human-AI collaborative SOP** for going from a raw idea to a polished, publishable OpenClaw skill. It handles:

- **0→1**: Rapid capture of fuzzy ideas → structured BRIEF → distilled skill
- **1→N**: Iterating an existing skill with new sources or structural improvements
- **N→∞**: Publishing, versioning, ClawHub distribution, and ongoing maintenance

The key insight: **this is not about capability, it's about workflow.** Any Claw instance with this skill loaded can build production-quality skills — the process is the product.

---

## How to Trigger This Skill

Just say something like:

> `New skill: [name], [1-2 sentences], [source URL (optional)]`

Examples:
- `New skill: prompt-engineering, best practices from Anthropic and OpenAI`
- `New skill: git-workflow, standardize my branching and PR flow, https://...`
- `Skill upgrade: nova-reader, add Semantic Scholar data source`

Claw will immediately enter **Phase 0** — no more information needed to start.

**中文用户**: `新 skill：[名字]，[1-2句说明]，[来源URL（可选）]`

---

## Four-Phase SOP

### Phase 0 · Capture（≤5 min）

**Goal**: Lock down the spec before any work begins.

1. Save raw idea to `inbox/<skill-name>.md` 
2. Ask exactly **3 questions** — no more:
   - What is the target scenario / user?
   - Are there reference sources? (If not, Claw will search)
   - Publish scope: local-only / GitHub / ClawHub distribution?
3. Generate `wip/<skill-name>/BRIEF.md`

**Key principle**: Phase 0 prevents over-engineering (LRN-003). Don't start building until the 3 questions are answered.

---

### Phase 1 · Collect（automated）

**Goal**: Gather raw material without processing.

1. `web_fetch` each source → save to `wip/<skill-name>/raw/`
2. If no sources provided, `web_search` for 2–3 high-quality references
3. Prioritize: official docs > primary blog posts > secondary analysis

**Rule**: At least 1 first-party source (official docs / original author's post). Raw content is saved as-is — no processing yet.

---

### Phase 2 · Distill（core work）

**Goal**: Extract signal, discard noise.

1. Read all `raw/` files
2. Write per skill-creator spec:
   - `SKILL.md` — triggers + workflow (≤200 lines)
   - `references/` — detailed knowledge, split by topic
   - `scripts/` — reusable code, only if needed
3. **Mandatory verification** (LRN-001): Re-fetch original source, diff against draft, check for gaps

**Quality checklist**:
- [ ] Trigger words are broad enough to cover all user phrasings
- [ ] SKILL.md has a clear "when to use" section
- [ ] Detail lives in `references/`, not bloating `SKILL.md`
- [ ] At least one mandatory re-read of primary source after distillation

---

### Phase 3 · Publish

**Goal**: Clean, versioned, standalone repo ready for GitHub/ClawHub.

#### Repo Structure (Minimal)

```
<skill-name>/
├── SKILL.md          # Entry point (triggers + workflow)
├── README.md         # Human-facing intro — bilingual (EN + ZH)
├── CHANGELOG.md      # Version history
├── LICENSE           # MIT recommended
├── .gitignore
└── references/       # Knowledge base
    └── *.md
```

For script-heavy skills, add:
```
└── scripts/
    └── *.py
```

#### README Spec

A skill README must answer 3 questions in ≤60 seconds of reading:
1. **What problem does it solve?** (1-2 sentences, no jargon)
2. **What makes it better than asking without it?** (key differentiator)
3. **How do I use it?** (one concrete example)

**Bilingual (EN + ZH)**: Use two separate files for maximum clarity.

```
README.md       # English only — no Chinese text anywhere
README_zh.md    # Chinese only — full detail, selling points, usage
```

Each file includes a badge linking to the other version. This allows GitHub to render clean language-specific views and enables future ClawHub to surface the right version per locale.

#### ClawHub Distribution

When the user wants to publish to ClawHub:
1. Ensure `SKILL.md` frontmatter has: `name`, `version`, `description`
2. `description` must contain broad trigger phrases covering multiple phrasings
3. `LICENSE` file present (MIT recommended)
4. Tag the release: `git tag v1.0.0 && git push --tags`

#### Sync to Local Workspace

After publishing, sync to `~/.workbuddy/skills/<skill-name>/` so Claw can use it immediately:

```powershell
Copy-Item -Recurse -Force "D:\WorkBuddy\<skill-name>\*" "$env:USERPROFILE\.workbuddy\skills\<skill-name>\"
```

---

## Version Management

Version semantics follow **Semantic Versioning** adapted for skills:

```
MAJOR.MINOR.PATCH
```

| Version bump | When | Example trigger |
|---|---|---|
| **PATCH** `x.x.1` | Typo fix, trigger word tweak, minor clarification | "修复了一个例子描述不准" |
| **MINOR** `x.1.0` | New reference source, new phase step, extended trigger coverage | "加入 Anthropic 最新文档" |
| **MAJOR** `2.0.0` | Scope change, structural refactor, paradigm shift | "从单文档改为多 reference 结构" |

### What warrants a MAJOR bump?

A MAJOR version (e.g. 1.x → 2.0) signals a **breaking change in the skill's mental model**:
- The core SOP phases are restructured
- The skill's scope is fundamentally redefined
- Files are reorganized in ways that break the previous structure
- The activation paradigm changes (e.g. from "ask anything" to "four-phase SOP")

**MAJOR ≠ more content**. A skill that doubles its references but keeps the same structure is still a MINOR bump.

### What warrants a MINOR bump?

A MINOR version (e.g. 1.0 → 1.1 → 1.2) signals **additive improvements** that don't break the existing pattern:
- New knowledge source added to `references/`
- New trigger words added to frontmatter
- New section added to SOP without restructuring existing phases
- README improvements, badge updates

### Commit message convention

```
feat: add [source] to references        → MINOR
fix: correct [description]              → PATCH
refactor: restructure [component]       → could be MAJOR
release: v2.0.0 - [summary]            → tag release commits
```

### Changelog discipline

Every release must update `CHANGELOG.md` with:
- Version number + date
- Summary sentence (1 line)
- Added / Changed / Fixed sections

---

## Skill Iteration (1→N)

When upgrading an existing skill:

1. Create a new branch or directly update `D:/WorkBuddy/<skill-name>/`
2. Add new source to `references/` with dated filename (`source-YYYYMMDD.md`)
3. Update `SKILL.md` version field and trigger words if needed
4. Update `CHANGELOG.md`
5. Bump version (MAJOR / MINOR / PATCH per rules above)
6. Commit with semantic message
7. Re-sync to local workspace

**Upgrade triggers**: User sends new URL, user says "skill has a gap", Claw detects missing knowledge during a task execution.

---

## Workspace Layout

```
D:/WorkBuddy/
├── .workspace-index.md      # Master skill status board
├── skill-factory/           # This meta-skill repo
│   ├── SKILL.md             # This file
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── LICENSE
│   ├── .gitignore
│   ├── inbox/               # Raw ideas drop zone
│   └── wip/                 # Active work-in-progress
│       └── <skill-name>/
│           ├── BRIEF.md
│           ├── raw/
│           └── draft/
│
├── harness/                 # ✅ v1.2.0 — ready for GitHub
├── nova-reader/             # ✅ v1.1.0 — ready for GitHub
└── <future-skills>/
```

---

## Lessons Learned (from .learnings)

| ID | Lesson | Fix in SOP |
|----|--------|-----------|
| LRN-001 | Missed content after distillation without re-reading source | Phase 2 mandatory re-fetch |
| LRN-002 | Skill evolved in workspace, hard to publish as standalone | Phase 3 independent repo |
| LRN-003 | Over-engineered before confirming real need | Phase 0 three-question lock |
| LRN-004 | Research notes mixed with skill docs | `raw/` vs `references/` separation |
