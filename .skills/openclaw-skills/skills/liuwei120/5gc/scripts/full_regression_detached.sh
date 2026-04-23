#!/usr/bin/env bash
set -euo pipefail
ROOT="/home/dotouch/.openclaw/workspace"
BASE="node $ROOT/skills/5gc/scripts/5gc.js"
OUTDIR="$ROOT/skills/5gc/test_results"
mkdir -p "$OUTDIR"
TS="$(date +%Y%m%d-%H%M%S)"
LOG="$OUTDIR/${TS}-full-regression.log"

run() {
  echo "===== $1 =====" | tee -a "$LOG"
  shift
  "$@" 2>&1 | tee -a "$LOG"
  echo | tee -a "$LOG"
}

# add / edit / bulk for main entities still in scope
run "AMF add" bash -lc "$BASE amf add --name AMF_REG_FULL_${TS} --project XW_S5GC_1"
run "AMF single edit" bash -lc "$BASE amf edit --name AMF_REG_FULL_${TS} --project XW_S5GC_1 --set-mcc 460"
run "AMF bulk edit" bash -lc "$BASE amf edit --project XW_S5GC_1 --set-mnc 01"

run "UDM add" bash -lc "$BASE udm add --name UDM_REG_FULL_${TS} --project XW_S5GC_1 --sip 10.200.5.9 --port 80"
run "UDM single edit" bash -lc "$BASE udm edit --name UDM_REG_FULL_${TS} --project XW_S5GC_1 --set-port 81"
run "UDM bulk edit" bash -lc "$BASE udm edit --project XW_S5GC_1 --set-port 82"

run "UPF add" bash -lc "$BASE upf add --name UPF_REG_FULL_${TS} --project XW_S5GC_1 --n4-ip 10.200.3.11 --n3-ip 10.200.3.12 --n6-ip 10.200.3.13"
run "UPF single edit" bash -lc "$BASE upf edit --name UPF_REG_FULL_${TS} --project XW_S5GC_1 --set-n4_ip 10.200.3.14"
run "UPF bulk edit" bash -lc "$BASE upf edit --project XW_S5GC_1 --set-n4_ip 10.200.3.15"

run "GNB add" bash -lc "$BASE gnb add --name GNB_REG_FULL_${TS} --project XW_S5GC_1 --count 100 --ngap-ip 10.200.4.11 --user-sip-ip-v4 10.200.4.12 --mcc 460 --mnc 01 --stac 1 --etac 100 --node-id 70"
run "GNB single edit" bash -lc "$BASE gnb edit --name GNB_REG_FULL_${TS} --project XW_S5GC_1 --set-replay_ip 10.200.4.13"
run "GNB bulk edit" bash -lc "$BASE gnb edit --project XW_S5GC_1 --set-replay_ip 10.200.4.14"

run "UE add" bash -lc "$BASE ue add --name UE_REG_FULL_${TS} --project XW_S5GC_1 --imsi 460001234567890 --msisdn 8613888888888 --mcc 460 --mnc 01"
run "UE single edit" bash -lc "$BASE ue edit --name UE_SMOKE_FINAL --project XW_S5GC_1 --set-msisdn 8613888886666"
run "UE bulk edit" bash -lc "$BASE ue edit --project XW_S5GC_1 --set-msisdn 8613888885555"

# additional entities/features
run "SMF add" bash -lc "$BASE smf add --name SMF_REG_FULL_${TS} --project XW_S5GC_1 --pfcp-ip 10.200.2.11 --n3-ip 10.200.2.12 --n6-ip 10.200.2.13"
run "SMF single edit" bash -lc "$BASE smf edit --name SMF_REG_FULL_${TS} --project XW_S5GC_1 --set-dnn internet_updated"
run "SMF bulk edit" bash -lc "$BASE smf edit --project XW_S5GC_1 --set-dnn internet"

run "PCF default-rule-add" bash -lc "$BASE pcf default-rule-add --project XW_SUPF_5_1_2_4 --pcf-name pcc"
run "NRF add" bash -lc "$BASE nrf add --name NRF_REG_FULL_${TS} --project XW_S5GC_1"
run "NRF single edit" bash -lc "$BASE nrf edit --name NRF_REG_FULL_${TS} --project XW_S5GC_1 --set-http2_port 81"
run "QOS add" bash -lc "$BASE qos add --project XW_SUPF_5_1_2_4 --qos-id qos_reg_${TS} --5qi 8 --maxbr-ul 10000000 --maxbr-dl 20000000"
run "TC add" bash -lc "$BASE tc add --project XW_SUPF_5_1_2_4 --tc-id tc_reg_${TS} --flow-status ENABLED"
run "PCC add" bash -lc "$BASE pcc add --project XW_SUPF_5_1_2_4 --pcc-id pcc_reg_${TS} --qos qos_reg_${TS} --tc tc_reg_${TS}"

echo "FULL REGRESSION DONE: $LOG" | tee -a "$LOG"
