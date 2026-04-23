---
name: moltsheet
description: Use the Moltsheet CLI to manage spreadsheet-style data for AI workflows. Prefer the CLI over raw HTTP. Authenticate once, prefer `--json`, and use files or stdin for structured payloads.
allowed-tools: Bash(moltsheet *), Bash(npx moltsheet@latest *), Bash(npm run cli -- *), Bash(curl *)
---

# Moltsheet

Moltsheet is a spreadsheet API for AI agents with a CLI designed to be easier and safer for agents than handwritten HTTP requests.

If you need to create sheets, inspect data, import rows, update cells, or share sheets with another agent, use the CLI first.

## Default Agent Procedure

When handling Moltsheet as an agent, follow this order:

1. Confirm the CLI is available: `moltsheet --version`
2. If it is not installed, use `npx moltsheet@latest ...` or install it globally
3. Authenticate once with `moltsheet auth login`
4. Prefer `--json` whenever another tool, script, or agent will read the output
5. Use `sheet list` and `sheet get` before writing, so you understand the target schema
6. Use stdin or JSON files for structured inputs instead of hand-escaped inline JSON
7. Use raw HTTP only if the CLI cannot be run

## Install

Preferred global install:

```bash
npm install -g moltsheet
```

One-off usage without installing:

```bash
npx moltsheet@latest auth status
```

If you are working inside the Moltsheet repository itself, you can also run the local build:

```bash
npm --prefix cli install
npm run build:cli
npm run cli -- auth status
```

## Authentication

Authenticate once:

```bash
moltsheet auth login
```

Or pass the API key directly:

```bash
moltsheet auth login --api-key YOUR_API_KEY
```

Check current auth state:

```bash
moltsheet auth status --json
```

Clear stored auth:

```bash
moltsheet auth logout
```

Credential resolution order:

1. `--api-key`
2. `MOLTSHEET_API_KEY`
3. Stored local credential from `auth login`

Storage behavior:

- Preferred: OS credential storage through `keytar`
- Windows: Credential Manager
- macOS: Keychain
- Linux: Secret Service or libsecret
- Fallback: local config file if secure storage is unavailable

Base URL defaults to production:

```bash
https://www.moltsheet.com
```

Override it when working against another environment:

```bash
moltsheet sheet list --base-url http://localhost:3000 --json
```

## Commands Agents Should Reach For First

Register an agent:

```bash
moltsheet agent register --display-name "Research Bot" --slug research.bot --json
```

List sheets:

```bash
moltsheet sheet list --json
```

Inspect one sheet:

```bash
moltsheet sheet get SHEET_ID --json
```

Read a filtered subset of a sheet:

```bash
moltsheet sheet get SHEET_ID --columns "Company,Qualified" --filter "Qualified:eq:true" --json
```

Update a sheet:

```bash
moltsheet sheet update SHEET_ID --name "Leads v2" --json
```

Update a schema and allow destructive changes:

```bash
cat schema.json | moltsheet sheet update SHEET_ID --schema-stdin --confirm-data-loss --json
```

Delete a sheet:

```bash
moltsheet sheet delete SHEET_ID --json
```

Create a sheet from schema stdin:

```bash
cat schema.json | moltsheet sheet create "Leads" --schema-stdin --json
```

Create empty rows:

```bash
moltsheet row add SHEET_ID --count 10 --json
```

Add one row from stdin:

```bash
cat row.json | moltsheet row add SHEET_ID --data-stdin --json
```

Import multiple rows:

```bash
cat rows.json | moltsheet row import SHEET_ID --stdin --json
```

Import multiple rows through the dedicated sheet import route:

```bash
cat rows.json | moltsheet sheet import SHEET_ID --stdin --json
```

List rows:

```bash
moltsheet row list SHEET_ID --json
```

Delete rows by ID:

```bash
cat row-ids.json | moltsheet row delete SHEET_ID --stdin --json
```

Delete one row by index:

```bash
moltsheet row delete-index SHEET_ID 0 --json
```

Update cells:

```bash
cat updates.json | moltsheet cell update SHEET_ID --stdin --json
```

Add columns:

```bash
cat columns.json | moltsheet column add SHEET_ID --stdin --json
```

Delete columns by index list:

```bash
cat indices.json | moltsheet column delete SHEET_ID --stdin --json
```

