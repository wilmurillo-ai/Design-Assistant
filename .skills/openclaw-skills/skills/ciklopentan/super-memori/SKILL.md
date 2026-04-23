---
name: super-memori
description: >
  Local-first hybrid memory skill for OpenClaw agents. Use when the agent needs to find, recall, search, or reuse past knowledge across
  episodic, semantic, procedural, and learning memory; when the user asks things like "what did we do about X", "remember", "find in memory",
  "что мы делали", or "найди в памяти"; when exact match and meaning-based recall both matter; or when designing, operating, or improving
  long-term agent memory on a local Ubuntu host. Includes manual-review learning improvement surfaces and memory-health guidance for degraded-mode detection,
  backup awareness before major operations, and risk-aware memory changes. Optimized for weak models by exposing a small command surface and clear degraded-mode rules.
---

# Super Memori — v4.0.0-candidate.25 Project Skill

**Release line:** `v4.0.0-candidate.25` pre-release for the current-generation local-only memory runtime.

**Release-line truth boundary:** the release line identifies the packaged skill artifact, not the live freshness state of whatever host runs it later. Current host freshness, semantic readiness, degraded state, and authority limits must be read from live command outputs such as `./health-check.sh --json` and `./query-memory.sh ... --json` at use time, not inferred from the release label alone.

**Runtime prerequisites:** Semantic / hybrid retrieval is now implemented in the runtime, but it only becomes active on hosts where local semantic prerequisites are actually present: `sentence-transformers`, `numpy`, a locally available embedding model, local Qdrant, and vectors built from canonical files. Without them, the skill remains operational in lexical/degraded mode and surfaces that state explicitly.

**Status:** v4 local-only memory runtime with real lexical, semantic, hybrid, temporal-relational, audit, and change-memory machinery in code, plus maintenance-only learning improvement / pattern-mining surfaces. Host state still matters: a host can run this release in lexical-only/degraded mode if semantic prerequisites or vector build state are missing.

## Current truth snapshot
- Lexical retrieval: active.
- Semantic / hybrid runtime: implemented in code, host-dependent.
- Change-memory: implemented and live.
- Change-audit integration: implemented and live.
- Minimal hot-change-buffer: implemented, internal, recovery-only.
- Current candidate-host validation snapshot: degraded/stale conditions may exist on the host used for the latest validation pass; treat those as host-scoped validation evidence, not as artifact-wide freshness truth.
- Overall release state: candidate, not stable.

## Host profiles
- `current-degraded-host` — safe-first, degraded-aware, no destructive auto-actions by default.
- `future-equipped-host` — stronger semantic / audit / index verification allowed, but still truth-tracked and rollback-aware.

## OpenClaw quickstart for weak models
If you need the shortest safe operating path under OpenClaw, use this order and do not improvise extra steps:
1. `cd ~/.openclaw/workspace/skills/super_memori`
2. `./health-check.sh --json`
3. If status is `FAIL` → stop.
4. If status is `WARN` → continue only in degraded mode and trust the returned warnings/checks.
5. For first query: `./query-memory.sh "<your query>" --mode auto --json`
6. Trust `mode_used`, `degraded`, `warnings`, `semantic_ready`, and `index_fresh`.
6a. Also trust `authoritative_result_present`, `low_authority_only`, and each result's `match_authority` when they are returned. They tell you whether the answer contains confirmed exact/hybrid memory or only heuristic/fallback matches.
7. Use `./memorize.sh` only for reusable lessons.
8. Use `./index-memory.sh` only when the contract below tells you to refresh or repair freshness.

This quickstart does not guarantee semantic-ready operation on every host. It gives the strongest safe first path on OpenClaw while keeping degraded truth explicit.

## OpenClaw host setup (weak-model executable)
Use this only when preparing `super-memori` on an OpenClaw host for first use or when rebuilding local prerequisites. Execute the steps in order.

### 1. Enter the skill directory
```bash
cd ~/.openclaw/workspace/skills/super_memori
```

