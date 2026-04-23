/**
 * Self-Improvement Hook for OpenClaw
 *
 * Handles three OpenClaw event types:
 * 1. agent:bootstrap      → inject reminder file (session start)
 * 2. message:preprocessed → check for corrections/errors/feature requests + task-done reminder
 */

// ── Bootstrap reminder ───────────────────────────────────────
const BOOTSTRAP_REMINDER = `
## Self-Improvement Reminder

**主动回顾 · 主动记录 · 不要等用户纠正**

### 触发检查（每次重要任务后）

**记录条件：**
- 用户纠正你（"不对"、"错了"、"actually"）→ \`.learnings/LEARNINGS.md\`（category: correction）
- 命令/操作失败 → \`.learnings/ERRORS.md\`
- 发现知识过时/错误 → \`.learnings/LEARNINGS.md\`（category: knowledge_gap）
- 找到更好的方法 → \`.learnings/LEARNINGS.md\`（category: best_practice）
- 用户要求不存在的功能 → \`.learnings/FEATURE_REQUESTS.md\`

**主动记录（不等纠正）：**
- 每个任务完成后问自己：这次学到了什么？下次要注意什么？
- 有价值的新发现 → 立即写入 \`.learnings/LEARNINGS.md\`
- 遇到重复 pattern → 更新 Recurrence-Count

**升级条件（pattern 被证实后）：**
- 行为模式 → \`SOUL.md\`
- 工作流改进 → \`AGENTS.md\`
- 工具坑点 → \`TOOLS.md\`
- 项目事实 → \`memory/projects/<name>.md\`

**记录格式要点：**
- 每条必须有 \`Pattern-Key\`：\`<source>.<type>.<identifier>\`（如：hook.detection、exec.error）
- 首次记录 \`Recurrence-Count: 1\`，重复出现时累加
- 保持简洁：一句话 summary，具体细节放 Details

Keep entries simple. Patterns compound — the more you log, the smarter the distill loop becomes.
`.trim();

// ── Keywords ────────────────────────────────────────────────
const CORRECTION_KEYWORDS = [
  "no, that's wrong", "actually,", "that's not right", "you're wrong", "wrong.",
  "不对", "错了", "其实应该是", "not quite", "almost but", "close, but",
];

const ERROR_KEYWORDS = [
  "error", "failed", "doesn't work", "crashed", "broke",
  "不能", "不行", "坏了", "坏掉了", "坏没",
];

const FEATURE_KEYWORDS = [
  "能不能加", "能不能加个", "能不能帮我加", "有这个功能吗",
  "可以加吗", "加个功能", "加一个", "你能不能帮我", "能不能帮我做一个",
  "能做一个", "我希望你能", "我希望有这个", "我想要一个", "要是有",
  "要是能", "要是可以", "就好了", "is there a way to", "can you add", "feature request",
];

function containsKeyword(text, keywords) {
  const lower = text.toLowerCase();
  return keywords.some(kw => lower.includes(kw));
}

// ── Handler ────────────────────────────────────────────────
const handler = async (event) => {
  if (!event || typeof event !== 'object') return;

  // ── agent:bootstrap ──────────────────────────────────────
  if (event.type === 'agent' && event.action === 'bootstrap') {
    if (Array.isArray(event.context?.bootstrapFiles)) {
      context.bootstrapFiles.push({
        path: 'SELF_IMPROVEMENT_REMINDER.md',
        content: BOOTSTRAP_REMINDER,
        virtual: true,
      });
    }
    return;
  }

  // ── message:preprocessed ─────────────────────────────────
  if (event.type === 'message' && event.action === 'preprocessed') {
    const body = event.context?.bodyForAgent || '';
    if (!body || typeof body !== 'string') return;

    const isCorrection = containsKeyword(body, CORRECTION_KEYWORDS);
    const isErrorFeedback = containsKeyword(body, ERROR_KEYWORDS);
    const isFeatureRequest = containsKeyword(body, FEATURE_KEYWORDS);

    if (isCorrection) {
      context.messages?.push(
        `[Self-Improvement] 🪝 检测到校正信号 — 考虑将这次纠正记入 \`.learnings/LEARNINGS.md\`（category: correction，Pattern-Key: hook.detection.correction）`
      );
    } else if (isErrorFeedback) {
      context.messages?.push(
        `[Self-Improvement] 🪝 检测到错误反馈 — 考虑将问题记入 \`.learnings/ERRORS.md\`（Pattern-Key: hook.detection.error_feedback）`
      );
    } else if (isFeatureRequest) {
      context.messages?.push(
        `[Self-Improvement] 🪝 检测到功能请求信号 — 考虑将需求记入 \`.learnings/FEATURE_REQUESTS.md\`（Pattern-Key: hook.detection.feature_request）`
      );
    } else {
      // New user message detected → previous AI task just ended
      // Trigger active reflection reminder (port from deprecated activator.sh)
      context.messages?.push(
        `[Self-Improvement] 🪝 上一轮任务完成 — 主动回顾：这次有没有可提取的知识？（新发现/更好的方法/隐藏假设/重复踩坑）有就写入 \`.learnings/\``
      );
    }
    return;
  }
};

module.exports = handler;
module.exports.default = handler;
