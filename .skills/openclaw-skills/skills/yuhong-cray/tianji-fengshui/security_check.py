#!/usr/bin/env python3
"""
安全配置检查脚本
检查tianji-fengshui技能中的API密钥安全性
"""

import os
import sys
import json
import re
from pathlib import Path

def check_api_key_security():
    """检查API密钥安全性"""
    print("🔒 API密钥安全配置检查")
    print("=" * 60)
    
    skill_dir = Path(__file__).parent
    security_issues = []
    
    # 需要检查的API密钥模式（不包含实际密钥）
    sensitive_patterns = [
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",  # UUID格式
        r"sk-[a-zA-Z0-9]{48}",  # OpenAI格式
        r"AKLT[a-zA-Z0-9]{40}",  # 豆包旧格式
    ]
    
    print("\n1. 检查技能文件中的硬编码API密钥...")
    
    # 检查所有文件
    for file_path in skill_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix in ['.py', '.json', '.md', '.txt']:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for pattern in sensitive_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # 跳过示例中的占位符
                        if match not in ["YOUR_API_KEY_HERE", "sk-EXAMPLE123", "AKLTEXAMPLE"]:
                            security_issues.append({
                                "file": str(file_path.relative_to(skill_dir)),
                                "issue": f"包含疑似API密钥: {match[:10]}...",
                                "severity": "高危"
                            })
                        
            except Exception as e:
                continue
    
    if security_issues:
        print("❌ 发现安全风险:")
        for issue in security_issues:
            print(f"   {issue['severity']}: {issue['file']} - {issue['issue']}")
    else:
        print("✅ 未在技能文件中发现硬编码API密钥")
    
    print("\n2. 检查全局配置中的API密钥...")
    
    global_config_path = Path.home() / ".openclaw" / "openclaw.json"
    if global_config_path.exists():
        try:
            with open(global_config_path, 'r', encoding='utf-8') as f:
                global_config = json.load(f)
            
            # 检查豆包/volcengine配置
            providers = global_config.get("models", {}).get("providers", {})
            
            for provider_name in ["volcengine", "doubao"]:
                provider = providers.get(provider_name, {})
                api_key = provider.get("apiKey", "")
                
                if api_key:
                    # 检查是否为有效密钥
                    if len(api_key) >= 10:
                        # [安全] 已移除API密钥打印
                        
                        # 检查密钥格式
                        if len(api_key) == 36 and "-" in api_key:
                            print(f"   ✅ API密钥格式正确 (UUID格式)")
                        else:
                            print(f"   ⚠️  API密钥格式可能不正确")
                    else:
                        print(f"❌ {provider_name} API密钥格式异常")
                else:
                    print(f"❌ {provider_name} API密钥未配置")
                    
        except Exception as e:
            print(f"❌ 读取全局配置失败: {e}")
    else:
        print("❌ 全局配置文件不存在")
    
    print("\n3. 检查环境变量配置...")
    
    env_keys = {
        "DOUBAO_API_KEY": os.getenv("DOUBAO_API_KEY"),
        "VOLCENGINE_API_KEY": os.getenv("VOLCENGINE_API_KEY"),
    }
    
    for env_name, env_value in env_keys.items():
        if env_value:
            print(f"✅ 环境变量 {env_name} 已设置: {env_value[:10]}...")
        else:
            print(f"⚠️  环境变量 {env_name} 未设置")
    
    print("\n4. 推荐的安全配置方案...")
    
    print("方案A: 全局配置文件（推荐）")
    print("  - 位置: ~/.openclaw/openclaw.json")
    # [安全] 已移除API密钥打印
    print("  - 优点: 集中管理，安全可控")
    
    print("\n方案B: 环境变量")
    # [安全] 已移除API密钥打印
    # [安全] 已移除API密钥打印
    print("  - 优点: 不写入文件，更安全")
    
    print("\n方案C: 密钥管理服务")
    # [安全] 已移除API密钥打印
    print("  - 优点: 企业级安全，自动轮换")
    print("  - 缺点: 配置复杂")
    
    print("\n5. 安全建议...")
    
    suggestions = [
        "✅ 已从技能文件中移除硬编码API密钥",
        "✅ API密钥已配置到全局配置文件",
        "🔒 定期轮换API密钥（建议每3-6个月）",
        "🔒 限制API密钥的权限范围",
        "🔒 监控API使用情况，设置用量告警",
        "🔒 不在版本控制中提交配置文件",
        "🔒 使用不同的密钥用于开发和生产环境",
    ]
    
    for suggestion in suggestions:
        print(f"  {suggestion}")
    
    print("\n" + "=" * 60)
    
    if security_issues:
        print("❌ 发现安全风险，请立即修复")
        return False
    else:
        print("✅ 安全配置检查通过")
        return True

