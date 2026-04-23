# micro-change-helper 本地验证记录

**日期**：2026-03-25
**目标**：验证 `micro-change-helper` 是否满足 OpenClaw 本地 skill 的最小目录结构要求。

## 验证对象

源目录：
- `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/openclawhaidong/agents/micro-change-helper/`

测试目录：
- `~/.openclaw/workspace/skills/micro-change-helper/`

## 验证步骤

1. 检查 OpenClaw 本地 skills workspace 是否存在。
2. 读取 OpenClaw skill 教程，确认最小要求为：
   - 一个 skill 目录
   - 一个 `SKILL.md`
3. 将 `micro-change-helper` 复制到本地 workspace。
4. 检查复制后的目录结构。

## 验证结果

### 结果：通过（最小结构验证）

复制后的目录包含：
- `SKILL.md`
- `_meta.json`

说明：
- 已满足教程中“一 skill 一目录 + 一个 `SKILL.md`”的最小结构要求
- 额外已有 `_meta.json`，可作为后续发布草稿元数据
- 当前未做真实执行级测试，也未做发布测试

## 当前结论

`micro-change-helper` 已经可以视为一个**本地可识别的 OpenClaw skill 草稿**。

## 尚未验证的部分

1. OpenClaw 是否能在真实运行中加载并调用该 skill
2. `SKILL.md` 文案是否需要进一步贴近平台 prompt 风格
3. `_meta.json` 字段是否与真实发布器完全一致
4. 是否需要 `README.md` / `SKILL_EN.md` / `version` 等扩展文件

## 下一步建议

### 路线 A（继续最小验证）
尝试在本地 OpenClaw workflow 中手动调用或安装这个 skill，验证实际可用性。

### 路线 B（补齐发布惯例）
参考现有 workspace 内较完整 skill（如 `learning-planner/`），继续补：
- `README.md`
- `SKILL_EN.md`
- `version`
- `test.sh`

### 路线 C（批量迁移）
如果这个流程没问题，可以把另外 4 个 skill 也同步进 `~/.openclaw/workspace/skills/`。