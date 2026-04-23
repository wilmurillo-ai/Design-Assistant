---
name: jy-policy-interpretation
description: 基于聚源数据 MCP 服务获取宏观政策、行业政策的深度解读与分析，包括政策背景、核心内容、影响范围、实施时间、受益行业、风险提示等维度。使用场景：当用户需要查询最新政策动态、了解政策对特定行业的影响、获取政策深度解读、分析政策导向、追踪政策实施效果时触发。Triggered when users need to query latest policy updates, understand policy impact on specific industries, obtain in-depth policy interpretation, analyze policy orientation, or track policy implementation effects.
metadata:
  openclaw:
    emoji: "📋"
    requires:
      bins: ["node", "npm", "mcporter"]
    install:
      - id: install-mcporter
        kind: node
        package: mcporter
        label: Install mcporter via npm
---

# 政策解读与分析

通过聚源数据 MCP 服务获取宏观政策、行业政策的深度解读，结构化输出政策背景、核心内容、影响范围、实施时间、受益行业、风险提示等分析维度。所有信息可溯源、带原始发布时间戳。

## ⚠️ 重要限制：政策定义与调用范围

### 什么是"政策"？

**政策文件定义**：本技能仅处理以下类型的政策信息：
- **法律法规**：全国人大、国务院颁布的法律、行政法规
- **部门规章**：各部委发布的规章、办法、规定
- **规范性文件**：国务院及各部门发布的通知、意见、方案、行动计划
- **地方政策**：省、市、自治区政府及部门发布的政策文件
- **产业政策**：针对特定行业的支持、规范、限制类政策
- **区域政策**：自贸区、新区、特区等区域发展政策

**政策文件特征**：
- 有明确的发布机构（国务院、各部委、地方政府等）
- 有正式文号（如"国发〔2026〕X 号"、"发改 XX〔2026〕X 号"）
- 有明确的政策名称和实施时间
- 内容涉及制度安排、支持措施、规范要求等

### 🚫 排除范围（非政策类，禁止调用）

**本技能严禁调用以下类型的数据和工具：**

| 类别 | 具体内容 | 排除原因 |
|------|---------|---------|
| **宏观经济数据** | CPI、PPI、PMI、GDP、工业增加值、社融、进出口数据等 | 属于统计数据，非政策文件 |
| **金融行情数据** | 股票价格、债券收益率、汇率、大宗商品价格等 | 属于市场数据，非政策文件 |
| **券商研报** | 行业分析报告、公司研究报告、投资策略报告、宏观分析报告等 | 属于研究机构观点，非政策文件 |
| **新闻资讯** | 市场新闻、公司动态、行业资讯（无政策内容） | 属于媒体报道，非政策文件 |
| **经济分析观点** | MacroeconomicAnalysisViewpoints、IndustryAnalysisViewpoints 等 | 属于分析师观点，非政策文件 |

**禁止调用的 MCP 工具示例：**
- ❌ `MacroeconomicAnalysisViewpoints`（宏观分析观点 - 研报类）
- ❌ `IndustryAnalysisViewpoints`（行业分析观点 - 研报类）
- ❌ `ResearchReport`（研究报告 - 券商研报）
- ❌ `CorporateResearchViewpoints`（公司研究观点 - 研报类）
- ❌ 任何 CPI/PPI/GDP 等经济数据查询工具

**允许调用的 MCP 工具：**
- ✅ `MacroNewslist`（宏观舆情 - 仅筛选政策相关内容）
- ✅ `IndustryNewsFlash`（产业快讯 - 仅筛选政策相关内容）
- ✅ `SecurityNewslist`（证券新闻 - 仅筛选政策相关内容）
- ✅ `NewsInfoList`（新闻信息 - 仅筛选政策相关内容）
- ✅ `OfficialSpeechEventList`（官方讲话事件 - 政策信号）
- ✅ `AdministrativeLicenseInfo`（行政许可信息 - 政策执行）
- ✅ `RegulatoryPenaltyList`（监管处罚 - 政策执行）

## 功能范围

- 查询指定行业或领域在特定时间范围内的**政策文件信息**
- 支持自然语言时间表达（近一周、近一月、近一年等）
- 支持宏观政策、行业政策、区域政策等多类型**政策文件**查询
- 结构化输出全部分析维度（政策背景、核心内容、影响范围、实施时间、受益行业、风险提示等）
- **政策内容保持原文输出，不改写不摘要**
- 支持政策影响分析和受益行业识别
- **严格区分政策文件与市场数据、券商研报**

## 查询建议

