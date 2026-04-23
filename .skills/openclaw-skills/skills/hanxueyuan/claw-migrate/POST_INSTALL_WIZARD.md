# claw-migrate Post-Installation Wizard Design

**Trigger Timing**: Automatically triggered after skill installation completes

**Core Principle**: Simple two-choice, let user choose backup or restore

---

## 🎯 Complete Flow

### Step 1: Installation Complete, Two-Choice

```bash
# User installs skill
openclaw skill install claw-migrate

# ✅ Automatically triggered after installation
🎉 claw-migrate installation complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Please select the operation you want to perform:

   1. 🔵 Start Backup Configuration
      Backup local configuration to GitHub private repository
      Suitable for: First-time use, regular backup

   2. 🟢 Restore/Migrate Configuration
      Restore configuration from GitHub repository to local
      Suitable for: New machine, configuration restore

   3. ⚪ Configure Later
      Skip wizard, configure manually later

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Select [1-3, auto-select 3 after 10 seconds]: _
```

---

## 🔵 Choice 1: Start Backup Configuration

### Step 2-B: GitHub Repository Configuration

```
✅ Great, let's configure backup!

📝 Backup Configuration Wizard - Step 1 / 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ GitHub Repository Configuration

   Please enter GitHub repository name (format: owner/repo):
   └─ Example: hanxueyuan/openclaw-backup
   
   > hanxueyuan/openclaw-backup

   ✅ Repository format correct

   Please enter branch name (default: main):
   
   > main

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Next]
```

### Step 3-B: Authentication Configuration

```
📝 Backup Configuration Wizard - Step 2 / 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Authentication Method

   Please select authentication method:
   
   1. Use GITHUB_TOKEN environment variable (Recommended)
   2. Use gh CLI (requires logged in)
   3. Manually enter Token
   
   Select [1-3]: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Next]
```

### Step 4-B: Backup Content Selection (Default Configuration + User Confirmation)

```
📝 Backup Configuration Wizard - Step 3 / 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Backup Content Selection

We recommend the following default configuration for you:

✅ Default backup content:
   • Core configuration (AGENTS.md, SOUL.md, USER.md, etc.)
   • Skill files (skills/)
   • Memory files (MEMORY.md, memory/)
   • Learning records (.learnings/)

⚠️  The following content is not backed up by default (optional):
   • Channel configuration (feishu/, telegram/, etc.) - Machine-specific
   • Environment configuration (.env and other sensitive information) - Contains API keys

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Your choice:
   
   1. Use default configuration (Recommended)
   2. Custom selection
   3. Go back to previous step

   Select [1-3]: 1
```

### Step 5-B: Custom Selection (If User Chooses Custom)

```
📝 Backup Configuration Wizard - Step 3 / 4 (Custom)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Please select content to backup (Spacebar to toggle, Enter to confirm):

Default backup content:
   ✅ [x] 1. Core configuration (AGENTS.md, SOUL.md, USER.md, etc.)
   ✅ [x] 2. Skill files (skills/)
   ✅ [x] 3. Memory files (MEMORY.md, memory/)
   ✅ [x] 4. Learning records (.learnings/)

Optional content:
   ⚠️  [ ] 5. Channel configuration (feishu/, telegram/, etc.)
         └─ Contains machine-specific configuration, recommended for multi-device sync
   ⚠️  [ ] 6. Environment configuration (.env and other sensitive information)
         └─ Contains API keys, only backup to trusted repository

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Tip: Use spacebar to toggle options, Enter to confirm

   [Previous] [Next]
```

### Step 6-B: Backup Frequency

```
📝 Backup Configuration Wizard - Step 4 / 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Backup Frequency

   Please select backup frequency:
   
   1. Daily at 2 AM (Recommended)
   2. Weekly on Monday at 2 AM
   3. Monthly on 1st at 2 AM
   4. Manual backup only
   
   Select [1-4]: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Next]
```

### Step 7-B: Confirm Configuration

