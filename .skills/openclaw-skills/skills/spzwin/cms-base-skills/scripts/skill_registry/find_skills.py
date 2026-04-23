#!/usr/bin/env python3
"""
Skill 发现 — 搜索、浏览、查看详情

用途：从玄关 Skill 管理平台查询已发布的 Skill

使用方式：
  # 浏览全部
  python3 xgjk-base-skills/scripts/skill_registry/find_skills.py

  # 按关键词搜索（名称/描述模糊匹配）
  python3 xgjk-base-skills/scripts/skill_registry/find_skills.py --search "机器人"

  # 查看某个 Skill 详情（按 code 或 name 匹配）
  python3 xgjk-base-skills/scripts/skill_registry/find_skills.py --detail "im-robot"

  # 仅返回 downloadUrl（供 install_skill.py 使用）
  python3 xgjk-base-skills/scripts/skill_registry/find_skills.py --url "im-robot"

说明：
  此接口为 nologin 接口，无需 XG_USER_TOKEN。
"""

import sys
import json
import argparse
import urllib.request
import urllib.error
import ssl

API_URL = "https://sg-cwork-api.mediportal.com.cn/im/skill/nologin/list"


def call_api() -> dict:
    """获取 Skill 列表（无需鉴权）"""
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(API_URL, headers=headers, method="GET")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_skills(result: dict) -> list:
    """从 API 响应中提取 skill 列表"""
    if isinstance(result, list):
        return result
    return result.get("data") or result.get("resultData") or []


def format_list(skills: list) -> str:
    """格式化为表格展示"""
    if not skills:
        return "（暂无已发布的 Skill）"
    lines = []
    lines.append(f"{'#':<4} {'名称':<20} {'Code':<20} {'版本':<6} {'状态':<10} {'描述'}")
    lines.append("-" * 100)
    for i, s in enumerate(skills, 1):
        name = (s.get("name") or "")[:18]
        code = (s.get("code") or "")[:18]
        version = str(s.get("version", ""))[:5]
        status = s.get("status") or ""
        desc = (s.get("description") or "")[:40]
        lines.append(f"{i:<4} {name:<20} {code:<20} {version:<6} {status:<10} {desc}")
    lines.append(f"\n共 {len(skills)} 个 Skill")
    return "\n".join(lines)


def format_detail(skill: dict) -> str:
    """格式化单个 Skill 详情"""
    lines = [
        "=" * 60,
        f"  名称: {skill.get('name', '-')}",
        f"  Code: {skill.get('code', '-')}",
        f"    ID: {skill.get('id', '-')}",
        f"  版本: {skill.get('version', '-')}",
        f"  状态: {skill.get('status', '-')}",
        f"  类型: {'内部' if skill.get('isInternal') else '外部'}",
        f"  标签: {skill.get('label', '-')}",
        f"  描述: {skill.get('description', '-')}",
        f"  下载: {skill.get('downloadUrl', '-')}",
        f"  创建: {skill.get('createTime', '-')}",
    ]
    if skill.get("delistReason"):
        lines.append(f"  下架原因: {skill['delistReason']}")
    lines.append("=" * 60)
    return "\n".join(lines)


def search_skills(skills: list, keyword: str) -> list:
    """按关键词搜索（名称/描述/code 模糊匹配）"""
    kw = keyword.lower()
    return [
        s for s in skills
        if kw in (s.get("name") or "").lower()
        or kw in (s.get("description") or "").lower()
        or kw in (s.get("code") or "").lower()
    ]


def find_one(skills: list, query: str) -> dict | None:
    """按 code 或 name 精确/模糊匹配单个 Skill"""
    q = query.lower()
    # 精确匹配 code
    for s in skills:
        if (s.get("code") or "").lower() == q:
            return s
    # 精确匹配 name
    for s in skills:
        if (s.get("name") or "").lower() == q:
            return s
    # 模糊匹配
    for s in skills:
        if q in (s.get("code") or "").lower() or q in (s.get("name") or "").lower():
            return s
    return None


def get_download_url(skills: list, query: str) -> str | None:
    """获取 Skill 的下载地址（供 install_skill.py 调用）"""
    skill = find_one(skills, query)
    if skill:
        return skill.get("downloadUrl")
    return None


def main():
    parser = argparse.ArgumentParser(description="Skill 发现 — 搜索、浏览、查看详情")
    parser.add_argument("--search", "-s", type=str, help="按关键词搜索 Skill")
    parser.add_argument("--detail", "-d", type=str, help="查看某个 Skill 的详情")
    parser.add_argument("--url", "-u", type=str, help="仅输出某个 Skill 的下载地址")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON 格式")
    args = parser.parse_args()

    try:
        result = call_api()
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)

    skills = extract_skills(result)

    # JSON 模式
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 下载地址模式（机器调用）
    if args.url:
        url = get_download_url(skills, args.url)
        if url:
            print(url)
        else:
            print(f"未找到 \"{args.url}\" 的下载地址", file=sys.stderr)
            sys.exit(1)
        return

    # 详情模式
    if args.detail:
        skill = find_one(skills, args.detail)
        if skill:
            print(format_detail(skill))
        else:
            print(f"未找到匹配 \"{args.detail}\" 的 Skill", file=sys.stderr)
            for s in skills:
                print(f"  - {s.get('code', '')} ({s.get('name', '')})", file=sys.stderr)
            sys.exit(1)
        return

    # 搜索模式
    if args.search:
        matched = search_skills(skills, args.search)
        if matched:
            print(f"搜索 \"{args.search}\" 匹配到 {len(matched)} 个结果：\n")
            print(format_list(matched))
        else:
            print(f"搜索 \"{args.search}\" 无结果", file=sys.stderr)
            sys.exit(1)
        return

    # 列表模式（默认）
    print(f"平台 Skill 列表\n")
    print(format_list(skills))


if __name__ == "__main__":
    main()