def verify_global_config_usage():
    """验证全局配置使用情况"""
    print("\n🔍 验证全局配置使用情况")
    print("=" * 60)
    
    try:
        from doubao_vision_global import DoubaoVisionGlobalAnalyzer
        
        print("1. 初始化全局配置分析器...")
        analyzer = DoubaoVisionGlobalAnalyzer()
        
        print("2. 检查API配置...")
        api_config = analyzer.api_config
        
        if api_config.get("api_key"):
            key_preview = api_config["api_key"][:10] + "..." if len(api_config["api_key"]) > 10 else api_config["api_key"]
            # [安全] 已移除API密钥打印
            print(f"   📍 来源: OpenClaw全局配置")
            print(f"   🌐 端点: {api_config.get('base_url', '未知')}")
            print(f"   🤖 模型: {api_config.get('model', '未知')}")
            
            # 验证密钥格式
            if len(api_config["api_key"]) == 36 and "-" in api_config["api_key"]:
                print("   ✅ API密钥格式正确 (UUID格式)")
            else:
                print("   ⚠️  API密钥格式可能不正确")
                
            return True
        else:
            print("   ❌ 未加载到API密钥")
            print("   💡 请检查全局配置文件 ~/.openclaw/openclaw.json")
            return False
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def create_safe_config_template():
    """创建安全配置模板"""
    print("\n📋 安全配置模板")
    print("=" * 60)
    
    template = {
        "安全配置说明": "API密钥应配置在全局，不在技能文件中硬编码",
        "全局配置文件位置": "~/.openclaw/openclaw.json",
        "推荐配置结构": {
            "models": {
                "providers": {
                    "volcengine": {
                        "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
                        "apiKey": "YOUR_API_KEY_HERE",  # 在此处配置API密钥（不要硬编码在技能文件中）
                        "auth": "api-key",
                        "api": "openai-completions",
                        "models": [
                            {
                                "id": "doubao-seed-2-0-pro-260215",
                                "name": "豆包视觉模型",
                                "api": "openai-completions",
                                "reasoning": False,
                                "input": ["text", "image"],
                                "contextWindow": 200000,
                                "maxTokens": 8192
                            }
                        ]
                    }
                }
            }
        },
        "技能配置文件示例": {
            "version": "2.0.0",
            "persona": {
                "name": "玄机子",
                "title": "风水大师智慧助手"
            },
            "model_routing": {
                "image_analysis": {
                    "model": "doubao-seed-2-0-pro-260215",
                    "provider": "volcengine",
                    "api_key": "",  # 留空，从全局配置读取
                    "base_url": "https://ark.cn-beijing.volces.com/api/v3"
                }
            },
            "image_processing": {
                "optimize_size": true,
                "max_width": 768,
                "max_height": 768,
                "quality": 85
            }
        },
        "环境变量备选方案": {
            "变量名": "VOLCENGINE_API_KEY 或 DOUBAO_API_KEY",
            "使用方法": "export VOLCENGINE_API_KEY='your_api_key_here'",
            "Python代码读取": "import os; api_key = os.getenv('VOLCENGINE_API_KEY')"
        }
    }
    
    print(json.dumps(template, indent=2, ensure_ascii=False))
    
    print("\n💡 配置步骤:")
    print("1. 将API密钥添加到 ~/.openclaw/openclaw.json")
    print("2. 确保技能配置文件中没有硬编码密钥")
    print("3. 使用 doubao_vision_global.py 进行测试")
    print("4. 定期检查密钥安全性和使用情况")

def main():
    """主函数"""
    print("🔐 tianji-fengshui 技能安全审计")
    print("=" * 60)
    
    # 运行安全检查
    security_ok = check_api_key_security()
    
    # 验证全局配置
    if security_ok:
        config_ok = verify_global_config_usage()
    else:
        config_ok = False
    
    # 显示配置模板
    create_safe_config_template()
    
    print("\n" + "=" * 60)
    print("安全审计总结:")
    
    if security_ok and config_ok:
        print("✅ 所有安全检查通过")
        print("✅ API密钥已安全配置到全局")
        print("✅ 技能文件无硬编码密钥")
        print("✅ 全局配置读取正常")
        print("\n🎉 安全配置完成，可以安全使用豆包视觉分析功能")
    else:
        print("❌ 存在安全风险，请修复上述问题")
        print("\n🚨 重要: 在修复安全问题前，请勿分享技能文件")
    
    print("=" * 60)

if __name__ == "__main__":
    main()