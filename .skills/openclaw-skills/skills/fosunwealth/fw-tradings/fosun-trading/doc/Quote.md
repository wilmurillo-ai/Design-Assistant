# 证券报价（批量）

> **POST** `https://openapi.fosunxcz.com/api/v1/market/secu/quote`

批量获取证券实时报价或延时报价。

---

## 请求

### Body（application/json）

请求体包含 `codes`（必填）和 `fields`（可选）。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `codes` | array[string] | 是 | 证券代码列表，最多 `300` 个。单个 `code` 格式为“市场+证券代码”，原始页面明确支持 `hk`=港股、`us`=美股，例如 `hk00700`、`usAAPL` |
| `fields` | array[string] | 否 | 指定返回字段；不传则返回全部字段。原始页面未给出可选字段枚举，一般传响应中的字段名 |

#### 请求说明

| 场景 | 说明 |
|------|------|
| 批量查询多个标的报价 | 传入多个 `codes` |
| 控制响应体大小 | 通过 `fields` 指定仅返回需要的字段 |
| 获取完整快照 | 仅传 `codes`，不传 `fields` |

---

## 响应

### 200 - 成功

```json
{
  "code": 0,
  "data": {
    "hk00700": {
      "price": 0,
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
      "name": "string",
      "rawSymbol": "string",
      "mkt": "hk",
      "delay": true
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
| `requestId` | string | 请求追踪 ID，示例值 `req-123456` |
| `data` | dictionary[string, object] | 报价结果字典。原始示例使用 `property1`、`property2` 占位，实际通常按证券标识组织 |

#### `data[code]` 字段详解

> 说明：
>
> - 价格类字段需要结合 `power` 还原真实数值。
> - 原始页面说明：价格类字段乘以 `10^power` 转为整数；其它浮点型数值默认乘以 `100` 转为整数。
> - 以下字段中，部分只在特定市场或特定品种下返回。

#### 1. 基础标识与状态

| 字段 | 类型 | 说明 |
|------|------|------|
| `rawSymbol` | string | 证券代码 |
| `name` | string | 名称 |
| `mkt` | string | 市场，`hk`=港股，`us`=美股 |
| `exchange` | string | 交易所标识 |
| `currency` | string | 交易币种 |
| `board` | string | 板块标识 |
| `logo` | string | Logo 地址或标识 |
| `delay` | boolean | 是否延时 |
| `tradeStatus` | integer | 交易状态：`0`=正常，`2`=停牌，`3`=待上市，`4`=暂停上市，`5`=已退市，`6`=已到期，`7`=暗盘交易，`8`=暗盘已收盘 |
| `tradable` | integer | 是否可交易，原始页面未展开枚举 |
| `nightTrading` | boolean | 是否支持夜盘 |
| `registration` | boolean | 是否为注册制相关标识，原始页面未展开说明 |
| `canVAExchange` | boolean | 是否可进行 VA 兑换，原始页面未展开说明 |
| `isMargin` | boolean | 是否支持保证金 |
| `isProfit` | boolean | 是否盈利 |
| `isVie` | boolean | 是否 VIE 架构标识 |
| `oneClassShare` | boolean | 是否同股同权 |
| `votingDiff` | boolean | 是否存在不同投票权 |
| `isCryptoETF` | boolean | 是否为加密资产 ETF |
| `isDeriv` | integer | 是否为衍生品标识 |
| `spacType` | integer | SPAC 类型 |
| `optStatus` | integer | 期权状态，原始页面未展开说明 |
| `connType` | integer | 联通/互联互通类型，原始页面未展开说明 |
| `posFlag` | integer | POS 阶段标记 |
| `casFlag` | integer | CAS 阶段标记 |

#### 2. 时间与精度

| 字段 | 类型 | 说明 |
|------|------|------|
| `qtDate` | integer | 行情日期，格式 `20060102`（年月日） |
| `qtTime` | integer | 行情时间，格式 `150405123`（时分秒毫秒） |
| `power` | integer | 价格精度基准。价格类字段需除以 `10^power` 还原 |
| `latestClose` | integer | 最近收盘价 |
| `pClose` | integer | 昨收价（prevClose） |
| `prePClose` | integer | 前盘昨收或前置昨收，原始页面说明为计算字段之一 |
| `postPClose` | integer | 盘后昨收或后置昨收，原始页面未展开说明 |

#### 3. 价格与涨跌

| 字段 | 类型 | 说明 |
|------|------|------|
| `price` | integer | 当前价 |
| `open` | integer | 今开价 |
| `high` | integer | 最高价 |
| `low` | integer | 最低价 |
| `avg` | integer | 平均价 |
| `chgVal` | integer | 涨跌额 |
| `chgPct` | integer | 涨跌幅 `%` |
| `chgPct5d` | integer | 5 日涨跌幅 `%` |
| `chgPct20d` | integer | 20 日涨跌幅 `%` |
| `chgPctYtd` | integer | 年初至今涨跌幅 `%` |
| `amp` | integer | 振幅 `%` |
| `week52High` | integer | 52 周最高价 |
| `week52Low` | integer | 52 周最低价 |
| `limitUp` | integer | 涨停价，A 股特有 |
| `limitDown` | integer | 跌停价，A 股特有 |

#### 4. 成交与活跃度

| 字段 | 类型 | 说明 |
|------|------|------|
| `vol` | integer | 成交量 |
| `turnover` | integer | 成交额 |
| `tor` | integer | 换手率 `%`（turnoverRatio） |
| `volRatio` | integer | 量比 |
| `afVol` | integer | 盘后成交量，上交所科创板特有 |
| `afTurnover` | integer | 盘后成交额，上交所科创板特有 |
| `bidAskRatio` | integer | 委比 |
| `spreadCode` | integer | 价差表类型 |
| `minTradeUnit` | integer | 每手股数 |

#### 5. 市值、股本与估值

| 字段 | 类型 | 说明 |
|------|------|------|
| `mktCap` | integer | 总市值 |
| `floatMktCap` | integer | 流通市值 |
| `assetSize` | integer | 资产规模 |
| `nav` | integer | 每股净值 |
| `floatShares` | integer | 流通股 |
| `totalShares` | integer | 总股本 |
| `issueVol` | integer | 总发行量 |
| `pb` | integer | 市净率 |
| `peStatic` | integer | 市盈率（静） |
| `peTTM` | integer | 市盈率 TTM |
| `dyrStatic` | integer | 股息率（静） |
| `dyrTTM` | integer | 股息率 TTM |
| `dpsTTM` | integer | 文档标注为 ETF 相关字段，原始页面未展开说明 |

#### 6. 分类与基金属性

| 字段 | 类型 | 说明 |
|------|------|------|
| `first` | integer | 一级分类 |
| `second` | integer | 二级分类 |
| `third` | integer | 三级分类 |
| `fundAssetType` | string | 资产类别（中文简体） |
| `fundAssetTypeChs` | string | 资产类别（中文简体） |
| `fundAssetTypeCht` | string | 资产类别（中文繁体） |
| `fundAssetTypeEng` | string | 资产类别（英文） |

#### 7. 衍生品 / 涡轮 / 牛熊证 / 期权相关

| 字段 | 类型 | 说明 |
|------|------|------|
| `strikePrice` | integer | 行权价 |
| `maturityDate` | integer | 到期日 |
| `lastTradingDate` | integer | 最后交易日期 |
| `listDate` | integer | 上市日期，原始页面标注为 cbbc 相关 |
| `callPrice` | integer | 回收价 |
| `toCallPrice` | integer | 距收回价 = （相关资产最新价 - 收回价）/ 收回价 * 100% |
| `breakEvenPrice` | integer | 打和点 |
| `premium` | integer | 溢价 |
| `moneyness` | integer | 价内 / 价外 |
| `delta` | integer | 对冲值 |
| `impliedVolatility` | integer | 引伸波幅 |
| `leverageRatio` | integer | 杠杆比率 |
| `effLeverage` | integer | 有效杠杆 / 实际杠杆 = 对冲值 × 杠杆比率 |
| `entRatio` | integer | 换股比例 |
| `convertPrice` | integer | 换股价 |
| `outstandingPct` | integer | 街货占比 |
| `outstandingQty` | integer | 街货量 |
| `lowerStrike` | integer | 下限价 |
| `upperStrike` | integer | 上限价 |
| `links` | object | 标的物代码对象 |

#### 8. 其它扩展字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `prepost` | object | 美股盘前/盘后行情对象 |
| `nightQuote` | object | 夜盘行情对象 |
| `adrQuote` | object | ADR 行情对象 |
| `dualCounterQuote` | object | 双柜台行情对象 |
| `cas` | object | POS / CAS 阶段报价数据，港股特有 |

#### 扩展对象字段

##### `links`

| 字段 | 类型 | 说明 |
|------|------|------|
| `links.target` | string | 标的物代码 |

##### `cas`

| 字段 | 类型 | 说明 |
|------|------|------|
| `cas.IEP` | integer | Indicative Equilibrium Price，原始页面未中文展开 |
| `cas.IEV` | integer | Indicative Equilibrium Volume，原始页面未中文展开 |
| `cas.imbDirection` | integer | 失衡方向 |
| `cas.imbQty` | integer | 失衡数量 |
| `cas.lowerPrice` | integer | 价格下限 |
| `cas.refPrice` | integer | 参考价 |
| `cas.upperPrice` | integer | 价格上限 |

##### `prepost`

| 字段 | 类型 | 说明 |
|------|------|------|
| `prepost.price` | integer | 当前价 |
| `prepost.pClose` | integer | 昨收价 |
| `prepost.open` | integer | 开盘价 |
| `prepost.high` | integer | 最高价 |
| `prepost.low` | integer | 最低价 |
| `prepost.chgVal` | integer | 涨跌额 |
| `prepost.chgPct` | integer | 涨跌幅 `%` |
| `prepost.vol` | integer | 成交量 |
| `prepost.turnover` | integer | 成交额 |
| `prepost.qtDate` | integer | 行情日期 |
| `prepost.qtTime` | integer | 行情时间 |
| `prepost.desc` | string | 描述 |
| `prepost.type` | integer | 类型标识 |

##### `nightQuote`

| 字段 | 类型 | 说明 |
|------|------|------|
| `nightQuote.price` | integer | 当前价 |
| `nightQuote.pClose` | integer | 昨收价 |
| `nightQuote.open` | integer | 开盘价 |
| `nightQuote.high` | integer | 最高价 |
| `nightQuote.low` | integer | 最低价 |
| `nightQuote.chgVal` | integer | 涨跌额 |
| `nightQuote.chgPct` | integer | 涨跌幅 `%` |
| `nightQuote.vol` | integer | 成交量 |
| `nightQuote.turnover` | integer | 成交额 |
| `nightQuote.qtDate` | integer | 行情日期 |
| `nightQuote.qtTime` | integer | 行情时间 |
| `nightQuote.desc` | string | 描述 |

##### `adrQuote` / `dualCounterQuote`

| 字段 | 类型 | 说明 |
|------|------|------|
| `price` | integer/null | 当前价 |
| `latestClose` | integer/null | 最近收盘价 |
| `chgVal` | integer/null | 涨跌额 |
| `chgPct` | integer/null | 涨跌幅 `%` |
| `premium` | integer/null | 溢价 |
| `rawSymbol` | string/null | 证券代码 |
| `name` | string/null | 名称 |
| `mkt` | string/null | 市场 |
| `power` | integer/null | 精度基准 |
| `type` | integer/null | 类型标识 |

### 400 - 请求错误

原始页面存在 `400` 响应标签，但未展示具体返回结构。

---

## 使用示例

### cURL

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/market/secu/quote \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
  "codes": [
    "hk00700",
    "usAAPL"
  ],
  "fields": [
    "price",
    "chgPct",
    "name",
    "rawSymbol",
    "power"
  ]
}'
```

