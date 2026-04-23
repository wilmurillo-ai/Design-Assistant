---
name: venture-capitalist
description: OpenClaw 风险投资分析助手 - 帮助投资者快速审阅商业计划书和路演材料，自动生成投资分析报告和演示文稿 | Help investors quickly review business plans and pitch decks, automatically generate investment analysis reports and presentation decks
version: 1.0.0
author: justin
tags: [openclaw, investment, analysis, vc, pitch-deck, business-plan, due-diligence, 风险投资, 投资分析, 商业计划书]
---

# OpenClaw 风险投资分析助手 | OpenClaw Venture Capitalist

**一句话介绍 | Tagline**: 帮助投资者快速审阅商业计划书和路演材料，自动生成投资分析报告和演示文稿 | Help investors quickly review business plans and pitch decks, automatically generate investment analysis reports and presentation decks.

---

## 概述 | Overview

**中文**：
本 SKILL 为风险投资人和投资者提供以下功能：
- 分析商业计划书和路演材料
- 提取关键信息（市场规模、团队、财务数据、牵引力指标）
- 生成全面的投资分析报告
- 创建投资委员会演示文稿
- 追踪交易管道和投资决策

**English**:
This SKILL helps venture capitalists and investors:
- Analyze business plans and pitch decks
- Extract key information (market size, team, financials, traction)
- Generate comprehensive investment analysis reports
- Create presentation decks for investment committees
- Track deal pipeline and investment decisions

---

## 命令 | Commands

### `/vc analyze <file>`

**中文说明**：分析商业计划书或路演材料文件（支持 PDF、PPT、DOCX）

**English**: Analyze a business plan or pitch deck file (PDF, PPT, DOCX)

**示例 | Example**:
```bash
/vc analyze startup-pitch.pdf
```

**输出 | Output**:
- 执行摘要 | Executive Summary
- 市场分析 | Market Analysis
- 团队评估 | Team Assessment
- 财务审查 | Financial Review
- 风险评估 | Risk Assessment
- 投资建议 | Investment Recommendation

---

### `/vc report <file>`

**中文说明**：生成完整的投资分析报告

**English**: Generate a comprehensive investment analysis report

**选项 | Options**:
- `--format` - 输出格式（markdown、pdf、docx），默认 markdown | Output format (markdown, pdf, docx), default: markdown
- `--template` - 使用自定义模板 | Use custom template
- `--sections` - 指定包含的章节 | Specific sections to include

**示例 | Example**:
```bash
/vc report startup-pitch.pdf --format pdf
```

---

### `/vc deck <file>`

**中文说明**：创建投资委员会演示文稿

**English**: Create an investment committee presentation deck

**示例 | Example**:
```bash
/vc deck startup-pitch.pdf --template ic-presentation
```

---

### `/vc compare <file1> <file2> [...]`

**中文说明**：并排比较多个投资机会

**English**: Compare multiple investment opportunities side-by-side

**示例 | Example**:
```bash
/vc compare startup-a.pdf startup-b.pdf startup-c.pdf
```

---

### `/vc extract <file> <field>`

**中文说明**：从路演材料中提取特定信息

**English**: Extract specific information from a pitch deck

**可提取字段 | Available Fields**:
- `market-size` - 市场规模（TAM/SAM/SOM）| Total addressable market
- `team` - 团队背景和经验 | Team background and experience
- `financials` - 财务预测 | Financial projections
- `traction` - 用户指标和增长 | User metrics and growth
- `competition` - 竞争格局 | Competitive landscape
- `ask` - 融资需求和条款 | Funding ask and terms

**示例 | Example**:
```bash
/vc extract startup-pitch.pdf market-size
```

---

## 分析框架 | Analysis Framework

本 SKILL 使用结构化的 10 维度框架评估投资机会：

This SKILL uses a structured 10-point framework to evaluate investments:

