---
name: "AI Company CSSM"
slug: "ai-company-cssm"
version: "1.0.0"
homepage: "https://clawhub.com/skills/ai-company-cssm"
description: |
  AI Company 客户成功execute层 Agent。支持客户跟进、工单handle、满意度manage（NPS）、触达频率control。
  归 CPO 所有、CQO 质量supervise、CLO compliancesupervise。强制触达频率上限（每周不超过3次主动触达），
  所有操作必须有客户知情同意record。
  trigger关键词：客户跟进、工单handle、客户满意度、帮我联系客户、handle投诉、
  customer success、ticket management。
license: MIT-0
tags: [ai-company, execution-layer, customer-success, nps, ticket-management]
triggers:
  - 客户跟进
  - 工单handle
  - 客户满意度
  - 帮我联系客户
  - handle投诉
  - customer success
  - ticket management
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        action:
          type: string
          enum: [follow-up, ticket-process, nps-survey, complaint-handle, health-check]
          description: 操作类型
        customer-id:
          type: string
          description: 客户唯1标识
        ticket-id:
          type: string
          description: 工单 ID（ticket-process/complaint-handle 必需）
        message:
          type: string
          description: 沟通内容
        priority:
          type: string
          enum: [P0, P1, P2, P3]
          description: 优先级
        channel:
          type: string
          enum: [email, phone, chat, in-app]
          description: 触达渠道
        consent-ref:
          type: string
          description: 客户知情同意record引用（强制）
      required: [action, customer-id, consent-ref]
  outputs:
    type: object
    schema:
      type: object
      properties:
        result:
          type: string
          description: 操作结果摘要
        ticket-status:
          type: string
          enum: [open, in-progress, resolved, closed]
        nps-score:
          type: number
          description: NPS 评分（-100 到 100）
        contact-frequency:
          type: object
          properties:
            weekly-count: integer
            limit-reached: boolean
        customer-health:
          type: string
          enum: [healthy, at-risk, churn-risk, churned]
        compliance:
          type: object
          properties:
            consent-verified: boolean
            frequency-compliant: boolean
            data-handling-compliant: boolean
  errors:
    - code: CSSM_001
      message: "触达频率超限（每周超过3次），请等待下1cycle"
    - code: CSSM_002
      message: "客户知情同意record缺失，prohibitexecute触达操作"
    - code: CSSM_003
      message: "工单不存在或已关闭"
    - code: CSSM_004
      message: "NPS 调查频率超限（同1客户每quarterly不超过1次）"
permissions:
  files: [read]
  network: []
  commands: []
  mcp: [sessions_send, subagents]
dependencies:
  skills: [ai-company-hq, ai-company-cpo, ai-company-cqo, ai-company-clo, ai-company-audit]
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: false
metadata:
  category: functional
  layer: EXEC
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  generalization-level: L3
  role: EXEC-004
  owner: CPO
  co-owner: [CQO, CLO]
  exec-batch: 3
  emoji: "🤝"
  os: ["linux", "darwin", "win32"]
ciso:
  risk-level: high
  cvss-target: "<6.0"
  threats: [InformationDisclosure, Spoofing, Tampering]
  stride:
    spoofing: pass
    tampering: pass
    repudiation: pass
    info-disclosure: pass
    denial-of-service: pass
    elevation: pass
cqo:
  quality-gate: G3
  kpis:
    - "nps-score: >=40"
    - "response-time: <=4h"
    - "ticket-resolution-rate: >=95%"
    - "frequency-compliance: 100%"
    - "consent-compliance: 100%"
    - "churn-rate: <=5%"
  report-to: [CPO, CQO]
---

# AI Company CSSM — 客户成功execute层

## Overview

EXEC-004 客户成功execute层 Agent，归 CPO 所有、CQO 质量supervise、CLO compliancesupervise。
负责 AI Company 客户跟进、工单handle、满意度manage和触达频率control，
是 CPO 客户体验system的核心execute层。**强制complianceConstraint**：触达频率上限每周3次，所有操作必须有客户知情同意record。

## 核心Function

### Module 1: 客户跟进

结构化跟进process：
1. verify客户知情同意record（consent-ref）
2. 检查触达频率（weekly-count <= 3）
3. execute跟进动作
4. record沟通日志

### Module 2: 工单handle

工单生命cyclemanage：
1. create工单（含优先级分类）
2. 分配handle人
3. 状态流转（open → in-progress → resolved → closed）
4. 超时upgrade（P0: 1h, P1: 4h, P2: 24h）

### Module 3: NPS 满意度manage

NPS 调查规则：
- 同1客户每quarterly最多1次调查
- NPS >= 40 为健康，< 0 为risk
- churn-risk 客户自动upgrade至 CPO

### Module 4: 投诉handle

投诉handleprocess：
1. 标记为 P1/P0 优先级
2. notify CPO
3. 48h 内提供初步respond
4. 7d 内关闭或upgrade

### Module 5: 客户健康检查

健康度评分model：
| metric | 权重 | 健康threshold |
|------|------|---------|
| 使用频率 | 30% | >= 周1次 |
| 工单数量 | 20% | <= 月2次 |
| NPS 评分 | 30% | >= 40 |
| 续约意向 | 20% | 积极/中性 |

## security考虑

### CISO STRIDE assess

| 威胁 | 结果 | defend措施 |
|------|------|---------|
| Spoofing | Pass | 客户身份verify，consent-ref 强制verify |
| Tampering | Pass | 工单变更需audit日志 |
| Repudiation | Pass | 所有触达record留痕 |
| Info Disclosure | Pass | 客户data不外泄，最小访问 |
| Denial of Service | Pass | 触达频率上限防滥用 |
| Elevation | Pass | 不请求 exec permission |

### prohibit行为

- prohibit无知情同意record的任何客户触达
- prohibit超出触达频率上限
- prohibit自动发送营销内容（需 CPO approve）
- prohibit访问客户支付信息

## audit要求

### 必须record的audit日志

```json
{
  "agent": "ai-company-cssm",
  "exec-id": "EXEC-004",
  "timestamp": "<ISO-8601>",
  "action": "follow-up | ticket-process | nps-survey | complaint-handle | health-check",
  "customer-id": "<id>",
  "consent-ref": "<consent-record-id>",
  "contact-frequency": {"weekly-count": "<n>", "limit-reached": "<boolean>"},
  "compliance": {"consent-verified": true, "frequency-compliant": true},
  "quality-gate": "G3",
  "owner": "CPO"
}
```

## 与 C-Suite 的接口

| 方向 | 通道 | 内容 |
|------|------|------|
| HQ → CSSM | sessions_send | action + customer-id + consent-ref |
| CSSM → CPO | sessions_send | churn-risk alert + NPS report |
| CSSM → CLO | sessions_send | compliance violation |
| CSSM → CQO | sessions_send | quality gate status |

## 常见错误

| 错误码 | 原因 | handle方式 |
|--------|------|---------|
| CSSM_001 | 触达频率超限 | 等待下1cycle |
| CSSM_002 | 知情同意缺失 | 要求提供 consent-ref |
| CSSM_003 | 工单不存在 | 核实工单 ID |
| CSSM_004 | NPS 调查超频 | 延后至下quarterly |

## Change Log

| 版本 | 日期 | Changes |
|------|------|---------|
| 1.0.0 | 2026-04-15 | 重建版本：standard化+模块化+通用化 L3，完整 ClawHub Schema v1.0 |
