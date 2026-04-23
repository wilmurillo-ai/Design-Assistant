# 八界机器人控制技能 (bajie-robot-control)

## 技能描述

本技能提供八界具身智能机器人的本体控制能力，通过 WebSocket 协议与机器人进行通信，执行导航、抓取、放置、回充等任务。

## 激活条件

当用户请求涉及以下操作时激活本技能：
- 移动/导航到某个位置
- 抓取/放置物品
- 寻找人或物体
- 回充/充电
- 查询机器人状态
- 控制机械臂操作

## 连接配置

```python
WEBSOCKET_URL = "ws://10.10.10.12:9900"
```

## 核心能力

### 1. 任务执行 (Mission)

所有任务遵循 request → response → (notify) → finish 流程。

#### 任务类型

| 任务名称 | 功能 | 关键参数 |
|---|---|---|
| semantic_navigation | 语义导航 | goal(区域名), goal_id |
| map_create | 建图 | 无 |
| chassis_move | 底盘移动 | move_distance, move_angle |
| find_person | 找人 | user_name, area_info |
| accurate_grab | 精准抓取 | object, position, orientation |
| semantic_place | 推荐放置 | area_name, object_name, direction |
| search | 搜索物体 | object, area_info |
| recharge | 回充 | 无 |
| tray_grab | 托盘抓取 | item |
| tray_place | 托盘放置 | 无 |
| restore | 整理物品 | name(SortDesk/SortShoes), area_info |

### 2. 状态订阅 (Event)

订阅机器人实时状态：
- 电量 (battery)
- 位置 (pos)
- 工作状态 (workState)
- 异常报警 (alarm)
- 家具地图 (furniture)

### 3. 错误处理

根据错误码等级处理：
- **等级 0**: 成功
- **等级 1**: 可恢复错误 → 重试 1-3 次
- **等级 3**: 严重错误 → 环境分析 + 清除障碍 + 重试

## 使用流程

### 步骤 1: 生成任务 ID
```python
import uuid
task_id = f"{task_name}_{uuid.uuid4().hex[:8]}"
```

### 步骤 2: 构建请求
```python
import time

request = {
    "header": {
        "mode": "mission",
        "type": "request",
        "cmd": "start",
        "ts": int(time.time()),
        "uuid": str(uuid.uuid4())
    },
    "body": {
        "name": task_name,
        "task_id": task_id,
        "data": task_data
    }
}
```

### 步骤 3: 发送并等待响应
```python
# 发送 WebSocket 消息
await websocket.send(json.dumps(request))

# 等待 response
response = await websocket.recv()
error_code = response["body"]["data"]["error_code"]["code"]

if error_code != 0:
    # 处理错误
    handle_error(error_code)
```

### 步骤 4: 监听任务完成
```python
# 等待 finish 消息
while True:
    msg = await websocket.recv()
    if msg["header"]["cmd"] == "finish":
        break
    elif msg["header"]["cmd"] == "notify":
        # 处理任务进度通知
        handle_notify(msg)
```

## 安全规则

### 最高优先级：即停把手
- 当用户握住即停把手时，**立即暂停所有移动**
- 松手后恢复运行
- 这是硬件级安全机制，软件必须尊重

### 电量管理
- 电量 < 30% 时，自动触发回充任务
- 除非用户有紧急指令干预

### 避障
- 移动时持续监测 LDS 激光雷达数据
- 检测到障碍物时自动停止
- 错误码 0x00007004 表示路径被阻挡，需清除障碍

## 复杂任务编排

复杂任务通过原子能力串联实现。

### 示例：整理桌子
```python
async def organize_desk():
    # 1. 准备姿态
    await robot_prepare_pose("整理桌子")
    
    # 2. 导航到桌子
    await semantic_navigation(goal="桌子")
    
    # 3. 搜索桌上物品
    search_result = await search(object={"item": ""}, area_info=[{"area_name": "桌子"}])
    
    # 4. 抓取物品
    for item in search_result["objects"]:
        await accurate_grab(
            object={"item": item["name"]},
            position=item["position"],
            orientation=item["orientation"]
        )
        
        # 5. 放置到收纳区
        await semantic_place(
            area_name="收纳筐",
            object_name=item["name"],
            direction="里"
        )
    
    # 6. 结束姿态
    await robot_ending_pose()
```

### 示例：洗衣任务
```python
async def do_laundry():
    # 1. 抓取衣物
    await grab_clothes(object={"item": "脏衣服"})
    
    # 2. 导航到洗衣机
    await semantic_navigation(goal="洗衣机")
    
    # 3. 打开洗衣机门
    await open_device_door()
    
    # 4. 放入衣物
    await put_clothes()
    
    # 5. 关闭洗衣机门并启动
    await close_device_door()
```

## 错误码处理策略

```python
ERROR_HANDLERS = {
    # 导航相关
    0x00007002: "全局规划失败 - 检查起始位置障碍物",
    0x00007003: "目标点不可达 - 重试或更换目标点",
    0x00007004: "路径被阻挡 - 清除可移动障碍物后重试",
    
    # 机械臂相关
    0x00009002: "轨迹规划失败 - 检查碰撞检测",
    0x00009006: "逆解失败 - 重新观测生成抓取位姿",
    0x00009021: "未抓到物体 - 重新尝试或报告用户",
    
    # 回充相关
    0x000028b0: "电量过低 - 立即回充",
    0x00033000: "上桩超时 - 检查充电桩位置",
    0x00033001: "找不到充电桩 - 重新定位后重试",
    
    # 寻物相关
    0x00019004: "无法找到物体 - 扩大搜索范围或报告用户",
}

def handle_error(error_code):
    if error_code in ERROR_HANDLERS:
        log(f"错误处理：{ERROR_HANDLERS[error_code]}")
        # 执行对应处理策略
    else:
        log(f"未知错误码：{error_code}")
        # 通用错误处理
```

