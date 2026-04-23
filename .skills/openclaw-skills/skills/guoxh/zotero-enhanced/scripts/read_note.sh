#!/bin/bash
set -e
set -o pipefail

# Zotero note reading script
# Reads a note and converts HTML to plain text
# Version: 1.3.0
# Safety: Only calls Zotero API. No eval, no obfuscation.

# Argument handling
OUTPUT_FORMAT="plain"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            cat <<EOF
Usage: $0 [OPTIONS] NOTE_KEY
Read a note from Zotero.

Options:
  --help, -h        Show this help
  --version         Show version
  --format FORMAT   Output format: plain (default), html, json

Environment variables:
  ZOTERO_USER_ID, ZOTERO_API_KEY required.

Examples:
  $0 ABC12
  $0 --format html ABC12
  $0 --format json ABC12

Security: This script only calls Zotero API.
No eval, no obfuscation, no hidden network calls.
EOF
            exit 0
            ;;
        --version)
            echo "zotero-enhanced read_note.sh v1.3.0"
            exit 0
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        *)
            # Assume it's the note key
            NOTE_KEY="$1"
            shift
            ;;
    esac
done

if [ -z "$NOTE_KEY" ]; then
    echo "Error: Note key not provided."
    exit 1
fi

: "${ZOTERO_USER_ID:?ZOTERO_USER_ID not set}"
: "${ZOTERO_API_KEY:?ZOTERO_API_KEY not set}"

API_URL="https://api.zotero.org/users/$ZOTERO_USER_ID/items/$NOTE_KEY"

echo "Reading note: $NOTE_KEY"

# Fetch the note
RESPONSE=$(curl -s -f \
    -H "Zotero-API-Key: $ZOTERO_API_KEY" \
    "$API_URL")

# Validate response
if ! echo "$RESPONSE" | jq -e '.data' > /dev/null; then
    echo "Error: Invalid response from Zotero API."
    echo "Response: $RESPONSE" >&2
    exit 1
fi

# Check if it's a note
ITEM_TYPE=$(echo "$RESPONSE" | jq -r '.data.itemType')
if [ "$ITEM_TYPE" != "note" ]; then
    echo "Error: Item is not a note (type: $ITEM_TYPE)." >&2
    exit 1
fi

# Output based on format
case "$OUTPUT_FORMAT" in
    html)
        # Output raw HTML
        echo "$RESPONSE" | jq -r '.data.note'
        ;;
    json)
        # Output full JSON
        echo "$RESPONSE" | jq '.data'
        ;;
    plain)
        # Convert HTML to plain text
        HTML_CONTENT=$(echo "$RESPONSE" | jq -r '.data.note')
        
        # Basic HTML to text conversion
        # Remove <p> tags and convert to newlines
        TEXT=$(echo "$HTML_CONTENT" | sed 's/<p>/\n/g; s/<\/p>/\n/g')
        # Remove other HTML tags
        TEXT=$(echo "$TEXT" | sed 's/<[^>]*>//g')
        # Remove extra newlines
        TEXT=$(echo "$TEXT" | sed '/^$/d' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
        
        echo "$TEXT"
        ;;
    *)
        echo "Error: Invalid format '$OUTPUT_FORMAT'. Use plain, html, or json." >&2
        exit 1
        ;;
esac
