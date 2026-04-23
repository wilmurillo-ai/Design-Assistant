# Polymarket BTC 1h Up/Down 交易策略
## 缝合自 polymarket-trader 技能

**作者**: drakec48 | **版本**: 1.0.0 | **缝合**: 小绿瓶

---

## 核心原理

Polymarket 上的 BTC 1h Up/Down 市场通过 **Binance BTCUSDT 1H K线** 结算：
- 结算规则：收盘价 vs 开盘价
- 我们使用 Binance 作为唯一真实信号源

---

## 公平概率模型

### 输入参数
- `open_px`: Binance 1H K线开盘价
- `spot`: 当前 BTCUSDT 现货价格
- `sigma_1m`: 1分钟收益率的标准差（回溯窗口 30-60 分钟）
- `minutes_left`: 剩余分钟数

### 计算公式
```
cur_ret = (spot - open_px) / open_px
stdev = sigma_1m × √(minutes_left)
z = cur_ret / stdev
p_up = Φ(z)  # 标准正态分布CDF

fair_up = p_up
fair_down = 1 - p_up
```

### 解读
- `|z|` 代表置信度
- |z| 很大 → 剩余时间不太可能翻转方向
- |z| 很小 → 方向不确定

---

## 边缘计算（Edge / 套利机会）

```
edge_up = fair_up - price_up
edge_down = fair_down - price_down
```

**入场条件**：最佳边缘超过阈值
- `EDGE_MIN`（初始值 ≈ 0.06，可调整）

---

## 强制护栏（Directional Guardrails）

### 方向护栏
如果 `|z| >= z_guard`（初始值 0.25）：
- 如果 `z > 0`：不能做空（不做 Down）
- 如果 `z < 0`：不能做多（不做 Up）

**原理**：不要逆着大趋势赌

### 交易频率控制
- 每个市场最大交易次数：`MAX_TRADES_PER_MARKET`（初始值 1-2）
- 退出后加入冷却期；止损后冷却期更长

---

## 退出管理

### 模型入场（趋势跟随）
- **持有到预收盘**：如果置信度极高且方向一致
  - 做多：`z >= Z_HOLD`（初始值 2.5）
  - 做空：`z <= -Z_HOLD`

- **否则**：使用边缘退出
  - 止盈：如果市场报价 >= `fair + EDGE_EXIT`
  - 止损：如果模型实质性翻转（fair 穿越 0.5 - margin）

### 均值回归入场
- **不要使用** `model_tp`
- 仅使用：止盈目标 / 追踪止损 / 区间翻转止损

---

## 调参检查清单

| 参数 | 初始值 | 调整方向 |
|------|--------|----------|
| `EDGE_MIN` | 0.06 | 如果过度交易 → 提高 |
| `z_guard` | 0.25 | 如果逆势交易 → 提高 |
| `Z_HOLD` | 2.5 | 如果持有太早 → 提高 |

---

## 与小绿瓶策略融合

这个策略非常适合 Polymarket 延迟套利：
1. **监控 Polymarket 价格偏差**：当市场定价与公平概率偏差 > 6% 时
2. **使用 Binance 信号验证**：不与 Binance 1H 信号对抗
3. **方向护栏避免被洗**：大趋势明确时不逆势

---

## 参考脚本

| 脚本 | 用途 |
|------|------|
| `binance_klines.py` | 获取 Binance K线数据 |
| `binance_regime.py` | 计算趋势/区间状态 |
| `explain_fills.py` | 分析历史交易记录 |

---

## 数学附录

### 标准正态分布 CDF（Python实现）
```python
import math
def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / (2.0**0.5)))
```

### 1分钟实现波动率
```python
import math
def realized_sigma_1m(closes):
    if len(closes) < 3:
        return None
    rets = []
    for a, b in zip(closes[:-1], closes[1:]):
        if a <= 0:
            continue
        rets.append((b - a) / a)
    if len(rets) < 3:
        return None
    mu = sum(rets) / len(rets)
    var = sum((x - mu) ** 2 for x in rets) / (len(rets) - 1)
    return var ** 0.5
```