### 1. 市场分析 | Market Analysis
- 总体可寻址市场（TAM）| Total Addressable Market
- 可服务市场（SAM）| Serviceable Addressable Market
- 市场增长率 | Market growth rate
- 市场趋势与动态 | Market trends and dynamics

### 2. 产品/解决方案 | Product/Solution
- 问题陈述 | Problem being solved
- 解决方案独特性 | Solution uniqueness
- 产品市场契合度 | Product-market fit evidence
- 技术/知识产权评估 | Technology/IP assessment

### 3. 团队评估 | Team Assessment
- 创始人背景 | Founder background
- 相关经验 | Relevant experience
- 团队完整性 | Team completeness
- 顾问团 | Advisory board

### 4. 商业模式 | Business Model
- 收入来源 | Revenue streams
- 单位经济 | Unit economics
- 可扩展性 | Scalability
- 客户获取策略 | Customer acquisition strategy

### 5. 牵引力与指标 | Traction & Metrics
- 当前用户/客户 | Current users/customers
- 收入增长 | Revenue growth
- 关键绩效指标 | Key performance indicators
- 已达成的里程碑 | Milestones achieved

### 6. 财务分析 | Financial Analysis
- 收入预测 | Revenue projections
- 烧钱率 | Burn rate
- 资金跑道 | Runway
- 资金使用计划 | Use of funds

### 7. 竞争分析 | Competition
- 竞争格局 | Competitive landscape
- 差异化优势 | Differentiation
- 进入壁垒 | Barriers to entry
- 竞争优势 | Competitive advantages

### 8. 风险评估 | Risk Assessment
- 市场风险 | Market risks
- 执行风险 | Execution risks
- 技术风险 | Technology risks
- 团队风险 | Team risks
- 财务风险 | Financial risks

### 9. 投资条款 | Investment Terms
- 估值 | Valuation
- 融资需求 | Funding ask
- 股权比例 | Equity offered
- 投资结构 | Investment structure

### 10. 投资建议 | Recommendation
- 投资论点 | Investment thesis
- 主要优势 | Key strengths
- 主要顾虑 | Key concerns
- 推进/放弃建议及理由 | Go/No-go recommendation with reasoning

---

## 输出格式 | Output Formats

### 投资分析报告（Markdown）| Investment Analysis Report

包含完整的 10 维度框架分析和投资建议

Includes complete 10-section framework analysis and investment recommendation

### 投资委员会演示文稿（幻灯片）| Investment Committee Deck (Slides)

- 第 1 页：执行摘要 | Slide 1: Executive Summary
- 第 2 页：市场机会 | Slide 2: Market Opportunity
- 第 3 页：产品与解决方案 | Slide 3: Product & Solution
- 第 4 页：团队 | Slide 4: Team
- 第 5 页：商业模式与牵引力 | Slide 5: Business Model & Traction
- 第 6 页：财务数据 | Slide 6: Financials
- 第 7 页：竞争格局 | Slide 7: Competition
- 第 8 页：风险 | Slide 8: Risks
- 第 9 页：投资条款 | Slide 9: Investment Terms
- 第 10 页：建议 | Slide 10: Recommendation

### 对比矩阵（表格）| Comparison Matrix (Table)

并排比较多个投资机会的关键指标

Side-by-side comparison of multiple opportunities across key metrics

---

## 配置 | Configuration

创建 `.vcconfig.json` 文件以自定义分析：

Create a `.vcconfig.json` file to customize analysis:

```json
{
  "analysis_framework": "custom",
  "required_sections": [
    "market",
    "team",
    "product",
    "financials",
    "traction"
  ],
  "scoring": {
    "enabled": true,
    "weights": {
      "market": 0.25,
      "team": 0.30,
      "product": 0.20,
      "traction": 0.15,
      "financials": 0.10
    }
  },
  "report_template": "default",
  "output_directory": "./reports"
}
```

---

