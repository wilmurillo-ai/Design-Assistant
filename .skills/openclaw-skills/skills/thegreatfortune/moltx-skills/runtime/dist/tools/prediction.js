import { formatEther } from "viem";
import { bigintFromUnknown, coreAbi, getPublicRuntime, getWriteRuntime, parseValue, predictionAbi, requireCoreAddress, requirePredictionAddress, requiredAddress, requiredBigInt, requiredNumber, requiredString, stringifyJson, toRecord, } from "./shared.js";
import { getWalletAddress } from "./config.js";
const accept_prediction_task = async (args) => {
    const record = toRecord(args);
    const tier = requiredNumber(record, "tier");
    if (tier < 1 || tier > 10) {
        throw new Error("tier must be between 1 and 10");
    }
    const maxPriceInput = requiredString(record, "maxPrice");
    const { config, publicClient, walletClient, account } = getWriteRuntime();
    const coreAddress = requireCoreAddress(config);
    const predictionAddress = requirePredictionAddress(config);
    const roundId = await publicClient.readContract({
        address: predictionAddress,
        abi: predictionAbi,
        functionName: "getCurrentRound",
    });
    const currentPrice = await publicClient.readContract({
        address: predictionAddress,
        abi: predictionAbi,
        functionName: "getTierCurrentPrice",
        args: [roundId, tier],
    });
    const maxPrice = parseValue(maxPriceInput, 18, "ether");
    const hash = await walletClient.writeContract({
        address: coreAddress,
        abi: coreAbi,
        functionName: "acceptPredictionTask",
        args: [tier, maxPrice],
        value: bigintFromUnknown(currentPrice, "currentPrice"),
        account,
        chain: undefined,
    });
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    return stringifyJson({
        tool: "accept_prediction_task",
        contractFunction: "MoltXCore.acceptPredictionTask",
        roundId: bigintFromUnknown(roundId, "roundId"),
        tier,
        currentPrice,
        maxPrice,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const create_prediction_task = async () => {
    const { config, publicClient, walletClient, account } = getWriteRuntime();
    const hash = await walletClient.writeContract({
        address: requireCoreAddress(config),
        abi: coreAbi,
        functionName: "createPredictionTask",
        args: [],
        account,
        chain: undefined,
    });
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    return stringifyJson({
        tool: "create_prediction_task",
        contractFunction: "MoltXCore.createPredictionTask",
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const claim_prediction_reward = async (args) => {
    const roundId = requiredBigInt(toRecord(args), "roundId");
    const { config, publicClient, walletClient, account } = getWriteRuntime();
    const hash = await walletClient.writeContract({
        address: requireCoreAddress(config),
        abi: coreAbi,
        functionName: "claimPredictionReward",
        args: [roundId],
        account,
        chain: undefined,
    });
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    return stringifyJson({
        tool: "claim_prediction_reward",
        contractFunction: "MoltXCore.claimPredictionReward",
        roundId,
        txHash: hash,
        status: receipt.status,
        blockNumber: receipt.blockNumber,
    });
};
const get_current_prediction_round = async () => {
    const { config, publicClient } = getPublicRuntime();
    const predictionAddress = requirePredictionAddress(config);
    const [roundId, bettingWindow, tierCount] = await Promise.all([
        publicClient.readContract({
            address: predictionAddress,
            abi: predictionAbi,
            functionName: "getCurrentRound",
        }),
        publicClient.readContract({
            address: predictionAddress,
            abi: predictionAbi,
            functionName: "BETTING_WINDOW",
        }),
        publicClient.readContract({
            address: predictionAddress,
            abi: predictionAbi,
            functionName: "TIER_COUNT",
        }),
    ]);
    return stringifyJson({
        roundId: bigintFromUnknown(roundId, "roundId"),
        tierCount: bigintFromUnknown(tierCount, "tierCount"),
        bettingWindow: bigintFromUnknown(bettingWindow, "bettingWindow"),
    });
};
const get_prediction_round_info = async (args) => {
    const roundId = requiredBigInt(toRecord(args), "roundId");
    const { config, publicClient } = getPublicRuntime();
    const predictionAddress = requirePredictionAddress(config);
    const roundInfo = await publicClient.readContract({
        address: predictionAddress,
        abi: predictionAbi,
        functionName: "getRoundInfo",
        args: [roundId],
    });
    const [yesterdayOutput, actualOutput, tierCurrentPrices, tierShares, totalPot, winningTier, settled, rolledOver] = roundInfo;
    return stringifyJson({
        roundId: roundId.toString(),
        yesterdayOutput,
        actualOutput,
        tierCurrentPrices,
        tierShares,
        totalPot,
        winningTier,
        settled,
        rolledOver,
    });
};
const get_prediction_user_bet = async (args) => {
    const record = toRecord(args);
    const roundId = requiredBigInt(record, "roundId");
    const user = record.user ? requiredAddress(record, "user") : getWalletAddress();
    const { config, publicClient } = getPublicRuntime();
    const predictionAddress = requirePredictionAddress(config);
    const [shares, claimed] = await publicClient.readContract({
        address: predictionAddress,
        abi: predictionAbi,
        functionName: "getUserBet",
        args: [roundId, user],
    });
    return stringifyJson({
        roundId: roundId.toString(),
        user,
        shares,
        claimed,
    });
};
const get_prediction_tier_price = async (args) => {
    const record = toRecord(args);
    const roundId = requiredBigInt(record, "roundId");
    const tier = requiredNumber(record, "tier");
    if (tier < 1 || tier > 10) {
        throw new Error("tier must be between 1 and 10");
    }
    const { config, publicClient } = getPublicRuntime();
    const predictionAddress = requirePredictionAddress(config);
    const price = await publicClient.readContract({
        address: predictionAddress,
        abi: predictionAbi,
        functionName: "getTierCurrentPrice",
        args: [roundId, tier],
    });
    return stringifyJson({
        roundId: roundId.toString(),
        tier,
        price: bigintFromUnknown(price, "price"),
        priceFormattedEth: formatEther(bigintFromUnknown(price, "price")),
    });
};
const get_prediction_historical_rounds = async (args) => {
    const record = toRecord(args);
    const count = record.count === undefined ? 10 : requiredNumber(record, "count");
    const { config, publicClient } = getPublicRuntime();
    const predictionAddress = requirePredictionAddress(config);
    const currentRoundId = bigintFromUnknown(await publicClient.readContract({
        address: predictionAddress,
        abi: predictionAbi,
        functionName: "getCurrentRound",
    }), "currentRoundId");
    if (currentRoundId === 0n) {
        return stringifyJson({ currentRoundId, historicalRounds: [] });
    }
    const safeCount = Math.min(count, Number(currentRoundId));
    const start = currentRoundId - BigInt(safeCount) + 1n;
    const rounds = [];
    for (let roundId = start; roundId <= currentRoundId; roundId += 1n) {
        const roundInfo = await publicClient.readContract({
            address: predictionAddress,
            abi: predictionAbi,
            functionName: "getRoundInfo",
            args: [roundId],
        });
        rounds.push({
            roundId: roundId.toString(),
            yesterdayOutput: roundInfo[0],
            actualOutput: roundInfo[1],
            totalPot: roundInfo[4],
            winningTier: roundInfo[5],
            settled: roundInfo[6],
            rolledOver: roundInfo[7],
        });
    }
    return stringifyJson({
        currentRoundId,
        historicalRounds: rounds,
    });
};
export const predictionTools = {
    accept_prediction_task,
    claim_prediction_reward,
    create_prediction_task,
    get_current_prediction_round,
    get_prediction_historical_rounds,
    get_prediction_round_info,
    get_prediction_tier_price,
    get_prediction_user_bet,
};
