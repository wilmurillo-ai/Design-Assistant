#!/bin/bash
cd /home/dotouch/.openclaw/workspace/skills/5gc/scripts
TS=$(date +%s)
BASE="node 5gc.js"
echo "=== QoS add === $(date)"
$BASE qos add --project XW_SUPF_5_1_2_4 --qos-id qos_reg_$TS --5qi 8 --maxbr-ul 10000000 --maxbr-dl 20000000 2>&1 | tail -5
echo "=== TC add === $(date)"
$BASE tc add --project XW_SUPF_5_1_2_4 --tc-id tc_reg_$TS --flow-status ENABLED 2>&1 | tail -5
echo "=== PCC add === $(date)"
$BASE pcc add --project XW_SUPF_5_1_2_4 --pcc-id pcc_reg_$TS --qos qos_reg_$TS --tc tc_reg_$TS 2>&1 | tail -5
echo "All batch2 done $(date)"