### 2. Confirm Python is available
```bash
python3 --version
```
Expected: Python is installed and callable as `python3`.

### 3. Optional: install semantic prerequisites for fuller local capability
```bash
pip3 install --user sentence-transformers numpy qdrant-client
```
Note: this installs only the Python client library; it does not install or start the Qdrant database service. Vector search will remain inactive until a reachable local Qdrant service is running and accessible.
If this step fails, the skill can still run in degraded lexical-only mode and will report that state honestly.

### 4. Build or refresh local indexes
```bash
./index-memory.sh --full --json
```
If semantic prerequisites are still unavailable, this may complete in degraded mode. Report that honestly; do not pretend semantic readiness.

### 5. Verify host health
```bash
./health-check.sh --json
```
Expected result:
- `OK` = normal operation
- `WARN` = degraded but usable operation
- `FAIL` = stop and escalate to maintenance

### 6. Run a first real query
```bash
./query-memory.sh "test query" --mode auto --json --limit 3
```
Confirm that the output includes at least `mode_used`, `degraded`, `warnings`, and `results`.

### 7. Return to the normal operating contract
After setup, follow only the four public commands and the `FOR ALL MODELS — REQUIRED OPERATING CONTRACT` below.

## Change-memory authority boundary
- Change-memory records are operational truth about agent-made changes.
- A minimal internal hot-change-buffer may hold very recent recovery-only state for recent agent-made changes, but it is not canonical truth.
- Neither durable change-memory nor the hot-change-buffer replaces direct live filesystem / service / package inspection when exact current machine state is required.
- `reverted` or `unverified` records must not be presented as active current state.

## Change-memory truth
- Supports structured change records.
- Supports `applied`, `failed`, `reverted`, and `unverified` distinctions.
- Supports current known state and recall bundle.
- Supports a minimal internal hot-change-buffer for very recent recovery-only agent-made changes.
- Does not claim destructive auto-actions by default.

## Minimal hot-change-buffer
- Internal only, not a public command.
- Recovery-only for very recent agent-made changes.
- Non-canonical and non-durable.
- Must not override direct live inspection or change-memory truth.

## Current host limitations
- The latest validation host snapshot is host-scoped evidence, not artifact-wide truth. Confirm the live host state with `./health-check.sh --json` instead of inferring it from this document alone.
- `system_hygiene` on the latest validation host may still be stale / partial-visibility; do not read that as a clean-health signal and do not generalize it to every host that installs this release.
- Minimal hot-change-buffer is enabled in safe-first mode only: RAM-resident, circular-buffer, recovery-only, non-canonical, non-durable, and aggressively noise-filtered.
- This is not a blocker for change-memory.
- Destructive auto-actions remain disabled by default.

## Current blocker classification
- Blocking for current candidate line: none currently known.
- Non-blocking unresolved (separate from change-memory candidate): the latest validation host may still show stale / partial-visibility `system_hygiene`; treat that as host-scoped degraded evidence rather than a clean-health signal or artifact-wide invariant.

## Truth precedence
### For current machine state
1. Canonical files and direct live inspection
2. Lexical index
3. Semantic / vector index when healthy
4. Learning memory
5. Inferred recall last

### For agent-made change history
1. Change-memory records
2. Change-audit integration
3. Canonical files that directly confirm the current result
4. Inferred recall last

Never let inferred, stale, degraded, or retrieval-only surfaces override canonical truth.

## Change-memory noise policy
- Do not log harmless reads as change-memory.
- Log only state-changing actions, failed writes, risky cleanup, package/service/config/runtime changes, and rollback events.

## Instructions

## RUNTIME CAPABILITY MATRIX (v4.0.0)

