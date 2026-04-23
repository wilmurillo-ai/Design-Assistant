# StarryForest Agent Mail API v1 使用说明

## 1. 目的与场景

本 API 用于通过邮件将结构化指令从 **OpenClaw** 发送到 **iOS 快捷指令自动化**：

- OpenClaw 发送邮件（正文含 JSON）
- iOS 自动化触发（收到邮件）
- 快捷指令解析 JSON，并执行动作（闹钟/提醒事项/备忘录/日历/专注/音乐/日记）

------

## 2. 邮件正文承载方式（锚定块）

为避免邮件签名、引用、富文本等干扰解析，正文建议使用锚定块包裹 JSON：

```text
AGENT_PAYLOAD_BEGIN
{ ... JSON ... }
AGENT_PAYLOAD_END
```

快捷指令应先提取 `AGENT_PAYLOAD_BEGIN` 与 `AGENT_PAYLOAD_END` 之间的文本，再解析为 JSON。

> 正则提取建议（跨行非贪婪）：
> `AGENT_PAYLOAD_BEGIN[ \t]*\r?\n?([\s\S]*?)\r?\n?[ \t]*AGENT_PAYLOAD_END`
> 捕获组 1 即 payload JSON。

------

## 3. 顶层结构（必须）

邮件中的 JSON 顶层结构如下：

```json
{
  "version": 1,
  "token": "starryforest_agent",
  "id": "unique-payload-id",
  "actions": [
    {
      "type": "创建提醒事项",
      "payload": {
        "title": "示例",
        "due": "2026-02-07 15:00"
      }
    }
  ]
}
```

### 3.1 顶层字段定义

| 字段      | 类型   | 必填 | 含义                                                         |
| --------- | ------ | ---- | ------------------------------------------------------------ |
| `version` | number | ✅    | 协议版本。当前固定为 `1`。                                   |
| `token`   | string | ✅    | 共享密钥，用于防伪。固定值：`"starryforest_agent"`。         |
| `id`      | string | ✅    | **指令包唯一 ID**。用于包级幂等/去重（避免重复执行）。       |
| `actions` | array  | ✅    | 动作列表。每个元素包含 `type`（中文）与 `payload`（英文键对象）。 |

### 3.2 actions 元素结构（通用）

```json
{
  "type": "创建备忘录",
  "payload": { }
}
```

- `type`：中文动作类型（见第 5 节）
- `payload`：动作参数对象（字段键为英文）

> 注意：**通用结构不包含** `action id`、`enabled`（按你的要求）。
> 去重仅依赖顶层 `id`。

------

## 4. 时间与日期格式规范（非常重要）

为避免 iOS/快捷指令对时区进行自动换算导致时间偏移，本协议对“时间点”采用**本地时间点字符串**：

### 4.1 时间点字段统一格式（推荐）

- 格式：`YYYY-MM-DD HH:mm`
- 示例：`"2026-02-07 15:00"`

适用字段：

- `due`（提醒事项到期）
- `start` / `end`（日历日程开始/结束）
- `until`（专注模式结束时间）

### 4.2 例外：闹钟时间

- `创建闹钟.payload.time` 使用 `HH:mm`（表示每天的闹钟时间）
- 示例：`"07:30"`

### 4.3 仅日期字段

- `写日记.payload.date` 使用 `YYYY-MM-DD`
- 示例：`"2026-02-07"`

------

## 5. 动作类型与 payload 定义

以下为 v1 支持的 7 种 action。

------

### 5.1 创建闹钟（type = `创建闹钟`）

**payload：**

| 字段      | 类型     | 必填 | 含义                           |
| --------- | -------- | ---- | ------------------------------ |
| `time`    | string   | ✅    | 闹钟时间（`HH:mm`）            |
| `label`   | string   | ⛔    | 闹钟标签                       |
| `enabled` | boolean  | ⛔    | 是否启用（默认 true）          |
| `repeat`  | string[] | ⛔    | 重复星期（**英文全称**，见下） |

`repeat` 允许值（必须全称）：

- `Monday` `Tuesday` `Wednesday` `Thursday` `Friday` `Saturday` `Sunday`

**示例：**

```json
{
  "type": "创建闹钟",
  "payload": {
    "time": "07:30",
    "label": "晨练",
    "enabled": true,
    "repeat": ["Monday", "Wednesday", "Friday"]
  }
}
```

------

### 5.2 创建提醒事项（type = `创建提醒事项`）

**payload：**

| 字段       | 类型   | 必填 | 含义                             |
| ---------- | ------ | ---- | -------------------------------- |
| `title`    | string | ✅    | 提醒事项标题                     |
| `due`      | string | ⛔    | 到期时间点（`YYYY-MM-DD HH:mm`） |
| `notes`    | string | ⛔    | 备注                             |
| `priority` | string | ⛔    | 优先级：`高` / `中` / `低`       |

**示例：**

```json
{
  "type": "创建提醒事项",
  "payload": {
    "title": "测试提醒：喝水",
    "due": "2026-02-07 15:00",
    "notes": "来自 OpenClaw 邮件自动化",
    "priority": "中"
  }
}
```

------

### 5.3 创建备忘录（type = `创建备忘录`）

**payload：**

| 字段      | 类型   | 必填 | 含义       |
| --------- | ------ | ---- | ---------- |
| `title`   | string | ✅    | 备忘录标题 |
| `content` | string | ✅    | 备忘录内容 |

**示例：**

```json
{
  "type": "创建备忘录",
  "payload": {
    "title": "OpenClaw 测试备忘录",
    "content": "这是一条通过邮件触发自动化创建的备忘录。"
  }
}
```

