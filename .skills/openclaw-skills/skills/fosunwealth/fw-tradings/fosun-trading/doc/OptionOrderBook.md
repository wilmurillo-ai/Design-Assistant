# 期权盘口/买卖档

> 对应证券版文档：`doc/OrderBook.md`
>
> **GET** `https://openapi.fosunxcz.com/api/v1/market/opt/secu/orderbook`

获取指定期权合约的买卖盘口数据。

---

## 与证券盘口的区别

| 项目 | 证券盘口 `OrderBook.md` | 期权盘口 |
|------|-------------------------|----------|
| 接口路径 | `/api/v1/market/secu/orderbook` | `/api/v1/market/opt/secu/orderbook` |
| 代码格式 | `hk00700`、`usAAPL` | `usAAPL 20260320 270.0 CALL` |
| 查询参数 | `code`、`count` | 仅 `code` |

---

## 请求

### Query Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `code` | string | 是 | 期权代码，需传完整合约字符串，例如 `usAAPL 20260320 270.0 CALL` |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 查询指定期权盘口 | 至少传 `code` |
| 查看买卖档位 | 返回默认盘口深度，具体层数由服务端决定 |

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
| `requestId` | string | 请求追踪 ID |
| `data` | object | 盘口数据对象 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.buyOrders` | array[object] | 买盘档位信息 |
| `data.buyPct` | integer | 买盘数量占比 `%` |
| `data.power` | integer | 价格精度基准，价格字段通常需除以 `10^power` 还原 |
| `data.qtDate` | integer | 行情日期，格式通常为 `YYYYMMDD` |
| `data.qtTime` | integer | 行情时间，格式通常为 `HHMMSSmmm` |
| `data.sellOrders` | array[object] | 卖盘档位信息 |
| `data.sellPct` | integer | 卖盘数量占比 `%` |

#### `data.buyOrders[]` / `data.sellOrders[]` 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `o` | integer | 档位标识，原始页面未展开具体含义 |
| `p` | integer | 价格整数值，需结合 `power` 还原 |
| `v` | integer | 该档位对应委托数量 |

### 400 - 请求错误

原始接口页存在 `400` 响应标签，但未展开具体错误结构。

---

## 使用示例

### cURL

```bash
curl --request GET \
  --url 'https://openapi.fosunxcz.com/api/v1/market/opt/secu/orderbook?code=usAAPL%2020260320%20270.0%20CALL' \
  --header 'Accept: application/json'
```

### 请求示例

```http
GET /api/v1/market/opt/secu/orderbook?code=usAAPL%2020260320%20270.0%20CALL HTTP/1.1
Host: openapi-uat.fosunxcz.com
Accept: application/json
```

### 命令行脚本示例

```bash
$FOSUN_PYTHON query_option_price.py orderbook "usAAPL 20260320 270.0 CALL"
```

---

## 说明

- 本文档根据 OpenAPI 接口页链接、SDK `optmarket.orderbook()` 调用签名以及仓库中的 `query_option_price.py` 整理。
- 当前可明确的请求参数只有 `code`，这点与证券盘口接口不同。
- 响应结构与证券盘口接口相近，但语义对象是期权合约，不是正股证券。
- 原始 OpenAPI 页面：[`/api/v1/market/opt/secu/orderbook`](https://openapi-docs-sit.fosunxcz.com/?spec=option#/paths/api-v1-market-opt-secu-orderbook/get)
