#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet Chat 常量模块 - 集中管理所有常量
"""

from enum import Enum

# ============== API 基础配置 ==============

# API 基础 URL
API_BASE_URL = "https://api.scnet.cn"
API_CENTER_URL = "https://www.scnet.cn/ac/openapi/v2/center"
API_USER_URL = "https://www.scnet.cn/ac/openapi/v2/user"

# 默认超时设置（秒）
DEFAULT_TIMEOUT = 30
UPLOAD_TIMEOUT = 300
DOWNLOAD_TIMEOUT = 300

# ============== 作业状态 ==============

class JobStatus(str, Enum):
    """作业状态枚举"""
    RUNNING = "statR"      # 🟢 运行中
    QUEUED = "statQ"       # ⏳ 排队中
    WAITING = "statW"      # ⏳ 等待中
    HELD = "statH"         # ⏸️ 保留
    SUSPENDED = "statS"    # ⏸️ 挂起
    EXITED = "statE"       # ❌ 退出
    COMPLETED = "statC"    # ✅ 完成
    TERMINATED = "statT"   # 🛑 终止
    DELETED = "statDE"     # 🗑️ 删除
    UNKNOWN = "unknown"    # 未知


# 作业状态中文映射
JOB_STATUS_MAP = {
    JobStatus.RUNNING: "🟢 运行中",
    JobStatus.QUEUED: "⏳ 排队中",
    JobStatus.WAITING: "⏳ 等待中",
    JobStatus.HELD: "⏸️ 保留",
    JobStatus.SUSPENDED: "⏸️ 挂起",
    JobStatus.EXITED: "❌ 退出",
    JobStatus.COMPLETED: "✅ 完成",
    JobStatus.TERMINATED: "🛑 终止",
    JobStatus.DELETED: "🗑️ 删除",
    JobStatus.UNKNOWN: "未知",
}

# 活跃状态列表（作业还在运行中）
ACTIVE_JOB_STATUSES = [
    JobStatus.RUNNING,
    JobStatus.QUEUED,
    JobStatus.WAITING,
]

# 结束状态列表
TERMINAL_JOB_STATUSES = [
    JobStatus.COMPLETED,
    JobStatus.TERMINATED,
    JobStatus.EXITED,
    JobStatus.DELETED,
]


# ============== Notebook 状态 ==============

class NotebookStatus(str, Enum):
    """Notebook 状态枚举"""
    CREATING = "Creating"
    RESTARTING = "Restarting"
    RUNNING = "Running"
    TERMINATED = "Terminated"
    FAILED = "Failed"
    SHUTTING = "Shutting"


NOTEBOOK_STATUS_MAP = {
    NotebookStatus.CREATING: "创建中",
    NotebookStatus.RESTARTING: "开机中",
    NotebookStatus.RUNNING: "运行中",
    NotebookStatus.TERMINATED: "已关机",
    NotebookStatus.FAILED: "失败",
    NotebookStatus.SHUTTING: "关机中",
}


# ============== 容器状态 ==============

class ContainerStatus(str, Enum):
    """容器状态枚举"""
    RUNNING = "Running"
    DEPLOYING = "Deploying"
    WAITING = "Waiting"
    TERMINATED = "Terminated"
    FAILED = "Failed"
    COMPLETED = "Completed"


CONTAINER_STATUS_MAP = {
    ContainerStatus.RUNNING: "运行中",
    ContainerStatus.DEPLOYING: "部署中",
    ContainerStatus.WAITING: "等待中",
    ContainerStatus.TERMINATED: "已终止",
    ContainerStatus.FAILED: "失败",
    ContainerStatus.COMPLETED: "已完成",
}


# ============== 计算中心名称映射 ==============

CLUSTER_KEYWORDS = {
    "昆山": "华东一区【昆山】",
    "华东一区": "华东一区【昆山】",
    "哈尔滨": "东北一区【哈尔滨】",
    "东北": "东北一区【哈尔滨】",
    "东北一区": "东北一区【哈尔滨】",
    "乌镇": "华东三区【乌镇】",
    "华东三区": "华东三区【乌镇】",
    "西安": "西北一区【西安】",
    "西北": "西北一区【西安】",
    "西北一区": "西北一区【西安】",
    "雄衡": "华北一区【雄衡】",
    "华北": "华北一区【雄衡】",
    "华北一区": "华北一区【雄衡】",
    "山东": "华东四区【山东】",
    "华东四区": "华东四区【山东】",
    "四川": "西南一区【四川】",
    "西南": "西南一区【四川】",
    "西南一区": "西南一区【四川】",
    "核心": "核心节点【分区一】",
    "核心节点": "核心节点【分区一】",
    "分区一": "核心节点【分区一】",
    "分区二": "核心节点【分区二】",
}


# ============== 错误码 ==============

class ErrorCode:
    """API 错误码"""
    SUCCESS = "0"
    FILE_EXISTS = "911021"  # 文件/目录已存在


# ============== 默认配置 ==============

DEFAULT_JOB_CONFIG = {
    "nnodes": "1",
    "ppn": "1",
    "wall_time": "01:00:00",
    "work_dir": "~/claw_workspace",
    "submit_type": "cmd",
    "appname": "BASE",
    "queue": "debug",
}

DEFAULT_NOTEBOOK_CONFIG = {
    "accelerator_type": "DCU",
    "accelerator_number": "1",
    "mount_home": True,
}


# 导出
__all__ = [
    # API 配置
    'API_BASE_URL', 'API_CENTER_URL', 'API_USER_URL',
    'DEFAULT_TIMEOUT', 'UPLOAD_TIMEOUT', 'DOWNLOAD_TIMEOUT',
    # 作业状态
    'JobStatus', 'JOB_STATUS_MAP', 'ACTIVE_JOB_STATUSES', 'TERMINAL_JOB_STATUSES',
    # Notebook 状态
    'NotebookStatus', 'NOTEBOOK_STATUS_MAP',
    # 容器状态
    'ContainerStatus', 'CONTAINER_STATUS_MAP',
    # 计算中心
    'CLUSTER_KEYWORDS',
    # 错误码
    'ErrorCode',
    # 默认配置
    'DEFAULT_JOB_CONFIG', 'DEFAULT_NOTEBOOK_CONFIG',
]
