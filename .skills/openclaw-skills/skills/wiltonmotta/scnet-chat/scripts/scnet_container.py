#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet Container Manager - 容器实例管理模块

注意：此模块已合并到 scnet_chat.py，保留此文件是为了向后兼容。
请直接从 scnet_chat 导入：
    from scnet_chat import ContainerManager, ContainerCreateWizard
"""

# 从主模块导入，保持向后兼容
from scnet_chat import ContainerManager

# 容器创建向导类（scnet_chat.py 中没有，需要在这里定义）
from typing import Optional, Dict, Any

class ContainerCreateWizard:
    """容器创建向导"""
    
    def __init__(self, manager: ContainerManager):
        self.manager = manager
        self.config = {}
    
    def preview_config(self) -> str:
        """预览配置"""
        lines = [
            "📋 容器配置预览:",
            "-" * 40,
            f"实例名称: {self.config.get('instanceServiceName', '未设置')}",
            f"任务类型: {self.config.get('taskType', '未设置')}",
            f"加速器类型: {self.config.get('acceleratorType', '未设置')}",
            f"镜像: {self.config.get('version', '未设置')}",
            f"CPU: {self.config.get('cpuNumber', '未设置')} 核",
            f"GPU: {self.config.get('gpuNumber', '未设置')} 个",
            f"内存: {self.config.get('ramSize', '未设置')} MB",
            f"资源分组: {self.config.get('resourceGroup', '未设置')}",
            f"实例数量: {self.config.get('taskNumber', 1)}",
            f"超时时间: {self.config.get('timeoutLimit', 'unlimited')}",
            "-" * 40,
        ]
        return "\n".join(lines)
    
    def create(self) -> Optional[str]:
        """创建容器"""
        result = self.manager.create_container(self.config)
        
        if result and result.get("code") == "0":
            return result.get("data")  # 返回任务ID
        return None


# 容器状态映射
CONTAINER_STATUS_MAP = {
    "Running": "运行中",
    "Deploying": "部署中",
    "Waiting": "等待中",
    "Terminated": "已终止",
    "Failed": "失败",
    "Completed": "已完成"
}


def format_container_status(status: str) -> str:
    """格式化容器状态"""
    return CONTAINER_STATUS_MAP.get(status, status)


# 导出
__all__ = ['ContainerManager', 'ContainerCreateWizard', 'format_container_status', 'CONTAINER_STATUS_MAP']


if __name__ == "__main__":
    print("Container Manager Module")
    print("请使用: from scnet_chat import ContainerManager")
