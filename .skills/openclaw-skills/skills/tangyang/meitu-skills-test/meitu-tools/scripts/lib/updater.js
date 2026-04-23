"use strict";

/**
 * Runtime update policy: version check, install, state persistence.
 */

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { runProcess, runMeitu, envInt } = require("./executor");

const SEMVER_PATTERN = /\b(\d+)\.(\d+)\.(\d+)\b/;
const DEFAULT_UPDATE_TTL_HOURS = 24;
const DEFAULT_UPDATE_CHANNEL = "latest";
const DEFAULT_UPDATE_PACKAGE = "meitu-cli";
const DEFAULT_RUNTIME_UPDATE_MODE = "check";
const VALID_RUNTIME_UPDATE_MODES = new Set(["off", "check", "apply"]);
const DEFAULT_TASK_WAIT_TIMEOUT_MS = 900000;
const DEFAULT_VIDEO_TASK_WAIT_TIMEOUT_MS = 600000;

function extractVersionFromText(text) {
  const value = String(text || "");
  const match = value.match(SEMVER_PATTERN);
  return match ? match[0] : "";
}

function parseSemverTuple(version) {
  const value = String(version || "").trim();
  if (!value) {
    return null;
  }
  const match = value.match(SEMVER_PATTERN);
  if (!match) {
    return null;
  }
  return [Number.parseInt(match[1], 10), Number.parseInt(match[2], 10), Number.parseInt(match[3], 10)];
}

function isNewerVersion(latest, current) {
  const latestTuple = parseSemverTuple(latest);
  const currentTuple = parseSemverTuple(current);
  if (latestTuple && currentTuple) {
    if (latestTuple[0] !== currentTuple[0]) {
      return latestTuple[0] > currentTuple[0];
    }
    if (latestTuple[1] !== currentTuple[1]) {
      return latestTuple[1] > currentTuple[1];
    }
    return latestTuple[2] > currentTuple[2];
  }

  const latestText = String(latest || "").trim();
  const currentText = String(current || "").trim();
  if (!latestText) {
    return false;
  }
  if (!currentText) {
    return true;
  }
  return latestText !== currentText;
}

function getInstalledVersion(env) {
  const proc = runMeitu(["--version"], env);
  const combinedText = `${proc.stdout || ""}\n${proc.stderr || ""}`;
  const version = extractVersionFromText(combinedText);
  if (version) {
    return { version, error: "" };
  }

  const message = String(proc.stderr || "").trim() || String(proc.error?.message || "").trim();
  return { version: "", error: message || `exit_code=${proc.returncode}` };
}

function fetchLatestVersion(packageName, channel, env) {
  const proc = runProcess(["npm"], ["view", `${packageName}@${channel}`, "version"], env, 30000);
  const combinedText = `${proc.stdout || ""}\n${proc.stderr || ""}`;
  const version = extractVersionFromText(combinedText);
  if (proc.returncode === 0 && version) {
    return { ok: true, version, error: "" };
  }
  const message = String(proc.stderr || "").trim() || String(proc.error?.message || "").trim();
  return { ok: false, version: "", error: message || "failed to query npm version" };
}

function installRuntimePackage(packageName, channel, env) {
  const proc = runProcess(["npm"], ["install", "-g", `${packageName}@${channel}`], env, 300000);
  if (proc.returncode === 0) {
    return { ok: true, error: "" };
  }
  let message = String(proc.stderr || "").trim() || String(proc.error?.message || "").trim();
  if (message.toLowerCase().includes("eexist")) {
    message = `${message}\nhint: existing binary conflict detected; run 'npm install -g ${packageName}@${channel} --force' if you want to override`;
  }
  return { ok: false, error: message || "npm install failed" };
}

function resolveRuntimeUpdateMode() {
  const raw = String(process.env.MEITU_RUNTIME_UPDATE_MODE || "")
    .trim()
    .toLowerCase();
  if (!raw) {
    return DEFAULT_RUNTIME_UPDATE_MODE;
  }
  if (VALID_RUNTIME_UPDATE_MODES.has(raw)) {
    return raw;
  }
  return DEFAULT_RUNTIME_UPDATE_MODE;
}

function runtimeStatePath() {
  return path.join(os.homedir(), ".meitu", "runtime-update-state.json");
}

function loadRuntimeState() {
  const filePath = runtimeStatePath();
  try {
    const raw = fs.readFileSync(filePath, "utf8");
    const payload = JSON.parse(raw);
    if (!payload || typeof payload !== "object") {
      return {};
    }
    return payload;
  } catch {
    return {};
  }
}

