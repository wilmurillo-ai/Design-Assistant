---
name: reflexio-embedded
description: "Captures user facts and procedural corrections into .reflexio/ so the agent learns across sessions. Use when: (1) user states a preference, fact, config, or constraint; (2) user corrects the agent and confirms the fix with an explicit 'good'/'perfect' or by moving on without re-correcting for 1-2 turns; (3) at start of a user turn, to retrieve relevant facts and playbooks from past sessions."
metadata:
  openclaw:
    homepage: https://github.com/reflexio-ai/reflexio/tree/main/reflexio/integrations/openclaw-embedded
    emoji: 🧠
    requires:
      bins: [openclaw, node, bash]
      plugins: [active-memory]
    writes:
      - ".reflexio/ (workspace-local: captured profiles and playbooks)"
      - "~/.openclaw/workspace/skills/reflexio-embedded/ (skill + consolidate command)"
      - "~/.openclaw/workspace/agents/reflexio-extractor.md"
      - "~/.openclaw/workspace/agents/reflexio-consolidator.md"
      - "~/.openclaw/workspace/plugins/reflexio-embedded/ (prompts + helper scripts)"
    sideEffects:
      - "Enables the active-memory plugin host-wide"
      - "Registers a daily 3am cron (reflexio-embedded-consolidate)"
      - "Restarts the Openclaw gateway on install"
      - "Spawns reflexio-extractor sub-agent on session:compact:before / command:stop / command:reset"
---

## Privacy, Credentials & Persistence — Read This First

This plugin runs entirely inside Openclaw — **there is no Reflexio server, no
separate backend process, and no dedicated API key owned by this plugin.**
However, the install script makes several privileged changes to your Openclaw
install, and the runtime captures conversation content that is not scrubbed.
Read this before enabling.

### Credentials

**This plugin declares no required env vars and owns no credentials.** It
does not prompt for or store any API key. This is a deliberate design
difference from the server-backed `reflexio` skill.

**But extraction still needs an LLM**, and it uses whichever model your
Openclaw gateway is already configured with:

- Flow C session-end extraction (sub-agent reads full transcript)
- Daily 3am consolidation cron (sub-agent runs n-way cluster merge)
- Embedding calls for memory search (if an embedding provider is configured
  in Openclaw)

If Openclaw is configured to use a hosted provider (OpenAI, Anthropic, Gemini,
etc.), **excerpts of your conversations and extracted summaries will traverse
that provider's network path.** If you need fully offline operation,
configure a local LLM (Ollama, LM Studio, vLLM) in Openclaw before installing
this plugin. The plugin itself adds no new outbound hop — all network traffic
goes through Openclaw's existing LLM config.

### What is captured, verbatim

The session-end extractor sub-agent and the daily consolidator read the full
transcript **un-scrubbed**. That includes:

- Full user and assistant messages
- Tool inputs, outputs, and error strings (including failures)
- Self-correction text from the assistant
- Anything pasted into the conversation

The in-session agent instructions say to redact secrets before writing to
`.reflexio/`, but the sub-agents operate on the raw transcript. If you are
about to paste credentials, tokens, private keys, PII, or otherwise sensitive
content, **disable the hook first** or tell the agent not to capture this
session.

### Where data is stored (on your machine only)

- `.reflexio/profiles/` and `.reflexio/playbooks/` — captured `.md` files in
  the current workspace
- `.reflexio/.setup_complete_<agentId>` — per-agent bootstrap marker
- `~/.openclaw/workspace/skills/reflexio-embedded/` — skill files
- `~/.openclaw/workspace/agents/reflexio-extractor.md`,
  `~/.openclaw/workspace/agents/reflexio-consolidator.md` — sub-agent defs
- `~/.openclaw/workspace/plugins/reflexio-embedded/` — prompts and scripts

No files are written outside these paths. There is no background database,
no `~/.reflexio/sessions.db`, and no outbound sync.

### Privileged install-time side effects

`./scripts/install.sh` (the only install path) makes the following
**host-wide** changes to your Openclaw install. You must approve these to use
the plugin — there is no "search-only" subset:

