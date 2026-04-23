#!/usr/bin/env python3
"""
玄机子技能最终安全增强脚本
根据安全审查意见进行最终修复
"""

import os
import re
import json
import sys
from pathlib import Path

def add_privacy_warnings():
    """添加隐私警告到所有相关文件"""
    skill_dir = Path(__file__).parent
    privacy_warning = """
⚠️ **隐私重要提示**
本技能会将图片Base64编码后发送到以下第三方API端点：
1. ark.cn-beijing.volces.com (火山引擎豆包视觉模型)
2. 配置的DeepSeek API端点

**只发送您愿意与这些服务商分享的图片**
- 避免发送包含个人身份信息、敏感文档、私人照片的图片
- 建议使用测试图片或已脱敏的图片
- 发送前确认图片内容符合服务商的使用条款
"""
    
    files_to_update = [
        'SKILL.md',
        'SECURITY_GUIDE.md',
        'install.sh',
        'tianji_core.py',
    ]
    
    updated_files = []
    for filename in files_to_update:
        file_path = skill_dir / filename
        if not file_path.exists():
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在文件开头或适当位置添加隐私警告
        if filename == 'SKILL.md':
            # 在快速使用部分后添加
            if '## 快速使用' in content and '⚠️ **隐私重要提示**' not in content:
                content = content.replace('## 快速使用', f'## 快速使用\n\n{privacy_warning}')
                updated_files.append(filename)
        
        elif filename == 'SECURITY_GUIDE.md':
            # 在开头添加
            if not content.startswith('⚠️ **隐私重要提示**'):
                content = privacy_warning + '\n\n' + content
                updated_files.append(filename)
        
        elif filename == 'install.sh':
            # 在脚本开头添加
            if not content.startswith('#!/bin/bash\n\n# ⚠️'):
                lines = content.split('\n')
                if len(lines) > 1:
                    lines.insert(1, '\n# ⚠️ 隐私重要提示')
                    lines.insert(2, '# 本技能会将图片发送到第三方API端点，请仔细阅读SKILL.md中的隐私警告')
                    content = '\n'.join(lines)
                    updated_files.append(filename)
        
        elif filename == 'tianji_core.py':
            # 在类文档字符串中添加
            if 'class TianjiProcessor:' in content and '隐私重要提示' not in content:
                class_start = content.find('class TianjiProcessor:')
                docstring_start = content.find('"""', class_start)
                if docstring_start != -1:
                    docstring_end = content.find('"""', docstring_start + 3)
                    if docstring_end != -1:
                        docstring = content[docstring_start:docstring_end+3]
                        new_docstring = docstring.replace('天机处理器', f'天机处理器\n\n{privacy_warning}')
                        content = content.replace(docstring, new_docstring)
                        updated_files.append(filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return updated_files

def create_restricted_config_template():
    """创建受限的配置模板"""
    restricted_config = {
        "models": {
            "providers": {
                "volcengine": {
                    "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
                    "apiKey": "YOUR_VOLCENGINE_API_KEY_HERE",
                    "auth": "api-key",
                    "api": "openai-completions",
                    "models": [
                        {
                            "id": "doubao-seed-2-0-pro-260215",
                            "name": "豆包视觉模型",
                            "api": "openai-completions",
                            "reasoning": false,
                            "input": ["text", "image"],
                            "contextWindow": 200000,
                            "maxTokens": 8192
                        }
                    ]
                },
                "deepseek": {
                    "baseUrl": "https://api.deepseek.com/v1",
                    "apiKey": "YOUR_DEEPSEEK_API_KEY_HERE",
                    "api": "openai-completions",
                    "models": [
                        {
                            "id": "deepseek-chat",
                            "name": "DeepSeek Chat",
                            "contextWindow": 128000,
                            "maxTokens": 8192
                        }
                    ]
                }
            }
        }
    }
    
    template_path = Path(__file__).parent / 'restricted_config_template.json'
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(restricted_config, f, indent=2, ensure_ascii=False)
    
    # 创建使用指南
    guide = f"""# 受限配置使用指南

## 为什么使用受限配置？
默认情况下，技能会读取完整的 `~/.openclaw/openclaw.json` 配置文件，这可能包含您不希望技能访问的其他密钥和配置。

## 如何使用受限配置
1. 复制此模板文件：
   ```bash
   cp restricted_config_template.json ~/.openclaw/tianji_config.json
   ```

2. 填入您的API密钥（仅限技能需要的）：
   - `volcengine.apiKey`: 豆包视觉模型API密钥
   - `deepseek.apiKey`: DeepSeek API密钥

3. 设置环境变量：
   ```bash
   export OPENCLAW_CONFIG_PATH=~/.openclaw/tianji_config.json
   ```

4. 运行技能：
   ```bash
   OPENCLAW_CONFIG_PATH=~/.openclaw/tianji_config.json python3 tianji_core.py "分析图片 /tmp/test.jpg"
   ```

## 安全优势
- ✅ 技能只能访问明确授权的API密钥
- ✅ 不会意外读取其他服务的密钥
- ✅ 便于密钥管理和轮换
- ✅ 可以针对不同技能使用不同配置

## 验证配置
运行安全检查脚本验证配置：
```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/tianji_config.json python3 security_check_fixed.py
```
"""
    
    guide_path = Path(__file__).parent / 'RESTRICTED_CONFIG_GUIDE.md'
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    return template_path, guide_path

def fix_code_quality_issues():
    """修复代码质量问题"""
    skill_dir = Path(__file__).parent
    fixed_issues = []
    
    # 1. 修复版本号不一致
    version_files = [
        ('SKILL.md', r'version: \d+\.\d+\.\d+', 'version: 2.0.0'),
        ('_meta.json', r'"version": "\d+\.\d+\.\d+"', '"version": "2.0.0"'),
        ('config.json', r'"version": "\d+\.\d+\.\d+"', '"version": "2.0.0"'),
    ]
    
    for filename, pattern, replacement in version_files:
        file_path = skill_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    fixed_issues.append(f"{filename}: 统一版本号为2.0.0")
    
    # 2. 修复模块级函数调用self方法的问题
    core_file = skill_dir / 'tianji_core.py'
    with open(core_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有模块级函数错误调用self方法
    if 'self.get_openclaw_config_path()' in content and 'def get_openclaw_config_path(self):' not in content:
        # 添加缺失的方法
        method_to_add = '''
    def get_openclaw_config_path(self):
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
'''
        
        # 在类中找到合适的位置插入
        class_pos = content.find('class TianjiProcessor:')
        if class_pos != -1:
            init_pos = content.find('def __init__', class_pos)
            if init_pos != -1:
                # 在__init__方法前插入
                content = content[:init_pos] + method_to_add + '\n\n    ' + content[init_pos:]
                fixed_issues.append("tianji_core.py: 添加缺失的get_openclaw_config_path方法")
    
    # 3. 修复install.sh中的问题
    install_file = skill_dir / 'install.sh'
    if install_file.exists():
        with open(install_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有危险的命令
        dangerous_patterns = [
            r'rm -rf',
            r'chmod 777',
            r'wget.*\|\s*sh',
            r'curl.*\|\s*sh',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                print(f"⚠️  警告: install.sh中包含可能危险的命令: {pattern}")
                # 添加警告注释
                content = f"# ⚠️ 安全警告: 请审查以下命令\n# {content.split('#!/bin/bash')[1]}"
                fixed_issues.append("install.sh: 添加危险命令警告")
                break
        
        with open(install_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 保存修复后的文件
    with open(core_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return fixed_issues

def create_script_review_checklist():
    """创建脚本审查清单"""
    checklist = """# 玄机子技能脚本审查清单

在安装或运行此技能前，请仔细审查以下文件：

## 🔍 必须审查的文件

### 1. install.sh - 安装脚本
- [ ] 检查是否有远程下载和执行命令
- [ ] 检查文件权限修改（chmod）
- [ ] 检查系统文件修改
- [ ] 检查环境变量设置
- [ ] 检查依赖安装命令

### 2. tianji_core.py - 核心处理器
- [ ] 检查文件路径提取逻辑
- [ ] 检查API密钥读取方式
- [ ] 检查外部API调用
- [ ] 检查临时文件创建
- [ ] 检查错误处理

### 3. 所有包含exec或subprocess调用的文件
```bash
grep -r "exec\\|subprocess\\|os.system" . --include="*.py" --include="*.sh"
```

### 4. 配置文件读取相关文件
- [ ] doubao_vision_global.py
- [ ] analyze_general_image.py
- [ ] compress_and_analyze_palm.py

## 🛡️ 安全审查要点

### 文件系统访问
- [ ] 技能只能访问白名单目录
- [ ] 拒绝路径遍历攻击（../）
- [ ] 文件大小限制（最大50MB）
- [ ] 仅允许图片格式文件

### API密钥管理
- [ ] 无硬编码API密钥
- [ ] API密钥从安全位置读取
- [ ] 密钥不会打印到日志
- [ ] 支持环境变量配置

### 外部通信
- [ ] 明确列出所有外部API端点
- [ ] 图片Base64编码发送
- [ ] 支持HTTPS连接
- [ ] 超时和错误处理

## 🧪 沙盒测试步骤

### 步骤1: 无网络测试
```bash
# 断开网络连接
# 运行安装脚本
./install.sh --dry-run
# 检查输出，确认无网络请求
```

### 步骤2: 无API密钥测试
```bash
# 使用测试配置
export OPENCLAW_CONFIG_PATH=/tmp/test_config.json
# 运行核心功能测试
python3 tianji_core.py "测试"
# 确认无API密钥错误
```

### 步骤3: 路径安全测试
```bash
# 测试危险路径
python3 test_path_safety.py
# 确认所有危险路径被拒绝
```

### 步骤4: 文件访问测试
```bash
# 创建测试目录结构
mkdir -p /tmp/tianji_test
# 测试文件访问限制
# 确认无法访问系统文件
```

## 📋 安装前确认清单

- [ ] 我已阅读并理解SKILL.md中的所有警告
- [ ] 我已审查install.sh脚本内容
- [ ] 我已设置受限的配置文件
- [ ] 我已备份当前的OpenClaw配置
- [ ] 我已在沙盒环境中测试过技能
- [ ] 我了解图片会发送到第三方API
- [ ] 我已准备好测试用的API密钥
- [ ] 我知道如何轮换API密钥

## 🔄 密钥轮换计划

如果测试后需要轮换密钥：
1. 登录相关服务商控制台
2. 生成新的API密钥
3. 更新配置文件
4. 撤销旧的API密钥
5. 监控API使用情况

## 📞 问题报告

如发现安全问题：
1. 立即停止使用技能
2. 审查所有生成的临时文件
3. 轮换所有相关API密钥
4. 报告给技能维护者

---
*安全第一，审查为先。在信任之前验证，在使用之前测试。*
"""
    
    checklist_path = Path(__file__).parent / 'SCRIPT_REVIEW_CHECKLIST.md'
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    return checklist_path

def enhance_filesystem_restrictions():
    """增强文件系统访问限制"""
    core_file = Path(__file__).parent / 'tianji_core.py'
    
    with open(core_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找现有的is_safe_file_path方法
    if 'def is_safe_file_path(self, file_path):' in content:
        # 增强白名单验证部分
        enhanced_validation = '''        # 显式白名单目录（严格控制）
        allowed_prefixes = [
            '/tmp/tianji_',  # 仅限tianji前缀的临时文件
            '/tmp/test_images/',  # 测试图片目录
            f'{user_home}/.openclaw/workspace/skills/tianji-fengshui/',  # 技能自身目录
            f'{user_home}/.openclaw/media/inbound/',  # 仅限inbound媒体
        ]
        
        # 用户文档目录（可选，需用户明确同意）
        user_allowed_dirs = os.getenv('TIANJI_ALLOWED_DIRS', '').split(':')
        allowed_prefixes.extend([d + '/' for d in user_allowed_dirs if d])
        
        # 验证2: 在允许的目录下
        is_allowed = False
        for prefix in allowed_prefixes:
            if abs_path.startswith(prefix):
                is_allowed = True
                break
        
        if not is_allowed:
            print(f"🚫 路径安全拒绝: 不在白名单目录中")
            print(f"   当前白名单: {allowed_prefixes}")
            print(f"   如需访问其他目录，请设置环境变量 TIANJI_ALLOWED_DIRS")
            return False'''
        
        # 替换现有的白名单验证部分
        pattern = r'# 显式白名单目录[\s\S]*?if not is_allowed:[\s\S]*?return False'
        content = re.sub(pattern, enhanced_validation, content)
        
        with open(core_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    return False

def create_key_rotation_guide():
    """创建密钥轮换指南"""
    guide = """# API密钥轮换指南

## 为什么需要轮换API密钥？
1. **安全最佳实践**：定期轮换减少密钥泄露风险
2. **技能移除后**：如果不再使用技能，应撤销相关密钥
3. **异常活动**：发现异常API调用时立即轮换
4. **员工变动**：相关人员离职时轮换密钥

## 轮换步骤

### 豆包（火山引擎）API密钥轮换
1. 登录火山引擎控制台：https://console.volcengine.com/
2. 进入「访问控制」→「密钥管理」
3. 找到当前使用的密钥
4. 点击「禁用」或「删除」
5. 创建新的密钥
6. 更新OpenClaw配置

### DeepSeek API密钥轮换
1. 登录DeepSeek平台：https://platform.deepseek.com/
2. 进入「API Keys」管理
3. 撤销旧的密钥
4. 生成新的密钥
5. 更新配置文件

### 百度文心一言API密钥轮换
1. 登录百度AI开放平台：https://ai.baidu.com/
2. 进入「应用管理」
3. 找到对应的应用
4. 重置AK/SK
5. 更新配置

## 紧急轮换流程
如果怀疑密钥泄露：
1. **立即行动**：5分钟内完成轮换
2. **监控日志**：检查异常API调用
3. **通知团队**：告知相关人员
4. **更新文档**：记录轮换时间和原因

## 定期轮换计划
建议每3-6个月轮换一次：
- 季度检查：每季度检查密钥使用情况
- 半年轮换：每6个月强制轮换
- 事件触发：安全事件后立即轮换

## 配置更新
轮换后更新以下位置：
1. OpenClaw全局配置：~/.openclaw/openclaw.json
2. 环境变量：相关API_KEY环境变量
3. 容器配置：如果使用容器化部署
4. 密钥管理服务：如Vault、AWS Secrets Manager

## 验证轮换
轮换后验证：
1. 运行技能测试
2. 检查API调用正常
3. 确认旧密钥已失效
4. 监控新密钥使用情况

---
*安全无小事，密钥需谨慎。定期轮换，防患未然。*"""
    
    guide_path = Path(__file__).parent / 'KEY_ROTATION_GUIDE.md'
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    return guide_path