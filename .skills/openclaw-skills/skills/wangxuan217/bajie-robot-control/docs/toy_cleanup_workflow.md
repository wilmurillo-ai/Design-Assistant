# 🧸 玩具收纳任务工作流 (v2 - 使用 search_container)

## 一、整体流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    玩具收纳任务 (Toy Cleanup)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤 0: robot_prepare_pose                                      │
│  机身准备姿态，mission_summary: "玩具收纳"                        │
│  协议：request → response → finish                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤 1: search_container (搜索收纳筐)                            │
│  目标：收纳筐 @ 客厅                                              │
│  参数：object + area_info (与 search 一致)                        │
│  协议：request → response → (notify: 位置) → finish              │
│  说明：找到容器后，系统会自动记录，后续 search 会过滤容器内物体    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤 2: 循环收拾玩具 (主循环)                                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  2.1 搜索玩具 (search) @ 多区域                             │  │
│  │      搜索区域：["地上", "地板", "地面", "地毯", "角落"]      │  │
│  │      输出：玩具位置 + 6D 位姿                                │  │
│  │      说明：系统自动过滤收纳筐内的玩具，无需手动检查          │  │
│  │                           │                                │  │
│  │                           ▼                                │  │
│  │  2.2 判断是否找到玩具                                        │  │
│  │      ├─ 未找到 → 计数器 +1                                  │  │
│  │      └─ 找到 → 执行抓取放置                                 │  │
│  │                           │                                │  │
│  │                           ▼                                │  │
│  │  2.3 accurate_grab                                          │  │
│  │      使用搜索返回的 position/orientation/box_length        │  │
│  │                           │                                │  │
│  │                           ▼                                │  │
│  │  2.4 semantic_place                                         │  │
│  │      放置目标：收纳筐，direction: "里"                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│                    连续 3 次没找到？                                │
│                    └─ 是 → 退出循环                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤 3: robot_ending_pose                                       │
│  机身结束姿态，机械臂归位                                         │
│  协议：request → response → finish                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                          ✅ 任务完成
```

---

## 二、协议交互细节

### 2.1 通用请求格式
```python
{
    "header": {
        "mode": "mission",
        "type": "request",
        "cmd": "start",
        "ts": int(time.time()),
        "uuid": "统一 UUID"  # 整个任务链共用
    },
    "body": {
        "name": "任务名称",
        "task_id": "独立 ID",  # 每个子任务独立
        "data": { ... }
    }
}
```

### 2.2 标准响应流程
```
Client → Server: request (cmd=start)
Server → Client: response (cmd=start, error_code)
Server → Client: notify x N (可选，包含中间数据如位置)
Server → Client: finish (cmd=finish, error_code)
```

### 2.3 关键任务协议

#### robot_prepare_pose
```python
{
    "name": "robot_prepare_pose",
    "data": {"mission_summary": "玩具收纳"}
}
```

#### search_container (搜索容器) ⭐ 更新
```python
{
    "name": "search_container",
    "data": {
        "object": {
            "item": "收纳筐",
            "color": "",
            "shape": "",
            "person": ""
        },
        "area_info": [
            {
                "area_id": "",
                "area_name": "客厅"
            }
        ]
    }
}
# notify 返回：position, orientation, box_length, frame_id
# 系统会自动记录容器位置，后续 search 会过滤容器内物体
```

#### search (搜索物体)
```python
{
    "name": "search",
    "data": {
        "object": {
            "item": "玩具",
            "color": "",
            "shape": "",
            "person": ""
        },
        "area_info": [
            {
                "area_id": "",
                "area_name": "地上"
            }
        ]
    }
}
# notify 返回：position, orientation, box_length, frame_id
# 系统自动过滤已在容器内的物体
```

#### accurate_grab (精准抓取)
```python
{
    "name": "accurate_grab",
    "data": {
        "object": {"item": "玩具", ...},
        "position": {"x": 1.0, "y": 2.0, "z": 3.0},
        "orientation": {"x": 1.0, "y": 2.0, "z": 3.0, "w": 4.0},
        "box_length": {"x": 0.1, "y": 0.1, "z": 0.1},
        "frame_id": "map"
    }
}
```

#### semantic_place (推荐放置)
```python
{
    "name": "semantic_place",
    "data": {
        "area_id": "",
        "area_name": "收纳筐",
        "object_name": "玩具",
        "direction": "里"
    }
}
```

---

## 三、核心算法逻辑

### 3.1 循环终止条件
```python
consecutive_not_found >= 3  # 连续 3 次没找到 → 任务完成
loop_count >= MAX_LOOPS     # 安全保护（默认 50 次）
```

### 3.2 简化后的主循环
```python
while loop_count < MAX_LOOPS:
    # 搜索玩具（系统自动过滤收纳筐内的）
    toy_data = await search_multi_area(ws, "玩具", SEARCH_AREAS)
    
    if not toy_data:
        consecutive_not_found += 1
        if consecutive_not_found >= 3:
            break  # 确认没有玩具了
    else:
        consecutive_not_found = 0  # 重置计数器
        # 直接抓取，无需位置检查
        await accurate_grab(ws, toy_data)
        await semantic_place(ws, "玩具", "收纳筐")
