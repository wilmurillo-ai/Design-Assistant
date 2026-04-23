---
name: jtexpress
description: Use J&T Express (极兔速递) for shipment tracking, shipping guidance, service-type comparison, outlet lookup, and delivery-time or fee estimation. Use when the user asks about J&T Express, Jitu, tracking J&T shipments, J&T delivery time, J&T shipping fees, J&T outlets, or wants practical help understanding or managing a J&T Express shipment. This skill may persist local user data for history and subscriptions when its runtime code is used.
---

# J&T Express (极兔速递)

## Overview

Use this skill to help users with common J&T Express tasks such as tracking shipments, understanding service levels, estimating timing or fees, and preparing to send a parcel.

## Local Persistence

When the local CLI/runtime code is used, this skill may create and persist local data under:

- `~/.openclaw/data/jtexpress/jtexpress.db`
  - stores query history
  - stores shipment-subscription records
  - may store saved address records if those commands are implemented/used
- `~/.openclaw/data/jtexpress/secure/`
  - stores encrypted local files used by the privacy/storage helper
- `~/.openclaw/data/jtexpress/secure/.key`
  - stores a local encryption key file with mode `600`
- `~/.openclaw/data/jtexpress/privacy_export.json`
  - may be created when the user runs privacy export

Only use persistence when it is necessary for the user's requested workflow. If the user asks about privacy, disclose these paths clearly.

## Privacy Controls

The local CLI supports privacy operations:

- `privacy info` — show local storage paths and stored-file info
- `privacy clear` — clear local SQLite history/subscription data and encrypted local files
- `privacy export` — export local storage metadata to `privacy_export.json`

## Workflow

1. Determine the user's goal:
   - track an existing shipment
   - estimate fee or delivery time
   - compare service types
   - find a nearby outlet or pickup point
   - prepare shipment details
   - review or clear local history/subscriptions/privacy data
2. Ask for only the missing essentials, such as tracking number, route, package size, or urgency.
3. Give the most practical answer first.
4. If exact fee or timing cannot be confirmed, provide a cautious estimate and state assumptions.
5. If the task uses local runtime features that persist data, mention that local history/subscription/privacy files may be created under `~/.openclaw/data/jtexpress/`.
6. Do not claim to complete real shipping actions unless live tools are available and confirmed.
