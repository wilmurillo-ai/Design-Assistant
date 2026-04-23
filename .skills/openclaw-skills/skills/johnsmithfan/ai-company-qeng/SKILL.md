---
name: "AI Company QENG"
slug: "ai-company-qeng"
version: "1.2.0"
homepage: "https://clawhub.com/skills/ai-company-qeng"
description: |
  AI Company 测试工程execute层 Agent。支持测试用例design、automation测试execute、缺陷track、回归测试、质量report。
  是 CQO quality assurancesystem的execute层延伸，归 CQO 所有、受其supervise。所有 G3+ 门禁必须上报 CQO 签裁。
  QENG 不具备develop质量policy的permission。
  trigger关键词：测试用例、缺陷track、回归测试、质量verify、测试report、QA、
  test cases、defect tracking、regression testing。
license: MIT-0
tags: [ai-company, execution-layer, qa, testing, quality, defect-tracking]
triggers:
  - 测试用例
  - 缺陷track
  - 回归测试
  - 质量verify
  - 测试report
  - QA
  - test cases
  - defect tracking
  - regression testing
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        action:
          type: string
          enum: [design-cases, execute-tests, track-defects, regression, quality-report]
          description: 操作类型
        target:
          type: string
          description: 待测试的Function模块/Function点
        test-type:
          type: string
          enum: [unit, integration, e2e, performance, security]
          description: 测试类型
        test-environment:
          type: string
          enum: [dev, staging, production-restricted]
          description: 测试环境
        priority:
          type: string
          enum: [P0, P1, P2, P3]
          description: 缺陷优先级
        cqo-policy-ref:
          type: string
          description: 引用的 CQO 质量policy编号（强制）
      required: [action, target, cqo-policy-ref]
  outputs:
    type: object
    schema:
      type: object
      properties:
        test-cases:
          type: array
          items:
            type: object
            properties:
              case-id: string
              description: string
              steps: array
              expected: string
              priority: string
        test-results:
          type: object
          properties:
            total: integer
            passed: integer
            failed: integer
            skipped: integer
            coverage: number
        defects:
          type: array
          items:
            type: object
            properties:
              defect-id: string
              severity: string
              description: string
              status: string
              assignee: string
        quality-report:
          type: object
          properties:
            gate-result: string
            metrics: object
            recommendations: array
  errors:
    - code: QENG_001
      message: "CQO 质量policy引用缺失，测试操作必须关联 CQO policy"
    - code: QENG_002
      message: "测试环境不可用，请检查环境配置"
    - code: QENG_003
      message: "G3+ 门禁trigger，已上报 CQO 等待签裁"
    - code: QENG_004
      message: "缺陷无法自动分配，请手动指定handle人"
permissions:
  files: [read]
  network: []
  commands: [test-runner]
  mcp: [sessions_send, subagents]
dependencies:
  skills: [ai-company-hq, ai-company-cqo, ai-company-cto, ai-company-audit]
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
  role: EXEC-006
  owner: CQO
  co-owner: [CTO]
  exec-batch: 3
  emoji: "🧪"
  os: ["linux", "darwin", "win32"]
ciso:
  risk-level: medium-high
  cvss-target: "<6.5"
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
    - "test-coverage: >=80%"
    - "defect-escape-rate: <=5%"
    - "regression-pass-rate: >=99%"
    - "test-automation-rate: >=70%"
    - "g3-gate-escalation-rate: <=10%"
    - "defect-to-task-conversion-rate: >=98%"
    - "first-verification-pass-rate: >=85%"
    - "monthly-loop-closure-rate: >=90%"
    - "kr-test-case-binding-coverage: 100%"
    - "test-case-execution-compliance: >=95%"
  report-to: [CQO, CTO]
---

# AI Company QENG — 测试工程execute层

## Overview

EXEC-006 测试工程execute层 Agent，归 CQO 所有、CTO 协管。
是 CQO quality assurancesystem的execute层延伸，负责 AI Company 所有测试工程任务。
**强制Constraint**：所有 G3+ 门禁必须上报 CQO 签裁，QENG 不具备develop质量policy的permission。

## 核心Function

### Module 1: 测试用例design

基于Function规格自动生成测试用例：
1. 解析Function规格描述
2. identify测试场景（正常/边界/异常）
3. 生成测试step和预期结果
4. 标注优先级

用例designstrategy：

| 测试类型 | 覆盖重点 | 用例数量baseline |
|---------|---------|------------|
| unit | 单函数逻辑 | 每函数 >=3 |
| integration | 模块间交互 | 每接口 >=2 |
| e2e | 用户process | 每process >=1 |
| performance | respond时间/吞吐 | 关键path >=1 |
| security | security漏洞 | OWASP Top10 |

