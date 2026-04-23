#!/usr/bin/env bash
set -euo pipefail
INPUT="${*:-}"
[ -z "$INPUT" ] && echo "Usage: content pillars: <brand/creator description and platform>" && exit 1
SESSION_ID="pillars-$(date +%s)"
PROMPT="You are a content strategy expert. Build a complete content pillar system for: ${INPUT}

## Brand/Creator Analysis
- Audience profile: [who they are, what they want]
- Platform primary: [best fit platform]
- Voice: [recommended tone]
- Unique angle: [what makes this different]

## 5 Content Pillars

For each pillar:
### Pillar [N]: [NAME]
- **Purpose:** [why this pillar exists — what it does for the audience]
- **Audience benefit:** [what they get from it]
- **Business benefit:** [what the creator/brand gets]
- **Content ratio:** X% of total posts
- **Best formats:** [reel / carousel / text post / story / thread]
- **10 Post Ideas:**
  1. [Specific post idea with angle]
  2. [Specific post idea]
  3. [Specific post idea]
  4. [Specific post idea]
  5. [Specific post idea]
  6. [Specific post idea]
  7. [Specific post idea]
  8. [Specific post idea]
  9. [Specific post idea]
  10. [Specific post idea]

[Repeat for all 5 pillars]

## Content Mix Formula
Weekly posting rhythm:
| Day | Pillar | Format | Goal |
|-----|--------|--------|------|
| Mon | | | |
| Tue | | | |
| Wed | | | |
| Thu | | | |
| Fri | | | |
| Sat | | | |
| Sun | | | |

## Growth Pillar Strategy
- Pillar to prioritize for fastest follower growth: [Pillar X] — why
- Pillar for deepest engagement: [Pillar X] — why
- Pillar for conversions/sales: [Pillar X] — why

## First 30 Days Post Plan
Map out the first 30 posts using the pillar system — one post per day, pillar rotation."

RESULT=$(openclaw agent --local --session-id "$SESSION_ID" --json -m "$PROMPT" 2>/dev/null)
REPORT=$(echo "$RESULT" | python3 -c "
import json,sys
data=json.load(sys.stdin)
texts=[p.get('text','') for p in data.get('payloads',[]) if p.get('text')]
print('\n'.join(texts))
" 2>/dev/null)
[ -z "$REPORT" ] && echo "Error: Could not generate content pillars." && exit 1
echo ""
echo "=== CONTENT PILLAR STRATEGY === ${INPUT} ==="
echo ""
echo "$REPORT"
