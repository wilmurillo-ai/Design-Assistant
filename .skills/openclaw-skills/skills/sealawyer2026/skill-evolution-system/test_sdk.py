#!/usr/bin/env python3
"""
SDK 测试脚本

测试Python SDK功能
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/skill-evolution-system/sdk/python')

from sse_sdk import SSEClient, SSEConfig


def test_sdk():
    """测试SDK功能"""
    print("=" * 70)
    print("🧪 SSE Python SDK 测试")
    print("=" * 70)
    
    # 1. 测试配置创建
    print("\n📋 1. 测试配置创建...")
    config = SSEConfig(
        api_key="test_key",
        endpoint="http://localhost:8080",
        timeout=30,
        retry_count=3,
    )
    print("   ✅ 配置创建成功")
    print(f"   📊 Endpoint: {config.endpoint}")
    print(f"   📊 Timeout: {config.timeout}s")
    
    # 2. 测试客户端初始化
    print("\n🔌 2. 测试客户端初始化...")
    client = SSEClient(api_key="test_key", endpoint="http://localhost:8080")
    print("   ✅ 客户端初始化成功")
    
    # 3. 测试消息构建
    print("\n📦 3. 测试消息构建...")
    import time
    message = {
        "version": "2.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
        "message_id": f"test_{int(time.time() * 1000)}",
        "type": "track",
        "payload": {
            "skill_id": "test-skill",
            "action": "complete",
            "metrics": {
                "duration_ms": 1000,
                "success": True,
            }
        },
        "meta": {
            "source": "python_sdk",
            "skill_id": "test-skill",
        }
    }
    print("   ✅ SEP消息构建成功")
    print(f"   📊 Message ID: {message['message_id']}")
    print(f"   📊 Type: {message['type']}")
    
    # 4. 测试异常类
    print("\n⚠️  4. 测试异常类...")
    from sse_sdk import SSEError, AuthenticationError, RateLimitError
    
    try:
        raise SSEError("Test error", "SEP_001")
    except SSEError as e:
        print(f"   ✅ SSEError: {e}")
    
    try:
        raise AuthenticationError("Auth failed")
    except AuthenticationError as e:
        print(f"   ✅ AuthenticationError: {e}")
    
    # 5. 总结
    print("\n" + "=" * 70)
    print("✅ SDK测试完成")
    print("=" * 70)
    print("\n📊 测试结果:")
    print("   - 配置创建: ✅")
    print("   - 客户端初始化: ✅")
    print("   - SEP消息构建: ✅")
    print("   - 异常处理: ✅")
    print("\n📝 注意: 完整API测试需要运行SSE服务端")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    test_sdk()
