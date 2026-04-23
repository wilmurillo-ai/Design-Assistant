"""
Auto-Coding Skill - 智能自主编码系统
Auto-Coding Skill - Intelligent Autonomous Coding System

通过多 Agent 协作完成从需求到代码的完整开发流程。

Usage:
    # OpenClaw Skill 调用
    # /auto-coding 创建一个 Todo 应用
    
    # Python 模块调用
    from auto_coding_workflow import AutoCodingWorkflow
    
    workflow = AutoCodingWorkflow(
        requirements="创建一个 Todo 应用",
        timeout_minutes=30
    )
    result = await workflow.run()

Version:
    v1.1.0 - 上下文管理增强版（验收标准/边界声明/接口契约）
    
Author:
    Krislu <krislu666@foxmail.com>
"""

__version__ = "1.1.0"
__author__ = "Krislu <krislu666@foxmail.com>"
__all__ = [
    "AutoCodingWorkflow",
    "DependencyManager",
    "AgentSoulLoader",
    "ModelSelector",
    "TaskManager",
]

# 核心模块导出
from .auto_coding_workflow import AutoCodingWorkflow
from .dependency_manager import DependencyManager
from .agent_soul_loader import AgentSoulLoader
from .model_selector import ModelSelector
from .task_manager import TaskManager
