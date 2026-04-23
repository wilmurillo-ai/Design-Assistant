#!/usr/bin/env python3
"""
统一鉴权解析模块。

职责：
- 解析 appKey：环境变量 -> 上下文 -> 扫描当前 workspace 下的 appkey_manager.py
- 解析 access-token：环境变量 -> 上下文 -> appKey 换取
- 按接口声明组装鉴权 header

被其他脚本引用：
  from auth.login import resolve_app_key, ensure_token, build_auth_headers
"""

import argparse
import importlib.util
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

AUTH_URL = "https://sg-cwork-web.mediportal.com.cn/user/login/appkey"
APP_CODE = "cms_gpt"

APPKEY_CONTEXT_KEYS = (
    "appKey",
    "app_key",
    "xg_biz_api_key",
    "xg_app_key",
    "cworkKey",
    "cwork_key",
)

APPKEY_TEXT_PATTERNS = (
    r'(?i)"appKey"\s*:\s*"([^"]+)"',
    r'(?i)"xg[_-]?biz[_-]?api[_-]?key"\s*:\s*"([^"]+)"',
    r'(?i)"xg[_-]?app[_-]?key"\s*:\s*"([^"]+)"',
    r'(?i)"cwork[_ ]?key"\s*:\s*"([^"]+)"',
)

ACCESS_TOKEN_CONTEXT_KEYS = (
    "access-token",
    "access_token",
    "accessToken",
    "xgToken",
    "xg_token",
    "XG_USER_TOKEN",
    "token",
)

ACCESS_TOKEN_TEXT_PATTERNS = (
    r'(?i)"access-token"\s*:\s*"([^"]+)"',
    r'(?i)"access[_-]?token"\s*:\s*"([^"]+)"',
    r'(?i)"xgToken"\s*:\s*"([^"]+)"',
    r'(?i)"token"\s*:\s*"([^"]+)"',
)


def _ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _log(message: str, quiet: bool):
    if not quiet:
        print(message, file=sys.stderr)


def _normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


