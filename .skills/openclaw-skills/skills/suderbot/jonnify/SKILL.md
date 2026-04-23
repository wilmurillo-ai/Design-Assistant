---
name: jonnify
description: Rewrite or reword provided text so it sounds like Jon (the user) wrote it. Use when the user asks to make a message/email “sound like me”, “in my voice”, “like I’d say it”, or wants a neutral-Jon rewrite with optional tone knobs (more professional, more edgy, goofier, warmer, shorter/longer). Preserve the original intent and structure; do not introduce new factual claims.
---

# Jonnify

Rewrite text into Jon’s voice.

## Quick workflow

1) Ask for the source text (or use the user-provided draft).
2) Ask for *optional* knobs (defaults below).
3) Rewrite **once**.
4) If the user says it doesn’t feel like them, ask what’s off and capture the correction as a new example.

## Defaults (when the user doesn’t specify)

- Voice: **Neutral Jon**
- Professionalism: medium
- Edge: low-to-medium (no swearing by default)
- Goofiness: low
- Warmth: medium
- Brevity: medium

## Hard constraints

- **No new facts.** Do not add details, numbers, commitments, names, timelines, or claims that were not present in the input.
- **Preserve intent.** Keep the meaning and requested outcome the same.
- **Preserve “units”.** If the input has separate paragraphs or bullets, keep that structure unless the user asks otherwise.
- **Sound plausible.** Mild embellishment is OK *only* in tone/flow, not in factual content.

## Tone knobs (user-facing)

Accept any of these phrases and map them to the internal knobs:

- “more professional” / “more formal”
- “more casual”
- “a bit edgier” (still rarely swear)
- “goofier” / “more playful”
- “warmer” / “more direct”
- “shorter” / “tighter” / “less wordy”
- “for email” / “for a quick text”
- “for my boss / coworker / client / friend / group chat” (audience)

When knobs conflict, prefer: **accuracy > clarity > Jon-ness > humour**.

## Use the voice profile

Load and follow:
- `references/voice-profile.md` (current distilled rules)
- `references/lexicon.md` (favourite phrases + anti-phrases)

When you notice new recurring patterns in Jon’s messages during normal conversation, add them during the next nightly refresh (don’t spam edits mid-chat).

## Capturing corrections (important)

If Jon provides feedback like “too formal”, “too cringe”, “not me”, “more blunt”, etc.:

1) Ask a single clarifying question if needed.
2) Update `references/voice-profile.md` with a short rule (1–3 lines).
3) Append a before/after pair to `references/examples.jsonl`.

Keep examples short and representative.

## Nightly refresh (separate automation)

A scheduled job maintains the profile by:

- pulling Jon’s recent messages since the last run,
- extracting style signals (phrasing, cadence, closers, hedges, humour style),
- updating the profile + lexicon,
- keeping a rolling 90-day window of raw samples, plus a curated “best-of” set.

State file: `references/state.json`.
