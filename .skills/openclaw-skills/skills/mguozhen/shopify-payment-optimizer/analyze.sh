#!/usr/bin/env bash
# shopify-payment-optimizer — Cross-border payment stack comparison
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: payment optimizer: <store details>"
  echo "Example: payment: compare options for \$50K/month US sales"
  exit 1
fi

SESSION_ID="payment-$(date +%s)"

PROMPT="You are a cross-border payment expert for Shopify stores selling globally. Analyze and optimize the payment stack for: ${INPUT}

## 1. Payment Provider Comparison Table
Compare these providers across key metrics:
| Provider | Transaction Fee | FX Spread | Settlement Speed | Min Withdrawal | Best For |
|----------|----------------|-----------|-----------------|----------------|----------|
| Airwallex | | | | | |
| WorldFirst | | | | | |
| Pingpong | | | | | |
| Lianlian Pay | | | | | |
| Payoneer | | | | | |
| PayPal | | | | | |
| Stripe | | | | | |
| Shopify Payments | | | | | |

## 2. Fee Deep Dive
For this specific use case, calculate real cost per \$10,000 in sales:
- Transaction fee cost
- FX conversion cost (assuming CNY settlement)
- Withdrawal fee
- **Total effective fee rate**
- Annual cost at projected volume

## 3. Settlement Speed & Cash Flow Impact
Rank providers by settlement speed for this scenario:
- Same-day / T+0 options
- T+1 to T+3 options
- T+7+ (avoid for cash flow)
→ Cash flow impact analysis

## 4. Currency & Market Coverage
Which providers support the target markets:
- List of supported currencies
- Markets with restrictions or higher risk
- Chargeback protection by region

## 5. Risk Assessment
| Provider | Account Freeze Risk | Reserve Policy | Dispute Resolution |
|----------|--------------------|-----------------|--------------------|

## 6. Recommended Payment Stack
**Primary:** [Provider] — why
**Backup:** [Provider] — why
**For PayPal customers:** [Provider] — why
**For high-ticket:** [Provider] — why

## 7. Implementation Checklist
Documents needed for each recommended provider:
- Business registration requirements
- KYC documents
- Shopify integration method (native / API / plugin)
- Typical approval timeline

## 8. Cost Savings vs PayPal-Only
Projected annual savings switching to recommended stack:
- Current PayPal cost estimate
- Optimized stack cost
- Annual savings
- Payback period on setup effort

## 9. Red Flags to Avoid
Common mistakes when setting up cross-border payments for Shopify stores."

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
echo "  PAYMENT OPTIMIZATION REPORT"
echo "  Scenario: ${INPUT}"
echo "================================================"
echo ""
echo "$REPORT"
echo ""
echo "================================================"
echo "  Powered by Shopify Payment Optimizer"
echo "  clawhub.ai/mguozhen/shopify-payment-optimizer"
echo "================================================"
