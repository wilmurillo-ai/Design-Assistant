#!/usr/bin/env python3
"""
Steering 引导模块

智能引导用户完成复杂任务
参考 Claude Code 的工作流引导
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """工作流步骤"""
    id: str
    name: str
    description: str
    action: Callable  # 要执行的函数
    required: bool = True
    retryable: bool = True
    max_retries: int = 3
    condition: Optional[Callable] = None  # 执行条件
    on_complete: Optional[Callable] = None  # 完成回调
    on_fail: Optional[Callable] = None  # 失败回调


@dataclass
class StepResult:
    """步骤结果"""
    step_id: str
    status: StepStatus
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retries: int = 0


@dataclass
class Workflow:
    """工作流"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    context: Dict[str, Any] = field(default_factory=dict)
    current_step: int = 0
    results: List[StepResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class SteeringGuide:
    """Steering 引导器"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflow: Optional[Workflow] = None
        self.step_handlers: Dict[str, Callable] = {}
        self._callbacks: Dict[str, List[Callable]] = {
            "on_step_start": [],
            "on_step_complete": [],
            "on_step_fail": [],
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
                print(f"{Fore.YELLOW}⚠ 回调执行失败: {e}{Fore.RESET}")
    
    def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[WorkflowStep] = None
    ) -> Workflow:
        """创建工作流"""
        import uuid
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            steps=steps or []
        )
        self.workflows[workflow.id] = workflow
        print(f"{Fore.CYAN}✓ 创建工作流: {name}{Fore.RESET}")
        return workflow
    
    def add_step(
        self,
        workflow_id: str,
        step: WorkflowStep
    ) -> bool:
        """添加步骤"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        workflow.steps.append(step)
        return True
    
    async def execute_step(self, step: WorkflowStep, context: Dict) -> StepResult:
        """执行单个步骤"""
        import time
        start_time = time.time()
        
        result = StepResult(step_id=step.id, status=StepStatus.IN_PROGRESS)
        self._emit("on_step_start", step, context)
        
        # 检查条件
        if step.condition and not step.condition(context):
            result.status = StepStatus.SKIPPED
            self._emit("on_step_complete", step, result, context)
            return result
        
        # 执行（带重试）
        for attempt in range(step.max_retries + 1):
            try:
                # 调用处理函数
                if asyncio.iscoroutinefunction(step.action):
                    output = await step.action(context)
                else:
                    output = step.action(context)
                
                result.output = output
                result.status = StepStatus.COMPLETED
                result.retries = attempt
                
                # 完成回调
                if step.on_complete:
                    if asyncio.iscoroutinefunction(step.on_complete):
                        await step.on_complete(output, context)
                    else:
                        step.on_complete(output, context)
                
                self._emit("on_step_complete", step, result, context)
                break
                
            except Exception as e:
                result.error = str(e)
                result.retries = attempt
                
                if attempt < step.max_retries and step.retryable:
                    print(f"{Fore.YELLOW}⚠ 步骤 {step.name} 失败，{step.max_retries - attempt} 次重试...{Fore.RESET}")
                    await asyncio.sleep(1)
                else:
                    result.status = StepStatus.FAILED
                    
                    if step.on_fail:
                        if asyncio.iscoroutinefunction(step.on_fail):
                            await step.on_fail(e, context)
                        else:
                            step.on_fail(e, context)
                    
                    self._emit("on_step_fail", step, result, context)
        
        result.execution_time = time.time() - start_time
        return result
    
    async def execute_workflow(
        self,
        workflow_id: str,
        initial_context: Dict = None,
        start_step: int = 0
    ) -> Workflow:
        """执行工作流"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        self.active_workflow = workflow
        workflow.context = initial_context or {}
        workflow.current_step = start_step
        
        print(f"{Fore.CYAN}▶ 开始工作流: {workflow.name}{Fore.RESET}")
        
        for i in range(start_step, len(workflow.steps)):
            step = workflow.steps[i]
            workflow.current_step = i
            
            print(f"{Fore.CYAN}  步骤 {i+1}/{len(workflow.steps)}: {step.name}{Fore.RESET}")
            
            result = await self.execute_step(step, workflow.context)
            workflow.results.append(result)
            
            if result.status == StepStatus.FAILED:
                print(f"{Fore.RED}✗ 工作流失败: {step.name}{Fore.RESET}")
                self._emit("on_workflow_fail", workflow)
                return workflow
            
            if result.status == StepStatus.SKIPPED:
                print(f"{Fore.YELLOW}○ 跳过步骤: {step.name}{Fore.RESET}")
        
        print(f"{Fore.GREEN}✓ 工作流完成: {workflow.name}{Fore.RESET}")
        self._emit("on_workflow_complete", workflow)
        return workflow
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """获取工作流状态"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {}
        
        completed = sum(1 for r in workflow.results if r.status == StepStatus.COMPLETED)
        failed = sum(1 for r in workflow.results if r.status == StepStatus.FAILED)
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": "completed" if failed == 0 else "failed" if completed < len(workflow.steps) else "running",
            "progress": f"{completed}/{len(workflow.steps)}",
            "current_step": workflow.current_step
        }
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """取消工作流"""
        if self.active_workflow and self.active_workflow.id == workflow_id:
            self.active_workflow = None
            return True
        return False


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== Steering 引导示例 ==={Fore.RESET}\n")
    
    # 创建引导器
    guide = SteeringGuide()
    
    # 定义步骤
    async def setup_project(ctx):
        print(f"   创建项目目录: {ctx.get('project_name', 'demo')}")
        return {"path": f"/tmp/{ctx.get('project_name', 'demo')}"}
    
    def install_dependencies(ctx):
        print(f"   安装依赖...")
        return {"packages": ["numpy", "pandas"]}
    
    async def run_tests(ctx):
        print(f"   运行测试...")
        return {"tests_passed": 10, "tests_failed": 0}
    
    # 创建工作流
    workflow = guide.create_workflow(
        name="项目初始化",
        description="初始化一个新项目"
    )
    
    # 添加步骤
    guide.add_step(workflow.id, WorkflowStep(
        id="step1",
        name="创建项目结构",
        description="创建项目目录和基础文件",
        action=setup_project,
        required=True
    ))
    
    guide.add_step(workflow.id, WorkflowStep(
        id="step2", 
        name="安装依赖",
        description="安装项目所需依赖",
        action=install_dependencies,
        required=True
    ))
    
    guide.add_step(workflow.id, WorkflowStep(
        id="step3",
        name="运行测试",
        description="执行测试确保一切正常",
        action=run_tests,
        required=False
    ))
    
    # 执行工作流
    print("\n执行工作流:")
    result = await guide.execute_workflow(
        workflow.id,
        {"project_name": "my-awesome-project"}
    )
    
    # 状态
    print("\n工作流状态:")
    status = guide.get_workflow_status(workflow.id)
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print(f"\n{Fore.GREEN}✓ Steering 引导示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())