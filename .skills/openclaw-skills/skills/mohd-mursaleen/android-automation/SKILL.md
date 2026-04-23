---
name: iota-sidequest
description: Run autonomous Android automations over ADB. Use this for any task inside an Android app — ordering food, booking tickets, shopping, rides, or anything else. OpenClaw gathers details from the user, fires the automation, and reports back.
metadata:
  {
    "openclaw":
      {
        "emoji": "🌀",
        "requires": { "bins": ["adb"], "anyBins": ["python3", "python"] },
        "primaryEnv": "GEMINI_API_KEY",
        "optionalEnv": ["OPENAI_API_KEY"],
      },
  }
---

# Iota Sidequest

Use this skill when the user wants to do something inside an Android app through ADB.

## Setup

Before the first run: `{baseDir}/scripts/setup_runtime.sh`. Ensure a device is visible in `adb devices`.

**API key** — set one of:

| Provider | Env var | Default model |
|---|---|---|
| Gemini (default) | `GEMINI_API_KEY` | `gemini-3.1-pro-preview` |
| OpenAI | `OPENAI_API_KEY` | `gpt-5.2` |

If only `OPENAI_API_KEY` is set, the runtime auto-switches to OpenAI. To force a provider when both keys exist, set `PHONE_AGENT_PROVIDER=openai` (or `gemini`).

## How It Works

1. **Gather details** from the user. Read `{baseDir}/references/planning.md` for what to ask per domain.
2. **Run the automation** in background with exit notification enabled:
   ```bash
   "{baseDir}/scripts/run_phase.sh" "<task description>"
   ```
3. **Wait** for the process to exit. Do not poll or babysit.
4. **Read the result** JSON printed to stdout.
5. **Act on the result** (see table below).

The runtime is autonomous — it opens the app, navigates, taps, types, and scrolls on its own. It stops when the task is done, when it needs a user decision, or when it gets stuck.

## Writing the Task Description

One natural-language string. Include: what app, what to do, what you know, what NOT to do yet.

First run example:
> Open Swiggy Instamart. Search for SuperYou chocolate protein bar. Add 1 to cart. Go to checkout. Default address. Do not select payment or confirm order.

Continuation after user input:
> Continue in Swiggy from checkout screen. SuperYou Protein Bar x1 in cart at ₹99. Select Google Pay. User authorized payment. Complete the order.

## Reading the Result

Key fields in the result JSON:

| Field | Meaning |
|---|---|
| `status` | `done`, `needs_input`, `stuck`, `max_steps`, `timeout`, or `failed` |
| `why` | Human-readable reason the automation stopped |
| `what_i_did` | Narrative of what the automation accomplished |
| `where_i_am` | Description of the current screen |
| `steps` | Step-by-step log of actions and observations |
| `screenshot_path` | Path to the final screenshot |

## What To Do After Each Result

| Status | Action |
|---|---|
| `done` | Tell the user the result. Task complete. |
| `needs_input` | Show user: `where_i_am` + attach the screenshot image + ask the question from `why`. |
| `stuck` | Show user: `what_i_did` + `where_i_am` + attach the screenshot image. Ask what to do. |
| `max_steps` | Show user where it got to + attach screenshot. Ask if it should continue. |
| `timeout` | Same as `max_steps`. |
| `failed` | Tell user what went wrong. Ask before retrying. |

When asking the user for input, **always attach the screenshot image** from `screenshot_path` so the user can see the current screen.

Continue automatically only when you have all needed information. Never wait for user to say "continue" or "now" between runs — if you have enough context, just fire the next run.

## Safety

Never guess through: payment method, OTP, final purchase confirmation, account switching, cancellation, or refund. If the user already authorized a sensitive action, include that authorization in the task description.

## Reference

Read `{baseDir}/references/planning.md` before complex tasks for domain-specific checklists on what details to gather.
