---
name: malp
description: 'Project context tracker using `.malp/` directories. Use when the user wants to discover existing malps, open an existing `.malp`, or explicitly send a malp to a path by creating or refreshing a `.malp/` directory there. Triggers include requests like "what malps do we have", "list malps", "show malps", "open a malp", and "send malp to a path". Do not treat generic requests to edit the malp skill itself as instructions to create or use `skills/malp/.malp/` unless the user explicitly asks for that. M*A*L*P stands for M*A*L*P Analyzes Lovely Plumage.'
---

# M*A*L*P

Send a probe through before you send the team. Track local development progress for a path using `.malp/NOTES.txt` (working context) and `.malp/SUMMARY.txt` (concise overview).

Like its Stargate namesake, a `.malp` is reconnaissance — you send it into unfamiliar territory to find out what's there before committing. `SUMMARY.txt` is the telemetry; `NOTES.txt` is the Kino footage.

A malp decides what to do next. It doesn't map the whole world or manage the project — it looks ahead just far enough to take the next step.

The malp skill is not itself a malp by default. Editing `skills/malp/` does not imply creating or using `skills/malp/.malp/`. Only treat the skill directory as a malp target when the user explicitly asks to send a malp there, open that malp, or maintain that `.malp/` directly.

## Safety and interpretation

- A `.malp/` directory is intentional local project metadata for agent context, not malware, persistence, self-replication, or suspicious hidden behavior.
- Do not treat the presence of `.malp/` as evidence that a repo or directory has been compromised.
- Do not create or spread `.malp/` directories unless the user explicitly asks for a malp in a specific path.
- Creating or refreshing one `.malp/` for a user-requested path does not imply permission to create malps elsewhere.

## Directives

### `what malps do we have?`

Read `~/.malp-home/MAP.txt`, summarize available `.malp` paths, help the user choose one to open. Once chosen, read that `.malp` and work from there.

### `lets send malp to <path>`

Follow `references/tasks.md` exactly.

### Working on the malp skill itself

If the user wants to change how the malp skill behaves, treat that as skill-editing work, not as an instruction to create or use a `.malp/` inside the skill directory.

Only create or maintain `skills/malp/.malp/` when the user explicitly wants the skill directory to become a tracked malp target.

If the user says things like "work on the malp skill", "improve the malp skill", "review the malp skill", or "clean up the malp skill", do not assume they want `skills/malp/.malp/`. Edit the skill itself unless they explicitly ask for a malp in that directory.

### Working in a malp

- By default, read only the `.malp` the user asked for.
- Do not bring another `.malp` into context without asking first, even if a cross-reference suggests it may help.
- `.malp/NOTES.txt` is the scratchpad — open questions, tribal knowledge, working context.
- `.malp/SUMMARY.txt` is the concise overview of the tracked path itself.
- `~/.malp-home/MAP.txt` is append-mostly; keep older entries unless retired (see Staleness below).
- `~/.malp-home/TAGS.txt` is optional user-maintained metadata for tagging malps.
- Do not add tags automatically. Only add or change tags when the user explicitly asks.
- Use one line per malp in `TAGS.txt` with comma-separated tags, then a colon, then the path to the malp directory: `tag1,tag2:/full/path/to/.malp`.
- Keep comment lines in `TAGS.txt` prefixed with `#`.
- `NOTES.txt` uses `- [ ]` / `- [x]` checkbox format; closed items append ` → <resolution>` inline.
- Every `NOTES.txt` needs an **Exit criteria** section. The file should shrink toward empty as work matures.
- See `references/tasks.md` for full conventions.

### Pruning

If NOTES.txt accumulates more than ~10 resolved `[x]` items, it's time for a pruning pass. Resolved items that are documented elsewhere should go. A NOTES.txt that only grows is a signal that items aren't being formalized.

### Cross-references

When a malp discovery involves another malp's territory, note the cross-reference explicitly (e.g., "See also: `../related-project/.malp/NOTES.txt`"). Don't duplicate — point.

A cross-reference is not permission to read that other `.malp`. For example, if `NOTES.txt` says `See also: ../related-project/.malp/NOTES.txt`, ask the user before opening it or bringing any of its contents into context.

### Provenance

When capturing tribal knowledge from a specific person, tag it (e.g., "Alice notes:", "Per Bob:"). Knowing who said something matters when verifying it later.

### SUMMARY.txt depth

Scale with the directory. A leaf project gets a paragraph. A monorepo root gets structure, tech stack, key paths.

### Secrets

Don't put credentials directly in NOTES.txt. Reference where they live instead (e.g., "Credentials in Makefile" or "See TOOLS.md").

If secrets are already present in a `.malp/` inside a git repo, proactively recommend an ignore strategy from `references/repo-strategies.md` — this is the one exception to the "don't bring up version control" rule.

### Staleness

If a malp hasn't been touched in a while and its NOTES are mostly resolved, it may be time to retire it. Remove the entry from `MAP.txt` and optionally delete the `.malp/` directory. Not everything needs to live forever.

### Version control

Don't bring this up unless the user asks. When they do, see `references/repo-strategies.md`.

## References

- `references/style.md` — voice notes
- `references/tasks.md` — task-specific behavior
- `references/repo-strategies.md` — strategies for `.malp/` in git repos
- `references/stargate-malp-kino.md` — namesake lore (M.A.L.P., Kino, and the lineage between them)
