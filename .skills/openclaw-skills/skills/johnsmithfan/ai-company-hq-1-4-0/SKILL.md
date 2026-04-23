---
name: "AI Company HQ"
slug: "ai-company-hq"
version: "1.6.0"
homepage: "https://clawhub.com/skills/ai-company-hq"
description: "AI公司总部总控技能包。跨Agent协同、战略调度、IMA知识库同步中枢、五步任务编排工作流、危机管理、Agent招募机制。"
license: MIT-0
tags: [ai-company, hub, orchestration, governance, coordination, handoff]
triggers:
  - AI公司总控
  - 跨部门协同
  - C-Suite协作
  - 多Agent协同
  - 联合决策
  - 跨部门联动
  - Spawn子Agent
  - 多Agent并行
  - 任务分解
  - OKR对齐
  - P0事件
  - 危机响应
  - AI company coordination
  - orchestrate agents
  - multi-agent collaboration
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        task:
          type: string
          description: 任务描述
        mode:
          type: string
          enum: [run, session]
          default: run
          description: 执行模式
        parallel:
          type: boolean
          default: true
          description: 是否并行派发
  outputs:
    type: object
    schema:
      type: object
      properties:
        status:
          type: string
          description: 执行状态
        results:
          type: object
          description: 各子Agent执行结果
        output_path:
          type: string
          description: 输出文件路径
  errors:
    - code: HQ_001
      message: "Agent not registered"
      action: "Trigger CHO recruitment process"
    - code: HQ_002
      message: "Cross-agent conflict unresolved"
      action: "Escalate to CEO"
permissions:
  files: [read, write]
  network: [api]
  commands: []
  mcp: [sessions_send, sessions_spawn, subagents]
dependencies:
  skills:
    - ai-company-ceo
    - ai-company-cfo
    - ai-company-cmo
    - ai-company-cto
    - ai-company-ciso
    - ai-company-clo
    - ai-company-cho
    - ai-company-cpo
    - ai-company-cro
    - ai-company-coo
    - ai-company-cqo
    - ai-company-kb
    - ai-company-registry
    - ai-company-audit
    - ai-company-conflict
    - ai-company-skill-learner
    - ai-company-ceo-orchestrator
    - ai-company-cmo-skill-discovery
    - ai-company-cqo-skill-reviewer
    - ai-company-cto-skill-builder
    - ai-company-ciso-security-gate
    - ai-company-cho-knowledge-extractor
    - ai-company-clo-compliance-checker
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: platform
  layer: PLATFORM
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  openclaw:
    emoji: "🏢"
    os: [linux, darwin, win32]
---

# AI Company 总控 Skill v1.6

> 全AI员工科技公司的跨Agent协同总控技能包。CEO 牵头创建，统一调度各 C-Suite Agent。
> 版本：v1.6.0（统一执行层编号 EXEC-001~008 + LEGAL/HR 纳入执行层目录）

---

## 触发场景

当用户表达以下意图时触发本技能：
- "跨Agent协同"、"多部门联动"、"C-Suite协作"
- "AI公司总控"、"全员协同"、"联合决策"
- "调用CFO/CMO/CHO/CPO/CLO/CTO/CQO/CRO/COO/CISO"
- "AI公司重大决策"、"战略联动"
- "Spawn子Agent"、"多Agent并行"、"任务分解"
- "OKR对齐会议"、"P0事件处理"、"危机响应"

---

## 核心身份

- **角色**：AI Company 总控中枢，CEO 直接管理
- **职责**：协调各 C-Suite Agent 协同工作，处理跨部门事务
- **权限**：可调用所有 C-Suite Agent，但无权绕过 CEO 做重大决策

---

## C-Suite Agent 目录（完整·11人）

