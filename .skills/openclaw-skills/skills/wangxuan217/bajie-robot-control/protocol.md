# 八界机器人 WebSocket 通信协议

## 1. 协议说明

- **通信方式**: 基于以太网的 WebSocket 通道
- **数据格式**: JSON
- **用途**: 与任务调度系统一对一通讯
- **连接信息**: `ws://10.10.10.12:9900`

## 2. 协议格式

### 2.1 基础结构

```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": "1234567"
  },
  "body": {
    "name": "navigation",
    "task_id": "navigation_0",
    "data": {}
  }
}
```

**所有字段必须存在**，`data` 内数据类型根据具体协议确定。

### 2.2 Header 字段说明

#### mode (消息模式)
| 值 | 说明 |
|---|---|
| mission | 任务模式 |
| event | 订阅模式 |

#### type (指令类型)
| 值 | 说明 | 是否需要应答 |
|---|---|---|
| request | 请求类 | 必须有 response |
| response | 应答类 | - |
| notify | 通知类 | 无须应答 |

**注意**: 
- `request` 必须有对应的 `response`
- `notify` 无须应答
- `mission` 如果失败，可直接上报 `finish`，可不发 `notify`

#### cmd (具体指令)

**所属 type: request**
| cmd 值 | 说明 | 作用域 | 方向 |
|---|---|---|---|
| start | 任务开始请求 | mode=mission 有效 | client → server |
| pause | 客户端暂停任务 | mode=mission 有效 | client → server |
| resume | 客户端恢复任务 | mode=mission 有效 | client → server |
| cancel | 客户端取消任务 | mode=mission 有效 | client → server |
| subscribe | event 模式下的持续订阅 | mode=event 有效 | client → server |
| unsubscribe | event 模式下的取消订阅 | mode=event 有效 | client → server |
| oneshot | event 模式下的单次订阅 | mode=event 有效 | client → server |

**所属 type: response**
| cmd 值 | 说明 | 作用域 | 方向 |
|---|---|---|---|
| start | 服务端任务开始 response 回复 | mode=mission 有效 | client ↔ server |
| oneshot | event 模式下的单次数据上报 | mode=event 有效 | client ↔ server |

**所属 type: notify**
| cmd 值 | 说明 | 作用域 | 方向 |
|---|---|---|---|
| notify | 服务端 notify，任务过程产生的数据 | mode=mission 有效 | client ← server |
| finish | 服务端任务结束 | mode=mission 有效 | client ← server |
| report | event 模式下的数据持续上报 | mode=event 有效 | client ← server |

#### ts (时间戳)
- 单位：秒 (s)

#### uuid
- 一条指令对应一个 uuid
- 上下文有关联的 mission 共用一个 uuid

### 2.3 Body 字段说明

#### task_id
- 一个请求对应唯一一个 id
- 由客户端生成，请求时下发，响应时带回

#### name
- 当前任务名称

#### data
- 协议具体内容，根据任务类型不同而不同

---

## 3. 协议内容

### 3.1 Event (事件模式)

#### 3.1.1 机器状态订阅

**请求 (client → server)**
```json
{
  "header": {
    "mode": "event",
    "type": "request",
    "cmd": "subscribe",
    "ts": 1620616047,
    "uuid": "xxxx",
    "host": ""
  },
  "body": {
    "name": "robot_info",
    "task_id": "xxxxx",
    "data": {}
  }
}
```

#### 3.1.2 机器状态取消订阅

**请求 (client → server)**
```json
{
  "header": {
    "mode": "event",
    "type": "request",
    "cmd": "unsubscribe",
    "ts": 1620616047,
    "uuid": "xxxx",
    "host": ""
  },
  "body": {
    "name": "robot_info",
    "task_id": "xxxxx",
    "data": {}
  }
}
```

#### 3.1.3 机器状态数据上报

**上报 (client ← server)**
```json
{
  "header": {
    "mode": "event",
    "type": "notify",
    "cmd": "report",
    "ts": 1620616047,
    "uuid": "xxxx",
    "host": ""
  },
  "body": {
    "name": "robot_info",
    "task_id": "xxxxxxx",
    "data": {
      "workState": {
        "name": "",
        "task_id": "",
        "cmd": "",
        "summary": ""
      },
      "ota": true,
      "battery": {
        "isCharge": 0,
        "mode": 3,
        "value": 100
      },
      "alarm": [100, 200, 300],
      "pos": {
        "room": "客厅",
        "x": 1.0,
        "y": 1.0,
        "yaw": 1.0
      },
      "furniture": {
        "info": [
          {
            "fid": "125415",
            "fname": "客厅",
            "mssid": ""
          },
          {
            "fid": "1512454",
            "fname": "餐桌",
            "mssid": "125415"
          }
        ]
      },
      "maintenance_mode": true,
      "gripper_usage_percent": 10
    }
  }
}
```

#### 3.1.4 机器状态单次获取

