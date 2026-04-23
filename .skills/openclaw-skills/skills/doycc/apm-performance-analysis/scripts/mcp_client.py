#!/usr/bin/env python3
"""
腾讯云 APM 智能运维 MCP 客户端桥接工具

通过 SSE（Server-Sent Events）传输机制连接远程 MCP Server，
发现并调用 APM 运维相关的 MCP 工具，为 OpenClaw 等 AI 智能体
提供标准化的工具调用能力。

MCP Server 地址配置：
    通过 .env 文件中的 APM_MCP_SSE_URL 变量设置，
    或使用命令行参数 --mcp-url 显式指定。

依赖安装：
    pip install mcp httpx

用法示例:
    # 列出 MCP Server 提供的所有工具
    python mcp_client.py list-tools

    # 调用指定工具
    python mcp_client.py call-tool --name <tool_name> --args '{"key": "value"}'

    # 交互式模式（逐步选择工具和填入参数）
    python mcp_client.py interactive
"""

import argparse
import asyncio
import json
import logging
import os
import stat
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# .env 加载和日志功能
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent.resolve()


def load_env(env_file=None):
    """从 .env 文件加载环境变量。"""
    candidates = []
    if env_file:
        candidates.append(env_file)
    env_from_var = os.environ.get("APM_ENV_FILE")
    if env_from_var:
        candidates.append(env_from_var)
    candidates.append(os.path.join(os.getcwd(), ".env"))
    candidates.append(os.path.join(str(SCRIPT_DIR), "..", ".env"))

    for candidate in candidates:
        candidate = os.path.abspath(candidate)
        if os.path.isfile(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key, value = key.strip(), value.strip()
                    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                        value = value[1:-1]
                    if key not in os.environ:
                        os.environ[key] = value
            return candidate
    return None


def _get_log_dir():
    log_dir = os.environ.get("APM_ERROR_LOG_DIR")
    if log_dir:
        return os.path.abspath(log_dir)
    return os.path.join(os.getcwd(), "logs")


def _init_logger():
    logger = logging.getLogger("apm_ops")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        log_dir = _get_log_dir()
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "apm_error.log")
        fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
        logger.addHandler(fh)
        try:
            os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass
    return logger


def log_error(action, error_code=None, error_message=None, request_id=None, extra=None):
    logger = _init_logger()
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "action": action, "error_code": error_code,
        "error_message": error_message, "request_id": request_id,
    }
    if extra:
        entry["extra"] = extra
    logger.error(json.dumps(entry, ensure_ascii=False))


def log_exception(action, exception, extra=None):
    logger = _init_logger()
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "action": action, "exception_type": type(exception).__name__,
        "exception_message": str(exception), "traceback": traceback.format_exc(),
    }
    if extra:
        entry["extra"] = extra
    logger.error(json.dumps(entry, ensure_ascii=False))


# ---------------------------------------------------------------------------
# MCP SDK 检查
# ---------------------------------------------------------------------------

MCP_SDK_AVAILABLE = False
try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    MCP_SDK_AVAILABLE = True
except ImportError:
    pass


def check_mcp_sdk():
    """检查 MCP SDK 是否已安装。"""
    if not MCP_SDK_AVAILABLE:
        msg = "MCP SDK 未安装"
        log_error("check_mcp_sdk", error_code="MCP_SDK_NOT_INSTALLED", error_message=msg)
        print(f"错误: {msg}。请执行以下命令安装:")
        print("  pip install mcp httpx")
        print("")
        print("如果仅需要 SSE 客户端功能:")
        print("  pip install mcp")
        sys.exit(1)


# ---------------------------------------------------------------------------
# MCP 服务地址获取
# ---------------------------------------------------------------------------

DEFAULT_MCP_SSE_URL = "https://mcp.tcop.woa.com/apm-console/sse"


def get_mcp_url(cli_url=None):
    """
    获取 MCP Server SSE 地址。

    优先级：
    1. 命令行参数 --mcp-url
    2. 环境变量 APM_MCP_SSE_URL（可通过 .env 设置）
    3. 内置默认地址
    """
    if cli_url:
        return cli_url

    env_url = os.environ.get("APM_MCP_SSE_URL")
    if env_url:
        return env_url

    return DEFAULT_MCP_SSE_URL


# ---------------------------------------------------------------------------
# 凭证获取（用于 MCP 请求 header）
# ---------------------------------------------------------------------------

