// ============================================================
// 使用示例 - AI造物主系统
// ============================================================

import {
  WorldStateInput,
  GenesisOutput,
  PlayerOption,
  EpisodeSummary,
  TurnRecord,
  TimelineEvent
} from './data_models';

import { createInterface } from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';

import { createPromptAssembler, CanonViolationError } from './prompt_assembler';
import { createMemoryAssembler } from './memory_assembler';
import {
  chooseSaveSlot,
  displayActionOptions,
  promptPlayerName,
  promptTurnInput,
  promptWorldRequirement,
  TurnInputResult
} from './cli_helpers';
import { GameSave, saveGame } from './save_store';
import {
  getKimiClientConfig,
  KimiClientConfig,
  kimiChatJson,
  loadGenesisPrompt,
  loadPromptFile
} from './kimi_client';
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
import { getMachineIdentity } from './device_identity';
import {
  activateLicenseCode,
  formatLicenseStatus,
  formatUnlockInstructions,
  getAccessibleSaveSlotCount,
  getLicenseStatus,
  isAdvancedGenerationEnabled,
  LicenseStatus
} from './license_service';

// ============================================================
// 示例1：基本世界状态
// ============================================================

export const exampleWorldState: WorldStateInput = {
  world_context: {
    current_location: "mountain-path",
    time: "黄昏",
    weather: "微风，薄雾",
    atmosphere: "神秘、寂静"
  },
  player: {
    name: "云游子",
    cultivation_level: "筑基初期",
    reputation: {
      "qingcheng-sect": 15,
      "demonic-cult": -30
    },
    active_effects: ["轻微内伤"],
    inventory_summary: ["青锋剑", "疗伤丹x3"]
  },
  location_state: {
    id: "mountain-path",
    name: "山腰小径",
    description: "蜿蜒的山间小路，两旁竹林茂密",
    connected_locations: ["village-entrance", "abandoned-temple"],
    present_npcs: [],
    discovered_secrets: ["路边石碑有古怪符文"],
    environmental_status: "竹叶沙沙，远处传来钟声"
  },
  active_npcs: [],
  active_quests: [
    {
      id: "quest-missing-disciple",
      title: "失踪的弟子",
      status: "active",
      objective: "在山中寻找青城派失踪的弟子"
    }
  ],
  world_memory: {
    recent_events: [
      "第1回合：玩家从村口出发，向山中进发",
      "第2回合：发现路边石碑，上面刻有古怪符文"
    ],
    plot_summary: "云游子受青城派委托，寻找失踪的弟子，已深入山中",
    major_events: [
      "青城派与魔教近日冲突不断"
    ]
  },
  player_input: "循着钟声方向前进，查看是否有线索"
};

// ============================================================
// 示例2：Genesis Engine 预期输出
// ============================================================