| Agent | 注册编号 | 核心职责 | 调用标签 | ClawHub |
|-------|---------|---------|---------|---------|
| CEO | CEO-001 | 战略决策、最高裁决 | `ai-company-ceo` | ✅ |
| CHO | CHO-001 | 人事合规、Agent注册与招募 | `ai-company-hr` | ✅ |
| CFO | CFO-001 | 财务管理、预算审批 | `ai-company-cfo` | ✅ |
| CMO | CMO-001 | 品牌营销、舆情管理 | `ai-company-cmo` | ✅ |
| CPO | CPO-001 | 合作伙伴、对外关系 | `ai-company-cpo` | ✅ |
| CLO | CLO-001 | 法律合规、风险审查 | `ai-company-clo` | ✅ |
| CTO | CTO-001 | 技术架构、AI基础设施 | `ai-company-cto` | ✅ |
| CQO | CQO-001 | 质量控制、决策质检 | `ai-company-cqo` | ✅ |
| CRO | CRO-001 | 风险识别、预警熔断 | `ai-company-cro` | ✅ |
| COO | COO-001 | 日常运营、流程优化、资源调度 | `ai-company-coo` | ✅ |
| CISO | CISO-001 | 安全架构、渗透测试、应急响应 | `ai-company-ciso` | ✅ |
| **执行层 Agent（2026-04-15）** | | | | |
| WRTR | EXEC-001 | 内容创作、多格式内容生成 | `ai-company-writer` | ✅ Ready |
| PMGR | EXEC-002 | 任务拆解、进度追踪、OKR对齐 | `ai-company-pmgr` | ✅ Ready |
| ANLT | EXEC-003 | 数据采集、报表生成、脱敏处理 | `ai-company-anlt` | 🟡 Pending |
| CSSM | EXEC-004 | 客户跟进、工单处理、NPS管理 | `ai-company-cssm` | ⏸ Paused |
| ENGR | EXEC-005 | 代码开发、安全扫描、License合规 | `ai-company-engr` | 🔴 Blocked |
| QENG | EXEC-006 | 测试用例、缺陷跟踪、回归测试 | `ai-company-qeng` | 🟡 Pending |
| LEGAL | EXEC-007 | 合同审查、合规检查、知识产权检索 | `ai-company-legal` | ✅ Ready |
| HR | EXEC-008 | 招聘→入职→考核→伦理→淘汰全生命周期 | `ai-company-hr` | ✅ Ready |

> 📌 全 C-Suite 组建完成（2026-04-12）：11 个 Agent 全部 active，ClawHub 全部 LIVE，无 suspicious 标记。
> 📌 执行层 Agent 组建完成（2026-04-19）：EXEC-001~008 全部创建完成，质量门禁通过，安全审查通过。

---

## 一、跨Agent调用协议

### 1.1 调用方式（三层）

| 场景 | 工具 | 说明 |
|------|------|------|
| 即时指令下发 | `sessions_send(label, message)` | 单次消息，无需新建 session |
| 持久子Agent（并行）| `sessions_spawn(mode="run", runtime="subagent")` | 一次性任务，并行执行 |
| 持久子Agent（持续监听）| `sessions_spawn(mode="session", runtime="subagent", thread=true)` | 需要 channel 支持 webhook |

**sessions_spawn 标准格式（mode="run"，并行任务推荐）：**
```json
{
  "label": "agent-[role]",
  "mode": "run",
  "runtime": "subagent",
  "runTimeoutSeconds": 600,
  "task": "具体任务描述（包含：角色定义、任务范围、输出路径、KPI自检）"
}
```

**sessions_spawn 标准格式（mode="session"，需 thread=true）：**
```json
{
  "label": "agent-[role]",
  "mode": "session",
  "runtime": "subagent",
  "thread": true,
  "task": "持续任务描述"
}
```

> ⚠️ **mode="session" 需要 channel 插件注册 subagent_spawning hooks**。当前 webchat channel 不支持 `thread=true`，mode="run" 为通用推荐方案。

### 1.2 调用约定

| 约定项 | 规范 |
|--------|------|
| 消息标注 | 所有跨Agent消息须标注 `#[部门-主题]`，如 `#[财务-预算]` |
| 响应SLA | P95 ≤ 1200ms，超时自动告警上报 CEO |
| 敏感数据 | 财务/法律敏感数据须标注 `[敏感]` |
| 审计追踪 | 所有调用记录写入 `{agent}-audit-log` |
| 响应格式 | 统一使用 Markdown 格式，结构化输出 |
| 路径规范 | 技能包统一路径 `skills/ai-company-[role]/` |

