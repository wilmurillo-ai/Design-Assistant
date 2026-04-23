import { decodeEventLog, formatUnits, maxUint256, } from "viem";
import { addressFromUnknown, bigintFromUnknown, coreAbi, getPublicRuntime, getWriteRuntime, modeLabel, numberFromUnknown, optionalAddress, optionalHex32, optionalString, parseValue, requiredAddress, requiredAddressArray, requiredBigInt, requiredBoolean, requiredNumber, requiredString, requireCoreAddress, statusLabel, stringifyJson, toRecord, tupleField, } from "./shared.js";
import { getRuntimeConfig, getWalletAddress, setRuntimeConfig } from "./config.js";
import { hashTextKeccak } from "./hash.js";
import { maybeSyncDisputeToApi, maybeSyncSubmissionToApi, maybeSyncTaskToApi, } from "./api.js";
import { prepareRequirementForTask, } from "./requirement.js";
const erc20Abi = [
    {
        type: "function",
        stateMutability: "view",
        name: "decimals",
        inputs: [],
        outputs: [{ name: "", type: "uint8" }],
    },
    {
        type: "function",
        stateMutability: "view",
        name: "symbol",
        inputs: [],
        outputs: [{ name: "", type: "string" }],
    },
    {
        type: "function",
        stateMutability: "view",
        name: "balanceOf",
        inputs: [{ name: "owner", type: "address" }],
        outputs: [{ name: "", type: "uint256" }],
    },
    {
        type: "function",
        stateMutability: "view",
        name: "allowance",
        inputs: [
            { name: "owner", type: "address" },
            { name: "spender", type: "address" },
        ],
        outputs: [{ name: "", type: "uint256" }],
    },
    {
        type: "function",
        stateMutability: "nonpayable",
        name: "approve",
        inputs: [
            { name: "spender", type: "address" },
            { name: "amount", type: "uint256" },
        ],
        outputs: [{ name: "", type: "bool" }],
    },
];
function parseTaskStruct(value) {
    return {
        maker: addressFromUnknown(tupleField(value, 0, "maker"), "maker"),
        bountyToken: addressFromUnknown(tupleField(value, 1, "bountyToken"), "bountyToken"),
        mode: numberFromUnknown(tupleField(value, 2, "mode"), "mode"),
        status: numberFromUnknown(tupleField(value, 3, "status"), "status"),
        bounty: bigintFromUnknown(tupleField(value, 4, "bounty"), "bounty"),
        deposit: bigintFromUnknown(tupleField(value, 5, "deposit"), "deposit"),
        maxTakers: numberFromUnknown(tupleField(value, 6, "maxTakers"), "maxTakers"),
        acceptedCount: numberFromUnknown(tupleField(value, 7, "acceptedCount"), "acceptedCount"),
        submittedCount: numberFromUnknown(tupleField(value, 8, "submittedCount"), "submittedCount"),
        categoryId: numberFromUnknown(tupleField(value, 9, "categoryId"), "categoryId"),
        minTakerLevel: numberFromUnknown(tupleField(value, 10, "minTakerLevel"), "minTakerLevel"),
        feesSettled: Boolean(tupleField(value, 11, "feesSettled")),
        acceptDeadline: bigintFromUnknown(tupleField(value, 12, "acceptDeadline"), "acceptDeadline"),
        submitDeadline: bigintFromUnknown(tupleField(value, 13, "submitDeadline"), "submitDeadline"),
        lastSubmitTime: bigintFromUnknown(tupleField(value, 14, "lastSubmitTime"), "lastSubmitTime"),
        lastAcceptTime: bigintFromUnknown(tupleField(value, 15, "lastAcceptTime"), "lastAcceptTime"),
        requirementHash: tupleField(value, 16, "requirementHash"),
        deliveryPrivate: Boolean(tupleField(value, 17, "deliveryPrivate")),
    };
}
function parseTakerStateStruct(value) {
    return {
        taker: addressFromUnknown(tupleField(value, 0, "taker"), "taker"),
        acceptTime: bigintFromUnknown(tupleField(value, 1, "acceptTime"), "acceptTime"),
        submitTime: bigintFromUnknown(tupleField(value, 2, "submitTime"), "submitTime"),
        rejectTime: bigintFromUnknown(tupleField(value, 3, "rejectTime"), "rejectTime"),
        deliveryRef: tupleField(value, 4, "deliveryRef"),
        hasSubmitted: Boolean(tupleField(value, 5, "hasSubmitted")),
        isRejected: Boolean(tupleField(value, 6, "isRejected")),
        hasClaimed: Boolean(tupleField(value, 7, "hasClaimed")),
        inDispute: Boolean(tupleField(value, 8, "inDispute")),
    };
}
function normalizeTask(taskId, task) {
    return {
        taskId: taskId.toString(),
        maker: task.maker,
        bountyToken: task.bountyToken,
        mode: modeLabel(task.mode),
        modeValue: task.mode,
        status: statusLabel(task.status),
        statusValue: task.status,
        bounty: task.bounty,
        deposit: task.deposit,
        maxTakers: task.maxTakers,
        acceptedCount: task.acceptedCount,
        submittedCount: task.submittedCount,
        categoryId: task.categoryId,
        minTakerLevel: task.minTakerLevel,
        feesSettled: task.feesSettled,
        acceptDeadline: task.acceptDeadline,
        submitDeadline: task.submitDeadline,
        lastSubmitTime: task.lastSubmitTime,
        lastAcceptTime: task.lastAcceptTime,
        requirementHash: task.requirementHash,
        deliveryPrivate: task.deliveryPrivate,
    };
}
function normalizeTakerState(taskId, taker, state, extras) {
    return {
        taskId: taskId.toString(),
        taker,
        acceptTime: state.acceptTime,
        submitTime: state.submitTime,
        rejectTime: state.rejectTime,
        deliveryRef: state.deliveryRef,
        hasSubmitted: state.hasSubmitted,
        isRejected: state.isRejected,
        hasClaimed: state.hasClaimed,
        inDisputeFlag: state.inDispute,
        activeDispute: extras?.activeDispute ?? false,
        rejection: extras?.rejection ?? state.isRejected,
        disputeOutcome: extras?.disputeOutcome ?? 0,
        disputeRaiseUsdcEquiv: extras?.disputeRaiseUsdcEquiv ?? 0n,
    };
}
async function readTokenDecimals(publicClient, token) {
    const decimals = await publicClient.readContract({
        address: token,
        abi: erc20Abi,
        functionName: "decimals",
    });
    return Number(decimals);
}
async function readTokenSymbol(publicClient, token) {
    return publicClient.readContract({
        address: token,
        abi: erc20Abi,
        functionName: "symbol",
    });
}
async function readTask(publicClient, coreAddress, taskId) {
    const result = await publicClient.readContract({
        address: coreAddress,
        abi: coreAbi,
        functionName: "getTask",
        args: [taskId],
    });
    return parseTaskStruct(result);
}
async function readTakerState(publicClient, coreAddress, taskId, taker) {
    const result = await publicClient.readContract({
        address: coreAddress,
        abi: coreAbi,
        functionName: "getTakerState",
        args: [taskId, taker],
    });
    return parseTakerStateStruct(result);
}
async function getLatestTimestamp(publicClient) {
    const block = await publicClient.getBlock({ blockTag: "latest" });
    return block.timestamp;
}
async function getChallengeWindow(publicClient, coreAddress) {
    const result = await publicClient.readContract({
        address: coreAddress,
        abi: coreAbi,
        functionName: "CHALLENGE_WINDOW",
    });
    return bigintFromUnknown(result, "CHALLENGE_WINDOW");
}
async function getDisputeWindow(publicClient, coreAddress) {
    const result = await publicClient.readContract({
        address: coreAddress,
        abi: coreAbi,
        functionName: "DISPUTE_WINDOW",
    });
    return bigintFromUnknown(result, "DISPUTE_WINDOW");
}
async function sendCoreTransaction(functionName, args, value) {
    const { config, publicClient, walletClient, account } = getWriteRuntime();
    const coreAddress = requireCoreAddress(config);
    const hash = await walletClient.writeContract({
        address: coreAddress,
        abi: coreAbi,
        functionName,
        args,
        value,
        account,
        chain: undefined,
    });
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    return { hash, receipt };
}
async function resolveDefaultOwner(record, config) {
    return optionalAddress(record, "owner") ?? config.walletAddress ?? getWalletAddress();
}
function parseJsonField(record, key) {
    const value = record[key];
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
    if (typeof value === "object") {
        return value;
    }
    throw new Error(`${key} must be valid JSON`);
}
function extractTaskIdFromReceipt(receipt) {
    for (const log of receipt.logs) {
        try {
            const decoded = decodeEventLog({
                abi: coreAbi,
                data: log.data,
                topics: log.topics,
            });
            if (decoded.eventName === "TaskCreated") {
                return bigintFromUnknown(decoded.args.taskId, "taskId");
            }
        }
        catch {
            continue;
        }
    }
    throw new Error("TaskCreated event not found in receipt");
}
const set_runtime_config = async (args) => {
    const record = toRecord(args);
    const patch = {};
    if (record.rpcUrl !== undefined) {
        patch.rpcUrl = requiredString(record, "rpcUrl");
    }
    if (record.walletAddress !== undefined) {
        patch.walletAddress = requiredAddress(record, "walletAddress");
    }
    return stringifyJson(setRuntimeConfig(patch));
};
const get_runtime_config = async () => stringifyJson(getRuntimeConfig());
const get_token_info = async (args) => {
    const record = toRecord(args);
    const token = requiredAddress(record, "token");
    const { publicClient } = getPublicRuntime();
    const [decimals, symbol] = await Promise.all([
        readTokenDecimals(publicClient, token),
        readTokenSymbol(publicClient, token),
    ]);
    return stringifyJson({ token, symbol, decimals });
};
const get_token_balance = async (args) => {
    const record = toRecord(args);
    const token = requiredAddress(record, "token");
    const { config, publicClient } = getPublicRuntime();
    const owner = await resolveDefaultOwner(record, config);
    const [symbol, decimals, balance] = await Promise.all([
        readTokenSymbol(publicClient, token),
        readTokenDecimals(publicClient, token),
        publicClient.readContract({
            address: token,
            abi: erc20Abi,
            functionName: "balanceOf",
            args: [owner],
        }),
    ]);
    return stringifyJson({
        token,
        owner,
        symbol,
        decimals,
        balance,
        formatted: formatUnits(balance, decimals),
    });
};
const get_token_allowance = async (args) => {
    const record = toRecord(args);
    const token = requiredAddress(record, "token");
    const { config, publicClient } = getPublicRuntime();
    const owner = await resolveDefaultOwner(record, config);
    const spender = optionalAddress(record, "spender") ?? requireCoreAddress(config);
    const [symbol, decimals, allowance] = await Promise.all([
        readTokenSymbol(publicClient, token),
        readTokenDecimals(publicClient, token),
        publicClient.readContract({
            address: token,
            abi: erc20Abi,
            functionName: "allowance",
            args: [owner, spender],
        }),
    ]);
    return stringifyJson({
        token,
        owner,
        spender,
        symbol,
        decimals,
        allowance,
        formatted: formatUnits(allowance, decimals),
    });
};
const approve_token = async (args) => {
    const record = toRecord(args);
    const token = requiredAddress(record, "token");
    const { config, publicClient, walletClient, account } = getWriteRuntime();
    const spender = optionalAddress(record, "spender") ?? requireCoreAddress(config);
    const decimals = await readTokenDecimals(publicClient, token);
    const amountInput = optionalString(record, "amount");
    const amount = amountInput ? parseValue(amountInput, decimals) : maxUint256;
    const hash = await walletClient.writeContract({
        address: token,
        abi: erc20Abi,
        functionName: "approve",
        args: [spender, amount],
        account,
        chain: undefined,
    });
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    return stringifyJson({
        tool: "approve_token",
        contractFunction: "approve",
        token,
        spender,
        amount,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const get_task = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { config, publicClient } = getPublicRuntime();
    const task = await readTask(publicClient, requireCoreAddress(config), taskId);
    return stringifyJson(normalizeTask(taskId, task));
};
const get_task_takers = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { config, publicClient } = getPublicRuntime();
    const takers = await publicClient.readContract({
        address: requireCoreAddress(config),
        abi: coreAbi,
        functionName: "getTaskTakers",
        args: [taskId],
    });
    return stringifyJson({ taskId: taskId.toString(), takers });
};
const get_taker_state = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const taker = requiredAddress(record, "taker");
    const { config, publicClient } = getPublicRuntime();
    const coreAddress = requireCoreAddress(config);
    const [state, activeDispute, rejection, disputeOutcome, disputeRaiseUsdcEquiv] = await Promise.all([
        readTakerState(publicClient, coreAddress, taskId, taker),
        publicClient.readContract({ address: coreAddress, abi: coreAbi, functionName: "activeDispute", args: [taskId, taker] }),
        publicClient.readContract({ address: coreAddress, abi: coreAbi, functionName: "rejections", args: [taskId, taker] }),
        publicClient.readContract({ address: coreAddress, abi: coreAbi, functionName: "disputeOutcomes", args: [taskId, taker] }),
        publicClient.readContract({ address: coreAddress, abi: coreAbi, functionName: "disputeRaiseUsdcEquiv", args: [taskId, taker] }),
    ]);
    return stringifyJson(normalizeTakerState(taskId, taker, state, {
        activeDispute: Boolean(activeDispute),
        rejection: Boolean(rejection),
        disputeOutcome: Number(disputeOutcome),
        disputeRaiseUsdcEquiv: bigintFromUnknown(disputeRaiseUsdcEquiv, "disputeRaiseUsdcEquiv"),
    }));
};
const get_whitelisted_tokens = async () => {
    const { config, publicClient } = getPublicRuntime();
    const coreAddress = requireCoreAddress(config);
    const tokens = await publicClient.readContract({
        address: coreAddress,
        abi: coreAbi,
        functionName: "getWhitelistedTokens",
    });
    const entries = await Promise.all(tokens.map(async (token) => ({
        token,
        fee: await publicClient.readContract({
            address: coreAddress,
            abi: coreAbi,
            functionName: "tokenPoolFee",
            args: [token],
        }),
    })));
    return stringifyJson({ count: entries.length, tokens: entries });
};
const is_task_expired = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { config, publicClient } = getPublicRuntime();
    const expired = await publicClient.readContract({
        address: requireCoreAddress(config),
        abi: coreAbi,
        functionName: "isTaskExpired",
        args: [taskId],
    });
    return stringifyJson({ taskId: taskId.toString(), expired: Boolean(expired) });
};
const get_current_emission_rate = async () => {
    const { config, publicClient } = getPublicRuntime();
    const rate = await publicClient.readContract({
        address: requireCoreAddress(config),
        abi: coreAbi,
        functionName: "getCurrentEmissionRate",
    });
    return stringifyJson({ emissionRate: bigintFromUnknown(rate, "emissionRate") });
};
const get_task_decision_plan = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const taker = optionalAddress(record, "taker") ?? getWalletAddress();
    const { config, publicClient } = getPublicRuntime();
    const coreAddress = requireCoreAddress(config);
    const [task, takerState, activeDispute, challengeWindow, disputeWindow, now] = await Promise.all([
        readTask(publicClient, coreAddress, taskId),
        readTakerState(publicClient, coreAddress, taskId, taker),
        publicClient.readContract({ address: coreAddress, abi: coreAbi, functionName: "activeDispute", args: [taskId, taker] }),
        getChallengeWindow(publicClient, coreAddress),
        getDisputeWindow(publicClient, coreAddress),
        getLatestTimestamp(publicClient),
    ]);
    const challengeDeadline = takerState.submitTime > 0n ? takerState.submitTime + challengeWindow : 0n;
    const disputeDeadline = takerState.rejectTime > 0n ? takerState.rejectTime + disputeWindow : 0n;
    const canAccept = task.status === 0 && now <= task.acceptDeadline;
    const canCancel = takerState.acceptTime > 0n && !takerState.hasSubmitted && now <= takerState.acceptTime + 30n * 60n;
    const canSubmit = takerState.acceptTime > 0n && !takerState.hasSubmitted && now <= task.submitDeadline;
    const canClaimFunds = takerState.acceptTime > 0n && !takerState.hasClaimed && ((takerState.hasSubmitted && !takerState.isRejected && now > challengeDeadline) ||
        (takerState.isRejected && !Boolean(activeDispute) && now > disputeDeadline) ||
        (task.status === 7 || task.status === 8 || task.status === 5 || task.status === 9) ||
        (!takerState.hasSubmitted && now > task.submitDeadline));
    const canReject = task.maker === (config.walletAddress ?? getWalletAddress()) && takerState.hasSubmitted && !takerState.isRejected && now <= challengeDeadline;
    const canRaiseDispute = takerState.isRejected && !Boolean(activeDispute) && now <= disputeDeadline;
    const canReclaimBounty = task.maker === (config.walletAddress ?? getWalletAddress()) && ((task.status === 0) ||
        (!takerState.hasSubmitted && now > task.submitDeadline) ||
        (takerState.isRejected && !Boolean(activeDispute) && now > disputeDeadline));
    let branch = "inactive";
    if (canAccept)
        branch = "open_accept";
    else if (canCancel)
        branch = "cancel_window";
    else if (canSubmit)
        branch = "accepted_submit";
    else if (takerState.hasSubmitted && !takerState.isRejected && !takerState.hasClaimed)
        branch = "submitted_challenge_window";
    else if (canClaimFunds && takerState.hasSubmitted && !takerState.isRejected)
        branch = "claim_optimistic";
    else if (canRaiseDispute)
        branch = "rejected_dispute_window";
    else if (canClaimFunds && takerState.isRejected)
        branch = "claim_post_rejection";
    else if (canReclaimBounty)
        branch = "maker_reclaim";
    else if (!takerState.hasSubmitted && takerState.acceptTime > 0n && now > task.submitDeadline)
        branch = "timeout_unsubmitted";
    return stringifyJson({
        task: normalizeTask(taskId, task),
        takerState: normalizeTakerState(taskId, taker, takerState, {
            activeDispute: Boolean(activeDispute),
        }),
        timing: {
            now,
            challengeWindow,
            disputeWindow,
            challengeDeadline,
            disputeDeadline,
        },
        branch,
        actions: {
            canAccept,
            canCancel,
            canSubmit,
            canClaimFunds,
            canReject,
            canRaiseDispute,
            canReclaimBounty,
        },
    });
};
const create_task = async (args) => {
    const record = toRecord(args);
    const bountyToken = requiredAddress(record, "bountyToken");
    const { publicClient } = getPublicRuntime();
    const decimals = await readTokenDecimals(publicClient, bountyToken);
    const bounty = parseValue(requiredString(record, "bounty"), decimals);
    const deposit = parseValue(optionalString(record, "deposit") ?? "0", decimals);
    if (record.requirementJson === undefined) {
        throw new Error("requirementJson must be provided");
    }
    const preparedRequirement = prepareRequirementForTask(record.requirementJson, optionalHex32(record, "requirementHash"));
    const { hash, receipt } = await sendCoreTransaction("createTask", [
        bountyToken,
        bounty,
        deposit,
        requiredNumber(record, "mode"),
        requiredNumber(record, "maxTakers"),
        requiredNumber(record, "categoryId"),
        requiredNumber(record, "minTakerLevel"),
        requiredBigInt(record, "acceptDeadline"),
        requiredBigInt(record, "submitDeadline"),
        preparedRequirement.requirementHash,
        requiredBoolean(record, "deliveryPrivate"),
    ]);
    const taskId = extractTaskIdFromReceipt(receipt);
    const onchainTask = await readTask(publicClient, requireCoreAddress(getRuntimeConfig()), taskId);
    if (onchainTask.requirementHash.toLowerCase() !== preparedRequirement.requirementHash.toLowerCase()) {
        throw new Error("on-chain requirementHash does not match canonical requirementJson after createTask");
    }
    const makerAddress = getWalletAddress();
    const apiSync = await maybeSyncTaskToApi({
        taskId: taskId.toString(),
        makerAddress,
        bountyToken,
        bounty: bounty.toString(),
        deposit: deposit.toString(),
        mode: requiredNumber(record, "mode") === 0 ? "SINGLE" : "MULTI",
        maxTakers: requiredNumber(record, "maxTakers"),
        minTakerLevel: requiredNumber(record, "minTakerLevel"),
        acceptDeadline: new Date(Number(requiredBigInt(record, "acceptDeadline")) * 1000).toISOString(),
        submitDeadline: new Date(Number(requiredBigInt(record, "submitDeadline")) * 1000).toISOString(),
        requirementHash: preparedRequirement.requirementHash,
        requirementJson: preparedRequirement.requirementJson,
        onchainRequirementHash: onchainTask.requirementHash,
        deliveryPrivate: requiredBoolean(record, "deliveryPrivate"),
        categoryId: record.categoryId === undefined ? undefined : requiredNumber(record, "categoryId"),
    });
    return stringifyJson({
        tool: "create_task",
        contractFunction: "createTask",
        taskId,
        bountyToken,
        bounty,
        deposit,
        requirementHash: preparedRequirement.requirementHash,
        canonicalRequirementJson: preparedRequirement.canonicalRequirementJson,
        apiSync,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const accept_task = async (args) => {
    const taskId = requiredBigInt(toRecord(args), "taskId");
    const { hash, receipt } = await sendCoreTransaction("acceptTask", [taskId]);
    return stringifyJson({ tool: "accept_task", contractFunction: "acceptTask", taskId, txHash: hash, status: receipt.status, blockNumber: receipt.blockNumber });
};
const cancel_task = async (args) => {
    const taskId = requiredBigInt(toRecord(args), "taskId");
    const { hash, receipt } = await sendCoreTransaction("cancelTask", [taskId]);
    return stringifyJson({ tool: "cancel_task", contractFunction: "cancelTask", taskId, txHash: hash, status: receipt.status, blockNumber: receipt.blockNumber });
};
const submit_completion = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { publicClient } = getPublicRuntime();
    const deliveryRef = optionalHex32(record, "deliveryRef") ?? await hashTextKeccak({
        text: requiredString(record, "deliveryText"),
    });
    const { hash, receipt } = await sendCoreTransaction("submitCompletion", [taskId, deliveryRef]);
    const block = await publicClient.getBlock({ blockNumber: receipt.blockNumber });
    const apiSync = await maybeSyncSubmissionToApi({
        taskId: taskId.toString(),
        takerAddress: getWalletAddress(),
        submitTime: new Date(Number(block.timestamp) * 1000).toISOString(),
        deliveryRef,
        deliveryNotes: optionalString(record, "deliveryNotes"),
        deliveryFiles: parseJsonField(record, "deliveryFiles"),
    });
    return stringifyJson({
        tool: "submit_completion",
        contractFunction: "submitCompletion",
        taskId,
        deliveryRef,
        apiSync,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const claim_funds = async (args) => {
    const taskId = requiredBigInt(toRecord(args), "taskId");
    const { hash, receipt } = await sendCoreTransaction("claimFunds", [taskId]);
    return stringifyJson({
        tool: "claim_funds",
        contractFunction: "claimFunds",
        taskId,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const reject_submission_single = async (args) => {
    const taskId = requiredBigInt(toRecord(args), "taskId");
    const { hash, receipt } = await sendCoreTransaction("rejectSubmission", [taskId]);
    return stringifyJson({ tool: "reject_submission_single", contractFunction: "rejectSubmission(uint256)", taskId, txHash: hash, status: receipt.status, blockNumber: receipt.blockNumber });
};
const reject_submission_multi = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const takers = requiredAddressArray(record, "takers");
    const { hash, receipt } = await sendCoreTransaction("rejectSubmission", [taskId, takers]);
    return stringifyJson({
        tool: "reject_submission_multi",
        contractFunction: "rejectSubmission(uint256,address[])",
        taskId,
        takers,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const raise_dispute = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { config, publicClient } = getPublicRuntime();
    const evidenceIPFSHash = optionalHex32(record, "evidenceIPFSHash") ?? await hashTextKeccak({
        text: requiredString(record, "evidenceText"),
    });
    const { hash, receipt } = await sendCoreTransaction("raiseDispute", [taskId, evidenceIPFSHash]);
    const block = await publicClient.getBlock({ blockNumber: receipt.blockNumber });
    const task = await readTask(publicClient, requireCoreAddress(config), taskId);
    const raisedAt = new Date(Number(block.timestamp) * 1000).toISOString();
    const commitDeadline = new Date((Number(block.timestamp) + 24 * 60 * 60) * 1000).toISOString();
    const revealDeadline = new Date((Number(block.timestamp) + 48 * 60 * 60) * 1000).toISOString();
    const apiSync = await maybeSyncDisputeToApi({
        taskId: taskId.toString(),
        takerAddress: getWalletAddress(),
        makerAddress: task.maker,
        evidenceIpfsHash: evidenceIPFSHash,
        commitDeadline,
        revealDeadline,
        raisedAt,
        evidenceDescription: optionalString(record, "evidenceDescription") ?? optionalString(record, "evidenceText"),
        evidenceFiles: parseJsonField(record, "evidenceFiles"),
    });
    return stringifyJson({
        tool: "raise_dispute",
        contractFunction: "raiseDispute",
        taskId,
        evidenceIPFSHash,
        apiSync,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const reclaim_bounty = async (args) => {
    const taskId = requiredBigInt(toRecord(args), "taskId");
    const { hash, receipt } = await sendCoreTransaction("reclaimBounty", [taskId]);
    return stringifyJson({ tool: "reclaim_bounty", contractFunction: "reclaimBounty", taskId, txHash: hash, status: receipt.status, blockNumber: receipt.blockNumber });
};
const set_council = async (args) => {
    const address = requiredAddress(toRecord(args), "address");
    const { hash, receipt } = await sendCoreTransaction("setCouncil", [address]);
    return stringifyJson({ tool: "set_council", contractFunction: "setCouncil", address, txHash: hash, status: receipt.status, blockNumber: receipt.blockNumber });
};
const set_liquidity = async (args) => {
    const address = requiredAddress(toRecord(args), "address");
    const { hash, receipt } = await sendCoreTransaction("setLiquidity", [address]);
    return stringifyJson({ tool: "set_liquidity", contractFunction: "setLiquidity", address, txHash: hash, status: receipt.status, blockNumber: receipt.blockNumber });
};
const add_whitelist_token = async (args) => {
    const record = toRecord(args);
    const token = requiredAddress(record, "token");
    const fee = requiredBigInt(record, "fee");
    const { hash, receipt } = await sendCoreTransaction("addWhitelistToken", [token, fee]);
    return stringifyJson({
        tool: "add_whitelist_token",
        contractFunction: "addWhitelistToken",
        token,
        fee,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
export const coreTools = {
    accept_task,
    add_whitelist_token,
    approve_token,
    cancel_task,
    claim_funds,
    create_task,
    get_current_emission_rate,
    get_runtime_config,
    get_task,
    get_task_decision_plan,
    get_task_takers,
    get_taker_state,
    get_token_allowance,
    get_token_balance,
    get_token_info,
    get_whitelisted_tokens,
    is_task_expired,
    raise_dispute,
    reclaim_bounty,
    reject_submission_multi,
    reject_submission_single,
    set_council,
    set_liquidity,
    set_runtime_config,
    submit_completion,
};
