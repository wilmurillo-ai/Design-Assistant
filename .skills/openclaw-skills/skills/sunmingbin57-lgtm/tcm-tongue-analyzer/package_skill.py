#!/usr/bin/env python3
"""
中医舌像分析技能打包脚本
将技能目录打包为.skill文件，准备发布到ClawHub
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

def validate_skill_structure(skill_dir):
    """验证技能目录结构"""
    print("验证技能目录结构...")
    
    required_files = ["SKILL.md"]
    required_dirs = ["scripts", "references", "assets"]
    
    errors = []
    
    # 检查必需文件
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            errors.append(f"缺少必需文件: {file}")
    
    # 检查SKILL.md格式
    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查YAML frontmatter
        if not content.startswith('---'):
            errors.append("SKILL.md缺少YAML frontmatter")
        else:
            # 提取frontmatter
            parts = content.split('---')
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                # 检查必需字段
                if 'name:' not in frontmatter:
                    errors.append("SKILL.md frontmatter缺少name字段")
                if 'description:' not in frontmatter:
                    errors.append("SKILL.md frontmatter缺少description字段")
    
    # 检查目录（不要求必须存在，但建议存在）
    for dir_name in required_dirs:
        dir_path = os.path.join(skill_dir, dir_name)
        if os.path.exists(dir_path) and not os.path.isdir(dir_path):
            errors.append(f"{dir_name} 不是目录")
    
    if errors:
        print("[错误] 技能结构验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("[成功] 技能目录结构验证通过")
    return True

def calculate_file_hash(file_path):
    """计算文件哈希值"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def create_skill_manifest(skill_dir):
    """创建技能清单文件"""
    print("创建技能清单...")
    
    manifest = {
        "name": "中医舌像分析",
        "version": "1.0.0",
        "author": "中医AI团队",
        "created_at": datetime.now().isoformat(),
        "description": "专业中医舌象分析系统，基于深度学习自动识别舌色、舌形、舌苔特征，提供中医辨证建议",
        "price_rmb": 6.0,
        "files": [],
        "dependencies": {
            "python": ">=3.8",
            "packages": [
                "opencv-python",
                "pillow",
                "numpy"
            ]
        },
        "requirements": {
            "min_memory_mb": 512,
            "min_disk_mb": 100,
            "supported_os": ["Windows", "Linux", "macOS"]
        }
    }
    
    # 遍历所有文件
    for root, dirs, files in os.walk(skill_dir):
        # 跳过隐藏文件和目录
        files = [f for f in files if not f.startswith('.')]
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, skill_dir)
            
            # 跳过打包脚本本身
            if file == "package_skill.py":
                continue
            
            file_info = {
                "path": rel_path,
                "size_bytes": os.path.getsize(file_path),
                "sha256": calculate_file_hash(file_path),
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
            
            manifest["files"].append(file_info)
    
    # 保存清单文件
    manifest_path = os.path.join(skill_dir, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"[成功] 技能清单已创建: {manifest_path}")
    print(f"  包含 {len(manifest['files'])} 个文件")
    print(f"  总大小: {sum(f['size_bytes'] for f in manifest['files']) / 1024:.1f} KB")
    
    return manifest

def create_skill_package(skill_dir, output_dir=None):
    """创建.skill包文件"""
    print("创建技能包...")
    
    skill_name = "中医舌像分析"
    package_name = skill_name.replace(" ", "-").lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_dir is None:
        output_dir = os.path.join(skill_dir, "dist")
    
    os.makedirs(output_dir, exist_ok=True)
    
    package_filename = f"{package_name}-v1.0.0-{timestamp}.skill"
    package_path = os.path.join(output_dir, package_filename)
    
    # 创建ZIP文件
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 跳过隐藏文件和目录
            files = [f for f in files if not f.startswith('.')]
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # 跳过打包脚本和dist目录
                if file == "package_skill.py" or "dist" in file_path:
                    continue
                
                rel_path = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, rel_path)
    
    package_size_mb = os.path.getsize(package_path) / (1024 * 1024)
    
    print(f"[成功] 技能包已创建: {package_path}")
    print(f"  包大小: {package_size_mb:.2f} MB")
    print(f"  包含文件: {len(zipfile.ZipFile(package_path).namelist())} 个")
    
    return package_path

