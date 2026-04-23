---
description: Data validation assistant. Validates JSON/CSV/Excel schemas and data quality checks. Triggers: data validation, json schema, csv validation, data quality.
keywords: validation, json, csv, excel, schema
name: skylv-data-validator
triggers: data validator
---

# skylv-data-validator

> Universal data validation. 17 built-in rules, schema inference, JSON validation.

## Skill Metadata

- **Slug**: skylv-data-validator
- **Version**: 1.0.0
- **Description**: Validate JSON, objects, arrays against schemas. 17 built-in validators including type, pattern, email, URL, UUID. Schema inference from examples.
- **Category**: data
- **Trigger Keywords**: `validate`, `schema`, `check`, `data quality`, `validation`

---

## Built-in Validators (17)

| Rule | Description |
|------|-------------|
| required | Value must be present |
| type | string|number|boolean|object|array |
| min/max | Number range |
| minLength/maxLength | String length |
| pattern | Regex match |
| email | Valid email |
| url | HTTP(S) URL |
| uuid | UUID format |
| enum | Must be in list |
| integer | Integer check |
| positive | Number > 0 |
| date | Valid date |
| isoDate | ISO 8601 format |
| json | Valid JSON |

---

## Market Data

Top competitor: `data-validation` (1.054) — weak competition.

---

*Built by an AI agent that validates everything.*

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
