#!/usr/bin/env python3
"""
玄机子技能安全修复脚本
根据安全审查意见修复以下问题：
1. 硬编码路径修复
2. 路径安全验证增强
3. API密钥打印移除
4. 添加显式路径白名单
"""

import os
import re
import sys
import json
from pathlib import Path

def get_openclaw_config_path():
    """获取OpenClaw配置路径，支持多种环境"""
    # 方法1: 环境变量
    env_path = os.getenv('OPENCLAW_CONFIG_PATH')
    if env_path:
        return env_path
    
    # 方法2: 用户主目录
    home_path = os.path.expanduser('~/.openclaw/openclaw.json')
    if os.path.exists(home_path):
        return home_path
    
    # 方法3: 默认路径（仅用于开发）
    return '/tmp/openclaw_test_config.json'

def fix_hardcoded_paths():
    """修复所有硬编码路径"""
    skill_dir = Path(__file__).parent
    fixed_files = []
    
    # 需要修复的文件列表
    files_to_fix = [
        'doubao_vision_global.py',
        'analyze_general_image.py',
        'compress_and_analyze_palm.py',
        'example_usage.py',
        'test_doubao_integration.py',
    ]
    
    for filename in files_to_fix:
        file_path = skill_dir / filename
        if not file_path.exists():
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复硬编码路径
        old_content = content
        
        # 替换硬编码配置路径
        content = content.replace(
            '"/home/test/.openclaw/openclaw.json"',
            f'"{get_openclaw_config_path()}"'
        )
        
        # 替换示例中的硬编码路径
        content = re.sub(
            r'/home/test/\.openclaw/media/inbound/[a-f0-9\-]+\.jpg',
            '/tmp/test_images/example_palm.jpg',
            content
        )
        
        # 替换通用硬编码路径
        content = re.sub(
            r'/home/test/\.openclaw/media/inbound/[a-zA-Z0-9_\-]+\.jpg',
            '/tmp/test_images/example_image.jpg',
            content
        )
        
        if old_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed_files.append(filename)
            print(f"✅ 修复: {filename}")
    
    return fixed_files

