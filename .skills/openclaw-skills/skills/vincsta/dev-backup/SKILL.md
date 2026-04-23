---
name: dev-backup
description: Create snapshots of a workspace project during development. Use when: (1) user asks to backup the current app, (2) before risky changes/refactoring, (3) "salva lo stato attuale" or "fai un backup dello sviluppo", (4) any point where the project could be corrupted or lost. Automatically adds progressive numbering per project.
---

# dev-backup

Snapshot the current state of a named project for safe rollback.

## Usage

Each project gets its own snapshot numbering. The project name is always the first argument.

```bash
# Backup any project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/dev-backup.sh" <project-name> --project-dir /path/to/your/project

# Example: backup a "my-app" project
bash "$SCRIPT_DIR/dev-backup.sh" my-app --project-dir /home/user/projects/my-app

# No --project-dir? Uses the current working directory
cd /home/user/projects/my-app
bash "$SCRIPT_DIR/dev-backup.sh" my-app
```

## Naming

Snapshots are named per project:

- **my-app-snapshot-1**, **my-app-snapshot-2**, …
- **another-project-snapshot-1**, **another-project-snapshot-2**, …

Each project tracks its own counter independently.

## Excluded from snapshot

- `.git`, `node_modules`, `.vite`, `.cache`, `*.log`, `.env`, `backups/`

## Restore

To restore a snapshot:

```bash
cp -r <backups-dir>/<project-name>-snapshot-3/ <your-project-dir>/
```

Or use the `.latest` symlink:

```bash
cp -r <backups-dir>/.latest/ <your-project-dir>/
```

## Verification

After backup, confirm:

```bash
ls -la <backups-dir>/
```

You should see the project-prefixed snapshot and `.latest` symlink.
