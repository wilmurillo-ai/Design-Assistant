---
name: human-ai-collab
description: 人机协作台技能。用户输入自然语言销售指令，AI自动分析拆解任务参数，调用 KocGo 平台接口提交任务，等待后查询 AiWa 挖掘客户数据，生成 xlsx 文件并返回。触发场景：用户说「帮我找客户」「挖掘XXX行业客户」「找XXX个客户」「提交任务」等与客户挖掘、销售任务相关的指令。需要提前配置环境变量 KOCGO_API_KEY。
---

# 人机协作台（Human-AI Collaboration）

## 功能简介

人机协作台是基于 KocGo 平台的智能销售任务助手，能够：

- **理解自然语言指令**：直接描述需求，如「帮我找50个美国做服装的客户」
- **智能任务拆解**：自动识别目标数量、行业、地区、执行周期等参数
- **多员工协作**：根据任务类型自动分配对应职能员工
  - **AiWa**：客户挖掘（找客户、行业客户等）
  - **Frank**：邮件销售
  - **Fran**：电话销售
  - **Lisa**：短信销售
- **自动提交任务**：调用 KocGo API 提交任务，后台异步执行
- **定时查询结果**：任务提交后 8 分钟自动查询并推送结果
- **生成 xlsx 报表**：客户数据自动生成带样式的 Excel 文件返回

---

## 前置条件：获取 API Key

