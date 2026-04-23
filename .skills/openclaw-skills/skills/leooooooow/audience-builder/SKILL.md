---
name: audience-builder
description: Design targeted ad audiences for ecommerce campaigns across Meta, TikTok, and Google by combining purchase behavior, interest signals, lookalike modeling, and retargeting segments with budget allocation recommendations.
---

# Audience Builder

Most ecommerce advertisers stack generic interest audiences on Meta, broad targeting on TikTok, and one branded search campaign on Google and call it a media plan. Audience Builder helps you design a layered audience architecture across all three platforms so your first-party purchase data, browsing behavior, and lookalike seeds are deployed where each platform actually rewards them.

## Use when

- A brand says "I'm burning ad budget on Meta interest stacks that don't convert — can you rebuild my audience structure from first-party data?"
- A TikTok Shop seller asks "what audiences should I turn on for Video Shopping Ads versus Product Shopping Ads, and how do I keep them from overlapping?"
- A DTC founder is launching on Google Ads for the first time and wants to know which customer match lists, in-market segments, and YouTube remarketing audiences to build before spending a dollar.
- A team is preparing a Q4 media plan and needs a complete audience map: cold prospecting, warm retargeting, and customer re-engagement — with budget splits that reflect funnel stage and platform strengths.

## What this skill does

Builds a three-column audience architecture for Meta, TikTok, and Google from your customer file and pixel data. For each platform it lays out prospecting audiences (interest stacks, broad with optimization, in-market segments), seeded lookalikes at multiple similarity percentages, engagement-based warm audiences (video viewers, profile visitors, page engagers), and bottom-of-funnel retargeting segments (viewed product, added to cart, initiated checkout, purchaser exclusions). It then recommends a budget split across funnel stages, flags overlap risks, and specifies exclusion rules so platforms don't compete for the same user.

## Inputs required

- **Customer file export** (required): at minimum email and purchase history, ideally with AOV, order count, first order date, and product categories.
- **Pixel / conversion API event volume** (required): monthly counts for view content, add to cart, initiate checkout, and purchase on each platform you advertise on.
- **Product catalog structure** (required): main categories, hero SKUs, bundle SKUs, and which products are allowed to be advertised (platform policy or margin reasons).
- **Current ad accounts and spend** (required): monthly spend per platform, current ROAS benchmarks, and any audience saturation issues you've already noticed.
- **Target markets** (optional): countries or regions to include and exclude; affects audience size and lookalike source selection.
- **Brand restrictions** (optional): any competitor or sensitive-interest exclusions, blocked placements, or creator-content policies.
- **Seasonality goals** (optional): upcoming launches, sales events, or inventory clearance windows that should shift audience weighting.

## Output format

A platform-by-platform audience map organized by funnel stage, each audience entry including exact setup instructions (what to name it, which source data to upload, which inclusion and exclusion logic to apply, which optimization event to pair it with, and the expected audience size range). Below the audience map, a budget allocation table shows monthly spend split across prospecting, warm, and retargeting on each platform, with reasoning. A final section lists the top three overlap and cannibalization risks with specific exclusion rules to prevent them.

## Scope

- Designed for: ecommerce operators, performance marketers, and agency account managers running multi-platform paid media.
- Platform context: Meta Ads, TikTok Ads Manager, and Google Ads. Other platforms (Pinterest, Snap) mentioned only as adjacent references.
- Language: English.

## Limitations

- Does not connect to ad platform APIs; all audience setup must be executed manually in each platform's UI.
- Lookalike performance depends on platform-side data availability and cannot be predicted with certainty.
- Does not replace creative strategy — audience architecture sets the stage, but creatives still determine conversion rate.
