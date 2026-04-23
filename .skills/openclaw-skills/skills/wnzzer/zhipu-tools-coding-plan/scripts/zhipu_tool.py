#!/usr/bin/env python3
"""
智谱工具 - 网络搜索、网页读取、仓库文档搜索和文件解析
默认使用 Z.AI Coding Plan MCP 端点（免费额度）
设置 ZHIPU_USE_MCP=false 切换到旧版 bigmodel API

使用方式:
    python3 zhipu_tool.py web_search "搜索关键词" [--count 10]
    python3 zhipu_tool.py web_reader "https://example.com"
    python3 zhipu_tool.py zread search "openai/openai" "how to use"
    python3 zhipu_tool.py zread structure "openai/openai" [--path src/]
    python3 zhipu_tool.py zread read "openai/openai" "README.md"
    python3 zhipu_tool.py file_parser /path/to/file [--file-type PDF]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests", file=sys.stderr)
    sys.exit(1)


class ZhipuTools:
    """智谱 AI 工具类 - 支持 MCP 和 Legacy 双模式"""

    API_KEY = os.environ.get("ZHIPU_API_KEY", "")
    USE_MCP = os.environ.get("ZHIPU_USE_MCP", "true").lower() != "false"

    MCP_BASE = "https://api.z.ai/api/mcp"
    LEGACY_BASE = "https://open.bigmodel.cn/api/paas/v4"

    # --- MCP Session Management ---

    @classmethod
    def _mcp_init(cls, endpoint: str) -> str:
        """MCP initialize → 获取 session id"""
        url = f"{cls.MCP_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream, application/json",
        }
        body = {
            "jsonrpc": "2.0", "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "openclaw-zhipu-tools", "version": "1.1.0"},
            },
        }
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()

        session_id = resp.headers.get("mcp-session-id", "")
        if not session_id:
            raise RuntimeError("MCP 初始化失败: 未获取到 mcp-session-id")

        # 发送 initialized 通知
        notify_headers = {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Mcp-Session-Id": session_id,
        }
        requests.post(
            url,
            headers=notify_headers,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            timeout=10,
        )
        return session_id

    @classmethod
    def _mcp_call(cls, endpoint: str, tool_name: str, arguments: dict, max_retries: int = 2) -> dict:
        """MCP tools/call → 返回解析后的结果"""
        url = f"{cls.MCP_BASE}{endpoint}"

        for attempt in range(max_retries + 1):
            try:
                session_id = cls._mcp_init(endpoint)
                call_headers = {
                    "Authorization": f"Bearer {cls.API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream, application/json",
                    "Mcp-Session-Id": session_id,
                }
                body = {
                    "jsonrpc": "2.0", "id": 2,
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                }
                resp = requests.post(url, headers=call_headers, json=body, timeout=120)
                resp.raise_for_status()

                # 解析 SSE 响应
                raw = resp.text
                for line in raw.split("\n"):
                    line = line.strip()
                    if line.startswith("data:"):
                        data_str = re.sub(r"^data:\s*", "", line).strip()
                        if not data_str:
                            continue
                        try:
                            obj = json.loads(data_str)
                            if "result" in obj:
                                result = obj["result"]
                                # 检查 MCP isError 标志
                                if isinstance(result, dict) and result.get("isError"):
                                    error_text = ""
                                    for c in result.get("content", []):
                                        if c.get("type") == "text":
                                            error_text = c["text"]
                                            break
                                    raise RuntimeError(f"MCP error: {error_text}")
                                return result
                            if "error" in obj:
                                raise RuntimeError(f"MCP error: {obj['error']}")
                        except json.JSONDecodeError:
                            pass

                raise RuntimeError(f"MCP 响应解析失败: {raw[:500]}")
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries:
                    import time
                    time.sleep(1 * (attempt + 1))
                    continue
                raise RuntimeError(f"MCP 连接失败（已重试 {max_retries} 次）: {e}")

        raise RuntimeError("MCP 调用失败: 未预期的重试循环退出")

    # --- Web Search (MCP: web_search_prime) ---

    @classmethod
    def web_search(
        cls,
        query: str,
        count: int = 10,
        search_engine: str = "search_std",
        search_intent: bool = False,
        domain_filter: str = None,
        recency_filter: str = "noLimit",
        content_size: str = "medium",
    ) -> dict:
        """网络搜索"""
        if cls.USE_MCP:
            try:
                return cls._web_search_mcp(query, content_size)
            except Exception as e:
                print(f"MCP 搜索失败，回退到 Legacy: {e}", file=sys.stderr)

        return cls._web_search_legacy(
            query, count, search_engine, search_intent,
            domain_filter, recency_filter, content_size,
        )

    @classmethod
    def _web_search_mcp(cls, query: str, content_size: str) -> dict:
        """MCP 模式搜索 - 端点: /web_search_prime/mcp, 工具: web_search_prime"""
        arguments = {
            "search_query": query,
            "content_size": content_size,
        }
        result = cls._mcp_call("/web_search_prime/mcp", "web_search_prime", arguments)
        return cls._extract_mcp_text(result)

    @classmethod
    def _web_search_legacy(
        cls, query, count, search_engine, search_intent,
        domain_filter, recency_filter, content_size,
    ) -> dict:
        """旧版 bigmodel API 搜索"""
        headers = {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "search_query": query,
            "search_engine": search_engine,
            "search_intent": search_intent,
            "count": count,
            "search_recency_filter": recency_filter,
            "content_size": content_size,
        }
        if domain_filter:
            payload["search_domain_filter"] = domain_filter

        resp = requests.post(f"{cls.LEGACY_BASE}/web_search", headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # --- Web Reader (MCP: webReader) ---

    @classmethod
    def web_reader(cls, url: str) -> dict:
        """网页读取"""
        if cls.USE_MCP:
            try:
                return cls._web_reader_mcp(url)
            except Exception as e:
                print(f"MCP 网页读取失败，回退到 Legacy: {e}", file=sys.stderr)

        return cls._web_reader_legacy(url)

    @classmethod
    def _web_reader_mcp(cls, url: str) -> dict:
        """MCP 模式网页读取 - 端点: /web_reader/mcp, 工具: webReader"""
        result = cls._mcp_call("/web_reader/mcp", "webReader", {"url": url})
        return cls._extract_mcp_text(result)

    @classmethod
    def _web_reader_legacy(cls, url: str) -> dict:
        """旧版 bigmodel API 网页读取"""
        headers = {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json",
        }
        resp = requests.post(
            f"{cls.LEGACY_BASE}/reader",
            headers=headers,
            json={"url": url},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    # --- Zread (MCP: search_doc / get_repo_structure / read_file) ---

    @classmethod
    def zread_search(cls, repo: str, query: str, language: str = None) -> dict:
        """GitHub 仓库文档搜索 - 端点: /zread/mcp, 工具: search_doc"""
        if not cls.USE_MCP:
            raise RuntimeError("Zread 仅支持 MCP 模式，请确保 ZHIPU_USE_MCP=true")
        arguments = {"repo_name": repo, "query": query}
        if language:
            arguments["language"] = language
        result = cls._mcp_call("/zread/mcp", "search_doc", arguments)
        return cls._extract_mcp_text(result)

    @classmethod
    def zread_structure(cls, repo: str, path: str = None) -> dict:
        """GitHub 仓库目录结构 - 端点: /zread/mcp, 工具: get_repo_structure"""
        if not cls.USE_MCP:
            raise RuntimeError("Zread 仅支持 MCP 模式，请确保 ZHIPU_USE_MCP=true")
        arguments = {"repo_name": repo}
        if path:
            arguments["dir_path"] = path
        result = cls._mcp_call("/zread/mcp", "get_repo_structure", arguments)
        return cls._extract_mcp_text(result)

    @classmethod
    def zread_file(cls, repo: str, file_path: str) -> dict:
        """GitHub 仓库文件读取 - 端点: /zread/mcp, 工具: read_file"""
        if not cls.USE_MCP:
            raise RuntimeError("Zread 仅支持 MCP 模式，请确保 ZHIPU_USE_MCP=true")
        result = cls._mcp_call("/zread/mcp", "read_file", {"repo_name": repo, "file_path": file_path})
        return cls._extract_mcp_text(result)

    @classmethod
    def _extract_mcp_text(cls, result) -> dict:
        """从 MCP 响应中提取文本内容，确保返回 dict"""
        if not isinstance(result, dict):
            return {"content": str(result)}
        if "content" in result:
            for c in result["content"]:
                if c.get("type") == "text":
                    try:
                        parsed = json.loads(c["text"])
                        if isinstance(parsed, dict):
                            return parsed
                        return {"content": parsed}
                    except (json.JSONDecodeError, TypeError):
                        return {"content": c["text"]}
        return result

    # --- File Parser (Legacy only) ---

    @classmethod
    def file_parser(cls, file_path: str, file_type: str = "WPS", tool_type: str = "prime-sync") -> dict:
        """文件解析（仅 Legacy API）"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        headers = {"Authorization": f"Bearer {cls.API_KEY}"}
        with open(file_path, "rb") as f:
            resp = requests.post(
                f"{cls.LEGACY_BASE}/files/parser/sync",
                headers=headers,
                files={"file": (file_path.name, f)},
                data={"tool_type": tool_type, "file_type": file_type},
                timeout=120,
            )
            resp.raise_for_status()
        return resp.json()


