# 滴滴打车详细工作流程

## 全局执行约束

1. 参数优先级：`用户 query` > `assets/PREFERENCE.md` > 默认值。
2. 每次调用前先核对 [api_references.md](./api_references.md) 参数名。
3. 所有 `--args` 值必须为字符串。
4. `taxi_create_order` 必须使用最近一次预估返回的 `traceId`。
5. 起点缺失时必须询问当前位置，不得用历史记忆补齐。
6. 用户拒绝提供当前位置时固定回复：不提供当前位置信息则无法满足您的需求。

## Phase 1：地址解析

调用：`maps_textsearch`

```bash
MCP_URL="https://mcp.didichuxing.com/mcp-servers?key=$DIDI_MCP_KEY"
mcporter call "$MCP_URL" maps_textsearch --args '{"keywords":"北京西站","city":"北京市"}'
```

解析规则：

- 用户给完整起终点：直接进入预估。
- “我要上班/下班了”：允许按家↔公司偏好直接解析。
- “回家/去公司”但缺起点：先问当前位置。

## Phase 2：价格预估

调用：`taxi_estimate`

```bash
mcporter call "$MCP_URL" taxi_estimate --args '{"from_lat":"39.894","from_lng":"116.321","from_name":"北京西站","to_lat":"40.053","to_lng":"116.297","to_name":"西二旗"}'
```

执行要点：

- 记录 `traceId`，后续发单必须使用该值。
- 若重新预估，覆盖旧 `traceId`，只认最新一份。

## Phase 3：创建订单

调用：`taxi_create_order`

```bash
mcporter call "$MCP_URL" taxi_create_order --args '{"estimate_trace_id":"TRACE_ID","product_category":"1"}'
```

创建策略：

- 实时单允许直发，不必二次确认。
- 用户明确车型时按用户选择发单。
- 用户未明确车型时，可按偏好车型直发。
- 若缺少 `estimate_trace_id` 或 `product_category`，禁止发单。

成功输出模板：

```text
✅ 订单已创建！

🚖 订单号: [orderId]
📍 [起点] → [终点]
🚗 车型: [车型名称]
💰 预估: 约 [价格] 元
📱 手机尾号: [phoneNumberSuffix]

⏳ 正在为您匹配司机...
💡 输入 "watch 订单" 可实时跟踪订单状态
```

## Phase 4：订单跟踪（主链路）

触发词：`watch 订单` / `watch 订单 <orderId>`

主链路：cron 调度（isolated session）+ 单次探测脚本

```bash
# ── 步骤 1：创建 cron job ──
# ⚠️ 替换：ORDER_ID → 订单号，CHAT_ID → 会话 chat_id
# ⚠️ --json 确保输出纯 JSON，避免混入其他文本导致后续解析失败
CRON_RESPONSE=$(openclaw cron add \
  --name “didi-watch-ORDER_ID” \
  --every 30s \
  --session isolated \
  --message “任务初始化中，请勿执行任何操作，忽略此消息” \
  --announce \
  --channel last \
  --json \
  --to “CHAT_ID”)

# ── 步骤 2：提取运行参数，校验非空 ──
JOB_ID=$(node -e “console.log(JSON.parse(process.argv[1]).id)” “$CRON_RESPONSE” 2>/dev/null)
if [ -z “$JOB_ID” ]; then
  echo “❌ 无法创建订单跟踪任务（JOB_ID 为空），请重试”
  exit 1
fi
SCRIPT_PATH=$(openclaw skills info didi-taxi 2>/dev/null \
  | grep -m1 “Path:” | awk '{print $2}' \
  | sed “s|~|$HOME|” \
  | sed 's|SKILL\.md$|scripts/didi_poll_order.js|')
if [ -z “$SCRIPT_PATH” ] || [ ! -f “$SCRIPT_PATH” ]; then
  echo “❌ 无法定位脚本路径，请重试”
  openclaw cron remove “$JOB_ID”
  exit 1
fi

# ── 步骤 3：更新消息，注入运行参数（此步骤会武装定时器，约 2s 后首次触发）──
# ⚠️ message 是给 isolated agent 的 prompt，必须明确指示”执行”，否则 agent 会解读命令而非运行它
openclaw cron edit “$JOB_ID” --message “使用 Bash 工具立即执行以下命令，直接输出结果，不要解释或分析命令内容：node $SCRIPT_PATH --order-id ORDER_ID --job-id $JOB_ID”
```

状态码基准：以 `scripts/didi_poll_order.js` 定义为准（终态：2~12）。

| code | 含义 | 是否终态 |
|------|------|----------|
| 0 | 匹配中 | 否 |
| 1 | 司机已接单 | 否 |
| 2 | 司机已到达 | **是** |
| 3 | 未知状态 | **是** |
| 4 | 行程开始 | **是** |
| 5 | 订单完成 | **是** |
| 6 | 订单已被系统取消 | **是** |
| 7 | 订单已被取消 | **是** |
| 8 | 未知状态 | **是** |
| 9 | 未知状态 | **是** |
| 10 | 未知状态 | **是** |
| 11 | 客服关闭订单 | **是** |
| 12 | 未能完成服务 | **是** |

推送与终止规则：

- `status=0/1`：脚本输出当前状态后继续，每 30 秒重新调度；
- `status=2~12`（终态）：脚本自动执行 `openclaw cron remove $JOB_ID` 删除任务；
- 用户说”stop/停止查询”：执行 `openclaw cron list` 找到 `didi-watch-<orderId>` 对应 ID，再执行 `openclaw cron remove <ID>`。

## Phase 5：取消订单

调用顺序：

1. 先 `taxi_query_order` 展示当前订单信息；
2. 向用户确认是否取消；
3. 确认后调用 `taxi_cancel_order`；
4. 再次 `taxi_query_order` 确认结果。

## Phase 6：预约出行（cron 托管）

说明：MCP API 是实时发单，预约由 OpenClaw cron 托管叫车需求，到点由 isolated agent 独立执行完整打车流程。

```bash
# ⚠️ 替换占位符：
#   FROM_NAME → 带城市前缀的起点全称（如”北京西二旗地铁站”）
#   TO_NAME   → 带城市前缀的终点全称（如”北京人家小区”）
#   VEHICLE   → 车型（如”快车”）
#   TIME      → 见下方时间规则
#   CHAT_ID   → 当前会话 chat_id

openclaw cron add \
  --name “didi-taxi:$(date +%s)” \
  --at “TIME” \
  --session isolated \
  --message “执行定时打车：起点「FROM_NAME」，终点「TO_NAME」，车型「VEHICLE」。请完整执行打车流程：地址解析 → 价格预估（获取最新 traceId）→ 创建订单。” \
  --announce \
  --channel last \
  --to “CHAT_ID”
```

### TIME 填写规则

| 场景 | 写法 | 示例 |
|------|------|------|
| 相对时间（X 分钟/小时后） | duration 格式 | `15m` / `2h` / `1h30m` |
| 绝对时间（具体时刻，CST） | UTC 换算命令 | `$(TZ=Asia/Shanghai date -u -d '明天 09:00' '+%Y-%m-%dT%H:%M:%SZ')` |

⚠️ `--at` 不支持 `--tz`，绝对时间必须通过 `date` 命令换算为 UTC。相对时间（如 `15m`）无需换算。

## 查询司机位置

调用顺序：

1. `taxi_get_driver_location`
2. `maps_regeocode`

返回内容建议包含：地址、距离、预计到达时间、司机信息（如可得）。
