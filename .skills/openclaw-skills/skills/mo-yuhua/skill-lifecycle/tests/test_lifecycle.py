#!/usr/bin/env python3
"""skill-lifecycle 自测试"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.version import parse_version, bump_version


def test_parse_version():
    """测试版本解析"""
    assert parse_version("1.0.0") == (1, 0, 0)
    assert parse_version("2.7.5") == (2, 7, 5)
    assert parse_version("0.1.0") == (0, 1, 0)
    print("✅ parse_version 测试通过")


def test_bump_version():
    """测试版本升级"""
    assert bump_version("1.0.0", "patch") == "1.0.1"
    assert bump_version("1.0.0", "minor") == "1.1.0"
    assert bump_version("1.0.0", "major") == "2.0.0"
    assert bump_version("2.7.5", "patch") == "2.7.6"
    print("✅ bump_version 测试通过")


def test_cli_import():
    """测试 CLI 导入"""
    from lifecycle import cli
    assert cli is not None
    print("✅ CLI 导入测试通过")


def test_commands_import():
    """测试命令模块导入"""
    from commands.version import version_cmd
    from commands.test import test_cmd
    from commands.quality import scan_cmd
    from commands.git_ops import commit_cmd
    from commands.publish import publish_cmd
    from commands.dev_flow import dev_flow, full_flow
    
    assert version_cmd is not None
    assert test_cmd is not None
    assert scan_cmd is not None
    assert commit_cmd is not None
    assert publish_cmd is not None
    assert dev_flow is not None
    assert full_flow is not None
    
    print("✅ 命令模块导入测试通过")


if __name__ == '__main__':
    print("=" * 60)
    print("skill-lifecycle 自测试")
    print("=" * 60)
    print()
    
    try:
        test_parse_version()
        test_bump_version()
        test_cli_import()
        test_commands_import()
        
        print()
        print("=" * 60)
        print("✅ 所有测试通过")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 测试失败：{e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
