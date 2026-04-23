#!/usr/bin/env python3
"""
Skill 安装 — 从平台下载并安装 Skill 到本地

用途：根据 Skill code 或下载地址，安装到指定目录

使用方式：
  # 按 code 从平台查找并安装（自动查询 downloadUrl）
  python3 xgjk-base-skills/scripts/skill_registry/install_skill.py --code "im-robot"

  # 按下载地址直接安装
  python3 xgjk-base-skills/scripts/skill_registry/install_skill.py --url "https://..."

  # 指定安装目标目录（默认为项目根目录）
  python3 xgjk-base-skills/scripts/skill_registry/install_skill.py --code "im-robot" --target /path/to/dir

  # 静默模式（供 check_deps.py 自动调用）
  python3 xgjk-base-skills/scripts/skill_registry/install_skill.py --code "im-robot" --quiet

说明：
  - 下载 .zip 文件后自动解压到目标目录
  - 如目标已存在同名文件夹，默认跳过（加 --force 覆盖）
  - 无需 XG_USER_TOKEN（nologin 接口 + 公开下载链接）
"""

import sys
import os
import json
import argparse
import zipfile
import tempfile
import shutil
import urllib.request
import urllib.error
import ssl

# 同级模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def log(msg: str, quiet: bool = False):
    """输出日志到 stderr"""
    if not quiet:
        print(msg, file=sys.stderr)


def get_download_url_from_platform(code: str) -> str | None:
    """从平台查询 Skill 的下载地址"""
    try:
        from find_skills import call_api, extract_skills, get_download_url
        result = call_api()
        skills = extract_skills(result)
        return get_download_url(skills, code)
    except Exception as e:
        print(f"查询平台失败: {e}", file=sys.stderr)
        return None


def download_file(url: str, dest_path: str, quiet: bool = False) -> bool:
    """下载文件到本地"""
    log(f"正在下载: {url}", quiet)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
            total = resp.headers.get("Content-Length")
            total = int(total) if total else None
            downloaded = 0
            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total and not quiet:
                        pct = downloaded * 100 // total
                        print(f"\r  进度: {pct}% ({downloaded}/{total})", end="", file=sys.stderr)
            if total and not quiet:
                print("", file=sys.stderr)
        log(f"下载完成: {dest_path}", quiet)
        return True
    except Exception as e:
        print(f"下载失败: {e}", file=sys.stderr)
        return False


def extract_zip(zip_path: str, target_dir: str, skill_code: str = "", quiet: bool = False) -> str | None:
    """
    解压 zip 文件到目标目录，返回解压后的文件夹路径。

    处理两种 zip 结构：
      A) zip 内有唯一顶层文件夹（如 office/SKILL.md）→ 直接解压
      B) zip 内文件散在根目录（如 SKILL.md）→ 先创建 {skill_code}/ 再解压进去
    """
    log(f"正在解压到: {target_dir}", quiet)
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()

            # 分析 zip 结构：收集顶层条目
            top_entries = set()
            for name in names:
                top = name.split("/")[0]
                if top:
                    top_entries.add(top)

            # 判断是否有唯一顶层文件夹
            # 条件：只有一个顶层条目，且所有文件都在它下面
            has_single_root = False
            if len(top_entries) == 1:
                root_name = top_entries.pop()
                # 检查这个条目是否是文件夹（所有文件路径都以它开头 + /）
                all_under_root = all(
                    name == root_name or name.startswith(root_name + "/")
                    for name in names
                )
                if all_under_root:
                    has_single_root = True

            if has_single_root:
                # 情况 A：zip 自带顶层文件夹，直接解压
                zf.extractall(target_dir)
                extracted = os.path.join(target_dir, root_name)
                log(f"解压完成: {extracted}", quiet)
                return extracted
            else:
                # 情况 B：zip 内文件散在根目录，需要创建子文件夹
                folder_name = skill_code or os.path.splitext(os.path.basename(zip_path))[0] or "skill"
                dest_dir = os.path.join(target_dir, folder_name)
                os.makedirs(dest_dir, exist_ok=True)
                zf.extractall(dest_dir)
                log(f"解压完成（已创建文件夹）: {dest_dir}", quiet)
                return dest_dir

    except Exception as e:
        print(f"解压失败: {e}", file=sys.stderr)
        return None


