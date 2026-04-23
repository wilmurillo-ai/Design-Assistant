---
name: Amazon Product Top Reviews API
description: Analyze Amazon Product Top Reviews workflows with JustOneAPI, including product Top Reviews.
author: JustOneAPI
homepage: https://api.justoneapi.com
metadata: {"openclaw":{"homepage":"https://api.justoneapi.com","primaryEnv":"JUST_ONE_API_TOKEN","requires":{"bins":["node"],"env":["JUST_ONE_API_TOKEN"]},"skillKey":"justoneapi_amazon_get_product_top_reviews"}}
---

# Amazon Product Top Reviews

This skill wraps 1 Amazon Product Top Reviews operations exposed by JustOneAPI. It is strongest for product Top Reviews. Expect common inputs such as `asin`, `country`.

## When To Use It

- The user needs product Top Reviews on Amazon Product Top Reviews.
- The user can provide identifiers or filters such as `asin`, `country`.
- The user wants an exact API-backed answer instead of a freeform summary.

## Representative Operations

- `getProductTopReviewsV1`: Product Top Reviews — Get Amazon product Top Reviews data, including most helpful) public reviews, for sentiment analysis and consumer feedback tracking, product research and quality assessment, and monitoring competitor customer experience

## Available Versions

These endpoint versions are grouped in this interface-level skill.

- `v1`: `getProductTopReviewsV1` - `GET /api/amazon/get-product-top-reviews/v1`

## Request Pattern

- 1 operations are available in this skill.
- HTTP methods used here: `GET`.
- The most common non-token parameters are `asin`, `country`.
- All operations in this skill are parameter-driven requests; none require a request body.
- This interface-level skill groups endpoint versions that share the same path after removing the trailing `/vN` version segment.

## How To Work

1. Read `generated/operations.md` before choosing an endpoint.
2. Start with one of these operations when it matches the user's request: `getProductTopReviewsV1`.
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
- Get a token from [Just One API Dashboard](https://dashboard.justoneapi.com/en/login?utm_source=clawhub.ai&utm_medium=referral&utm_campaign=justoneapi_amazon_get_product_top_reviews&utm_content=project_link).
- Authentication details: [Just One API Usage Guide](https://docs.justoneapi.com/en/?utm_source=clawhub.ai&utm_medium=referral&utm_campaign=justoneapi_amazon_get_product_top_reviews&utm_content=project_link).

## Output Rules

- Start with a plain-language answer tied to the Amazon Product Top Reviews task the user asked for.
- Include the most decision-relevant fields from the selected endpoint before dumping raw JSON.
- When using `getProductTopReviewsV1`, explain why the returned fields answer the user's question.
- If the user gave filters such as `asin`, `country`, echo those back so the scope is explicit.
- If the backend errors, include the backend payload and the exact operation ID.
