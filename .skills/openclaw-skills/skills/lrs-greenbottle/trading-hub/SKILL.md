---
name: trading-hub
description: 统一交易技能中心 - BTC/ETH/SOL/A股/美股/外汇/期货。包含技术分析、仓位管理、警报系统、回测、舆情分析、情绪监控、主动扫描、自动进化。【触发词】分析BTC/分析A股/查持仓/查仓位/开仓/平仓/止损/止盈/交易/炒币/买币
version: 5.3.0
author: 小绿瓶
tags:
  - trading
  - crypto
  - bitcoin
  - astock
  - usstock
  - Binance
  - trading-hub
metadata:
  openclaw:
    emoji: "🫙"
    autonomous: true
---

# Trading Hub v5.2.0 🫙✨
# 主动型赚钱缝合兽

**会学习 · 会赚钱 · 会反思 · 会进化**

---

## 📚 学习成果 (2026-03-21 13:51)

### 🧬 ClawHub 扫描结果

| 技能 | 版本 | 价值 | 状态 |
|------|------|------|------|
| quant-trading-system | v6.0.0 | 多策略投票系统（10+策略） | ✅ 已在库 |
| crypto-self-learning | v1.0.0 | 自进化交易日志，自动更新规则 | ✅ 已在库 |
| trading-brain | v1.0.0 | Next-Wave 3-Act框架 + 1%风控 | ✅ 已在库 |
| polymarket-trader | - | Polymarket延迟套利策略 | ✅ 已在库 |

> ⚠️ ClawHub 主站当前不可访问，以上为本地已缝合技能记录

### 当前市场快照（Kraken API）

| 品种 | 价格 | 24h涨跌 |
|------|------|---------|
| BTC | $70,702 | +0.26% |
| ETH | $2,155 | +0.42% |
| SOL | $90.6 | +0.85% |

**观察**：BTC 在 $69,400-$70,800 区间震荡，多策略投票结果：全策略HOLD，无明确信号。

### 本次新增学习
1. **Kraken API** 作为 Binance 备选数据源（已测试可用）
2. **Next-Wave 候选板块**：人形机器人零部件、网络安全、美国以外AI基础设施建设
3. **问题发现**：Binance API 全面受限，需接入多数据源

### v5.3.0 任务重构 (2026-03-21)
- **合并进化任务**：每周进化合并到每日总结，每天22:00汇报
- **精简学习任务**：learn 专注大佬策略+案例，不搜ClawHub
- **删除冗余**：`trading-hub_evolve` 已移除
- 当前5个定时任务：仓位监控/主动扫描/情绪早报/自主学习/每日总结

### 模拟训练进度
- Day 1/7 | 交易 1/20 笔 | 胜率 0% | 浮盈 +$1.9
- ⚠️ 需加速交易频率，目标：剩余6天完成19笔，胜率≥50%

---

## 🚀 六大核心能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 主动设立任务 | ✅ | 自动注册5种定时任务 |
| 主动学习知识 | ✅ | 每4小时自动学习大佬策略+案例 |
| 主动总结 | ✅ | 每日22点生成日报（含进化成果） |
| 主动改进策略 | ✅ | 根据交易结果调整 |
| 跨技能协同 | ✅ | 与A股/美股技能联动 |

---

## 决策树

```
触发场景
  ├─ 查询持仓/交易 → 执行对应脚本
  ├─ 定时任务触发
  │   ├─ 每1分钟仓位监控 → 触发止损/止盈/持仓/平仓 → 汇报
  │   ├─ 每30分钟主动扫描市场和技术分析 → 信号BUY/SELL → 发现机会 → 自行判断持仓/设置止损止盈 → 触发止损/止盈/持仓/平仓 → 汇报
  │   ├─ 每4小时自主学习圈内大佬策略+成功案例
  │   ├─ 每日9点 → 市场情绪 + 昨日交易回顾总结 → 生成分析汇报
  │   └─ 每日22点 → 交易总结（含ClawHub扫描缝合+今日学习进化成果）
```

## 🤖 自动运行的任务