## 使用案例 | Use Cases

### 风险投资机构 | For Venture Capital Firms
- 快速筛选交易 | Rapidly screen incoming deals
- 标准化投资分析 | Standardize investment analysis
- 准备合伙人会议 | Prepare for partner meetings
- 追踪交易管道 | Track deal pipeline

### 天使投资人 | For Angel Investors
- 评估创业机会 | Evaluate startup opportunities
- 生成投资备忘录 | Generate investment memos
- 比较多个投资 | Compare multiple investments
- 尽职调查支持 | Due diligence support

### 企业风投 | For Corporate VCs
- 评估战略契合度 | Assess strategic fit
- 分析市场定位 | Analyze market positioning
- 评估技术对齐度 | Evaluate technology alignment
- 生成投资报告 | Generate investment reports

### 投资委员会 | For Investment Committees
- 审查交易摘要 | Review deal summaries
- 比较投资机会 | Compare opportunities
- 做出明智决策 | Make informed decisions
- 追踪投资理由 | Track investment rationale

---

## 最佳实践 | Best Practices

**中文**：
1. 上传完整的路演材料 - 包含所有幻灯片以进行全面分析
2. 提供背景信息 - 添加关于行业重点或投资论点的说明
3. 审查输出结果 - AI 分析应作为补充，而非替代人工判断
4. 自定义模板 - 根据你的投资标准调整分析框架
5. 追踪决策 - 保存报告以供未来参考和模式分析

**English**:
1. Upload complete pitch decks - Include all slides for comprehensive analysis
2. Provide context - Add notes about industry focus or investment thesis
3. Review outputs - AI analysis should supplement, not replace, human judgment
4. Customize templates - Adapt analysis framework to your investment criteria
5. Track decisions - Save reports for future reference and pattern analysis

---

## 使用提示 | Tips

**中文**：
- 在合伙人讨论期间使用 `/vc extract` 获取快速数据点
- 在投资委员会会议前生成 `/vc compare` 报告
- 在 `.vcconfig.json` 中自定义评分权重以匹配你的基金优先级
- 保存所有分析报告以建立投资决策知识库

**English**:
- Use `/vc extract` for quick data points during partner discussions
- Generate `/vc compare` reports before investment committee meetings
- Customize scoring weights in `.vcconfig.json` to match your fund's priorities
- Save all analysis reports to build a knowledge base of investment decisions

---

## 限制说明 | Limitations

**中文**：
- AI 分析仅基于提供的文档
- 无法验证声明或进行独立研究
- 应作为决策支持工具，而非唯一决策者
- 财务预测应独立验证
- 市场数据应与独立来源交叉核对

**English**:
- AI analysis is based on provided documents only
- Cannot verify claims or conduct independent research
- Should be used as a decision support tool, not sole decision maker
- Financial projections should be validated independently
- Market data should be cross-referenced with independent sources

---

## 隐私与安全 | Privacy & Security

**中文**：
- 所有上传的文档在本地处理
- 未经明确同意，不会将数据发送到外部服务
- 投资分析报告仅保存在本地
- 如需要，可在处理前删除敏感信息

**English**:
- All uploaded documents are processed locally
- No data is sent to external services without explicit consent
- Investment analysis reports are saved locally only
- Sensitive information should be redacted before processing if needed

---

## 支持 | Support

**中文支持**：
- GitHub: https://github.com/ZhenRobotics/openclaw-venture-capitalist
- npm: https://www.npmjs.com/package/openclaw-venture-capitalist
- 邮箱: support@openclaw.ai

**English Support**:
- GitHub: https://github.com/ZhenRobotics/openclaw-venture-capitalist
- npm: https://www.npmjs.com/package/openclaw-venture-capitalist
- Email: support@openclaw.ai

---

**用 AI 做出更明智的投资决策** 🚀📊

**Make smarter investment decisions with AI-powered analysis** 🚀📊
