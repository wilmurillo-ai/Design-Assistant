#!/usr/bin/env python3
"""
微信公众号草稿创建脚本
Usage: python3 create_draft.py "<标题>" "<正文HTML>"
正文HTML中的占位符会被替换:
  COVERIMG_URL -> 封面微信URL
  CHAPIMG1_URL ~ CHAPIMG6_URL -> 章节微信URL
"""
import sys, os, json, urllib.request, urllib.parse, shutil, re

APPID = 'wx89c939070fc20789'
APPSECRET = '6cb9a52250e39cb52bc61d9f5b520066'
UPLOAD_IMG_URL = 'https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}'
ADD_MATERIAL_URL = 'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
DRAFT_URL = 'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}'

def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'
    with urllib.request.urlopen(url, timeout=10) as r:
        d = json.loads(r.read())
    if d.get('errcode'):
        raise Exception(f'token失败: {d}')
    return d['access_token']

def upload_img_file(token, filepath):
    """uploadimg: 上传图片，返回永久URL (mmbiz.qpic.cn)"""
    if not os.path.exists(filepath):
        raise Exception(f'文件不存在: {filepath}')
    boundary = '----FormBoundary7MA4YWxkTrZu0gW'
    with open(filepath, 'rb') as f:
        fd = f.read()
    fname = os.path.basename(filepath)
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{fname}"\r\nContent-Type: image/png\r\n\r\n'
    ).encode() + fd + f'\r\n--{boundary}--\r\n'.encode()
    req = urllib.request.Request(
        UPLOAD_IMG_URL.format(token=token), data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}, method='POST'
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read())
    if result.get('errcode'):
        raise Exception(f'uploadimg失败: {result}')
    return result['url']

def upload_material(token, filepath):
    """add_material: 上传永久素材，返回media_id（字段名必须用'media'）"""
    if not os.path.exists(filepath):
        raise Exception(f'文件不存在: {filepath}')
    boundary = '----FormBoundary7MA4YWxkTrZu0gW'
    with open(filepath, 'rb') as f:
        fd = f.read()
    fname = os.path.basename(filepath)
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="media"; filename="{fname}"\r\nContent-Type: image/png\r\n\r\n'
    ).encode() + fd + f'\r\n--{boundary}--\r\n'.encode()
    req = urllib.request.Request(
        ADD_MATERIAL_URL.format(token=token), data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}, method='POST'
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read())
    if result.get('errcode'):
        raise Exception(f'add_material失败: {result}')
    return result['media_id']

def create_draft(token, title, html_content, thumb_media_id):
    payload = {
        'articles': [{
            'title': title,
            'author': 'jimo',
            'digest': '',
            'content': html_content,
            'content_source_url': '',
            'thumb_media_id': thumb_media_id,
            'need_open_comment': 0,
            'only_fans_can_comment': 0
        }]
    }
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        DRAFT_URL.format(token=token), data=data,
        headers={'Content-Type': 'application/json'}, method='POST'
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def clean_title_from_body(html, title):
    """去除正文中的标题重复：去掉<title>标签，去掉body开头重复的h1/p标题"""
    # 去掉<title>xxx</title>
    html = re.sub(r'<title>[^<]*</title>', '', html, flags=re.IGNORECASE)
    if not title:
        return html
    # 去掉纯文本标题（AI直接写在body开头的）
    t = title.strip()
    # 去掉<h1>xxx</h1>或<h2>xxx</h2>（全文范围内，包含样式的）
    html = re.sub(r'<h[12][^>]*>' + re.escape(t) + r'</h[12]>', '', html, flags=re.IGNORECASE)
    # 去掉<p>纯标题文本</p>
    html = re.sub(r'<p[^>]*>' + re.escape(t) + r'</p>', '', html, flags=re.IGNORECASE)
    return html

