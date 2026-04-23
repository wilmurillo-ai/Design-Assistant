---
name: devopsellence
description: Install the devopsellence CLI, initialize project config, deploy the current app, inspect status, and manage secrets or bring-your-own nodes from OpenClaw.
homepage: https://www.devopsellence.com/docs
metadata: {"openclaw":{"homepage":"https://www.devopsellence.com/docs","skillKey":"devopsellence"}}
---

# devopsellence

Use this skill when the user wants to deploy an app with devopsellence, check deployment state, manage secrets, or bootstrap and assign their own nodes.

## Default flow

1. Work in the app directory the user wants to deploy.
2. Check whether the CLI is already installed:

```bash
command -v devopsellence
```

If the command is missing, install the latest compatible CLI:

```bash
curl -fsSL https://www.devopsellence.com/lfg.sh | bash
```

3. Validate local state before changing anything:

```bash
devopsellence doctor
```

4. If the project is not initialized yet, run:

```bash
devopsellence init
```

If the user already knows the target workspace values, prefer explicit flags:

```bash
devopsellence init --org acme --project shop --env staging
```

5. Deploy the app:

```bash
devopsellence deploy
```

If the user wants to deploy an existing image digest instead of building locally:

```bash
devopsellence deploy --image docker.io/example/app@sha256:...
```

6. Verify the result:

```bash
devopsellence status --json
```

## Secrets

Prefer stdin over literal secret values in prompts or shell history:

```bash
printf '%s' "$VALUE" | devopsellence secret set --service web --name NAME --stdin
devopsellence secret list
devopsellence secret delete --service web --name NAME
```

## Bring your own node

Use these when the user wants to run on their own machine or VM:

```bash
devopsellence node bootstrap
devopsellence node list --json
devopsellence node assign <id>
devopsellence node unassign <id>
```

## Heuristics

- Prefer `devopsellence doctor` before `devopsellence deploy`.
- If Docker is missing or not running, surface the problem clearly, or switch to `devopsellence deploy --image ...` when the user already has a pushed image digest.
- If the workspace is not a git checkout and the CLI needs git metadata, stop and ask before creating a repo or commit.
- Keep secrets out of logs and chat output. Use environment variables plus `--stdin`.
- After installing this skill from ClawHub, start a new OpenClaw session if the current session does not pick it up.
