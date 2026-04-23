---
name: tuniu-cruise
description: 途牛邮轮助手 - 通过 exec + curl 调用 MCP 实现邮轮产品搜索、团期查询、预订下单。适用于用户询问邮轮、查询邮轮价格或提交邮轮订单时使用。兼容用户说"游轮"的情况。
version: 1.0.1
metadata: {"openclaw": {"emoji": "🚢", "category": "travel", "tags": ["途牛", "邮轮", "游轮", "预订"], "requires": {"bins": ["curl"]}, "env": {"TUNIU_API_KEY": {"type": "string", "description": "途牛开放平台 API key，用于 apiKey 请求头", "required": true}}}}
---

# 途牛邮轮助手

当用户询问邮轮搜索、团期查询或邮轮预订时，使用此 skill 通过 exec 执行 curl 调用途牛邮轮 MCP 服务。兼容用户说"游轮"的情况。

## 运行环境要求

本 skill 通过 **shell exec** 执行 **curl** 向 MCP endpoint 发起 HTTP POST 请求，使用 JSON-RPC 2.0 / `tools/call` 协议。**运行环境必须提供 curl 或等效的 HTTP 调用能力**（如 wget、fetch 等可发起 POST 的客户端），否则无法调用 MCP 服务。

## 隐私与个人信息（PII）说明

预订功能会将用户提供的**个人信息**（联系人姓名、手机号、乘客姓名、证件号等）通过 HTTP POST 发送至途牛邮轮 MCP 远端服务（`https://openapi.tuniu.cn/mcp/cruise`），以完成邮轮预订。使用本 skill 即表示用户知晓并同意上述 PII 被发送到外部服务。请勿在日志或回复中暴露用户个人信息。

## 适用场景

- 按日期范围搜索邮轮产品（支持按航线、品牌、天数筛选、分页）
- 查看指定邮轮产品的详情和团期价格日历
- 用户确认后创建邮轮预订订单
- 用户说"游轮"时等同于"邮轮"

## 配置要求

### 必需配置

- **TUNIU_API_KEY**：途牛开放平台 API key，用于 `apiKey` 请求头