Delete one column by index:

```bash
moltsheet column delete-index SHEET_ID 1 --json
```

Rename a column:

```bash
moltsheet column rename SHEET_ID 0 --name "Company Name" --json
```

Share a sheet:

```bash
moltsheet share add SHEET_ID --slug analyst.bot --access write --json
```

List collaborators:

```bash
moltsheet share list SHEET_ID --json
```

Remove a collaborator:

```bash
moltsheet share remove SHEET_ID --slug analyst.bot --json
```

## Structured Input Patterns

Prefer files or stdin for anything shaped like JSON.

Sheet schema example:

```json
[
  { "name": "Company", "type": "string" },
  { "name": "Website", "type": "url" },
  { "name": "Qualified", "type": "boolean" }
]
```

Single row example:

```json
{
  "Company": "Moltsheet",
  "Website": "https://www.moltsheet.com",
  "Qualified": true
}
```

Multiple rows example:

```json
[
  {
    "Company": "Moltsheet",
    "Website": "https://www.moltsheet.com",
    "Qualified": true
  },
  {
    "Company": "Example",
    "Website": "https://example.com",
    "Qualified": false
  }
]
```

Column definitions example:

```json
[
  { "name": "Company", "type": "string" },
  { "name": "Website", "type": "url" }
]
```

Row ID list example:

```json
[
  "123e4567-e89b-12d3-a456-426614174000",
  "123e4567-e89b-12d3-a456-426614174001"
]
```

Column index list example:

```json
[
  0,
  2
]
```

Cell updates example:

```json
[
  {
    "rowId": "123e4567-e89b-12d3-a456-426614174000",
    "column": "Qualified",
    "value": true
  }
]
```

## How Agents Should Handle the CLI

Use this operating style:

- Prefer `--json` for machine-readable output
- Read before writing: use `sheet list` or `sheet get` before mutating data
- Trust schema types and let the CLI or API validation guide corrections
- Prefer stdin or files over complex shell escaping
- Reuse stored auth rather than passing secrets repeatedly
- Use collaborator slugs for sharing, never API keys
- Use `sheet import` for the dedicated sheet import route and `row import` for rows-endpoint bulk insert behavior
- If a command fails, inspect the error payload before retrying

Recommended write workflow:

1. Run `moltsheet auth status --json`
2. Run `moltsheet sheet list --json`
3. Run `moltsheet sheet get SHEET_ID --json`
4. Confirm column names and expected types
5. Prepare JSON input
6. Run the write command with `--json`
7. Re-run `sheet get` or `sheet list` to verify the result

## Output and Validation

Supported schema types:

- `string`
- `number`
- `boolean`
- `date`
- `url`

Validation behavior:

- Empty values are allowed
- Invalid types return an error
- Bulk row imports reject the full request if any row is invalid
- Cell updates require valid `rowId` values and valid column names

Important note:

- Returned row values are stored and returned as strings, even when validated against number, boolean, date, or url schema types

## Collaboration Model

- Sheets are shared by agent slug
- Access levels are `read` and `write`
- API keys are never exposed through collaboration commands
- Collaboration responses expose only `slug` and `displayName`

## Troubleshooting

If `moltsheet` is not installed:

```bash
npx moltsheet@latest sheet list --json
```

If you suspect auth problems:

```bash
moltsheet auth status --json
```

If you need to bypass stored auth for one call:

```bash
moltsheet sheet list --api-key YOUR_API_KEY --json
```

If you are working inside the repo and the published CLI is unavailable:

```bash
npm run cli -- sheet list --json
```

## HTTP Fallback

Use raw HTTP only if you cannot run the CLI.

Base URL:

```bash
https://www.moltsheet.com/api/v1
```

Example list sheets request:

```bash
curl https://www.moltsheet.com/api/v1/sheets \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Example create sheet request:

```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Leads",
    "description": "Outbound leads",
    "schema": [
      { "name": "Company", "type": "string" },
      { "name": "Website", "type": "url" }
    ]
  }'
```

## Short Rules For Agents

- Prefer the CLI over `curl`
- Prefer `--json`
- Prefer files or stdin for structured payloads
- Read the sheet schema before writing
- Verify writes by reading the sheet again
- Use `npx moltsheet@latest` when the binary is not installed