## 状态查询

### 订阅机器状态
```python
subscribe_request = {
    "header": {
        "mode": "event",
        "type": "request",
        "cmd": "subscribe",
        "ts": int(time.time()),
        "uuid": str(uuid.uuid4())
    },
    "body": {
        "name": "robot_info",
        "task_id": "subscribe_001",
        "data": {}
    }
}
```

### 单次获取状态
```python
oneshot_request = {
    "header": {
        "mode": "event",
        "type": "request",
        "cmd": "oneshot",
        "ts": int(time.time()),
        "uuid": str(uuid.uuid4())
    },
    "body": {
        "name": "robot_info",
        "task_id": "oneshot_001",
        "data": {
            "topics": ["pos", "battery", "workState", "alarm"]
        }
    }
}
```

## 任务控制

### 暂停任务
```python
pause_request = {
    "header": {
        "mode": "mission",
        "type": "request",
        "cmd": "pause",
        "ts": int(time.time()),
        "uuid": task_uuid
    },
    "body": {
        "name": task_name,
        "task_id": task_id,
        "data": {}
    }
}
```

### 恢复任务
```python
resume_request = {
    "header": {
        "mode": "mission",
        "type": "request",
        "cmd": "resume",
        "ts": int(time.time()),
        "uuid": task_uuid
    },
    "body": {
        "name": task_name,
        "task_id": task_id,
        "data": {}
    }
}
```

### 取消任务
```python
cancel_request = {
    "header": {
        "mode": "mission",
        "type": "request",
        "cmd": "cancel",
        "ts": int(time.time()),
        "uuid": task_uuid
    },
    "body": {
        "name": task_name,
        "task_id": task_id,
        "data": {}
    }
}
```

## 最佳实践

1. **任务 ID 唯一性**: 每个请求生成唯一的 task_id
2. **UUID 关联**: 同一任务的所有消息共用同一个 uuid
3. **超时处理**: 所有请求设置合理超时 (建议 30-60 秒)
4. **错误重试**: 等级 1 错误重试 1-3 次，等级 3 错误先分析环境
5. **状态反馈**: 通过语音和屏幕实时反馈任务进展
6. **电量监控**: 持续监控电量，<30% 优先回充

## 文件结构

```
bajie-robot-control/
├── SKILL.md                 # 本技能说明文件
├── protocol.md              # 完整 WebSocket 通信协议
├── protocol_flow.md         # 协议流程图示
├── error_code.md            # 错误码详细说明
├── MAP_CREATE_README.md     # 建图功能说明
└── scripts/                 # Python 脚本代码目录
    ├── bajie_robot.py       # 核心机器人控制客户端库
    ├── map_create_optimized.py  # 建图脚本
    ├── reset_arm.py         # 机械臂复位脚本
    ├── navigate_living_room.py  # 导航测试脚本
    │
    ├── 任务脚本/
    │   ├── cleanup_toys_multi.py      # 多区域玩具整理
    │   ├── cleanup_toys_multi_v2.py   # 多区域整理 v2
    │   ├── cleanup_toys_simple.py     # 简单整理脚本
    │   ├── cleanup_toys_task.py       # 整理任务脚本
    │   └── cleanup_toys_v2~v7.py      # 整理脚本迭代版本
    │
    ├── 搜索与抓取/
    │   ├── search_and_grab.py         # 搜索并抓取
    │   ├── search_move_grab.py        # 搜索移动抓取
    │   └── test_grab_with_search_data.py  # 带搜索数据抓取测试
    │
    └── 测试脚本/
        ├── test_connection.py         # 连接测试
        ├── test_full_task.py          # 完整任务测试
        ├── test_map_create_final.py   # 建图测试
        ├── test_mapping.py            # 地图测试
        ├── test_move.py               # 移动测试
        ├── test_place_fixed.py        # 放置测试
        ├── test_restore.py            # 整理测试
        ├── test_search_basket.py      # 搜索篮子测试
        ├── test_search_full.py        # 完整搜索测试
        └── test_unique_task_id.py     # 任务 ID 唯一性测试
```

## 相关文件

### 核心文档
- [`protocol.md`](./protocol.md) - 完整 WebSocket 通信协议
- [`protocol_flow.md`](./protocol_flow.md) - 协议流程图示
- [`error_code.md`](./error_code.md) - 错误码详细说明
- [`MAP_CREATE_README.md`](./MAP_CREATE_README.md) - 建图功能说明

### 脚本代码 (scripts/)
- **核心库**: [`bajie_robot.py`](./scripts/bajie_robot.py) - Python 客户端实现
- **建图**: [`map_create_optimized.py`](./scripts/map_create_optimized.py)
- **机械臂复位**: [`reset_arm.py`](./scripts/reset_arm.py)
- **导航测试**: [`navigate_living_room.py`](./scripts/navigate_living_room.py)
- **整理任务**: `cleanup_toys_*.py` 系列脚本
- **搜索抓取**: `search_and_grab.py`, `search_move_grab.py`
- **测试脚本**: `test_*.py` 系列脚本

## 注意事项

1. 所有 header 字段必须存在
2. data 字段根据具体协议确定内容
3. request 必须有对应的 response
4. mission 模式失败可直接上报 finish，可不发 notify
5. 尊重即停把手的最高优先级安全机制
6. 在上一次请求没有返回finish的时候，一定不能开始下一次请求
7. 任务finish为失败时若尝试其他解决方法，最多再尝试1次，如果finish仍然为失败就直接结束并告知两次失败的原因，等待接受新的指令
