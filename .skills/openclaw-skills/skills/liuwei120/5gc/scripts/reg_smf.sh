#!/bin/bash
cd /home/dotouch/.openclaw/workspace/skills/5gc/scripts
node smf-pgwc-add-skill.js SMF_REG_$(date +%s) --project XW_S5GC_1 --pfcp_sip 10.200.2.50 --http2_sip 10.200.2.51 --ue_min 30.30.30.30 --ue_max 30.30.30.60 --mcc 460 --mnc 01 --pdu_capacity 200000 --interest_tac 101
