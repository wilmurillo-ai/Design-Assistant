import {
  EpisodeSummary,
  GenesisOutput,
  PlayerOption,
  TimelineEvent,
  TurnRecord,
  WorldStateInput
} from './data_models';
import { KimiClientConfig, kimiChatJson } from './kimi_client';
import { createPromptAssembler } from './prompt_assembler';
import { GameSave } from './save_store';
import {
  generateEpisodeSummary,
  generateInitialWorld,
  runCanonGuardianCheck
} from './world_generation';
import { buildTimelineEventsFromTurn } from './timeline_builder';
import {
  ensureActionOptions,
  formatCurrentStateSummary,
  updateWorldState
} from './world_state_utils';
import { LicenseStatus, getAccessibleSaveSlotCount, isAdvancedGenerationEnabled } from './license_service';

export type GameRuntimeState = {
  currentWorldState: WorldStateInput;
  allTurnRecords: TurnRecord[];
  allEpisodeSummaries: EpisodeSummary[];
  allTimelineEvents: TimelineEvent[];
  previousSummary: string;
  currentOptions: PlayerOption[];
  currentTurn: number;
  playerName: string;
  worldRequirement: string;
  narrativeStyle: string;
  currentSelectedOption: number;
  currentSlotId: string;
  licenseStatus: LicenseStatus;
};

export type EnginePrompts = {
  genesisPrompt: string;
  canonPrompt: string;
  episodePrompt: string;
};

export type NewGameResult = {
  runtime: GameRuntimeState;
  storyOverview: string;
  openingNarrative: string;
};

export type TurnExecutionResult = {
  runtime: GameRuntimeState;
  narrative: string;
  stateSummary: string;
  optionsText: string;
  estimatedTokens: number;
  generatedSummaryTitle: string | null;
};

export type ActionResolution =
  | {
      kind: "action";
      playerInput: string;
      selectedOption: number;
    }
  | {
      kind: "needs_custom_action";
      message: string;
    };

function buildTurnPrompt(
  assembler: ReturnType<typeof createPromptAssembler>,
  runtime: GameRuntimeState,
  licenseStatus: LicenseStatus
): ReturnType<ReturnType<typeof createPromptAssembler>["assemble"]> {
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

  if (isAdvancedGenerationEnabled(licenseStatus)) {
    notes.push("- 当前为完整版，请进一步增强细节密度、环境层次和情绪变化");
  }

  return {
    ...prompt,
    userMessage: `${prompt.userMessage}\n${notes.join("\n")}`,
    estimatedTokens: prompt.estimatedTokens + 160
  };
}

function buildAssemblerFromRuntime(
  genesisPrompt: string,
  runtime: GameRuntimeState
): ReturnType<typeof createPromptAssembler> {
  const assembler = createPromptAssembler(genesisPrompt);
  assembler.setCurrentTurnNumber(runtime.currentTurn);
  runtime.allTurnRecords.forEach(record => assembler.addTurnRecord(record));
  runtime.allEpisodeSummaries.forEach(summary => assembler.addEpisodeSummary(summary));
  runtime.allTimelineEvents.forEach(event => assembler.addTimelineEvent(event));
  return assembler;
}

async function generateApprovedTurnOutput(
  client: KimiClientConfig,
  canonPrompt: string,
  prompt: ReturnType<ReturnType<typeof createPromptAssembler>["assemble"]>,
  currentWorldState: WorldStateInput
): Promise<GenesisOutput> {
  let outputObj: GenesisOutput | null = null;

  for (let attempt = 1; attempt <= 3; attempt += 1) {
    outputObj = await kimiChatJson<GenesisOutput>(client, prompt.systemPrompt, prompt.userMessage);

    if (!client.enableCanonGuardian) {
      return outputObj;
    }

    const canonResult = await runCanonGuardianCheck(client, canonPrompt, currentWorldState, outputObj);
    if (canonResult.verdict !== "rejected") {
      return outputObj;
    }

    outputObj = null;
  }

  throw new Error("连续多次生成均被否决，已中止运行");
}

function recordTurnArtifacts(
  runtime: GameRuntimeState,
  assembler: ReturnType<typeof createPromptAssembler>,
  output: GenesisOutput
): void {
  const record: TurnRecord = {
    turnNumber: runtime.currentTurn,
    timestamp: Date.now(),
    playerInput: runtime.currentWorldState.player_input,
    narrative: output.narrative,
    stateChanges: output.state_changes,
    selectedOption: runtime.currentSelectedOption
  };

  runtime.allTurnRecords.push(record);
  assembler.addTurnRecord(record);

  const timelineEvents = buildTimelineEventsFromTurn(
    runtime.currentTurn,
    runtime.currentWorldState.player_input,
    runtime.currentWorldState,
    output
  );
  timelineEvents.forEach(event => assembler.addTimelineEvent(event));
  runtime.allTimelineEvents.push(...timelineEvents);
}