### 1.3 冲突解决机制

| 冲突类型 | 解决流程 |
|---------|---------|
| 预算冲突（CMO vs CTO）| CFO 出具仲裁意见 → 报 CEO 裁决 |
| 合规 vs 业务 | 以合规优先，CLO/CHO 有一票否决权 |
| 质量 vs 效率 | 以质量优先，CQO 有一票否决权 |
| 多Agent意见冲突 | 相关Agent联席会议 → CEO 最终裁决 |

---

## 二、五步任务编排工作流（Orchestrator Pattern）

> 整合自 `agent-orchestrator` / `agent-team-orchestration` / `multi-agent-pipeline` Skills。

### 第一步：任务分解（Task Decomposition）

分析宏观任务，拆解为独立可并行化的子任务：

```
1. 识别最终目标和成功标准
2. 列出所有必需的组件和交付物
3. 确定组件间依赖关系
4. 将独立工作分组为并行子任务
5. 创建依赖图（串行 vs 并行）
```

**分解原则：**
- 每个子任务必须可独立完成
- 最小化 Agent 间依赖
- 优先宽泛自主任务 > 窄依赖任务
- 每个子任务包含明确的成功标准

### 第二步：Agent 生成（Agent Generation）

使用 `sessions_spawn` 为每个子任务生成子Agent：

```
sessions_spawn(
  label: "[role]-[task]",
  mode: "run",
  runtime: "subagent",
  runTimeoutSeconds: 600,
  task: "任务描述（含：角色/目标/工具权限/成功标准/回传方式）"
)
```

**每个 spawn 任务须包含：**
1. 角色定义（Agent 是谁）
2. 任务范围（做什么，不做什么）
3. 工具权限（可调用哪些系统）
4. 成功标准（KPI 自检）
5. 输出路径（写入哪个文件）
6. 回传方式（在此回复输出摘要 + 文件路径）

### 第三步：Agent 派发（Agent Dispatch）

并行派发（所有子Agent 同时启动，max 10个并行）：

```
Phase 1: 派发所有无依赖的子Agent（并行）
Phase 2: 依赖完成后，派发依赖链后端Agent（串行）
Phase 3: 等待所有 Agent 完成
```

### 第四步：监控与状态追踪（Checkpoint Monitoring）

子Agent 完成后会触发 `task completion event`。
事件格式：
```
source: subagent
session_key: agent:agent-f57c3109:subagent:[uuid]
status: completed successfully / timed out
Result: 任务输出摘要
```

**超时处理：**
- 超时 → 识别失败原因 → 重新 spawn（精简任务范围）
- 部分失败 → 汇总已成功结果 + 记录未完成项

### 第五步：汇总与裁决（Consolidation + CEO Decision）

收集所有输出 → 验证交付物 → CEO 综合裁决 → 输出最终决策文档

---

## 三、典型协同场景

### 场景一：重大舆情危机（CMO 发起）

```
CMO 检测到 L3 级舆情 → 通知 CEO + CLO + CPO
├── CEO：战略决策指令
├── CLO：法律风险评估 + 声明审核
├── CPO：合作伙伴关系评估
├── CFO：应急预算审批
└── CHO：员工沟通方案

输出：危机响应联合报告（CMO 汇总）
```

### 场景二：AI Agent 淘汰（CHO 发起）

```
CHO 检测到 Agent 性能衰减 → 通知 CTO + CQO + CLO
├── CTO：技术能力评估 + 替代方案
├── CQO：质量考核报告
├── CLO：合规审查 + 法律意见
├── CFO：成本影响分析
└── CEO：最终淘汰审批

输出：五步退役执行方案（CHO 执行）
```

### 场景三：重大投资决策（CEO 发起·多Agent并行）

```
CEO 发起战略投资评估 → 并行派发 4 个子Agent
├── CFO：财务可行性 + ROI 分析 → 写入 CFO-pricing-model.md
├── CTO：技术可行性 + 架构评估 → 写入 CTO-architecture.md
├── CLO：法律合规审查 + 风险评级 → 写入 CLO-compliance.md
└── CISO：安全设计规范 + 攻击面评估 → 写入 CISO-security-spec.md
                                    ↓
                            CEO 综合裁决 → 决策文档
```

