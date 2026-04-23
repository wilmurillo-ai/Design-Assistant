# 分时数据

> **GET** `https://openapi.fosunxcz.com/api/v1/market/min`

获取指定证券当日分时数据（分钟级价格、成交量等）。

---

## 请求

### Query Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `code` | string | 是 | 市场+证券代码。市场定义：`hk`=港股，`us`=美股，例如 `hk00700`、`usAAPL` |
| `count` | integer | 否 | 分时点数相关参数，需大于 `0`，默认 `5` |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 查询指定标的分时数据 | 至少传 `code` |
| 控制返回点数 | 可通过 `count` 指定返回的分时点数量 |
| 查询港股或美股 | `code` 需带市场前缀，例如 `hk00700`、`usAAPL` |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "data": {
    "delay": true,
    "min": [
      {
        "data": [
          {
            "avg": 0,
            "price": 0,
            "time": 0,
            "turnover": 0,
            "vol": 0
          }
        ],
        "date": 0,
        "pClose": 0,
        "power": 0,
        "preDate": 0,
        "total": 0,
        "type": 0
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
| `data` | object | 分时数据对象 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.delay` | boolean | 是否为延时数据 |
| `data.min` | array[object] | 分时数据列表 |

#### data.min 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | array[object] | 分钟级明细数据列表 |
| `date` | integer | 交易日期 |
| `pClose` | number | 前收盘价 |
| `power` | integer | 复权或数据权限相关标识，原始页面未展开说明 |
| `preDate` | integer | 前一交易日日期 |
| `total` | number | 汇总值，原始页面未展开说明 |
| `type` | integer | 数据类型标识，原始页面未展开说明 |

#### `data.min[].data` 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `avg` | number | 均价 |
| `price` | number | 当前价 / 成交价 |
| `time` | integer | 时间戳或时间值 |
| `turnover` | number | 成交额 |
| `vol` | number | 成交量 |

### 400 - 请求错误

原始页面存在 `400` 响应标签，但未展示具体返回结构。

---

## 使用示例

### cURL

```bash
curl --request GET \
  --url 'https://openapi.fosunxcz.com/api/v1/market/min?code=hk00700&count=5' \
  --header 'Accept: application/json'
```

### 请求示例

```http
GET /api/v1/market/min?code=hk00700&count=5 HTTP/1.1
Host: openapi-uat.fosunxcz.com
Accept: application/json
```

### 响应示例

```json
{
  "code": 0,
  "data": {
    "delay": true,
    "min": [
      {
        "data": [
          {
            "avg": 0,
            "price": 0,
            "time": 0,
            "turnover": 0,
            "vol": 0
          }
        ],
        "date": 0,
        "pClose": 0,
        "power": 0,
        "preDate": 0,
        "total": 0,
        "type": 0
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
- 原始页面仅明确了 `code`、`count`、`delay`、`min` 及分钟明细字段。
- 对于 `power`、`total`、`type`、`time` 等未给出完整定义的字段，本文按原文结构保留，并做了谨慎说明。
