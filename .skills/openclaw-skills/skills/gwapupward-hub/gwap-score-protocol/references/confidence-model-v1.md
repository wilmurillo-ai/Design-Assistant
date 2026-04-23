# Confidence Model v1

## Objective
Confidence measures how strongly the protocol can defend the assigned score. It is a reflection of certainty about the trust estimate, not a measure of trust itself.

## Confidence levels
- **low**
- **moderate**
- **high**
- **very high**

## Confidence drivers

### Positive confidence inputs
- Evidence spans more than **180 days**
- Multiple independent sources agree
- At least one verified issuer or partner source exists
- Protocol‑native outcomes are abundant
- No major unresolved contradictions exist

### Negative confidence inputs
- New wallet or thin history
- Weak social linkage
- Conflicting partner evidence
- Incomplete onchain data
- Unresolved dispute or review
- Sudden sharp score movement from limited evidence

## Suggested numeric mapping
Internal confidence score range:
- **0.00–0.29**: low
- **0.30–0.59**: moderate
- **0.60–0.84**: high
- **0.85–1.00**: very high

## Example confidence formula
```
confidence_score = bounded weighted average of:
  evidence coverage
  source independence
  time depth
  verification level
  contradiction penalty
  review pending penalty
```

## Simplified operational rubric

### Low
- Thin or weak evidence
- Young subject
- Conflicting signals
- Score should be treated cautiously

### Moderate
- Some meaningful history
- Limited but useful corroboration
- No strong verified breadth yet

### High
- Strong and consistent history
- Multiple reliable inputs
- Low unresolved conflict

### Very high
- Long time horizon
- Verified, consistent, multi‑source evidence
- Very low contradiction
- Little ambiguity