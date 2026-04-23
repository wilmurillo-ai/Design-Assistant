#!/usr/bin/env python3
"""
多 Agent 协作系统

Planner → Executor → Reviewer 架构
参考 Claude Code 的 Agent 协作模式
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from datetime import datetime

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = MAGENTA = ""


class AgentRole(Enum):
    """Agent 角色"""
    PLANNER = "planner"       # 规划者
    EXECUTOR = "executor"     # 执行者
    REVIEWER = "reviewer"     # 审查者
    COORDINATOR = "coordinator"  # 协调者


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务"""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMessage:
    """Agent 消息"""
    id: str
    from_agent: str
    to_agent: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role
        self._inbox: List[AgentMessage] = []
        self._outbox: List[AgentMessage] = []
        self._context: Dict[str, Any] = {}
    
    @abstractmethod
    async def think(self, context: Dict[str, Any]) -> str:
        """思考"""
        pass
    
    @abstractmethod
    async def act(self, action: str, params: Dict[str, Any]) -> Any:
        """行动"""
        pass
    
    def receive_message(self, message: AgentMessage) -> None:
        """接收消息"""
        self._inbox.append(message)
    
    def send_message(self, to_agent: str, content: str, metadata: Dict = None) -> AgentMessage:
        """发送消息"""
        import uuid
        message = AgentMessage(
            id=str(uuid.uuid4()),
            from_agent=self.name,
            to_agent=to_agent,
            content=content,
            metadata=metadata or {}
        )
        self._outbox.append(message)
        return message
    
    def get_messages(self) -> List[AgentMessage]:
        """获取消息"""
        messages = self._inbox.copy()
        self._inbox.clear()
        return messages
    
    def set_context(self, key: str, value: Any) -> None:
        """设置上下文"""
        self._context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文"""
        return self._context.get(key, default)


class PlannerAgent(BaseAgent):
    """规划 Agent"""
    
    def __init__(self, name: str = "planner"):
        super().__init__(name, AgentRole.PLANNER)
    
    async def think(self, context: Dict[str, Any]) -> str:
        """分析任务，生成计划"""
        goal = context.get("goal", "")
        constraints = context.get("constraints", [])
        
        # 简单的规划逻辑
        plan = f"分析目标: {goal}\n"
        
        if "code" in goal.lower() or "写" in goal.lower():
            plan += "1. 理解需求\n2. 编写代码\n3. 测试验证\n"
        elif "搜索" in goal.lower() or "查找" in goal.lower():
            plan += "1. 分析查询\n2. 执行搜索\n3. 整理结果\n"
        else:
            plan += "1. 理解任务\n2. 分解子任务\n3. 执行计划\n"
        
        return plan
    
    async def act(self, action: str, params: Dict[str, Any]) -> Any:
        """执行规划动作"""
        if action == "create_tasks":
            tasks = params.get("tasks", [])
            return [Task(id=f"task_{i}", description=t) for i, t in enumerate(tasks)]
        elif action == "prioritize":
            tasks = params.get("tasks", [])
            return sorted(tasks, key=lambda t: t.get("priority", 5), reverse=True)
        return None


class ExecutorAgent(BaseAgent):
    """执行 Agent"""
    
    def __init__(self, name: str = "executor"):
        super().__init__(name, AgentRole.EXECUTOR)
        self._tools: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, func: Callable) -> None:
        """注册工具"""
        self._tools[name] = func
    
    async def think(self, context: Dict[str, Any]) -> str:
        """决定如何执行"""
        task = context.get("current_task")
        if task:
            return f"执行任务: {task.description}"
        return "等待任务"
    
    async def act(self, action: str, params: Dict[str, Any]) -> Any:
        """执行动作"""
        if action == "execute_task":
            task = params.get("task")
            if task:
                # 模拟执行
                await asyncio.sleep(0.1)
                return {"status": "completed", "result": f"完成: {task.description}"}
        elif action == "use_tool":
            tool_name = params.get("tool")
            tool_params = params.get("params", {})
            if tool_name in self._tools:
                tool = self._tools[tool_name]
                if asyncio.iscoroutinefunction(tool):
                    return await tool(**tool_params)
                return tool(**tool_params)
        return None


class ReviewerAgent(BaseAgent):
    """审查 Agent"""
    
    def __init__(self, name: str = "reviewer"):
        super().__init__(name, AgentRole.REVIEWER)
        self._rules: List[Callable] = []
    
    def add_rule(self, rule: Callable) -> None:
        """添加审查规则"""
        self._rules.append(rule)
    
    async def think(self, context: Dict[str, Any]) -> str:
        """审查计划或结果"""
        target = context.get("target")
        target_type = context.get("type", "result")
        
        if target_type == "plan":
            return f"审查计划: {target[:50]}..."
        elif target_type == "result":
            return f"审查结果: {target}"
        return "等待审查"
    
    async def act(self, action: str, params: Dict[str, Any]) -> Any:
        """执行审查动作"""
        if action == "review":
            target = params.get("target")
            issues = []
            
            for rule in self._rules:
                try:
                    result = rule(target)
                    if result:
                        issues.append(result)
                except Exception:
                    pass
            
            return {
                "passed": len(issues) == 0,
                "issues": issues
            }
        elif action == "suggest_improvements":
            return ["添加更多测试", "优化性能", "完善文档"]
        
        return None


class AgentTeam:
    """Agent 团队"""
    
    def __init__(self, name: str = "team"):
        self.name = name
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.message_bus: List[AgentMessage] = []
        self._callbacks: Dict[str, List[Callable]] = {
            "on_task_start": [],
            "on_task_complete": [],
            "on_task_fail": [],
            "on_message": []
        }
    
    def add_agent(self, agent: BaseAgent) -> None:
        """添加 Agent"""
        self.agents[agent.name] = agent
        print(f"{Fore.GREEN}✓ 添加 Agent: {agent.name} ({agent.role.value}){Fore.RESET}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """获取 Agent"""
        return self.agents.get(name)
    
    def create_task(self, description: str, dependencies: List[str] = None) -> Task:
        """创建任务"""
        import uuid
        task = Task(
            id=str(uuid.uuid4()),
            description=description,
            dependencies=dependencies or []
        )
        self.tasks[task.id] = task
        return task
    
    def assign_task(self, task_id: str, agent_name: str) -> bool:
        """分配任务"""
        task = self.tasks.get(task_id)
        agent = self.agents.get(agent_name)
        
        if task and agent:
            task.assigned_to = agent_name
            return True
        return False
    
    def add_callback(self, event: str, callback: Callable) -> None:
        """添加回调"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _emit(self, event: str, *args, **kwargs) -> None:
        """触发回调"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ 回调失败: {e}{Fore.RESET}")
    
    async def run_task(self, task_id: str) -> Task:
        """运行任务"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        
        # 检查依赖
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if dep_task and dep_task.status != TaskStatus.COMPLETED:
                task.status = TaskStatus.FAILED
                task.error = f"依赖任务未完成: {dep_id}"
                return task
        
        # 分配给 Agent
        if not task.assigned_to:
            task.assigned_to = "executor"
        
        agent = self.agents.get(task.assigned_to)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = f"Agent 不存在: {task.assigned_to}"
            return task
        
        # 执行
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self._emit("on_task_start", task)
        
        try:
            # Agent 思考
            context = {"current_task": task, "all_tasks": self.tasks}
            thought = await agent.think(context)
            
            # Agent 行动
            result = await agent.act("execute_task", {"task": task})
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            self._emit("on_task_complete", task)
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            self._emit("on_task_fail", task)
        
        return task
    
    async def run_workflow(self, goal: str) -> Dict[str, Task]:
        """运行工作流"""
        # Planner 规划
        planner = self.agents.get("planner")
        if not planner:
            raise ValueError("需要 Planner Agent")
        
        plan = await planner.think({"goal": goal})
        print(f"{Fore.CYAN}计划: {plan}{Fore.RESET}")
        
        # 创建任务
        task_descriptions = [line.strip() for line in plan.split("\n") if line.strip() and line[0].isdigit()]
        tasks = []
        for desc in task_descriptions:
            task = self.create_task(desc)
            tasks.append(task)
        
        # 分配任务
        for i, task in enumerate(tasks):
            self.assign_task(task.id, "executor")
        
        # 执行任务
        results = {}
        for task in tasks:
            result = await self.run_task(task.id)
            results[task.id] = result
        
        # Reviewer 审查
        reviewer = self.agents.get("reviewer")
        if reviewer:
            context = {"target": results, "type": "result"}
            feedback = await reviewer.think(context)
            print(f"{Fore.CYAN}审查反馈: {feedback}{Fore.RESET}")
        
        return results


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== 多 Agent 协作示例 ==={Fore.RESET}\n")
    
    # 创建团队
    team = AgentTeam("dev_team")
    
    # 添加 Agent
    planner = PlannerAgent("planner")
    executor = ExecutorAgent("executor")
    reviewer = ReviewerAgent("reviewer")
    
    # 注册工具到执行器
    def read_file(path: str) -> str:
        with open(path, 'r') as f:
            return f.read()
    
    executor.register_tool("read_file", read_file)
    
    team.add_agent(planner)
    team.add_agent(executor)
    team.add_agent(reviewer)
    
    # 运行工作流
    print("\n执行工作流:")
    results = await team.run_workflow("帮我写一个 Python 脚本读取文件")
    
    # 结果
    print("\n任务结果:")
    for task_id, task in results.items():
        status_icon = "✓" if task.status == TaskStatus.COMPLETED else "✗"
        print(f"   {status_icon} {task.description[:30]}... -> {task.status.value}")
    
    print(f"\n{Fore.GREEN}✓ 多 Agent 协作示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())