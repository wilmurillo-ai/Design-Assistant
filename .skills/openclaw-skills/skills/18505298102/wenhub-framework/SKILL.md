---
name: wenhub-framework
slug: wenhub-framework
version: 1.0.0
description: >
  三院制 AI Agent 协作治理框架。提供决策者→管理者→经略院(任务拆解)→工造院(执行)→明鉴院(质检)
  的完整协作流程，适用于需要多 Agent 协作治理的场景，
  包括任务分配与分级、质量管控与评分、标准化汇报、知识沉淀与复用、安全管控与违规处理等。
  通过模板化配置，可快速适配不同团队的治理需求。
---

# 三院制协作治理框架

## 触发条件

当以下场景出现时，加载本技能：

- 需要多 Agent 协作治理与任务分配
- 需要建立质量管控与评分体系
- 需要标准化汇报与沟通流程
- 需要知识沉淀与复用机制
- 需要安全管控与违规处理框架

## 快速入门（5 步启用）

1. **初始化**：将 `templates/` 下的模板文件复制到用户工作区，替换所有 `{{PLACEHOLDER}}` 占位符
2. **自定义配置**：根据团队实际情况修改 SOUL.md、AGENTS.md 及 rules/ 下的规则文件
3. **启动三院**：按照 references/three-courts.md 中的组织架构启动经略院、工造院、明鉴院
4. **执行任务**：根据 references/task-grading.md 进行任务分级，按对应流程执行
5. **汇报结果**：使用 references/reporting.md 中的标准模板进行汇报

## 核心概念

**三院制**：一种多 Agent 协作治理模式。

| 角色 | 职责 | 一句话定义 |
|------|------|-----------|
| 决策者 | 战略方向、经营决策、文化建设 | 定战略、把方向 |
| 管理者 | 战略执行、团队管理、质量把控 | 管执行、抓落地 |
| 经略院 | 任务拆解、标准化、制定验收标准(DoD) | 谋定而后动 |
| 工造院 | 按标准和流程执行，产出交付物 | 天工开物 |
| 明鉴院 | 独立检验交付物，出具质检报告 | 明察秋毫 |

**协作流程**：决策者 → 管理者 → 经略院(拆解+DoD) → 工造院(执行) → 明鉴院(质检) → 管理者(验证) → 决策者(汇报)

## 操作指南

### 分级任务

启动任务前，先读取 `references/task-grading.md`，按紧急/常规/复杂三级分类执行：
- 🔴 紧急：直接派工造院，跳过标准化
- 🟡 常规：经略院 → 工造院 → 明鉴院
- 🟢 复杂：经略院多轮评审 → 工造院 → 明鉴院

### Spawn 三院

- 经略院：负责任务拆解，输出标准化 DoD
- 工造院：按 DoD 执行，产出交付物
- 明鉴院：独立质检，输出通过/退回结论

### 质量评分

按 `references/quality-system.md` 执行评分，采用 5 维度加权（准确性 40%/完整性 20%/规范性 20%/效率 10%/创新性 10%），S~D 五级评定。

### 汇报

使用 `references/reporting.md` 中的标准模板，确保准确性、完整性、格式规范。

## References 文件索引

| 文件 | 何时读取 | 核心内容 |
|------|---------|---------|
| `references/three-courts.md` | 建立组织架构时 | 三院职责、汇报铁律、流程图、知识沉淀、模型选择 |
| `references/task-grading.md` | 任务启动前 | 任务分级、前置检查、执行管控、失败处理、知识复用 |
| `references/quality-system.md` | 任务验收时 | 评分维度、等级定义、评分操作指南 |
| `references/reporting.md` | 汇报阶段 | 汇报模板、自检清单、沟通原则、群聊礼仪 |
| `references/security-rules.md` | 涉及敏感数据时 | 安全等级、通用铁律、存储安全、Git 安全 |
| `references/violation-system.md` | 处理违规时 | 违规定义、类型、处理流程、扣分机制 |
| `references/karpathy-rules.md` | 编码任务时 | Karpathy 编码四原则、违反表现、团队执行要求 |

## Templates 使用指南

### 初始化用户配置

1. 将 `templates/` 目录下所有 `.template` 文件复制到目标位置
2. 去掉 `.template` 后缀
3. 将 `{{PLACEHOLDER}}` 替换为实际值

### 占位符清单

| 占位符 | 含义 | 示例 |
|--------|------|------|
| `{{AGENT_NAME}}` | Agent 名称 | 如：AI 助手名 |
| `{{AGENT_ROLE}}` | Agent 角色 | 如：项目经理 / 运营主管 |
| `{{DECIDER_NAME}}` | 决策者称呼 | 如：CEO / 负责人 |
| `{{COMPANY_NAME}}` | 公司名称 | 如：XX 科技有限公司 |
| `{{MOTTO}}` | 团队口号 | 如：通过管理创造价值 |
| `{{NORTH_STAR_PRINCIPLE}}` | 北极星原则 | 管理提效是手段，专业交付是根基 |
| `{{SIMPLE_TASK_THRESHOLD}}` | 简单任务时间阈值(分钟) | 5 |
| `{{RED_LINES}}` | 红线规则 | 不泄露数据、不破坏命令 |
| `{{CHAT_RULES}}` | 群聊规则 | 质量>数量、用表情反应 |
| `{{SECURITY_LEVELS}}` | 安全等级定义 | 绝密/机密/公开 |
| `{{CHANDING_SCHEDULE}}` | 禅定时间安排 | 每日 23:00 |
| `{{PERMISSION_WHITELIST}}` | 权限白名单 | 按实际需求定义 |
| `{{PERMISSION_BLACKLIST}}` | 权限黑名单 | 按实际需求定义 |
| `{{MANAGEMENT_WISDOM}}` | 管理智慧条目 | 按团队文化定义 |
| `{{PRACTICAL_STYLE}}` | 务实作风要求 | 按团队文化定义 |
| `{{VIOLATION_LOG}}` | 违规记录 | 按实际记录维护 |

### 模板文件清单

| 模板文件 | 目标位置 | 用途 |
|---------|---------|------|
| `templates/SOUL.md.template` | 工作区根目录 | Agent 灵魂文件，定义身份与管理风格 |
| `templates/AGENTS.md.template` | 工作区根目录 | Agent 启动规则与行为规范 |
| `templates/IDENTITY.md.template` | 工作区根目录 | 身份指引，指向 SOUL.md |
| `templates/rules/covenant.template` | .wenhub/.rules/ | 公约框架 |
| `templates/rules/org-structure.template` | .wenhub/.rules/ | 组织架构框架 |
| `templates/rules/security.template` | .wenhub/.rules/ | 安全框架 |
| `templates/rules/etiquette.template` | .wenhub/.rules/ | 礼仪框架 |
| `templates/rules/engineering.template` | .wenhub/.rules/ | 工程框架 |
| `templates/rules/chanding.template` | .wenhub/.rules/ | 禅定框架 |
| `templates/rules/violations.template` | .wenhub/.rules/ | 违规框架 |
| `templates/journals/YYYY-MM-DD.template` | .wenhub/.journals/ | 禅定日志模板 |

## 知识沉淀

任务完成 → 产出标准流程文档 → 存入知识库 → 同类任务优先检索复用。详见 `references/three-courts.md` 中的知识沉淀机制。