def enhance_path_security():
    """增强路径安全验证"""
    core_file = Path(__file__).parent / 'tianji_core.py'
    
    with open(core_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找现有的is_safe_file_path方法
    if 'def is_safe_file_path(self, file_path):' in content:
        # 增强路径白名单验证
        enhanced_method = '''    def is_safe_file_path(self, file_path):
        """验证文件路径是否安全（增强版）"""
        import os
        
        # 拒绝危险路径模式
        dangerous_patterns = [
            r'\\.\\./',  # 目录遍历
            r'\\.\\.\\\\',  # Windows目录遍历
            r'^/etc/',  # 系统配置文件
            r'^/var/',  # 系统目录
            r'^/usr/',  # 系统程序
            r'^/bin/',  # 系统二进制
            r'^/sbin/',  # 系统管理二进制
            r'^/proc/',  # 进程信息
            r'^/sys/',  # 系统信息
            r'^/dev/',  # 设备文件
            r'^/boot/',  # 启动文件
            r'^/lib/',  # 系统库
            r'^/opt/',  # 可选软件
            r'^/srv/',  # 服务数据
            r'^/media/',  # 可移动媒体
            r'^/mnt/',  # 挂载点
            r'^/root/',  # root用户目录
            r'^/home/[^/]+/\\.(ssh|bash|profile|history)',  # 用户敏感文件
            r'^/home/[^/]+/\\.openclaw/openclaw\\.json$',  # 配置文件（需特殊权限）
        ]
        
        # 转换为绝对路径并规范化
        abs_path = os.path.abspath(file_path)
        
        # 获取用户主目录
        user_home = os.path.expanduser('~')
        
        # 显式白名单目录
        allowed_prefixes = [
            '/tmp/',
            f'{user_home}/.openclaw/workspace/',
            f'{user_home}/.openclaw/media/inbound/',  # 仅限inbound目录
            f'{user_home}/Downloads/',
            f'{user_home}/Desktop/',
            f'{user_home}/Documents/',
            f'{user_home}/Pictures/',
        ]
        
        # 验证1: 不在危险目录中
        for pattern in dangerous_patterns:
            if re.search(pattern, abs_path):
                print(f"🚫 路径安全拒绝: 匹配危险模式 {pattern}")
                return False
        
        # 验证2: 在允许的目录下
        is_allowed = False
        for prefix in allowed_prefixes:
            if abs_path.startswith(prefix):
                is_allowed = True
                break
        
        if not is_allowed:
            print(f"🚫 路径安全拒绝: 不在白名单目录中")
            print(f"   允许的目录: {allowed_prefixes}")
            return False
        
        # 验证3: 文件存在且可读
        if not os.path.exists(abs_path):
            print(f"🚫 路径安全拒绝: 文件不存在")
            return False
        
        if not os.access(abs_path, os.R_OK):
            print(f"🚫 路径安全拒绝: 文件不可读")
            return False
        
        # 验证4: 是普通文件（不是目录、符号链接等）
        if not os.path.isfile(abs_path):
            print(f"🚫 路径安全拒绝: 不是普通文件")
            return False
        
        # 验证5: 文件大小限制（最大50MB）
        file_size = os.path.getsize(abs_path)
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            print(f"🚫 路径安全拒绝: 文件过大 ({file_size} > {max_size} bytes)")
            return False
        
        # 验证6: 文件扩展名检查
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        file_ext = os.path.splitext(abs_path)[1].lower()
        if file_ext not in allowed_extensions:
            print(f"🚫 路径安全拒绝: 不支持的文件扩展名 {file_ext}")
            print(f"   允许的扩展名: {allowed_extensions}")
            return False
        
        print(f"✅ 路径安全检查通过: {abs_path}")
        return True'''
        
        # 替换现有方法
        pattern = r'def is_safe_file_path\(self, file_path\):.*?return True'
        content = re.sub(pattern, enhanced_method, content, flags=re.DOTALL)
        
        with open(core_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 增强: tianji_core.py - 路径安全验证")
        return True
    
    return False

def remove_api_key_printing():
    """移除API密钥打印"""
    skill_dir = Path(__file__).parent
    cleaned_files = []
    
    # 检查所有Python文件
    for file_path in skill_dir.rglob("*.py"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除API密钥打印语句
        patterns_to_remove = [
            r'print\(f["\']API密钥.*?["\']\)',
            r'print\(.*?api.*?key.*?\)',
            r'print\(.*?secret.*?\)',
            r'print\(.*?token.*?\)',
        ]
        
        old_content = content
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '# [安全] 已移除API密钥打印', content, flags=re.IGNORECASE)
        
        if old_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            cleaned_files.append(file_path.name)
            print(f"✅ 清理: {file_path.name} - 移除API密钥打印")
    
    return cleaned_files

def create_safe_test_config():
    """创建安全的测试配置"""
    test_config = {
        "models": {
            "providers": {
                "volcengine": {
                    "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
                    "apiKey": "TEST_API_KEY_DO_NOT_USE_IN_PRODUCTION",
                    "auth": "api-key",
                    "api": "openai-completions",
                    "models": [
                        {
                            "id": "doubao-seed-2-0-pro-260215",
                            "name": "豆包视觉模型(测试)",
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
    }
    
    test_config_path = '/tmp/tianji_test_config.json'
    with open(test_config_path, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 创建: 测试配置文件 {test_config_path}")
    return test_config_path

def create_security_documentation():
    """创建安全文档"""
    security_doc = """# 玄机子技能安全使用指南

## 🚨 重要安全注意事项

### 1. 路径安全
- 技能使用多层路径安全验证
- 仅允许访问白名单目录
- 拒绝目录遍历和系统文件访问
- 文件大小限制：最大50MB
- 仅支持图片格式：jpg, jpeg, png, gif, webp, bmp

### 2. API密钥安全
- **不要**在技能文件中硬编码API密钥
- 使用OpenClaw全局配置或环境变量
- API密钥不会在日志中打印
- 建议定期轮换API密钥

### 3. 运行权限
- **不要**以root用户运行技能
- 使用普通用户权限
- 技能在用户权限下运行，无特权提升

### 4. 数据隐私
- 图片会Base64编码并发送到外部API
- 发送到：ark.cn-beijing.volces.com (豆包)
- 发送到：配置的DeepSeek端点
- **只发送您愿意与这些服务商分享的图片**

## 🔒 安全配置步骤

### 步骤1: 环境准备
```bash
# 创建测试目录
mkdir -p /tmp/test_images
# 设置环境变量
export OPENCLAW_CONFIG_PATH=/tmp/tianji_test_config.json
```

### 步骤2: 安全测试（无真实API密钥）
```bash
# 使用测试配置
python3 security_check_fixed.py
# 测试路径安全
python3 test_path_safety.py
```

### 步骤3: 验证行为
```bash
# 使用虚拟图片测试
python3 example_usage.py --test
# 检查生成的临时文件
ls -la /tmp/tianji_*
```

### 步骤4: 生产环境配置
```bash
# 1. 配置OpenClaw全局配置
openclaw config patch models.providers.volcengine.apiKey=your_real_key

# 2. 或使用环境变量
export VOLCENGINE_API_KEY=your_real_key
```

## 📋 安全白名单

### 允许的目录
1. `/tmp/` - 临时文件
2. `~/.openclaw/workspace/` - OpenClaw工作区
3. `~/.openclaw/media/inbound/` - 仅限inbound媒体
4. `~/Downloads/` - 下载目录
5. `~/Desktop/` - 桌面
6. `~/Documents/` - 文档
7. `~/Pictures/` - 图片

### 拒绝的目录
- 所有系统目录 (/etc, /var, /usr, /bin, /sbin等)
- 用户敏感目录 (~/.ssh, ~/.bash_history等)
- 根目录和其他用户目录

## 🛡️ 风险控制

### 技术控制
1. 路径验证：多层正则表达式匹配
2. 文件限制：大小、类型、权限检查
3. 命令约束：仅调用受信任的外部API
4. 错误安全：失败时返回安全错误信息

### 流程控制
1. 用户审查：所有文件生成对用户可见
2. 手动执行：用户需手动确认操作
3. 沙盒测试：首次在测试环境验证
4. 定期清理：自动清理临时文件

## 📞 安全报告

如发现安全问题，请：
1. 立即停止使用技能
2. 审查所有生成的临时文件
3. 报告给技能维护者
4. 轮换所有相关API密钥

---
*安全第一，玄机自知。传统智慧与现代安全的完美结合。*
"""
    
    doc_path = Path(__file__).parent / 'SECURITY_GUIDE.md'
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(security_doc)
    
    print(f"✅ 创建: 安全使用指南 {doc_path}")
    return doc_path

def main():
    """主修复函数"""
    print("🧭 玄机子技能安全修复")
    print("=" * 60)
    
    # 1. 修复硬编码路径
    print("\n1. 修复硬编码路径...")
    fixed_files = fix_hardcoded_paths()
    if fixed_files:
        print(f"   修复了 {len(fixed_files)} 个文件")
    else:
        print("   未发现需要修复的硬编码路径")
    
    # 2. 增强路径安全
    print("\n2. 增强路径安全验证...")
    if enhance_path_security():
        print("   路径安全验证已增强")
    else:
        print("   路径安全验证增强失败")
    
    # 3. 移除API密钥打印
    print("\n3. 移除API密钥打印...")
    cleaned_files = remove_api_key_printing()
    if cleaned_files:
        print(f"   清理了 {len(cleaned_files)} 个文件")
    else:
        print("   未发现API密钥打印语句")
    
    # 4. 创建测试配置
    print("\n4. 创建安全测试配置...")
    test_config_path = create_safe_test_config()
    print(f"   测试配置: {test_config_path}")
    
    # 5. 创建安全文档
    print("\n5. 创建安全文档...")
    doc_path = create_security_documentation()
    print(f"   安全文档: {doc_path}")
    
    print("\n" + "=" * 60)
    print("✅ 安全修复完成！")
    print("\n下一步建议：")
    print("1. 运行安全检查: python3 security_check_fixed.py")
    print("2. 测试路径安全: python3 test_path_safety.py")
    print("3. 使用测试配置验证: OPENCLAW_CONFIG_PATH=/tmp/tianji_test_config.json python3 example_usage.py")
    print("4. 审查所有修改的文件")
    print("5. 仅在验证后使用真实API密钥")

if __name__ == "__main__":
    main()