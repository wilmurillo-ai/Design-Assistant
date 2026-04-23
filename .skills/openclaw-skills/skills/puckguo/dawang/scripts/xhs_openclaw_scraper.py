#!/usr/bin/env python3
"""
小红书 OpenClaw 龙虾北京活动爬虫 V2
访问每个笔记详情页获取完整活动信息：时间、地点、主办方等
"""

import json
import re
import sys
import os
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# 配置
CHROME_DEBUG_PORT = 18800
FEISHU_DOC_TOKEN = "XgKqdoo0AoXiCrxdHeqcwasnnae"
DATA_FILE = os.path.expanduser("~/.openclaw/workspaces/dawang/scripts/xhs_openclaw_data.json")
LOG_FILE = os.path.expanduser("~/.openclaw/workspaces/dawang/scripts/xhs_scraper.log")


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")


def find_xhs_search_page(browser):
    """找到小红书搜索页面"""
    for ctx in browser.contexts:
        for page in ctx.pages:
            url = page.url
            if 'search_result' in url and 'openclaw' in url.lower():
                return page
    return None


def extract_notes_basic(page):
    """从搜索页面提取笔记基础信息"""
    try:
        page.wait_for_selector('.search-layout', timeout=15000)
        time.sleep(0.5)
        
        result = page.evaluate("""
            () => {
                const results = [];
                const seenUrls = new Set();
                const searchLayout = document.querySelector('.search-layout');
                if (!searchLayout) return { notes: [], count: 0 };
                
                const allLinks = searchLayout.querySelectorAll('a[href]');
                allLinks.forEach(a => {
                    const href = a.href;
                    if (href.includes('/search_result/') && !seenUrls.has(href)) {
                        seenUrls.add(href);
                        const parent = a.closest('div');
                        const grandParent = parent ? parent.parentElement : null;
                        const contextText = grandParent ? grandParent.innerText : '';
                        const lines = contextText.split('\\n').filter(l => l.trim());
                        
                        results.push({
                            url: href,
                            context: lines.slice(0, 6).join(' | ')
                        });
                    }
                });
                
                return { notes: results, count: results.length };
            }
        """)
        return result.get('notes', [])
    except Exception as e:
        log(f"提取失败: {e}")
        return []


def extract_note_detail(ctx, url):
    """访问笔记详情页，提取完整内容"""
    try:
        note_page = ctx.new_page()
        note_page.goto(url, timeout=20000)
        time.sleep(3)  # 等待页面加载
        
        # 获取页面内容 - 提取笔记正文部分
        content = note_page.evaluate("""
            () => {
                // 尝试多种方式找到笔记正文
                let noteContent = '';
                
                // 方法1: 查找 note-content 类
                const nc1 = document.querySelector('.note-content');
                if (nc1) noteContent = nc1.innerText;
                
                // 方法2: 查找包含作者信息的容器
                const authorEl = document.querySelector('.author-info, .user-info, [class*="author"]');
                if (authorEl && !noteContent) {
                    const parent = authorEl.closest('div[class*="note"], div[class*="content"]');
                    if (parent) noteContent = parent.innerText;
                }
                
                // 方法3: 查找主内容区域 (排除底部导航和页脚)
                if (!noteContent) {
                    const mainAreas = document.querySelectorAll('main, article, .main, #main');
                    for (let area of mainAreas) {
                        const text = area.innerText;
                        if (text.length > 100 && text.length < 10000) {
                            noteContent = text;
                            break;
                        }
                    }
                }
                
                // 方法4: 查找包含特定关键词的区域
                if (!noteContent) {
                    const keywords = ['openclaw', '龙虾', '活动', '比赛', 'meetup', '线下'];
                    const allDivs = document.querySelectorAll('div');
                    for (let div of allDivs) {
                        const text = div.innerText.toLowerCase();
                        if (keywords.some(k => text.includes(k)) && div.innerText.length > 200) {
                            noteContent = div.innerText;
                            break;
                        }
                    }
                }
                
                // 最终方法: 获取 body 文本并排除已知的导航/页脚
                if (!noteContent) {
                    const body = document.body.innerText;
                    // 移除常见的页眉页脚内容
                    const lines = body.split('\\n');
                    const filtered = lines.filter(line => {
                        const l = line.trim();
                        return !l.includes('沪ICP备') && 
                               !l.includes('营业执照') &&
                               !l.includes('创作中心') &&
                               !l.includes('发现') && 
                               !l.includes('直播') &&
                               !l.includes('发布') &&
                               !l.includes('通知') &&
                               l.length > 5;
                    });
                    noteContent = filtered.join('\\n');
                }
                
                return {
                    title: document.title.replace(' - 小红书', '').trim(),
                    fullText: noteContent.substring(0, 8000)
                };
            }
        """)
        
        note_page.close()
        return content
        
    except Exception as e:
        log(f"获取详情失败 {url[:50]}: {e}")
        return {'title': '', 'fullText': ''}


