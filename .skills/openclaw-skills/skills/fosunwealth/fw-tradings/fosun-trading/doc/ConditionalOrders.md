# 条件单说明

> 本文专门整理交易里常见的几类条件单，重点说明它们各自的含义、触发方式、必填参数和典型示例。
>
> 这里讨论的主要是以下 4 类：
> - `stop_loss_limit(31)` 止损限价单
> - `take_profit_limit(32)` 止盈限价单
> - `trailing_stop(33)` 跟踪止损单
> - `take_profit_stop_loss(35)` 止盈止损组合单

---

## 1. 先看核心概念

条件单和普通限价单最大的区别是：

- 普通限价单：提交后立刻进入市场排队。
- 条件单：先等待条件满足，条件被触发后，系统才会真正提交委托。

对条件单来说，最容易混淆的是下面两类价格：

- `trigPrice`：触发价，决定“什么时候触发”
- `price`：委托价，决定“触发后按什么价格报出”

因此：

- 条件单不是“到了 `price` 就成交”
- 条件单通常是“先看 `trigPrice` 是否满足，满足后再按 `price` 发出限价委托”

---

## 2. 几类条件单的区别

| 订单类型 | 含义 | 什么时候触发 | 触发后做什么 | 常见用途 |
|----------|------|--------------|--------------|----------|
| `stop_loss_limit(31)` | 止损限价单 | 到达止损触发条件时 | 按 `price` 发出限价单 | 止损卖出、突破买入 |
| `take_profit_limit(32)` | 止盈限价单 | 到达止盈触发条件时 | 按 `price` 发出限价单 | 止盈卖出、回落买入 |
| `trailing_stop(33)` | 跟踪止损单 | 市场价相对高/低点回撤到设定幅度时 | 提交对应委托 | 跟随行情动态保护利润 |
| `take_profit_stop_loss(35)` | 止盈止损组合单 | 止盈条件或止损条件任一触发 | 提交一侧委托并撤销另一侧 | 同时挂止盈和止损 |

---

## 3. 止损限价单 `stop_loss_limit(31)`

### 含义

止损限价单是一种“先触发、后报单”的条件单。

- 卖出方向下：通常表示“跌到某个价格后止损卖出”
- 买入方向下：通常表示“涨到某个价格后触发买入”，常用于突破追价

### 必填参数

- `--order-type stop_loss_limit`
- `--price`
- `--trig-price`

### 参数理解

- `--trig-price`：触发价
- `--price`：触发后真正提交的限价委托价

常见理解：

- 卖出止损时，`price` 往往会略低于 `trig-price`，这样触发后更容易成交
- 买入突破时，`trig-price` 通常高于当前市价

### 示例 1：港股卖出止损

场景：

- 你持有腾讯 `00700`
- 当前价格大约 `386`
- 希望跌到 `385.000` 时启动止损
- 真正发出去的卖单价格设为 `380.000`

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction sell --quantity 100 --order-type stop_loss_limit --price 380.000 --trig-price 385.000
```

解释：

- 市场先观察是否跌到 `385.000`
- 一旦触发，系统再按 `380.000` 发出限价卖单

### 示例 2：美股突破买入

场景：

- 你想等 `AAPL` 向上突破后再追价买入
- 当前股价低于 `176.00`
- 当价格涨到 `176.00` 时触发
- 触发后按 `176.20` 报买单

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction buy --quantity 5 --order-type stop_loss_limit --price 176.20 --trig-price 176.00
```

解释：

- 这不是“低价买入”单
- 这是“突破后跟进”的条件单

---

## 4. 止盈限价单 `take_profit_limit(32)`

### 含义

止盈限价单同样是“先触发、后报单”的条件单。

- 卖出方向下：通常表示“涨到某个价格后止盈卖出”
- 买入方向下：通常表示“跌到某个价格后触发买入”，常用于回落承接

### 必填参数

- `--order-type take_profit_limit`
- `--price`
- `--trig-price`

### 参数理解

- `--trig-price`：什么时候触发止盈条件
- `--price`：触发后真正提交的限价委托价

常见理解：

- 卖出止盈时，`trig-price` 常设在目标位附近
- 买入回落承接时，`trig-price` 往往低于当前市价

### 示例 1：美股卖出止盈

场景：

- 你持有 `AAPL`
- 当前价格低于 `184.00`
- 想在涨到 `184.00` 后开始止盈卖出
- 触发后按 `185.00` 报出卖单

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction sell --quantity 5 --order-type take_profit_limit --price 185.00 --trig-price 184.00
```

解释：

- 价格先达到 `184.00`
- 触发后系统按 `185.00` 发出限价卖单

### 示例 2：回落买入

场景：

- 你不想追高，希望 `AAPL` 回落到 `170.00` 再考虑买入
- 触发价设为 `170.00`
- 触发后按 `170.20` 提交买单

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction buy --quantity 5 --order-type take_profit_limit --price 170.20 --trig-price 170.00
```

解释：

- 买入方向下，不要只看“止盈”这两个字
- 它在这个方向里更像“跌到目标位后触发买入”

---

## 5. 跟踪止损单 `trailing_stop(33)`

### 含义

跟踪止损单不是盯住一个固定触发价，而是盯住市场价格的阶段高点或低点，按你设定的回撤幅度动态跟踪。

