"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildOptionsText = buildOptionsText;
exports.buildLicenseBannerText = buildLicenseBannerText;
exports.buildRuntimeOverviewText = buildRuntimeOverviewText;
exports.createRuntimeFromSave = createRuntimeFromSave;
exports.toGameSave = toGameSave;
exports.createNewGameRuntime = createNewGameRuntime;
exports.resolvePlayerActionInput = resolvePlayerActionInput;
exports.executeTurn = executeTurn;
const kimi_client_1 = require("./kimi_client");
const prompt_assembler_1 = require("./prompt_assembler");
const world_generation_1 = require("./world_generation");
const timeline_builder_1 = require("./timeline_builder");
const world_state_utils_1 = require("./world_state_utils");
const license_service_1 = require("./license_service");
function buildTurnPrompt(assembler, runtime, licenseStatus) {
    const prompt = assembler.assemble(runtime.currentWorldState);
    const notes = [
        "",
        "=".repeat(50),
        "【本回合生成要求】",
        `- 叙事风格：${runtime.narrativeStyle}`,
        "- narrative 长度控制在 300 字左右，不要太长",
        "- 用语要通俗、顺滑、好读，少用过分古奥的句式和堆砌辞藻",
        "- 风格参考《庆余年》：聪明、利落、有人味，有画面也有推进感",
        "- 允许保留古代世界观，但表达要让现代读者一眼看懂",
        "- 不要只写气氛，要写清动作、反馈、人物反应、局势推进",
        "- 仍需严格输出结构化 JSON"
    ];
    if ((0, license_service_1.isAdvancedGenerationEnabled)(licenseStatus)) {
        notes.push("- 当前为完整版，请进一步增强细节密度、环境层次和情绪变化");
    }
    return {
        ...prompt,
        userMessage: `${prompt.userMessage}\n${notes.join("\n")}`,
        estimatedTokens: prompt.estimatedTokens + 160
    };
}
function buildAssemblerFromRuntime(genesisPrompt, runtime) {
    const assembler = (0, prompt_assembler_1.createPromptAssembler)(genesisPrompt);
    assembler.setCurrentTurnNumber(runtime.currentTurn);
    runtime.allTurnRecords.forEach(record => assembler.addTurnRecord(record));
    runtime.allEpisodeSummaries.forEach(summary => assembler.addEpisodeSummary(summary));
    runtime.allTimelineEvents.forEach(event => assembler.addTimelineEvent(event));
    return assembler;
}
async function generateApprovedTurnOutput(client, canonPrompt, prompt, currentWorldState) {
    let outputObj = null;
    for (let attempt = 1; attempt <= 3; attempt += 1) {
        outputObj = await (0, kimi_client_1.kimiChatJson)(client, prompt.systemPrompt, prompt.userMessage);
        if (!client.enableCanonGuardian) {
            return outputObj;
        }
        const canonResult = await (0, world_generation_1.runCanonGuardianCheck)(client, canonPrompt, currentWorldState, outputObj);
        if (canonResult.verdict !== "rejected") {
            return outputObj;
        }
        outputObj = null;
    }
    throw new Error("连续多次生成均被否决，已中止运行");
}
function recordTurnArtifacts(runtime, assembler, output) {
    const record = {
        turnNumber: runtime.currentTurn,
        timestamp: Date.now(),
        playerInput: runtime.currentWorldState.player_input,
        narrative: output.narrative,
        stateChanges: output.state_changes,
        selectedOption: runtime.currentSelectedOption
    };
    runtime.allTurnRecords.push(record);
    assembler.addTurnRecord(record);
    const timelineEvents = (0, timeline_builder_1.buildTimelineEventsFromTurn)(runtime.currentTurn, runtime.currentWorldState.player_input, runtime.currentWorldState, output);
    timelineEvents.forEach(event => assembler.addTimelineEvent(event));
    runtime.allTimelineEvents.push(...timelineEvents);
}
async function maybeGenerateSummary(client, episodePrompt, runtime, assembler) {
    if (runtime.currentTurn % 5 !== 0) {
        return null;
    }
    const last5 = runtime.allTurnRecords.slice(-5);
    const quests = runtime.currentWorldState.active_quests
        .filter(quest => quest.status === "active")
        .map(quest => quest.title);
    const summary = await (0, world_generation_1.generateEpisodeSummary)(client, episodePrompt, runtime.currentTurn, last5, runtime.previousSummary, quests);
    assembler.addEpisodeSummary(summary);
    runtime.allEpisodeSummaries.push(summary);
    runtime.previousSummary = summary.content;
    return summary.title;
}
function buildOptionsText(options) {
    return options
        .map((option, index) => `${index + 1}. ${option.description}${option.hint ? ` (${option.hint})` : ""}`)
        .join("\n");
}
function buildLicenseBannerText(status) {
    const versionLabel = status.isFullVersion ? "完整版" : "免费版";
    return `[授权] 当前为${versionLabel}，可用存档槽：${(0, license_service_1.getAccessibleSaveSlotCount)(status)}`;
}
function buildRuntimeOverviewText(runtime) {
    return [
        `【世界观】`,
        runtime.worldRequirement || "未记录世界观",
        "",
        "【叙事风格】",
        runtime.narrativeStyle,
        "",
        "【当前状态】",
        (0, world_state_utils_1.formatCurrentStateSummary)(runtime.currentWorldState),
        "",
        "【可选行动】",
        buildOptionsText(runtime.currentOptions)
    ].join("\n");
}
function createRuntimeFromSave(slotId, loadedSave, licenseStatus) {
    return {
        currentWorldState: loadedSave.worldState,
        allTurnRecords: loadedSave.allTurnRecords || [],
        allEpisodeSummaries: loadedSave.allEpisodeSummaries || [],
        allTimelineEvents: loadedSave.allTimelineEvents || [],
        previousSummary: loadedSave.previousSummary || "",
        currentOptions: (0, world_state_utils_1.ensureActionOptions)(loadedSave.currentOptions || []),
        currentTurn: loadedSave.currentTurn,
        playerName: loadedSave.playerName || "旅人",
        worldRequirement: loadedSave.worldRequirement || "未记录世界观",
        narrativeStyle: loadedSave.narrativeStyle || "通俗、利落，偏《庆余年》式叙事",
        currentSelectedOption: 0,
        currentSlotId: slotId,
        licenseStatus
    };
}
function toGameSave(runtime) {
    return {
        version: "2.0",
        savedAt: new Date().toISOString(),
        playerName: runtime.playerName,
        worldRequirement: runtime.worldRequirement,
        narrativeStyle: runtime.narrativeStyle,
        currentTurn: runtime.currentTurn,
        worldState: runtime.currentWorldState,
        allTurnRecords: runtime.allTurnRecords,
        allEpisodeSummaries: runtime.allEpisodeSummaries,
        allTimelineEvents: runtime.allTimelineEvents,
        previousSummary: runtime.previousSummary,
        currentOptions: runtime.currentOptions,
        saveSlot: runtime.currentSlotId
    };
}
async function createNewGameRuntime(client, slotId, playerName, worldRequirement, narrativeStyle, licenseStatus) {
    const initialWorld = await (0, world_generation_1.generateInitialWorld)(client, worldRequirement, playerName, narrativeStyle);
    const runtime = {
        currentWorldState: {
            ...initialWorld.world_state,
            player_input: ""
        },
        allTurnRecords: [],
        allEpisodeSummaries: [],
        allTimelineEvents: [],
        previousSummary: "",
        currentOptions: (0, world_state_utils_1.ensureActionOptions)(initialWorld.player_options),
        currentTurn: 1,
        playerName,
        worldRequirement,
        narrativeStyle,
        currentSelectedOption: 0,
        currentSlotId: slotId,
        licenseStatus
    };
    return {
        runtime,
        storyOverview: initialWorld.story_overview,
        openingNarrative: initialWorld.opening_narrative
    };
}
function resolvePlayerActionInput(rawInput, options) {
    const trimmed = rawInput.trim();
    const selected = Number(trimmed);
    if (Number.isFinite(selected) && selected >= 1 && selected <= options.length) {
        const selectedOption = selected - 1;
        if (selectedOption === options.length - 1) {
            return {
                kind: "needs_custom_action",
                message: "你选择了“自定义行动”。请直接回复你想做的具体动作，例如：我悄悄跟上那名黑衣人。"
            };
        }
        return {
            kind: "action",
            playerInput: options[selectedOption].description,
            selectedOption
        };
    }
    return {
        kind: "action",
        playerInput: trimmed,
        selectedOption: options.length - 1
    };
}
async function executeTurn(runtime, playerInput, selectedOption, client, prompts) {
    const assembler = buildAssemblerFromRuntime(prompts.genesisPrompt, runtime);
    runtime.currentWorldState.player_input = playerInput;
    runtime.currentSelectedOption = selectedOption;
    const prompt = buildTurnPrompt(assembler, runtime, runtime.licenseStatus);
    const outputObj = await generateApprovedTurnOutput(client, prompts.canonPrompt, prompt, runtime.currentWorldState);
    (0, world_state_utils_1.updateWorldState)(runtime.currentWorldState, outputObj);
    runtime.currentOptions = (0, world_state_utils_1.ensureActionOptions)(outputObj.player_options);
    recordTurnArtifacts(runtime, assembler, outputObj);
    const generatedSummaryTitle = await maybeGenerateSummary(client, prompts.episodePrompt, runtime, assembler);
    assembler.incrementTurn();
    runtime.currentTurn += 1;
    return {
        runtime,
        narrative: outputObj.narrative,
        stateSummary: (0, world_state_utils_1.formatCurrentStateSummary)(runtime.currentWorldState),
        optionsText: buildOptionsText(runtime.currentOptions),
        estimatedTokens: prompt.estimatedTokens,
        generatedSummaryTitle
    };
}
