# Publish to ClawHub — OpenClaw Skill Publishing Workflow

![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A complete workflow for publishing an OpenClaw skill to **GitHub** and **ClawHub** — from English internationalization and proprietary reference cleanup, through clean git history reconstruction, to live ClawHub publication.

## What This Does

When you ask to "publish a skill", this skill takes over the entire end-to-end process:

1. **Analyze** existing skill files for Chinese content and proprietary references
2. **English-ize** SKILL.md, README.md, and script comments
3. **Sanitize** all drug names, protein names, tokens, emails, and personal data
4. **GitHub** initialization, commit, push, and optional clean-history rebuild
5. **ClawHub** publish via CLI with version and changelog

## Usage

Activate when the user says things like:

- "Publish this skill to ClawHub"
- "Put this on GitHub and ClawHub"
- "Help me release this skill"
- "How do I share a skill I made?"

## Prerequisites

- **GitHub SSH key** (recommended) or **PAT** with `repo` scope (for git push)
  - ⚠️ Never embed a token in a URL — use SSH or credential helper instead
- **ClawHub CLI** installed: `npm i -g clawhub`
- **ClawHub account** logged in: `clawhub login`
- Skill folder must exist at `~/.openclaw/workspace/skills/<skill-name>/`

## Quick Start

```bash
# 1. Install clawhub CLI
npm i -g clawhub

# 2. Login to ClawHub
clawhub login

# 3. The AI will handle everything else once you say "publish this skill"
```

## Complete Workflow

```
┌─────────────────────────────────────────────────────┐
│  Step 1: Analyze skill files                        │
│    • Scan for Chinese text                           │
│    • Scan for proprietary references                │
│    • Review SKILL.md, README.md, scripts            │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Step 2: English-ize                                │
│    • Rewrite SKILL.md description in English         │
│    • Translate README.md to English                  │
│    • Convert Chinese script comments to English      │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Step 3: Remove Proprietary References               │
│    • Replace drug/protein names → placeholders       │
│    • Remove tokens, keys, emails                     │
│    • Generic examples only                          │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Step 4: GitHub                                    │
│    • Create empty repo on github.com/new            │
│    • git init + add remote + commit + push          │
│    • Optional: rebuild clean single-commit history   │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Step 5: ClawHub Publish                            │
│    • clawhub publish --slug --name --version        │
│    • Returns package ID                              │
│    • Available at clawhub.com/skills/<slug>        │
└─────────────────────────────────────────────────────┘
```

## Common Proprietary Patterns to Remove

| Find | Replace With |
|------|-------------|
| Real drug compound names | `Drug_Candidate` |
| Real protein names | `ChainA`, `ChainB` |
| Specific species names | `Human_Target`, `Bacterial_Target` |
| File names with real IDs | `target_protein.fasta` |
| API tokens / keys | `YOUR_TOKEN_HERE` |
| Personal email addresses | `example@example.com` |

## ClawHub Commands

```bash
# Install clawhub CLI (verify package integrity before installing)
npm i -g clawhub

# Login
clawhub login

# Publish a skill (use absolute path)
clawhub publish /path/to/skill \
  --slug my-skill \
  --name "My Skill Name" \
  --version 1.0.0 \
  --changelog "Initial release"

# Search
clawhub search my-skill

# Install as a user
clawhub install my-skill
```

## Security Notes

⚠️ **This skill performs `git push -f` (force push)** which rewrites remote git history.
Always backup the remote repository before running force-push operations.

⚠️ **Credentials**: Never embed tokens in URLs. Use SSH keys or `git credential` helpers.
If you must use a PAT, run `git push` manually and enter credentials interactively.

## License

MIT — see [LICENSE](LICENSE) in the parent skill folder.