export const exampleGenesisOutput: GenesisOutput = {
  narrative: "暮色四合，古刹钟声悠悠荡开。你推开斑驳的山门，一尊断首的佛像静默相对。香炉余烬尚温，似有人刚离去。墙角蛛网间，一柄断剑斜插，剑穗上系着的玉佩泛着幽光。",
  atmosphere_shift: "从宁静转为神秘紧张",
  state_changes: {
    new_locations: [
      {
        id: "abandoned-temple",
        name: "破败古刹",
        description: "山腰上的废弃寺庙，佛像断首，香火已绝多年",
        connected_to: ["mountain-path"],
        secrets: ["佛像底座有暗格", "断剑是某门派信物"],
        first_visit_narrative: "古刹年久失修，却透着一股说不出的诡异"
      }
    ],
    new_items: [
      {
        id: "broken-sword-jade",
        name: "断剑玉佩",
        type: "misc",
        rarity: "uncommon",
        description: "一柄断剑，剑穗系着刻有\"凌\"字的玉佩",
        properties: { clue_to: "ling-family" },
        obtained_from: "abandoned-temple"
      }
    ],
    new_npcs: [
      {
        id: "mysterious-wanderer",
        name: "神秘行者",
        description: "身披斗篷的陌生人，在寺庙外徘徊",
        motivation: "寻找某样东西",
        initial_attitude: 0,
        is_hostile: false,
        can_trade: true,
        combat_strength: "strong"
      }
    ],
    world_events: [
      {
        event_type: "discovered",
        description: "发现破败古刹",
        importance: "minor"
      }
    ]
  },
  player_options: [
    {
      type: "investigate",
      description: "查看佛像底座",
      hint: "可能需要细心观察"
    },
    {
      type: "investigate",
      description: "取下断剑细查",
      hint: "可能有危险"
    },
    {
      type: "dialogue",
      description: "与神秘行者搭话"
    },
    {
      type: "movement",
      description: "退出古刹，继续上山"
    }
  ],
  gm_notes: {
    hidden_clues: [
      "佛像底座暗格中有青城派信物",
      "神秘行者其实是魔教探子"
    ],
    foreshadowing: [
      "\"凌\"字暗示与凌家有关",
      "古刹曾是某个门派的据点"
    ],
    npc_intentions: {
      "mysterious-wanderer": "监视是否有青城派弟子出现"
    },
    suggested_future_events: [
      "神秘行者可能暴露身份",
      "暗格中的信物指向失踪弟子"
    ]
  }
};

// ============================================================
// 示例3：完整使用流程
// ============================================================

export async function exampleGameFlow() {
  const client = await getKimiClientConfig();
  const genesisPrompt = await loadGenesisPrompt();
  const canonPrompt = await loadPromptFile('prompts/canon_guardian_prompt.md');
  const episodePrompt = await loadPromptFile('prompts/episode_summary_prompt.md');

  const assembler = createPromptAssembler(genesisPrompt);

  let currentTurn = 1;
  const maxTurns = 10;
  const allTurnRecords: TurnRecord[] = [];
  let previousSummary = "";

  while (currentTurn <= maxTurns) {
    console.log(`\n========== 第 ${currentTurn} 回合 ==========`);
    
    // 1. 组装 Prompt
    const prompt = assembler.assemble(exampleWorldState);
    console.log(`预估 Token: ${prompt.estimatedTokens}`);
    
    const outputObj = await kimiChatJson<GenesisOutput>(client, prompt.systemPrompt, prompt.userMessage);

    if (client.enableCanonGuardian) {
      const canonResult = await runCanonGuardianCheck(client, canonPrompt, exampleWorldState, outputObj);
      
      if (canonResult.verdict === "rejected") {
        console.log("Canon Guardian 否决，需要重新生成");
        console.log("违规:", canonResult.violations);
        continue;
      }
    }
    
    // 5. 展示给玩家
    console.log("\n【叙事】");
    console.log(outputObj.narrative);
    
    console.log("\n【可选行动】");
    outputObj.player_options.forEach((opt, i) => {
      console.log(`${i + 1}. ${opt.description}`);
    });
    
    // 6. 更新世界状态（实际应用中会更新数据库）
    updateWorldState(exampleWorldState, outputObj);

    const record: TurnRecord = {
      turnNumber: currentTurn,
      timestamp: Date.now(),
      playerInput: exampleWorldState.player_input,
      narrative: outputObj.narrative,
      stateChanges: outputObj.state_changes,
      selectedOption: 0
    };
    allTurnRecords.push(record);
    assembler.addTurnRecord(record);
    
    // 7. 进入下一回合
    assembler.incrementTurn();
    currentTurn++;
    
    // 每5回合生成摘要
    if (currentTurn % 5 === 0 && allTurnRecords.length >= 5) {
      const last5 = allTurnRecords.slice(-5);
      const quests = exampleWorldState.active_quests.filter(q => q.status === "active").map(q => q.title);
      const summary = await generateEpisodeSummary(
        client,
        episodePrompt,
        currentTurn - 1,
        last5,
        previousSummary,
        quests
      );
      assembler.addEpisodeSummary(summary);
      previousSummary = summary.content;
    }
  }
}