def parse_relative_date(date_str):
    """解析相对日期"""
    today = datetime.now()
    if "天前" in date_str or "日前" in date_str:
        match = re.search(r'(\d+)', date_str)
        if match:
            return today - timedelta(days=int(match.group(1)))
    elif "昨天" in date_str:
        return today - timedelta(days=1)
    elif "今天" in date_str or "今日" in date_str:
        return today
    elif "小时前" in date_str or "分钟前" in date_str:
        return today
    return None


def parse_absolute_date(date_str):
    """解析绝对日期格式如 03-16"""
    try:
        if re.match(r'\d{2}-\d{2}', date_str):
            month, day = map(int, date_str.split('-'))
            return datetime(datetime.now().year, month, day)
    except:
        pass
    return None


def is_recent(date_str):
    """判断日期是否为今天或昨天"""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    rel_date = parse_relative_date(date_str)
    if rel_date:
        return rel_date.date() in [today, yesterday]
    
    abs_date = parse_absolute_date(date_str)
    if abs_date:
        return abs_date.date() in [today, yesterday]
    
    return True


def parse_time_location(text):
    """从文本中提取时间和地点"""
    result = {'time': '', 'location': '', 'organizer': ''}
    
    # 清理文本 - 移除 ICP 备案等无关内容
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if (not l.startswith('沪ICP备') and 
            not l.startswith('营业执照') and
            not l.startswith('2024沪公网安备') and
            not l.startswith('增值电信业务') and
            not l.startswith('违法不良信息') and
            not l.startswith('上海市互联网举报') and
            not l.startswith('网上有害信息') and
            not l.startswith('网络文化经营') and
            not l.startswith('行吟信息科技') and
            not l.startswith('©') and
            not l.startswith('内容可能使用AI') and
            not l.startswith('可以添加到收藏') and
            not l.startswith('共 ') and
            not l.startswith('说点什么') and
            not l.startswith('发送') and
            not l.startswith('取消') and
            not l.startswith('展开 ') and
            not l.startswith('回复') and
            not l.startswith('赞') and
            not l.startswith('收藏') and
            not '小南园' not in l and  # 这是一个评论者
            len(l) > 2):
            cleaned_lines.append(l)
    
    cleaned_text = ' '.join(cleaned_lines)
    
    # 提取地点关键词 - 更精确的模式
    location_patterns = [
        r'((?:北京|上海|深圳|广州|杭州|成都|武汉|南京|西安|苏州)[^\s,，。（】]{0,30})',
        r'地址[：:]\s*([^\n]{0,50})',
        r'地点[：:]\s*([^\n]{0,50})',
        r'在\s*([^\s,，。（】]{2,30}(?:大厦|园区|中心|学院|大学|酒店|咖啡厅|办公室|空间|基地|孵化器))[^\s,。]',
        r'([^\s]{0,10}(?:中关村|望京|国贸|三里屯|五道口|清华|北大)[^\s,。]{0,20})',
        r'([^\n]{0,30}(?:学院|大学|研究院|研究所|实验室)[^\n]{0,10})',
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            loc = match.group(1).strip()
            # 过滤掉太短的或包含特殊字符的
            if len(loc) > 3 and not loc.startswith('http'):
                result['location'] = loc
                break
    
    # 提取时间
    time_patterns = [
        r'(\d{1,2}[月年\-/]\d{1,2}[日号]?\s*(?:下午|上午|晚上)?\s*\d{1,2}[:：]\d{1,2})',
        r'(\d{1,2}月\d{1,2}日[^\n]{0,30})',
        r'(?:周[一二三四五六日]|今天|明天|后天)[^\n]{0,15}',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            result['time'] = match.group(0).strip()[:50]
            break
    
    # 提取主办方
    organizer_patterns = [
        r'主办[：:]\s*([^\n]{0,30})',
        r'组织[：:]\s*([^\n]{0,30})',
        r'举办方[：:]\s*([^\n]{0,30})',
        r'([^\s]{2,20})(?:主办|组织|举办|联合举办)',
    ]
    
    for pattern in organizer_patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            result['organizer'] = match.group(1).strip()
            break
    
    return result


def parse_search_context(context):
    """解析搜索结果中的上下文"""
    parts = context.split(' | ')
    cleaned = [p.strip() for p in parts if p.strip()]
    
    if len(cleaned) >= 3:
        title = cleaned[0]
        second = cleaned[1]
        
        # 检查 second 是否是日期
        if any(x in second for x in ['天前', '日前', '昨天', '今天', '分钟']) or re.match(r'\d{2}-\d{2}', second):
            # 格式: 标题 | 日期 | 点赞 | 作者
            return {
                'title': title,
                'author': cleaned[3] if len(cleaned) > 3 and not cleaned_parts[3].isdigit() else '',
                'date': second,
                'likes': cleaned[2] if cleaned[2].isdigit() else ''
            }
        else:
            # 格式: 标题 | 作者 | 日期 | 点赞
            return {
                'title': title,
                'author': second,
                'date': cleaned[2] if len(cleaned) > 2 else '',
                'likes': cleaned[3] if len(cleaned) > 3 and cleaned[3].isdigit() else ''
            }
    
    return {'title': '', 'author': '', 'date': '', 'likes': ''}


def filter_recent_notes(notes_data):
    """过滤并解析最近的活动笔记"""
    recent = []
    
    for note in notes_data:
        context = note.get('context', '')
        parsed = parse_search_context(context)
        
        if is_recent(parsed.get('date', '')):
            url = note.get('url', '')
            match = re.search(r'/search_result/([a-f0-9]+)', url)
            note_id = match.group(1) if match else ''
            
            recent.append({
                'note_id': note_id,
                'title': parsed['title'],
                'author': parsed['author'],
                'date': parsed['date'],
                'likes': parsed['likes'],
                'url': url
            })
    
    return recent


def generate_feishu_content(events, date_str):
    """生成飞书文档内容"""
    if not events:
        return f"""# OpenClaw 龙虾北京活动日报

> 自动更新于 {date_str} 晚上 7 点 | 数据来源：小红书搜索「openclaw 龙虾 北京活动」

---

## {date_str} 最新活动

暂无新的活动信息。

---

## 说明

- 本文档每天晚上 7 点自动更新
- 去重依据：小红书笔记 ID（唯一标识）
- 只展示当天和前一天发布的活动
- 点赞数反映活动热度
"""
    
    lines = [
        f"# OpenClaw 龙虾北京活动日报",
        "",
        f"> 自动更新于 {date_str} 晚上 7 点 | 数据来源：小红书搜索「openclaw 龙虾 北京活动」",
        "",
        "---",
        "",
        f"## {date_str} 最新活动",
        "",
        f"共 {len(events)} 个活动",
        "",
    ]
    
    for i, evt in enumerate(events, 1):
        lines.append(f"### {i}. {evt.get('title', '未知活动')}")
        lines.append("")
        
        if evt.get('author'):
            lines.append(f"- **作者:** {evt['author']}")
        if evt.get('date'):
            lines.append(f"- **发布日期:** {evt['date']}")
        if evt.get('time'):
            lines.append(f"- **活动时间:** {evt['time']}")
        if evt.get('location'):
            lines.append(f"- **活动地点:** {evt['location']}")
        if evt.get('organizer'):
            lines.append(f"- **主办方:** {evt['organizer']}")
        if evt.get('likes'):
            lines.append(f"- **点赞数:** {evt['likes']}")
        
        # 内容摘要
        content = evt.get('content', '')
        if content:
            # 截取前200字
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append("")
            lines.append(f"> {content}")
        
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## 说明",
        "",
        "- 本文档每天晚上 7 点自动更新",
        "- 去重依据：小红书笔记 ID（唯一标识）",
        "- 只展示当天和前一天发布的活动",
        "- 点赞数反映活动热度",
    ])
    
    return "\n".join(lines)