# --- Formatting Helpers ---

def format_search_result(result: dict) -> str:
    output = []
    # content 可能是 JSON 编码的搜索结果数组
    content = result.get("content", "")
    if isinstance(content, str):
        try:
            search_results = json.loads(content)
            if isinstance(search_results, list):
                content = search_results
        except (json.JSONDecodeError, TypeError):
            pass

    if isinstance(content, list):
        for i, item in enumerate(content, 1):
            output.append(f"\n### 结果 {i}")
            output.append(f"**标题**: {item.get('title', 'N/A')}")
            output.append(f"**链接**: {item.get('link', 'N/A')}")
            snippet = item.get("content", "N/A")
            output.append(f"**摘要**: {snippet[:200]}{'...' if len(snippet) > 200 else ''}")
    elif isinstance(content, str):
        output.append(content)
    else:
        output.append(json.dumps(result, ensure_ascii=False, indent=2))
    return "\n".join(output)


def format_web_reader_result(result: dict) -> str:
    output = ["# 网页读取结果\n"]
    content = result.get("content", "")
    # content 可能是 JSON 编码的完整响应
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                result = parsed
                content = result.get("content", "")
        except (json.JSONDecodeError, TypeError):
            pass

    if "title" in result:
        output.append(f"**标题**: {result['title']}\n")
    if isinstance(content, str):
        output.append(content)
    elif "markdown" in result:
        output.append(result["markdown"])
    elif "text" in result:
        output.append(result["text"])
    else:
        output.append(json.dumps(result, ensure_ascii=False, indent=2))
    return "\n".join(output)


