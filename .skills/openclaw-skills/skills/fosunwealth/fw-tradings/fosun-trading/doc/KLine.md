# K 线

> **POST** `https://openapi.fosunxcz.com/api/v1/market/kline`

获取指定证券的 K 线数据（开高低收、成交量等）。

---

## 请求

### Body（application/json）

请求体中，`code`（港股：`hk+证券代码`，美股：`us+证券代码`）和 `ktype` 为必填字段。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `code` | string | 是 | 证券代码，例如 `hk00700` |
| `delay` | boolean | 否 | 是否延时 |
| `endTime` | integer | 否 | 结束时间 |
| `ktype` | string | 是 | K 线周期，见下方枚举 |
| `num` | integer | 否 | 返回条数 |
| `right` | string | 否 | 复权类型 |
| `startTime` | integer | 否 | 开始时间 |
| `suspension` | integer | 否 | 停牌处理 |
| `time` | integer | 否 | 时间戳，定位点 |

#### ktype 周期枚举

| 值 | 说明 |
|----|------|
| `min1` | 1 分钟 |
| `min5` | 5 分钟 |
| `min15` | 15 分钟 |
| `min30` | 30 分钟 |
| `min60` | 60 分钟 |
| `day` | 日 K |
| `week` | 周 K |
| `month` | 月 K |
| `quarter` | 季 K |
| `year` | 年 K |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 查询指定标的 K 线 | 至少传 `code`、`ktype` |
| 限定时间范围 | 可结合 `startTime`、`endTime` 使用 |
| 指定返回条数 | 可通过 `num` 控制返回数量 |
| 按时间点定位 | 可通过 `time` 指定定位时间戳 |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "data": {
    "data": [
      {
        "close": 0,
        "high": 0,
        "low": 0,
        "open": 0,
        "pClose": 0,
        "time": 0,
        "tor": 0,
        "turnover": 0,
        "vol": 0
      }
    ],
    "delay": true,
    "power": 0,
    "total": 0
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
| `data` | object | K 线数据对象 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.data` | array[object] | K 线数据列表 |
| `data.delay` | boolean | 是否为延时数据 |
| `data.power` | integer | 复权相关信息，原始文档未展开说明 |
| `data.total` | integer | 返回总数 |

#### data.data 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `close` | number | 收盘价 |
| `high` | number | 最高价 |
| `low` | number | 最低价 |
| `open` | number | 开盘价 |
| `pClose` | number | 前收盘价 |
| `time` | integer | 时间戳 |
| `tor` | number | 换手率 |
| `turnover` | number | 成交额 |
| `vol` | number | 成交量 |

### 400 - 请求错误

原始页面存在 `400` 响应标签，但未展示具体返回结构。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/market/kline \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
  "code": "hk00700",
  "delay": true,
  "endTime": 0,
  "ktype": "day",
  "num": 0,
  "right": "string",
  "startTime": 0,
  "suspension": 0,
  "time": 0
}'
```

### 请求示例

```json
{
  "code": "hk00700",
  "ktype": "day",
  "delay": true,
  "num": 200
}
```

### 响应示例

```json
{
  "code": 0,
  "data": {
    "data": [
      {
        "close": 0,
        "high": 0,
        "low": 0,
        "open": 0,
        "pClose": 0,
        "time": 0,
        "tor": 0,
        "turnover": 0,
        "vol": 0
      }
    ],
    "delay": true,
    "power": 0,
    "total": 0
  },
  "message": "success",
  "requestId": "req-123456"
}
```

---

## 说明

- 本文档根据原始接口页面整理而成。
- 对于 `right`、`suspension`、`power` 等未给出完整枚举或定义的字段，暂按原文保留。