------

### 5.4 创建日历日程（type = `创建日历日程`）

**payload：**

| 字段       | 类型    | 必填 | 含义                             |
| ---------- | ------- | ---- | -------------------------------- |
| `title`    | string  | ✅    | 日程标题                         |
| `start`    | string  | ✅    | 开始时间点（`YYYY-MM-DD HH:mm`） |
| `end`      | string  | ⛔    | 结束时间点（`YYYY-MM-DD HH:mm`） |
| `location` | string  | ⛔    | 地点                             |
| `notes`    | string  | ⛔    | 备注                             |
| `allDay`   | boolean | ⛔    | 是否全天（默认 false）           |

**示例：**

```json
{
  "type": "创建日历日程",
  "payload": {
    "title": "OpenClaw 测试日程",
    "start": "2026-02-07 10:00",
    "end": "2026-02-07 10:30",
    "location": "Home",
    "notes": "测试：创建日历事件（本地时间点）",
    "allDay": false
  }
}
```

------

### 5.5 专注模式（type = `专注模式`）

**payload：**

| 字段    | 类型    | 必填 | 含义                                                  |
| ------- | ------- | ---- | ----------------------------------------------------- |
| `name`  | string  | ✅    | 专注模式名称：`工作` / `个人` / `睡眠`                |
| `on`    | boolean | ✅    | true 开启 / false 关闭                                |
| `until` | string  | ⛔    | 结束时间点（`YYYY-MM-DD HH:mm`；仅 on=true 时有意义） |

**示例：**

```json
{
  "type": "专注模式",
  "payload": {
    "name": "工作",
    "on": true,
    "until": "2026-02-07 12:00"
  }
}
```

------

### 5.6 播放音乐（type = `播放音乐`）

**payload：**

| 字段       | 类型    | 必填 | 含义                                     |
| ---------- | ------- | ---- | ---------------------------------------- |
| `play`     | boolean | ✅    | true 播放 / false 暂停（由快捷指令映射） |
| `playlist` | string  | ✅    | 播放列表：`每日推荐` / `私人漫游`        |

**示例：**

```json
{
  "type": "播放音乐",
  "payload": {
    "play": true,
    "playlist": "每日推荐"
  }
}
```

------

### 5.7 写日记（type = `写日记`）

**payload：**

| 字段      | 类型   | 必填 | 含义                      |
| --------- | ------ | ---- | ------------------------- |
| `title`   | string | ✅    | 日记标题（如“日记/日报”） |
| `date`    | string | ✅    | 日期（`YYYY-MM-DD`）      |
| `content` | string | ✅    | 日记正文                  |

**示例：**

```json
{
  "type": "写日记",
  "payload": {
    "title": "日记",
    "date": "2026-02-07",
    "content": "测试：OpenClaw → 邮件 → iOS 自动化 → 写日记。"
  }
}
```

------

## 6. iOS 端解析与执行建议（实现要点）

### 6.1 校验与去重（强烈建议）

1. 提取锚定块 JSON
2. 解析 JSON → Dictionary
3. 校验 `token == "starryforest_agent"`，不匹配立即停止
4. 用顶层 `id` 做包级去重（例如写入“OpenClaw Processed IDs”备忘录）
   - 已存在则停止
   - 不存在则执行 actions，全部成功后再写入 id

### 6.2 遍历 actions

- 对 `actions` 做 Repeat
- 每次取 `type`，按中文 `type` 分发到对应动作
- 从 `payload` 取字段并执行系统动作

### 6.3 时间点解析

- 对 `due/start/end/until`（`YYYY-MM-DD HH:mm`）统一走“解析日期/Date”动作
- 若 `end` 缺省，可在快捷指令里默认 `start + 30 分钟`

------

## 7. 完整邮件示例（锚定块 + 全动作联调包）

你可以用这个做一次性全链路验证（7 个分支都跑一遍）：

```json
AGENT_PAYLOAD_BEGIN
{
  "version": 1,
  "token": "starryforest_agent",
  "id": "test-all-20260207-0001",
  "actions": [
    {
      "type": "创建闹钟",
      "payload": {
        "time": "07:30",
        "label": "晨练",
        "enabled": true,
        "repeat": ["Monday", "Wednesday", "Friday"]
      }
    },
    {
      "type": "创建提醒事项",
      "payload": {
        "title": "测试提醒：喝水",
        "due": "2026-02-07 15:00",
        "notes": "来自 OpenClaw 邮件自动化",
        "priority": "中"
      }
    },
    {
      "type": "创建备忘录",
      "payload": {
        "title": "OpenClaw 测试备忘录",
        "content": "联调包：已触发自动化并开始执行 actions。"
      }
    },
    {
      "type": "创建日历日程",
      "payload": {
        "title": "OpenClaw 测试日程",
        "start": "2026-02-07 10:00",
        "end": "2026-02-07 10:30",
        "location": "Home",
        "notes": "联调包：创建日历事件（本地时间点）",
        "allDay": false
      }
    },
    {
      "type": "专注模式",
      "payload": {
        "name": "工作",
        "on": true,
        "until": "2026-02-07 12:00"
      }
    },
    {
      "type": "播放音乐",
      "payload": {
        "play": true,
        "playlist": "每日推荐"
      }
    },
    {
      "type": "写日记",
      "payload": {
        "title": "日记",
        "date": "2026-02-07",
        "content": "联调包：7 个动作已下发，等待执行结果检查。"
      }
    }
  ]
}
AGENT_PAYLOAD_END
```

