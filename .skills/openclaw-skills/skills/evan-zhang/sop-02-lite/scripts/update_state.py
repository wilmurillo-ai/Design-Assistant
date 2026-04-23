#!/usr/bin/env python3
"""
SOP-02-Lite: 更新实例状态脚本
功能：
1) 更新 state.json 的 status / stage / owner / reason
2) 支持 pause / resume / shelve / restart 语义化操作
3) 高风险操作门禁（owner 切换、DONE/ARCHIVED/UPGRADED）
4) 每次状态变更追加 LOG.md 记录
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# 状态枚举（R005）
STATUS_CHOICES = [
    'DISCUSSING',
    'READY',
    'RUNNING',
    'BLOCKED',
    'PAUSED',
    'DONE',
    'ARCHIVED',
    'HANDOVER_PENDING',
    'UPGRADED',
    # 兼容历史值（自动映射）
    'ACTIVE',
    'COMPLETED',
    'FAILED',
]

# 阶段枚举（保留 + 向后兼容 + 支持验收命令）
STAGE_CHOICES = [
    'TARGET',
    'PLAN',
    'CHECKLIST',
    'EXECUTE',
    'ARCHIVE',
    # 常用运行态/完结态（验收命令依赖）
    'RUNNING',
    'DONE',
]

HIGH_RISK_STATUSES = {'DONE', 'ARCHIVED', 'UPGRADED'}


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='更新 SOP-02-Lite 实例状态')
    parser.add_argument('--instance-path', required=True, help='实例目录路径')
    parser.add_argument('--status', choices=STATUS_CHOICES, help='状态值')
    parser.add_argument('--stage', choices=STAGE_CHOICES, help='阶段值')
    parser.add_argument('--owner', help='新负责人（可选，切换时需要 --confirm）')
    parser.add_argument('--reason', help='状态变更原因（可选）')
    parser.add_argument(
        '--action',
        choices=['pause', 'resume', 'shelve', 'restart'],
        help='语义化操作（自动设置对应状态）'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='显式确认高风险操作（owner 切换、DONE/ARCHIVED/UPGRADED）'
    )

    args = parser.parse_args()

    # 至少需要一种状态变更意图
    if not args.status and not args.action:
        parser.error('必须提供 --status 或 --action')

    return args


def normalize_status(status: str) -> str:
    """兼容历史状态映射到新状态机"""
    mapping = {
        'ACTIVE': 'RUNNING',
        'COMPLETED': 'DONE',
        'FAILED': 'BLOCKED',
    }
    return mapping.get(status, status)


def load_state(instance_path: Path) -> dict:
    state_file = instance_path / 'state.json'
    if not state_file.exists():
        raise FileNotFoundError(f"state.json 不存在: {state_file}")
    with open(state_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_state(instance_path: Path, state: dict):
    state_file = instance_path / 'state.json'
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def ensure_checklist_completed_before_run(state: dict):
    """
    执行前确认单门禁（R010）
    约定：state.checklistConfirmed = false 时，禁止进入 RUNNING
    兼容旧实例：字段缺失默认放行
    """
    if state.get('checklistConfirmed') is False:
        raise PermissionError('执行前确认单未完成，禁止进入 RUNNING')


def apply_action(action: str, current_reason: Optional[str]) -> Tuple[str, Optional[str], Optional[str]]:
    """
    返回: (new_status, reason_override, blocked_reason_value)
    blocked_reason_value:
      - None: 不改 blockedReason
      - '': 清空 blockedReason
    """
    if action == 'pause':
        return 'PAUSED', current_reason or '暂停', None
    if action == 'resume':
        return 'RUNNING', current_reason or '恢复执行', None
    if action == 'shelve':
        return 'PAUSED', current_reason or '搁置', None
    if action == 'restart':
        return 'RUNNING', current_reason or '重启执行', ''
    raise ValueError(f'不支持的 action: {action}')


def append_log_entry(
    instance_path: Path,
    stage: str,
    operation: str,
    reason: Optional[str],
    detail: str,
):
    """在 LOG.md 追加状态变更记录（R001）"""
    log_file = instance_path / 'LOG.md'
    if not log_file.exists():
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    note = reason or 'N/A'
    entry = f"\n| {timestamp} | {stage} | {operation} | {detail}; 原因: {note} |\n"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)


def main():
    args = parse_args()

    instance_path = Path(args.instance_path).resolve()
    if not instance_path.exists():
        print(f"ERROR: 实例目录不存在: {instance_path}", file=sys.stderr)
        sys.exit(1)

    try:
        state = load_state(instance_path)

        old_owner = state.get('owner')
        old_status = normalize_status(state.get('status', 'DISCUSSING'))
        old_stage = state.get('stage', 'TARGET')

        # 计算目标状态
        reason = args.reason
        blocked_reason_update = None
        new_status = normalize_status(args.status) if args.status else old_status

        if args.action:
            new_status, reason, blocked_reason_update = apply_action(args.action, reason)

        new_stage = args.stage if args.stage else old_stage

        # 执行前确认单门禁：进入 RUNNING 时检查
        if new_status == 'RUNNING' or new_stage == 'RUNNING':
            ensure_checklist_completed_before_run(state)

        # 高风险门禁：owner 切换或状态设为 DONE/ARCHIVED/UPGRADED
        owner_changed = bool(args.owner and args.owner != old_owner)
        high_risk = owner_changed or (new_status in HIGH_RISK_STATUSES)
        if high_risk and not args.confirm:
            print('高风险操作需要显式确认，请加 --confirm 参数', file=sys.stderr)
            sys.exit(1)

        # 写入 state.json
        state['status'] = new_status
        state['stage'] = new_stage
        state['updatedAt'] = datetime.now().isoformat()

        if args.owner:
            state['owner'] = args.owner

        if reason is not None:
            state['reason'] = reason

        if blocked_reason_update == '':
            state['blockedReason'] = ''

        save_state(instance_path, state)

        # 记录日志（每次状态变更都记录）
        op = args.action.upper() if args.action else 'UPDATE_STATE'
        owner_detail = ''
        if args.owner and args.owner != old_owner:
            owner_detail = f'; owner: {old_owner} → {args.owner}'
        detail = f'status: {old_status} → {new_status}; stage: {old_stage} → {new_stage}{owner_detail}'
        append_log_entry(instance_path, new_stage, op, reason, detail)

        print(f"✓ 状态已更新: {new_status} / {new_stage}")
        if args.owner and args.owner != old_owner:
            print(f"✓ Owner 已切换: {old_owner} → {args.owner}")

    except PermissionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
