# Conversational Wizard

Use this file for **wizard behavior**, not schema details.

Purpose:
- guide setup one question at a time
- reduce misconfiguration
- prefer sensible defaults
- generate local deployment files only
- leave the reusable skill package unchanged

## Wizard rules
- ask one thing at a time
- keep each question short and concrete
- prefer defaults for first rollout
- summarize before writing files
- stop and clarify if the user gives conflicting requirements
- keep live trading out of scope unless the user explicitly pushes there

## Recommended defaults
- deployment mode = daily assessment
- strategy = Trend Breakout v1
- paper account = $10,000
- max risk per trade = $100
- max position value = $2,000
- buy approval = yes
- sell approval = yes
- one job per watchlist = yes
- schedule = manual first

## What success looks like
By the end of the wizard, the user should know:
- what will be created
- where local files will live
- what still needs validation
- how to run the first daily assessment

For the exact question order, read `wizard-question-flow.md`.
For the tracked fields and output scope, read `wizard-v1.md` and `wizard-outputs.md`.
