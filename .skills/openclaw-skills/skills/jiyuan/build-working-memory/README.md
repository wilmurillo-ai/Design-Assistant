# Working Memory System for AI Agents

A file-based memory architecture that gives AI agents a sense of continuous identity across sessions.

## Architecture

```
project-root/
├── MEMORY.md                  # Curated long-term memory (distilled, reviewed)
├── RETRIEVAL.md               # Retrieval workflow documentation
├── loader.py                  # Session-start memory loader (four-phase)
├── writer.py                  # Session-end memory writer
└── memory/
    ├── resumption.md          # First-person handoff note for next session
    ├── threads.md             # Ongoing topics with state and momentum
    ├── state.json             # Machine-readable ephemeral state
    ├── index.md               # Daily log index for fast retrieval
    ├── archive.md             # Demoted long-term memories
    └── YYYY-MM-DD.md      # Raw session logs (episodic, conversational)
```

## Session Lifecycle

### On Start (loader.py)
```
Phase 1: Orient     →  state.json                ~200 tokens, always
Phase 2: Anchor     →  resumption.md             ~300 tokens, always
Phase 3: Context    →  MEMORY.md + threads.md    ~1500 tokens, conditional
Phase 4: Deep Recall →  daily logs + archive      variable, on-demand
```

Loading adapts to context:
- **< 2h gap**: Light — just resumption.md, skip Phase 3
- **2-24h gap**: Standard — Phases 1-3 based on user's opening message
- **1-7 days**: Full reload — add recent daily logs
- **7+ days**: Deep reload — all phases, treat resumption as potentially stale

Phase 3 branches by signal:
- **Known thread detected**: Load that thread + relevant MEMORY.md section
- **New/ambiguous topic**: Load full MEMORY.md + all thread headers
- **Maintenance due**: Load MEMORY.md + recent daily log summaries for curation

See RETRIEVAL.md for full specification.

### During Session
- Update `memory/threads.md` if new ongoing topics emerge
- Note decisions and their reasoning as they happen
- Track open questions that surface

### On End (writer.py)
1. Write/append to `memory/YYYY-MM-DD.md` → raw session log
2. Update `memory/threads.md` → advance thread positions
3. Update `memory/state.json` → snapshot current state
4. Write `memory/resumption.md` → first-person handoff to next session
5. Periodically: review and curate `MEMORY.md` (promote, merge, demote)

## Usage

```python
from loader import MemoryLoader
from writer import MemoryWriter

# --- Session start ---
loader = MemoryLoader("./")
context = loader.load_session_context(user_message="Let's continue the design")
# Inject context.text into the agent's system prompt

# --- During session ---
writer = MemoryWriter("./")
writer.note_decision("Chose X over Y", "reason...")
writer.note_open_question("Should we also consider Z?")
writer.note_thread_touched("thread-wm-design")

# --- Session end ---
writer.end_session(
    session_summary="Worked on retrieval workflow...",
    resumption_note="We just finished the loader. Yuan will want to test it...",
    thread_updates={"thread-wm-design": {"current_position": "Retrieval done."}},
    mood="productive",
)
```

## Design Principles

- **Separation of concerns**: Raw logs vs. curated memory vs. active threads
- **Decay and refresh**: Memories strengthen through recall, weaken through neglect
- **Cross-referencing**: Bidirectional links between logs, threads, and long-term memory
- **Decisions over facts**: Capture *why*, not just *what*
- **First-person continuity**: resumption.md creates subjective anchor points
- **Machine + human readable**: state.json for fast parsing, markdown for rich context
