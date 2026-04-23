---
name: headphone-review
description: Use this skill when the user wants a buyer-facing long review of a headphone, IEM, earbud, or TWS model by name. Use AskUserQuestion in option mode first for language and description mode, then turn multilingual reviews and official specs into a pure-Markdown article with a strong but concise disagreement section and more human-sounding prose.
---

# Headphone Review

Use this skill when the user names a headphone, IEM, earbud, or TWS model and wants a buyer-facing long review: what it sounds like, who it fits, who should skip it, and where reviewers agree or disagree.

When web lookup is needed, also use `$web-access` or the environment's browsing tools.

## Trigger Hints

- Model-name requests such as `WH-1000XM5`, `IE 900`, `Blessing 3`, `Susvara`
- Questions like `这耳机适合谁`, `什么声音`, `值不值得买`, `fit`, `sound signature`, `should I buy`
- Requests to aggregate multilingual reviews into one conclusion

Do not use this skill for pure repair, firmware, pairing, or EQ-only tasks unless the user also wants a buying summary.

## Workflow

1. Ask the missing preference questions first with `AskUserQuestion` in option mode, not as free-form text.
Language options: `中文`, `English`
Description mode options: `客观（偏理性、直接）`, `情绪化抽象（偏氛围、意象）`
Read [`rules/intake.md`](./rules/intake.md).

2. Gather multilingual evidence and reduce it into facts, consensus, and uncertainty.
Read [`rules/research.md`](./rules/research.md).

3. Write the review in pure Markdown with the chosen language and description mode.
Read [`rules/output.md`](./rules/output.md) and [`rules/humanize.md`](./rules/humanize.md).

4. If you are validating sample outputs, score them against the eval rules.
Read [`rules/eval.md`](./rules/eval.md).

## Done When

The review clearly answers:

1. what it sounds like
2. strengths and weaknesses
3. who should buy it
4. who should avoid it
5. where reviewers disagree and why
6. confidence level and evidence boundary
