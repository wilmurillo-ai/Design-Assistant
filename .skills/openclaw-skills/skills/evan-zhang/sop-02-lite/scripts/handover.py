#!/usr/bin/env python3
"""
SOP-02-Lite: 交接脚本
功能：创建 HANDOVER.md，更新状态为 HANDOVER_PENDING，记录到 LOG.md
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='SOP-02-Lite 任务交接')
    parser.add_argument('--instance-path', required=True, help='实例目录路径')
    parser.add_argument('--from-owner', required=True, help='当前负责人')
    parser.add_argument('--to-owner', required=True, help='新负责人')
    parser.add_argument('--reason', required=True, help='交接原因')
    parser.add_argument('--next-steps', required=True, help='后续步骤说明')
    return parser.parse_args()


def load_state(instance_path: Path) -> dict:
    state_file = instance_path / 'state.json'
    if not state_file.exists():
        raise FileNotFoundError(f"state.json 不存在: {state_file}")
    with open(state_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_from_owner(instance_path: Path, from_owner: str):
    """R007: 校验 from-owner 与 state.json.owner 一致"""
    state = load_state(instance_path)
    current_owner = state.get('owner')
    if from_owner != current_owner:
        print(
            f"交接失败：from-owner={from_owner} 与当前 owner={current_owner} 不一致，请确认",
            file=sys.stderr
        )
        sys.exit(1)


def create_handover_file(instance_path: Path, from_owner: str, to_owner: str, reason: str, next_steps: str):
    """创建 HANDOVER.md 文件"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    instance_id = instance_path.name

    content = f"""# HANDOVER.md - {instance_id}

## 交接信息

- **交接时间**: {timestamp}
- **原负责人**: {from_owner}
- **新负责人**: {to_owner}

## 交接原因

{reason}

## 后续步骤

{next_steps}

## 交接检查清单

- [ ] 已完成当前阶段的所有任务
- [ ] 已更新 state.json 状态
- [ ] 已在 LOG.md 记录关键操作
- [ ] 已向新负责人说明背景和上下文

---

*交接时间: {timestamp}*
"""

    handover_file = instance_path / 'HANDOVER.md'
    with open(handover_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return handover_file


def append_handover_to_log(instance_path: Path, from_owner: str, to_owner: str, reason: str):
    """在 LOG.md 追加交接记录"""
    log_file = instance_path / 'LOG.md'

    if not log_file.exists():
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f"\n| {timestamp} | HANDOVER | {from_owner} → {to_owner} | {reason} |\n"

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)


def call_update_state(instance_path: Path, to_owner: str, reason: str):
    """调用 update_state.py 设置状态为 HANDOVER_PENDING"""
    script_dir = Path(__file__).parent
    update_script = script_dir / 'update_state.py'

    if not update_script.exists():
        raise FileNotFoundError(f"update_state.py 不存在: {update_script}")

    state = load_state(instance_path)
    current_stage = state.get('stage', 'TARGET')

    cmd = [
        'python3', str(update_script),
        '--instance-path', str(instance_path),
        '--status', 'HANDOVER_PENDING',
        '--stage', current_stage,
        '--owner', to_owner,
        '--reason', f'交接: {reason}',
        '--confirm',
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"update_state.py 执行失败: {result.stderr.strip()}")


def main():
    args = parse_args()

    instance_path = Path(args.instance_path).resolve()

    if not instance_path.exists():
        print(f"ERROR: 实例目录不存在: {instance_path}", file=sys.stderr)
        sys.exit(1)

    try:
        validate_from_owner(instance_path, args.from_owner)

        handover_file = create_handover_file(
            instance_path,
            args.from_owner,
            args.to_owner,
            args.reason,
            args.next_steps
        )
        print(f"✓ 已创建: {handover_file}")

        append_handover_to_log(
            instance_path,
            args.from_owner,
            args.to_owner,
            args.reason
        )
        print("✓ 已追加交接记录到 LOG.md")

        call_update_state(
            instance_path,
            args.to_owner,
            args.reason
        )
        print("✓ 已更新状态为 HANDOVER_PENDING")

        print(f"\n交接完成: {args.from_owner} → {args.to_owner}")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
