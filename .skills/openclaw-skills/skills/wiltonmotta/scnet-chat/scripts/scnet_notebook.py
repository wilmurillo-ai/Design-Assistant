#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet Notebook Manager - Notebook实例管理模块

注意：此模块已合并到 scnet_chat.py，保留此文件是为了向后兼容。
请直接从 scnet_chat 导入：
    from scnet_chat import NotebookManager, NotebookCreateWizard
"""

# 从主模块导入，保持向后兼容
from scnet_chat import NotebookManager, NotebookCreateWizard

# 导出
__all__ = ['NotebookManager', 'NotebookCreateWizard']


if __name__ == "__main__":
    print("Notebook Manager Module")
    print("请使用: from scnet_chat import NotebookManager")
