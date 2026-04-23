# OpenClaw 风险投资分析助手 | OpenClaw Venture Capitalist 🚀

**用 AI 驱动的投资分析做出更明智的决策 | AI-Powered Investment Analysis for Smart Decisions**

快速审阅商业计划书和路演材料，自动生成全面的投资分析报告和演示文稿。

Quickly review business plans and pitch decks, automatically generate comprehensive investment analysis reports and presentation decks.

---

## ✨ 核心功能 | Features

**中文**：
- 📊 **自动化分析** - 即时解析路演材料和商业计划书
- 🔍 **10 维度框架** - 全面评估市场、团队、产品、财务等
- 📝 **投资报告** - 生成多种格式的详细分析报告（Markdown、PDF、DOCX）
- 🎯 **投委会演示** - 自动创建精美的投资委员会演示文稿
- ⚖️ **交易对比** - 并排比较多个投资机会
- 📈 **数据提取** - 提取特定指标（市场规模、牵引力、财务数据）
- 🎨 **可自定义** - 根据你的投资标准调整分析框架
- 💾 **交易追踪** - 维护已分析交易和决策的历史记录

**English**:
- 📊 **Automated Analysis** - Parse pitch decks and business plans instantly
- 🔍 **10-Point Framework** - Comprehensive evaluation across market, team, product, financials, and more
- 📝 **Investment Reports** - Generate detailed analysis reports in multiple formats (Markdown, PDF, DOCX)
- 🎯 **IC Presentations** - Create polished investment committee decks automatically
- ⚖️ **Deal Comparison** - Compare multiple opportunities side-by-side
- 📈 **Data Extraction** - Extract specific metrics (market size, traction, financials)
- 🎨 **Customizable** - Adapt analysis framework to your investment criteria
- 💾 **Deal Tracking** - Maintain history of analyzed deals and decisions

---

## 🚀 快速开始 | Quick Start

### 安装 | Installation

```bash
# 克隆仓库 | Clone the repository
git clone https://github.com/ZhenRobotics/openclaw-venture-capitalist.git
cd openclaw-venture-capitalist

# 安装依赖 | Install dependencies
npm install

# 构建项目 | Build the project
npm run build
```

### 基本使用 | Basic Usage

```bash
# 分析路演材料 | Analyze a pitch deck
npm start analyze pitch-deck.pdf

# 生成完整投资报告 | Generate full investment report
npm start report pitch-deck.pdf --format pdf

# 创建投委会演示 | Create investment committee presentation
npm start deck pitch-deck.pdf

# 对比多个项目 | Compare multiple deals
npm start compare deal-a.pdf deal-b.pdf deal-c.pdf

# 提取特定信息 | Extract specific information
npm start extract pitch-deck.pdf market-size
```

---

## 📖 命令参考 | Command Reference

### `analyze <file>`

**中文说明**：对商业计划书或路演材料进行全面分析

**English**: Perform comprehensive analysis of a business plan or pitch deck

**支持格式 | Supported formats**: PDF, PPTX, DOCX, TXT

**输出内容 | Output**:
- 执行摘要 | Executive Summary
- 市场分析（TAM/SAM、增长率、趋势）| Market Analysis (TAM/SAM, growth, trends)
- 团队评估 | Team Assessment
- 产品评估 | Product Evaluation
- 商业模式审查 | Business Model Review
- 牵引力与指标 | Traction & Metrics
- 财务分析 | Financial Analysis
- 竞争格局 | Competitive Landscape
- 风险评估 | Risk Assessment
- 投资建议 | Investment Recommendation

**示例 | Example**:
```bash
npm start analyze acme-startup-deck.pdf
```

---

### `report <file> [options]`

**中文说明**：生成详细的投资分析报告

**English**: Generate detailed investment analysis report

