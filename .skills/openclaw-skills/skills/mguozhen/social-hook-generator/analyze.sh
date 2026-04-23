#!/usr/bin/env bash
set -euo pipefail
INPUT="${*:-}"
[ -z "$INPUT" ] && echo "Usage: hook: <topic and platform>" && exit 1
SESSION_ID="hook-$(date +%s)"
PROMPT="You are a viral content expert who writes scroll-stopping social media hooks. Generate hooks for: ${INPUT}

## Platform Analysis
First identify the target platform(s) from the input. If not specified, cover: X/Twitter, LinkedIn, TikTok/Instagram.

## 10 Hook Variations
Write 10 hooks using these proven styles:

1. **Bold Claim** — make a surprising, counterintuitive statement
2. **Curiosity Gap** — hint at something without revealing it
3. **Question Hook** — ask a question that hits a pain point
4. **Data/Stats** — lead with a specific, surprising number
5. **Story Setup** — open mid-scene or with a relatable moment
6. **Contrarian Take** — challenge a common belief
7. **\"I Did X\" Hook** — personal experience that promises value
8. **List Hook** — promise N things the reader needs
9. **\"Most People Don't Know\"** — exclusivity and insight
10. **FOMO/Urgency** — create fear of missing out

For each hook:
- Write the hook (under 280 chars for X, under 150 chars for TikTok)
- Name the emotion trigger it activates
- Rate scroll-stop power: 🔥 (low) / 🔥🔥 (medium) / 🔥🔥🔥 (high)

## Top 3 A/B Test Pairs
Pick the 3 strongest hooks and pair each with a variant for split testing:
- Hook A: [original]
- Hook B: [same idea, different angle]

## Platform Customization
How to adapt the top hook for each platform:
- X/Twitter: [specific adaptation]
- LinkedIn: [specific adaptation]
- TikTok caption: [specific adaptation]
- Instagram Reels: [specific adaptation]
- Threads: [specific adaptation]

## Hook Writing Rules
Remind the user of the 3 rules to never break when writing hooks."

RESULT=$(openclaw agent --local --session-id "$SESSION_ID" --json -m "$PROMPT" 2>/dev/null)
REPORT=$(echo "$RESULT" | python3 -c "
import json,sys
data=json.load(sys.stdin)
texts=[p.get('text','') for p in data.get('payloads',[]) if p.get('text')]
print('\n'.join(texts))
" 2>/dev/null)
[ -z "$REPORT" ] && echo "Error: Could not generate hooks." && exit 1
echo ""
echo "=== VIRAL HOOK GENERATOR === Topic: ${INPUT} ==="
echo ""
echo "$REPORT"
