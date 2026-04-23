# Feature Gating Thresholds

## Purpose
Support product features based on trust score bands without hardcoding raw score logic everywhere. Feature gating allows the product to enable or restrict capabilities based on risk tolerance and user trustworthiness.

## Suggested thresholds

### Read‑only / basic participation
- **300+**

### Low‑risk community features
- **450+**

### Marketplace participation
- **550+**

### Seller / creator monetization access
- **600+**

### Escrow‑light transactions
- **620+**

### Escrow‑optional higher‑value interactions
- **680+**

### Premium visibility / verified trust badge consideration
- **720+**

### Fast‑lane approvals / reduced friction
- **760+**

### Institutional‑grade partner trust tier
- **800+**

## Important rule
Use both score and confidence where risk matters. For example, do not grant a high‑value feature at a score of 720 if the confidence level is low and a cap is active. Always consider the presence of severe negative attestations and manual review flags.