---
name: skylv-webhook-tester
slug: skylv-webhook-tester
version: 1.0.0
description: "Tests and debugs webhooks. Inspects requests and validates responses. Triggers: test webhook, webhook debug, http webhook."
author: SKY-lv
license: MIT
tags: [automation, tools]
keywords: [automation, tools]
triggers: webhook-tester
---

# Webhook Tester

## Overview
Helps test, debug, and validate webhook integrations.

## When to Use
- User asks to "test a webhook" or "debug webhook"

## Send Test Payload

$headers = @{ "Content-Type" = "application/json" }
$body = @{ event = "test" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://example.com/webhook" -Method POST -Headers $headers -Body $body

## Response Codes
- 200 OK = success
- 401 = authentication failed
- 403 = signature verification failed
- 429 = rate limited
- 5xx = server error

## Common Testing Tools
- https://webhook.site - temporary public URL
- https://requestbin.com - inspect payloads
- ngrok http 3000 - forward to localhost