// ============================================================
// 示例4：错误处理
// ============================================================

export async function exampleWithErrorHandling() {
  const assembler = createPromptAssembler(await loadGenesisPrompt());
  
  try {
    const prompt = assembler.assemble(exampleWorldState);
    const client = await getKimiClientConfig();
    const output = await kimiChatJson<GenesisOutput>(client, prompt.systemPrompt, prompt.userMessage);
    
    if (client.enableCanonGuardian) {
      const canonPrompt = await loadPromptFile('prompts/canon_guardian_prompt.md');
      const canonResult = await runCanonGuardianCheck(client, canonPrompt, exampleWorldState, output);

      if (canonResult.verdict === "rejected") {
        throw new CanonViolationError(canonResult.violations || []);
      }
    }
    
    return output;
  } catch (error) {
    if (error instanceof CanonViolationError) {
      console.error("正典违规:");
      error.violations.forEach((v: unknown) => console.error(v));
      
      // 可以选择：
      // 1. 重新生成
      // 2. 人工介入
      // 3. 记录并继续
    } else if (error instanceof SyntaxError) {
      console.error("JSON 解析失败，LLM 输出格式错误");
    } else {
      console.error("未知错误:", error);
    }
    throw error;
  }
}

// ============================================================
// 示例5：记忆系统使用
// ============================================================

export function exampleMemorySystem() {
  const memoryAssembler = createMemoryAssembler();
  
  // 添加回合记录
  memoryAssembler.addTurnRecord({
    turnNumber: 1,
    timestamp: Date.now(),
    playerInput: "进入山林",
    narrative: "你踏入密林，阳光透过树叶洒下斑驳光影...",
    stateChanges: {
      new_locations: [{ 
        id: "deep-forest", 
        name: "密林深处", 
        description: "阳光难以透过的茂密森林，充满了未知的危险" 
      }]
    },
    selectedOption: 0
  });
  
  // 添加剧情摘要
  memoryAssembler.addEpisodeSummary({
    id: "episode-1",
    title: "初入江湖",
    startTurn: 1,
    endTurn: 5,
    content: "云游子离开师门，踏入江湖，在密林中遭遇神秘人...",
    keyDecisions: ["选择帮助神秘人", "拒绝魔教邀请"],
    stateImpact: "与魔教关系恶化，获得神秘人好感",
    newQuestsStarted: ["寻找失落的秘籍"],
    questsCompleted: [],
    importantDiscoveries: ["魔教正在寻找某样东西"],
    npcRelationshipChanges: {
      "mysterious-stranger": "从陌生变为友好"
    },
    foreshadowing: ["神秘人身份不简单"],
    hasActiveQuest: true,
    involvesCurrentLocation: true
  });
  
  // 添加时间线事件
  memoryAssembler.addTimelineEvent({
    id: "event-demonic-cult-rise",
    turn: 3,
    description: "魔教势力开始扩张，江湖动荡",
    importance: "major",
    affectedFactions: ["demonic-cult", "righteous-sects"],
    relatedNPCs: [],
    relatedQuests: []
  });
  
  // 组装上下文
  const context = memoryAssembler.assembleContext(10);
  
  console.log("近景记忆:");
  console.log(context.recent);
  
  console.log("\n中景摘要:");
  console.log(context.episodes);
  
  console.log("\n远景时间线:");
  console.log(context.timeline);
}

type GameRuntimeState = {
  currentWorldState: WorldStateInput;
  allTurnRecords: TurnRecord[];
  allEpisodeSummaries: EpisodeSummary[];
  allTimelineEvents: TimelineEvent[];
  previousSummary: string;
  currentOptions: PlayerOption[];
  currentTurn: number;
  playerName: string;
  worldRequirement: string;
  currentSelectedOption: number;
  currentSlotId: string;
  licenseStatus: LicenseStatus;
};