1. Registers this plugin via `openclaw plugins install --link`
2. **Enables the `active-memory` plugin host-wide** — affects all agents in
   your Openclaw install, not just agents that use this skill
3. **Registers a daily cron job** (`reflexio-embedded-consolidate`) that runs
   at 3am local time and spawns a sub-agent session
4. **Restarts the Openclaw gateway** at the end of install

The per-agent bootstrap (run by SKILL.md on first skill invocation) also
prompts to run `openclaw config set` against
`plugins.entries.active-memory.config.agents` and
`agents.defaults.memorySearch.extraPaths`. You can decline either; the
consequences are documented in the SKILL.md bootstrap section.

### How to disable

- **Per-session**, stop auto-capture and extraction:
  `openclaw hooks disable reflexio-embedded`
- **Per-session**, tell the agent to skip Reflexio writes — in-session Flow
  A/B will stop; still disable the hook to prevent Flow C at session end
- **Remove entirely**: `./scripts/uninstall.sh` (preserves `.reflexio/` data)
  or `./scripts/uninstall.sh --purge` (also deletes user data)
- **Stop the cron without uninstalling**:
  `openclaw cron rm reflexio-embedded-consolidate`

---


## First-Use Setup

This plugin requires a one-time install script **before** any agent can use
it. Read the Privacy, Credentials & Persistence section above first — the
install script makes host-wide changes to your Openclaw installation.

```bash
# After downloading this skill from ClawHub (or cloning the source repo):
./scripts/install.sh
```

**Prerequisites** (install script checks these):

- `openclaw` CLI on PATH
- `node` on PATH
- bash-compatible shell (macOS / Linux / WSL)

**Strongly recommended** (plugin works without them, with degraded retrieval):

- An embedding provider configured in Openclaw (OpenAI, Gemini, Voyage, or
  Mistral) — enables vector search; without it, retrieval falls back to
  FTS-only
- The `active-memory` plugin available in your Openclaw install — without it,
  you must call `memory_search` explicitly at turn start

**The plugin declares no API key of its own** — it relies on the LLM
Openclaw is already configured with for extraction and embedding. Configure a
local LLM (Ollama, LM Studio, vLLM) in Openclaw if you need fully offline
operation. See the Privacy section above for what excerpts traverse that
provider.

After install, the first time an agent uses this skill, SKILL.md runs a
one-time per-agent bootstrap that may prompt for additional `openclaw config
set` calls. You can decline; degraded modes are documented.

**Uninstall**: `./scripts/uninstall.sh` (preserves `.reflexio/`) or
`./scripts/uninstall.sh --purge` (deletes user data too). Also removes the
cron and the host-wide workspace files.

---


# Reflexio Embedded Skill

Captures user facts (profiles) and procedural corrections (playbooks) into `.reflexio/`, so the agent learns across sessions. All memory lives in Openclaw's native primitives — no external service required.

## First-time setup per agent

If `.reflexio/.setup_complete_<agentId>` does NOT exist (where `<agentId>` is your current agent id), perform this one-time check. The setup step runs probing commands via `exec` and asks for approval before making changes.

**Steps:**

1. Probe current config:
   - `openclaw config get plugins.entries.active-memory.config.agents`
   - `openclaw config get agents.defaults.memorySearch.extraPaths`
   - `openclaw memory status --deep`

2. If active-memory is not targeting this agent:
   Ask user: *"To auto-inject relevant facts into each turn, I can enable active-memory for this agent. OK if I run `openclaw config set plugins.entries.active-memory.config.agents '[\"<agentId>\"]' --strict-json`?"*
   On approval, run the command.

3. If `.reflexio/` is not registered as an extraPath:
   Ask user: *"I need to register .reflexio/ as a memory path. OK if I run `openclaw config set agents.defaults.memorySearch.extraPaths '[\".reflexio/\"]' --strict-json`?"*
   On approval, run the command.

4. If no embedding provider is configured (FTS-only mode):
   Tell user: *"Vector search requires an embedding API key (OpenAI, Gemini, Voyage, or Mistral). The plugin works without one but retrieval quality drops. Would you like guidance on adding one?"*
   If yes, guide them through `openclaw config set` or `openclaw configure`.

