#!/usr/bin/env bash
# MaybeAI Sheet — Charts & Pictures
# Usage: export MAYBEAI_API_TOKEN=your_token_here
#        export DOC_ID=your_document_id_here
#        bash 07-charts-pictures.sh

BASE_URL="https://play-be.omnimcp.ai"
TOKEN="${MAYBEAI_API_TOKEN:?Please set MAYBEAI_API_TOKEN}"
DOC_ID="${DOC_ID:?Please set DOC_ID}"
DOC_URI="https://www.maybe.ai/docs/spreadsheets/d/$DOC_ID"
PICTURE_FILE_BASE64="${PICTURE_FILE_BASE64:-iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4////fwAJ+wP9KobjigAAAABJRU5ErkJggg==}"

# ── Add Chart ─────────────────────────────────────────────────────────────────
# Supported types: line, bar, col, pie, scatter, area, doughnut, radar
echo "=== Add Bar Chart ==="
curl -s -X POST "$BASE_URL/api/v1/excel/add_chart" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"uri\": \"$DOC_URI\",
    \"worksheet_name\": \"Sheet1\",
    \"cell\": \"E2\",
    \"chart\": {
      \"type\": \"bar\",
      \"series\": [
        {
          \"name\": \"Revenue\",
          \"categories\": \"Sheet1!\$A\$2:\$A\$10\",
          \"values\": \"Sheet1!\$B\$2:\$B\$10\"
        }
      ],
      \"title\": {\"name\": \"Monthly Revenue\"},
      \"legend\": {\"position\": \"bottom\"}
    }
  }" \
  | jq .

# ── Add Line Chart ────────────────────────────────────────────────────────────
echo "=== Add Line Chart ==="
curl -s -X POST "$BASE_URL/api/v1/excel/add_chart" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"uri\": \"$DOC_URI\",
    \"worksheet_name\": \"Sheet1\",
    \"cell\": \"E20\",
    \"chart\": {
      \"type\": \"line\",
      \"series\": [
        {
          \"name\": \"Sales\",
          \"categories\": \"Sheet1!\$A\$2:\$A\$12\",
          \"values\": \"Sheet1!\$C\$2:\$C\$12\"
        }
      ],
      \"title\": {\"name\": \"Sales Trend\"}
    }
  }" \
  | jq .

# ── Edit Chart ────────────────────────────────────────────────────────────────
echo "=== Edit Chart ==="
curl -s -X POST "$BASE_URL/api/v1/excel/set_chart" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"uri\": \"$DOC_URI\",
    \"worksheet_name\": \"Sheet1\",
    \"cell\": \"E2\",
    \"chart\": {
      \"type\": \"bar\",
      \"series\": [
        {
          \"name\": \"Revenue\",
          \"categories\": \"Sheet1!\$A\$2:\$A\$10\",
          \"values\": \"Sheet1!\$B\$2:\$B\$10\"
        }
      ],
      \"title\": {\"name\": \"Updated Title\"}
    }
  }" \
  | jq .

# ── Delete Chart ──────────────────────────────────────────────────────────────
echo "=== Delete Chart ==="
curl -s -X POST "$BASE_URL/api/v1/excel/delete_chart" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"$DOC_URI\", \"worksheet_name\": \"Sheet1\", \"cell\": \"E2\"}" \
  | jq .

# ── Add Picture ───────────────────────────────────────────────────────────────
echo "=== Add Picture ==="
curl -s -X POST "$BASE_URL/api/v1/excel/add_picture" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"uri\": \"$DOC_URI\",
    \"worksheet_name\": \"Sheet1\",
    \"cell\": \"H2\",
    \"picture\": {
      \"file_base64\": \"$PICTURE_FILE_BASE64\",
      \"extension\": \"png\"
    }
  }" \
  | jq .

# ── Read Pictures ─────────────────────────────────────────────────────────────
echo "=== Read Pictures ==="
curl -s -X POST "$BASE_URL/api/v1/excel/read_picture" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"$DOC_URI\", \"worksheet_name\": \"Sheet1\", \"cell\": \"H2\"}" \
  | jq .

# ── Delete Picture ────────────────────────────────────────────────────────────
echo "=== Delete Picture ==="
curl -s -X POST "$BASE_URL/api/v1/excel/delete_picture" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"$DOC_URI\", \"worksheet_name\": \"Sheet1\", \"cell\": \"H2\"}" \
  | jq .