| Capability | Implementation status | Host requirement |
|---|---|---|
| Lexical search (SQLite FTS5) | **Implemented** | Always available |
| Learning-memory retrieval | **Implemented** | Always available |
| Semantic embeddings | **Implemented** | `sentence-transformers` + `numpy` + local model files |
| Vector search (Qdrant local) | **Implemented** | Local Qdrant reachable + vectors built |
| Hybrid fusion (RRF) | **Implemented** | Semantic stack ready |
| Temporal / relation-aware rerank | **Implemented** | Semantic or temporal rerank path selected |
| Integrity audit | **Implemented** | Local lexical DB available |
| Pattern mining (block-level) | **Implemented** | `.learnings` populated |
| Change-memory records | **Implemented** | Always available |
| Change-audit integration | **Implemented** | Always available |
| Optional semantic-ready host state | **Optional host capability** | Semantic deps + local model + vectors built |

## IMPLEMENTED VS OPTIONAL VS HOST-STATE TRUTH
- **Implemented now in code:** lexical search, semantic search, hybrid fusion, temporal-relational rerank, integrity audit, relation-aware write metadata, block-level pattern mining, change-memory capture, change-audit integration, and a minimal internal recovery-only non-canonical non-durable hot-change-buffer.
- **Optional host state:** semantic embeddings, vector search, and hybrid selection only activate when local semantic dependencies/model/vector state are actually ready.
- **Not implemented / not claimed:** cloud backends, remote embeddings endpoints, remote vector DB, auto-promotion into durable memory, internet-dependent memory runtime, destructive auto-actions by default.

## FOR ALL MODELS — REQUIRED OPERATING CONTRACT

### Public commands
- `./query-memory.sh`
- `./memorize.sh`
- `./index-memory.sh`
- `./health-check.sh`

### Maintenance-only entrypoint
- `./audit-memory.sh` — human/maintenance integrity audit; do not add it to the normal weak-model command loop unless maintenance is explicitly requested.

### Weak-model operating rules
1. Default to `./query-memory.sh --mode auto`. The script will choose the strongest available local path and will report what actually ran via `mode_used`.
2. Trust the returned `mode_used`, `degraded`, `warnings[]`, `semantic_ready`, `semantic_fresh`, `index_fresh`, `authoritative_result_present`, and `low_authority_only` fields. Do not infer stronger capability than the payload states.
3. `--mode semantic` and `--mode hybrid` are now real implemented runtime modes. They are no longer compatibility stubs. Weak models still should prefer `auto` unless the task clearly requires a forced semantic/hybrid retrieval query.
4. If `--mode semantic` or `--mode hybrid` is requested on a host where the runtime reports `semantic_ready=false` or otherwise returns `degraded=true`, do not pretend semantic execution succeeded. Trust the returned `mode_used` and warnings: the request may honestly degrade to the strongest available local lexical path on this host. In that case, report the degraded lexical outcome as such and do not describe the result as semantic or hybrid retrieval. **Exception:** if the same payload also reports `index_fresh=false` (or `index_stale=true`) together with semantic unavailability, this rule no longer grants lexical fallback authority; defer to the Health & Safety Gate combined degraded-state rule and present the result only as a non-authoritative degraded match.
5. For the lowest-friction safe path, weak models should think in this order: `health-check -> query(auto) -> read returned fields -> only then decide whether memorize or index is needed`.
6. `--mode learning` remains a learning-memory-oriented retrieval lane, but it now sits on top of the stronger v4 retrieval stack and still reports its true `mode_used` honestly.
7. Use `memorize.sh` only for reusable lessons that should influence future behavior. Do not log expected misses, one-off noise, duplicate lessons, or `checked, nothing relevant`.
8. Relation targets in `memorize.sh` are canonical, not freeform. Use only `learn:<signature>`, `chunk:<chunk_id>`, or `path:<canonical_path>` relation targets.
9. Do not execute internal helper scripts or reason about backend selection manually during normal use. The runtime owns retrieval choice; you consume the structured output.

