// Reflexio Embedded — pure handler logic.
//
// This module is intentionally decoupled from the Openclaw SDK so that:
//   1. The TTL sweep / transcript serialization logic is easy to unit-test via
//      `smoke-test.js` without spinning up a gateway.
//   2. Swapping the SDK wiring (see ../index.ts) never requires touching the
//      behavioural code here.
import * as fs from "node:fs";
import * as path from "node:path";

/** Minimal subset of the Openclaw runtime we actually use. */
type SubagentRuntime = {
  subagent?: {
    run: (params: {
      sessionKey: string;
      message: string;
      extraSystemPrompt?: string;
      lane?: string;
      idempotencyKey?: string;
    }) => Promise<{ runId: string }>;
  };
};

type Logger = {
  info?: (msg: string) => void;
  warn?: (msg: string) => void;
  error?: (msg: string) => void;
};

/**
 * Find the workspace root. Openclaw passes it via ctx.workspaceDir; fall back
 * to the WORKSPACE env var (handy for smoke tests) and finally process.cwd().
 */
export function resolveWorkspace(hint?: string): string {
  if (hint && hint.trim()) return hint;
  if (process.env.WORKSPACE) return process.env.WORKSPACE;
  return process.cwd();
}

/**
 * TTL sweep: scan .reflexio/profiles/*.md and unlink expired files.
 * Cheap: filesystem + YAML frontmatter parse only. Target <50ms for dozens of files.
 */
export async function ttlSweepProfiles(workspaceHint?: string): Promise<void> {
  const workspace = resolveWorkspace(workspaceHint);
  const dir = path.join(workspace, ".reflexio", "profiles");
  if (!fs.existsSync(dir)) return;

  const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  const entries = await fs.promises.readdir(dir);

  for (const entry of entries) {
    if (!entry.endsWith(".md")) continue;
    const full = path.join(dir, entry);
    let contents: string;
    try {
      contents = await fs.promises.readFile(full, "utf8");
    } catch {
      continue;
    }
    const expiresMatch = /^expires:\s*(\S+)/m.exec(contents);
    if (!expiresMatch) continue;
    const expires = expiresMatch[1];
    if (expires === "never") continue;
    if (expires < today) {
      try {
        await fs.promises.unlink(full);
      } catch (err) {
        console.error(
          `[reflexio-embedded] ttl sweep: failed to unlink ${full}: ${err}`,
        );
      }
    }
  }
}

/**
 * Short system-prompt reminder injected on every agent run so the LLM knows
 * the Reflexio SKILL.md is available.
 */
export function injectBootstrapReminder(): string {
  return [
    "# Reflexio Embedded",
    "",
    "This agent has the openclaw-embedded plugin installed. Its SKILL.md",
    "describes how to capture user facts and corrections into .reflexio/.",
    "",
    "Load the skill when: user states a preference/fact/config, user corrects",
    "you and later confirms the fix, or you need to retrieve past context.",
  ].join("\n");
}

type TranscriptMessage = {
  role?: string;
  content?: unknown;
  timestamp?: string;
};

/**
 * Redact obvious secrets before the transcript leaves the host for the
 * extractor sub-agent (which calls the configured LLM provider). This is a
 * best-effort scrub, not a guarantee — see SECURITY.md. Patterns here target
 * high-confidence matches; anything subtler must be avoided by the user.
 */
const REDACTION_PATTERNS: ReadonlyArray<[RegExp, string]> = [
  // Private key blocks (PEM)
  [
    /-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----/g,
    "[REDACTED_PRIVATE_KEY]",
  ],
  // Vendor-prefixed tokens: OpenAI, Anthropic, GitHub, GitLab, Slack, Stripe, etc.
  [/\bsk-ant-[A-Za-z0-9_-]{20,}/g, "[REDACTED_ANTHROPIC_KEY]"],
  [/\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}/g, "[REDACTED_OPENAI_KEY]"],
  [/\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}/g, "[REDACTED_GITHUB_TOKEN]"],
  [/\bglpat-[A-Za-z0-9_-]{20,}/g, "[REDACTED_GITLAB_TOKEN]"],
  [/\bxox[abpors]-[A-Za-z0-9-]{10,}/g, "[REDACTED_SLACK_TOKEN]"],
  [/\bAKIA[0-9A-Z]{16}\b/g, "[REDACTED_AWS_ACCESS_KEY]"],
  [/\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{20,}/g, "[REDACTED_STRIPE_KEY]"],
  // Bearer tokens in headers
  [/\b[Bb]earer\s+[A-Za-z0-9._~+\/-]{20,}=*/g, "Bearer [REDACTED_TOKEN]"],
  [
    /\b[Aa]uthorization:\s*[A-Za-z]+\s+[A-Za-z0-9._~+\/-]{8,}=*/g,
    "Authorization: [REDACTED]",
  ],
  // KEY=value / KEY: value for common secret-looking names
  // (match through end-of-line; keep quotes intact for readability)
  [
    /\b([A-Z][A-Z0-9_]*(?:PASSWORD|PASSWD|SECRET|TOKEN|API_KEY|APIKEY|PRIVATE_KEY|ACCESS_KEY|AUTH))\s*[:=]\s*["']?[^\s"'\n]+["']?/g,
    "$1=[REDACTED]",
  ],
  // JWTs: three base64url segments joined by dots
  [
    /\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}/g,
    "[REDACTED_JWT]",
  ],
];

