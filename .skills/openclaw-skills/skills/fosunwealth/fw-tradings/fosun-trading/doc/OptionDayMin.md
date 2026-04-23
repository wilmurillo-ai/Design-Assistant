# 期权多日分时

> 对应证券版文档：`doc/Min.md`
>
> **GET** `https://openapi.fosunxcz.com/api/v1/market/opt/day_min`

获取指定期权合约的多日分时数据。

---

## 与证券分时的区别

| 项目 | 证券分时 `Min.md` | 期权多日分时 |
|------|-------------------|--------------|
| 接口路径 | `/api/v1/market/min` | `/api/v1/market/opt/day_min` |
| 代码格式 | `hk00700`、`usAAPL` | `usAAPL 20260320 270.0 CALL` |
| 天数参数 | `count` | `num` |
| 返回范围 | 单日分时 | 多日分时 |

---

## 请求

### Query Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `code` | string | 是 | 期权代码，需传完整合约字符串，例如 `usAAPL 20260320 270.0 CALL` |
| `num` | integer | 否 | 查询天数，SDK 注释标明范围为 `1~10`，默认 `5` |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 查询某个期权近几日分时 | 至少传 `code` |
| 控制返回天数 | 通过 `num` 指定返回的交易日数量 |
| 查看单个期权分钟级走势 | 返回结果按天分组，每天包含分钟明细 |

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
| `requestId` | string | 请求追踪 ID |
| `data` | object | 多日分时数据对象 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.delay` | boolean | 是否为延时数据 |
| `data.min` | array[object] | 按交易日分组的分时数据列表 |

#### `data.min[]` 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | array[object] | 当日分钟级明细 |
| `date` | integer | 交易日期 |
| `pClose` | number | 前收盘价 |
| `power` | integer | 价格精度基准，价格字段通常需除以 `10^power` 还原 |
| `preDate` | integer | 前一交易日日期 |
| `total` | number | 汇总值，原始页面未展开说明 |
| `type` | integer | 数据类型标识，原始页面未展开说明 |

#### `data.min[].data[]` 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `avg` | number | 均价 |
| `price` | number | 当前价 / 成交价 |
| `time` | integer | 时间值或时间戳 |
| `turnover` | number | 成交额 |
| `vol` | number | 成交量 |

### 400 - 请求错误

原始接口页存在 `400` 响应标签，但未展开具体错误结构。

---

## 使用示例

### cURL

```bash
curl --request GET \
  --url 'https://openapi.fosunxcz.com/api/v1/market/opt/day_min?code=usAAPL%2020260320%20270.0%20CALL&num=3' \
  --header 'Accept: application/json'
```

### 请求示例

```http
GET /api/v1/market/opt/day_min?code=usAAPL%2020260320%20270.0%20CALL&num=3 HTTP/1.1
Host: openapi-uat.fosunxcz.com
Accept: application/json
```

### 命令行脚本示例

```bash
$FOSUN_PYTHON query_option_price.py day-min "usAAPL 20260320 270.0 CALL" --days 3
```

---

## 说明

- 本文档根据 OpenAPI 接口页链接、SDK `optmarket.day_min()` 调用签名以及仓库中的 `query_option_price.py` 整理。
- SDK 明确该接口为“期权多日分时”，并支持 `code`、`num` 两个参数，其中 `num` 为查询天数。
- 响应结构与证券分时接口相近，但语义上是“多日分组”，不要与证券单日 `min` 接口混用。
- 原始 OpenAPI 页面：[`/api/v1/market/opt/day_min`](https://openapi-docs-sit.fosunxcz.com/?spec=option#/paths/api-v1-market-opt-day_min/get)