5. On each decline, note the degraded mode but do not block:
   - No active-memory → you must run `memory_search` explicitly at turn start (see "Retrieval" section below).
   - No extraPath → WARN the user the plugin cannot function without this step.
   - No embedding → continue with FTS-only.

6. When all checks resolved (approved or accepted with warning): create the marker:
   ```bash
   mkdir -p .reflexio
   touch .reflexio/.setup_complete_<agentId>
   ```

**If exec is not available** (strict admin policy): fall back to telling the user the exact commands to run manually.

## First-Use Initialisation

Before any write, ensure `.reflexio/` and its subdirectories exist. This is idempotent — safe to run every session:

```bash
mkdir -p .reflexio/profiles .reflexio/playbooks
```

Never overwrite existing files. Never write secrets, tokens, private keys, environment variables, or credentials into `.reflexio/` files. When capturing a fact involves a user-pasted snippet that contains credentials, redact first.

> **Redaction boundary.** The hook (Flow C) runs a best-effort regex scrub for common credential patterns (API keys, bearer tokens, PEM private keys, `*_SECRET`/`*_PASSWORD` env assignments, JWTs) on the transcript *before* it is sent to the extractor sub-agent — which may in turn call a hosted LLM provider. This is a backstop, not a guarantee. You (the agent) are still responsible for never copying secrets into `.reflexio/` writes in Flows A/B, and the user is responsible for not pasting secrets into sessions. See `SECURITY.md` for the full threat model.

## Quick Reference

| Situation                                                 | Action                                     |
|-----------------------------------------------------------|--------------------------------------------|
| User states preference, fact, config, or constraint       | Write profile via `reflexio-write.sh`      |
| User correction → you adjust → user confirms              | Write playbook via `reflexio-write.sh`     |
| Start of user turn, no Active Memory injection appeared   | Run `memory_search` fallback (see below)   |
| Unsure whether to capture                                 | Skip; batch pass at session-end has a second shot |

## Detection Triggers

### Profile signals (write immediately, same turn)

- **Preferences**: "I prefer X", "I like Y", "I don't like Z", "I always do Q"
- **Facts about self**: "I'm a [role]", "my timezone is X", "I've been doing Y for Z years"
- **Config**: "use X", "our team uses Y", "the repo is at Z"
- **Constraints**: "I'm vegetarian", "no dairy", "I can't X", "don't use Y"

For each such signal, invoke `reflexio-write.sh` with a kebab-case topic slug and an appropriate TTL. See "TTL Selection" below.

### Playbook signals (write AFTER confirmation)

Playbooks require a specific multi-turn pattern:

1. **Correction**: *"No, that's wrong"*, *"Actually..."*, *"Don't do X"*, *"Not like that"*, *"We don't use X here"*.
2. **You adjust**: you redo the work per the correction.
3. **Confirmation** (required — without this, do NOT write a playbook):
   - Explicit: *"good"*, *"perfect"*, *"yes that's right"*, *"correct"*.
   - Implicit: the user moves to an unrelated topic without re-correcting for 1-2 more turns.

**Explicit don't-write rule**: if you see a correction without subsequent confirmation, do not write a playbook. The fix may be wrong; let the batch pass at session end re-evaluate.

## Retrieval

### When Active Memory is enabled

Your turn context may already contain Reflexio-prefixed entries injected by Active Memory. Incorporate them before responding. No tool call needed.

### Fallback when Active Memory is absent

At the start of each user turn, call:

```
memory_search(query=<user's current message>, filter={type: profile|playbook})
```

Incorporate any `.reflexio/`-sourced results before responding. Skip if the user's message is trivial (greeting, acknowledgment).

## File Format

**Do NOT construct filenames or frontmatter by hand.** Use `./scripts/reflexio-write.sh` (via the `exec` tool). The script generates IDs, enforces the frontmatter schema, and writes atomically.

### Profile template (for mental model — the script emits this)

```markdown
---
type: profile
id: prof_<nanoid>
created: <ISO timestamp>
ttl: <enum>
expires: <ISO date or "never">
supersedes: [<old_id>]   # optional, only after a merge
---

<1-3 sentences, one fact per file>
```

