#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成各平台提交文本
Usage:
  python gen_submission.py <slug> [slug2] [slug3]
  python gen_submission.py all
  python gen_submission.py health-checkup-recommender
"""

import json
import os
import sys

SKILLS_DIR = "/home/node/.openclaw/workspace/skills"
PLATFORMS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'platforms.json')


def load_platforms():
    with open(PLATFORMS_FILE) as f:
        return json.load(f)


def load_skill(slug):
    meta_path = os.path.join(SKILLS_DIR, slug, '_meta.json')
    skill_path = os.path.join(SKILLS_DIR, slug, 'SKILL.md')
    if not os.path.exists(meta_path):
        return None, None
    with open(meta_path) as f:
        meta = json.load(f)
    description = ""
    if os.path.exists(skill_path):
        with open(skill_path) as f:
            content = f.read()
        # Extract first non-header line as description
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
        description = lines[0][:200] if lines else meta.get('description', '')[:200]
    return meta, description


def extract_features(skill_path, max_features=4):
    """从 SKILL.md 提取功能特点（排除脚本命令和流程说明）"""
    if not os.path.exists(skill_path):
        return []
    with open(skill_path) as f:
        content = f.read()

    # Skip these lines (script/tool related, not features)
    skip_patterns = [
        'npm:', 'python:', 'node ', 'pip install',
        'qrcode', 'generate_qr', 'verify_items',
        'scripts/', '.js', '.py', 'shell',
        '回复"', '好的', '可以', '不用', '算了',
        '发送', 'channel', 'openclaw',
        'memory/', 'USER.md', 'avatars/',
        'require(', 'import ', 'from ',
        '##', '#', '```', '---',
    ]

    features = []
    keywords = ['根据', '智能', '每日', '支持', '自动', '生成', '推荐', '监测', '追踪', '实时', '循证', '个性化', '二维码', '变动', '推送']

    for line in content.split('\n'):
        line = line.strip()
        # Only short bullet lines (likely feature descriptions)
        if not (line.startswith('-') or line.startswith('•')):
            continue
        if len(line) < 10 or len(line) > 100:
            continue
        # Skip code/config lines
        skip = any(p in line for p in skip_patterns)
        if skip:
            continue
        # Must contain a meaningful keyword
        if not any(kw in line for kw in keywords):
            continue
        feat = line.lstrip('-*• ').strip()
        feat = feat.split('|')[0].strip()
        feat = feat.split('`')[0].strip()
        if len(feat) > 5:
            features.append(feat)
        if len(features) >= max_features:
            break

    return features[:max_features]


def gen_coze(meta, description, features, slug, github_repo):
    """生成 COZE/扣子 提交文本"""
    version = meta.get('version', '1.0.0')
    changelog = meta.get('changelog', '')
    tags = ', '.join(meta.get('tags', []))

    return f"""
# COZE/扣子 提交文本

## 基础信息
- **技能名称**：{meta.get('name', slug)}
- **版本**：v{version}
- **GitHub**：https://github.com/{github_repo}
- **标签**：{tags}

## 一句话简介
{description[:100]}

## 功能特点
""" + '\n'.join(f"{i+1}. {f}" for i, f in enumerate(features)) + f"""

## 详细说明
{description[:500]}

## 更新日志
{changelog}

## 安装方式
在 OpenClaw 客户端搜索「{slug}」安装，或访问 GitHub 仓库查看完整说明。

## 开源许可证
MIT-0

## 提交注意事项
- 上传到 COZE 时可选择「从 GitHub 导入」
- 或手动复制 SKILL.md 内容创建智能体
- 审核周期约1-3个工作日
"""


def gen_yuanqi(meta, description, features, slug, github_repo):
    """生成 腾讯元器 提交文本"""
    version = meta.get('version', '1.0.0')
    changelog = meta.get('changelog', '')
    tags = ', '.join(meta.get('tags', []))

    return f"""
# 腾讯元器 提交文本

## 智能体名称
{meta.get('name', slug)}

## 类型
AI 助手 / 工具类智能体

## 功能介绍
""" + '\n'.join(f"• {f}" for f in features) + f"""

{description[:300]}

## 版本
v{version}

## GitHub 地址
https://github.com/{github_repo}

## 标签
{tags}

## 更新说明
{changelog}

## 开源协议
MIT-0（可自由使用、修改和分发）
"""


def gen_bailian(meta, description, features, slug, github_repo):
    """生成 阿里百炼 提交文本"""
    version = meta.get('version', '1.0.0')
    changelog = meta.get('changelog', '')
    tags = ', '.join(meta.get('tags', []))

    return f"""
# 阿里百炼 提交文本

## 智能体名称
{meta.get('name', slug)}

## 简介
{description[:150]}

## 核心功能
""" + '\n'.join(f"{i+1}. {f}" for i, f in enumerate(features)) + f"""

## 详细介绍
{description[:500]}

## 版本
v{version}

## 开源地址
https://github.com/{github_repo}

## 标签/关键词
{tags}

## 更新日志
{changelog}

## 协议
MIT-0
"""


def gen_skillzwave(meta, description, features, slug, github_repo):
    """生成 SkillzWave 提交文本"""
    version = meta.get('version', '1.0.0')
    tags = ', '.join(meta.get('tags', []))
    features_text = ' / '.join(features[:3])

    return f"""# SkillzWave 提交信息

**Skill Name**: {meta.get('name', slug)}
**Version**: {version}
**Repository**: https://github.com/{github_repo}
**License**: MIT-0
**Tags**: {tags}

**Short Description**:
{description[:150]}

**Features**: {features_text}

**Full Description**:
{description[:500]}

**Steps to Submit on SkillzWave**:
1. Visit https://skillzwave.ai/submit/
2. Click "Login with GitHub" (OAuth)
3. Select repository: {github_repo}
4. Verify information auto-populated
5. Submit
"""


def generate_for_skill(slug):
    meta, description = load_skill(slug)
    if not meta:
        print(f"[ERROR] Skill not found: {slug}")
        return

    github_repo = f"ryanbihai/{slug}"
    features = extract_features(os.path.join(SKILLS_DIR, slug, 'SKILL.md'))

    print(f"\n{'='*60}")
    print(f"📦 {meta.get('name', slug)} v{meta.get('version', '?')}")
    print(f"{'='*60}\n")

    print(gen_coze(meta, description, features, slug, github_repo))
    print(gen_yuanqi(meta, description, features, slug, github_repo))
    print(gen_bailian(meta, description, features, slug, github_repo))
    print(gen_skillzwave(meta, description, features, slug, github_repo))


def main():
    args = sys.argv[1:]
    if not args or 'all' in args:
        # All registered skills
        data = load_platforms()
        slugs = list(data.get('skills', {}).keys())
    else:
        slugs = args

    for slug in slugs:
        generate_for_skill(slug)


if __name__ == '__main__':
    main()