export function redactSecrets(text: string): string {
  let out = text;
  for (const [pattern, replacement] of REDACTION_PATTERNS) {
    out = out.replace(pattern, replacement);
  }
  return out;
}

/** Decide whether the current transcript is worth extracting from. */
function transcriptWorthExtracting(messages: unknown[] | undefined): boolean {
  if (!Array.isArray(messages) || messages.length < 2) return false;
  return messages.some((m) => (m as TranscriptMessage).role === "user");
}

/** Serialize transcript into a plain-text form suitable for the sub-agent task prompt. */
function serializeTranscript(messages: unknown[] | undefined): string {
  if (!Array.isArray(messages)) return "";
  return messages
    .map((raw) => {
      const m = raw as TranscriptMessage;
      const role = m.role ?? "unknown";
      const rawContent =
        typeof m.content === "string" ? m.content : JSON.stringify(m.content);
      const content = redactSecrets(rawContent);
      const ts = m.timestamp ? ` [${m.timestamp}]` : "";
      return `### ${role}${ts}\n${content}`;
    })
    .join("\n\n");
}

/**
 * Build the task prompt handed to the reflexio-extractor sub-agent. The
 * sub-agent's system prompt already contains its workflow (from
 * agents/reflexio-extractor.md). This prompt just provides the transcript and
 * reminds it of its job.
 */
function buildExtractionTaskPrompt(
  messages: unknown[] | undefined,
  sessionFile: string | undefined,
): string {
  const parts = [
    "Run your extraction workflow on the recent transcript.",
    "",
    "Follow your system prompt: extract profiles and playbooks, then run shallow pairwise dedup against existing .reflexio/ entries.",
    "",
  ];
  const transcript = serializeTranscript(messages);
  if (transcript) {
    parts.push("## Transcript", "", transcript);
  } else if (sessionFile) {
    parts.push(
      "## Transcript",
      "",
      `The transcript lives on disk at: ${sessionFile}`,
      "Read that file to reconstruct the session.",
    );
  } else {
    parts.push(
      "## Transcript",
      "",
      "No in-memory transcript is available for this event; skip if you cannot find a session file.",
    );
  }
  return parts.join("\n");
}

export type SpawnExtractorParams = {
  runtime: SubagentRuntime | undefined;
  workspaceDir?: string;
  sessionKey?: string;
  messages?: unknown[];
  sessionFile?: string;
  log?: Logger;
  reason: string;
};

/**
 * Fire-and-forget spawn of the reflexio-extractor sub-agent. The caller should
 * NOT await the run itself — Openclaw manages the lifecycle via its Background
 * Tasks ledger.
 *
 * Returns the runId when the spawn succeeds (caller can await the spawn to be
 * sure the request reached the runtime, but not the sub-agent's completion).
 */
export async function spawnExtractor(
  params: SpawnExtractorParams,
): Promise<string | undefined> {
  const { runtime, sessionKey, messages, sessionFile, log, reason } = params;

  if (!transcriptWorthExtracting(messages) && !sessionFile) {
    return undefined;
  }
  const runFn = runtime?.subagent?.run;
  if (!runFn) {
    log?.warn?.(
      "[reflexio-embedded] runtime.subagent.run unavailable; skipping extraction",
    );
    return undefined;
  }

  // Session-key namespacing: each extractor run gets its own sub-session so
  // the parent session transcript is not polluted.
  const childSessionKey = `reflexio-extractor:${sessionKey ?? "unknown"}:${Date.now()}`;
  const message = buildExtractionTaskPrompt(messages, sessionFile);

  try {
    const result = await runFn({
      sessionKey: childSessionKey,
      message,
      lane: "reflexio-extractor",
      idempotencyKey: `${reason}:${childSessionKey}`,
    });
    log?.info?.(
      `[reflexio-embedded] extractor spawned (runId=${result.runId}, reason=${reason})`,
    );
    return result.runId;
  } catch (err) {
    log?.error?.(
      `[reflexio-embedded] failed to spawn extractor (reason=${reason}): ${err}`,
    );
    return undefined;
  }
}