def get_mcp_headers(cli_secret_id=None, cli_secret_key=None):
    """
    获取 MCP 请求所需的认证 headers。

    MCP Server 要求通过 HTTP header 传递腾讯云凭证：
        - secretId: 腾讯云 SecretId
        - secretKey: 腾讯云 SecretKey

    优先级：
    1. 命令行参数 --secret-id / --secret-key
    2. 环境变量 TENCENTCLOUD_SECRET_ID / TENCENTCLOUD_SECRET_KEY（可通过 .env 设置）

    Args:
        cli_secret_id: 命令行传入的 SecretId（可选）
        cli_secret_key: 命令行传入的 SecretKey（可选）

    Returns:
        dict: 包含 secretId 和 secretKey 的 header 字典；
              如果凭证缺失则返回空字典并输出警告
    """
    secret_id = cli_secret_id or os.environ.get("TENCENTCLOUD_SECRET_ID")
    secret_key = cli_secret_key or os.environ.get("TENCENTCLOUD_SECRET_KEY")

    if not secret_id or not secret_key:
        print(
            "警告: 未找到腾讯云凭证 (TENCENTCLOUD_SECRET_ID / TENCENTCLOUD_SECRET_KEY)。\n"
            "MCP 请求将不携带认证 header，部分工具可能无法正常调用。\n"
            "请通过 .env 文件或 --secret-id / --secret-key 参数配置凭证。"
        )
        return {}

    return {
        "secretId": secret_id,
        "secretKey": secret_key,
    }


# ---------------------------------------------------------------------------
# MCP 核心操作：连接、发现工具、调用工具
# ---------------------------------------------------------------------------

def _extract_input_schema(tool):
    """
    从 MCP Tool 对象中安全提取 inputSchema，确保 required 等关键字段不丢失。

    MCP Python SDK 中 Tool 的 input_schema 字段是 dict[str, Any]（标准 JSON Schema），
    但在 Pydantic 模型序列化/反序列化过程中，有可能通过 model_dump() 或直接属性访问
    获取到的内容不一致。本函数统一处理各种情况，确保返回完整的 JSON Schema dict。

    Args:
        tool: MCP SDK 返回的 Tool 对象

    Returns:
        dict: 完整的 JSON Schema 字典，包含 properties、required 等字段
    """
    schema = {}

    # 方式 1：尝试通过 model_dump() 获取完整序列化（Pydantic v2）
    if hasattr(tool, "model_dump"):
        try:
            dumped = tool.model_dump()
            # Pydantic v2 中字段名可能是 input_schema（snake_case）
            if "input_schema" in dumped and isinstance(dumped["input_schema"], dict):
                schema = dumped["input_schema"]
            elif "inputSchema" in dumped and isinstance(dumped["inputSchema"], dict):
                schema = dumped["inputSchema"]
        except Exception:
            pass

    # 方式 2：直接属性访问（兜底）
    if not schema:
        raw_schema = None
        # MCP SDK 使用 input_schema（snake_case）作为 Python 属性名
        if hasattr(tool, "input_schema") and tool.input_schema:
            raw_schema = tool.input_schema
        elif hasattr(tool, "inputSchema") and tool.inputSchema:
            raw_schema = tool.inputSchema

        if raw_schema is not None:
            if isinstance(raw_schema, dict):
                schema = raw_schema
            elif hasattr(raw_schema, "model_dump"):
                # 如果 schema 本身也是 Pydantic 模型
                try:
                    schema = raw_schema.model_dump()
                except Exception:
                    schema = dict(raw_schema) if hasattr(raw_schema, "__iter__") else {}
            elif hasattr(raw_schema, "dict"):
                # Pydantic v1 兼容
                try:
                    schema = raw_schema.dict()
                except Exception:
                    pass

    # 方式 3：通过 JSON 序列化/反序列化（最终兜底，确保 camelCase alias 也被正确处理）
    if not schema or "properties" not in schema:
        if hasattr(tool, "model_dump_json"):
            try:
                tool_json = json.loads(tool.model_dump_json(by_alias=True))
                if "inputSchema" in tool_json and isinstance(tool_json["inputSchema"], dict):
                    schema = tool_json["inputSchema"]
                elif "input_schema" in tool_json and isinstance(tool_json["input_schema"], dict):
                    schema = tool_json["input_schema"]
            except Exception:
                pass

    # 确保 required 字段是列表类型
    if "required" in schema and not isinstance(schema["required"], list):
        schema["required"] = list(schema["required"]) if schema["required"] else []

    return schema