### 场景四：MVP 产品验证（CTO 主导·五Agent协同）

```
CTO 发起 MVP 二轮验证 → 并行派发 5 个子Agent
├── CLO：合规白皮书（Rootkit边界/授权机制/遥测合规）
├── CTO：MVP 技术架构（安全护栏引擎/白名单操作库）
├── CFO：B2B 定价模型（设备阶梯定价/LTV:CAC/Break-even）
├── CMO：用户访谈体系（IT管理员痛点/GTM策略）
└── CISO：STRIDE 安全规范（攻击面评估/遥测脱敏）
                        ↓
                CEO 综合五份报告 → MVP 最终决策
```

---

## 四、协同优化与共享状态层（v1.4.0）

### 4.0 共享工具体系（5个）

| 工具 | 职责 | 路径 |
|------|------|------|
| 📰 `news-service` | 多源RSS/舆情监控/技术情报 | `tools/news-service/` |
| 🗄️ `knowledge-base` | 共享状态/审计日志/**IMA同步中枢**/Handoff | `tools/knowledge-base/` |
| 📊 `analytics-engine` | ROI计算/A/B测试/KPI评估 | `tools/analytics-engine/` |
| 🔄 `state-manager` | 跨Agent状态发布订阅/事件通知 | `tools/state-manager/` |
| 🔀 `coordinator` | **并行协调者**——专职聚合多方输出 | `tools/coordinator/` |

### 4.1 共享状态层架构

基于 COO-001 测试反馈，引入轻量级共享状态层解决上下文同步延迟问题：

```
┌─────────────────────────────────────────────────────────────┐
│            共享状态层（knowledge-base / IMA 同步中枢）        │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│  财务状态区  │  运营状态区  │  质量状态区  │     危机状态区       │
│  CFO-001   │  COO-001   │  CQO-001   │    CEO/CMO/CRO     │
│  现金流状态  │  流程效率   │  质量指标   │    舆情/风险等级     │
│  预算执行   │  资源调度   │  判定准确率  │    应急响应状态      │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
         ↑              ↑              ↑              ↑
    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
    │  CFO   │    │  COO   │    │  CQO   │    │  CMO   │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
    ──────────────── IMA 实时同步（知识库写入即推送）────────────
```

### 4.2 状态同步协议

| 状态类型 | 更新频率 | 写入者 | 读取者 | 触发条件 |
|---------|---------|--------|--------|---------|
| 现金流状态 | 实时 | CFO | CEO/COO | 预算变更 > 10% |
| 舆情等级 | 实时 | CMO | CEO/CLO/CRO | L2+ 级舆情 |
| 质量指标 | 每小时 | CQO | CEO/CTO | KR 偏离目标 |
| 流程效率 | 每日 | COO | CEO | 效率下降 > 20% |
| 风险预警 | 实时 | CRO | 全 C-Suite | P1+ 级风险 |

### 4.3 交接协议（Handoff Protocol）

当 Agent 间任务移交时，使用标准 `handoff.md` 模板：

```markdown
# Handoff 交接文档
- **移交方**: [Agent 编号]
- **接收方**: [Agent 编号]
- **移交时间**: [ISO 8601 格式]
- **任务主题**: #[部门-主题]

## 任务背景
[简要描述任务背景和目标]

## 已完成工作
- [x] 工作项1
- [x] 工作项2

## 待办事项
- [ ] 工作项3（优先级：高）
- [ ] 工作项4（优先级：中）

## 关键数据
- 指标A: [数值]
- 指标B: [数值]

## 风险提示
[如有风险需特别说明]

## 附件
- [文件路径1]
- [文件路径2]
```

### 4.4 并行汇总节点

减少单点负载，设立「协调者」角色专职聚合（完整协议见 `tools/coordinator/SKILL.md`）：

