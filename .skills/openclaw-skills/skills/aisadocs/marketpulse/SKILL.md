---
name: marketpulse
description: 'Query stocks, crypto, prediction markets, and portfolio research through AIsa. Use when: the user needs market data, screening, price history, or investment analysis. Supports research and analysis-ready outputs.'
author: AIsa
version: 1.0.1
license: MIT
user-invocable: true
primaryEnv: AISA_API_KEY
requires:
  bins:
  - python3
  env:
  - AISA_API_KEY
metadata:
  aisa:
    emoji: 📊
    requires:
      bins:
      - python3
      env:
      - AISA_API_KEY
    primaryEnv: AISA_API_KEY
    compatibility:
    - openclaw
    - claude-code
    - hermes
  openclaw:
    emoji: 📊
    requires:
      bins:
      - python3
      env:
      - AISA_API_KEY
    primaryEnv: AISA_API_KEY
---

# Marketpulse

Query stocks, crypto, prediction markets, and portfolio research through AIsa. Use when: the user needs market data, screening, price history, or investment analysis. Supports research and analysis-ready outputs.

## When to use

- The user needs stocks, crypto, prediction market, or portfolio research.
- The user wants prices, screening, valuation, or event-driven analysis.
- The user wants structured financial output for downstream analysis.

## High-Intent Workflows

- Check price action and market movement.
- Screen assets or equities that match filters.
- Research portfolios, dividends, or market opportunities.

## Quick Reference

- `python3 scripts/market_client.py --help`

## Setup

- `AISA_API_KEY` is required for AIsa-backed API access.
- Use repo-relative `scripts/` paths from the shipped package.
- Prefer explicit CLI auth flags when a script exposes them.

## Example Requests

- Query NVDA price history and analyst expectations
- Find stocks matching a screening rule
- Check BTC and ETH market data for a portfolio view

## Guardrails

- Do not invent prices or financial metrics.
- Do not turn examples into financial advice.
- If an upstream endpoint is limited, say so directly.
