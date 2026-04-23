---
name: invassistant
version: "2.0.0"
description: >
  US stock portfolio buy/sell signal checker — tells you WHEN to buy, WHEN to sell, and WHY.
  Uses a "Three Red Lines" entry filter (emotion-driven drop + technical reversal + no systemic risk)
  and a multi-layered exit engine (take-profit tiers, stop-loss, trend break, momentum fade, VIX panic defense).
  Fetches real-time data from Yahoo Finance, checks entry/exit signals for each holding,
  and pushes actionable alerts to WeChat Work, DingTalk, or Feishu group bots.

  美股持仓买卖信号检查器 — 告诉你什么时候该买、什么时候该卖、以及为什么。
  基于「三条红线」入场过滤（情绪释放+技术止跌+市场环境）和多层退出引擎
  （阶梯止盈/止损清仓/趋势破位/动量衰竭/VIX恐慌防守），
  从 Yahoo Finance 获取实时行情，逐标的检查买卖信号，推送到企微/钉钉/飞书群机器人。
read_when:
  - 检查持仓
  - 持仓信号
  - 今日信号
  - 红线检查
  - TSLA红线
  - 建仓检查
  - 减仓信号
  - 止盈检查
  - 止损检查
  - 退出信号
  - 趋势破位
  - 动量衰竭
  - portfolio check
  - trading signal
  - entry check
  - exit check
  - red line check
  - stock signal
  - take profit
  - stop loss
  - 投资信号
  - 交易信号
  - 持仓检查
  - 详细分析
allowed-tools:
  - read_file
  - write_to_file
  - replace_in_file
  - execute_command
disable: false
metadata:
  openclaw:
    requires:
      bins:
        - python3
      env: []
    tags:
      - investment
      - trading
      - portfolio
      - signal
      - stock
      - finance
      - us-stock
      - buy-sell
      - alert
---

# InvAssistant — US Stock Buy/Sell Signal Checker | 美股买卖信号检查器

**What it does | 做什么**：Check your US stock portfolio every day — should you BUY, SELL, or HOLD? This skill answers that question with a rules-based, emotion-free approach.

**How it works | 怎么做**：Fetches real-time price/volume data from Yahoo Finance → applies the "Three Red Lines" entry filter and a multi-layered exit engine → outputs actionable signals per holding → optionally pushes alerts to WeChat Work / DingTalk / Feishu group bots.

---

## Core Concept: Three Red Lines Entry System | 核心概念：三条红线入场系统

> **Red Lines are FILTERS, not scores.** ALL three must pass → BUY. Any single failure → NO TRADE.
>
> **红线是过滤条件，不是评分制。** 全部通过才允许建仓，任何一条未通过 = 不交易。

### Red Line 1: Emotion-Driven Drop (Most Critical) | 红线1：情绪释放型下跌（最关键）

Trigger (either one):
- Single-day drop ≥ 4% (configurable)
- 3+ consecutive down days (configurable)

触发条件（满足任一）：单日跌幅 ≥ 4%，或连续 3 个交易日下跌。

No emotion release → no mispricing → no entry reason. | 没有情绪释放 → 没有情绪错配 → 没有入场理由。

### Red Line 2: Technical Reversal Confirmation (Strict) | 红线2：技术止跌信号（严格标准）

Requires **real** reversal confirmation — "near moving average" or "single bounce" does NOT count:
- Volume shrinkage after sell-off (< 70% of previous day)
- Strong MA support = lower shadow + up close + (volume surge 120%+ OR strong bounce ≥ 1.5%)
- Complete Higher Low structure (Low A → bounce → Low B > A → 2-day confirmation)

需要**真实的止跌确认**，"接近均线"或"单次反弹"不算通过。

### Red Line 3: No Systemic Market Risk | 红线3：市场未进入系统性风险

ALL must be true | 必须全部满足：
- QQQ not down 3 consecutive days | QQQ 未连续 3 日暴跌
- SPX not down 3 consecutive days | SPX 未连续 3 日暴跌
- VIX < 25 (configurable) | VIX < 25（可配置）

## Strategy Types | 策略类型

