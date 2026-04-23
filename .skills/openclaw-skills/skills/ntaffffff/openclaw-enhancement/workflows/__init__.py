#!/usr/bin/env python3
"""
工作流编排模块

DAG 任务编排、依赖管理、并行执行
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict, deque

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务"""
    id: str
    name: str
    action: Callable
    dependencies: Set[str] = field(default_factory=set)  # 依赖的任务ID
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowDAG:
    """工作流 DAG（有向无环图）"""
    
    def __init__(self, name: str = "workflow"):
        self.name = name
        self.tasks: Dict[str, Task] = {}
        self.edges: Dict[str, Set[str]] = defaultdict(set)  # task -> dependencies
        self.reverse_edges: Dict[str, Set[str]] = defaultdict(set)  # task -> dependents
        
        # 执行状态
        self._ready_queue: deque = deque()
        self._running_tasks: Set[str] = set()
        self._completed_tasks: Set[str] = set()
        self._failed_tasks: Set[str] = set()
    
    def add_task(
        self,
        task_id: str,
        name: str,
        action: Callable,
        dependencies: List[str] = None,
        max_retries: int = 3,
        metadata: Dict = None
    ) -> Task:
        """添加任务"""
        task = Task(
            id=task_id,
            name=name,
            action=action,
            dependencies=set(dependencies or []),
            max_retries=max_retries,
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        
        # 构建图
        for dep_id in task.dependencies:
            self.edges[task_id].add(dep_id)
            self.reverse_edges[dep_id].add(task_id)
        
        # 检查是否有环
        if self._has_cycle():
            raise ValueError(f"添加任务 {task_id} 会导致循环依赖")
        
        return task
    
    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        if task_id not in self.tasks:
            return False
        
        del self.tasks[task_id]
        
        # 清理边
        for deps in self.edges.values():
            deps.discard(task_id)
        
        for deps in self.reverse_edges.values():
            deps.discard(task_id)
        
        del self.edges[task_id]
        del self.reverse_edges[task_id]
        
        return True
    
    def _has_cycle(self) -> bool:
        """检查是否有环"""
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.edges.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in self.tasks:
            if task_id not in visited:
                if dfs(task_id):
                    return True
        
        return False
    
    def get_ready_tasks(self) -> List[Task]:
        """获取就绪的任务（所有依赖都已完成）"""
        ready = []
        
        for task_id, task in self.tasks.items():
            if task.status != TaskStatus.PENDING:
                continue
            
            # 检查所有依赖是否完成
            all_deps_done = all(
                self.tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )
            
            if all_deps_done:
                ready.append(task)
        
        return ready
    
    def get_execution_order(self) -> List[List[str]]:
        """获取执行顺序（层次拓扑排序）"""
        in_degree = {tid: len(t.dependencies) for tid, t in self.tasks.items()}
        levels = []
        remaining = set(self.tasks.keys())
        
        while remaining:
            # 找出入度为0的任务
            current_level = [tid for tid in remaining if in_degree[tid] == 0]
            
            if not current_level:
                raise ValueError("无法生成执行顺序（存在循环依赖）")
            
            levels.append(current_level)
            
            # 更新入度
            for task_id in current_level:
                remaining.remove(task_id)
                for dependent in self.reverse_edges[task_id]:
                    in_degree[dependent] -= 1
        
        return levels


class WorkflowExecutor:
    """工作流执行器"""
    
    def __init__(self, workflow: WorkflowDAG = None, max_parallel: int = 4):
        self.workflow = workflow or WorkflowDAG()
        self.max_parallel = max_parallel
        self._running = False
        self._cancelled: Set[str] = set()
        self._callbacks: Dict[str, List[Callable]] = {
            "on_task_start": [],
            "on_task_complete": [],
            "on_task_fail": [],
            "on_workflow_complete": [],
            "on_workflow_fail": []
        }
    
    def register_callback(self, event: str, callback: Callable):
        """注册回调"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _emit(self, event: str, *args, **kwargs):
        """触发回调"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ 回调失败: {e}{Fore.RESET}")
    
    async def execute(self, start_tasks: List[str] = None) -> Dict[str, Task]:
        """执行工作流"""
        self._running = True
        self._cancelled.clear()
        
        # 重置任务状态
        for task in self.workflow.tasks.values():
            task.status = TaskStatus.PENDING
            task.result = None
            task.error = None
        
        print(f"{Fore.CYAN}▶ 开始执行工作流: {self.workflow.name}{Fore.RESET}")
        
        # 获取执行顺序
        try:
            execution_order = self.workflow.get_execution_order()
        except ValueError as e:
            print(f"{Fore.RED}✗ 工作流配置错误: {e}{Fore.RESET}")
            return {}
        
        # 逐层执行
        for level_idx, level_tasks in enumerate(execution_order):
            if not self._running:
                break
            
            # 过滤起始任务
            if start_tasks:
                level_tasks = [t for t in level_tasks if t in start_tasks]
            
            print(f"{Fore.CYAN}  层级 {level_idx + 1}/{len(execution_order)}: {len(level_tasks)} 个任务{Fore.RESET}")
            
            # 并行执行当前层
            tasks_to_run = []
            for task_id in level_tasks:
                task = self.workflow.tasks[task_id]
                if task.status == TaskStatus.PENDING:
                    tasks_to_run.append(self._execute_task(task))
            
            # 限制并行数
            results = []
            for i in range(0, len(tasks_to_run), self.max_parallel):
                batch = tasks_to_run[i:i + self.max_parallel]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                results.extend(batch_results)
            
            # 检查失败
            failed = any(isinstance(r, Exception) for r in results)
            if failed and not self._running:
                print(f"{Fore.RED}✗ 工作流执行失败{Fore.RESET}")
                self._emit("on_workflow_fail", self.workflow.tasks)
                return self.workflow.tasks
        
        print(f"{Fore.GREEN}✓ 工作流执行完成{Fore.RESET}")
        self._emit("on_workflow_complete", self.workflow.tasks)
        return self.workflow.tasks
    
    async def _execute_task(self, task: Task) -> Any:
        """执行单个任务"""
        if task.id in self._cancelled:
            task.status = TaskStatus.CANCELLED
            return
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        self._emit("on_task_start", task)
        
        print(f"    ▶ {task.name}")
        
        # 执行（带重试）
        for attempt in range(task.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(task.action):
                    result = await task.action(task.metadata)
                else:
                    result = task.action(task.metadata)
                
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                
                print(f"    ✓ {task.name}")
                self._emit("on_task_complete", task)
                return result
                
            except Exception as e:
                task.retry_count = attempt + 1
                task.error = str(e)
                
                if attempt < task.max_retries:
                    print(f"    ⚠ {task.name} 失败，{task.max_retries - attempt} 次重试...")
                    await asyncio.sleep(1)
                else:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.now()
                    
                    print(f"    ✗ {task.name} 失败: {e}")
                    self._emit("on_task_fail", task, e)
                    return
        
        return task.result
    
    def cancel(self, task_id: str = None):
        """取消执行"""
        self._running = False
        if task_id:
            self._cancelled.add(task_id)


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== 工作流编排示例 ==={Fore.RESET}\n")
    
    # 创建工作流
    workflow = WorkflowDAG("项目构建")
    
    # 定义任务
    async def fetch_dependencies(meta):
        await asyncio.sleep(0.5)
        return {"packages": ["numpy", "pandas"]}
    
    def run_linter(meta):
        return {"lint": "passed"}
    
    def run_tests(meta):
        return {"tests": 15, "passed": 14}
    
    def build_project(meta):
        return {"artifact": "app.tar.gz"}
    
    def deploy(meta):
        return {"deployed": True}
    
    # 添加任务
    workflow.add_task("deps", "获取依赖", fetch_dependencies)
    workflow.add_task("lint", "代码检查", run_linter, dependencies=["deps"])
    workflow.add_task("test", "运行测试", run_tests, dependencies=["deps"])
    workflow.add_task("build", "构建项目", build_project, dependencies=["lint", "test"])
    workflow.add_task("deploy", "部署上线", deploy, dependencies=["build"])
    
    # 执行
    executor = WorkflowExecutor(workflow, max_parallel=3)
    
    print("执行工作流:")
    results = await executor.execute()
    
    # 结果
    print("\n任务结果:")
    for task_id, task in results.items():
        status_icon = "✓" if task.status == TaskStatus.COMPLETED else "✗"
        print(f"   {status_icon} {task.name}: {task.status.value}")
    
    print(f"\n{Fore.GREEN}✓ 工作流编排示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())