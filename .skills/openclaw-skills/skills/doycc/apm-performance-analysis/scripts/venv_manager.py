#!/usr/bin/env python3
"""
APM 智能运维 Skill 虚拟环境管理工具

自动在用户工作目录中创建和管理 Python 虚拟环境（.apm-venv），
确保 skill 所需的第三方依赖安装在隔离环境中，不会污染用户的
全局 Python 环境。

功能：
    - 自动检测并创建虚拟环境
    - 自动安装 skill 所需依赖（mcp、httpx）
    - 提供 activate 命令输出用于 shell 中激活
    - 提供 run 命令在虚拟环境中执行任意脚本
    - 支持自定义虚拟环境路径

用法示例:
    # 创建/确保虚拟环境就绪（含依赖安装）
    python scripts/venv_manager.py ensure

    # 在虚拟环境中运行 mcp_client.py
    python scripts/venv_manager.py run scripts/mcp_client.py list-tools

    # 查看虚拟环境激活命令
    python scripts/venv_manager.py activate

    # 查看虚拟环境状态
    python scripts/venv_manager.py status

    # 安装额外依赖
    python scripts/venv_manager.py install mcp httpx

    # 清理虚拟环境
    python scripts/venv_manager.py clean
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import venv
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量定义
# ---------------------------------------------------------------------------

# 虚拟环境目录名
VENV_DIR_NAME = ".apm-venv"

# skill 所需的核心依赖
# MCP 桥接方式的依赖
MCP_DEPENDENCIES = ["mcp", "httpx"]

# requirements.txt 模板内容
REQUIREMENTS_CONTENT = """\
# APM 智能运维 Skill 依赖
# MCP 桥接
mcp>=1.0.0
httpx>=0.24.0
"""

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent


# ---------------------------------------------------------------------------
# 虚拟环境路径计算
# ---------------------------------------------------------------------------

def get_venv_dir(custom_path=None):
    """
    获取虚拟环境目录路径。

    优先级：
    1. 命令行参数 --venv-dir 显式指定
    2. 环境变量 APM_VENV_DIR
    3. 当前工作目录下的 .apm-venv/

    Returns:
        Path: 虚拟环境绝对路径
    """
    if custom_path:
        return Path(custom_path).resolve()

    env_path = os.environ.get("APM_VENV_DIR")
    if env_path:
        return Path(env_path).resolve()

    return Path(os.getcwd()).resolve() / VENV_DIR_NAME


def get_venv_python(venv_dir):
    """获取虚拟环境中的 Python 可执行文件路径。"""
    venv_dir = Path(venv_dir)
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def get_venv_pip(venv_dir):
    """获取虚拟环境中的 pip 可执行文件路径。"""
    venv_dir = Path(venv_dir)
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "pip"


def get_activate_command(venv_dir):
    """获取虚拟环境激活命令。"""
    venv_dir = Path(venv_dir)
    if platform.system() == "Windows":
        return str(venv_dir / "Scripts" / "activate.bat")
    return f"source {venv_dir / 'bin' / 'activate'}"


def is_venv_valid(venv_dir):
    """检查虚拟环境是否存在且有效。"""
    python_path = get_venv_python(venv_dir)
    return python_path.is_file()


# ---------------------------------------------------------------------------
# 虚拟环境操作
# ---------------------------------------------------------------------------

def create_venv(venv_dir, with_pip=True):
    """
    创建 Python 虚拟环境。

    Args:
        venv_dir: 虚拟环境目录路径
        with_pip: 是否安装 pip

    Returns:
        bool: 是否创建成功
    """
    venv_dir = Path(venv_dir)

    if is_venv_valid(venv_dir):
        print(f"虚拟环境已存在: {venv_dir}")
        return True

    print(f"正在创建虚拟环境: {venv_dir}")

    try:
        # 使用 venv 模块创建虚拟环境
        builder = venv.EnvBuilder(
            system_site_packages=False,
            clear=False,
            symlinks=(platform.system() != "Windows"),
            with_pip=with_pip,
            upgrade_deps=False,
        )
        builder.create(str(venv_dir))

        # 验证创建结果
        if not is_venv_valid(venv_dir):
            print(f"错误: 虚拟环境创建后验证失败: {venv_dir}")
            return False

        print(f"虚拟环境创建成功: {venv_dir}")

        # 升级 pip 到最新版本
        python_path = get_venv_python(venv_dir)
        print("正在升级 pip...")
        subprocess.run(
            [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            check=False,
        )

        return True

    except Exception as e:
        print(f"错误: 创建虚拟环境失败: {e}")
        return False


def install_dependencies(venv_dir, packages=None, requirements_file=None):
    """
    在虚拟环境中安装依赖包。

    Args:
        venv_dir: 虚拟环境目录路径
        packages: 要安装的包列表（如 ['mcp', 'httpx']）
        requirements_file: requirements.txt 文件路径

    Returns:
        bool: 是否安装成功
    """
    python_path = get_venv_python(venv_dir)

    if not python_path.is_file():
        print(f"错误: 虚拟环境 Python 不存在: {python_path}")
        return False

    cmd = [str(python_path), "-m", "pip", "install"]

    if requirements_file:
        cmd.extend(["-r", str(requirements_file)])
    elif packages:
        cmd.extend(packages)
    else:
        # 使用默认的 MCP 依赖
        cmd.extend(MCP_DEPENDENCIES)

    print(f"正在安装依赖: {' '.join(cmd[4:])}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print(f"依赖安装出现问题:")
            if result.stderr:
                # 只打印关键错误行，过滤掉 pip 的 warning
                for line in result.stderr.strip().split("\n"):
                    if "ERROR" in line or "error" in line.lower():
                        print(f"  {line}")
            # 即使部分失败也不完全中断，某些可选包可能不需要
            return result.returncode == 0

        print("依赖安装完成。")
        return True

    except Exception as e:
        print(f"错误: 安装依赖失败: {e}")
        return False


def install_mcp_dependencies(venv_dir):
    """安装 MCP 桥接所需的依赖。"""
    return install_dependencies(venv_dir, packages=MCP_DEPENDENCIES)


def ensure_venv(venv_dir, deps="mcp"):
    """
    确保虚拟环境已就绪（创建 + 安装依赖）。

    Args:
        venv_dir: 虚拟环境目录路径
        deps: 要安装的依赖类型（保留参数兼容性，始终安装 MCP 依赖）

    Returns:
        bool: 是否就绪
    """
    venv_dir = Path(venv_dir)

    # 1. 创建虚拟环境
    if not create_venv(venv_dir):
        return False

    # 2. 安装 MCP 依赖
    return install_mcp_dependencies(venv_dir)


def run_in_venv(venv_dir, script_args):
    """
    在虚拟环境中运行 Python 脚本。

    Args:
        venv_dir: 虚拟环境目录路径
        script_args: 脚本路径及参数列表

    Returns:
        int: 脚本退出码
    """
    python_path = get_venv_python(venv_dir)

    if not python_path.is_file():
        print(f"错误: 虚拟环境不存在或未初始化: {venv_dir}")
        print(f"请先运行: python {__file__} ensure")
        return 1

    cmd = [str(python_path)] + script_args

    try:
        result = subprocess.run(
            cmd,
            check=False,
        )
        return result.returncode
    except Exception as e:
        print(f"错误: 执行脚本失败: {e}")
        return 1


def get_venv_status(venv_dir):
    """
    获取虚拟环境状态信息。

    Returns:
        dict: 状态信息
    """
    venv_dir = Path(venv_dir)
    python_path = get_venv_python(venv_dir)

    status = {
        "venv_dir": str(venv_dir),
        "exists": venv_dir.is_dir(),
        "valid": is_venv_valid(venv_dir),
        "python_path": str(python_path),
        "activate_command": get_activate_command(venv_dir),
        "installed_packages": [],
    }

    if status["valid"]:
        # 获取已安装包列表
        try:
            result = subprocess.run(
                [str(python_path), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                status["installed_packages"] = [
                    {"name": p["name"], "version": p["version"]}
                    for p in packages
                ]
        except Exception:
            pass

        # 检查核心依赖是否已安装
        pkg_names = {p["name"].lower() for p in status["installed_packages"]}
        status["mcp_installed"] = "mcp" in pkg_names
        status["httpx_installed"] = "httpx" in pkg_names

    return status


def clean_venv(venv_dir):
    """
    清理（删除）虚拟环境。

    Args:
        venv_dir: 虚拟环境目录路径

    Returns:
        bool: 是否清理成功
    """
    venv_dir = Path(venv_dir)

    if not venv_dir.is_dir():
        print(f"虚拟环境不存在: {venv_dir}")
        return True

    print(f"正在清理虚拟环境: {venv_dir}")
    try:
        shutil.rmtree(venv_dir)
        print("虚拟环境已清理。")
        return True
    except Exception as e:
        print(f"错误: 清理虚拟环境失败: {e}")
        return False


def generate_requirements(output_path=None):
    """
    生成 requirements.txt 文件。

    Args:
        output_path: 输出路径，默认为当前目录的 requirements.txt
    """
    if output_path is None:
        output_path = Path(os.getcwd()) / "requirements.txt"

    output_path = Path(output_path)
    output_path.write_text(REQUIREMENTS_CONTENT, encoding="utf-8")
    print(f"requirements.txt 已生成: {output_path}")


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="APM 智能运维 Skill 虚拟环境管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  # 创建虚拟环境并安装 MCP 依赖\n"
            "  python venv_manager.py ensure\n"
            "\n"
            "  # 在虚拟环境中运行 MCP 客户端\n"
            "  python venv_manager.py run scripts/mcp_client.py list-tools\n"
            "\n"
            "  # 查看虚拟环境状态\n"
            "  python venv_manager.py status\n"
        ),
    )

    parser.add_argument(
        "--venv-dir",
        help=f"虚拟环境目录路径（默认: ./{VENV_DIR_NAME}）",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ensure - 确保虚拟环境就绪
    ensure_parser = subparsers.add_parser(
        "ensure",
        help="创建虚拟环境并安装依赖",
    )
    ensure_parser.add_argument(
        "--deps",
        default="mcp",
        help="安装的依赖类型，默认 mcp",
    )

    # run - 在虚拟环境中运行脚本
    run_parser = subparsers.add_parser(
        "run",
        help="在虚拟环境中运行 Python 脚本",
    )
    run_parser.add_argument(
        "script_args",
        nargs=argparse.REMAINDER,
        help="要运行的脚本路径及参数",
    )

    # activate - 输出激活命令
    subparsers.add_parser(
        "activate",
        help="输出虚拟环境激活命令",
    )

    # status - 查看虚拟环境状态
    status_parser = subparsers.add_parser(
        "status",
        help="查看虚拟环境状态",
    )
    status_parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="输出格式，默认 text",
    )

    # install - 安装额外依赖
    install_parser = subparsers.add_parser(
        "install",
        help="在虚拟环境中安装额外依赖",
    )
    install_parser.add_argument(
        "packages",
        nargs="+",
        help="要安装的包名",
    )

    # clean - 清理虚拟环境
    subparsers.add_parser(
        "clean",
        help="清理（删除）虚拟环境",
    )

    # gen-requirements - 生成 requirements.txt
    gen_parser = subparsers.add_parser(
        "gen-requirements",
        help="生成 requirements.txt 文件",
    )
    gen_parser.add_argument(
        "--output-file",
        help="输出文件路径（默认当前目录的 requirements.txt）",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    venv_dir = get_venv_dir(getattr(args, "venv_dir", None))

    if args.command == "ensure":
        ok = ensure_venv(venv_dir, deps=args.deps)
        if ok:
            print(f"\n虚拟环境已就绪: {venv_dir}")
            print(f"激活命令: {get_activate_command(venv_dir)}")
            print(f"\n使用虚拟环境运行脚本:")
            print(f"  python {__file__} run scripts/mcp_client.py list-tools")
        sys.exit(0 if ok else 1)

    elif args.command == "run":
        if not args.script_args:
            print("错误: 请提供要运行的脚本路径及参数")
            print(f"示例: python {__file__} run scripts/mcp_client.py list-tools")
            sys.exit(1)

        # 如果虚拟环境不存在，自动创建
        if not is_venv_valid(venv_dir):
            print(f"虚拟环境不存在，正在自动创建...")
            if not ensure_venv(venv_dir, deps="mcp"):
                print("错误: 虚拟环境创建失败")
                sys.exit(1)
            print("")  # 空行分隔

        exit_code = run_in_venv(venv_dir, args.script_args)
        sys.exit(exit_code)

    elif args.command == "activate":
        if not is_venv_valid(venv_dir):
            print(f"虚拟环境不存在: {venv_dir}")
            print(f"请先运行: python {__file__} ensure")
            sys.exit(1)
        print(get_activate_command(venv_dir))

    elif args.command == "status":
        status = get_venv_status(venv_dir)

        if args.output == "json":
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print(f"虚拟环境状态")
            print("=" * 60)
            print(f"  目录:      {status['venv_dir']}")
            print(f"  存在:      {'是' if status['exists'] else '否'}")
            print(f"  有效:      {'是' if status['valid'] else '否'}")
            print(f"  Python:    {status['python_path']}")
            print(f"  激活命令:  {status['activate_command']}")

            if status["valid"]:
                print(f"\n  核心依赖状态:")
                print(f"    mcp:                {'已安装' if status.get('mcp_installed') else '未安装'}")
                print(f"    httpx:              {'已安装' if status.get('httpx_installed') else '未安装'}")

                print(f"\n  已安装包 (共 {len(status['installed_packages'])} 个):")
                for pkg in status["installed_packages"]:
                    print(f"    {pkg['name']}=={pkg['version']}")
            print("=" * 60)

    elif args.command == "install":
        if not is_venv_valid(venv_dir):
            print(f"虚拟环境不存在，正在自动创建...")
            if not create_venv(venv_dir):
                print("错误: 虚拟环境创建失败")
                sys.exit(1)

        ok = install_dependencies(venv_dir, packages=args.packages)
        sys.exit(0 if ok else 1)

    elif args.command == "clean":
        ok = clean_venv(venv_dir)
        sys.exit(0 if ok else 1)

    elif args.command == "gen-requirements":
        generate_requirements(getattr(args, "output_file", None))


if __name__ == "__main__":
    main()
