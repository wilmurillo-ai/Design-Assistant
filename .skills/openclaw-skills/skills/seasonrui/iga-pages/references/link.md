# Link

Link a local directory to an existing IGA Pages project (or create a new one).

## Basic Usage

```bash
iga pages link        # interactive mode
iga pages link -y     # non-interactive (auto-confirm)
iga pages link --yes  # same as -y
```

## Requirements

- Must be logged in (`~/.iga/auth.json` or env vars)
- **Non-TTY requires `--yes`** — without it, the command exits immediately to avoid hanging

## Behavior

- If remote projects exist, the CLI tries to auto-match by current directory name
- If no match or no projects exist, prompts to create a new one (or auto-creates with `--yes`)
- Result is written to `.iga/project.json`

## Overwrite Protection

If `.iga/project.json` already exists and points to a **different** project:

- **Interactive**: asks for confirmation before overwriting
- **With `--yes`**: overwrites silently

## Config Written

```json
// .iga/project.json
{
  "projectId": "proj_xxxx",
  "projectName": "my-project",
  "provider": "upload_v2"   // or "github"
}
```

The CLI also appends `.iga/` to `.gitignore` automatically.

## When to Use Link vs Deploy

- Use `iga pages link` when: you want to connect to an existing project without deploying.
- Use `iga pages deploy` directly when: it's fine to create a new project and deploy in one step.

`iga pages deploy` writes `.iga/project.json` on first deploy, so `link` is optional if you always deploy.