用户需在[途牛开放平台](https://open.tuniu.com/mcp)注册并获取上述密钥。

### 可选配置

- **CRUISE_MCP_URL**：MCP 服务地址，默认 `https://openapi.tuniu.cn/mcp/cruise`

## 调用方式

**直接调用工具**：使用以下请求头调用 `tools/call` 即可：

- `apiKey: $TUNIU_API_KEY`
- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`

## 可用工具

**重要**：下方示例中的参数均为占位，调用时需**根据用户当前需求**填入实际值（日期、城市、航线、品牌、乘客信息等），勿直接照抄示例值。

### 1. 邮轮列表搜索 (searchCruiseList)

**必填参数**：`departsDateBegin`（起始日期）、`departsDateEnd`（结束日期），格式 YYYY-MM-DD。

**日期约束（与实现一致）**：`departsDateBegin` 不得早于**当天**；`departsDateEnd` 不得早于 `departsDateBegin`。

**可选参数**：`cruiseLineName`（航线名称）、`cruiseBrand`（品牌名称）、`tourDay`（行程天数）、`pageNum`（页码，从 1 开始；未传或小于 1 时按 1 处理）。

**筛选说明**：接口**不支持**将「出发城市」单独作为必填筛选条件；用户只说日期范围（例如「查三天内的邮轮/游轮」）时，仅用日期参数即可查询。**不要为了补齐可选参数而额外追问**航线、品牌、行程天数等，除非用户主动要筛。

**翻页**：传相同的筛选条件和 `pageNum`（2=第二页，3=第三页…）。用户说「还有吗」「翻页」「下一页」时用相同参数 + pageNum 再次调用即可。

**触发词**：查邮轮、邮轮产品、游轮搜索、某航线邮轮、某品牌邮轮、某天数邮轮

**展示约束**：`departsDateBegin`、`departsDateEnd` 仅用于传给 `getCruiseProductDetail`，属于内部透传字段，不要向用户展示或解读为「产品适用日期范围」或出发日期。

**列表展示**：当前页 `data.rows` 应**逐条**解析并在回复中体现，不得无说明地只展示部分示例；若条数较多，可说明「分批展示第 X/Y 页」后再分段输出。展示完成后引导用户用 `productId` 或能区分产品的名称关键词进入详情。

**响应字段**：
```typescript
{
  success: boolean;          // 是否成功
  errorCode: number;         // 错误码
  msg: string;               // 错误信息
  data: {
    count: number;           // 符合条件的产品总数
    rows: [{                 // 当前页产品列表
      productId: string;                // 产品 ID（⭐ 调用详情接口必需）
      productName: string;              // 产品名称
      departsDateBegin: string;         // 产品日期范围起始（⭐ 内部字段，调用详情接口必需）
      departsDateEnd: string;           // 产品日期范围结束（⭐ 内部字段，调用详情接口必需）
      departCityCode: number[];         // 出发城市代码数组（⭐ 必须原样传递给详情接口）
      departCityName: string[];         // 出发城市名称数组
      classBrandId: number;             // 品牌 ID（⭐ 调用详情接口时作为 classBrandParentId，整型）
      proMode: number;                  // 采购方式（⭐ 调用详情接口必需，整型）
      price: number;                    // 起价（人民币元）
      cruiseLineName: string;           // 邮轮航线名称
      cruiseBrand: string;              // 邮轮品牌名称
      ticketTypeName: string;           // 船票类型
      departurePortName: string;        // 出发港口名称
      tourDay: number;                  // 行程天数
      satisfaction: number;             // 满意度（百分比）
      peopleNum: number;               // 出游人数（若有）
      picUrl: string;                   // 产品缩略图
      isDirectSale: string;             // 是否船司直营
      customConditionName: string[];   // 产品标签，如「亲子游」等
    }]
  }
}
```

**响应样例**：
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\":true,\"errorCode\":0,\"msg\":\"查询成功\",\"data\":{\"count\":22,\"rows\":[{\"productId\":\"321648365\",\"productName\":\"[春节]<海洋光谱号上海-济州-上海4晚5天>上海登船2026，免签韩国\",\"departsDateBegin\":\"2026-02-10\",\"departsDateEnd\":\"2026-02-14\",\"departCityCode\":[1602],\"departCityName\":[\"上海\"],\"classBrandId\":12,\"proMode\":1,\"price\":3299,\"cruiseLineName\":\"日韩航线\",\"cruiseBrand\":\"皇家加勒比\",\"tourDay\":5,\"satisfaction\":97}]}}"
      }
    ]
  }
}
```

```bash
# 第一页：日期范围按用户需求填写（日期格式 YYYY-MM-DD）
curl -s -X POST "${CRUISE_MCP_URL:-https://openapi.tuniu.cn/mcp/cruise}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchCruiseList","arguments":{"departsDateBegin":"<用户指定的起始日期 YYYY-MM-DD>","departsDateEnd":"<用户指定的结束日期 YYYY-MM-DD>"}}}'

# 按航线和品牌筛选
curl -s -X POST "${CRUISE_MCP_URL:-https://openapi.tuniu.cn/mcp/cruise}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchCruiseList","arguments":{"departsDateBegin":"2026-03-17","departsDateEnd":"2026-03-30","cruiseLineName":"长江三峡","cruiseBrand":"世纪邮轮"}}}'

# 翻页：传相同的筛选条件 + pageNum
curl -s -X POST "${CRUISE_MCP_URL:-https://openapi.tuniu.cn/mcp/cruise}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"searchCruiseList","arguments":{"departsDateBegin":"<起始日期>","departsDateEnd":"<结束日期>","pageNum":2}}}'
```

### 2. 产品详情查询 (getCruiseProductDetail)

**入参来源**：所有参数必须从 `searchCruiseList` 返回的 `data.rows[]` 中获取，不可自行构造。

**必填参数**：
- `productId`：从 `data.rows[].productId` 中获取
- `departsDateBegin`：从 `data.rows[].departsDateBegin` 中获取
- `departsDateEnd`：从 `data.rows[].departsDateEnd` 中获取
- `departCityCode`：⚠️ 从 `data.rows[].departCityCode` 中获取，**必须原样传递数组格式**（如 `[1602]`），不得提取单个元素
- `classBrandParentId`：从 `data.rows[].classBrandId` 中获取（整型）
- `proMode`：从 `data.rows[].proMode` 中获取（整型）
- `departsDateBegin` + `departsDateEnd` 必须与同一条 `rows[]` 数据保持一致，禁止自行改写

**返回**：`productId`、`departureCityName`、`duration`、`productNight`（下单必需）、`productPriceCalendar`（可用团期价格日历，用户需要选择 `departDate`）。

**团期展示规则**：
- 必须展示可选团期总数（`count`）和各团期日期价格；
- 当 `rows` 为空或 `count=0` 时，明确告知无可售团期并停止后续下单链路；
- `tuniuPrice > 0 && tuniuChildPrice = 0` 时，仅展示成人价，不提儿童价；
- `tuniuPrice = 0 && tuniuChildPrice = 0` 的团期视为无效，不展示；
- `tuniuPrice = 0 && tuniuChildPrice > 0` 时，儿童价仅作参考，需提示以下单结果为准；
- 用户确认团期后再调用 `getCruiseCabinAndRoom`，并在下单时使用 `departureDate = data.base.beginDate`。
- 用户选择的 `departDate` 必须来自 `productPriceCalendar.rows`；不得接受列表外日期。

**链路建议**：
- `traceId` 建议从 `getCruiseProductDetail` 透传到 `getCruiseCabinAndRoom` 和 `saveCruiseOrder`，用于排障。

**缓存**：相同入参的详情查询结果可能被服务端缓存约 **5 分钟**，重复调用可能直接命中缓存（响应中的 `traceId` 仍会更新）。

**触发词**：看一下这个邮轮、这个产品的详情、有哪些团期、价格日历

**响应字段**：
```typescript
{
  success: boolean;
  errorCode: number;
  msg: string;
  data: {
    productId: string;              // 产品 ID（⭐ 下单必需）
    productName: string;            // 产品名称
    departureCityName: string;      // 出发城市名称（⭐ 下单必需）
    duration: number;               // 行程天数（⭐ 下单必需）
    productNight: number;           // 晚数（⭐ 下单时作为 night 参数）
    productPriceCalendar: {         // 团期价格日历
      count: number;                // 可选团期总数
      rows: [{                      // 团期列表
        departDate: string;         // 出发日期（⭐ 用户选择后用于调用getCruiseCabinAndRoom，查询对应团期下的舱位和房型）
        tuniuPrice: number;         // 成人价格（元）
        tuniuChildPrice: number;    // 儿童价格（元，为 0 时不支持儿童价）
        bookCityCode: number;       // 预订城市代码
        departCityCode: number;     // 出发城市代码
        backCityCode: number;       // 返回城市代码
      }]
    }
  };
  traceId: string;                  // 链路追踪 ID（建议传给下单接口）
}
```

**响应样例**：
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\":true,\"errorCode\":0,\"data\":{\"productId\":\"321648365\",\"productName\":\"[春节]<海洋光谱号上海-济州-上海4晚5天>\",\"departureCityName\":\"上海\",\"duration\":5,\"productNight\":4,\"productPriceCalendar\":{\"count\":8,\"rows\":[{\"departDate\":\"2026-05-01\",\"tuniuPrice\":3299,\"tuniuChildPrice\":2999},{\"departDate\":\"2026-05-08\",\"tuniuPrice\":3499,\"tuniuChildPrice\":3199},{\"departDate\":\"2026-05-15\",\"tuniuPrice\":3699,\"tuniuChildPrice\":0}]}},\"traceId\":\"f47ac10b-58cc-4372-a567-0e02b2c3d479\"}"
      }
    ]
  }
}
```

```bash
# productId、departsDateBegin、departsDateEnd、departCityCode、classBrandParentId、proMode 均从列表查询结果获取
# ⚠️ 重要：departCityCode 必须保持数组格式，如 [1602] 或 [1602, 1603]
curl -s -X POST "${CRUISE_MCP_URL:-https://openapi.tuniu.cn/mcp/cruise}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"getCruiseProductDetail","arguments":{"productId":"<产品ID>","departsDateBegin":"<产品日期范围起始>","departsDateEnd":"<产品日期范围结束>","departCityCode":[<城市代码数组>],"classBrandParentId":<品牌ID数字>,"proMode":<采购方式数字>}}}'
```

### 3. 查询舱位房型 (getCruiseCabinAndRoom)

**功能**：在用户选定团期后查询舱位与房型，并拿到下单必需的 `vendorId`、`journeyId`、`resourceId`/`subResourceId`。

**必填参数**：
- `productId`：从 `getCruiseProductDetail.data.productId` 中获取
- `departDate`：用户从 `productPriceCalendar.rows[].departDate` 中选择的日期

**可选参数**：
- `vendorId`：切换行程时传，来源 `data.vendorList[].vendorId`
- `traceId`：建议透传 `getCruiseProductDetail` 返回值

**人数说明**：工具**不要求**传入成人数/儿童数；**实际出行人**在 `saveCruiseOrder.tourists` 中填写。

**关键映射**：
- `saveCruiseOrder.vendorId` ← `getCruiseCabinAndRoom.data.base.vendorId`（或用户在 `vendorList` 中切换后选中的 `vendorId`）
- `saveCruiseOrder.departureDate` ← `getCruiseCabinAndRoom.data.base.beginDate`
- `saveCruiseOrder.selectRes[].journeyId` ← `data.cabinList[].journeyId`
- `saveCruiseOrder.selectRes[].resourceId` ← `priceRes` 中 `roomTypeResType=0` 的 `resId`；若不存在 `roomTypeResType` 且 `priceRes` 仅一条，可用该条的 `resId`
- `saveCruiseOrder.selectRes[].subResourceId`（可选）← `priceRes` 中 `roomTypeResType=1` 的 `resId`

**展示要求**：有数据时应完整列出 `vendorList`、`cabinList` 及每个舱等下的全部 `roomList`（不可无说明地抽样省略）；房型对用户优先说明人数/面积/楼层/阳台/起价等，仅在「下单映射」场景向用户解释 `resourceId`/`subResourceId` 含义。

**触发词**：看一下这个团期的舱位、这个日期能订哪些房型、查一下舱位和房间、这个邮轮怎么选房

```bash
curl -s -X POST "${CRUISE_MCP_URL:-https://openapi.tuniu.cn/mcp/cruise}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"getCruiseCabinAndRoom","arguments":{"productId":"<产品ID>","departDate":"<用户选择的团期日期 YYYY-MM-DD>","traceId":"<traceId>"}}}'
```

**响应字段**：
```typescript
{
  success: boolean;
  errorCode: number;
  msg: string;
  data: {
    base: {                           // 团期基础信息
      vendorId: number;               // 供应商 ID（⭐ 下单必需）
      vendorName: string;             // 供应商名称
      beginDate: string;              // 出发日期（⭐ 下单必需，传 saveCruiseOrder.departureDate）
      endDate: string;                // 返程日期
      cruiseName: string;             // 邮轮名称
      lineName: string;               // 线路名称
      arrivalPortName: string;        // 抵达港口
      departurePortName: string;      // 出发港口
      cruiseCompanyName: string;      // 邮轮公司
    };
    vendorList: [{                    // 可切换行程供应商列表
      vendorId: number;               // 供应商 ID（可作为下次请求 vendorId）
      vendorName: string;             // 供应商名称
      adultPrice: number;             // 该供应商起价
    }];
    cabinList: [{                     // 舱位列表
      cabinName: string;              // 舱位名称
      journeyId: number;              // 行程 ID（⭐ 下单必需，传 selectRes[].journeyId）
      startPrice: number;             // 起价
      unit: string;                   // 价格单位
      roomList: [{                    // 房型列表
        roomName: string;             // 房型名称
        startPrice: number;           // 房型起价
        minCapacity: number;          // 最小入住人数
        maxCapacity: number;          // 最大入住人数
        startNum?: number;            // 起售人数（若有）
        priceNotice?: string;         // 价格说明（若有）
        bookNotice?: string;          // 订房须知（若有）
        roomArea?: string;            // 面积
        floor?: string;               // 楼层
        hasBalcony?: number;          // 是否有阳台（1/0）
        balconyArea?: string | null;  // 阳台面积（若有）
        priceRes: [{                  // 价格资源（⭐ 下单核心映射）
          resId: number;              // 资源 ID（roomTypeResType=0 -> resourceId；=1 -> subResourceId）
          roomTypeResType: number;    // 资源类型：0 第1/2人，1 第3/4人（可选）
          adultPrice: number;         // 成人价
          childPrice: number;         // 儿童价
          vendorId: number;           // 供应商 ID
        }];
      }];
    }];
  };
}
```

**响应样例（精简）**：

```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\":true,\"errorCode\":0,\"msg\":\"\",\"data\":{\"base\":{\"vendorId\":73197,\"vendorName\":\"梦幻之旅\",\"beginDate\":\"2026-04-28\",\"endDate\":\"2026-04-30\",\"cruiseName\":\"盛世号\",\"lineName\":\"长江三峡&西沙\",\"arrivalPortName\":\"宜昌港\",\"departurePortName\":\"重庆港\",\"cruiseCompanyName\":\"上海葛洲坝国际旅游有限公司\"},\"vendorList\":[{\"vendorId\":73197,\"vendorName\":\"梦幻之旅\",\"adultPrice\":1399}],\"cabinList\":[{\"cabinName\":\"标准间\",\"journeyId\":91808486,\"unit\":\"起/人\",\"startPrice\":1399,\"roomList\":[{\"roomName\":\"标准间-内宾-成人（2楼）\",\"startPrice\":1399,\"minCapacity\":1,\"maxCapacity\":1,\"priceRes\":[{\"resId\":2121750804,\"roomTypeResType\":0,\"adultPrice\":1399,\"childPrice\":0,\"vendorId\":73197}]}]}]}}"
      }
    ]
  }
}
```

### 4. 获取预订信息 (getCruiseBookingRequiredInfo)

**功能**：返回**固定长文本**说明（房型与 `selectRes` 规则、`tourists` 与 `selectRes` 分传、乘客/联系人字段、填写示例、合规与隐私链接等）。应在用户已选定团期与房型后、收集乘客信息前调用。

**响应形态**：`result.content[0].text` 为**纯文本**（非 JSON），**不要**按 `JSON.parse` 解析为 `{ success, data }`。直接向用户展示该文案并引导逐人填写 `tourists`（至少 1 人）。

**触发词**：预订邮轮要填什么、下单需要什么信息、预订游轮需要什么

```bash
curl -s -X POST "${CRUISE_MCP_URL:-https://openapi.tuniu.cn/mcp/cruise}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"getCruiseBookingRequiredInfo","arguments":{}}}'
```

### 5. 创建订单 (saveCruiseOrder)

**前置条件**：
- 必须先调用 `getCruiseProductDetail` 获取产品详情和可用团期
- 必须先调用 `getCruiseCabinAndRoom` 并完成房型选择
- 必须先调用 `getCruiseBookingRequiredInfo` 展示说明文案，再收集乘客信息

**校验要点（与实现一致）**：`duration` 须 **> 0**；`night` 须 **≥ 0**（允许为 0）；`selectRes` 至少一条且每条 `journeyId`、`resourceId` 须为**正整数**（`subResourceId` 可选）；`tourists` 至少一位。下游落单依赖请求上下文中的用户 ID：**若无法从请求解析用户身份**，可能返回「当前无法获取登录信息，请重新登录或稍后重试」。

**必填参数**：
- `productId`：从 `getCruiseProductDetail.data.productId` 中获取
- `departureDate`：从 `getCruiseCabinAndRoom.data.base.beginDate` 中获取（通常与用户所选团期 `departDate` 同一天）
- `departureCityName`：从 `getCruiseProductDetail.data.departureCityName` 中获取
- `duration`：从 `getCruiseProductDetail.data.duration` 中获取
- `night`：从 `getCruiseProductDetail.data.productNight` 中获取（允许为 0）
- `vendorId`：从 `getCruiseCabinAndRoom.data.base.vendorId` 中获取（或 `vendorList` 所选）
- `selectRes`：每选一种房型一条；从 `journeyId` + `priceRes` 组装，**勿**把乘客写入 `selectRes`
- `tourists`：乘客信息列表（用户提供，至少一位即可提交）
- `traceId`：可选；建议传入 `getCruiseProductDetail` 的 traceId，不传则服务端可能自动生成

**tourists 格式**：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 姓名（必填） |
| idType | string | 证件类型中文（必填）。常用：身份证、因私护照/护照、军官证、港澳通行证、台胞证、回乡证、户口簿、出生证明、台湾通行证、驾驶证、其他；未在映射表中的类型可能按默认规则处理 |
| idNumber | string | 证件号码（必填） |
| mobile | string | 手机号（必填） |
| type / passengerType | string | 乘客类型：成人 / 儿童 / 婴儿，二者同义；不填则按生日与出发日自动判断（可选） |
| psptEndDate | string | 证件有效期，格式 yyyy-MM-dd；非中国居民身份证场景下必填（可选） |
| sex | number | 性别，1 男 0 女 9 未知；非身份证必填（可选） |
| birthday | string | 生日，格式 yyyy-MM-dd；非身份证必填（可选） |

**身份证乘客**：系统可从证件号解析性别、生日，通常无需再传 `sex`、`birthday`、`psptEndDate`。

**contactTourist 格式**：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 联系人姓名（可选，不填则使用第一个乘客姓名） |
| mobile | string | 联系人手机号（可选，不填则使用第一个乘客电话） |
| email | string | 联系人邮箱（可选） |

**selectRes 格式**：

| 字段 | 类型 | 说明 |
|------|------|------|
| journeyId | number/string | 行程编号（来自 `cabinList[].journeyId`），解析为整数 |
| resourceId | number/string | 必填（来自 `priceRes` 中 `roomTypeResType=0` 的 `resId`，或仅一条 `priceRes` 时取该条 `resId`） |
| subResourceId | number/string | 可选（来自 `priceRes` 中 `roomTypeResType=1` 的 `resId`） |

**触发词**：预订、下单、订邮轮、我要订、提交订单、预订游轮

**响应字段**：
```typescript
{
  success: boolean;
  errorCode: number;
  msg: string;
  data: {
    orderId: string;    // 订单号
  };
  traceId: string;      // 链路追踪 ID
}
```

**响应样例**：
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\":true,\"errorCode\":0,\"msg\":\"下单成功\",\"data\":{\"orderId\":\"1260278419\"},\"traceId\":\"f47ac10b-58cc-4372-a567-0e02b2c3d479\"}"
      }
    ]
  }
}
```

