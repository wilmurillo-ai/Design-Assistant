---
name: tuniu-holiday
description: 途牛度假助手 - 通过 exec + curl 调用 MCP 实现度假产品搜索、团期查询和预订下单。适用于用户询问度假产品、查看团期价格或提交度假产品订单时使用。兼容用户说“度假产品/旅游产品/跟团产品/自助产品/自驾产品/当地游产品/当地参团产品”等。
version: 1.0.0
metadata: {"openclaw": {"emoji": "🏖️","category": "travel","tags": ["途牛", "度假产品", "旅游产品", "跟团", "自助游", "自驾游", "预订"],"requires": {"bins": ["curl"]},"env": {"TUNIU_API_KEY": {"type": "string","description": "途牛开放平台 API key，用于 apiKey 请求头","required": true}}}}
---

# 途牛度假助手

当用户询问度假产品搜索、团期价格或提交度假产品订单时，使用此 skill 通过 exec 执行 curl 调用途牛度假产品 MCP 服务。

## 运行环境要求

本 skill 通过 **shell exec** 执行 **curl** 向 MCP endpoint 发起 HTTP POST 请求，使用 JSON-RPC 2.0 / `tools/call` 协议。**运行环境必须提供 curl 或等效的 HTTP 调用能力**（如 wget、fetch 等可发起 POST 的客户端），否则无法调用 MCP 服务。

## 隐私与个人信息（PII）说明

预订功能会将用户提供的**个人信息**（联系人姓名、手机号、乘客姓名、证件号等）通过 HTTP POST 发送至途牛度假产品 MCP 远端服务（`https://openapi.tuniu.cn/mcp/holiday`），以完成预订。使用本 skill 即表示用户知晓并同意上述 PII 被发送到外部服务。请勿在日志或回复中暴露用户个人信息。

## 适用场景

- 按目的地与日期范围搜索度假产品（第一页、翻页）
- 查看指定度假产品详情和团期价格日历
- 用户确认后创建度假产品预订订单

## 配置要求

### 必需配置

- **TUNIU_API_KEY**：途牛开放平台 API key，用于 `apiKey` 请求头

