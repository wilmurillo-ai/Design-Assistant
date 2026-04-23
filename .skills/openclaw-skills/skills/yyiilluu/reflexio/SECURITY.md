# Security & Privacy — Reflexio Embedded

This plugin captures user profiles and playbooks by reading session transcripts and handing them to an extractor sub-agent. That work has real privacy and blast-radius implications. This document states them plainly so you can decide whether — and how — to install.

## Threat Model

### What leaves the host

When Flow C (session-end batch extraction) or the daily consolidation cron fires, a sub-agent reads the session transcript (including user messages, assistant replies, and any tool I/O captured in the transcript). That sub-agent runs through whatever LLM / embedding provider your OpenClaw instance is configured with.

**If your OpenClaw is wired to a hosted provider (OpenAI, Anthropic, Gemini, Voyage, Mistral, etc.), transcript excerpts will be sent to that provider.** This is inherent to LLM-based extraction, not a bug. If you need strictly on-host operation, configure OpenClaw with a local LLM (Ollama, LM Studio, vLLM) *before* installing.

### Redaction: scope and limits

`hook/handler.ts` runs a best-effort regex scrub on the transcript before it reaches the extractor sub-agent. The scrub targets high-confidence patterns:

- PEM private key blocks (RSA/EC/DSA/OpenSSH/encrypted)
- Vendor-prefixed API keys: OpenAI (`sk-...`, `sk-proj-...`), Anthropic (`sk-ant-...`), GitHub (`ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`), GitLab (`glpat-`), Slack (`xox[abpors]-`), AWS (`AKIA...`), Stripe (`sk_live_`/`pk_live_`/etc.)
- `Authorization: Bearer <token>` / `Bearer <token>` headers
- `*_PASSWORD` / `*_SECRET` / `*_TOKEN` / `*_API_KEY` / `*_PRIVATE_KEY` / `*_ACCESS_KEY` / `*_AUTH` env-style assignments
- JWTs (three base64url segments)

**This is a backstop, not a guarantee.** Arbitrary credentials that don't match a known pattern (custom internal token formats, raw high-entropy strings, secrets quoted in unusual contexts) will pass through. Treat the scrub as defense-in-depth; the real defense is not pasting secrets into sessions.

You can verify or extend the scrub rules: see `REDACTION_PATTERNS` in `hook/handler.ts` and the smoke test in `hook/smoke-test.ts`.

### What the plugin writes to disk

Profiles and playbooks land under `.reflexio/profiles/` and `.reflexio/playbooks/` in your workspace. These files are plain Markdown with YAML frontmatter — auditable by hand. `SKILL.md` and the extraction prompts instruct agents not to write secrets; if you ever see one in a `.reflexio/` file, delete it and open an issue.

## Host-Wide Side Effects

The install script is structured so nothing privileged happens without an explicit flag.

| Action | Behavior | Flag to opt in |
|---|---|---|
| Link/copy plugin files to `$OPENCLAW_HOME/workspace/` | Always happens | (default) |
| Enable `reflexio-embedded` plugin for the current agent | Always happens | (default) |
| Enable `active-memory` plugin **host-wide** | Skipped by default | `--enable-active-memory` |
| Register daily 3am consolidation cron | Skipped by default | `--enable-cron` |
| Restart the OpenClaw gateway | Skipped by default | `--restart-gateway` |
| All of the above | | `--all` |

The `--enable-active-memory`, `--enable-cron`, and `--restart-gateway` flags affect every agent and session on the host, not just the one you're installing from. On shared/team OpenClaw instances, keep them off unless the team has signed off.

Per-agent configuration (active-memory targeting for this specific agent, `.reflexio/` extraPath registration) happens on first use via the `SKILL.md` bootstrap, with user approval for each `openclaw config set` call.

## Prompt-Injection Surface

The extraction and consolidation prompts under `prompts/` structure LLM calls — they tell the sub-agent how to read a transcript and emit Markdown profiles/playbooks. The transcript itself is untrusted input; a malicious user message could in principle try to override extraction instructions.

Mitigations already in place:
- Extractor runs in an **isolated sub-session** (`sessionKey: "reflexio-extractor:..."`), so it cannot pollute the parent agent's transcript or alter its system prompt.
- Extractor output is parsed as Markdown with a fixed frontmatter schema before being written; free-form "execute this shell command" output has nowhere to go.
- The plugin does not grant the extractor tool access to modify OpenClaw config or install other plugins.

What still warrants review:
- `prompts/*.md` — inspect these to confirm the sub-agent's instructions cannot be co-opted via transcript content.
- `hook/handler.ts` → `buildExtractionTaskPrompt` — this is where transcript content is interpolated into the task prompt. The redaction pass runs first; the transcript is then placed under a `## Transcript` heading.

## Recommended Stances

**Personal instance, trusted user:**  `./scripts/install.sh --all` is fine. You're the only one paying the blast-radius cost.

**Shared/team instance:**  Start with the default minimal install. Decide per-item whether to enable `active-memory` host-wide or wire it per-agent; decide whether a daily cron is acceptable; run `openclaw gateway restart` on your own schedule.

**Compliance-sensitive workloads (PII, healthcare, regulated code):**  Run OpenClaw against a local LLM/embedding stack before installing, and audit `prompts/` + `hook/handler.ts` end-to-end. The redaction pass is not a HIPAA/SOC2 control.

## Disable Capture Per-Session

- Disable the hook:  `openclaw hooks disable reflexio-embedded`
- Remove the cron:   `openclaw cron rm reflexio-embedded-consolidate`
- Uninstall entirely: `./scripts/uninstall.sh` (add `--purge` to delete `.reflexio/` data)

## Reporting Issues

Found a secret leaking through the scrub, or a prompt-injection path that escalates privileges? Open an issue at the Reflexio repository, or email the maintainers directly if the issue is sensitive.
