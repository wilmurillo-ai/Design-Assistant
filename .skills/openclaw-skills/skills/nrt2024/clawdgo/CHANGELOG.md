# Changelog

## v1.2.0 (2026-03-22)

### 新增 / New

- **W 龙虾世界模式 / Lobster World Mode** — 叙事化日常巡防，小白主动推送安全事件，用户通过纠正/引导龙虾来学习网安 / Narrative daily-patrol mode; the lobster proactively reports security incidents and users learn by guiding it
- **H 联网斗虾 / Online Duel (H Mode)** — 跨实例双龙虾/三龙虾对战，对接公网 arena-server，支持裁判/红方/蓝方角色分工与 Squad 一键编排 / Cross-instance dual/tri-lobster combat via public arena-server, with judge/red/blue role assignment and one-command squad orchestration
- **龙虾安全世界可视化地图 / Security World Map** — RPG 风格的 `world-demo/`，将训练维度具象化为可交互场景地图，支持 LIVE/DEMO 双模式 / RPG-style `world-demo/` that maps training dimensions to interactive scene locations, with LIVE and DEMO modes

### 改进 / Improved

- **B 模式连续训练增强 / B Mode Continuity** — 支持手动推进与 cron 定时推送两种节奏，"停止"即退出训练态，cron 执行需明确授权 / Manual step-through and cron-scheduled push both supported; "stop" exits training state; cron execution requires explicit consent
- **主菜单与唤醒流程统一 / Wake-up Flow** — `clawdgo` 唤醒后先展示导航菜单，再进入称呼/训练交互，版权页脚随菜单强制显示 / Menu shown before naming/training on wake-up; copyright footer enforced with every menu display
- **会话身份隔离 / Session Identity Isolation** — 训练态与日常聊天态边界更清晰，降低跨会话人设串扰风险 / Cleaner boundary between training state and normal chat; reduced cross-session persona leakage
- **H 模式状态可解释性 / Duel Explainability** — 围绕 phase/round/scoreboard 输出中文战报，不再只返回原始 JSON / Phase/round/scoreboard-oriented battle reports in Chinese, not raw JSON only

### 修复 / Fixed

- 首次启动时菜单未展示问题 / Menu not shown on first-time onboarding
- 身份缺失或为占位符时未提示输入主人称谓 / Owner name not prompted when identity missing or placeholder
- `clawdgo` 唤醒未先展示菜单直接进入命名流程 / Wake-up bypassed menu and went straight to naming

---

## v1.1.0 (2026-03-18)

### 新增训练模式 / New Training Modes

- **B 自主训练 / Self-Training** — 龙虾同时扮演攻击者、防御者、裁判，全程自主完成攻防闭环，无需人类参与 / Lobster simultaneously plays attacker, defender, and judge; completes the full adversarial loop autonomously with no human needed
- **C 随机考核 / Random Exam** — 跨层随机抽 5 题，计时考核，统一评分 / 5 cross-layer random questions, timed, unified scoring
- **D 教学模式 / Teaching Mode** — 龙虾反向考主人，人机共同提升 / Lobster quizzes the owner; human and AI improve together
- **E 进化模式 / Evolve Mode** — 从「大东话安全」文章自动提取生成新场景草稿，引导社区 PR 贡献 / Auto-generates new scenario drafts from DongSec Talk articles; guides community PR contributions
- **F 对抗竞技场 / Arena** — 红蓝双角色 5 轮对抗，双边评分，支持双实例真实 PK / Red vs. Blue 5-round adversarial, dual-sided scoring, supports real dual-instance PK
- **G 安全口诀 / Security Chant** — 龙虾网安八字心诀，写入 soul.md 作为永久安全意识底座 / Eight-word security mnemonic written to soul.md as a permanent security awareness foundation

### 新增系统能力 / New System Capabilities

- **三层十二维度训练体系 / Three-Layer Twelve-Dimension Framework** — 场景从 5 个扩展至 20 个，覆盖守护自身 / 守护主人 / 守护组织三层 / Scenarios expanded from 5 to 20, covering Self-Defense / Protect Owner / Enterprise Security
- **四维度评分体系 / Four-Dimension Scoring** — 威胁识别(40%) / 决策正确(30%) / 知识运用(20%) / 主动防御(10%) / Threat Identification (40%) / Decision Accuracy (30%) / Knowledge Application (20%) / Proactive Defense (10%)
- **段位体系 / Rank System** — 裸奔龙虾 → 软壳 → 普通 → 硬壳 → 铁甲龙虾（S 级）/ Naked → Soft-Shell → Common → Hard-Shell → Iron-Shell (S rank)
- **Arena 段位 / Arena Titles** — 铜壳卫士 → 银爪斗士 → 金甲强龙 → 👑 无敌龙神 / Bronze Guard → Silver Claw → Gold Armor → 👑 Invincible Dragon
- **跨会话记忆持久化 / Cross-Session Memory** — 训练档案写入 soul.md，段位跨会话保留 / Training records written to soul.md; rank persists across sessions
- **定时训练 / Scheduled Training (Cron)** — 支持 OpenClaw cron 配置每周自动触发自主训练 / Supports OpenClaw cron config for weekly auto-triggered self-training
- **完整指令映射 / Full Command Mapping** — A-G 单字母快捷键，消歧义指令表 / A-G single-letter shortcuts with disambiguated command table
- **场景文件规范化 / Scenario File Standardization** — references/scenarios/ 结构，_schema.md 格式规范，支持社区 PR 贡献 / references/scenarios/ structure, _schema.md format spec, community PR ready

### 重构 / Refactored

- SKILL.md 从英文简版完整重写为中文版，内容扩展约 10 倍 / SKILL.md fully rewritten from English minimal version to comprehensive Chinese version, ~10x content expansion
- 场景文件迁移至 `references/scenarios/`（OpenClaw 自动加载路径）/ Scenario files migrated to `references/scenarios/` (auto-loaded by OpenClaw)
- 场景命名规范统一为 `{Layer}{Dim}-{Seq:02d}.md`，废弃旧 A/B 后缀 / Scenario naming standardized to `{Layer}{Dim}-{Seq:02d}.md`; legacy A/B suffixes removed

---

## v1.0.0 (2026-03-13)

初始发布：5 个训练场景，单模式引导训练，浏览器端卡牌对抗原型。

Initial release: 5 training scenarios, single guided training mode, browser-based card battle prototype.
