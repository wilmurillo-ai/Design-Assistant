"""
SSE 适配器层 - 支持多平台技能接入
"""

from .base import SkillAdapter, AdapterRegistry
from .openclaw import OpenClawAdapter
from .gpts import GPTsAdapter
from .dingtalk import DingTalkAdapter
from .feishu import FeishuAdapter

__all__ = [
    "SkillAdapter",
    "AdapterRegistry",
    "OpenClawAdapter",
    "GPTsAdapter",
    "DingTalkAdapter",
    "FeishuAdapter",
]
