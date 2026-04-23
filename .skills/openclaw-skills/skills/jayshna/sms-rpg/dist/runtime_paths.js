"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getPackageRoot = getPackageRoot;
exports.resolvePackagePath = resolvePackagePath;
exports.getPromptPath = getPromptPath;
exports.getDataRootCandidates = getDataRootCandidates;
const node_os_1 = require("node:os");
const node_path_1 = require("node:path");
const PACKAGE_ROOT = (0, node_path_1.resolve)(__dirname, "..");
const DEFAULT_DATA_ROOT = (0, node_path_1.join)(PACKAGE_ROOT, ".sms-rpg-data");
function uniquePaths(paths) {
    const seen = new Set();
    const result = [];
    for (const value of paths) {
        const normalized = value?.trim();
        if (!normalized || seen.has(normalized)) {
            continue;
        }
        seen.add(normalized);
        result.push(normalized);
    }
    return result;
}
function getPackageRoot() {
    return PACKAGE_ROOT;
}
function resolvePackagePath(filePath) {
    if ((0, node_path_1.isAbsolute)(filePath)) {
        return filePath;
    }
    return (0, node_path_1.join)(PACKAGE_ROOT, filePath);
}
function getPromptPath(fileName) {
    return (0, node_path_1.join)(PACKAGE_ROOT, "prompts", fileName);
}
function getDataRootCandidates(includeLegacyAiCreator = false) {
    return uniquePaths([
        process.env.SMS_DATA_DIR,
        process.env.OPENCLAW_SMS_DATA_DIR,
        process.env.OPENCLAW_DATA_DIR,
        DEFAULT_DATA_ROOT,
        includeLegacyAiCreator ? (0, node_path_1.join)((0, node_os_1.homedir)(), ".config", "ai-creator-world-seed") : undefined,
        (0, node_path_1.join)((0, node_os_1.homedir)(), ".config", "sms-generate-cli"),
        (0, node_path_1.join)(process.cwd(), ".sms-generate-cli")
    ]);
}