async def list_mcp_tools(mcp_url, timeout=30, sse_read_timeout=300, headers=None):
    """
    连接 MCP Server 并列出所有可用工具。

    Args:
        mcp_url: MCP SSE Server 地址
        timeout: 连接超时（秒）
        sse_read_timeout: SSE 读取超时（秒）
        headers: 自定义 HTTP headers（dict），用于传递认证凭证等信息

    Returns:
        list[dict]: 工具列表，每个工具包含 name、description、inputSchema
    """
    check_mcp_sdk()

    tools_list = []

    # 构造 SSE 连接参数
    sse_kwargs = {
        "url": mcp_url,
        "timeout": timeout,
        "sse_read_timeout": sse_read_timeout,
    }
    if headers:
        sse_kwargs["headers"] = headers

    try:
        async with sse_client(**sse_kwargs) as (read, write):
            async with ClientSession(
                read, write,
                read_timeout_seconds=timedelta(seconds=timeout),
            ) as session:
                await session.initialize()

                tools_result = await session.list_tools()

                for tool in tools_result.tools:
                    # 使用安全提取函数获取完整的 inputSchema
                    schema = _extract_input_schema(tool)

                    tool_info = {
                        "name": tool.name,
                        "description": getattr(tool, "description", "") or "",
                        "inputSchema": schema,
                    }

                    tools_list.append(tool_info)

        return tools_list

    except Exception as e:
        log_exception(
            action="list_mcp_tools",
            exception=e,
            extra={"mcp_url": mcp_url},
        )
        raise


async def call_mcp_tool(mcp_url, tool_name, arguments=None, timeout=60, sse_read_timeout=300, headers=None):
    """
    连接 MCP Server 并调用指定工具。

    Args:
        mcp_url: MCP SSE Server 地址
        tool_name: 要调用的工具名称
        arguments: 工具参数（dict）
        timeout: 连接/调用超时（秒）
        sse_read_timeout: SSE 读取超时（秒）
        headers: 自定义 HTTP headers（dict），用于传递认证凭证等信息

    Returns:
        dict: 包含 success、content、isError 字段的结果
    """
    check_mcp_sdk()

    if arguments is None:
        arguments = {}

    # 构造 SSE 连接参数
    sse_kwargs = {
        "url": mcp_url,
        "timeout": timeout,
        "sse_read_timeout": sse_read_timeout,
    }
    if headers:
        sse_kwargs["headers"] = headers

    try:
        async with sse_client(**sse_kwargs) as (read, write):
            async with ClientSession(
                read, write,
                read_timeout_seconds=timedelta(seconds=timeout),
            ) as session:
                await session.initialize()

                result = await session.call_tool(tool_name, arguments)

                # 解析返回内容
                content_parts = []
                if result.content:
                    for part in result.content:
                        if hasattr(part, "text"):
                            content_parts.append(part.text)
                        elif hasattr(part, "data"):
                            content_parts.append(str(part.data))
                        else:
                            content_parts.append(str(part))

                is_error = getattr(result, "isError", False)

                if is_error:
                    log_error(
                        action=f"call_mcp_tool:{tool_name}",
                        error_code="MCP_TOOL_ERROR",
                        error_message="\n".join(content_parts),
                        extra={
                            "mcp_url": mcp_url,
                            "tool_name": tool_name,
                            "arguments": arguments,
                        },
                    )

                return {
                    "success": not is_error,
                    "content": "\n".join(content_parts),
                    "isError": is_error,
                    "tool_name": tool_name,
                    "arguments": arguments,
                }

    except Exception as e:
        log_exception(
            action=f"call_mcp_tool:{tool_name}",
            exception=e,
            extra={
                "mcp_url": mcp_url,
                "tool_name": tool_name,
                "arguments": arguments,
            },
        )
        return {
            "success": False,
            "content": f"调用工具 {tool_name} 失败: {type(e).__name__}: {str(e)}",
            "isError": True,
            "tool_name": tool_name,
            "arguments": arguments,
        }


# ---------------------------------------------------------------------------
# 输出格式化
# ---------------------------------------------------------------------------