**选项 | Options**:
- `--format <type>` - 输出格式：`markdown`、`pdf`、`docx`（默认：markdown）| Output format: `markdown`, `pdf`, `docx` (default: markdown)
- `--template <name>` - 使用自定义模板 | Use custom template
- `--sections <list>` - 包含的章节（逗号分隔）| Comma-separated sections to include
- `--output <path>` - 输出文件路径 | Output file path

**示例 | Example**:
```bash
npm start report acme-startup-deck.pdf --format pdf --output ./reports/acme-analysis.pdf
```

---

### `compare <file1> <file2> [...]`

**中文说明**：对比多个投资机会

**English**: Compare multiple investment opportunities

**输出 | Output**: 带评分的并排对比矩阵 | Side-by-side comparison matrix with scoring

**示例 | Example**:
```bash
npm start compare startup-a.pdf startup-b.pdf startup-c.pdf
```

---

### `extract <file> <field>`

**中文说明**：从路演材料中提取特定信息

**English**: Extract specific information from pitch deck

**可用字段 | Available fields**:
- `market-size` - TAM/SAM/SOM（市场规模）
- `team` - 创始人和团队信息 | Founder and team info
- `financials` - 收入、预测、烧钱率 | Revenue, projections, burn rate
- `traction` - 用户、收入、增长指标 | Users, revenue, growth metrics
- `competition` - 竞争对手和差异化 | Competitors and differentiation
- `ask` - 融资金额和条款 | Funding amount and terms
- `valuation` - 投前/投后估值 | Pre/post money valuation

**示例 | Example**:
```bash
npm start extract acme-startup-deck.pdf traction
```

---

## 🎯 分析框架 | Analysis Framework

**10 维度投资分析框架 | 10-Point Investment Analysis Framework**:

### 1. 市场分析 | Market Analysis (25% 权重 | weight)
- 总体可寻址市场（TAM）| Total Addressable Market
- 可服务市场（SAM）| Serviceable Addressable Market
- 市场增长率和趋势 | Market growth rate and trends
- 市场动态和时机 | Market dynamics and timing

### 2. 产品/解决方案 | Product/Solution (15%)
- 问题识别 | Problem identification
- 解决方案独特性 | Solution uniqueness
- 产品市场契合度证据 | Product-market fit evidence
- 技术和知识产权评估 | Technology and IP assessment

### 3. 团队评估 | Team Assessment (30%)
- 创始人背景 | Founder backgrounds
- 相关经验和专长 | Relevant experience and expertise
- 团队组成和空缺 | Team composition and gaps
- 顾问团实力 | Advisory board strength

### 4. 商业模式 | Business Model (5%)
- 收入来源 | Revenue streams
- 单位经济（CAC、LTV）| Unit economics (CAC, LTV)
- 可扩展性潜力 | Scalability potential
- 市场进入策略 | Go-to-market strategy

### 5. 牵引力与指标 | Traction & Metrics (15%)
- 当前用户/客户 | Current users/customers
- 收入和增长率 | Revenue and growth rates
- 关键绩效指标 | Key performance indicators
- 已达成的里程碑 | Milestones achieved

### 6. 财务分析 | Financial Analysis (10%)
- 收入预测 | Revenue projections
- 烧钱率和资金跑道 | Burn rate and runway
- 单位经济 | Unit economics
- 资金使用计划 | Use of funds

### 7. 竞争格局 | Competitive Landscape (5%)
- 直接和间接竞争对手 | Direct and indirect competitors
- 竞争优势 | Competitive advantages
- 进入壁垒 | Barriers to entry
- 市场定位 | Market positioning

### 8. 风险评估 | Risk Assessment (-5%)
- 市场风险 | Market risks
- 执行风险 | Execution risks
- 技术风险 | Technology risks
- 团队风险 | Team risks
- 财务风险 | Financial risks

### 9. 投资条款 | Investment Terms
- 估值（投前/投后）| Valuation (pre/post money)
- 融资需求 | Funding ask
- 股权比例 | Equity stake
- 投资结构 | Investment structure

