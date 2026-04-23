# 八界机器人控制脚本库

本目录包含所有与八界机器人控制相关的 Python 脚本。

## 目录结构

```
scripts/
├── bajie_robot.py              # 核心机器人控制客户端库
├── map_create_optimized.py     # 建图脚本
├── reset_arm.py                # 机械臂复位脚本
├── navigate_living_room.py     # 导航测试脚本
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

## 核心库

### bajie_robot.py
机器人控制核心客户端库，提供：
- WebSocket 连接管理
- 任务请求构建与发送
- 响应解析与错误处理
- 状态订阅与监听

**使用示例：**
```python
from bajie_robot import BajieRobot

robot = BajieRobot("ws://10.10.10.12:9900")
await robot.connect()

# 获取状态
status = await robot.get_robot_status()
print(f"电量：{status['battery']['value']}%")

# 执行任务
await robot.semantic_navigation(goal="客厅")
await robot.accurate_grab(object={"item": "玩具"}, position=..., orientation=...)

await robot.disconnect()
```

## 快速调用指南

### 查询机器人状态
```bash
python3 scripts/bajie_robot.py --action status
```

### 导航到指定位置
```bash
python3 scripts/navigate_living_room.py
```

### 整理玩具
```bash
python3 scripts/cleanup_toys_simple.py
```

### 搜索并抓取物体
```bash
python3 scripts/search_and_grab.py
```

### 机械臂复位
```bash
python3 scripts/reset_arm.py
```

### 建图
```bash
python3 scripts/map_create_optimized.py
```

## 依赖安装

```bash
pip3 install websockets
```

## 注意事项

1. 所有脚本需要 Python 3.7+
2. 确保机器人在同一网络（10.10.10.x）
3. 运行脚本前确认机器人电量充足（>30%）
4. 尊重即停把手安全机制
