---
name: cross-check
description: "Inline assumption checker that challenges your agent's thinking before responding. Extracts assumptions, sends them to a verifier model (or runs independent rounds with same model), identifies blind spots, missing perspectives, and logical flaws. Always asks before activating. Includes pre-mortem risk analysis, dialectical inquiry, and multi-perspective synthesis. Works immediately with no setup using your existing model, or with a second model for stronger verification. Stateless, no file I/O, no data persistence. Use when: (1) 'cross-check this', (2) 'challenge your assumptions', (3) 'am I missing something?', (4) complex decisions, (5) long prompts where accuracy matters, (6) 'get a second opinion', (7) 'stress-test this idea'. Homepage: https://clawhub.ai/skills/cross-check"
---

# Cross-Check

Inline assumption verification and multi-perspective analysis. Catches flawed reasoning before it reaches you.

## Language

Detect from the user's message language. Default: English.

## How It Works

Cross-Check never activates automatically. When a query is identified as suitable, the agent presents a one-time choice:

```
This query looks like a candidate for Cross-Check verification:
- It involves [complex reasoning / a decision / multiple assumptions]
- Verification could improve accuracy by [specific benefit]

Activate Cross-Check? [Yes / No]

  🔵 Reinforced Mode (your current model, 3 independent rounds)
  🟢 Cross-Check Mode (requires a second configured model)
```

**The user always chooses.** If they say no, the agent proceeds normally.

## Detection Criteria

Suggest Cross-Check when the query involves:

- Multiple interdependent assumptions
- A decision with significant consequences
- Claims that could be factually wrong
- Complex analysis with many moving parts
- Strategic planning or architecture decisions
- The user explicitly asks: "cross-check", "challenge this", "second opinion", "am I missing something?"

**Do NOT suggest** for: simple factual lookups, short questions, casual conversation, or queries already answered with high confidence.

---

## Mode A: Reinforced Thinking (1 model, zero setup)

Uses the user's current model. Runs 3 independent rounds, each starting from scratch.

### Round Structure

```
Round 1 — "The Analyst"
  Task: Solve the problem with maximum effort.
  Constraint: Produce a complete, final answer.
  Output: Answer + explicit list of ASSUMPTIONS made.

Round 2 — "The Challenger"
  Task: Solve the same problem again from scratch.
  Input: The problem only (NOT Round 1's answer).
  Constraint: Deliberately explore different angles.
  Output: Answer + assumptions.

Round 3 — "The Synthesizer"
  Task: Solve again, but now with BOTH previous rounds visible.
  Input: Problem + Round 1 answer + Round 2 answer.
  Constraint: Identify where they agree (likely correct), where they disagree (needs resolution), and what both missed (blind spot).
  Output: Final answer + synthesis notes.
```

### Assumption Tracking (each round)

Every round must explicitly state:
1. **Core assumptions** — What facts does this answer depend on being true?
2. **Confidence level** — High / Medium / Low for each assumption
3. **Unknowns** — What information is missing that could change the answer?
4. **Biases to watch** — What biases might be influencing this reasoning?

### Pre-Mortem Integration (Round 3)

In the final round, the synthesizer runs a quick pre-mortem:

```
"Imagine this answer is completely wrong. What would be the most likely reasons?"
List 3-5 failure modes, then check if the current answer is vulnerable to any.
```

### Synthesis Output Format

```
## 🔵 Cross-Check Result (Reinforced Mode)

### Consensus (all 3 rounds agree)
- [finding 1]
- [finding 2]

### Divergence (rounds disagreed)
- Round 1 said X, Round 2 said Y → Resolution: [Z]
- [reasoning for why Z is stronger]

### Blind Spots (identified in Round 3)
- [thing neither Round 1 nor Round 2 considered]

### Assumption Audit
| Assumption | R1 Confidence | R2 Confidence | R3 Verdict |
|-----------|:---:|:---:|:---:|
| [assumption] | High | Medium | ✅ Confirmed |
| [assumption] | Medium | Low | ⚠️ Uncertain |
| [assumption] | High | High | ❌ Challenged |

### Pre-Mortem
- Risk: [potential failure] — Mitigated by [action]
- Risk: [potential failure] — Not mitigated

### Final Answer
[revised answer incorporating all findings]
```

---

## Mode B: Cross-Check (2 models, stronger verification)

Uses a second model as an independent verifier. Best when the user has multiple providers configured.

### Flow

