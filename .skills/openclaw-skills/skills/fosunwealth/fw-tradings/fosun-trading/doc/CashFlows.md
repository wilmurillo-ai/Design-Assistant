# 资金流水 - CashFlows

> **POST** `https://openapi.fosunxcz.com/api/v1/trade/CashFlows`

查询指定账户的资金流水记录。

---

## 请求

### Headers

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `X-api-key` | string | 是 | API Key，标识客户端 |
| `X-lang` | string | 是 | 语言，如 `zh-CN`、`en` |
| `X-request-id` | string | 是 | 请求追踪 ID，必填 |
| `X-session` | string | 是 | 会话 ID |
| `Content-Type` | string | 是 | 固定值 `application/json` |
| `Accept` | string | 是 | 固定值 `application/json` |

### Body（application/json）

资金流水请求。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `subAccountId` | string | 是 | 证券账户 |
| `applyAccountId` | string | 条件必填 | 子账户，查询期权流水时传期权子账户 ID |
| `subAccountClass` | integer | 否 | 账号类型，默认 `1` 主账号，`9` 期权账户；传 `9` 时走期权流水且 `applyAccountId` 必填 |
| `businessType` | array[integer] | 否 | 业务类型 |
| `date` | string | 否 | 日期，格式 `YYYY-MM-DD` |
| `flowType` | integer | 否 | 流水类型 |
| `tradeDateFrom` | string | 否 | 交易开始日期 |
| `tradeDateTo` | string | 否 | 交易结束日期 |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 普通资金流水 | 使用主账户查询时可仅传 `subAccountId`，`subAccountClass` 默认按 `1` 处理 |
| 期权资金流水 | 需传 `subAccountClass=9`，同时必须传 `applyAccountId`（期权子账户 ID） |

---

## 响应

### 200 - OK

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "count": 0,
    "list": [
      {
        "amount": "string",
        "businessType": 0,
        "createdAt": "string",
        "currency": "string",
        "direction": 0,
        "exchangeCode": "string",
        "flowId": 0,
        "flowType": 0,
        "productCode": "string",
        "remark": "string",
        "tradeDate": "string"
      }
    ],
    "start": 0,
    "total": 0
  }
}
```

#### 响应公共字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，示例值 `0` |
| `message` | string | 状态消息，示例值 `success` |
| `data` | object | 返回数据对象 |
| `data.count` | integer | 当前返回记录数 |
| `data.list` | array[object] | 资金流水列表 |
| `data.start` | integer | 起始偏移量 |
| `data.total` | integer | 总记录数 |

#### list 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `amount` | string | 金额 |
| `businessType` | integer | 业务类型 |
| `createdAt` | string | 创建时间 |
| `currency` | string | 币种 |
| `direction` | integer | 资金方向 |
| `exchangeCode` | string | 交易所代码 |
| `flowId` | integer | 流水 ID |
| `flowType` | integer | 流水类型 |
| `productCode` | string | 产品代码 |
| `remark` | string | 备注 |
| `tradeDate` | string | 交易日期 |

### 400 - 请求错误

请求参数不合法或缺少必填字段时返回。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/CashFlows \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "subAccountId": "SA001",
  "subAccountClass": 1,
  "tradeDateFrom": "2026-03-01",
  "tradeDateTo": "2026-03-12"
}'
```

### Python（使用 SDK）

```python
import json
import uuid

import requests

BASE_URL = "https://openapi.fosunxcz.com"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-api-key": "YOUR_API_KEY",
    "X-lang": "zh-CN",
    "X-request-id": str(uuid.uuid4()),
    "X-session": "YOUR_SESSION_ID",
}

payload = {
    "subAccountId": "SA001",
    "subAccountClass": 1,
    "tradeDateFrom": "2026-03-01",
    "tradeDateTo": "2026-03-12",
}

url = f"{BASE_URL}/api/v1/trade/CashFlows"
response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

---

## 常见场景

### 1. 查询指定日期范围的资金流水

```json
{
  "subAccountId": "SA001",
  "subAccountClass": 1,
  "tradeDateFrom": "2026-03-01",
  "tradeDateTo": "2026-03-12"
}
```

### 2. 查询指定日期的资金流水

```json
{
  "subAccountId": "SA001",
  "date": "2026-03-12"
}
```

### 3. 按业务类型筛选资金流水

```json
{
  "subAccountId": "SA001",
  "businessType": [1, 2],
  "tradeDateFrom": "2026-03-01",
  "tradeDateTo": "2026-03-12"
}
```

### 4. 按流水类型筛选

```json
{
  "subAccountId": "SA001",
  "flowType": 1,
  "tradeDateFrom": "2026-03-01",
  "tradeDateTo": "2026-03-12"
}
```

### 5. 查询期权账户资金流水

```json
{
  "subAccountId": "SA001",
  "applyAccountId": "OPTION_SUB_001",
  "subAccountClass": 9,
  "tradeDateFrom": "2026-03-01",
  "tradeDateTo": "2026-03-12"
}
```