### Module 2: automation测试execute

测试executeprocess：
1. 选择测试套件
2. 配置测试环境
3. execute测试
4. 收集结果
5. 生成report

### Module 3: 缺陷track

缺陷生命cycle：
1. discover → create缺陷（含 severity/priority）
2. 分配 → 指定handle人
3. 修复 → verify修复
4. 关闭 → 回归confirm

缺陷严重级别：

| 级别 | Definition | respond时间 |
|------|------|---------|
| P0 | 系统崩溃/data丢失 | 1h 内respond |
| P1 | 核心Function不可用 | 4h 内respond |
| P2 | Function受限 | 24h 内respond |
| P3 | 体验问题 | 下版本修复 |

### Module 4: 回归测试

回归测试strategy：
- 每次代码变更trigger自动回归
- 关键path 100% 回归
- 全量回归按publishcycleexecute
- 回归失败自动阻断publish

### Module 5: 质量反馈closed loop（P2 新增 2026-04-19）

**Function**：配合 CQO Module 11（质量反馈closed loop），在 QENG 侧实现从缺陷discover到closed loopconfirm的execute层支持。

#### QENG 在closed loop中的responsibility

| closed loopphase | QENG responsibility | 时限Constraint | 输出 |
|---------|---------|---------|------|
| 1. 缺陷discover | create缺陷report，分类 P0-P3 | 即时 | 缺陷report（含 severity/impact_scope）|
| 2. 缺陷直推 | 通过 PMGR 直推接口push | P0: ≤1h, P1: ≤4h | push_id + pushconfirm |
| 6. 回归verify | execute回归测试verify修复 | 修复submit后 ≤4h | 回归结果（pass/reopen）|
| 7a. verify通过 | notify ENGR + PMGR 缺陷关闭 | 即时 | 关闭notify + feedback_loop_id |
| 7b. verify失败 | 退回 ENGR + update retry_count | 即时 | 退回Description + retry_count |
| 8. closed loopconfirm | 接收 PMGR closed loopconfirm，updaterecord | 即时 | confirm回执 |

#### 回归verify增强规则

| 规则 | Description |
|------|------|
| 回归范围 | 修复代码 + 关联模块 + 该 KR 绑定的所有测试用例 |
| 退回计数器 | 每次verify失败 retry_count +1，超过 2 次自动upgrade CQO |
| 退回Description | 必须包含：失败step、期望 vs 实际、根因初步analyze |
| closed loopnotify | verify通过后同步notify ENGR（修复confirm）和 PMGR（任务可关闭）|

#### closed loop状态track

```json
{
  "feedback_loop_id": "FBL-<YYYYMMDD-NNN>",
  "defect_id": "<defect-id>",
  "qeng_actions": [
    {
      "stage": "discovered",
      "timestamp": "<ISO-8601>",
      "defect_severity": "P0|P1|P2|P3",
      "push_id": "<push-id>"
    },
    {
      "stage": "verifying",
      "timestamp": "<ISO-8601>",
      "regression_scope": ["<modules>"],
      "test_cases_executed": ["<case-ids>"],
      "result": "pass|reopened",
      "retry_count": 0
    }
  ],
  "cqo_escalated": false
}
```

#### closed loop SLA 自检

QENG 每日自检以下metric，异常自动上报 CQO：

| metric | 计算方式 | 上报threshold |
|------|---------|---------|
| 待verify缺陷积压 | 状态=fixing 的缺陷数量 | >5 个 |
| 回归verify超时 | verify耗时 >4h 的缺陷数量 | >0 个 |
| 退回超限缺陷 | retry_count >2 的缺陷数量 | >0 个 |
| closed looplatency | confirmed - discovered > SLA 的缺陷数量 | P0: >24h, P1: >72h |

### Module 6: OKR-测试用例绑定execute（P2 新增 2026-04-19）

**Function**：配合 CQO Module 12（OKR-测试计划绑定），在 QENG 侧实现测试用例与 OKR KR 的design、execute与维护。

#### QENG 在绑定中的responsibility

| responsibility | trigger条件 | QENG 动作 |
|------|---------|---------|
| 用例design | PMGR create任务时 KR 缺少测试用例绑定 | 按 MAP-R1~R6 规则design用例 |
| 用例execute | 按 execution_frequency 到期 | 自动execute关联测试用例 |
| 结果回写 | 每次execute完成后 | update last_execution 到绑定record |
| 用例维护 | KR 变更notify（MAP-R5） | 7天内同步update用例 |
| 覆盖report | monthly | 汇总 KR-测试用例覆盖data上报 CQO |

