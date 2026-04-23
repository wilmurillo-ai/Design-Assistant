#!/usr/bin/env bash
# shopify-email-segmentation — Email marketing segmentation strategy
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: email segmentation: <store details>"
  echo "Example: email segmentation: pet store 5000 subscribers Klaviyo"
  exit 1
fi

SESSION_ID="email-seg-$(date +%s)"

PROMPT="You are a Shopify email marketing expert specializing in Klaviyo segmentation and lifecycle automation. Build a complete email marketing strategy for: ${INPUT}

## 1. Core Segment Architecture
Define 10 essential segments with entry/exit criteria:

| Segment | Definition | Size Estimate | Goal |
|---------|-----------|---------------|------|
| Champions | | | |
| Loyal Customers | | | |
| At Risk | | | |
| Lost Customers | | | |
| Promising | | | |
| New Subscribers | | | |
| Browse Abandoners | | | |
| Cart Abandoners | | | |
| One-Time Buyers | | | |
| VIP (High LTV) | | | |

## 2. RFM Scoring Framework
Build RFM model (1-5 scale each):
- Recency breakpoints (days since last purchase)
- Frequency breakpoints (number of orders)
- Monetary breakpoints (total spend in $)
- Combined RFM action matrix

## 3. Automated Flow Map
Design 8 essential flows:

**Flow 1: Welcome Series (5 emails)**
- Email 1 (Day 0): subject, goal, content outline
- Email 2 (Day 2): subject, goal, content outline
- Email 3 (Day 5): subject, goal, content outline
- Email 4 (Day 8): subject, goal, content outline
- Email 5 (Day 14): subject, goal, content outline

**Flow 2: Abandoned Cart (3 emails)**
- Email 1 (1 hour): urgency + product reminder
- Email 2 (24 hours): social proof + FAQ
- Email 3 (72 hours): discount offer

**Flow 3: Browse Abandonment (2 emails)**
**Flow 4: Post-Purchase (4 emails)**
**Flow 5: Winback / Re-engagement (3 emails)**
**Flow 6: VIP / Loyalty (ongoing)**
**Flow 7: Sunset (unengaged cleanup)**
**Flow 8: Birthday / Anniversary**

## 4. Campaign Calendar (12 Months)
Monthly send plan by segment:
| Month | Campaign | Segment | Goal |
|-------|----------|---------|------|
[Fill all 12 months with specific campaign ideas for this niche]

## 5. Subject Line Playbook
10 proven subject line formulas for each segment type:
- Welcome: [5 examples]
- Cart abandon: [5 examples]
- Win-back: [5 examples]
- VIP: [5 examples]
- Promotional: [5 examples]

## 6. Revenue Attribution Targets
Benchmarks for this niche:
- % of total revenue from email (target)
- Revenue per subscriber per month target
- Flow vs campaign revenue split
- Open rate / CTR / CVR benchmarks by flow

## 7. A/B Testing Roadmap (90 Days)
Priority testing queue:
- Week 1-2: Test [variable] in [flow]
- Week 3-4: Test [variable] in [campaign]
- Week 5-8: Test [variable]
- Week 9-12: Test [variable]

## 8. Klaviyo Setup Checklist
Step-by-step to implement this strategy:
- List hygiene steps
- Segment creation order
- Flow activation sequence
- Integration with Shopify data"

RESULT=$(openclaw agent --local --session-id "$SESSION_ID" --json -m "$PROMPT" 2>/dev/null)
REPORT=$(echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
payloads = data.get('payloads', [])
texts = [p.get('text','') for p in payloads if p.get('text')]
print('\n'.join(texts))
" 2>/dev/null)

if [ -z "$REPORT" ]; then
  echo "Error: Could not generate report."
  exit 1
fi

echo ""
echo "================================================"
echo "  EMAIL SEGMENTATION STRATEGY"
echo "  Store: ${INPUT}"
echo "================================================"
echo ""
echo "$REPORT"
echo ""
echo "================================================"
echo "  Powered by Shopify Email Segmentation"
echo "  clawhub.ai/mguozhen/shopify-email-segmentation"
echo "================================================"
