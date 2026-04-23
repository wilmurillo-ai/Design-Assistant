# M*A*L*P Tasks

## NOTES.txt conventions

`NOTES.txt` is a living scratchpad, not a log. It should shrink over time.

### Open questions format

Use checkbox format for open questions and tasks:

```
- [ ] Unresolved item — describe what needs to be determined or done.
- [x] Resolved item — brief description. → What was decided or found.
```

- Open items use `- [ ]`.
- Closed items use `- [x]` and append ` → <resolution>` inline so the decision is visible alongside the item.
- Closed items can remain briefly for context, but should be pruned once the resolution is formalized elsewhere (README, committed code, etc.).
- **Pruning signal**: more than ~10 resolved items means it's time to prune. Remove resolved items whose resolutions are already captured in committed files.

### Exit criteria section

Every `NOTES.txt` should include an explicit **Exit criteria** section near the top:

```
Exit criteria
-------------
Before this work is considered done, each note here should be one of:
- formally documented in a committed file (README, code, etc.)
- checked off as solved
- removed because it is no longer relevant
```

The goal is for `NOTES.txt` to shrink toward empty as work matures. If it keeps growing, that's a signal that items aren't being resolved or formalized.

### What belongs in NOTES.txt

- Open questions and unresolved decisions
- Tribal knowledge not yet in committed files (tag provenance: "Per Alice:", "Bob notes:", etc.)
- Working context (partial findings, hypotheses, things to verify)
- Design philosophy and intent not obvious from the code
- Cross-references to related malps (e.g., "See also: `../related-project/.malp/NOTES.txt`")

Cross-references are pointers, not permission. By default, read only the `.malp` the user asked for. If another `.malp` looks relevant, ask before reading it or bringing it into context. Example: if one malp says `See also: ../related-project/.malp/NOTES.txt`, do not open that file unless the user says to.

### What does NOT belong

- Resolved items with no pending follow-up (prune these)
- Content already formalized in README or committed code
- Raw logs or meeting notes (summarize the actionable parts)
- Credentials or secrets (reference where they live instead). If secrets are already present and the path is inside a git repo, proactively recommend an ignore strategy — see `repo-strategies.md`.

### SUMMARY.txt depth

Scale with the directory:
- **Leaf project / small tool** — a paragraph: what it is, how to run it, one or two key details.
- **Larger project** — structured sections: what it is, architecture, tech stack, key files.
- **Monorepo root** — directory structure, tech stack, key paths, recent activity.

## `what malps do we have?`

When the user asks `what malps do we have?` or an equivalent discovery request:

1. Read `~/.malp-home/MAP.txt`.
2. If `~/.malp-home/TAGS.txt` exists, read it too and use it only to surface user-defined tags alongside matching malp paths.
3. Summarize the available `.malp` paths in a short list.
4. If the map is empty or missing, say so plainly.
5. Ask the user which `.malp` they want to open.
6. When the user chooses one, read that `.malp` and summarize the relevant contents or follow-up instructions.

`TAGS.txt` is optional and user-maintained. Do not add tags automatically. Use one line per malp in this format:

```
backend,legacy:/full/path/to/.malp
```

Keep explanatory or disabled lines commented out with `#`.

## `lets send malp to <path>`

When the user says `lets send malp to <path>`:

1. Create a `.malp` directory inside `<path>`.
2. Perform a quick summary of the contents of `<path>`.
3. Write the summary to `.malp/SUMMARY.txt`. Scale depth to directory complexity.
4. Keep `.malp/NOTES.txt` as the primary workspace for project-local progress, problems, design philosophy, and tribal knowledge.
5. Keep `SUMMARY.txt` up to date as the concise overview of `<path>` itself, using `<path>/.malp/NOTES.txt` for context when helpful.
6. Remove items from `NOTES.txt` as they are solved or formalized in `<path>`.
7. After a new `.malp` has been created, maintain `~/.malp-home/MAP.txt` as a newline-delimited list of every `.malp` directory path created so far; primarily append new paths and leave old ones in place.
8. If a `.malp` already exists for `<path>`, verify whether `SUMMARY.txt` still fits the current contents, verify that `MAP.txt` still references the path, refresh the summary if needed, and report that the existing `.malp` was refreshed.
9. Reply to the user with the summary.
10. Do **not** proactively raise version control concerns about `.malp/`. See `repo-strategies.md` if the user asks.

## Staleness and retirement

- If a malp's NOTES are mostly resolved and it hasn't been touched recently, suggest retirement.
- Retirement means removing the path from `MAP.txt` and optionally deleting the `.malp/` directory.
- Don't retire without asking — the user may want to keep it for historical context.
