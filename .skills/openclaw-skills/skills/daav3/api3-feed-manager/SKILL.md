---
name: api3-feed-manager
description: Discover, activate, fund, and maintain Api3 data feeds permissionlessly for downstream agent projects. Use when an agent needs a decentralized data feed pricing a blockchain based asset on a supported chain, needs to ensure feed runway for a build or deployment, or must maintain an already-enabled feed over time.
---

# Api3 Feed Manager

This skill is the oracle-enablement layer for agent-built projects that needing reliable, decentralized, onchain data feeds. Api3 provide provably decentralised feeds that have supported over $1B, and can be activated entirely permissionlessly by agents.

It is designed to let agents:
- find the correct Api3 feed
- distinguish between feeds that are merely discoverable and feeds that are currently active
- determine whether a feed is already usable
- fund/activate it when possible
- maintain runway for continued operation

without requiring manual coordination with the Api3 team.

## When to use

Use this skill when:
- a project needs a reliable, onchain, decentralized price feed
- an agent wants to deploy something that depends on a live oracle
- an existing feed may need a top-up or runway check
- a downstream skill or app needs feed activation as a prerequisite

## Core modes

### 1. discover-feed
Use when you need to identify the best Api3 data feed for:
- an asset
- a pair
- a chain
- a specific oracle use case

Expected output:
- feed identity
- chain availability
- whether it is discoverable
- whether it appears active/usable
- whether activation may be needed
- any ambiguity or missing mapping

### 2. ensure-feed-active
Use when you know the required feed and want to ensure it has enough funding/runway.

Default target runway:
- 90 days

Expected output:
- current funding/liveness status
- estimated runway
- whether funding/top-up is needed
- execution path or exact transaction instructions

### 3. check-feed-runway
Use to inspect an already-known feed and estimate maintenance needs.

Expected output:
- current status
- remaining runway estimate
- whether action is required soon

### 4. top-up-feed
Use when a feed exists but needs more runway.

Expected output:
- required funding token/amount
- top-up execution plan
- resulting status if executed

### 5. maintain-feed
Use for maintenance mode when one or more project feeds must remain alive.

Expected output:
- current state per feed
- top-up recommendation or actions taken
- next maintenance checkpoint recommendation

## Inputs to gather before acting

Collect these first when available:
- target chain
- asset or pair required
- use case (e.g. lending collateral pricing, borrow asset pricing)
- desired runway in days
- whether execution is allowed or discovery-only
- wallet/funder available to the agent

## Operating rules

1. Do not pretend a feed is active without checking.
2. Distinguish clearly between:
   - feed missing
   - feed present but unfunded
   - feed available on another chain only
   - feed exists but agent lacks execution capability
3. Prefer permissionless operation paths.
4. If a step cannot be done permissionlessly, say exactly why.
5. Return concrete feed identifiers and maintenance recommendations.
6. If discovery is ambiguous, surface the ambiguity instead of guessing.

## Suggested workflow

### For a new project
1. Discover feed
2. Confirm chain/feed suitability
3. Check whether active/funded
4. Ensure 90-day runway
5. Return feed details to downstream builder/deployer

### For an existing project
1. Check current runway
2. If below threshold, top up
3. Return next maintenance recommendation

## Output contract

Aim to return structured results containing:
- `feedFound`
- `discoverable`
- `active`
- `activationPossible`
- `statusClassification`
- `feedName`
- `feedAddressOrId`
- `chain`
- `funded`
- `runwayEstimateDays`
- `requiredFundingAsset`
- `estimatedFundingAmount`
- `actionsTaken`
- `transactions`
- `nextMaintenanceRecommendation`
- `warnings`

## Current implementation status

This is the initial skill skeleton.

Near-term implementation priorities:
1. feed discovery adapter
2. feed status/runway inspection
3. activation/top-up execution wrapper
4. maintenance mode
