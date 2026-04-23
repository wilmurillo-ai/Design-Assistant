---
name: crypto-monitor-v9
version: 3.0.0
description: V9多时间框架交易系统 - BTC/ETH专业分析 + EMA12小级别趋势 + 入场评分系统
author: dengqishen76
triggers:
  - "分析BTC"
  - "分析ETH"
  - "BTC走势"
  - "做空分析"
  - "V9策略"
  - "入场评分"
metadata:
  openclaw:
    requires:
      bins: ["openclaw"]
    emoji: "📊📈🧠"
    category: "crypto-trading"
---

# V9 多时间框架交易系统

## 核心功能

### 1. V9 多时间框架分析
- 4H Vega过滤 (最高优先级)
- 1H EMA144确认
- 15M结构确认 (HH/HL)

### 2. EMA12 小级别趋势模型
- EMA12穿越EMA144/169
- 回测胜率 82.6%
- 金叉做多，死叉做空

### 3. 入场评分系统 (9分制)
| 条件 | 分数 |
|------|------|
| 4H趋势 | +2 |
| 1H回踩 | +2 |
| EMA12穿越 | +2 |
| ADX>25 | +1 |
| 结构HL/LH | +2 |

- ≥7分 → 强烈开仓
- 5-6分 → 轻仓尝试
- <5分 → 禁止

### 4. 多因子量化模型 (100分制)
- 技术面 50%
- 宏观面 20%
- 链上面 15%
- 情绪面 15%

### 5. 直觉交易系统
- 9条学习直觉
- 自动模式识别

## 技术指标
- RSI (4H/1H)
- 布林带 (BB)
- ATR (波动率)
- EMA 12/50/100/144/169

## 宏观数据
- DXY 美元指数 (FRED)
- VIX 恐慌指数
- FED利率

## 禁止规则
- 禁止日内交易 (中长线)
- 禁止逆趋势
- VIX>25 禁止交易
- ADX<20 禁止交易

## 使用方法
输入"分析BTC" / "分析ETH" / "BTC走势"
