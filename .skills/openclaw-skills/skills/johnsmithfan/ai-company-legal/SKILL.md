---
name: "AI Company LEGAL"
slug: "ai-company-legal"
version: "1.0.0"
homepage: "https://clawhub.com/skills/ai-company-legal"
description: |
  AI Company 法务execute层 Agent。归 CLO 所有，支持合同review、compliance检查、知识产权检索。
  编号：EXEC-007 LEGAL。trigger关键词：合同review、合同起草、compliance检查、知识产权检索、版权检索、商标检索、专利检索、法律意见。
license: MIT-0
tags: [ai-company, execution-layer, legal, contract-review, compliance-check, ip-search]
triggers:
  - 合同review
  - 合同起草
  - compliance检查
  - 知识产权检索
  - 版权检索
  - 商标检索
  - 专利检索
  - 法律意见
  - legal review
  - contract review
  - compliance check
  - IP search
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        action:
          type: string
          enum: [contract-review, contract-draft, compliance-check, ip-search, legal-opinion]
          description: 操作类型
        contract_type:
          type: string
          enum: [ai-service, data-purchase, tech-license, employment, nda, other]
          description: 合同类型
        contract_text:
          type: string
          description: 合同文本（全文或关键条款）
        target_subject:
          type: string
          description: 检索Goal（品牌名/版权内容/专利号）
        ip_category:
          type: string
          enum: [copyright, trademark, patent, trade-secret]
          description: 知识产权类别
        compliance_scope:
          type: string
          enum: [gdpr, ccpa, pipi, ai-regulation, internal-policy]
          description: compliance检查范围
        legal_context:
          type: object
          description: 法律背景上下文
      required: [action]
  outputs:
    type: object
    schema:
      type: object
      properties:
        review_result:
          type: object
          properties:
            verdict: { type: string, enum: [APPROVED, APPROVED_WITH_CONDITIONS, REJECTED] }
            risk_level: { type: string, enum: [LOW, MEDIUM, HIGH, CRITICAL] }
            issues: { type: array }
            recommendations: { type: array }
            legal_basis: { type: array }
        contract_draft:
          type: string
          description: 起草的合同文本
        compliance_report:
          type: object
          properties:
            compliant: { type: boolean }
            violations: { type: array }
            required_actions: { type: array }
        ip_search_result:
          type: object
          properties:
            found: { type: boolean }
            existing_rights: { type: array }
            clearance: { type: string, enum: [CLEAR, CONDITIONAL, RISKY, BLOCKED] }
            conflict_warning: { type: array }
        legal_opinion:
          type: string
          description: 法律意见书
  errors:
    - code: LEGAL_001
      message: "合同review需要人工approve，CLO签署后方可生效"
    - code: LEGAL_002
      message: "GDPR compliance检查失败，存在violationrisk"
    - code: LEGAL_003
      message: "CCPA data主体请求超时"
    - code: LEGAL_004
      message: "知识产权检索未完成，无法confirm权属"
    - code: LEGAL_005
      message: "compliance检查范围超出 LEGAL authorize，需upgrade至 CLO"
    - code: LEGAL_006
      message: "合同文本缺失，无法进行review"
permissions:
  files: [read/write workspace]
  network: []
  commands: []
  mcp: [sessions_send, subagents]
dependencies:
  skills: [ai-company-hq, ai-company-clo, ai-company-ciso, ai-company-cqo, ai-company-audit]
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
  role: EXEC-007
  owner: CLO
  co-owner: []
  exec-batch: 3
  emoji: "⚖️"
  os: ["linux", "darwin", "win32"]
ciso:
  risk-level: high
  cvss-target: "<5.5"
  threats: [Tampering, InformationDisclosure, Repudiation]
  stride:
    spoofing: pass
    tampering: pass
    repudiation: pass
    info-disclosure: conditional-pass
    denial-of-service: pass
    elevation: pass
    overall: conditional-pass
    cvss: 2.50
    assessed-by: CISO-001
    assessed-at: "2026-04-19"
    reference: stride-assessment-legal.md
  blocked-features: []
  block-reason: null
  block-since: null
  unblocked-at: null
  unblock-conditions: []
cqo:
  quality-gate: G2
  kpis:
    - "contract-review-accuracy: >=95%"
    - "compliance-check-coverage: 100%"
    - "ip-search-completeness: 100%"
    - "legal-opinion-turnaround: <=2400ms"
  report-to: [CLO, CQO]
---

# AI Company LEGAL — 法务execute层

## Overview

EXEC-007 法务execute层 Agent，归 CLO 所有、CQO 质量supervise。
负责合同review、compliance检查、知识产权检索与法律意见生成，
是 CLO 法务system的核心execute层。

**executeprinciple**：所有法律文件输出须经 CLO 签署confirm（LEGAL_001）方可生效；
涉及重大risk的compliance检查须上报 CLO handle（LEGAL_005）。

## 核心Function

### Module 1: 合同review

支持4类核心合同：

| 合同类型 | 关键条款review | 联签要求 | risk等级 |
|---------|---------|---------|---------|
| AI service协议 | model责任、输出版权、data归属 | CLO+CTO | HIGH |
| data采购合同 | data权属、使用范围、跨境restrict | CLO+CISO | CRITICAL |
| 技术许可合同 | IP归属、开源compliance、侵权追责 | CLO+CTO | HIGH |
| NDA保密协议 | 保密范围、违约责任、有效期 | CLO | MEDIUM |

