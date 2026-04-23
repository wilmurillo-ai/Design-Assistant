#!/bin/bash
# Fetch the latest morning context from Spark's dream cycle
# Returns the morning briefing if one exists from the last 24h
# Usage: ./spark-morning.sh

SPARK_API_KEY="${SPARK_API_KEY:-}"
SPARK_ORG_ID="${SPARK_ORG_ID:-}"
SPARK_API_URL="${SPARK_API_URL:-https://zellin.ai/api}"

if [ -z "$SPARK_API_KEY" ] || [ -z "$SPARK_ORG_ID" ]; then
  echo '{"error": "SPARK_API_KEY and SPARK_ORG_ID must be set"}'
  exit 1
fi

curl -s -X POST "${SPARK_API_URL}/spark-memory-insights" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${SPARK_API_KEY}" \
  -d "{\"org_id\": \"${SPARK_ORG_ID}\", \"section\": \"dreams\"}" \
| python3 -c "
import sys, json
from datetime import datetime, timezone, timedelta

data = json.loads(sys.stdin.read())
dreams = data.get('dreams', [])

# Find the latest morning_context
morning = None
for d in dreams:
    if d.get('dream_phase') == 'morning_context':
        morning = d
        break

if not morning:
    print(json.dumps({'has_morning': False}))
    sys.exit(0)

content = morning.get('content', '')
if isinstance(content, dict):
    text = content.get('text', '')
elif isinstance(content, str):
    text = content
else:
    text = str(content)

# Check if it's recent (within last 36h to account for timezone differences)
created = morning.get('created_at', '')
is_recent = True
if created:
    try:
        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
        age_hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
        is_recent = age_hours < 36
    except:
        pass

print(json.dumps({
    'has_morning': True,
    'is_recent': is_recent,
    'text': text,
    'created_at': created,
}))
"
