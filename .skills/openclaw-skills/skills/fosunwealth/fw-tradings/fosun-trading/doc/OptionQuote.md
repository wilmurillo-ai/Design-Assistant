# 期权报价（批量）

> 对应证券版文档：`doc/Quote.md`
>
> **POST** `https://openapi.fosunxcz.com/api/v1/market/opt/secu/quote`

批量获取期权合约的报价快照。

---

## 与证券报价的区别

| 项目 | 证券报价 `Quote.md` | 期权报价 |
|------|---------------------|----------|
| 接口路径 | `/api/v1/market/secu/quote` | `/api/v1/market/opt/secu/quote` |
| 代码格式 | `hk00700`、`usAAPL` | `usAAPL 20260320 270.0 CALL` |
| 返回重点 | 正股/基金/ETF 等 | 合约报价、行权价、到期日、IV、Delta 等 |

---

## 请求

### Body（application/json）

请求体包含 `codes`（必填）和 `fields`（可选）。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `codes` | array[string] | 是 | 期权代码列表，最多 `300` 个；单个代码示例：`usAAPL 20260320 270.0 CALL` |
| `fields` | array[string] | 否 | 指定返回字段；不传通常返回完整快照 |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 批量查询多个期权报价 | 传入多个 `codes` |
| 控制响应体大小 | 通过 `fields` 指定只返回所需字段 |
| 获取完整快照 | 仅传 `codes` |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "data": {
    "usAAPL 20260320 270.0 CALL": {
      "price": 0,
      "bid": 0,
      "ask": 0,
      "pClose": 0,
      "chgVal": 0,
      "chgPct": 0,
      "open": 0,
      "high": 0,
      "low": 0,
      "vol": 0,
      "turnover": 0,
      "power": 0,
      "qtDate": 0,
      "qtTime": 0,
      "rawSymbol": "AAPL",
      "mkt": "us",
      "delay": true,
      "strikePrice": 0,
      "maturityDate": 20260320,
      "delta": 0,
      "impliedVolatility": 0
    }
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
| `data` | dictionary[string, object] | 按期权代码组织的报价结果 |

#### `data[code]` 常见字段

说明：

- 价格类字段通常需要结合 `power` 还原真实数值。
- 这类接口通常采用“价格字段乘以 `10^power` 转为整数、百分比类字段默认乘以 `100`”的编码方式。
- `fields` 的完整枚举当前资料未完全展开，下面列出整理文档时能确认的常见字段。

| 字段 | 类型 | 说明 |
|------|------|------|
| `rawSymbol` | string | 标的代码或原始代码标识 |
| `name` | string | 合约名称 |
| `mkt` | string | 市场标识，如 `us` |
| `delay` | boolean | 是否延时 |
| `power` | integer | 价格精度基准 |
| `qtDate` | integer | 行情日期 |
| `qtTime` | integer | 行情时间 |
| `price` | integer | 当前价 |
| `bid` | integer | 申买价 |
| `ask` | integer | 申卖价 |
| `pClose` | integer | 昨收价 |
| `open` | integer | 今开价 |
| `high` | integer | 最高价 |
| `low` | integer | 最低价 |
| `chgVal` | integer | 涨跌额 |
| `chgPct` | integer | 涨跌幅 `%` |
| `vol` | integer | 成交量 |
| `turnover` | integer | 成交额 |
| `strikePrice` | integer | 行权价 |
| `maturityDate` | integer | 到期日 |
| `lastTradingDate` | integer | 最后交易日 |
| `premium` | integer | 溢价 |
| `moneyness` | integer | 价内 / 价外程度 |
| `delta` | integer | Delta |
| `impliedVolatility` | integer | 隐含波动率 |
| `leverageRatio` | integer | 杠杆比率 |
| `effLeverage` | integer | 有效杠杆 |
| `links` | object | 标的物等关联信息 |

#### 扩展对象字段

##### `links`

| 字段 | 类型 | 说明 |
|------|------|------|
| `links.target` | string | 标的物代码 |

### 400 - 请求错误

原始接口页存在 `400` 响应标签，但未展开具体错误结构。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/market/opt/secu/quote \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
  "codes": [
    "usAAPL 20260320 270.0 CALL",
    "usAAPL 20260320 260.0 PUT"
  ],
  "fields": [
    "price",
    "bid",
    "ask",
    "chgPct",
    "impliedVolatility",
    "delta",
    "power"
  ]
}'
```

### 请求示例

```json
{
  "codes": [
    "usAAPL 20260320 270.0 CALL",
    "usAAPL 20260320 260.0 PUT"
  ],
  "fields": [
    "price",
    "bid",
    "ask",
    "chgPct",
    "impliedVolatility",
    "delta",
    "power"
  ]
}
```

### 命令行脚本示例

```bash
$FOSUN_PYTHON query_option_price.py quote "usAAPL 20260320 270.0 CALL"
$FOSUN_PYTHON query_option_price.py quote "usAAPL 20260320 270.0 CALL" "usAAPL 20260320 260.0 PUT" --fields price bid ask delta impliedVolatility power
```

#### 数值还原示例

如果返回：

```json
{
  "price": 325,
  "chgPct": 125,
  "power": 2
}
```

则可理解为：

- `price = 325 / 10^2 = 3.25`
- `chgPct = 125 / 100 = 1.25%`

---

## 说明

- 本文档根据 OpenAPI 接口页链接、SDK `optmarket.quote()` 方法签名、仓库脚本 `query_option_price.py` 以及现有普通报价文档中的公共字段整理。
- 当前可以明确确认的是：请求体支持 `codes`、`fields`，且 `codes` 上限为 `300`。
- 实际返回字段会受市场、期权品种和账号权限影响。
- 原始 OpenAPI 页面：[`/api/v1/market/opt/secu/quote`](https://openapi-docs-sit.fosunxcz.com/?spec=option#/paths/api-v1-market-opt-secu-quote/post)
