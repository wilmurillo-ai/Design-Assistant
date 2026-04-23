# 撤单接口 - OrderCancel

> **POST** `https://openapi.fosunxcz.com/api/v1/trade/OrderCancel`

撤销未成交或部分成交的订单。

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

撤单请求。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `clientId` | integer | 否 | 客户 ID |
| `orderId` | string | 是 | 订单 ID，待撤销的订单标识 |
| `subAccountId` | string | 是 | 证券账户 ID |
| `applyAccountId` | string | 否 | 需要下单的子账号柜台账号 |
| `productType` | integer | 条件必填 | 产品类型，`15`=期权。期权订单撤单必传 |

#### 条件字段说明

| 场景 | 必填字段 |
|------|----------|
| 期权订单撤单 | `productType`（值为 `15`） |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "string",
    "orderStatus": 0
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，示例值 `0` |
| `message` | string | 状态消息，示例值 `success` |
| `data.orderId` | string | 订单 ID |
| `data.orderStatus` | integer | 撤单后的订单状态，见下方枚举 |

#### orderStatus 订单状态枚举

| 值 | 说明 |
|----|------|
| `10` | 未报 |
| `20` | 待报 |
| `21` | 条件单-待触发 |
| `22` | 待处理 |
| `23` | 待复核 |
| `40` | 已报 |
| `50` | 全成 |
| `60` | 部成 |
| `70` | 已撤 |
| `71` | 条件单-已撤销 |
| `80` | 部撤 |
| `90` | 废单 |
| `91` | 条件单-已取消 |
| `92` | 复核未通过 |
| `100` | 已失效 |
| `101` | 条件单-过期 |
| `901` | 条件单废单 |

### 400 - 请求错误

请求参数不合法、缺少必填字段，或订单当前状态不允许撤单时返回。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/OrderCancel \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "clientId": 12345,
  "orderId": "ORDER123456",
  "subAccountId": "SA001"
}'
```

### Python

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
    "clientId": 12345,
    "orderId": "ORDER123456",
    "subAccountId": "SA001",
}

response = requests.post(
    f"{BASE_URL}/api/v1/trade/OrderCancel",
    headers=headers,
    json=payload,
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

---

## 常见场景

### 1. 撤销普通股票订单

```json
{
  "clientId": 12345,
  "orderId": "ORDER123456",
  "subAccountId": "SA001"
}
```

### 2. 撤销期权订单

```json
{
  "clientId": 12345,
  "orderId": "OPTION_ORDER001",
  "subAccountId": "SA001",
  "productType": 15
}
```
