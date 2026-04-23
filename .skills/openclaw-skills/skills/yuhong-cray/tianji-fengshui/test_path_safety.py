#!/usr/bin/env python3
"""
测试天机·玄机子技能路径安全验证
验证路径提取逻辑的安全性改进
"""

import os
import sys
import re
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from tianji_core import TianjiProcessor

def test_path_safety():
    """测试路径安全验证"""
    processor = TianjiProcessor()
    
    print("🧭 天机·玄机子路径安全测试")
    print("=" * 70)
    
    test_cases = [
        # (输入文本, 是否应该提取路径, 安全描述)
        ("分析 /tmp/palm.jpg", True, "安全：/tmp/目录下的图片"),
        ("分析掌纹 /home/test/photos/hand.png", True, "安全：用户home目录下的图片"),
        ("分析 /tmp/../etc/passwd", False, "危险：路径遍历到系统文件"),
        ("看看这个 /etc/passwd", False, "危险：系统配置文件"),
        ("分析图片 ../secret.jpg", False, "危险：相对路径遍历"),
        ("/var/log/syslog", False, "危险：系统日志文件"),
        ("/root/.ssh/id_rsa", False, "危险：root用户密钥"),
        ("分析 ~/.openclaw/config.json", True, "安全：OpenClaw配置文件（用户主目录）"),
        ("/usr/bin/bash", False, "危险：系统二进制"),
        ("/proc/self/environ", False, "危险：进程环境"),
        ("C:\\Windows\\System32\\cmd.exe", False, "危险：Windows系统路径"),
        ("分析 /tmp/normal_image.JPG", True, "安全：大写扩展名"),
        ("/tmp/test_image.gif", False, "危险：不支持的文件扩展名"),
        ("/home/test/../other_user/private.jpg", False, "危险：路径遍历到其他用户"),
        ("分析 /tmp/valid/path/to/image.jpg", True, "安全：/tmp/下的深层路径"),
    ]
    
    results = []
    
    for i, (input_text, should_extract, description) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {description}")
        print(f"输入: '{input_text}'")
        
        # 测试路径提取
        file_path = processor.extract_file_path(input_text)
        
        if file_path:
            print(f"✅ 提取到路径: {file_path}")
            
            # 测试安全验证
            is_safe = processor.is_safe_file_path(file_path)
            safe_status = "✅ 安全" if is_safe else "❌ 危险"
            print(f"安全验证: {safe_status}")
            
            # 验证是否符合预期
            if should_extract and is_safe:
                result = "✅ 通过：正确接受安全路径"
            elif not should_extract and not is_safe:
                result = "✅ 通过：正确拒绝危险路径"
            else:
                result = f"❌ 失败：预期{'接受' if should_extract else '拒绝'}，但{'接受' if is_safe else '拒绝'}"
                
        else:
            print(f"❌ 未提取到路径")
            if not should_extract:
                result = "✅ 通过：正确未提取危险路径"
            else:
                result = "❌ 失败：应该提取但未提取到路径"
        
        print(f"结果: {result}")
        results.append((i, description, result))
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结:")
    print("-" * 70)
    
    passed = 0
    failed = 0
    
    for i, description, result in results:
        status = "✅" if "通过" in result else "❌"
        if "通过" in result:
            passed += 1
        else:
            failed += 1
        print(f"{status} 测试 {i}: {description}")
        print(f"    {result}")
    
    print("-" * 70)
    print(f"总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有路径安全测试通过！")
    else:
        print(f"⚠️  {failed} 个测试失败，需要检查路径安全逻辑")
    
    # 额外测试：文件存在性验证
    print("\n" + "=" * 70)
    print("文件存在性验证测试:")
    print("-" * 70)
    
    # 创建测试文件
    test_file = "/tmp/tianji_test_safety.jpg"
    with open(test_file, "w") as f:
        f.write("test image content")
    
    test_cases_existence = [
        (test_file, True, "存在的文件"),
        ("/tmp/nonexistent_file_12345.jpg", False, "不存在的文件"),
        ("/tmp", False, "目录而非文件"),
    ]
    
    for file_path, should_exist, description in test_cases_existence:
        print(f"\n测试: {description}")
        print(f"路径: {file_path}")
        
        if processor.is_safe_file_path(file_path):
            if should_exist:
                print("✅ 通过：正确验证存在的文件")
            else:
                print("❌ 失败：不应该验证通过不存在的文件/目录")
        else:
            if not should_exist:
                print("✅ 通过：正确拒绝不存在的文件/目录")
            else:
                print("❌ 失败：应该验证通过但被拒绝")
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\n已清理测试文件: {test_file}")
    
    print("\n" + "=" * 70)
    print("安全建议:")
    print("1. 定期运行此测试脚本验证路径安全逻辑")
    print("2. 审查 extract_file_path 和 is_safe_file_path 方法")
    print("3. 用户教育：仅提供明确、受信任的文件路径")
    print("4. 监控技能的文件访问行为")
    print("=" * 70)

if __name__ == "__main__":
    test_path_safety()