| Type | EN Description | 中文说明 | Entry | Exit |
|------|---------------|---------|-------|------|
| `redline` | Three Red Lines filter | 三条红线建仓 | All 3 pass → BUY | Take-profit / Stop-loss / Trend-break / Momentum-fade |
| `hold` | Permanent hold | 永久持有，不加不减 | — | Systemic risk defense only |
| `pullback` | Buy on pullback | 回调达阈值时加仓 | Pullback ≥ threshold | Take-profit / Stop-loss / Trend-break |
| `satellite` | Satellite position | 卫星仓，不动 | — | Tight stop-loss + wide take-profit |

## Exit Signal Engine | 退出信号系统

> Exit signals are **discipline-driven**, not emotion-driven. Checked by priority — higher priority triggers skip lower ones.
>
> 退出信号是**纪律驱动**，不是情绪驱动。按优先级从高到低检查。

### Stop-Loss (CRITICAL) | 止损清仓（最高优先级）

When unrealized loss exceeds the stop-loss line → **SELL ALL immediately**, no hesitation.

当浮亏超过止损线时**立即清仓**，不留余地。

- Default: -15% (redline) / -12% (pullback) / -20% (satellite)
- Configurable: `exit_params.stop_loss_pct`
- HOLD holdings: stop-loss disabled (systemic risk defense only)

### Take-Profit Tiers (HIGH) | 阶梯止盈（高优先级）

Tiered profit-taking — lock in gains gradually, not all at once:

阶梯式止盈，分批锁利而非一次性出清：

| Gain | Action | 浮盈 | 操作 |
|------|--------|------|------|
| 20% | Sell 1/3 | 20% | 减仓 1/3 |
| 40% | Sell another 1/3 | 40% | 再减 1/3 |
| 80% | Keep core only | 80% | 仅保留底仓 |

- Configurable: `exit_params.take_profit_tiers`
- Requires `exit_params.cost_basis` (your buy price) to be set | 需要配置持仓成本价才能生效

### Trend Break (HIGH) | 趋势破位（高优先级）

When price **effectively breaks below** a key moving average → defensive reduction:

当价格有效跌破关键均线时减仓防守：

- Close below MA50 for N consecutive days (default 3) | 收盘价连续 N 日低于 MA50
- No support signals during that period | 期间无明显承接信号
- Moving average turning downward | 均线拐头向下
- Action: reduce 50% (configurable) | 触发后减仓 50%

### Momentum Fade (MEDIUM) | 动量衰竭（中优先级）

Early warning of weakening uptrend — reduce before reversal:

上涨趋势中出现动量减弱的早期预警：

- Volume-price divergence: new highs but declining volume | 创新高但成交量萎缩
- Consecutive volume decline | 连续多日量能递减
- MACD divergence: price new high but MACD bars shrinking | MACD 顶背离
- Action: reduce 1/3 (configurable) | 触发后减仓 1/3

### Systemic Risk Defense (Portfolio-level) | 系统性风险防守（全组合层级）

The **ONLY exit that overrides HOLD** strategy. Protects the entire portfolio:

这是**唯一可以覆盖「永久 HOLD」策略**的退出条件：

| Level | Condition | Action |
|-------|-----------|--------|
| ⚠️ Warning | VIX ≥ 25.5 | Stay alert, prepare plan | 提高警惕 |
| 🟠 Panic | VIX ≥ 30 or QQQ/SPX 3-day crash | Non-core reduce 50% | 非核心仓减半 |
| 🔴 Extreme | VIX ≥ 40 | Entire portfolio reduce to 50% | 全组合减至 50% |

## Workflow | 工作流程

### Step 1: Load Config [Deterministic] | 确认配置 [确定性]

Config search order | 配置文件查找顺序：
1. `INVASSISTANT_CONFIG` env variable | 环境变量指定路径
2. `my_portfolio.json` in project root (personal format, auto-adapted) | 项目根目录个人配置（自动适配）
3. `invassistant-config.json` in project root (standard Skill format) | 项目根目录通用配置
4. Built-in defaults via `scripts/init_config.py` | 内置默认配置

If neither file exists, run `python scripts/init_config.py` to generate defaults.

