#!/usr/bin/env python3
"""
多平台集成测试

测试所有平台适配器
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/skill-evolution-system')

from ssee.adapters import AdapterRegistry, OpenClawAdapter


def test_all_platforms():
    """测试所有平台"""
    print("=" * 70)
    print("🌍 多平台适配器集成测试")
    print("=" * 70)
    
    platforms = AdapterRegistry.list_adapters()
    print(f"\n📋 已注册平台: {', '.join(platforms)}")
    
    # 测试 OpenClaw
    print("\n" + "-" * 70)
    print("🔷 OpenClaw 平台")
    print("-" * 70)
    
    adapter = OpenClawAdapter({
        "skills_dir": "~/.openclaw/workspace/skills"
    })
    
    if adapter.connect():
        print("   ✅ 连接成功")
        skills = adapter.get_skill_list()
        print(f"   📊 发现 {len(skills)} 个技能")
        
        for skill in skills[:5]:
            print(f"      - {skill['name']} (v{skill['version']})")
        if len(skills) > 5:
            print(f"      ... 还有 {len(skills) - 5} 个")
    else:
        print("   ❌ 连接失败")
    
    # 测试钉钉
    print("\n" + "-" * 70)
    print("🔷 钉钉平台")
    print("-" * 70)
    
    from ssee.adapters import DingTalkAdapter
    adapter = DingTalkAdapter({
        "app_key": "dingwjjrqbfpfsksmkbu",
        "app_secret": "",  # 需要真实secret
        "agent_id": "4363797954",
    })
    
    if adapter.connect():
        print("   ✅ 连接成功")
    else:
        print("   ⚠️  需要有效凭证（演示模式）")
    
    skills = adapter.get_skill_list()
    print(f"   📊 发现 {len(skills)} 个应用")
    for skill in skills:
        print(f"      - {skill['name']}")
    
    # 测试飞书
    print("\n" + "-" * 70)
    print("🔷 飞书平台")
    print("-" * 70)
    
    from ssee.adapters import FeishuAdapter
    adapter = FeishuAdapter({
        "app_id": "cli_xxx",  # 需要真实app_id
        "app_secret": "",  # 需要真实secret
    })
    
    if adapter.connect():
        print("   ✅ 连接成功")
    else:
        print("   ⚠️  需要有效凭证（演示模式）")
    
    # 测试GPTs
    print("\n" + "-" * 70)
    print("🔷 GPTs 平台")
    print("-" * 70)
    
    from ssee.adapters import GPTsAdapter
    adapter = GPTsAdapter({
        "api_key": "",  # 需要OpenAI API key
    })
    
    if adapter.connect():
        print("   ✅ 连接成功")
    else:
        print("   ⚠️  需要API key（演示模式）")
    
    print("\n" + "=" * 70)
    print("✅ 多平台测试完成")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    test_all_platforms()
