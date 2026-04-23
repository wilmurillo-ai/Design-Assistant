#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书评论回复工具 - 交互式版本
支持：单篇笔记 / Notion批量 → 获取评论 → AI生成回复 → 审核后发送
特性：自动检测当前模型配置，支持多种 AI 模型，支持 Notion 批量处理
"""

import sys
import os
import json
import requests
import random
import re
from pathlib import Path
from datetime import datetime

# 配置
BASE_DIR = Path(__file__).parent
MCP_URL = "http://localhost:18060/mcp"
IDENTITY_FILE = BASE_DIR / "identity.json"
RULES_FILE = BASE_DIR / "reply_rules.json"
MODEL_CONFIG_FILE = BASE_DIR / ".model_config.json"
NOTION_CONFIG_FILE = BASE_DIR / ".notion_config.json"

# Notion API
NOTION_API_VERSION = "2022-06-28"
NOTION_API_BASE = "https://api.notion.com/v1"

# 支持的模型配置
SUPPORTED_MODELS = {
    "glm-4-flash": {
        "name": "GLM-4-Flash（智谱）",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "env_key": "GLM_API_KEY",
        "params": {"enable_thinking": False}
    },
    "glm-5": {
        "name": "GLM-5（智谱）",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "env_key": "GLM_API_KEY",
        "params": {"enable_thinking": False}
    },
    "doubao-pro-32k": {
        "name": "Doubao Pro（豆包）",
        "api_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "env_key": "DOUBAO_API_KEY",
        "params": {}
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini（OpenAI）",
        "api_url": "https://api.openai.com/v1/chat/completions",
        "env_key": "OPENAI_API_KEY",
        "params": {}
    },
    "deepseek-chat": {
        "name": "DeepSeek Chat",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "env_key": "DEEPSEEK_API_KEY",
        "params": {}
    }
}


# ============== 模型配置 ==============

def get_current_model_config():
    """获取当前 OpenClaw 使用的模型配置"""
    model = os.environ.get("OPENCLAW_MODEL", "")
    api_key = os.environ.get("OPENCLAW_API_KEY", "")
    api_url = os.environ.get("OPENCLAW_API_URL", "")
    
    if model and api_key:
        return {
            "model": model,
            "api_key": api_key,
            "api_url": api_url or "https://api.openai.com/v1/chat/completions",
            "params": {}
        }
    
    if MODEL_CONFIG_FILE.exists():
        try:
            with open(MODEL_CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    
    return None


def save_model_config(config):
    """保存模型配置"""
    with open(MODEL_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ 模型配置已保存到 {MODEL_CONFIG_FILE}")


def setup_model():
    """交互式配置模型"""
    print("\n" + "=" * 50)
    print("   🔧 模型配置")
    print("=" * 50)
    print("\n请选择要使用的 AI 模型：")
    
    models = list(SUPPORTED_MODELS.keys())
    for i, key in enumerate(models, 1):
        info = SUPPORTED_MODELS[key]
        print(f"  {i}. {info['name']}")
    
    print(f"  {len(models) + 1}. 自定义模型")
    
    choice = input("\n请输入序号：").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(models):
            model_key = models[idx]
            model_info = SUPPORTED_MODELS[model_key]
            
            print(f"\n已选择：{model_info['name']}")
            print(f"需要配置 API Key（环境变量：{model_info['env_key']}）")
            
            api_key = os.environ.get(model_info['env_key'], "")
            if api_key:
                print(f"✅ 检测到环境变量 {model_info['env_key']} 已设置")
                use_env = input("使用环境变量中的 Key？(y/n)：").strip().lower()
                if use_env != 'n':
                    config = {
                        "model": model_key,
                        "api_key": f"env:{model_info['env_key']}",
                        "api_url": model_info['api_url'],
                        "params": model_info.get('params', {})
                    }
                    save_model_config(config)
                    return config
            
            api_key = input(f"请输入 API Key：").strip()
            if api_key:
                config = {
                    "model": model_key,
                    "api_key": api_key,
                    "api_url": model_info['api_url'],
                    "params": model_info.get('params', {})
                }
                save_model_config(config)
                return config
        
        elif idx == len(models):
            print("\n配置自定义模型：")
            model = input("模型名称（如 gpt-4）：").strip()
            api_url = input("API URL：").strip()
            api_key = input("API Key：").strip()
            
            if model and api_url and api_key:
                config = {
                    "model": model,
                    "api_key": api_key,
                    "api_url": api_url,
                    "params": {}
                }
                save_model_config(config)
                return config
    except:
        pass
    
    print("❌ 配置失败")
    return None


def get_api_key(config):
    """获取实际的 API Key"""
    api_key = config.get("api_key", "")
    if api_key.startswith("env:"):
        env_name = api_key[4:]
        return os.environ.get(env_name, "")
    return api_key


def call_ai(prompt, config):
    """调用 AI 模型"""
    model = config.get("model", "")
    api_url = config.get("api_url", "")
    api_key = get_api_key(config)
    params = config.get("params", {})
    
    if not api_key:
        return None, "API Key 未配置"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}]
    }
    data.update(params)
    
    try:
        resp = requests.post(api_url, headers=headers, json=data, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content, None
        else:
            return None, f"API 错误：{resp.status_code}"
    except Exception as e:
        return None, str(e)


# ============== Notion 配置 ==============

def get_notion_config():
    """获取 Notion 配置"""
    if NOTION_CONFIG_FILE.exists():
        try:
            with open(NOTION_CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return None


def save_notion_config(config):
    """保存 Notion 配置"""
    with open(NOTION_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Notion 配置已保存到 {NOTION_CONFIG_FILE}")


def setup_notion():
    """交互式配置 Notion"""
    print("\n" + "=" * 50)
    print("   🔧 Notion 配置")
    print("=" * 50)
    print("\n请按以下步骤配置：")
    print("1. 访问 https://www.notion.so/my-integrations")
    print("2. 创建或选择一个 Integration")
    print("3. 复制「Internal Integration Token」（以 secret_ 开头）")
    print("4. 在 Notion 数据库页面，点击「...」→「Add connections」→ 选择你的 Integration")
    print("5. 复制数据库 URL 中的 database_id（32位字符，含连字符）")
    
    api_token = input("\n请输入 Notion API Token：").strip()
    database_id = input("请输入数据库 ID：").strip()
    
    if api_token and database_id:
        config = {
            "api_token": api_token,
            "database_id": database_id
        }
        
        # 测试连接
        print("\n🔍 测试 Notion 连接...")
        success, error = test_notion_connection(config)
        if success:
            save_notion_config(config)
            return config
        else:
            print(f"❌ 连接失败：{error}")
            retry = input("是否仍然保存配置？(y/n)：").strip().lower()
            if retry == 'y':
                save_notion_config(config)
                return config
    
    return None


def test_notion_connection(config):
    """测试 Notion API 连接"""
    api_token = config.get("api_token", "")
    database_id = config.get("database_id", "")
    
    if not api_token or not database_id:
        return False, "Token 或 Database ID 为空"
    
    try:
        resp = requests.post(
            f"{NOTION_API_BASE}/databases/{database_id}/query",
            headers={
                "Authorization": f"Bearer {api_token}",
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json"
            },
            json={"page_size": 1},
            timeout=10
        )
        
        if resp.status_code == 200:
            return True, None
        elif resp.status_code == 401:
            return False, "Token 无效或已被撤销（401）"
        elif resp.status_code == 403:
            return False, "无权限访问数据库，请添加 Integration 连接（403）"
        elif resp.status_code == 404:
            return False, "数据库 ID 无效（404）"
        else:
            return False, f"API 错误：{resp.status_code}"
    except Exception as e:
        return False, str(e)


def fetch_notion_note_links(config):
    """从 Notion 获取笔记链接列表"""
    api_token = config.get("api_token", "")
    database_id = config.get("database_id", "")
    
    try:
        resp = requests.post(
            f"{NOTION_API_BASE}/databases/{database_id}/query",
            headers={
                "Authorization": f"Bearer {api_token}",
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json"
            },
            json={
                "filter": {
                    "property": "笔记地址",
                    "url": {"is_not_empty": True}
                },
                "page_size": 100
            },
            timeout=30
        )
        
        if resp.status_code != 200:
            return None, f"Notion API 错误：{resp.status_code}"
        
        data = resp.json()
        results = data.get("results", [])
        
        note_links = []
        for page in results:
            props = page.get("properties", {})
            url_prop = props.get("笔记地址", {})
            url = url_prop.get("url", "")
            
            if url and "xiaohongshu.com" in url:
                title_prop = props.get("笔记标题", {})
                if title_prop.get("type") == "title":
                    title = title_prop.get("title", [{}])[0].get("plain_text", "")
                elif title_prop.get("type") == "rich_text":
                    title = title_prop.get("rich_text", [{}])[0].get("plain_text", "")
                else:
                    title = ""
                
                note_links.append({
                    "url": url,
                    "title": title or url.split("/")[-1][:20],
                    "page_id": page.get("id", "")
                })
        
        return note_links, None
    except Exception as e:
        return None, str(e)


def update_notion_status(config, page_id, status="已完成"):
    """更新 Notion 页面状态"""
    api_token = config.get("api_token", "")
    
    try:
        resp = requests.patch(
            f"{NOTION_API_BASE}/pages/{page_id}",
            headers={
                "Authorization": f"Bearer {api_token}",
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json"
            },
            json={
                "properties": {
                    "状态": {"select": {"name": status}}
                }
            },
            timeout=10
        )
        return resp.status_code == 200
    except:
        return False


# ============== 配置加载 ==============

def load_config():
    """加载配置文件"""
    identity = {}
    rules = {}
    
    if IDENTITY_FILE.exists():
        with open(IDENTITY_FILE, 'r', encoding='utf-8') as f:
            identity = json.load(f)
    
    if RULES_FILE.exists():
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            rules = json.load(f)
    
    return identity, rules


# ============== MCP 相关 ==============

def get_mcp_session():
    """获取 MCP Session"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json"},
            json={"jsonrpc": "2.0", "method": "initialize",
                  "params": {"protocolVersion": "2024-11-05", "capabilities": {}}},
            timeout=10)
        session_id = resp.headers.get("Mcp-Session-Id")
        if session_id:
            requests.post(MCP_URL,
                headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                timeout=5)
        return session_id
    except:
        return None


