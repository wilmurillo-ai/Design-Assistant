# family-baby-asistant

基于 OpenClaw / Codex Skill 的家庭宝贝协作技能。

这个仓库现在是 `family-cultivation-coach` 的独立维护仓库。它的目标不是输出泛泛育儿建议，而是把孩子画像、家庭约束、培养目标和执行偏好整理成真实可执行的每周培养课表。

## Skill

- 名称：`family-cultivation-coach`
- 中文名：家庭培养协作官
- 入口文件：`SKILL.md`
- 默认打包格式：`.skill`

## 适合场景

- 整理孩子画像和家庭作息
- 生成每周培养课表
- 处理兴趣班、陪伴时间、学习任务之间的冲突
- 设计可执行的游戏化激励
- 每日 20:00 生成速记卡，支持数字 + 字母快速记录
- 回复速记卡后自动生成日报
- 每周复盘前检查记录完整性
- 支持飞书多维表格和 Notion 两种记录后端
- 基于新约束做增量调整

## 目录结构

```text
.
├── SKILL.md
├── skill.json
├── rules/
├── templates/
├── examples/
├── USER_GUIDE.md
├── DEVELOPMENT_LOG.md
├── feishu_config.example.md
├── README.md
└── LICENSE
```

## 使用方式

支持目录式 skill 的工具可以直接把本仓库作为 skill 目录使用，或者复制到本地 skill 目录：

```bash
mkdir -p ~/.codex/skills/family-cultivation-coach
cp -R ./* ~/.codex/skills/family-cultivation-coach/
```

首次验证建议显式点名：

```text
$family-cultivation-coach 帮我根据孩子课表和家庭作息生成一版每周培养计划
```

## 飞书配置提醒

安装 Skill 后不会自动弹出配置向导。首次启用飞书多维表格、每日速记卡、日报推送或 OpenClaw 定时能力前，请先完成本地配置：

```bash
cp feishu_config.example.md feishu_config.md
```

然后在 `feishu_config.md` 中填入自己的飞书域名、App Token 和各表 Table ID。`feishu_config.md` 是本地私有文件，已加入 `.gitignore`，不要提交到公开仓库。

如果没有飞书机器人环境，可以先使用 Notion 模式，或只使用课表生成和每周复盘模板。

## 维护规则

- `SKILL.md` 是主入口。
- `skill.json` 是机器可读元数据。
- `rules/` 放排程和奖励规则。
- `templates/` 放可复用输出模板。
- `examples/` 放示例输入输出。
- `USER_GUIDE.md` 放日常使用方式，包含速记卡、日报和周复盘。
- `DEVELOPMENT_LOG.md` 保留开发过程和产品决策记录。
- `feishu_config.example.md` 放飞书多维表格配置模板；真实 `feishu_config.md` 为本地私有文件，不提交公开仓库。
- 修改核心能力后，同步更新 README 和示例。
