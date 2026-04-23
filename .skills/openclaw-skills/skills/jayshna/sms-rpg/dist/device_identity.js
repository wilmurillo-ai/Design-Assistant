"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getMachineIdentity = getMachineIdentity;
const node_crypto_1 = require("node:crypto");
const node_os_1 = require("node:os");
function readFirstEnvValue(names) {
    for (const name of names) {
        const value = process.env[name]?.trim();
        if (value) {
            return value;
        }
    }
    return undefined;
}
function summarizeMachineId(machineId) {
    if (machineId.length <= 16) {
        return machineId;
    }
    return `${machineId.slice(0, 8)}...${machineId.slice(-6)}`;
}
function getMachineIdentity() {
    const fingerprintParts = [
        readFirstEnvValue(["OPENCLAW_USER", "OPENCLAW_SESSION_USER", "USER", "LOGNAME"]),
        process.env.HOME?.trim() || (0, node_os_1.homedir)(),
        (0, node_os_1.hostname)(),
        process.platform
    ].filter((value) => typeof value === "string" && value.length > 0);
    const rawFingerprint = fingerprintParts.join("|") || "unknown-machine";
    const digest = (0, node_crypto_1.createHash)("sha256").update(rawFingerprint).digest("hex");
    const machineId = `sms-${digest.slice(0, 32)}`;
    return {
        machineId,
        summary: summarizeMachineId(machineId),
        rawFingerprint
    };
}