### Health & Safety Gate
- **OK** → proceed normally.
- **WARN** → state: `⚠️ MEMORY DEGRADED: <reason>. Results are partial.` You may continue only if you acknowledge the degradation limits. For write or maintenance continuations, also say: `⚠️ Continuing in degraded mode. Rollback path: <git/backup>.` For read-only degraded queries, state the degradation and fallback scope, then proceed without requiring a rollback path.
- If semantic dependencies are unavailable but lexical freshness is still OK, lexical/index-backed results remain authoritative for exact/path/time-style matches, but do not describe them as semantic or meaning-based retrieval.
- If `authoritative_result_present=false` and `low_authority_only=true`, treat returned matches as heuristic/fallback assistance only, not confirmed memory truth, even when the query still returned usable degraded results.
- If `WARN` is caused by a stale lexical index, also say: `⚠️ Memory index may be stale. Results may miss recent changes. Consider running ./index-memory.sh.` In that stale-lexical-only case, indexed results remain usable but freshness-limited; do not present them as fully current.
- If `index_stale=true` (or `index_fresh=false`) **and** semantic dependencies are unavailable in the same WARN state, rely only on the degraded results surfaced by `./query-memory.sh`; treat them as non-authoritative degraded matches only, not fresh indexed truth and not semantic matches. Do not present them as lexical truth or as `the best available answer`; lexical authority is revoked in this combined degraded state. Do not invent manual retrieval steps outside the four public commands. State: `⚠️ MEMORY DEGRADED: index stale, semantic unavailable. Results from query-memory fallback only. Missing recent changes and meaning-based matches. Run ./index-memory.sh and restore semantic prerequisites to resolve.` In JSON-capable outputs, mandatory degraded notices must live inside structured warning fields rather than outside the payload.
- Do not treat every `warnings[]` note as a degraded retrieval result. Informational notes may appear even when the current request was satisfied exactly as designed; rely on the script's `degraded` field and exit code, not on the mere presence of warning text.
- Queue/backlog WARN states do not by themselves disable read/query authority, but they do require reporting that recent learnings or pending index work may not yet be reflected.
- **FAIL** → stop. Output: `❌ MEMORY UNAVAILABLE: health check FAIL.` Do not query, memorize, or edit memory files.

### Interpreting `query-memory.sh` exit codes
After running `./query-memory.sh`, you MUST check the exit code and act accordingly:

| Exit Code | Meaning | Permitted Action |
|-----------|---------|------------------|
| `0` | Results found, stack healthy. | Use results normally. |
| `1` | No results found. Check `degraded` and `warnings[]` to tell whether this was a clean miss or a degraded no-results outcome. | **First, inspect `degraded`.** If `degraded=true`, state: `⚠️ Degraded search found no entries for this query. Results may be incomplete.` If `degraded=false`, state: `No memory entries found for this query.` If the payload reflects the combined stale-index + semantic-unavailable WARN state, override the generic degraded phrasing above and use the exact degraded notice from the Health & Safety Gate WARN section so the lexical-authority revocation rule remains explicit. Outside that combined-state override, use returned `warnings[]` to surface any freshness-relevant notes such as queue/backlog delay, stale lexical index, or similar recent-changes-may-be-missing warnings. Do **not** treat exit code `1` as an automatic stack failure. |
| `2` | Degraded but usable results returned. | State degradation explicitly using the query response itself (`degraded=true`, `warnings[]`, `authoritative_result_present`, and `low_authority_only`). Do **not** treat this as a clean success. |
| `3` | Retrieval stack unavailable. | **STOP.** State: `❌ MEMORY UNAVAILABLE: Cannot search memory at all.` Do **not** continue as if this were a clean no-results case. Escalate to human maintenance. |
| `4` | Bad arguments provided to script. | **STOP.** State the argument error and re-evaluate the command. |
| `5` | Internal script error. | **STOP.** State: `❌ MEMORY INTERNAL ERROR.` Escalate to human maintenance. |

**CRITICAL:** Do not confuse exit code `1` (clean miss) with exit code `3` (broken retrieval stack). The former is normal operation; the latter requires immediate escalation.

### Interpreting `memorize.sh` exit codes
After running `./memorize.sh`, you MUST check the exit code and act accordingly:

