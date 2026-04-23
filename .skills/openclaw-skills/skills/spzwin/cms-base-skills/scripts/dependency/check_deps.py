#!/usr/bin/env python3
"""
依赖检查 — 读取 SKILL.md 的 dependencies，自动安装缺失的 Skill

用途：任何 Skill 启动前调用此脚本，确保依赖已就绪

使用方式：
  # 检查某个 Skill 的依赖
  python3 xgjk-base-skills/scripts/dependency/check_deps.py --skill-path /path/to/some-skill

  # 检查并自动安装缺失的依赖
  python3 xgjk-base-skills/scripts/dependency/check_deps.py --skill-path /path/to/some-skill --auto-install

  # 仅检查，不安装（默认）
  python3 xgjk-base-skills/scripts/dependency/check_deps.py --skill-path /path/to/some-skill --check-only

  # 被其他脚本调用（Python API）
  from dependency.check_deps import ensure_dependencies
  ensure_dependencies("/path/to/some-skill", auto_install=True)

流程：
  1. 读取 <skill-path>/SKILL.md 的 YAML frontmatter
  2. 提取 dependencies 列表
  3. 逐个检查同级目录下是否存在对应的 Skill 文件夹
  4. 缺失的 → 调用 install_skill.py 从平台下载安装
"""

import sys
import os
import re
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_DIR = os.path.join(SCRIPT_DIR, "..", "skill_registry")
sys.path.insert(0, REGISTRY_DIR)


def parse_frontmatter(skill_md_path: str) -> dict:
    """
    解析 SKILL.md 的 YAML frontmatter（简易解析，不依赖 PyYAML）

    支持格式：
      ---
      name: xxx
      dependencies:
        - aaa
        - bbb
      ---
    """
    if not os.path.isfile(skill_md_path):
        return {}

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取 frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    fm_text = match.group(1)
    result = {}
    current_key = None
    current_list = None

    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # 列表项：  - xxx
        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(stripped[2:].strip())
            result[current_key] = current_list
            continue

        # 键值对：key: value 或 key:
        kv_match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)', stripped)
        if kv_match:
            if current_list is not None:
                current_list = None
            current_key = kv_match.group(1)
            value = kv_match.group(2).strip()
            if value:
                # 尝试解析内联列表 [a, b, c]
                if value.startswith("[") and value.endswith("]"):
                    items = [x.strip().strip("'\"") for x in value[1:-1].split(",")]
                    result[current_key] = [x for x in items if x]
                    current_list = result[current_key]
                else:
                    result[current_key] = value.strip("'\"")
                    current_list = None
            else:
                # 值为空，可能是列表的开始
                result[current_key] = []
                current_list = result[current_key]

    return result


def find_skill_dir(skill_name: str, search_dir: str) -> str | None:
    """
    在 search_dir 中查找 Skill 文件夹

    搜索策略（按优先级）：
      1. 精确匹配：<search_dir>/<skill_name>/SKILL.md
      2. 带后缀：<search_dir>/<skill_name>-skills/SKILL.md
      3. 带前缀：<search_dir>/xgjk-<skill_name>/SKILL.md
    """
    candidates = [
        skill_name,
        f"{skill_name}-skills",
        f"xgjk-{skill_name}",
        f"xgjk-{skill_name}-skills",
    ]
    # 也尝试去掉前缀
    if skill_name.startswith("xgjk-"):
        base = skill_name[5:]
        candidates.extend([base, f"{base}-skills"])

    for name in candidates:
        candidate_path = os.path.join(search_dir, name)
        if os.path.isdir(candidate_path):
            # 验证是否是 Skill（有 SKILL.md）
            if os.path.isfile(os.path.join(candidate_path, "SKILL.md")):
                return candidate_path
    return None


def check_dependencies(skill_path: str) -> dict:
    """
    检查 Skill 的依赖状态

    Args:
        skill_path: Skill 根目录路径

    Returns:
        {
            "skill_name": str,
            "dependencies": [str],
            "resolved": {"dep_name": "/path/to/dep"},
            "missing": ["dep_name"],
        }
    """
    skill_md = os.path.join(skill_path, "SKILL.md")
    fm = parse_frontmatter(skill_md)
    skill_name = fm.get("name", os.path.basename(skill_path))
    deps = fm.get("dependencies", [])

    if isinstance(deps, str):
        deps = [deps]

    # 搜索目录 = Skill 的父目录（同级）
    search_dir = os.path.dirname(os.path.abspath(skill_path))

    resolved = {}
    missing = []

    for dep in deps:
        dep_dir = find_skill_dir(dep, search_dir)
        if dep_dir:
            resolved[dep] = dep_dir
        else:
            missing.append(dep)

    return {
        "skill_name": skill_name,
        "dependencies": deps,
        "resolved": resolved,
        "missing": missing,
    }


