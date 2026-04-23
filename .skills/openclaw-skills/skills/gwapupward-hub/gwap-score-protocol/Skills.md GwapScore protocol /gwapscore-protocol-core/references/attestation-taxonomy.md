# Attestation Taxonomy

## Purpose
Attestations are durable, score‑relevant protocol facts derived from canonical events. They represent the distilled judgement about an event’s impact on trust, along with metadata for weight, decay, and severity. An attestation captures whether an event is positive, negative, or contextual and how long its influence should last.

## Required fields
- `attestationId`
- `subjectId`
- `attestationType`
- `polarity`
- `severity`
- `sourceEvidence`
- `firstObservedAt`
- `lastConfirmedAt`
- `expiresAt`
- `decayModel`
- `scoreWeight`
- `explanation`
- `status`

## Status values
- **active**: currently influencing the score
- **decayed**: influence reduced according to decay model
- **revoked**: invalidated by dispute or error
- **disputed**: under review, not currently applied
- **superseded**: replaced by a new attestation of the same type

## Positive attestations
- `WALLET_LONGEVITY_CONFIRMED`
- `LINKED_IDENTITY_CONTINUITY_CONFIRMED`
- `CONSISTENT_ACTIVITY_CONFIRMED`
- `COUNTERPARTY_DIVERSITY_CONFIRMED`
- `REPEAT_TRUSTED_COUNTERPARTY_BEHAVIOR`
- `PROTOCOL_PARTICIPATION_CONFIRMED`
- `ESCROW_RELIABILITY_CONFIRMED`
- `REPAYMENT_RELIABILITY_CONFIRMED`
- `VERIFIED_PUBLIC_REPUTATION_CONFIRMED`
- `AUTHENTIC_SOCIAL_ENGAGEMENT_CONFIRMED`
- `COMMUNITY_REPUTATION_CONFIRMED`
- `RECOVERY_STREAK_CONFIRMED`

## Negative attestations
- `SCAM_EXPOSURE_RISK`
- `CIRCULAR_FLOW_RISK`
- `SYBIL_PATTERN_RISK`
- `SUSPICIOUS_BALANCE_BEHAVIOR_RISK`
- `REPAYMENT_RELIABILITY_FAILURE`
- `DISPUTE_RISK`
- `FRAUD_REPORT_RISK`
- `CONFIRMED_FRAUD_RISK`
- `BOT_ENGAGEMENT_RISK`
- `IDENTITY_LINK_INTEGRITY_RISK`
- `ADMIN_ABUSE_RISK`
- `INACTIVITY_DECAY_ACTIVE`

## Neutral / contextual attestations
- `LIMITED_HISTORY_CONTEXT`
- `NEW_SUBJECT_CONTEXT`
- `MANUAL_REVIEW_PENDING`
- `PARTNER_ATTESTATION_PRESENT`
- `DATA_COMPLETENESS_LIMITED`

## Rule
Never score raw social signals directly if the protocol requires they first become capped attestations. Social metrics should flow through this attestation layer to enforce caps and decay.