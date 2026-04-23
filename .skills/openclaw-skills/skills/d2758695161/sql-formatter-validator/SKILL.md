# sql-formatter

Format, validate, and analyze SQL queries. Paste SQL or point to a file.

## Usage

```
Format this SQL: [paste SQL]
Validate [SQL file] and report errors
Explain this query: [paste SQL]
```

## What it does

- **Format** — Pretty-print SQL with proper indentation
- **Validate** — Check syntax errors with line/column numbers
- **Explain** — Show query execution plan (PostgreSQL/MySQL)
- **Detect type** — Identifies SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER

## Supported Dialects

- PostgreSQL
- MySQL / MariaDB
- SQLite
- SQL Server (T-SQL)

## Notes

- Auto-detects dialect from context
- Preserves query comments
- Handles nested queries and CTEs
