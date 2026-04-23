---
name: tronclass-cli
description: Use this skill to interact with the TronClass learning management system (currently optimized for FJU). Use it whenever the user asks anything about their courses, assignments, deadlines, grades, or course materials on TronClass — even if they don't say "TronClass" explicitly. This includes checking what homework is due, finding and downloading lecture slides or PDFs, submitting assignments, listing enrolled courses, or viewing activity details. If the user mentions school, assignments, due dates, course files, or anything that sounds like an LMS task, lean toward using this skill.
repository: https://github.com/YuJun-BO2/tronclass-cli-skill
homepage: https://github.com/YuJun-BO2/tronclass-cli-ts
---

# TronClass CLI Skill

You have access to `tronclass-cli`, a command-line tool for managing the user's TronClass account.

## Setup

Install globally (once):
```bash
npm install -g tronclass-cli
```

## General Guidelines

- **Authentication**: Most commands require a saved session. If a command fails, tell the user to run `tronclass auth login <username>` (requires interactive password input). Session is saved after login and reused automatically.
- **FJU users**: Use `tronclass auth login --fju <student_id>` for the CAS flow with CAPTCHA support.
- **Finding IDs**: The typical lookup chain is `courses list` → `activities list <course_id>` → `activities view <activity_id>`. The `todo` command shows activity IDs directly in the first column.
- **Aliases**: `activities` → `a`, `courses` → `c`, `homework` → `hw`, `todo` → `td`. Subcommands also have short aliases (`list`→`l`, `view`→`v`, `download`→`d`).

## Command Quick Reference

| Command | What it does |
|---|---|
| `tronclass auth login [--fju] <user>` | Log in (interactive) |
| `tronclass auth check` | Show current session info |
| `tronclass auth logout` | Clear saved session |
| `tronclass todo` | Pending tasks — first column is the activity ID |
| `tronclass courses list [--all] [--raw]` | List courses |
| `tronclass activities list <course_id>` | List activities in a course |
| `tronclass activities view <activity_id>` | Rich view: metadata + description + attachments |
| `tronclass activities download <ref_id> [output]` | Download file (defaults to ~/Downloads/) |
| `tronclass homework list <course_id>` | List homework for a course |
| `tronclass homework submit <activity_id> <files...>` | Submit homework files |

All commands support `--fields f1,f2,...` to customize displayed columns.

## Key Behaviors

**`tronclass todo`** — shows `id, course_name, title, end_time` by default. The `id` column is the activity ID you can pass directly to `activities view`.

**`tronclass activities view <id>`** — displays a formatted table (not raw JSON). The Attachments section lists each file with its `ref_id` and a ready-to-run download command. No need to manually dig through JSON.

**`tronclass activities download <ref_id>`** — `output_file` is optional. If omitted, the file is saved to `~/Downloads/<filename>` using the server-provided filename.

## Common Workflows

**Check what's due:**
```bash
tronclass todo
```

**Download a course file:**
```bash
tronclass courses list                        # get course_id
tronclass activities list <course_id>         # get activity_id
tronclass activities view <activity_id>       # see Attachments table → note ref_id
tronclass activities download <ref_id>        # saves to ~/Downloads/ automatically
```

**Submit homework:**
```bash
tronclass homework list <course_id>           # find activity_id
tronclass homework submit <activity_id> ./my_essay.pdf
```

## Reference Files

For detailed option lists, field names, and edge cases, load the relevant reference:

- `references/auth.md` — login flows, session management
- `references/todo.md` — todo fields, filtering
- `references/courses.md` — course fields, `--raw` flag
- `references/activities.md` — activities list/view/download in depth
- `references/homework.md` — homework list, submit options, draft mode
