---
name: "AI Company Skill Learner"
slug: ai-company-skill-learner
version: 1.0.0
homepage: https://clawhub.com/skills/ai-company-skill-learner
description: |
  AI Companyskilllearning引擎。自动化执行八阶段skilllearning流程：搜索→review→learning→创建→标准化→模块化→通用化→发布。
  触发关键词：skilllearning、learningskill、创建新skill、开发skill包
license: MIT-0
tags: [ai-company, skill-learning, automation, pipeline, c-suite]
triggers:
  - skilllearning
  - learningskill
  - 创建新skill
  - 开发skill包
  - skill learning
  - learn skill
  - create skill
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        topic:
          type: string
          description: learning主题/领域
        target_platforms:
          type: array
          items:
            type: string
            enum: [clawhub, github, web]
          default: [clawhub, github]
        max_search_results:
          type: integer
          default: 10
          description: 最大搜索结果数
        target_level:
          type: string
          enum: [L1, L2, L3, L4, L5]
          default: L3
          description: 通用化目标等级
        auto_publish:
          type: boolean
          default: false
          description: 是否自动发布
      required: [topic]
  outputs:
    type: object
    schema:
      type: object
      properties:
        status:
          type: string
          enum: [success, failed, partial]
        skill_name:
          type: string
        skill_path:
          type: string
        pipeline_report:
          type: object
          properties:
            phases_completed:
              type: integer
            phases_total:
              type: integer
            quality_score:
              type: number
            security_score:
              type: number
        artifacts:
          type: array
          items:
            type: string
      required: [status]
  errors:
    - code: LEARNER_001
      message: "Topic not specified"
    - code: LEARNER_002
      message: "Discovery phase failed - no skills found"
    - code: LEARNER_003
      message: "Review phase failed - security check not passed"
    - code: LEARNER_004
      message: "Creation phase failed - invalid skill structure"
    - code: LEARNER_005
      message: "Quality gate failed"
    - code: LEARNER_006
      message: "Max retry exceeded"
permissions:
  files: [read, write]
  network: [api]
  commands: []
  mcp: [sessions_send, sessions_spawn, subagents]
dependencies:
  skills:
    - ai-company-hq
    - ai-company-kb
    - ai-company-cmo-skill-discovery
    - ai-company-cqo-skill-reviewer
    - ai-company-cto-skill-builder
    - ai-company-ciso-security-gate
    - ai-company-cho-knowledge-extractor
    - ai-company-clo-compliance-checker
    - ai-company-ceo-orchestrator
    - ai-company-standardization
    - ai-company-modularization
    - ai-company-generalization
    - ai-company-audit
    - ai-company-skill-creator
  cli: [clawhub]
quality:
  saST: Pass
  vetter: Approved
  idempotent: false
metadata:
  category: governance
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  tags: [ai-company, skill-learning, automation, pipeline]
---

# AI Company Skill Learner v1.0

> AI Companyskilllearning引擎。自动化执行八阶段skilllearning流程，从网络搜索到ClawHub发布的完整闭环。

---

## 概述

**ai-company-skill-learner** 是AI Company的自动化skilllearning引擎，整合C-Suite全员协同能力，实现：

1. **智能搜索**: CMO主导多平台skilldiscovery
2. **质量review**: CQO主导G0-G7quality gate
3. **深度learning**: CTO主导技术解析与知识提取
4. **自动创建**: 基于ai-skill-creator六阶段流程
5. **标准化**: 符合ClawHub Schema v1.0
6. **模块化**: 原子化可复用模块分解
7. **通用化**: 跨组织/行业/平台适配
8. **security发布**: CISO主导最终security审查

---

## 核心功能

### Module 1: 八阶段learning管道

**功能**: 执行完整的skilllearning生命周期

| 阶段 | 主导Agent | 核心任务 | 输出物 |
|------|----------|----------|--------|
| 1-搜索 | CMO | 多平台skill搜索、评估、排序 | 候选skill清单 |
| 2-review | CQO/CISO/CTO | 质量/security/技术三重review | review报告 |
| 3-learning | CTO | skill解析、知识提取、能力映射 | learning笔记 |
| 4-创建 | CTO | 目录初始化、SKILL.md编写、脚本开发 | Skill目录 |
| 5-标准化 | CQO | Frontmatteraudit、Schemacompliance | 标准化Skill |
| 6-模块化 | CTO | 边界识别、接口定义、依赖分析 | 模块化Skill |
| 7-通用化 | CTO | 特异性识别、参数化、跨上下文验证 | 通用化Skill |
| 8-发布 | CISO | 最终security审查、法务compliance、ClawHub发布 | 发布URL |

