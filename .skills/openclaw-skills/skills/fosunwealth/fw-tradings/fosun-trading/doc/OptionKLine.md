# 期权 K 线

> 对应证券版文档：`doc/KLine.md`
>
> **POST** `https://openapi.fosunxcz.com/api/v1/market/opt/kline`

获取指定期权合约的 K 线数据。

---

## 与证券 K 线的区别

| 项目 | 证券 K 线 `KLine.md` | 期权 K 线 |
|------|----------------------|-----------|
| 接口路径 | `/api/v1/market/kline` | `/api/v1/market/opt/kline` |
| 代码格式 | `hk00700`、`usAAPL` | `usAAPL 20260320 270.0 CALL` |
| 额外参数 | 有 `delay`、`right` | 有 `interval`，无 `delay`、`right` |

---

## 请求

### Body（application/json）

请求体中，`code` 和 `ktype` 为必填字段。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `code` | string | 是 | 期权代码，例如 `usAAPL 20260320 270.0 CALL` |
| `ktype` | string | 是 | K 线周期。SDK 示例常见取值有 `1`、`5`、`15`、`day` |
| `endTime` | integer | 否 | 结束时间 |
| `interval` | integer | 否 | K 线间隔 |
| `num` | integer | 否 | 返回条数 |
| `startTime` | integer | 否 | 开始时间 |
| `suspension` | integer | 否 | 停牌处理方式 |
| `time` | integer | 否 | 时间戳定位点 |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 查询指定期权 K 线 | 至少传 `code`、`ktype` |
| 限定时间范围 | 可结合 `startTime`、`endTime` 使用 |
| 控制返回条数 | 通过 `num` 指定 |
| 按某一时点附近定位 | 可传 `time` |

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
| `requestId` | string | 请求追踪 ID |
| `data` | object | K 线数据对象 |

#### data 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.data` | array[object] | K 线明细列表 |
| `data.delay` | boolean | 是否为延时数据 |
| `data.power` | integer | 价格精度基准，价格字段通常需除以 `10^power` 还原 |
| `data.total` | integer | 返回总数 |

#### `data.data[]` 数组中每个对象的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `close` | number | 收盘价 |
| `high` | number | 最高价 |
| `low` | number | 最低价 |
| `open` | number | 开盘价 |
| `pClose` | number | 前收盘价 |
| `time` | integer | 时间戳 |
| `tor` | number | 换手率或活跃度相关字段，原始页面未展开说明 |
| `turnover` | number | 成交额 |
| `vol` | number | 成交量 |

### 400 - 请求错误

原始接口页存在 `400` 响应标签，但未展开具体错误结构。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/market/opt/kline \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
  "code": "usAAPL 20260320 270.0 CALL",
  "ktype": "day",
  "num": 10
}'
```

### 请求示例

```json
{
  "code": "usAAPL 20260320 270.0 CALL",
  "ktype": "day",
  "num": 10
}
```

### 命令行脚本示例

```bash
$FOSUN_PYTHON query_option_price.py kline "usAAPL 20260320 270.0 CALL" --ktype day -n 10
```

---

## 说明

- 本文档根据 OpenAPI 接口页链接、SDK `optmarket.kline()` 方法签名以及仓库脚本 `query_option_price.py` 整理。
- 目前可明确的请求字段包括 `code`、`ktype`、`endTime`、`interval`、`num`、`startTime`、`suspension`、`time`。
- `ktype` 的完整枚举在当前可见资料中未完全展开；仓库示例已明确支持 `1`、`5`、`15`、`day`。
- 原始 OpenAPI 页面：[`/api/v1/market/opt/kline`](https://openapi-docs-sit.fosunxcz.com/?spec=option#/paths/api-v1-market-opt-kline/post)
