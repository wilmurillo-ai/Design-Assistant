# 经纪商列表（买卖盘经纪）

> **GET** `https://openapi.fosunxcz.com/api/v1/market/secu/brokerq`

获取指定证券的买卖盘经纪商队列。

---

## 请求

### Query Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `code` | string | 是 | 市场+证券代码。市场定义：`hk`=港股，`us`=美股，例如 `hk00700`、`usAAPL` |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 查询指定标的的买卖盘经纪商队列 | 传入 `code` 即可 |
| 查询港股标的 | 示例：`hk00700` |
| 查询美股标的 | 示例：`usAAPL` |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "data": {
    "buyBrokers": [
      {
        "ids": [
          "string"
        ],
        "num": 0
      }
    ],
    "qtDate": 0,
    "qtTime": 0,
    "sellBrokers": [
      {
        "ids": [
          "string"
        ],
        "num": 0
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
| `data` | object | 经纪商队列数据 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.buyBrokers` | array[object] | 买盘经纪商队列 |
| `data.qtDate` | integer | 行情日期，原始页面未给出格式说明 |
| `data.qtTime` | integer | 行情时间，原始页面未给出格式说明 |
| `data.sellBrokers` | array[object] | 卖盘经纪商队列 |

#### `data.buyBrokers[]` / `data.sellBrokers[]` 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `ids` | array[string] | 经纪商编号列表 |
| `num` | integer | 对应档位或数量标识，原始页面未展开说明 |

### 400 - 请求错误

原始页面存在 `400` 响应标签，但未展示具体返回结构。

---

## 使用示例

### cURL

```bash
curl --request GET \
  --url 'https://openapi.fosunxcz.com/api/v1/market/secu/brokerq?code=hk00700' \
  --header 'Accept: application/json'
```

### 请求示例

```http
GET /api/v1/market/secu/brokerq?code=hk00700 HTTP/1.1
Host: openapi-uat.fosunxcz.com
Accept: application/json
```

### 响应示例

```json
{
  "code": 0,
  "data": {
    "buyBrokers": [
      {
        "ids": [
          "string"
        ],
        "num": 0
      }
    ],
    "qtDate": 0,
    "qtTime": 0,
    "sellBrokers": [
      {
        "ids": [
          "string"
        ],
        "num": 0
      }
    ]
  },
  "message": "success",
  "requestId": "req-123456"
}
```

---

## 说明

- 本文档根据原始接口页面整理而成。
- 原始页面明确了请求参数 `code`，以及响应中的 `buyBrokers`、`sellBrokers`、`qtDate`、`qtTime` 字段结构。
- 对于 `qtDate`、`qtTime`、`num` 等未给出完整业务语义的字段，本文按原文结构保留，并做了谨慎说明。
