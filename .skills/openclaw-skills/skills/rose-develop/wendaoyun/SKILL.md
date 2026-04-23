---
name: wendaoyun
description: 问道云企业信息查询工具，支持通过问道云 API 查询企业基本信息、经营信息、财务信息、舆情信息、企业各类风险指标等功能，当用户需要查询企业相关信息时触发。
version: 1.1.12
author: 技能开发者
config:
  - name: WENDAOYUN_API_KEY
    description: 问道云 API Key，可从 https://open.wintaocloud.com/home 获取
    required: true
    path:
      - ~/.config/wendao-yun/config.json
      - wendao-yun-config.json
    format: json
    example: '{"api_key": "your-api-key-here"}'
    env_var: WENDAOYUN_API_KEY
---

# 问道云 (WenDaoYun)

## Overview

问道云是问道云提供的企业信息查询 API 服务，本技能封装了问道云 API 的调用流程。

### 核心设计理念

- **两步查询**：始终先搜索企业 → 用户确认 → 再查询详细信息
- **模块化扩展**：新增接口只需在「Supported APIs」中添加定义，并在「详细信息类型」中注册
- **统一交互**：所有详细查询（处罚、失信人、经营异常等）遵循相同的确认流程

### 已支持的详细信息类型

| 类型 | 接口名 | 用户说法示例 | 状态 |
|------|--------|--------------|------|
| 企业基本信息 | `fuzzy-search-org` | "查询腾讯企业" | ✅ 已实现 |
| 行政处罚 | `get-punishments` | "查腾讯的行政处罚" | ✅ 已实现 |
| 失信被执行人 | `get-dishonest` | "查腾讯是不是老赖" | ⏳ 待接入 |
| 经营异常 | `get-abnormal` | "查腾讯经营异常" | ✅ 已实现 |
| 股权质押 | `get-equity-pledge` | "查腾讯股权质押" | ✅ 已实现 |
| 环保处罚 | `get-environmental-penalties` | "查腾讯环保处罚" | ✅ 已实现 |
| 欠税公告 | `get-tax-notice` | "查腾讯欠税公告" | ✅ 已实现 |
| 简易注销 | `get-simple-cancel` | "查腾讯简易注销" | ✅ 已实现 |
| 土地抵押 | `get-land-mortgage` | "查腾讯土地抵押" | ✅ 已实现 |
| 清算信息 | `get-clear-info` | "查腾讯清算信息" | ✅ 已实现 |
| 公示催告 | `get-public-inform` | "查腾讯公示催告" | ✅ 已实现 |
| 送达报告(劳动仲裁) | `get-labour-arb` | "查腾讯送达报告" | ✅ 已实现 |
| 担保信息 | `get-gua-info` | "查腾讯担保信息" | ✅ 已实现 |
| 开庭公告(劳动仲裁) | `get-open-court-arb` | "查腾讯开庭公告" | ✅ 已实现 |
| 税收违法 | `get-tax-violation` | "查腾讯税收违法" | ⏳ 待接入 |

> 💡 **提示用户时可以说**："我可以帮你查询企业的行政处罚、失信被执行人、经营异常、税收违法等信息"

---

## Configuration

使用前需要先配置 API Key：
1. 前往 https://open.wintaocloud.com/home 登录获取 API Key
2. 在技能配置文件中设置 `api_key`（配置文件路径：工作空间根目录的 `wendao-yun-config.json`）
3. 每个用户每日有 200 次调用额度，请妥善保管 API Key 避免泄露

详细配置说明见 [references/config.md](references/config.md)

---

## Universal Workflow（通用查询流程）

### 所有查询都遵循以下流程


