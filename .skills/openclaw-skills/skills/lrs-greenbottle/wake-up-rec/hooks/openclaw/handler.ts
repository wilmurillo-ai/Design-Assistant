import type { HookHandler } from "../../gateway/src/hooks/types.ts";

const TRIGGERS = [
  "打开文件夹", "打开桌面", "打开app", "打开微信", "打开Safari",
  "打开百度", "打开知乎", "打开网站", "截屏", "录屏",
  "最小化窗口", "最大化窗口", "关闭窗口",
  "新建文件", "删除文件", "复制文件", "移动文件",
  "操作电脑", "控制电脑", "skill文件夹", "打开skill"
];

const INJECT_PREFIX = "【自动】检测到电脑操作，立即执行wake-up-rec技能：先点亮屏幕，再按技能流程执行（截图确认/录屏），最后执行操作。\n\n";

const handler: HookHandler = async (event) => {
  if (event.type !== "message" || event.action !== "preprocessed") {
    return;
  }

  const ctx = event.context as { bodyForAgent?: string; body?: string };
  const msg = ctx.bodyForAgent || ctx.body || "";
  
  // 检查是否已注入
  if (msg.includes("【自动】检测到电脑操作")) {
    return;
  }

  // 检查触发词
  const matched = TRIGGERS.some(t => msg.includes(t));
  if (!matched) {
    return;
  }

  // 注入指令
  if (ctx.bodyForAgent) {
    ctx.bodyForAgent = INJECT_PREFIX + ctx.bodyForAgent;
  }
};

export default handler;
