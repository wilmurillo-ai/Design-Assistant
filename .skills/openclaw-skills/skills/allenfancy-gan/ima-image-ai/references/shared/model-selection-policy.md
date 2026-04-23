# Model Selection Policy

Formal selection rules live in `catalog-aware-selection.md`.

The runtime chooses models in this order:

1. explicit `--model-id`
2. prompt-inferred model alias such as `MJ` or `香蕉`
3. live catalog compatibility match when the request carries explicit model constraints such as `size`, `aspect_ratio`, `n`, or `quality`
4. saved per-user preference from `~/.openclaw/memory/ima_prefs.json`
5. recommended default model for the task type

`--version-id` is optional. When omitted, the runtime binds the last matching product-list leaf, treating it as the newest available version in the current API ordering.

Current recommended defaults:

- `text_to_image` -> `doubao-seedream-4.5`
- `image_to_image` -> `doubao-seedream-4.5`

Persistence rule:

- explicit user choices and existing saved preferences may be persisted
- auto-selected live catalog compatibility matches are operational choices and are not written back as new long-term preferences
- auto-selected recommended defaults are not written back as new long-term preferences

Known aliases are normalized before lookup:

- `MJ` -> `midjourney`
- `香蕉` -> `gemini-3.1-flash-image`
- `香蕉Pro` -> `gemini-3-pro-image`
- `可梦` -> `doubao-seedream-4.5`