def create_installation_guide(skill_dir, manifest):
    """创建安装指南"""
    print("创建安装指南...")
    
    guide_content = f"""# 中医舌像分析技能安装指南

## 产品信息
- **名称**: {manifest['name']}
- **版本**: {manifest['version']}
- **作者**: {manifest['author']}
- **价格**: {manifest['price_rmb']} 元人民币
- **创建时间**: {manifest['created_at']}

## 系统要求
- **操作系统**: {', '.join(manifest['requirements']['supported_os'])}
- **内存**: 最少 {manifest['requirements']['min_memory_mb']} MB
- **磁盘空间**: 最少 {manifest['requirements']['min_disk_mb']} MB
- **Python版本**: {manifest['dependencies']['python']}

## 安装步骤

### 方法1: 通过ClawHub安装（推荐）
```bash
# 从ClawHub安装
npx clawhub@latest install 中医舌像分析

# 或使用包名
npx clawhub@latest install tcm-tongue-analyzer
```

### 方法2: 手动安装
1. 下载.skill包文件
2. 解压到OpenClaw技能目录:
   ```bash
   # Windows
   mkdir "%USERPROFILE%\.openclaw\skills\中医舌像分析"
   
   # Linux/macOS
   mkdir -p ~/.openclaw/skills/中医舌像分析
   ```
3. 将解压后的文件复制到技能目录
4. 重启OpenClaw或刷新技能列表

## 使用方法

### 基本命令
```bash
# 分析单张舌象照片
tcm-tongue analyze --image "舌象照片路径"

# 批量分析
tcm-tongue batch --folder "舌象照片文件夹"

# 生成详细报告
tcm-tongue report --image "照片路径" --output "报告文件"
```

### 参数说明
- `--image`: 舌象照片路径（支持JPG、PNG格式）
- `--format`: 输出格式（text/json/html）
- `--detail`: 详细程度（basic/standard/detailed）
- `--compare`: 对比分析多张照片

## 功能验证

安装完成后，运行测试验证功能：
```bash
# 进入技能目录
cd ~/.openclaw/skills/中医舌像分析/scripts

# 运行测试
python test_tongue_analyzer.py
```

所有测试应该通过，输出包含：
1. 舌象特征分析
2. 中医辨证结果
3. 治疗建议（组方+穴位）
4. 生活调理建议

## 文件清单

本技能包包含以下文件：
```
"""
    
    # 添加文件列表
    for file_info in manifest['files']:
        size_kb = file_info['size_bytes'] / 1024
        guide_content += f"{file_info['path']:40} {size_kb:6.1f} KB\n"
    
    guide_content += """
```

## 技术支持

如有问题或建议，请联系：
- 邮箱: support@tcm-tongue.com
- 网站: https://tcm-tongue.clawhub.ai
- 文档: 参考技能目录中的references/目录

## 更新日志

### v1.0.0
- 初始版本发布
- 基础舌色分类功能
- 简单辨证建议
- 批量处理功能

## 免责声明

本工具为中医诊断辅助工具，不能替代专业医师诊断。临床决策请咨询执业中医师。

---

**购买即表示您同意以上条款**
"""
    
    guide_path = os.path.join(skill_dir, "INSTALLATION_GUIDE.md")
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"[成功] 安装指南已创建: {guide_path}")
    return guide_path

def main():
    """主函数"""
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认使用当前目录的父目录
        skill_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("中医舌像分析技能打包工具")
    print("=" * 60)
    print(f"技能目录: {skill_dir}")
    
    # 验证技能结构
    if not validate_skill_structure(skill_dir):
        print("❌ 技能结构验证失败，无法打包")
        return 1
    
    # 创建清单
    manifest = create_skill_manifest(skill_dir)
    
    # 创建安装指南
    create_installation_guide(skill_dir, manifest)
    
    # 创建技能包
    package_path = create_skill_package(skill_dir)
    
    # 生成发布说明
    print("\n" + "=" * 60)
    print("发布准备完成！")
    print("=" * 60)
    print(f"技能包: {package_path}")
    print(f"版本: {manifest['version']}")
    print(f"价格: {manifest['price_rmb']} 元人民币")
    print(f"文件数: {len(manifest['files'])}")
    print(f"总大小: {sum(f['size_bytes'] for f in manifest['files']) / 1024:.1f} KB")
    
    print("\n下一步:")
    print("1. 将.skill文件上传到ClawHub")
    print("2. 设置价格为6元人民币")
    print("3. 添加详细描述和标签")
    print("4. 发布技能")
    
    print("\n发布命令参考:")
    print(f"npx clawhub@latest publish {package_path} --price 6 --category medical")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())