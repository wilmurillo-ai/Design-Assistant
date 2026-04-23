# 下单 - OrderCreate

> **POST** `https://openapi.fosunxcz.com/api/v1/trade/OrderCreate`

提交委托订单。支持正股、期权（`productType=15`）；期权需传 `expiry`、`strike`、`right`。

Stoplight 页面对应 Schema：请求体 `mapping.OrderCreateRequest`，响应体 `mapping.OrderCreateResponse`。

---

## 请求

### Headers

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `X-api-key` | string | 是 | API Key，标识客户端 |
| `X-lang` | string | 是 | 语言，如 `zh-CN`、`en` |
| `X-request-id` | string | 是 | 请求追踪 ID，必填 |
| `X-session` | string | 是 | 会话 ID |

### Body（`application/json`）

下单请求。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `timeInForce` | integer | 否 | 时段控制，枚举值：`0`=当日有效，`2`=允许美股盘前盘后，`4`=允许夜盘 |
| `clientId` | integer | 否 | 客户 ID |
| `currency` | string | 是 | 币种，枚举值：`HKD`=港币，`USD`=美元，`CNH`=人民币 |
| `direction` | integer | 是 | 买卖方向，枚举值：`1`=买，`2`=卖 |
| `expiry` | string | 条件必填 | 期权到期日，格式 `YYYYMMDD`（如 `20060102`），期权单必填 |
| `expType` | integer | 否 | 订单时效类型，常用值：`1`=当日有效 |
| `marketCode` | string | 是 | 市场代码，枚举值：`hk`=港股，`us`=美股，`sh`=上交所，`sz`=深交所 |
| `orderType` | integer | 是 | 订单类型，见下方枚举 |
| `price` | string | 条件必填 | 委托订单价格，港股保留 3 位小数，其他两位小数。非追踪单且非市价单时必填 |
| `productType` | integer | 条件必填 | 产品类型，枚举值：`5`=港股，`6`=美股，`7`=A股，`15`=期权。期权下单必传 |
| `quantity` | string | 是 | 委托订单数量，正整数 |
| `right` | string | 条件必填 | 期权方向，枚举值：`CALL`=看涨，`PUT`=看跌。期权单必传 |
| `shortSellType` | string | 否 | 沽空类型，枚举值：`A`=指数套利，`B`=强制平仓，`C`=补仓，`F`=被迫抛售，`M`=做市商/证券专家，`N`=没有沽空，`S`=做市商/衍生品专家，`Y`=沽空 |
| `spread` | string | 否 | 追踪止损单价差 |
| `profitPrice` | string | 条件必填 | 止盈触发价格，止盈止损组合单使用 |
| `profitQuantity` | string | 条件必填 | 止盈触发数量，止盈止损组合单使用 |
| `stopLossPrice` | string | 条件必填 | 止损触发价格，止盈止损组合单使用 |
| `stopLossQuantity` | string | 条件必填 | 止损触发数量，止盈止损组合单使用 |
| `stockCode` | string | 是 | 股票代码，如 `00700` |
| `strike` | string | 条件必填 | 行权价，期权的行权价，期权单必传 |
| `subAccountId` | string | 是 | 证券账户 ID |
| `applyAccountId` | string | 否 | 下单申购的账号 |
| `tailAmount` | string | 条件必填 | 追踪止损单追踪金额，订单类型为 `33` 且 `tailType=1` 时必填 |
| `tailPct` | string | 条件必填 | 追踪止损单追踪比例，订单类型为 `33` 且 `tailType=2` 时必填，如 `0.05` 表示 5% |
| `tailType` | integer | 条件必填 | 追踪止损单追踪类型，枚举值：`1`=金额，`2`=比例 |
| `trigPrice` | string | 条件必填 | 条件单触发价，订单类型为 `31`、`32` 时必填 |

#### orderType 订单类型枚举

| 值 | 说明 |
|----|------|
| `1` | 竞价限价单 |
| `2` | 竞价单 |
| `3` | 限价单 |
| `4` | 增强限价单 |
| `5` | 特殊限价单 |
| `6` | 暗盘订单 |
| `9` | 市价单 |
| `31` | 止损限价单 |
| `32` | 止盈限价单 |
| `33` | 跟踪止损单 |
| `35` | 止盈止损单 |

#### 条件字段说明

| 场景 | 必填字段 |
|------|----------|
| 期权下单 | `productType`、`expiry`、`strike`、`right` |
| 非追踪单且非市价单 | `price` |
| `orderType=31` 或 `32` | `trigPrice` |
| `orderType=33` | `tailType` |
| `orderType=33` 且 `tailType=1` | `tailAmount` |
| `orderType=33` 且 `tailType=2` | `tailPct` |
| `orderType=35` | `profitPrice`、`profitQuantity`、`stopLossPrice`、`stopLossQuantity` |

#### `orderType=35` 触发语义补充

`orderType=35`（止盈止损单）表示一张同时带有止盈条件和止损条件的组合条件单，两侧条件互斥：

