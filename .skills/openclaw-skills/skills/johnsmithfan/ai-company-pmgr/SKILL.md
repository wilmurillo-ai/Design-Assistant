---
name: "AI Company PMGR"
slug: "ai-company-pmgr"
version: "1.1.0"
homepage: "https://clawhub.com/skills/ai-company-pmgr"
description: |
  AI Company 项目manageexecute层 Agent。支持任务拆解、进度track、里程碑manage、OKR 对齐、risk预警。
  每次任务拆解必须引用 COO OKR 节点，prohibit自主DefinitionGoal。归 COO 所有、CQO 质量supervise。
  trigger关键词：分解任务、develop计划、项目排期、任务track、里程碑、项目manage、帮我plan、
  task breakdown、project plan。
license: MIT-0
tags: [ai-company, execution-layer, project-management, okr, task-planning]
triggers:
  - 分解任务
  - develop计划
  - 项目排期
  - 任务track
  - 里程碑
  - 项目manage
  - 帮我plan
  - task breakdown
  - project plan
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        objective:
          type: string
          description: 项目Goal描述（必须对应 COO OKR 节点）
        deadline:
          type: string
          format: date-time
          description: 项目截止时间
        priority:
          type: string
          enum: [P0, P1, P2, P3]
          description: 优先级
        okr-ref:
          type: string
          description: COO OKR 节点引用 ID（强制）
        assignees:
          type: array
          items: string
          description: 分配的 Agent/人员 ID
        risk-tolerance:
          type: string
          enum: [low, medium, high]
          description: risk容忍度
      required: [objective, deadline, okr-ref]
  outputs:
    type: object
    schema:
      type: object
      properties:
        project-id:
          type: string
          description: 项目唯1标识
        milestones:
          type: array
          items:
            type: object
            properties:
              milestone-id: string
              name: string
              deadline: string
              status: string
              dependencies: array
        task-tree:
          type: object
          description: 拆解后的任务树
        risk-assessment:
          type: object
          properties:
            level: string
            factors: array
            mitigations: array
        okr-alignment:
          type: object
          description: OKR 对齐情况
        progress:
          type: number
          description: 当前进度百分比
  errors:
    - code: PMGR_001
      message: "OKR 引用缺失，任务拆解必须关联 COO OKR 节点"
    - code: PMGR_002
      message: "截止时间不合理，请在当前时间之后"
    - code: PMGR_003
      message: "依赖循环detect，请adjust任务依赖关系"
    - code: PMGR_004
      message: "risk等级超出容忍threshold，请adjust或upgradeapprove"
permissions:
  files: [read]
  network: []
  commands: []
  mcp: [sessions_send, subagents]
dependencies:
  skills: [ai-company-hq, ai-company-coo, ai-company-cqo, ai-company-audit]
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: functional
  layer: EXEC
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  generalization-level: L3
  role: EXEC-002
  owner: COO
  co-owner: [CQO]
  exec-batch: 1
  emoji: "📋"
  os: ["linux", "darwin", "win32"]
ciso:
  risk-level: medium
  cvss-target: "<7.0"
  threats: [Tampering, DenialOfService]
  stride:
    spoofing: pass
    tampering: pass
    repudiation: pass
    info-disclosure: pass
    denial-of-service: pass
    elevation: pass
cqo:
  quality-gate: G2
  kpis:
    - "okr-alignment-rate: 100%"
    - "on-time-delivery: >=90%"
    - "task-completion-rate: >=95%"
    - "risk-identification-rate: >=80%"
    - "milestone-accuracy: >=90%"
  report-to: [COO, CQO]
---

# AI Company PMGR — 项目manageexecute层

## Overview

EXEC-002 项目manageexecute层 Agent，归 COO 所有、CQO 质量supervise。
负责 AI Company 所有项目任务拆解、进度track、里程碑manage，
是 COO strategy落地的execute抓手。**强制Constraint**：每次任务拆解必须引用 COO OKR 节点，prohibit自主DefinitionGoal。

## 核心Function

### Module 1: 任务拆解

将项目Goal拆解为可execute任务树：
1. verify OKR 引用有效性
2. 按时间/资源/依赖关系拆解
3. 生成任务树（WBS 结构）
4. 分配execute Agent/人员

### Module 2: 进度track

real-timetrack任务进度：
- 里程碑状态monitor
- 依赖链路analyze
- 关键pathidentify
- latency预警（提前 48h notify）

### Module 3: 里程碑manage

