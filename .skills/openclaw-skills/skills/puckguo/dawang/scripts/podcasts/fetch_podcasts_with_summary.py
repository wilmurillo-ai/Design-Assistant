#!/usr/bin/env python3
"""
播客精选日报生成器 (含完整转录 + AI双语摘要)
支持: Lex Fridman, Lenny's Newsletter, Latent Space, All-In
"""
import subprocess, json, re, html
from datetime import datetime
import os

# ====== 配置 ======
AUTH_FILE = '/Users/godspeed/.openclaw/agents/dawang/agents/dawang/auth-profiles.json'
MINIMAX_URL = 'https://api.minimaxi.com/anthropic/v1/messages'

PODCASTS = {
    'Lex Fridman': {
        'rss': 'https://lexfridman.com/feed/podcast/',
        'transcript_url': 'https://lexfridman.com/{slug}-transcript',
    },
    "Lenny's Newsletter": {
        'rss': 'https://www.lennysnewsletter.com/feed/',
    },
    'Latent Space': {
        'rss': 'https://www.latent.space/feed',
    },
}

def get_minimax_key():
    with open(AUTH_FILE) as f:
        d = json.load(f)
    return d['profiles']['minimax:default']['key']

def call_minimax(prompt, max_tokens=2000):
    """调用 MiniMax M2.7 生成内容"""
    key = get_minimax_key()
    system_prompt = """你是一个专业的播客内容摘要助手。请为以下播客内容生成摘要：
1. 用中文和英文两种语言输出摘要
2. 根据内容长度智能调整摘要长度（短内容1-2段，长内容3-5段）
3. 摘要要涵盖：核心主题、关键观点、重要细节
4. 如果是技术内容，确保技术术语准确"""
    
    payload = {
        'model': 'MiniMax-M2.7',
        'system': system_prompt,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens
    }
    
    r = subprocess.run(
        ['curl', '-s', '--noproxy', '*', '-X', 'POST', MINIMAX_URL,
         '-H', 'Authorization: Bearer ' + key,
         '-H', 'Content-Type: application/json',
         '-H', 'anthropic-version: 2023-06-01',
         '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=60)
    
    try:
        data = json.loads(r.stdout)
        # MiniMax: content[0]=thinking, content[1]=text
        if 'content' in data:
            for c in data['content']:
                if c.get('type') == 'text':
                    return c['text']
        return f"API Error: {str(data)[:200]}"
    except:
        return f"Error: {r.stdout[:200]}"

def fetch_rss(url):
    """通过 curl 获取 RSS（绕过代理）"""
    r = subprocess.run(
        ['curl', '-s', '--noproxy', '*', '--compressed',
         '-L', '-m', '30', url],
        capture_output=True, text=True, timeout=40)
    return r.stdout

def extract_text_from_html(html_content):
    """从 HTML 提取纯净文本"""
    # 移除 script 和 style 标签
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', ' ', text)
    # 解码 HTML 实体
    text = html.unescape(text)
    # 清理空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_rss_items(xml_content):
    """解析 RSS XML，提取 items"""
    items = []
    # 匹配 item 块
    item_pattern = re.compile(r'<item>(.*?)</item>', re.DOTALL)
    for match in item_pattern.finditer(xml_content):
        item_xml = match.group(1)
        item = {}
        
        def get_field(tag):
            m = re.search(rf'<{tag}[^>]*>(.*?)</{tag}>', item_xml, re.DOTALL)
            return m.group(1).strip() if m else ''
        
        item['title'] = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', get_field('title'))
        item['link'] = get_field('link')
        item['pubDate'] = get_field('pubDate')
        
        # 提取 description / content
        desc = get_field('description') + ' ' + get_field('content:encoded')
        item['raw_content'] = desc
        item['text'] = extract_text_from_html(desc)[:2000]
        
        items.append(item)
    return items

def get_lex_transcript(slug):
    """获取 Lex Fridman 节目转录"""
    url = f'https://lexfridman.com/{slug}-transcript'
    r = subprocess.run(
        ['curl', '-s', '--noproxy', '*', '-L', '-m', '30', url],
        capture_output=True, text=True, timeout=40)
    
    content = r.stdout
    # 提取 ts-text 段落（Lex Fridman 特有的转录格式）
    texts = re.findall(r'<span class="ts-text">(.*?)</span>', content, re.DOTALL)
    
    transcript = []
    for t in texts:
        text = re.sub(r'<[^>]+>', '', t)
        text = html.unescape(text).strip()
        if text and len(text) > 20:
            transcript.append(text)
    
    return '\n'.join(transcript)[:15000]  # 限制长度

def format_podcast_entry(name, items, limit=3):
    """格式化单个播客的条目"""
    output = f"\n{'='*60}\n"
    output += f"📻 {name}\n"
    output += f"{'='*60}\n\n"
    
    for i, item in enumerate(items[:limit]):
        title = item.get('title', 'No Title')[:100]
        link = item.get('link', '')
        pub = item.get('pubDate', '')[:16]
        text = item.get('text', '')[:500]
        
        output += f"▶ Episode {i+1}: {title}\n"
        output += f"  🔗 {link}\n"
        output += f"  📅 {pub}\n"
        output += f"  📝 摘要: {text[:300]}...\n\n"
        
        # Lex Fridman: 获取转录
        if name == 'Lex Fridman' and link:
            slug = link.split('lexfridman.com/')[-1].rstrip('/')
            transcript = get_lex_transcript(slug)
            if transcript:
                output += f"  📄 转录 (节选):\n{transcript[:3000]}...\n"
        
        output += f"{'-'*40}\n\n"
    
    return output

def generate_summary(content):
    """使用 AI 生成摘要"""
    if len(content) < 200:
        return content
    
    prompt = f"""请为以下播客内容生成中英文双语摘要：

{content[:8000]}

请输出：
1. 一句话总结（中文）
2. 一句话总结（English）
3. 详细摘要（中英文）
"""
    return call_minimax(prompt, max_tokens=3000)

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 播客日报: {today}")
    
    all_entries = []
    report = f"""# 🎙️ 播客精选日报
**日期**: {today}

---
"""
    
    for name, config in PODCASTS.items():
        print(f"\n📡 获取 {name}...")
        try:
            rss_xml = fetch_rss(config['rss'])
            items = parse_rss_items(rss_xml)
            print(f"   找到 {len(items)} 条目")
            
            entry = format_podcast_entry(name, items, limit=2)
            report += entry
            
            if items:
                all_entries.append((name, items[0]))
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            report += f"\n{name}: 获取失败 ({e})\n"
    
    # 为最新条目生成 AI 摘要
    if all_entries:
        report += "\n" + "="*60 + "\n"
        report += "🤖 AI 双语摘要\n"
        report += "="*60 + "\n\n"
        
        for name, item in all_entries[:4]:
            print(f"\n🤖 生成 {name} 摘要...")
            content = item.get('text', '') or item.get('raw_content', '')[:5000]
            if not content:
                continue
            
            summary = generate_summary(content)
            report += f"### 📻 {name}: {item.get('title', '')[:80]}\n"
            report += f"{summary}\n\n"
            print(f"   ✅ 摘要生成完成")
    
    # 保存报告
    out_dir = os.path.expanduser('~/.openclaw/workspaces/dawang/scripts/podcasts')
    os.makedirs(out_dir, exist_ok=True)
    
    report_file = f'{out_dir}/report_{today}.md'
    with open(report_file, 'w') as f:
        f.write(report)
    
    latest = f'{out_dir}/latest_report.md'
    with open(latest, 'w') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存: {report_file}")
    return report_file

if __name__ == '__main__':
    main()