def load_data():
    """加载已有数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('notes', [])
    return []


def save_data(notes):
    """保存数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'last_update': datetime.now().isoformat(), 'notes': notes}, f, ensure_ascii=False, indent=2)


def main():
    log("=" * 50)
    log("小红书 OpenClaw 活动爬虫 V2 启动")
    log("=" * 50)
    
    try:
        with sync_playwright() as p:
            log("连接 Chrome...")
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CHROME_DEBUG_PORT}")
            
            # 找到搜索页面
            page = find_xhs_search_page(browser)
            if not page:
                log("未找到小红书搜索页面")
                sys.exit(1)
            
            log(f"找到搜索页面")
            
            # 提取搜索结果
            log("提取搜索结果...")
            notes_data = extract_notes_basic(page)
            log(f"找到 {len(notes_data)} 个搜索结果")
            
            if not notes_data:
                sys.exit(1)
            
            # 过滤最近的活动
            recent_notes = filter_recent_notes(notes_data)
            log(f"最近活动: {len(recent_notes)} 个")
            
            # 去重
            existing_notes = load_data()
            existing_ids = set(n['note_id'] for n in existing_notes if n.get('note_id'))
            new_notes = [n for n in recent_notes if n['note_id'] not in existing_ids]
            log(f"新增活动: {len(new_notes)} 个")
            
            # 获取每个新笔记的详情
            ctx = browser.contexts[0] if browser.contexts else None
            if not ctx:
                log("无法获取浏览器上下文")
                sys.exit(1)
            
            events = []
            for note in new_notes:
                log(f"获取详情: {note['title'][:30]}...")
                detail = extract_note_detail(ctx, note['url'])
                
                # 解析时间和地点
                parsed = parse_time_location(detail.get('fullText', ''))
                
                event = {
                    'note_id': note['note_id'],
                    'title': note['title'],
                    'author': note['author'],
                    'date': note['date'],
                    'likes': note['likes'],
                    'url': note['url'],
                    'content': detail.get('fullText', '')[:500],  # 保留前500字
                    'time': parsed['time'],
                    'location': parsed['location'],
                    'organizer': parsed['organizer']
                }
                events.append(event)
                
                # 避免请求过快
                time.sleep(1)
            
            # 合并
            all_events = existing_notes + events
            
            # 生成内容
            date_str = datetime.now().strftime("%Y-%m-%d")
            content = generate_feishu_content(all_events, date_str)
            
            # 保存
            save_data(all_events)
            
            # 输出
            output = {
                'success': True,
                'notes_count': len(all_events),
                'new_notes_count': len(events),
                'content': content,
                'has_new': len(events) > 0
            }
            
            output_file = os.path.join(os.path.dirname(DATA_FILE), 'xhs_openclaw_output.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print("XHS_SCRAPER_OUTPUT:")
            print(json.dumps(output, ensure_ascii=False))
            
            log(f"爬虫执行完成，新增 {len(events)} 个活动")
            
    except Exception as e:
        log(f"执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
