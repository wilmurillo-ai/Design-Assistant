---
name: supplier-scorecard
description: Track and score supplier reliability, quality consistency, lead time accuracy, and communication to make sourcing decisions based on evidence.
---

# Supplier Scorecard

Choosing the wrong supplier costs far more than the price difference on a quote — it shows up as late shipments, inconsistent quality, customer returns, and listing suspensions. This skill builds a structured scoring framework for evaluating your suppliers across reliability, quality, lead time accuracy, communication responsiveness, and cost competitiveness so you can make sourcing decisions backed by evidence instead of gut feeling or whoever quoted cheapest last month.

## Use when

- You are comparing two or more suppliers for the same product and need an objective framework to evaluate which one is the better long-term partner beyond just unit cost
- You have been experiencing recurring quality issues like defective units, wrong color batches, or inconsistent sizing and want to document the pattern systematically before negotiating with or replacing a supplier
- Your supplier frequently ships late or delivers quantities that do not match your purchase order and you want to quantify the reliability gap to support a conversation about penalties or alternative sourcing
- You manage a portfolio of 5 or more suppliers across different product categories and need a quarterly review process to rank them and allocate future orders toward your best performers
- You are onboarding a new supplier from Alibaba, 1688, or a trade show contact and want to set up a tracking system from day one to monitor their performance against your standards

## What this skill does

This skill creates a weighted scoring matrix that evaluates each supplier across five core dimensions: on-time delivery rate, product quality and defect rate, lead time accuracy versus quoted timelines, communication responsiveness and problem resolution speed, and total landed cost competitiveness. You provide your experience data — delivery dates versus promised dates, inspection results, defect counts, response times to messages, and pricing — and the skill calculates a composite score from 0 to 100 for each supplier. It then ranks your suppliers, highlights critical performance gaps, flags any supplier whose score has declined over recent evaluation periods, and provides specific talking points for performance review meetings. The framework is designed to work whether you have two suppliers or twenty, and whether you track data in spreadsheets, your ERP, or just your email history.

## Inputs required

- **Supplier name(s)** (required): The suppliers you want to evaluate. Example: "Guangzhou Textiles Co., Yiwu Smart Home Factory, Bangkok Packaging Ltd."
- **Delivery performance data** (required): How many orders were placed, how many arrived on time, how many were late and by how many days. Example: "12 POs placed in Q1, 9 on time, 2 late by 5 days, 1 late by 14 days."
- **Quality data** (required): Defect rates, return rates, or inspection results per supplier. Example: "3.2% defect rate on last 3 shipments, mostly cosmetic scratches on outer packaging."
- **Lead time data** (required): Quoted lead time versus actual lead time for recent orders. Example: "Quoted 30 days, actual average 38 days across last 5 orders."
- **Communication notes** (optional): How quickly the supplier responds to messages, whether they proactively flag delays or issues, and how they handle disputes. Including this gives a more complete picture. Example: "Usually replies within 4 hours on WeChat, proactively notified us about a 3-day delay once."
- **Pricing and cost data** (optional): Unit costs, MOQ requirements, payment terms, and any hidden costs like tooling fees or labeling charges. Helps the cost competitiveness scoring. Example: "Unit cost $4.20 at MOQ 500, 30% deposit required, free labeling."

## Output format

The output contains five sections. First, a **Scorecard Summary Table** showing each supplier's score across all five dimensions plus a weighted composite score out of 100, with color-coded risk levels for any dimension scoring below 60. Second, a **Supplier Ranking** listing all evaluated suppliers from highest to lowest composite score with a one-line summary of their key strength and biggest weakness. Third, a **Detailed Dimension Breakdowns** providing the data behind each score so you can see exactly where points were gained or lost — for example, "on-time delivery scored 72 because 3 of 12 orders arrived more than 3 days late." Fourth, a **Trend Analysis** comparing current scores to previous evaluations if historical data is provided, flagging any supplier whose score dropped by more than 10 points. Fifth, an **Action Recommendations** section with specific next steps: which suppliers to reward with larger orders, which to put on performance improvement plans, and which to begin replacing.

## Scope

- Designed for: ecommerce operators, sourcing managers, and brand owners who work with manufacturing or trading company suppliers
- Platform context: platform-agnostic — applicable whether you sell on Amazon, TikTok Shop, Shopify, Shopee, or wholesale channels
- Language: English

## Limitations

- Does not integrate with supplier management platforms or ERPs directly; you must input performance data manually or from your own tracking records
- Scoring weights are based on general ecommerce best practices and may need adjustment for industries with unusual requirements like perishable goods or hazardous materials
- Cannot verify supplier claims independently — the quality of the scorecard depends on the accuracy and completeness of the data you provide