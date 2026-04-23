#!/usr/bin/env python3
"""
云瞻威胁情报查询示例 - 增强版
展示新功能：自动识别IOC类型、缓存、结果格式化等
"""

import json
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from hs_ti_plugin import YunzhanThreatIntel, IOCTypeDetector
from result_formatter import ResultFormatter, ResultExporter


def demo_auto_detection():
    """演示IOC类型自动识别"""
    print("\n" + "="*60)
    print("🔍 IOC类型自动识别演示")
    print("="*60)
    
    test_iocs = [
        "192.168.1.1",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "example.com",
        "https://example.com/path",
        "d41d8cd98f00b204e9800998ecf8427e",
        "da39a3ee5e6b4b0d3255bfef95601890afd80709",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "invalid-ioc"
    ]
    
    for ioc in test_iocs:
        detected_type = IOCTypeDetector.detect(ioc)
        print(f"  {ioc:50} -> {detected_type}")


def demo_single_query():
    """演示单次查询（带自动识别）"""
    print("\n" + "="*60)
    print("🔍 单次查询演示（自动识别IOC类型）")
    print("="*60)
    
    intel = YunzhanThreatIntel()
    
    test_iocs = [
        "example.com",
        "8.8.8.8",
        "https://example.com"
    ]
    
    for ioc in test_iocs:
        print(f"\n查询: {ioc}")
        result = intel.query_ioc_auto(ioc)
        
        if 'error' in result:
            print(f"  ❌ 错误: {result['error']}")
        else:
            formatted = ResultFormatter.format_text(result, intel.language)
            print(f"  ✅ 结果:\n{formatted}")


def demo_batch_query():
    """演示批量查询"""
    print("\n" + "="*60)
    print("🔍 批量查询演示")
    print("="*60)
    
    intel = YunzhanThreatIntel()
    
    iocs = [
        {"value": "example.com", "type": "domain"},
        {"value": "8.8.8.8", "type": "ip"},
        {"value": "https://example.com", "type": "url"}
    ]
    
    print(f"\n批量查询 {len(iocs)} 个IOC...")
    result = intel.batch_query(iocs)
    
    formatted = ResultFormatter.format_batch_results(result, intel.language)
    print(formatted)


def demo_cache():
    """演示缓存功能"""
    print("\n" + "="*60)
    print("🔍 缓存功能演示")
    print("="*60)
    
    intel = YunzhanThreatIntel()
    
    test_ioc = "example.com"
    
    print(f"\n第一次查询: {test_ioc}")
    start_time = time.time()
    result1 = intel.query_ioc(test_ioc, use_cache=True)
    time1 = time.time() - start_time
    
    print(f"第二次查询: {test_ioc} (使用缓存)")
    start_time = time.time()
    result2 = intel.query_ioc(test_ioc, use_cache=True)
    time2 = time.time() - start_time
    
    print(f"\n第一次查询耗时: {time1:.4f}秒")
    print(f"第二次查询耗时: {time2:.4f}秒 (缓存)")
    print(f"性能提升: {(time1 - time2) / time1 * 100:.1f}%")
    
    cache_stats = intel.get_cache_stats()
    print(f"\n缓存统计:")
    print(f"  总条目: {cache_stats['total_entries']}")
    print(f"  有效条目: {cache_stats['valid_entries']}")
    print(f"  过期条目: {cache_stats['expired_entries']}")


def demo_export():
    """演示结果导出功能"""
    print("\n" + "="*60)
    print("🔍 结果导出功能演示")
    print("="*60)
    
    intel = YunzhanThreatIntel()
    
    iocs = [
        {"value": "example.com", "type": "domain"},
        {"value": "8.8.8.8", "type": "ip"}
    ]
    
    result = intel.batch_query(iocs)
    results = result['results']
    batch_stats = result['batch_stats']
    total_stats = result['total_stats']
    
    export_dir = os.path.join(os.path.dirname(__file__), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    csv_file = os.path.join(export_dir, f"report_{timestamp}.csv")
    json_file = os.path.join(export_dir, f"report_{timestamp}.json")
    html_file = os.path.join(export_dir, f"report_{timestamp}.html")
    md_file = os.path.join(export_dir, f"report_{timestamp}.md")
    
    print(f"\n导出结果到:")
    
    ResultExporter.export_csv(results, csv_file, intel.language)
    print(f"  ✅ CSV: {csv_file}")
    
    ResultExporter.export_json(results, json_file, batch_stats, total_stats)
    print(f"  ✅ JSON: {json_file}")
    
    ResultExporter.export_html(results, html_file, intel.language, batch_stats, total_stats)
    print(f"  ✅ HTML: {html_file}")
    
    ResultExporter.export_markdown(results, md_file, intel.language, batch_stats, total_stats)
    print(f"  ✅ Markdown: {md_file}")


def demo_advanced_query():
    """演示高级查询"""
    print("\n" + "="*60)
    print("🔍 高级查询演示")
    print("="*60)
    
    intel = YunzhanThreatIntel()
    
    test_ioc = "8.8.8.8"
    
    print(f"\n普通查询: {test_ioc}")
    result_normal = intel.query_ioc(test_ioc, "ip", advanced=False)
    print(f"  结果: {result_normal.get('data', {}).get('result', 'N/A')}")
    
    print(f"\n高级查询: {test_ioc}")
    result_advanced = intel.query_ioc(test_ioc, "ip", advanced=True)
    print(f"  结果: {result_advanced.get('data', {}).get('result', 'N/A')}")
    
    if 'data' in result_advanced:
        data = result_advanced['data']
        print(f"  威胁类型: {data.get('threat_type', [])}")
        print(f"  可信度: {data.get('credibility', 0)}")


def demo_language_switching():
    """演示语言切换"""
    print("\n" + "="*60)
    print("🔍 语言切换演示")
    print("="*60)
    
    intel = YunzhanThreatIntel()
    
    print(f"\n当前语言: {intel.language}")
    print(f"错误消息: {intel.get_text('api_key_not_configured')}")
    
    intel.set_language('cn')
    print(f"\n切换到中文: {intel.language}")
    print(f"错误消息: {intel.get_text('api_key_not_configured')}")
    
    intel.set_language('en')
    print(f"\n切换回英文: {intel.language}")
    print(f"错误消息: {intel.get_text('api_key_not_configured')}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 云瞻威胁情报查询技能 - 增强功能演示")
    print("="*60)
    
    try:
        demo_auto_detection()
        demo_language_switching()
        demo_single_query()
        demo_batch_query()
        demo_cache()
        demo_advanced_query()
        demo_export()
        
        print("\n" + "="*60)
        print("✅ 演示完成！")
        print("="*60)
        print("\n💡 提示:")
        print("  1. 确保在config.json中配置了有效的API密钥")
        print("  2. 导出的报告文件保存在examples/exports/目录")
        print("  3. 日志文件保存在~/.openclaw/logs/hs_ti.log")
        print("  4. 运行测试: python tests/test_hs_ti.py")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
