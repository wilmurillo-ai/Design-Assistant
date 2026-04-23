---
name: feishu-room-booking
description: |
  飞书会议室查询与预订。当用户提到"查会议室"、"订会议室"、"空闲会议室"、"预订会议室"、"开会"、"找个会议室"、"F4会议室"、"紫金会议室"、"哪个会议室有空"、或者创建会议时需要自动匹配空闲会议室时，必须使用此 skill。也适用于用户要求创建日程并指定楼栋/区域时自动完成会议室预订的场景。也适用于用户提到"会议室偏好"、"我的偏好"、"候补"、"补订会议室"、"自动订会议室"时。
---

# 飞书会议室查询与预订

管理飞书会议室的忙闲查询、自动匹配、日程预订、偏好管理和候补轮询。

## 前置依赖

- `lark-cli` 已安装且 bot 身份可用
- 飞书应用已开通相关权限（calendar:calendar.free_busy:read, calendar:calendar.event:create 等）
- 数据文件：`references/room-mapping.json`、`references/user-preferences.json`、`references/room-waitlist.json`
- 脚本目录：`scripts/`

## 工具脚本

所有会议室操作**必须通过脚本**，不要手写 bash 循环。

### query_rooms.py — 会议室查询

```bash
# 列出所有楼栋
python3 scripts/query_rooms.py --list-buildings

# 列出指定楼栋的会议室
python3 scripts/query_rooms.py --list-rooms -b "丽金"

# 查询空闲会议室（表格输出）
python3 scripts/query_rooms.py -b "丽金" \
  -s "2026-04-20T14:00:00+08:00" \
  -e "2026-04-20T15:00:00+08:00" -o table

# 按容量筛选
python3 scripts/query_rooms.py -b "丽金" \
  -s "2026-04-20T14:00:00+08:00" \
  -e "2026-04-20T15:00:00+08:00" \
  --capacity-gte 8 -o table
```

### manage_preferences.py — 偏好管理

```bash
# 设置偏好
python3 scripts/manage_preferences.py --set \
  --user "ou_xxx" --building "丽金" --capacity-gte 8 \
  --preferred-rooms "F11-07,F11-15" --note "偏好靠近电梯"

# 读取偏好
python3 scripts/manage_preferences.py --get --user "ou_xxx"

# 记录用户选择（自动学习）
python3 scripts/manage_preferences.py --learn \
  --user "ou_xxx" --room "F11-15(8)" --building "丽金智地中心 B座"

# 列出所有偏好
python3 scripts/manage_preferences.py --list
```

### watch_waitlist.py — 候补管理

```bash
# 查看候补状态
python3 scripts/watch_waitlist.py --status

# 执行一轮轮询
python3 scripts/watch_waitlist.py --poll

# 添加候补
python3 scripts/watch_waitlist.py --add \
  --event-id "xxx" --summary "周会" \
  --start "2026-04-20T14:00:00+08:00" --end "2026-04-20T15:00:00+08:00" \
  --building "丽金" --capacity-gte 8

# 移除候补
python3 scripts/watch_waitlist.py --remove --event-id "xxx"

# 清理过期候补
python3 scripts/watch_waitlist.py --clean
```

## 数据文件

| 文件 | 用途 |
|------|------|
| `references/room-mapping.json` | 会议室资源 ID 映射 |
| `references/user-preferences.json` | 用户个人偏好 |
| `references/room-waitlist.json` | 候补预订队列 |

## 核心流程

### 流程 A：查询空闲会议室

用户只想看哪些会议室有空。

1. **解析意图** — 时间段、楼栋、容量需求
2. **确定日期** — ⚠️ 严格验证星期几
3. **执行查询** — `python3 scripts/query_rooms.py -b "楼栋" -s ... -e ... -o table`
4. **呈现结果** — 直接转发脚本输出

### 流程 B：创建会议并自动预订

用户要开会，需要创建日程 + 匹配会议室。

1. **解析意图** — 标题、时间、楼栋、容量、参会人
2. **确定日期** — ⚠️ 严格验证星期几
3. **读取用户偏好** — `python3 scripts/manage_preferences.py --get --user "ou_xxx"`
   - 有偏好时自动填充默认楼栋和容量，不需要每次询问
   - 没有偏好时正常询问