def check_login(session_id):
    """检查登录状态"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "check_login_status", "arguments": {}}},
            timeout=15)
        data = resp.json()
        if "result" in data:
            text = data["result"].get("content", [{}])[0].get("text", "")
            return "已登录" in text
        return False
    except:
        return False


def get_login_qrcode(session_id):
    """获取登录二维码"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "get_login_qrcode", "arguments": {}}},
            timeout=30)
        data = resp.json()
        if "result" in data and "content" in data["result"]:
            for item in data["result"]["content"]:
                if item.get("type") == "image":
                    import base64
                    qr_path = BASE_DIR / "login_qrcode.png"
                    with open(qr_path, "wb") as f:
                        f.write(base64.b64decode(item["data"]))
                    return str(qr_path)
    except Exception as e:
        print(f"❌ 获取二维码失败: {e}")
    return None


def parse_note_url(url):
    """解析笔记链接"""
    match = re.search(r'explore/([a-f0-9]+)', url)
    if match:
        feed_id = match.group(1)
    else:
        return None, None
    
    token_match = re.search(r'xsec_token=([A-Za-z0-9+=\-]+)', url)
    xsec_token = token_match.group(1) if token_match else ""
    
    return feed_id, xsec_token


def fetch_comments(session_id, feed_id, xsec_token):
    """获取评论"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "get_feed_detail", "arguments": {
                      "feed_id": feed_id,
                      "xsec_token": xsec_token,
                      "load_all_comments": True,
                      "click_more_replies": True
                  }}},
            timeout=60)
        
        data = resp.json()
        if "result" in data and "content" in data["result"]:
            text = data["result"]["content"][0].get("text", "")
            try:
                result = json.loads(text)
                comments = result.get("data", {}).get("comments", {}).get("list", [])
                return comments
            except:
                pass
    except Exception as e:
        print(f"❌ 获取评论失败: {e}")
    return []


def extract_all_comments(comments, feed_id, note_title):
    """提取所有待回复评论"""
    all_comments = []
    
    for comment in comments:
        is_author = "is_author" in comment.get("showTags", [])
        if is_author:
            continue
        
        has_author_reply = False
        for sub in comment.get("subComments", []):
            if "is_author" in sub.get("showTags", []):
                has_author_reply = True
                break
        
        if not has_author_reply:
            all_comments.append({
                "comment_id": comment["id"],
                "user_name": comment.get("userInfo", {}).get("nickname", "用户"),
                "user_id": comment.get("userInfo", {}).get("userId", ""),
                "content": comment["content"],
                "is_sub": False,
                "parent_id": None,
                "feed_id": feed_id,
                "note_title": note_title
            })
        
        for sub in comment.get("subComments", []):
            sub_is_author = "is_author" in sub.get("showTags", [])
            if sub_is_author:
                continue
            
            sub_has_reply = False
            for third in sub.get("subComments", []):
                if "is_author" in third.get("showTags", []):
                    sub_has_reply = True
                    break
            
            if not sub_has_reply:
                all_comments.append({
                    "comment_id": sub["id"],
                    "user_name": sub.get("userInfo", {}).get("nickname", "用户"),
                    "user_id": sub.get("userInfo", {}).get("userId", ""),
                    "content": sub["content"],
                    "is_sub": True,
                    "parent_id": comment["id"],
                    "feed_id": feed_id,
                    "note_title": note_title
                })
    
    return all_comments


# ============== 回复生成和发送 ==============

def generate_reply(comment, user_name, identity, rules, model_config):
    """AI 生成回复"""
    role = identity.get("identity", {}).get("role", "小红书博主")
    personality = "、".join(identity.get("identity", {}).get("personality", ["幽默", "接地气"]))
    
    safety_rules = rules.get("safety_rules", {})
    safety_text = "\n".join([f"{i+1}. {v}" for i, (k, v) in enumerate(safety_rules.items()) if k.startswith("铁律")])
    
    reply_rules_list = rules.get("reply_rules", [])
    rules_text = "\n".join([f"- {r}" for r in reply_rules_list])
    
    today = datetime.now()
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    date_str = today.strftime("%Y年%m月%d日")
    weekday = weekday_cn[today.weekday()]
    
    prompt = f"""你是小多，一个{role}，性格{personality}。今天是{date_str} {weekday}。

