---
name: aicoin-monitor
description: AiCoin 币圈数据监控 - 30+项数据，完全独立，可定制简报，自动存储
version: 3.0.0
author: OpenClaw
---

# aicoin-monitor - 终极币圈数据监控技能

一个功能完整的币圈数据监控工具，提供30+项数据，可生成定制简报，自动存储历史数据，完全独立可移植。

## 📊 功能清单

### 📈 行情数据
- BTC/ETH/SOL/DOGE 实时价格、涨跌幅、成交量
- 可自定义监控币种

### 📊 链上健康度
- 活跃地址数、交易笔数、平均Gas费、新增地址数
- 监控比特币网络健康状况

### 🏦 机构风向
- BTC ETF 每日流入流出
- CME 持仓量及变化
- 上市公司 BTC 持仓（MicroStrategy 等）
- 灰度溢价率

### 🌍 宏观环境
- 美元指数 DXY
- 美债收益率（2年/10年）
- 全球流动性指标
- 通胀数据（CPI/PCE）

### 📊 市场情绪
- 恐慌贪婪指数
- 社交媒体热度
- 开发者活动（GitHub提交）

### 🔥 热点叙事
- 板块轮动监控（AI/RWA/Meme/Depin 等）
- 各板块涨跌幅

### 📊 衍生品数据
- 多空比（持仓量比例）
- 多空持仓人数比
- 资金费率历史
- 清算地图（多空清算密集区）
- 爆仓数据（总额/多空占比）
- 永续合约 OI
- 期权持仓量
- DEX/CEX 交易比

### 💸 资金流向
- 交易所资金流入流出（币安/欧易/Bybit）
- 巨鲸动向（大额转账监控）
- 聪明钱地址追踪

### 📰 资讯与宏观
- 新闻快讯
- 宏观日历（美联储议息/CPI/非农等）

## 📝 可定制简报

简报内容完全通过 `config.yaml` 配置：

```yaml
# 技能目录下的 config.yaml

# 启用/禁用模块
enabled_modules:
  prices: true      # 显示行情
  onchain: false    # 不显示链上数据
  institutions: true # 显示机构数据

# 自定义顺序
module_order:
  - prices
  - institutions
  - news

# 模块级配置
module_config:
  prices:
    symbols: ['BTC', 'ETH']  # 只监控 BTC 和 ETH
  news:
    limit: 3                 # 只显示3条快讯
```

## ⚙️ 严格隔离配置说明

### ⚠️ 重要安全声明

本技能采用**严格隔离模式**：
- ✅ **绝不读取** `/root/.openclaw-zero/config.yaml` 或任何全局配置文件
- ✅ **绝不读取** 任何环境变量（包括 `AICOIN_API_KEY`、`HTTP_PROXY` 等）
- ✅ **绝不写入** `/root/.openclaw-zero/workspace/memory/` 或任何全局路径
- ✅ **所有配置** 必须来自技能目录下的 `config.yaml`
- ✅ **所有数据** 只写入技能目录下的 `data/` 文件夹

### 配置文件位置（唯一）
```
你的技能安装路径/aicoin-monitor/config.yaml
```

**如果此文件不存在，脚本将直接报错退出，不会尝试任何 fallback。**

### 验证隔离性

你可以通过以下命令验证脚本是否严格遵守隔离原则：

```bash
# 1. 将技能移动到任意位置
mv /旧路径/aicoin-monitor /新路径/

# 2. 确保配置文件存在
cp /新路径/aicoin-monitor/config.yaml.example /新路径/aicoin-monitor/config.yaml

# 3. 运行脚本
cd /新路径/aicoin-monitor/scripts/
python3 monitor.py --briefing evening

# 4. 检查数据是否只写在本地
ls /新路径/aicoin-monitor/data/briefings/  # 应该有新文件

# 5. 确认没有写入任何全局路径
find /root/.openclaw-zero -name "*aicoin*" -mmin -5  # 应该为空
```

### 完整配置示例
```yaml
# aicoin-monitor/config.yaml

aicoin:
  api_key: "你的_AccessKeyId"      # 必填，从 AiCoin 获取
  api_secret: "你的_AccessSecret"   # 必填，从 AiCoin 获取

proxy:
  http: "http://127.0.0.1:7890"    # 可选，HTTP 代理
  https: "http://127.0.0.1:7890"   # 可选，HTTPS 代理
  enabled: true                     # 可选，是否启用代理

briefing:
  enabled_modules:
    prices: true
    onchain: true
    institutions: true
    macro: true
    sentiment: true
    narratives: true
    derivatives: true
    exchange_flows: true
    whales: true
    smart_money: true
    news: true
    macro_calendar: true
  
  module_order:
    - prices
    - onchain
    - institutions
    - macro
    - sentiment
    - narratives
    - derivatives
    - exchange_flows
    - whales
    - smart_money
    - news
    - macro_calendar
  
  module_config:
    prices:
      symbols: ['BTC', 'ETH', 'SOL', 'DOGE']
    onchain:
      chains: ['bitcoin']
    institutions:
      show_etf: true
      show_cme: true
      show_corporate: true
    macro:
      show_dxy: true
      show_treasury: true
      show_inflation: true
    narratives:
      show_top: 5
    derivatives:
      symbols: ['BTC']
      show_ls_ratio: true
      show_funding: true
      show_liquidation_map: true
      show_perpetual_oi: true
      show_dex_cex_ratio: true
    exchange_flows:
      exchanges: ['binance', 'okx', 'bybit']
    whales:
      min_usd: 1000000
      limit: 3
    smart_money:
      limit: 3
    news:
      limit: 5
    macro_calendar:
      days: 7

storage:
  retention_days: 30  # 数据保留天数
  auto_clean: true    # 自动清理旧数据
```