Key config sections | 配置核心结构：
- `portfolio.watchlist` — Stock watchlist (symbol, strategy, params, exit_params) | 关注标的列表
- `portfolio.systemic_risk_exit` — Systemic risk defense parameters | 系统性风险防守参数
- `portfolio.vix_threshold` — VIX entry threshold (default 25) | VIX 入场阈值
- `adapters` — Push channels (wechatwork / dingtalk / feishu) | 推送渠道
- `commands` — Command-to-action mapping | 指令映射

### Step 2: Run Check [Deterministic] | 执行检查 [确定性]

Choose execution mode based on user command | 根据用户指令选择执行模式：

**Full portfolio check | 全组合检查** ("检查持仓" / "今日信号" / "portfolio check"):
```bash
python scripts/portfolio_checker.py
```

**Single stock deep analysis | 单标的详细分析** ("TSLA红线" / "详细分析"):
```bash
python scripts/portfolio_checker.py --detail TSLA
```

**Check and push alerts | 检查并推送** ("检查并推送" / "推送信号"):
```bash
python scripts/portfolio_checker.py --push
```

### Step 3: Read Output [Deterministic] | 解读输出 [确定性]

Results show **entry signals** and **exit signals** per holding | 检查结果按标的输出入场信号和退出信号：

- `redline` holdings: Three Red Lines verdict + exit signal check | 三条红线逐条判定 + 退出检查
- `pullback` holdings: Pullback magnitude + threshold check + exit signals | 回调幅度 + 退出检查
- `hold` / `satellite` holdings: Current price + exit warnings | 当前价格 + 退出预警

Exit signal priority labels | 退出信号优先级标注：
- 🔴 CRITICAL — Stop-loss, SELL ALL now | 止损清仓（立即执行）
- 🟠 HIGH — Take-profit / Trend-break, act soon | 止盈减仓/趋势破位（尽快执行）
- 🟡 MEDIUM — Momentum-fade, watch and prepare | 动量衰竭（观察并准备）

Portfolio self-check summary (5 questions) | 全组合自检汇总：
1. Any emotion-mispriced assets? (redline holdings all pass) | 是否出现情绪错配资产？
2. Any core holdings forced undervalued? (pullback threshold met) | 是否出现核心仓被迫低估？
3. Any holdings triggering exit signals? | 是否有标的触发退出信号？
4. Systemic risk detected? (VIX panic + market crash) | 是否出现系统性风险？
5. Final verdict: BUY / SELL / NO TRADE | 综合结论：入场 / 退出 / 不交易

### Step 4: Push Alerts (Optional) [Deterministic] | 推送（按配置）[确定性]

Push results via configured channels | 根据配置推送结果：

1. **WeChat Work | 企业微信**：`scripts/send_wecom.py` — Markdown message
2. **DingTalk | 钉钉**：`scripts/send_dingtalk.py` — Markdown + HMAC signing
3. **Feishu | 飞书**：`scripts/send_feishu.py` — Rich text (post) or interactive card

Each push script supports `--test` to verify config | 每个推送脚本支持 `--test` 参数验证配置。

## Configuration Guide | 配置指南

### Modify Watchlist | 修改关注股票

Edit `portfolio.watchlist` in `invassistant-config.json`:

编辑 `invassistant-config.json` 中的 `portfolio.watchlist`：

```json
{
  "symbol": "TSLA",
  "name": "Tesla / 特斯拉",
  "strategy": "redline",
  "params": {
    "emotion_drop_threshold": -4,
    "consecutive_days": 3,
    "bounce_threshold": 1.5,
    "volume_ratio": 1.2,
    "entry_size": 0.3
  }
}
```

- **Add**: Append an entry to the watchlist array | 添加：在 watchlist 数组中追加条目
- **Remove**: Delete the entry from the array | 删除：从数组中移除对应条目

### Configure Exit Conditions | 配置退出条件

Edit `exit_params` for each holding | 编辑每个标的的 `exit_params`：

