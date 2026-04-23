#!/bin/bash

NOTEBOOK_ID=$1
FILE_PATH=$2

/Users/block/notebooklm-env/bin/notebooklm source add \
  --notebook "$NOTEBOOK_ID" \
  --type file "$FILE_PATH"
