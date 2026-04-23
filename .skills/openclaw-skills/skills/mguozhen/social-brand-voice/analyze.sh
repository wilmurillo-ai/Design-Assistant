#!/usr/bin/env bash
set -euo pipefail
INPUT="${*:-}"
[ -z "$INPUT" ] && echo "Usage: brand voice: <brand description and target audience>" && exit 1
SESSION_ID="voice-$(date +%s)"
PROMPT="You are a brand strategist specializing in voice and tone. Create a complete brand voice guide for: ${INPUT}

## Brand Personality
Define 4 core personality traits (like 'The Trusted Expert' + 'The Witty Friend'):
For each trait:
- Trait name: [X]
- What it means in practice: [description]
- In our content we: [3 behaviors]
- We never: [3 anti-behaviors]

## Tone Spectrum
Rate on 5 axes (1=left extreme, 10=right extreme):
| Axis | 1 | Score | 10 |
|------|---|-------|-----|
| Formal | | X/10 | Casual |
| Serious | | X/10 | Playful |
| Reserved | | X/10 | Bold |
| Professional | | X/10 | Conversational |
| Distant | | X/10 | Warm |

## Vocabulary Guide
**Words/phrases we love:** [20 specific words that fit the brand]
**Words/phrases we ban:** [20 words that kill the vibe]
**Phrases we own:** [5 signature phrases unique to this brand]
**Emojis we use:** [approved emoji set]
**Emojis we avoid:** [banned emojis]

## Sentence & Structure Rules
- Average sentence length: [X words — short/medium/long]
- Paragraph length: [X sentences max]
- Use of questions: [how often and what kind]
- Use of lists: [when yes, when no]
- Punctuation style: [rules]
- Capitalization: [rules]

## Platform Voice Variants
How the core voice adapts without losing identity:
| Platform | Tone Shift | Format Notes | Example Opening |
|----------|-----------|--------------|-----------------|
| LinkedIn | | | |
| Instagram | | | |
| TikTok | | | |
| X/Twitter | | | |
| Email | | | |

## Before & After Rewrites
Take 3 generic captions and rewrite them in brand voice:

**Post 1 — Product Announcement:**
Before: 'Excited to announce our new product is available now!'
After: [rewrite in brand voice]

**Post 2 — Educational Content:**
Before: 'Here are 5 tips to improve your workflow.'
After: [rewrite in brand voice]

**Post 3 — Customer Story:**
Before: 'Check out what our customer said about us!'
After: [rewrite in brand voice]

## One-Page Quick Reference Card
Summarize everything in a cheat sheet format:
BRAND VOICE: [4 words]
WE SOUND LIKE: [analogy — e.g., 'your smartest friend at a dinner party']
WE NEVER SAY: [top 5 banned phrases]
WE ALWAYS: [top 5 must-do behaviors]
OUR SIGNATURE MOVE: [one thing that makes our writing unmistakably us]"

RESULT=$(openclaw agent --local --session-id "$SESSION_ID" --json -m "$PROMPT" 2>/dev/null)
REPORT=$(echo "$RESULT" | python3 -c "
import json,sys
data=json.load(sys.stdin)
texts=[p.get('text','') for p in data.get('payloads',[]) if p.get('text')]
print('\n'.join(texts))
" 2>/dev/null)
[ -z "$REPORT" ] && echo "Error: Could not generate brand voice guide." && exit 1
echo ""
echo "=== BRAND VOICE GUIDE === ${INPUT} ==="
echo ""
echo "$REPORT"
