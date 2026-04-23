#!/usr/bin/env python3
"""
云瞻威胁情报 - IP地址批量查询示例
"""

import json
import time
import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from hs_ti_plugin import YunzhanThreatIntel

def main():
    # 示例IP地址列表
    ip_list = [
        "45.74.17.165",
        "164.132.75.23", 
        "91.195.240.12",
        "178.16.55.5",
        "185.225.74.140"
    ]
    
    print("🔍 开始查询IP地址威胁情报...")
    print("=" * 60)
    
    # 初始化云瞻客户端
    try:
        intel = YunzhanThreatIntel()
        print("✅ 云瞻客户端初始化成功")
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        return
    
    results = {}
    success_count = 0
    failed_count = 0
    
    # 批量查询
    for i, ip in enumerate(ip_list, 1):
        print(f"\n[{i}/{len(ip_list)}] 查询 IP: {ip}")
        try:
            result = intel.query_ioc(ip)
            if result and 'error' not in result:
                results[ip] = result
                success_count += 1
                print(f"✅ 查询成功")
                print(f"   响应时间: {result.get('response_time_ms', 0)}ms")
            else:
                results[ip] = result
                failed_count += 1
                print(f"❌ 查询失败: {result}")
                
        except Exception as e:
            results[ip] = {'error': str(e)}
            failed_count += 1
            print(f"❌ 查询异常: {e}")
        
        # 避免API限流，添加延迟
        if i < len(ip_list):
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"📊 查询完成!")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {failed_count}")
    
    # 显示响应时间统计
    if intel.response_times:
        total_avg = sum(intel.response_times) / len(intel.response_times)
        print(f"⏱️  平均响应时间: {total_avg:.2f}ms")
        print(f"📈 总查询次数: {len(intel.response_times)}")
    
    return results

if __name__ == "__main__":
    main()
