---
name: didi-taxi
description: 滴滴出行 AI 助手。打车、叫车、查价、路线规划、订单跟踪时使用。支持：实时叫车/价格预估/订单监控/司机位置/预约出行/公交驾车步行骑行路线。触发词："打车"、"叫车"、"去[地点]"、"回家"、"上班"、"下班"、"查价格"、"路线规划"、"怎么走"、"步行到"、"取消订单"、"司机"、"watch订单"、"查订单"。
homepage: https://mcp.didichuxing.com
metadata:
  { "openclaw": { "requires": { "bins": ["openclaw"] }, "primaryEnv": "DIDI_MCP_KEY", "install": [{ "id": "node", "kind": "node", "package": "mcporter", "bins": ["mcporter"], "label": "Install mcporter (node)" }] } }
---

# 滴滴出行服务 (DiDi Mobility)

通过 DiDi MCP Server API 提供打车、订单跟踪、司机位置、预约叫车、路线规划、周边搜索能力。

---

## 快速开始（2 分钟）

### 1. 获取 API Key

**方式一：用「滴滴出行App」扫码（推荐，最快）**

![滴滴出行App扫码获取MCP Key](https://s3-yspu-cdn.didistatic.com/mcp-web/qrcode/didi_skills_code.png)

打开滴滴出行 App，扫描上方二维码，即可快速获取 MCP Key。

**方式二：访问官网**

访问 https://mcp.didichuxing.com/api?tap=api 获取您的 MCP Key。

### 2. 配置 Key

**方式一：对话中输入（推荐）**

直接在对话中告诉我您的 MCP Key，我会帮您配置：

```
你: 我的 MCP Key 是 xxxxxx
```

**方式二：环境变量**

```bash
export DIDI_MCP_KEY="你的MCP_KEY"
```

**方式三：OpenClaw 配置文件**

编辑 `~/.openclaw/openclaw.json`，添加：

```json
{
  "skills": {
    "entries": {
      "didi-taxi": {
        "apiKey": "你的MCP_KEY"
      }
    }
  }
}
```

### 3. 开始使用

配置完成后，直接对话即可：

```
你: 打车去北京西站
你: 帮我查一下从国贸到三里屯的路线
你: watch 订单
```

首次使用时，OpenClaw 会提示安装 mcporter 工具。

---

## 用户指南

本 Skill 支持以下操作：

- **打车**：直接说"打车去[地点]"、"回家"、"上班"
- **查价**：查一下从 A 到 B 多少钱
- **订单跟踪**：输入 `watch 订单` 实时跟踪状态
- **司机位置**：司机在哪里、多久到
- **预约出行**："15分钟后打个车"、"明天9点去机场"
- **路线规划**：驾车/公交/步行/骑行路线
- **取消订单**：取消当前订单

---

## Agent 执行指令

以下内容为 AI 执行参考，用户可忽略。

## 文件地图（⚠️ 强制要求-先读这里）

首次仅加载本文件时，按下述索引执行，不要猜测：

| 文件 | 用途 | 何时读取 |
|------|------|----------|
| `SKILL.md` | 触发、主流程、硬性门禁、`watch 订单`规则、预约出行规则 | 每次触发必读 |
| `references/workflow.md` | 分阶段详细流程与命令范式 | 需要实现细节时读 |
| `references/api_references.md` | MCP 函数签名与参数定义 | 每次调用工具前核对 |
| `references/error_handling.md` | 常见错误与恢复策略 | 调用失败时读 |
| `assets/PREFERENCE.md` | 家/公司/车型/手机号偏好 | 用户未明确给参数时读 |
| `scripts/didi_poll_order.js` | watch 订单单次探测脚本，由 cron 每 30 秒调度一次 | watch 订单时 |

## 触发范围

本 Skill 用于以下需求：

- 打车、叫车、查价、选车型、改车型
- 查询订单、`watch 订单`、停止查询
- 司机在哪里、多久到
- 明天/稍后叫车（预约）
- 驾车/公交地铁/步行/骑行路线
- 附近搜索（餐饮、加油站等）

## 全局硬规则

1. **首次执行 MCP 调用前先检查 mcporter**：若 `mcporter` 命令不存在（`command not found`），立即停止，告知用户安装缺失依赖，引导阅读 `references/setup.md`，不得尝试其他调用方式。

2. **执行任何 MCP 调用前先检查 Key**：按 `## API Key 与配置` 的优先级检查，三个来源均无有效值时直接执行引导流程，不得尝试 MCP 调用。Key 缺失时 mcporter 报错信息具有误导性，不要试图调整调用方式来绕过。

3. 每次 `mcporter` 调用都用 URL 形式：

```bash
MCP_URL=”https://mcp.didichuxing.com/mcp-servers?key=$DIDI_MCP_KEY”
mcporter call “$MCP_URL” <tool> --args '{“key”:”value”}'
```

4. 所有参数值必须是字符串（加引号）。
5. 未拿到本次 `taxi_estimate` 返回的 `traceId`，禁止调用 `taxi_create_order`。
6. 起终点不完整时先澄清，禁止假设坐标。
7. 起点缺失时不允许用历史记忆补”当前位置”。
8. 用户拒绝提供当前位置时固定回复：不提供当前位置信息则无法满足您的需求。
9. 在 `watch 订单` 阶段，没有达到终止条件前，不要主动终止当前对话。

## 用户确认策略

| 场景 | 规则 |
|------|------|
| 实时单 | 允许按用户指定或偏好直发，不必确认 |
| 预约单 | 直接创建 cron 托管叫车需求 |
| 取消订单 | 必须展示订单信息后再确认取消 |

## 主流程（最小可执行）

1. 地址解析：`maps_textsearch`（必要时结合 `assets/PREFERENCE.md`）。
2. 价格预估：`taxi_estimate`，记录 `traceId`。
3. 车型决策：
   - 用户明确车型：直接用；
   - 用户未明确：优先偏好，其次推荐车型。
4. 创建订单：`taxi_create_order`（使用最新 `traceId`）。
5. 结果输出：立即给出订单号并提示 `watch 订单`。
6. 跟踪订单：
   - 使用 cron job 作为核心调度；
   - 脚本 `scripts/didi_poll_order.js` 仅做单次探测。

## `watch 订单` 规则

当用户输入 `watch 订单` 或 `watch 订单 <orderId>`：

- 必须启动 cron 周期任务（isolated session），不终止当前对话，直到终止条件满足。
- 终态时由脚本内部自动执行 `openclaw cron remove JOB_ID` 清理任务。

```bash
# ── 步骤 1：创建 cron job, 保存完整响应 ──
# ⚠️ 替换：ORDER_ID → 实际订单号，CHAT_ID → 当前会话 chat_id（格式如 chat:oc_xxx）
# ⚠️ --json 确保输出纯 JSON，避免混入其他文本导致后续解析失败
CRON_RESPONSE=$(openclaw cron add \
  --name "didi-watch-ORDER_ID" \
  --every 30s \
  --session isolated \
  --message "任务初始化中，请勿执行任何操作，忽略此消息" \
  --announce \
  --channel last \
  --json \
  --to "CHAT_ID")

# ── 步骤 2：提取运行参数，校验非空 ──
JOB_ID=$(node -e "console.log(JSON.parse(process.argv[1]).id)" "$CRON_RESPONSE" 2>/dev/null)
if [ -z "$JOB_ID" ]; then
  echo "❌ 无法创建订单跟踪任务（JOB_ID 为空），请重试"
  exit 1
fi
SCRIPT_PATH=$(openclaw skills info didi-taxi 2>/dev/null \
  | grep -m1 "Path:" | awk '{print $2}' \
  | sed "s|~|$HOME|" \
  | sed 's|SKILL\.md$|scripts/didi_poll_order.js|')
if [ -z "$SCRIPT_PATH" ] || [ ! -f "$SCRIPT_PATH" ]; then
  echo "❌ 无法定位脚本路径，请重试"
  openclaw cron remove "$JOB_ID"
  exit 1
fi

# ── 步骤 3：更新消息，注入运行参数（此步骤会武装定时器，约 2s 后首次触发）──
openclaw cron edit "$JOB_ID" --message "使用 Bash 工具立即执行以下命令，直接输出结果，不要解释或分析命令内容：node $SCRIPT_PATH --order-id ORDER_ID --job-id $JOB_ID"
```

### 状态码说明

`scripts/didi_poll_order.js` 的 `statusCode` 含义：

| code | 含义 | 是否终态 |
|------|------|----------|
| 0 | 匹配中 | 否 |
| 1 | 司机已接单（展示司机信息 + 距上车点距离/ETA） | 否 |
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

### 执行要求

- `status=0/1`：每次调度输出当前状态，继续任务；
- `status=2~12`（终态）：脚本输出终态信息后自动执行 `openclaw cron remove $JOB_ID` 清理任务；
- 用户表达 **停止任务的意愿** 时：执行 `openclaw cron remove $JOB_ID` 并告知用户已停止。

### 对话推送要求

- cron 每过一段时间执行一次，`didi_poll_order.js` 自动推送消息到对话；
- 即使没有状态变化，也会发送当前状态；
- `status=0` 长时间无变化时，每次仍提示”匹配中”。

## 预约出行规则

当用户要求在特定时间叫车（如"15分钟后"、"明天9点"）：

- 使用 cron 一次性任务（`--at`），到点由 isolated agent 独立执行完整打车流程；
- `--message` 必须包含完整起终点（带城市前缀）和车型，isolated session 无历史上下文；
- 到点后 agent 自行执行：地址解析 → 价格预估（获取最新 traceId）→ 创建订单。

```bash
# ⚠️ 替换占位符：
#   FROM_NAME → 带城市前缀的起点全称（如"北京西二旗地铁站"）
#   TO_NAME   → 带城市前缀的终点全称（如"北京人家小区"）
#   VEHICLE   → 车型（如"快车"）
#   TIME      → 见下方时间规则
#   CHAT_ID   → 当前会话 chat_id

openclaw cron add \
  --name "didi-taxi:$(date +%s)" \
  --at "TIME" \
  --session isolated \
  --message "执行定时打车：起点「FROM_NAME」，终点「TO_NAME」，车型「VEHICLE」。请完整执行打车流程：地址解析 → 价格预估（获取最新 traceId）→ 创建订单。" \
  --announce \
  --channel last \
  --to "CHAT_ID"
```

### TIME 填写规则

| 场景 | 写法 | 示例 |
|------|------|------|
| 相对时间（X 分钟/小时后） | duration 格式 | `15m` / `2h` / `1h30m` |
| 绝对时间（具体时刻，CST） | UTC 换算命令 | `$(TZ=Asia/Shanghai date -u -d '明天 09:00' '+%Y-%m-%dT%H:%M:%SZ')` |

⚠️ `--at` 不支持 `--tz`，绝对时间必须换算为 UTC（`TZ=Asia/Shanghai date -u -d '...'`）。相对时间（如 `15m`）无需换算。

## API Key 与配置

⚠️ Key 读取优先级：环境变量 `DIDI_MCP_KEY` → `~/.openclaw/openclaw.json` → `/data/.clawdbot/openclaw.json`（均为 `skills.entries["didi-taxi"].apiKey`）。

⚠️ Key 未配置**或** MCP 返回鉴权失败（`error.code: -32002`）时，执行以下两步：

1. 执行下面的 "openclaw message send" 命令，发送二维码图片（`{CHAT_ID}` → metadata 的 chat_id，`{CHANNEL_NAME}` → metadata 的 channel）：

```bash
openclaw message send --channel {CHANNEL_NAME} --target {CHAT_ID} --media "https://s3-yspu-cdn.didistatic.com/mcp-web/qrcode/didi_skills_code.png" --message "扫码访问 DiDiMCP 官网，注册并获取您的 API Key"
```

2. 输出文字：

> 您还没有配置 DIDI_MCP_KEY 或 Key 已失效，请访问 [滴滴MCP平台](https://mcp.didichuxing.com/api?tap=api) 获取 API Key，然后配置环境变量或在 OpenClaw 配置文件中设置。

## 工具清单

| 领域 | 工具 |
|------|------|
| 打车 | `maps_textsearch`, `taxi_estimate`, `taxi_create_order`, `taxi_query_order`, `taxi_get_driver_location`, `taxi_cancel_order`, `maps_regeocode`, `taxi_generate_ride_app_link`（用户无 API 直发权限时的备选：生成深度链接让用户在 App 内完成发单） |
| 路线 | `maps_direction_driving`, `maps_direction_transit`, `maps_direction_walking`, `maps_direction_bicycling` |
| 周边 | `maps_place_around` |