def beautify_html(html):
    """给HTML内容添加专业排版样式并重构内容结构，增加视觉层次"""
    css = """
    <style>
    body, section {
        font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif !important;
        font-size: 17px !important;
        line-height: 2 !important;
        letter-spacing: 0.3px !important;
        color: #3a3a3a !important;
    }
    p {
        margin: 14px 0 !important;
        line-height: 2 !important;
        text-align: justify !important;
    }
    p:last-of-type { margin-bottom: 20px !important; }
    h2 {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #fff !important;
        background: linear-gradient(135deg, #e07b2a 0%, #c96a1a 100%) !important;
        padding: 12px 16px !important;
        margin: 32px 0 16px !important;
        border-radius: 10px !important;
        line-height: 1.4 !important;
        box-shadow: 0 3px 10px rgba(224,123,42,0.25) !important;
        letter-spacing: 0.5px !important;
    }
    h3 {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #e07b2a !important;
        background: linear-gradient(to right, #fff8f0, #fffaf5) !important;
        padding: 10px 14px !important;
        margin: 24px 0 12px !important;
        border-left: 5px solid #e07b2a !important;
        border-radius: 0 8px 8px 0 !important;
        line-height: 1.5 !important;
        box-shadow: 0 2px 8px rgba(224,123,42,0.1) !important;
    }
    strong, b {
        font-weight: 700 !important;
        color: #d44a0a !important;
        background: linear-gradient(transparent 60%, #ffe0b2 60%) !important;
        padding: 0 2px !important;
    }
    em, i {
        font-style: normal !important;
        color: #888 !important;
    }
    img {
        max-width: 100% !important;
        height: auto !important;
        display: block !important;
        margin: 18px auto !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1) !important;
    }
    ul {
        padding-left: 20px !important;
        margin: 12px 0 !important;
    }
    ul li {
        margin: 8px 0 !important;
        line-height: 1.9 !important;
        list-style: none !important;
        padding-left: 20px !important;
        position: relative !important;
    }
    ul li::before {
        content: "👉 " !important;
        position: absolute !important;
        left: 0 !important;
    }
    ol {
        padding-left: 24px !important;
        margin: 12px 0 !important;
    }
    ol li {
        margin: 8px 0 !important;
        line-height: 1.9 !important;
        font-weight: 500 !important;
    }
    blockquote {
        border-left: 5px solid #4caf50 !important;
        background: #f6ffed !important;
        padding: 14px 18px !important;
        margin: 18px 0 !important;
        border-radius: 0 10px 10px 0 !important;
        color: #555 !important;
        font-size: 16px !important;
        line-height: 1.9 !important;
    }
    blockquote strong { color: #2e7d32 !important; background: none !important; }
    hr {
        border: none !important;
        text-align: center !important;
        margin: 28px 0 !important;
        color: #ccc !important;
        font-size: 14px !important;
        letter-spacing: 8px !important;
    }
    </style>
    """
    if '<style>' in html or '<style ' in html:
        html = re.sub(r'(</style>)', css + '\n</style>', html, count=1)
        return html
    html = restructure_content(html)
    html = highlight_content(html)
    html = convert_lists(html)
    if '<head>' in html:
        html = html.replace('<head>', '<head>' + css)
    else:
        html = css + html
    return html


def restructure_content(html):
    """将连续长段落拆分成带结构的小节，增加小标题"""
    def make_subheading(m):
        p_content = m.group(1)
        text = re.sub(r'<[^>]+>', '', p_content).strip()
        if len(text) < 60:
            return m.group(0)
        if re.search(r'[一二三四五六七八九十][.、]|[0-9]+[.、]', text) or re.search(r'[必吃|必去|推荐|攻略|打卡|收藏]', text):
            short_title = text[:20].strip()
            if len(text) > 50:
                return f'<h3>{short_title}</h3><p>{p_content.strip()}</p>'
        lead_words = ['美食推荐', '必吃清单', '景点攻略', '交通指南', '住宿推荐', '实用信息', '注意事项', '亮点', '特色']
        for w in lead_words:
            if text.startswith(w) and len(text) > 40:
                return f'<h3>{text[:20]}</h3><p>{p_content.strip()}</p>'
        return m.group(0)
    result = re.sub(r'(<p[^>]*>.*?</p>)', make_subheading, html, flags=re.DOTALL)
    return result


def highlight_content(html):
    """给关键信息加粗高亮：数字、感受词"""
    # 数字+量词
    html = re.sub(
        r'([0-9]+[多个几半]+[^\s\.,;!?]{0,5}|[0-9]+[\.。][0-9]+[^\s\.,;!?]{0,3}|[一二三四五六七八九十百千万]+[天个人家店种道条公里米层座个口])',
        r'<strong>\1</strong>', html
    )
    # 感受词
    for word in ['好吃到哭', '绝绝子', '太香了', '爆火', '出片', '宝藏', 'yyds', '封神', '天花板', '绝了', '无敌', '超级赞', '强烈推荐', '必去', '必吃', '值得', '私藏', '隐藏', '小众', '美到窒息']:
        html = html.replace(word, f'<strong>{word}</strong>')
    return html