### Playbook template

```markdown
---
type: playbook
id: pbk_<nanoid>
created: <ISO timestamp>
supersedes: [<old_id>]   # optional
---

## When
<1-sentence trigger — this is the search anchor; make it a noun phrase>

## What
<2-3 sentences of the procedural rule; DO / DON'T as actually observed>

## Why
<rationale, can be longer — reference only, not recall content>
```

### How to invoke `reflexio-write.sh`

**Profile:**

```bash
echo "User is vegetarian — no meat or fish." | \
  ./scripts/reflexio-write.sh profile diet-vegetarian one_year
```

**Playbook:**

```bash
./scripts/reflexio-write.sh playbook commit-no-ai-attribution --body "$(cat <<'EOF'
## When
Composing a git commit message on this project.

## What
Write conventional, scope-prefixed messages. Do not add AI-attribution trailers.

## Why
On <date> the user corrected commits that included Co-Authored-By trailers. Project's git-conventions rule prohibits them. Correction stuck across subsequent commits.
EOF
)"
```

## TTL Selection (profiles only)

- `infinity` — durable, non-perishable facts (diet, name, permanent preferences)
- `one_year` — stable but could plausibly change (address, role, team)
- `one_quarter` — current focus (active project, sprint theme)
- `one_month` — short-term context
- `one_week` / `one_day` — transient (today's agenda, this week's priorities)

Pick the most generous TTL that still reflects reality. When in doubt, prefer `infinity` — let dedup handle later contradictions via supersession.

## Shallow Dedup (in-session writes only)

When you are about to write a profile or playbook in-session (Flow A or Flow B), first check whether a similar one already exists:

1. Call `memory_search(query=<your candidate content>, top_k=5, filter={type})`.
2. If `results[0].similarity < 0.7` (or no results): write normally.
3. If `results[0].similarity >= 0.7`: there is a near-duplicate. Your options:
   - **Best choice**: skip the write; the existing file covers it. The session-end batch pass can revisit if needed.
   - **If you are certain the candidate supersedes the existing one**: use `--supersedes "<existing_id>"` when writing, and `rm <existing_path>` afterward. Only do this when the content is an outright replacement.

Session-end (Flow C) runs deeper dedup with an LLM merge decision. You don't need to replicate that in-session.

The daily consolidation cron runs full n-way consolidation across all files. You never need to run this yourself.

## Safety

- **Never write secrets.** No API keys, tokens, access tokens, private keys, environment variables, OAuth secrets, auth headers. If the user's message contains any of these, redact them before writing.
- **Redact pasted code.** User-pasted snippets often contain credentials. Strip them first.
- **PII.** Do not capture PII beyond what's operationally useful (name, timezone, role are fine; government IDs, addresses, phone numbers only if explicitly relevant).

## Best Practices

1. **Write immediately** on a clear signal. Don't queue to session-end — that's Flow C's job; you have a different role.
2. **One fact per profile file.** Multi-fact files are harder to dedupe and easier to contradict.
3. **Trigger phrase = search anchor.** Write `## When` as a noun phrase describing the situation, not a sentence. Retrieval hits on semantic similarity to this field.
4. **Skip writing when uncertain.** Flow C has a second pass over the full transcript. It's better to let it handle ambiguous cases.
5. **Prefer shorter TTL for transient facts.** Don't let "working on project X" accumulate as infinity-TTL cruft.

## Opt-in Hook

This skill works standalone — your in-session Flow A (profile) and Flow B (playbook) writes populate `.reflexio/` without any hook.

The optional hook (`hook/` directory of this plugin) adds two capabilities:

1. **TTL sweep at session start**: deletes expired profiles before Active Memory runs.
2. **Session-end batch extraction (Flow C)**: on `session:compact:before`, `command:stop`, or `command:reset`, spawns a `reflexio-extractor` sub-agent that extracts profiles/playbooks from the full transcript and runs shallow pairwise dedup.

See this plugin's `README.md` for install instructions (runs via `./scripts/install.sh`). If the hook is not installed, Flows A+B still work.