function displayLicenseBanner(status: LicenseStatus): void {
  const versionLabel = status.isFullVersion ? "完整版" : "免费版";
  const slotCount = getAccessibleSaveSlotCount(status);
  console.log(`\n[授权] 当前为${versionLabel}，可用存档槽：${slotCount}`);
  if (!status.isFullVersion) {
    console.log("[授权] 输入“解锁”查看购买方式，输入“授权状态”查看当前授权。");
  }
}

function buildTurnPrompt(
  assembler: ReturnType<typeof createPromptAssembler>,
  worldState: WorldStateInput,
  licenseStatus: LicenseStatus
): ReturnType<ReturnType<typeof createPromptAssembler>["assemble"]> {
  const prompt = assembler.assemble(worldState);
  if (!isAdvancedGenerationEnabled(licenseStatus)) {
    return prompt;
  }

  const advancedModeNote = [
    "",
    "=".repeat(50),
    "【高级生成模式】",
    "- 当前为完整版，请输出更细腻的环境细节、角色动作和情绪变化",
    "- 优先保证叙事层次与临场感，但仍需遵守结构化 JSON 输出要求"
  ].join("\n");

  return {
    ...prompt,
    userMessage: `${prompt.userMessage}\n${advancedModeNote}`,
    estimatedTokens: prompt.estimatedTokens + 80
  };
}

async function handleRuntimeCommand(commandInput: Extract<TurnInputResult, { kind: "command" }>): Promise<LicenseStatus> {
  if (commandInput.command === "license_status") {
    const status = await getLicenseStatus();
    console.log(`\n${formatLicenseStatus(status)}`);
    return status;
  }

  if (!commandInput.code) {
    console.log(`\n${formatUnlockInstructions()}`);
    return getLicenseStatus();
  }

  const identity = getMachineIdentity();
  const result = await activateLicenseCode(commandInput.code, identity.machineId);
  console.log(`\n[授权] ${result.message}`);
  if (result.ok) {
    console.log(`[授权] 机器摘要：${identity.summary}`);
    console.log("[授权] 完整版已解锁。更多存档槽与高级生成模式将在当前或下次游戏中生效。");
  }
  return result.status;
}

async function resolveTurnActionInput(
  rl: ReturnType<typeof createInterface>,
  currentTurn: number,
  options: PlayerOption[],
  licenseStatus: LicenseStatus
): Promise<{
  input: Extract<TurnInputResult, { kind: "action" | "exit" }>;
  licenseStatus: LicenseStatus;
}> {
  let currentStatus = licenseStatus;

  while (true) {
    const result = await promptTurnInput(rl, currentTurn, options);
    if (result.kind !== "command") {
      return { input: result, licenseStatus: currentStatus };
    }

    currentStatus = await handleRuntimeCommand(result);
  }
}

async function initializeGameRuntime(
  rl: ReturnType<typeof createInterface>,
  client: KimiClientConfig,
  assembler: ReturnType<typeof createPromptAssembler>,
  licenseStatus: LicenseStatus
): Promise<GameRuntimeState | null> {
  const slotSelection = await chooseSaveSlot(rl, getAccessibleSaveSlotCount(licenseStatus));
  if (!slotSelection) {
    return null;
  }

  return slotSelection.startNewGame || !slotSelection.loadedSave
    ? createNewGameRuntime(rl, client, slotSelection.slotId, licenseStatus)
    : resumeGameRuntime(rl, assembler, slotSelection.slotId, slotSelection.loadedSave, licenseStatus);
}