1. 访问 [https://staging.kocgo.vip](https://staging.kocgo.vip) 注册并登录账号
2. 登录后进入「设置」或「API 管理」页面
3. 新建 API Key，复制以 `sk-` 开头的密钥
4. 在 OpenClaw 中配置环境变量：

```
KOCGO_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
```

> 所有 API 请求头需携带：`X-Api-Key: $KOCGO_API_KEY`
> API Base URL：`https://staging.kocgo.vip/stage-api`

---

## 完整执行流程

### Step 1：第一轮 AI 分析（任务拆解）

用以下 prompt 分析用户指令，严格返回 JSON，不含任何额外文字：

```
根据【指令】描述，Json格式返回数据
不需要多余的描述，不要过度解读，没有提及的内容请不要擅自理解，识别结果除了Json数据其他文字不要出现
规则如下：
{
  "totalTarget": "提取描述中提及的数量（无单位纯数字）",
  "employeeList": "首先将描述按逗号、顿号等分隔符拆分成多个子任务，然后为每个子任务匹配对应员工：挖掘客户职能（AiWa）：匹配任何包含'找'、'行业'、'客户'等与客户挖掘相关的描述，以及没有明确匹配其他职能的单子任务；邮件销售职能（Frank）：匹配包含'邮件'、'发邮件'等关键词；电话销售职能（Fran）：匹配包含'电话'、'打电话'、'电话销售'等关键词；短信销售职能（Lisa）：匹配包含'短信'、'发短信'等关键词。如果拆分后只有一个子任务且没有匹配上员工，则默认匹配挖掘客户职能（AiWa）。最后汇总所有匹配到的员工名称组成一个逗号拼接的字符串并返回（去重）",
  "language": "判断描述中是否明确提及国家或地区，若提及了国家或地区但和中国没有关联则返回'英文'，其他情况返回'中文'",
  "taskName": "根据描述总结出一个简洁的任务名称",
  "executionMode": "判断描述中是否明确提及每日/每天/周期性，如果提及则返回'周期性任务'，未提及则返回'定额任务'"
}
```

解析结果字段：
- `totalTarget`：目标数量（数字）
- `employeeList`：参与员工逗号字符串，如 `"AiWa"` 或 `"AiWa,Frank"`
- `language`：`"中文"` 或 `"英文"`
- `taskName`：任务名称
- `executionMode`：`"定额任务"` 或 `"周期性任务"`（接口参数：定额=1，周期=2）

---

### Step 2：第二轮 AI 分析（仅当 employeeList 包含 AiWa）

用以下 prompt 对同一用户指令做第二轮分析，严格返回 JSON：

```
根据【指令】描述，Json格式返回数据，其中数值部分用字符串输出
涉及数值规则仅处理描述中明确出现的数字和比较词，最小值规则：'X以上'=X，'X以下'=空，'X左右'=X；最大值规则：'X以上'=空，'X以下'=X，'X左右'=X
涉及七大洲和国家：如果提及了详细某些国家，七大洲则不用去识别；如果没提及国家则去识别有没有提及七大洲
涉及地址：如果是中国地址原文放入，如果是非中国的地址则以英文放入
不需要多余的描述，不要过度解读，没有提及的内容请不要擅自理解，识别结果除了Json数据其他文字不要出现
规则如下：
{
  "keywordList": "提取描述中的核心名词作为关键词，排除七大洲、国家、地址类关键词。如果是'找X'格式的描述，提取'X'作为关键词。同时添加相关的中文同义词和英文对应词，所有关键词用英文逗号分隔（如：服装,clothing）",
  "continent": "明确提及的七大洲，多个用英文逗号分隔（如：亚洲,欧洲）",
  "country": "明确提及的国家，多个用英文逗号分隔（如：中国,英国）",
  "countryCodeList": "对应国家的ISO代码，多个用英文逗号分隔（如：CN,GB）",
  "address": "明确提及的国家层级之下的详细地址（如：浙江省杭州市）；拆分为一级地址（省）、二级地址（市）、三级地址（区县镇），把一二三级有效地址通过逗号拼接返回（如：浙江宁波 返回 浙江,宁波）",
  "employeeNumberRangeStart": "只有当描述中明确提及员工数量并使用'员工X人以上/以下/左右'等范围描述时，按最小值规则提取；否则为空字符串",
  "employeeNumberRangeEnd": "只有当描述中明确提及员工数量并使用'员工X人以上/以下/左右'等范围描述时，按最大值规则提取；否则为空字符串",
  "storeNumberRangeStart": "只有当描述中明确提及门店数量并使用'门店X家以上/以下/左右'或'X家门店以上/以下/左右'等范围描述时，按最小值规则提取；否则为空字符串。单纯的'找X家门店'属于目标数量不在此提取",
  "storeNumberRangeEnd": "只有当描述中明确提及门店数量并使用'门店X家以上/以下/左右'或'X家门店以上/以下/左右'等范围描述时，按最大值规则提取；否则为空字符串。单纯的'找X家门店'属于目标数量不在此提取",
  "industryList": "根据以上字段推断行业分类，多个用英文逗号分隔（如：服装,数码,家居）"
}
```

---

### Step 3：构建并提交任务

**接口：** `POST https://staging.kocgo.vip/stage-api/ai/presetEmployee/submitTask`

**请求头：**
```
Content-Type: application/json
X-Api-Key: $KOCGO_API_KEY
```

**参数构建规则：**

- `taskName`：来自 Step 1
- `taskDescription`：用户原始输入
- `executionMode`：定额任务=1，周期性任务=2
- AiWa 参数中：
  - `totalTarget`：定额模式下填 Step 1 的 totalTarget，周期模式下为 null
  - `incrementalTarget`：必填，两种模式下均填 Step 1 的 totalTarget（不可为 null）
  - `upperLimitTarget`：填 Step 1 的 totalTarget
  - `keywordList`：Step 2 的 keywordList 拆分成数组
  - `continent`：Step 2 的 continent（无则 null）
  - `country`：Step 2 的 country（无则 null）
  - `countryCodeList`：Step 2 的 countryCodeList 拆分成数组（无则 null）
  - `addressObjList`：根据 Step 2 的 address 构建，无则 `[{"type":1,"province":"","city":"","county":"","address":""}]`
  - `industryList`：Step 2 的 industryList 拆分成数组

**请求体示例：**
```json
{
  "collaborationSubmitTaskParam": {
    "taskName": "挖掘美国客户",
    "taskDescription": "我是做口红的工厂，帮我挖掘美国的客户",
    "executionMode": 1,
    "employeeParams": {
      "AiWa": {
        "totalTarget": 10,
        "incrementalTarget": 10,
        "upperLimitTarget": 10,
        "keywordList": ["口红", "lipstick"],
        "continent": null,
        "country": "美国",
        "countryCodeList": ["US"],
        "addressObjList": [{"type": 1, "province": "", "city": "", "county": "", "address": ""}],
        "industryList": ["化妆品", "美妆"]
      }
    },
    "sourceSettings": null
  },
  "completed": true
}
```

**成功响应：**
```json
{"msg": "<taskId>", "code": 200}
```
提取 `msg` 字段作为 `taskId`。

提交成功后，告知用户：
> 任务已提交！任务名：{taskName}，目标数量：{totalTarget}，任务ID：{taskId}。AiWa 正在后台挖掘客户，将在 8 分钟后自动查询结果...

---

### Step 4：设置 8 分钟后自动查询

任务提交成功后，使用 `cron` 工具设置一次性定时任务，8 分钟后自动触发查询：

```json
{
  "action": "add",
  "job": {
    "name": "aiwa-query-{taskId前8位}",
    "schedule": { "kind": "at", "at": "{当前时间+8分钟的ISO8601字符串，如2026-03-19T15:00:00+08:00}" },
    "sessionTarget": "main",
    "wakeMode": "now",
    "payload": {
      "kind": "systemEvent",
      "text": "人机协作台提醒：请立即查询 AiWa 客户数据并返回给用户。taskId={taskId}，任务名：{taskName}，目标数量：{totalTarget}。调用 GET https://staging.kocgo.vip/stage-api/ai/customerPoolDetail/listByTaskId?taskId={taskId} 查询结果并格式化返回。"
    },
    "deleteAfterRun": true
  }
}
```

`schedule.at` = 当前时间 + 480 秒，ISO8601 格式，含时区（如 `+08:00`）。

cron 触发后，systemEvent 注入 main session，agent 收到后立即执行 Step 5。

---

### Step 5：生成 xlsx 并返回给用户

查询完成后**必须主动回复用户**，根据结果分两种情况：

**情况一：有数据（data 非空）**

1. 将完整 API 响应 JSON 传给脚本生成 xlsx 文件：

```bash
python3 ~/.openclaw/workspace/skills/human-ai-collab/scripts/format_customers.py '<完整响应JSON>' '/tmp/aiwa_{taskId前8位}.xlsx'
```

脚本成功后输出文件路径（如 `/tmp/aiwa_a32f78c4.xlsx`）。

2. 根据当前 channel 决定如何返回文件：

**飞书（feishu）：** 直接发送文件
```
message(action=send, channel="feishu", to="{user_open_id}", path='/tmp/aiwa_{taskId前8位}.xlsx', caption='✅ AiWa 挖掘完成！任务：{taskName}，共 {N} 位客户。')
```

**Telegram / WhatsApp：** 直接发送文件
```
message(action=send, channel="telegram", path='/tmp/aiwa_{taskId前8位}.xlsx', caption='✅ AiWa 挖掘完成！任务：{taskName}，共 {N} 位客户。')
```

**webchat 或其他不支持文件的 channel：** 告知用户文件路径
> ✅ xlsx 文件已生成：`/tmp/aiwa_{taskId前8位}.xlsx`，共 {N} 位客户。
> 请从服务器下载该文件，或配置飞书/Telegram 等 channel 以支持直接发送文件。

3. 同时以文字形式展示前5条预览：

```
序号. 👤 {personName}（{position}）
   🏢 公司：{companyName}
   🏭 行业：{industry}
   📧 邮箱：{email}
   📱 手机：{phone}
   💬 WhatsApp：{whatsapp}
   🔗 LinkedIn：{linkedin}
```

社媒字段若为 null 则整行不显示。超过5条附上：`...共 {N} 位，完整数据见 xlsx 文件`

**情况二：data 为空或 code 非 200**

> 8 分钟已到，已查询任务结果。暂未获取到客户数据，任务可能仍在执行中。
> 任务ID：{taskId}
> 你可以告诉我「再查一次」，我会立即重新查询。

---

## 实现方式

- **AI 分析**：直接在当前对话中用 LLM 完成，分析时告知用户正在处理
- **HTTP 请求**：使用 `exec` 工具调用 `curl`
- **定时等待**：使用 `cron(action=add)` 设置 8 分钟后触发的 systemEvent
- **xlsx 生成**：使用 `exec` 调用 Python 脚本

---

## 依赖

- Python 3（系统自带）
- openpyxl：`python3 -m pip install openpyxl --user --break-system-packages`
- 生成脚本：`~/.openclaw/workspace/skills/human-ai-collab/scripts/format_customers.py`

---

## 错误处理

- `KOCGO_API_KEY` 未设置：提示用户前往 https://staging.kocgo.vip 注册登录后新建 API Key，配置环境变量后再使用
- POST 接口返回非 200：展示错误信息，提示检查参数或稍后重试
- GET 接口 data 为空：提示任务可能仍在执行，给出 taskId 供用户告知「再查一次」
- Python 脚本执行失败：直接以文字列表格式返回客户数据，不中断流程
- 网络请求失败：展示 curl 错误信息
