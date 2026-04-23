import {
  configureKimiApiKey,
  getKimiClientConfigNonInteractive,
  hasConfiguredKimiApiKey,
  isConfiguredKimiApiKeyUsable,
  loadGenesisPrompt,
  loadPromptFile
} from './kimi_client';
import {
  buildLicenseBannerText,
  buildRuntimeOverviewText,
  createNewGameRuntime,
  createRuntimeFromSave,
  executeTurn,
  resolvePlayerActionInput,
  toGameSave
} from './game_engine';
import {
  loadDialogSave,
  loadDialogSessionMeta,
  PendingSetup,
  saveDialogSave,
  saveDialogSessionMeta
} from './dialog_store';
import {
  activateLicenseCode,
  formatLicenseStatus,
  formatUnlockInstructions,
  getAccessibleSaveSlotCount,
  getLicenseStatus,
  getPurchaseUrl
} from './license_service';
import { getMachineIdentity } from './device_identity';

type DialogResponse = {
  content: string;
  slotId: string;
  shouldContinue: boolean;
};

export type OpenClawDialogContext = {
  userId: string;
  slotId?: string;
};

const TOTAL_SAVE_SLOTS = 5;
const DEFAULT_NARRATIVE_STYLE = "通俗、利落、有人味，整体接近《庆余年》的小说叙事感";

let promptCache: { genesisPrompt: string; canonPrompt: string; episodePrompt: string } | null = null;

function toSlotId(slotNumber: number): string {
  return `save_${String(slotNumber).padStart(3, "0")}`;
}

function fromSlotId(slotId: string): number {
  const matched = slotId.match(/^save_(\d{3})$/);
  if (!matched) {
    return 1;
  }

  return Number.parseInt(matched[1], 10);
}

function parseSlotNumber(text: string | undefined): number | null {
  if (!text) {
    return null;
  }

  const parsed = Number.parseInt(text, 10);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > TOTAL_SAVE_SLOTS) {
    return null;
  }

  return parsed;
}

function normalizeMessage(input: string): string {
  return input.trim();
}

function buildHelpText(): string {
  return [
    "可用指令：",
    "1. 设置API sk-xxx",
    "2. 开始新游戏 [槽位号]",
    "3. 继续游戏 [槽位号]",
    "4. 存档列表",
    "5. 解锁 / 解锁 WUXIA-XXXX-XXXX",
    "6. 授权状态",
    "7. 取消",
    "",
    "新手推荐顺序：",
    "- 先设置 API",
    "- 再填写主角名",
    "- 然后填写世界观",
    "- 最后确定叙事风格",
    "",
    "普通游玩方式：",
    "- 直接回复 1/2/3 选择推荐行动",
    "- 或直接输入一句自然语言行动",
    "- 如果想自定义行动，不用输 4，直接把你的动作发出来即可"
  ].join("\n");
}

function buildApiPrompt(slotId: string): string {
  return [
    `开始新游戏前，请先设置 Kimi API Key（存档 ${fromSlotId(slotId)}）。`,
    "直接发送：",
    "设置API sk-xxxx",
    "或直接发送完整的 sk- 开头 Key。"
  ].join("\n");
}

function buildStartPrompt(slotId: string, existingSave: boolean): string {
  const slotNumber = fromSlotId(slotId);
  return [
    `准备在存档 ${slotNumber} 开始新游戏。${existingSave ? "注意：该槽位已有旧存档，新游戏会覆盖后续进度。" : ""}`,
    "请先回复主角名称。",
    "例如：",
    "主角名 云游子",
    "或直接回复一个名字。"
  ].join("\n");
}

function buildWorldRequirementPrompt(slotId: string, playerName: string): string {
  return [
    `主角已设为：${playerName}`,
    `接下来请回复你想要的世界观，用于创建存档 ${fromSlotId(slotId)} 的新游戏。`,
    "例如：",
    "武侠修仙，江湖门派与朝廷暗斗",
    "或使用：世界观 赛博修仙末日废土"
  ].join("\n");
}

function buildNarrativeStylePrompt(slotId: string, playerName: string, worldRequirement: string): string {
  return [
    `主角：${playerName}`,
    `世界观：${worldRequirement}`,
    `最后一步，请告诉我你要的叙事风格，用于创建存档 ${fromSlotId(slotId)}。`,
    "如果没有特别要求，直接回复：默认",
    `默认风格：${DEFAULT_NARRATIVE_STYLE}`,
    "也可以回复：叙事风格 更冷幽默一点，但依旧通俗"
  ].join("\n");
}

