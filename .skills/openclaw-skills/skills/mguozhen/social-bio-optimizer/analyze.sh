#!/usr/bin/env bash
set -euo pipefail
INPUT="${*:-}"
[ -z "$INPUT" ] && echo "Usage: bio: <platform, role/niche, target audience, and goal>" && exit 1
SESSION_ID="bio-$(date +%s)"
PROMPT="You are a social media profile optimization expert. Write optimized bios for: ${INPUT}

## Platform Character Limits
- Instagram: 150 chars
- TikTok: 80 chars
- X/Twitter: 160 chars
- LinkedIn Summary: 2,600 chars / Headline: 220 chars
- Threads: 150 chars

## Bio Formula Analysis
Best formula for this person/brand:
[WHO you help] + [WHAT result they get] + [HOW/unique angle] + [CTA]

## 5 Bio Variations

**Variation 1 — Value-First**
[Bio leading with the benefit the audience gets]
Character count: [X]
Best for: [platform]

**Variation 2 — Identity-Led**
[Bio leading with who you are and who you help]
Character count: [X]
Best for: [platform]

**Variation 3 — Results/Proof**
[Bio leading with a credibility signal or result]
Character count: [X]
Best for: [platform]

**Variation 4 — Personality/Vibe**
[Bio with more personality, humor, or emoji]
Character count: [X]
Best for: [platform]

**Variation 5 — Ultra-Short Punchy**
[One-liner bio — max 80 chars]
Character count: [X]
Best for: TikTok, Twitter

## Platform-Specific Versions

**Instagram Bio (max 150 chars):**
[Optimized version with line breaks — Instagram renders each line separately]
Line 1: [Role / who you help]
Line 2: [What result / unique angle]
Line 3: [Social proof or personality]
Line 4: [CTA + emoji]

**LinkedIn Headline (max 220 chars):**
[Professional headline with keywords]
Keyword audit: [3 keywords integrated]

**LinkedIn About Section (first 300 chars that show before 'See more'):**
[Opening paragraph that hooks readers]

**TikTok Bio (max 80 chars):**
[Ultra-compressed version]

**X/Twitter Bio (max 160 chars):**
[Version with personality + keywords]

**Threads Bio (max 150 chars):**
[Version]

## Keyword Integration
Top 5 searchable keywords to include in bio for discoverability:
1. [keyword] — search volume estimate
2. [keyword]
3. [keyword]
4. [keyword]
5. [keyword]

## CTA Optimization
Best link-in-bio CTA options based on goal:
- If goal = grow email list: '[CTA text]'
- If goal = sell product: '[CTA text]'
- If goal = drive DMs: '[CTA text]'
- If goal = grow following: '[CTA text]'

## A/B Test Recommendation
Test these two against each other:
- **Bio A:** [Best overall variation]
- **Bio B:** [Second best — different angle]
Change only the bio, keep everything else constant. Run for 2 weeks."

RESULT=$(openclaw agent --local --session-id "$SESSION_ID" --json -m "$PROMPT" 2>/dev/null)
REPORT=$(echo "$RESULT" | python3 -c "
import json,sys
data=json.load(sys.stdin)
texts=[p.get('text','') for p in data.get('payloads',[]) if p.get('text')]
print('\n'.join(texts))
" 2>/dev/null)
[ -z "$REPORT" ] && echo "Error: Could not generate bio." && exit 1
echo ""
echo "=== BIO OPTIMIZER === ${INPUT} ==="
echo ""
echo "$REPORT"
