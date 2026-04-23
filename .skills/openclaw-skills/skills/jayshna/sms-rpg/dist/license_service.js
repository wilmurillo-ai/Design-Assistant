"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getPurchaseUrl = getPurchaseUrl;
exports.loadLicense = loadLicense;
exports.getLicenseStatus = getLicenseStatus;
exports.formatUnlockInstructions = formatUnlockInstructions;
exports.formatLicenseStatus = formatLicenseStatus;
exports.getAccessibleSaveSlotCount = getAccessibleSaveSlotCount;
exports.isAdvancedGenerationEnabled = isAdvancedGenerationEnabled;
exports.activateLicenseCode = activateLicenseCode;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const runtime_paths_1 = require("./runtime_paths");
const LICENSE_CODE_PATTERN = /^WUXIA-[A-Z2-9]{4}-[A-Z2-9]{4}$/;
const DEFAULT_VERIFY_URL = "https://license.lorecast.top/verify";
const DEFAULT_PURCHASE_URL = "https://ifdian.net/item/019051e4370e11f1be3652540025c377";
const LICENSE_FILE_PATHS = (0, runtime_paths_1.getDataRootCandidates)().map(root => (0, node_path_1.join)(root, "license.json"));
function readConfiguredUrl(names, fallback) {
    for (const name of names) {
        const value = process.env[name]?.trim();
        if (value) {
            return value;
        }
    }
    return fallback;
}
function summarizeMachineId(machineId) {
    if (!machineId) {
        return null;
    }
    if (machineId.length <= 16) {
        return machineId;
    }
    return `${machineId.slice(0, 8)}...${machineId.slice(-6)}`;
}
function normalizeLicenseCode(code) {
    return code.trim().toUpperCase();
}
function toLicenseStatus(record) {
    const verifyUrl = getVerifyUrl();
    const purchaseUrl = getPurchaseUrl();
    return {
        hasLicense: record !== null,
        isFullVersion: record?.plan === "full" && record.offline_valid === true,
        plan: record?.plan || "free",
        licenseCode: record?.license || null,
        activatedAt: record?.activated_at || null,
        machineId: record?.machine_id || null,
        machineSummary: summarizeMachineId(record?.machine_id || null),
        verifyUrl,
        purchaseUrl
    };
}
async function readLicenseFile(filePath) {
    try {
        const raw = await (0, promises_1.readFile)(filePath, 'utf-8');
        const parsed = JSON.parse(raw);
        if (typeof parsed.license !== "string" ||
            typeof parsed.plan !== "string" ||
            typeof parsed.machine_id !== "string" ||
            typeof parsed.activated_at !== "string") {
            return null;
        }
        return {
            license: normalizeLicenseCode(parsed.license),
            plan: parsed.plan.trim() || "free",
            machine_id: parsed.machine_id.trim(),
            activated_at: parsed.activated_at.trim(),
            offline_valid: parsed.offline_valid !== false,
            verify_url: typeof parsed.verify_url === "string" && parsed.verify_url.trim().length > 0
                ? parsed.verify_url.trim()
                : getVerifyUrl()
        };
    }
    catch {
        return null;
    }
}
async function getWritableLicensePath() {
    for (const filePath of LICENSE_FILE_PATHS) {
        try {
            await (0, promises_1.mkdir)((0, node_path_1.dirname)(filePath), { recursive: true });
            return filePath;
        }
        catch {
            continue;
        }
    }
    return null;
}
function getVerifyUrl() {
    return readConfiguredUrl(["SMS_LICENSE_VERIFY_URL", "OPENCLAW_LICENSE_VERIFY_URL"], DEFAULT_VERIFY_URL) || DEFAULT_VERIFY_URL;
}
function getPurchaseUrl() {
    return readConfiguredUrl(["SMS_PRODUCT_URL", "OPENCLAW_PRODUCT_URL"], DEFAULT_PURCHASE_URL);
}
async function saveLicense(record) {
    const filePath = await getWritableLicensePath();
    if (!filePath) {
        return null;
    }
    await (0, promises_1.writeFile)(filePath, JSON.stringify(record, null, 2), 'utf-8');
    return filePath;
}
async function loadLicense() {
    for (const filePath of LICENSE_FILE_PATHS) {
        const record = await readLicenseFile(filePath);
        if (record) {
            return record;
        }
    }
    return null;
}
async function getLicenseStatus() {
    return toLicenseStatus(await loadLicense());
}
function formatUnlockInstructions() {
    const purchaseUrl = getPurchaseUrl();
    return [
        "完整版购买方式：",
        purchaseUrl ? `1. 前往购买页面：${purchaseUrl}` : "1. 前往爱发电购买完整版",
        "2. 支付后会自动获得兑换码",
        "3. 回到这里输入：解锁 你的兑换码"
    ].join("\n");
}
function formatLicenseStatus(status) {
    if (!status.hasLicense) {
        return [
            "当前授权状态：免费版",
            "Plan：free",
            `验证地址：${status.verifyUrl}`,
            "如需解锁完整版，请输入：解锁"
        ].join("\n");
    }
    return [
        `当前授权状态：${status.isFullVersion ? "完整版" : "已授权但未解锁完整版"}`,
        `Plan：${status.plan}`,
        `兑换码：${status.licenseCode || "未知"}`,
        `激活时间：${status.activatedAt || "未知"}`,
        `机器摘要：${status.machineSummary || "未知"}`,
        `验证地址：${status.verifyUrl}`
    ].join("\n");
}
function getAccessibleSaveSlotCount(status) {
    return status.isFullVersion ? 5 : 1;
}
function isAdvancedGenerationEnabled(status) {
    return status.isFullVersion;
}
async function activateLicenseCode(code, machineId) {
    const normalizedCode = normalizeLicenseCode(code);
    if (!LICENSE_CODE_PATTERN.test(normalizedCode)) {
        const status = await getLicenseStatus();
        return {
            ok: false,
            message: "兑换码格式错误，请检查后重试。",
            status
        };
    }
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);
    try {
        const response = await fetch(getVerifyUrl(), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                code: normalizedCode,
                machine_id: machineId
            }),
            signal: controller.signal
        });
        const payload = await response.json();
        if (!response.ok || !payload.valid) {
            const status = await getLicenseStatus();
            return {
                ok: false,
                message: payload.valid === false && payload.error ? payload.error : "兑换码验证失败，请稍后重试。",
                status
            };
        }
        const record = {
            license: normalizedCode,
            plan: payload.plan || "full",
            machine_id: machineId,
            activated_at: payload.activated_at || new Date().toISOString(),
            offline_valid: true,
            verify_url: getVerifyUrl()
        };
        await saveLicense(record);
        return {
            ok: true,
            message: "完整版已激活。",
            status: toLicenseStatus(record)
        };
    }
    catch (error) {
        const status = await getLicenseStatus();
        const message = error instanceof Error && error.name === "AbortError"
            ? "验证服务超时，请稍后重试。"
            : "验证服务不可用，请检查网络后重试。";
        return {
            ok: false,
            message,
            status
        };
    }
    finally {
        clearTimeout(timeoutId);
    }
}