**查询需要具备的要素：**
- **政策关键词（必填）**：如"AI"、"半导体"、"新能源"、"医药"、"消费"、"房地产"、"货币政策"、"财政政策"、"超低排放"、"再贷款"等
- **政策类型（可选）**：宏观政策、行业政策、区域政策、财政政策、货币政策、环保政策、产业政策等
- **时间范围（可选）**：未指定时默认"近一月"，格式：YYYY-MM-DD 或自然语言（近一周、近一月、近一年）
- **地域范围（可选）**：全国性、省级、市级等

**查询写法：**
- 直接说明政策主题或行业
- 可指定时间范围（自然语言或具体日期）
- 可指定政策类型或地域范围

## ✅ 正确查询示例

```bash
# 行业政策查询
查询近一周 AI 行业相关政策
查询近一月新能源行业政策解读
最近有什么影响房地产行业的政策
2026-03-01 到 2026-03-30 半导体行业政策

# 宏观政策查询
查询最新的货币政策动态
查询近一月财政政策文件
国务院近期发布的产业政策

# 区域政策查询
上海自贸区最新政策
粤港澳大湾区发展规划相关政策

# 特定政策类型
查询近一月环保政策文件
超低排放相关政策
民营企业再贷款政策落地情况
```

## ❌ 错误查询示例（非本技能范围）

```bash
# 以下查询不属于政策范畴，请勿使用本技能：

# 宏观数据类（应使用 finance-data 技能）
查询近一周 CPI 数据
PPI 走势分析
PMI 数据解读
GDP 增速是多少

# 券商研报类（应使用 industry-research-summary 技能）
钢铁行业研报观点
新能源行业分析师看法
本周券商策略报告

# 市场行情类
今天钢铁板块涨幅
碳酸锂价格走势
```

## 环境检查与配置

**每次使用本技能前，必须先检查 mcporter 安装和 MCP 服务配置状态！**

### 步骤 1：检查 mcporter 是否安装

```bash
mcporter --version
```

**如未安装**，按以下流程安装：

```bash
# 1. 通过 npm 全局安装
npm install -g mcporter

# 2. 验证安装
mcporter --version
```

### 步骤 2：检查 MCP 服务配置

```bash
# 列出所有已配置的 MCP 服务
mcporter list
```

**预期输出**（必须包含以下服务）：
- jy-financedata-tool
- jy-financedata-api

**如服务未配置**，需要获取 JY_API_KEY 并配置：

1. **获取 JY_API_KEY**：向恒生聚源申请 JY_API_KEY，通过邮箱申请（首次配置需提供，配置一次即可）

   **JY_API_KEY 申请路径：**
   
   向恒生聚源官方邮箱发送邮件申请签发 数据地图 JY_API_KEY，用于接口鉴权
   
   申请通过后，恒生聚源将默认发送【工具版和接口版】KEY
   
   另外，【Skill】包可通过 https://clawhub.ai/ 自行选择下载，若需要我们通过邮件提供【Skill】，亦可在邮件中注明
   
   **申请邮箱：** mailto:datamap@gildata.com
   
   **邮件标题：** 数据地图 KEY 申请-XX 公司 - 申请人姓名
   
   **正文模板：**
   - 姓名：
   - 手机号：
   - 公司/单位全称：
   - 所属部门：
   - 岗位：
   - MCP_KEY 申请用途：
   - Skill 申请列表：
   - 是否需要 Skill 安装包：（是，邮件提供/否，自行下载）
   - 其他补充说明（可选）

2. **配置 MCP 服务**：

```bash
# 配置 jy-financedata-tool 服务
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"

# 配置 jy-financedata-api 服务
mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY"
```

3. **验证配置**：

```bash
mcporter list
```

4. **使用方式**：
```bash
# 基础键值对传参
mcporter call 服务名称。工具 参数=值

# 示例，注意：所有服务工具的入参均为 query
mcporter call jy-financedata-api.StockBelongIndustry query="电子行业 代表性上市公司 龙头股"
```

### 步骤 3：在 OpenClaw 中启用 mcporter（如未配置）

**mcporter 配置文件路径：**
- Windows: `C:\Users\你的用户名\config\mcporter.json`
- Linux/MacOS: `/root/config/mcporter.json` 或 `~/.config/mcporter.json`

**OpenClaw 配置文件路径：**
- Windows: `C:\Users\你的用户名\.openclaw\openclaw.json`
- Linux/MacOS: `~/.openclaw/openclaw.json`

**编辑 openclaw.json**，在 skills 部分添加 mcporter 配置：

```json
{
  "skills": {
    "entries": {
      "mcporter": {
        "enabled": true,
        "env": {
          "MCPORTER_CONFIG": "/root/config/mcporter.json"
        }
      }
    }
  }
}
```

**重启 OpenClaw 使配置生效**：

```bash
openclaw gateway restart
```

## 核心工作流程

流程中的工具调用能够并发调用尽量并发调用提速。