- 当市场价格跌至 `profitPrice` 时，系统提交限价单，并自动撤销止损侧条件单。
- 当市场价格涨至 `stopLossPrice` 时，系统提交限价单，并自动撤销止盈侧条件单。
- `profitQuantity` 表示止盈侧触发后的委托数量，`stopLossQuantity` 表示止损侧触发后的委托数量。
- `price` 是条件触发后真正提交的限价委托价格。

方向补充：

- 卖出方向下，通常用于给已有持仓同时设置止盈与止损。
- 买入平仓方向下，`profitPrice` 应低于当前市价，`stopLossPrice` 应高于当前市价。
- 设计请求参数时，建议同时核对当前市价、`direction`、`profitPrice`、`stopLossPrice` 与 `price` 的相对关系，避免条件方向与交易意图相反。

#### `orderType=31 / 32` 触发语义补充

`orderType=31`（止损限价单）与 `orderType=32`（止盈限价单）都属于条件单：先等待 `trigPrice` 触发，触发后再按 `price` 提交限价委托。

| 订单类型 | `direction=2` 卖出 | `direction=1` 买入 |
|----------|--------------------|--------------------|
| `31` 止损限价单 | 跌到或跌破某个价格后止损卖出 | 涨到某个价格后触发买入，常用于向上突破后的追价买入，`trigPrice` 通常高于当前市价 |
| `32` 止盈限价单 | 涨到某个价格后止盈卖出 | 跌到某个价格后触发买入，常用于价格回落到目标区间后逢低买入，`trigPrice` 通常低于当前市价 |

补充说明：

- `trigPrice` 是条件触发价，不等同于最终报单价。
- `price` 是触发后真正发出的限价委托价格。
- 设计请求参数时，建议同时核对当前市价、`direction`、`trigPrice` 与 `price` 的相对关系，避免条件方向与交易意图相反。

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
| `data.orderId` | string | 订单 ID，系统生成的唯一订单标识 |
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

请求参数不合法或缺少必填字段时返回。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/OrderCreate \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "timeInForce": 0,
  "clientId": 12345,
  "currency": "HKD",
  "direction": 1,
  "expType": 1,
  "marketCode": "hk",
  "orderType": 3,
  "price": "400.000",
  "quantity": "100",
  "stockCode": "00700",
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
    "timeInForce": 0,
    "clientId": 12345,
    "currency": "HKD",
    "direction": 1,
    "expType": 1,
    "marketCode": "hk",
    "orderType": 3,
    "price": "400.000",
    "quantity": "100",
    "stockCode": "00700",
    "subAccountId": "SA001",
}

response = requests.post(
    f"{BASE_URL}/api/v1/trade/OrderCreate",
    headers=headers,
    json=payload,
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

---

## 常见场景

### 1. 港股限价买入

```json
{
  "timeInForce": 0,
  "clientId": 12345,
  "subAccountId": "SA001",
  "stockCode": "00700",
  "marketCode": "hk",
  "currency": "HKD",
  "direction": 1,
  "orderType": 3,
  "price": "400.000",
  "quantity": "100"
}
```

### 2. 美股市价卖出（允许盘前盘后）

```json
{
  "timeInForce": 2,
  "clientId": 12345,
  "subAccountId": "SA001",
  "stockCode": "AAPL",
  "marketCode": "us",
  "currency": "USD",
  "direction": 2,
  "orderType": 9,
  "quantity": "10"
}
```

### 3. 期权下单（看涨期权买入）

```json
{
  "timeInForce": 0,
  "clientId": 12345,
  "subAccountId": "SA001",
  "stockCode": "AAPL",
  "marketCode": "us",
  "currency": "USD",
  "direction": 1,
  "orderType": 3,
  "price": "5.50",
  "quantity": "1",
  "productType": 15,
  "expiry": "20260630",
  "strike": "200.00",
  "right": "CALL"
}
```

### 4. 止损限价单

```json
{
  "timeInForce": 0,
  "clientId": 12345,
  "subAccountId": "SA001",
  "stockCode": "00700",
  "marketCode": "hk",
  "currency": "HKD",
  "direction": 2,
  "orderType": 31,
  "price": "380.000",
  "quantity": "100",
  "trigPrice": "385.000"
}
```

### 5. 跟踪止损单（按比例）

```json
{
  "timeInForce": 0,
  "clientId": 12345,
  "subAccountId": "SA001",
  "stockCode": "00700",
  "marketCode": "hk",
  "currency": "HKD",
  "direction": 2,
  "orderType": 33,
  "quantity": "100",
  "tailType": 2,
  "tailPct": "0.05"
}
```

### 6. 止盈止损组合单

```json
{
  "timeInForce": 0,
  "clientId": 12345,
  "subAccountId": "SA001",
  "stockCode": "00700",
  "marketCode": "hk",
  "currency": "HKD",
  "direction": 2,
  "orderType": 35,
  "price": "400.000",
  "quantity": "100",
  "profitPrice": "420.000",
  "profitQuantity": "100",
  "stopLossPrice": "390.000",
  "stopLossQuantity": "100"
}
```
