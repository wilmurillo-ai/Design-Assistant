---
name: csv-deduper
description: Remove duplicate rows from CSV files by key columns. Use when asked to deduplicate CSVs or keep unique records.
---
# Overview
Deduplicate CSV rows using one or more key columns. Keeps the first row by default.

# Inputs
- A CSV file.
- Optional key columns (comma separated).

# Outputs
- A new CSV file with duplicates removed.

# Workflow
1. Choose the key columns (or use the whole row).
2. Run the script to produce a deduped CSV.
3. Validate row counts.

# Usage
```bash
python scripts/csv_dedupe.py --input data.csv --output data.deduped.csv --keys id,email
python scripts/csv_dedupe.py --input data.csv --output data.deduped.csv
```

# Safety
- No network access.
- Only reads/writes the file paths you pass in.