def _stringify_scalar(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _parse_context(context: Any) -> Any:
    if context is None:
        return None
    if isinstance(context, (dict, list)):
        return context
    if not isinstance(context, str):
        return context

    text = context.strip()
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _extract_by_path(payload: Any, path: tuple[str, ...]) -> str | None:
    current = payload
    for segment in path:
        if not isinstance(current, dict):
            return None

        matched = None
        target = _normalize_key(segment)
        for key, value in current.items():
            if _normalize_key(key) == target:
                matched = value
                break

        if matched is None:
            return None
        current = matched

    return _stringify_scalar(current)


def _extract_from_mapping(payload: Any, candidate_keys: tuple[str, ...], extra_paths: tuple[tuple[str, ...], ...] = ()) -> str | None:
    if payload is None:
        return None

    normalized_candidates = {_normalize_key(key) for key in candidate_keys}
    queue = [payload]

    while queue:
        current = queue.pop(0)
        if isinstance(current, dict):
            for key, value in current.items():
                if _normalize_key(key) in normalized_candidates:
                    extracted = _stringify_scalar(value)
                    if extracted:
                        return extracted
            for path in extra_paths:
                extracted = _extract_by_path(current, path)
                if extracted:
                    return extracted
            queue.extend(current.values())
        elif isinstance(current, list):
            queue.extend(current)

    return None


def _extract_from_text(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip()
            if value:
                return value
    return None


def extract_appkey_from_context(context: Any) -> str | None:
    """从上下文中提取 appKey。"""
    payload = _parse_context(context)
    if payload is None:
        return None

    extracted = _extract_from_mapping(
        payload,
        APPKEY_CONTEXT_KEYS,
        extra_paths=(
            ("auth", "appKey"),
            ("headers", "appKey"),
        ),
    )
    if extracted:
        return extracted

    if isinstance(payload, str):
        return _extract_from_text(payload, APPKEY_TEXT_PATTERNS)

    return None


def extract_access_token_from_context(context: Any) -> str | None:
    """从上下文中提取 access-token / xgToken / token。"""
    payload = _parse_context(context)
    if payload is None:
        return None

    extracted = _extract_from_mapping(
        payload,
        ACCESS_TOKEN_CONTEXT_KEYS,
        extra_paths=(
            ("auth", "access-token"),
            ("auth", "xgToken"),
            ("headers", "access-token"),
            ("data", "xgToken"),
            ("session", "token"),
        ),
    )
    if extracted:
        return extracted

    if isinstance(payload, str):
        return _extract_from_text(payload, ACCESS_TOKEN_TEXT_PATTERNS)

    return None


def _remember_app_key(app_key: str):
    os.environ["XG_BIZ_API_KEY"] = app_key
    os.environ["XG_APP_KEY"] = app_key


def _remember_token(token: str):
    os.environ["XG_USER_TOKEN"] = token


def _find_workspace_appkey_manager() -> Path:
    """
    从当前脚本位置向上找到 workspace 目录，再在其中扫描 appkey_manager.py。
    """
    script_path = Path(__file__).resolve()
    search_roots = [script_path.parent, *script_path.parents]

    for root in search_roots:
        workspace_dir = root / "workspace"
        if not workspace_dir.is_dir():
            continue

        matches = sorted(workspace_dir.rglob("appkey_manager.py"))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            matched_paths = ", ".join(str(path) for path in matches)
            raise RuntimeError(
                f"当前 workspace 下找到多个 appkey_manager.py，请保留唯一一个: {matched_paths}"
            )

    raise RuntimeError("未找到当前 workspace 下可用的 appkey_manager.py")


def _load_workspace_get_appkey():
    appkey_manager_file = _find_workspace_appkey_manager()
    module_name = "_xg_workspace_appkey_manager"
    spec = importlib.util.spec_from_file_location(module_name, appkey_manager_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 appkey_manager.py: {appkey_manager_file}")

    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        raise RuntimeError(
            f"无法执行 appkey_manager.py: {appkey_manager_file}: {exc}"
        ) from exc

    get_appkey = getattr(module, "get_appkey", None)
    if not callable(get_appkey):
        raise RuntimeError(f"appkey_manager.py 中未找到可调用的 get_appkey(): {appkey_manager_file}")

    return get_appkey


def get_token(app_key: str) -> str:
    """
    用 AppKey 换取 access-token。
    """
    normalized_key = app_key.strip()
    if not normalized_key:
        raise RuntimeError("登录失败：appKey 不能为空")

    url = f"{AUTH_URL}?appCode={APP_CODE}&appKey={normalized_key}"
    req = urllib.request.Request(url, method="GET")

    try:
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"登录请求失败 (HTTP {e.code}): {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"登录请求失败: {e.reason}") from e

    result_data = data.get("data") or {}
    token = result_data.get("xgToken") or result_data.get("token") or result_data.get("access-token")
    if token:
        return token

    message = data.get("resultMsg") or data.get("detailMsg") or data.get("message") or "未知错误"
    raise RuntimeError(f"登录失败: {message}")


def get_session(app_key: str) -> dict:
    """
    用 AppKey 换取完整会话信息。
    """
    normalized_key = app_key.strip()
    if not normalized_key:
        raise RuntimeError("登录失败：appKey 不能为空")

    url = f"{AUTH_URL}?appCode={APP_CODE}&appKey={normalized_key}"
    req = urllib.request.Request(url, method="GET")

    try:
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"登录请求失败 (HTTP {e.code}): {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"登录请求失败: {e.reason}") from e

    result_data = data.get("data") or {}
    token = result_data.get("xgToken") or result_data.get("token") or result_data.get("access-token")
    if not token:
        message = data.get("resultMsg") or data.get("detailMsg") or data.get("message") or "未知错误"
        raise RuntimeError(f"登录失败: {message}")

    return {
        "token": token,
        "userId": result_data.get("userId", ""),
        "userName": result_data.get("userName", ""),
        "avatar": result_data.get("avatar", ""),
        "corpId": result_data.get("corpId", ""),
        "personId": result_data.get("personId", ""),
    }


def resolve_app_key(context: Any = None, quiet: bool = False) -> str:
    """
    解析 appKey。

    优先级：
    1. 环境变量 XG_BIZ_API_KEY / XG_APP_KEY
    2. 上下文里的 appKey
    3. 扫描当前 workspace 下的 appkey_manager.py，并执行其中的 get_appkey()
    """
    env_app_key = (os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY") or "").strip()
    if env_app_key:
        _remember_app_key(env_app_key)
        return env_app_key

    context_app_key = extract_appkey_from_context(context)
    if context_app_key:
        _remember_app_key(context_app_key)
        _log("已从上下文解析 appKey", quiet)
        return context_app_key

    try:
        get_appkey = _load_workspace_get_appkey()
        app_key = get_appkey()
    except Exception as exc:
        _log(f"当前 workspace 下的 appkey_manager.py 不可用，进入向用户索要 CWork Key 的兜底流程: {exc}", quiet)
        raise RuntimeError(
            "无法获取 appKey：未找到环境变量 XG_BIZ_API_KEY / XG_APP_KEY，且上下文中也没有可用 appKey。请向用户索要 CWork Key。"
        ) from exc

    _remember_app_key(app_key)
    _log("已通过当前 workspace 下的 appkey_manager.py 获取 appKey", quiet)
    return app_key


def ensure_token(context: Any = None, quiet: bool = False) -> str:
    """
    解析并确保一个有效的 access-token。

    优先级：
    1. 环境变量 XG_USER_TOKEN
    2. 上下文里的 access-token / xgToken / token
    3. 先解析 appKey，再调用登录接口换取 token
    """
    env_token = os.environ.get("XG_USER_TOKEN", "").strip()
    if env_token:
        _remember_token(env_token)
        _log("使用环境变量中的 access-token", quiet)
        return env_token

    context_token = extract_access_token_from_context(context)
    if context_token:
        _remember_token(context_token)
        _log("已从上下文解析 access-token", quiet)
        return context_token

    app_key = resolve_app_key(context=context, quiet=quiet)
    new_token = get_token(app_key)
    _remember_token(new_token)
    _log("已通过 appKey 换取新的 access-token", quiet)
    return new_token


def build_auth_headers(
    auth_mode: str,
    context: Any = None,
    content_type: str | None = "application/json",
    quiet: bool = False,
) -> dict[str, str]:
    """
    按接口鉴权模式组装 header。

    支持：
    - none / nologin
    - appKey
    - access-token
    """
    mode = (auth_mode or "none").strip().lower().replace("_", "-")
    headers: dict[str, str] = {}

    if content_type:
        headers["Content-Type"] = content_type

    if mode in ("none", "nologin", "no-auth"):
        return headers
    if mode in ("appkey", "app-key"):
        headers["appKey"] = resolve_app_key(context=context, quiet=quiet)
        return headers
    if mode in ("access-token", "token"):
        headers["access-token"] = ensure_token(context=context, quiet=quiet)
        return headers

    raise ValueError(f"不支持的 auth_mode: {auth_mode}")


def main():
    parser = argparse.ArgumentParser(description="统一鉴权解析：appKey / access-token")
    parser.add_argument("--app-key", "-k", type=str, help="显式传入 CWork AppKey")
    parser.add_argument("--context-json", type=str, default="", help="显式传入上下文 JSON/文本")
    parser.add_argument("--full", action="store_true", help="输出完整会话信息（JSON 格式）")
    parser.add_argument("--resolve-app-key", action="store_true", help="输出一个可用的 appKey")
    parser.add_argument("--ensure", action="store_true", help="输出一个可用的 access-token")
    parser.add_argument("--headers", action="store_true", help="按 --auth-mode 输出鉴权 headers（JSON）")
    parser.add_argument(
        "--auth-mode",
        type=str,
        default="access-token",
        help="header 模式：none / appKey / access-token（默认 access-token）",
    )
    args = parser.parse_args()

    context = args.context_json

    if args.app_key:
        _remember_app_key(args.app_key.strip())

    try:
        if args.headers:
            headers = build_auth_headers(args.auth_mode, context=context)
            print(json.dumps(headers, ensure_ascii=False, indent=2))
            return

        if args.ensure:
            print(ensure_token(context=context))
            return

        if args.resolve_app_key:
            print(resolve_app_key(context=context))
            return

        app_key = args.app_key.strip() if args.app_key else resolve_app_key(context=context)
        if args.full:
            print(json.dumps(get_session(app_key), ensure_ascii=False, indent=2))
            return

        print(get_token(app_key))
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
