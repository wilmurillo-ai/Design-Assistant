#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill 测试文件
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skill import handle_message


def load_test_data():
    """加载测试数据"""
    data_path = os.path.join(os.path.dirname(__file__), 'test_data.json')
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def test_search():
    """测试商品搜索"""
    print("\n=== 测试商品搜索 ===")

    test_cases = [
        "iPhone 16",
        "在京东搜索手机",
        "淘宝搜索连衣裙",
    ]

    for test_input in test_cases:
        print(f"\n输入: {test_input}")
        result = handle_message(test_input)
        print(f"输出: {result[:200] if result else 'None'}...")


def test_convert():
    """测试链接转换"""
    print("\n=== 测试链接转换 ===")

    test_cases = [
        "https://item.jd.com/10021724657015.html",
        "https://item.taobao.com/item.htm?id=123456",
        "https://mobile.yangkeduo.com/goods.html?goods_id=123456",
    ]

    for test_input in test_cases:
        print(f"\n输入: {test_input}")
        result = handle_message(test_input)
        print(f"输出: {result[:200] if result else 'None'}...")


def test_parse():
    """测试分享解析"""
    print("\n=== 测试分享解析 ===")

    test_cases = [
        "【淘宝】假一赔四 https://e.tb.cn/h.iVW7Wnbs5Woz1ZI",
        "【京东】10:/京鲜生 云南石林树熟人参果",
        "【拼多多】https://p.pinduoduo.com/xxx",
    ]

    for test_input in test_cases:
        print(f"\n输入: {test_input}")
        result = handle_message(test_input)
        print(f"输出: {result[:200] if result else 'None'}...")


def test_compare():
    """测试价格对比"""
    print("\n=== 测试价格对比 ===")

    test_cases = [
        "对比 iPhone 16",
        "比价 华为手机",
    ]

    for test_input in test_cases:
        print(f"\n输入: {test_input}")
        result = handle_message(test_input)
        print(f"输出: {result[:200] if result else 'None'}...")


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")

    test_cases = [
        "",
        "https://invalid-url.com",
        "xyzabc123nonexistent",
    ]

    for test_input in test_cases:
        print(f"\n输入: {test_input}")
        result = handle_message(test_input)
        print(f"输出: {result if result else 'None'}")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("省钱购物助手 Skill 测试套件")
    print("=" * 60)

    test_search()
    test_convert()
    test_parse()
    test_compare()
    test_error_handling()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