def format_parser_result(result: dict) -> str:
    output = ["# 文件解析结果\n"]
    if "content" in result:
        output.append(result["content"])
    elif "text" in result:
        output.append(result["text"])
    else:
        output.append(json.dumps(result, ensure_ascii=False, indent=2))
    return "\n".join(output)


def format_zread_result(result: dict) -> str:
    if "content" in result:
        return result["content"]
    return json.dumps(result, ensure_ascii=False, indent=2)


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="智谱 AI 工具 - 网络搜索、网页读取、仓库文档搜索和文件解析",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # web_search
    sp = subparsers.add_parser("web_search", help="网络搜索 (MCP: web_search_prime)")
    sp.add_argument("query", help="搜索关键词")
    sp.add_argument("--count", type=int, default=10)
    sp.add_argument("--engine", default="search_std")
    sp.add_argument("--recency", default="noLimit", choices=["noLimit", "day", "week", "month"])
    sp.add_argument("--domain")
    sp.add_argument("--raw", action="store_true")

    # web_reader
    rp = subparsers.add_parser("web_reader", help="网页读取 (MCP: webReader)")
    rp.add_argument("url", help="目标 URL")
    rp.add_argument("--raw", action="store_true")

    # zread
    zp = subparsers.add_parser("zread", help="GitHub 仓库文档搜索 (MCP: zread)")
    zsub = zp.add_subparsers(dest="zread_cmd", help="Zread 子命令")

    zs = zsub.add_parser("search", help="搜索仓库文档")
    zs.add_argument("repo", help="GitHub 仓库 (如 'openai/openai')")
    zs.add_argument("query", help="搜索关键词")

    zst = zsub.add_parser("structure", help="查看仓库目录结构")
    zst.add_argument("repo", help="GitHub 仓库")
    zst.add_argument("path", nargs="?", default=None, help="子目录路径")

    zr = zsub.add_parser("read", help="读取仓库文件")
    zr.add_argument("repo", help="GitHub 仓库")
    zr.add_argument("file_path", help="文件路径 (如 'README.md')")

    # file_parser
    fp = subparsers.add_parser("file_parser", help="文件解析 (Legacy only)")
    fp.add_argument("file_path", help="文件路径")
    fp.add_argument("--file-type", default="WPS")
    fp.add_argument("--raw", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not ZhipuTools.API_KEY:
        print("错误: 请设置 ZHIPU_API_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == "web_search":
            result = ZhipuTools.web_search(
                query=args.query, count=args.count, search_engine=args.engine,
                recency_filter=args.recency, domain_filter=args.domain,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.raw else format_search_result(result))

        elif args.command == "web_reader":
            result = ZhipuTools.web_reader(url=args.url)
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.raw else format_web_reader_result(result))

        elif args.command == "zread":
            if not args.zread_cmd:
                zp.print_help()
                sys.exit(1)
            if args.zread_cmd == "search":
                result = ZhipuTools.zread_search(repo=args.repo, query=args.query)
            elif args.zread_cmd == "structure":
                result = ZhipuTools.zread_structure(repo=args.repo, path=args.path)
            elif args.zread_cmd == "read":
                result = ZhipuTools.zread_file(repo=args.repo, file_path=args.file_path)
            print(format_zread_result(result))

        elif args.command == "file_parser":
            result = ZhipuTools.file_parser(file_path=args.file_path, file_type=args.file_type)
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.raw else format_parser_result(result))

    except requests.HTTPError as e:
        print(f"API 错误: {e}", file=sys.stderr)
        if e.response is not None:
            print(f"响应: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
