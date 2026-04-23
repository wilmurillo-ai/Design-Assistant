# Eval Rules

Chinese output is the primary evaluation surface.

If the sample includes interaction, first check whether it asked for:

- language
- description mode
- whether it used the question tool path correctly

Before scoring, check `rules/humanize.md`.

Hard fail signals:

- em dash appears in the review
- contrast templates like `不是……而是……` or `与其说……不如说……` appear more than once
- the prose reads like a clean template with repeated paragraph rhythm

Score these `6` dimensions from `1-5`:

1. language choice is explicit
2. model identification is correct or clearly assumed
3. Chinese reads like a human long article rather than bullet expansion
4. the two-sentence verdict stays within 200 Chinese characters and says something real
5. the disagreement section is specific, concise, easy to understand, and not formulaic
6. source/confidence handling is honest even without listing sources at the end

Pass bar:

- `26/30+` usable as the main output shape
- `22-25/30` usable but still soft in prose or judgment
- `21/30 and below` revise before scaling
