---
name: jy-industry-research-summary
description: 基于聚源数据 MCP 服务获取券商行业研报观点速览，结构化输出行业发展趋势、竞争格局、技术创新、政策环境、投资建议、风险提示等分析维度。使用场景：当用户需要快速了解某行业的券商研报观点、查询特定行业的投资分析、获取行业发展趋势、竞争格局分析、政策解读、投资建议或风险提示时触发。Triggered when users need to quickly understand broker research report views on a specific industry, query investment analysis for a particular industry, obtain industry development trends, competitive landscape analysis, policy interpretation, investment recommendations, or risk warnings.
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins: ["node", "npm", "mcporter"]
    install:
      - id: install-mcporter
        kind: node
        package: mcporter
        label: Install mcporter via npm
---

# 行业研报观点速览

通过聚源数据 MCP 服务获取券商研究报告，结构化输出行业发展趋势、竞争格局、技术创新、政策环境、投资建议、风险提示等分析维度。所有信息可溯源、带原始发布时间戳。

## 功能范围

- 查询指定行业在特定时间范围内的券商研报观点
- 支持自然语言时间表达（近一周、近一月等）
- 限定主流券商机构范围（广发证券、国泰海通、招商证券等 12 家）
- 结构化输出全部分析维度（行业发展趋势、竞争格局、技术创新、政策环境、投资建议、风险提示等）
- 观点内容保持原文输出，不改写不摘要

## 查询建议

**查询需要具备的要素：**
- 行业关键词（必需）：如"AI"、"半导体"、"新能源"、"医药"、"消费"等
- 时间范围（可选）：未指定时默认"近一周"
- 券商机构（可选）：默认查询 12 家主流券商

**查询写法：**
- 直接说明行业名称
- 可指定时间范围（自然语言或具体日期）
- 可指定特定券商（可选）

## 查询示例

```
查询近一周 AI 行业的券商研报观点
查询 2026-03-01 到 2026-03-25 半导体行业研报
新能源行业最近有什么研报观点
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
mcporter call jy-financedata-tool.StockBelongIndustry query="电子行业 代表性上市公司 龙头股"
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
- **行业关键词（keyWord）**：提取行业名称，如"AI"、"半导体"、"新能源"、"医药"、"消费"等
- **日期范围（beginDate / endDate）**：
  - 用户明确指定日期则直接使用
  - 自然语言按自然日换算："近一周"=往前 7 天，"近一月"=往前 30 天，以此类推
  - 未指定时间默认"近一周"
  - 格式：YYYY-MM-DD
- **券商机构限制**：仅查询以下 12 家机构（ID 与名称对应关系）：

| ID | 机构名称 |
|----|---------|
| 41126 | 广发证券 |
| 3099 | 国泰海通 |
| 41424 | 招商证券 |
| 2921 | 中信建投证券 |
| 41194 | 天风证券 |
| 12120 | 银河证券 |
| 22291 | 平安证券 |
| 2726 | 光大证券 |
| 121604 | 兴业证券 |
| 378 | 申银万国 |
| 41130 | 太平洋 |
| 42442 | 中金财富 |

### 步骤 2：调用 MCP 工具获取数据

使用解析后的参数调用研究报告工具，获取全部分析维度的研报观点数据。

**工具调用命令：**
```bash
mcporter call jy-financedata-tool.ResearchReport query="{查询参数}"
```

**查询参数说明：**
- 包含行业关键词、日期范围、券商机构 ID 列表
- 所有参数通过 query 传入

**若查询结果为空**，提示用户调整查询条件并终止流程：
- 建议放宽日期范围
- 建议调整行业关键词
- 建议检查 MCP 服务配置

### 步骤 3：合并整理数据

- 按 reportID 合并相同研报下的所有分析维度观点，归入同一条记录的 viewResults 数组
- 按 publishDate 降序排列（最新研报在前）
- 观点内容保持原文输出，不改写不摘要

### 步骤 4：结构化输出

严格按以下 JSON 格式输出：

```json
[
  {
    "reportID": "研报 ID",
    "title": "研报标题",
    "publishDate": "YYYY-MM-DD HH:mm:ss",
    "orgName": "券商机构名称",
    "viewResults": [
      {
        "perspectivesOnDimensions": "分析维度",
        "viewOutcomes": "分析观点"
      }
    ]
  }
]
```

**分析维度包括但不限于：**
- 行业发展趋势
- 竞争格局
- 技术创新
- 政策环境
- 投资建议
- 风险提示
- 接口返回的其他维度同样保留

**完整输出示例请查看：** `references/EXAMPLE_OUTPUT.md`

## 快速开始

**工具调用命令：**
```bash
# 基础调用格式
mcporter call jy-financedata-tool.ResearchReport query="{查询参数}"

# 示例：查询近一周 AI 行业研报
mcporter call jy-financedata-tool.ResearchReport query="行业=AI&beginDate=2026-03-23&endDate=2026-03-30&orgIds=41126,3099,41424,2921,41194,12120,22291,2726,121604,378,41130,42442"
```

**数据获取策略：**
1. 优先使用研究报告工具（jy-financedata-tool.ResearchReport）获取数据
2. 若 MCP 工具调用失败，提示用户检查 token 配置或网络状态
3. 查询结果为空时，建议用户放宽日期范围或调整行业关键词

**完整执行示例：**

```bash
# 1. 检查 mcporter 安装
mcporter --version

# 2. 检查 MCP 服务配置
mcporter list

# 3. 调用工具获取数据
mcporter call jy-financedata-tool.ResearchReport query="行业=新能源&beginDate=2026-03-23&endDate=2026-03-30&orgIds=41126,3099,41424,2921,41194,12120,22291,2726,121604,378,41130,42442"

# 4. 处理返回结果，按 reportID 合并，按 publishDate 降序排列

# 5. 输出结构化 JSON
```

## 资源清单

```
~/.openclaw/skills/jy-industry-research-summary/
├── SKILL.md                 # 技能主文件
├── references/              # 参考资料目录
│   ├── EXAMPLE_OUTPUT.md    # 完整输出示例和字段说明
│   └── CONFIG_GUIDE.md      # 详细配置指南和常见问题
```

- **EXAMPLE_OUTPUT.md**: 完整输出示例、字段说明、分析维度列表
- **CONFIG_GUIDE.md**: 快速配置流程、常见问题解答、配置文件位置

## 限制

- 仅支持查询已配置的 12 家主流券商机构的研报
- 观点内容保持原文输出，不进行改写或摘要
- 查询结果依赖于聚源数据 MCP 服务的可用性和数据覆盖范围
- 若 MCP 工具调用失败，需检查 JY_API_KEY 配置是否有效
- 所有服务工具的入参均为 query，其他入参格式不支持

## 注意事项

- 首次使用前必须完成 mcporter 安装和 MCP 服务配置
- JY_API_KEY 申请后配置一次即可，无需每次使用都重新配置
- 自然语言时间表达会自动转换为具体日期范围
- 行业关键词从用户提问中自动提取，建议用户使用明确的行业名称
- 若查询结果为空，可尝试放宽时间范围或使用更通用的行业关键词
