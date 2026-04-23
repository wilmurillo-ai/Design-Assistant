---
name: stockapi
description: 通过 www.stockAPI.com.cn 查询中国 A 股市场数据。获取日 K 线、实时行情、技术指标（MACD、KDJ、BOLL 等）、涨跌停个股、龙虎榜、游资数据。当用户询问股价、市场数据、技术分析或 A 股市场相关信息时调用。需要使用 STOCKAPI_TOKEN 环境变量。
---

# StockAPI Skill

通过 StockAPI 查询中国 A 股市场数据。支持股票日线、实时行情、技术指标、涨停跌停、龙虎榜、游资数据等。

## 配置

### 设置 Token（必需）

在使用前必须设置 `STOCKAPI_TOKEN` 环境变量：

```bash
# Linux/Mac
export STOCKAPI_TOKEN='your_token_here'

# Windows (PowerShell)
$env:STOCKAPI_TOKEN="your_token_here"

# Windows (CMD)
set STOCKAPI_TOKEN=your_token_here
```

**获取 Token：**
1. 访问 https://www.stockapi.com.cn 注册账号
2. 登录后在个人中心获取 API Token
3. Token 是免费的，但有调用频率限制

### 验证配置

```bash
cd /home/admin/openclaw/workspace/skills/stockapi
python3 scripts/stockapi.py test
```

## 快速使用

### 查询股票日线数据

```bash
python3 scripts/stockapi.py stock daily --code 600004 --start-date 2024-01-01 --end-date 2024-01-10
```

### 查询实时行情

```bash
python3 scripts/stockapi.py stock quote --code 000001
```

### 查询涨停股票

```bash
python3 scripts/stockapi.py limit up
```

### 查询技术指标（MACD）

```bash
python3 scripts/stockapi.py indicator macd --code 600004 --start-date 2024-01-01 --end-date 2024-01-10
```

## 命令参考

### 股票数据 (stock)

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `stock daily` | 日线 K 线数据 | --code, --start-date, --end-date |
| `stock quote` | 实时行情 | --code |

### 指数数据 (index)

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `index daily` | 指数日线 | --code, --start-date, --end-date |

### 涨跌停 (limit)

| 命令 | 说明 | 参数 |
|------|------|------|
| `limit up` | 涨停池 | --date (可选，默认今天) |
| `limit down` | 跌停池 | --date (可选，默认今天) |

### 龙虎榜/游资

| 命令 | 说明 | 参数 |
|------|------|------|
| `dragon` | 龙虎榜 | --date (可选) |
| `hotmoney` | 游资数据 | --date (可选) |

### 技术指标 (indicator)

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `indicator macd` | MACD 指标 | --code, --start-date, --end-date |
| `indicator kdj` | KDJ 指标 | --code, --start-date, --end-date |

### 输出格式

```bash
# JSON 格式（默认）
python3 scripts/stockapi.py stock quote --code 600004 --format json

# 表格格式
python3 scripts/stockapi.py stock daily --code 600004 --start-date 2024-01-01 --end-date 2024-01-10 --format table
```

## 常见使用场景

### 1. 查询某股票近期走势

```bash
python3 scripts/stockapi.py stock daily \
  --code 600004 \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

### 2. 查看今天涨停的股票

```bash
python3 scripts/stockapi.py limit up
```

### 3. 分析股票技术指标

```bash
# MACD
python3 scripts/stockapi.py indicator macd \
  --code 000001 \
  --start-date 2024-01-01 \
  --end-date 2024-01-31

# KDJ
python3 scripts/stockapi.py indicator kdj \
  --code 000001 \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

### 4. 查看龙虎榜数据

```bash
python3 scripts/stockapi.py dragon --date 2024-01-15
```

### 5. 追踪游资动向

```bash
python3 scripts/stockapi.py hotmoney --date 2024-01-15
```

## 股票代码格式

- **上交所 A 股**：6 开头（如 `600004` 南方航空）
- **深交所主板**：0 开头（如 `000001` 平安银行）
- **深交所中小板**：2 开头（如 `002001`）
- **创业板**：3 开头（如 `300001` 特锐德）
- **指数**：具体代码（如 `000001` 上证指数）

## 常见问题

### Token 错误

```
Error: STOCKAPI_TOKEN not set
```

**解决：** 确保已设置环境变量：
```bash
export STOCKAPI_TOKEN='your_token'
```

### API 请求失败

检查：
1. Token 是否正确
2. 网络连接是否正常
3. 股票代码格式是否正确
4. 日期格式是否为 YYYY-MM-DD

### 数据为空

可能原因：
- 日期范围无交易数据（周末/节假日）
- 股票代码不存在
- API 服务暂时不可用

## 更多资源

- **详细 API 文档**：见 `references/api-docs.md`
- **官方网站**：https://www.stockapi.com.cn
- **API 示例**：https://www.stockapi.com.cn/demo

## 注意事项

1. **数据延迟**：实时数据可能有 15 分钟延迟
2. **调用频率**：免费 Token 有调用次数限制
3. **投资风险提示**：数据仅供参考，不构成投资建议
4. **Token 安全**：不要将 Token 提交到代码仓库
