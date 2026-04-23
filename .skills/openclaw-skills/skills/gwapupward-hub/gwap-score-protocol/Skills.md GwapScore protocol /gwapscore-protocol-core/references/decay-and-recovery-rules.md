# Decay and Recovery Rules

## Purpose
Ensure the model values recency and allows trust repair without letting severe misconduct disappear overnight. These rules define how positive and negative attestations weaken over time and how trust can be regained through sustained positive behavior.

## Positive decay
Some positive attestations weaken if not refreshed.

### Examples
- **AUTHENTIC_SOCIAL_ENGAGEMENT_CONFIRMED**
  - Partial decay after **90 days**
  - Substantial decay after **180 days** without refresh

- **COMMUNITY_REPUTATION_CONFIRMED**
  - Partial decay after **120 days**

- **PROTOCOL_PARTICIPATION_CONFIRMED**
  - Partial decay after **180 days** of inactivity

## Stable positives
These should decay slowly or not at all while still valid:
- **WALLET_LONGEVITY_CONFIRMED**
- **LINKED_IDENTITY_CONTINUITY_CONFIRMED**
- **VERIFIED_PUBLIC_REPUTATION_CONFIRMED**

## Negative decay
Negative attestations decay more slowly than lightweight positives.

### Moderate negatives
- **DISPUTE_RISK**
  - May decay gradually after **180 days** of clean activity

- **FRAUD_REPORT_RISK**
  - Decay only if unresolved and unconfirmed after policy window
  - Repeated reports slow decay

### Severe negatives
- **CONFIRMED_FRAUD_RISK**
- **ADMIN_ABUSE_RISK**
- Strong **SYBIL_PATTERN_RISK**

These should not decay automatically in a meaningful way without review or strong recovery evidence.

## Inactivity decay
If subject is dormant:
- **90+ days** low activity: **-10**
- **180+ days** low activity: **-20**
- **365+ days** low activity: **-35**

Do not punish healthy dormant long‑term holders too aggressively if other strong trust evidence exists.

## Recovery rules
Recovery should be possible through:
- sustained clean activity
- repeated successful protocol‑native outcomes
- dispute‑free period
- repayment reliability restoration
- manual‑review clearance

## Recovery credit
- **light recovery**: **+10**
- **moderate recovery**: **+20**
- **strong recovery**: **+30**

Recovery should never erase confirmed severe misconduct instantly. Persistent negative attestations require consistent evidence of change and possibly manual review.