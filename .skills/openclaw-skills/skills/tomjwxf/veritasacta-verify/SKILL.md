---
name: veritasacta-verify
description: >
  Offline receipt verifier. Verifies Ed25519-signed decision receipts,
  agent manifests, and audit bundles without contacting any server.
  MIT licensed. Works with protect-mcp receipts and any Veritas Acta artifact.
metadata:
  emoji: ✅
  requires:
    bins:
      - npx
    env: []
  install: |
    npm install -g @veritasacta/verify@latest
  license: MIT
  allowed-tools:
    - Bash
    - Read
---

# Veritas Acta Verify — Offline Receipt Verification

## What This Skill Does

Verifies Ed25519-signed receipts and artifacts without contacting any server.
The verifier doesn't know ScopeBlind exists — it's pure cryptographic math.

## Quick Start

```bash
# Self-test: verify a built-in sample receipt
npx @veritasacta/verify --self-test

# Verify a specific receipt file
npx @veritasacta/verify receipt.json --key issuer-public.json

# Verify an audit bundle
npx @veritasacta/verify bundle.json
```

## Links

- npm: https://npmjs.com/package/@veritasacta/verify
- IETF Draft: https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/
