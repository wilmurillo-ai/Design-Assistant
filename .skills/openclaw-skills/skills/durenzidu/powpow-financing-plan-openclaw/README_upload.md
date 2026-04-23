# PowPow 投融资技能上传包使用说明

本包包含可上传至 OpenClaw 与 ClawHub 的完整数据 Asset，包含结构化技能 JSON、兼容 ClawHub 的模板、上传说明及哈希占位文件。

## 包内容结构
- openclaw_skill.json: OpenClaw 原始技能 JSON，结构化定义 PowPow 投融资技能。
- clawhub_skill.json: ClawHub 兼容模板 JSON，字段与 OpenClaw 对应，便于跨平台上传。
- SKILL.md: 技术文档，包含字段定义、结构、对照表。
- SKILL.md 已替代 source_hash.sha256 的哈希校验需求，请参考 SKILL.md 的上传与验证部分。
- manifest.json: 打包清单，描述包内文件。

## 上传步骤（快速版）
1) 打包：确保以下文件在打包根目录下（不要多级目录嵌套）：
   - package/openclaw_skill.json
   - package/clawhub_skill.json
   - package/SKILL.md
   - package/manifest.json

2) 上传：到 clawhub.ai/upload，选择你的包进行上传（ZIP）。

3) 验证：使用 ClawHub 的预览功能验证对话触发与结构显示是否符合预期。

4) 更新：如需版本迭代，修改版本号并重新打包上传。

如需，我可以为你生成一个一键打包与哈希替换的脚本，帮助你在本地自动完成打包与上传准备。 
