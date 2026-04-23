import { homedir } from 'node:os';
import { isAbsolute, join, resolve } from 'node:path';

const PACKAGE_ROOT = resolve(__dirname, "..");
const DEFAULT_DATA_ROOT = join(PACKAGE_ROOT, ".sms-rpg-data");

function uniquePaths(paths: Array<string | undefined>): string[] {
  const seen = new Set<string>();
  const result: string[] = [];

  for (const value of paths) {
    const normalized = value?.trim();
    if (!normalized || seen.has(normalized)) {
      continue;
    }

    seen.add(normalized);
    result.push(normalized);
  }

  return result;
}

export function getPackageRoot(): string {
  return PACKAGE_ROOT;
}

export function resolvePackagePath(filePath: string): string {
  if (isAbsolute(filePath)) {
    return filePath;
  }

  return join(PACKAGE_ROOT, filePath);
}

export function getPromptPath(fileName: string): string {
  return join(PACKAGE_ROOT, "prompts", fileName);
}

export function getDataRootCandidates(includeLegacyAiCreator = false): string[] {
  return uniquePaths([
    process.env.SMS_DATA_DIR,
    process.env.OPENCLAW_SMS_DATA_DIR,
    process.env.OPENCLAW_DATA_DIR,
    DEFAULT_DATA_ROOT,
    includeLegacyAiCreator ? join(homedir(), ".config", "ai-creator-world-seed") : undefined,
    join(homedir(), ".config", "sms-generate-cli"),
    join(process.cwd(), ".sms-generate-cli")
  ]);
}