def install_skill(code: str = None, url: str = None, target_dir: str = None,
                  force: bool = False, quiet: bool = False) -> dict:
    """
    安装 Skill 到本地

    Args:
        code: Skill code（从平台查询 downloadUrl）
        url: 直接提供的下载地址
        target_dir: 安装目标目录（默认为脚本所在项目的根目录）
        force: 是否覆盖已存在的同名目录
        quiet: 静默模式

    Returns:
        {"success": bool, "path": str, "message": str}
    """
    # 确定下载地址
    download_url = url
    if not download_url and code:
        download_url = get_download_url_from_platform(code)

    if not download_url:
        return {
            "success": False,
            "message": f"无法获取 Skill \"{code or ''}\" 的下载地址，可能该 Skill 不存在或未发布",
        }

    # 确定目标目录（默认为项目根目录 = base-skills 的上两级）
    if not target_dir:
        target_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

    # 如果有 code，检查目标是否已存在
    if code:
        # 尝试多种可能的目录名
        possible_names = [code, f"{code}-skills", f"xgjk-{code}", f"xgjk-{code}-skills"]
        for name in possible_names:
            existing = os.path.join(target_dir, name)
            if os.path.isdir(existing):
                if not force:
                    log(f"已存在: {existing}（跳过，使用 --force 覆盖）", quiet)
                    return {
                        "success": True,
                        "path": existing,
                        "message": f"Skill \"{code}\" 已存在于 {existing}",
                        "skipped": True,
                    }
                else:
                    log(f"覆盖: {existing}", quiet)
                    shutil.rmtree(existing)

    # 下载到临时文件
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 猜测文件扩展名
        filename = download_url.split("/")[-1].split("?")[0]
        if not filename.endswith(".zip"):
            filename = f"{code or 'skill'}.zip"
        tmp_file = os.path.join(tmp_dir, filename)

        if not download_file(download_url, tmp_file, quiet):
            return {"success": False, "message": "下载失败"}

        # 尝试解压（zip）
        if zipfile.is_zipfile(tmp_file):
            extracted = extract_zip(tmp_file, target_dir, skill_code=code or "", quiet=quiet)
            if extracted:
                return {
                    "success": True,
                    "path": extracted,
                    "message": f"Skill 已安装到 {extracted}",
                }
            return {"success": False, "message": "解压失败"}

        # 非 zip 文件：直接复制到目标目录
        dest_name = code or filename
        dest_dir = os.path.join(target_dir, dest_name)
        os.makedirs(dest_dir, exist_ok=True)
        dest_file = os.path.join(dest_dir, filename)
        shutil.copy2(tmp_file, dest_file)
        log(f"文件已保存到: {dest_file}", quiet)
        return {
            "success": True,
            "path": dest_dir,
            "message": f"文件已安装到 {dest_dir}",
        }


def main():
    parser = argparse.ArgumentParser(description="Skill 安装 — 从平台下载并安装到本地")
    parser.add_argument("--code", "-c", type=str, help="Skill code（从平台查找 downloadUrl）")
    parser.add_argument("--url", "-u", type=str, help="直接提供下载地址")
    parser.add_argument("--target", "-t", type=str, help="安装目标目录（默认项目根目录）")
    parser.add_argument("--force", "-f", action="store_true", help="覆盖已存在的同名目录")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    args = parser.parse_args()

    if not args.code and not args.url:
        parser.error("需要 --code 或 --url 之一")

    result = install_skill(
        code=args.code,
        url=args.url,
        target_dir=args.target,
        force=args.force,
        quiet=args.quiet,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
