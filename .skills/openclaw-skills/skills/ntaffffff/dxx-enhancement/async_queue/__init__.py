#!/usr/bin/env python3
"""
异步消息队列模块

支持发布/订阅、优先级队列、消息持久化
"""

import asyncio
import json
import uuid
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import heapq

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


class MessagePriority(Enum):
    """消息优先级"""
    LOW = 0
    NORMAL = 5
    HIGH = 10
    URGENT = 20


@dataclass
class Message:
    """消息"""
    id: str
    topic: str
    payload: Any
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    expiry: Optional[datetime] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class Subscription:
    """订阅"""
    id: str
    topic: str
    callback: Callable
    filter_func: Optional[Callable] = None
    created_at: datetime = field(default_factory=datetime.now)


class AsyncQueue:
    """异步队列"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self._queue: List[tuple] = []  # (priority, timestamp, message)
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition(self._lock)
    
    async def put(self, message: Message):
        """放入消息"""
        async with self._lock:
            heapq.heappush(self._queue, (
                -message.priority.value,  # 优先级高的在前
                message.timestamp.timestamp(),
                message
            ))
            self._not_empty.notify()
    
    async def get(self, timeout: float = None) -> Optional[Message]:
        """获取消息"""
        async with self._not_empty:
            while not self._queue:
                try:
                    await asyncio.wait_for(
                        self._not_empty.wait(),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    return None
            
            _, _, message = heapq.heappop(self._queue)
            return message
    
    async def get_nowait(self) -> Optional[Message]:
        """非阻塞获取"""
        async with self._lock:
            if self._queue:
                _, _, message = heapq.heappop(self._queue)
                return message
            return None
    
    def qsize(self) -> int:
        """队列大小"""
        return len(self._queue)
    
    def empty(self) -> bool:
        """是否为空"""
        return len(self._queue) == 0


class MessageBus:
    """消息总线（发布/订阅）"""
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path.home() / ".openclaw" / "mq"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.subscriptions: Dict[str, List[Subscription]] = defaultdict(list)
        self.topics: Dict[str, AsyncQueue] = {}
        self.message_history: List[Message] = []
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # 持久化
        self._persist_file = self.storage_path / "messages.json"
        self._load_history()
    
    def _load_history(self):
        """加载历史消息"""
        if self._persist_file.exists():
            try:
                data = json.loads(self._persist_file.read_text())
                for msg_data in data.get("messages", []):
                    msg_data["timestamp"] = datetime.fromisoformat(msg_data["timestamp"])
                    if msg_data.get("expiry"):
                        msg_data["expiry"] = datetime.fromisoformat(msg_data["expiry"])
                    msg = Message(**msg_data)
                    self.message_history.append(msg)
            except Exception:
                pass
    
    def _save_history(self):
        """保存历史消息"""
        data = {
            "messages": [
                {
                    "id": m.id,
                    "topic": m.topic,
                    "payload": str(m.payload)[:500],  # 简化
                    "priority": m.priority.value,
                    "timestamp": m.timestamp.isoformat(),
                    "expiry": m.expiry.isoformat() if m.expiry else None
                }
                for m in self.message_history[-100:]  # 只保留最近100条
            ]
        }
        self._persist_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def _get_or_create_queue(self, topic: str) -> AsyncQueue:
        """获取或创建队列"""
        if topic not in self.topics:
            self.topics[topic] = AsyncQueue(topic)
        return self.topics[topic]
    
    async def publish(self, topic: str, payload: Any, priority: MessagePriority = MessagePriority.NORMAL):
        """发布消息"""
        message = Message(
            id=str(uuid.uuid4()),
            topic=topic,
            payload=payload,
            priority=priority
        )
        
        # 放入队列
        queue = self._get_or_create_queue(topic)
        await queue.put(message)
        
        # 记录历史
        self.message_history.append(message)
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-1000:]
        
        # 触发订阅回调
        await self._dispatch(topic, message)
        
        # 持久化
        self._save_history()
        
        return message.id
    
    async def subscribe(
        self,
        topic: str,
        callback: Callable,
        filter_func: Callable = None
    ) -> str:
        """订阅主题"""
        subscription = Subscription(
            id=str(uuid.uuid4()),
            topic=topic,
            callback=callback,
            filter_func=filter_func
        )
        
        self.subscriptions[topic].append(subscription)
        
        return subscription.id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        for topic, subs in self.subscriptions.items():
            for sub in subs:
                if sub.id == subscription_id:
                    subs.remove(sub)
                    return True
        return False
    
    async def _dispatch(self, topic: str, message: Message):
        """分发消息"""
        # 精确匹配
        for sub in self.subscriptions.get(topic, []):
            await self._execute_subscription(sub, message)
        
        # 通配符匹配
        for pattern, subs in self.subscriptions.items():
            if "*" in pattern:
                import re
                regex_pattern = pattern.replace("*", ".*")
                if re.match(regex_pattern, topic):
                    for sub in subs:
                        await self._execute_subscription(sub, message)
    
    async def _execute_subscription(self, sub: Subscription, message: Message):
        """执行订阅回调"""
        # 检查过滤器
        if sub.filter_func:
            try:
                if not sub.filter_func(message):
                    return
            except Exception:
                return
        
        # 执行回调
        try:
            if asyncio.iscoroutinefunction(sub.callback):
                await sub.callback(message)
            else:
                sub.callback(message)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ 订阅回调执行失败: {e}{Fore.RESET}")
    
    async def consume(self, topic: str, timeout: float = None) -> Optional[Message]:
        """消费消息"""
        queue = self._get_or_create_queue(topic)
        return await queue.get(timeout)
    
    def get_topic_stats(self, topic: str) -> Dict[str, Any]:
        """获取主题统计"""
        queue = self.topics.get(topic)
        return {
            "topic": topic,
            "subscribers": len(self.subscriptions.get(topic, [])),
            "queue_size": queue.qsize() if queue else 0,
            "messages_sent": sum(1 for m in self.message_history if m.topic == topic)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有统计"""
        return {
            "total_topics": len(self.topics),
            "total_subscriptions": sum(len(s) for s in self.subscriptions.values()),
            "total_messages": len(self.message_history),
            "topics": {topic: self.get_topic_stats(topic) for topic in self.topics}
        }