### Module 2: quality gate体系

**功能**: 嵌入G0-G7quality gate，确保输出质量

```yaml
quality_gates:
  G0: { name: "文件结构", check: "目录结构符compliance范" }
  G1: { name: "Frontmatter", check: "YAML格式正确" }
  G2: { name: "描述质量", check: "description > 50字" }
  G3: { name: "security扫描", check: "CVSS < 7.0" }
  G4: { name: "文档完整性", check: "无悬空引用" }
  G5: { name: "脚本测试", check: "零报错" }
  G6: { name: "SKILL.md长度", check: "< 500行" }
  G7: { name: "禁止文件", check: "无README.md等" }
```

### Module 3: review反馈循环

**功能**: review失败时自动修复并重新提交

```yaml
feedback_loop:
  max_iterations: 3
  backoff_strategy: "线性增加review深度"
  escalation:
    condition: "3次未通过"
    action: "上报CEO裁决"
```

### Module 4: 跨Agent协同调度

**功能**: Hub-and-Spoke架构，CEO总控coordination

```
CEO (总控)
  ├── CMO (搜索)
  ├── CQO (质量)
  ├── CTO (技术)
  ├── CISO (security)
  ├── CHO (知识)
  └── CLO (法务)
```

---

## 接口定义

### `learn-skill`

执行完整的skilllearning流程。

**Input:**
```yaml
topic: "PDF处理"
target_platforms: ["clawhub", "github"]
max_search_results: 10
target_level: L3
auto_publish: false
```

**Output:**
```yaml
status: success
skill_name: ai-company-cto-pdf-processor
skill_path: "~/.qclaw/skills/ai-company-cto-pdf-processor"
pipeline_report:
  phases_completed: 8
  phases_total: 8
  quality_score: 95
  security_score: 92
artifacts:
  - "discovery-report.md"
  - "security-review.md"
  - "quality-gate.md"
  - "skill-package.skill"
```

### `search-skills`

仅执行搜索阶段。

**Input:**
```yaml
topic: "string"
platforms: ["clawhub", "github", "web"]
max_results: 10
```

**Output:**
```yaml
results:
  - name: "string"
    source: "clawhub|github|web"
    relevance_score: 0-100
    quality_pre_score: 0-100
```

### `review-skill`

对指定Skill进行review。

**Input:**
```yaml
skill_path: "string"
review_depth: "basic|full"
```

**Output:**
```yaml
verdict: "APPROVED|CONDITIONAL|REJECTED"
quality_score: 0-100
security_score: 0-100
issues: []
```

---

## KPI 仪表板

| 维度 | KPI | 目标值 | 监测频率 |
|------|-----|--------|----------|
| 效率 | 端到端learning周期 | ≤ 2小时 | 按任务 |
| 质量 | quality gate通过率 | ≥ 95% | 按任务 |
| security | security审查通过率 | 100% | 按任务 |
| 产出 | 成功发布率 | ≥ 80% | 月度 |
| 反馈 | 平均修复迭代次数 | ≤ 1.5次 | 按任务 |
| 通用化 | 跨上下文验证通过率 | ≥ 3/3 | 按任务 |

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-04-15 | 初始版本：八阶段learning管道 + quality gate + 反馈循环 |

---

## 使用示例

### 示例1: learningPDF处理skill

```yaml
skill: ai-company-skill-learner
task: learn-skill
params:
  topic: "PDF处理"
  target_platforms: ["clawhub", "github"]
  target_level: L3
```

### 示例2: 仅搜索相关skill

```yaml
skill: ai-company-skill-learner
task: search-skills
params:
  topic: "邮件发送"
  max_results: 5
```

---

*本Skill由AI Company C-Suite联合开发*  
*遵循NIST AI RMF与ISO/IEC 42001:2023标准*
