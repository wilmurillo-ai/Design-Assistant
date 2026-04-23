---
name: amazon-review-management
description: "Amazon review management and response agent. Write professional responses to negative reviews, analyze review patterns to find product improvements, build compliant review generation strategies, and manage Vine enrollment. Triggers: review management, negative review, respond to review, amazon reviews, review response, bad review, star rating, review strategy, vine program, review generation, seller feedback, product review, amazon vine, review analysis, 1 star review, review reply"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-review-management
---

# Amazon Review Management Agent

Handle negative reviews professionally, spot product improvement signals in review data, and build a compliant review strategy that grows your star rating over time.

## Commands

```
review respond [paste review]   # write professional response to a review
review analyze [paste reviews]  # find patterns and product insights
review strategy                 # build review generation plan
review vine                     # Vine enrollment guide
review request [market]         # compliant review request strategy
review report [competitor ASIN] # analyze competitor review weaknesses
review crisis [situation]       # crisis response for review bombing
review save [product]           # save review profile and history
```

## What Data to Provide

- **Negative review text** -- paste the review to respond to
- **Your product details** -- so responses are accurate
- **Review history** -- overall star rating, total count
- **Specific complaint patterns** -- recurring issues
- **Competitor ASIN** -- for competitive review analysis

## Negative Review Response Framework

### Response Principles
1. **Respond within 24 hours** -- speed signals you care
2. **Never argue** -- even when customer is wrong
3. **Acknowledge, don't defend** -- validate their experience first
4. **Take it offline** -- move resolution to private channel
5. **Keep it short** -- 3-4 sentences max in public response

### Response Template Structure
```
[Acknowledge their experience]
[Brief, non-defensive explanation if relevant]
[Offer specific resolution]
[Invite them to contact you directly]
```

### Response Templates by Review Type

**Product didn't meet expectations:**
> "Thank you for your honest feedback. We're sorry our product didn't meet your expectations -- that's not the experience we want for our customers. Please reach out to us and we'll make it right, whether that's a replacement, refund, or troubleshooting assistance. We appreciate you giving us the chance to improve."

**Shipping/packaging complaint:**
> "We sincerely apologize for the condition your order arrived in. Damage during shipping is rare but unacceptable, and we take full responsibility. Please contact us directly and we'll send a replacement immediately at no charge. Thank you for letting us know."

**Size/fit issue:**
> "Thank you for this feedback. We're sorry the sizing didn't work for you -- we know how frustrating that is. We've noted your feedback for our size guide improvements. Please message us and we're happy to exchange for the right size or issue a full refund."

**Competitor-placed fake negative review:**
> "We appreciate all feedback. If you have specific concerns about your order, please contact our customer service team directly -- we'd love the opportunity to resolve this for you."

**Wrong product expectations:**
> "Thank you for your review. We're sorry our listing didn't clearly set the right expectations -- your feedback helps us improve. Please reach out to us directly if you'd like a refund or if there's anything we can do to help."

## Review Pattern Analysis Framework

When analyzing a set of reviews, categorize complaints:

| Category | Examples | Action |
|----------|----------|--------|
| **Product defect** | "Broke after 2 weeks", "stopped working" | Contact supplier, quality check |
| **Listing mismatch** | "Smaller than expected", "not as described" | Update listing, improve images |
| **Shipping damage** | "Arrived broken", "crushed box" | Improve packaging |
| **Missing pieces** | "Part was missing" | Review packing process |
| **Usage confusion** | "Didn't know how to..." | Add instructions, video |
| **Wrong expectations** | "Too basic for my needs" | Clarify target customer in listing |

**Signal thresholds:**
- Same complaint appearing 3+ times = systematic issue, fix the root cause
- 1-star spike in 2-week window = possible review manipulation or batch defect

## Compliant Review Generation Strategy

### What Amazon Allows
- OK: Request a review via "Request a Review" button in Seller Central (neutral, Amazon-worded)
- OK: Packaging inserts with neutral language ("We'd love to hear your feedback")
- OK: Follow-up emails via Buyer-Seller Messaging (neutral only)
- OK: Amazon Vine program (pay per unit enrolled)
- OK: Early Reviewer Program (some markets, legacy)

### What Amazon Prohibits
- NOT OK: Incentivized reviews ("Leave a review for 10% off")
- NOT OK: Asking specifically for positive reviews
- NOT OK: Family/friend reviews
- NOT OK: Review swapping with other sellers
- NOT OK: Threatening consequences for negative reviews
- NOT OK: Manipulative inserts ("Only contact us before leaving negative feedback")

### Compliant Insert Card Copy
```
Thank you for your purchase!

We're a small team that puts everything into making our products.
If you love it, we'd be grateful if you shared your experience --
your review helps other customers make the right choice.

If anything's not right, please email us first --
we'll make it right, guaranteed.
```

## Vine Program Guide

**What it is**: Amazon sends free units to vetted reviewers ("Voices") who leave honest reviews.

**Cost**: $200 per parent ASIN enrolled (US, 2024)
**Units**: 1-30 units enrolled
**Timeline**: Reviews appear within 4-8 weeks
**Best for**: New products with fewer than 30 reviews

**Eligibility**:
- Brand Registry enrolled
- Fewer than 30 reviews
- FBA listing (not FBM)
- New or relaunched products

**When NOT to use Vine**:
- Product has known quality issues (Vine reviewers are thorough)
- Category where product needs more social proof first
- If you can't afford 30 free units + $200 fee

## Star Rating Recovery Plan

If your rating drops below 4.0:

1. **Diagnose**: Find the root complaint (use Pattern Analysis)
2. **Fix the product/listing** (don't just respond to reviews)
3. **Enroll in Vine** to get fresh honest reviews
4. **Activate Request-a-Review** for all eligible orders
5. **Monitor weekly**: Track new review velocity vs. old negative reviews

Timeline: Rating typically recovers in 60-90 days with consistent action.

## Output Format

1. **Review Response Draft** -- professional, on-brand, ready to post
2. **Pattern Analysis** -- top 3 complaint categories with action items
3. **Review Strategy Plan** -- timeline and tactics for rating improvement
4. **Vine ROI Estimate** -- cost vs. projected review count
5. **Compliance Check** -- flag any current practices that risk policy violation
