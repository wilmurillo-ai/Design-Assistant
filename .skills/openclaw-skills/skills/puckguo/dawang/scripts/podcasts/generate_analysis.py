#!/usr/bin/env python3
"""
播客深度分析总结生成器
基于标题和描述生成AI深度分析
"""

import json
import os
from datetime import datetime

DATA_PATH = os.path.expanduser("~/.openclaw/workspaces/dawang/scripts/podcasts/podcast_data.json")
REPORT_PATH = os.path.expanduser("~/.openclaw/workspaces/dawang/scripts/podcasts/latest_report.md")

# 播客分析prompt模板
ANALYSIS_PROMPT = """
你是一个专业的科技播客内容分析师。请根据以下播客信息，生成深度分析总结：

**播客名称**: {podcast}
**集数标题**: {title}
**发布时间**: {published}
**简介/描述**: {summary}

请生成包含以下内容的深度总结（用中文输出，Markdown格式）：

## 🎯 核心要点
列出3-5个本期最重要的观点或话题

## 💡 深度洞察
对本期内容进行深度解读，分析其意义和影响

## 🔑 关键语录/观点
摘录或推断本期最值得关注的观点

## 📊 与行业趋势的关联
分析本期内容与当前AI/科技行业趋势的关联

## 🎬 适合人群
说明这期内容最适合谁听

请用专业、简洁的语言输出分析结果。
"""

def generate_analysis(podcast, title, published, summary):
    """生成单期播客的分析"""
    prompt = ANALYSIS_PROMPT.format(
        podcast=podcast,
        title=title,
        published=published,
        summary=summary or "无详细描述"
    )
    return prompt

def main():
    print("="*60)
    print("开始生成播客深度分析...")
    print("="*60)
    
    # 读取数据
    if not os.path.exists(DATA_PATH):
        print(f"数据文件不存在: {DATA_PATH}")
        return None
    
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updates = data.get('updates', [])
    
    if not updates:
        print("没有播客更新数据")
        return None
    
    # 生成分析报告
    today = datetime.now().strftime("%Y年%m月%d日")
    
    report = f"""# 🎧 播客深度分析精选

**生成时间**: {today}
**更新期数**: {len(updates)} 期

---

"""
    
    for i, ep in enumerate(updates[:6], 1):  # 最多分析6期
        title = ep.get('title', '无标题')
        podcast = ep.get('podcast', '')
        published = ep.get('published', '')[:16]
        summary = ep.get('summary', '')
        link = ep.get('link', '')
        
        report += f"""## {i}. {title}

**播客**: {podcast} | **时间**: {published}

"""
    
    report += """
---

## 📌 使用说明

以上是对本期播客更新的基础信息整理。如需深度分析某一期内容，请告诉我具体想了解哪一期，我可以针对该期进行深入解读。

**订阅的播客**：
- Lex Fridman Podcast - 深度技术访谈
- All-In Podcast - 硅谷投资视角
- Latent Space - AI工程实践
- Lenny's Broadcast - 产品增长与创业
"""
    
    # 保存报告
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"分析报告已生成: {REPORT_PATH}")
    return report

if __name__ == "__main__":
    main()