function buildNewGameContent(
  storyOverview: string,
  openingNarrative: string,
  runtimeOverview: string,
  slotId: string
): string {
  return [
    `【新游戏已创建：存档 ${fromSlotId(slotId)}】`,
    "",
    "【世界设定】",
    storyOverview,
    "",
    "【开场引子】",
    openingNarrative,
    "",
    runtimeOverview,
    "",
    "请直接回复 1/2/3 选择推荐行动，或直接输入你想做的动作。"
  ].join("\n");
}

function buildContinueContent(slotId: string, runtimeOverview: string): string {
  return [
    `【已载入存档 ${fromSlotId(slotId)}】`,
    "",
    runtimeOverview,
    "",
    "请直接回复 1/2/3 继续推进，或直接输入你想做的动作。"
  ].join("\n");
}

async function loadPrompts() {
  if (!promptCache) {
    const [genesisPrompt, canonPrompt, episodePrompt] = await Promise.all([
      loadGenesisPrompt(),
      loadPromptFile('prompts/canon_guardian_prompt.md'),
      loadPromptFile('prompts/episode_summary_prompt.md')
    ]);
    promptCache = { genesisPrompt, canonPrompt, episodePrompt };
  }

  return promptCache;
}

function extractApiKey(message: string): string | null {
  const normalized = normalizeMessage(message);
  if (/^sk-[A-Za-z0-9]+$/.test(normalized)) {
    return normalized;
  }

  const prefixed = normalized.match(/^设置API\s+(sk-[A-Za-z0-9]+)$/i);
  if (prefixed) {
    return prefixed[1];
  }

  return null;
}

function normalizeNarrativeStyle(input: string): string {
  const normalized = input.replace(/^叙事风格\s+/, "").trim();
  if (!normalized || normalized === "默认") {
    return DEFAULT_NARRATIVE_STYLE;
  }

  return normalized;
}

function isValidNarrativeStyleInput(input: string): boolean {
  const normalized = normalizeNarrativeStyle(input);
  if (normalized === DEFAULT_NARRATIVE_STYLE) {
    return true;
  }

  if (/^\d+$/.test(normalized)) {
    return false;
  }

  return normalized.length >= 4;
}

function buildUpgradePromptText(): string {
  const purchaseUrl = getPurchaseUrl();
  return [
    "如果你想提升存档槽数量，可以解锁完整版。",
    purchaseUrl ? `爱发电链接：${purchaseUrl}` : "请在环境变量 SMS_PRODUCT_URL 中配置你的爱发电链接。",
    "",
    formatUnlockInstructions()
  ].join("\n");
}

function buildChapterPromotionText(completedTurn: number): string | null {
  if (completedTurn <= 0 || completedTurn % 10 !== 0) {
    return null;
  }

  const purchaseUrl = getPurchaseUrl();
  return [
    `【章节提示】你已经推进到第 ${completedTurn} 章节点。`,
    purchaseUrl
      ? `如果你想解锁更多存档槽，支持继续追更，可以前往爱发电：${purchaseUrl}`
      : "如果你想解锁更多存档槽，请配置 SMS_PRODUCT_URL 后展示爱发电链接。"
  ].join("\n");
}

function formatDialogError(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);

  if (/401|认证失败|Invalid Authentication|Unauthorized/i.test(message)) {
    return [
      "当前无法调用 Kimi 模型：API Key 认证失败。",
      "请检查 `MOONSHOT_API_KEY` 是否有效，或更新本地配置后再试。"
    ].join("\n");
  }

  if (/timed out|超时|timeout/i.test(message)) {
    return "调用 Kimi 超时，请稍后重试。";
  }

  return `处理当前对话时出错：${message}`;
}

function buildPendingStageRetryHint(pendingSetup: PendingSetup): string {
  if (pendingSetup.stage === "awaiting_world_requirement") {
    return "你当前仍停留在“输入世界观”这一步。修复后可以直接重新发送世界观。";
  }

  if (pendingSetup.stage === "awaiting_narrative_style") {
    return "你当前仍停留在“输入叙事风格”这一步。修复后可以直接回复“默认”或新的风格描述。";
  }

  return "修复后可以继续当前创建流程，无需从头开始。";
}

