---
name: garden-irrigation
description: Prototype smart irrigation skill scaffold for greenhouse and outdoor zones using Tuya sensors and weather data.
license: MIT
---

# garden-irrigation

This skill scaffold:
- reads soil sensors from the existing `skills/tuya-cloud`
- fetches weather history and forecast
- creates per-zone irrigation plans
- stores logs and reports under `/data/workspace-garden_manager/garden-irrigation/data`

Current status:
- planning and logging implemented
- live valve actuation not enabled yet
