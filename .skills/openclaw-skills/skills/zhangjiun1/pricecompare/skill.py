#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
省钱购物助手 Skill
"""

import re
from typing import Optional, Dict, Any

try:
    from config import PLATFORMS, TOKEN_PATTERNS, DEFAULT_SEARCH_PAGE_SIZE
    from utils import (
        call_api, detect_platform, detect_token, extract_search_keyword,
        extract_compare_keyword, extract_url
    )
    from formatters import (
        format_search_results, format_convert_result, format_parse_result,
        format_compare_result, format_error_message
    )
except ImportError:
    from .config import PLATFORMS, TOKEN_PATTERNS, DEFAULT_SEARCH_PAGE_SIZE
    from .utils import (
        call_api, detect_platform, detect_token, extract_search_keyword,
        extract_compare_keyword, extract_url
    )
    from .formatters import (
        format_search_results, format_convert_result, format_parse_result,
        format_compare_result, format_error_message
    )


def search_goods(keyword: str, platform: str = None, page_size: int = DEFAULT_SEARCH_PAGE_SIZE) -> str:
    """
    搜索商品

    Args:
        keyword: 搜索关键词
        platform: 平台标识（可选）
        page_size: 每页数量

    Returns:
        格式化的搜索结果
    """
    if platform:
        result = call_api('/search', {
            'platform': platform,
            'keyword': keyword,
            'page': 1,
            'page_size': page_size
        })
    else:
        result = call_api('/compare', {
            'keyword': keyword
        })

        if result and result.get('success'):
            comparison = result.get('comparison', [])
            return format_search_results(comparison, keyword)

    if not result:
        return format_error_message('api_error')

    if not result.get('success'):
        error = result.get('error', '未知错误')
        return f"❌ 搜索失败：{error}"

    data = result.get('data', [])
    return format_search_results(data if isinstance(data, list) else [data], keyword)


def convert_link(url: str, platform: str = None) -> str:
    """
    转换链接

    Args:
        url: 商品链接
        platform: 平台标识（可选）

    Returns:
        格式化的转换结果
    """
    if not platform:
        platform = detect_platform(url)

    if not platform:
        return format_error_message('invalid_link')

    result = call_api('/convert', {
        'platform': platform,
        'url': url
    })

    if not result:
        return format_error_message('api_error')

    if not result.get('success'):
        error = result.get('error', '未知错误')
        return f"❌ 转换失败：{error}"

    return format_convert_result(result)


def parse_share_content(content: str) -> str:
    """
    解析分享内容

    Args:
        content: 分享内容

    Returns:
        格式化的解析结果
    """
    result = call_api('/parse_share', {
        'content': content
    })

    if not result:
        return format_error_message('api_error')

    if not result.get('success'):
        return format_error_message('parse_failed')

    platform = result.get('platform', '未知平台')
    data = result.get('data', result)

    return format_parse_result(data, platform)


def compare_prices(keyword: str) -> str:
    """
    价格对比

    Args:
        keyword: 商品关键词

    Returns:
        格式化的对比结果
    """
    result = call_api('/compare', {
        'keyword': keyword
    })

    if not result:
        return format_error_message('api_error')

    if not result.get('success'):
        error = result.get('error', '未知错误')
        return f"❌ 价格对比失败：{error}"

    return format_compare_result(result)


def handle_message(message: str) -> Optional[str]:
    """
    处理用户消息（主入口函数）

    Args:
        message: 用户输入的消息

    Returns:
        助手回复，如果不需要处理返回None
    """
    if not message or not message.strip():
        return None

    message = message.strip()

    # 1. 检测是否为价格对比请求
    compare_keyword = extract_compare_keyword(message)
    if compare_keyword:
        return compare_prices(compare_keyword)

    # 2. 检测是否包含口令
    if detect_token(message):
        return parse_share_content(message)

    # 3. 检测是否包含URL
    url = extract_url(message)
    if url:
        return convert_link(url)

    # 4. 检测是否为搜索请求
    search_keyword, platform = extract_search_keyword(message)
    if search_keyword:
        return search_goods(search_keyword, platform)

    # 5. 默认作为搜索关键词处理
    if not message.startswith('http'):
        return search_goods(message)

    return None


# ==================== 测试入口 ====================

if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("省钱购物助手 Skill 测试")
    print("=" * 60)

    # 测试用例
    test_cases = [
        "iPhone 16",
        "在京东搜索手机",
        "对比 iPhone 16",
        "https://item.jd.com/10021724657015.html",
        "【淘宝】假一赔四 https://e.tb.cn/h.iVW7Wnbs5Woz1ZI",
    ]

    if len(sys.argv) > 1:
        # 使用命令行参数测试
        test_message = ' '.join(sys.argv[1:])
        print(f"输入: {test_message}")
        print()
        result = handle_message(test_message)
        print(result or "无需处理")
    else:
        # 运行所有测试
        for test_msg in test_cases:
            print(f"\n{'=' * 60}")
            print(f"输入: {test_msg}")
            print('-' * 60)
            result = handle_message(test_msg)
            print(result or "无需处理")
