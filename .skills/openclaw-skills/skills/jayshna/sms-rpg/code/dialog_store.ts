import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

import { GameSave } from './save_store';
import { getDataRootCandidates } from './runtime_paths';

export type PendingSetup =
  | {
      stage: "awaiting_api_key";
      slotId: string;
    }
  | {
      stage: "awaiting_player_name";
      slotId: string;
    }
  | {
      stage: "awaiting_world_requirement";
      slotId: string;
      playerName: string;
    }
  | {
      stage: "awaiting_narrative_style";
      slotId: string;
      playerName: string;
      worldRequirement: string;
    };

export type DialogSessionMeta = {
  userId: string;
  currentSlotId: string;
  pendingSetup: PendingSetup | null;
};

const DIALOG_ROOT_PATHS = getDataRootCandidates().map(root => join(root, "dialog"));

function sanitizeSegment(value: string): string {
  return value
    .trim()
    .replace(/[^a-zA-Z0-9._-]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 80) || "default-user";
}

function isPendingSetup(value: unknown): value is PendingSetup {
  if (!value || typeof value !== "object") {
    return false;
  }

  const record = value as Record<string, unknown>;
  if (record.stage === "awaiting_player_name") {
    return typeof record.slotId === "string";
  }

  if (record.stage === "awaiting_api_key") {
    return typeof record.slotId === "string";
  }

  if (record.stage === "awaiting_world_requirement") {
    return typeof record.slotId === "string" && typeof record.playerName === "string";
  }

  if (record.stage === "awaiting_narrative_style") {
    return typeof record.slotId === "string"
      && typeof record.playerName === "string"
      && typeof record.worldRequirement === "string";
  }

  return false;
}

async function getWritableDialogRoot(): Promise<string | null> {
  for (const root of DIALOG_ROOT_PATHS) {
    try {
      await mkdir(root, { recursive: true });
      return root;
    } catch {
      continue;
    }
  }

  return null;
}

function buildMetaPath(root: string, userId: string): string {
  return join(root, "meta", `${sanitizeSegment(userId)}.json`);
}

function buildSavePath(root: string, userId: string, slotId: string): string {
  return join(root, "saves", sanitizeSegment(userId), `${slotId}.json`);
}

async function readJsonFile<T>(filePath: string): Promise<T | null> {
  try {
    const raw = await readFile(filePath, 'utf-8');
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export async function loadDialogSessionMeta(userId: string): Promise<DialogSessionMeta> {
  for (const root of DIALOG_ROOT_PATHS) {
    const parsed = await readJsonFile<Partial<DialogSessionMeta>>(buildMetaPath(root, userId));
    if (!parsed) {
      continue;
    }

    return {
      userId,
      currentSlotId: typeof parsed.currentSlotId === "string" ? parsed.currentSlotId : "save_001",
      pendingSetup: isPendingSetup(parsed.pendingSetup) ? parsed.pendingSetup : null
    };
  }

  return {
    userId,
    currentSlotId: "save_001",
    pendingSetup: null
  };
}

export async function saveDialogSessionMeta(meta: DialogSessionMeta): Promise<string | null> {
  const root = await getWritableDialogRoot();
  if (!root) {
    return null;
  }

  const filePath = buildMetaPath(root, meta.userId);
  await mkdir(join(filePath, ".."), { recursive: true });
  await writeFile(filePath, JSON.stringify(meta, null, 2), 'utf-8');
  return filePath;
}

export async function loadDialogSave(userId: string, slotId: string): Promise<GameSave | null> {
  for (const root of DIALOG_ROOT_PATHS) {
    const parsed = await readJsonFile<GameSave>(buildSavePath(root, userId, slotId));
    if (parsed) {
      return parsed;
    }
  }

  return null;
}

export async function saveDialogSave(
  userId: string,
  slotId: string,
  save: GameSave
): Promise<string | null> {
  const root = await getWritableDialogRoot();
  if (!root) {
    return null;
  }

  const filePath = buildSavePath(root, userId, slotId);
  await mkdir(join(filePath, ".."), { recursive: true });
  await writeFile(filePath, JSON.stringify(save, null, 2), 'utf-8');
  return filePath;
}