async function ensureSlotAllowed(slotId: string): Promise<{ ok: boolean; message?: string }> {
  const status = await getLicenseStatus();
  const allowed = getAccessibleSaveSlotCount(status);
  const requested = fromSlotId(slotId);
  if (requested <= allowed) {
    return { ok: true };
  }

  return {
    ok: false,
    message: `当前授权最多可使用 ${allowed} 个存档槽。请先输入“解锁 兑换码”，或改用存档 ${allowed} 以内的槽位。`
  };
}

async function listSlotStatus(userId: string): Promise<string> {
  const status = await getLicenseStatus();
  const allowed = getAccessibleSaveSlotCount(status);
  const lines = [buildLicenseBannerText(status), "", "【存档列表】"];

  for (let slotNumber = 1; slotNumber <= TOTAL_SAVE_SLOTS; slotNumber += 1) {
    const slotId = toSlotId(slotNumber);
    const save = await loadDialogSave(userId, slotId);
    if (slotNumber > allowed) {
      lines.push(`- 存档 ${slotNumber}：完整版可用`);
      continue;
    }

    if (!save) {
      lines.push(`- 存档 ${slotNumber}：空`);
      continue;
    }

    lines.push(`- 存档 ${slotNumber}：${save.playerName} / 第${save.currentTurn}回合 / ${save.worldState.location_state.name}`);
  }

  return lines.join("\n");
}

async function handleUnlockMessage(message: string): Promise<DialogResponse> {
  const normalized = normalizeMessage(message);
  if (normalized === "解锁") {
    return {
      content: formatUnlockInstructions(),
      slotId: "save_001",
      shouldContinue: true
    };
  }

  const code = normalized.replace(/^解锁\s+/, "").trim();
  const identity = getMachineIdentity();
  const result = await activateLicenseCode(code, identity.machineId);
  return {
    content: [
      `[授权] ${result.message}`,
      result.ok ? `[授权] 机器摘要：${identity.summary}` : "",
      formatLicenseStatus(result.status)
    ].filter(Boolean).join("\n"),
    slotId: "save_001",
    shouldContinue: true
  };
}

async function continueGame(userId: string, slotId: string): Promise<DialogResponse> {
  const guard = await ensureSlotAllowed(slotId);
  if (!guard.ok) {
    return {
      content: guard.message || "该存档槽当前不可用。",
      slotId,
      shouldContinue: true
    };
  }

  const status = await getLicenseStatus();
  const save = await loadDialogSave(userId, slotId);
  if (!save) {
    return {
      content: `存档 ${fromSlotId(slotId)} 目前为空。请先输入“开始新游戏 ${fromSlotId(slotId)}”。`,
      slotId,
      shouldContinue: true
    };
  }

  const runtime = createRuntimeFromSave(slotId, save, status);
  return {
    content: buildContinueContent(slotId, buildRuntimeOverviewText(runtime)),
    slotId,
    shouldContinue: true
  };
}

