import fs from "node:fs";
import os from "node:os";
import path from "node:path";
const STATE_DIR = path.join(os.homedir(), ".moltx");
const SYNC_STATE_PATH = path.join(STATE_DIR, "sync-state.json");
const MAKER_TASKS_PATH = path.join(STATE_DIR, "maker-tasks.json");
const TAKER_TASKS_PATH = path.join(STATE_DIR, "taker-tasks.json");
const DISPUTES_PATH = path.join(STATE_DIR, "disputes.json");
const PREDICTION_BETS_PATH = path.join(STATE_DIR, "prediction-bets.json");
const PROCESSED_EVENTS_PATH = path.join(STATE_DIR, "processed-events.json");
const DEFAULT_SYNC_STATE = {
    walletAddress: "",
    core: { lastSyncBlock: "0", lastSyncTime: new Date().toISOString() },
    prediction: { lastSyncBlock: "0", lastSyncTime: new Date().toISOString() },
};
function ensureStateDir() {
    fs.mkdirSync(STATE_DIR, { recursive: true });
}
function readJsonFile(filePath, defaultValue) {
    if (!fs.existsSync(filePath)) {
        return defaultValue;
    }
    try {
        return JSON.parse(fs.readFileSync(filePath, "utf8"));
    }
    catch {
        return defaultValue;
    }
}
function writeJsonFile(filePath, value) {
    ensureStateDir();
    fs.writeFileSync(filePath, JSON.stringify(value, null, 2));
}
export function readSyncState() {
    return readJsonFile(SYNC_STATE_PATH, DEFAULT_SYNC_STATE);
}
export function writeSyncState(state) {
    writeJsonFile(SYNC_STATE_PATH, state);
}
export function updateCoreSyncBlock(blockNumber, walletAddress) {
    const state = readSyncState();
    state.walletAddress = walletAddress;
    state.core = { lastSyncBlock: blockNumber, lastSyncTime: new Date().toISOString() };
    writeSyncState(state);
}
export function updatePredictionSyncBlock(blockNumber, walletAddress) {
    const state = readSyncState();
    state.walletAddress = walletAddress;
    state.prediction = { lastSyncBlock: blockNumber, lastSyncTime: new Date().toISOString() };
    writeSyncState(state);
}
export function readMakerTasks() {
    return readJsonFile(MAKER_TASKS_PATH, { tasks: {} });
}
export function writeMakerTasks(state) {
    writeJsonFile(MAKER_TASKS_PATH, state);
}
export function addOrUpdateMakerTask(task) {
    const state = readMakerTasks();
    state.tasks[task.taskId] = task;
    writeMakerTasks(state);
}
export function getMakerTask(taskId) {
    return readMakerTasks().tasks[taskId];
}
export function readTakerTasks() {
    return readJsonFile(TAKER_TASKS_PATH, { tasks: {} });
}
export function writeTakerTasks(state) {
    writeJsonFile(TAKER_TASKS_PATH, state);
}
export function addOrUpdateTakerTask(task) {
    const state = readTakerTasks();
    state.tasks[task.taskId] = task;
    writeTakerTasks(state);
}
export function getTakerTask(taskId) {
    return readTakerTasks().tasks[taskId];
}
export function readDisputes() {
    return readJsonFile(DISPUTES_PATH, { disputes: {} });
}
export function writeDisputes(state) {
    writeJsonFile(DISPUTES_PATH, state);
}
export function addOrUpdateDispute(dispute) {
    const state = readDisputes();
    state.disputes[dispute.taskId] = dispute;
    writeJsonFile(DISPUTES_PATH, state);
}
export function readPredictionBets() {
    return readJsonFile(PREDICTION_BETS_PATH, { bets: {} });
}
export function writePredictionBets(state) {
    writeJsonFile(PREDICTION_BETS_PATH, state);
}
export function addOrUpdatePredictionBet(bet) {
    const state = readPredictionBets();
    state.bets[`${bet.roundId}:${bet.tier}`] = bet;
    writePredictionBets(state);
}
function readProcessedEvents() {
    return readJsonFile(PROCESSED_EVENTS_PATH, {
        txHashes: [],
        lastCleanup: new Date().toISOString(),
    });
}
function writeProcessedEvents(state) {
    writeJsonFile(PROCESSED_EVENTS_PATH, {
        ...state,
        txHashes: state.txHashes.slice(-1000),
    });
}
export function isEventProcessed(txHash) {
    return readProcessedEvents().txHashes.includes(txHash);
}
export function markEventProcessed(txHash) {
    const state = readProcessedEvents();
    if (!state.txHashes.includes(txHash)) {
        state.txHashes.push(txHash);
    }
    writeProcessedEvents(state);
}
export function resetAllAgentState() {
    ensureStateDir();
    writeSyncState(DEFAULT_SYNC_STATE);
    writeMakerTasks({ tasks: {} });
    writeTakerTasks({ tasks: {} });
    writeJsonFile(DISPUTES_PATH, { disputes: {} });
    writePredictionBets({ bets: {} });
    writeProcessedEvents({ txHashes: [], lastCleanup: new Date().toISOString() });
}
