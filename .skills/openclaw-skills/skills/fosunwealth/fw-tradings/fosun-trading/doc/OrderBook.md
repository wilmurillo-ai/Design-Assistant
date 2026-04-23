# 盘口/买卖档

> **GET** `https://openapi.fosunxcz.com/api/v1/market/secu/orderbook`

获取指定证券的买卖盘口数据（档位报价与数量）。

---

## 请求

### Query Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `code` | string | 是 | 市场+证券代码。市场定义：`hk`=港股，`us`=美股，例如 `hk00700`、`usAAPL` |
| `count` | integer | 否 | 档位数量，默认 `5` |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 查询指定标的盘口 | 至少传 `code` |
| 控制返回档位数 | 可通过 `count` 指定返回档位数量 |
| 查询港股或美股 | `code` 需带市场前缀，例如 `hk00700`、`usAAPL` |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "data": {
    "buyOrders": [
      {
        "o": 0,
        "p": 0,
        "v": 0
      }
    ],
    "buyPct": 0,
    "power": 0,
    "qtDate": 0,
    "qtTime": 0,
    "sellOrders": [
      {
        "o": 0,
        "p": 0,
        "v": 0
      }
    ],
    "sellPct": 0
  },
  "message": "success",
  "requestId": "req-123456"
}
```

#### 响应公共字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，示例值 `0` |
| `message` | string | 状态消息，示例值 `success` |
| `requestId` | string | 请求追踪 ID，示例值 `req-123456` |
| `data` | object | 盘口数据对象 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.buyOrders` | array[object] | 买盘档位信息 |
| `data.buyPct` | integer | 买盘数量占比 `%` |
| `data.power` | integer | 价格基准。价格类字段乘以 `10^power` 转为整数，其它浮点型数值默认乘以 `100` 转为整数 |
| `data.qtDate` | integer | 行情日期，格式 `20060102`（年月日） |
| `data.qtTime` | integer | 行情时间，格式 `150405123`（时分秒毫秒） |
| `data.sellOrders` | array[object] | 卖盘档位信息 |
| `data.sellPct` | integer | 卖盘数量占比 `%` |

#### `data.buyOrders[]` / `data.sellOrders[]` 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `o` | integer | 档位标识。原始页面未展开具体语义，通常可理解为档位序号或档位编号 |
| `p` | integer | 档位价格的整数值，需结合 `data.power` 还原为实际价格 |
| `v` | integer | 该档位对应的委托数量 |

### 400 - 请求错误

原始页面存在 `400` 响应标签，但未展示具体返回结构。

---

## 使用示例

### cURL

```bash
curl --request GET \
  --url 'https://openapi.fosunxcz.com/api/v1/market/secu/orderbook?code=hk00700&count=5' \
  --header 'Accept: application/json'
```

### 请求示例

```http
GET /api/v1/market/secu/orderbook?code=hk00700&count=5 HTTP/1.1
Host: openapi-uat.fosunxcz.com
Accept: application/json
```

### 响应示例

```json
{
  "code": 0,
  "data": {
    "buyOrders": [
      {
        "o": 0,
        "p": 0,
        "v": 0
      }
    ],
    "buyPct": 0,
    "power": 0,
    "qtDate": 0,
    "qtTime": 0,
    "sellOrders": [
      {
        "o": 0,
        "p": 0,
        "v": 0
      }
    ],
    "sellPct": 0
  },
  "message": "success",
  "requestId": "req-123456"
}
```

---

## 说明

- 本文档根据原始接口页面整理而成。
- 原始页面明确了请求参数 `code`、`count`，以及响应中的 `buyOrders`、`sellOrders`、`buyPct`、`sellPct`、`power`、`qtDate`、`qtTime` 字段结构。
- 原始页面未展开 `o` 字段的精确定义，本文按盘口语义谨慎标注为“档位标识”。
- 价格字段通常需要按 `实际价格 = p / 10^power` 进行还原。