```bash
# productId、departureCityName、duration、night 从 getCruiseProductDetail 结果取
# departureDate、vendorId、selectRes 从 getCruiseCabinAndRoom 结果取
# tourists、contactTourist 按用户需求填
# traceId 建议从 getCruiseProductDetail 结果中获取
curl -s -X POST "${CRUISE_MCP_URL:-https://openapi.tuniu.cn/mcp/cruise}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "saveCruiseOrder",
      "arguments": {
        "productId": "<产品ID>",
        "departureDate": "<从 base.beginDate 获取的日期 YYYY-MM-DD>",
        "departureCityName": "<出发城市名称>",
        "duration": <行程天数>,
        "night": <晚数>,
        "vendorId": <供应商ID>,
        "selectRes": [
          {
            "journeyId": <行程编号>,
            "resourceId": <1/2人资源ID>,
            "subResourceId": <3/4人资源ID，可选>
          }
        ],
        "tourists": [
          {
            "name": "<乘客姓名>",
            "idType": "身份证",
            "idNumber": "<证件号码>",
            "mobile": "<手机号>"
          }
        ],
        "contactTourist": {
          "name": "<联系人姓名>",
          "mobile": "<联系人手机号>",
          "email": "<联系人邮箱>"
        },
        "traceId": "<从详情接口获取的 traceId>"
      }
    }
  }'
```