async function completePendingSetup(
  userId: string,
  input: string,
  pendingSetup: PendingSetup,
  currentSlotId: string
): Promise<DialogResponse> {
  const normalized = normalizeMessage(input);
  if (normalized === "取消") {
    await saveDialogSessionMeta({
      userId,
      currentSlotId,
      pendingSetup: null
    });
    return {
      content: "已取消当前的新游戏创建流程。",
      slotId: currentSlotId,
      shouldContinue: true
    };
  }

  if (pendingSetup.stage === "awaiting_player_name") {
    const playerName = normalized.replace(/^主角名\s+/, "").trim();
    if (!playerName) {
      return {
        content: "主角名称不能为空，请重新输入。",
        slotId: pendingSetup.slotId,
        shouldContinue: true
      };
    }

    await saveDialogSessionMeta({
      userId,
      currentSlotId: pendingSetup.slotId,
      pendingSetup: {
        stage: "awaiting_world_requirement",
        slotId: pendingSetup.slotId,
        playerName
      }
    });
    return {
      content: buildWorldRequirementPrompt(pendingSetup.slotId, playerName),
      slotId: pendingSetup.slotId,
      shouldContinue: true
    };
  }

  if (pendingSetup.stage === "awaiting_api_key") {
    const apiKey = extractApiKey(normalized);
    if (!apiKey) {
      return {
        content: "API Key 格式不正确。请直接发送完整的 `sk-...`，或使用“设置API sk-...”格式。",
        slotId: pendingSetup.slotId,
        shouldContinue: true
      };
    }

    try {
      const message = await configureKimiApiKey(apiKey);
      await saveDialogSessionMeta({
        userId,
        currentSlotId: pendingSetup.slotId,
        pendingSetup: {
          stage: "awaiting_player_name",
          slotId: pendingSetup.slotId
        }
      });
      return {
        content: [
          message,
          "",
          buildStartPrompt(pendingSetup.slotId, (await loadDialogSave(userId, pendingSetup.slotId)) !== null)
        ].join("\n"),
        slotId: pendingSetup.slotId,
        shouldContinue: true
      };
    } catch (error) {
      return {
        content: formatDialogError(error),
        slotId: pendingSetup.slotId,
        shouldContinue: true
      };
    }
  }

  const worldRequirement = normalized.replace(/^世界观\s+/, "").trim();
  if (pendingSetup.stage === "awaiting_world_requirement" && !worldRequirement) {
    return {
      content: "世界观描述不能为空，请重新输入。",
      slotId: pendingSetup.slotId,
      shouldContinue: true
    };
  }

  if (pendingSetup.stage === "awaiting_world_requirement") {
    await saveDialogSessionMeta({
      userId,
      currentSlotId: pendingSetup.slotId,
      pendingSetup: {
        stage: "awaiting_narrative_style",
        slotId: pendingSetup.slotId,
        playerName: pendingSetup.playerName,
        worldRequirement
      }
    });
    return {
      content: buildNarrativeStylePrompt(pendingSetup.slotId, pendingSetup.playerName, worldRequirement),
      slotId: pendingSetup.slotId,
      shouldContinue: true
    };
  }

  try {
    if (pendingSetup.stage === "awaiting_narrative_style" && !isValidNarrativeStyleInput(normalized)) {
      return {
        content: [
          "叙事风格描述太短，或看起来像误输入的编号。",
          "请直接回复“默认”，或补充一句风格说明。",
          `默认风格：${DEFAULT_NARRATIVE_STYLE}`
        ].join("\n"),
        slotId: pendingSetup.slotId,
        shouldContinue: true
      };
    }

    const [client, licenseStatus] = await Promise.all([
      getKimiClientConfigNonInteractive(),
      getLicenseStatus()
    ]);
    const result = await createNewGameRuntime(
      client,
      pendingSetup.slotId,
      pendingSetup.playerName,
      pendingSetup.worldRequirement,
      normalizeNarrativeStyle(normalized),
      licenseStatus
    );
    await saveDialogSave(userId, pendingSetup.slotId, toGameSave(result.runtime));
    await saveDialogSessionMeta({
      userId,
      currentSlotId: pendingSetup.slotId,
      pendingSetup: null
    });

    return {
      content: buildNewGameContent(
        result.storyOverview,
        result.openingNarrative,
        buildRuntimeOverviewText(result.runtime),
        pendingSetup.slotId
      ),
      slotId: pendingSetup.slotId,
      shouldContinue: true
    };
  } catch (error) {
    return {
      content: [
        formatDialogError(error),
        "",
        buildPendingStageRetryHint(pendingSetup)
      ].join("\n"),
      slotId: pendingSetup.slotId,
      shouldContinue: true
    };
  }
}

function parseGameCommand(message: string): { kind: string; slotId?: string } | null {
  const normalized = normalizeMessage(message);
  if (!normalized) {
    return null;
  }

  if (normalized === "帮助" || normalized.toLowerCase() === "help") {
    return { kind: "help" };
  }

  if (normalized === "授权状态") {
    return { kind: "license_status" };
  }

  if (normalized === "存档列表") {
    return { kind: "slot_list" };
  }

  if (normalized === "扩容存档" || normalized === "更多存档槽" || normalized === "提升存档槽" || normalized === "购买完整版") {
    return { kind: "upgrade_slots" };
  }

  if (normalized === "解锁" || normalized.startsWith("解锁 ")) {
    return { kind: "unlock" };
  }

  const newGameMatch = normalized.match(/^(开始新游戏|新游戏)(?:\s+(\d+))?$/);
  if (newGameMatch) {
    const slotNumber = parseSlotNumber(newGameMatch[2]) || 1;
    return { kind: "start_new_game", slotId: toSlotId(slotNumber) };
  }

  const continueMatch = normalized.match(/^(继续游戏|继续)(?:\s+(\d+))?$/);
  if (continueMatch) {
    const slotNumber = parseSlotNumber(continueMatch[2]) || 1;
    return { kind: "continue_game", slotId: toSlotId(slotNumber) };
  }

  return null;
}

