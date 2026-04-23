---
name: skylv-skill-quality-assurance
description: Analyzes and scores OpenClaw skill quality across 5 dimensions. Detects missing frontmatter, weak descriptions, poor examples, and actionable improvement recommendations.
keywords: skill, quality, analysis, scoring, improvement, documentation, review
triggers: quality, score, analyze skill, skill review, documentation
---

# Skill Quality Assurance

Automatically analyze and score OpenClaw skill documentation quality. Identifies critical issues and provides actionable fixes.

## Overview

This skill runs a multi-dimensional quality analysis on any OpenClaw skill's SKILL.md file, scoring it across:
- **Clarity** — Structure, headings, sentence length
- **Completeness** — Required fields, install/usage sections
- **Actionability** — Step-by-step guides, commands
- **Discoverability** — Keywords, description, categories
- **Examples** — Code examples, before/after, use cases

## Usage

### Analyze a single skill

```
Analyze the skill at: C:\path\to\skills\my-skill
```

### Analyze all skills in a directory

```
Run: node engine.js C:\path\to\skills
```

### Interpretation

| Score | Grade | Meaning |
|-------|-------|---------|
| 8-10 | A | Production-ready |
| 6-7 | B | Needs minor improvements |
| 4-5 | C | Needs significant work |
| <4 | F | Rewrite recommended |

## Scoring Dimensions

### 1. Clarity (20%)
Checks for: headings hierarchy, sentence length, filler words, markdown formatting

### 2. Completeness (20%)
Checks for: `name`, `description`, `keywords`, install section, usage section

### 3. Actionability (25%)
Checks for: numbered steps, runnable commands, configuration guides

### 4. Discoverability (15%)
Checks for: keywords (5+), description length (50+ chars), category/tags

### 5. Examples (20%)
Checks for: code blocks (3+), before/after cases, use case descriptions

## Quality Thresholds

For ClawHub publication:
- Overall score ≥ 7.0 required
- No dimension below 5.0
- Must have keywords field
- Must have description ≥ 50 chars

## Auto-Fix

The companion script `fix_skill_md.cjs` automatically fixes:
- Missing `description` field
- Missing `keywords` field
- Missing `Install` section
- Missing `Usage` section

```bash
node fix_skill_md.cjs
```

## Example Output

```
# Skill Quality Report

Analyzed: 34 skills

## Overall Rankings
 1. ✅ skylv-browser-automation-agent   9.4/10
 2. ✅ skylv-openclaw-evomap-connector   9.3/10

Average score: 8.1/10
Grade A (7+): 29
Grade B (5-6): 5
Grade C (<5): 0
```

## MIT License © SKY-lv
