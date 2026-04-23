# Provider Adapter Contract

## Purpose
A provider adapter fetches raw market data from a provider and returns normalized output to the strategy engine.

## Inputs
- provider_id
- market
- symbols
- timeframe
- lookback_days
- as_of_time / as_of_date
- exchange/calendar context

## Per-symbol normalized output
- provider
- market
- symbol_requested
- symbol_provider
- status
- error_code
- error_message
- freshness
- bars

## Freshness fields
- latest_bar_date
- as_of_date
- stale_days
- freshness_status

## Standard status values
- ok
- stale
- permission_denied
- symbol_invalid
- provider_error
- empty
- partial

## Provider summary
- provider
- market
- symbols_requested
- symbols_ok
- symbols_stale
- symbols_permission_denied
- symbols_failed
- overall_status

## Core rule
The strategy engine should consume normalized provider output only and must not depend on provider-specific quirks.