export async function processGameInput(
  userId: string,
  input: string,
  preferredSlotId?: string
): Promise<DialogResponse> {
  const message = normalizeMessage(input);
  const meta = await loadDialogSessionMeta(userId);
  const activeSlotId = preferredSlotId || meta.currentSlotId || "save_001";
  const command = parseGameCommand(message);
  const directApiKey = extractApiKey(message);

  if (!message) {
    return {
      content: buildHelpText(),
      slotId: activeSlotId,
      shouldContinue: true
    };
  }

  if (directApiKey && !meta.pendingSetup) {
    try {
      const resultMessage = await configureKimiApiKey(directApiKey);
      return {
        content: [
          resultMessage,
          "",
          "现在可以输入：开始新游戏",
          "接下来我会继续引导你填写主角名、世界观和叙事风格。"
        ].join("\n"),
        slotId: activeSlotId,
        shouldContinue: true
      };
    } catch (error) {
      return {
        content: formatDialogError(error),
        slotId: activeSlotId,
        shouldContinue: true
      };
    }
  }

  if (meta.pendingSetup) {
    if (message === "取消") {
      return completePendingSetup(userId, message, meta.pendingSetup, activeSlotId);
    }

    if (command?.kind === "help") {
      return {
        content: [
          "你当前正在创建新游戏。",
          "如果要继续，请直接回复主角名称或世界观。",
          "如果要退出，请输入“取消”。",
          "",
          buildHelpText()
        ].join("\n"),
        slotId: activeSlotId,
        shouldContinue: true
      };
    }

    if (command?.kind === "license_status") {
      return {
        content: formatLicenseStatus(await getLicenseStatus()),
        slotId: activeSlotId,
        shouldContinue: true
      };
    }

    if (command?.kind === "slot_list") {
      return {
        content: await listSlotStatus(userId),
        slotId: activeSlotId,
        shouldContinue: true
      };
    }

    if (command?.kind === "upgrade_slots") {
      return {
        content: buildUpgradePromptText(),
        slotId: activeSlotId,
        shouldContinue: true
      };
    }

    if (command?.kind === "unlock") {
      const response = await handleUnlockMessage(message);
      return {
        ...response,
        slotId: activeSlotId
      };
    }

    if (command?.kind === "start_new_game" || command?.kind === "continue_game") {
      return {
        content: "你当前正在创建一个新游戏。如果要切换流程，请先输入“取消”，然后再执行新的指令。",
        slotId: activeSlotId,
        shouldContinue: true
      };
    }

    return completePendingSetup(userId, message, meta.pendingSetup, activeSlotId);
  }
  if (command?.kind === "help") {
    return {
      content: buildHelpText(),
      slotId: activeSlotId,
      shouldContinue: true
    };
  }

  if (command?.kind === "license_status") {
    return {
      content: formatLicenseStatus(await getLicenseStatus()),
      slotId: activeSlotId,
      shouldContinue: true
    };
  }

  if (command?.kind === "slot_list") {
    return {
      content: await listSlotStatus(userId),
      slotId: activeSlotId,
      shouldContinue: true
    };
  }

  if (command?.kind === "upgrade_slots") {
    return {
      content: buildUpgradePromptText(),
      slotId: activeSlotId,
      shouldContinue: true
    };
  }

  if (command?.kind === "unlock") {
    const response = await handleUnlockMessage(message);
    return {
      ...response,
      slotId: activeSlotId
    };
  }

  if (command?.kind === "start_new_game" && command.slotId) {
    if (!await hasConfiguredKimiApiKey() || !await isConfiguredKimiApiKeyUsable()) {
      await saveDialogSessionMeta({
        userId,
        currentSlotId: command.slotId,
        pendingSetup: {
          stage: "awaiting_api_key",
          slotId: command.slotId
        }
      });
      return {
        content: buildApiPrompt(command.slotId),
        slotId: command.slotId,
        shouldContinue: true
      };
    }

    const guard = await ensureSlotAllowed(command.slotId);
    if (!guard.ok) {
      return {
        content: [guard.message || "该存档槽当前不可用。", "", buildUpgradePromptText()].join("\n"),
        slotId: command.slotId,
        shouldContinue: true
      };
    }

    const existingSave = await loadDialogSave(userId, command.slotId);
    await saveDialogSessionMeta({
      userId,
      currentSlotId: command.slotId,
      pendingSetup: {
        stage: "awaiting_player_name",
        slotId: command.slotId
      }
    });
    return {
      content: buildStartPrompt(command.slotId, existingSave !== null),
      slotId: command.slotId,
      shouldContinue: true
    };
  }

  if (command?.kind === "continue_game" && command.slotId) {
    const response = await continueGame(userId, command.slotId);
    await saveDialogSessionMeta({
      userId,
      currentSlotId: command.slotId,
      pendingSetup: null
    });
    return response;
  }

  const guard = await ensureSlotAllowed(activeSlotId);
  if (!guard.ok) {
    return {
      content: [guard.message || "该存档槽当前不可用。", "", buildUpgradePromptText()].join("\n"),
      slotId: activeSlotId,
      shouldContinue: true
    };
  }

  const save = await loadDialogSave(userId, activeSlotId);
  if (!save) {
    return {
      content: [
        "当前还没有可继续的游戏。",
        `请先输入“开始新游戏 ${fromSlotId(activeSlotId)}”，或输入“存档列表”查看可用槽位。`
      ].join("\n"),
      slotId: activeSlotId,
      shouldContinue: true
    };
  }

  const licenseStatus = await getLicenseStatus();
  const runtime = createRuntimeFromSave(activeSlotId, save, licenseStatus);
  const resolvedAction = resolvePlayerActionInput(message, runtime.currentOptions);
  if (resolvedAction.kind === "needs_custom_action") {
    return {
      content: resolvedAction.message,
      slotId: activeSlotId,
      shouldContinue: true
    };
  }

  try {
    const [client, prompts] = await Promise.all([
      getKimiClientConfigNonInteractive(),
      loadPrompts()
    ]);

    const turnResult = await executeTurn(
      runtime,
      resolvedAction.playerInput,
      resolvedAction.selectedOption,
      client,
      prompts
    );
    await saveDialogSave(userId, activeSlotId, toGameSave(turnResult.runtime));
    await saveDialogSessionMeta({
      userId,
      currentSlotId: activeSlotId,
      pendingSetup: null
    });

    return {
      content: [
        `【第 ${turnResult.runtime.currentTurn - 1} 回合】`,
        `预估 Token：${turnResult.estimatedTokens}`,
        "",
        "【叙事】",
        turnResult.narrative,
        "",
        "【当前状态】",
        turnResult.stateSummary,
        turnResult.generatedSummaryTitle ? `\n[系统] 已生成剧情摘要：${turnResult.generatedSummaryTitle}` : "",
        buildChapterPromotionText(turnResult.runtime.currentTurn - 1) ? `\n${buildChapterPromotionText(turnResult.runtime.currentTurn - 1)}` : "",
        "",
        "【可选行动】",
        turnResult.optionsText,
        "",
        "请继续回复 1/2/3，或直接输入你的行动。"
      ].filter(Boolean).join("\n"),
      slotId: activeSlotId,
      shouldContinue: true
    };
  } catch (error: any) {
    return {
      content: [
        formatDialogError(error),
        error.stack,
        "",
        "本回合未推进，你可以直接重试刚才的行动。"
      ].join("\n"),
      slotId: activeSlotId,
      shouldContinue: true
    };
  }
}

export async function handleOpenClawMessage(
  message: string,
  context: OpenClawDialogContext
): Promise<string> {
  const result = await processGameInput(context.userId, message, context.slotId);
  return result.content;
}

function parseCliArgs(argv: string[]): { userId: string; input: string; slotId?: string } {
  let userId = "local-user";
  let input = "";
  let slotId: string | undefined;

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    const next = argv[index + 1];
    if (arg === "--user" && next) {
      userId = next.trim();
      index += 1;
      continue;
    }
    if (arg === "--input" && next) {
      input = next;
      index += 1;
      continue;
    }
    if (arg === "--slot" && next) {
      const slotNumber = parseSlotNumber(next);
      slotId = slotNumber ? toSlotId(slotNumber) : undefined;
      index += 1;
    }
  }

  return { userId, input, slotId };
}

if (require.main === module) {
  const { userId, input, slotId } = parseCliArgs(process.argv.slice(2));
  if (!input.trim()) {
    console.log("用法：npm run dialog -- --user demo --input \"开始新游戏\"");
    process.exit(0);
  }

  processGameInput(userId, input, slotId)
    .then(result => {
      console.log(result.content);
    })
    .catch(error => {
      console.error(error);
      process.exit(1);
    });
}
