# 改单接口 - OrderModify

> **POST** `https://openapi.fosunxcz.com/api/v1/trade/OrderModify`

修改未成交或部分成交的订单，支持修改价格、数量、触发价等字段。支持正股、期权的改单操作。

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

改单请求。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `clientId` | integer | 否 | 客户 ID |
| `modifyType` | integer | 是 | 改单类型，枚举值：`1`=修改普通订单，`2`=修改条件单 |
| `orderId` | string | 是 | 待修改的订单 ID |
| `price` | string | 条件必填 | 委托订单价格，港股保留 3 位小数，其他保留 2 位小数。非追踪单时必填 |
| `productType` | integer | 条件必填 | 产品类型。A 股不允许改单，枚举值：`5`=港股，`6`=美股，`15`=期权。期权改单必传 |
| `profitPrice` | string | 否 | 止盈止损组合单的止盈触发价 |
| `profitQuantity` | string | 否 | 止盈止损组合单的止盈触发数量 |
| `quantity` | string | 否 | 修改后的委托数量 |
| `spread` | string | 否 | 追踪止损单价差 |
| `stopLossPrice` | string | 否 | 止盈止损组合单的止损触发价 |
| `stopLossQuantity` | string | 否 | 止盈止损组合单的止损触发数量 |
| `subAccountId` | string | 是 | 证券账户 ID |
| `applyAccountId` | string | 否 | 子账号下单时传入子账号信息，例如期权 |
| `tailAmount` | string | 条件必填 | 追踪止损单的追踪金额，`tailType=1` 时填写 |
| `tailPct` | string | 条件必填 | 追踪止损单的追踪比例，`tailType=2` 时填写，如 `0.05` 表示 `5%` |
| `tailType` | integer | 否 | 追踪止损单追踪类型，枚举值：`1`=金额，`2`=比例 |
| `trigPrice` | string | 条件必填 | 条件单触发价，修改条件单时必填 |

#### modifyType 改单类型枚举

| 值 | 说明 |
|----|------|
| `1` | 修改普通订单 |
| `2` | 修改条件单 |

#### productType 产品类型枚举

| 值 | 说明 |
|----|------|
| `5` | 港股 |
| `6` | 美股 |
| `15` | 期权 |

#### 条件字段说明

| 场景 | 必填字段 |
|------|----------|
| 修改普通订单 | `modifyType=1` |
| 修改条件单 | `modifyType=2`、`trigPrice` |
| 非追踪单 | `price` |
| 期权改单 | `productType=15` |
| 追踪止损单且按金额追踪 | `tailType=1`、`tailAmount` |
| 追踪止损单且按比例追踪 | `tailType=2`、`tailPct` |

#### 说明

- 仅支持修改未成交或部分成交的订单。
- 支持修改普通订单和条件单。
- A 股不支持改单。
- 止盈止损组合单可通过 `profitPrice`、`profitQuantity`、`stopLossPrice`、`stopLossQuantity` 调整止盈止损参数。

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
| `data.orderId` | string | 订单 ID。改单后仍为原单 ID，或返回柜台生成的新 ID |
| `data.orderStatus` | integer | 订单状态，见下方枚举 |

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

请求参数不合法、缺少必填字段，或订单状态不允许改单时返回。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/OrderModify \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "clientId": 12345,
  "modifyType": 1,
  "orderId": "ORDER123456",
  "price": "400.000",
  "quantity": "200",
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
    "modifyType": 1,
    "orderId": "ORDER123456",
    "price": "400.000",
    "quantity": "200",
    "subAccountId": "SA001",
}

response = requests.post(
    f"{BASE_URL}/api/v1/trade/OrderModify",
    headers=headers,
    json=payload,
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

---

## 常见场景

### 1. 修改普通限价单价格和数量

```json
{
  "clientId": 12345,
  "modifyType": 1,
  "orderId": "ORDER123456",
  "price": "400.000",
  "quantity": "200",
  "subAccountId": "SA001"
}
```

### 2. 修改条件单触发价

```json
{
  "clientId": 12345,
  "modifyType": 2,
  "orderId": "ORDER123457",
  "price": "398.000",
  "trigPrice": "395.000",
  "quantity": "100",
  "subAccountId": "SA001"
}
```

### 3. 修改追踪止损单（按金额）

```json
{
  "clientId": 12345,
  "modifyType": 1,
  "orderId": "ORDER123458",
  "quantity": "100",
  "tailType": 1,
  "tailAmount": "5.000",
  "spread": "1.000",
  "subAccountId": "SA001"
}
```

### 4. 修改追踪止损单（按比例）

```json
{
  "clientId": 12345,
  "modifyType": 1,
  "orderId": "ORDER123459",
  "quantity": "100",
  "tailType": 2,
  "tailPct": "0.05",
  "subAccountId": "SA001"
}
```

### 5. 修改止盈止损组合单

```json
{
  "clientId": 12345,
  "modifyType": 1,
  "orderId": "ORDER123460",
  "quantity": "100",
  "profitPrice": "420.000",
  "profitQuantity": "100",
  "stopLossPrice": "390.000",
  "stopLossQuantity": "100",
  "subAccountId": "SA001"
}
```

### 6. 修改期权订单

```json
{
  "clientId": 12345,
  "modifyType": 1,
  "orderId": "ORDER123461",
  "price": "5.50",
  "quantity": "2",
  "productType": 15,
  "subAccountId": "SA001",
  "applyAccountId": "OPTION001"
}
```