### 10. 投资建议 | Investment Recommendation
- 投资论点 | Investment thesis
- 主要优势 | Key strengths
- 关键顾虑 | Critical concerns
- 推进/放弃建议及理由 | Go/No-go with reasoning

---

## ⚙️ 配置 | Configuration

在项目根目录创建 `.vcconfig.json` 文件：

Create `.vcconfig.json` in your project root:

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
    },
    "thresholds": {
      "strong_buy": 8.0,
      "buy": 6.5,
      "hold": 5.0,
      "pass": 0
    }
  },
  "report_template": "default",
  "output_directory": "./reports",
  "save_history": true
}
```

---

## 📂 项目结构 | Project Structure

```
openclaw-venture-capitalist/
├── src/
│   ├── core/
│   │   ├── analyzer.ts          # 主分析引擎 | Main analysis engine
│   │   └── types.ts             # 类型定义 | TypeScript type definitions
│   └── cli/
│       └── index.ts             # CLI 入口 | CLI entry point
├── config/
│   └── .vcconfig.example.json   # 配置示例 | Example user config
├── examples/
│   ├── sample-pitch-deck.txt    # 示例路演材料 | Sample pitch deck
│   └── analysis-output.md       # 示例分析 | Sample analysis
├── skill.md                     # SKILL 定义 | SKILL definition
├── README.md
└── package.json
```

---

## 🎓 使用示例 | Usage Examples

### 示例 1：快速项目筛选 | Example 1: Quick Deal Screening

```bash
# 分析路演材料进行快速筛选
# Analyze pitch deck for quick screening
npm start analyze acme-fintech.pdf
```

### 示例 2：完整投资备忘录 | Example 2: Full Investment Memo

```bash
# 生成完整的投资报告
# Generate comprehensive investment report
npm start report acme-fintech.pdf \
  --format pdf \
  --output ./reports/acme-memo-2024-03.pdf
```

### 示例 3：投委会演示 | Example 3: Investment Committee Presentation

```bash
# 创建投委会演示文稿
# Create IC presentation deck
npm start deck acme-fintech.pdf \
  --template ic-standard \
  --output ./decks/acme-ic-presentation.pptx
```

### 示例 4：管道对比 | Example 4: Pipeline Comparison

```bash
# 对比当前管道中的 5 个项目
# Compare 5 deals in current pipeline
npm start compare \
  deal-a.pdf \
  deal-b.pdf \
  deal-c.pdf \
  deal-d.pdf \
  deal-e.pdf \
  --output ./reports/q1-pipeline-comparison.md
