import { createRequire } from "node:module";
import { createPublicClient, createWalletClient, formatEther, formatUnits, getAddress, http, isAddress, isHex, parseEther, parseUnits, } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { DEFAULT_CORE_ADDRESS, DEFAULT_COUNCIL_ADDRESS, DEFAULT_PREDICTION_ADDRESS, getPrivateKey, getRuntimeConfig, readRuntimeConfig, } from "./config.js";
const require = createRequire(import.meta.url);
export const coreArtifact = require("../contracts/MoltXCore.json");
export const councilArtifact = require("../contracts/MoltXCouncil.json");
export const predictionArtifact = require("../contracts/MoltXPrediction.json");
export const coreAbi = coreArtifact.abi;
export const councilAbi = councilArtifact.abi;
export const predictionAbi = predictionArtifact.abi;
export function stringifyJson(value) {
    return JSON.stringify(value, (_key, currentValue) => typeof currentValue === "bigint" ? currentValue.toString() : currentValue, 2);
}
export function toRecord(value) {
    if (value === null || typeof value !== "object" || Array.isArray(value)) {
        throw new Error("tool payload must be a JSON object");
    }
    return Object.fromEntries(Object.entries(value));
}
export function tupleField(value, index, key) {
    if (Array.isArray(value)) {
        return value[index];
    }
    const record = toRecord(value);
    if (!(key in record)) {
        throw new Error(`missing tuple field ${key}`);
    }
    return record[key];
}
export function requiredString(record, key) {
    const value = record[key];
    if (typeof value !== "string" || value.trim() === "") {
        throw new Error(`${key} must be a non-empty string`);
    }
    return value;
}
export function optionalString(record, key) {
    const value = record[key];
    if (value === undefined) {
        return undefined;
    }
    return requiredString(record, key);
}
export function requiredBoolean(record, key) {
    const value = record[key];
    if (typeof value !== "boolean") {
        throw new Error(`${key} must be a boolean`);
    }
    return value;
}
export function optionalBoolean(record, key) {
    const value = record[key];
    if (value === undefined) {
        return undefined;
    }
    if (typeof value !== "boolean") {
        throw new Error(`${key} must be a boolean`);
    }
    return value;
}
export function bigintFromUnknown(value, key) {
    if (typeof value === "bigint") {
        return value;
    }
    if (typeof value === "number" && Number.isInteger(value)) {
        return BigInt(value);
    }
    if (typeof value === "string" && value.trim() !== "") {
        return BigInt(value);
    }
    throw new Error(`${key} must be an integer string or integer number`);
}
export function requiredBigInt(record, key) {
    return bigintFromUnknown(record[key], key);
}
export function optionalBigInt(record, key) {
    if (record[key] === undefined) {
        return undefined;
    }
    return bigintFromUnknown(record[key], key);
}
export function numberFromUnknown(value, key) {
    if (typeof value === "number" && Number.isInteger(value)) {
        return value;
    }
    if (typeof value === "string" && value.trim() !== "") {
        const parsed = Number(value);
        if (Number.isInteger(parsed)) {
            return parsed;
        }
    }
    throw new Error(`${key} must be an integer`);
}
export function requiredNumber(record, key) {
    return numberFromUnknown(record[key], key);
}
export function optionalNumber(record, key) {
    if (record[key] === undefined) {
        return undefined;
    }
    return numberFromUnknown(record[key], key);
}
export function addressFromUnknown(value, key) {
    if (typeof value !== "string" || !isAddress(value)) {
        throw new Error(`${key} must be a valid address`);
    }
    return getAddress(value);
}
export function requiredAddress(record, key) {
    return addressFromUnknown(record[key], key);
}
export function optionalAddress(record, key) {
    if (record[key] === undefined) {
        return undefined;
    }
    return addressFromUnknown(record[key], key);
}
export function requiredHex32(record, key) {
    const value = record[key];
    if (typeof value !== "string" || !isHex(value) || value.length !== 66) {
        throw new Error(`${key} must be a 32-byte hex string`);
    }
    return value;
}
export function optionalHex32(record, key) {
    const value = record[key];
    if (value === undefined) {
        return undefined;
    }
    return requiredHex32(record, key);
}
export function requiredAddressArray(record, key) {
    const value = record[key];
    if (!Array.isArray(value) || value.length === 0) {
        throw new Error(`${key} must be a non-empty address array`);
    }
    return value.map((entry) => addressFromUnknown(entry, key));
}
export function getPublicRuntime() {
    const config = getRuntimeConfig();
    const publicClient = createPublicClient({
        transport: http(config.rpcUrl),
    });
    return { config, publicClient };
}
export function getWriteRuntime() {
    const config = readRuntimeConfig();
    const account = privateKeyToAccount(getPrivateKey());
    const publicClient = createPublicClient({
        transport: http(config.rpcUrl),
    });
    const walletClient = createWalletClient({
        account,
        transport: http(config.rpcUrl),
    });
    return { config, publicClient, walletClient, account };
}
export function requireCoreAddress(config) {
    if (config.coreAddress === DEFAULT_CORE_ADDRESS) {
        throw new Error("coreAddress placeholder has not been replaced yet");
    }
    return config.coreAddress;
}
export function requireCouncilAddress(config) {
    if (!config.councilAddress || config.councilAddress === DEFAULT_COUNCIL_ADDRESS) {
        throw new Error("councilAddress placeholder has not been replaced yet");
    }
    return config.councilAddress;
}
export function requirePredictionAddress(config) {
    if (!config.predictionAddress || config.predictionAddress === DEFAULT_PREDICTION_ADDRESS) {
        throw new Error("predictionAddress placeholder has not been replaced yet");
    }
    return config.predictionAddress;
}
export const TASK_MODES = ["SINGLE", "MULTI"];
export const TASK_STATUSES = [
    "OPEN",
    "ACCEPTED",
    "SUBMITTED",
    "COMPLETED",
    "REJECTED",
    "COMPLETED_MAKER",
    "DISPUTED",
    "RESOLVED",
    "DISPUTE_UNRESOLVED",
    "EXPIRED",
];
export function modeLabel(mode) {
    return TASK_MODES[mode] ?? `UNKNOWN_${mode}`;
}
export function statusLabel(status) {
    return TASK_STATUSES[status] ?? `UNKNOWN_${status}`;
}
export function formatBigintValue(value, decimals, kind = "token") {
    return kind === "ether" ? formatEther(value) : formatUnits(value, decimals);
}
export function parseValue(value, decimals, kind = "token") {
    return kind === "ether" ? parseEther(value) : parseUnits(value, decimals);
}
