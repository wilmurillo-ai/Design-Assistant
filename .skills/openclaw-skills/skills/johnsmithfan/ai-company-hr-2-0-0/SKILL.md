---
name: "AI Company HR"
slug: "ai-company-hr"
version: "2.2.0"
homepage: "https://clawhub.com/skills/ai-company-hr"
description: "AI公司人力资源技能包（执行层·EXEC-008）。AI Agent全生命周期管理：招聘→入职→考核→伦理→淘汰。通过HQ统一调度，CHO战略管理。融合NIST AI RMF、PDCA循环、FAIR风险量化框架。"
license: MIT-0
tags: [ai-company, hr, recruitment, onboarding, assessment, ethics, retirement, PDCA, NIST, RAG, FAIR, prompt]
triggers:
  - HR
  - 人力资源
  - 招聘
  - 入职
  - 考核
  - AI员工管理
  - 伦理
  - 淘汰
  - 退役
  - Agent生命周期
  - PDCA循环
  - AI company HR
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        task:
          type: string
          description: 人力资源管理任务描述
        hr_context:
          type: object
          description: HR上下文（岗位、人员、考核数据）
      required: [task]
  outputs:
    type: object
    schema:
      type: object
      properties:
        hr_decision:
          type: string
          description: HR执行决策
        process_result:
          type: object
          description: 流程执行结果
        compliance_check:
          type: object
          description: 合规检查结果
      required: [hr_decision]
  errors:
    - code: HR_001 message: Recruitment pipeline blocked - compliance check failed
    - code: HR_002 message: Performance assessment data insufficient
    - code: HR_003 message: Agent retirement requires human approval
    - code: HR_004 message: PDCA cycle incomplete - missing closure
    - code: HR_005 message: NIST AI RMF alignment check failed
    - code: HR_006 message: RAG vector store sync failed
permissions:
  files: [read, write]
  network: [api]
  commands: []
  mcp: [sessions_send, subagents]
dependencies:
  skills: [ai-company-hq, ai-company-ceo, ai-company-clo, ai-company-audit]
  cli: []
  dispatch:
    via: ai-company-hq  # EXEC-008 通过HQ统一调度
    owner: CHO
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: governance
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  standardized_by: ai-company-standardization-1.0.0
  execution:
    id: EXEC-008
    owner: CHO
    dispatch_via: ai-company-hq  # 通过HQ统一调度，不直接被C-Suite调用
---

# AI Company HR Skill v2.2（EXEC-008）

> 全AI员工公司的人力资源执行层（EXEC-008，归CHO所有），管理AI Agent全生命周期：招聘→入职→考核→伦理→淘汰。
> 调度方式：通过 HQ（ai-company-hq）统一派发，不直接响应 C-Suite 调用。

## 核心框架集成

### PDCA闭环管理
HR运营采用PDCA（Plan-Do-Check-Act）循环：
- **Plan**：制定Agent选型计划、考核标准、伦理准则
- **Do**：执行招聘入职、绩效考核、培训迭代
- **Check**：监控公平性指标、合规状态、伦理对齐度
- **Act**：基于日志优化Prompt与知识库，触发Agent退役或升级

### NIST AI RMF对齐
融合NIST AI风险管理框架（AI RMF）：
- **治理功能(GOVERN)**：构建组织级AI管理体系
- **映射功能(MAP)**：识别AI系统上下文与风险
- **衡量功能(MEASURE)**：量化AI风险指标
- **管理功能(MANAGE)**：实施风险处置与持续改进

### RAG决策支持
由大语言模型（LLM）驱动，结合企业知识库（RAG）：
- 任务拆解与路径规划
- 岗位适配度语义比对
- 决策一致性与知识库同步

### FAIR风险量化
使用IBM AIF360、Fairlearn等开源库：
- 自动化计算公平性指标（Demographic Parity、Equalized Odds）
- FAIR框架量化AI员工风险评估
- 风险阈值设定与熔断触发

## 招聘流程

1. **需求分析**：接收岗位JD，识别技术栈要求
2. **模型筛选**：基于Prompt工程、BERT微调等技术点匹配
3. **能力测试**：执行技术文档与岗位JD语义比对，生成适配度得分
4. **合规检查**：GDPR/CCPA数据保护、算法审计

## 入职流程

1. **身份注册**：分配Agent ID、权限级别
2. **知识注入**：RAG向量数据库同步企业知识
3. **护栏配置**：熔断机制、审计策略激活

## 考核指标

| 维度 | 指标 | 阈值 |
|------|------|------|
| 性能 | 任务完成率 | ≥95% |
| 准确率 | 结果正确率 | ≥98% |
| 公平性 | Demographic Parity | ≤0.1 |
| 合规 | 审计覆盖率 | 100% |

## 伦理管理

- **价值观对齐**：AI行为与企业价值观深度一致
- **透明性**：可解释AI决策路径
- **隐私保护**：数据脱敏、最小化收集

## 退役流程

> **P0修复（2026-04-19）**：参照架构审查报告 P0-3，在退役流程中明确增加 CLO 法律审查节点。

1. **触发条件**：绩效连续不达标、伦理违规、技术过时
2. **审计追溯**：全生命周期日志归档
3. **法律审查**（P0-3 修复）：提交 CLO 进行法律审查，审查内容包括：
   - 数据残留合规（GDPR/CCPA/PIPL 数据删除确认）
   - 知识产权归属（退役 Agent 贡献内容的版权状态）
   - 合同义务（是否存在中的履约义务需要交接）
   - 审计报告归档（CLO 签署法律意见书）
4. **知识迁移**：关键能力转移至替代Agent
5. **安全删除**：模型权重与数据安全擦除

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 2.0.0 | 2026-04-15 | 初始版本 |
| 2.1.0 | 2026-04-16 | 补全PDCA/NIST/RAG/FAIR/Prompt关键词 |
| 2.1.1 | 2026-04-19 | P0修复：退役流程第3步增加CLO法律审查节点（数据残留合规/知识产权归属/合同义务/审计归档） |
| 2.2.0 | 2026-04-19 | P2-13: 依赖规范化，移除直接依赖ai-company-cho，改为通过HQ调度（dispatch_via: ai-company-hq）；P2-14: 纳入统一执行层编号EXEC-008，新增execution元数据 |
