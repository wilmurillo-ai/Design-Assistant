# 查询订单列表 - OrderList

> **POST** `https://openapi.fosunxcz.com/api/v1/trade/OrderList`

分页查询指定账户的订单列表。

---

## 请求

### Headers

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `X-api-key` | string | 是 | API Key，标识客户端 |
| `X-lang` | string | 是 | 语言，如 `zh-CN`、`en` |
| `X-request-id` | string | 是 | 请求追踪 ID，必填 |
| `X-session` | string | 是 | 会话 ID |

### Body（application/json）

查询订单列表请求。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `clientId` | integer | 否 | 客户 ID |
| `count` | integer | 否 | 返回数量，分页大小，默认 `20` |
| `direction` | integer | 否 | 查询指定订单方向，枚举值：`1`=买，`2`=卖。不传则返回全部方向 |
| `fromDate` | string | 否 | 开始日期，格式 `yyyy-mm-dd`，不传则默认查询最近 `7` 天 |
| `market` | array[string] | 否 | 查询指定市场，枚举值：`hk`=港股，`us`=美股。不传则返回全部市场 |
| `sort` | string | 否 | 排序方式，枚举值：`desc`=逆序（默认），`asc`=顺序。按提交时间排序 |
| `start` | integer | 否 | 偏移量，分页起始位置，从 `0` 开始 |
| `statusArr` | array[integer] | 否 | 查询指定状态订单，枚举值见下方状态枚举 |
| `stockCode` | string | 否 | 股票代码 |
| `subAccountId` | string | 是 | 证券账户 |
| `applyAccountId` | string | 否 | 下单申购的账号 |
| `showType` | integer | 否 | 展示类型，`0`=只有正股订单，`1`=正股和期权订单，`2`=只有期权订单 |
| `toDate` | string | 否 | 结束日期，格式 `yyyy-mm-dd` |

#### statusArr 订单状态枚举

