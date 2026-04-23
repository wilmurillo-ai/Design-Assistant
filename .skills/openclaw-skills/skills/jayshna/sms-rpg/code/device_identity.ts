import { createHash } from 'node:crypto';
import { homedir, hostname } from 'node:os';

type MachineIdentity = {
  machineId: string;
  summary: string;
  rawFingerprint: string;
};

function readFirstEnvValue(names: string[]): string | undefined {
  for (const name of names) {
    const value = process.env[name]?.trim();
    if (value) {
      return value;
    }
  }

  return undefined;
}

function summarizeMachineId(machineId: string): string {
  if (machineId.length <= 16) {
    return machineId;
  }

  return `${machineId.slice(0, 8)}...${machineId.slice(-6)}`;
}

export function getMachineIdentity(): MachineIdentity {
  const fingerprintParts = [
    readFirstEnvValue(["OPENCLAW_USER", "OPENCLAW_SESSION_USER", "USER", "LOGNAME"]),
    process.env.HOME?.trim() || homedir(),
    hostname(),
    process.platform
  ].filter((value): value is string => typeof value === "string" && value.length > 0);

  const rawFingerprint = fingerprintParts.join("|") || "unknown-machine";
  const digest = createHash("sha256").update(rawFingerprint).digest("hex");
  const machineId = `sms-${digest.slice(0, 32)}`;

  return {
    machineId,
    summary: summarizeMachineId(machineId),
    rawFingerprint
  };
}
