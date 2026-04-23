# 逐笔成交

> **GET** `https://openapi.fosunxcz.com/api/v1/market/secu/tick`

获取指定证券的逐笔成交数据。

---

## 请求

### Query Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `code` | string | 是 | 市场+证券代码。常见格式：`hk00700`、`usAAPL`、`sh600519`、`sz000001` |
| `count` | integer | 否 | 返回条数，默认 `20` |
| `id` | integer | 否 | 起始 tick ID，`-1` 表示从最新逐笔开始返回 |
| `ts` | integer(int64) | 否 | 时间戳，用于按时间定位查询 |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 查询指定标的最新逐笔成交 | 至少传 `code`，其余参数使用默认值即可 |
| 控制返回条数 | 通过 `count` 指定返回的逐笔记录数量 |
| 从指定成交位置继续拉取 | 通过 `id` 指定起始 tick ID |
| 按时间点附近查询 | 可传 `ts` 指定时间戳 |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "data": {
    "code": "hk00700",
    "ticks": [
      {
        "id": 12345,
        "price": 350.0,
        "side": "B",
        "time": 1699000000000,
        "volume": 100
      },
      {
        "id": 12346,
        "price": 350.2,
        "side": "S",
        "time": 1699000001000,
        "volume": 50
      }
    ]
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
| `data` | object | 逐笔成交数据对象 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.code` | string | 标的代码 |
| `data.ticks` | array[object] | 逐笔成交记录列表 |

#### `data.ticks[]` 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 逐笔成交记录 ID |
| `price` | number | 成交价 |
| `side` | string | 成交方向，示例值：`B`=买盘，`S`=卖盘 |
| `time` | integer(int64) | 成交时间戳 |
| `volume` | integer | 成交量 |

### 400 - 请求错误

原始接口资料中存在错误响应说明，但未展开更完整的字段结构；常见错误通常包括参数错误、权限错误或下游服务错误。

---

## 使用示例

### cURL

```bash
curl --request GET \
  --url 'https://openapi.fosunxcz.com/api/v1/market/secu/tick?code=hk00700&count=20&id=-1' \
  --header 'Accept: application/json'
```

### 请求示例

```http
GET /api/v1/market/secu/tick?code=hk00700&count=20&id=-1 HTTP/1.1
Host: openapi-uat.fosunxcz.com
Accept: application/json
```

### 响应示例

```json
{
  "code": 0,
  "data": {
    "code": "hk00700",
    "ticks": [
      {
        "id": 12345,
        "price": 350.0,
        "side": "B",
        "time": 1699000000000,
        "volume": 100
      },
      {
        "id": 12346,
        "price": 350.2,
        "side": "S",
        "time": 1699000001000,
        "volume": 50
      }
    ]
  },
  "message": "success",
  "requestId": "req-123456"
}
```

---

## 说明

- 本文档根据 OpenAPI 接口页与仓库内 SDK 示例整理而成。
- 请求参数已确认包含 `code`、`count`、`id`、`ts`。
- 对于 `side` 的业务枚举含义，当前资料可明确看到示例值 `B`、`S`；如后续接口页补充更多取值，建议再同步完善。
- 原始 OpenAPI 页面：[`/api/v1/market/secu/tick`](https://openapi-docs-sit.fosunxcz.com/?spec=stocks#/paths/api-v1-market-secu-tick/get)