| 值 | 说明 |
|----|------|
| `20` | 待报 |
| `22` | 待处理 |
| `23` | 待复核 |
| `40` | 已报 |
| `50` | 全成 |
| `60` | 部成 |
| `70` | 已撤 |
| `80` | 部撤 |
| `90` | 废单 |
| `92` | 复核未通过 |
| `100` | 已失效 |
| `21` | 条件单-待触发 |
| `71` | 条件单-已撤销 |
| `91` | 条件单-已取消 |
| `101` | 条件单-过期 |
| `901` | 条件单废单 |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "count": 0,
    "list": [
      {
        "canCancel": 0,
        "canModify": 0,
        "currency": "string",
        "direction": 0,
        "embeddedBillStatus": 0,
        "expType": 0,
        "filledPrice": "string",
        "filledQuantity": "string",
        "filledTime": "string",
        "marketCode": "string",
        "name": "string",
        "orderId": "string",
        "orderStatus": 0,
        "orderType": 0,
        "power": 0,
        "price": "string",
        "quantity": "string",
        "spread": "string",
        "spreadCode": 0,
        "stockCode": "string",
        "subAccountId": "string",
        "submittedTime": "string",
        "submittedTimestamp": 0,
        "tailAmount": "string",
        "tailPct": "string",
        "tailType": 0,
        "timeInForce": 0,
        "timeZone": "string",
        "trigPrice": "string",
        "trigTime": "string",
        "productType": 0,
        "expiry": "string",
        "strike": "string",
        "right": "string"
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
| `code` | integer | 状态码，示例值为 `0` |
| `message` | string | 状态消息，示例值为 `success` |

#### data 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `count` | integer | 当前返回数量 |
| `list` | array[object] | 订单列表 |
| `start` | integer | 当前分页起始位置 |
| `total` | integer | 符合条件的订单总数 |

#### list 中每个订单对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `canCancel` | integer | 是否可撤单 |
| `canModify` | integer | 是否可改单 |
| `currency` | string | 币种 |
| `direction` | integer | 买卖方向 |
| `embeddedBillStatus` | integer | 内嵌账单状态 |
| `expType` | integer | 订单时效类型 |
| `filledPrice` | string | 成交价格 |
| `filledQuantity` | string | 成交数量 |
| `filledTime` | string | 成交时间 |
| `marketCode` | string | 市场代码 |
| `name` | string | 标的名称 |
| `orderId` | string | 订单 ID |
| `orderStatus` | integer | 订单状态 |
| `orderType` | integer | 订单类型 |
| `power` | integer | 购买力标识 |
| `price` | string | 委托价格 |
| `quantity` | string | 委托数量 |
| `spread` | string | 追踪止损价差 |
| `spreadCode` | integer | 价差代码 |
| `stockCode` | string | 股票代码 |
| `subAccountId` | string | 证券账户 |
| `submittedTime` | string | 提交时间 |
| `submittedTimestamp` | integer | 提交时间戳 |
| `tailAmount` | string | 追踪金额 |
| `tailPct` | string | 追踪比例 |
| `tailType` | integer | 追踪类型 |
| `timeInForce` | integer | 有效期类型 |
| `timeZone` | string | 时区 |
| `trigPrice` | string | 触发价格 |
| `trigTime` | string | 触发时间 |
| `productType` | integer | 产品类型 |
| `expiry` | string | 期权到期日 |
| `strike` | string | 行权价 |
| `right` | string | 期权方向 |

#### orderType 订单类型枚举

| 值 | 说明 |
|----|------|
| `1` | 竞价限价单 |
| `2` | 竞价单 |
| `3` | 限价单 |
| `4` | 增强限价单 |
| `5` | 特殊限价单 |
| `9` | 市价单 |
| `31` | 止损限价单 |
| `32` | 止盈限价单 |
| `33` | 跟踪止损单 |
| `34` | 止损单 |
| `35` | 止盈止损单 |

### 400 - 请求错误

请求参数不合法或缺少必填字段时返回。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/OrderList \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "clientId": 12345,
  "count": 20,
  "direction": 1,
  "fromDate": "2026-03-01",
  "market": [
    "hk"
  ],
  "sort": "desc",
  "start": 0,
  "statusArr": [
    40,
    60
  ],
  "stockCode": "00700",
  "subAccountId": "SA001",
  "applyAccountId": "APPLY001",
  "showType": 1,
  "toDate": "2026-03-12"
}'
```

### Python

```python
import json
import uuid

import requests

BASE_URL = "https://openapi.fosunxcz.com"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-api-key": "YOUR_API_KEY",
    "X-lang": "zh-CN",
    "X-request-id": str(uuid.uuid4()),
    "X-session": "YOUR_SESSION_ID",
}

payload = {
    "clientId": 12345,
    "count": 20,
    "direction": 1,
    "fromDate": "2026-03-01",
    "market": ["hk"],
    "sort": "desc",
    "start": 0,
    "statusArr": [40, 60],
    "stockCode": "00700",
    "subAccountId": "SA001",
    "applyAccountId": "APPLY001",
    "showType": 1,
    "toDate": "2026-03-12",
}

url = f"{BASE_URL}/api/v1/trade/OrderList"
response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

if result["code"] == 0:
    data = result["data"]
    print(f"总订单数: {data['total']}")
    for order in data["list"]:
        print(
            f"订单 {order['orderId']}: {order['stockCode']} "
            f"状态={order['orderStatus']} 数量={order['quantity']} 价格={order['price']}"
        )
```

---

## 常见场景

### 1. 查询全部订单（默认分页）

```json
{
  "subAccountId": "SA001",
  "start": 0,
  "count": 20,
  "sort": "desc"
}
```

### 2. 按市场筛选（仅港股）

```json
{
  "subAccountId": "SA001",
  "market": ["hk"],
  "start": 0,
  "count": 20
}
```

### 3. 查询指定状态订单（已报 + 部成）

```json
{
  "subAccountId": "SA001",
  "statusArr": [40, 60],
  "start": 0,
  "count": 20
}
```

### 4. 按日期范围查询

```json
{
  "subAccountId": "SA001",
  "fromDate": "2026-03-01",
  "toDate": "2026-03-12",
  "start": 0,
  "count": 50
}
```

### 5. 查询正股和期权订单

```json
{
  "subAccountId": "SA001",
  "showType": 1,
  "start": 0,
  "count": 20
}
```