async function createNewGameRuntime(
  rl: ReturnType<typeof createInterface>,
  client: KimiClientConfig,
  slotId: string,
  licenseStatus: LicenseStatus
): Promise<GameRuntimeState | null> {
  const playerName = await promptPlayerName(rl);
  const worldRequirement = await promptWorldRequirement(rl);

  console.log("\n[正在生成初始世界，请稍候...]");
  const initialWorld = await generateInitialWorld(client, worldRequirement, playerName);
  const currentOptions = ensureActionOptions(initialWorld.player_options);

  console.log("\n【世界设定已生成】");
  console.log(initialWorld.story_overview);
  console.log("\n【开场引子】");
  console.log(initialWorld.opening_narrative);
  console.log("\n【当前状态】");
  console.log(formatCurrentStateSummary(initialWorld.world_state));
  console.log("\n【开局选择】");
  displayActionOptions(currentOptions);

  const firstTurn = await resolveTurnActionInput(rl, 1, currentOptions, licenseStatus);
  if (firstTurn.input.kind === "exit") {
    return null;
  }

  return {
    currentWorldState: {
      ...initialWorld.world_state,
      player_input: firstTurn.input.playerInput
    },
    allTurnRecords: [],
    allEpisodeSummaries: [],
    allTimelineEvents: [],
    previousSummary: "",
    currentOptions,
    currentTurn: 1,
    playerName,
    worldRequirement,
    currentSelectedOption: firstTurn.input.selectedOption,
    currentSlotId: slotId,
    licenseStatus: firstTurn.licenseStatus
  };
}

async function resumeGameRuntime(
  rl: ReturnType<typeof createInterface>,
  assembler: ReturnType<typeof createPromptAssembler>,
  slotId: string,
  loadedSave: GameSave,
  licenseStatus: LicenseStatus
): Promise<GameRuntimeState | null> {
  const currentOptions = ensureActionOptions(loadedSave.currentOptions || []);

  assembler.setCurrentTurnNumber(loadedSave.currentTurn);
  loadedSave.allTurnRecords.forEach(record => assembler.addTurnRecord(record));
  loadedSave.allEpisodeSummaries.forEach(summary => assembler.addEpisodeSummary(summary));
  loadedSave.allTimelineEvents.forEach(event => assembler.addTimelineEvent(event));

  console.log("\n[系统] 正在恢复游戏进度...");
  console.log(`\n【世界观】\n${loadedSave.worldRequirement || "未记录世界观"}`);
  console.log("\n【当前状态】");
  console.log(formatCurrentStateSummary(loadedSave.worldState));
  console.log("\n【可选行动】");
  displayActionOptions(currentOptions);

  const firstTurn = await resolveTurnActionInput(rl, loadedSave.currentTurn, currentOptions, licenseStatus);
  if (firstTurn.input.kind === "exit") {
    return null;
  }

  return {
    currentWorldState: {
      ...loadedSave.worldState,
      player_input: firstTurn.input.playerInput
    },
    allTurnRecords: loadedSave.allTurnRecords || [],
    allEpisodeSummaries: loadedSave.allEpisodeSummaries || [],
    allTimelineEvents: loadedSave.allTimelineEvents || [],
    previousSummary: loadedSave.previousSummary || "",
    currentOptions,
    currentTurn: loadedSave.currentTurn,
    playerName: loadedSave.playerName || "旅人",
    worldRequirement: loadedSave.worldRequirement || "未记录世界观",
    currentSelectedOption: firstTurn.input.selectedOption,
    currentSlotId: slotId,
    licenseStatus: firstTurn.licenseStatus
  };
}

async function generateApprovedTurnOutput(
  client: KimiClientConfig,
  canonPrompt: string,
  prompt: ReturnType<ReturnType<typeof createPromptAssembler>["assemble"]>,
  currentWorldState: WorldStateInput
): Promise<GenesisOutput> {
  let outputObj: GenesisOutput | null = null;

  for (let attempt = 1; attempt <= 3; attempt++) {
    outputObj = await kimiChatJson<GenesisOutput>(client, prompt.systemPrompt, prompt.userMessage);

    if (!client.enableCanonGuardian) {
      return outputObj;
    }

    const canonResult = await runCanonGuardianCheck(client, canonPrompt, currentWorldState, outputObj);

    if (canonResult.verdict !== "rejected") {
      return outputObj;
    }

    console.log("Canon Guardian 否决，尝试重新生成：");
    (canonResult.violations || []).forEach((violation: unknown) => console.log(JSON.stringify(violation)));
    outputObj = null;
  }

  throw new Error("连续多次生成均被否决，已中止运行");
}

