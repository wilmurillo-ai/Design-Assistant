---
name: maybeai-sheet
description: "MaybeAI Sheet skill for full Excel/spreadsheet lifecycle management. Upload, read, edit, and analyze Excel files via the MaybeAI platform. Use when the user wants to: upload or import an Excel file, read spreadsheet data, inspect worksheet headers, update cell ranges, insert/delete rows or columns, manage worksheets, add charts or images, apply filters or conditional formatting, calculate formulas, generate SQL-assisted pivot/result tables, export files, manage versions, or perform any Excel data operation."
version: 0.1.4
metadata:
  openclaw:
    requires:
      env:
        - MAYBEAI_API_TOKEN
    primaryEnv: MAYBEAI_API_TOKEN
    emoji: "📊"
    homepage: https://github.com/OmniMCP-AI/maybeai-uni
---

# MaybeAI Sheet Skill

Full Excel/spreadsheet lifecycle management powered by the [MaybeAI](https://maybe.ai) platform. Upload files, read and write data, manage worksheets, add charts, apply formatting, and build SQL-assisted pivot/result tables via natural language.

## Scripts

Ready-to-run curl examples are in the [`scripts/`](./scripts/) folder. Each script reads credentials from environment variables — no hardcoded tokens.

```bash
export MAYBEAI_API_TOKEN=your_token_here
export DOC_ID=your_document_id_here          # needed by most scripts

bash scripts/01-file-management.sh   # upload, import, list, rename, delete, export
bash scripts/02-read-data.sh         # read sheet, list worksheets, versions
bash scripts/03-write-data.sh        # update range, append rows, copy range
bash scripts/04-rows-columns.sh      # insert/delete/move rows & columns, widths/heights
bash scripts/05-worksheets.sh        # create, rename, move, duplicate, delete worksheets
bash scripts/06-formulas.sh          # calc single/batch formulas, recalculate all
bash scripts/07-charts-pictures.sh   # add/edit/delete charts and pictures
bash scripts/08-formatting.sh        # freeze panes, auto filter, conditional formats
bash scripts/09-end-to-end.sh        # 3 complete workflow examples (upload→edit→export)
```

> **Requires**: `curl` and `jq`. Install jq with `brew install jq` (macOS) or `apt install jq` (Linux).

---

## Setup

### Get your API token

1. Go to **[https://maybe.ai/user/my-plan](https://maybe.ai/user/my-plan)** in your browser.
   *(Or click your avatar / name at the bottom-left of the app → **My Plan**.)*
2. Find the **API Token** card below the plan summary — it shows a masked Bearer token with copy and reveal buttons.
3. Copy the token and set it as an environment variable:

```bash
export MAYBEAI_API_TOKEN=your_token_here
```

### Required environment variable

| Variable | Description |
|---|---|
| `MAYBEAI_API_TOKEN` | Your MaybeAI Bearer token. Get it from [maybe.ai/user/my-plan](https://maybe.ai/user/my-plan). |

### Base URL

```
https://play-be.omnimcp.ai
```

All authenticated endpoints require the header:

```
Authorization: Bearer <MAYBEAI_API_TOKEN>
```

---

## Quick Reference

| User says | Action |
|---|---|
| "Upload this Excel file" | `POST /api/v1/excel/upload` |
| "Import from URL" | `POST /api/v1/excel/import_by_url` |
| "Read Sheet1 data" | `POST /api/v1/excel/read_sheet` |
| "List my files" | `POST /api/v1/excel/list_files` |
| "List worksheets" | `POST /api/v1/excel/list_worksheets` |
| "Update cells A1:B3" | `POST /api/v1/excel/update_range` |
| "Replace all data rows but keep headers" | `POST /api/v1/excel/update_data_keep_headers` |
| "Upsert rows by key, append new ones" | `POST /api/v1/excel/update_range_by_lookup` |
| "Append new rows" | `POST /api/v1/excel/append_rows` |
| "Insert 2 rows at row 5" | `POST /api/v1/excel/insert_rows` |
| "Delete rows 3–5" | `POST /api/v1/excel/delete_rows` |
| "Add a new worksheet" | `POST /api/v1/excel/write_new_worksheet` |
| "Add a bar chart" | `POST /api/v1/excel/add_chart` |
| "Freeze the header row" | `POST /api/v1/excel/freeze_panes` |
| "Format one or more ranges" | `POST /api/v1/excel/batch_set_cell_style` |
| "Add auto filter" | `POST /api/v1/excel/set_auto_filter` |
| "Calculate formula =SUM(A1:A10)" | `POST /api/v1/excel/calc_formulas` |
| "Build a pivot/result sheet from worksheet data" | `POST /api/v1/excel/sql/compile` then `POST /api/v1/excel/sql/write_result` |
| "Export/download the file" | `GET /api/v1/excel/export/{document_id}` |
| "Copy this spreadsheet" | `POST /api/v1/excel/copy_excel` |

---

## API Reference

### File Management

#### Upload Excel File
```
POST /api/v1/excel/upload
Content-Type: multipart/form-data

file: <xlsx file>
user_id: (optional)
```
Returns `{ document_id, uri, ... }`. Use `document_id` (also called `uri`) in all subsequent calls.

#### Import File by URL
```
POST /api/v1/excel/import_by_url
Authorization: Bearer <token>

{ "url": "https://..." }
```
Downloads the file from the URL into MaybeAI storage. Returns `document_id`.

#### List Files
```
POST /api/v1/excel/list_files
Authorization: Bearer <token>

{}
```

#### Search Files
```
POST /api/v1/excel/search_files
Authorization: Bearer <token>

{ "keyword": "sales" }
```

#### Rename File
```
POST /api/v1/excel/rename_file
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "new_filename": "new_name.xlsx" }
```

#### Delete File
```
POST /api/v1/excel/delete_file
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>" }
```

#### Export (Download) File
```
GET /api/v1/excel/export/{document_id}
```
Returns the raw `.xlsx` file.

#### Download File (from GridFS)
```
POST /api/v1/excel/download

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>" }
```

#### Copy Excel Document
```
POST /api/v1/excel/copy_excel
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>" }
```

---

### Reading Data

#### Get Spreadsheet Data (MOST USEFUL & FREQUENTLY USE) (JSON)
```
GET /api/v1/excel/spreadsheets/{doc_id}?gid=<sheet_index>
```
Returns spreadsheet data as JSON. `gid` selects the worksheet (0-indexed).

#### View Spreadsheet (HTML)
```
GET /api/v1/excel/spreadsheets/d/{doc_id}
```
Returns an HTML preview of the spreadsheet.

#### List Worksheets
```
POST /api/v1/excel/list_worksheets

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>" }
```

#### Read Sheet
```
POST /api/v1/excel/read_sheet

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1" }
```
Returns all cell data from the specified worksheet.

#### Read Headers
```
POST /api/v1/excel/read_headers

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=0" }
```
Use this first for fast schema inspection before writing SQL for pivot/result output.

#### Worksheet Targeting Rule

- Do not rely on `"sheet"` for `excelize-mcp`-backed read/write calls.
- Use `"worksheet_name"` when the endpoint supports it, such as `read_sheet`, `update_range`, `clear_range`, and `update_data_keep_headers`.
- Use `?gid=<sheet_index>` inside `uri` when the endpoint does not expose `worksheet_name`, such as `read_headers`, `append_rows`, and `update_range_by_lookup`.
- If neither `worksheet_name` nor `?gid=` is provided, the backend resolves to the first worksheet, which is effectively `gid=0`.

#### List Versions
```
POST /api/v1/excel/list_versions

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>" }
```

#### Read Version
```
POST /api/v1/excel/read_version

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "version": 1 }
```

---

### Writing & Editing Data

#### Update Range
```
POST /api/v1/excel/update_range
Authorization: Bearer <token>

{

  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Sheet1",
  "range_address": "A1:B3",
  "values": [["Name", "Score"], ["Alice", 95], ["Bob", 87]]
}
```

Use `uri: "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2"` instead of `worksheet_name` if you want to target a sheet by gid.

#### Update Data Keep Headers
Use this when the sheet already has the correct header row and you want to replace the data rows underneath it without rebuilding column order manually.

```
POST /api/v1/excel/update_data_keep_headers
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Sheet1",
  "data": [
    {"Name": "Alice", "Score": 95, "Rate": "12%"},
    {"Name": "Bob", "Score": 87, "Rate": "18%"}
  ],
  "preserve_formulas": true,
  "start_row": 2
}
```

What it does:
- Keeps the existing header row unchanged and preserves its column order.
- Rewrites data rows using header names, so agents can send list-of-dict data instead of manually ordered row arrays.
- Can preserve formula columns that are not present in `data` and auto-fill those formulas down.
- Is often easier than `update_range` when the goal is "replace the table contents but keep the sheet structure".

#### Update Range by Lookup
Use this for key-based updates or upserts. It is more agent-friendly than low-level `update_range` when rows should be matched by business keys such as `id`, `sku`, or composite keys.

```
POST /api/v1/excel/update_range_by_lookup
Authorization: Bearer <token>

{

  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=0",
  "data": [
    { "ID": "001", "Status": "Done" }
  ],
  "on": ["ID"],
  "override": false,
  "skip_recalculation": false
}
```

What it does:
- Matches existing rows by the `on` key column(s), then updates only the matching rows.
- Automatically appends unmatched rows as new rows, so one call can do update + append.
- Preserves existing headers and appends new columns to the right if the incoming data contains unseen fields.
- Does not overwrite existing formula cells.
- With `override: false`, empty values in the incoming data do not blank out existing cells.

#### Clear Range
```
POST /api/v1/excel/clear_range
Authorization: Bearer <token>


{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "range_address": "A1:D10" }
```

#### Append Rows
```
POST /api/v1/excel/append_rows
Authorization: Bearer <token>

{

  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=0",
  "data": [
    {"Name": "Alice", "Score": 95},
    {"Name": "Bob", "Score": 87}
  ]
}
```

`append_rows` selects the target worksheet from `uri`. If you omit `?gid=`, it appends to the first worksheet.

#### Choosing the right write API

- Use `append_rows` when you have object rows keyed by existing headers and want a simple blind append.
- Use `update_data_keep_headers` when you have list-of-dict data and want to replace all table rows while keeping row 1, column order, styles, and optional formula columns.
- Use `update_range_by_lookup` when you need upsert behavior: update rows that match a key and append rows that do not exist yet.
- Use `update_range` when you truly need exact A1 targeting such as `B7:D12`, header rewrites, or non-tabular cell edits.
- Use `batch_set_cell_style` for visual formatting on one or more ranges. Even a single range must be sent as `range_addresses: ["B2:B100"]`.
- For non-first worksheets, always set `worksheet_name` or `uri?gid=N` explicitly. Otherwise writes can land on the first sheet.

#### Agent-friendly patterns

- Easier append than `append_rows`:
  If the agent has object-shaped rows like `{"sku":"A1","qty":2,"price":10}` and does not want to manually map them into the sheet's column order, prefer `update_range_by_lookup` for upsert-or-append or `update_data_keep_headers` for full-table replacement.
- Easier update than `update_range`:
  If the user says "update rows by order ID" or "sync these records into the sheet", prefer `update_range_by_lookup` so the agent does not need to read row numbers and construct A1 ranges first.
- Keep formulas intact:
  If the sheet has computed columns like `Total` or `Margin`, prefer `update_data_keep_headers` with `preserve_formulas: true` or `update_range_by_lookup`, which avoids overwriting existing formula cells.
- Simpler styling for agents:
  Prefer `batch_set_cell_style` over low-level Excel style objects or style IDs. It fits common LLM-safe actions like date formatting, currency formatting, header emphasis, alignment, and wrap text.

#### Write New Sheet (creates a new workbook)
```
POST /api/v1/excel/write_new_sheet
Authorization: Bearer <token>

{
  "sheet_name": "Summary",
  "data": [
    {"Col1": 1, "Col2": 2},
    {"Col1": 3, "Col2": 4}
  ]
}
```

#### Copy Range with Formulas
```
POST /api/v1/excel/copy_range_with_formulas
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Sheet1",
  "from_range": "A1:D10",
  "to_range": "F1",
  "auto_fill": false
}
```

#### Copy Range by Lookup
```
POST /api/v1/excel/copy_range_by_lookup
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=0", "from_range": "A2:D2", "lookup_column": "ID", "on": ["ID"], "skip_if_exists": true }
```

---

### Row & Column Operations

#### Insert Rows
```
POST /api/v1/excel/insert_rows
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "start_row": 3, "row_count": 2 }
```
Inserts `row_count` blank rows starting at `start_row` (1-indexed).

#### Delete Rows
```
POST /api/v1/excel/delete_rows
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "start_row": 3, "row_count": 2 }
```

#### Move Row
```
POST /api/v1/excel/move_row
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "from_row": 5, "to_row": 2 }
```

#### Move Rows (batch)
```
POST /api/v1/excel/move_rows
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "from_row": 5, "count": 2, "to_row": 2 }
```

#### Undo Delete Rows
```
POST /api/v1/excel/undo_delete_rows
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "version_before": 12, "start_row": 3, "row_count": 2 }
```

#### Insert Columns
```
POST /api/v1/excel/insert_columns
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "start_column": 3, "column_count": 1 }
```

#### Delete Columns
```
POST /api/v1/excel/delete_columns
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "start_column": 3, "column_count": 1 }
```

#### Move Column
```
POST /api/v1/excel/move_column
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "from_column": "E", "to_column": "B" }
```

#### Move Columns (batch)
```
POST /api/v1/excel/move_columns
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "from_column": "E", "count": 2, "to_column": "B" }
```

#### Undo Delete Columns
```
POST /api/v1/excel/undo_delete_columns
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "version_before": 12, "start_column": 3, "column_count": 1 }
```

#### Add Header Columns
```
POST /api/v1/excel/add_header_columns
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=0", "headers": ["NewCol1", "NewCol2"], "position": "end" }
```

#### Set Columns Width
```
POST /api/v1/excel/set_columns_width
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "start_column": "A", "end_column": "A", "width": 20 }
```

#### Set Rows Height
```
POST /api/v1/excel/set_rows_height
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "start_row": 1, "end_row": 1, "height": 30 }
```

---

### Worksheet Management

#### Write New Worksheet
```
POST /api/v1/excel/write_new_worksheet
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "NewSheet", "values": [["A", "B"], ["1", "2"]] }
```

#### Delete Worksheet
```
POST /api/v1/excel/delete_worksheet
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2" }
```

#### Rename Worksheet
```
POST /api/v1/excel/rename_worksheet
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "old_name": "Sheet1", "new_name": "Sales" }
```

#### Move Worksheet
```
POST /api/v1/excel/move_worksheet
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Summary", "new_index": 0 }
```

#### Duplicate Worksheet
```
POST /api/v1/excel/copy_worksheet
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "new_worksheet_name": "Sheet1_copy" }
```

#### List Worksheets (with versions)
```
POST /api/v1/excel/list_worksheets_version

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>" }
```

---

### Formulas

#### Calculate Single Formula
```
POST /api/v1/excel/calc-formula
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=0", "cellAddress": "A11", "formula": "=SUM(A1:A10)" }
```

#### Calculate Multiple Formulas
```
POST /api/v1/excel/calc_formulas
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=0",
  "formulas": [
    { "cell": "B11", "formula": "=SUM(B1:B10)" },
    { "cell": "C11", "formula": "=AVERAGE(C1:C10)" }
  ]
}
```

#### Compile SQL for Pivot/Result Output
```
POST /api/v1/excel/sql/compile
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2",
  "sql": "select \"Region\", sum(\"Revenue\") as \"Revenue\" from gid_2 group by \"Region\" order by \"Revenue\" desc"
}
```
Validate SQL against backend SQLite + worksheet/gid rules before writing any output.

#### Write SQL Result to Worksheet
```
POST /api/v1/excel/sql/write_result
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2",
  "sql": "select \"Region\", sum(\"Revenue\") as \"Revenue\" from gid_2 group by \"Region\" order by \"Revenue\" desc",
  "target_worksheet_name": "Pivot_RegionRevenue",
  "target_start_cell": "A1",
  "create_sheet_if_missing": true,
  "clear_target_range": true,
  "include_headers": true
}
```
Execute SQL and write the pivot/result matrix into a worksheet.

#### SQL Pivot Workflow

Use this for SQL-assisted pivot/result-table generation from worksheet data. Do not describe it as a general SQL engine on sheets. The recommended path is raw SQL authoring, compile-only validation, then dedicated result writing.

Default sequence:

1. Inspect source worksheet names with `POST /api/v1/excel/list_worksheets`.
2. Inspect headers with `POST /api/v1/excel/read_headers`, or inspect a small sample with `POST /api/v1/excel/read_sheet` and a narrow `range_address`.
3. Draft SQL using either the worksheet name or a `gid_*` table reference.
4. Validate SQL with `POST /api/v1/excel/sql/compile`.
5. If compile succeeds, write the result block with `POST /api/v1/excel/sql/write_result`.
6. Optionally verify the written output with `POST /api/v1/excel/read_sheet`.

Table naming rules:

- SQL can reference a worksheet name directly.
- SQL can reference `gid_*` such as `gid_2`.
- `gid_*` uses the backend worksheet gid mapping returned by worksheet inspection.
- Quote worksheet names when they contain spaces, for example `from "Sales Data"`.
- Compile first to catch unsupported syntax or unsupported SQL features.

Examples:

```sql
select "Region", sum("Revenue") as "Revenue"
from gid_2
group by "Region"
order by "Revenue" desc
```

```sql
select "SKU", sum("Qty") as "Qty"
from "Sales Data"
group by "SKU"
order by "Qty" desc
```

Important limitations:

- Not every SQL feature is supported.
- Backend behavior follows the current SQL formula compatibility rules and SQLite-based worksheet resolution.
- `POST /api/v1/excel/calc_formulas` remains useful for preview/debug of formula-driven work, but it is not the main recommended path for pivot/result output.
- If compile fails, fix the SQL before calling `sql/write_result`.

Example: Revenue by Region

Inspect headers first:

```http
POST /api/v1/excel/read_headers
```

```json
{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2"
}
```

If headers are not enough, read a small sample:

```http
POST /api/v1/excel/read_sheet
```

```json
{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2",
  "range_address": "A1:F10"
}
```

Draft SQL:

```sql
select "Region", sum("Revenue") as "Revenue"
from gid_2
group by "Region"
order by "Revenue" desc
```

Compile before write:

```http
POST /api/v1/excel/sql/compile
```

```json
{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2",
  "sql": "select \"Region\", sum(\"Revenue\") as \"Revenue\" from gid_2 group by \"Region\" order by \"Revenue\" desc"
}
```

Write the result:

```http
POST /api/v1/excel/sql/write_result
```

```json
{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2",
  "sql": "select \"Region\", sum(\"Revenue\") as \"Revenue\" from gid_2 group by \"Region\" order by \"Revenue\" desc",
  "target_worksheet_name": "Pivot_RegionRevenue",
  "target_start_cell": "A1",
  "create_sheet_if_missing": true,
  "clear_target_range": true,
  "include_headers": true
}
```

Verify the final output:

```http
POST /api/v1/excel/read_sheet
```

```json
{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Pivot_RegionRevenue",
  "range_address": "A1:B20"
}
```

#### Recalculate All Formulas
```
POST /api/v1/excel/recalculate_formulas
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>" }
```

---

### Charts

#### Add Chart
```
POST /api/v1/excel/add_chart
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Sheet1",
  "cell": "E2",
  "chart": {
    "type": "bar",
    "series": [{ "name": "Sales", "categories": "Sheet1!A2:A10", "values": "Sheet1!B2:B10" }],
    "title": { "name": "Monthly Sales" }
  }
}
```
Supported chart types: `line`, `bar`, `col`, `pie`, `scatter`, `area`, `doughnut`, `radar`.

#### Edit Chart
```
POST /api/v1/excel/set_chart
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "cell": "E2", "chart": { ... } }
```

#### Delete Chart
```
POST /api/v1/excel/delete_chart
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "cell": "E2" }
```

---

### Pictures

#### Add Picture
```
POST /api/v1/excel/add_picture
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "cell": "D2", "picture": { "file_base64": "<base64_png>", "extension": "png" } }
```

#### Read Picture
```
POST /api/v1/excel/read_picture

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "cell": "D2" }
```

#### Delete Picture
```
POST /api/v1/excel/delete_picture
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "cell": "D2" }
```

---

### Formatting

#### Freeze Panes
```
POST /api/v1/excel/freeze_panes
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Sheet1",
  "freeze_rows": 1,
  "freeze_columns": 0
}
```
Set `freeze_rows: 1` to lock the header row while scrolling.

#### Batch Set Cell Style
Use this for both single-range and multi-range styling. There is no separate `set_cell_style` API. For a single range, pass a one-item `range_addresses` array.

Simplest single-range request:

```
POST /api/v1/excel/batch_set_cell_style
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Sheet1",
  "range_addresses": ["B2:B100"],
  "style": {
    "format": "date"
  }
}
```

Typical multi-range request:

```
POST /api/v1/excel/batch_set_cell_style
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Sheet1",
  "range_addresses": ["B2:B100", "E2:E100", "A1:F1"],
  "style": {
    "bold": true,
    "horizontal": "center",
    "wrap_text": true,
    "bg_color": "#D9EAD3"
  }
}
```

Use only the simplified `style` keys:
- `format`: `date`, `datetime`, `currency`, `percent`, `integer`, `decimal`, `text`
- `format_code`
- `bold`, `italic`, `wrap_text`
- `font_color`, `bg_color`
- `horizontal`, `vertical`
- `font_size`, `font_family`

This API applies only the specified keys and preserves existing unspecified style properties.

#### Set Auto Filter
```
POST /api/v1/excel/set_auto_filter
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Sheet1",
  "auto_filter": {
    "ref": "A1:F100",
    "filter_columns": []
  }
}
```

#### Remove Auto Filter
```
POST /api/v1/excel/remove_auto_filter
Authorization: Bearer <token>

{ "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1" }
```

#### Set Conditional Formats
```
POST /api/v1/excel/set_conditional_formats
Authorization: Bearer <token>

{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>",
  "worksheet_name": "Sheet1",
  "formats": [
    {
      "sqref": "B2:B100",
      "type": "cell",
      "criteria": ">",
      "value": "90",
      "format": { "font": { "color": "FF0000" } }
    }
  ]
}
```

---

## Common Workflows

### Workflow 1: Upload and read a file

```
1. Upload: POST /api/v1/excel/upload  → get document_id
2. List sheets: POST /api/v1/excel/list_worksheets  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>"}
3. Read data: POST /api/v1/excel/read_sheet  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1"}
```

### Workflow 2: Build a SQL-assisted pivot/result sheet

```
1. List worksheets: POST /api/v1/excel/list_worksheets  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>"}
2. Inspect headers: POST /api/v1/excel/read_headers  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2"}
3. Compile SQL: POST /api/v1/excel/sql/compile  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2", "sql": "select \"Region\", sum(\"Revenue\") as \"Revenue\" from gid_2 group by \"Region\" order by \"Revenue\" desc"}
4. Write result: POST /api/v1/excel/sql/write_result  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2", "sql": "select \"Region\", sum(\"Revenue\") as \"Revenue\" from gid_2 group by \"Region\" order by \"Revenue\" desc", "target_worksheet_name": "Pivot_RegionRevenue", "target_start_cell": "A1", "create_sheet_if_missing": true, "clear_target_range": true, "include_headers": true}
5. Verify: POST /api/v1/excel/read_sheet  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Pivot_RegionRevenue", "range_address": "A1:B20"}
```

### Workflow 3: Update existing data

```
1. Find file: POST /api/v1/excel/search_files  {"keyword": "sales"}
2. Read current data: POST /api/v1/excel/read_sheet  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1"}
3. Upsert changed rows by key: POST /api/v1/excel/update_range_by_lookup  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2", "data": [...], "on": ["Order ID"]}
4. Recalculate: POST /api/v1/excel/recalculate_formulas  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>"}
```

### Workflow 4: Bulk data append

```
1. Identify document_id (list_files or upload)
2. Choose the target worksheet first: either `worksheet_name` or `uri?gid=N`
3. Append object rows: POST /api/v1/excel/append_rows  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2", "data": [...]}
4. Upsert object rows by key: POST /api/v1/excel/update_range_by_lookup  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>?gid=2", "data": [...], "on": [...]}
5. Replace the table under existing headers: POST /api/v1/excel/update_data_keep_headers  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1", "data": [...]}
6. Read back to verify: POST /api/v1/excel/read_sheet  {"uri": "https://www.maybe.ai/docs/spreadsheets/d/<document_id>", "worksheet_name": "Sheet1"}
```

### Workflow 5: Refresh a table but keep headers and formulas

```
1. Identify document_id and worksheet
2. Read current data or headers if needed: POST /api/v1/excel/read_sheet or /read_headers
3. Replace table rows: POST /api/v1/excel/update_data_keep_headers
4. Use preserve_formulas=true if computed columns should remain
5. Read back to verify: POST /api/v1/excel/read_sheet
```

---

## Notes

- **`uri` format**: Build `uri` from the returned `document_id` as `https://www.maybe.ai/docs/spreadsheets/d/{document_id}`. Add `?gid={gid}` only when the API needs worksheet selection from the URI itself.
- **SQL authoring**: For pivot/result-table generation, inspect worksheet names first, then use `read_headers` or a small `read_sheet` sample before writing SQL. Prefer `sql/compile` plus `sql/write_result` over `calc_formulas` for this workflow.
- **SQL table references**: Use either the worksheet name or `gid_*`. Quote worksheet names with spaces, for example `"Sales Data"`.
- **Range format**: Use Excel-style ranges like `A1`, `A1:B10`, `A:A`.
- **Style API rule**: Use only `batch_set_cell_style` for cell formatting. For a single target range, still send `range_addresses` as a one-item array.
- **Style input rule**: Keep style payloads small and explicit. Prefer keys like `format`, `bold`, `bg_color`, `horizontal`, and `wrap_text` instead of low-level Excel style structures.
- **Row/column indexing**: Row numbers are 1-indexed (row 1 = first data row). Columns use Excel letters (`A`, `B`, ...).
- **Worksheet targeting is explicit**: If you do not pass `worksheet_name` or `?gid=` in `uri`, many endpoints fall back to the first worksheet. This is the common reason writes appear to go to `gid=0`.
- **Header-aware tools are usually safer for agents**: `update_data_keep_headers` and `update_range_by_lookup` work with header names instead of raw column positions, which reduces mistakes when sheet layouts change.
- **Authentication**: Endpoints marked `AUTH` require `Authorization: Bearer <MAYBEAI_API_TOKEN>`. Public endpoints work without a token.
- **Spreadsheet viewer URL**: `https://www.maybe.ai/docs/spreadsheets/d/{doc_id}` renders a live HTML preview of the file and is the same base format used for request `uri` values.
