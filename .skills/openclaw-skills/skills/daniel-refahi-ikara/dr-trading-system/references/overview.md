# Overview

`dr-trading-system` is a reusable trading-job framework.

## Goals
- shared engine
- config-driven jobs
- provider abstraction
- paper-first execution
- approval-gated buy/sell actions
- per-job reporting
- daily assessment mode

## Core principle
Keep these separated:
- data collection engine
- calculation / strategy engine
- execution engine
- reporting engine

This allows provider replacement with minimal impact to the strategy engine.
