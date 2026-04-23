"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadDialogSessionMeta = loadDialogSessionMeta;
exports.saveDialogSessionMeta = saveDialogSessionMeta;
exports.loadDialogSave = loadDialogSave;
exports.saveDialogSave = saveDialogSave;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const runtime_paths_1 = require("./runtime_paths");
const DIALOG_ROOT_PATHS = (0, runtime_paths_1.getDataRootCandidates)().map(root => (0, node_path_1.join)(root, "dialog"));
function sanitizeSegment(value) {
    return value
        .trim()
        .replace(/[^a-zA-Z0-9._-]+/g, "_")
        .replace(/^_+|_+$/g, "")
        .slice(0, 80) || "default-user";
}
function isPendingSetup(value) {
    if (!value || typeof value !== "object") {
        return false;
    }
    const record = value;
    if (record.stage === "awaiting_player_name") {
        return typeof record.slotId === "string";
    }
    if (record.stage === "awaiting_api_key") {
        return typeof record.slotId === "string";
    }
    if (record.stage === "awaiting_world_requirement") {
        return typeof record.slotId === "string" && typeof record.playerName === "string";
    }
    if (record.stage === "awaiting_narrative_style") {
        return typeof record.slotId === "string"
            && typeof record.playerName === "string"
            && typeof record.worldRequirement === "string";
    }
    return false;
}
async function getWritableDialogRoot() {
    for (const root of DIALOG_ROOT_PATHS) {
        try {
            await (0, promises_1.mkdir)(root, { recursive: true });
            return root;
        }
        catch {
            continue;
        }
    }
    return null;
}
function buildMetaPath(root, userId) {
    return (0, node_path_1.join)(root, "meta", `${sanitizeSegment(userId)}.json`);
}
function buildSavePath(root, userId, slotId) {
    return (0, node_path_1.join)(root, "saves", sanitizeSegment(userId), `${slotId}.json`);
}
async function readJsonFile(filePath) {
    try {
        const raw = await (0, promises_1.readFile)(filePath, 'utf-8');
        return JSON.parse(raw);
    }
    catch {
        return null;
    }
}
async function loadDialogSessionMeta(userId) {
    for (const root of DIALOG_ROOT_PATHS) {
        const parsed = await readJsonFile(buildMetaPath(root, userId));
        if (!parsed) {
            continue;
        }
        return {
            userId,
            currentSlotId: typeof parsed.currentSlotId === "string" ? parsed.currentSlotId : "save_001",
            pendingSetup: isPendingSetup(parsed.pendingSetup) ? parsed.pendingSetup : null
        };
    }
    return {
        userId,
        currentSlotId: "save_001",
        pendingSetup: null
    };
}
async function saveDialogSessionMeta(meta) {
    const root = await getWritableDialogRoot();
    if (!root) {
        return null;
    }
    const filePath = buildMetaPath(root, meta.userId);
    await (0, promises_1.mkdir)((0, node_path_1.join)(filePath, ".."), { recursive: true });
    await (0, promises_1.writeFile)(filePath, JSON.stringify(meta, null, 2), 'utf-8');
    return filePath;
}
async function loadDialogSave(userId, slotId) {
    for (const root of DIALOG_ROOT_PATHS) {
        const parsed = await readJsonFile(buildSavePath(root, userId, slotId));
        if (parsed) {
            return parsed;
        }
    }
    return null;
}
async function saveDialogSave(userId, slotId, save) {
    const root = await getWritableDialogRoot();
    if (!root) {
        return null;
    }
    const filePath = buildSavePath(root, userId, slotId);
    await (0, promises_1.mkdir)((0, node_path_1.join)(filePath, ".."), { recursive: true });
    await (0, promises_1.writeFile)(filePath, JSON.stringify(save, null, 2), 'utf-8');
    return filePath;
}
