# 八界机器人 WebSocket 通信协议流程图

## 1. 协议基础结构

```mermaid
graph TB
    subgraph 消息结构
        Msg[WebSocket 消息] --> Header[Header 头部]
        Msg --> Body[Body 主体]
        
        Header --> Mode[mode: mission/event]
        Header --> Type[type: request/response/notify]
        Header --> Cmd[cmd: 具体指令]
        Header --> TS[ts: 时间戳]
        Header --> UUID[uuid: 唯一标识]
        
        Body --> Name[name: 任务名称]
        Body --> TaskID[task_id: 任务 ID]
        Body --> Data[data: 任务数据]
    end
```

## 2. 两种通信模式

```mermaid
graph TB
    subgraph Event 模式 - 事件订阅
        EM[mode: event] --> Subscribe[subscribe 订阅]
        EM --> Unsubscribe[unsubscribe 取消订阅]
        EM --> Oneshot[oneshot 单次获取]
        EM --> Report[report 持续上报]
    end
    
    subgraph Mission 模式 - 任务执行
        MM[mode: mission] --> Start[start 任务开始]
        MM --> Pause[pause 暂停]
        MM --> Resume[resume 恢复]
        MM --> Cancel[cancel 取消]
        MM --> Notify[notify 过程通知]
        MM --> Finish[finish 任务结束]
    end
```

## 3. Mission 模式任务流程

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant Server as 服务端
    
    Client->>Server: request/start (任务开始)
    Server-->>Client: response/start (确认开始)
    
    loop 任务执行中
        Server-->>Client: notify (过程数据)
    end
    
    Server-->>Client: notify/finish (任务结束)
    
    Note over Client,Server: 可随时发送 pause/resume/cancel
```

## 4. Event 模式数据流

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant Server as 服务端
    
    Client->>Server: request/subscribe (订阅)
    Server-->>Client: response (确认订阅)
    
    loop 持续上报
        Server-->>Client: notify/report (状态数据)
    end
    
    Client->>Server: request/unsubscribe (取消订阅)
```

## 5. 任务类型总览

```mermaid
mindmap
  root((八界机器人任务))
    导航类
      semantic_navigation 语义导航
      point_navigation 定点导航
      chassis_move 底盘移动
    建图类
      map_create 建图
    抓取类
      accurate_grab 精准抓取
      tray_grab 托盘抓取
      grab_clothes 衣物抓取
    放置类
      semantic_place 推荐放置
      tray_place 托盘放置
    搜索类
      search 搜索物体
      search_container 搜索容器
      find_person 找人
    设备交互
      open_device_door 开洗衣机门
      close_device_door 关洗衣机门并启动
      put_clothes 放衣物进洗衣机
    系统类
      recharge 回充
      restore 整理物品
      robot_prepare_pose 准备姿态
      robot_ending_pose 结束姿态
    事件订阅
      robot_info 机器状态订阅
```

## 6. 完整通信示例 - 语义导航

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant Server as 服务端
    
    Client->>Server: {header: {mode:mission,type:request,cmd:start},<br/>body: {name:semantic_navigation,goal:客厅}}
    Server-->>Client: {header: {mode:mission,type:response,cmd:start},<br/>body: {error_code: {code:0}}}
    
    loop 导航中
        Server-->>Client: {header: {mode:mission,type:notify,cmd:notify},<br/>body: {pos: {x,y,yaw}, room:客厅}}
    end
    
    Server-->>Client: {header: {mode:mission,type:notify,cmd:finish},<br/>body: {error_code: {code:0}}}
```

## 7. 连接信息

- **WebSocket 地址**: `ws://10.10.10.12:9900`
- **通信方式**: 以太网 WebSocket
- **数据格式**: JSON
- **连接模式**: 一对一通讯（任务调度系统）

## 8. 关键字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| mode | string | mission(任务模式) / event(订阅模式) |
| type | string | request(请求) / response(应答) / notify(通知) |
| cmd | string | 具体指令 (start/pause/resume/cancel/subscribe 等) |
| uuid | string | 唯一标识，关联上下文共用 |
| ts | number | 时间戳 (秒) |
| task_id | string | 任务唯一 ID，客户端生成 |
| name | string | 任务/事件名称 |
| data | object | 具体任务数据 |

## 9. 错误码结构

```json
{
  "error_code": {
    "code": 0,
    "module": "模块名",
    "msg": "错误信息",
    "version_info": "版本信息"
  }
}
```

- `code: 0` 表示成功
- `code: 非 0` 表示失败，查看 module 和 msg
