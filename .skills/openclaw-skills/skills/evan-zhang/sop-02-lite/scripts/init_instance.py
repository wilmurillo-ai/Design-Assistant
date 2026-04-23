#!/usr/bin/env python3
"""
SOP-02-Lite: 初始化实例脚本
功能：原子性创建 SOP 实例目录，分配序号，初始化文件
"""

import argparse
import fcntl
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='初始化 SOP-02-Lite 实例')
    parser.add_argument('--title', required=True, help='任务标题')
    parser.add_argument('--owner', default='factory-orchestrator', help='负责人（默认：factory-orchestrator）')
    parser.add_argument('--root', default='~/.openclaw/sop-instances/', help='实例根目录')
    return parser.parse_args()


def get_next_instance_number(root_dir: Path, date_str: str) -> int:
    """
    扫描当天已有实例，返回下一个序号
    格式：SOP-YYYYMMDD-NNN
    """
    pattern = re.compile(rf'^SOP-{date_str}-(\d{{3}})$')
    max_num = 0
    
    if root_dir.exists():
        for item in root_dir.iterdir():
            if item.is_dir():
                match = pattern.match(item.name)
                if match:
                    num = int(match.group(1))
                    max_num = max(max_num, num)
    
    return max_num + 1


def create_instance(root_dir: Path, instance_id: str, title: str, owner: str, templates_dir: Path) -> Path:
    """
    创建实例目录并初始化文件
    """
    instance_path = root_dir / instance_id
    instance_path.mkdir(parents=True, exist_ok=False)
    
    # 当前时间戳
    now = datetime.now().isoformat()
    
    # 初始化 state.json
    state = {
        "id": instance_id,
        "title": title,
        "owner": owner,
        "status": "ACTIVE",
        "stage": "TARGET",
        "createdAt": now,
        "updatedAt": now,
        "reason": ""
    }
    
    with open(instance_path / "state.json", 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    # 从模板创建三件套
    template_files = {
        'TASK.md.template': 'TASK.md',
        'LOG.md.template': 'LOG.md',
        'RESULT.md.template': 'RESULT.md'
    }
    
    for tpl_name, target_name in template_files.items():
        tpl_path = templates_dir / tpl_name
        if tpl_path.exists():
            with open(tpl_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换占位符
            content = content.replace('{{id}}', instance_id)
            content = content.replace('{{title}}', title)
            content = content.replace('{{owner}}', owner)
            content = content.replace('{{createdAt}}', now)
            
            with open(instance_path / target_name, 'w', encoding='utf-8') as f:
                f.write(content)
    
    return instance_path


def main():
    args = parse_args()
    
    # 展开路径
    root_dir = Path(os.path.expanduser(args.root)).resolve()
    script_dir = Path(__file__).parent
    templates_dir = script_dir.parent / 'references' / 'templates'
    
    # 确保根目录存在
    root_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取当天日期
    date_str = datetime.now().strftime('%Y%m%d')
    
    # 使用文件锁保证原子性
    lock_file = root_dir / '.create.lock'
    
    try:
        with open(lock_file, 'w') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            
            try:
                # 获取下一个序号
                next_num = get_next_instance_number(root_dir, date_str)
                instance_id = f"SOP-{date_str}-{next_num:03d}"
                
                # 创建实例
                instance_path = create_instance(
                    root_dir, instance_id, args.title, args.owner, templates_dir
                )
                
                # 输出实例路径
                print(str(instance_path))
                
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
