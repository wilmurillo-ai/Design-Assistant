#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
"""

import os

# API配置
# 开发环境: http://localhost:8000
# 生产环境: http://op.squirrel2.cn
API_BASE_URL = os.getenv('API_BASE_URL', 'http://op.squirrel2.cn')
API_PREFIX = '/api/v1'
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

PLATFORMS = {
    'jd': {
        'name': '京东',
        'keywords': ['京东', 'jd.com', 'jingfen', 'u.jd.com', '3.cn'],
        'link_patterns': [
            r'https?://item\.jd\.com/\d+\.html',
            r'https?://u\.jd\.com/[\w\-]+',
            r'https?://3\.cn/[\w\-]+',
            r'https?://jingfen\.jd\.com/detail/[\w\-]+',
        ]
    },
    'taobao': {
        'name': '淘宝',
        'keywords': ['淘宝', '天猫', 'taobao.com', 'tmall.com', 'tb.cn'],
        'link_patterns': [
            r'https?://item\.taobao\.com/item\.htm\?id=\d+',
            r'https?://detail\.tmall\.com/item\.htm\?id=\d+',
            r'https?://m\.tb\.cn/[\w\-]+',
            r'https?://e\.tb\.cn/[\w\-]+',
            r'https?://s\.click\.taobao\.com/[\w\-]+',
        ]
    },
    'pinduoduo': {
        'name': '拼多多',
        'keywords': ['拼多多', 'pinduoduo.com', 'yangkeduo.com'],
        'link_patterns': [
            r'https?://mobile\.yangkeduo\.com/goods\.html\?goods_id=\d+',
            r'https?://p\.pinduoduo\.com/[\w\-]+',
            r'https?://yangkeduo\.com/goods\.html\?goods_id=\d+',
        ]
    }
}

TOKEN_PATTERNS = {
    'symmetric': [
        ('！', '！'),
        ('!', '!'),
        ('$', '$'),
        ('@', '@'),
        ('#', '#'),
        ('￥', '￥'),
    ],
    'special_format': [
        r'\$[^\$]{10,}\$://',
        r'￥[^￥]{10,}￥://',
    ],
    'mixed_string': {
        'min_length': 17,
        'min_types': 2
    }
}

DEFAULT_SEARCH_PAGE_SIZE = 5
MAX_SEARCH_RESULTS = 10

ERROR_MESSAGES = {
    'parse_failed': '口令解析失败',
    'invalid_link': '无法识别的链接格式',
    'no_results': '未找到相关商品',
    'api_error': '系统繁忙，请稍后重试',
    'platform_not_supported': '不支持的平台',
}

SUCCESS_MESSAGES = {
    'parse_success': '商品信息已解析',
    'search_success': '找到相关商品',
    'convert_success': '优惠链接已生成',
    'compare_success': '价格对比完成',
}
