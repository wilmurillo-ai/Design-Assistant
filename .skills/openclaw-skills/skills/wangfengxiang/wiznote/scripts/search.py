#!/usr/bin/env python3
"""
WizNote Search Module
搜索功能模块 - 关键词搜索、标签搜索

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


def search_notes(
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
    folder: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    搜索笔记
    
    Args:
        keyword: 搜索关键词（标题或内容）
        tag: 标签（可同时使用 keyword 和 tag）
        folder: 限定文件夹（可选）
        limit: 返回数量限制
        offset: 偏移量（用于分页）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 搜索结果
        
    Raises:
        WizNoteAPIError: 搜索失败
    """
    if api is None:
        api = WizNoteAPI()
    
    if not keyword and not tag:
        logger.warning("搜索参数为空，请提供 keyword 或 tag")
        return {
            "success": False,
            "error": "请提供搜索关键词或标签"
        }
    
    logger.info(f"搜索笔记: keyword={keyword}, tag={tag}, folder={folder}")
    
    data = {
        "limit": limit,
        "offset": offset
    }
    
    if keyword:
        data['keyword'] = keyword
    if tag:
        data['tag'] = tag
    if folder:
        data['folder'] = folder
    
    try:
        result = api.post("/api/search", data)
        
        notes = result.get('result', {}).get('notes', [])
        total = result.get('result', {}).get('total', len(notes))
        
        logger.info(f"✅ 搜索成功，找到 {total} 条结果")
        
        return {
            "success": True,
            "notes": notes,
            "total": total,
            "keyword": keyword,
            "tag": tag,
            "limit": limit,
            "offset": offset
        }
        
    except WizNoteAPIError as e:
        logger.error(f"搜索失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def search_by_keyword(
    keyword: str,
    folder: Optional[str] = None,
    limit: int = 100,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    按关键词搜索笔记
    
    Args:
        keyword: 搜索关键词
        folder: 限定文件夹（可选）
        limit: 返回数量限制
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 搜索结果
    """
    return search_notes(
        keyword=keyword,
        folder=folder,
        limit=limit,
        api=api
    )


def search_by_tag(
    tag: str,
    folder: Optional[str] = None,
    limit: int = 100,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    按标签搜索笔记
    
    Args:
        tag: 标签名称
        folder: 限定文件夹（可选）
        limit: 返回数量限制
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 搜索结果
    """
    return search_notes(
        tag=tag,
        folder=folder,
        limit=limit,
        api=api
    )


def search_by_multiple_tags(
    tags: List[str],
    operator: str = "AND",
    folder: Optional[str] = None,
    limit: int = 100,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    按多个标签搜索笔记
    
    Args:
        tags: 标签列表
        operator: 逻辑运算符（AND 或 OR）
        folder: 限定文件夹（可选）
        limit: 返回数量限制
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 搜索结果
    """
    if api is None:
        api = WizNoteAPI()
    
    if not tags:
        return {
            "success": False,
            "error": "标签列表不能为空"
        }
    
    logger.info(f"多标签搜索: tags={tags}, operator={operator}")
    
    # 如果是 OR 操作，分别搜索每个标签并合并结果
    if operator.upper() == "OR":
        all_notes = []
        seen_ids = set()
        
        for tag in tags:
            result = search_by_tag(tag=tag, folder=folder, limit=limit, api=api)
            if result.get('success'):
                for note in result.get('notes', []):
                    note_id = note.get('note_id')
                    if note_id and note_id not in seen_ids:
                        all_notes.append(note)
                        seen_ids.add(note_id)
        
        return {
            "success": True,
            "notes": all_notes[:limit],
            "total": len(all_notes),
            "tags": tags,
            "operator": "OR"
        }
    
    # 如果是 AND 操作，搜索第一个标签，然后过滤
    elif operator.upper() == "AND":
        result = search_by_tag(tag=tags[0], folder=folder, limit=limit * len(tags), api=api)
        
        if not result.get('success'):
            return result
        
        notes = result.get('notes', [])
        filtered_notes = []
        
        for note in notes:
            note_tags = note.get('tags', [])
            # 检查是否包含所有标签
            if all(tag in note_tags for tag in tags):
                filtered_notes.append(note)
        
        return {
            "success": True,
            "notes": filtered_notes[:limit],
            "total": len(filtered_notes),
            "tags": tags,
            "operator": "AND"
        }
    
    else:
        return {
            "success": False,
            "error": f"不支持的运算符: {operator}"
        }


def search_advanced(
    query: Dict[str, Any],
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    高级搜索（支持复杂查询条件）
    
    Args:
        query: 查询条件字典，支持：
            - keyword: 关键词
            - tags: 标签列表
            - folder: 文件夹
            - date_from: 起始日期
            - date_to: 结束日期
            - author: 作者
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 搜索结果
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"高级搜索: {query}")
    
    try:
        result = api.post("/api/search/advanced", query)
        
        notes = result.get('result', {}).get('notes', [])
        total = result.get('result', {}).get('total', len(notes))
        
        logger.info(f"✅ 高级搜索成功，找到 {total} 条结果")
        
        return {
            "success": True,
            "notes": notes,
            "total": total,
            "query": query
        }
        
    except WizNoteAPIError as e:
        logger.error(f"高级搜索失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_all_tags(
    folder: Optional[str] = None,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    获取所有标签
    
    Args:
        folder: 限定文件夹（可选）
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 标签列表
        
    Raises:
        WizNoteAPIError: 获取失败
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"获取标签列表: folder={folder}")
    
    params = {}
    if folder:
        params['folder'] = folder
    
    try:
        result = api.get("/api/tags", params)
        
        tags = result.get('result', {}).get('tags', [])
        logger.info(f"✅ 获取标签成功，共 {len(tags)} 个")
        
        return {
            "success": True,
            "tags": tags,
            "total": len(tags)
        }
        
    except WizNoteAPIError as e:
        logger.error(f"获取标签失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def suggest_keywords(
    prefix: str,
    limit: int = 10,
    api: Optional[WizNoteAPI] = None
) -> Dict[str, Any]:
    """
    关键词自动补全建议
    
    Args:
        prefix: 关键词前缀
        limit: 返回数量限制
        api: WizNoteAPI 实例（可选）
        
    Returns:
        Dict: 建议列表
    """
    if api is None:
        api = WizNoteAPI()
    
    logger.info(f"获取关键词建议: prefix={prefix}")
    
    params = {
        "prefix": prefix,
        "limit": limit
    }
    
    try:
        result = api.get("/api/search/suggest", params)
        
        suggestions = result.get('result', {}).get('suggestions', [])
        logger.info(f"✅ 获取建议成功，共 {len(suggestions)} 条")
        
        return {
            "success": True,
            "suggestions": suggestions,
            "prefix": prefix
        }
        
    except WizNoteAPIError as e:
        logger.error(f"获取建议失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def format_search_results(result: Dict[str, Any]) -> str:
    """
    格式化搜索结果为可读字符串
    
    Args:
        result: search_notes 的返回结果
        
    Returns:
        str: 格式化后的字符串
    """
    if not result.get('success'):
        return f"❌ 搜索失败: {result.get('error')}"
    
    notes = result.get('notes', [])
    total = result.get('total', 0)
    
    output = [f"搜索结果（共 {total} 条）：", "=" * 60]
    
    if not notes:
        output.append("未找到匹配的笔记")
        return "\n".join(output)
    
    for idx, note in enumerate(notes, 1):
        title = note.get('title', '无标题')
        folder = note.get('folder', '/')
        tags = note.get('tags', [])
        created = note.get('created_time', '未知时间')
        
        output.append(f"\n{idx}. {title}")
        output.append(f"   文件夹: {folder}")
        if tags:
            output.append(f"   标签: {', '.join(tags)}")
        output.append(f"   创建时间: {created}")
    
    return "\n".join(output)


def main():
    """测试入口"""
    print("=" * 60)
    print("搜索功能测试")
    print("=" * 60)
    
    # 初始化 API
    try:
        api = WizNoteAPI()
    except WizNoteAPIError as e:
        print(f"❌ 初始化失败: {e}")
        print("请确保设置了环境变量: WIZ_ENDPOINT, WIZ_USER, WIZ_TOKEN")
        return
    
    # 测试关键词搜索
    print("\n测试 1: 关键词搜索")
    result = search_by_keyword(keyword="OpenClaw", limit=5, api=api)
    print(format_search_results(result))
    
    # 测试标签搜索
    print("\n测试 2: 标签搜索")
    result = search_by_tag(tag="测试", limit=5, api=api)
    print(format_search_results(result))
    
    # 测试组合搜索
    print("\n测试 3: 组合搜索（关键词 + 标签）")
    result = search_notes(keyword="OpenClaw", tag="测试", limit=5, api=api)
    print(format_search_results(result))
    
    # 测试获取所有标签
    print("\n测试 4: 获取所有标签")
    tags_result = get_all_tags(api=api)
    if tags_result.get('success'):
        tags = tags_result.get('tags', [])
        print(f"✅ 共 {len(tags)} 个标签:")
        for tag in tags[:10]:  # 只显示前 10 个
            print(f"  - {tag}")
    else:
        print(f"❌ 获取标签失败: {tags_result.get('error')}")


if __name__ == '__main__':
    main()