```
┌─────────────────────────────────────────────────────┐
│  第 1 步：用户提出查询需求                              │
│  例如："帮我查询腾讯的行政处罚"                        │
│       或："查一下阿里的失信被执行人"                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  第 2 步：模糊搜索企业（调用 fuzzy-search-org）        │
│  - 使用用户提供的关键词作为 searchKey                 │
│  - 如果 total=0：提示用户调整关键词                    │
│  - 如果 total>0：列出前 5 条结果                       │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  第 3 步：等待用户确认具体企业                         │
│  **必须询问**："找到多家相关企业，请确认你想查询哪一家？"│
│  - 提供序号或全称让用户选择                           │
│  - 用户可以说"第 X 家"或直接说企业全称                   │
│  ⚠️ 此阶段不要调用任何详细信息接口！                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  第 4 步：用户确认后，查询详细信息                      │
│  - 根据用户请求的类型，调用对应接口                    │
│    - 行政处罚 → get-punishments                      │
│    - 失信被执行 → get-dishonest（待接入）             │
│    - 经营异常 → get-abnormal                        │
│    - ...                                             │
│  - 整理结果返回给用户                                 │
└─────────────────────────────────────────────────────┘
```


---

## Scenario Examples（场景示例）

### 场景一：只查询企业基本信息

**用户**："帮我查询腾讯企业"

**助手**：
1. 调用 `fuzzy-search-org`（searchKey="腾讯"）
2. 展示前 5 条结果
3. 询问："以上有你想要查询的企业吗？"
4. 用户确认后，可以结束或等待进一步指令

---

### 场景二：查询企业 + 详细信息（如行政处罚）

**用户**："帮我查询腾讯的行政处罚"

**助手**：
1. 调用 `fuzzy-search-org`（searchKey="腾讯"）
2. 展示前 5 条结果
3. **必须询问**："找到多家相关企业，请确认你想查询哪一家的行政处罚？"
4. 用户回复："第 3 家" 或 "腾讯科技（深圳）有限公司"
5. 调用 `get-punishments`（searchKey=用户确认的企业全称）
6. 返回处罚记录

---

### 场景三：查询新类型信息（如失信被执行人）

**用户**："查查腾讯是不是老赖" / "查询腾讯的失信被执行人"

**助手**：
1. 调用 `fuzzy-search-org`（searchKey="腾讯"）
2. 展示前 5 条结果
3. **必须询问**："找到多家相关企业，请确认你想查询哪一家的失信被执行人？"
4. 用户回复："第 3 家"
5. 调用 `get-dishonest`（searchKey=用户确认的企业全称）**← 新接口**
6. 返回失信记录

> 💡 **关键点**：无论查询什么类型的详细信息，**前 3 步完全相同**，只有第 4 步调用的接口不同。

---

## Supported APIs

### 基础接口（必选）

#### `fuzzy-search-org` - 企业模糊搜索

**用途**：所有查询的第一步，用于获取企业列表和用户确认

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 查询关键词（最少 2 个字符） |
| pageNum | integer | 否 | 分页页码，默认从 1 开始，每页固定返回 5 条数据 |

**响应字段**：
```json
{
  "orgId": 227606194,
  "orgName": "腾讯科技（深圳）有限公司",
  "usCreditCode": "9144030071526726XG",
  "incDate": "2000-02-24T00:00:00.000+08:00",
  "legalName": "马化腾",
  "status": "存续/在业",
  "address": "深圳市南山区高新区科技中一路腾讯大厦 35 层"
}
```

**使用说明**：
- ⚠️ 搜索结果可能非常多（如"腾讯"返回 7895 条），**始终只展示前 5 条**
- ✅ 展示时必须包含：序号、企业全称、法定代表人、成立日期、状态
- ✅ 必须询问用户："以上有你想要查询的企业吗？"
- 💡 引导用户：
  - 添加更具体的关键字（如"腾讯科技深圳"而不是"腾讯"）
  - 查询下一页（"帮我查第 2 页"）

---

### 详细信息接口（可选扩展）

#### `get-punishments` - 查询行政处罚 ✅ 已实现

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 企业全称（orgName，从模糊搜索结果获取） |
| pageNum | integer | 否 | 分页页码，默认 1 |
| pageSize | integer | 否 | 每页条数，默认 10，最大 20 |

