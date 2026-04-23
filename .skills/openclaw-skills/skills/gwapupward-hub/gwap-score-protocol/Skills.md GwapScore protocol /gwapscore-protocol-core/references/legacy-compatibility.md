# Legacy Compatibility

## Purpose
Support coexistence with older **0–100** scoring systems during migration. This guide explains how to translate between legacy scores and the GwapScore 300–900 scale to aid adoption and compatibility with partner systems.

## Mapping concept
Legacy scores should be treated as compatibility views, not canonical truth. Always compute and store the canonical protocol score internally, then translate it when necessary.

## Suggested translation bands

- **300–399 → 0–19**
- **400–499 → 20–39**
- **500–599 → 40–59**
- **600–699 → 60–79**
- **700–799 → 80–89**
- **800–900 → 90–100**

## Rule
Store and compute only the canonical protocol score internally. Expose a translated legacy score only when required for compatibility. The translation is linear within each band but may use partner‑specific formulas outside this guidance.

## Recommended payload
When returning a legacy score for clients still using the old scale, include these fields:
- `protocolScore`
- `legacyScore`
- `scoreBand`
- `confidence`
- `scoreVersion`

Always indicate which scoring version or policy is used to avoid confusion.