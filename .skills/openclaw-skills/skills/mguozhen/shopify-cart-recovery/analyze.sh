#!/usr/bin/env bash
# shopify-cart-recovery — Multi-channel cart abandonment recovery system
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: cart recovery: <store details>"
  echo "Example: cart recovery: fashion store \$75 AOV 2.5% conversion rate"
  exit 1
fi

SESSION_ID="cart-$(date +%s)"

PROMPT="You are a Shopify conversion rate expert specializing in cart abandonment recovery. Build a complete recovery system for: ${INPUT}

## 1. Recovery Rate Benchmark
Industry benchmarks for this niche:
- Average cart abandonment rate: X%
- Average email recovery rate: X%
- Average SMS recovery rate: X%
- Average retargeting recovery rate: X%
- **Total addressable recovery revenue estimate**

## 2. Multi-Channel Recovery Sequence (Timeline)
Map the complete recovery journey:

| Time | Channel | Message Type | Goal |
|------|---------|-------------|------|
| 1 hour | Email | Reminder | Soft nudge |
| 3 hours | SMS | Reminder | Urgency |
| 24 hours | Email | Social proof | Build trust |
| 48 hours | Retargeting | Product focus | Stay top of mind |
| 72 hours | Email | Incentive | Last chance offer |
| 7 days | Email | Win-back | Reengagement |

## 3. Email Sequence (5 Emails)

**Email 1 — Reminder (1 hour after abandonment)**
Subject line options (5 variations):
1. [Option]
2. [Option]
3. [Option]
4. [Option]
5. [Option]

Full body copy (200 words):
[Write complete email for this niche]

**Email 2 — Social Proof (24 hours)**
Subject: [subject]
Body: [Full email — lead with reviews/testimonials, address objections]

**Email 3 — FAQ/Objection Handler (48 hours)**
Subject: [subject]
Body: [Full email — address top 3 reasons people don't buy in this niche]

**Email 4 — Urgency + Incentive (72 hours)**
Subject: [subject]
Body: [Full email — limited time offer, X% off or free shipping]

**Email 5 — Final Goodbye (7 days)**
Subject: [subject]
Body: [Full email — last chance, what they'll miss, close the loop]

## 4. SMS Sequence (3 Messages)
All messages under 160 characters with STOP opt-out:

**SMS 1 (3 hours):** [Message] Reply STOP to unsubscribe.
**SMS 2 (48 hours):** [Message] Reply STOP to unsubscribe.
**SMS 3 (72 hours):** [Message] Reply STOP to unsubscribe.

## 5. Retargeting Ad Strategy
Facebook/Instagram ads for cart abandoners:
- Audience window: 1-day / 3-day / 7-day segments
- Creative angle by window:
  - 1-day: [angle + copy]
  - 3-day: [angle + copy]
  - 7-day: [angle + copy]
- Budget allocation: $X/day per segment
- Frequency cap recommendation

## 6. Incentive Strategy
When and what to offer:
- No discount (Email 1-3): focus on [value prop]
- Discount trigger: only if [criteria]
- Discount type: % off vs free shipping vs gift (which converts better for this niche)
- Incentive amount: X% (margin-safe threshold)
- Urgency mechanism: countdown timer setup

## 7. Revenue Impact Calculator
Assuming this store's metrics:
- Monthly traffic: X visitors
- Add-to-cart rate: X%
- Cart abandonment rate: X%
- Monthly abandoned carts: X
- Recovery rate with this system: X%
- Average order value: $X
- **Monthly recovered revenue: $X**
- **Annual impact: $X**

## 8. Klaviyo / Shopify Setup Guide
Step-by-step to implement:
1. Trigger setup in Klaviyo
2. Shopify checkout abandonment tracking
3. SMS compliance setup (TCPA)
4. A/B test configuration
5. Analytics dashboard setup

## 9. Optimization Checklist (First 30 Days)
What to monitor and optimize after launch."

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
echo "  CART RECOVERY SYSTEM"
echo "  Store: ${INPUT}"
echo "================================================"
echo ""
echo "$REPORT"
echo ""
echo "================================================"
echo "  Powered by Shopify Cart Recovery"
echo "  clawhub.ai/mguozhen/shopify-cart-recovery"
echo "================================================"
