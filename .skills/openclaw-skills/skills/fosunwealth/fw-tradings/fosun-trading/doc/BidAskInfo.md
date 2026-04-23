# 查询买卖信息 - BidAskInfo

> **POST** `https://openapi.fosunxcz.com/api/v1/trade/BidAskInfo`

根据账户与标的查询最大可买、可卖数量及购买力等。

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

查询买卖信息请求。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `clientId` | integer | 否 | 客户 ID |
| `direction` | integer | 否 | 订单方向，枚举值：`1`=买（默认），`2`=卖 |
| `marketCode` | string | 是 | 市场代码，枚举值：`hk`=港股，`us`=美股，`sh`=上交所，`sz`=深交所 |
| `orderType` | integer | 否 | 订单类型，详见下方枚举表 |
| `quantity` | string | 否 | 委托订单数量 |
| `stockCode` | string | 是 | 股票代码 |
| `subAccountId` | string | 是 | 证券账号 |
| `trigPrice` | string | 条件必填 | 条件单触发价，订单类型为 `31`、`32` 时必填 |
| `price` | string | 否 | 委托订单价格 |
| `productType` | integer | 否 | 产品类型，枚举值：`5`=港股，`6`=美股，`7`=A股，`15`=期权 |
| `expiry` | string | 条件必填 | 期权到期日，格式 `YYYYMMDD`，`productType=15` 时必填 |
| `strike` | string | 条件必填 | 期权执行价，`productType=15` 时必填 |
| `right` | string | 条件必填 | 期权方向，`CALL`/`PUT`，`productType=15` 时必填 |
| `timeInForce` | integer | 否 | 盘前盘后/夜盘标记，枚举值：`0`=普通，`2`=允许美股盘前，`4`=夜盘 |

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

---

## 响应

### 200 - OK

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "availableWithdrawBalance": "string",
    "baseQuantitySell": 0,
    "cashPurchasePower": "string",
    "cashQuantityBuy": 0,
    "currency": "string",
    "financingQty": 0,
    "lotSize": 0,
    "maxPurchasePower": "string",
    "maxQuantityBuy": 0,
    "maxQuantitySell": 0,
    "singleWithdrawBalance": "string",
    "totalAssets": "string"
  }
}
```

#### 响应公共字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，示例值 `0` |
| `message` | string | 状态消息，示例值 `success` |
| `data` | object | 返回的买卖信息数据 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `availableWithdrawBalance` | string | 总账户可用现金 |
| `baseQuantitySell` | integer | 本币种可卖数量，不包含关联币种可卖持仓数量 |
| `cashPurchasePower` | string | 现金购买力 |
| `cashQuantityBuy` | integer | 现金可买 |
| `currency` | string | 币种，`HKD`=港币，`USD`=美元，`CNH`/`CNY`=人民币 |
| `financingQty` | integer | 最大可融资（买多）/ 融券（卖空） |
| `lotSize` | integer | 每手股数 |
| `maxPurchasePower` | string | 最大购买力 |
| `maxQuantityBuy` | integer | 最大可买 |
| `maxQuantitySell` | integer | 持仓可卖，包含关联币种可卖持仓数量 |
| `singleWithdrawBalance` | string | 当前股票币种对应的币种账户可用现金 |
| `totalAssets` | string | 总资产 |

### 400 - 请求错误

请求参数不合法或缺少必填字段时返回。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/BidAskInfo \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "clientId": 12345,
  "direction": 1,
  "marketCode": "hk",
  "orderType": 3,
  "quantity": "100",
  "stockCode": "00700",
  "subAccountId": "SA001",
  "price": "400.000",
  "productType": 5,
  "timeInForce": 0
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
    "direction": 1,
    "marketCode": "hk",
    "orderType": 3,
    "quantity": "100",
    "stockCode": "00700",
    "subAccountId": "SA001",
    "price": "400.000",
    "productType": 5,
    "timeInForce": 0,
}

url = f"{BASE_URL}/api/v1/trade/BidAskInfo"
response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

---

## 典型使用场景

### 1. 港股买入前查询最大可买

```json
{
  "clientId": 12345,
  "direction": 1,
  "marketCode": "hk",
  "orderType": 3,
  "quantity": "100",
  "stockCode": "00700",
  "subAccountId": "SA001",
  "price": "400.000",
  "productType": 5,
  "timeInForce": 0
}
```

### 2. 卖出前查询可卖数量

```json
{
  "clientId": 12345,
  "direction": 2,
  "marketCode": "hk",
  "orderType": 3,
  "stockCode": "00700",
  "subAccountId": "SA001",
  "productType": 5
}
```

### 3. 美股盘前查询买入能力

```json
{
  "clientId": 12345,
  "direction": 1,
  "marketCode": "us",
  "orderType": 9,
  "stockCode": "AAPL",
  "subAccountId": "SA001",
  "productType": 6,
  "timeInForce": 2
}
```
