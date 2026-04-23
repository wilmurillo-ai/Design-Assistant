---
name: Amazon Best Sellers API
description: Analyze Amazon Best Sellers workflows with JustOneAPI, including best Sellers.
author: JustOneAPI
homepage: https://api.justoneapi.com
metadata: {"openclaw":{"homepage":"https://api.justoneapi.com","primaryEnv":"JUST_ONE_API_TOKEN","requires":{"bins":["node"],"env":["JUST_ONE_API_TOKEN"]},"skillKey":"justoneapi_amazon_get_best_sellers"}}
---

# Amazon Best Sellers

This skill wraps 1 Amazon Best Sellers operations exposed by JustOneAPI. It is strongest for best Sellers. Expect common inputs such as `category`, `country`, `page`.

## When To Use It

- The user needs best Sellers on Amazon Best Sellers.
- The user can provide identifiers or filters such as `category`, `country`, `page`.
- The user wants an exact API-backed answer instead of a freeform summary.

## Representative Operations

- `getBestSellersV1`: Best Sellers — Get Amazon best Sellers data, including rank positions, product metadata, and pricing, for identifying trending products in specific categories, market share analysis and category research, and tracking sales rank and popularity over time

## Available Versions

These endpoint versions are grouped in this interface-level skill.

- `v1`: `getBestSellersV1` - `GET /api/amazon/get-best-sellers/v1`

## Request Pattern

- 1 operations are available in this skill.
- HTTP methods used here: `GET`.
- The most common non-token parameters are `category`, `country`, `page`.
- All operations in this skill are parameter-driven requests; none require a request body.
- This interface-level skill groups endpoint versions that share the same path after removing the trailing `/vN` version segment.

## How To Work

1. Read `generated/operations.md` before choosing an endpoint.
2. Start with one of these operations when it matches the user's request: `getBestSellersV1`.
3. Pick the smallest matching operation instead of guessing.
4. Ask the user for any missing required parameter. Do not invent values.
5. Call the helper with:

```bash
node {baseDir}/bin/run.mjs --operation "<operation-id>" --token "$JUST_ONE_API_TOKEN" --params-json '{"key":"value"}'
```

## Environment

- Required: `JUST_ONE_API_TOKEN`
- This skill uses `JUST_ONE_API_TOKEN` only for authenticated Just One API requests.
- Keep `JUST_ONE_API_TOKEN` private. Do not paste it into chat messages, screenshots, or logs.
- Get a token from [Just One API Dashboard](https://dashboard.justoneapi.com/en/login?utm_source=clawhub.ai&utm_medium=referral&utm_campaign=justoneapi_amazon_get_best_sellers&utm_content=project_link).
- Authentication details: [Just One API Usage Guide](https://docs.justoneapi.com/en/?utm_source=clawhub.ai&utm_medium=referral&utm_campaign=justoneapi_amazon_get_best_sellers&utm_content=project_link).

## Output Rules

- Start with a plain-language answer tied to the Amazon Best Sellers task the user asked for.
- Include the most decision-relevant fields from the selected endpoint before dumping raw JSON.
- When using `getBestSellersV1`, explain why the returned fields answer the user's question.
- If the user gave filters such as `category`, `country`, `page`, echo those back so the scope is explicit.
- If the backend errors, include the backend payload and the exact operation ID.