def _get_required_fields(schema):
    """
    从 JSON Schema 中提取必填字段列表。

    支持多种 required 声明方式：
    1. 标准 JSON Schema: schema["required"] = ["field1", "field2"]
    2. 嵌套在 properties 内部的 required 标记（非标准但某些 MCP Server 使用）

    Args:
        schema: JSON Schema 字典

    Returns:
        set: 必填字段名集合
    """
    required = set()

    # 方式 1: 标准 JSON Schema required（顶层数组）
    top_required = schema.get("required")
    if isinstance(top_required, list):
        required.update(top_required)
    elif isinstance(top_required, set):
        required.update(top_required)

    # 方式 2: 检查 properties 中单个字段的 "required" 标记（某些非标准实现）
    properties = schema.get("properties", {})
    for param_name, param_info in properties.items():
        if isinstance(param_info, dict):
            # 有些 MCP Server 在 property 内部设置 "required": true
            if param_info.get("required") is True:
                required.add(param_name)

    return required


def format_tools_list(tools, output_format="table"):
    """格式化工具列表输出。"""
    if output_format == "json":
        print(json.dumps(tools, indent=2, ensure_ascii=False))
        return

    if not tools:
        print("MCP Server 未返回任何工具。")
        return

    print(f"MCP APM 运维工具列表 (共 {len(tools)} 个)")
    print("=" * 100)

    for i, tool in enumerate(tools, 1):
        name = tool.get("name", "N/A")
        desc = tool.get("description", "(无描述)")
        schema = tool.get("inputSchema", {})

        print(f"\n  [{i}] {name}")
        print(f"      描述: {desc}")

        # 展示参数
        properties = schema.get("properties", {})
        required = _get_required_fields(schema)

        if properties:
            print(f"      参数:")
            for param_name, param_info in properties.items():
                param_type = param_info.get("type", "any")
                param_desc = param_info.get("description", "")
                is_required = "必填" if param_name in required else "可选"
                print(f"        - {param_name} ({param_type}, {is_required}): {param_desc}")
        else:
            print(f"      参数: 无")

    print("\n" + "=" * 100)


def format_tool_result(result, output_format="text"):
    """格式化工具调用结果输出。"""
    if output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    tool_name = result.get("tool_name", "N/A")
    success = result.get("success", False)
    content = result.get("content", "")
    is_error = result.get("isError", False)

    status = "成功" if success else "失败"
    print(f"\n工具调用结果: {tool_name} [{status}]")
    print("-" * 60)

    if is_error:
        log_dir = _get_log_dir()
        log_file = os.path.join(log_dir, "apm_error.log")
        print(f"错误: {content}")
        print(f"错误日志: {log_file}")
    else:
        # 尝试美化 JSON 输出
        try:
            parsed = json.loads(content)
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except (json.JSONDecodeError, TypeError):
            print(content)

    print("-" * 60)


# ---------------------------------------------------------------------------
# 交互式模式
# ---------------------------------------------------------------------------

