#!/bin/bash
cd /home/dotouch/.openclaw/workspace/skills/5gc/scripts
TS=$(date +%s)
echo "=== UPF add === $(date)"
node upf-add-skill.js UPF_REG_$TS --project XW_S5GC_1 --pfcp_ip 10.200.2.60 --s5s8_ip 10.200.2.61 --teid 20000 --mcc 460 --mnc 01 2>&1 | tail -5
echo "=== GNB add === $(date)"
node gnb-add-skill.js GNB_REG_$TS --project XW_S5GC_1 --gNB_ID 10000 --mcc 460 --mnc 01 --Tac 101 2>&1 | tail -5
echo "=== UE add === $(date)"
node ue-add-skill.js UE_REG_$TS --project XW_S5GC_1 --imsi 460010000000001 --key 0000111122223333 --opc 00000000000000000000000000000000 --sqn 000000000001 2>&1 | tail -5
echo "=== NRF add === $(date)"
node nrf-add-skill.js NRF_REG_$TS --project XW_S5GC_1 --sbi_ip 10.200.2.70 --http_port 8080 2>&1 | tail -5
echo "All batch1 done $(date)"
