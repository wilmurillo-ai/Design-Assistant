import { createInterface } from 'node:readline/promises';

import { PlayerOption } from './data_models';
import { GameSave, listSaveSlots, SaveSlotSummary } from './save_store';

type PromptInterface = ReturnType<typeof createInterface>;

export type TurnInputResult =
  | {
      kind: "exit";
      selectedOption: number;
    }
  | {
      kind: "action";
      playerInput: string;
      selectedOption: number;
    }
  | {
      kind: "command";
      command: "unlock" | "license_status";
      code?: string;
    };

export function readPresetValue(names: string[]): string | undefined {
  for (const name of names) {
    const value = process.env[name]?.trim();
    if (value) {
      return value;
    }
  }

  return undefined;
}

function truncateText(value: string, maxLength: number): string {
  return value.length > maxLength ? `${value.slice(0, maxLength - 1)}…` : value;
}

function formatSaveTime(savedAt: string): string {
  const timestamp = Date.parse(savedAt);
  if (Number.isNaN(timestamp)) {
    return "时间未知";
  }

  return new Date(timestamp).toLocaleString();
}

export function displayActionOptions(options: PlayerOption[]): void {
  options.forEach((opt, index) => {
    console.log(`${index + 1}. ${opt.description}`);
  });
}

function displaySaveSlots(slots: SaveSlotSummary[], accessibleSlotCount: number): void {
  console.log("\n【存档状态】");
  console.log("| 槽位 | 游戏 | 回合 | 状态 |");
  console.log("|------|------|------|------|");

  slots.forEach((slot, index) => {
    const locked = index >= accessibleSlotCount;
    const gameLabel = slot.data ? truncateText(slot.data.worldRequirement, 12) : slot.statusText;
    const turnLabel = slot.data ? `第${slot.data.currentTurn}回合` : "-";
    const statusLabel = locked
      ? "完整版可用"
      : slot.data
      ? `${formatSaveTime(slot.data.savedAt)} @ ${truncateText(slot.data.worldState.location_state.name, 8)}`
      : slot.statusText;
    console.log(`| 存档 ${index + 1} | ${gameLabel} | ${turnLabel} | ${statusLabel} |`);
  });
}

export async function promptPlayerName(rl: PromptInterface): Promise<string> {
  const preset = readPresetValue(["SMS_PLAYER_NAME", "OPENCLAW_PLAYER_NAME"]);
  if (preset) {
    console.log(`\n[系统] 已使用预设主角名称：${preset}`);
    return preset;
  }

  const value = (await rl.question("请设定主角名称（默认：旅人）：")).trim();
  return value || "旅人";
}

export async function promptWorldRequirement(rl: PromptInterface): Promise<string> {
  const preset = readPresetValue(["SMS_WORLD_REQUIREMENT", "OPENCLAW_WORLD_REQUIREMENT"]);
  if (preset) {
    console.log(`\n[系统] 已使用预设世界观：${preset}`);
    return preset;
  }

  while (true) {
    const value = (await rl.question("请描述你想要的世界观（如：武侠修仙、赛博朋克、末日废土等）：")).trim();
    if (value.length > 0) {
      return value;
    }

    console.log("世界观不能为空，请重新输入。");
  }
}

export async function promptTurnInput(
  rl: PromptInterface,
  currentTurn: number,
  options: PlayerOption[]
): Promise<TurnInputResult> {
  const answer = (await rl.question(
    `请输入第${currentTurn}回合玩家行动（输入 1-${options.length}，或输入 解锁 / 授权状态 / /exit）：`
  )).trim();
  if (answer === "/exit") {
    return { kind: "exit", selectedOption: options.length - 1 };
  }

  if (answer === "授权状态") {
    return { kind: "command", command: "license_status" };
  }

  if (answer === "解锁") {
    return { kind: "command", command: "unlock" };
  }

  if (answer.startsWith("解锁 ")) {
    const code = answer.slice("解锁 ".length).trim();
    return { kind: "command", command: "unlock", code };
  }

  const index = Number(answer);
  if (Number.isFinite(index) && index >= 1 && index <= options.length) {
    const selectedOption = index - 1;
    if (selectedOption === options.length - 1) {
      while (true) {
        const customAction = (await rl.question("请输入你的自定义行动：")).trim();
        if (customAction === "/exit") {
          return { kind: "exit", selectedOption };
        }
        if (customAction.length > 0) {
          return { kind: "action", playerInput: customAction, selectedOption };
        }
        console.log("自定义行动不能为空，请重新输入。");
      }
    }

    return { kind: "action", playerInput: options[selectedOption].description, selectedOption };
  }

  if (answer.length > 0) {
    return { kind: "action", playerInput: answer, selectedOption: options.length - 1 };
  }

  return { kind: "action", playerInput: options[0]?.description || "继续观察", selectedOption: 0 };
}

export async function chooseSaveSlot(
  rl: PromptInterface,
  accessibleSlotCount: number
): Promise<{ slotId: string; loadedSave: GameSave | null; startNewGame: boolean } | null> {
  const slots = await listSaveSlots();
  displaySaveSlots(slots, accessibleSlotCount);

  const presetSlot = readPresetValue(["SMS_SAVE_SLOT", "OPENCLAW_SAVE_SLOT"]);

  while (true) {
    const answer = (presetSlot ?? await rl.question("请选择存档槽位（输入槽位编号，或 /exit 结束）：")).trim();
    const slotIndex = Number(answer);
    if (answer === "/exit") {
      return null;
    }
    if (!Number.isFinite(slotIndex) || slotIndex < 1 || slotIndex > slots.length) {
      console.log("请输入有效的存档槽位编号。");
      if (presetSlot) {
        return null;
      }
      continue;
    }

    const selectedSlot = slots[slotIndex - 1];
    if (slotIndex > accessibleSlotCount) {
      console.log("该槽位仅完整版可用。请先在游戏内输入“解锁 兑换码”后重启，或选择前两个免费槽位。");
      if (presetSlot) {
        return null;
      }
      continue;
    }

    if (!selectedSlot.data && selectedSlot.filePath) {
      const confirm = (await rl.question(`检测到 ${selectedSlot.slotId} 文件损坏。输入 YES 覆盖此槽位，其他输入返回：`)).trim();
      if (confirm === "YES") {
        return { slotId: selectedSlot.slotId, loadedSave: null, startNewGame: true };
      }
      continue;
    }

    if (!selectedSlot.data) {
      return { slotId: selectedSlot.slotId, loadedSave: null, startNewGame: true };
    }

    console.log(`\n已选择 ${selectedSlot.slotId}：${selectedSlot.data.playerName} / 第${selectedSlot.data.currentTurn}回合 / ${selectedSlot.data.worldState.location_state.name}`);
    const action = (await rl.question("输入 1 继续游戏，输入 2 新建并覆盖此槽位：")).trim();
    if (action === "1") {
      return { slotId: selectedSlot.slotId, loadedSave: selectedSlot.data, startNewGame: false };
    }
    if (action === "2") {
      const confirm = (await rl.question(`确认覆盖 ${selectedSlot.slotId} 吗？输入 YES 确认：`)).trim();
      if (confirm === "YES") {
        return { slotId: selectedSlot.slotId, loadedSave: null, startNewGame: true };
      }
      continue;
    }

    console.log("输入无效，请重新选择。");
  }
}