async def interactive_mode(mcp_url, timeout=30, sse_read_timeout=300, headers=None):
    """
    交互式模式：列出工具、选择工具、填入参数、调用并展示结果。
    """
    print(f"正在连接 MCP Server: {mcp_url}")
    print("正在获取可用工具列表...\n")

    try:
        tools = await list_mcp_tools(mcp_url, timeout, sse_read_timeout, headers=headers)
    except Exception as e:
        print(f"连接 MCP Server 失败: {e}")
        return

    if not tools:
        print("MCP Server 未返回任何工具。")
        return

    format_tools_list(tools)

    while True:
        print("\n输入工具编号调用（输入 q 退出，输入 l 重新列出工具）:")
        user_input = input("> ").strip()

        if user_input.lower() == "q":
            print("退出交互式模式。")
            break

        if user_input.lower() == "l":
            format_tools_list(tools)
            continue

        try:
            tool_idx = int(user_input) - 1
            if tool_idx < 0 or tool_idx >= len(tools):
                print(f"无效编号，请输入 1-{len(tools)} 之间的数字。")
                continue
        except ValueError:
            print("请输入有效的数字编号。")
            continue

        selected_tool = tools[tool_idx]
        tool_name = selected_tool["name"]
        schema = selected_tool.get("inputSchema", {})
        properties = schema.get("properties", {})
        required = _get_required_fields(schema)

        print(f"\n已选择工具: {tool_name}")

        # 收集参数
        arguments = {}
        if properties:
            print("请输入参数（直接回车跳过可选参数）:")
            for param_name, param_info in properties.items():
                param_type = param_info.get("type", "any")
                param_desc = param_info.get("description", "")
                is_req = param_name in required
                req_label = "必填" if is_req else "可选"

                prompt_str = f"  {param_name} ({param_type}, {req_label})"
                if param_desc:
                    prompt_str += f" - {param_desc}"
                prompt_str += ": "

                value = input(prompt_str).strip()

                if not value and is_req:
                    print(f"  警告: {param_name} 为必填参数，请重新输入。")
                    value = input(f"  {param_name}: ").strip()

                if value:
                    # 类型转换
                    if param_type == "integer":
                        try:
                            value = int(value)
                        except ValueError:
                            print(f"  警告: 无法转换为整数，保留原始字符串。")
                    elif param_type == "number":
                        try:
                            value = float(value)
                        except ValueError:
                            print(f"  警告: 无法转换为数字，保留原始字符串。")
                    elif param_type == "boolean":
                        value = value.lower() in ("true", "1", "yes")
                    elif param_type == "array" or param_type == "object":
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            print(f"  警告: 无法解析 JSON，保留原始字符串。")

                    arguments[param_name] = value
        else:
            print("该工具不需要参数。")

        print(f"\n正在调用工具 {tool_name}...")
        result = await call_mcp_tool(mcp_url, tool_name, arguments, timeout=60, sse_read_timeout=sse_read_timeout, headers=headers)
        format_tool_result(result)


# ---------------------------------------------------------------------------
# 生成 OpenClaw Skill 桥接代码
# ---------------------------------------------------------------------------