### 请求示例

```json
{
  "codes": [
    "hk00700",
    "usAAPL"
  ],
  "fields": [
    "price",
    "chgPct",
    "name",
    "rawSymbol",
    "power"
  ]
}
```

### 响应示例

```json
{
  "code": 0,
  "data": {
    "hk00700": {
      "price": 32345,
      "chgPct": 125,
      "name": "腾讯控股",
      "rawSymbol": "00700",
      "power": 2
    },
    "usAAPL": {
      "price": 21567,
      "chgPct": -84,
      "name": "Apple Inc.",
      "rawSymbol": "AAPL",
      "power": 2
    }
  },
  "message": "success",
  "requestId": "req-123456"
}
```

#### 数值还原示例

如果返回：

```json
{
  "price": 32345,
  "chgPct": 125,
  "power": 2
}
```

则可理解为：

- `price = 32345 / 10^2 = 323.45`
- `chgPct = 125 / 100 = 1.25%`

---

## 与脚本对应

当前仓库中的命令行脚本可直接调用该接口：

```bash
$FOSUN_PYTHON query_price.py quote hk00700 usAAPL
$FOSUN_PYTHON query_price.py quote hk00700 usAAPL --fields price chgPct name rawSymbol power
```

---

## 说明

- 本文档根据原始接口页面整理而成。
- 原始页面对 `fields` 的可选值没有给出完整清单，因此本文按响应字段进行归纳。
- 原始页面同时出现了港股、美股、A 股、衍生品等多个场景字段；实际返回哪些字段，取决于市场、证券品种与权限。
- 对于 `tradable`、`optStatus`、`connType`、`registration` 等未展开枚举说明的字段，本文按原文保留并做谨慎描述。
