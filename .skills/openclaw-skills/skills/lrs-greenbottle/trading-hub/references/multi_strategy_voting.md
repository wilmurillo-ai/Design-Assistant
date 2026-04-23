# 多策略投票系统
## 缝合自 quant-trading-system (v6.0.0)

**来源**: ClawHub quant-trading-system | **作者**: pikachu022700 | **缝合**: 小绿瓶
**时间**: 2026-03-21

---

## 核心理念

**不依赖单一策略，用多个策略投票决定方向。**

单个策略有偏见、有盲点。多策略投票可以：
- 减少假信号
- 捕捉不同时间维度的机会
- 适应不同市场环境

---

## 策略库（10+ 策略）

| 策略 | 逻辑 | 适合市场 |
|------|------|---------|
| momentum | RSI < 35 → LONG, RSI > 65 → SHORT | 趋势市场 |
| mean_reversion | RSI < 30 → LONG, RSI > 70 → SHORT | 震荡市场 |
| breakout | 价格 > 20日高点 → LONG | 突破行情 |
| macd_cross | MACD直方图 > 0 → LONG | 趋势市场 |
| supertrend | 价格 > MA20 → LONG | 趋势市场 |
| rsi_extreme | RSI < 25 → LONG, RSI > 75 → SHORT | 极端行情 |
| bollinger_bounce | 价格 < 布林下轨 → LONG | 震荡市场 |
| trend_following | MA5 > MA20 → LONG | 趋势市场 |
| volatility_breakout | ATR > 1.5倍均值 → LONG | 波动放大 |
| ai_hybrid | RSI < 40 + MACD > 0 → LONG | 多条件共振 |

---

## 投票机制

```
所有启用策略各自投票：
- LONG: +1
- HOLD: 0
- SHORT: -1

最终信号 = 简单相加：
- 总分 > 0 → LONG（多数看多）
- 总分 < 0 → SHORT（多数看空）
- 总分 = 0 → HOLD（分歧大，不操作）
```

---

## 与小绿瓶融合

### 改进 crypto_scanner.py

当前扫描器是单策略决定。可以改造为：

```python
# 多策略扫描
strategies = ["momentum", "macd_cross", "rsi_extreme", "bollinger_bounce"]
votes = {"LONG": 0, "SHORT": 0, "HOLD": 0}

for strat in strategies:
    signal = run_strategy(strat, factors)
    votes[signal] += 1

# 多数票决定
if votes["LONG"] >= 3:  # 至少3个策略同意
    final_signal = "BUY"
elif votes["SHORT"] >= 3:
    final_signal = "SELL"
else:
    final_signal = "HOLD"
```

### 改进止损/止盈

来自 quant-trading-system：
- 止损: 5%
- 止盈: 10%
- 风险回报比: 至少 1:2

---

## Dashboard（可选扩展）

quant-trading-system 提供了一个本地 dashboard：
- `/status` - 组合状态
- `/strategies` - 策略列表

未来可考虑集成到小绿瓶 Web 界面。

---

## 缝合价值

| 价值点 | 说明 |
|--------|------|
| ✅ 多策略互补 | 不同策略覆盖不同市场环境 |
| ✅ 减少假信号 | 单一RSI超卖可能假信号，3个策略同时信号更可靠 |
| ✅ 易于扩展 | 新策略只需添加到库中 |
| ⚠️ 计算成本 | 多策略同时计算，约增加30%时间 |

**结论**：值得缝合到 `crypto_scanner.py` 中，作为信号确认机制。
