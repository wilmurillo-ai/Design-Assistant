# GwapScore Scoring Model v1

## Objective
Produce a deterministic 300–900 trust score using a base score plus weighted attestation impacts, caps, and floors. The scoring model is designed to reward clean, consistent behavior and penalize severe risk signals while remaining conservative when evidence is thin.

## Base score
All new subjects begin at **500**. This baseline is neutral: neither trusted nor condemned. It indicates that evidence is still needed before making judgments.

## Score formula

```
protocol_score = clamp(300, 900, base_score + positive_sum - negative_sum + recovery_sum + manual_adjustment)
```

Where:
- `base_score = 500`
- `positive_sum` = sum of active positive attestation weights
- `negative_sum` = sum of active negative attestation penalties
- `recovery_sum` = bounded recovery credit
- `manual_adjustment` = 0 by default, or policy‑bound override after manual review

## Positive attestation weights

### Identity / continuity
- `WALLET_LONGEVITY_CONFIRMED`: **+20**
- `LINKED_IDENTITY_CONTINUITY_CONFIRMED`: **+15**
- `VERIFIED_PUBLIC_REPUTATION_CONFIRMED`: **+12**

### Behavioral reliability
- `CONSISTENT_ACTIVITY_CONFIRMED`: **+35**
- `COUNTERPARTY_DIVERSITY_CONFIRMED`: **+18**
- `REPEAT_TRUSTED_COUNTERPARTY_BEHAVIOR`: **+25**
- `PROTOCOL_PARTICIPATION_CONFIRMED`: **+12**
- `ESCROW_RELIABILITY_CONFIRMED`: **+40**
- `REPAYMENT_RELIABILITY_CONFIRMED`: **+45**
- `COMMUNITY_REPUTATION_CONFIRMED`: **+10**

### Social support
- `AUTHENTIC_SOCIAL_ENGAGEMENT_CONFIRMED`: **+8**

### Recovery
- `RECOVERY_STREAK_CONFIRMED`: **+10** to **+30** depending on sustained period

## Negative attestation penalties

### Risk
- `SCAM_EXPOSURE_RISK`: **-35**
- `CIRCULAR_FLOW_RISK`: **-60**
- `SYBIL_PATTERN_RISK`: **-75**
- `SUSPICIOUS_BALANCE_BEHAVIOR_RISK`: **-25**
- `BOT_ENGAGEMENT_RISK`: **-12**
- `IDENTITY_LINK_INTEGRITY_RISK`: **-30**

### Outcome failures
- `REPAYMENT_RELIABILITY_FAILURE`: **-55**
- `DISPUTE_RISK`: **-30**
- `FRAUD_REPORT_RISK`: **-20**
- `CONFIRMED_FRAUD_RISK`: **-120**
- `ADMIN_ABUSE_RISK`: **-90**
- `INACTIVITY_DECAY_ACTIVE`: **-10** to **-35** depending on length of inactivity

## Caps and policy ceilings

### Severe risk caps
If any of the following are active:
- `CONFIRMED_FRAUD_RISK`
- `ADMIN_ABUSE_RISK`
- `SYBIL_PATTERN_RISK` with strong evidence

Then the score ceiling defaults to **540** until manual review clears or downgrades severity.

### Moderate‑risk caps
If a subject has:
- two or more active `FRAUD_REPORT_RISK`
- active `CIRCULAR_FLOW_RISK`
- repeated `DISPUTE_RISK`

Then the score ceiling defaults to **640**.

## Social influence cap
Total score contribution from social‑linked attestations must not exceed **+25** in sum. This prevents popularity from overriding behavioral facts.

## Community vouch cap
Community or partner vouches may support confidence and minor score lift, but total non‑behavioral endorsement lift must not exceed **+20**.

## Data thinness rule
If the subject is new or evidence is incomplete:
- preserve score conservatively
- do not force the score upward using weak evidence
- attach `DATA_COMPLETENESS_LIMITED` context

## New subject policy
A new subject with low evidence may sit between **480** and **540**, depending on early positive or negative evidence.

## Exceptional band rule
Scores above **800** should require:
- strong history
- multiple independent positive sources
- low or no severe risk
- moderate‑to‑high confidence minimum