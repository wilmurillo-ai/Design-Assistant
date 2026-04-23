#!/usr/bin/env python3
"""
技能进化系统初始化脚本
一键设置数据目录和基础配置
"""

import os
import json
from pathlib import Path

def init_system():
    """初始化技能进化系统"""
    
    # 数据目录
    data_dir = Path(os.path.expanduser("~/.openclaw/workspace/skills/.evolution-data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份目录
    backup_dir = data_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    # 初始化数据文件
    files = {
        "usage_stats.json": {},
        "feedback.json": {},
        "analysis_results.json": {},
        "evolution_plans.json": {},
        "system_config.json": {
            "initialized_at": str(__import__('datetime').datetime.now()),
            "version": "1.0.0",
            "auto_backup": True,
            "max_records_per_skill": 1000,
            "health_thresholds": {
                "success_rate": 0.8,
                "avg_duration": 30,
                "satisfaction": 3.5
            }
        }
    }
    
    for filename, default_data in files.items():
        filepath = data_dir / filename
        if not filepath.exists():
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 创建: {filepath}")
        else:
            print(f"⏭️  已存在: {filepath}")
    
    # 创建示例技能追踪代码
    example_code = '''# 在技能脚本中集成追踪的示例代码

import sys
from pathlib import Path

# 添加技能进化系统到路径
sys.path.insert(0, str(Path.home() / ".openclaw/workspace/skills/skill-evolution-system"))

try:
    from scripts.track_usage import SkillUsageTracker
    
    # 初始化追踪器
    tracker = SkillUsageTracker()
    
    # 记录使用开始
    def on_skill_start(skill_name, context):
        return tracker.record_usage(skill_name, context)
    
    # 记录使用结果
    def on_skill_end(record_id, success, satisfaction=None):
        tracker.update_result(record_id, success, satisfaction)
    
    # 收集反馈
    def collect_feedback(skill_name, feedback_type, details, rating=None):
        tracker.collect_feedback(skill_name, feedback_type, details, rating)
        
except ImportError:
    # 技能进化系统未安装，静默忽略
    def on_skill_start(*args): return None
    def on_skill_end(*args): pass
    def collect_feedback(*args): pass
'''
    
    example_file = data_dir / "integration_example.py"
    with open(example_file, 'w', encoding='utf-8') as f:
        f.write(example_code)
    print(f"✅ 创建集成示例: {example_file}")
    
    print("\n" + "="*50)
    print("🎉 技能进化系统初始化完成！")
    print("="*50)
    print(f"\n数据目录: {data_dir}")
    print("\n下一步:")
    print("1. 开始使用技能时记录数据")
    print("2. 运行: python scripts/track_usage.py record <skill-name>")
    print("3. 分析: python scripts/analyze_performance.py analyze-all")
    print("4. 查看报告: python scripts/generate_report.py")

if __name__ == "__main__":
    init_system()
