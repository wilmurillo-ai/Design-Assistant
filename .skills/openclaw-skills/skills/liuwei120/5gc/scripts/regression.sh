#!/bin/bash
cd /home/dotouch/.openclaw/workspace/skills/5gc/scripts
TS=$(date +%s)
SMF_NAME="SMF_REG_${TS}"
SMF_RESULT=$(bash -c '
SMF_NAME="SMF_REG_'"${TS}"'"
node smf-pgwc-add-skill.js "$SMF_NAME" --project XW_S5GC_1 --pfcp_sip 10.200.2.50 --http2_sip 10.200.2.51 --ue_min 30.30.30.30 --ue_max 30.30.30.60 --mcc 460 --mnc 01 --pdu_capacity 200000 --interest_tac 101
' 2>&1)
echo "=== SMF ADD ==="
echo "$SMF_RESULT"
if echo "$SMF_RESULT" | grep -q "添加成功"; then
  echo "✅ SMF ADD PASS"
else
  echo "❌ SMF ADD FAIL"
fi
