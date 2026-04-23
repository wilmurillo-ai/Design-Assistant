---
name: macro-monitor
version: 0.1.0
description: 宏观数据抓取工具，整合 Alpha Vantage、Tushare 与 Stooq 备用源，只输出原始数据。
trigger_patterns:
  - 宏观数据抓取
  - macro monitor
  - 获取宏观数据
  - 汇率和美债数据
  - 中国宏观指标
---

# 宏观数据抓取

`macro-monitor` 现在只负责数据获取与聚合，不再包含分析、波动率计算或文本报告生成。

## 数据源

| 数据源 | 数据类型 | 优先级 |
|--------|----------|--------|
| Alpha Vantage | USD/CNY、美债收益率、BTC、WTI、天然气 | P0 |
| Tushare | 中国 CPI、PPI、社融、PMI | P0 |
| Stooq | BTC、黄金、WTI、天然气、纳指期货 | P1（备用） |

## 使用方式

### 获取全部数据

```python
from macro_monitor import MacroDataMonitor

monitor = MacroDataMonitor()
data = monitor.get_all_data()
print(data)
```

### 调用原子化抓取方法

```python
monitor = MacroDataMonitor()

fx_data = monitor.fetch_fx_data()
us_rates = monitor.fetch_us_rates_data()
crypto_data = monitor.fetch_crypto_data()
energy_data = monitor.fetch_energy_data()
china_macro = monitor.fetch_china_macro_data()
backup_market = monitor.fetch_backup_market_data()
```

### 只抓市场数据

```python
market_data = monitor.fetch_market_data()
```

### 强制使用备用源

```python
market_data = monitor.fetch_market_data(use_backup=True)
```

## 输出格式

### `get_all_data()`

```python
{
    "timestamp": "2026-03-28 12:00:00",
    "sources": {
        "alpha_vantage": "OK",
        "tushare": "OK"
    },
    "data": {
        "USD_CNY": 7.24,
        "US_TREASURY_10Y": 4.25,
        "BTC": 67245.0,
        "WTI": 81.45,
        "NATURAL_GAS": 2.85,
        "CHINA_MACRO": {
            "CPI": {"value": 0.7, "yoy": 0.7, "date": "202502"}
        }
    }
}
```

## 环境变量

```bash
export ALPHAVANTAGE_API_KEY="your_alphavantage_key"
export TUSHARE_TOKEN="your_tushare_token"
```

## 依赖

```bash
pip3 install requests pandas tushare
```
