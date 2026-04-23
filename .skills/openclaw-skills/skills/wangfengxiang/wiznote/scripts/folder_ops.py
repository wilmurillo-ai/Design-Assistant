#!/usr/bin/env python3
"""
WizNote Folder Operations Module
文件夹/分类管理模块

Author: OpenClaw Worker
Date: 2026-03-26
"""

import os
import sys
from typing import Optional, Dict, Any, List

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wiznote_api import WizNoteAPI, WizNoteAPIError
import logging

logger = logging.getLogger(__name__)


def create_folder(
    name: str,
    parent: str = "/",
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    创建文件夹
    
    Args:
        name: 文件夹名称
        parent: 父文件夹路径（默认为根目录）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 创建结果，包含 folder_id
        
    Raises:
        WizNoteAPIError: 创建失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"创建文件夹: {name} (父文件夹: {parent})")
    
    data = {
        "name": name,
        "parent": parent
    }
    
    try:
        result = api.post("/api/folder/create", data)
        
        folder_id = result.get('result', {}).get('folder_id')
        logger.info(f"✅ 文件夹创建成功，ID: {folder_id}")
        
        return {
            "success": True,
            "folder_id": folder_id,
            "name": name,
            "parent": parent
        }
        
    except WizNoteAPIError as e:
        logger.error(f"创建文件夹失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def list_folders(
    parent: Optional[str] = None,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    获取文件夹列表
    
    Args:
        parent: 父文件夹路径（可选，不传则获取根目录下的文件夹）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 文件夹列表
        
    Raises:
        WizNoteAPIError: 获取失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"获取文件夹列表: parent={parent or '/'}")
    
    params = {}
    if parent:
        params['parent'] = parent
    
    try:
        result = api.get("/api/folder/list", params)
        
        folders = result.get('result', {}).get('folders', [])
        logger.info(f"✅ 获取文件夹列表成功，共 {len(folders)} 个")
        
        return {
            "success": True,
            "folders": folders,
            "total": len(folders)
        }
        
    except WizNoteAPIError as e:
        logger.error(f"获取文件夹列表失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_folder(
    folder_id: str,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    获取文件夹详情
    
    Args:
        folder_id: 文件夹 ID
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 文件夹详情
        
    Raises:
        WizNoteAPIError: 获取失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"获取文件夹详情: {folder_id}")
    
    try:
        result = api.get(f"/api/folder/{folder_id}")
        
        folder_data = result.get('result', {})
        logger.info(f"✅ 获取文件夹详情成功: {folder_data.get('name')}")
        
        return {
            "success": True,
            "folder_id": folder_id,
            "name": folder_data.get('name'),
            "parent": folder_data.get('parent'),
            "note_count": folder_data.get('note_count', 0),
            "created_time": folder_data.get('created_time')
        }
        
    except WizNoteAPIError as e:
        logger.error(f"获取文件夹详情失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def delete_folder(
    folder_id: str,
    force: bool = False,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    删除文件夹
    
    Args:
        folder_id: 文件夹 ID
        force: 是否强制删除（即使文件夹内有笔记）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 删除结果
        
    Raises:
        WizNoteAPIError: 删除失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"删除文件夹: {folder_id} (force={force})")
    
    params = {"force": "true"} if force else None
    
    try:
        result = api.delete(f"/api/folder/{folder_id}")
        
        logger.info(f"✅ 文件夹删除成功: {folder_id}")
        
        return {
            "success": True,
            "folder_id": folder_id
        }
        
    except WizNoteAPIError as e:
        logger.error(f"删除文件夹失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def move_note(
    note_id: str,
    target_folder: str,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    移动笔记到指定文件夹
    
    Args:
        note_id: 笔记 ID
        target_folder: 目标文件夹路径
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 移动结果
        
    Raises:
        WizNoteAPIError: 移动失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"移动笔记: {note_id} -> {target_folder}")
    
    data = {
        "note_id": note_id,
        "target_folder": target_folder
    }
    
    try:
        result = api.post("/api/note/move", data)
        
        logger.info(f"✅ 笔记移动成功")
        
        return {
            "success": True,
            "note_id": note_id,
            "target_folder": target_folder
        }
        
    except WizNoteAPIError as e:
        logger.error(f"移动笔记失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def rename_folder(
    folder_id: str,
    new_name: str,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    重命名文件夹
    
    Args:
        folder_id: 文件夹 ID
        new_name: 新名称
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 重命名结果
        
    Raises:
        WizNoteAPIError: 重命名失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"重命名文件夹: {folder_id} -> {new_name}")
    
    data = {
        "name": new_name
    }
    
    try:
        result = api.put(f"/api/folder/{folder_id}", data)
        
        logger.info(f"✅ 文件夹重命名成功")
        
        return {
            "success": True,
            "folder_id": folder_id,
            "new_name": new_name
        }
        
    except WizNoteAPIError as e:
        logger.error(f"重命名文件夹失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_folder_tree(
    root: str = "/",
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    获取文件夹树形结构
    
    Args:
        root: 根文件夹路径（默认为根目录）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 树形结构的文件夹列表
        
    Raises:
        WizNoteAPIError: 获取失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"获取文件夹树: root={root}")
    
    def build_tree(parent_path: str) -> List[Dict]:
        """递归构建文件夹树"""
        result = list_folders(parent=parent_path, api=api)
        
        if not result.get('success'):
            return []
        
        folders = result.get('folders', [])
        tree = []
        
        for folder in folders:
            node = {
                "id": folder.get('folder_id'),
                "name": folder.get('name'),
                "path": folder.get('path'),
                "note_count": folder.get('note_count', 0),
                "children": []
            }
            
            # 递归获取子文件夹
            children = build_tree(folder.get('path'))
            if children:
                node['children'] = children
            
            tree.append(node)
        
        return tree
    
    try:
        tree = build_tree(root)
        
        logger.info(f"✅ 获取文件夹树成功")
        
        return {
            "success": True,
            "tree": tree,
            "root": root
        }
        
    except Exception as e:
        logger.error(f"获取文件夹树失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """测试入口"""
    print("=" * 60)
    print("文件夹操作测试")
    print("=" * 60)
    
    # 初始化 API
    try:
        api = WizNoteAPI()
    except WizNoteAPIError as e:
        print(f"❌ 初始化失败: {e}")
        print("请确保设置了环境变量: WIZ_ENDPOINT, WIZ_USER, WIZ_TOKEN")
        return
    
    # 测试创建文件夹
    print("\n测试 1: 创建文件夹")
    result = create_folder(
        name="测试文件夹 - OpenClaw",
        parent="/",
        api=api
    )
    
    if result.get('success'):
        print(f"✅ 创建成功，ID: {result['folder_id']}")
        folder_id = result['folder_id']
        
        # 测试列出文件夹
        print("\n测试 2: 列出文件夹")
        folders_result = list_folders(api=api)
        if folders_result.get('success'):
            folders = folders_result.get('folders', [])
            print(f"✅ 共 {len(folders)} 个文件夹")
            for folder in folders[:5]:  # 只显示前 5 个
                print(f"  - {folder.get('name')} ({folder.get('note_count', 0)} 篇笔记)")
        
        # 测试重命名文件夹
        print("\n测试 3: 重命名文件夹")
        rename_result = rename_folder(
            folder_id=folder_id,
            new_name="测试文件夹 - OpenClaw (已重命名)",
            api=api
        )
        if rename_result.get('success'):
            print(f"✅ 重命名成功")
        
        # 测试删除文件夹
        print("\n测试 4: 删除文件夹")
        delete_result = delete_folder(folder_id, api=api)
        if delete_result.get('success'):
            print(f"✅ 删除成功")
    else:
        print(f"❌ 创建失败: {result.get('error')}")


if __name__ == '__main__':
    main()
