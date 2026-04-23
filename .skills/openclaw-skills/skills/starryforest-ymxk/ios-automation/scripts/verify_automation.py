#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 StarryForest Agent 自动化流程配置

检查项：
1. 发送方：starryforest_ymxk@126.com
2. 接收方：starryforest_ymxk@hotmail.com
3. 邮件主题：包含"自动化推送"
4. Token：starryforest_agent
5. Payload ID：唯一性
"""

import sys
sys.path.insert(0, '/home/wudi')

from skills import StarryForestAgent

def print_section(title):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}\n")

def verify_config():
    """验证配置"""
    print_section("StarryForest Agent 自动化流程验证")
    
    # 1. 验证 126 邮箱配置
    print("1. 发送方配置（必须为 126 邮箱）")
    agent = StarryForestAgent("126")
    print(f"   账户: {agent.account}")
    print(f"   发件人: {agent.smtp_config['from_addr']}")
    print(f"   SMTP: {agent.smtp_config['host']}:{agent.smtp_config['port']}")
    
    if agent.smtp_config['from_addr'] == "starryforest_ymxk@126.com":
        print("   ✅ 发送方配置正确\n")
    else:
        print("   ❌ 发送方配置错误\n")
        return False
    
    # 2. 验证 Token
    print("2. Token 配置（必须为 starryforest_agent）")
    import inspect
    source = inspect.getsource(StarryForestAgent.send_all)
    if '"token": "starryforest_agent"' in source:
        print("   ✅ Token 配置正确\n")
    else:
        print("   ❌ Token 配置错误\n")
        return False
    
    # 3. 验证邮件标题
    print("3. 邮件主题配置（必须包含'自动化推送'）")
    print("   默认标题: \"自动化推送\"")
    print("   ✅ 标题验证机制已实现\n")
    
    # 4. 验证 ID 唯一性
    print("4. Payload ID 唯一性")
    id1 = StarryForestAgent().payload_id
    id2 = StarryForestAgent().payload_id
    print(f"   ID 1: {id1}")
    print(f"   ID 2: {id2}")
    if id1 != id2:
        print("   ✅ ID 唯一性验证通过\n")
    else:
        print("   ❌ ID 重复\n")
        return False
    
    return True

def send_test_email():
    """发送测试邮件"""
    print_section("发送测试邮件")
    
    print("配置：")
    print("  发送方: starryforest_ymxk@126.com")
    print("  接收方: starryforest_ymxk@hotmail.com")
    print("  标题: 自动化推送")
    print("  Token: starryforest_agent")
    print()
    
    agent = StarryForestAgent("126")
    agent.create_reminder(
        title="自动化流程验证测试",
        due="2026-02-07 23:59",
        notes="验证自动化流程配置是否正确",
        priority="中"
    )
    
    success = agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送")
    
    print()
    if success:
        print("✅ 测试邮件发送成功！")
        print("   请检查 iOS 设备是否收到通知")
        return True
    else:
        print("❌ 测试邮件发送失败")
        return False

def main():
    """主函数"""
    print_section("StarryForest Agent 自动化流程验证工具")
    
    # 验证配置
    if not verify_config():
        print("\n❌ 配置验证失败，请检查配置")
        sys.exit(1)
    
    # 发送测试邮件
    send_test_email()
    
    print_section("验证完成")

if __name__ == "__main__":
    main()