```
📝 Backup Configuration Wizard - Confirm Configuration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Configuration Summary

   Repository: hanxueyuan/openclaw-backup
   Branch: main
   Authentication: env
   
   Backup content:
     ✅ Core configuration
     ✅ Skill files
     ✅ Memory files
     ✅ Learning records
     ⚠️  Channel configuration (optional)
     ❌ Environment configuration (optional)
   
   Backup frequency: Daily at 2 AM

   Confirm configuration? (y/n): y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Confirm]
```

### Step 8-B: Configuration Complete

```
🎉 Backup configuration complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Backup configuration saved

📌 Next steps:

   1. Execute first backup
      openclaw skill run claw-migrate backup

   2. View backup status
      openclaw skill run claw-migrate status

   3. Modify configuration
      openclaw skill run claw-migrate config --edit

💡 Tips:
   • Backup will execute automatically, no manual intervention needed
   • Next backup time: 2026-03-16 02:00:00
   • View help: openclaw skill run claw-migrate --help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enjoy using!
```

---

## 🟢 Choice 2: Restore/Migrate Configuration

### Step 2-R: GitHub Repository Configuration

```
✅ Great, let's restore configuration!

📝 Restore Configuration Wizard - Step 1 / 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ GitHub Repository Configuration

   Please enter GitHub repository name (format: owner/repo):
   └─ Example: hanxueyuan/openclaw-backup
   
   > hanxueyuan/openclaw-backup

   ✅ Repository format correct

   Please enter branch name (default: main):
   
   > main

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Next]
```

### Step 3-R: Authentication Configuration

```
📝 Restore Configuration Wizard - Step 2 / 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Authentication Method

   Please select authentication method:
   
   1. Use GITHUB_TOKEN environment variable (Recommended)
   2. Use gh CLI (requires logged in)
   3. Manually enter Token
   
   Select [1-3]: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Next]
```

### Step 4-R: Restore Strategy Selection

```
📝 Restore Configuration Wizard - Step 3 / 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Restore Strategy

   Please select restore content:
   
   1. Restore general configuration only (Recommended)
      • Core configuration, skills, memory, learning records
      • Preserve current machine's Channel configuration
      • Preserve current machine's .env configuration
   
   2. Full restore
      • Restore all backed up content
      • Overwrite current machine's configuration
      • Need to reconfigure Channel and API keys
   
   3. Custom selection
      • Manually select content to restore
   
   Select [1-3]: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Next]
```

### Step 5-R: Preview Restore Content

```
📝 Restore Configuration Wizard - Step 4 / 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Preview Restore Content

   Will restore following files:
   
   ✓ AGENTS.md (New version)
   ✓ SOUL.md (New version)
   ✓ USER.md (New version)
   ✓ skills/weather/SKILL.md (New skill)
   ✓ MEMORY.md (Merge)
   ⏭️ .env (Preserve local)
   ⏭️ feishu/pairing/ (Preserve local)
   
   Total 15 files, skip 2

   Confirm restore? (y/n): y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Confirm]
```

### Step 6-R: Restore Complete

```
🎉 Restore complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Configuration restored

📌 Next steps:

   1. Check if configuration files are correct
   2. If needed, configure Channel pairing
   3. Run `openclaw memory rebuild` to rebuild memory index

💡 Tips:
   • View help: openclaw skill run claw-migrate --help
   • Configure backup: openclaw skill run claw-migrate setup

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enjoy using!
```

---

## ⚪ Choice 3: Configure Later

```
👌 Okay, skipped wizard.

💡 Tips:
   You can run following commands anytime:
   
   • openclaw skill run claw-migrate backup   - Backup configuration
   • openclaw skill run claw-migrate restore  - Restore configuration
   • openclaw skill run claw-migrate setup    - Reconfigure

Enjoy using!
```

---

## 🎯 Design Points

1. **Simple Two-Choice** - Backup or restore, clear at a glance
2. **Default Configuration** - Provide recommended default backup content, user confirms
3. **Custom Options** - Users can customize backup content selection
4. **Clear Prompts** - Sensitive information, risks clearly prompted
5. **Preview Confirmation** - Preview before restore, execute after confirmation

---

**Implementation Priority**: P0  
**Status**: Pending implementation
