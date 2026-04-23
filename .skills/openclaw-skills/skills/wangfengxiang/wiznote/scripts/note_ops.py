#!/usr/bin/env python3
"""
WizNote Note Operations Module
笔记操作模块 - 创建、读取、更新、删除（CRUD）

Author: OpenClaw Worker
Date: 2026-03-26
"""

import os
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wiznote_api import WizNoteAPI, WizNoteAPIError
import logging

logger = logging.getLogger(__name__)


def create_note(
    title: str,
    content: str,
    folder: str = "/",
    tags: Optional[List[str]] = None,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    创建笔记
    
    Args:
        title: 笔记标题
        content: 笔记内容（HTML 格式）
        folder: 所属文件夹路径（默认为根目录）
        tags: 标签列表
        api: WizNoteAPI 实例（可选，不传则自动创建）
        
    Returns:
        Dict: 创建结果，包含 note_id
        
    Raises:
        WizNoteAPIError: 创建失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"创建笔记: {title}")
    
    # 构造请求数据
    data = {
        "title": title,
        "content": content,
        "folder": folder,
        "tags": tags or [],
        "created_time": datetime.now().isoformat(),
        "modified_time": datetime.now().isoformat()
    }
    
    try:
        result = api.post("/api/note/create", data)
        
        note_id = result.get('result', {}).get('note_id')
        logger.info(f"✅ 笔记创建成功，ID: {note_id}")
        
        return {
            "success": True,
            "note_id": note_id,
            "title": title,
            "folder": folder
        }
        
    except WizNoteAPIError as e:
        logger.error(f"创建笔记失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_note(
    note_id: str,
    format: str = "html",
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    获取笔记内容
    
    Args:
        note_id: 笔记 ID
        format: 内容格式（html 或 markdown）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 笔记详情
        
    Raises:
        WizNoteAPIError: 获取失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"获取笔记: {note_id}")
    
    try:
        params = {"format": format} if format != "html" else None
        result = api.get(f"/api/note/{note_id}", params)
        
        note_data = result.get('result', {})
        logger.info(f"✅ 获取笔记成功: {note_data.get('title')}")
        
        return {
            "success": True,
            "note_id": note_id,
            "title": note_data.get('title'),
            "content": note_data.get('content'),
            "folder": note_data.get('folder'),
            "tags": note_data.get('tags', []),
            "created_time": note_data.get('created_time'),
            "modified_time": note_data.get('modified_time')
        }
        
    except WizNoteAPIError as e:
        logger.error(f"获取笔记失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def update_note(
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    folder: Optional[str] = None,
    tags: Optional[List[str]] = None,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    更新笔记
    
    Args:
        note_id: 笔记 ID
        title: 新标题（可选）
        content: 新内容（可选）
        folder: 新文件夹（可选）
        tags: 新标签列表（可选）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 更新结果
        
    Raises:
        WizNoteAPIError: 更新失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"更新笔记: {note_id}")
    
    # 构造更新数据（只包含非 None 的字段）
    data = {
        "modified_time": datetime.now().isoformat()
    }
    
    if title is not None:
        data['title'] = title
    if content is not None:
        data['content'] = content
    if folder is not None:
        data['folder'] = folder
    if tags is not None:
        data['tags'] = tags
    
    try:
        result = api.put(f"/api/note/{note_id}", data)
        
        logger.info(f"✅ 笔记更新成功: {note_id}")
        
        return {
            "success": True,
            "note_id": note_id,
            "updated_fields": list(data.keys())
        }
        
    except WizNoteAPIError as e:
        logger.error(f"更新笔记失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def delete_note(
    note_id: str,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    删除笔记
    
    Args:
        note_id: 笔记 ID
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 删除结果
        
    Raises:
        WizNoteAPIError: 删除失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"删除笔记: {note_id}")
    
    try:
        result = api.delete(f"/api/note/{note_id}")
        
        logger.info(f"✅ 笔记删除成功: {note_id}")
        
        return {
            "success": True,
            "note_id": note_id
        }
        
    except WizNoteAPIError as e:
        logger.error(f"删除笔记失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def list_notes(
    folder: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    获取笔记列表
    
    Args:
        folder: 文件夹路径（可选，不传则获取所有）
        limit: 返回数量限制
        offset: 偏移量（用于分页）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 笔记列表
        
    Raises:
        WizNoteAPIError: 获取失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"获取笔记列表: folder={folder}, limit={limit}, offset={offset}")
    
    params = {
        "limit": limit,
        "offset": offset
    }
    
    if folder:
        params['folder'] = folder
    
    try:
        result = api.get("/api/note/list", params)
        
        notes = result.get('result', {}).get('notes', [])
        total = result.get('result', {}).get('total', len(notes))
        
        logger.info(f"✅ 获取笔记列表成功，共 {total} 条")
        
        return {
            "success": True,
            "notes": notes,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except WizNoteAPIError as e:
        logger.error(f"获取笔记列表失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_note_by_title(
    title: str,
    folder: Optional[str] = None,
    api: Optional[WizNoteAPI] = None
) -> Optional[Dict[str, Any]]:
    """
    根据标题获取笔记（模糊匹配）
    
    Args:
        title: 笔记标题
        folder: 文件夹路径（可选）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict or None: 笔记详情，未找到返回 None
    """
    if api is None:
        api = WizNoteAPI()
    
    # 获取笔记列表
    result = list_notes(folder=folder, limit=1000, api=api)
    
    if not result.get('success'):
        return None
    
    # 模糊匹配标题
    notes = result.get('notes', [])
    for note in notes:
        if title.lower() in note.get('title', '').lower():
            # 找到匹配的笔记，获取完整内容
            return get_note(note['note_id'], api=api)
    
    logger.warning(f"未找到标题包含 '{title}' 的笔记")
    return None


def main():
    """测试入口"""
    print("=" * 60)
    print("笔记操作测试")
    print("=" * 60)
    
    # 初始化 API
    try:
        api = WizNoteAPI()
    except WizNoteAPIError as e:
        print(f"❌ 初始化失败: {e}")
        print("请确保设置了环境变量: WIZ_ENDPOINT, WIZ_USER, WIZ_TOKEN")
        return
    
    # 测试创建笔记
    print("\n测试 1: 创建笔记")
    result = create_note(
        title="测试笔记 - OpenClaw",
        content="<h1>测试笔记</h1><p>这是由 OpenClaw 创建的测试笔记</p>",
        folder="/",
        tags=["测试", "OpenClaw"],
        api=api
    )
    
    if result.get('success'):
        print(f"✅ 创建成功，ID: {result['note_id']}")
        note_id = result['note_id']
        
        # 测试获取笔记
        print("\n测试 2: 获取笔记")
        note = get_note(note_id, api=api)
        if note.get('success'):
            print(f"✅ 获取成功: {note['title']}")
        
        # 测试更新笔记
        print("\n测试 3: 更新笔记")
        update_result = update_note(
            note_id=note_id,
            title="测试笔记 - OpenClaw (已更新)",
            tags=["测试", "OpenClaw", "已更新"],
            api=api
        )
        if update_result.get('success'):
            print(f"✅ 更新成功")
        
        # 测试删除笔记
        print("\n测试 4: 删除笔记")
        delete_result = delete_note(note_id, api=api)
        if delete_result.get('success'):
            print(f"✅ 删除成功")
    else:
        print(f"❌ 创建失败: {result.get('error')}")


if __name__ == '__main__':
    main()
