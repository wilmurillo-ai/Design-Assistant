#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标监控脚本 — 可配置版
从 config.json 读取所有配置，支持多数据源、关键词过滤、飞书/Telegram推送
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import re
from datetime import datetime
from urllib.parse import urlparse

# ==================== 配置加载 ====================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

def load_config():
    """加载配置文件"""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config()

# 数据目录（相对于脚本目录）
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
LOG_FILE = os.path.join(DATA_DIR, "monitor.log")

# ==================== 工具函数 ====================

def log(msg):
    """日志"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def fetch_page(url, encoding="utf-8"):
    """获取网页"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.encoding = encoding
        return resp.text
    except Exception as e:
        log(f"获取失败: {url} — {e}")
        return None


def resolve_url(href, base_url):
    """相对路径 → 绝对路径"""
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        p = urlparse(base_url)
        return f"{p.scheme}://{p.netloc}{href}"
    if base_url.endswith("/"):
        return base_url + href
    return base_url.rsplit("/", 1)[0] + "/" + href


# ==================== 解析器 ====================

def parse_table(html, source):
    """表格型解析器"""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    items = []
    table = soup.find("table")
    if not table:
        return items
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        a = cols[1].find("a")
        if not a:
            continue
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if href:
            href = resolve_url(href, source["url"])
        date = cols[-1].get_text(strip=True) if len(cols) >= 3 else ""
        items.append({"title": title, "url": href, "date": date,
                       "source": source["name"], "type": source["type"]})
    return items


def parse_links(html, source):
    """通用链接解析器（企业官网等）"""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    items = []
    bidding_kw = ["招标", "采购", "公告", "中标", "询价", "比选", "竞价"]
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if any(kw in text for kw in bidding_kw) and len(text) > 4:
            href = resolve_url(a["href"], source["url"])
            date = ""
            parent = a.parent
            if parent:
                m = re.search(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', parent.get_text())
                if m:
                    date = m.group()
            items.append({"title": text, "url": href, "date": date,
                           "source": source["name"], "type": source["type"]})
    return items


PARSERS = {"table": parse_table, "links": parse_links}


# ==================== 详情抓取 ====================

def fetch_detail(url):
    """抓取详情页正文"""
    html = fetch_page(url)
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    for cls_kw in ["content", "main", "body"]:
        for div in soup.find_all(["div", "td"], class_=lambda x, kw=cls_kw: x and kw in x.lower()):
            t = div.get_text(strip=True)
            if len(t) > 100:
                return t[:5000]
    body = soup.find("body")
    if body:
        return body.get_text(separator=" ", strip=True)[:5000]
    return ""


# ==================== 评分 ====================

def score_item(item):
    """关键词评分：总承包类必须正文明确含智能化相关内容才推送"""
    scoring = CONFIG["scoring"]
    kw_core = CONFIG["keywords"]["core"]
    kw_ext = CONFIG["keywords"]["extend"]
    kw_exc = CONFIG["keywords"]["exclude"]

    title = item.get("title", "")
    content = item.get("content", "")
    text = title + " " + content
    score = 0
    matched = []
    reasons = []

    smart_words = [
        "智能化", "信息化", "弱电", "安防", "监控", "门禁", "综合布线", "楼宇自控",
        "机房", "视频监控", "停车系统", "广播系统", "会议系统", "通信工程", "消防联动", "智慧工地"
    ]
    epc_words = ["工程总承包", "施工总承包", "EPC", "总承包"]
    bid_result_words = ["中标", "成交", "候选人", "定标", "结果公告"]

    for kw in kw_core:
        if kw in content:
            score += scoring.get("core_content_weight", 15)
            matched.append(f"{kw}[内容]")
        elif kw in title:
            score += scoring.get("core_title_weight", 10)
            matched.append(kw)

    for kw in kw_ext:
        if kw in content:
            score += scoring.get("extend_content_weight", 5)
            matched.append(f"{kw}[内容]")
        elif kw in title:
            score += scoring.get("extend_title_weight", 2)
            matched.append(kw)

    for kw in kw_exc:
        if kw in text:
            return None

    has_epc_title = any(w in title for w in epc_words)
    smart_hits = [w for w in smart_words if w in content or w in title]
    is_award = any(w in title for w in bid_result_words)

    # 精准收紧：总承包/中标类如果没有明确智能化内容，直接过滤
    if has_epc_title and not smart_hits:
        return None
    if is_award and has_epc_title and not smart_hits:
        return None

    if has_epc_title and smart_hits:
        score += scoring.get("epc_smart_bonus", 12)
        reasons.append(f"总承包项目，建设内容含{'、'.join(smart_hits[:4])}")

    if is_award and (matched or smart_hits):
        score += scoring.get("award_bonus", 6)
        reasons.append("中标/成交类公告")

    if not reasons and matched:
        reasons.append("关键词命中：" + "、".join(matched[:4]))

    if score < scoring.get("threshold", 5):
        return None

    item["score"] = score
    item["matched_keywords"] = matched
    item["match_reasons"] = reasons
    return item


# ==================== 历史管理 ====================

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    os.makedirs(DATA_DIR, exist_ok=True)
    max_r = CONFIG.get("history", {}).get("max_records", 500)
    history = history[-max_r:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def is_new(item, history):
    for h in history:
        if h.get("title") == item.get("title") and h.get("date") == item.get("date"):
            return False
    return True


# ==================== 推送 ====================

def get_feishu_token():
    """获取飞书 tenant_access_token"""
    app_id = CONFIG["push"].get("app_id", "")
    app_secret = CONFIG["push"].get("app_secret", "")
    if not app_id or not app_secret:
        return None
    try:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": app_id, "app_secret": app_secret}, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return data.get("tenant_access_token")
        log(f"飞书token失败: {data}")
    except Exception as e:
        log(f"飞书token异常: {e}")
    return None


def send_feishu(text):
    """发送飞书消息"""
    token = get_feishu_token()
    if not token:
        log("飞书推送跳过: 未配置 app_id/app_secret")
        return False
    target = CONFIG["push"]["target"]
    try:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            params={"receive_id_type": "open_id"},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"receive_id": target, "msg_type": "text", "content": json.dumps({"text": text})},
            timeout=10)
        if resp.json().get("code") == 0:
            log("飞书推送成功")
            return True
        log(f"飞书推送失败: {resp.json()}")
    except Exception as e:
        log(f"飞书推送异常: {e}")
    return False


