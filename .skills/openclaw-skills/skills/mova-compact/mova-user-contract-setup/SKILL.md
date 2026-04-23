---
name: mova-user-contract-setup
description: Walk the user through registering their own MOVA contract — from source_url to first successful run. Trigger when the user says "register my contract", "add my contract to MOVA", "I have a contract at a URL", "set up my contract", or wants to run their own contract through MOVA.
license: MIT-0
---

> **Ecosystem Skill** — Supports building and managing the MOVA ecosystem. Requires the `openclaw-mova` plugin.

# MOVA User Contract Setup

Walk the user through registering a MOVA-spec contract hosted at their own URL, setting visibility, and running it for the first time — all via MOVA plugin tools.

## What this skill does

1. Collects the contract's `source_url` and a lightweight manifest (title, version, mode)
2. Registers the contract at MOVA — MOVA stores only the manifest, the contract body stays at the user's URL
3. Optionally sets visibility (`private` → `public`)
4. Runs the contract with test inputs and shows the result

---

## When to trigger

Activate when the user:
- Says "register my contract", "add my contract", "I have a contract at a URL"
- Wants to run a custom contract through MOVA
- Asks about user-owned contracts or the contract registry

**Before starting**, say:

> "Let's register your contract with MOVA. I'll need a few details — your contract JSON stays at your URL, MOVA only stores a pointer. Ready?"

Wait for confirmation.

---

## Step 1 — Collect source_url

Ask:

> "What is the HTTPS URL to your contract JSON file?"

Requirements:
- Must start with `https://`
- Must be a direct link to a JSON file (not a GitHub HTML page)

If the user gives a GitHub repo page URL, help them convert it to a raw URL:
- `github.com/user/repo/blob/main/contract.json` → `raw.githubusercontent.com/user/repo/main/contract.json`

---

## Step 2 — Collect manifest fields

Ask these one at a time:

1. **Title** — "What is the title of this contract? (e.g. Invoice Approval Agent)"
2. **Version** — "What version is it? (e.g. 1.0.0)"
3. **Execution mode** — "What is the execution mode?"
   - Show options: `deterministic` / `bounded_variance` / `ai_assisted` / `human_gated`
   - If unsure: recommend `ai_assisted` for most custom contracts
4. **Description** *(optional)* — "Brief description of what this contract does? (press Enter to skip)"
5. **Visibility** — "Should this contract be `private` (only your org) or `public` (discoverable by all MOVA users)?"

---

## Step 3 — Register

Call tool `mova_register_contract` with:
- `source_url`: from Step 1
- `title`, `version`, `execution_mode`, `description`: from Step 2
- `visibility`: from Step 2

On success, show:

> "✓ Contract registered.
> ID: [contract_id]
> Visibility: [visibility]
>
> Your contract body stays at [source_url] — MOVA fetches it on each run."

If error `409 Conflict` — a contract with this source_url is already registered. Show the existing `contract_id` and ask if they want to update visibility or run it instead.

If error `422` on source_url — the URL must use HTTPS with a valid hostname. Ask for a corrected URL.

---

## Step 4 — Optional: change visibility

If the user wants to change visibility after registration:

Call tool `mova_set_contract_visibility` with:
- `contract_id`: from Step 3
- `visibility`: `private` or `public`

---

## Step 5 — Test run

Ask:

> "Want to run a test now? I'll execute the contract and show you the result. Do you have input data, or should we try with empty inputs?"

If yes — collect inputs as key-value pairs (ask one at a time if needed).

Call tool `mova_run_contract` with:
- `contract_id`: from Step 3
- `inputs`: collected or `{}`

**If `status: "waiting_human"`** — the contract has a human gate. Show the analysis and options, then ask the user to choose. Call `mova_hitl_decide` with the `contract_id`, chosen `option`, and `reason`.

**If `status: "completed"`** — show the verdict and output.

**If `status: "failed"`** — show the error. Common causes:
- Contract JSON doesn't match MOVA spec — the user needs to fix the contract at source_url
- Required connector not registered — suggest `mova_list_connectors` to find the connector and `mova_register_connector` to set up their endpoint

---

## Step 6 — Check run status (if needed)

If the run is still in progress, call `mova_run_status` with the `run_id` to get the latest status.

---

## After setup — show summary

```
CONTRACT REGISTERED
───────────────────────────────────
ID:           [contract_id]
Title:        [title]
Version:      [version]
Mode:         [execution_mode]
Visibility:   [private/public]
Source URL:   [source_url]

NEXT STEPS
- Run it:        mova_run_contract({ contract_id: "[id]", inputs: {...} })
- Check a run:   mova_run_status({ run_id: "..." })
- List yours:    mova_list_my_contracts()
- Change access: mova_set_contract_visibility({ contract_id: "[id]", visibility: "public" })
- Remove it:     mova_delete_contract({ contract_id: "[id]" })
```

---

## Rules

- NEVER make HTTP requests manually to fetch or validate the contract — use MOVA tools only
- NEVER invent contract_id or run_id — they come from tool responses
- NEVER skip asking for source_url — it is always required
- If the user doesn't know the execution mode, recommend `ai_assisted` and explain the options
- If registration fails, show the exact error — do not guess or retry silently
- After a successful run, always show the full output including verdict and any audit receipt
