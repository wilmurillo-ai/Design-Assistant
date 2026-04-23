# claw-migrate Complete Design Specification

**Version**: v2.1.0  
**Update Date**: 2026-03-15  
**Status**: Pending implementation

---

## 🎯 Core Design Principles

### 1. User-Led
- ✅ Let users choose, don't decide automatically
- ✅ Clear prompts, don't hide risks
- ✅ Modify anytime, don't lock configuration

### 2. Simple and Efficient
- ✅ Two-choice after installation (backup or restore)
- ✅ Default configuration recommendations, reduce decision burden
- ✅ Preview confirmation, avoid misoperation

### 3. Privacy Protection
- ✅ Sensitive information not backed up by default
- ✅ Machine-specific configuration handled separately
- ✅ Clear risk prompts

---

## 📋 Complete Function Design

### I. Post-Installation Wizard

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

### II. Backup Configuration Flow

#### Step 1: GitHub Repository

```
🔵 Backup Configuration Wizard - Step 1 / 5

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

#### Step 2: Authentication Method

```
🔵 Backup Configuration Wizard - Step 2 / 5

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

#### Step 3: Backup Content Selection (Core Optimization)

```
🔵 Backup Configuration Wizard - Step 3 / 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Backup Content Selection

We recommend the following default configuration for you:

✅ Default backup content (Recommended):
   • Core configuration (AGENTS.md, SOUL.md, USER.md, etc.)
   • Skill files (skills/)
   • Memory files (MEMORY.md, memory/)
   • Learning records (.learnings/)

⚠️  The following content is not backed up by default (Optional):
   • Channel configuration (feishu/, telegram/, etc.)
     └─ Machine-specific configuration, recommended for multi-device sync
   • Environment configuration (.env and other sensitive information)
     └─ Contains API keys, only backup to trusted repository

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Your choice:
   
   1. Use default configuration (Recommended)
   2. Custom selection
   3. Go back to previous step

   Select [1-3]: 1
```

#### Step 4: Custom Selection (Optional)

```
🔵 Backup Configuration Wizard - Step 3 / 5 (Custom)

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

#### Step 5: Backup Frequency

```
🔵 Backup Configuration Wizard - Step 4 / 5

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

#### Step 6: Confirm Configuration

```
🔵 Backup Configuration Wizard - Step 5 / 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Configuration Summary

   Repository: hanxueyuan/openclaw-backup
   Branch: main
   Authentication: GITHUB_TOKEN
   
   Backup content:
     ✅ Core configuration
     ✅ Skill files
     ✅ Memory files
     ✅ Learning records
     ❌ Channel configuration
     ❌ Environment configuration
   
   Backup frequency: Daily at 2 AM

   Confirm configuration? (y/n): y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Confirm]
```

#### Step 7: Configuration Complete

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

### III. Restore/Migrate Configuration Flow

#### Step 1: GitHub Repository

```
🟢 Restore Configuration Wizard - Step 1 / 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ GitHub Repository Configuration

   Please enter GitHub repository name (format: owner/repo):
   └─ Example: hanxueyuan/openclaw-backup
   
   > hanxueyuan/openclaw-backup

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   [Previous] [Next]
```

#### Step 2: Authentication Configuration

```
🟢 Restore Configuration Wizard - Step 2 / 5

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

#### Step 3: Restore Strategy Selection

```
🟢 Restore Configuration Wizard - Step 3 / 5

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

#### Step 4: Preview Restore Content

```
🟢 Restore Configuration Wizard - Step 4 / 5

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

#### Step 5: Restore Complete

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

### IV. Backup Execution Flow

#### Manual Backup

```bash
openclaw skill run claw-migrate backup
```

```
🚀 Starting backup...

📦 Detect changes
   • Detected 3 file changes
   • Added: skills/new-skill/SKILL.md
   • Modified: MEMORY.md
   • Modified: .learnings/LEARNINGS.md

🔐 Sensitive information check
   • Skip .env (user did not select backup)
   • Skip feishu/pairing/ (machine-specific configuration)

📤 Upload to GitHub
   • Create commit: backup-2026-03-15T02-00-00
   • Push to hanxueyuan/openclaw-backup/main

✅ Backup complete!
   • Backup time: 2026-03-15 02:00:05
   • Backup size: 1.2 MB
   • File count: 15
```

#### Automatic Backup (Scheduled Task)

```
[2026-03-15 02:00:00] Starting automatic backup...
[2026-03-15 02:00:01] Detected 3 file changes
[2026-03-15 02:00:02] Skip sensitive information
[2026-03-15 02:00:03] Create commit
[2026-03-15 02:00:04] Push to GitHub
[2026-03-15 02:00:05] ✅ Backup complete
```

---

### V. Configuration Management

#### View Configuration

```bash
openclaw skill run claw-migrate config
```

```
📋 Current Configuration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Repository Configuration:
   • Repository: hanxueyuan/openclaw-backup
   • Branch: main

Authentication Configuration:
   • Method: GITHUB_TOKEN
   • Status: ✅ Valid

Backup Content:
   ✅ Core configuration
   ✅ Skill files
   ✅ Memory files
   ✅ Learning records
   ❌ Channel configuration
   ❌ Environment configuration

Backup Frequency:
   • Daily at 2 AM
   • Next backup: 2026-03-16 02:00:00

Backup History:
   • Recent backup: 2026-03-15 02:00:05
   • Backup count: 15
   • Total size: 18.5 MB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Operation Options:
   1. Modify configuration
   2. Backup immediately
   3. View backup history
   4. Restore configuration
   5. Exit

   Select [1-5]: _
```

#### Modify Configuration

```bash
openclaw skill run claw-migrate config --edit
```

```
📝 Modify Configuration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current selection:
   ✅ Core configuration
   ✅ Skill files
   ✅ Memory files
   ✅ Learning records
   ❌ Channel configuration
   ❌ Environment configuration

   Want to modify backup content selection? (y/n): y

   Please select content to backup (multi-select):
```
