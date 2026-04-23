import { getWalletAddress } from "./config.js";
import { coreAbi, getPublicRuntime, optionalNumber, optionalString, requireCoreAddress, requiredBigInt, requiredString, stringifyJson, toRecord, tupleField, } from "./shared.js";
import { prepareRequirementForTask, verifyRequirementHash, } from "./requirement.js";
function readApiConfig() {
    const url = process.env.MOLTX_API_URL?.trim();
    if (!url) {
        return undefined;
    }
    return {
        url: url.replace(/\/+$/, ""),
        apiKey: process.env.MOLTX_API_KEY?.trim(),
        jwt: process.env.MOLTX_API_JWT?.trim(),
    };
}
function requireApiConfig() {
    const config = readApiConfig();
    if (!config) {
        throw new Error("MOLTX_API_URL not set");
    }
    return config;
}
function buildApiHeaders(config, hasBody = false) {
    const headers = {};
    if (hasBody) {
        headers["Content-Type"] = "application/json";
    }
    if (config.apiKey) {
        headers.apikey = config.apiKey;
    }
    if (config.jwt) {
        headers.Authorization = `Bearer ${config.jwt}`;
    }
    else if (config.apiKey) {
        headers.Authorization = `Bearer ${config.apiKey}`;
    }
    return headers;
}
async function apiGet(viewName, query) {
    const config = requireApiConfig();
    const response = await fetch(`${config.url}/rest/v1/${viewName}?${query.toString()}`, {
        headers: buildApiHeaders(config),
    });
    if (!response.ok) {
        throw new Error(`api read failed: ${response.status} ${await response.text()}`);
    }
    return response.json();
}
async function apiRpc(functionName, payload) {
    const config = requireApiConfig();
    const response = await fetch(`${config.url}/rest/v1/rpc/${functionName}`, {
        method: "POST",
        headers: buildApiHeaders(config, true),
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error(`api rpc failed: ${response.status} ${await response.text()}`);
    }
    if (response.status === 204) {
        return null;
    }
    const text = await response.text();
    return text === "" ? null : JSON.parse(text);
}
function parseJsonLike(value, key) {
    if (value === undefined) {
        return undefined;
    }
    if (typeof value === "string") {
        const trimmed = value.trim();
        if (trimmed === "") {
            return undefined;
        }
        return JSON.parse(trimmed);
    }
    if (value === null || typeof value === "number" || typeof value === "boolean") {
        return value;
    }
    if (Array.isArray(value) || typeof value === "object") {
        return value;
    }
    throw new Error(`${key} must be valid JSON`);
}
function toIsoFromUnixSeconds(seconds) {
    return new Date(Number(seconds) * 1000).toISOString();
}
async function fetchOnchainRequirementHash(taskId) {
    const { config, publicClient } = getPublicRuntime();
    const task = await publicClient.readContract({
        address: requireCoreAddress(config),
        abi: coreAbi,
        functionName: "getTask",
        args: [BigInt(taskId)],
    });
    return requiredString({ requirementHash: tupleField(task, 16, "requirementHash") }, "requirementHash");
}
export async function maybeSyncTaskToApi(payload) {
    if (!readApiConfig()) {
        return {
            attempted: false,
            success: false,
            skippedReason: "MOLTX_API_URL not set",
        };
    }
    try {
        const prepared = prepareRequirementForTask(payload.requirementJson, payload.requirementHash);
        const onchainRequirementHash = payload.onchainRequirementHash ?? await fetchOnchainRequirementHash(payload.taskId);
        if (onchainRequirementHash.toLowerCase() !== prepared.requirementHash.toLowerCase()) {
            throw new Error("on-chain requirementHash does not match canonical requirementJson");
        }
        await apiRpc("rpc_create_task", {
            p_task_id: Number(payload.taskId),
            p_maker_address: payload.makerAddress.toLowerCase(),
            p_bounty_token: payload.bountyToken.toLowerCase(),
            p_bounty: payload.bounty,
            p_deposit: payload.deposit,
            p_mode: payload.mode,
            p_max_takers: payload.maxTakers,
            p_min_taker_level: payload.minTakerLevel,
            p_accept_deadline: payload.acceptDeadline,
            p_submit_deadline: payload.submitDeadline,
            p_requirement_hash: prepared.requirementHash,
            p_onchain_requirement_hash: onchainRequirementHash,
            p_requirement_json: prepared.requirementJson,
            p_delivery_private: payload.deliveryPrivate,
            p_category_id: payload.categoryId,
        });
        return { attempted: true, success: true, endpoint: "rpc_create_task" };
    }
    catch (error) {
        return {
            attempted: true,
            success: false,
            endpoint: "rpc_create_task",
            error: error instanceof Error ? error.message : "unknown api sync error",
        };
    }
}
export async function maybeSyncSubmissionToApi(payload) {
    if (!readApiConfig()) {
        return {
            attempted: false,
            success: false,
            skippedReason: "MOLTX_API_URL not set",
        };
    }
    try {
        await apiRpc("rpc_create_submission", {
            p_task_id: Number(payload.taskId),
            p_taker_address: payload.takerAddress.toLowerCase(),
            p_submit_time: payload.submitTime,
            p_delivery_ref: payload.deliveryRef,
            p_delivery_notes: payload.deliveryNotes,
            p_delivery_files: payload.deliveryFiles,
        });
        return { attempted: true, success: true, endpoint: "rpc_create_submission" };
    }
    catch (error) {
        return {
            attempted: true,
            success: false,
            endpoint: "rpc_create_submission",
            error: error instanceof Error ? error.message : "unknown api sync error",
        };
    }
}
export async function maybeSyncDisputeToApi(payload) {
    if (!readApiConfig()) {
        return {
            attempted: false,
            success: false,
            skippedReason: "MOLTX_API_URL not set",
        };
    }
    try {
        await apiRpc("rpc_raise_dispute", {
            p_task_id: Number(payload.taskId),
            p_taker_address: payload.takerAddress.toLowerCase(),
            p_maker_address: payload.makerAddress.toLowerCase(),
            p_evidence_ipfs_hash: payload.evidenceIpfsHash,
            p_commit_deadline: payload.commitDeadline,
            p_reveal_deadline: payload.revealDeadline,
            p_raised_at: payload.raisedAt,
            p_evidence_description: payload.evidenceDescription,
            p_evidence_files: payload.evidenceFiles,
        });
        return { attempted: true, success: true, endpoint: "rpc_raise_dispute" };
    }
    catch (error) {
        return {
            attempted: true,
            success: false,
            endpoint: "rpc_raise_dispute",
            error: error instanceof Error ? error.message : "unknown api sync error",
        };
    }
}
const list_active_tasks = async (args) => {
    const record = toRecord(args ?? {});
    const query = new URLSearchParams();
    query.set("select", "*");
    query.set("order", "created_at.desc");
    if (record.status !== undefined) {
        query.set("status", `eq.${requiredString(record, "status")}`);
    }
    if (record.maker !== undefined) {
        query.set("maker_address", `eq.${requiredString(record, "maker").toLowerCase()}`);
    }
    if (record.categoryId !== undefined) {
        query.set("category_id", `eq.${requiredString(record, "categoryId")}`);
    }
    if (record.limit !== undefined) {
        query.set("limit", String(optionalNumber(record, "limit")));
    }
    if (record.offset !== undefined) {
        query.set("offset", String(optionalNumber(record, "offset")));
    }
    return stringifyJson(await apiGet("active_tasks", query));
};
const get_task_details = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const query = new URLSearchParams();
    query.set("select", "*");
    query.set("task_id", `eq.${taskId.toString()}`);
    const rows = await apiGet("task_details", query);
    return stringifyJson(Array.isArray(rows) ? rows[0] ?? null : rows);
};
const list_disputes = async (args) => {
    const record = toRecord(args ?? {});
    const query = new URLSearchParams();
    query.set("select", "*");
    query.set("order", "raised_at.desc");
    if (record.taskId !== undefined) {
        query.set("task_id", `eq.${requiredBigInt(record, "taskId").toString()}`);
    }
    if (record.taker !== undefined) {
        query.set("taker_address", `eq.${requiredString(record, "taker").toLowerCase()}`);
    }
    if (record.maker !== undefined) {
        query.set("maker_address", `eq.${requiredString(record, "maker").toLowerCase()}`);
    }
    if (record.resolved !== undefined) {
        query.set("resolved_at", Boolean(record.resolved) ? "not.is.null" : "is.null");
    }
    if (record.limit !== undefined) {
        query.set("limit", String(optionalNumber(record, "limit")));
    }
    if (record.offset !== undefined) {
        query.set("offset", String(optionalNumber(record, "offset")));
    }
    return stringifyJson(await apiGet("dispute_overview", query));
};
const sync_task_to_api = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId").toString();
    if (record.requirementJson === undefined) {
        throw new Error("requirementJson must be provided");
    }
    const makerAddress = optionalString(record, "makerAddress") ?? getWalletAddress();
    const mode = requiredString(record, "mode");
    const prepared = prepareRequirementForTask(record.requirementJson, optionalString(record, "requirementHash"));
    const onchainRequirementHash = await fetchOnchainRequirementHash(taskId);
    return stringifyJson(await maybeSyncTaskToApi({
        taskId,
        makerAddress,
        bountyToken: requiredString(record, "bountyToken"),
        bounty: requiredString(record, "bounty"),
        deposit: optionalString(record, "deposit") ?? "0",
        mode: mode === "0" || mode.toUpperCase() === "SINGLE" ? "SINGLE" : "MULTI",
        maxTakers: Number(requiredBigInt(record, "maxTakers")),
        minTakerLevel: Number(requiredBigInt(record, "minTakerLevel")),
        acceptDeadline: toIsoFromUnixSeconds(requiredBigInt(record, "acceptDeadline")),
        submitDeadline: toIsoFromUnixSeconds(requiredBigInt(record, "submitDeadline")),
        requirementHash: prepared.requirementHash,
        requirementJson: prepared.requirementJson,
        onchainRequirementHash,
        deliveryPrivate: Boolean(record.deliveryPrivate),
        categoryId: record.categoryId === undefined ? undefined : Number(requiredBigInt(record, "categoryId")),
    }));
};
const verify_task_requirement = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { config, publicClient } = getPublicRuntime();
    const onchainTask = await publicClient.readContract({
        address: requireCoreAddress(config),
        abi: coreAbi,
        functionName: "getTask",
        args: [taskId],
    });
    const onchainRequirementHash = requiredString({ requirementHash: tupleField(onchainTask, 16, "requirementHash") }, "requirementHash");
    const query = new URLSearchParams();
    query.set("select", "*");
    query.set("task_id", `eq.${taskId.toString()}`);
    const rows = await apiGet("task_details", query);
    const taskDetails = Array.isArray(rows) ? rows[0] : undefined;
    if (!taskDetails) {
        return stringifyJson({
            match: false,
            onchainRequirementHash,
            reason: "task details not found in api",
        });
    }
    if (taskDetails.requirement_json === undefined || taskDetails.requirement_json === null) {
        return stringifyJson({
            match: false,
            onchainRequirementHash,
            reason: "task details missing requirement_json",
        });
    }
    return stringifyJson(verifyRequirementHash(onchainRequirementHash, taskDetails.requirement_json));
};
const sync_submission_to_api = async (args) => {
    const record = toRecord(args);
    return stringifyJson(await maybeSyncSubmissionToApi({
        taskId: requiredBigInt(record, "taskId").toString(),
        takerAddress: optionalString(record, "takerAddress") ?? getWalletAddress(),
        submitTime: requiredString(record, "submitTime"),
        deliveryRef: requiredString(record, "deliveryRef"),
        deliveryNotes: optionalString(record, "deliveryNotes"),
        deliveryFiles: parseJsonLike(record.deliveryFiles, "deliveryFiles"),
    }));
};
const sync_dispute_to_api = async (args) => {
    const record = toRecord(args);
    return stringifyJson(await maybeSyncDisputeToApi({
        taskId: requiredBigInt(record, "taskId").toString(),
        takerAddress: optionalString(record, "takerAddress") ?? getWalletAddress(),
        makerAddress: requiredString(record, "makerAddress"),
        evidenceIpfsHash: requiredString(record, "evidenceIpfsHash"),
        commitDeadline: requiredString(record, "commitDeadline"),
        revealDeadline: requiredString(record, "revealDeadline"),
        raisedAt: requiredString(record, "raisedAt"),
        evidenceDescription: optionalString(record, "evidenceDescription"),
        evidenceFiles: parseJsonLike(record.evidenceFiles, "evidenceFiles"),
    }));
};
export const apiTools = {
    get_task_details,
    list_active_tasks,
    list_disputes,
    sync_dispute_to_api,
    sync_submission_to_api,
    sync_task_to_api,
    verify_task_requirement,
};
