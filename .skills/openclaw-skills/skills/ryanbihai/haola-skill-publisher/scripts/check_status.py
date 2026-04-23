#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有 Skill 的发布状态
Usage:
  python scripts/check_status.py [slug]
  python scripts/check_status.py all

依赖 .env 文件中的 GITHUB_TOKEN
"""
import json, os, subprocess, sys, urllib.request
from pathlib import Path

SKILLS_DIR = "/home/node/.openclaw/workspace/skills"
SKILL_PKG  = Path(__file__).resolve().parent.parent
ENV_FILE   = SKILL_PKG / ".env"
PLATFORMS_FILE = SKILL_PKG / "data" / "platforms.json"

def load_env():
    """从 .env 文件加载环境变量"""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

def get_github_info(repo):
    token = os.environ.get('GITHUB_TOKEN', '')
    try:
        url = f"https://api.github.com/repos/{repo}"
        headers = {"Authorization": f"token {token}"} if token else {}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except:
        return {}

def check_clawhub(slug):
    try:
        r = subprocess.run(
            ['npx', '-y', 'clawhub', 'inspect', slug, '--json'],
            capture_output=True, text=True, timeout=15,
            cwd=str(SKILL_PKG)
        )
        data = json.loads(r.stdout)
        s = data.get('skill', {})
        stats = s.get('stats', {})
        ver = s.get('tags', {}).get('latest', '?')
        return {
            'status': '✅ 已发布', 'version': ver,
            'downloads': stats.get('downloads', 0),
            'stars': stats.get('stars', 0),
            'url': f'https://clawhub.ai/skills/{slug}'
        }
    except Exception as e:
        return {'status': f'❌ ({str(e)[:50]})', 'version': '?', 'downloads': 0, 'stars': 0, 'url': ''}

def check_github(slug):
    try:
        data = get_github_info(f"ryanbihai/{slug}")
        if data.get('id'):
            return {
                'status': '✅ 已推送',
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'updated': data.get('updated_at', '')[:10],
                'url': data.get('html_url', '')
            }
    except: pass
    return {'status': '❌ 未推送', 'stars': 0, 'forks': 0, 'url': ''}

def get_local(slug):
    p = SKILLS_DIR + f"/{slug}/_meta.json"
    if os.path.exists(p):
        d = json.load(open(p))
        return d.get('version', '?'), d.get('changelog', '')[:60]
    return '?', ''

def main():
    load_env()
    args = sys.argv[1:]
    with open(PLATFORMS_FILE) as f:
        data = json.load(f)
    slugs = args if args and args[0] != 'all' else list(data.get('skills', {}).keys())

    print("\n" + "=" * 56)
    print("📊 Skill 发布状态总览")
    print("=" * 56)

    for slug in sorted(slugs):
        ver, changelog = get_local(slug)
        ch = check_clawhub(slug)
        gh = check_github(slug)
        print(f"\n📦 {slug}")
        print(f"   本地版本: v{ver}")
        print(f"   更新说明: {changelog}")
        print(f"   ─────────────────────────────────────")
        print(f"   🌐 ClawHub:  {ch['status']} | v{ch.get('version','?')} | ↓{ch.get('downloads',0)} | ⭐{ch.get('stars',0)}")
        print(f"   💻 GitHub:   {gh['status']} | ⭐{gh.get('stars',0)} | 更新:{gh.get('updated','?')}")
        print(f"   🏪 SkillsMP: 自动同步")
        print(f"   🌊 SkillzWave: ⏳ 需手动提交")
        print(f"   🤖 COZE:       ⏳ 需手动提交")
        print(f"   🟢 腾讯元器:   ⏳ 需手动提交")
        print(f"   🔵 阿里百炼:   ⏳ 需手动提交")

    print("\n" + "=" * 56)
    print("💡 运行 python scripts/gen_submission.py [slug] 生成提交文本")
    print("⚠️  首次使用请复制 .env.example 为 .env 并填入 GITHUB_TOKEN")
    print()

if __name__ == '__main__':
    main()