async function maybeGenerateSummary(
  client: KimiClientConfig,
  episodePrompt: string,
  runtime: GameRuntimeState,
  assembler: ReturnType<typeof createPromptAssembler>
): Promise<void> {
  if (runtime.currentTurn % 5 !== 0) {
    return;
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
  console.log(`\n[已生成剧情摘要：${summary.title}]`);
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

async function persistRuntimeState(runtime: GameRuntimeState): Promise<void> {
  const saveData: GameSave = {
    version: "2.0",
    savedAt: new Date().toISOString(),
    playerName: runtime.playerName,
    worldRequirement: runtime.worldRequirement,
    currentTurn: runtime.currentTurn,
    worldState: runtime.currentWorldState,
    allTurnRecords: runtime.allTurnRecords,
    allEpisodeSummaries: runtime.allEpisodeSummaries,
    allTimelineEvents: runtime.allTimelineEvents,
    previousSummary: runtime.previousSummary,
    currentOptions: runtime.currentOptions,
    saveSlot: runtime.currentSlotId
  };
  const savedFilePath = await saveGame(runtime.currentSlotId, saveData);
  if (savedFilePath) {
    console.log(`[系统] 游戏进度已自动保存至槽位：${runtime.currentSlotId}`);
  }
}

function applyNextTurnInput(
  runtime: GameRuntimeState,
  nextTurnInput: Extract<TurnInputResult, { kind: "action" }>
): void {
  runtime.currentWorldState.player_input = nextTurnInput.playerInput;
  runtime.currentSelectedOption = nextTurnInput.selectedOption;
}

async function runInteractiveGame() {
  const client = await getKimiClientConfig();
  const genesisPrompt = await loadGenesisPrompt();
  const canonPrompt = client.enableCanonGuardian
    ? await loadPromptFile('prompts/canon_guardian_prompt.md')
    : "";
  const episodePrompt = await loadPromptFile('prompts/episode_summary_prompt.md');

  const assembler = createPromptAssembler(genesisPrompt);
  const rl = createInterface({ input, output });

  try {
    const initialLicenseStatus = await getLicenseStatus();
    displayLicenseBanner(initialLicenseStatus);

    const runtime = await initializeGameRuntime(rl, client, assembler, initialLicenseStatus);
    if (!runtime) {
      return;
    }

    while (true) {
      console.log(`\n========== 第 ${runtime.currentTurn} 回合 ==========`);

      const prompt = buildTurnPrompt(assembler, runtime.currentWorldState, runtime.licenseStatus);
      console.log(`预估 Token: ${prompt.estimatedTokens}`);

      const outputObj = await generateApprovedTurnOutput(client, canonPrompt, prompt, runtime.currentWorldState);

      console.log("\n【叙事】");
      console.log(outputObj.narrative);

      updateWorldState(runtime.currentWorldState, outputObj);

      console.log("\n【当前状态】");
      console.log(formatCurrentStateSummary(runtime.currentWorldState));

      console.log("\n【可选行动】");
      runtime.currentOptions = ensureActionOptions(outputObj.player_options);
      displayActionOptions(runtime.currentOptions);

      recordTurnArtifacts(runtime, assembler, outputObj);
      await maybeGenerateSummary(client, episodePrompt, runtime, assembler);

      assembler.incrementTurn();
      runtime.currentTurn++;
      await persistRuntimeState(runtime);

      const nextTurn = await resolveTurnActionInput(rl, runtime.currentTurn, runtime.currentOptions, runtime.licenseStatus);
      runtime.licenseStatus = nextTurn.licenseStatus;
      if (nextTurn.input.kind === "exit") {
        break;
      }
      applyNextTurnInput(runtime, nextTurn.input);
    }
  } finally {
    rl.close();
  }
}

// ============================================================
// 运行示例
// ============================================================

runInteractiveGame().catch(console.error);