**请求 (client → server)**
```json
{
  "header": {
    "mode": "event",
    "type": "request",
    "cmd": "oneshot",
    "ts": 1620616047,
    "uuid": "xxxx",
    "host": ""
  },
  "body": {
    "name": "robot_info",
    "task_id": "xxxxxxx",
    "data": {
      "topics": [
        "pos",
        "furniture",
        "battery",
        "ota",
        "workState",
        "alarm",
        "maintenance_mode",
        "gripper_usage_percent"
      ]
    }
  }
}
```

**响应 (client ← server)**
```json
{
  "header": {
    "mode": "event",
    "type": "response",
    "cmd": "oneshot",
    "ts": 1620616047,
    "uuid": "xxxx",
    "host": ""
  },
  "body": {
    "name": "robot_info",
    "task_id": "xxxxxxx",
    "data": {
      "workState": {
        "name": "",
        "task_id": "",
        "cmd": "",
        "summary": ""
      },
      "ota": true,
      "battery": {
        "isCharge": 0,
        "mode": 3,
        "value": 100
      },
      "alarm": [100, 200, 300],
      "pos": {
        "room": "客厅",
        "x": 1.0,
        "y": 1.0,
        "yaw": 1.0
      },
      "furniture": {
        "info": [
          {
            "fid": "125415",
            "fname": "客厅",
            "mssid": ""
          },
          {
            "fid": "1512454",
            "fname": "餐桌",
            "mssid": "125415"
          }
        ]
      },
      "maintenance_mode": true,
      "gripper_usage_percent": 10
    }
  }
}
```

---

### 3.2 Mission (任务模式)

#### 通用格式

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": ""
  },
  "body": {
    "name": "xxxxxxxxx",
    "task_id": "xxxxxxxxxx",
    "data": {}
  }
}
```

**Response**
```json
{
  "header": {
    "mode": "mission",
    "type": "response",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": ""
  },
  "body": {
    "name": "xxxxxxxxx",
    "task_id": "xxxxxxxxx",
    "data": {
      "error_code": {
        "code": 0,
        "module": "",
        "msg": ""
      }
    }
  }
}
```

**Notify**
```json
{
  "header": {
    "mode": "mission",
    "type": "notify",
    "cmd": "notify",
    "ts": 1620616047,
    "uuid": ""
  },
  "body": {
    "name": "xxxxxxxxx",
    "task_id": "xxxxxxxxx",
    "data": {}
  }
}
```

**Finish**
```json
{
  "header": {
    "mode": "mission",
    "type": "notify",
    "cmd": "finish",
    "ts": 1620616047,
    "uuid": ""
  },
  "body": {
    "name": "xxxxxxxxx",
    "task_id": "xxxxxxxxx",
    "data": {
      "error_code": {
        "code": 0,
        "module": "",
        "msg": "",
        "version_info": ""
      }
    }
  }
}
```

---

### 3.2.1 语义导航 (semantic_navigation)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": "xxxxxxxxxxx"
  },
  "body": {
    "name": "semantic_navigation",
    "user_id": "xxxxxx",
    "task_id": "semantic_navigation_0",
    "data": {
      "goal": "客厅",
      "goal_id": ""
    }
  }
}
```

**说明**:
- `goal`: 区域或者家具名称
- `goal_id`: 区域或者家具 id，可以为空

---

### 3.2.2 建图 (map_create)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": "123qwe"
  },
  "body": {
    "name": "map_create",
    "task_id": "map_create_0",
    "data": {}
  }
}
```

---

### 3.2.3 控制机器人移动 (chassis_move)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "chassis_move",
    "task_id": "chassis_move_0",
    "data": {
      "move_distance": 0.1,
      "move_angle": 0.0
    }
  }
}
```

**说明**:
- `move_distance`: 移动距离，单位 m，正值表示前进，负值表示后退
- `move_angle`: 旋转角度，单位 rad，正值表示顺时针，负值表示逆时针

**示例**: 向前 10cm → `move_distance: 0.1`

---

### 3.2.4 找人 (find_person)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": "45435465"
  },
  "body": {
    "name": "find_person",
    "task_id": "find_person_0",
    "data": {
      "user_name": "张三",
      "user_id": "",
      "area_info": [
        {
          "area_id": "",
          "area_name": "客厅"
        }
      ]
    }
  }
}
```

---

### 3.2.5 精准抓取 (accurate_grab)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": "452348564"
  },
  "body": {
    "name": "accurate_grab",
    "task_id": "accurate_grab_0",
    "data": {
      "object": {
        "rag_id": "",
        "item": "玩具",
        "color": "",
        "shape": "",
        "person": ""
      },
      "position": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0
      },
      "orientation": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0,
        "w": 4.0
      },
      "box_length": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0
      },
      "frame_id": "map"
    }
  }
}
```

---

### 3.2.7 推荐放置 (semantic_place)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": "5435214654"
  },
  "body": {
    "name": "semantic_place",
    "task_id": "semantic_place_0",
    "data": {
      "area_id": "",
      "area_name": "收纳筐",
      "object_name": "玩具",
      "direction": "里"
    }
  }
}
```

**说明**:
- `direction`: 里，上

---

### 3.2.10 整理物品 (restore)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "restore",
    "task_id": "restore_0",
    "data": {
      "name": "SortDesk",
      "area_info": {
        "area_name": "桌子",
        "area_id": ""
      },
      "object_info": {
        "object_name": ""
      }
    }
  }
}
```

