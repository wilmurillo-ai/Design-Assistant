---
name: clawcaptcha
description: CAPTCHA solving service for AI agents — solve reCAPTCHA, hCaptcha, Cloudflare Turnstile, FunCaptcha, and image CAPTCHAs automatically.
metadata: {"openclaw":{"requires":{"env":["CLAWCAPTCHA_API_KEY"]},"primaryEnv":"CLAWCAPTCHA_API_KEY","homepage":"https://clawise.dev"}}
---

# ClawCaptcha

CAPTCHA solving service for AI agents.

ClawCaptcha lets your agent bypass human verification challenges automatically, so it can access websites and services without getting blocked.

- **reCAPTCHA v2/v3** — Token-based solving with site key
- **hCaptcha** — Full support including enterprise
- **Cloudflare Turnstile** — Bypass Turnstile challenges
- **FunCaptcha** — Arkose Labs challenge solving
- **Image CAPTCHA** — OCR-based image recognition
- **GeeTest** — Slide and click verification

## Getting Started

1. Get your API key at [clawise.dev](https://clawise.dev)
2. Set `CLAWCAPTCHA_API_KEY` in your environment

Documentation: [docs.clawise.dev](https://docs.clawise.dev)