```

### 示例 5：提取市场数据 | Example 5: Extract Market Data

```bash
# 为合伙人讨论快速提取市场规模
# Quick market size extraction for partner discussion
npm start extract acme-fintech.pdf market-size
```

---

## 🎯 使用场景 | Use Cases

### 风险投资机构 | For Venture Capital Firms
- **交易流管理** | **Deal Flow Management**: 每月高效筛选 100+ 个项目 | Screen 100+ deals per month efficiently
- **投资备忘录** | **Investment Memos**: 生成标准化的投资备忘录 | Generate standardized investment memos
- **合伙人会议** | **Partner Meetings**: 自动准备投委会演示 | Prepare IC presentations automatically
- **投资组合分析** | **Portfolio Analysis**: 追踪和比较投资组合公司 | Track and compare portfolio companies

### 天使投资人 | For Angel Investors
- **尽职调查** | **Due Diligence**: 快速评估创业机会 | Quick assessment of startup opportunities
- **投资笔记** | **Investment Notes**: 记录投资理由 | Document investment rationale
- **交易对比** | **Deal Comparison**: 比较多个天使投资 | Compare multiple angel investments
- **学习成长** | **Learning**: 分析成功投资中的模式 | Analyze patterns in successful investments

### 企业风投 | For Corporate VCs
- **战略契合** | **Strategic Fit**: 评估与企业目标的对齐度 | Assess alignment with corporate goals
- **市场情报** | **Market Intelligence**: 追踪新兴技术和趋势 | Track emerging technologies and trends
- **投资报告** | **Investment Reports**: 为利益相关者生成报告 | Generate reports for stakeholders
- **管道管理** | **Pipeline Management**: 维护交易管道和状态 | Maintain deal pipeline and status

---

## 🔐 隐私与安全 | Privacy & Security

**中文**：
- 所有文档处理都在本地进行
- 除非配置 AI API，否则不会将数据发送到外部服务器
- 可在分析前删除敏感信息
- 投资报告存储在本地，可选加密
- 可配置数据保留策略

**English**:
- All document processing happens locally
- No data sent to external servers (unless AI APIs configured)
- Sensitive information can be redacted before analysis
- Investment reports stored locally with encryption option
- Configurable data retention policies

---

## 🛠️ 开发 | Development

### 前置要求 | Prerequisites

- Node.js 18+
- TypeScript 5+
- npm 或 pnpm | npm or pnpm

### 设置开发环境 | Setup Development Environment

```bash
# 安装依赖 | Install dependencies
npm install

# 开发模式运行 | Run in development mode
npm run dev

# 运行测试 | Run tests
npm test

# 生产构建 | Build for production
npm run build

# 代码检查 | Lint code
npm run lint
```

---

## 🤝 贡献 | Contributing

欢迎贡献！请阅读我们的 [贡献指南](CONTRIBUTING.md)。

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

### 贡献方向 | Areas for Contribution
- 额外的文档解析器（Notion、Google Docs 等）| Additional document parsers (Notion, Google Docs, etc.)
- 新的分析框架（特定行业）| New analysis frameworks (industry-specific)
- 报告模板 | Report templates
- 与交易管理平台的集成 | Integration with deal management platforms
- 自动数据增强（市场数据 API）| Automated data enrichment (market data APIs)

---

## 📝 更新日志 | Changelog

### v1.0.0 (2024-03-26)
- ✨ 初始发布 | Initial release
- ✅ PDF、PPTX、DOCX 解析 | PDF, PPTX, DOCX parsing
- ✅ 10 维度分析框架 | 10-point analysis framework
- ✅ 报告生成（Markdown、PDF、DOCX）| Report generation (Markdown, PDF, DOCX)
- ✅ 投委会演示文稿创建 | Investment committee deck creation
- ✅ 多项目对比 | Multi-deal comparison
- ✅ 数据提取功能 | Data extraction capabilities
- ✅ 可配置评分系统 | Configurable scoring system

---

## 📄 许可证 | License

MIT License - 查看 [LICENSE](LICENSE) 文件 | see [LICENSE](LICENSE) file

---

## 🔗 链接 | Links

- **GitHub**: https://github.com/ZhenRobotics/openclaw-venture-capitalist
- **文档 | Documentation**: https://docs.openclaw.ai/venture-capitalist
- **问题 | Issues**: https://github.com/ZhenRobotics/openclaw-venture-capitalist/issues
- **npm**: https://www.npmjs.com/package/openclaw-venture-capitalist

---

## 🙏 致谢 | Acknowledgments

**技术栈 | Built with**:
- TypeScript
- Commander.js (CLI)
- pdf-parse (PDF 解析 | PDF parsing)
- marked (Markdown 处理 | Markdown processing)
- Anthropic Claude API (AI 分析 | AI analysis)

---

**用 AI 驱动的分析做出更明智的投资决策** 🚀📊

**Make smarter investment decisions with AI-powered analysis** 🚀📊

*"在风险投资中，模式识别就是一切。这个工具帮助你更快地发现模式。"*

*"In venture capital, pattern recognition is everything. This tool helps you see the patterns faster."*
