# Dropshipping Product Research

## Overview

Dropshipping Product Research helps beginners and small operators evaluate whether a product is worth testing. It is a descriptive, non-API MVP focused on structured scoring, risk filtering, and clear go / test / reject decisions.

## Trigger

Use this skill when the user wants to:
- evaluate a product idea for dropshipping
- compare multiple product candidates
- estimate risk, margin, and creative fit
- build a weekly shortlist for testing

### Example prompts
- "Evaluate this product for dropshipping in the US"
- "Should I test a galaxy projector or pet grooming glove?"
- "Give me a go / test / reject recommendation"
- "Help me score 3 product ideas for my store"

## Workflow

1. Capture candidate, market, and positioning constraints.
2. Infer demand, competition, margin, creative angle, and risk.
3. Produce a viability score and recommendation.
4. Summarize why it may win, why it may fail, and what to test next.

## Inputs
- product name or keyword
- optional product link or niche
- target market
- price target or cost hints
- mode: single product / batch / trend scouting

## Outputs
- viability score
- sub-scores: demand, competition, margin, creative fit, risk
- recommendation: Go / Test / Reject
- memo with hypotheses and next steps

## Safety
- No marketplace scraping or real-time trend API access
- No guarantee of profit or compliance clearance
- Recommendations are heuristic and should be validated with real tests

## Acceptance Criteria
- Must output markdown
- Must include all five scoring dimensions
- Must include Go / Test / Reject recommendation
- Must include at least three risk or execution notes