| Exit Code | Meaning | Permitted Action |
|-----------|---------|------------------|
| `0` | Learning was written successfully, or an exact duplicate was safely skipped. | State success honestly. Do **not** retry a duplicate write as if persistence failed. |
| `4` | Bad arguments provided to script. | **STOP.** State the argument error and re-evaluate the command. |
| `5` | Internal script error. | **STOP.** State: `❌ MEMORY INTERNAL ERROR.` Escalate to human maintenance. |

If you need machine-readable confirmation, prefer `./memorize.sh --json ...` and inspect its `status` field (`written` vs `duplicate`) instead of inventing extra exit-code meanings.

### Interpreting `health-check.sh` exit codes
After running `./health-check.sh`, you MUST check the exit code and act accordingly:

| Exit Code | Meaning | Permitted Action |
|-----------|---------|------------------|
| `0` | Overall status is `OK`. | Proceed normally. |
| `2` | Overall status is `WARN`. | Follow the WARN protocol from the Health & Safety Gate above. |
| `3` | Overall status is `FAIL`. | **STOP.** State: `❌ MEMORY UNAVAILABLE: health check FAIL.` Do not continue with memory edits or retrieval-dependent work. |
| `4` | Bad arguments provided to script. | **STOP.** State the argument error and re-evaluate the command. |
| `5` | Internal script error. | **STOP.** State: `❌ MEMORY INTERNAL ERROR.` Escalate to human maintenance. |

If you need machine-readable status decisions, prefer `./health-check.sh --json` and inspect structured `status`, `warnings`, and `checks[]` fields rather than guessing from free text.

### Interpreting `index-memory.sh` exit codes
After running `./index-memory.sh`, you MUST check the exit code and act accordingly:

| Exit Code | Meaning | Permitted Action |
|-----------|---------|------------------|
| `0` | Requested indexing/maintenance action completed without warnings. | Continue normally. |
| `2` | Action completed with warnings or expected degraded conditions. | Report the warning state explicitly. Treat indexing as usable-but-degraded until the warning cause is resolved. On lexical-only hosts, `--rebuild-vectors` returning `2` because semantic dependencies are unavailable is an expected degraded outcome, not an unexpected hard failure. |
| `3` | Index maintenance failed at the storage/runtime layer. | **STOP.** State: `❌ MEMORY UNAVAILABLE: index maintenance failed.` Escalate to human maintenance. |
| `4` | Bad arguments provided to script. | **STOP.** State the argument error and re-evaluate the command. |
| `5` | Internal script error. | **STOP.** State: `❌ MEMORY INTERNAL ERROR.` Escalate to human maintenance. |

If you need machine-readable details, prefer `./index-memory.sh --json` and inspect `actions[]`, `warnings[]`, and any mode-specific fields returned by the script.

### Before any script / policy / index edit (modifying files) or before using `./memorize.sh` for a high-value lesson you want durably recorded
1. Run `./health-check.sh` directly and enforce the Health & Safety Gate above. Do not invoke these public script entrypoints with `bash <script>`.
2. Verify rollback exists (`git status`, backup directory, or untouched canonical files).
3. If status is `WARN`, proceed only with explicit degraded-mode awareness and the rollback path stated.
4. Do not expand the maintenance block below unless you are doing human-led maintenance or this skill explicitly tells you to read it.
5. If rollback is unclear, abort and escalate to human maintenance.

### Deterministic fallback
- If a request does not clearly map to the four public commands or the explicit maintenance path, reply: `Out of scope for super-memori v4 local-only runtime. Please specify which command to run or escalate to human maintenance.` After running a public command, follow the exit-code interpretation rules above exactly.
- If you are unsure whether information qualifies for `memorize.sh`, default to not memorizing.

## Maintenance Reference
For retrieval pipeline contracts, write/learning contracts, promotion rules, maintenance entrypoints, release gates, and anti-patterns, see [`references/maintenance.md`](references/maintenance.md).
