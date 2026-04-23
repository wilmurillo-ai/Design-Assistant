import fs from "node:fs";
import os from "node:os";
import path from "node:path";
const STATE_DIR = path.join(os.homedir(), ".moltx");
const EVENT_STATE_PATH = path.join(STATE_DIR, "event-state.json");
const DEFAULT_STATE = {
    coreLastBlock: "0",
    predictionLastBlock: "0",
    processedTxHashes: [],
};
function ensureStateDir() {
    fs.mkdirSync(STATE_DIR, { recursive: true });
}
export function readEventState() {
    if (!fs.existsSync(EVENT_STATE_PATH)) {
        return DEFAULT_STATE;
    }
    try {
        return JSON.parse(fs.readFileSync(EVENT_STATE_PATH, "utf8"));
    }
    catch {
        return DEFAULT_STATE;
    }
}
function writeEventState(state) {
    ensureStateDir();
    fs.writeFileSync(EVENT_STATE_PATH, JSON.stringify({
        ...state,
        processedTxHashes: state.processedTxHashes.slice(-1000),
    }, null, 2));
}
export function updateCoreLastBlock(blockNumber) {
    const state = readEventState();
    state.coreLastBlock = blockNumber;
    writeEventState(state);
}
export function updatePredictionLastBlock(blockNumber) {
    const state = readEventState();
    state.predictionLastBlock = blockNumber;
    writeEventState(state);
}
export function markTxProcessed(txHash) {
    const state = readEventState();
    if (!state.processedTxHashes.includes(txHash)) {
        state.processedTxHashes.push(txHash);
    }
    writeEventState(state);
}
export function isTxProcessed(txHash) {
    return readEventState().processedTxHashes.includes(txHash);
}
export function resetEventState() {
    ensureStateDir();
    fs.writeFileSync(EVENT_STATE_PATH, JSON.stringify(DEFAULT_STATE, null, 2));
}
