# 期权逐笔成交

> 对应证券版文档：`doc/Tick.md`
>
> **GET** `https://openapi.fosunxcz.com/api/v1/market/opt/tick`

获取指定期权合约的逐笔成交数据。

---

## 与证券逐笔的区别

| 项目 | 证券逐笔 `Tick.md` | 期权逐笔 |
|------|--------------------|----------|
| 接口路径 | `/api/v1/market/secu/tick` | `/api/v1/market/opt/tick` |
| 代码格式 | `hk00700`、`usAAPL` | `usAAPL 20260320 270.0 CALL` |
| 查询参数 | `code`、`count`、`id`、`ts` | `code`、`count`、`id` |

---

## 请求

### Query Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `code` | string | 是 | 期权代码，需传完整合约字符串，例如 `usAAPL 20260320 270.0 CALL` |
| `count` | integer | 否 | 返回条数，默认 `20` |
| `id` | integer | 否 | 起始 tick ID，`-1` 表示从最新逐笔开始返回 |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 查询某个期权最新逐笔成交 | 至少传 `code` |
| 控制返回条数 | 通过 `count` 指定 |
| 从指定成交位置继续拉取 | 通过 `id` 指定起始 tick ID |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "data": {
    "code": "usAAPL 20260320 270.0 CALL",
    "ticks": [
      {
        "id": 12345,
        "price": 325,
        "side": "B",
        "time": 1699000000000,
        "volume": 100
      },
      {
        "id": 12346,
        "price": 330,
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
| `requestId` | string | 请求追踪 ID |
| `data` | object | 逐笔成交数据对象 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.code` | string | 期权代码 |
| `data.ticks` | array[object] | 逐笔成交记录列表 |

#### `data.ticks[]` 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 逐笔成交记录 ID |
| `price` | number | 成交价；若接口按整数编码返回，需结合精度规则还原 |
| `side` | string | 成交方向，常见示例值：`B`=买盘，`S`=卖盘 |
| `time` | integer(int64) | 成交时间戳 |
| `volume` | integer | 成交量 |

### 400 - 请求错误

原始接口页存在错误响应标签，但未展开更完整的字段结构。

---

## 使用示例

### cURL

```bash
curl --request GET \
  --url 'https://openapi.fosunxcz.com/api/v1/market/opt/tick?code=usAAPL%2020260320%20270.0%20CALL&count=20&id=-1' \
  --header 'Accept: application/json'
```

### 请求示例

```http
GET /api/v1/market/opt/tick?code=usAAPL%2020260320%20270.0%20CALL&count=20&id=-1 HTTP/1.1
Host: openapi-uat.fosunxcz.com
Accept: application/json
```

### 命令行脚本示例

```bash
$FOSUN_PYTHON query_option_price.py tick "usAAPL 20260320 270.0 CALL" -n 20
```

---

## 说明

- 本文档根据 OpenAPI 接口页链接、SDK `optmarket.tick()` 调用签名以及仓库中的 `query_option_price.py` 整理。
- 已确认请求参数包含 `code`、`count`、`id`。
- 该接口没有证券逐笔接口中的 `ts` 参数。
- 原始 OpenAPI 页面：[`/api/v1/market/opt/tick`](https://openapi-docs-sit.fosunxcz.com/?spec=option#/paths/api-v1-market-opt-tick/get)