用户需在[途牛开放平台](https://open.tuniu.com/mcp)注册并获取上述密钥。

### 可选配置

- **HOLIDAY_MCP_URL**：MCP 服务地址，默认 `https://openapi.tuniu.cn/mcp/holiday`

## 调用方式

**直接调用工具**：使用以下请求头调用 `tools/call` 即可：

- `apiKey: $TUNIU_API_KEY`
- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`

## 可用工具

**重要**：下方示例中的参数均为占位，调用时需**根据用户当前需求**填入实际值（目的地、日期、产品选择、乘客信息等），勿直接照抄示例值。

### 1. 度假产品列表搜索 (searchHolidayList)

**必填参数**：`destinationName`（目的地城市名称），仅支持单个城市。

**可选参数**：

- `departsDateBegin` / `departsDateEnd`：出游日期范围（yyyy-MM-dd）。如果传入任意一个，另一个也必须传入。
- `departCityName`：出发城市名称
- `queryTypeName`：产品类型，只支持枚举：`自驾游` / `自助游` / `跟团`
- `tourDay`：行程天数
- `brandTypeName`：产品品牌（仅支持枚举：`牛人专线`、`牛专`、`牛人严选`、`严选`、`乐开花爸妈游`、`瓜果亲子游`）
- `conditions`：产品标签数组（如 `["亲子游","美食"]`）
- `lowPrice` / `highPrice`：价格区间（人民币元）
- `pageNum`：页码，从 1 开始

**翻页**：用户说「还有吗」「翻页」「下一页」时，保持相同筛选条件，只把 `pageNum` 改为 2/3/4... 再调用即可。

**触发词**：查度假产品、旅游产品、跟团产品、自助产品、自驾产品、当地游、当地参团、某地度假、某地旅游

**响应字段**（JSON.parse 后的结构）：

```typescript
{
  success: boolean;
  errorCode: number;
  msg: string;
  data: {
    count: number; // 符合条件的产品总数
    rows: Array<{
      productId: string; // ⭐ 调用 getHolidayProductDetail 必填
      productName: string;

      // 可展示字段（可按需要选取）
      price?: number; // 起价（人民币元）
      tourDay?: number; // 行程天数
      satisfaction?: number; // 满意度/评分
      peopleNum?: number; // 出游人数
      picUrl?: string; // 缩略图
      customConditionName?: string[]; // 标签数组
      brandTypeName?: string; // 品牌类型名称
      departCityName?: string[]; // 出发城市名称数组（可展示）

      // 内部字段（用于联动详情接口入参；不要向用户展示/解读）
      departsDateBegin?: string; // ⭐ 详情接口可选入参：仅当列表行返回存在时才传；需与列表结果完全一致
      departsDateEnd?: string; // ⭐ 详情接口可选入参：仅当列表行返回存在时才传；需与列表结果完全一致
      departCityCode?: number[]; // ⭐ 必须原样传递给详情接口（保持数组格式）
      classBrandId?: number; // ⭐ 用于详情接口 classBrandParentId
      proMode?: number; // ⭐ 用于详情接口 proMode

      // 其它可能由上游返回的扩展字段（可用于展示，不做强依赖）
      isNewproduct?: string; //是否新品（如"新品"）
    }>;
  };
}
```

**响应样例**：
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\":true,\"errorCode\":0,\"msg\":\"查询成功\",\"data\":{\"count\":1,\"rows\":[{\"productId\":\"321619424\",\"productName\":\"<产品名称>\",\"price\":33,\"tourDay\":2,\"satisfaction\":97,\"peopleNum\":2,\"picUrl\":\"https://...\",\"customConditionName\":[\"亲子游\"],\"brandTypeName\":\"牛专\",\"departCityName\":[\"南京\"],\"departsDateBegin\":\"2026-03-18\",\"departsDateEnd\":\"2026-03-26\",\"departCityCode\":[1602],\"classBrandId\":8,\"proMode\":1}]}}"
      }
    ]
  }
}
```

**curl 示例**：

```bash
# 第一页：destinationName/dates 按用户需求填
curl -s -X POST "${HOLIDAY_MCP_URL:-https://openapi.tuniu.cn/mcp/holiday}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchHolidayList","arguments":{"destinationName":"三亚","departsDateBegin":"2026-03-17","departsDateEnd":"2026-03-20"}}}'

# 自助游 + 指定出发城市 + 翻页可按 pageNum 改 2/3/4...
curl -s -X POST "${HOLIDAY_MCP_URL:-https://openapi.tuniu.cn/mcp/holiday}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"searchHolidayList","arguments":{"destinationName":"杭州","departsDateBegin":"2026-03-13","departsDateEnd":"2026-03-14","departCityName":"上海","queryTypeName":"自助游","pageNum":1}}}'
```

### 2. 产品详情查询 (getHolidayProductDetail)

**入参来源**：所有参数必须从 `searchHolidayList` 返回的 `data.rows[]` 中取，不能自行构造。

**必填参数**：

- `productId`
- `departCityCode`：⚠️ 必须保持数组格式（如 `[1602]` 或 `[1602,1603]`），不要提取单个元素
- `classBrandParentId`：来自 `classBrandId`
- `proMode`：来自 `proMode`

**可选参数**：

- `departsDateBegin` / `departsDateEnd`：仅当 `searchHolidayList` 返回的该产品行明确包含这两个字段时才传入；字段缺失则不传；如传入则必须成对出现，且需与列表结果完全一致

**触发词**：看一下这个度假产品、详情、团期价格日历、有哪些团期、价格如何

**响应重点**：

- `data.productPriceCalendar.count`：可选团期数量
- `data.productPriceCalendar.rows[]`：团期列表，每个包含 `departDate`、成人价 `tuniuPrice`、儿童价 `tuniuChildPrice`
- 若存在 `data.journeySummary`：按天展示“第N天 + 标题（journeySummary[].title）”，并遍历 `journeySummary[].moduleList`，根据 `moduleType` 映射展示内容（hotel=酒店, scenic=景点, food=餐饮, shopping=购物, activity=活动, reminder=提醒, flight=航班）。
  - `activity`：优先展示 `description`（HTML 转可读纯文本）
  - `hotel`：展示 `hotelList[].title` 等住宿信息
  - `food`：解析 `food.hasList`，根据 `has/hasChild`（为空按 0）生成含餐/自理对客文案
  - `scenic`：展示 `scenicList[].content`、`type`（如是否含门票）及图片链接（如有）
  - `reminder`：展示 `remind.type` 与 `remind.content`（HTML 转可读纯文本）
  - `shopping/flight`：按返回结构展示关键信息；字段为空明确“未提供详细信息”
  - 未知 `moduleType`：兜底保留原字段，不丢失行程信息
- 若 `count=0` 或 `rows` 为空，表示该产品暂无可售团期，应明确告知用户并停止下单（不可再调用 `saveHolidayOrder`）

**响应字段**（JSON.parse 后的结构，简化）：

```typescript
{
  success: boolean;
  errorCode: number;
  msg: string;
  traceId: string;
  data: {
    productId: string; // 下单必填
    departureCityName: string; // 下单必填（用于 saveHolidayOrder.departCityName）
    duration: number; // 下单必填
    productNight: number; // 下单必填（允许为 0 或空；半日游等可能为 0/空）

    productPriceCalendar: {
      count: number; // 可选团期总数
      rows: Array<{
        departDate: string; // 用户要从中选择的出发日期（下单必填）
        tuniuPrice: number; // 成人价
        tuniuChildPrice: number; // 儿童价；为 0 表示不支持儿童价
        bookCityCode: number; // 预订城市代码（通常不展示给用户）
        departCityCode: number; // 出发城市代码（通常不展示给用户）
        backCityCode: number; // 返回城市代码（通常不展示给用户）
      }>;
    };

    // 上游可能还会返回其它字段（如舱位、资源信息等），但本 skill 的下单关键字段如上。
    cabins?: Array<any>;
  };
}
```

**响应样例 JSON**（示例为简化内容）：

```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\":true,\"errorCode\":0,\"msg\":\"查询成功\",\"traceId\":\"<uuid>\",\"data\":{\"productId\":\"321619424\",\"departureCityName\":\"南京\",\"duration\":5,\"productNight\":4,\"productPriceCalendar\":{\"count\":2,\"rows\":[{\"departDate\":\"2026-05-01\",\"tuniuPrice\":2999,\"tuniuChildPrice\":1999,\"bookCityCode\":1602,\"departCityCode\":1602,\"backCityCode\":1602},{\"departDate\":\"2026-05-08\",\"tuniuPrice\":2899,\"tuniuChildPrice\":0,\"bookCityCode\":1602,\"departCityCode\":1602,\"backCityCode\":1602}]}}}"
      }
    ]
  }
}
```

**curl 示例**：

```bash
# productId/departCityCode/classBrandId/proMode 均从上一轮列表结果取；`departsDateBegin/departsDateEnd` 为可选：仅当列表行返回了这两个字段时才传入
curl -s -X POST "${HOLIDAY_MCP_URL:-https://openapi.tuniu.cn/mcp/holiday}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"getHolidayProductDetail","arguments":{"productId":"<产品ID>","departCityCode":[<城市代码数组>],"classBrandParentId":<品牌父级ID>,"proMode":<采购方式数字>}}}'
```

### 3. 获取预订信息 (getHolidayBookingRequiredInfo)

**功能**：返回下单填写所需信息与合规提示文本（非 JSON，放在 `result.content[0].text`）。

**触发词**：预订要填什么、下单需要什么信息、预订度假产品

```bash
curl -s -X POST "${HOLIDAY_MCP_URL:-https://openapi.tuniu.cn/mcp/holiday}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"getHolidayBookingRequiredInfo","arguments":{}}}'
```

### 4. 创建订单 (saveHolidayOrder)

**前置条件**：

- 必须先调用 `getHolidayProductDetail`
- 用户必须从 `data.productPriceCalendar.rows[]` 中明确选择一个具体的 `departDate`
- 建议将 `getHolidayProductDetail` 返回的 `traceId` 传入本工具

**必填参数**：

- `productId`：从详情 `data.productId`
- `departDate`：用户选择的团期日期（来自详情的 `productPriceCalendar.rows[].departDate`）
- `departCityName`：从详情 `data.departureCityName`
- `duration`：从详情 `data.duration`
- `night`：从详情 `data.productNight`（允许为 0 或空；半日游可能不含晚数）
- `tourists`：乘客信息列表（用户提供）
- `contactTourist`：联系人信息（可选；不填则默认使用第一个乘客姓名/电话）
- `traceId`：可选，建议用详情返回的 traceId

**tourists（乘客）字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 姓名（必填） |
| `idType` | string | 证件类型（必填）如：`身份证`、`因私护照`等 |
| `idNumber` | string | 证件号码（必填） |
| `mobile` | string | 手机号（必填） |
| `type` | string | 乘客类型：`成人` / `儿童` / `婴儿`（可选；不填则按生日自动判断） |
| `psptEndDate` | string | 证件有效期（可选；非身份证必填） |
| `sex` | number | 性别：1 男 0 女 9 未知（可选；非身份证必填/可选） |
| `birthday` | string | 生日 yyyy-MM-dd（可选；非身份证必填/可选） |

**contactTourist（联系人）字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 联系人姓名（可选） |
| `mobile` | string | 联系人手机号（可选） |
| `email` | string | 邮箱地址（可选） |

**触发词**：预订、下单、订度假产品、我要订、提交订单

**curl 示例**：

```bash
# productId/departCityName/duration/night/traceId 从详情接口结果取
# departDate 必须来自详情 productPriceCalendar.rows[] 中的 departDate
curl -s -X POST "${HOLIDAY_MCP_URL:-https://openapi.tuniu.cn/mcp/holiday}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"saveHolidayOrder","arguments":{"productId":"<产品ID>","departDate":"<用户选择的出发日期 YYYY-MM-DD>","departCityName":"<出发城市名称>","duration":<行程天数>,"night":<晚数或0或空>,"tourists":[{"name":"<乘客姓名>","idType":"身份证","idNumber":"<证件号码>","mobile":"<手机号>","type":"成人"}],"contactTourist":{"name":"<联系人姓名>","mobile":"<联系人手机号>","email":"<联系人邮箱>"},"traceId":"<从详情接口获取的traceId>"}}}'
```

**下单响应**：

```typescript
{
  success: boolean;
  errorCode: number;
  msg: string;
  data: { orderId: string; orderDetailUrl: string };
  traceId: string;
}
```

**响应样例 JSON**（示例为简化内容）：

```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\":true,\"errorCode\":0,\"msg\":\"下单成功\",\"data\":{\"orderId\":\"20260320123456789\",\"orderDetailUrl\":\"https://m.tuniu.com/u/gt/order/20260320123456789\"},\"traceId\":\"<uuid>\"}"
      }
    ]
  }
}
```

下单成功后请向用户展示订单号（orderId）和订单详情链接（orderDetailUrl），供用户自行选择使用，并告知可通过途牛 App 查看订单详情。

## 响应处理

### 本项目结果解析规则

- 本项目中工具结果统一放在 `result.content[0].text`。
- 对于 `searchHolidayList` / `getHolidayProductDetail` / `saveHolidayOrder`：`text` 为 JSON 字符串，需要先 `JSON.parse(result.content[0].text)` 再使用。
- 对于 `getHolidayBookingRequiredInfo`：`text` 为**纯文本**（含必填字段说明与合规提示），无需 JSON.parse；应直接展示给用户。

### 成功解析要点

- `searchHolidayList`：读取 `data.count` 和 `data.rows`
- `getHolidayProductDetail`：读取 `data.productPriceCalendar.count` 与 `data.productPriceCalendar.rows[]`
- `saveHolidayOrder`：读取 `data.orderId` 和 `data.orderDetailUrl`

### 错误响应

本项目中错误分两类，需分别处理：

1. **传输/会话层错误**（无 `result`，仅有顶层 `error`，通常伴随 HTTP 4xx/5xx）：

```json
{
  "jsonrpc": "2.0",
  "error": { "code": -32000, "message": "..." },
  "id": null
}
```

- Method Not Allowed：GET 等非 POST 请求
- Internal server error（code -32603）：服务内部异常

2. **工具层错误**（HTTP 仍为 200，有 `result`）：`result.content[0].text` 解析后为 JSON，且 `success=false`，通过 `errorCode` 与 `msg` 给用户提示/重试。

### 团期价格展示规则

- 当 `tuniuPrice > 0` 且 `tuniuChildPrice = 0`：仅展示成人价，不要展示或提及儿童价
- 当 `tuniuPrice = 0` 且 `tuniuChildPrice > 0`：将儿童价作为参考价，但仍需提醒用户以实际下单结果为准
- 当 `tuniuPrice = 0` 且 `tuniuChildPrice = 0`：该团期无有效价格，不向用户展示或推荐
- 其它正常情况：同时展示成人价和儿童价

## 输出格式建议

- **搜索列表**：以表格或清单展示 `productName`、起价 `price`、行程天数 `tourDay`、品牌 `brandTypeName`、标签 `customConditionName`、满意度 `satisfaction` 等；可提示「可以说翻页/下一页」
- **产品详情**：先展示行程概览（`journeySummary`，按“第N天+标题”逐日组织；文本含 HTML 时转为可读纯文本）。其中餐饮（`moduleType=food`）文案仅按当天 `food.hasList` 中的 `has`、`hasChild`、`title` 判断成人/儿童是否含餐；【强约束】餐饮文案的数据来源仅限于当天 food.hasList 中的 has、hasChild、title 字段；严禁从 characteristic、bookNotice、天标题（title）、reminder 或其他任何字段中提取金额、餐标等信息拼接到餐饮展示文案中。再展示团期价格日历（`departDate` + 对应成人/儿童价），并引导用户在以上日期中选择一个具体 `departDate` 用于下单（例如 `2026-05-01`）
- **预订成功**：明确写出 `orderId` 和 `orderDetailUrl`，告知可通过途牛 App 查看订单详情

## 使用示例

以下示例中，所有参数均从**用户表述或上一轮结果**中解析并填入，勿用固定值。

**用户**：查一下三亚未来 3 天的度假产品

**AI 执行**：按用户意图填参：`destinationName=三亚`、`departsDateBegin=2026-03-17`、`departsDateEnd=2026-03-20`，调用 `searchHolidayList`，展示 `data.rows` 产品列表并提示可选项翻页/查看详情。

**用户**：下一页 / 还有吗

**AI 执行**：保持相同筛选条件，仅把 `pageNum=2`（或 3、4…）调用 `searchHolidayList`。

**用户**：看第一个产品详情

**AI 执行**：从上一轮列表结果取 `productId/departCityCode/classBrandId/proMode`，调用 `getHolidayProductDetail`；若列表行包含 `departsDateBegin/departsDateEnd`，则需一并成对传入。

**用户**：有哪些团期？价格如何

**AI 执行**：读取 `data.productPriceCalendar.count` 与所有 `rows[].departDate/tuniuPrice/tuniuChildPrice`，按团期价格展示规则展示，并引导用户选择具体 `departDate`（例如 `2026-05-01`）用于下单。

**用户**：我选 2026-05-01 出发，帮我订。乘客：张三 身份证 110101199003075412，手机号 13800138000；联系人张三 13800138000

**AI 执行**：可先调用 `getHolidayBookingRequiredInfo` 展示必填字段与合规提示；然后调用 `saveHolidayOrder`：`productId` 来自详情、`departDate` 用用户选择值、`departCityName=departureCityName`、`duration` 用详情 `duration`、`night` 用详情 `productNight`，并按用户提供的 `tourists` 与 `contactTourist` 填参（建议带详情返回的 `traceId`）。

## 注意事项

1. 密钥安全：不要在回复或日志中暴露 `TUNIU_API_KEY` / 任何鉴权信息
2. PII 安全：联系人姓名、手机号、乘客姓名、证件号等仅在预订时发送至 MCP 服务，勿在日志或回复中暴露
3. 参数来源：`getHolidayProductDetail` 的所有入参必须完全来自 `searchHolidayList` 返回结果，不可自行构造
4. 日期一致性：若列表行返回了 `departsDateBegin` / `departsDateEnd`，则这两个字段必须与列表结果完全一致，且需成对传入
5. 数组传递：`departCityCode` 必须保持数组格式（如 `[1602]`），不得提取单个元素或转换类型
6. 团期选择：必须等用户明确选择一个 `departDate`（来自详情 `productPriceCalendar.rows[].departDate`）后才调用 `saveHolidayOrder`
7. 儿童价展示：遵循团期价格展示规则（`tuniuPrice/tuniuChildPrice` 均可能为 0）
8. `getHolidayBookingRequiredInfo`：返回的是**纯文本**，无需 JSON.parse
9. 证件/乘客字段（非身份证时）：需要补全 `sex`、`birthday`、`psptEndDate` 等信息；`idType` 建议使用工具支持的中文证件类型（如：`身份证`、`因私护照`、`军官证`、`港澳通行证`、`台胞证`、`驾驶证`、`回乡证`、`户口簿`、`出生证明`、`其他`、`台湾通行证`）
10. date 格式：所有日期均为 `YYYY-MM-DD`
11. 链路追踪：建议把 `getHolidayProductDetail` 返回的 `traceId` 传入 `saveHolidayOrder` 便于排查问题
12. **下单成功提示**：订单提交成功后，需向用户展示订单号（orderId）和订单详情链接（orderDetailUrl：`https://m.tuniu.com/u/gt/order/【订单ID】`），供用户自行选择使用，并告知可通过途牛 App 查看订单详情与后续确认进度及出行通知

