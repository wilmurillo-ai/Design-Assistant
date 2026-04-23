import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

import {
  EpisodeSummary,
  PlayerOption,
  TimelineEvent,
  TurnRecord,
  WorldStateInput
} from './data_models';
import {
  ensureActionOptions,
  isRecord,
  normalizeWorldState,
  uniqueStrings
} from './world_state_utils';
import { getDataRootCandidates } from './runtime_paths';

export type GameSave = {
  version: "2.0";
  savedAt: string;
  playerName: string;
  worldRequirement: string;
  narrativeStyle?: string;
  currentTurn: number;
  worldState: WorldStateInput;
  allTurnRecords: TurnRecord[];
  allEpisodeSummaries: EpisodeSummary[];
  allTimelineEvents: TimelineEvent[];
  previousSummary: string;
  currentOptions: PlayerOption[];
  saveSlot: string;
};

export type SaveSlotSummary = {
  slotId: string;
  filePath: string | null;
  data: GameSave | null;
  statusText: string;
};

const SAVE_SLOT_IDS = ["save_001", "save_002", "save_003", "save_004", "save_005"] as const;
const SAVE_DIRECTORY_PATHS = getDataRootCandidates(true).map(root => join(root, "saves"));

export function toPositiveInteger(value: unknown, fallback: number): number {
  if (typeof value === "number" && Number.isInteger(value) && value > 0) {
    return value;
  }

  if (typeof value === "string") {
    const parsed = Number.parseInt(value, 10);
    if (Number.isInteger(parsed) && parsed > 0) {
      return parsed;
    }
  }

  return fallback;
}

function toIsoString(value: unknown): string {
  if (typeof value === "string" && value.trim().length > 0) {
    return value;
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return new Date(value).toISOString();
  }

  return new Date().toISOString();
}

function normalizeTimelineEvent(raw: unknown): TimelineEvent | null {
  if (!isRecord(raw) || typeof raw.id !== "string" || typeof raw.description !== "string") {
    return null;
  }

  return {
    id: raw.id,
    turn: toPositiveInteger(raw.turn, 1),
    description: raw.description.trim(),
    category: typeof raw.category === "string" ? raw.category as TimelineEvent["category"] : undefined,
    importance: raw.importance === "world_shaking" || raw.importance === "major" || raw.importance === "minor"
      ? raw.importance
      : "minor",
    affectedFactions: Array.isArray(raw.affectedFactions) ? uniqueStrings(raw.affectedFactions) : [],
    relatedNPCs: Array.isArray(raw.relatedNPCs) ? uniqueStrings(raw.relatedNPCs) : [],
    relatedQuests: Array.isArray(raw.relatedQuests) ? uniqueStrings(raw.relatedQuests) : [],
    relatedLocations: Array.isArray(raw.relatedLocations) ? uniqueStrings(raw.relatedLocations) : [],
    npcNames: Array.isArray(raw.npcNames) ? uniqueStrings(raw.npcNames) : [],
    questTitles: Array.isArray(raw.questTitles) ? uniqueStrings(raw.questTitles) : [],
    locationNames: Array.isArray(raw.locationNames) ? uniqueStrings(raw.locationNames) : [],
    tags: Array.isArray(raw.tags) ? uniqueStrings(raw.tags) : [],
    searchText: typeof raw.searchText === "string" ? raw.searchText.trim() : raw.description.trim()
  };
}

function normalizeGameSave(raw: unknown, slotId: string): GameSave | null {
  if (!isRecord(raw) || !isRecord(raw.worldState)) {
    return null;
  }

  const playerName = typeof raw.playerName === "string" && raw.playerName.trim().length > 0
    ? raw.playerName.trim()
    : "旅人";
  const normalizedState = normalizeWorldState(raw.worldState as unknown as WorldStateInput, playerName);

  return {
    version: "2.0",
    savedAt: toIsoString(raw.savedAt ?? raw.timestamp),
    playerName,
    worldRequirement: typeof raw.worldRequirement === "string" && raw.worldRequirement.trim().length > 0
      ? raw.worldRequirement.trim()
      : "未记录世界观",
    narrativeStyle: typeof raw.narrativeStyle === "string" && raw.narrativeStyle.trim().length > 0
      ? raw.narrativeStyle.trim()
      : "通俗、利落，偏《庆余年》式叙事",
    currentTurn: toPositiveInteger(raw.currentTurn ?? raw.turnNumber, 1),
    worldState: normalizedState,
    allTurnRecords: Array.isArray(raw.allTurnRecords) ? raw.allTurnRecords as TurnRecord[] : [],
    allEpisodeSummaries: Array.isArray(raw.allEpisodeSummaries) ? raw.allEpisodeSummaries as EpisodeSummary[] : [],
    allTimelineEvents: Array.isArray(raw.allTimelineEvents)
      ? raw.allTimelineEvents
          .map(normalizeTimelineEvent)
          .filter((event): event is TimelineEvent => event !== null)
      : [],
    previousSummary: typeof raw.previousSummary === "string" ? raw.previousSummary : "",
    currentOptions: ensureActionOptions(Array.isArray(raw.currentOptions) ? raw.currentOptions as PlayerOption[] : []),
    saveSlot: typeof raw.saveSlot === "string" && raw.saveSlot.trim().length > 0 ? raw.saveSlot : slotId
  };
}

async function readSaveSlot(slotId: string): Promise<SaveSlotSummary> {
  for (const saveDir of SAVE_DIRECTORY_PATHS) {
    const filePath = join(saveDir, `${slotId}.json`);
    try {
      const content = await readFile(filePath, 'utf-8');
      const data = normalizeGameSave(JSON.parse(content) as unknown, slotId);
      return {
        slotId,
        filePath,
        data,
        statusText: data ? "可继续" : "文件损坏"
      };
    } catch {
      continue;
    }
  }

  return {
    slotId,
    filePath: null,
    data: null,
    statusText: "未找到文件"
  };
}

export async function listSaveSlots(): Promise<SaveSlotSummary[]> {
  return Promise.all(SAVE_SLOT_IDS.map(slotId => readSaveSlot(slotId)));
}

async function getWritableSaveDirectory(): Promise<string | null> {
  for (const saveDir of SAVE_DIRECTORY_PATHS) {
    try {
      await mkdir(saveDir, { recursive: true });
      return saveDir;
    } catch {
      continue;
    }
  }

  return null;
}

export async function saveGame(slotId: string, data: GameSave): Promise<string | null> {
  const saveDir = await getWritableSaveDirectory();
  if (!saveDir) {
    console.error("\n[警告] 保存进度失败：没有可写的存档目录");
    return null;
  }

  try {
    const filePath = join(saveDir, `${slotId}.json`);
    await writeFile(filePath, JSON.stringify(data, null, 2), 'utf-8');
    return filePath;
  } catch (error) {
    console.error(`\n[警告] 保存进度失败：${String(error)}`);
    return null;
  }
}
