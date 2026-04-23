import { decodeEventLog } from "viem";
import { bigintFromUnknown, councilAbi, getPublicRuntime, getWriteRuntime, optionalHex32, requireCouncilAddress, requiredAddress, requiredBigInt, requiredBoolean, requiredHex32, stringifyJson, toRecord, tupleField, } from "./shared.js";
function normalizeDispute(taskId, value) {
    return {
        taskId: taskId.toString(),
        maker: requiredAddress({ maker: tupleField(value, 0, "maker") }, "maker"),
        taker: requiredAddress({ taker: tupleField(value, 1, "taker") }, "taker"),
        bountyUsdcEquiv: bigintFromUnknown(tupleField(value, 2, "bountyUsdcEquiv"), "bountyUsdcEquiv"),
        evidenceHash: requiredHex32({ evidenceHash: tupleField(value, 3, "evidenceHash") }, "evidenceHash"),
        commitDeadline: bigintFromUnknown(tupleField(value, 4, "commitDeadline"), "commitDeadline"),
        revealDeadline: bigintFromUnknown(tupleField(value, 5, "revealDeadline"), "revealDeadline"),
        commitCount: Number(tupleField(value, 6, "commitCount")),
        selectedCount: Number(tupleField(value, 7, "selectedCount")),
        revealCount: Number(tupleField(value, 8, "revealCount")),
        commitFinalized: Boolean(tupleField(value, 9, "commitFinalized")),
        revealFinalized: Boolean(tupleField(value, 10, "revealFinalized")),
        resolved: Boolean(tupleField(value, 11, "resolved")),
        commitFinalizer: requiredAddress({ commitFinalizer: tupleField(value, 12, "commitFinalizer") }, "commitFinalizer"),
        revealFinalizer: requiredAddress({ revealFinalizer: tupleField(value, 13, "revealFinalizer") }, "revealFinalizer"),
    };
}
function normalizeVote(taskId, arbiter, value) {
    return {
        taskId: taskId.toString(),
        arbiter,
        commitHash: requiredHex32({ commitHash: tupleField(value, 0, "commitHash") }, "commitHash"),
        hasCommitted: Boolean(tupleField(value, 1, "hasCommitted")),
        isSelected: Boolean(tupleField(value, 2, "isSelected")),
        hasRevealed: Boolean(tupleField(value, 3, "hasRevealed")),
        verdict: Boolean(tupleField(value, 4, "verdict")),
    };
}
async function writeCouncil(functionName, args) {
    const { config, publicClient, walletClient, account } = getWriteRuntime();
    const councilAddress = requireCouncilAddress(config);
    const hash = await walletClient.writeContract({
        address: councilAddress,
        abi: councilAbi,
        functionName,
        args,
        account,
        chain: undefined,
    });
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    return { hash, receipt };
}
const get_dispute_status = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { config, publicClient } = getPublicRuntime();
    const councilAddress = requireCouncilAddress(config);
    const dispute = await publicClient.readContract({
        address: councilAddress,
        abi: councilAbi,
        functionName: "disputes",
        args: [taskId],
    });
    return stringifyJson(normalizeDispute(taskId, dispute));
};
const get_jury_status = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { config, publicClient } = getPublicRuntime();
    const councilAddress = requireCouncilAddress(config);
    const [committers, selectedJurors, dispute] = await Promise.all([
        publicClient.readContract({
            address: councilAddress,
            abi: councilAbi,
            functionName: "getCommitters",
            args: [taskId],
        }),
        publicClient.readContract({
            address: councilAddress,
            abi: councilAbi,
            functionName: "getSelectedJurors",
            args: [taskId],
        }),
        publicClient.readContract({
            address: councilAddress,
            abi: councilAbi,
            functionName: "disputes",
            args: [taskId],
        }),
    ]);
    return stringifyJson({
        taskId: taskId.toString(),
        committers,
        selectedJurors,
        dispute: normalizeDispute(taskId, dispute),
    });
};
const get_commit_window_status = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { config, publicClient } = getPublicRuntime();
    const councilAddress = requireCouncilAddress(config);
    const [dispute, now] = await Promise.all([
        publicClient.readContract({
            address: councilAddress,
            abi: councilAbi,
            functionName: "disputes",
            args: [taskId],
        }),
        publicClient.getBlock({ blockTag: "latest" }),
    ]);
    const normalized = normalizeDispute(taskId, dispute);
    return stringifyJson({
        taskId: taskId.toString(),
        now: now.timestamp,
        commitDeadline: normalized.commitDeadline,
        commitCount: normalized.commitCount,
        commitFinalized: normalized.commitFinalized,
        stillOpen: now.timestamp <= normalized.commitDeadline && !normalized.commitFinalized,
    });
};
const get_reveal_window_status = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { config, publicClient } = getPublicRuntime();
    const councilAddress = requireCouncilAddress(config);
    const [dispute, now] = await Promise.all([
        publicClient.readContract({
            address: councilAddress,
            abi: councilAbi,
            functionName: "disputes",
            args: [taskId],
        }),
        publicClient.getBlock({ blockTag: "latest" }),
    ]);
    const normalized = normalizeDispute(taskId, dispute);
    return stringifyJson({
        taskId: taskId.toString(),
        now: now.timestamp,
        revealDeadline: normalized.revealDeadline,
        revealCount: normalized.revealCount,
        revealFinalized: normalized.revealFinalized,
        stillOpen: now.timestamp <= normalized.revealDeadline && !normalized.revealFinalized,
    });
};
const get_vote_status = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const arbiter = requiredAddress(record, "arbiter");
    const { config, publicClient } = getPublicRuntime();
    const councilAddress = requireCouncilAddress(config);
    const vote = await publicClient.readContract({
        address: councilAddress,
        abi: councilAbi,
        functionName: "getVote",
        args: [taskId, arbiter],
    });
    return stringifyJson(normalizeVote(taskId, arbiter, vote));
};
const commit_vote = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const voteHash = requiredHex32(record, "voteHash");
    const { hash, receipt } = await writeCouncil("commitVote", [taskId, voteHash]);
    return stringifyJson({
        tool: "commit_vote",
        contractFunction: "commitVote",
        taskId,
        voteHash,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const reveal_vote = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const verdict = requiredBoolean(record, "verdict");
    const salt = optionalHex32(record, "salt") ?? requiredHex32(record, "salt");
    const { hash, receipt } = await writeCouncil("revealVote", [taskId, verdict, salt]);
    return stringifyJson({
        tool: "reveal_vote",
        contractFunction: "revealVote",
        taskId,
        verdict,
        salt,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const finalize_commit = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { hash, receipt } = await writeCouncil("finalizeCommit", [taskId]);
    return stringifyJson({
        tool: "finalize_commit",
        contractFunction: "finalizeCommit",
        taskId,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const finalize_reveal = async (args) => {
    const record = toRecord(args);
    const taskId = requiredBigInt(record, "taskId");
    const { hash, receipt } = await writeCouncil("finalizeReveal", [taskId]);
    const disputeResolved = receipt.logs.find((log) => {
        try {
            const decoded = decodeEventLog({
                abi: councilAbi,
                data: log.data,
                topics: log.topics,
            });
            return decoded.eventName === "DisputeResolved" || decoded.eventName === "DisputeUnresolved";
        }
        catch {
            return false;
        }
    });
    return stringifyJson({
        tool: "finalize_reveal",
        contractFunction: "finalizeReveal",
        taskId,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
        disputeResolved: Boolean(disputeResolved),
    });
};
export const councilTools = {
    commit_vote,
    finalize_commit,
    finalize_reveal,
    get_commit_window_status,
    get_dispute_status,
    get_jury_status,
    get_reveal_window_status,
    get_vote_status,
    reveal_vote,
};
