# Invoice Verification Service

ClawHub skill for the `invoice-api-service` v4 plugin APIs.

## What This Skill Does

- Initialize or rotate an `appKey` with `POST /api/v4/plugin/key/init`
- Query remaining quota with `GET /api/v4/plugin/quota`
- Query quota ledger with `GET /api/v4/plugin/ledger`
- Verify invoice text or image payload with `POST /api/v4/plugin/verify`

## Runtime Requirements

- Node.js 18 or newer
- Reachable backend base URL, for example `http://192.168.154.76:18888`

## Bundled Files

- `SKILL.md`: trigger instructions and execution workflow
- `agents/openai.yaml`: ClawHub/OpenClaw UI metadata
- `scripts/invoice_service.js`: executable helper script

## Local Usage

```bash
node "{baseDir}/scripts/invoice_service.js" config set --api-base-url http://192.168.154.76:18888
node "{baseDir}/scripts/invoice_service.js" init-key
node "{baseDir}/scripts/invoice_service.js" quota
node "{baseDir}/scripts/invoice_service.js" ledger --page 1 --page-size 20
node "{baseDir}/scripts/invoice_service.js" verify --text "发票号码25367000000079597464，开票日期2025-05-30，金额260.65" --format json
```

Install the skill first, then run `init-key` once before the first real use.
`init-key` calls the backend to create and persist the `appKey`, and the backend grants the free 5-trial quota at the same time.

## Publish To ClawHub

The current `clawhub` CLI publishes a skill folder directly. `SKILL.md` is mandatory; `README.md` is recommended.

```bash
clawhub login
clawhub publish . --slug invoice-verification-service --name "Invoice Verification Service" --version 0.2.0 --changelog "Align skill with invoice-api-service v4 plugin APIs."
```

## Install From ClawHub

After the skill is published publicly:

```bash
clawhub install invoice-verification-service
node "{installDir}/scripts/invoice_service.js" init-key
```

If a specific version is needed:

```bash
clawhub install invoice-verification-service --version 0.2.0
```

## Notes

- The script stores config in `~/.openclaw/invoice-skill/config.json`.
- The script also reads the legacy plugin config from `~/.openclaw/invoice-plugin/config.json` if present.
- Recharge, renew, and order APIs were removed from this skill because the current `invoice-api-service` controller only exposes the v4 plugin endpoints.
