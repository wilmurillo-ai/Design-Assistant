# feishu-room-booking

飞书会议室智能查询与预订 Skill，支持自然语言交互完成会议室查询、预订、偏好管理和自动补订。

## 功能

- 🔍 查询任意楼栋的空闲会议室
- 📅 自动创建日程并预订会议室
- 👤 个人偏好记忆与自动学习
- 🔄 缺会议室日程自动扫描补订
- ⏳ 会议室满时自动候补轮询

## 快速开始

### 1. 安装

```bash
# ClawHub 安装
clawhub install feishu-room-booking

# 或手动安装：将整个目录复制到你的 OpenClaw skills 目录
```

### 2. 环境要求

| 依赖 | 说明 |
|------|------|
| OpenClaw | Agent 运行框架 |
| lark-cli | `npm install -g lark-cli` |
| Python 3.8+ | 运行查询脚本 |

### 3. 飞书应用权限

创建企业自建应用，开通以下权限：

**应用权限：**
- `calendar:calendar.free_busy:read`
- `calendar:calendar.event:create`
- `calendar:calendar.event:read`
- `calendar:calendar.event.attendee:create`
- `calendar:calendar:read`

**用户权限：**
- `calendar:calendar.event:create`
- `calendar:calendar.event:read`
- `calendar:calendar.free_busy:read`
- `calendar:calendar.event.attendee:create`
- `calendar:calendar.event.attendee:read`

> ⚠️ 修改权限后必须创建新版本并发布，且需要用户完成 OAuth 授权。

### 4. 认证配置

```bash
lark-cli config init                    # 配置应用
lark-cli auth login --no-wait --recommend  # 用户授权
lark-cli auth status                     # 验证
```

### 5. 配置会议室映射

将 `references/room-mapping.example.json` 复制为 `references/room-mapping.json`，填入你公司的会议室数据：

```json
{
  "buildings": [
    {
      "name": "你的办公楼",
      "alias": ["别名1", "别名2"],
      "rooms": [
        {
          "name": "301会议室(8)",
          "room_id": "omm_xxxxxxxxxx",
          "capacity": 8
        }
      ]
    }
  ]
}
```

**获取 room_id 的方法：**
- 查看已有日程中的会议室参会人（`type: "resource"` 的 `room_id`）
- 飞书日历 → 会议室 → 查看详情
- 调用飞书会议室搜索 API（需 `vc:room:search` 权限）

### 6. 验证

```bash
python3 scripts/query_rooms.py --list-buildings
python3 scripts/query_rooms.py -b "楼栋关键词" -s "开始时间" -e "结束时间" -o table
```

## 使用示例

```
# 查询空闲会议室
"帮我查一下丽金11楼明天下午的空闲会议室"

# 创建会议并预订
"明天下午3点开会，参会人我、李楠、陈科"

# 按容量筛选
"找个8人以上的会议室"

# 设置偏好
"我一般用丽金B座8人以上的会议室"

# 扫描补订
"帮我检查有没有缺会议室的日程"
```

## 目录结构

```
feishu-room-booking/
├── SKILL.md                           # 核心指令（5 个流程）
├── README.md                          # 本文件
├── scripts/
│   ├── query_rooms.py                 # 会议室查询（模糊匹配+批量忙闲）
│   ├── manage_preferences.py          # 偏好管理（设置/读取/自动学习）
│   ├── scan_events.py                 # 扫描缺会议室日程
│   └── watch_waitlist.py              # 候补轮询
└── references/
    ├── room-mapping.json              # 会议室映射（需要配置！）
    ├── room-mapping.example.json      # 映射示例
    ├── user-preferences.json          # 用户偏好（自动生成）
    └── room-waitlist.json             # 候补队列（自动生成）
```

## 常见问题

| 问题 | 解决 |
|------|------|
| user token 过期 | `lark-cli auth login --no-wait --recommend` |
| freebusy 报 invalid parameters | 确认用 `room_id` 字段而非 `user_ids` |
| 创建日程后看不到 | 确保传了 `user_open_id` |
| 会议室 decline | 时间冲突，检查 room_id 是否正确 |
| 日期算错 | Skill 会自动验证星期几 |

## License

MIT
