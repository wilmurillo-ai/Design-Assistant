#!/bin/bash
# Phone Call Script - Make calls via FaceTime
# Usage: call.sh +491234567890

NUMBER="$1"

if [ -z "$NUMBER" ]; then
    echo "Usage: call.sh <phone-number>"
    echo "Example: call.sh +491234567890"
    exit 1
fi

# Clean number - remove spaces, dashes
CLEAN_NUMBER=$(echo "$NUMBER" | tr -d '[:space:]\-\(\)')

echo "Calling $CLEAN_NUMBER..."

# Make the call via FaceTime tel: URL
open "tel:$CLEAN_NUMBER"

echo "Call initiated!"
