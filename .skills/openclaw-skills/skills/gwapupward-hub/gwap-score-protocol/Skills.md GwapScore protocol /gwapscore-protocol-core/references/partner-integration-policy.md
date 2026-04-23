# Partner Integration Policy

## Purpose
Define how external platforms contribute score‑relevant evidence safely and consistently. Partners provide critical data for attesting escrow outcomes, repayments, and identity verification, but their inputs must follow strict standards to prevent abuse.

## Partner responsibilities
Partners should send:
- Stable subject identifiers (e.g., wallet address, subject ID)
- Canonical or mappable event types
- Timestamps for when the event occurred and was observed
- Evidence references or transaction IDs
- Event outcome or status
- Issuer identity (partner name and relevant key)
- Idempotency key to avoid duplication

## Good partner event categories
- **Escrow completion**: signals successful trade or transaction
- **Repayment success**: indicates timely and full loan repayment
- **Dispute outcome**: outcome of dispute resolution
- **Verified merchant onboarding**: confirms a business’s legitimacy
- **Fraud adjudication**: outcome of an investigation
- **Identity link confirmation**: when a partner verifies social identity linkage
- **Successful order completion**: deliverable or service executed

## Poor partner event categories
- Vague reputation claims with no evidence
- Vanity or popularity stats
- Unverified “trusted user” flags with no backing data

## Partner scoring rules
- Partner evidence contributes more when verified and historically reliable
- Partner evidence must still pass canonical event mapping; events with unknown types must be reviewed before inclusion
- Conflicting partner evidence lowers confidence rather than simply averaging out

## Integration safeguards
- Partners must implement idempotency; duplicate events should not inflate or reduce scores
- Events should be signed or authenticated
- Rate limits should be applied to prevent spam