```json
{
  "symbol": "TSLA",
  "strategy": "redline",
  "params": { ... },
  "exit_params": {
    "cost_basis": 250.00,
    "position_size": 100,
    "take_profit_enabled": true,
    "take_profit_tiers": [
      {"gain_pct": 20, "action": "Sell 1/3 | 减仓1/3", "reduce_pct": 33, "label": "Tier 1 | 第一阶梯"},
      {"gain_pct": 40, "action": "Sell 1/3 | 再减1/3", "reduce_pct": 33, "label": "Tier 2 | 第二阶梯"}
    ],
    "stop_loss_enabled": true,
    "stop_loss_pct": -15,
    "stop_loss_action": "SELL ALL | 清仓",
    "trend_break_enabled": true,
    "trend_break_ma": 50,
    "trend_break_confirm_days": 3,
    "trend_break_action": "Reduce 50% | 减仓50%",
    "momentum_fade_enabled": true,
    "momentum_action": "Reduce 1/3 | 减仓1/3"
  }
}
```

**Important**: Set `cost_basis` (your buy price) for take-profit/stop-loss to work | **重要**：填入持仓成本价后止盈/止损检查才会生效。

### Configure Systemic Risk Defense | 配置系统性风险防守

```json
{
  "portfolio": {
    "systemic_risk_exit": {
      "enabled": true,
      "vix_panic_threshold": 30,
      "vix_extreme_threshold": 40,
      "market_consecutive_drop_days": 3,
      "market_drop_magnitude": -2,
      "panic_action": "Non-core reduce 50% | 非核心仓减半",
      "extreme_action": "Portfolio reduce to 50% | 全组合减至50%"
    }
  }
}
```

### Configure Push Channels | 配置推送渠道

Enable a channel in `adapters` and fill in the Webhook URL | 在 `adapters` 中启用渠道并填入 Webhook URL：

| Channel | Config Key | Main Config | Env Variable |
|---------|-----------|-------------|--------------|
| WeChat Work | `wechatwork` | `webhook_url` | `WECOM_WEBHOOK_URL` |
| DingTalk | `dingtalk` | `webhook_url`, `secret` | `DINGTALK_WEBHOOK_URL`, `DINGTALK_SECRET` |
| Feishu | `feishu` | `webhook_url`, `secret` | `FEISHU_WEBHOOK_URL`, `FEISHU_SECRET` |

### Configure Command Triggers | 配置指令接收

Map group bot commands to actions | 映射群机器人指令到动作：

```json
{
  "检查持仓": "full_check",
  "TSLA红线": "tsla_detail",
  "今日信号": "full_check"
}
```

@bot + command text in group → trigger check | 在群里 @机器人 + 指令文本 → 触发对应检查

## Quick Entry Scripts | 快捷入口

Convenience scripts in project root | 项目根目录的兼容入口脚本：
- `check_portfolio_v2.py` — **Recommended**: Modular entry point calling scripts/ | 推荐入口（模块化）
- `check_portfolio.py` — Legacy full-check (fallback) | 旧版全量检查（回退用）
- `check_tsla_entry.py` — TSLA red line check | TSLA 红线检查
- `check_detail.py` — TSLA detailed analysis | TSLA 详细分析

---

## Hard Rules | 硬性规则

These rules are **absolute** — no exceptions, no overrides:

1. **Signal priority is fixed**: Stop-loss > Take-profit > Trend-break > Momentum-fade > Systemic-risk. Higher priority signal fires → skip lower checks.
2. **Red Lines are filters, NOT scores**: ALL three must pass → BUY. One fails → NO TRADE. Never "average" or "weigh" partial passes.
3. **Never fabricate data**: If API returns error or empty data → report the failure. Never invent prices, volumes, or signals.
4. **HOLD protection**: HOLD strategy holdings are immune to all exit signals EXCEPT systemic risk (VIX ≥ 30). Never suggest selling HOLD positions for profit-taking or trend breaks.
5. **Push confirmation**: Before sending any push notification (WeChat Work / DingTalk / Feishu), confirm with user UNLESS running in automated mode (`--push` flag).

## Failure Handling | 失败处理

| Scenario | Action |
|----------|--------|
| Config file missing | Run `python scripts/init_config.py`, report to user |
| Yahoo Finance API rate limit / timeout | Retry once after 5s. If still fails, report which symbols failed and continue with remaining |
| Insufficient historical data (< 20 days) | Skip technical analysis for that symbol, note in output |
| `cost_basis` not configured | Skip take-profit / stop-loss for that symbol, warn user |
| Push channel webhook fails | Log error, continue with other channels, report failure in output |
| All symbols fail to fetch | Report complete failure, suggest checking network / API status |
