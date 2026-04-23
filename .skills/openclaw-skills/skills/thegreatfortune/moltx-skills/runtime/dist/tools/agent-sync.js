import { decodeEventLog } from "viem";
import { coreAbi, getPublicRuntime, requireCoreAddress, stringifyJson, } from "./shared.js";
import { addOrUpdateDispute, addOrUpdateMakerTask, addOrUpdatePredictionBet, addOrUpdateTakerTask, getMakerTask, getTakerTask, isEventProcessed, markEventProcessed, readSyncState, resetAllAgentState, updateCoreSyncBlock, updatePredictionSyncBlock, } from "./agent-state.js";
import { getWalletAddress } from "./config.js";
function isoFromTs(ts) {
    if (ts === undefined) {
        return undefined;
    }
    return new Date(Number(ts) * 1000).toISOString();
}
const sync_agent_state = async (args) => {
    const { fromBlock } = (args ?? {});
    const walletAddress = getWalletAddress().toLowerCase();
    const { config, publicClient } = getPublicRuntime();
    const syncState = readSyncState();
    const currentBlock = await publicClient.getBlockNumber();
    const startBlock = fromBlock === "auto" || fromBlock === undefined
        ? (syncState.core.lastSyncBlock === "0" ? currentBlock - 1000n : BigInt(syncState.core.lastSyncBlock) + 1n)
        : BigInt(fromBlock);
    const logs = await publicClient.getLogs({
        address: requireCoreAddress(config),
        fromBlock: startBlock,
        toBlock: "latest",
    });
    let processedEvents = 0;
    let maxBlock = startBlock;
    for (const log of logs) {
        if (log.transactionHash && isEventProcessed(log.transactionHash)) {
            continue;
        }
        try {
            const decoded = decodeEventLog({
                abi: coreAbi,
                data: log.data,
                topics: log.topics,
            });
            processCoreEvent(decoded.eventName, decoded.args, walletAddress, log.blockNumber?.toString() ?? "0");
            if (log.transactionHash) {
                markEventProcessed(log.transactionHash);
            }
            processedEvents += 1;
            if (log.blockNumber && log.blockNumber > maxBlock) {
                maxBlock = log.blockNumber;
            }
        }
        catch {
            continue;
        }
    }
    updateCoreSyncBlock(maxBlock.toString(), walletAddress);
    updatePredictionSyncBlock(maxBlock.toString(), walletAddress);
    return stringifyJson({
        success: true,
        walletAddress,
        fromBlock: startBlock,
        toBlock: maxBlock,
        processedEvents,
    });
};
function processCoreEvent(eventName, args, walletAddress, blockNumber) {
    switch (eventName) {
        case "TaskCreated":
            handleTaskCreated(args, walletAddress, blockNumber);
            break;
        case "TaskAccepted":
            handleTaskAccepted(args, walletAddress, blockNumber);
            break;
        case "TaskSubmitted":
            handleTaskSubmitted(args, walletAddress, blockNumber);
            break;
        case "SubmissionRejected":
            handleSubmissionRejected(args, walletAddress, blockNumber);
            break;
        case "DisputeRaised":
            handleDisputeRaised(args, walletAddress, blockNumber);
            break;
        case "DisputeVerdictRecorded":
            handleDisputeResolved(args, blockNumber, "VERDICT_RECORDED");
            break;
        case "DisputeOutcomeRecorded":
            handleDisputeResolved(args, blockNumber, "UNRESOLVED");
            break;
        case "BountyReclaimed":
            handleBountyReclaimed(args, walletAddress, blockNumber);
            break;
        case "PredictionTaskAccepted":
            handlePredictionAccepted(args, walletAddress, blockNumber);
            break;
        case "PredictionRewardClaimed":
            handlePredictionClaimed(args, walletAddress, blockNumber);
            break;
        default:
            break;
    }
}
function handleTaskCreated(args, walletAddress, blockNumber) {
    const maker = String(args.maker).toLowerCase();
    if (maker !== walletAddress) {
        return;
    }
    const task = {
        taskId: String(args.taskId),
        mode: Number(args.mode) === 0 ? "SINGLE" : "MULTI",
        status: "OPEN",
        bountyToken: String(args.bountyToken),
        bounty: String(args.bounty),
        deposit: String(args.deposit),
        acceptedCount: 0,
        submittedCount: 0,
        acceptDeadline: isoFromTs(args.acceptDeadline) ?? "",
        submitDeadline: isoFromTs(args.submitDeadline) ?? "",
        takers: {},
        lastUpdatedBlock: blockNumber,
    };
    addOrUpdateMakerTask(task);
}
function handleTaskAccepted(args, walletAddress, blockNumber) {
    const taskId = String(args.taskId);
    const taker = String(args.taker).toLowerCase();
    const makerTask = getMakerTask(taskId);
    if (makerTask) {
        makerTask.status = "ACCEPTED";
        makerTask.acceptedCount += 1;
        makerTask.takers[taker] = {
            ...(makerTask.takers[taker] ?? { status: "ACCEPTED" }),
            acceptedAt: isoFromTs(args.acceptTime),
            status: "ACCEPTED",
        };
        makerTask.lastUpdatedBlock = blockNumber;
        addOrUpdateMakerTask(makerTask);
    }
    if (taker === walletAddress) {
        const takerTask = {
            taskId,
            maker: makerTask ? String(makerTask.taskId) : "",
            mode: makerTask?.mode ?? "UNKNOWN",
            status: "ACCEPTED",
            bountyToken: makerTask?.bountyToken ?? "",
            bounty: makerTask?.bounty ?? "0",
            deposit: makerTask?.deposit ?? "0",
            acceptedAt: isoFromTs(args.acceptTime),
            lastUpdatedBlock: blockNumber,
        };
        addOrUpdateTakerTask(takerTask);
    }
}
function handleTaskSubmitted(args, walletAddress, blockNumber) {
    const taskId = String(args.taskId);
    const taker = String(args.taker).toLowerCase();
    const makerTask = getMakerTask(taskId);
    if (makerTask) {
        makerTask.status = "SUBMITTED";
        makerTask.submittedCount += 1;
        makerTask.takers[taker] = {
            ...(makerTask.takers[taker] ?? { status: "SUBMITTED" }),
            submittedAt: isoFromTs(args.submitTime),
            deliveryRef: String(args.deliveryRef),
            status: "SUBMITTED",
        };
        makerTask.lastUpdatedBlock = blockNumber;
        addOrUpdateMakerTask(makerTask);
    }
    if (taker === walletAddress) {
        const takerTask = getTakerTask(taskId);
        addOrUpdateTakerTask({
            ...(takerTask ?? {
                taskId,
                maker: "",
                mode: "UNKNOWN",
                bountyToken: "",
                bounty: "0",
                deposit: "0",
            }),
            status: "SUBMITTED",
            submittedAt: isoFromTs(args.submitTime),
            deliveryRef: String(args.deliveryRef),
            lastUpdatedBlock: blockNumber,
        });
    }
}
function handleSubmissionRejected(args, walletAddress, blockNumber) {
    const taskId = String(args.taskId);
    const taker = String(args.taker).toLowerCase();
    const rejectedAt = isoFromTs(args.rejectTime);
    const makerTask = getMakerTask(taskId);
    if (makerTask?.takers[taker]) {
        makerTask.takers[taker].status = "REJECTED";
        makerTask.takers[taker].rejectedAt = rejectedAt;
        makerTask.lastUpdatedBlock = blockNumber;
        addOrUpdateMakerTask(makerTask);
    }
    if (taker === walletAddress) {
        const takerTask = getTakerTask(taskId);
        if (takerTask) {
            takerTask.status = "REJECTED";
            takerTask.rejectedAt = rejectedAt;
            takerTask.lastUpdatedBlock = blockNumber;
            addOrUpdateTakerTask(takerTask);
        }
    }
}
function handleDisputeRaised(args, walletAddress, blockNumber) {
    const dispute = {
        taskId: String(args.taskId),
        maker: "",
        taker: String(args.taker),
        status: "RAISED",
        commitDeadline: isoFromTs(args.deadline),
        lastUpdatedBlock: blockNumber,
    };
    addOrUpdateDispute(dispute);
    const takerTask = getTakerTask(dispute.taskId);
    if (takerTask && dispute.taker.toLowerCase() === walletAddress) {
        takerTask.status = "DISPUTED";
        takerTask.disputeDeadline = isoFromTs(args.deadline);
        takerTask.lastUpdatedBlock = blockNumber;
        addOrUpdateTakerTask(takerTask);
    }
}
function handleDisputeResolved(args, blockNumber, status) {
    addOrUpdateDispute({
        taskId: String(args.taskId),
        maker: "",
        taker: String(args.taker),
        status,
        takerWon: typeof args.takerWon === "boolean" ? args.takerWon : undefined,
        lastUpdatedBlock: blockNumber,
    });
}
function handleBountyReclaimed(args, walletAddress, blockNumber) {
    if (String(args.maker).toLowerCase() !== walletAddress) {
        return;
    }
    const makerTask = getMakerTask(String(args.taskId));
    if (makerTask) {
        makerTask.status = "COMPLETED_MAKER";
        makerTask.lastUpdatedBlock = blockNumber;
        addOrUpdateMakerTask(makerTask);
    }
}
function handlePredictionAccepted(args, walletAddress, blockNumber) {
    if (String(args.user).toLowerCase() !== walletAddress) {
        return;
    }
    const bet = {
        roundId: String(args.roundId),
        tier: Number(args.tier),
        shares: String(args.shares),
        status: "ACCEPTED",
        acceptedAt: new Date().toISOString(),
        lastUpdatedBlock: blockNumber,
    };
    addOrUpdatePredictionBet(bet);
}
function handlePredictionClaimed(args, walletAddress, blockNumber) {
    if (String(args.user).toLowerCase() !== walletAddress) {
        return;
    }
    const bet = {
        roundId: String(args.roundId),
        tier: 0,
        shares: "0",
        status: "CLAIMED",
        claimedAt: new Date().toISOString(),
        lastUpdatedBlock: blockNumber,
    };
    addOrUpdatePredictionBet(bet);
}
const reset_agent_state = async () => {
    resetAllAgentState();
    return stringifyJson({ success: true });
};
export const agentSyncTools = {
    reset_agent_state,
    sync_agent_state,
};
