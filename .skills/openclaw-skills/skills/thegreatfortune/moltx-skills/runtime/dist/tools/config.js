import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { getAddress, isAddress, isHex, zeroAddress } from "viem";
import { privateKeyToAccount } from "viem/accounts";
const DEFAULT_RPC_URL = "https://sepolia.base.org";
export const DEFAULT_CORE_ADDRESS = zeroAddress;
export const DEFAULT_COUNCIL_ADDRESS = zeroAddress;
export const DEFAULT_PREDICTION_ADDRESS = zeroAddress;
const CONFIG_DIR = path.join(os.homedir(), ".moltx");
const CONFIG_PATH = path.join(CONFIG_DIR, "config.json");
const DEFAULT_CONFIG = {
    rpcUrl: DEFAULT_RPC_URL,
    coreAddress: DEFAULT_CORE_ADDRESS,
    councilAddress: DEFAULT_COUNCIL_ADDRESS,
    predictionAddress: DEFAULT_PREDICTION_ADDRESS,
};
function ensureConfigDir() {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
}
function parseAddress(value, key) {
    if (value === undefined || value === null || value === "") {
        return undefined;
    }
    if (typeof value !== "string" || !isAddress(value)) {
        throw new Error(`${key} must be a valid address`);
    }
    return getAddress(value);
}
function normalizeRuntimeConfig(value) {
    if (value === null || typeof value !== "object" || Array.isArray(value)) {
        throw new Error("runtime config must be a JSON object");
    }
    const record = value;
    const rpcUrl = typeof record.rpcUrl === "string" && record.rpcUrl.trim() !== ""
        ? record.rpcUrl
        : DEFAULT_RPC_URL;
    const coreAddress = parseAddress(record.coreAddress ?? DEFAULT_CORE_ADDRESS, "coreAddress") ??
        DEFAULT_CORE_ADDRESS;
    return {
        rpcUrl,
        coreAddress,
        councilAddress: parseAddress(record.councilAddress ?? DEFAULT_COUNCIL_ADDRESS, "councilAddress") ??
            DEFAULT_COUNCIL_ADDRESS,
        predictionAddress: parseAddress(record.predictionAddress ?? DEFAULT_PREDICTION_ADDRESS, "predictionAddress") ??
            DEFAULT_PREDICTION_ADDRESS,
        walletAddress: parseAddress(record.walletAddress, "walletAddress"),
    };
}
function readConfigFile() {
    if (!fs.existsSync(CONFIG_PATH)) {
        return DEFAULT_CONFIG;
    }
    return normalizeRuntimeConfig(JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8")));
}
export function getRuntimeConfig() {
    return readConfigFile();
}
export function readRuntimeConfig() {
    return readConfigFile();
}
export function setRuntimeConfig(patch) {
    const next = normalizeRuntimeConfig({
        ...readConfigFile(),
        ...patch,
    });
    ensureConfigDir();
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(next, null, 2));
    return next;
}
export function getPrivateKey() {
    const value = process.env.MOLTX_PRIVATE_KEY;
    if (!value) {
        throw new Error("MOLTX_PRIVATE_KEY environment variable not set");
    }
    if (!isHex(value) || value.length !== 66) {
        throw new Error("MOLTX_PRIVATE_KEY must be a 32-byte hex string (0x...)");
    }
    return value;
}
export function getWalletAddress() {
    const config = getRuntimeConfig();
    if (config.walletAddress) {
        return config.walletAddress;
    }
    const account = privateKeyToAccount(getPrivateKey());
    const walletAddress = getAddress(account.address);
    setRuntimeConfig({ walletAddress });
    return walletAddress;
}