## 💾 数据存储

### 存储位置
所有历史数据自动保存在技能目录下的 `data/` 文件夹中：
```
你的技能路径/aicoin-monitor/data/
├── prices/          # 行情数据
├── onchain/         # 链上数据
├── institutions/    # 机构数据
├── macro/           # 宏观数据
├── sentiment/       # 情绪数据
├── narratives/      # 热点叙事
├── derivatives/     # 衍生品数据
├── exchange_flows/  # 交易所资金流
├── whales/          # 巨鲸动向
├── smart_money/     # 聪明钱
├── news/            # 新闻快讯
├── macro_calendar/  # 宏观日历
└── briefings/       # 完整简报
```

### 文件命名
```
prices_2026-03-18.json          # 按日期命名
briefing_evening_2026-03-18.json # 简报包含类型
```

### 查看历史数据
```bash
# 进入技能目录
cd 你的技能路径/aicoin-monitor/

# 查看今天的行情数据
cat data/prices/prices_$(date +%Y-%m-%d).json

# 查看所有历史简报
ls -la data/briefings/
```

### 数据分析示例
```python
import json
import os
from datetime import datetime, timedelta

# 获取技能目录
skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 读取一周的行情数据
prices_data = []
for i in range(7):
    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
    filepath = os.path.join(skill_dir, 'data', 'prices', f'prices_{date}.json')
    try:
        with open(filepath) as f:
            data = json.load(f)
            prices_data.append({
                'date': date,
                'btc_price': data['data']['BTC']['price']
            })
    except:
        continue

# 分析数据
for item in prices_data:
    print(f"{item['date']}: ${item['btc_price']:,.0f}")
```

### 自动清理
- 默认保留 **30天** 的历史数据
- 可在 `config.yaml` 中修改 `storage.retention_days`
- 自动删除过期文件，避免磁盘占满

## 🚀 使用方法

### 1. 生成完整简报
```bash
cd 你的技能路径/aicoin-monitor/scripts/
python3 monitor.py --briefing evening
```

### 2. 单独查询功能
```bash
# 查询 BTC 价格
python3 monitor.py --price BTC

# 查询币安资金费率
python3 monitor.py --funding btcswapusdt:binance --interval 1h --limit 5

# 查询巨鲸动向（>$1M）
python3 monitor.py --whale --min 1000000 --limit 3

# 查看所有可用命令
python3 monitor.py --help
```

### 3. 通过包装脚本（自动设置代理）
```bash
/你的技能路径/aicoin-monitor/generate_briefing.sh --briefing evening
```

### 4. 查看配置
```bash
python3 monitor.py --config-show
```

## 🔧 依赖安装

```bash
# Python 3.8+
pip3 install requests pyyaml
```

## 📁 文件结构

```
你的技能路径/aicoin-monitor/
├── SKILL.md                 # 本文档
├── config.yaml              # 唯一配置文件（必须）
├── generate_briefing.sh     # 包装脚本
├── requirements.txt         # Python 依赖
├── data/                    # 历史数据（自动创建）
│   ├── prices/
│   ├── onchain/
│   ├── institutions/
│   ├── macro/
│   ├── sentiment/
│   ├── narratives/
│   ├── derivatives/
│   ├── exchange_flows/
│   ├── whales/
│   ├── smart_money/
│   ├── news/
│   ├── macro_calendar/
│   └── briefings/
└── scripts/
    ├── __init__.py
    └── monitor.py            # 主程序
```

## 🎯 核心原则

1. **绝不撒谎** ❌ 没有数据就不展示，写明原因
2. **完全独立** 🔒 配置只在技能目录，不依赖外部
3. **可定制** ⚙️ 通过 `config.yaml` 自由增删模块
4. **可单独查询** 🔍 30+功能都可独立调用
5. **数据存储** 💾 所有历史数据保存在技能文件夹内
6. **自动清理** 🧹 保留30天，自动删除旧数据

## 🔄 完全独立可移植

由于所有配置和数据都在技能目录内，你可以：

```bash
# 复制整个技能到新位置
cp -r /旧路径/aicoin-monitor/ /新路径/aicoin-monitor/

# 直接运行，无需任何修改
cd /新路径/aicoin-monitor/scripts/
python3 monitor.py --briefing evening

# 创建多个独立实例
cp -r aicoin-monitor/ aicoin-monitor-btc/
cp -r aicoin-monitor/ aicoin-monitor-eth/
# 分别修改各自的 config.yaml 即可

# 备份整个技能（包含所有历史数据）
tar -czf aicoin-monitor-backup.tar.gz aicoin-monitor/
```

## ❓ 常见问题

**Q: 配置文件不存在怎么办？**
A: 脚本会提示错误，并显示配置示例，按示例创建 `config.yaml` 即可。

**Q: 如何修改监控的币种？**
A: 在 `config.yaml` 中修改 `module_config.prices.symbols`。

**Q: 数据存哪里了？**
A: 都在技能目录的 `data/` 文件夹里，按类型分类。

**Q: 如何迁移到新服务器？**
A: 直接复制整个技能文件夹，所有配置和数据都跟着走。

**Q: 可以同时运行多个实例吗？**
A: 可以，复制多个文件夹，分别修改配置即可。

## 🔗 相关链接

- AiCoin 官网：https://www.aicoin.com
- API 文档：https://docs.aicoin.com
- API Key 申请：https://www.aicoin.com/zh-Hans/opendata

## 📝 更新日志

### v3.0.0 (2026-03-18)
- ✅ 30+项数据监控
- ✅ 可定制简报
- ✅ 数据自动存储
- ✅ 完全独立，配置只在技能目录
- ✅ 可移植，复制即用
- ✅ 绝不撒谎原则

---

**现在开始监控你的币圈数据吧！** 🚀