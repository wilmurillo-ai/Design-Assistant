---
name: mobile-ux-audit
description: Audit the mobile shopping experience of your ecommerce store for friction points including slow load times, hard-to-tap buttons, confusing navigation, checkout form issues, and payment method gaps that kill mobile conversion rates.
---

# Mobile UX Audit

This skill performs a structured mobile UX audit of an ecommerce storefront, identifying the specific friction points — layout, speed, input, payment, and navigation issues — that cause mobile visitors to bounce or abandon carts even when desktop performance looks healthy.

## Use when

- The user sees a large gap between mobile and desktop conversion rates, for example 1.1% on mobile versus 2.8% on desktop, and wants to understand where mobile shoppers are actually dropping off.
- The user just finished a theme migration on Shopify, BigCommerce, or WooCommerce and wants a pre-launch mobile review before turning paid traffic back on.
- The user runs mostly Meta, TikTok, or Google Shopping ads where over 70% of traffic lands on phones and suspects the landing pages, PDPs, or checkout are breaking the journey.
- The user says their Lighthouse or PageSpeed Insights mobile score is below 50 and wants practical, prioritized fixes rather than a generic checklist.

## What this skill does

Walks the full mobile shopping funnel — homepage, collection, product detail, cart, checkout, and account flows — and flags concrete issues at each step. Evaluates page weight and Core Web Vitals (LCP, INP, CLS), tap-target size and spacing, thumb-reach of primary CTAs, form field behavior (input types, autofill, error states), image and video loading strategy, sticky element intrusiveness, payment method coverage (Apple Pay, Google Pay, Shop Pay, local wallets), and accessibility basics like text contrast and zoom behavior. Every finding is tagged with severity, estimated conversion impact, and implementation effort so the team can triage.

## Inputs required

- **Store URL** (required): The public storefront URL so each page can be referenced explicitly in the findings.
- **Top 3 landing pages by paid traffic** (required): Typically a hero collection and two bestseller PDPs; audit depth focuses here.
- **Current mobile conversion rate and AOV** (required): Used to estimate dollar impact of each fix.
- **Platform and theme** (optional): Shopify theme name, WooCommerce template, or headless stack — shapes which fixes are realistic.
- **Screenshots or Loom of a real mobile session** (optional): Reveals friction that static audits miss, like scroll jank or popup stacking.

## Output format

Three deliverables. (1) Executive summary — five to eight bullet-equivalent findings ranked by expected revenue impact, written in plain language a founder can act on. (2) Per-page findings table — columns for page, issue, severity (Critical, High, Medium, Low), root cause, recommended fix, estimated dev effort in hours, and expected conversion lift band. (3) Prioritized 30-day remediation roadmap — week-by-week sequence grouping fixes by theme (speed wins, form fixes, payment wallet rollout, navigation cleanup) with dependencies and suggested owners (developer, designer, marketer).

## Scope

- Designed for: ecommerce operators, CRO leads, product managers, and front-end developers
- Platform context: Shopify, WooCommerce, BigCommerce, Magento, and headless stacks; audit logic applies to any storefront
- Language: English

## Limitations

- Does not execute live Lighthouse or WebPageTest runs — metrics must be supplied or described.
- Does not write the production code or theme edits; the output is a specification that your development team implements.
- Accessibility findings cover common WCAG A and AA issues visible from the front end; a full accessibility audit including screen-reader flows is out of scope.
