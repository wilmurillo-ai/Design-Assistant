#!/usr/bin/env python3
"""
DeepResearch Agent API 调用脚本

用法:
    python deepresearch.py --query "研究小米汽车发展历程" \
                           --api-key "bce-v3/ALTAK-..." \
                           --agent-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

参数也可通过环境变量提供:
    export BAIDU_API_KEY="bce-v3/ALTAK-..."
    export QIANFAN_AGENT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    python deepresearch.py --query "研究小米汽车发展历程"
"""

import argparse
import json
import os
import sys
import time
from typing import Tuple, Dict
from urllib.parse import urlparse


# 禁用输出缓冲，确保 print 立即显示（等同于 python -u 或 PYTHONUNBUFFERED=1）
sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
except ImportError:
    print("缺少依赖: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://qianfan.baidubce.com/v2"
IDLE_TIMEOUT = 600  # 10 分钟空闲超时


# ── 参数解析 ──────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="DeepResearch Agent API 调用工具")
    parser.add_argument("--query", required=True, help="研究问题")
    parser.add_argument("--api-key", default=os.environ.get("BAIDU_API_KEY"),
                        help="千帆 API Key（或设置环境变量 BAIDU_API_KEY）")
    parser.add_argument("--agent-id", default=os.environ.get("QIANFAN_AGENT_ID"),
                        help="深度研究 Agent ID（或设置环境变量 QIANFAN_AGENT_ID）")
    parser.add_argument("--skip-clarification", action="store_true", default=True,
                        help="自动跳过需求澄清阶段（默认开启）")
    parser.add_argument("--clarification-wait", type=int, default=10,
                        help="发送跳过澄清前的等待秒数（默认 10s）")
    return parser.parse_args()


def check_params(args):
    missing = []
    if not args.api_key:
        missing.append("--api-key / BAIDU_API_KEY")
    if not args.agent_id:
        missing.append("--agent-id / QIANFAN_AGENT_ID")
    if missing:
        print("缺少必要参数：", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)


# ── Step 1: 创建会话 ──────────────────────────────────────

def create_conversation(api_key, agent_id):
    print("[Step 1] 创建会话...")
    url, headers = resolve_sandbox_url(api_key, f"{BASE_URL}/agent/deepresearch/create")
    resp = requests.post(
        url,
        headers=headers,
        json={"agent_id": agent_id},
        timeout=30,
    )
    resp.raise_for_status()
    conversation_id = resp.json()["result"]["conversation_id"]
    print(f"         conversation_id: {conversation_id}")
    return conversation_id


# ── SSE 流读取 ────────────────────────────────────────────

def stream_sse(api_key, agent_id, payload, label="", early_stop=None):
    """
    发送 POST /run 并读取 SSE 流，返回所有事件列表。
    early_stop: callable(event) -> bool，返回 True 时提前退出
    """
    events = []
    url, headers = resolve_sandbox_url(api_key, f"{BASE_URL}/agent/deepresearch/run")

    with requests.post(
        url,
        headers=headers,
        json=payload,
        stream=True,
        timeout=None,  # 不设整体超时，通过 IDLE_TIMEOUT 控制
    ) as resp:
        resp.raise_for_status()

        # 用 iter_content 逐字节读取，避免 iter_lines 在某些版本/环境下
        # 对超长行（>chunk_size）的拼接行为不一致。
        # SSE 协议：空行分隔事件，data: 行可连续多行（内容拼接后一起解析）。
        pending_data: list = []
        buf = b""

        def _process_event(raw_json: str) -> bool:
            """解析并处理一个完整 SSE 事件，返回 True 表示需要退出循环"""
            nonlocal events
            if raw_json == "[DONE]":
                return True
            try:
                event = json.loads(raw_json)
            except json.JSONDecodeError:
                return False
            events.append(event)
            _print_event_progress(event, label)
            if event.get("status") == "interrupt":
                return True
            for content in event.get("content", []):
                ev_info = content.get("event") or {}
                if ev_info.get("is_end") and ev_info.get("is_stop"):
                    return True
            if early_stop and early_stop(event):
                return True
            return False

        done = False
        for chunk in resp.iter_content(chunk_size=4096):
            if not chunk:
                continue
            last_data_time = time.time()
            buf += chunk

            # 按行处理 buf 中已完整的行（以 \n 结尾）
            while b"\n" in buf:
                if time.time() - last_data_time > IDLE_TIMEOUT:
                    raise TimeoutError(f"SSE 空闲超时（{IDLE_TIMEOUT}s 无数据）")

                line_bytes, buf = buf.split(b"\n", 1)
                line = line_bytes.rstrip(b"\r").decode("utf-8", errors="replace")

                if not line:
                    # 空行 = 事件边界
                    if pending_data:
                        raw = "".join(pending_data)
                        pending_data.clear()
                        if _process_event(raw):
                            done = True
                            break
                    continue

                if line.startswith("data: "):
                    pending_data.append(line[6:])
                elif line.startswith("data:"):
                    pending_data.append(line[5:])

            if done:
                break

        # 流结束时若还有未处理的 data
        if not done and pending_data:
            raw = "".join(pending_data)
            _process_event(raw)

    return events


def _print_event_progress(event, label):
    """打印所有收到的 SSE 事件（完整原始内容）"""
    prefix = f"[{label}] " if label else ""
    role = event.get("role", "")
    status = event.get("status", "")
    contents = event.get("content", [])
    if not contents:
        print(f"  {prefix}[SSE] role={role} status={status} | (no content)", flush=True)
        return
    for content in contents:
        ev_info = content.get("event") or {}
        ename = ev_info.get("name", "")
        estatus = ev_info.get("status", "")
        ctype = content.get("type", "")
        text = content.get("text")
        if isinstance(text, dict):
            text_str = json.dumps(text, ensure_ascii=False)
        elif isinstance(text, str):
            text_str = text
        else:
            text_str = str(text)
        if len(text_str) > 200:
            text_str = text_str[:200] + "..."
        print(f"  {prefix}[SSE] role={role} status={status} | type={ctype} event.name={ename!r} event.status={estatus!r} | text={text_str}", flush=True)


# ── 事件解析工具 ──────────────────────────────────────────

def has_clarification(events):
    """判断是否出现了需求澄清事件"""
    for event in events:
        if event.get("role") == "assistant":
            for content in event.get("content", []):
                ev_info = content.get("event") or {}
                if ev_info.get("name") == "/chat/chat_agent":
                    return True
    return False


def extract_interrupt_id(events):
    """从事件流中提取 interrupt_id（text.data 是嵌套 JSON 字符串，需二次解析）"""
    for event in events:
        if event.get("status") == "interrupt":
            for content in event.get("content", []):
                if content.get("type") == "json":
                    ev_info = content.get("event") or {}
                    if ev_info.get("name") == "/toolcall/interrupt":
                        text = content.get("text") or {}
                        data_str = text.get("data", "")
                        if data_str:
                            try:
                                inner = json.loads(data_str)
                                if inner.get("interrupt_id"):
                                    return inner["interrupt_id"]
                            except json.JSONDecodeError:
                                pass
    return None


def extract_structured_outline(events):
    """从事件流中提取 structured_outline（text.data 是嵌套 JSON 字符串，需二次解析）。

    服务端推送顺序：
      1. status=preparing，event.name=/toolcall/structured_outline（title 为空，占位）
      2. status=done，    event.name=/toolcall/structured_outline（title 非空，完整大纲）
      3. status=interrupt，event.name=/toolcall/interrupt（等待用户确认）

    脚本收到 interrupt 时 break，因此 done 事件必须在 interrupt 之前到达才能被收集到。
    正常情况下 done 先于 interrupt，所以这里只需找 title 非空的事件即可。
    """
    for event in events:
        for content in event.get("content", []):
            if content.get("type") != "json":
                continue
            ev_info = content.get("event") or {}
            if ev_info.get("name") != "/toolcall/structured_outline":
                continue
            text = content.get("text") or {}
            data_str = text.get("data", "")
            if not data_str:
                continue
            try:
                outline = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            if outline.get("title"):
                return outline
    return None


def extract_files(events):
    """从事件流中提取生成的文件信息"""
    files = {}
    for event in events:
        for content in event.get("content", []):
            if content.get("type") == "files":
                text = content.get("text") or {}
                filename = text.get("filename", "")
                if filename.endswith(".md") and "md" not in files:
                    files["md"] = text
                elif filename.endswith(".html") and "html" not in files:
                    files["html"] = text
    return files


# ── 主流程 ────────────────────────────────────────────────

def run_deepresearch(query, api_key, agent_id, skip_clarification=True, clarification_wait=10):
    """执行完整的深度研究流程，返回生成的文件信息"""

    # Step 1: 创建会话
    conversation_id = create_conversation(api_key, agent_id)

    # Step 2: 发起初始查询
    print(f"\n[Step 2] 发起研究: {query}")
    init_payload = {
        "query": query,
        "agent_id": agent_id,
        "conversation_id": conversation_id,
    }
    events = stream_sse(api_key, agent_id, init_payload, label="初始查询")
    print()

    # Step 3: 判断是否需要处理澄清
    if has_clarification(events):
        if skip_clarification:
            print(f"[Step 3] 检测到需求澄清，{clarification_wait}s 后自动跳过...")
            time.sleep(clarification_wait)
            skip_payload = {
                "query": "跳过",
                "agent_id": agent_id,
                "conversation_id": conversation_id,
            }
            events = stream_sse(api_key, agent_id, skip_payload, label="跳过澄清")
            print()
        else:
            print("[Step 3] 检测到需求澄清（--skip-clarification=false 时需手动处理）")
            sys.exit(0)
    else:
        print("[Step 3] 无需澄清，直接进入大纲确认")

    # Step 4: 提取大纲数据
    print("\n[Step 4] 提取大纲数据...")
    interrupt_id = extract_interrupt_id(events)
    outline = extract_structured_outline(events)

    if not interrupt_id:
        print("错误: 未找到 interrupt_id", file=sys.stderr)
        sys.exit(1)
    if not outline:
        print("错误: 未找到完整的 structured_outline（title 为空）")
        print("诊断: 收到的 structured_outline 事件如下：")
        for ev in events:
            for c in ev.get("content", []):
                evt = c.get("event") or {}
                if evt.get("name") == "/toolcall/structured_outline":
                    text = c.get("text") or {}
                    print(f"  event.status={evt.get('status')!r}  text.data={text.get('data', '')[:100]!r}")
        print("可能原因: 服务端 done 事件（完整大纲）未推送，请重试")
        sys.exit(1)

    print(f"         大纲标题: {outline.get('title')}")
    print(f"         章节数量: {len(outline.get('sub_chapters', []))}")
    print(f"         interrupt_id: {interrupt_id}")

    # Step 5: 确认大纲，生成报告
    print("\n[Step 5] 确认大纲，开始生成报告（可能需要 10~30 分钟）...")

    def is_html_file(event):
        for content in event.get("content", []):
            if content.get("type") == "files":
                filename = (content.get("text") or {}).get("filename", "")
                if filename.endswith(".html"):
                    return True
        return False

    confirm_payload = {
        "query": "确认",
        "agent_id": agent_id,
        "conversation_id": conversation_id,
        "interrupt_id": interrupt_id,
        "structured_outline": outline,
    }
    events = stream_sse(api_key, agent_id, confirm_payload, label="生成报告", early_stop=is_html_file)
    print()

    # 提取文件下载链接
    files = extract_files(events)
    return files

def resolve_sandbox_url(api_key: str, original_url: str) -> Tuple[str, Dict[str, str]]:
    """若当前在沙盒环境中，将目标 URL 替换为代理 URL，并返回需要附加的 headers。"""
    session_id = os.environ.get("DUMATE_SESSION_ID")
    scheduler_url = os.environ.get("DUMATE_SCHEDULER_URL")

    headers = {
        "Content-Type": "application/json",
        "Accept-Encoding": "identity",
    }
    if not session_id or not scheduler_url:
        if not api_key:
            raise ValueError("未设置 API Key，请通过环境变量 BAIDU_API_KEY 设置或使用")
        headers.update({
            "Authorization": f"Bearer {api_key}",
            "X-Appbuilder-From": "openclaw",
        })
        return original_url, headers

    parsed = urlparse(original_url)
    proxy_url = f"{scheduler_url}/api/qianfanproxy{parsed.path}"
    if parsed.query:
        proxy_url += f"?{parsed.query}"

    headers.update({
        "Host": parsed.netloc,
        "X-Dumate-Session-Id": session_id,
        "X-Appbuilder-From": "desktop",
    })
    return proxy_url, headers

# ── 入口 ──────────────────────────────────────────────────

def main():
    args = parse_args()
    check_params(args)

    print("=" * 60)
    print("DeepResearch Agent API")
    print("=" * 60)

    start = time.time()
    try:
        files = run_deepresearch(
            query=args.query,
            api_key=args.api_key,
            agent_id=args.agent_id,
            skip_clarification=args.skip_clarification,
            clarification_wait=args.clarification_wait,
        )
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        sys.exit(1)

    elapsed = time.time() - start
    print("=" * 60)
    print(f"完成！总耗时: {elapsed:.1f}s")

    if files:
        if "md" in files:
            print(f"\nMarkdown 报告:")
            print(f"  文件名: {files['md'].get('filename')}")
            print(f"  下载:   {files['md'].get('download_url')}")
        if "html" in files:
            print(f"\nHTML 报告:")
            print(f"  文件名: {files['html'].get('filename')}")
            print(f"  下载:   {files['html'].get('download_url')}")
    else:
        print("\n未获取到报告文件（任务可能仍在后台运行）")

    print("=" * 60)


if __name__ == "__main__":
    main()