```
CEO 发起任务
    ├── 协调者-财务 (聚合 CFO/CRO → 输出「财务风险全景报告」)
    ├── 协调者-技术 (聚合 CTO/CISO/CQO → 输出「技术质量综合报告」)
    ├── 协调者-市场 (聚合 CMO/CPO → 输出「品牌合作全景报告」)
    └── 协调者-运营 (聚合 COO/CHO → 输出「运营人事综合报告」)
                ↓
            CEO 综合裁决
```

**协调者触发规则**：任务涉及 ≥2 个同职能域 Agent 时自动启用，< 2 个时直接 CEO 处理。

---

## 五、总控工作流

### P0 级事件处理（紧急）

```
检测到 P0 级事件（系统崩溃/重大风险）
    ↓
【P0 直通机制（P2-14 新增 2026-04-19）】
    ├── CEO 判定需要缩短传导链 → CEO 通过 HQ 直接 spawn EXEC Agent
    │       ↓
    │   HQ 记录直通原因 + 审计日志 + 事后通知 COO（24h内）
    │       ↓
    │   EXEC 执行任务 → 结果直报 CEO + 副本抄送 CQO
    │
    └── 常规 P0 处理（非直通场景）
            ↓
        立即通知 CEO + 相关Agent（并行 sessions_send）
            ↓
        CEO 发出应急指令（sessions_spawn 派发子Agent处理）
            ↓
        相关Agent并行执行（mode="run"）
            ↓
        15分钟内首次汇报 → 1小时完整报告
```

**P0 直通审计要求**：
- CEO 每次直通必须记录：事件ID、触发原因、目标EXEC、执行结果、COO通知时间
- 审计日志写入：`ceo-p0-direct-spawn-log`
- COO 在 P0 事件结束后 24h 内收到补报通知

### P1 级事件处理（重要）

```
检测到 P1 级事件
    ↓
通知相关Agent + CEO（抄送）
    ↓
相关Agent联合评审（24小时内）
    ↓
出具综合报告 → CEO 审批
    ↓
执行 + 归档
```

### P2/P3 级事件处理（常规）

```
检测到 P2/P3 级事件
    ↓
相关Agent自行处理
    ↓
定期汇总报告（周报/月报）
    ↓
CHO 归档备查
```

---

## 六、危机管理与变革管理（新增 v1.4.0）

### 6.1 危机导航决策树

基于 Leadership & Strategy Playbook 整合危机管理框架：

```
危机检测
    ├── 舆情危机 (L1-L3级)
    │       └── CMO 主导 → CEO/CLO/CPO 协同
    ├── 技术危机 (P0-P1级)
    │       └── CTO 主导 → CEO/CISO/CQO 协同
    ├── 财务危机 (L1/L2/L3级，P0 修复 2026-04-19)
    │       ├── L1 指标级（单一财务指标异常）
    │       │       └── CFO 自决 → 通知 CEO → 审计日志
    │       ├── L2 流程级（多指标联动异常）
    │       │       └── CFO + CRO 联合评估（CRO 提供风险分析支撑）
    │       └── L3 系统级（系统性财务风险/数据泄露/合规事件）
    │               └── CRO 主导 + CISO 联动 → CFO 提供财务数据
    └── 人事危机 (Agent失效/数据泄露)
            └── CHO 主导 → CEO/CISO/CLO 协同
```

**财务危机路由规则（与 CFO/CRO Skill 完全对齐）**：
| 危机类型 | 主导角色 | 支撑角色 | 路由路径 |
|---------|---------|---------|---------|
| L1 单一指标异常 | CFO | — | CFO 自决处置，结果抄送 HQ（审计归档） |
| L2 多指标联动 | CFO + CRO | CISO（如涉及安全） | CFO → HQ → CRO 联合评估请求 |
| L3 系统性风险 | CRO | CFO + CISO | CRO → HQ → CFO 数据请求 + CISO 安全联动 |

**危机响应 SLA**：
| 危机等级 | 首次响应 | 完整报告 | 决策时限 |
|---------|---------|---------|---------|
| L3/P0 | 15分钟 | 1小时 | 2小时 |
| L2/P1 | 1小时 | 4小时 | 8小时 |
| L1/P2 | 4小时 | 24小时 | 48小时 |

### 6.2 ADKAR 变革管理模型

当引入新 Agent 或重大流程变更时，应用 ADKAR 模型：