def send_webhook(text):
    """Webhook 推送（通用）"""
    url = CONFIG["push"].get("webhook_url", "")
    if not url:
        log("Webhook推送跳过: 未配置 webhook_url")
        return False
    try:
        resp = requests.post(url, json={"text": text}, timeout=10)
        log(f"Webhook推送: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        log(f"Webhook异常: {e}")
        return False


def send_notification(items):
    """根据配置选择推送渠道"""
    items.sort(key=lambda x: x["score"], reverse=True)
    max_items = CONFIG["push"].get("max_items", 10)

    msg = f"📢 发现 {len(items)} 条新招投标信息\n\n"
    for item in items[:max_items]:
        stars = "★" * min(item["score"] // 5, 5)
        t = item["title"][:40] + ("..." if len(item["title"]) > 40 else "")
        reason = "；".join(item.get("match_reasons", [])[:2])
        msg += f"【{item['type']}】{t}\n"
        msg += f"   相关度: {stars} | {item['date']}\n"
        if reason:
            msg += f"   命中原因: {reason}\n"
        msg += f"   链接: {item['url']}\n\n"

    channel = CONFIG["push"].get("channel", "feishu")
    if channel == "feishu":
        send_feishu(msg)
    elif channel == "webhook":
        send_webhook(msg)
    else:
        log(f"未知推送渠道: {channel}，仅打印")
        print(msg)


# ==================== 主流程 ====================

def run():
    log("=" * 50)
    log("开始招标监控...")
    history = load_history()
    new_items = []

    for source in CONFIG["sources"]:
        if not source.get("enabled", True):
            continue
        log(f"抓取: {source['name']}")
        html = fetch_page(source["url"], source.get("encoding", "utf-8"))

        parser_fn = PARSERS.get(source.get("parser", "table"), parse_table)
        items = parser_fn(html, source)

        all_kw = CONFIG["keywords"]["core"] + CONFIG["keywords"]["extend"]
        for item in items:
            title = item.get("title", "")
            # 标题有关键词 → 抓详情
            if any(kw in title for kw in all_kw) or \
               any(kw in title for kw in ["智能", "系统", "集成", "工程", "施工"]):
                item["content"] = fetch_detail(item.get("url", ""))
            else:
                item["content"] = ""

            scored = score_item(item)
            if scored and is_new(scored, history):
                new_items.append(scored)
                log(f"  ✅ 新项目: {scored['title'][:40]} (分数:{scored['score']})")

        import time; time.sleep(1)

    for item in new_items:
        history.append(item)
    save_history(history)

    log(f"完成: 共抓取 {len(history)} 条历史, 本次新增 {len(new_items)} 条")
    if new_items:
        send_notification(new_items)
    return new_items


if __name__ == "__main__":
    run()
