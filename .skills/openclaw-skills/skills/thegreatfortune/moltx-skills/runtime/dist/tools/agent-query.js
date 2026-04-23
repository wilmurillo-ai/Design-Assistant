import { readMakerTasks, readTakerTasks, readDisputes, readPredictionBets, readSyncState, } from "./agent-state.js";
const get_my_tasks = async (args) => {
    const { role = "all", status } = (args || {});
    const result = {
        syncState: readSyncState(),
    };
    if (role === "maker" || role === "all") {
        const makerState = readMakerTasks();
        let tasks = Object.values(makerState.tasks);
        if (status) {
            tasks = tasks.filter(t => t.status === status);
        }
        result.makerTasks = tasks;
    }
    if (role === "taker" || role === "all") {
        const takerState = readTakerTasks();
        let tasks = Object.values(takerState.tasks);
        if (status) {
            tasks = tasks.filter(t => t.status === status);
        }
        result.takerTasks = tasks;
    }
    return JSON.stringify(result, null, 2);
};
const get_my_disputes = async (args) => {
    const { status } = (args || {});
    const disputesState = readDisputes();
    let disputes = Object.values(disputesState.disputes);
    if (status) {
        disputes = disputes.filter(d => d.status === status);
    }
    return JSON.stringify({
        disputes,
        syncState: readSyncState(),
    }, null, 2);
};
const get_my_prediction_bets = async (args) => {
    const { status, claimable } = (args || {});
    const betsState = readPredictionBets();
    let bets = Object.values(betsState.bets);
    if (status) {
        bets = bets.filter(b => b.status === status);
    }
    if (claimable !== undefined) {
        bets = bets.filter(b => (b.status === "ACCEPTED") === claimable);
    }
    return JSON.stringify({
        bets,
        syncState: readSyncState(),
    }, null, 2);
};
const get_urgent_tasks = async () => {
    const makerState = readMakerTasks();
    const takerState = readTakerTasks();
    const now = Date.now();
    const urgentMakerTasks = [];
    const urgentTakerTasks = [];
    // Maker: tasks with challenge window ending soon or reclaim window reached
    for (const task of Object.values(makerState.tasks)) {
        if (task.status === "SUBMITTED") {
            for (const [takerAddr, takerState] of Object.entries(task.takers)) {
                if (takerState.submittedAt) {
                    const endsAt = new Date(takerState.submittedAt).getTime() + 24 * 3600 * 1000;
                    const hoursLeft = (endsAt - now) / (3600 * 1000);
                    if (hoursLeft > 0 && hoursLeft < 6) {
                        urgentMakerTasks.push({
                            taskId: task.taskId,
                            taker: takerAddr,
                            reason: "challenge_window",
                            hoursLeft: hoursLeft.toFixed(2),
                            challengeWindowEnds: new Date(endsAt).toISOString(),
                        });
                    }
                }
            }
        }
        if ((task.status === "ACCEPTED" || task.status === "OPEN") && task.submitDeadline) {
            const submitEndsAt = new Date(task.submitDeadline).getTime();
            const hoursLeft = (submitEndsAt - now) / (3600 * 1000);
            if (hoursLeft <= 0 && task.acceptedCount > 0 && task.submittedCount === 0) {
                urgentMakerTasks.push({
                    taskId: task.taskId,
                    reason: "reclaim_bounty_available",
                    submitDeadline: task.submitDeadline,
                });
            }
        }
    }
    // Taker: tasks with submit or dispute windows ending soon
    for (const task of Object.values(takerState.tasks)) {
        if ((task.status === "ACCEPTED" || task.status === "OPEN") && task.submitDeadline) {
            const endsAt = new Date(task.submitDeadline).getTime();
            const hoursLeft = (endsAt - now) / (3600 * 1000);
            if (hoursLeft > 0 && hoursLeft < 6) {
                urgentTakerTasks.push({
                    taskId: task.taskId,
                    reason: "submit_deadline",
                    hoursLeft: hoursLeft.toFixed(2),
                    submitDeadline: task.submitDeadline,
                });
            }
        }
        if (task.status === "REJECTED" && task.disputeDeadline) {
            const endsAt = new Date(task.disputeDeadline).getTime();
            const hoursLeft = (endsAt - now) / (3600 * 1000);
            if (hoursLeft > 0 && hoursLeft < 12) {
                urgentTakerTasks.push({
                    taskId: task.taskId,
                    reason: "dispute_window",
                    hoursLeft: hoursLeft.toFixed(2),
                    disputeWindowEnds: task.disputeDeadline,
                });
            }
        }
    }
    return JSON.stringify({
        urgentMakerTasks,
        urgentTakerTasks,
        message: urgentMakerTasks.length === 0 && urgentTakerTasks.length === 0
            ? "No urgent tasks"
            : "Action required soon!",
    }, null, 2);
};
export const agentQueryTools = {
    get_my_tasks,
    get_my_disputes,
    get_my_prediction_bets,
    get_urgent_tasks,
};
