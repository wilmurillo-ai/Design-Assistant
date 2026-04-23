// OpenClaw Hook Handler - agent:bootstrap
// 注入睡眠脑波 Skill 提示词

export default function handler(event) {
  return {
    inject: `
## 睡眠脑波声疗助手
当用户提到播放睡眠音频、脑波、入睡困难、易醒、焦虑失眠、浅眠多梦等关键词时，
请读取 skill/SKILL.md 并按照其中指引处理。从 audio_library/manifest.json 获取音频 URL。
回复必须附加合规声明：温馨提示：本音频为非药物健康辅助，不替代医疗诊断与治疗。
`,
  };
}