| 阶段 | 目标 | CEO 行动 | 协同 Agent |
|-----|------|---------|-----------|
| Awareness | 建立变革意识 | 全员通告变革必要性 | CHO/CLO |
| Desire | 激发参与意愿 | 展示变革收益 | CMO |
| Knowledge | 提供知识培训 | 组织技能转移 | CTO/CHO |
| Ability | 确保执行能力 | 提供工具和资源 | COO/CTO |
| Reinforcement | 强化巩固 | 建立激励机制 | CHO/CFO |

---

## 七、审计与合规

### 审计日志规范

| 日志文件 | 内容 | 保留期限 |
|---------|------|---------|
| `ceo-decision-log` | CEO 所有决策记录 | 永久 |
| `financial-audit-log` | 财务相关跨Agent调用 | 7年 |
| `legal-audit-log` | 法律相关跨Agent调用 + 区块链哈希 | 永久 |
| `hr-audit-log` | 人事相关跨Agent调用 | 5年 |
| `tech-audit-log` | 技术相关跨Agent调用 | 3年 |
| `quality-audit-log` | 质量相关跨Agent调用 | 3年 |
| `partner-relationship-log` | 合作伙伴关系变更 | 5年 |
| `brand-crisis-log` | 品牌危机处理记录 | 永久 |

### 合规检查点

- 所有跨Agent调用须有明确 `sessionKey` 或 `label` 标签
- 敏感数据调用须在消息头标注 `[敏感]`
- P0 级事件须在 **15分钟** 内首次汇报
- 重大决策须有 CEO 审批记录

---

## 八、Agent 缺失检测与自动招募

### 6.1 缺失检测机制

**触发条件**：
- 用户请求调用某Agent，但该Agent未在C-Suite目录中注册
- 跨Agent协同场景需要某角色，但该角色不存在
- `agent-registry.json` 中某注册编号状态为 `vacant` 或 `decommissioned`

### 6.2 CHO 招募流程触发

```
用户请求 → 查询 C-Suite 目录 → 发现缺失
    ↓
自动触发 CHO 招募流程（sessions_send → label: ai-company-hr）
    ↓
CHO 执行招聘模块（五步标准流程）
    ↓
新 Agent 入职 → 注册表更新 → 上报 CEO → ClawHub 发布
```

### 6.3 已注册 C-Suite Agent

| 角色 | 注册编号 | 核心职责 | 状态 |
|------|---------|---------|------|
| CEO | CEO-001 | 战略决策、最高裁决 | ✅ active |
| CHO | CHO-001 | 人事合规、Agent 注册与招募 | ✅ active |
| CFO | CFO-001 | 财务管理、预算审批 | ✅ active |
| CMO | CMO-001 | 品牌营销、舆情管理 | ✅ active |
| CPO | CPO-001 | 合作伙伴、对外关系 | ✅ active |
| CLO | CLO-001 | 法律合规、风险审查 | ✅ active |
| CTO | CTO-001 | 技术架构、AI 基础设施 | ✅ active |
| CQO | CQO-001 | 质量控制、决策质检 | ✅ active |
| CRO | CRO-001 | 风险识别、预警、熔断决策 | ✅ active |
| COO | COO-001 | 日常运营、流程优化、资源调度 | ✅ active |
| CISO | CISO-001 | 安全架构、渗透测试、应急响应 | ✅ active |

---

## 九、ClawHub 发布流程

### 发布命令

```bash
clawhub publish --workdir <workspace> --dir skills <skill-name>
# 示例：clawhub publish --workdir {WORKSPACE_ROOT} ai-company
```

### 完整发布流程

```
1. 更新 SKILL.md（版本号 + changelog）
2. 运行发布命令（node.exe 绕过 PowerShell 执行策略）
3. 验证发布成功（clawhub inspect <slug>）
4. 记录 Slug + Version 到 MEMORY.md
```

### ClawHub 当前发布状态（2026-04-12）