class MessageProducer:
    """消息生产者"""
    
    def __init__(self, bus: MessageBus, topic: str):
        self.bus = bus
        self.topic = topic
    
    async def send(self, payload: Any, priority: MessagePriority = MessagePriority.NORMAL):
        """发送消息"""
        return await self.bus.publish(self.topic, payload, priority)
    
    async def send_batch(self, payloads: List[Any]):
        """批量发送"""
        results = []
        for payload in payloads:
            msg_id = await self.send(payload)
            results.append(msg_id)
        return results


class MessageConsumer:
    """消息消费者"""
    
    def __init__(self, bus: MessageBus, topic: str):
        self.bus = bus
        self.topic = topic
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self, handler: Callable):
        """开始消费"""
        self._running = True
        
        async def consume_loop():
            while self._running:
                message = await self.bus.consume(self.topic, timeout=1.0)
                if message:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            handler(message)
                    except Exception as e:
                        print(f"{Fore.RED}✗ 消息处理失败: {e}{Fore.RESET}")
        
        self._task = asyncio.create_task(consume_loop())
    
    async def stop(self):
        """停止消费"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== 异步消息队列示例 ==={Fore.RESET}\n")
    
    # 创建消息总线
    bus = MessageBus()
    
    # 1. 发布/订阅
    print("1. 发布/订阅:")
    
    async def on_notification(message):
        print(f"   收到通知: {message.payload}")
    
    await bus.subscribe("notifications", on_notification)
    await bus.publish("notifications", {"type": "alert", "msg": "你好!"})
    await bus.publish("notifications", {"type": "info", "msg": "有新消息"})
    
    # 等待异步处理
    await asyncio.sleep(0.1)
    
    # 2. 生产者/消费者
    print("\n2. 生产者/消费者:")
    
    producer = MessageProducer(bus, "tasks")
    consumer = MessageConsumer(bus, "tasks")
    
    async def handle_task(msg):
        print(f"   处理任务: {msg.payload}")
    
    await consumer.start(handle_task)
    
    # 发送任务
    for i in range(3):
        await producer.send(f"任务 {i+1}", MessagePriority.NORMAL)
        await asyncio.sleep(0.05)
    
    await asyncio.sleep(0.2)
    await consumer.stop()
    
    # 3. 统计
    print("\n3. 消息统计:")
    stats = bus.get_all_stats()
    for key, value in stats.items():
        if key != "topics":
            print(f"   {key}: {value}")
    
    print(f"\n{Fore.GREEN}✓ 异步消息队列示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())