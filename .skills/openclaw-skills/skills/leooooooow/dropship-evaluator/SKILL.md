---
name: dropship-evaluator
description: Evaluate dropshipping product opportunities and supplier reliability by scoring margin potential, shipping times, supplier communication quality, sample quality, and competition saturation to avoid common pitfalls.
---

# Dropship Evaluator

This skill scores a dropshipping product idea and its supplier on the criteria that actually predict outcome — real margin after ad cost and refunds, shipping time from the customer's country, supplier responsiveness, sample quality, and how saturated the winning angle already is — so you can reject dud products before sinking ad spend on them.

## Use when

- The user is running a general or niche Shopify dropshipping store and has a shortlist of AliExpress, CJdropshipping, Zendrop, or Spocket products they are considering testing with Meta or TikTok ads.
- The user just received samples from a new supplier and wants a structured quality and reliability review before committing to a product page and creative build.
- The user is debating between two or three similar products in the same category and needs a scoring framework that compares margin potential, shipping risk, and competitive density side by side.
- The user has been burned before by long shipping times, hidden cost creep, or refund spikes and wants a pre-flight checklist that catches those risks upfront.

## What this skill does

Scores the opportunity on six weighted dimensions: margin potential (landed cost, shipping, expected CPA, refund rate), shipping reliability (origin warehouse, courier, typical days to destination, tracking quality), supplier quality (response time, stock stability, packaging, defect rate from sample), market saturation (ad library hits, search trends, number of visibly profitable competitors), product-market fit (perceived value versus price, problem-solving strength, impulse appeal), and policy risk (platform compliance, trademark exposure, category restrictions). Produces a composite score with a clear go, test-small, or skip recommendation plus the two or three specific factors most likely to break the product.

## Inputs required

- **Product URL from the supplier platform** (required): AliExpress, CJ, Zendrop, Spocket, or a direct supplier link — used as the factual anchor for cost, shipping, and supplier data.
- **Target country or countries** (required): Shipping time and refund risk shift dramatically between US, EU, UK, AU, and LATAM destinations.
- **Intended retail price and ad platform** (required): Needed to compute margin and realistic CPA ranges.
- **Sample received, yes or no, and notes** (optional): If yes, describe packaging quality, perceived value, defects, and unboxing feel.
- **Links to competitor ads, stores, or listings** (optional): Sharpens the saturation and angle-differentiation scoring.

## Output format

Four sections. (1) Scorecard table — six dimensions scored 1 to 5 with a one-sentence justification per row and a weighted composite score. (2) Economics snapshot — landed cost, suggested retail, projected contribution margin after typical refund rate, breakeven CPA, and target ROAS. (3) Risk flags — bullet-equivalent list of the top two or three concrete risks ranked by likelihood and impact, each with a mitigation. (4) Recommendation — go, test-small with a defined ad budget cap, or skip, with a short rationale and suggested next action such as ordering a sample, negotiating MOQ pricing, or moving on.

## Scope

- Designed for: dropshippers, ecommerce operators early in product validation, and agencies vetting client offers
- Platform context: AliExpress, CJdropshipping, Zendrop, Spocket, and direct factory sourcing; selling stores on Shopify, WooCommerce, or TikTok Shop
- Language: English

## Limitations

- Does not access live supplier APIs or ad libraries — all facts come from the inputs you provide.
- Margin math assumes the inputs are current; supplier prices and shipping fees shift frequently and must be re-verified before launch.
- Trademark and IP risk flags are heuristics; do not treat them as legal advice. For anything borderline, consult a qualified attorney in your jurisdiction.
