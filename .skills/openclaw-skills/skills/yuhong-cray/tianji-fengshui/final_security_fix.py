#!/usr/bin/env python3
"""
玄机子技能最终安全修复
专注于最关键的安全问题
"""

import os
import re
import json
from pathlib import Path

def main():
    print("🔒 玄机子技能最终安全修复")
    print("=" * 60)
    
    skill_dir = Path(__file__).parent
    
    # 1. 在SKILL.md开头添加隐私警告
    print("\n1. 添加隐私警告到SKILL.md...")
    skill_md = skill_dir / 'SKILL.md'
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        privacy_warning = """## ⚠️ 重要隐私警告

**在安装或使用此技能前，请仔细阅读以下警告：**

### 图片隐私
- 本技能会将图片Base64编码后发送到第三方API端点：
  1. `ark.cn-beijing.volces.com` (火山引擎豆包视觉模型)
  2. 配置的DeepSeek API端点
- **只发送您愿意与这些服务商分享的图片**
- 避免发送包含个人身份信息、敏感文档、私人照片的图片

### 配置访问
- 技能会读取 `~/.openclaw/openclaw.json` 或 `OPENCLAW_CONFIG_PATH` 环境变量指定的配置文件
- 确保配置文件中不包含您不希望技能访问的其他密钥
- 建议使用受限配置文件（见下文）

### 安全使用建议
1. **审查代码**：在运行前审查所有脚本
2. **沙盒测试**：先在测试环境中验证行为
3. **受限配置**：使用仅包含必要密钥的配置文件
4. **密钥轮换**：测试后考虑轮换API密钥

---
"""
        
        if '## ⚠️ 重要隐私警告' not in content:
            # 在版本信息后插入
            version_pos = content.find('version:')
            if version_pos != -1:
                # 找到版本信息结束位置
                tags_pos = content.find('tags:', version_pos)
                if tags_pos != -1:
                    content = content[:tags_pos] + privacy_warning + content[tags_pos:]
        
        with open(skill_md, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ SKILL.md隐私警告已添加")
    
    # 2. 创建受限配置模板
    print("\n2. 创建受限配置模板...")
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
    
    template_path = skill_dir / 'restricted_config.json'
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(restricted_config, f, indent=2, ensure_ascii=False)
    print(f"✅ 受限配置模板: {template_path}")
    
    # 3. 修复install.sh
    print("\n3. 修复install.sh...")
    install_sh = skill_dir / 'install.sh'
    if install_sh.exists():
        with open(install_sh, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加明确的警告
        warning = """#!/bin/bash

# ⚠️ 重要：在运行此脚本前请仔细审查
# 本脚本将：
# 1. 检查Python依赖
# 2. 测试核心功能
# 3. 可能调用外部API（如果配置了API密钥）
#
# 审查要点：
# - 检查所有命令，特别是exec/subprocess调用
# - 确认无远程代码下载和执行
# - 确认文件权限修改合理
#
# 建议先在沙盒环境中测试

echo "🔍 开始安装玄机子技能..."
echo "⚠️  请确保已阅读SKILL.md中的隐私警告"
echo ""
"""
        
        if not content.startswith('#!/bin/bash\n\n# ⚠️ 重要：在运行此脚本前请仔细审查'):
            content = warning + content.split('#!/bin/bash', 1)[-1]
        
        with open(install_sh, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ install.sh已添加安全警告")
    
    # 4. 创建审查清单
    print("\n4. 创建脚本审查清单...")
    checklist = """# 玄机子技能安装前审查清单

## 🔍 必须审查的文件

### 核心文件
- [ ] `install.sh` - 安装脚本（检查所有命令）
- [ ] `tianji_core.py` - 核心处理器（检查文件访问和API调用）
- [ ] `doubao_vision_global.py` - 豆包集成（检查API密钥读取）

### 辅助脚本
- [ ] `analyze_general_image.py` - 通用图片分析
- [ ] `compress_and_analyze_palm.py` - 掌纹压缩分析
- [ ] 所有包含 `exec`、`subprocess`、`os.system` 的文件

## 🛡️ 安全验证步骤

### 步骤1：代码审查
```bash
# 检查危险命令
grep -r "exec\\|subprocess\\|os.system\\|rm -rf\\|chmod 777" . --include="*.py" --include="*.sh"

# 检查API密钥硬编码
grep -r "apiKey\\|secret\\|token" . --include="*.py" --include="*.json" --include="*.md"

# 检查外部URL
grep -r "http://\\|https://" . --include="*.py" --include="*.sh"
```

### 步骤2：沙盒测试
```bash
# 使用受限配置
export OPENCLAW_CONFIG_PATH=/tmp/test_config.json

# 创建测试配置
cat > /tmp/test_config.json << EOF
{
  "models": {
    "providers": {
      "volcengine": {
        "apiKey": "TEST_KEY_ONLY_FOR_SANDBOX",
        "baseUrl": "https://ark.cn-beijing.volces.com/api/v3"
      }
    }
  }
}
EOF

# 运行安装脚本（仅检查，不实际安装）
bash -n install.sh  # 语法检查
./install.sh --dry-run  # 如果有dry-run选项
```

### 步骤3：路径安全测试
```bash
# 测试危险路径拦截
python3 -c "
from tianji_core import TianjiProcessor
p = TianjiProcessor()

# 测试安全路径
print('安全路径测试:', p.is_safe_file_path('/tmp/test.jpg'))

# 测试危险路径（应该返回False）
print('危险路径测试:', p.is_safe_file_path('/etc/passwd'))
print('路径遍历测试:', p.is_safe_file_path('/tmp/../etc/passwd'))
"
```

## 📋 安装前确认

- [ ] 我已阅读SKILL.md中的所有警告
- [ ] 我已审查install.sh和所有Python脚本
- [ ] 我了解图片会发送到第三方API
- [ ] 我已准备测试用的API密钥
- [ ] 我已在沙盒环境中测试过
- [ ] 我知道如何轮换API密钥

## 🔧 生产环境准备

1. **使用受限配置**：
   ```bash
   cp restricted_config.json ~/.openclaw/tianji_config.json
   # 编辑文件，填入真实API密钥
   export OPENCLAW_CONFIG_PATH=~/.openclaw/tianji_config.json
   ```

2. **设置文件访问限制**：
   ```bash
   # 限制技能只能访问特定目录
   export TIANJI_ALLOWED_DIRS=/tmp:/home/$(whoami)/Pictures
   ```

3. **监控API使用**：
   - 设置API用量告警
   - 定期检查日志
   - 监控异常调用

---
*安全无小事，审查为先。在信任之前验证，在使用之前测试。*
"""
    
    checklist_path = skill_dir / 'INSTALL_CHECKLIST.md'
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(checklist)
    print(f"✅ 审查清单: {checklist_path}")
    
    # 5. 修复代码质量问题
    print("\n5. 修复代码质量问题...")
    
    # 检查版本一致性
    version = "2.0.0"
    files_to_check = [
        ('SKILL.md', r'version: \d+\.\d+\.\d+', f'version: {version}'),
        ('_meta.json', r'"version": "\d+\.\d+\.\d+"', f'"version": "{version}"'),
    ]
    
    for filename, pattern, replacement in files_to_check:
        file_path = skill_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ {filename}: 版本统一为{version}")
    
    print("\n" + "=" * 60)
    print("🎉 最终安全修复完成！")
    print("\n下一步：")
    print("1. 仔细阅读 INSTALL_CHECKLIST.md")
    print("2. 审查所有标记的文件")
    print("3. 在沙盒环境中测试")
    print("4. 使用 restricted_config.json 进行生产部署")
    print("5. 定期轮换API密钥")

if __name__ == "__main__":
    main()