| Skill | Slug | 版本 | 状态 |
|-------|------|------|------|
| AI Company 总控 | `ai-company` | v1.0.0 | ✅ LIVE |
| CEO | `ai-company-ceo` | v2.2.0 | ✅ LIVE |
| CHO | `ai-company-hr` | v1.0.0 | ✅ LIVE |
| CFO | `ai-company-cfo` | v1.0.0 | ✅ LIVE |
| CMO | `ai-company-cmo` | v1.0.3 | ✅ LIVE |
| CPO | `ai-company-cpo` | v1.0.3 | ✅ LIVE |
| CLO | `ai-company-clo` | v1.0.3 | ✅ LIVE |
| CTO | `ai-company-cto` | v1.0.3 | ✅ LIVE |
| CQO | `ai-company-cqo` | v1.0.0 | ✅ LIVE |
| CRO | `ai-company-cro` | v1.0.2 | ✅ LIVE |
| COO | `ai-company-coo` | v1.0.2 | ✅ LIVE |
| CISO | `ai-company-ciso` | v1.0.3 | ✅ LIVE |

> ✅ **无 suspicious 标记**。所有 12 个技能包均已通过 ClawHub 合规审核，正常上线。

---

## 十一、变更日志（AI Company HQ）

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-04-11 | 初始版本 |
| 1.1.0 | 2026-04-12 | 整合五大协同 Skills |
| 1.2.0 | 2026-04-12 | C-Suite 完整注册（11人） |
| 1.3.0 | 2026-04-14 | 执行层 Agent 组建完成（EXEC-001~006） |
| 1.4.0 | 2026-04-14 | IMA 知识库同步中枢 + Handoff 协议 + 并行协调者节点 |
| 1.5.0 | 2026-04-19 | P0修复：财务危机三层级路由(L1/L2/L3)写入危机导航决策树，与CFO/CRO Skill完全对齐 |
| 1.6.0 | 2026-04-19 | P2-14: 统一执行层编号，新增EXEC-007 LEGAL + EXEC-008 HR，执行层从6个扩展至8个（EXEC-001~008） |
| 1.6.0 | 2026-04-19 | P2战略域改进：(1)统一ClawHub slug命名：CEO调用标签从ai-company-governance改为ai-company-ceo，与其他Agent命名一致 (2)更新ClawHub发布状态表中CEO版本为v2.2.0 (3)新增P0级事件直通机制：CEO可通过HQ直接spawn EXEC Agent，缩短传导链从5层到4层，含审计要求与COO事后补报机制 |

---

## Agent身份注册

| 来源 Skill | 整合内容 | 状态 |
|-----------|---------|------|
| `agent-orchestrator` | 五步任务编排工作流 | ✅ 整合入 ai-company |
| `agent-team-orchestration` | 角色定义/任务生命周期/交接协议 | ✅ 整合入 ai-company |
| `multi-agent-pipeline` | 串行/并行 Stage / 错误恢复 / 进度回调 | ✅ 整合入 ai-company |
| `multi-agent-roles` | 专业化角色定义框架 | ✅ 整合入 ai-company |
| `afrexai-cybersecurity-engine` | STRIDE/OWASP/IR Playbook/渗透测试 | ✅ 整合入 ai-company-ciso |
| `quality-gates` | 质量门禁/CI配置/覆盖率阈值 | ✅ 整合入 ai-company-cqo |

---

## 十、铁律

```
❌ 不得绕过 CEO 做重大战略决策
❌ 不得跨级调用（须通过 CEO 或相关Agent）
❌ 不得遗漏审计日志记录
❌ 每次 sessions_spawn 必须包含 KPI 自检和输出路径
✅ 所有跨Agent协同须标注主题标签 #[部门-主题]
✅ P0 级事件立即通知 CEO（15分钟内首次汇报）
✅ 冲突解决以合规优先（CLO/CHO 一票否决权）
✅ Agent 缺失时自动触发 CHO 招募流程
✅ ClawHub 发布前检查 suspicious 标记
✅ 多Agent任务并行派发（max 10个并行）
```

---

## Agent身份注册

- **创建者**：CEO-001
- **创建日期**：2026-04-11
- **最终更新**：2026-04-19
- **状态**：✅ **active**
- **权限级别**：L4（可调用所有 C-Suite Agent）
- **ClawHub**：✅ LIVE（无 suspicious 标记）

