---
name: Amazon Products By Category API
description: Analyze Amazon Products By Category workflows with JustOneAPI, including products By Category.
author: JustOneAPI
homepage: https://api.justoneapi.com
metadata: {"openclaw":{"homepage":"https://api.justoneapi.com","primaryEnv":"JUST_ONE_API_TOKEN","requires":{"bins":["node"],"env":["JUST_ONE_API_TOKEN"]},"skillKey":"justoneapi_amazon_get_category_products"}}
---

# Amazon Products By Category

This skill wraps 1 Amazon Products By Category operations exposed by JustOneAPI. It is strongest for products By Category. Expect common inputs such as `categoryId`, `country`, `page`, `sortBy`.

## When To Use It

- The user needs products By Category on Amazon Products By Category.
- The user can provide identifiers or filters such as `categoryId`, `country`, `page`, `sortBy`.
- The user wants an exact API-backed answer instead of a freeform summary.

## Representative Operations

- `getProductsByCategoryV1`: Products By Category — Get Amazon products By Category data, including title, price, and rating, for category-based product discovery and returns product information such as title, price, and rating

## Available Versions

These endpoint versions are grouped in this interface-level skill.

- `v1`: `getProductsByCategoryV1` - `GET /api/amazon/get-category-products/v1`

## Request Pattern

- 1 operations are available in this skill.
- HTTP methods used here: `GET`.
- The most common non-token parameters are `categoryId`, `country`, `page`, `sortBy`.
- All operations in this skill are parameter-driven requests; none require a request body.
- This interface-level skill groups endpoint versions that share the same path after removing the trailing `/vN` version segment.

## How To Work

1. Read `generated/operations.md` before choosing an endpoint.
2. Start with one of these operations when it matches the user's request: `getProductsByCategoryV1`.
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
- Get a token from [Just One API Dashboard](https://dashboard.justoneapi.com/en/login?utm_source=clawhub.ai&utm_medium=referral&utm_campaign=justoneapi_amazon_get_category_products&utm_content=project_link).
- Authentication details: [Just One API Usage Guide](https://docs.justoneapi.com/en/?utm_source=clawhub.ai&utm_medium=referral&utm_campaign=justoneapi_amazon_get_category_products&utm_content=project_link).

## Output Rules

- Start with a plain-language answer tied to the Amazon Products By Category task the user asked for.
- Include the most decision-relevant fields from the selected endpoint before dumping raw JSON.
- When using `getProductsByCategoryV1`, explain why the returned fields answer the user's question.
- If the user gave filters such as `categoryId`, `country`, `page`, echo those back so the scope is explicit.
- If the backend errors, include the backend payload and the exact operation ID.
