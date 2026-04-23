#!/usr/bin/env python3
"""
添加待办事项脚本
支持文字和图片两种输入模式，通过 OpenClaw Gateway 调用 AI 解析。
用法：
  python todo_add.py --text "待办内容"
  python todo_add.py --image /path/to/image.jpg

环境变量（自动从 OpenClaw 配置读取）：
  OPENCLAW_GATEWAY_TOKEN  - Gateway 认证 token
"""

import os
import sys
import json
import uuid
import base64
import re
from datetime import datetime


def get_gateway_config():
    """从 openclaw.json 读取 gateway 配置"""
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        with open(config_path, 'rb') as f:
            content = f.read()
        # 提取 token（配置文件中的 token 字段）
        match = re.search(rb'"token":\s*"([^"]+)"', content)
        token = match.group(1).decode() if match else None
        # 提取 port
        port_match = re.search(rb'"port":\s*(\d+)', content)
        port = int(port_match.group(1)) if port_match else 18789
        return token, port
    except Exception as e:
        print(f"读取 OpenClaw 配置失败: {e}")
        return None, 18789


def load_todos():
    """加载 todos.json"""
    todo_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'todos.json')
    try:
        with open(todo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_todos(todos):
    """保存 todos.json"""
    todo_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'todos.json')
    with open(todo_file, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def call_gateway_chat(model, messages, max_tokens=500):
    """通过 OpenClaw Gateway 调用 AI"""
    token, port = get_gateway_config()
    if not token:
        print("错误: 无法获取 Gateway token")
        sys.exit(1)

    import urllib.request
    import urllib.error

    url = f"http://127.0.0.1:{port}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        print(f"Gateway API 错误: {e.code} - {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"调用 Gateway 失败: {e}")
        sys.exit(1)


def parse_text_with_ai(text):
    """使用 AI 解析文字内容，提取任务"""
    model = os.environ.get("MODEL_NAME", "MiniMax-M2.7-highspeed")
    messages = [
        {"role": "user", "content": f"请解析以下待办事项，提取核心任务内容（简洁明了，10-50字）：{text}"}
    ]
    return call_gateway_chat(model, messages, max_tokens=200)


def parse_image_with_ai(image_path):
    """使用 AI 视觉理解解析图片中的待办"""
    model = os.environ.get("MODEL_NAME", "MiniMax-M2.7-highspeed")

    # 将图片转为 base64 data URL
    try:
        with open(image_path, "rb") as img_file:
            base64_data = base64.b64encode(img_file.read()).decode('utf-8')
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(ext, 'image/jpeg')
            image_url = f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        print(f"读取图片失败: {e}")
        sys.exit(1)

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                },
                {
                    "type": "text",
                    "text": "请提取图片中的所有待办事项，每条给出：任务内容。如无法提取，请说明。"
                }
            ]
        }
    ]
    return call_gateway_chat(model, messages, max_tokens=500)


def add_todo(content, mode="text", image_description=None):
    """添加新的待办事项"""
    todos = load_todos()

    new_todo = {
        "id": str(uuid.uuid4())[:8],
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "mode": mode
    }

    if mode == "image" and image_description:
        new_todo["image_description"] = image_description

    todos.append(new_todo)
    save_todos(todos)

    print(f"✅ 待办已添加 (ID: {new_todo['id']})")
    print(f"   内容: {content}")
    print(f"   时间: {new_todo['created_at']}")
    return new_todo


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python todo_add.py --text '待办内容'")
        print("  python todo_add.py --image /path/to/image.jpg")
        sys.exit(1)

    if sys.argv[1] == "--text":
        if len(sys.argv) < 3:
            print("错误: 请提供待办内容")
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        parsed = parse_text_with_ai(text)
        add_todo(parsed, mode="text")

    elif sys.argv[1] == "--image":
        if len(sys.argv) < 3:
            print("错误: 请提供图片路径")
            sys.exit(1)
        image_path = sys.argv[2]
        parsed = parse_image_with_ai(image_path)
        add_todo(parsed, mode="image", image_description=f"原图路径: {image_path}")

    else:
        print("错误: 必须是 --text 或 --image 参数")
        sys.exit(1)


if __name__ == "__main__":
    main()