| 任务 | 频率 | 职责 | delivery |
|------|------|------|----------|
| 🏓 仓位监控 | 每1分钟 | 触发止损/止盈/持仓/平仓时汇报，无操作静默 | `none` |
| 🔍 主动扫描 | 每30分钟 | 信号BUY/SELL→自行判断持仓/设置止损止盈→触发操作才汇报 | `none` |
| 🌡️ 市场情绪 | 每天09:00 | 市场情绪分析+昨日回顾总结，生成早报汇报 | `announce(feishu)` |
| 📚 自主学习 | 每4小时 | 大佬交易策略分析+成功案例，记录到 .learnings/，有重要心得时汇报 | `announce(feishu)` |
| 📋 每日总结 | 每天22:00 | 交易日志+ClawHub扫描+今日进化+主动问主人"有什么可以主动做"，生成日报汇报主人 | `announce(feishu)` |

---

## 🚀 安装定时任务

安装后说"配置技能"，我会自动执行以下命令注册定时任务：

```bash
# 仓位监控（每分钟）
openclaw cron add --name "trading-hub_monitor" --cron "* * * * *" --session isolated --wake now --deliver none --message "执行 trading-hub 仓位监控：运行 btc_monitor.py 检查持仓，触发止损/止盈/持仓/平仓时主动发消息汇报主人，无操作则静默不汇报。"

# 主动扫描（每30分钟）
openclaw cron add --name "trading-hub_analysis" --cron "*/30 * * * *" --session isolated --wake now --deliver none --message "执行 trading-hub 每30分钟主动扫描：运行 crypto_scanner.py 扫描市场+技术分析，信号BUY/SELL时自行判断是否持仓/设置止损止盈，触发止损/止盈/持仓/平仓时主动发消息汇报主人，无操作则静默不汇报。"

# 自主学习（每4小时）
openclaw cron add --name "trading-hub_learn" --cron "0 */4 * * *" --session isolated --wake now --deliver announce --channel feishu --message "执行 trading-hub 自主学习：分析圈内大佬交易策略，学习成功案例，记录到 .learnings/ 和 skills/trading-hub/references/，有重要心得时主动汇报主人。"

# 市场情绪（每天09:00）
openclaw cron add --name "trading-hub_sentiment" --cron "0 9 * * *" --session isolated --wake now --deliver announce --channel feishu --message "执行 trading-hub 市场情绪分析：运行 sentiment.py 分析A股和加密市场情绪，同时回顾昨日交易记录生成总结，生成早报（含市场情绪+昨日交易回顾）汇报给主人。"

# 每日总结（每天22:00）
openclaw cron add --name "trading-hub_summary" --cron "0 22 * * *" --session isolated --wake now --deliver announce --channel feishu --message "执行 trading-hub 每日交易总结：1) 运行交易日志分析，统计今日盈亏；2) 搜索ClawHub交易类新技能，评估是否有价值值得缝合，有则更新技能文档；3) 汇总今日自主学习的大佬策略心得和进化成果；4) 主动问主人：有什么我可以主动做的吗？生成交易日报（含交易记录+ClawHub扫描结果+今日学习进化总结+主动询问）推送给主人。"
```

---

## 🎯 主动交易策略

### 交易信号类型

| 信号 | 说明 | 操作 |
|------|------|------|
| 超跌反弹 | RSI日线超卖 + 跌幅收窄 | 买涨 |
| 回踩支撑 | 价格回踩EMA20/EMA60 | 买涨 |
| MACD金叉 | 小时级别MACD交叉 | 买涨 |
| 强势突破 | RSI超买 + 放量 | 追涨 |
| 反弹做空 | 日线空头 + RSI反弹 | 买跌 |

### 风险控制

- 单笔最大亏损: **1%**（来自 trading-brain，更严格）
- 每日最大回撤: **3%**，达到停止交易
- 止损: 通常2-5%
- 止盈: 通常5-10%
- 风险回报比: 至少1:2
- 最多同时持仓: **5个**（单仓位不超过组合20%）

### 仓位管理

- 单笔不超过模拟账户20%
- 同时持仓不超过3个币种
- 止损触发立即平仓

---

## 📊 支持市场

| 市场 | 品种 | 数据源 |
|------|------|--------|
| 加密货币 | BTC/ETH/SOL等15+币种 | Binance API（主动扫描） |
| A股 | 全市场 | 集思录 |
| 美股 | 热门股 | 股票分析模块 |
| 外汇 | 主要货币对 | 公开数据 |
| 期货 | 商品期货 | 公开数据 |

---

## 🛠️ 核心脚本

