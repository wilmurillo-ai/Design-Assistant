#!/usr/bin/env bash
# shopify-crowdfunding — Crowdfunding campaign strategy for Shopify product launches
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: crowdfunding campaign plan: <product idea>"
  exit 1
fi

SESSION_ID="shopify-crowdfunding-$(date +%s)"

PROMPT="You are a Shopify crowdfunding and product launch expert specializing in Kickstarter and Indiegogo campaigns, backer community building, and post-campaign DTC transition strategies. Build a complete crowdfunding strategy for: ${INPUT}

Produce a complete crowdfunding campaign plan with these sections:

## 1. Platform Selection & Strategy
- Kickstarter: all-or-nothing funding model, discovery advantages, category fit
- Indiegogo: flexible funding, InDemand post-campaign, less discovery
- Backerkit: pre-launch reservation system and post-campaign store
- Recommendation for this product type with specific reasoning

## 2. Pre-Campaign Audience Building (60-Day Pre-Launch)
- Email list building goal: target 1,000 interested backers before launch
- Lead magnet strategy: what to offer for email sign-ups
- Facebook Group or community for early supporters
- Social media content strategy: problem storytelling and product teasers
- PR and media outreach: relevant tech/product blogs and journalists

## 3. Campaign Page Blueprint
- Campaign title formula: what it is, who it's for, key benefit
- Campaign video structure: problem, solution, product demo, team, call to action
- Story section: narrative arc that makes people root for you to succeed
- Social proof elements: prototype testing results, advisor quotes, beta user feedback
- FAQ section: top 10 questions to address pre-emptively

## 4. Reward Tier Architecture
- Early bird tier: significant discount for first 24 hours to create urgency
- Standard tier: main product with realistic fulfillment pricing
- Deluxe tier: product + extras for higher-value backers
- Corporate/bulk tier: multiple units for business customers
- Stretch goal tie-in rewards: how to motivate shares and funding growth

## 5. Launch Day & Momentum Strategy
- Day 1 goal: reach 30-40% of funding target within first 24 hours
- Backer mobilization: personal outreach to first 50 backers
- Social media blitz: coordinated posts across all channels at launch
- Press coverage timing: embargo lifts at midnight of launch day
- Stretch goal cadence: reveal new goals as each is hit

## 6. Backer Communication & Community
- Update frequency: weekly during campaign, bi-weekly post-campaign
- Update structure: progress, milestone celebration, next steps
- Community management: responding to comments within 24 hours
- Delay communication: honest, proactive updates if timeline changes

## 7. Post-Campaign Shopify Transition
- Immediate actions (launch day): campaign live, email to full pre-launch list
- Short-term (month 1): reach funding goal, stretch goals, media coverage
- Long-term (post-campaign): InDemand or Shopify store launch, backer fulfillment, DTC scaling

Include Kickstarter success benchmarks: average funding amounts, category success rates, importance of the first 48 hours, and how successful crowdfunding campaigns translate to Shopify store success."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
