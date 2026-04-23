#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有爬虫函数是否有效
"""

import sys
import os

# 添加脚本目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from fetch_policy import (
    crawl_guowuyuan, crawl_cac, crawl_miit, crawl_most, crawl_ndrc,
    crawl_gd, crawl_gz, crawl_sz, crawl_foshan, crawl_dongguan,
    crawl_xinhua, crawl_people, crawl_cctv, crawl_thepaper, crawl_sina, crawl_ifeng,
    crawl_smartcity
)

# 测试函数
def test_crawler(name, func):
    print(f"\n测试 {name}...")
    try:
        # 测试运行，设置days=1，减少数据量
        results = func(1, ['人工智能'])
        if isinstance(results, list):
            print(f"  ✅ 成功，返回 {len(results)} 条结果")
            if results:
                print(f"  示例: {results[0]['title'][:50]}...")
        else:
            print(f"  ❌ 失败，返回类型错误: {type(results)}")
        return True
    except Exception as e:
        print(f"  ❌ 失败，错误: {e}")
        return False

# 测试所有爬虫函数
def main():
    crawlers = [
        ("国务院", crawl_guowuyuan),
        ("网信办", crawl_cac),
        ("工信部", crawl_miit),
        ("科技部", crawl_most),
        ("发改委", crawl_ndrc),
        ("广东省", crawl_gd),
        ("广州市", crawl_gz),
        ("深圳市", crawl_sz),
        ("佛山市", crawl_foshan),
        ("东莞市", crawl_dongguan),
        ("新华社", crawl_xinhua),
        ("人民日报", crawl_people),
        ("央视网", crawl_cctv),
        ("澎湃新闻", crawl_thepaper),
        ("新浪新闻", crawl_sina),
        ("凤凰网", crawl_ifeng),
        ("智慧城市行业分析", crawl_smartcity),
    ]

    print("开始测试所有爬虫函数...")
    print("=" * 60)

    success_count = 0
    total_count = len(crawlers)

    for name, func in crawlers:
        if test_crawler(name, func):
            success_count += 1

    print("=" * 60)
    print(f"测试完成: {success_count}/{total_count} 个爬虫函数正常")

if __name__ == '__main__':
    main()