def convert_lists(html):
    """将纯文本列表转换成带图标的<ul>列表"""
    def make_list(m):
        prefix = m.group(1)
        items_text = m.group(2)
        items = re.split(r'[、，,]\s*', items_text)
        items = [it.strip() for it in items if it.strip() and len(it) > 1]
        clean_items = [f'<li>{it}</li>' for it in items if not re.match(r'^<[^>]+>', it)]
        if len(clean_items) >= 2:
            return f'{prefix}<ul>{"".join(clean_items)}</ul>'
        return m.group(0)
    html = re.sub(
        r'^([\s\n]*[<p>]*)([\d一二三四五六七八九十]+[.、)）][^<\n]{10,}(?:[、，,][^<\n]{5,}){2,})',
        make_list, html, flags=re.MULTILINE
    )
    return html


def inject_emoji(html):
    """自动给HTML段落注入emoji关键词"""
    emoji_map = [
        ('美食', '🍜'), ('小吃', '🥟'), ('甜品', '🍰'), ('火锅', '🍲'),
        ('烧烤', '🍖'), ('烤肉', '🥩'), ('海鲜', '🦐'), ('寿司', '🍣'),
        ('咖啡', '☕'), ('奶茶', '🧋'), ('面包', '🥖'),
        ('蔬菜', '🥦'), ('沙拉', '🥗'), ('素菜', '🥬'),
        ('肉', '🥩'), ('鸡', '🍗'), ('鱼', '🐟'), ('蛋', '🥚'),
        ('旅行', '🧳'), ('旅游', '🗺️'), ('景点', '🏞️'), ('攻略', '📝'),
        ('打卡', '📍'), ('拍照', '📸'), ('酒店', '🏨'), ('民宿', '🏠'),
        ('出行', '✈️'), ('航班', '🛫'), ('火车', '🚄'), ('自驾', '🚗'),
        ('春天', '🌸'), ('樱花', '🌸'), ('桃花', '🌸'), ('油菜花', '🌼'),
        ('日出', '🌅'), ('日落', '🌇'), ('星空', '🌌'), ('海边', '🏖️'),
        ('雪山', '🏔️'), ('森林', '🌲'), ('草原', '🌿'),
        ('健康', '💪'), ('养生', '🌿'),
        ('推荐', '✅'), ('必吃', '🔥'), ('人气', '🔥'), ('热门', '🔥'),
        ('避坑', '⚠️'), ('注意', '❗'), ('提醒', '🔔'),
        ('实用', '💡'), ('技巧', '💡'), ('指南', '📖'),
        ('好处', '👍'), ('特色', '✨'),
        ('城市', '🏙️'), ('乡村', '🏡'), ('古镇', '🏘️'),
        ('文化', '🎎'), ('历史', '📜'), ('传统', '🏮'),
        ('活动', '🎉'), ('节日', '🎊'),
        ('广州', '🏙️'), ('广交会', '🏛️'),
        ('茶', '🍵'), ('早茶', '🍵'), ('点心', '🥮'),
    ]
    emoji_chars = set(e for _, e in emoji_map)
    
    def add_emoji(line):
        # 如果已有emoji不重复加
        if any(c in line for c in emoji_chars):
            return line
        for kw, emo in emoji_map:
            if kw in line:
                # 在段落/标题/列表标签的内容前面加emoji
                m = re.match(r'(<(?:p|h[1-6]|li)[^>]*>)(.*)', line)
                if m:
                    return m.group(1) + emo + ' ' + m.group(2)
                break
        return line
    
    # 把HTML分成标签和文本块，只对块级元素内的文本加emoji
    result = []
    i = 0
    while i < len(html):
        if html[i:i+2] == '</':
            # 结束标签
            m = re.match(r'</([a-zA-Z]+)>', html[i:])
            if m:
                result.append(html[i:i+len(m.group(0))])
                i += len(m.group(0))
                continue
        elif html[i] == '<':
            # 开始标签或自闭合
            m = re.match(r'<[a-zA-Z][^>]*/?>', html[i:])
            if m:
                result.append(html[i:i+len(m.group(0))])
                i += len(m.group(0))
                continue
        else:
            # 文本节点：找到下一个标签的位置
            next_tag = html.find('<', i)
            if next_tag == -1:
                text = html[i:]
                i = len(html)
            else:
                text = html[i:next_tag]
                i = next_tag
            if text.strip():
                # 检查文本中是否有关键词
                for kw, emo in emoji_map:
                    if kw in text:
                        emoji_added = False
                        for kk, ee in emoji_map:
                            if ee in text:
                                text = text.replace(kk, '').strip()
                                text = ee + ' ' + text
                                emoji_added = True
                        if not emoji_added:
                            text = emo + ' ' + text.strip()
                        break
            if text:
                result.append(text)
    return ''.join(result)

