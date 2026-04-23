# Dispute and Recalculation Policy

## Purpose
Define how score disputes are handled and how recalculation requests are processed. Disputes ensure the protocol remains accountable and correctable when evidence changes or errors occur.

## Dispute triggers
- Subject claims the score is inaccurate
- Subject contests identity linkage
- Subject contests fraud or dispute attribution
- Partner submits correction or retraction
- Evidence source is amended or corrected
- Scoring model version changes

## Recalculation steps
1. Identify the prior score state, including score, confidence, and active caps
2. Gather changed events or attestations
3. Compare removed, added, refreshed, or downgraded evidence
4. Re‑run scoring with the updated attestations
5. Compare the new score and confidence against the prior state
6. Issue an explanation for the score movement
7. Preserve an audit trail of the change

## Delta categories
- **Evidence correction**: removal of incorrectly attributed events
- **Evidence expiry / decay**: removal or reduction of influence after time passes
- **New positive history**: additional positive attestations
- **New negative history**: new risk events
- **Review outcome change**: manual review decisions altering status
- **Model policy change**: update to scoring weights or rules

## Required response fields
- Prior score
- New score
- Score delta
- Changed attestations
- Confidence change
- Review result, if any
- Explanation summary