---
name: review-analyzer
description: Extract sentiment patterns, repeated pain points, and feature requests from customer reviews to prioritize product fixes and copy improvements.
---

# Review Analyzer

Customer reviews contain the most honest, unfiltered product feedback available — but reading hundreds of individual comments to find patterns is time-consuming and easy to get wrong. This skill systematically extracts sentiment trends, recurring pain points, and explicit feature requests from review data so you can prioritize what to fix in the product and what to address proactively in your listing copy and creator briefs.

## Use when

- You have accumulated 20 or more reviews on a TikTok Shop, Amazon, Shopee, or Shopify product listing and want to understand systematically what buyers love, tolerate, or actively dislike about the item.
- Your product rating has dropped below your target threshold and you need to diagnose which specific issues are driving negative reviews before you can design a fix or supplier conversation.
- You are planning a product version update, sourcing renegotiation, or packaging redesign and want to prioritize changes based on the frequency and severity of issues customers have actually reported.
- You are rewriting a product listing, preparing a creator brief, or building a FAQ section and want to address the most common buyer objections and confusion points preemptively in the copy.

## What this skill does

Review Analyzer ingests raw customer review text — pasted directly, uploaded as a CSV, or copied from a product listing page — and applies a structured extraction framework to surface patterns across the entire review set. It categorizes each review by sentiment as positive, neutral, or negative, then tags every review with up to five topic labels drawn from a predefined ecommerce taxonomy covering packaging quality, product functionality, size and fit accuracy, delivery speed, instructions clarity, and value for money perception. It ranks pain points and praise themes by both frequency of mention and severity of customer frustration, identifies verbatim phrases most commonly used by unhappy customers which can be directly adapted into FAQ answers and listing copy improvements, and separates feature requests from quality complaints so each category can be routed to the appropriate team or action owner. The final output is structured for immediate action, not just summarized for awareness.

## Inputs required

- **reviews_text** (required): Raw customer review text in any format. Can be pasted as plain text, provided as a CSV with a review text column, or submitted as a bullet list copied from a product detail page. A minimum of ten reviews is required and thirty or more reviews is strongly recommended for statistically meaningful pattern detection.
- **product_name** (optional): Product name or category description to help the skill apply the most relevant review taxonomy and filter out off-topic or misdirected review content. Example: silicone kitchen utensil set.
- **rating_filter** (optional): Restrict analysis to reviews within a specific star rating range. Example: one to three stars only, to focus exclusively on identifying negative feedback drivers.
- **output_goal** (optional): Specify the intended use of the analysis to tailor framing and emphasis. Options include listing copy improvement, product development roadmap, creator brief objection handling, or supplier quality brief.

## Output format

The skill produces a four-section structured analysis report. The first section is a sentiment breakdown showing the percentage distribution of positive, neutral, and negative reviews alongside a one-sentence overall product health assessment. The second section is a ranked pain points list covering the top five to eight recurring issues sorted by frequency of mention, with representative verbatim quotes included for each issue to enable direct copy adaptation. The third section is a praise themes list showing what customers consistently highlight as product strengths, formatted for direct use in listing bullet points or creator talking point scripts. The fourth section is an action recommendations table that maps each identified pain point to a suggested resolution in one of three categories: product or sourcing change, listing copy update, or customer service response template. Each recommendation includes an estimated implementation effort level as low, medium, or high, and an estimated review score impact if the issue were resolved.

## Scope

- Designed for: TikTok Shop sellers, Amazon sellers, Shopify brand operators, and product development teams working with customer feedback at scale.
- Platform: Platform-agnostic — works with review text from TikTok Shop, Amazon, Shopee, Lazada, Shopify, and any other platform where customer reviews can be copied or exported.
- Language: English

## Limitations

- Requires review text to be provided manually as an input; the skill does not scrape or retrieve reviews directly from live platform pages.
- Pattern detection accuracy improves significantly with thirty or more reviews — small review sets below ten entries may produce frequency rankings that are not statistically representative.
- Does not automatically distinguish verified purchase reviews from unverified ones unless that distinction is explicitly included in the input data provided.
