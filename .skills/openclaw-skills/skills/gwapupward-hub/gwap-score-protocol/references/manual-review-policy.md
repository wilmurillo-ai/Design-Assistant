# Manual Review Policy

## Purpose
Define when automatic scoring is insufficient and human oversight is required. Manual review provides a check on the deterministic engine, catching edge cases, conflicting evidence, and abuse attempts.

## Trigger manual review when
- Severe negative attestation appears (e.g., **CONFIRMED_FRAUD_RISK**, **ADMIN_ABUSE_RISK**)
- Large score movement occurs from thin evidence
- Social linkage is disputed or contradicted
- Partner attestations conflict
- Fraud allegations accumulate
- Score ceiling/cap affects important feature access
- Strong Sybil or scam‑cluster risk appears
- A manual override is requested by subject or partner

## Review outcomes
- **cleared**: evidence no longer supports the risk; attestation downgraded or removed
- **downgraded risk**: severity reduced; score cap may be raised
- **risk confirmed**: evidence validated; cap remains or is intensified
- **temporary cap retained**: caution remains until more evidence arrives
- **trust freeze**: subject access is limited pending further evidence
- **score corrected**: scoring error fixed; explanation logged
- **attestation revoked**: a specific attestation is invalidated
- **dispute escalated**: forwarded to arbitration or higher authority

## Manual adjustment rules
Manual overrides must:
- Be explicit and associated with a user/analyst identity
- Be logged with date/time and reason
- Explain the rationale for the adjustment
- Be bounded (e.g., maximum ±25 normally; larger only for severe correction cases)
- Never hide the original evidence or reasoning path

## Suggested manual adjustment bound
- **±25** normally
- Larger adjustments require a documented policy deviation and audit note