## 响应处理

### 成功响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{"type": "text", "text": "..."}]
  },
  "id": 2
}
```

- **本项目中** 多数工具结果放在 **`result.content[0].text`**。除 **getCruiseBookingRequiredInfo** 外，`text` 一般为 **JSON 字符串**，需 `JSON.parse(result.content[0].text)` 后再用。
- **getCruiseBookingRequiredInfo**：`text` 为**纯文本说明**，直接展示给用户，勿当 JSON 解析。
- 解析后为业务对象，各工具结构不同：
  - **邮轮列表**（searchCruiseList）：`success`、`data.count`（总数）、`data.rows`（产品列表，含 productId、productName、price、cruiseBrand、tourDay 等）。
  - **产品详情**（getCruiseProductDetail）：`success`、`data`（含 productId、departureCityName、duration、productNight、productPriceCalendar 等）、`traceId`。
  - **舱位房型**（getCruiseCabinAndRoom）：`success`、`data.vendorList/base/cabinList`、`traceId`。
  - **创建订单**（saveCruiseOrder）：`success`、`data.orderId`（字符串）、`traceId`。
- 错误时 `text` 解析后为 `{ "success": false, "errorCode": ..., "msg": "错误信息" }`（可能含 `traceId`），可从 `msg` 字段取提示文案。

### 错误响应

本项目中错误分两类，需分别处理：

**1. 传输/会话层错误**（无 `result`，仅有顶层 `error`，通常伴随 HTTP 4xx/5xx）：

```json
{
  "jsonrpc": "2.0",
  "error": {"code": -32000, "message": "..."},
  "id": null
}
```
- **Method Not Allowed**：GET 等非 POST 请求
- **Internal server error**（code -32603）：服务内部异常

**2. 工具层错误**（HTTP 仍为 200，有 `result`）：与成功响应结构相同，但 `result.content[0].text` 解析后为 `{ "success": false, "errorCode": ..., "msg": "错误信息" }`。例如参数校验失败、产品不存在、下单失败等，从 `msg` 字段取文案提示用户或重试。

## 输出格式建议

- **搜索列表**：以表格或清单展示产品名称、价格、航线、品牌、天数、满意度；可提示「可以说翻页/下一页」
- **产品详情**：展示产品基本信息，重点展示团期价格日历（遍历所有团期，显示出发日期、成人价、儿童价），明确提示用户需要选择一个出发日期
- **团期价格展示规则**：
  - 当 `tuniuChildPrice > 0` 时，显示"成人价 ¥X，儿童价 ¥Y"
  - 当 `tuniuChildPrice = 0` 时，仅显示成人价，不要提及儿童价
  - 过滤掉 `tuniuPrice = 0` 的无效团期
- **预订成功**：明确写出订单号、产品名称、出发日期、乘客信息，提示用户联系客服或前往途牛官网完成支付

## 使用示例

以下示例中，所有参数均从**用户表述或上一轮结果**中解析并填入，勿用固定值。

**用户**：查一下 3 月 17 号到 3 月 30 号的邮轮

**AI 执行**：按用户意图填参：departsDateBegin=2026-03-17、departsDateEnd=2026-03-30，调用 searchCruiseList（请求头需带 apiKey、Content-Type、Accept）。解析 result.content[0].text，整理产品列表回复，展示产品名称、价格、航线、品牌等。

**用户**：还有吗？/ 下一页

**AI 执行**：用相同的日期范围 + pageNum=2（或 3、4…）再次调用 searchCruiseList。

**用户**：看一下第一个产品的详情

**AI 执行**：从上一轮列表结果取第一个产品的 productId、departsDateBegin、departsDateEnd、departCityCode（⚠️ 必须原样传递数组）、classBrandId（作为 classBrandParentId）、proMode，调用 getCruiseProductDetail；解析团期价格日历后，逐条展示所有团期的出发日期和价格，并提示用户需要选择一个出发日期。

**用户**：我选 5 月 1 号出发，帮我订，联系人张三 13800138000，乘客李四 身份证 310101199001011234

**AI 执行**：
1. 验证用户选择的 "2026-05-01" 在团期列表中
2. 用户已在详情中确认团期后，调用 `getCruiseCabinAndRoom(productId, departDate)` 获取舱位房型，并让用户明确房型
3. 从舱位结果中组装 `selectRes`：`journeyId` + `resourceId`（可选 `subResourceId`）
4. 调用 `getCruiseBookingRequiredInfo`，再收集游客信息
5. 从最近一次详情结果取 `productId`、`departureCityName`、`duration`、`productNight`、`traceId`，从舱位结果取 `departureDate=base.beginDate`、`vendorId=base.vendorId`
6. 调用 `saveCruiseOrder`，成功后回复订单号，并提醒用户联系客服或前往途牛官网完成支付

**用户**：查一下长江三峡的游轮（注意用户说的是"游轮"）

**AI 执行**：识别"游轮"等同于"邮轮"，调用 searchCruiseList，传入 cruiseLineName="长江三峡"，按正常流程处理。

## 注意事项

1. **密钥安全**：不要在回复或日志中暴露 TUNIU_API_KEY
2. **PII 安全**：联系人姓名、手机号、乘客姓名、证件号等仅在预订时发送至 MCP 服务，勿在日志或回复中暴露
3. **认证**：若遇协议或认证错误，可重试或检查 TUNIU_API_KEY
4. **日期格式**：所有日期均为 YYYY-MM-DD
5. **参数来源**：getCruiseProductDetail 的所有参数必须从 searchCruiseList 返回结果中获取，不可自行构造
6. **数组传递**：departCityCode 必须原样传递数组格式（如 `[1602]`），不得提取单个元素或转换类型
7. **团期与房型链路**：
   - 必须先展示所有可选团期（productPriceCalendar.rows）
   - 明确提示用户需要选择一个具体的出发日期
   - 用户选定团期后必须先调用 `getCruiseCabinAndRoom`
   - 下单时 `departureDate` 必须取 `data.base.beginDate`
8. **selectRes 组装**：
   - `journeyId` 来自 `cabinList[].journeyId`
   - `resourceId` 来自 `priceRes` 中 `roomTypeResType=0` 的 `resId`
   - `subResourceId`（可选）来自 `roomTypeResType=1` 的 `resId`
9. **儿童价展示**：当 tuniuChildPrice 为 0 时，不要向用户展示或提及儿童价
10. **翻页**：用户要「更多」「下一页」时用相同的筛选条件 + pageNum（≥2）调用即可
11. **链路追踪**：建议将 getCruiseProductDetail 返回的 traceId 透传到 getCruiseCabinAndRoom 和 saveCruiseOrder，便于问题排查
12. **游轮兼容**：系统已兼容"游轮"说法，用户说"游轮"时按"邮轮"处理即可，无需特殊转换
13. **支付提醒**：订单提交成功后，需提醒用户联系途牛客服，或打开途牛 APP / 小程序，及时查看订单详情、后续确认进度及出行通知
14. **列表日期**：`searchCruiseList` 的起止日期不得早于今天，且结束日不得早于起始日；违反时接口返回失败文案，应提示用户修正范围