```

---

## 四、错误处理策略

| 错误场景 | 错误码 | 处理策略 |
|---------|--------|---------|
| search_container 失败 | 0x00019004 | 使用默认容器，继续任务 |
| 搜索失败 | 0x00019004 | 扩大搜索区域，重试 |
| 抓取失败 | 0x00009021 | 重新观测，重试 1 次 |
| 放置失败 | 0x00009015 | 检查托盘/收纳筐状态 |
| 导航被阻挡 | 0x00007004 | 清除障碍物后重试 |
| 电量过低 | 0x000028b0 | 暂停任务，触发回充 |

---

## 五、关键设计要点

### ✅ v2 改进
1. **使用 search_container** - 专用接口搜索容器
2. **参数格式统一** - object + area_info 与 search 一致
3. **移除位置检查** - 系统自动过滤容器内物体，简化逻辑
4. **移除距离计算** - 不再需要 calculate_distance/is_toy_in_basket
5. **移除位置去重** - 系统自动处理，无需 processed_positions

### ✅ 保留
1. **统一 UUID** - 整个任务链共用一个 uuid，共享上下文
2. **独立 task_id** - 每个子任务有唯一标识
3. **严格等待 finish** - 每个任务必须等待 finish 后才执行下一步
4. **连续跳过检测** - 连续 3 次跳过确认任务完成
5. **机械臂归位** - 任务结束执行 ending_pose

---

## 六、任务统计输出

```
📊 任务统计:
├─ 收拾玩具数量：X 个
├─ 循环次数：N 次
└─ 连续未找到次数：3 次 (确认完成)
```

---

## 七、执行流程示例

```
时间：2026-03-10 09:30:00
连接：ws://10.10.10.12:9900
统一 uuid: abc12345-xxxx-xxxx-xxxx-xxxxxxxxxxxx

✅ 已连接到机器人

【准备】robot_prepare_pose
✓ 准备姿态任务启动成功
✅ 准备姿态完成：0x00000000 - SUCCESS

【步骤 1】搜索收纳筐 (search_container)
✓ search_container 任务启动成功
📍 找到收纳筐：位置={x: 1.5, y: 2.0, z: 0.1}
✅ search_container 完成：0x00000000 - SUCCESS
💾 系统已记录容器位置，后续 search 将自动过滤

【步骤 2】循环收拾玩具
═══════════════════════════════════════════════════════════
【第 1 次循环】
【搜索】玩具 @ 地上
✓ search 任务启动成功
📍 找到玩具：位置={x: 0.8, y: 1.2, z: 0.05}
✅ search 完成：0x00000000 - SUCCESS
【抓取】玩具
✓ accurate_grab 任务启动成功
✅ accurate_grab 完成：0x00000000 - SUCCESS
【放置】玩具 → 收纳筐
✓ semantic_place 任务启动成功
✅ semantic_place 完成：0x00000000 - SUCCESS
📊 已收拾：1 个

【第 2 次循环】
【搜索】玩具 @ 地上
✓ search 任务启动成功
📍 找到玩具：位置={x: 1.0, y: 1.5, z: 0.05}
✅ search 完成：0x00000000 - SUCCESS
【抓取】玩具
✓ accurate_grab 任务启动成功
✅ accurate_grab 完成：0x00000000 - SUCCESS
【放置】玩具 → 收纳筐
✓ semantic_place 任务启动成功
✅ semantic_place 完成：0x00000000 - SUCCESS
📊 已收拾：2 个

【第 3 次循环】
【搜索】玩具 @ 地上
✓ search 任务启动成功
✅ search 完成：0x00019004 - 无法找到物体
🔍 没有找到玩具（连续 1/3 次）

【第 4 次循环】
【搜索】玩具 @ 地板
✓ search 任务启动成功
✅ search 完成：0x00019004 - 无法找到物体
🔍 没有找到玩具（连续 2/3 次）

【第 5 次循环】
【搜索】玩具 @ 地面
✓ search 任务启动成功
✅ search 完成：0x00019004 - 无法找到物体
🔍 没有找到玩具（连续 3/3 次）
✅ 确认地上没有需要收拾的玩具了！

【步骤 3】机械臂归位
✓ 结束姿态任务启动成功
✅ 结束姿态完成：0x00000000 - SUCCESS

═══════════════════════════════════════════════════════════
✅ 任务完成！
📊 共收拾了 2 个玩具
═══════════════════════════════════════════════════════════
```

---

## 八、与 v1 的对比

| 项目 | v1 (旧版) | v2 (新版) |
|------|-----------|-----------|
| 容器搜索 | search | search_container ⭐ |
| 容器参数 | area (单对象) | area_info (数组) ⭐ |
| 位置检查 | 手动计算距离 | 系统自动过滤 ⭐ |
| 位置去重 | 需要 processed_positions | 无需 ⭐ |
| 代码复杂度 | 较高 | 简化 ⭐ |
| 可靠性 | 依赖手动逻辑 | 依赖系统逻辑 ⭐ |

---

**版本：** v2  
**更新日期：** 2026-03-10  
**主要改进：** 使用 search_container 接口，系统自动过滤容器内物体
