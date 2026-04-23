---
name: openclaw-plugin-workbench
description: Build and ship OpenClaw plugins with fewer publish failures. Use to scaffold plugins, run preflight validation, and prepare exact Publish Plugin fields (changelog, source repo, source commit, source ref) before dashboard submission.
user-invocable: true
metadata: {"openclaw":{"emoji":"🛠️","os":["linux","darwin","win32"],"requires":{"bins":["git","jq"]}}}
---

# OpenClaw Plugin Workbench

One skill for plugin creation, preflight checks, and release metadata handoff.

## Best for

- Starting a new OpenClaw plugin scaffold fast
- Catching publish blockers before dashboard submission
- Producing exact source/changelog fields required by Publish Plugin

## Not for

- Publishing arbitrary npm packages unrelated to OpenClaw plugins
- Skipping manifest compatibility fields
- Blind dashboard submission without preflight

## 60-second happy path

```bash
./scripts/new-plugin.sh my-plugin ./plugins
./scripts/plugin-preflight.sh ./plugins/my-plugin
./scripts/plugin-release-fields.sh ./plugins/my-plugin
```

Then publish in ClawHub Dashboard -> **Publish Plugin**.

## Mode 1) Init plugin scaffold

```bash
./scripts/new-plugin.sh <plugin-slug> [dir]
```

Creates:
- `package.json` with required `openclaw.compat` + `openclaw.build`
- `openclaw.plugin.json`
- `index.js`

## Mode 2) Preflight validation (mandatory before publish)

```bash
./scripts/plugin-preflight.sh <plugin-dir>
```

Validates:
- required files and JSON syntax
- required manifest keys and OpenClaw compat/build fields
- version alignment between `package.json` and `openclaw.plugin.json`
- quality warnings (`description`, `README.md`)
- risk-pattern warning (`child_process`, `execSync`, `spawn`)

Treat any `[error]` as release blocker.

## Mode 3) Release fields helper

```bash
./scripts/plugin-release-fields.sh <repo-dir>
```

Returns dashboard-ready fields:
- source repo
- source commit
- source ref
- changelog template

## Release gate checklist

Before dashboard publish, confirm:

- [ ] preflight passed with no `[error]`
- [ ] version is correct and synchronized
- [ ] source repo/commit/ref are final
- [ ] changelog is specific (what changed + why)

## Troubleshooting

1. Missing manifests -> rerun scaffold or add required files.
2. JSON parse fail -> fix syntax and rerun preflight.
3. Version mismatch -> align both manifest versions.
4. Missing repo fields -> ensure git remote `origin` exists.
5. Static-analysis warning -> refactor risky runtime patterns.

## Author

Vassiliy Lakhonin
