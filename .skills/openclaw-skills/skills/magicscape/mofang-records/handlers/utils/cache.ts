/**
 * 魔方网表 Skill 缓存
 * 存储于 ~/.mofang-skills/cache_{baseUrlHash}.json
 * 支持：最近使用空间/表单、用户说法→空间/表单的别名（使用中学习）
 */

import { createHash } from 'crypto';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';

export interface CacheEntry {
  spaceId: string;
  spaceLabel?: string;
  formId?: string;
  formLabel?: string;
}

export interface CacheData {
  lastSpace?: { spaceId: string; spaceLabel: string };
  lastForm?: { spaceId: string; formId: string; spaceLabel: string; formLabel: string };
  aliases?: Record<string, CacheEntry>;
}

const CACHE_DIR = '.mofang-skills';
const MAX_ALIASES = 50;

function getCacheDir(): string {
  const home = process.env.HOME || process.env.USERPROFILE || '';
  if (!home) return '';
  return join(home, CACHE_DIR);
}

function hashBaseUrl(baseUrl: string): string {
  return createHash('sha256').update(baseUrl || '').digest('hex').slice(0, 12);
}

export function getCachePath(baseUrl: string): string {
  const dir = getCacheDir();
  if (!dir) return '';
  const hash = hashBaseUrl(baseUrl);
  return join(dir, `cache_${hash}.json`);
}

/**
 * 别名 key 归一化：trim + 合并多余空格
 */
export function normalizeAliasKey(s: string): string {
  if (typeof s !== 'string') return '';
  return s.trim().replace(/\s+/g, ' ');
}

export async function readCache(baseUrl: string): Promise<CacheData> {
  const path = getCachePath(baseUrl);
  if (!path || !existsSync(path)) return {};
  try {
    const raw = await readFile(path, 'utf-8');
    const data = JSON.parse(raw) as CacheData;
    return data || {};
  } catch {
    return {};
  }
}

export async function writeCache(baseUrl: string, data: CacheData): Promise<void> {
  const path = getCachePath(baseUrl);
  if (!path) return;
  const dir = getCacheDir();
  if (!dir) return;
  try {
    if (!existsSync(dir)) {
      await mkdir(dir, { recursive: true });
    }
    await writeFile(path, JSON.stringify(data, null, 0), 'utf-8');
  } catch {
    // 静默失败，不影响主流程
  }
}

export async function updateLastSpace(
  baseUrl: string,
  spaceId: string,
  spaceLabel: string
): Promise<void> {
  const data = await readCache(baseUrl);
  data.lastSpace = { spaceId, spaceLabel };
  await writeCache(baseUrl, data);
}

export async function updateLastForm(
  baseUrl: string,
  spaceId: string,
  formId: string,
  spaceLabel: string,
  formLabel: string
): Promise<void> {
  const data = await readCache(baseUrl);
  data.lastForm = { spaceId, formId, spaceLabel, formLabel };
  await writeCache(baseUrl, data);
}

export async function addAlias(
  baseUrl: string,
  key: string,
  entry: CacheEntry
): Promise<void> {
  const normKey = normalizeAliasKey(key);
  if (!normKey) return;
  const data = await readCache(baseUrl);
  data.aliases = data.aliases || {};
  data.aliases[normKey] = entry;
  const keys = Object.keys(data.aliases);
  if (keys.length > MAX_ALIASES) {
    const toRemove = keys.slice(0, keys.length - MAX_ALIASES);
    toRemove.forEach((k) => delete data.aliases![k]);
  }
  await writeCache(baseUrl, data);
}

export async function getAlias(baseUrl: string, key: string): Promise<CacheEntry | null> {
  const normKey = normalizeAliasKey(key);
  if (!normKey) return null;
  const data = await readCache(baseUrl);
  const entry = data.aliases?.[normKey];
  return entry || null;
}

export async function getLastSpace(baseUrl: string): Promise<{ spaceId: string; spaceLabel: string } | null> {
  const data = await readCache(baseUrl);
  return data.lastSpace || null;
}

export async function getLastForm(baseUrl: string): Promise<{
  spaceId: string;
  formId: string;
  spaceLabel: string;
  formLabel: string;
} | null> {
  const data = await readCache(baseUrl);
  return data.lastForm || null;
}
