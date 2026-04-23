---
name: skylv-cron-parser
slug: skylv-cron-parser
version: 1.0.0
description: "Parses, validates, and explains cron expressions. Converts between human-readable and cron format. Triggers: parse cron, validate cron, cron expression."
author: SKY-lv
license: MIT
tags: [automation, tools]
keywords: [automation, tools]
triggers: cron-parser
---

# Cron Expression Parser

## Overview
Parses, validates, and explains cron expressions.

## Cron Format
* * * * *
| | | | |
| | | | day of week
| | | month
| | day of month
| hour
minute

## Common Patterns

* * * * *   Every minute
0 * * * *   Every hour
0 0 * * *   Daily at midnight
0 9 * * 1-5 Weekdays at 9 AM
*/5 * * * * Every 5 minutes
0 0 1 * *   First day of month

## Popular Crontab
@yearly  = 0 0 1 1 *
@monthly = 0 0 1 * *
@weekly  = 0 0 * * 0
@daily   = 0 0 * * *
@hourly  = 0 * * * *

## Validation
Minute: 0-59, Hour: 0-23, Day: 1-31, Month: 1-12, Weekday: 0-6
Use - for ranges (1-5), , for lists (1,3,5), / for steps (*/5)