【安全铁律 - 必须遵守】
{safety_text}

【回复规则】
{rules_text}

用户 {user_name} 说：{comment}

请根据以上规则回复："""
    
    content, error = call_ai(prompt, model_config)
    
    if content:
        return content[:80] if "🐾" in content else content.strip() + "🐾"
    else:
        print(f"⚠️ AI 调用失败: {error}")
        return random.choice(["哈哈🐾", "确实🐾", "怎么说呢🐾"])


def send_reply(session_id, feed_id, comment_id, user_id, content):
    """发送回复"""
    try:
        resp = requests.post(MCP_URL,
            headers={"Content-Type": "application/json", "Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "reply_comment_in_feed", "arguments": {
                      "feed_id": feed_id,
                      "comment_id": comment_id,
                      "user_id": user_id,
                      "content": content
                  }}},
            timeout=60)
        
        data = resp.json()
        if "result" in data:
            return True, None
        elif "error" in data:
            return False, data["error"].get("message", "未知错误")
    except Exception as e:
        return False, str(e)
    
    return False, "未知错误"


# ============== 主流程 ==============

def main():
    print("=" * 50)
    print("   小红书评论回复工具 - 交互式版本")
    print("=" * 50)
    
    # 加载配置
    identity, rules = load_config()
    
    # 获取模型配置
    model_config = get_current_model_config()
    if not model_config:
        print("\n⚠️ 未检测到模型配置")
        model_config = setup_model()
        if not model_config:
            print("❌ 模型配置失败，无法继续")
            sys.exit(1)
    
    print(f"\n✅ 使用模型：{model_config.get('model', 'unknown')}")
    
    # 测试模型连接
    print("🔍 测试模型连接...")
    test_content, test_error = call_ai("回复'测试成功'", model_config)
    if test_error:
        print(f"⚠️ 模型连接失败：{test_error}")
        print("请重新配置模型")
        model_config = setup_model()
        if not model_config:
            print("❌ 模型配置失败，无法继续")
            sys.exit(1)
    else:
        print("✅ 模型连接正常")
    
    # 选择数据源
    print("\n" + "=" * 50)
    print("   📊 选择数据源")
    print("=" * 50)
    print("  1. 单篇笔记 - 输入一个小红书笔记链接")
    print("  2. Notion 批量 - 从 Notion 获取多个笔记链接")
    
    mode = input("\n请选择 (1/2)：").strip()
    
    # 获取 MCP Session
    print("\n📡 连接 MCP 服务...")
    session_id = get_mcp_session()
    if not session_id:
        print("❌ 无法连接 MCP 服务，请确保服务已启动")
        print("   启动命令：DISPLAY=:99 ~/xiaohongshu-mcp/xiaohongshu-mcp-linux-amd64 -port :18060 &")
        sys.exit(1)
    
    # 检查登录状态
    print("🔍 检查登录状态...")
    if not check_login(session_id):
        print("⚠️ 未登录小红书")
        qr_path = get_login_qrcode(session_id)
        if qr_path:
            print(f"📱 请扫码登录，二维码已保存到：{qr_path}")
        sys.exit(1)
    
    print("✅ 已登录")
    
    all_comments = []
    notion_config = None
    note_links = []
    
    if mode == "1":
        # 单篇笔记模式
        print("\n📝 请输入小红书笔记链接：")
        url = input("> ").strip()
        
        feed_id, xsec_token = parse_note_url(url)
        if not feed_id:
            print("❌ 无法解析笔记链接")
            sys.exit(1)
        
        print(f"\n📥 正在获取评论...")
        comments = fetch_comments(session_id, feed_id, xsec_token)
        if not comments:
            print("❌ 获取评论失败或没有评论")
            sys.exit(1)
        
        all_comments = extract_all_comments(comments, feed_id, "当前笔记")
        
    elif mode == "2":
        # Notion 批量模式
        notion_config = get_notion_config()
        if not notion_config:
            print("\n⚠️ 未检测到 Notion 配置")
            notion_config = setup_notion()
            if not notion_config:
                print("❌ Notion 配置失败，无法继续")
                sys.exit(1)
        
        print(f"\n📥 从 Notion 获取笔记链接...")
        note_links, error = fetch_notion_note_links(notion_config)
        if error:
            print(f"❌ 获取笔记链接失败：{error}")
            sys.exit(1)
        
        if not note_links:
            print("❌ 没有找到包含笔记地址的记录")
            sys.exit(1)
        
        print(f"\n📋 获取到 {len(note_links)} 篇笔记：")
        for i, link in enumerate(note_links, 1):
            print(f"  {i}. {link['title']}")
        
        print(f"\n📥 正在获取所有笔记的评论...")
        for link in note_links:
            feed_id, xsec_token = parse_note_url(link['url'])
            if not feed_id:
                print(f"  ⚠️ 无法解析：{link['title']}")
                continue
            
            comments = fetch_comments(session_id, feed_id, xsec_token)
            if comments:
                extracted = extract_all_comments(comments, feed_id, link['title'])
                # 添加 Notion page_id
                for c in extracted:
                    c['page_id'] = link.get('page_id', '')
                all_comments.extend(extracted)
                print(f"  ✅ {link['title']}：{len(extracted)} 条待回复")
            else:
                print(f"  ⚠️ {link['title']}：无评论")
        
    else:
        print("❌ 无效选择")
        sys.exit(1)
    
    # 检查待回复评论
    if not all_comments:
        print("\n✅ 所有评论都已回复，没有待回复的评论")
        sys.exit(0)
    
    # 展示待回复评论
    print(f"\n📋 待回复评论（共 {len(all_comments)} 条）：\n")
    for i, c in enumerate(all_comments, 1):
        note_prefix = f"[{c.get('note_title', '')[:10]}] " if c.get('note_title') else ""
        print(f"{i}. {note_prefix}@{c['user_name']}：{c['content'][:30]}...")
    
    # 选择要回复的评论
    print("\n请选择要回复的评论：")
    print("- 输入序号（如 1,2,3）")
    print("- 或输入 '全部'")
    selection = input("> ").strip()
    
    if selection == "全部":
        selected = all_comments
    else:
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(",")]
            selected = [all_comments[i] for i in indices if 0 <= i < len(all_comments)]
        except:
            print("❌ 输入无效")
            sys.exit(1)
    
    # 生成回复
    print(f"\n🤖 正在生成 {len(selected)} 条回复...\n")
    replies = []
    for c in selected:
        reply = generate_reply(c["content"], c["user_name"], identity, rules, model_config)
        replies.append({**c, "reply": reply})
        note_prefix = f"[{c.get('note_title', '')[:10]}] " if c.get('note_title') else ""
        print(f"{note_prefix}@{c['user_name']}：{c['content'][:20]}...")
        print(f"    → {reply}")
        print()
    
    # 审核
    print("=" * 50)
    print("📋 回复预览：\n")
    for i, r in enumerate(replies, 1):
        note_prefix = f"[{r.get('note_title', '')[:10]}] " if r.get('note_title') else ""
        print(f"{i}. {note_prefix}@{r['user_name']}：{r['content'][:25]}...")
        print(f"   回复：{r['reply']}")
        print()
    
    print("请审核：")
    print("1. 确认发送")
    print("2. 修改某条回复")
    print("3. 仅复制（不发送）")
    print("4. 取消")
    choice = input("> ").strip()
    
    if choice == "1":
        print("\n📤 正在发送...")
        success = 0
        failed = 0
        for r in replies:
            ok, err = send_reply(session_id, 
                                 r['feed_id'],
                                 r["parent_id"] if r["is_sub"] else r["comment_id"],
                                 r["user_id"], r["reply"])
            if ok:
                success += 1
                print(f"  ✅ @{r['user_name']}")
                # 更新 Notion 状态
                if notion_config and r.get('page_id'):
                    update_notion_status(notion_config, r['page_id'], "已完成")
            else:
                failed += 1
                print(f"  ❌ @{r['user_name']}: {err}")
        
        print(f"\n✅ 发送完成：成功 {success} 条，失败 {failed} 条")
    
    elif choice == "2":
        print("请输入序号和新回复（如：1 这是新的回复内容🐾）")
        mod = input("> ").strip()
        parts = mod.split(None, 1)
        if len(parts) == 2:
            idx = int(parts[0]) - 1
            if 0 <= idx < len(replies):
                replies[idx]["reply"] = parts[1]
                print(f"✅ 已修改第 {idx+1} 条回复")
        print("\n修改后的回复：")
        for r in replies:
            print(f"  @{r['user_name']} → {r['reply']}")
    
    elif choice == "3":
        print("\n📋 回复内容：")
        for r in replies:
            print(r["reply"])
    
    else:
        print("❌ 已取消")


if __name__ == "__main__":
    main()