| 脚本 | 功能 |
|------|------|
| `binance_api.py` | Binance统一API（现货/合约/杠杆） |
| `mock_trade.py` | **模拟交易系统**（隔离真实资金） |
| `trade.py` | 统一交易入口（支持mock/real切换） |
| `crypto_scanner.py` | **主动市场扫描**（发现交易机会） |
| `auto_trader.py` | **自动交易引擎**（扫描+下单+追踪一体化） |
| `btc_analyzer.py` | BTC技术分析（EMA/RSI/MACD/布林带） |
| `btc_monitor.py` | 多币种仓位监控 |
| `astock.py` | A股情绪分析 |
| `position_manager.py` | 统一仓位管理 |
| `alerts.py` | 价格警报系统 |
| `sentiment.py` | 市场舆情分析 |
| `backtest.py` | 策略回测 |
| `analyze_stock.py` | 股票深度分析 |
| `dividends.py` | 股息分析 |
| `hot_scanner.py` | 热门股票扫描 |
| `rumor_scanner.py` | 消息扫描 |
| `portfolio.py` | 投资组合管理 |
| `watchlist.py` | 自选股监控 |
| `whale_tracker.py` | 鲸鱼追踪（订单簿+大单监控） |

---

## 🎯 交易模式

| 模式 | 说明 | 命令 |
|------|------|------|
| **mock** | 模拟交易，$1,000虚拟资金 | `python3 trade.py mode mock` |
| **real** | 真实交易，真实资金 | `python3 trade.py mode real` |

### 模拟交易流程

```
1. 切换到模拟模式: trade.py mode mock
2. 买入: trade.py buy BTC 1000
3. 查看状态: trade.py status
4. 交易历史: trade.py history
5. 盈亏统计: trade.py profit
6. 重置账户: trade.py reset
```

### 模拟训练计划（1周）

| 天数 | 目标 |
|------|------|
| Day 1-2 | 熟悉交易命令，执行5-10笔模拟单 |
| Day 3-4 | 测试止盈止损策略 |
| Day 5-6 | 尝试不同策略（趋势/网格/布林带） |
| Day 7 | 复盘总结，评估是否可切换真实交易 |

**切换真实交易条件：**
- 模拟账户盈利 ≥ 5%
- 交易记录 ≥ 20笔
- 胜率 ≥ 50%

---

## 📁 数据文件

| 文件 | 用途 |
|------|------|
| `data/positions.json` | 持仓状态 |
| `data/trade_log.json` | 交易日志 |
| `data/alerts.json` | 警报配置 |
| `data/scheduler_tasks.json` | 任务注册表 |
| `data/simulation_plan.json` | **模拟训练计划** |
| `auto_trades.json` | **自动交易记录** |
| `auto_config.json` | **自动交易配置** |
| `references/` | **策略参考文档**（Polymarket策略、Next-Wave框架、多策略投票、自进化日志） |

---

## 🔄 跨技能协同

当检测到以下情况时，自动协同：

```
BTC大涨 → 检查是否影响A股情绪 → 调整仓位建议
A股冰点 → 自动降低仓位 → 记录到交易日志
发现机会 → 生成分析报告 → 通知主人
```

---

## 🧬 自动进化机制

1. **每周自动搜索** ClawHub 交易类新技能
2. **评估缝合价值**（功能是否独特/重复）
3. **执行缝合**（合并到对应模块）
4. **更新文档**（记录进化历程）
5. **汇报结果**（告诉主人学到了什么）

### 本次进化发现的新技能
- **quant-trading-system**: 10+策略库 + 多策略投票 → 可改进 crypto_scanner.py
- **crypto-self-learning**: 自进化日志系统 → 缝合到 auto_trade.py 日志格式
- **trading-brain**: Next-Wave框架 + 1%风控 → 已缝合到 references/
- **trading-devbox**: 自然语言回测沙盒 → 未来可集成

---

## 🏃‍♂️ 初始化命令

技能首次加载后自动执行：
```bash
python3 skills/_core/autonomous.py register trading-hub trading
```

---

## 🙏 致谢

缝合自：
- binance-pro, binance-spot-trader, btc-analyzer, btc-position-monitor
- btc-trading-assistant, position-management, stock-analysis, stock-watcher

---

**版本：v5.2.0 | 作者：小绿瓶 | 🫙✨**