async function maybeGenerateSummary(
  client: KimiClientConfig,
  episodePrompt: string,
  runtime: GameRuntimeState,
  assembler: ReturnType<typeof createPromptAssembler>
): Promise<string | null> {
  if (runtime.currentTurn % 5 !== 0) {
    return null;
  }

  const last5 = runtime.allTurnRecords.slice(-5);
  const quests = runtime.currentWorldState.active_quests
    .filter(quest => quest.status === "active")
    .map(quest => quest.title);
  const summary = await generateEpisodeSummary(
    client,
    episodePrompt,
    runtime.currentTurn,
    last5,
    runtime.previousSummary,
    quests
  );

  assembler.addEpisodeSummary(summary);
  runtime.allEpisodeSummaries.push(summary);
  runtime.previousSummary = summary.content;
  return summary.title;
}

export function buildOptionsText(options: PlayerOption[]): string {
  return options
    .map((option, index) => `${index + 1}. ${option.description}${option.hint ? ` (${option.hint})` : ""}`)
    .join("\n");
}

export function buildLicenseBannerText(status: LicenseStatus): string {
  const versionLabel = status.isFullVersion ? "完整版" : "免费版";
  return `[授权] 当前为${versionLabel}，可用存档槽：${getAccessibleSaveSlotCount(status)}`;
}

export function buildRuntimeOverviewText(runtime: GameRuntimeState): string {
  return [
    `【世界观】`,
    runtime.worldRequirement || "未记录世界观",
    "",
    "【叙事风格】",
    runtime.narrativeStyle,
    "",
    "【当前状态】",
    formatCurrentStateSummary(runtime.currentWorldState),
    "",
    "【可选行动】",
    buildOptionsText(runtime.currentOptions)
  ].join("\n");
}

export function createRuntimeFromSave(
  slotId: string,
  loadedSave: GameSave,
  licenseStatus: LicenseStatus
): GameRuntimeState {
  return {
    currentWorldState: loadedSave.worldState,
    allTurnRecords: loadedSave.allTurnRecords || [],
    allEpisodeSummaries: loadedSave.allEpisodeSummaries || [],
    allTimelineEvents: loadedSave.allTimelineEvents || [],
    previousSummary: loadedSave.previousSummary || "",
    currentOptions: ensureActionOptions(loadedSave.currentOptions || []),
    currentTurn: loadedSave.currentTurn,
    playerName: loadedSave.playerName || "旅人",
    worldRequirement: loadedSave.worldRequirement || "未记录世界观",
    narrativeStyle: loadedSave.narrativeStyle || "通俗、利落，偏《庆余年》式叙事",
    currentSelectedOption: 0,
    currentSlotId: slotId,
    licenseStatus
  };
}

export function toGameSave(runtime: GameRuntimeState): GameSave {
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

export async function createNewGameRuntime(
  client: KimiClientConfig,
  slotId: string,
  playerName: string,
  worldRequirement: string,
  narrativeStyle: string,
  licenseStatus: LicenseStatus
): Promise<NewGameResult> {
  const initialWorld = await generateInitialWorld(client, worldRequirement, playerName, narrativeStyle);
  const runtime: GameRuntimeState = {
    currentWorldState: {
      ...initialWorld.world_state,
      player_input: ""
    },
    allTurnRecords: [],
    allEpisodeSummaries: [],
    allTimelineEvents: [],
    previousSummary: "",
    currentOptions: ensureActionOptions(initialWorld.player_options),
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

export function resolvePlayerActionInput(rawInput: string, options: PlayerOption[]): ActionResolution {
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

export async function executeTurn(
  runtime: GameRuntimeState,
  playerInput: string,
  selectedOption: number,
  client: KimiClientConfig,
  prompts: EnginePrompts
): Promise<TurnExecutionResult> {
  const assembler = buildAssemblerFromRuntime(prompts.genesisPrompt, runtime);
  runtime.currentWorldState.player_input = playerInput;
  runtime.currentSelectedOption = selectedOption;

  const prompt = buildTurnPrompt(assembler, runtime, runtime.licenseStatus);
  const outputObj = await generateApprovedTurnOutput(
    client,
    prompts.canonPrompt,
    prompt,
    runtime.currentWorldState
  );

  updateWorldState(runtime.currentWorldState, outputObj);
  runtime.currentOptions = ensureActionOptions(outputObj.player_options);
  recordTurnArtifacts(runtime, assembler, outputObj);
  const generatedSummaryTitle = await maybeGenerateSummary(
    client,
    prompts.episodePrompt,
    runtime,
    assembler
  );

  assembler.incrementTurn();
  runtime.currentTurn += 1;

  return {
    runtime,
    narrative: outputObj.narrative,
    stateSummary: formatCurrentStateSummary(runtime.currentWorldState),
    optionsText: buildOptionsText(runtime.currentOptions),
    estimatedTokens: prompt.estimatedTokens,
    generatedSummaryTitle
  };
}
