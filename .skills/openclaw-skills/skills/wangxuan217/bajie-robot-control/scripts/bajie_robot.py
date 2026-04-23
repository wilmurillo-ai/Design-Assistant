#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 WebSocket 客户端
实现与八界机器人本体的通信控制

连接配置:
    WebSocket URL: ws://10.10.10.12:9900
    协议：JSON over WebSocket
    模式：mission(任务) / event(事件)

相关文件:
    - protocol.md: 完整 WebSocket 通信协议
    - error_code.md: 错误码详细说明
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException


# ========== 协议常量 ==========

class Mode(Enum):
    """消息模式"""
    MISSION = "mission"
    EVENT = "event"


class Type(Enum):
    """指令类型"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFY = "notify"


class Cmd(Enum):
    """具体指令"""
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ONESHOT = "oneshot"
    NOTIFY = "notify"
    FINISH = "finish"
    REPORT = "report"


# ========== 错误码处理 ==========

@dataclass
class ErrorCode:
    """错误码"""
    code: int
    module: str = ""
    msg: str = ""
    
    @property
    def is_success(self) -> bool:
        return self.code == 0
    
    @property
    def level(self) -> int:
        """
        错误等级：
        0 = 成功
        1 = 警告/可恢复错误（重试 1-3 次）
        3 = 严重错误（需环境分析 + 清除障碍）
        """
        if self.code == 0:
            return 0
        # 导航严重错误
        if self.code in [0x00007002, 0x00007004, 0x00007006, 0x00007008]:
            return 3
        # 机械臂严重错误
        if self.code in [0x00009004, 0x00009008, 0x00009021]:
            return 3
        return 1
    
    def should_retry(self) -> bool:
        """是否应该重试"""
        return self.level == 1
    
    def get_handler_strategy(self) -> str:
        """获取处理策略"""
        strategies = {
            0x00007002: "全局规划失败 - 检查起始位置障碍物",
            0x00007003: "目标点不可达 - 重试或更换目标点",
            0x00007004: "路径被阻挡 - 清除可移动障碍物后重试",
            0x00007006: "机器陷入致命障碍物层 - 需要人工干预",
            0x00009002: "轨迹规划失败 - 检查碰撞检测",
            0x00009004: "目标点超出机械臂工作范围 - 调整位置",
            0x00009006: "逆解失败 - 重新观测生成抓取位姿",
            0x00009021: "未抓到物体 - 重新尝试或报告用户",
            0x000028b0: "电量过低 - 立即回充",
            0x00033000: "上桩超时 - 检查充电桩位置",
            0x00033001: "找不到充电桩 - 重新定位后重试",
            0x00019004: "无法找到物体 - 扩大搜索范围或报告用户",
        }
        return strategies.get(self.code, "未知错误 - 使用通用处理流程")


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    name: str
    success: bool
    error_code: Optional[ErrorCode] = None
    data: Dict = field(default_factory=dict)
    notifications: List[Dict] = field(default_factory=list)
    
    def __bool__(self) -> bool:
        return self.success


class TaskExecutionError(Exception):
    """任务执行异常"""
    def __init__(self, result: TaskResult):
        self.result = result
        super().__init__(f"任务 {result.name} 失败：{result.error_code}")


# ========== 机器人状态 ==========

@dataclass
class RobotState:
    """机器人状态"""
    battery_value: int = 100
    is_charging: bool = False
    room: str = ""
    x: float = 0.0
    y: float = 0.0
    yaw: float = 0.0
    work_state: str = "idle"
    current_task: str = ""
    alarms: List[int] = field(default_factory=list)
    maintenance_mode: bool = False
    gripper_usage_percent: int = 0
    
    @property
    def needs_recharge(self) -> bool:
        """是否需要回充（电量<30%）"""
        return self.battery_value < 30 and not self.is_charging
    
    def update_from_report(self, data: Dict):
        """从上报数据更新状态"""
        if "battery" in data:
            self.battery_value = data["battery"].get("value", 100)
            self.is_charging = data["battery"].get("isCharge", 0) == 1
        if "pos" in data:
            self.room = data["pos"].get("room", "")
            self.x = data["pos"].get("x", 0.0)
            self.y = data["pos"].get("y", 0.0)
            self.yaw = data["pos"].get("yaw", 0.0)
        if "workState" in data:
            self.work_state = data["workState"].get("cmd", "idle")
            self.current_task = data["workState"].get("name", "")
        if "alarm" in data:
            self.alarms = data["alarm"]
        if "maintenance_mode" in data:
            self.maintenance_mode = data["maintenance_mode"]
        if "gripper_usage_percent" in data:
            self.gripper_usage_percent = data["gripper_usage_percent"]


# ========== 八界机器人客户端 ==========

class BajieRobot:
    """
    八界机器人 WebSocket 客户端
    
    提供原子任务执行和复杂任务编排能力
    
    使用示例:
        async with BajieRobot() as robot:
            # 原子任务
            result = await robot.semantic_navigation("客厅")
            
            # 复杂任务
            await robot.organize_desk("桌子")
    """
    
    def __init__(self, host: str = "10.10.10.12", port: int = 9900):
        """
        初始化机器人客户端
        
        Args:
            host: WebSocket 主机地址（默认 10.10.10.12）
            port: WebSocket 端口（默认 9900）
        
        Note:
            所有任务失败后均不自动重试，直接返回错误信息
        """
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._connected = False
        self._state = RobotState()
        self._task_handlers: Dict[str, Callable] = {}
        self._event_handlers: Dict[str, Callable] = {}
        self._pending_responses: Dict[str, asyncio.Future] = {}
        self._receive_task: Optional[asyncio.Task] = None
        self._task_futures: Dict[str, asyncio.Future] = {}
        
        # 回调函数
        self.on_state_update: Optional[Callable[[RobotState], None]] = None
        self.on_task_progress: Optional[Callable[[str, Dict], None]] = None
        self.on_error: Optional[Callable[[ErrorCode], None]] = None
    
    async def connect(self, timeout: float = 10.0) -> bool:
        """
        连接到机器人（清理历史状态）
        
        Note:
            每次连接都会清理所有历史任务状态，确保新任务不受干扰
        """
        try:
            # 清理历史状态
            self._task_handlers.clear()
            self._event_handlers.clear()
            self._pending_responses.clear()
            self._task_futures.clear()
            self._state = RobotState()
            
            self.websocket = await asyncio.wait_for(
                websockets.connect(
                    self.uri, 
                    ping_interval=30, 
                    ping_timeout=10,
                    close_timeout=5
                ),
                timeout=timeout
            )
            self._connected = True
            self._receive_task = asyncio.create_task(self._receive_loop())
            print(f"✓ 已连接到八界机器人 {self.uri}")
            return True
        except Exception as e:
            print(f"✗ 连接失败：{e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        self._connected = False
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        print("✓ 已断开连接")
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def _receive_loop(self):
        """接收消息循环"""
        try:
            async for message in self.websocket:
                await self._handle_message(json.loads(message))
        except ConnectionClosed:
            print("⚠ 连接已关闭")
            self._connected = False
        except Exception as e:
            print(f"⚠ 接收错误：{e}")
            self._connected = False
    
    async def _handle_message(self, msg: Dict):
        """处理接收到的消息"""
        header = msg.get("header", {})
        body = msg.get("body", {})
        
        mode = header.get("mode")
        msg_type = header.get("type")
        cmd = header.get("cmd")
        task_id = body.get("task_id")
        name = body.get("name")
        
        # 处理响应
        if msg_type == Type.RESPONSE.value:
            if task_id in self._pending_responses:
                future = self._pending_responses.pop(task_id)
                if not future.done():
                    future.set_result(msg)
            return
        
        # 处理事件通知
        if mode == Mode.EVENT.value:
            if cmd == Cmd.REPORT.value and name == "robot_info":
                self._state.update_from_report(body.get("data", {}))
                if self.on_state_update:
                    self.on_state_update(self._state)
            if name in self._event_handlers:
                await self._event_handlers[name](msg)
            return
        
        # 处理任务通知
        if mode == Mode.MISSION.value:
            # 任务完成
            if cmd == Cmd.FINISH.value:
                if task_id in self._task_futures:
                    future = self._task_futures.pop(task_id)
                    if not future.done():
                        future.set_result(msg)
            # 任务进度通知
            elif cmd == Cmd.NOTIFY.value:
                if task_id in self._task_handlers:
                    await self._task_handlers[task_id](msg)
                if self.on_task_progress:
                    self.on_task_progress(task_id, body.get("data", {}))
    
    def _build_header(self, mode: Mode, msg_type: Type, cmd: Cmd, 
                      uuid_str: str = None) -> Dict:
        """构建消息头"""
        return {
            "mode": mode.value,
            "type": msg_type.value,
            "cmd": cmd.value,
            "ts": int(time.time()),
            "uuid": uuid_str or str(uuid.uuid4())
        }
    
    def _build_body(self, name: str, task_id: str, data: Dict = None) -> Dict:
        """构建消息体"""
        return {
            "name": name,
            "task_id": task_id,
            "data": data or {}
        }
    
    async def _send_request(self, mode: Mode, name: str, task_id: str, 
                           data: Dict = None, cmd: Cmd = Cmd.START,
                           timeout: float = 30.0) -> Dict:
        """发送请求并等待响应"""
        if not self._connected or not self.websocket:
            raise ConnectionError("未连接到机器人")
        
        uuid_str = str(uuid.uuid4())
        request = {
            "header": self._build_header(mode, Type.REQUEST, cmd, uuid_str),
            "body": self._build_body(name, task_id, data)
        }
        
        # 创建等待响应的 future
        future = asyncio.get_event_loop().create_future()
        self._pending_responses[task_id] = future
        
        # 发送请求
        await self.websocket.send(json.dumps(request))
        
        # 等待响应
        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            self._pending_responses.pop(task_id, None)
            raise TimeoutError(f"任务 {task_id} 响应超时")
    
    async def _wait_task_finish(self, task_id: str, timeout: float = 300.0) -> Dict:
        """等待任务完成"""
        future = asyncio.get_event_loop().create_future()
        self._task_futures[task_id] = future
        
        try:
            finish_msg = await asyncio.wait_for(future, timeout=timeout)
            return finish_msg
        except asyncio.TimeoutError:
            self._task_futures.pop(task_id, None)
            raise TimeoutError(f"任务 {task_id} 执行超时")
    
    async def _execute_mission(self, name: str, data: Dict = None,
                               task_id: str = None, timeout: float = 300.0,
                               notify_handler: Callable = None) -> TaskResult:
        """
        执行任务（不自动重试）
        
        Args:
            name: 任务名称
            data: 任务数据
            task_id: 任务 ID（可选，自动生成唯一 ID）
            timeout: 超时时间（秒）
            notify_handler: 通知处理器
        
        Returns:
            TaskResult: 任务执行结果
        
        Note:
            任务失败后直接返回，不进行重试
            每次执行都会生成唯一的 task_id，避免历史任务干扰
        """
        # 清理历史任务状态
        self._task_handlers.clear()
        self._pending_responses.clear()
        
        # 生成唯一任务 ID，避免历史任务干扰
        if task_id is None:
            task_id = f"{name}_{uuid.uuid4().hex[:8]}"
        if task_id is None:
            task_id = f"{name}_{uuid.uuid4().hex[:8]}"
        
        notifications = []
        
        # 注册通知处理器
        async def handle_notify(msg: Dict):
            notifications.append(msg)
            if notify_handler:
                await notify_handler(msg)
        
        self._task_handlers[task_id] = handle_notify
        
        try:
            # 发送开始请求
            response = await self._send_request(
                Mode.MISSION, name, task_id, data, 
                cmd=Cmd.START, timeout=30.0
            )
            
            # 检查响应错误码
            error_data = response.get("body", {}).get("data", {}).get("error_code", {})
            error_code = ErrorCode(
                code=error_data.get("code", -1),
                module=error_data.get("module", ""),
                msg=error_data.get("msg", "")
            )
            
            if not error_code.is_success:
                # 任务启动失败，直接返回
                print(f"❌ 任务 {name} 启动失败：{error_code.msg}")
                return TaskResult(
                    task_id=task_id,
                    name=name,
                    success=False,
                    error_code=error_code,
                    notifications=notifications
                )
            
            # 等待任务完成
            finish_msg = await self._wait_task_finish(task_id, timeout=timeout)
            
            # 检查完成时的错误码
            finish_error = finish_msg.get("body", {}).get("data", {}).get("error_code", {})
            finish_code = ErrorCode(
                code=finish_error.get("code", 0),
                module=finish_error.get("module", ""),
                msg=finish_error.get("msg", "")
            )
            
            if not finish_code.is_success:
                # 任务执行失败，直接返回
                print(f"❌ 任务 {name} 执行失败：{finish_code.msg}")
                return TaskResult(
                    task_id=task_id,
                    name=name,
                    success=False,
                    error_code=finish_code,
                    data=finish_msg.get("body", {}).get("data", {}),
                    notifications=notifications
                )
            
            return TaskResult(
                task_id=task_id,
                name=name,
                success=True,
                error_code=finish_code,
                data=finish_msg.get("body", {}).get("data", {}),
                notifications=notifications
            )
            
        except TimeoutError as e:
            print(f"❌ 任务 {name} 超时：{e}")
            return TaskResult(
                task_id=task_id,
                name=name,
                success=False,
                error_code=ErrorCode(code=-1, msg=str(e)),
                notifications=notifications
            )
        finally:
            self._task_handlers.pop(task_id, None)
    
    # ========== 任务控制 ==========
    
    async def pause_task(self, task_id: str, name: str) -> TaskResult:
        """暂停任务"""
        return await self._execute_mission(name, task_id=task_id, 
                                           data={}, cmd=Cmd.PAUSE)
    
    async def resume_task(self, task_id: str, name: str) -> TaskResult:
        """恢复任务"""
        return await self._execute_mission(name, task_id=task_id,
                                           data={}, cmd=Cmd.RESUME)
    
    async def cancel_task(self, task_id: str, name: str) -> TaskResult:
        """取消任务"""
        return await self._execute_mission(name, task_id=task_id,
                                           data={}, cmd=Cmd.CANCEL)
    
    # ========== 原子任务：导航类 ==========
    
    async def semantic_navigation(self, goal: str, goal_id: str = "",
                                  user_id: str = "") -> TaskResult:
        """
        语义导航到指定区域或家具
        
        Args:
            goal: 区域或家具名称（如"客厅", "桌子"）
            goal_id: 区域或家具 id（可选）
            user_id: 用户 id（可选）
        """
        data = {"goal": goal, "goal_id": goal_id}
        if user_id:
            data["user_id"] = user_id
        return await self._execute_mission("semantic_navigation", data)
    
    async def point_navigation(self, goal: str, goal_id: str = "") -> TaskResult:
        """定点导航"""
        data = {"goal": goal, "goal_id": goal_id}
        return await self._execute_mission("point_navigation", data)
    
    async def chassis_move(self, move_distance: float, 
                           move_angle: float = 0.0) -> TaskResult:
        """
        控制底盘移动
        
        Args:
            move_distance: 移动距离（米），正值前进，负值后退
            move_angle: 旋转角度（弧度），正值顺时针，负值逆时针
        """
        data = {
            "move_distance": move_distance,
            "move_angle": move_angle
        }
        return await self._execute_mission("chassis_move", data)
    
    async def recharge(self) -> TaskResult:
        """回充"""
        return await self._execute_mission("recharge", {})
    
    async def map_create(self, timeout: float = 900.0) -> TaskResult:
        """
        建图任务（每次执行都使用唯一 task_id）
        
        Args:
            timeout: 超时时间（秒），默认 900 秒（15 分钟）
        
        Returns:
            TaskResult: 建图结果
        
        Note:
            任务失败后直接返回，不自动重试
            每次执行都使用唯一 task_id，避免历史任务干扰
        """
        return await self._execute_mission("map_create", {}, timeout=timeout)
    
    # ========== 原子任务：抓取与放置类 ==========
    
    async def accurate_grab(self, item: str, position: Dict,
                           orientation: Dict, box_length: Dict,
                           frame_id: str = "map",
                           rag_id: str = "", color: str = "", 
                           shape: str = "", person: str = "") -> TaskResult:
        """
        精准抓取
        
        Args:
            item: 物品名称
            position: 位置 {x, y, z}
            orientation: 姿态 {x, y, z, w}
            box_length: 物体尺寸 {x, y, z}
            frame_id: 坐标系
        """
        data = {
            "object": {
                "rag_id": rag_id,
                "item": item,
                "color": color,
                "shape": shape,
                "person": person
            },
            "position": position,
            "orientation": orientation,
            "box_length": box_length,
            "frame_id": frame_id
        }
        return await self._execute_mission("accurate_grab", data)
    
    async def semantic_place(self, area_name: str, object_name: str,
                            direction: str = "里", 
                            area_id: str = "") -> TaskResult:
        """
        推荐放置
        
        Args:
            area_name: 放置区域名称
            object_name: 物品名称
            direction: 方向（里/上）
            area_id: 区域 id
        """
        data = {
            "area_id": area_id,
            "area_name": area_name,
            "object_name": object_name,
            "direction": direction
        }
        return await self._execute_mission("semantic_place", data)
    
    async def tray_grab(self, item: str = "") -> TaskResult:
        """托盘抓取"""
        data = {"item": item}
        return await self._execute_mission("tray_grab", data)
    
    async def tray_place(self) -> TaskResult:
        """托盘放置"""
        return await self._execute_mission("tray_place", {})
    
    async def grab_clothes(self, item: str, position: Dict,
                          orientation: Dict, box_length: Dict,
                          rag_id: str = "", color: str = "",
                          shape: str = "", person: str = "") -> TaskResult:
        """衣物抓取"""
        data = {
            "object": {
                "rag_id": rag_id,
                "item": item,
                "color": color,
                "shape": shape,
                "person": person
            },
            "position": position,
            "orientation": orientation,
            "box_length": box_length,
            "frame_id": "map"
        }
        return await self._execute_mission("grab_clothes", data)
    
    # ========== 原子任务：搜索类 ==========
    
    async def search(self, item: str, area_info: List[Dict],
                    color: str = "", shape: str = "", 
                    person: str = "") -> TaskResult:
        """
        搜索物体
        
        Args:
            item: 物品名称
            area_info: 搜索区域列表 [{"area_name": "客厅", "area_id": ""}]
        """
        data = {
            "object": {
                "item": item,
                "color": color,
                "shape": shape,
                "person": person
            },
            "area_info": area_info
        }
        return await self._execute_mission("search", data)
    
    async def find_person(self, user_name: str, 
                         area_info: List[Dict],
                         user_id: str = "") -> TaskResult:
        """
        找人
        
        Args:
            user_name: 人名
            area_info: 搜索区域列表
            user_id: 用户 id
        """
        data = {
            "user_name": user_name,
            "user_id": user_id,
            "area_info": area_info
        }
        return await self._execute_mission("find_person", data)
    
    async def search_container(self, item: str, area_info: List[Dict],
                              color: str = "", shape: str = "",
                              person: str = "") -> TaskResult:
        """搜索放置容器"""
        data = {
            "object": {
                "item": item,
                "color": color,
                "shape": shape,
                "person": person
            },
            "area_info": area_info
        }
        return await self._execute_mission("search_container", data)
    
    # ========== 原子任务：整理类 ==========
    
    async def restore(self, name: str, area_name: str,
                     object_name: str = "", area_id: str = "") -> TaskResult:
        """
        整理物品
        
        Args:
            name: SortDesk 或 SortShoes
            area_name: 区域名称
            object_name: 物品名称（可选）
        """
        data = {
            "name": name,
            "area_info": {
                "area_name": area_name,
                "area_id": area_id
            },
            "object_info": {
                "object_name": object_name
            }
        }
        return await self._execute_mission("restore", data)
    
    # ========== 原子任务：设备控制类 ==========
    
    async def open_device_door(self) -> TaskResult:
        """打开设备门（如洗衣机）"""
        return await self._execute_mission("open_device_door", {})
    
    async def close_device_door(self) -> TaskResult:
        """关闭设备门并启动"""
        return await self._execute_mission("close_device_door", {})
    
    async def put_clothes(self) -> TaskResult:
        """将衣物放入洗衣机"""
        return await self._execute_mission("put_clothes", {})
    
    # ========== 原子任务：姿态控制类 ==========
    
    async def robot_prepare_pose(self, mission_summary: str = "") -> TaskResult:
        """机身准备姿态"""
        data = {"mission_summary": mission_summary}
        return await self._execute_mission("robot_prepare_pose", data)
    
    async def robot_ending_pose(self) -> TaskResult:
        """机身结束姿态"""
        return await self._execute_mission("robot_ending_pose", {})
    
    async def robot_height_ctrl(self, mode: int) -> TaskResult:
        """
        机身高度控制
        
        Args:
            mode: 高度模式
                1 = 置顶（升到最高）
                2 = 置底（降到最低）
        """
        data = {"mode": mode}
        return await self._execute_mission("robot_height_ctrl", data)
    
    # ========== 事件订阅 ==========
    
    async def subscribe_robot_info(self) -> TaskResult:
        """订阅机器状态"""
        task_id = f"subscribe_{uuid.uuid4().hex[:8]}"
        request = {
            "header": self._build_header(Mode.EVENT, Type.REQUEST, Cmd.SUBSCRIBE),
            "body": self._build_body("robot_info", task_id, {})
        }
        await self.websocket.send(json.dumps(request))
        return TaskResult(task_id=task_id, name="subscribe", success=True)
    
    async def unsubscribe_robot_info(self, task_id: str) -> TaskResult:
        """取消订阅机器状态"""
        request = {
            "header": self._build_header(Mode.EVENT, Type.REQUEST, Cmd.UNSUBSCRIBE),
            "body": self._build_body("robot_info", task_id, {})
        }
        await self.websocket.send(json.dumps(request))
        return TaskResult(task_id=task_id, name="unsubscribe", success=True)
    
    async def oneshot_robot_info(self, topics: List[str] = None) -> Dict:
        """
        单次获取机器状态
        
        Args:
            topics: 需要的主题列表 [pos, battery, workState, alarm, ...]
        """
        if topics is None:
            topics = ["pos", "battery", "workState", "alarm", 
                     "furniture", "ota", "maintenance_mode", "gripper_usage_percent"]
        
        task_id = f"oneshot_{uuid.uuid4().hex[:8]}"
        data = {"topics": topics}
        
        response = await self._send_request(
            Mode.EVENT, "robot_info", task_id, data, 
            cmd=Cmd.ONESHOT
        )
        return response.get("body", {}).get("data", {})
    
    # ========== 状态查询 ==========
    
    @property
    def state(self) -> RobotState:
        """获取当前机器人状态"""
        return self._state
    
    @property
    def battery(self) -> int:
        """当前电量"""
        return self._state.battery_value
    
    @property
    def position(self) -> Tuple[float, float, float]:
        """当前位置 (x, y, yaw)"""
        return (self._state.x, self._state.y, self._state.yaw)
    
    @property
    def is_busy(self) -> bool:
        """是否忙碌"""
        return self._state.work_state != "idle"
    
    # ========== 复杂任务编排 ==========
    
    async def _check_battery_and_recharge(self):
        """检查电量，如需要则回充"""
        if self._state.needs_recharge:
            print(f"⚠ 电量过低 ({self._state.battery_value}%)，开始回充")
            result = await self.recharge()
            if not result.success:
                raise TaskExecutionError(result)
            print("✓ 回充完成")
    
    async def organize_desk(self, desk_name: str = "桌子", 
                           storage_name: str = "收纳筐") -> TaskResult:
        """
        复杂任务：整理桌子
        
        流程：
        1. 准备姿态
        2. 导航到桌子
        3. 搜索桌上物品
        4. 逐个抓取并放置到收纳区
        5. 结束姿态
        """
        task_id = f"organize_desk_{uuid.uuid4().hex[:8]}"
        print(f"📋 开始整理任务：{desk_name} → {storage_name}")
        
        try:
            # 1. 准备姿态
            print("  [1/5] 准备姿态...")
            result = await self.robot_prepare_pose("整理桌子")
            if not result.success:
                return TaskResult(task_id, "organize_desk", False, result.error_code)
            
            # 2. 导航到桌子
            print(f"  [2/5] 导航到 {desk_name}...")
            result = await self.semantic_navigation(desk_name)
            if not result.success:
                return TaskResult(task_id, "organize_desk", False, result.error_code)
            
            # 3. 搜索桌上物品
            print(f"  [3/5] 搜索 {desk_name} 上的物品...")
            result = await self.search(item="", area_info=[{"area_name": desk_name}])
            if not result.success:
                return TaskResult(task_id, "organize_desk", False, result.error_code)
            
            # 4. 抓取并放置（从 notify 中获取物体位置）
            print(f"  [4/5] 抓取并放置物品...")
            objects_found = result.notifications if result.notifications else []
            
            for notify in objects_found:
                obj_data = notify.get("body", {}).get("data", {})
                if "position" not in obj_data:
                    continue
                
                item_name = obj_data.get("item", "物品")
                print(f"    → 抓取：{item_name}")
                
                # 抓取
                grab_result = await self.accurate_grab(
                    item=item_name,
                    position=obj_data["position"],
                    orientation=obj_data.get("orientation", {"x":0,"y":0,"z":0,"w":1}),
                    box_length=obj_data.get("box_length", {"x":0.1,"y":0.1,"z":0.1})
                )
                
                if not grab_result.success:
                    print(f"    ⚠ 抓取失败：{grab_result.error_code.msg}")
                    continue
                
                # 放置
                print(f"    → 放置到：{storage_name}")
                place_result = await self.semantic_place(
                    area_name=storage_name,
                    object_name=item_name,
                    direction="里"
                )
                
                if not place_result.success:
                    print(f"    ⚠ 放置失败：{place_result.error_code.msg}")
            
            # 5. 结束姿态
            print("  [5/5] 结束姿态...")
            result = await self.robot_ending_pose()
            
            return TaskResult(task_id, "organize_desk", result.success, result.error_code)
            
        except Exception as e:
            return TaskResult(task_id, "organize_desk", False, 
                            ErrorCode(code=-1, msg=str(e)))
    
    async def do_laundry(self) -> TaskResult:
        """
        复杂任务：洗衣任务
        
        流程：
        1. 检查电量
        2. 准备姿态
        3. 抓取脏衣物
        4. 导航到洗衣机
        5. 打开洗衣机门
        6. 放入衣物
        7. 关闭洗衣机门并启动
        8. 结束姿态
        """
        task_id = f"do_laundry_{uuid.uuid4().hex[:8]}"
        print("📋 开始洗衣任务")
        
        try:
            # 1. 检查电量
            await self._check_battery_and_recharge()
            
            # 2. 准备姿态
            print("  [1/7] 准备姿态...")
            result = await self.robot_prepare_pose("洗衣任务")
            if not result.success:
                return TaskResult(task_id, "do_laundry", False, result.error_code)
            
            # 3. 抓取脏衣物
            print("  [2/7] 抓取脏衣物...")
            result = await self.search(item="脏衣服", area_info=[{"area_name": "脏衣篮"}])
            if not result.success:
                return TaskResult(task_id, "do_laundry", False, result.error_code)
            
            # 抓取衣物
            for notify in result.notifications:
                obj_data = notify.get("body", {}).get("data", {})
                if "position" in obj_data:
                    grab_result = await self.grab_clothes(
                        item="脏衣服",
                        position=obj_data["position"],
                        orientation=obj_data.get("orientation", {}),
                        box_length=obj_data.get("box_length", {})
                    )
                    if not grab_result.success:
                        return TaskResult(task_id, "do_laundry", False, grab_result.error_code)
            
            # 4. 导航到洗衣机
            print("  [3/7] 导航到洗衣机...")
            result = await self.semantic_navigation("洗衣机")
            if not result.success:
                return TaskResult(task_id, "do_laundry", False, result.error_code)
            
            # 5. 打开洗衣机门
            print("  [4/7] 打开洗衣机门...")
            result = await self.open_device_door()
            if not result.success:
                return TaskResult(task_id, "do_laundry", False, result.error_code)
            
            # 6. 放入衣物
            print("  [5/7] 放入衣物...")
            result = await self.put_clothes()
            if not result.success:
                return TaskResult(task_id, "do_laundry", False, result.error_code)
            
            # 7. 关闭洗衣机门并启动
            print("  [6/7] 关闭洗衣机门并启动...")
            result = await self.close_device_door()
            if not result.success:
                return TaskResult(task_id, "do_laundry", False, result.error_code)
            
            # 8. 结束姿态
            print("  [7/7] 结束姿态...")
            result = await self.robot_ending_pose()
            
            return TaskResult(task_id, "do_laundry", result.success, result.error_code)
            
        except Exception as e:
            return TaskResult(task_id, "do_laundry", False,
                            ErrorCode(code=-1, msg=str(e)))
    
    async def fetch_and_deliver(self, item: str, from_area: str, 
                                to_area: str) -> TaskResult:
        """
        复杂任务：取物配送
        
        流程：
        1. 检查电量
        2. 导航到物品位置
        3. 搜索物品
        4. 抓取物品
        5. 导航到目标位置
        6. 放置物品
        7. 结束姿态
        """
        task_id = f"fetch_deliver_{uuid.uuid4().hex[:8]}"
        print(f"📋 开始配送任务：{item} ({from_area} → {to_area})")
        
        try:
            # 1. 检查电量
            await self._check_battery_and_recharge()
            
            # 2. 导航到物品位置
            print(f"  [1/6] 导航到 {from_area}...")
            result = await self.semantic_navigation(from_area)
            if not result.success:
                return TaskResult(task_id, "fetch_and_deliver", False, result.error_code)
            
            # 3. 搜索物品
            print(f"  [2/6] 搜索 {item}...")
            result = await self.search(item=item, area_info=[{"area_name": from_area}])
            if not result.success:
                return TaskResult(task_id, "fetch_and_deliver", False, result.error_code)
            
            # 4. 抓取物品
            print(f"  [3/6] 抓取 {item}...")
            for notify in result.notifications:
                obj_data = notify.get("body", {}).get("data", {})
                if "position" in obj_data:
                    grab_result = await self.accurate_grab(
                        item=item,
                        position=obj_data["position"],
                        orientation=obj_data.get("orientation", {}),
                        box_length=obj_data.get("box_length", {})
                    )
                    if not grab_result.success:
                        return TaskResult(task_id, "fetch_and_deliver", False, grab_result.error_code)
            
            # 5. 导航到目标位置
            print(f"  [4/6] 导航到 {to_area}...")
            result = await self.semantic_navigation(to_area)
            if not result.success:
                return TaskResult(task_id, "fetch_and_deliver", False, result.error_code)
            
            # 6. 放置物品
            print(f"  [5/6] 放置 {item}...")
            result = await self.semantic_place(
                area_name=to_area,
                object_name=item,
                direction="上"
            )
            if not result.success:
                return TaskResult(task_id, "fetch_and_deliver", False, result.error_code)
            
            # 7. 结束姿态
            print("  [6/6] 结束姿态...")
            result = await self.robot_ending_pose()
            
            return TaskResult(task_id, "fetch_and_deliver", result.success, result.error_code)
            
        except Exception as e:
            return TaskResult(task_id, "fetch_and_deliver", False,
                            ErrorCode(code=-1, msg=str(e)))
    
    async def clean_and_charge(self) -> TaskResult:
        """
        复杂任务：清理并回充
        
        流程：
        1. 检查电量（如<30% 直接回充）
        2. 整理鞋子
        3. 整理桌子
        4. 回充
        """
        task_id = f"clean_charge_{uuid.uuid4().hex[:8]}"
        print("📋 开始清理并回充任务")
        
        try:
            # 1. 检查电量
            if self._state.needs_recharge:
                print(f"⚠ 电量过低 ({self._state.battery_value}%)，优先回充")
                result = await self.recharge()
                return TaskResult(task_id, "clean_and_charge", result.success, result.error_code)
            
            # 2. 整理鞋子
            print("  [1/3] 整理鞋子...")
            result = await self.restore(name="SortShoes", area_name="玄关")
            if not result.success:
                print(f"  ⚠ 整理鞋子失败：{result.error_code.msg}")
            
            # 3. 整理桌子
            print("  [2/3] 整理桌子...")
            result = await self.organize_desk("桌子", "收纳筐")
            if not result.success:
                print(f"  ⚠ 整理桌子失败：{result.error_code.msg}")
            
            # 4. 回充
            print("  [3/3] 回充...")
            result = await self.recharge()
            
            return TaskResult(task_id, "clean_and_charge", result.success, result.error_code)
            
        except Exception as e:
            return TaskResult(task_id, "clean_and_charge", False,
                            ErrorCode(code=-1, msg=str(e)))


# ========== 主函数示例 ==========

async def main():
    """使用示例"""
    async with BajieRobot() as robot:
        # 订阅状态更新
        await robot.subscribe_robot_info()
        
        # 示例 1: 简单导航
        print("\n=== 示例 1: 导航到客厅 ===")
        result = await robot.semantic_navigation("客厅")
        print(f"结果：{'成功' if result.success else '失败'}")
        if not result.success:
            print(f"错误：{result.error_code}")
        
        # 示例 2: 复杂任务 - 整理桌子
        print("\n=== 示例 2: 整理桌子 ===")
        result = await robot.organize_desk("桌子", "收纳筐")
        print(f"结果：{'成功' if result.success else '失败'}")
        
        # 示例 3: 复杂任务 - 取物配送
        print("\n=== 示例 3: 取物配送 ===")
        result = await robot.fetch_and_deliver("水杯", "厨房", "客厅")
        print(f"结果：{'成功' if result.success else '失败'}")


if __name__ == "__main__":
    asyncio.run(main())
