# claw-migrate Usage Examples

## Scenario 1: Newly Installed OpenClaw

### Situation
You just installed OpenClaw on a new server and want to pull configuration from GitHub private repository.

### Steps

```bash
# 1. Set GitHub Token
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# 2. Execute migration
openclaw skill run claw-migrate --repo your-username/your-repo --path workspace/projects/workspace

# 3. Verify configuration
cat AGENTS.md
cat SOUL.md
ls skills/
```

### Expected Output
```
============================================================
  OpenClaw GitHub Configuration Migration Tool
============================================================

📡 Connecting to GitHub...
✅ Connected to repository: your-username/your-repo
   Type: Private repository

📋 Analyzing files...
   Found 25 files pending migration

💾 Creating backup...
✅ Backup created: .migrate-backup/2024-01-15T10-30-00-000Z

🚀 Starting migration...

   ✓ AGENTS.md
   ✓ SOUL.md
   ✓ IDENTITY.md
   ✓ USER.md
   ✓ skills/claw-migrate/SKILL.md
   ✓ skills/weather/SKILL.md
   ...

==================================================
✅ Migration complete!
   Success: 25 files
   Skipped: 0 files

📌 Next steps:
   • Check if configuration is correct, can restore from backup if issues
   • Verify configuration files like AGENTS.md, SOUL.md
   • Check if new skills work correctly
```

---

## Scenario 2: Configuration Restore

### Situation
Local configuration files are corrupted or accidentally deleted, need to restore from GitHub repository.

### Steps

```bash
# 1. Preview which files will be restored
openclaw skill run claw-migrate --repo your-username/your-repo --dry-run

# 2. Execute restore
openclaw skill run claw-migrate --repo your-username/your-repo

# 3. If issues occur, restore from backup
cp .migrate-backup/<timestamp>/AGENTS.md ./AGENTS.md
```

---

## Scenario 3: Update Skills Only

### Situation
You want to get the latest skills from repository, but don't want to overwrite local configuration.

### Steps

```bash
# Pull skill files only
openclaw skill run claw-migrate --repo your-username/your-repo --type skills

# Example output:
#    ⏭️  AGENTS.md (Already exists locally, skip)
#    ✓ skills/new-skill/SKILL.md
#    ⏭️  skills/weather/SKILL.md (Already exists locally, skip)
```

---

## Scenario 4: Multi-Device Sync

### Situation
You have OpenClaw at both office and home, want to keep configuration synchronized.

### Steps

```bash
# On home server (central repository)
# 1. Ensure configuration is committed to GitHub
cd /workspace/projects/workspace
git add .
git commit -m "Update configuration"
git push

# On office server
# 2. Pull latest configuration
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
openclaw skill run claw-migrate --repo your-username/your-repo --type config --type skills
```

---

## Scenario 5: Preview Mode

### Situation
Before executing actual migration, want to see which files will be changed first.

### Steps

```bash
openclaw skill run claw-migrate --repo your-username/your-repo --dry-run
```

### Expected Output
```
📝 Preview files to be migrated:

   + AGENTS.md
   + SOUL.md
   + IDENTITY.md
   + USER.md
   + skills/claw-migrate/SKILL.md
   + skills/weather/SKILL.md
   + memory/2024-01-15-daily-review.md
   + .learnings/LEARNINGS.md

💡 Use parameters other than --dry-run to execute actual migration
```

---

## Scenario 6: Using gh CLI Authentication

### Situation
You have already installed GitHub CLI and logged in, want to use it directly for authentication.

### Steps

```bash
# Ensure logged in
gh auth status

# Execute migration (automatically get Token from gh CLI)
openclaw skill run claw-migrate --repo your-username/your-repo
```

---

## Scenario 7: Interactive Token Input

### Situation
No environment variable set, no gh CLI, want to temporarily input Token.

### Steps

```bash
# Run directly, will prompt for Token input
openclaw skill run claw-migrate --repo your-username/your-repo

# Output:
# ⚠️  GITHUB_TOKEN environment variable not detected
#    Please enter your GitHub Personal Access Token:
#    (Token only used for this session, will not be saved)
# 
# GitHub Token: [Enter Token]
```

---

## Common Questions

### Q: How do I know if migration was successful?

A: Check the statistics in output:
```
✅ Migration complete!
   Success: 25 files
   Skipped: 0 files
```

### Q: How to restore backup after migration?

A: 
```bash
# List backups
ls .migrate-backup/

# Restore specific file
cp .migrate-backup/2024-01-15T10-30-00-000Z/AGENTS.md ./AGENTS.md
```

### Q: How to skip backup?

A: 
```bash
openclaw skill run claw-migrate --repo your-username/your-repo --no-backup
```

### Q: How to view detailed logs?

A: 
```bash
openclaw skill run claw-migrate --repo your-username/your-repo --verbose
```

---

## Best Practices

1. **Use --dry-run to preview before first migration**
2. **Keep backups** (enabled by default, don't use --no-backup)
3. **Regularly update GitHub repository**, keep configuration current
4. **Use private repository**, avoid sensitive information leakage
5. **Regularly rotate tokens**, recommended to update every 90 days