4. **查询空闲会议室** — 用脚本查询，带上容量筛选
5. **用户选择** — `feishu_ask_user_question` 弹卡片
6. **创建日程** — `feishu_calendar_event` create
7. **添加会议室+参会人** — `feishu_calendar_event_attendee` create
   - ⚠️ 字段名是 `attendee_id`，不是 `id`
8. **验证 RSVP** — 等 5 秒后查 attendee list
9. **Fallback** — decline 时自动换下一个空闲会议室
10. **记录选择** — `python3 scripts/manage_preferences.py --learn --user "ou_xxx" --room "F11-15(8)" --building "..."`

### 流程 C：用户偏好管理

用户设置或修改会议室偏好，后续自动应用。

**设置偏好：**
- 用户说"我一般用丽金B座8人以上的会议室"
- 调用 `--set` 写入偏好

**自动学习：**
- 每次流程 B 完成后，调用 `--learn` 记录选择
- 连续 3 次选同一个会议室 → 自动标记为偏好会议室
- 最近 3 次选同一楼栋 → 自动设为默认楼栋

**应用偏好：**
- 流程 B 的 Step 3 自动读取偏好
- 偏好楼栋不匹配时，按偏好查；没空闲时追问是否换楼栋
- 容量需求自动带入查询

### 流程 D：扫描日程自动补订

自动检测用户日程中缺少会议室的会议并补订。

**触发方式：**
- **手动**：用户说"帮我检查一下有没有缺会议室的日程"、"补订会议室"
- **自动**：Heartbeat 定时任务

**扫描步骤：**
1. 调用 `feishu_calendar_event` list 获取用户近期日程（未来 24 小时）
2. 逐个检查：是否有 resource 类型参会人 → 已有会议室则跳过
3. 对没有会议室的线下会议：
   - 读取用户偏好确定默认楼栋和容量
   - 查询空闲会议室
   - 有空闲 → 自动预订（跳过用户确认，因为是补订场景）
   - 全满 → 加入候补队列

**判断是否需要会议室的逻辑：**
- ❌ 跳过：已有 resource 参会人、纯线上视频会议、全天事件、标题含"1:1/线上/phone"
- ✅ 补订：线下会议、有 location 但没有 resource 参会人

### 流程 E：候补轮询

会议室满了时的自动候补机制。

**添加候补：**
- 流程 D 发现全满时，调用 `watch_waitlist.py --add` 加入队列

**轮询检查：**
- Heartbeat 或手动触发 `watch_waitlist.py --poll`
- 对每个 waiting 状态的候补，查询当前时段空闲会议室
- 找到空闲 → 标记为 ready，通知 agent 执行预订
- 仍然满 → 记录已尝试列表，等待下次轮询

**预订成功后：**
- agent 添加会议室 → 验证 RSVP accept → 从候补移除
- decline → 保持 waiting 状态

**清理：**
- 定期 `--clean` 清理已过期的候补（开始时间超过 1 小时）

---

## 交互规范

### 自然语言解析
| 用户说 | 解析 |
|--------|------|
| "明天下午3点开会" | 明天 15:00，默认 1 小时 |
| "找个会议室" | 读取偏好 → 用默认楼栋和容量 |
| "帮我设个偏好，丽金B座8人以上" | 流程 C，设置偏好 |
| "查一下我有没有缺会议室的会" | 流程 D，扫描日程 |
| "候补状态怎么样了" | 流程 E，查看候补 |

### 用户确认原则
- 流程 B（主动创建）：必须确认时间、会议室、参会人
- 流程 D（自动补订）：不需要确认，直接执行
- 流程 E（候补预订）：不需要确认，直接执行

## 注意事项

1. **room_id vs user_id**：freebusy 用 `room_id`，每次只查一个
2. **会议室是 resource**：attendee type 为 `"resource"`，`attendee_id` 传 `omm_xxx`
3. **预订异步**：添加后等 5 秒再查 RSVP
4. **时区统一**：`Asia/Shanghai`（+08:00），ISO 8601
5. **日期验证**：涉及相对时间必须验证星期几
6. **脚本优先**：统一用 scripts/ 下的脚本
7. **时间修改风险**：patch 改时间后会议室可能 decline，必须重新验证
8. **偏好自动学习**：每次预订成功后调用 `--learn` 记录