def main():
    if len(sys.argv) < 3:
        print('用法: python3 create_draft.py "<标题>" "<HTML文件路径>"')
        sys.exit(1)

    title = sys.argv[1]
    html_arg = sys.argv[2]
    
    # 如果第二个参数是文件路径，读取文件；否则当作HTML内容直接使用
    if os.path.exists(html_arg):
        with open(html_arg, encoding='utf-8') as f:
            html_content = f.read()
        print(f'从文件读取HTML: {html_arg}')
    else:
        html_content = html_arg
        print(f'直接使用HTML内容 (长度: {len(html_content)})')

    print(f'标题: {title}')
    print(f'获取 access_token...')
    token = get_access_token()
    print(f'✅ token获取成功\n')

    # 找所有本地图片路径
    # 从HTML中提取所有本地文件路径（/tmp/xxx.png）
    img_paths = []
    for m in set(re.findall(r'/tmp/[\w\-]+\.png', html_content)):
        if os.path.exists(m):
            img_paths.append(m)
            print(f'  找到图片: {m}')

    if not img_paths:
        print('HTML中未找到本地图片路径（如 /tmp/xxx.png）')
        print('请先生成图片并把路径写入HTML')
        sys.exit(1)

    print(f'\n上传 {len(img_paths)} 张图片...')

    # 上传每张图片并建立本地路径->URL的映射
    path_to_url = {}
    for path in img_paths:
        url = upload_img_file(token, path)
        fname = os.path.basename(path)
        print(f'  {fname} -> {url[:60]}')
        path_to_url[path] = url

    # 替换HTML中的所有本地图片路径为上传后的URL
    for local_path, url in path_to_url.items():
        if local_path in html_content:
            html_content = html_content.replace(local_path, url)
            print(f'  替换本地路径 {os.path.basename(local_path)} -> {url[:40]}...')

    # 兼容旧的占位符格式（COVERIMG_URL / CHAPIMG1_URL）
    for placeholder, url in path_to_url.items():
        fname = os.path.basename(placeholder)
        if 'cover' in fname.lower():
            ph = 'COVERIMG_URL'
        else:
            m = re.search(r'chap(\d+)', fname.lower())
            ph = f'CHAPIMG{m.group(1)}_URL' if m else None
        if ph and ph in html_content:
            html_content = html_content.replace(ph, path_to_url[placeholder])
            print(f'  替换占位符 {ph} -> {path_to_url[placeholder][:40]}...')

    # 上传封面作为永久素材（thumb_media_id）
    cover_path = [p for p in img_paths if 'cover' in p.lower()]
    if cover_path:
        print(f'\n上传封面为永久素材...')
        thumb_media_id = upload_material(token, cover_path[0])
        print(f'  thumb_media_id: {thumb_media_id}')
    else:
        thumb_media_id = path_to_url.get(img_paths[0], '')

    # 去除正文中的标题重复
    print('\n清理标题重复...')
    html_content = clean_title_from_body(html_content, title)
    print('  标题重复已清理')

    # 自动注入emoji
    print('\n注入emoji...')
    html_content = inject_emoji(html_content)
    print('  emoji注入完成')

    # 排版美化
    print('\n排版美化...')
    html_content = beautify_html(html_content)
    print('  排版完成（字体17px、行高1.9、字间距0.5px、两端对齐）')

    # 创建草稿
    print('\n创建草稿...')
    result = create_draft(token, title, html_content, thumb_media_id)

    # 成功判断：无errcode字段 或 errcode==0
    if 'errcode' not in result or result.get('errcode') == 0:
        print(f"✅ 草稿创建成功!")
        print(f"media_id: {result.get('media_id', 'N/A')}")
    else:
        print(f"❌ 草稿创建失败: {result}")
        sys.exit(1)

if __name__ == '__main__':
    import re
    main()