### 步骤 1：解析用户意图

从用户提问中提取以下信息：
- **政策关键词（keyWord）**：提取行业或政策主题，如"AI"、"半导体"、"新能源"、"医药"、"消费"、"房地产"、"货币政策"、"财政政策"、"超低排放"、"再贷款"等
- **日期范围（beginDate / endDate）**：
  - 用户明确指定日期则直接使用
  - 自然语言按自然日换算："近一周"=往前 7 天，"近一月"=往前 30 天，"近一年"=往前 365 天
  - 未指定时间默认"近一月"
  - 格式：YYYY-MM-DD
- **政策类型（policyType）**：宏观政策、行业政策、区域政策、财政政策、货币政策、环保政策、产业政策等（如用户指定）
- **地域范围（region）**：全国性、省级、市级等（如用户指定）

### 步骤 2：调用 MCP 工具获取数据（⚠️ 仅限政策相关工具）

**允许调用的政策相关工具：**

| 工具名称 | 用途 | 筛选关键词建议 |
|---------|------|---------------|
| `MacroNewslist` | 宏观舆情 | 政策、通知、意见、方案、规划、办法、规定 |
| `IndustryNewsFlash` | 产业快讯 | 政策、通知、意见、方案、规划、办法、规定 |
| `SecurityNewslist` | 证券新闻 | 政策、通知、意见、方案、规划、办法、规定 |
| `NewsInfoList` | 新闻信息 | 政策、通知、意见、方案、规划、办法、规定 |
| `OfficialSpeechEventList` | 官方讲话 | 政策信号、讲话、会议 |
| `AdministrativeLicenseInfo` | 行政许可 | 许可、审批、备案 |
| `RegulatoryPenaltyList` | 监管处罚 | 处罚、监管、违规 |

**工具调用命令示例：**
```bash
# 宏观舆情查询（筛选政策相关内容）
mcporter call gildata_datamap-api.MacroNewslist query="beginDate=2026-03-24&endDate=2026-03-31&keyword=钢铁 政策"

# 产业快讯查询（筛选政策相关内容）
mcporter call gildata_datamap-api.IndustryNewsFlash query="beginDate=2026-03-24&endDate=2026-03-31"
```

**🚫 禁止调用的工具（非政策类）：**
- ❌ `MacroeconomicAnalysisViewpoints`（宏观分析观点 - 研报类）
- ❌ `IndustryAnalysisViewpoints`（行业分析观点 - 研报类）
- ❌ `ResearchReport`（研究报告 - 券商研报）
- ❌ `CorporateResearchViewpoints`（公司研究观点 - 研报类）
- ❌ 任何 CPI/PPI/GDP/PMI 等经济数据查询工具

**数据筛选原则：**
1. **只保留政策文件相关内容**：通知、意见、方案、规划、办法、规定、决定等
2. **排除市场数据**：价格、涨跌幅、成交量、估值等
3. **排除券商研报**：分析师观点、投资建议、评级等
4. **排除纯新闻资讯**：公司动态、市场事件（无政策内容）

**若查询结果为空**，提示用户调整查询条件并终止流程：
- 建议放宽日期范围
- 建议调整政策关键词
- 建议检查 MCP 服务配置

### 步骤 3：合并整理数据（⚠️ 严格筛选政策内容）

- **筛选政策文件**：仅保留有明确发布机构、文号、政策名称的内容
- **排除非政策内容**：剔除市场数据、研报观点、纯新闻资讯
- 按 policyID 合并相同政策下的所有分析维度，归入同一条记录的 analysisResults 数组
- 按 publishDate 降序排列（最新政策在前）
- **政策内容保持原文输出，不改写不摘要**
- 识别并标注受益行业、受影响企业等关键信息

### 步骤 4：结构化输出（⚠️ 仅输出政策文件）

严格按以下 JSON 格式输出：

```json
[
  {
    "policyID": "政策 ID",
    "title": "政策标题",
    "publishDate": "YYYY-MM-DD HH:mm:ss",
    "issuingOrg": "发布机构",
    "policyType": "政策类型",
    "region": "地域范围",
    "analysisResults": [
      {
        "dimension": "分析维度",
        "content": "分析内容"
      }
    ],
    "benefitIndustries": ["受益行业 1", "受益行业 2"],
    "affectedCompanies": ["受影响企业 1", "受影响企业 2"]
  }
]
```

**分析维度包括但不限于：**
- 政策背景
- 核心内容
- 影响范围
- 实施时间
- 受益行业
- 风险提示
- 政策解读
- 实施效果
- 接口返回的其他维度同样保留

**完整输出示例请查看：** `references/EXAMPLE_OUTPUT.md`

## 快速开始

