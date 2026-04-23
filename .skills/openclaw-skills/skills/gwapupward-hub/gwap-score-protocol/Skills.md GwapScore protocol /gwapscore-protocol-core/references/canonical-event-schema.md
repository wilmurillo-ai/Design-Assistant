# Canonical Event Schema

## Purpose
Canonical events normalize source‑specific activity into protocol‑understandable events. They provide a single vocabulary for representing disparate signals from onchain data, partner platforms, and protocol‑native operations.

## Required event fields
- `eventId`
- `subjectId`
- `subjectType`
- `eventType`
- `source`
- `sourceEventType`
- `timestamp`
- `observedAt`
- `evidenceStrength`
- `value`
- `metadata`
- `evidenceRef`
- `issuer`
- `idempotencyKey`

## Subject types
- **wallet**
- **user**
- **merchant**
- **creator**
- **partner**
- **verifier**

## Evidence strength
- **weak**: unverified or anecdotal
- **moderate**: partially verified
- **strong**: well‑supported
- **verified**: confirmed by trusted issuer

## Canonical event types

### Identity / continuity
- `SUBJECT_LINKED_IDENTITY_CONFIRMED`
- `SUBJECT_IDENTITY_LINK_DISPUTED`
- `WALLET_AGE_MILESTONE_REACHED`
- `SOCIAL_ACCOUNT_CONTINUITY_CONFIRMED`
- `VERIFIED_PUBLIC_PRESENCE_CONFIRMED`

### Behavioral
- `TX_ACTIVITY_CONSISTENCY_CONFIRMED`
- `COUNTERPARTY_DIVERSITY_CONFIRMED`
- `REPEAT_TRUSTED_COUNTERPARTY_CONFIRMED`
- `PROTOCOL_PARTICIPATION_CONFIRMED`
- `REPAYMENT_COMPLETED`
- `REPAYMENT_MISSED`
- `ESCROW_COMPLETED`
- `ESCROW_FAILED`
- `SETTLEMENT_COMPLETED`
- `REFUND_ISSUED`
- `REFUND_DISPUTED`

### Risk
- `SCAM_CLUSTER_EXPOSURE_DETECTED`
- `CIRCULAR_FLOW_PATTERN_DETECTED`
- `SYBIL_CLUSTER_PATTERN_DETECTED`
- `SUSPICIOUS_BALANCE_SPIKE_DETECTED`
- `FRAUD_REPORT_FILED`
- `FRAUD_REPORT_CONFIRMED`
- `DISPUTE_OPENED`
- `DISPUTE_LOST`
- `DISPUTE_WON`
- `ADMIN_ABUSE_CONFIRMED`

### Social / reputation
- `AUTHENTIC_ENGAGEMENT_CONFIRMED`
- `BOT_LIKE_ENGAGEMENT_DETECTED`
- `CREATOR_REPUTATION_CONFIRMED`
- `BUSINESS_REPUTATION_CONFIRMED`
- `COMMUNITY_VOUCH_RECEIVED`
- `COMMUNITY_VOUCH_REVOKED`

### Recovery / decay
- `INACTIVITY_DECAY_APPLIED`
- `RECOVERY_STREAK_CONFIRMED`
- `MANUAL_REVIEW_CLEARED`
- `MANUAL_REVIEW_FLAGGED`

## Canonical event rules
- Events must be idempotent: repeated identical source events should map to the same canonical event to avoid double counting.
- Source‑specific duplicates must map to one logical event.
- Partner events must include issuer identity to enable trust weighting.
- Evidence strength must be explicit.
- Severe risk events must be durable enough for audit; they should not be automatically removed without review or decay logic.