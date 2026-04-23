#!/usr/bin/env python3
"""
钉钉API集成测试

测试钉钉开放平台API对接
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/skill-evolution-system')

from ssee.adapters import DingTalkAdapter


def test_dingtalk_connection():
    """测试钉钉连接"""
    print("=" * 60)
    print("🔌 钉钉API集成测试")
    print("=" * 60)
    
    # 使用九章法律AI助手的凭证
    adapter = DingTalkAdapter({
        "app_key": "dingwjjrqbfpfsksmkbu",
        "app_secret": "",  # 需要真实secret
        "agent_id": "4363797954",
    })
    
    print("\n📡 1. 测试连接...")
    if adapter.connect():
        print("   ✅ 钉钉连接成功")
        print(f"   📊 Access Token: {adapter.access_token[:20]}...")
    else:
        print("   ⚠️  钉钉连接失败（需要有效的app_secret）")
        print("   💡 演示模式：使用模拟数据")
    
    print("\n📋 2. 获取技能列表...")
    skills = adapter.get_skill_list()
    print(f"   📊 发现 {len(skills)} 个应用")
    for skill in skills:
        print(f"   - {skill['name']} (ID: {skill['id']})")
    
    print("\n📊 3. 获取技能元数据...")
    if skills:
        metadata = adapter.get_skill_metadata(skills[0]['id'])
        print(f"   📋 技能名称: {metadata.get('name', 'N/A')}")
        print(f"   📋 平台: {metadata['platform']}")
        print(f"   📋 Agent ID: {metadata.get('agent_id', 'N/A')}")
    
    print("\n📈 4. 追踪技能使用...")
    track_result = adapter.track_skill_usage("4363797954", {
        "duration": 2.5,
        "success": True,
        "user_count": 1,
    })
    print(f"   ✅ 追踪状态: {track_result['status']}")
    
    print("\n" + "=" * 60)
    print("✅ 钉钉API测试完成")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    test_dingtalk_connection()
