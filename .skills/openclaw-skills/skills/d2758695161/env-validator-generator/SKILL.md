# env-validator

Validate and document environment configuration files (.env, .env.example).

## Usage

```
Validate .env file and check for missing required vars
Generate .env.example from .env
Document required environment variables
Check for common security issues in .env
```

## What it does

- **Validate** — Check all required vars are present, types are correct
- **Generate .env.example** — Create a template with descriptions
- **Security check** — Detect hardcoded secrets, weak keys, missing encryption
- **Document** — Generate a table of all env vars with descriptions

## Features

- Supports `.env`, `.env.local`, `.env.production`, `.env.test`
- Detects: missing required vars, invalid formats (URLs, emails, UUIDs), weak credentials
- Warns about: debug mode in production, CORS wildcards, unencrypted secrets
- Suggests: variable names if typos detected, correct formats for known vars

## Examples

- "Validate my .env and flag any security issues"
- "Generate .env.example with all the vars from my current .env"
- "Check if all required vars for Railway deployment are set"

## Notes

- Never logs or exposes secret values — only checks format/presence
- Supports Vercel, Railway, Fly.io, Render deployment conventions