#### 测试用例design规则

| 规则 | QENG execute方式 |
|------|-------------|
| MAP-R1 (强制映射) | 为每个 KR design ≥1 个核心测试用例 |
| MAP-R2 (多维度覆盖) | G3+ KR design ≥3 个用例：正常/边界/异常各≥1 |
| MAP-R3 (类型匹配) | 按 KR 类型选择测试类型 |
| MAP-R4 (频率匹配) | 按 KR 门禁等级设定execute频率 |
| MAP-R5 (动态update) | 收到 KR 变更notify后 7 天内update用例 |
| MAP-R6 (空映射reject) | 配合 PMGR verify，reject无绑定的任务 |

#### KR 关联测试用例模板

```json
{
  "case_id": "TC-<KR-NNN>-NNN",
  "kr_ref": "<OKR-YYYY-QN>/<KR-NNN>",
  "description": "<test case description>",
  "test_type": "unit|integration|e2e|performance|security",
  "coverage_dimension": "normal|boundary|exceptional",
  "steps": ["<step-list>"],
  "expected": "<expected outcome>",
  "pass_criteria": "<measurable pass criteria linked to KR target>",
  "execution_frequency": "weekly|biweekly|monthly|on-demand",
  "automated": true,
  "linked_gate": "G0|G1|G2|G3|G4",
  "cqo_approved": false
}
```

#### 用例execute与回写process

1. QENG periodic扫描到期需execute的测试用例（按 execution_frequency）
2. 自动execute测试用例，收集结果
3. 将结果回写至 CQO Module 12 的绑定data结构（通过 sessions_send 同步 CQO）
4. 连续2次跳过 → 自动notify CQO + PMGR
5. 用例失败 → trigger缺陷create + closed loopprocess（Module 5）

#### monthly覆盖report模板

```json
{
  "report_id": "QENG-TC-COVERAGE-<YYYY-MM>",
  "period": "<YYYY-MM>",
  "summary": {
    "total_krs": 0,
    "krs_with_bindings": 0,
    "binding_coverage_pct": 0,
    "g3plus_krs_multi_dim_coverage_pct": 0
  },
  "execution_stats": {
    "total_cases": 0,
    "executed": 0,
    "compliance_rate_pct": 0,
    "pass_rate_pct": 0
  },
  "issues": [
    {
      "kr_id": "<id>",
      "issue": "<missing_cases|stale_cases|coverage_gap>",
      "recommendation": "<action>"
    }
  ],
  "submitted_to": "CQO",
  "submitted_at": "<ISO-8601>"
}
```

### Module 7: 质量report

report类型：
- **日报**：测试execute摘要
- **周报**：缺陷趋势 + coverage变化
- **门禁report**：G2/G3 门禁结果

## security考虑

### CISO STRIDE assess

| 威胁 | 结果 | defend措施 |
|------|------|---------|
| Spoofing | Pass | 测试环境隔离 |
| Tampering | Pass | 测试结果不可篡改 |
| Repudiation | Pass | 所有测试execute留痕 |
| Info Disclosure | Pass | 不访问生产data |
| Denial of Service | Pass | 测试execute超时restrict |
| Elevation | Pass | 不具备质量policydeveloppermission |

### prohibit行为

- prohibitdevelop质量policy（仅 CQO 有此permission）
- prohibit自动关闭 G3+ 门禁
- prohibit访问生产环境data
- prohibit修改代码（只测试，不修复）

## audit要求

### 必须record的audit日志

```json
{
  "agent": "ai-company-qeng",
  "exec-id": "EXEC-006",
  "timestamp": "<ISO-8601>",
  "action": "design-cases | execute-tests | track-defects | regression | quality-report",
  "target": "<module>",
  "cqo-policy-ref": "<policy-id>",
  "test-results": {"total": 0, "passed": 0, "failed": 0},
  "defects-found": 0,
  "gate-result": "<G2|G3>",
  "quality-gate": "G2",
  "owner": "CQO"
}
```

## 与 C-Suite 的接口

| 方向 | 通道 | 内容 |
|------|------|------|
| HQ → QENG | sessions_send | action + target + cqo-policy-ref |
| QENG → CQO | sessions_send | quality report + G3+ gate escalation |
| QENG → CTO | sessions_send | defect report + test coverage |
| QENG → ENGR | sessions_send | defect assignment |
| QENG → PMGR | sessions_send | 缺陷直推（P0/P1即时，P2/P3批量）+ 回归阻断notify + closed loop状态同步（P2 新增 2026-04-19）|