**说明**:
- `name`: `SortDesk` 或 `SortShoes`

---

### 3.2.11 搜索物体 (search)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": "4d54sa54d"
  },
  "body": {
    "name": "search",
    "task_id": "search_0",
    "data": {
      "object": {
        "item": "玩具",
        "color": "",
        "shape": "",
        "person": ""
      },
      "area": {
          "area_id": "",
          "area_name": "玩具收纳区"
        }
    }
  }
}
```

**Notify (找到物体的 6D pose)**
```json
{
  "header": {
    "mode": "mission",
    "type": "notify",
    "cmd": "notify",
    "ts": 1620616047
  },
  "body": {
    "name": "search",
    "task_id": "search_0",
    "data": {
      "position": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0
      },
      "orientation": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0,
        "w": 4.0
      },
      "box_length": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0
      },
      "frame_id": "map"
    }
  }
}
```

---

### 3.2.12 回充 (recharge)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047,
    "uuid": "4s65465s"
  },
  "body": {
    "name": "recharge",
    "task_id": "recharge_0",
    "data": {}
  }
}
```

---

### 3.2.13 托盘抓取 (tray_grab)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "tray_grab",
    "task_id": "tray_grab_0",
    "data": {
      "item": ""
    }
  }
}
```

---

### 3.2.14 托盘放置 (tray_place)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "tray_place",
    "task_id": "tray_place_0",
    "data": {}
  }
}
```

---

### 3.2.15 机身准备姿态 (robot_prepare_pose)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "robot_prepare_pose",
    "task_id": "robot_prepare_pose_0",
    "data": {
      "mission_summary": ""
    }
  }
}
```

---

### 3.2.16 机身结束姿态 (robot_ending_pose)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "robot_ending_pose",
    "task_id": "robot_ending_pose_0",
    "data": {}
  }
}
```

---

### 3.2.17 机身高度控制 (robot_height_ctrl)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "robot_height_ctrl",
    "task_id": "robot_height_ctrl_0",
    "data": {
      "mode": 1
    }
  }
}
```

**说明**:
- `mode`: 高度模式
  - `1` = 置顶（升到最高）
  - `2` = 置底（降到最低）

**示例**: 升到最高 → `mode: 1`

---

### 3.2.20 搜索放置容器 (search_container)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "search_container",
    "task_id": "search_container_0",
    "data": {
      "object": {
        "item": "",
        "color": "",
        "shape": "",
        "person": ""
      },
      "area": {
          "area_id": "",
          "area_name": ""
        }
    }
  }
}
```

---

### 3.2.21 衣物抓取 (grab_clothes)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "grab_clothes",
    "task_id": "grab_clothes_0",
    "data": {
      "object": {
        "rag_id": "",
        "item": "",
        "color": "",
        "shape": "",
        "person": ""
      },
      "position": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0
      },
      "orientation": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0,
        "w": 4.0
      },
      "box_length": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0
      },
      "frame_id": "map"
    }
  }
}
```

---

### 3.2.22 导航到洗衣机并将夹爪上衣物放进洗衣机 (put_clothes)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "put_clothes",
    "task_id": "put_clothes_0",
    "data": {}
  }
}
```

---

### 3.2.23 导航到洗衣机并打开洗衣机 (open_device_door)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "open_device_door",
    "task_id": "open_device_door_0",
    "data": {}
  }
}
```

---

### 3.2.24 导航到洗衣机，关上洗衣机，按按钮启动 (close_device_door)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "close_device_door",
    "task_id": "close_device_door_0",
    "data": {}
  }
}
```

---

### 3.2.26 定点导航 (point_navigation)

**Request**
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "start",
    "ts": 1620616047
  },
  "body": {
    "name": "point_navigation",
    "task_id": "point_navigation_0",
    "data": {
      "goal": "",
      "goal_id": ""
    }
  }
}
```

---

## 4. 任务控制指令

### 4.1 暂停任务
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "pause",
    "ts": 1620616047,
    "uuid": "xxxxxxxxxxx"
  },
  "body": {
    "name": "semantic_navigation",
    "task_id": "semantic_navigation_0",
    "data": {}
  }
}
```

### 4.2 恢复任务
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "resume",
    "ts": 1620616047,
    "uuid": "xxxxxxxxxxx"
  },
  "body": {
    "name": "semantic_navigation",
    "task_id": "semantic_navigation_0",
    "data": {}
  }
}
```

### 4.3 取消任务
```json
{
  "header": {
    "mode": "mission",
    "type": "request",
    "cmd": "cancel",
    "ts": 1620616047,
    "uuid": "xxxxxxxxxxx"
  },
  "body": {
    "name": "semantic_navigation",
    "task_id": "semantic_navigation_0",
    "data": {}
  }
}
```
