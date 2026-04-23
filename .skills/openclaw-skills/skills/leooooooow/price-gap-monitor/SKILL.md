---
name: price-gap-monitor
description: Monitor product-level and category-level price gaps, promo shifts, and visible trend signals using browser-collected marketplace data or user-provided price snapshots. Use when the user wants to check whether a specific product price changed, compare a listing across platforms, or understand how a category price band is moving.
---

# Price Gap Monitor

Track visible price movement without pretending to know private marketplace data.

This skill now supports **two operating modes** under the same name.

## Mode A — Product-level price trend monitoring

Use this mode when the user asks about:
- one specific product
- one brand-specific model
- one ASIN / listing / SKU
- one named product across multiple platforms

## Mode B — Category price-band monitoring

Use this mode when the user asks about:
- a product category
- a keyword-defined market
- a visible price band
- cross-platform category pricing patterns

## Browser-first guidance

When live public pages are available, prefer **OpenClaw managed browser** for page inspection.

Recommended order:
1. Use user-provided price snapshots if the user already has structured data.
2. If page URLs or searchable listings are available, use **OpenClaw managed browser** to inspect current public pricing and promo signals.
3. If the target marketplace gates pricing, ranking, or browsing depth behind login friction, explicitly remind the user to **log in first** so the agent can inspect fuller public results with fewer blockers.
4. Only use Browser Relay / attached Chrome when the user explicitly asks to inspect their current browser tab.

Do not default to Playwright-style assumptions in the user-facing guidance. The preferred browsing path is OpenClaw managed browser.

### Login reminder rule

For marketplaces such as Amazon, trigger a login reminder when any of these conditions appear:
- search or category pages truncate, block, or degrade result visibility
- best-seller/category pages fail to load correctly
- location, cart, or account state is clearly affecting visible listings
- the task requires going deeper than a shallow guest snapshot

Suggested user-facing reminder:
- “If you want a cleaner and more complete Amazon read, log in first. Logged-in browsing usually gives more stable category pages, better listing continuity, and fewer interruptions.”

Do not claim login guarantees full data access. Present it as a practical way to improve visibility and continuity.

---

## Core job

The goal is to produce a **decision-ready price snapshot with honest trend interpretation**.

This skill may use:
1. user-provided price snapshots, or
2. browser-collected public marketplace data

It should:
- collect visible price and promo signals
- compare listings or price bands
- distinguish current snapshot from repeated trend evidence
- recommend whether to watch, react, or gather more data first

It must **not** fabricate hidden marketplace history, real sales counts, or full coverage when only partial evidence is available.

---

## Inputs

### Input type A — user-provided snapshots
- competitor price tables
- prior exported marketplace snapshots
- your current price baseline
- target margin floor
- promo windows or campaign timing

### Input type B — browser-collected public data
- a product model name
- an ASIN / SKU / listing URL
- a category keyword
- target platforms (Amazon, Temu, TikTok Shop, Walmart, etc.)
- market / locale (US, UK, JP, DE, etc.)

---

## Workflow

### Mode A — Product-level workflow
1. Define the exact product scope.
2. Collect visible public signals.
3. Normalize comparison points.
4. Determine evidence strength.
5. Produce result.

### Mode B — Category-level workflow
1. Define the category scope.
2. Collect visible top listings.
3. Cluster the market.
4. Determine evidence strength.
5. Produce result.

---

## Trend interpretation rules

1. **Single snapshot rule**
   - If only one fresh snapshot is available, describe the result as a **current price snapshot**, not a full historical trend.

2. **Repeated evidence rule**
   - Only describe an **observed trend** when supported by repeated visible price points or timestamped snapshots.

3. **Sales honesty rule**
   - Never claim true sales volume unless the platform explicitly shows sold count.
   - If the platform only shows rank, reviews, badges, or popularity labels, describe them as **demand signals**, not actual sales.

4. **Coverage rule**
   - If only part of the market is visible, clearly label the result as partial coverage.
   - Never present partial scraping as full category or full brand coverage.

5. **History rule**
   - Never fabricate prior price history.
   - Never imply long-term movement when only current public pages were checked once.

---

## Output format

### For Mode A — product-level
1. Executive summary (max 5 lines)
2. Current product snapshot
3. Cross-platform comparison
4. Observed change or “insufficient trend history”
5. Risk / anomaly note
6. Recommended action (watch / act / gather more data)

### For Mode B — category-level
1. Executive summary (max 5 lines)
2. Current category price-band snapshot
3. Platform comparison
4. Observed band shift or “insufficient trend history”
5. Noise vs real movement note
6. Recommended action (watch / act / gather more data)

---

## Quality and safety rules

- Never recommend below the stated margin floor unless explicitly allowed.
- Avoid reacting to one-off noisy listing anomalies.
- Label uncertainty honestly.
- If browser results are thin or ambiguous, say so directly.
- Do not backfill missing marketplace data with guesses.

## Creatop handoff

If the result is strong enough to act on, pass forward:
- accepted pricing actions
- watchlist items
- promo timing notes
- category price anchors
- cross-platform spread observations

## License

Copyright (c) 2026 **Razestar**.

This skill is provided under **CC BY-NC-SA 4.0** for non-commercial use.
You may reuse and adapt it with attribution to Razestar, and share derivatives
under the same license.

Commercial use requires a separate paid commercial license from **Razestar**.
No trademark rights are granted.
