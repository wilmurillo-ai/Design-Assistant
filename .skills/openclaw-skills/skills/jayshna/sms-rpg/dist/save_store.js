"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.toPositiveInteger = toPositiveInteger;
exports.listSaveSlots = listSaveSlots;
exports.saveGame = saveGame;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const world_state_utils_1 = require("./world_state_utils");
const runtime_paths_1 = require("./runtime_paths");
const SAVE_SLOT_IDS = ["save_001", "save_002", "save_003", "save_004", "save_005"];
const SAVE_DIRECTORY_PATHS = (0, runtime_paths_1.getDataRootCandidates)(true).map(root => (0, node_path_1.join)(root, "saves"));
function toPositiveInteger(value, fallback) {
    if (typeof value === "number" && Number.isInteger(value) && value > 0) {
        return value;
    }
    if (typeof value === "string") {
        const parsed = Number.parseInt(value, 10);
        if (Number.isInteger(parsed) && parsed > 0) {
            return parsed;
        }
    }
    return fallback;
}
function toIsoString(value) {
    if (typeof value === "string" && value.trim().length > 0) {
        return value;
    }
    if (typeof value === "number" && Number.isFinite(value)) {
        return new Date(value).toISOString();
    }
    return new Date().toISOString();
}
function normalizeTimelineEvent(raw) {
    if (!(0, world_state_utils_1.isRecord)(raw) || typeof raw.id !== "string" || typeof raw.description !== "string") {
        return null;
    }
    return {
        id: raw.id,
        turn: toPositiveInteger(raw.turn, 1),
        description: raw.description.trim(),
        category: typeof raw.category === "string" ? raw.category : undefined,
        importance: raw.importance === "world_shaking" || raw.importance === "major" || raw.importance === "minor"
            ? raw.importance
            : "minor",
        affectedFactions: Array.isArray(raw.affectedFactions) ? (0, world_state_utils_1.uniqueStrings)(raw.affectedFactions) : [],
        relatedNPCs: Array.isArray(raw.relatedNPCs) ? (0, world_state_utils_1.uniqueStrings)(raw.relatedNPCs) : [],
        relatedQuests: Array.isArray(raw.relatedQuests) ? (0, world_state_utils_1.uniqueStrings)(raw.relatedQuests) : [],
        relatedLocations: Array.isArray(raw.relatedLocations) ? (0, world_state_utils_1.uniqueStrings)(raw.relatedLocations) : [],
        npcNames: Array.isArray(raw.npcNames) ? (0, world_state_utils_1.uniqueStrings)(raw.npcNames) : [],
        questTitles: Array.isArray(raw.questTitles) ? (0, world_state_utils_1.uniqueStrings)(raw.questTitles) : [],
        locationNames: Array.isArray(raw.locationNames) ? (0, world_state_utils_1.uniqueStrings)(raw.locationNames) : [],
        tags: Array.isArray(raw.tags) ? (0, world_state_utils_1.uniqueStrings)(raw.tags) : [],
        searchText: typeof raw.searchText === "string" ? raw.searchText.trim() : raw.description.trim()
    };
}
function normalizeGameSave(raw, slotId) {
    if (!(0, world_state_utils_1.isRecord)(raw) || !(0, world_state_utils_1.isRecord)(raw.worldState)) {
        return null;
    }
    const playerName = typeof raw.playerName === "string" && raw.playerName.trim().length > 0
        ? raw.playerName.trim()
        : "旅人";
    const normalizedState = (0, world_state_utils_1.normalizeWorldState)(raw.worldState, playerName);
    return {
        version: "2.0",
        savedAt: toIsoString(raw.savedAt ?? raw.timestamp),
        playerName,
        worldRequirement: typeof raw.worldRequirement === "string" && raw.worldRequirement.trim().length > 0
            ? raw.worldRequirement.trim()
            : "未记录世界观",
        narrativeStyle: typeof raw.narrativeStyle === "string" && raw.narrativeStyle.trim().length > 0
            ? raw.narrativeStyle.trim()
            : "通俗、利落，偏《庆余年》式叙事",
        currentTurn: toPositiveInteger(raw.currentTurn ?? raw.turnNumber, 1),
        worldState: normalizedState,
        allTurnRecords: Array.isArray(raw.allTurnRecords) ? raw.allTurnRecords : [],
        allEpisodeSummaries: Array.isArray(raw.allEpisodeSummaries) ? raw.allEpisodeSummaries : [],
        allTimelineEvents: Array.isArray(raw.allTimelineEvents)
            ? raw.allTimelineEvents
                .map(normalizeTimelineEvent)
                .filter((event) => event !== null)
            : [],
        previousSummary: typeof raw.previousSummary === "string" ? raw.previousSummary : "",
        currentOptions: (0, world_state_utils_1.ensureActionOptions)(Array.isArray(raw.currentOptions) ? raw.currentOptions : []),
        saveSlot: typeof raw.saveSlot === "string" && raw.saveSlot.trim().length > 0 ? raw.saveSlot : slotId
    };
}
async function readSaveSlot(slotId) {
    for (const saveDir of SAVE_DIRECTORY_PATHS) {
        const filePath = (0, node_path_1.join)(saveDir, `${slotId}.json`);
        try {
            const content = await (0, promises_1.readFile)(filePath, 'utf-8');
            const data = normalizeGameSave(JSON.parse(content), slotId);
            return {
                slotId,
                filePath,
                data,
                statusText: data ? "可继续" : "文件损坏"
            };
        }
        catch {
            continue;
        }
    }
    return {
        slotId,
        filePath: null,
        data: null,
        statusText: "未找到文件"
    };
}
async function listSaveSlots() {
    return Promise.all(SAVE_SLOT_IDS.map(slotId => readSaveSlot(slotId)));
}
async function getWritableSaveDirectory() {
    for (const saveDir of SAVE_DIRECTORY_PATHS) {
        try {
            await (0, promises_1.mkdir)(saveDir, { recursive: true });
            return saveDir;
        }
        catch {
            continue;
        }
    }
    return null;
}
async function saveGame(slotId, data) {
    const saveDir = await getWritableSaveDirectory();
    if (!saveDir) {
        console.error("\n[警告] 保存进度失败：没有可写的存档目录");
        return null;
    }
    try {
        const filePath = (0, node_path_1.join)(saveDir, `${slotId}.json`);
        await (0, promises_1.writeFile)(filePath, JSON.stringify(data, null, 2), 'utf-8');
        return filePath;
    }
    catch (error) {
        console.error(`\n[警告] 保存进度失败：${String(error)}`);
        return null;
    }
}