function saveRuntimeState(payload) {
  try {
    const filePath = runtimeStatePath();
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  } catch {
    // ignore state persistence errors
  }
}

function mergeUpdateReports(base, extra) {
  if (!extra) {
    return base;
  }
  if (!base) {
    return extra;
  }
  return {
    mode: extra.mode || base.mode,
    checked: Boolean(base.checked || extra.checked),
    update_available: Boolean(base.update_available || extra.update_available),
    applied: Boolean(base.applied || extra.applied),
    package: extra.package || base.package,
    channel: extra.channel || base.channel,
    reason: extra.reason || base.reason,
    current_version: extra.current_version || base.current_version,
    latest_version: extra.latest_version || base.latest_version,
    to_version: extra.to_version || base.to_version,
    error: extra.error || base.error,
  };
}

function maybeRuntimeUpdate(env, force = false, reason = "startup") {
  const mode = resolveRuntimeUpdateMode();
  const ttlHours = envInt("MEITU_UPDATE_CHECK_TTL_HOURS", DEFAULT_UPDATE_TTL_HOURS, 1);
  const channel = String(process.env.MEITU_UPDATE_CHANNEL || DEFAULT_UPDATE_CHANNEL).trim() || DEFAULT_UPDATE_CHANNEL;
  const packageName =
    String(process.env.MEITU_UPDATE_PACKAGE || DEFAULT_UPDATE_PACKAGE).trim() || DEFAULT_UPDATE_PACKAGE;

  const report = {
    mode,
    checked: false,
    update_available: false,
    applied: false,
    package: packageName,
    channel,
    reason,
    current_version: "",
    latest_version: "",
    to_version: "",
    error: "",
  };

  if (mode === "off") {
    return report;
  }

  const nowTs = Math.floor(Date.now() / 1000);
  const state = loadRuntimeState();
  const current = getInstalledVersion(env);
  report.current_version = current.version;

  const lastCheckTs = Number.parseInt(String(state.last_check_ts || "0"), 10) || 0;
  const ttlSec = ttlHours * 3600;
  const stale = nowTs - lastCheckTs >= ttlSec;
  const channelChanged = String(state.channel || "") !== channel;
  const packageChanged = String(state.package || "") !== packageName;
  const installedChanged = String(state.installed_version || "") !== String(current.version || "");

  const shouldCheck = force || !lastCheckTs || stale || channelChanged || packageChanged || installedChanged;
  if (!shouldCheck) {
    return report;
  }

  report.checked = true;

  const latest = fetchLatestVersion(packageName, channel, env);
  if (!latest.ok) {
    report.error = latest.error;
    saveRuntimeState({
      package: packageName,
      channel,
      installed_version: current.version || "",
      latest_version: String(state.latest_version || ""),
      last_check_ts: nowTs,
      last_error: latest.error,
    });
    return report;
  }

  report.latest_version = latest.version;
  report.update_available = !current.version || isNewerVersion(latest.version, current.version);

  if (!report.update_available || mode === "check") {
    saveRuntimeState({
      package: packageName,
      channel,
      installed_version: current.version || "",
      latest_version: latest.version || "",
      last_check_ts: nowTs,
      last_error: "",
    });
    return report;
  }

  const installResult = installRuntimePackage(packageName, channel, env);
  if (!installResult.ok) {
    report.error = installResult.error;
    saveRuntimeState({
      package: packageName,
      channel,
      installed_version: current.version || "",
      latest_version: latest.version || "",
      last_check_ts: nowTs,
      last_error: installResult.error,
    });
    return report;
  }

  const refreshed = getInstalledVersion(env);
  report.applied = true;
  report.update_available = false;
  report.to_version = refreshed.version || latest.version;
  saveRuntimeState({
    package: packageName,
    channel,
    installed_version: report.to_version || "",
    latest_version: latest.version || "",
    last_check_ts: nowTs,
    last_error: refreshed.error || "",
  });

  return report;
}

function looksLikeRuntimeMismatch(stderr) {
  const text = String(stderr || "").toLowerCase();
  const patterns = [
    "invalid choice",
    "unknown command",
    "command not found",
    "enoent",
    "current meitu runtime does not include built-in commands",
  ];
  return patterns.some((pattern) => text.includes(pattern));
}

module.exports = {
  DEFAULT_TASK_WAIT_TIMEOUT_MS,
  DEFAULT_VIDEO_TASK_WAIT_TIMEOUT_MS,
  maybeRuntimeUpdate,
  mergeUpdateReports,
  looksLikeRuntimeMismatch,
};