**响应字段**：
```json
[{
  "punishNo": "行政处罚决定文书号",
  "illegalFact": "违法事实",
  "punishResult": "处罚结果",
  "unitName": "作出处罚单位名称",
  "punishTime": "处罚日期",
  "punishAmount": 10000
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| punishNo | String | 行政处罚决定文书号 |
| illegalFact | String | 违法事实 |
| punishResult | String | 处罚结果 |
| unitName | String | 作出处罚单位名称 |
| punishTime | String | 处罚日期 |
| punishAmount | Integer | 处罚金额（单位：分，换算需÷100才是元） |

---

#### `get-dishonest` - 查询失信被执行人 ⏳ 待接入

**用途**：查询企业是否为失信被执行人（俗称"老赖"）

**请求方式**：GET（待定）

**请求参数**（预期）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 企业全称（orgName） |
| pageNum | integer | 否 | 分页页码，默认 1 |
| pageSize | integer | 否 | 每页条数，默认 10 |

**响应字段**（预期）：
```json
{
  "caseNo": "（2023）京 01 执 123 号",
  "courtName": "北京市第一中级人民法院",
  "giverDate": "2023-05-15",
  "giverReason": "有履行能力而拒不履行生效法律文书确定义务",
  "holdStatus": "全部未履行",
  "performanceForm": "全部未履行",
  "regDate": "2023-06-01"
}
```

**接入步骤**：
1. 在问道云开放平台查看该接口的确切文档
2. 在 `scripts/api_client.py` 中添加 `get_dishonest()` 方法
3. 在此文档中更新接口定义（替换"预期"为实际参数）
4. 在上方的"已支持的详细信息类型"表格中将状态改为 ✅

---

#### `get-abnormal` - 查询经营异常 ✅ 已实现

**用途**：查询企业是否被列入经营异常名录

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |

**响应字段**：
```json
[{
  "department": "横琴粤澳深度合作区商事服务局",
  "removeDepartment": null,
  "removeDate": null,
  "removeReason": null,
  "abnormalDate": "2024-07-17",
  "abnormalReason": "未按照规定报送年报"
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| department | String | 列入部门 |
| removeDepartment | String | 移出部门 |
| removeDate | String | 移出日期 |
| removeReason | String | 移出原因 |
| abnormalDate | String | 列入日期 |
| abnormalReason | String | 列入原因 |

---

#### `get-equity-pledge` - 查询股权质押 ✅ 已实现

**用途**：查询企业股权质押信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |
| pageNum | Integer | 否 | 分页页码，默认1 |
| pageSize | Integer | 否 | 每页大小，默认10，最大20 |

**响应字段**：
```json
[{
  "pledgeeNameList": [{"name": "质权人名称", "type": 1}],
  "riskState": "股权质押状态",
  "pledgeeName": "质权人名称",
  "publicTime": "公告日期",
  "pledgeName": "出质人名称",
  "pledgeNameList": [{"type": 1, "name": "出质人名称"}]
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| pledgeeNameList | List\<Object> | 质权人列表 |
| pledgeeNameList[].name | String | 质权人名称 |
| pledgeeNameList[].type | Integer | 质权人类型：1=企业，2=人员 |
| riskState | String | 股权质押状态 |
| pledgeeName | String | 质权人名称 |
| publicTime | String | 公告日期 |
| pledgeName | String | 出质人名称 |
| pledgeNameList | List\<Object> | 出质人列表 |
| pledgeNameList[].type | Integer | 出质人类型：1=企业，2=人员 |
| pledgeNameList[].name | String | 出质人名称 |

---

#### `get-environmental-penalties` - 查询环保处罚 ✅ 已实现

**用途**：查询企业环保处罚信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |
| pageNum | Integer | 否 | 分页页码，默认1 |
| pageSize | Integer | 否 | 每页大小，默认10，最大20 |

**响应字段**：
```json
[{
  "punishBehavior": "违法事实",
  "punishAmount": 100000,
  "punishInstitution": "做出处罚单位名称",
  "publishDate": "发布日期",
  "punishDate": "处罚日期",
  "punishNumber": "环保处罚决定书文号"
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| punishBehavior | String | 违法事实 |
| punishAmount | Integer | 处罚金额（单位：分） |
| punishInstitution | String | 做出处罚单位名称 |
| publishDate | String | 发布日期 |
| punishDate | String | 处罚日期 |
| punishNumber | String | 环保处罚决定书文号 |

---

#### `get-tax-notice` - 查询欠税公告 ✅ 已实现

**用途**：查询企业欠税公告信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |
| pageNum | Integer | 否 | 分页页码，默认1 |
| pageSize | Integer | 否 | 每页大小，默认10，最大20 |

**响应字段**：
```json
[{
  "taxDepartment": "发布单位",
  "publishDate": "发布日期",
  "newOwnTaxBalance": 100000,
  "ownTaxBalance": 500000,
  "taxCategory": "欠税税种"
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| taxDepartment | String | 发布单位 |
| publishDate | String | 发布日期 |
| newOwnTaxBalance | Integer | 当前发生新欠税余额（单位：分） |
| ownTaxBalance | Integer | 欠税余额（单位：分） |
| taxCategory | String | 欠税税种 |

---

#### `get-simple-cancel` - 查询简易注销 ✅ 已实现

**用途**：查询企业简易注销信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |
| pageNum | Integer | 否 | 分页页码，默认1 |
| pageSize | Integer | 否 | 每页大小，默认10，最大20 |

**响应字段**：
```json
[{
  "result": "简易注销结果",
  "objectionList": [{"objectionDate": "时间", "content": "内容", "objectionName": "异议申请人名称"}],
  "promiseUrl": "全体投资人承诺书Url",
  "publicDate": "公告日期",
  "regInstitute": "登记机关",
  "usCreditCode": "统一社会信用代码",
  "orgName": "企业名称"
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| result | String | 简易注销结果 |
| objectionList | List\<Object> | 异议信息 |
| objectionList[].objectionDate | String | 异议时间 |
| objectionList[].content | String | 异议内容 |
| objectionList[].objectionName | String | 异议申请人名称 |
| promiseUrl | String | 全体投资人承诺书Url |
| publicDate | String | 公告日期 |
| regInstitute | String | 登记机关 |
| usCreditCode | String | 统一社会信用代码 |
| orgName | String | 企业名称 |

---

#### `get-land-mortgage` - 查询土地抵押 ✅ 已实现

**用途**：查询企业土地抵押信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |
| pageNum | Integer | 否 | 分页页码，默认1 |
| pageSize | Integer | 否 | 每页大小，默认10，最大20 |

**响应字段**：
```json
[{
  "mortgageAmount": 100000000,
  "mortgageEndTime": "2025-12-31",
  "mortgageBeginTime": "2024-01-01",
  "mortgageArea": "抵押面积",
  "address": "地址"
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| mortgageAmount | Integer | 抵押金额（单位：分） |
| mortgageEndTime | String | 抵押结束日期 |
| mortgageBeginTime | String | 抵押开始日期 |
| mortgageArea | String | 抵押面积 |
| address | String | 地址 |

---

#### `get-clear-info` - 查询清算信息 ✅ 已实现

**用途**：查询企业清算信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |

**响应字段**：
```json
{
  "liquidationMembers": "清算组成员",
  "liquidationLeader": "清算组负责人名称"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| liquidationMembers | String | 清算组成员 |
| liquidationLeader | String | 清算组负责人名称 |

---

#### `get-public-inform` - 查询公示催告 ✅ 已实现

**用途**：查询企业公示催告信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |
| pageNum | Integer | 否 | 分页页码，默认1 |
| pageSize | Integer | 否 | 每页大小，默认10，最大20 |

**响应字段**：
```json
[{
  "publishAuthority": "发布机关名称",
  "billType": "票据类型",
  "faceValue": 100000,
  "publishDate": "公告日期",
  "orgName": "企业名称",
  "billNumber": "票据号"
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| publishAuthority | String | 发布机关名称 |
| billType | String | 票据类型 |
| faceValue | Integer | 票面金额 |
| publishDate | String | 公告日期 |
| orgName | String | 企业名称 |
| billNumber | String | 票据号 |

---

#### `get-labour-arb` - 查询劳动仲裁 ✅ 已实现

**用途**：查询企业送达报告（劳动仲裁）信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |
| pageNum | Integer | 否 | 分页页码，默认1 |
| pageSize | Integer | 否 | 每页大小，默认10，最大20 |

**响应字段**：
```json
[{
  "publishDate": "公告日期",
  "respondentName": "被告名称",
  "applicantName": "原告名称",
  "caseNo": "案号"
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| publishDate | String | 公告日期 |
| respondentName | String | 被告名称 |
| applicantName | String | 原告名称 |
| caseNo | String | 案号 |

---

#### `get-gua-info` - 查询担保信息 ✅ 已实现

**用途**：查询企业担保信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |
| pageNum | Integer | 否 | 分页页码，默认1 |
| pageSize | Integer | 否 | 每页大小，默认10，最大20 |

**响应字段**：
```json
[{
  "assureDealTime": "处理日期",
  "transactionDate": "交易日期",
  "isRpt": "是否关联交易",
  "performState": "履行状态",
  "assureEndTime": "担保终止日",
  "assureBeginTime": "担保起始日",
  "assureTerm": "担保期限（年）",
  "currency": "币种",
  "assureAmount": 100000000,
  "reportDate": "报告期",
  "assuredEntityName": "被担保方名称",
  "assureEntityName": "担保方名称",
  "assureName": "担保方式"
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| assureDealTime | String | 处理日期 |
| transactionDate | String | 交易日期 |
| isRpt | String | 是否关联交易 |
| performState | String | 履行状态 |
| assureEndTime | String | 担保终止日 |
| assureBeginTime | String | 担保起始日 |
| assureTerm | String | 担保期限（年） |
| currency | String | 币种 |
| assureAmount | Integer | 担保金额（单位：分，换算需÷100才是元） |
| reportDate | String | 报告期 |
| assuredEntityName | String | 被担保方名称 |
| assureEntityName | String | 担保方名称 |
| assureName | String | 担保方式 |

---

#### `get-open-court-arb` - 查询开庭公告（劳动仲裁）✅ 已实现

**用途**：查询企业开庭公告（劳动仲裁）信息

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | String | 是 | 企业全称（orgName） |
| pageNum | Integer | 否 | 分页页码，默认1 |
| pageSize | Integer | 否 | 每页大小，默认10，最大20 |

**响应字段**：
```json
[{
  "courtOpenTime": "开庭日期",
  "undertakeDept": "承办部门名称",
  "caseReason": "案由",
  "defendantName": "被告名称",
  "plaintiffName": "原告名称",
  "caseNo": "案号",
  "dataOpenCourtId": 123456789
}]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| courtOpenTime | String | 开庭日期 |
| undertakeDept | String | 承办部门名称 |
| caseReason | String | 案由 |
| defendantName | String | 被告名称 |
| plaintiffName | String | 原告名称 |
| caseNo | String | 案号 |
| dataOpenCourtId | Long | 开庭公告ID |

---

#### `get-tax-violation` - 查询税收违法 ⏳ 待接入

**用途**：查询企业是否有税收违法记录

**请求方式**：GET（待定）

**请求参数**（预期）：同上

**响应字段**（预期）：
```json
{
  "taxNo": "9144030071526726XG",
  "violationType": "偷税",
  "decisionDocNo": "深国税稽罚〔2023〕123 号",
  "decisionDate": "2023-03-15",
  "taxAmount": "500000",
  "fineAmount": "250000"
}
```

---

## How to Add New Interface（如何添加新接口）

当你需要添加新的查询类型（如"股权出质"、"动产抵押"等）时：

### 第 1 步：查阅问道云 API 文档

访问问道云开放平台，找到新接口的文档，确认：
- 接口路径（如 `/get-equity-pledge`）
- 请求方式（GET/POST）
- 请求参数
- 响应格式

### 第 2 步：更新 Python 客户端

编辑 `scripts/api_client.py`，添加新方法：

```python
def get_equity_pledge(self, org_name: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    查询企业股权出质信息
    :param org_name: 企业全称
    :param page_num: 分页页码
    :param page_size: 每页大小
    :return: 股权出质列表
    """
    params = {
        "searchKey": org_name,
        "pageNum": page_num,
        "pageSize": page_size
    }
    return self.call_api("get-equity-pledge", params, method="GET")
```

### 第 3 步：更新本文档

1. **在"已支持的详细信息类型"表格中添加一行**：
   ```markdown
   | 股权质押 | `get-equity-pledge` | "查腾讯股权质押" | ✅ 已实现 |
   ```

2. **在"详细信息接口"章节添加新接口定义**（参考上面的模板）

3. **如果用户可能用多种说法**，在场景示例中添加：
   ```markdown
   ### 场景 X：查询股权出质
   **用户**："查查腾讯的股权出质" / "腾讯有没有股权质押"
   ```

### 第 4 步：测试

```bash
cd /home/gem/workspace/agent
python3 skills/wendaoyun/scripts/api_client.py --equity-pledge "腾讯科技（深圳）有限公司"
```

### 第 5 步：完成

将表格中的状态改为 ✅ 已实现

---

## API Base URL

固定前缀：`https://h5.wintaocloud.com/prod-api/api/invoke`

完整请求 URL = 基础前缀 + 接口路径，例如：
- `https://h5.wintaocloud.com/prod-api/api/invoke/fuzzy-search-org`
- `https://h5.wintaocloud.com/prod-api/api/invoke/get-punishments`
- `https://h5.wintaocloud.com/prod-api/api/invoke/get-dishonest` ← 新接口示例

---

## Authentication

所有请求都需要在 HTTP Header 中添加认证信息：
Authorization: Bearer {api_key}

---

## Request Methods

- **GET**：参数通过 URL 查询字符串拼接
- **POST**：参数通过 JSON 格式请求体发送

---

## Resources

### references
- `config.md` - 配置文件模板和说明
- `apis.md` - 完整 API 接口文档（同步更新）

### scripts
- `api_client.py` - Python API 客户端封装

---

## Quick Reference Card（快速参考卡）

### 用户说法 → 接口映射

| 用户可能说的话 | 对应接口 | 备注 |
|---------------|----------|------|
| "查询 XX 企业" | `fuzzy-search-org` | 只查基本信息 |
| "XX 的行政处罚" | `fuzzy-search-org` → `get-punishments` | 需确认企业 |
| "XX 是不是老赖" | `fuzzy-search-org` → `get-dishonest` | 需确认企业 |
| "XX 的失信记录" | `fuzzy-search-org` → `get-dishonest` | 需确认企业 |
| "XX 经营异常" | `fuzzy-search-org` → `get-abnormal` | 需确认企业 |
| "XX 税收违法" | `fuzzy-search-org` → `get-tax-violation` | 需确认企业 |

### 关键原则（再次强调）

- ✅ **所有详细查询都必须先搜索、再确认、后查询**
- ❌ **不要在未确认企业时直接调用详细信息接口**
- 💡 **新增接口只需复制模板，修改接口名和字段说明即可**

---

## 附录：完整对话示例

### 示例：查询失信被执行人（新接口）

```
用户：帮我查查腾讯是不是老赖

助手：（调用 fuzzy-search-org，searchKey="腾讯"）

助手：
🔍 搜索关键词："腾讯"
共找到 7,895 家相关企业，以下是第 1 页（前 5 条）：

| # | 企业名称 | 法定代表人 | 成立日期 | 状态 |
|---|----------|------------|----------|------|
| 1 | 深圳市腾讯斐泰科技有限公司 | 洪丹毅 | 2014-08-11 | 存续/在业 |
| 2 | 深圳市腾讯鑫信科技有限公司 | 林海峰 | 2021-05-25 | 存续/在业 |
| 3 | 深圳市腾讯网域计算机网络有限公司 | 何迪亮 | 1997-04-28 | 存续/在业 |
| 4 | 深圳市腾讯科融企业管理有限公司 | 马化腾 | 2021-05-25 | 存续/在业 |
| 5 | 深圳市腾讯信航有限合伙企业 | 深圳市腾讯博远科技有限公司 | 2017-06-30 | 注销 |

❓ 找到多家相关企业，请确认你想查询哪一家的失信被执行人记录？
- 请告诉我序号（如"第 3 家"）或企业全称

用户：第 3 家

助手：（调用 get-dishonest，searchKey="深圳市腾讯网域计算机网络有限公司"）

助手：
✅ 查询到 **深圳市腾讯网域计算机网络有限公司** 的失信被执行人记录：

共找到 0 条记录

🎉 该企业目前没有失信被执行人记录。
```

---

**文档版本**：v2.0  
**最后更新**：2026-04-08  
**维护者**：技能开发者
