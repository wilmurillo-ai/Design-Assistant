# Intake Rules

Use the `AskUserQuestion` tool to ask the following before starting:

1. Language — options: `中文`, `English`
2. Description mode — options: `客观（偏理性、直接）`, `情绪化抽象（偏氛围、意象）`

Normalize answers into:

- `中文` or `English`
- `客观` or `情绪化抽象`

If the user already gave one choice, use `AskUserQuestion` only for the missing one.
Do not start the review before both choices are known, unless the run is a fixed eval preset.

Model lock:

- Normalize to `brand + model + revision/form factor`.
- If the name is ambiguous, choose the most likely current meaning and mark the assumption in the report.
- Common traps: `Dusk`, `Xelento`, `QuietComfort Ultra`, `Utopia`.