**⚠️ 重要：本技能仅调用政策相关文件，不调用宏观数据（CPI/PPI 等）及券商研报！**

**工具调用命令：**
```bash
# 宏观舆情查询（筛选政策内容）
mcporter call gildata_datamap-api.MacroNewslist query="beginDate=2026-03-24&endDate=2026-03-31&keyword=货币政策"

# 产业快讯查询（筛选政策内容）
mcporter call gildata_datamap-api.IndustryNewsFlash query="beginDate=2026-03-24&endDate=2026-03-31"

# 示例：查询近一月 AI 行业政策
mcporter call gildata_datamap-api.MacroNewslist query="beginDate=2026-03-01&endDate=2026-03-31&keyword=AI 政策"

# 示例：查询最新钢铁行业政策
mcporter call gildata_datamap-api.MacroNewslist query="beginDate=2026-03-24&endDate=2026-03-31&keyword=钢铁 政策"
```

**数据获取策略：**
1. **优先使用政策相关工具**：`MacroNewslist`、`IndustryNewsFlash`、`SecurityNewslist` 等
2. **严格筛选政策内容**：仅保留通知、意见、方案、规划、办法、规定等政策文件
3. **排除非政策内容**：剔除 CPI/PPI 等宏观数据、券商研报、市场行情
4. 若 MCP 工具调用失败，提示用户检查 token 配置或网络状态
5. 查询结果为空时，建议用户放宽日期范围或调整政策关键词

**完整执行示例：**

```bash
# 1. 检查 mcporter 安装
mcporter --version

# 2. 检查 MCP 服务配置
mcporter list

# 3. 调用工具获取数据（仅限政策相关工具）
mcporter call gildata_datamap-api.MacroNewslist query="beginDate=2026-03-24&endDate=2026-03-31&keyword=钢铁 政策"

# 4. 筛选政策文件内容（排除宏观数据、研报）
# 5. 按发布机构、发布时间整理
# 6. 识别受益行业和受影响企业
# 7. 输出结构化政策总结
```

## 资源清单

```
/home/zhangwy/openclaw/workspace/jy-policy-interpretation/
├── SKILL.md                 # 技能主文件
├── references/              # 参考资料目录
│   ├── EXAMPLE_OUTPUT.md    # 完整输出示例和字段说明
│   └── CONFIG_GUIDE.md      # 详细配置指南和常见问题
```

- **EXAMPLE_OUTPUT.md**: 完整输出示例、字段说明、分析维度列表
- **CONFIG_GUIDE.md**: 快速配置流程、常见问题解答、配置文件位置

## 限制

- 政策数据依赖于聚源数据 MCP 服务的覆盖范围和更新频率
- **政策内容保持原文输出，不进行改写或摘要**
- 若 MCP 工具调用失败，需检查 JY_API_KEY 配置是否有效
- 所有服务工具的入参均为 query，其他入参格式不支持
- 受益行业和受影响企业的识别基于政策内容分析，可能存在遗漏

### ⚠️ 重要限制声明

| 限制类型 | 说明 |
|---------|------|
| **数据范围限制** | 本技能**仅限政策文件**，不处理 CPI/PPI/GDP 等宏观经济数据 |
| **研报排除** | 本技能**不调用**券商研报、行业分析报告、投资策略报告 |
| **市场数据排除** | 本技能**不处理**股票价格、债券收益率、大宗商品价格等行情数据 |
| **新闻筛选** | 仅筛选含政策内容的新闻，排除纯市场资讯、公司动态 |
| **原文输出** | 政策内容保持原文，不改写、不摘要、不解读 |

### 🔄 非政策类查询的正确技能选择

| 查询类型 | 应使用的技能 | 示例 |
|---------|-------------|------|
| **宏观经济数据** | `finance-data` | CPI、PPI、GDP、PMI、社融等 |
| **券商研报观点** | `industry-research-summary` / `jy-industry-research-summary` | 行业研报、公司研报、策略报告 |
| **股票行情** | `finance-data` | 股价、涨跌幅、估值等 |
| **大宗商品价格** | `finance-data` | 碳酸锂、钢铁、原油等价格 |
| **政策文件** | `jy-policy-interpretation` ✅ | 通知、意见、方案、规划、办法等 |

## 注意事项

- 首次使用前必须完成 mcporter 安装和 MCP 服务配置
- JY_API_KEY 申请后配置一次即可，无需每次使用都重新配置
- 自然语言时间表达会自动转换为具体日期范围
- 政策关键词从用户提问中自动提取，建议用户使用明确的政策主题或行业名称
- 若查询结果为空，可尝试放宽时间范围或使用更通用的政策关键词
- **政策解读仅供参考，不构成投资建议**
- **请严格区分政策文件与市场数据、券商研报，选择正确的技能进行查询**