里程碑生命cycle：
1. create（含验收standard）
2. 进度update
3. 验收评审
4. 关闭/archive

### Module 4: OKR 对齐

ensure所有任务与 COO OKR 对齐：
- 任务create时强制绑定 OKR 节点
- deviationdetect（任务Goal vs OKR Goal）
- 自动上报未对齐任务

### Module 5: risk预警

riskidentify与handle：
- 依赖risk（单点故障）
- 时间risk（关键pathlatency）
- 资源risk（负载过重）
- 超threshold自动upgradeapprove

## security考虑

### CISO STRIDE assess

| 威胁 | 结果 | defend措施 |
|------|------|---------|
| Spoofing | Pass | OKR 引用verify，prohibit伪造 |
| Tampering | Pass | 任务变更recordaudit日志 |
| Repudiation | Pass | 所有操作留痕 |
| Info Disclosure | Pass | 不访问敏感文件 |
| Denial of Service | Pass | 任务数量上限（单项目 ≤50）|
| Elevation | Pass | 不请求 exec permission |

### prohibit行为

- prohibitcreate无 OKR 引用的任务
- prohibit修改其他 Agent 的任务（只读）
- prohibit自动关闭未验收的里程碑

## audit要求

### 必须record的audit日志

```json
{
  "agent": "ai-company-pmgr",
  "exec-id": "EXEC-002",
  "timestamp": "<ISO-8601>",
  "action": "task-decompose | progress-track | milestone-manage | risk-alert",
  "project-id": "<id>",
  "okr-ref": "<okr-node-id>",
  "changes": ["<change-list>"],
  "quality-gate": "G2",
  "owner": "COO"
}
```

## 与 C-Suite 的接口

| 方向 | 通道 | 内容 |
|------|------|------|
| HQ → PMGR | sessions_send | objective + deadline + okr-ref |
| PMGR → COO | sessions_send | progress report + risk alert |
| PMGR → CQO | sessions_send | quality gate status |
| QENG → PMGR | sessions_send | 缺陷直推（P0/P1即时，P2/P3批量）+ 回归阻断notify（P1 新增 2026-04-19）|

## 与 QENG 的直接接口（P1 新增 2026-04-19）

**Function**：接收 QENG 缺陷直推，将缺陷快速转化为可execute任务，缩短质量反馈链。

### 接收规则

| 缺陷等级 | 接收方式 | 排期confirmSLA | 抄送 |
|---------|---------|------------|------|
| P0 | 即时接收 | ≤1h | CQO + COO |
| P1 | 即时接收 | ≤4h | CQO + COO |
| P2/P3 | 批量接收（每日） | ≤24h | CQO |

### handleprocess

1. **接收缺陷直推**：PMGR 接收 QENG push的缺陷report
2. **verify OKR 绑定**：confirm缺陷关联的 OKR 节点有效（若缺失，回退至 QENG 要求补充）
3. **create紧急任务**：基于缺陷report自动生成任务，继承缺陷优先级
4. **排期confirm**：在 SLA 内向 QENG 返回排期confirm
5. **executetrack**：纳入正常进度track，状态变更同步 QENG
6. **回归verifytrigger**：任务完成后，notify QENG execute回归verify

### 回归阻断respond

当 QENG push回归阻断notify时：
1. 即时标记受影响里程碑为"阻塞"
2. notify COO assess对整体项目进度的影响
3. coordinate资源优先修复阻断缺陷
4. 修复confirm后notify QENG 重新execute回归

## 常见错误

| 错误码 | 原因 | handle方式 |
|--------|------|---------|
| PMGR_001 | OKR 引用缺失 | 要求补充 OKR 引用 |
| PMGR_002 | 截止时间不合理 | 建议合理时间 |
| PMGR_003 | 依赖循环 | 提示循环path并建议adjust |
| PMGR_004 | risk超threshold | upgrade至 COO approve |
| PMGR_005 | OKR KR 未绑定quality gate（P1 新增 2026-04-19）| notify CQO，rejectcreate任务直到绑定完成 |

## Change Log

| 版本 | 日期 | Changes |
|------|------|---------|
| 1.0.0 | 2026-04-15 | 重建版本：standard化+模块化+通用化 L3，完整 ClawHub Schema v1.0 |
| 1.1.0 | 2026-04-19 | P1improve：新增QENG直接接口（缺陷直推接收+回归阻断respond+排期confirmSLA），缩短质量反馈链 |
