# StockAPI 参考文档

StockAPI 是国内领先的股票数据服务提供商，提供 A 股市场的实时行情、深度数据和专业技术指标。

## 官方文档

- 网站：https://www.stockapi.com.cn
- API 文档：https://www.stockapi.com.cn/demo

## 获取 Token

1. 访问 https://www.stockapi.com.cn 注册账号
2. 登录后在个人中心获取 API Token
3. 将 Token 设置为环境变量：`export STOCKAPI_TOKEN='your_token'`

## API 基础信息

- 基础 URL: `https://www.stockapi.com.cn`
- 请求方式：GET
- 返回格式：JSON
- 必需参数：`token` (API 访问令牌)

## 主要数据类别

### 1. 基础数据

| 接口 | 路径 | 说明 |
|------|------|------|
| 股票日线 | `/v1/base/day` | K 线数据（开盘、收盘、最高、最低、成交量等） |
| 实时行情 | `/v1/base/quote` | 实时报价数据 |
| 股票列表 | `/v1/base/stockList` | 全部 A 股列表 |
| 指数日线 | `/v1/index/day` | 指数 K 线数据 |

### 2. 技术指标

| 指标 | 路径 | 说明 |
|------|------|------|
| MACD | `/v1/indicator/macd` | 平滑异同移动平均线 |
| KDJ | `/v1/indicator/kdj` | 随机指标 |
| BOLL | `/v1/indicator/boll` | 布林线指标 |
| CCI | `/v1/indicator/cci` | 顺势指标 |
| WR | `/v1/indicator/wr` | 威廉指标 |
| RSI | `/v1/indicator/rsi` | 相对强弱指标 |
| BIAS | `/v1/indicator/bias` | 乖离率指标 |
| 神奇九转 | `/v1/indicator/magic9` | 神奇九转指标 |

### 3. 特色数据

| 数据 | 路径 | 说明 |
|------|------|------|
| 涨停池 | `/v1/limit/limitUp` | 当日涨停股票列表 |
| 跌停池 | `/v1/limit/limitDown` | 当日跌停股票列表 |
| 炸板池 | `/v1/limit/broken` | 炸板股票列表 |
| 龙虎榜 | `/v1/dragon/list` | 龙虎榜数据 |
| 游资数据 | `/v1/hotmoney/list` | 游资交割单数据 |
| 排行榜 | `/v1/rank/list` | 股票排行榜 |

### 4. 实时数据

| 数据 | 路径 | 说明 |
|------|------|------|
| 逐笔成交 | `/v1/realtime/deal` | 实时逐笔成交数据 |
| 分时成交 | `/v1/realtime/timeShare` | 分时成交量数据 |
| 历史逐笔 | `/v1/realtime/historyDeal` | 历史逐笔成交 |
| 历史分时 | `/v1/realtime/historyTimeShare` | 历史分时成交量 |

## 通用请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token | string | 是 | API 访问令牌 |
| code | string | 通常 | 股票代码（如：600004） |
| startDate | string | 通常 | 开始日期（YYYY-MM-DD） |
| endDate | string | 通常 | 结束日期（YYYY-MM-DD） |
| date | string | 有时 | 指定日期（YYYY-MM-DD） |
| calculationCycle | int | 否 | 计算周期 |

## 响应格式

成功响应：
```json
{
  "code": 200,
  "msg": "success",
  "data": [...]
}
```

错误响应：
```json
{
  "code": 60048,
  "msg": "亲！您传入的 token 不存在，请检查 token 是否正确"
}
```

## 常见错误码

| 错误码 | 说明 |
|--------|------|
| 60048 | Token 不存在或错误 |
| 400 | 参数错误 |
| 401 | 未授权 |
| 429 | 请求频率超限 |
| 500 | 服务器错误 |

## 使用注意事项

1. **Token 安全**：不要将 Token 提交到代码仓库，使用环境变量
2. **请求频率**：注意 API 调用频率限制，避免被封禁
3. **数据延迟**：实时数据可能有 15 分钟延迟
4. **股票代码**：
   - 上交所：6 开头（如 600004）
   - 深交所：0/2/3 开头（如 000001、200001、300001）
5. **日期格式**：必须使用 `YYYY-MM-DD` 格式

## 示例请求

### Python 示例
```python
import requests

BASE_URL = "https://www.stockapi.com.cn/v1/base/day"
TOKEN = "your_token"

params = {
    "token": TOKEN,
    "code": "600004",
    "startDate": "2024-01-01",
    "endDate": "2024-01-10"
}

response = requests.get(BASE_URL, params=params)
data = response.json()
print(data)
```

### curl 示例
```bash
curl "https://www.stockapi.com.cn/v1/base/day?token=YOUR_TOKEN&code=600004&startDate=2024-01-01&endDate=2024-01-10"
```
