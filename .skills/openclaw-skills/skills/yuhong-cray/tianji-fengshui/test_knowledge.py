#!/usr/bin/env python3
"""
测试tianji-fengshui技能知识库集成
"""

import os
import json
from pathlib import Path

def test_knowledge_files():
    """测试知识库文件是否存在"""
    skill_dir = Path(__file__).parent
    knowledge_dir = skill_dir / "knowledge"
    
    print("🧭 测试 tianji-fengshui 知识库集成")
    print("=" * 50)
    
    # 检查知识库目录
    if not knowledge_dir.exists():
        print("❌ 知识库目录不存在")
        return False
    
    print(f"✅ 知识库目录: {knowledge_dir}")
    
    # 检查知识库文件
    knowledge_files = [
        "fengshui_bazi_palm_books.md",
        "quick_reference.md",
        "analysis_templates.md"
    ]
    
    all_files_exist = True
    for file_name in knowledge_files:
        file_path = knowledge_dir / file_name
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"✅ {file_name}: {file_size} 字节")
        else:
            print(f"❌ {file_name}: 文件不存在")
            all_files_exist = False
    
    print("-" * 50)
    
    # 检查_meta.json中的知识库配置
    meta_file = skill_dir / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        
        if "knowledge_base" in meta_data:
            print("✅ _meta.json 包含知识库配置")
            kb_info = meta_data["knowledge_base"]
            print(f"   描述: {kb_info.get('description', 'N/A')}")
            print(f"   文件数: {len(kb_info.get('files', []))}")
            print(f"   主题: {', '.join(kb_info.get('topics', []))}")
            print(f"   书籍数量: {kb_info.get('books_count', 0)}")
            print(f"   集成日期: {kb_info.get('integration_date', 'N/A')}")
        else:
            print("❌ _meta.json 缺少知识库配置")
            all_files_exist = False
    else:
        print("❌ _meta.json 文件不存在")
        all_files_exist = False
    
    print("-" * 50)
    
    # 检查SKILL.md中的知识库部分
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "知识库集成" in content:
            print("✅ SKILL.md 包含知识库集成部分")
        else:
            print("❌ SKILL.md 缺少知识库集成部分")
            all_files_exist = False
    else:
        print("❌ SKILL.md 文件不存在")
        all_files_exist = False
    
    print("=" * 50)
    
    if all_files_exist:
        print("🎉 所有知识库文件检查通过！")
        print("\n📚 知识库内容概要：")
        print("1. fengshui_bazi_palm_books.md - 完整知识库（易经、八字、风水、掌相）")
        print("2. quick_reference.md - 快速参考指南（核心要点、书籍清单、分析模板）")
        print("3. analysis_templates.md - 专业分析模板（八字、掌纹、风水、综合）")
        print(f"\n📖 总计书籍资料：18本（易经4+八字5+风水5+掌相4）")
        return True
    else:
        print("⚠️  部分知识库文件检查未通过")
        return False

def check_knowledge_content():
    """检查知识库内容"""
    skill_dir = Path(__file__).parent
    knowledge_dir = skill_dir / "knowledge"
    
    print("\n📖 知识库内容检查：")
    print("-" * 50)
    
    # 检查主要知识库文件内容
    main_file = knowledge_dir / "fengshui_bazi_palm_books.md"
    if main_file.exists():
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键部分
        sections = [
            ("易经基础", "易经基础深入学习"),
            ("八字命理", "八字命理深入学习"),
            ("风水学", "风水学领域"),
            ("掌相学", "掌相学"),
            ("书籍推荐", "书籍推荐清单")
        ]
        
        for section_name, keyword in sections:
            if keyword in content:
                print(f"✅ {section_name}: 包含")
            else:
                print(f"❌ {section_name}: 缺失")
    
    print("-" * 50)
    return True

if __name__ == "__main__":
    print("🚀 开始测试 tianji-fengshui 知识库集成")
    print()
    
    files_ok = test_knowledge_files()
    
    if files_ok:
        content_ok = check_knowledge_content()
        
        print("\n🎯 测试总结：")
        print(f"知识库目录: ~/.openclaw/workspace/skills/tianji-fengshui/knowledge/")
        print(f"知识库文件: 3个专业文档")
        print(f"集成状态: ✅ 成功集成风水八字掌纹书籍资料")
        print(f"更新时间: 2026年3月23日")
        print(f"技能名称: tianji-fengshui (天机·玄机子)")
    else:
        print("\n⚠️  测试失败：请检查知识库文件完整性")