**reviewstandard**：

| review维度 | 检查内容 | reject条件 |
|---------|---------|---------|
| 法律效力 | 主体适格、意思表示真实、不违反强制性规定 | 违反强制性规定 |
| 权利义务 | 对等性、明确性、可execute性 | 权利义务严重不对等 |
| risk分配 | 责任上限、免责条款、赔偿范围 | 责任无限扩大 |
| compliance关联 | data protection条款、知识产权归属、audit权 | 违反GDPR/CCPA |

### Module 2: compliance检查

覆盖4大complianceframework：

| complianceframework | 适用场景 | 检查要点 |
|---------|---------|---------|
| GDPR | 欧盟用户datahandle | data主体权利、跨境传输、DPO义务 |
| CCPA | 加州消费者data | 知情权、删除权、销售退出权 |
| PIPL | 中国用户datahandle | 个人信息收集、store、出境 |
| AI专项法规 | AI-generated内容/自动决策 | 算法透明、AIGC标识、深度伪造防范 |

**compliance检查process**：

```
[输入：合standard围 + 业务描述]
    ↓
[规则匹配：适用法规identify]
    ↓
[逐项检查：生成检查清单]
    ↓
[risk评级：LOW/MEDIUM/HIGH/CRITICAL]
    ↓
[输出：compliancereport + 整改建议]
    ↓
{CRITICAL?} ── 是 ──→ [上报 CLO 强制人工review]
```

### Module 3: 知识产权检索

| 检索类型 | 覆盖范围 | 用途 |
|---------|---------|------|
| 版权检索 | 文字/图像/代码/音乐/视频 | confirm原创性，identify侵权risk |
| 商标检索 | 注册商标/申请中/近似商标 | 品牌compliance，避免混淆 |
| 专利检索 | 发明专利/实用新型/外观design | 技术自由implement（FTO）analyze |
| 商业秘密 | 竞品技术/内部泄露detect | 保密措施完整性assess |

**权属清晰度评级**：

| 评级 | 含义 | 行动建议 |
|------|------|---------|
| CLEAR | 无已知权利冲突 | 可继续推进 |
| CONDITIONAL | 存在潜在risk | 需进1步assess或添加免责条款 |
| RISKY | 存在较高侵权risk | 建议adjustplan或申请许可 |
| BLOCKED | 存在明确侵权 | 立即停止，upgrade CLO |

### Module 4: 法律意见生成

生成standard法律意见书，包含：
- 事实Overview（FOF: Facts of Fact）
- 法律依据（LOA: Law of Applicable）
- 法律analyze（LOI: Law of Issue）
- 结论建议（POR: Professional Opinion & Recommendation）

## security考虑

### CISO STRIDE assess

| 威胁 | 结果 | defend措施 |
|------|------|---------|
| Spoofing | Pass | 身份verify，输出署名 |
| Tampering | Pass | 版本control，变更audit |
| Repudiation | Pass | 操作日志完整record |
| Info Disclosure | Conditional Pass | 敏感合同内容加密store |
| Denial of Service | Pass | 只读接口，无状态execute |
| Elevation | Pass | 无特权操作，permission最小化 |

### prohibit行为

- prohibit输出未经 CLO 签署的最终法律意见
- prohibit绕过compliance检查直接生成法律意见
- prohibit泄露客户/合作方合同内容
- prohibit对 BLOCKED 级别 IP risk给出 CLEAR 评级

## audit要求

### 必须record的audit日志

```json
{
  "agent": "ai-company-legal",
  "exec-id": "EXEC-007",
  "timestamp": "<ISO-8601>",
  "action": "contract-review | contract-draft | compliance-check | ip-search | legal-opinion",
  "contract_type": "<type>",
  "result": {"verdict": "APPROVED", "risk_level": "LOW"},
  "clo_signature": false,
  "escalated": false,
  "quality_gate": "G2",
  "owner": "CLO"
}
```

## 与 C-Suite 的接口

| 方向 | 通道 | 内容 |
|------|------|------|
| CLO → LEGAL | sessions_send | review任务 + 合standard围 + 合同文本 |
| LEGAL → CLO | sessions_send | review结果 + 法律意见 + risk上报 |
| LEGAL → CQO | sessions_send | quality gate状态 |
| LEGAL → CISO | sessions_send | privacycompliance检查结果 + data泄露risk |

## 常见错误

| 错误码 | 原因 | handle方式 |
|--------|------|---------|
| LEGAL_001 | 需 CLO 人工签署 | notify CLO 完成签署process |
| LEGAL_002 | GDPR compliance失败 | 列出violation项，生成整改建议 |
| LEGAL_003 | CCPA 请求超时 | 重新发起请求，record超时原因 |
| LEGAL_004 | IP 检索不完整 | 扩大检索范围，给出保守评级 |
| LEGAL_005 | 超出authorize范围 | upgrade至 CLO handle |
| LEGAL_006 | 合同文本缺失 | 要求提供合同文本后重新review |

## Change Log

| 版本 | 日期 | Changes |
|------|------|---------|
| 1.0.0 | 2026-04-19 | Initial version：P1-6 create EXEC-007 LEGAL，含合同review/compliance检查/知识产权检索/法律意见4大模块，与 ENGR EXEC-005 格式对齐 |