它适合这种场景：

- 持仓已经有浮盈
- 你不想过早卖出
- 但又希望一旦价格明显回撤，就自动退出

### 必填参数

- `--order-type trailing_stop`
- `--tail-type`

二选一：

- `--tail-type 1` 时必须传 `--tail-amount`
- `--tail-type 2` 时必须传 `--tail-pct`

### 参数理解

- `--tail-type 1`：按固定金额跟踪
- `--tail-type 2`：按比例跟踪
- `--tail-amount`：固定回撤金额
- `--tail-pct`：固定回撤比例，例如 `0.05` 表示 5%

### 示例 1：港股按比例跟踪止损

场景：

- 你持有腾讯 `00700`
- 希望价格从阶段高点回撤 `5%` 时触发卖出

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction sell --quantity 100 --order-type trailing_stop --tail-type 2 --tail-pct 0.05
```

解释：

- 市场创新高时，系统会随着高点抬升跟踪线
- 一旦从高点回撤达到 `5%`，就触发对应委托

### 示例 2：A 股按比例跟踪止损

```bash
$FOSUN_PYTHON place_order.py --stock 600519 --market sh --direction sell --quantity 100 --order-type trailing_stop --tail-type 2 --tail-pct 0.03
```

解释：

- 表示从阶段高点回撤 `3%` 时触发

---

## 6. 止盈止损组合单 `take_profit_stop_loss(35)`

### 含义

止盈止损组合单可以理解为：

- 同时挂一个止盈条件
- 再同时挂一个止损条件
- 两侧互斥，谁先触发就执行谁，另一侧自动取消

这类单最适合：

- 已经持有仓位
- 想预先设好“赚到哪里卖”和“跌到哪里砍”

### 必填参数

- `--order-type take_profit_stop_loss`
- `--price`
- `--profit-price`
- `--profit-quantity`
- `--stop-loss-price`
- `--stop-loss-quantity`

### 参数理解

- `--profit-price` / `--profit-quantity`：止盈侧触发条件和数量
- `--stop-loss-price` / `--stop-loss-quantity`：止损侧触发条件和数量
- `--price`：任一侧触发后，真正报出的限价委托价

### 示例 1：港股同时设止盈和止损

场景：

- 你持有腾讯 `00700` 100 股
- 希望涨到 `420.000` 附近止盈
- 如果跌到 `390.000` 附近则止损
- 触发后统一按 `400.000` 的限价发出委托

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction sell --quantity 100 --order-type take_profit_stop_loss --price 400.000 --profit-price 420.000 --profit-quantity 100 --stop-loss-price 390.000 --stop-loss-quantity 100
```

解释：

- 一旦某一侧条件先满足，系统会提交对应限价单
- 另一侧条件会被自动撤销

### 示例 2：美股同时设止盈和止损

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction sell --quantity 5 --order-type take_profit_stop_loss --price 180.00 --profit-price 185.00 --profit-quantity 5 --stop-loss-price 175.00 --stop-loss-quantity 5
```

---

## 7. 常见误区

### 误区 1：把 `trig-price` 当成最终成交价

不是。

- `trig-price` 是触发价
- `price` 才是触发后报出去的限价

### 误区 2：名字里有“止盈”“止损”，买卖两边含义就完全一样

也不是。

- 卖出方向和买入方向的触发语义不同
- 一定要结合 `direction` 和当前市场价格一起理解

### 误区 3：条件单触发后一定成交

不一定。

条件触发后，系统只是提交委托；如果你给出的 `price` 不合适，仍然可能挂单、部分成交或最终不成交。

### 误区 4：跟踪止损单一定比固定止损更安全

不一定。

- 跟踪止损更灵活
- 但在波动较大的市场里，也可能因为短时波动过早触发

---

## 8. 选型建议

可以用下面的简单思路选单型：

- 想“跌破某价就卖出止损” -> `stop_loss_limit(31)`
- 想“涨到某价就卖出止盈” -> `take_profit_limit(32)`
- 想“让止损线跟着盈利一起上移” -> `trailing_stop(33)`
- 想“同时预设止盈和止损，两边二选一” -> `take_profit_stop_loss(35)`

---

## 9. 下单前检查清单

提交条件单前，建议至少确认以下几点：

- 方向是否正确：`buy` / `sell`
- 市场是否正确：`hk` / `us` / `sh` / `sz`
- 订单类型是否正确：`31` / `32` / `33` / `35`
- 触发逻辑是否正确：是突破触发，还是回落触发
- `trig-price` 和 `price` 是否区分清楚
- 数量是否正确
- 条件触发后报出的 `price` 是否有成交可能

---

## 10. 命令速查

### 止损限价单

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction sell --quantity 100 --order-type stop_loss_limit --price 380.000 --trig-price 385.000
```

### 止盈限价单

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction sell --quantity 5 --order-type take_profit_limit --price 185.00 --trig-price 184.00
```

### 跟踪止损单

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction sell --quantity 100 --order-type trailing_stop --tail-type 2 --tail-pct 0.05
```

### 止盈止损组合单

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction sell --quantity 5 --order-type take_profit_stop_loss --price 180.00 --profit-price 185.00 --profit-quantity 5 --stop-loss-price 175.00 --stop-loss-quantity 5
```