def install_missing(missing: list, target_dir: str, quiet: bool = False) -> dict:
    """
    尝试安装缺失的依赖

    Returns:
        {"installed": ["dep1"], "failed": ["dep2"]}
    """
    installed = []
    failed = []

    try:
        from install_skill import install_skill
    except ImportError:
        print("无法导入 install_skill 模块", file=sys.stderr)
        return {"installed": [], "failed": missing}

    for dep in missing:
        if not quiet:
            print(f"正在安装依赖: {dep}", file=sys.stderr)

        result = install_skill(code=dep, target_dir=target_dir, quiet=quiet)

        if result.get("success"):
            installed.append(dep)
            if not quiet:
                print(f"  已安装: {dep} → {result.get('path', '')}", file=sys.stderr)
        else:
            failed.append(dep)
            if not quiet:
                print(f"  安装失败: {dep} — {result.get('message', '')}", file=sys.stderr)

    return {"installed": installed, "failed": failed}


def ensure_dependencies(skill_path: str, auto_install: bool = False, quiet: bool = False) -> dict:
    """
    一键检查并安装依赖（供其他脚本调用的主入口）

    Args:
        skill_path: Skill 根目录
        auto_install: 是否自动安装缺失依赖
        quiet: 静默模式

    Returns:
        {
            "ready": bool,           # 所有依赖是否就绪
            "skill_name": str,
            "dependencies": [str],
            "resolved": {str: str},  # 已解析的依赖
            "missing": [str],        # 缺失的依赖
            "installed": [str],      # 本次安装成功的
            "failed": [str],         # 本次安装失败的
        }
    """
    check = check_dependencies(skill_path)

    result = {
        "ready": len(check["missing"]) == 0,
        "skill_name": check["skill_name"],
        "dependencies": check["dependencies"],
        "resolved": check["resolved"],
        "missing": check["missing"],
        "installed": [],
        "failed": [],
    }

    if check["missing"] and auto_install:
        target_dir = os.path.dirname(os.path.abspath(skill_path))
        install_result = install_missing(check["missing"], target_dir, quiet)
        result["installed"] = install_result["installed"]
        result["failed"] = install_result["failed"]
        result["missing"] = install_result["failed"]  # 最终缺失 = 安装失败的
        result["ready"] = len(result["failed"]) == 0

    return result


def main():
    parser = argparse.ArgumentParser(description="依赖检查 — 读取 SKILL.md 的 dependencies 并检查/安装")
    parser.add_argument("--skill-path", "-p", type=str, required=True, help="Skill 根目录路径")
    parser.add_argument("--auto-install", "-a", action="store_true", help="自动安装缺失的依赖")
    parser.add_argument("--check-only", action="store_true", help="仅检查，不安装（默认）")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    args = parser.parse_args()

    result = ensure_dependencies(
        skill_path=args.skill_path,
        auto_install=args.auto_install and not args.check_only,
        quiet=args.quiet,
    )

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 人类可读摘要
    if not args.quiet:
        print(f"\n--- 依赖检查: {result['skill_name']} ---", file=sys.stderr)
        if not result["dependencies"]:
            print("  无依赖声明", file=sys.stderr)
        else:
            for dep in result["dependencies"]:
                if dep in result["resolved"]:
                    print(f"  [OK] {dep} → {result['resolved'][dep]}", file=sys.stderr)
                elif dep in result["installed"]:
                    print(f"  [INSTALLED] {dep}", file=sys.stderr)
                else:
                    print(f"  [MISSING] {dep}", file=sys.stderr)

        if result["ready"]:
            print("\n所有依赖已就绪", file=sys.stderr)
        else:
            print(f"\n缺失 {len(result['missing'])} 个依赖: {', '.join(result['missing'])}", file=sys.stderr)
            if not args.auto_install:
                print("提示：添加 --auto-install 自动安装缺失依赖", file=sys.stderr)

    if not result["ready"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