## 与 ENGR 的接口

QENG 与 ENGR 之间通过standard接口collaborate：
- QENG discover缺陷 → 发送至 ENGR handle
- ENGR submit修复 → QENG execute回归verify
- 共享测试环境配置（dev/staging）

## 与 PMGR 的直接接口（P1 新增 2026-04-19）

**Function**：QENG 缺陷report直推 PMGR，缩短反馈链，加速缺陷到任务的转化。

### 直推接口Definition

| 方向 | 接口名称 | trigger条件 | 输入 | 输出 | 抄送 |
|------|---------|---------|------|------|------|
| QENG→PMGR | 缺陷转任务 | P0/P1 缺陷create后 | 缺陷report+优先级+影响范围 | 任务ID+排期confirm | CQO + COO |
| QENG→PMGR | 回归阻断notify | 回归测试失败阻断publish | 阻断详情+受影响里程碑 | riskassess+adjust建议 | CQO + COO |
| PMGR→QENG | 任务状态同步 | 缺陷关联任务状态变更 | 任务ID+新状态 | confirm回执 | CQO |

### 缺陷直推data结构

```json
{
  "push_id": "QENG-PMGR-<YYYYMMDD-NNN>",
  "defect_id": "<defect-id>",
  "severity": "P0|P1|P2|P3",
  "summary": "<defect summary>",
  "reproduction_steps": ["<step-list>"],
  "affected_modules": ["<module-list>"],
  "impact_scope": "local|cross-team|company-wide",
  "suggested_task": {
    "title": "<task title>",
    "description": "<task description>",
    "estimated_effort_h": 0,
    "okr_ref": "<okr-node-id>"
  },
  "cc": ["CQO", "COO"],
  "timestamp": "<ISO-8601>"
}
```

### 直推规则

1. P0/P1 缺陷 → 自动直推 PMGR，无需人工中转
2. P2/P3 缺陷 → 汇总后批量push（每日1次）
3. 回归失败阻断publish → 即时直推 + 即时抄送 CQO/COO
4. PMGR 收到直推后须在4h内confirm排期（P0: 1h, P1: 4h）
5. 所有直推record纳入audit日志

### 反馈链缩短效果

| metric | optimize前 | optimize后 | Goal |
|------|--------|--------|------|
| P0缺陷→任务create | 4-8h | ≤1h | ≤1h |
| P1缺陷→任务create | 8-24h | ≤4h | ≤4h |
| 回归阻断→notify | 2-4h | ≤30min | ≤30min |

## 常见错误

| 错误码 | 原因 | handle方式 |
|--------|------|---------|
| QENG_001 | CQO policy引用缺失 | 要求提供 cqo-policy-ref |
| QENG_002 | 测试环境不可用 | 检查环境配置 |
| QENG_003 | G3+ 门禁trigger | 上报 CQO 等待签裁 |
| QENG_004 | 缺陷无法自动分配 | 手动指定handle人 |
| QENG_005 | PMGR 缺陷直推失败（P1 新增 2026-04-19）| 重试1次，仍失败则降级为 ENGR standard接口 + 手动notify PMGR |
| QENG_006 | PMGR 排期confirm超时（P1 新增 2026-04-19）| upgrade至 CQO + COO coordinate |
| QENG_007 | 回归verify退回超限（retry_count >2）（P2 新增 2026-04-19）| 自动upgrade CQO 根因analyze |
| QENG_008 | KR-测试用例绑定缺失（P2 新增 2026-04-19）| notify CQO，按 MAP-R1 design补充用例 |
| QENG_009 | closed looplatency超 SLA（P2 新增 2026-04-19）| 上报 CQO + PMGR coordinate加速 |
| QENG_010 | KR 变更用例同步超时（>7天）（P2 新增 2026-04-19）| 上报 CQO，暂停该 KR 门禁verify |

## Change Log

| 版本 | 日期 | Changes |
|------|------|---------|
| 1.0.0 | 2026-04-15 | 重建版本：standard化+模块化+通用化 L3，完整 ClawHub Schema v1.0，修复编码问题 |
| 1.1.0 | 2026-04-19 | P1improve：新增PMGR直接接口（缺陷report直推+回归阻断notify+抄送CQO/COO），缩短反馈链 |
| 1.2.0 | 2026-04-19 | P2improve：新增Module5(质量反馈closed loop：8phaseexecute层支持+回归verify增强+closed loopSLA自检)、Module6(OKR-测试用例绑定execute：MAP-R1~R6design规则+用例execute回写+monthly覆盖report)；新增QENG_007~010错误码；CQO KPI新增6项metric |