def generate_openclaw_skill_bridge(tools, mcp_url):
    """
    根据 MCP Server 返回的工具列表，生成适用于 OpenClaw 的 SKILL.md
    工具调用桥接文档片段。

    Args:
        tools: MCP 工具列表
        mcp_url: MCP SSE Server 地址

    Returns:
        str: SKILL.md 格式的工具说明片段
    """
    lines = []
    lines.append("## MCP 工具列表\n")
    lines.append(f"以下工具由 MCP Server (`{mcp_url}`) 提供，")
    lines.append("可通过 `scripts/mcp_client.py` 进行调用。\n")

    for i, tool in enumerate(tools, 1):
        name = tool.get("name", "N/A")
        desc = tool.get("description", "(无描述)")
        schema = tool.get("inputSchema", {})

        lines.append(f"### {i}. {name}\n")
        lines.append(f"**描述**: {desc}\n")

        properties = schema.get("properties", {})
        required = _get_required_fields(schema)

        if properties:
            lines.append("**参数**:\n")
            lines.append("| 参数名 | 类型 | 必填 | 说明 |")
            lines.append("|--------|------|------|------|")
            for param_name, param_info in properties.items():
                param_type = param_info.get("type", "any")
                param_desc = param_info.get("description", "")
                is_req = "是" if param_name in required else "否"
                lines.append(f"| {param_name} | {param_type} | {is_req} | {param_desc} |")
            lines.append("")

        lines.append("**调用示例**:\n")
        # 生成示例参数
        example_args = {}
        for param_name, param_info in properties.items():
            param_type = param_info.get("type", "string")
            if param_type == "string":
                example_args[param_name] = f"<{param_name}>"
            elif param_type == "integer":
                example_args[param_name] = 0
            elif param_type == "number":
                example_args[param_name] = 0.0
            elif param_type == "boolean":
                example_args[param_name] = True
            elif param_type == "array":
                example_args[param_name] = []
            elif param_type == "object":
                example_args[param_name] = {}

        args_json = json.dumps(example_args, ensure_ascii=False) if example_args else "{}"
        lines.append(f"```bash")
        lines.append(f"python scripts/mcp_client.py call-tool --name {name} --args '{args_json}'")
        lines.append(f"```\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 APM 智能运维 MCP 客户端桥接工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "MCP Server 地址配置:\n"
            "  通过 .env 文件中的 APM_MCP_SSE_URL 变量设置，\n"
            "  或使用 --mcp-url 参数显式指定。\n"
            "\n"
            "依赖安装:\n"
            "  pip install mcp httpx\n"
            "\n"
            "错误日志:\n"
            "  默认写入 ./logs/apm_error.log\n"
        ),
    )

    parser.add_argument(
        "--env-file",
        help="指定 .env 文件路径",
    )
    parser.add_argument(
        "--mcp-url",
        help="MCP SSE Server 地址（覆盖 .env 中的 APM_MCP_SSE_URL）",
    )
    parser.add_argument(
        "--secret-id",
        help="腾讯云 SecretId（覆盖 .env 中的 TENCENTCLOUD_SECRET_ID，用于 MCP header 认证）",
    )
    parser.add_argument(
        "--secret-key",
        help="腾讯云 SecretKey（覆盖 .env 中的 TENCENTCLOUD_SECRET_KEY，用于 MCP header 认证）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="连接超时（秒），默认 30",
    )
    parser.add_argument(
        "--sse-read-timeout",
        type=int,
        default=300,
        help="SSE 读取超时（秒），默认 300",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # list-tools
    list_parser = subparsers.add_parser(
        "list-tools",
        help="列出 MCP Server 提供的所有工具",
    )
    list_parser.add_argument(
        "--output",
        choices=["table", "json"],
        default="table",
        help="输出格式，默认 table",
    )

    # call-tool
    call_parser = subparsers.add_parser(
        "call-tool",
        help="调用 MCP Server 的指定工具",
    )
    call_parser.add_argument(
        "--name",
        required=True,
        help="要调用的工具名称",
    )
    call_parser.add_argument(
        "--args",
        default="{}",
        help="工具参数（JSON 格式字符串），默认 {}",
    )
    call_parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="输出格式，默认 text",
    )

    # interactive
    subparsers.add_parser(
        "interactive",
        help="交互式模式",
    )

    # generate-bridge
    gen_parser = subparsers.add_parser(
        "generate-bridge",
        help="根据 MCP 工具列表生成 OpenClaw SKILL.md 桥接文档片段",
    )
    gen_parser.add_argument(
        "--output-file",
        help="输出到文件（默认输出到终端）",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 1. 加载 .env 文件
    loaded_env = load_env(env_file=getattr(args, "env_file", None))
    if loaded_env:
        print(f"已加载配置: {loaded_env}")

    # 2. 初始化日志
    _init_logger()

    # 3. 获取 MCP URL
    mcp_url = get_mcp_url(getattr(args, "mcp_url", None))
    timeout = args.timeout
    sse_read_timeout = args.sse_read_timeout

    # 4. 构造 MCP 认证 headers
    headers = get_mcp_headers(
        cli_secret_id=getattr(args, "secret_id", None),
        cli_secret_key=getattr(args, "secret_key", None),
    )

    # 5. 执行命令
    if args.command == "list-tools":
        try:
            tools = asyncio.run(list_mcp_tools(mcp_url, timeout, sse_read_timeout, headers=headers))
            format_tools_list(tools, args.output)
        except Exception as e:
            log_dir = _get_log_dir()
            log_file = os.path.join(log_dir, "apm_error.log")
            print(f"获取工具列表失败: {type(e).__name__}: {e}")
            print(f"错误日志: {log_file}")
            sys.exit(1)

    elif args.command == "call-tool":
        try:
            arguments = json.loads(args.args)
        except json.JSONDecodeError as e:
            print(f"参数 JSON 解析失败: {e}")
            print(f"请确保 --args 参数为有效的 JSON 字符串")
            sys.exit(1)

        result = asyncio.run(
            call_mcp_tool(mcp_url, args.name, arguments, timeout=60, sse_read_timeout=sse_read_timeout, headers=headers)
        )
        format_tool_result(result, args.output)

        if result.get("isError"):
            sys.exit(1)

    elif args.command == "interactive":
        asyncio.run(interactive_mode(mcp_url, timeout, sse_read_timeout, headers=headers))

    elif args.command == "generate-bridge":
        try:
            tools = asyncio.run(list_mcp_tools(mcp_url, timeout, sse_read_timeout, headers=headers))
            bridge_doc = generate_openclaw_skill_bridge(tools, mcp_url)
            if args.output_file:
                with open(args.output_file, "w", encoding="utf-8") as f:
                    f.write(bridge_doc)
                print(f"桥接文档已生成: {args.output_file}")
            else:
                print(bridge_doc)
        except Exception as e:
            print(f"生成桥接文档失败: {type(e).__name__}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