```
Step 1 — Primary Model: "The Analyst"
  Solve the problem fully.
  Extract: Assumptions + confidence levels + unknowns.

Step 2 — Verifier Model: "The Adversary"
  Input: "Here is another model's answer to this problem:
  [primary answer + assumptions + confidence levels]
  
  Your job:
  1. Challenge each assumption — is it valid? What contradicts it?
  2. Find blind spots — what perspectives are missing?
  3. Identify logical fallacies or biases
  4. Propose alternative interpretations
  5. Rate each assumption: Valid / Questionable / Wrong"
  
  Output: Challenges + alternative perspectives + revised confidence ratings.

Step 3 — Primary Model: "The Integrator"
  Input: Original answer + verifier challenges.
  Task: Revise the answer. Be honest about what was wrong.
  
  Output: Revised answer + change log.
```

### Dialectical Inquiry Integration

Borrowed from adversarial decision theory. The verifier must:

1. **Invent counter-assumptions** — For each primary assumption, construct a plausible scenario where it is false
2. **Search for the "Third Path"** — Not just "agree or disagree" but "what's a better option neither considered?"
3. **Stress-test with pre-mortem** — "If this answer leads to a bad outcome, what's the most likely cause?"

### Multi-Perspective Protocol

The verifier evaluates from 4 fixed perspectives:

| Perspective | Question |
|-------------|----------|
| **Skeptic** | "What's the weakest link in this reasoning?" |
| **Domain Expert** | "Would a specialist in this field agree?" |
| **Beneficiary** | "Does this actually solve the user's real need?" |
| **Contrarian** | "What if the opposite is true?" |

### Cross-Check Output Format

```
## 🟢 Cross-Check Result

### Models Used
- Primary: [model name]
- Verifier: [model name]

### Challenges Accepted
- [challenge that changed the answer] → [how it was integrated]

### Challenges Rejected  
- [challenge considered but kept original] → [reasoning]

### New Perspectives Added
- [insight from verifier that primary model missed]

### Assumption Audit
| Assumption | Primary | Verifier | Final |
|-----------|:---:|:---:|:---:|
| [assumption] | High | ❌ Wrong | ⚠️ Revised to [X] |
| [assumption] | Medium | ✅ Valid | ✅ Confirmed |

### Pre-Mortem Risks
| Risk | Likelihood | Impact | Mitigation |
|------|:---:|:---:|---|
| [risk] | Medium | High | [action] |

### Final Answer
[revised answer with change log at the bottom]
```

---

## Chain of Thought Protocol

Both modes use explicit chain-of-thought reasoning throughout:

### For the Primary Model (each round)
```
THINKING PROCESS:
1. What is the user actually asking? (Restate the core question)
2. What do I know for certain? (Facts only)
3. What am I assuming? (Explicit assumptions)
4. What are the possible approaches? (Generate 3+ options)
5. What are the trade-offs of each approach?
6. What would I recommend and why?
7. What could make me wrong? (Self-challenge)
8. Final answer.
```

### For the Verifier Model
```
THINKING PROCESS:
1. What did the primary model conclude? (Summarize)
2. What assumptions underlie each conclusion?
3. For each assumption: Is there evidence for AND against it?
4. What perspective is missing from this analysis?
5. What would an expert in this domain say differently?
6. What would happen if the opposite is true?
7. What is the strongest version of the opposing view?
8. My verdict on each assumption and the overall answer.
```

---

## Quick Commands

| User says | Action |
|-----------|--------|
| "cross-check" / "sjekk dette" | Detect + offer activation |
| "cross-check force" / "alltid sjekk" | Skip detection, always activate |
| "cross-check lite" | Reinforced mode, 2 rounds instead of 3 |
| "cross-check deep" | 5 rounds (reinforced) or 2 verifier passes (cross-check) |
| "what mode am I in" | Show current mode and configured models |
| "cross-check off" | Disable auto-detection for this session |

---

## Privacy and Safety

- This skill processes content in-session only — nothing is persisted
- No personal data is written to any files
- When using Cross-Check Mode, only the problem context and assumptions are sent to the verifier — never raw user data
- No file I/O of any kind
- No web searches unless explicitly requested by the user
- No external API calls — uses only OpenClaw's configured providers via sessions_spawn

## What This Skill Does NOT Do

- Does NOT automatically activate — always asks first
- Does NOT replace the primary model — it improves its output
- Does NOT debate endlessly — verifier gives one pass, primary integrates once
- Does NOT store or persist anything
- Does NOT send user data or private information to any external service
- Does NOT access the filesystem

## More by TommoT2

- **setup-doctor** — Diagnose and fix OpenClaw setup issues
- **tommo-skill-guard** — Security scanner for all installed skills
- **locale-dates** — Format dates/times per locale

Install the full starter pack:
```bash
clawhub install setup-doctor locale-dates tommo-skill-guard
```
