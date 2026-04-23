#!/usr/bin/env python3
"""
飞书卡片审核工具
将笔记内容渲染为飞书卡片发送给用户审核

用法:
    python3 send_review_card.py \
        --title "标题" \
        --desc "正文" \
        --images card1.jpg card2.jpg card3.jpg \
        --chat_id oc_xxx
"""
import argparse, os, json, urllib.request

def get_token():
    env = open('/root/.openclaw/workspace/.env').read()
    app_id = app_secret = None
    for line in env.split('\n'):
        if line.startswith('FEISHU_APP_ID'): app_id = line.split('=',1)[1].strip()
        elif line.startswith('FEISHU_APP_SECRET'): app_secret = line.split('=',1)[1].strip()

    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data, headers={"Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req, timeout=10).read()).get('tenant_access_token', '')


def upload_image(token, image_path):
    import requests
    with open(image_path, 'rb') as f:
        r = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/images",
            headers={"Authorization": f"Bearer {token}"},
            files={"image_type": (None, "message"), "image": (os.path.basename(image_path), f, "image/jpeg")},
            timeout=15
        )
    return json.loads(r.text).get('data', {}).get('image_key', '')


def send_card(token, chat_id, title, desc, image_keys):
    """发送审核卡片"""
    import requests

    # 构建卡片图片元素
    img_elements = []
    for k in image_keys:
        img_elements.append({
            "tag": "img",
            "img_key": k,
            "alt": {"tag": "plain_text", "content": "配图"}
        })
        img_elements.append({"tag": "hr"})

    payload = {
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps({
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"🍠 {title}"},
                "template": "purple"
            },
            "elements": img_elements + [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**正文预览：**\n\n{desc[:500]}"}},
                {"tag": "hr"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "📌 回复「通过」→ 私密发布 · 回复「修改」→ 我来调整"}]}
            ]
        })
    }

    r = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload, timeout=15
    )
    return json.loads(r.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', required=True)
    parser.add_argument('--desc', required=True)
    parser.add_argument('--images', nargs='+', required=True)
    parser.add_argument('--chat_id', required=True)
    args = parser.parse_args()

    token = get_token()
    print("上传图片...")
    keys = [upload_image(token, img) for img in args.images]
    print(f"图片keys: {keys}")

    result = send_card(token, args.chat_id, args.title, args.desc, keys)
    if result.get('code') == 0:
        msg_id = result.get('data', {}).get('message_id', '')
        print(f"✅ 审核卡片已发送: {msg_id}")
    else:
        print(f"❌ 发送失败: {result}")
