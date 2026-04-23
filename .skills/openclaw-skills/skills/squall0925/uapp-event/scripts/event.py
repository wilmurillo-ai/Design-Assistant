#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""uapp-event: 友盟 App 自定义事件查询入口脚本

功能目标：
- 读取 umeng-config.json（支持 --config / UMENG_CONFIG_PATH / 当前目录 / .env）
- 解析应用（支持 --app / --account / --platform，含模糊匹配）
- 支持事件列表查询（分页）
- 支持事件统计查询（触发次数、独立用户数）
- 支持参数分析（参数列表、参数值分布、参数值时长）
- 支持时间范围：yesterday / last_7_days / last_30_days
- 输出：
  - 文本模式：表格/摘要
  - JSON 模式：结构化数据
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

# -------------------------
# 工具函数：路径 & 配置加载
# -------------------------


def resolve_workspace_root() -> str:
    """解析 workspace 根目录。

    约定：
    - skill 独立发布时，workspace 即为 skill 所在的父目录
    """
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workspace = os.path.dirname(skill_dir)
    return workspace


def load_env_config_path() -> str | None:
    """从环境变量或 .env 中加载 UMENG_CONFIG_PATH。"""
    env_path = os.environ.get("UMENG_CONFIG_PATH")
    if env_path:
        return env_path

    workspace = resolve_workspace_root()
    env_file = os.path.join(workspace, ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("UMENG_CONFIG_PATH="):
                        return line.split("UMENG_CONFIG_PATH=", 1)[1].strip()
        except Exception:
            pass
    return None


def resolve_config_path(cli_config: str | None) -> str:
    """解析配置文件路径。

    优先级：
    1. CLI 参数 --config
    2. UMENG_CONFIG_PATH（环境变量/.env）
    3. workspace 根目录下的 umeng-config.json
    """
    if cli_config:
        return cli_config

    env_config = load_env_config_path()
    if env_config:
        return env_config

    workspace = resolve_workspace_root()
    default_path = os.path.join(workspace, "umeng-config.json")
    return default_path


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------
# 应用解析（含模糊匹配）
# -------------------------


def normalize_app_name(name: str) -> str:
    """去除半角/全角空格，用于模糊匹配。"""
    return name.replace(" ", "").replace("\u3000", "")


def find_app_by_name(config: dict, app_name: str, account_id: str | None = None, platform: str | None = None):
    """按应用名称查找应用配置，支持精确匹配 + 去空格模糊匹配。"""
    matches = []
    normalized_input = normalize_app_name(app_name)

    for account in config.get("accounts", []):
        if account_id and account.get("id") != account_id:
            continue
        for app in account.get("apps", []):
            if platform and app.get("platform") != platform:
                continue
            name = app.get("name", "")
            if name == app_name or normalize_app_name(name) == normalized_input:
                matches.append({
                    "account_id": account.get("id"),
                    "apiKey": account.get("apiKey"),
                    "apiSecurity": account.get("apiSecurity"),
                    "app": app,
                })

    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    return matches


def resolve_app(config: dict, app_name: str | None, account_id: str | None, platform: str | None) -> dict:
    """解析最终使用的应用配置。"""
    if app_name:
        result = find_app_by_name(config, app_name, account_id=account_id, platform=platform)
        if not result:
            available = []
            for account in config.get("accounts", []):
                for app in account.get("apps", []):
                    available.append(app.get("name", ""))
            raise ValueError(f"未找到名称匹配的应用: {app_name}，可用应用: {', '.join(available)}")
        if isinstance(result, list):
            raise ValueError("存在多个同名应用，请通过 --account / --platform 进一步限定")
        return result

    # 没有指定 app，尝试 defaultApp
    default_app = config.get("defaultApp")
    if default_app:
        return {
            "account_id": default_app.get("account_id"),
            "apiKey": default_app.get("apiKey"),
            "apiSecurity": default_app.get("apiSecurity"),
            "app": {
                "name": default_app.get("name"),
                "appkey": default_app.get("appkey"),
                "platform": default_app.get("platform"),
            },
        }

    raise ValueError("未指定应用且配置中未设置 defaultApp，请使用 --app 指定应用名称")


# -------------------------
# 时间范围解析
# -------------------------


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def resolve_time_range(range_name: str, today: date | None = None) -> tuple[date, date]:
    """解析时间范围名称到起止日期（含）。"""
    if today is None:
        today = date.today()

    if range_name == "yesterday":
        d = today - timedelta(days=1)
        return d, d
    if range_name == "last_7_days":
        end = today - timedelta(days=1)
        start = end - timedelta(days=6)
        return start, end
    if range_name == "last_30_days":
        end = today - timedelta(days=1)
        start = end - timedelta(days=29)
        return start, end

    # 默认视作单日日期
    try:
        d = parse_date(range_name)
        return d, d
    except Exception:
        raise ValueError(f"不支持的时间范围: {range_name}")


# -------------------------
# Umeng SDK 调用
# -------------------------


def get_sdk_root() -> str:
    """获取当前 skill 内部 SDK 根目录。"""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(skill_dir, "友盟_openapi_python_SDK")


def init_sdk(api_key: str, api_security: str) -> None:
    """初始化 SDK 路径和默认服务器配置。"""
    sdk_root = get_sdk_root()
    if sdk_root not in sys.path:
        sys.path.insert(0, sdk_root)

    import aop
    aop.set_default_server('gateway.open.umeng.com')
    aop.set_default_appinfo(int(api_key), api_security)


# -------------------------
# 事件列表查询
# -------------------------


def query_event_list(appkey: str, start: date, end: date, page: int = 1, per_page: int = 50) -> dict:
    """查询事件列表（分页）。

    返回格式：
    {
        "events": [{"id": "...", "name": "...", "displayName": "...}, ...],
        "page": 1,
        "perPage": 50,
        "total": 100,
        "totalPages": 2
    }
    """
    from aop import api

    req = api.UmengUappEventListRequest()
    req.appkey = appkey
    req.startDate = start.strftime("%Y-%m-%d")
    req.endDate = end.strftime("%Y-%m-%d")
    req.page = page
    req.perPage = per_page

    resp = req.get_response()
    if not isinstance(resp, dict):
        return {"events": [], "page": page, "perPage": per_page, "total": 0, "totalPages": 0}

    # API 响应字段：eventInfo, totalPage, page
    events = resp.get("eventInfo", []) or resp.get("events", []) or []
    total_pages = resp.get("totalPage", 0) or 0
    current_page = resp.get("page", page) or page

    # 计算 total（API 不返回 total，根据 totalPages 和当前页数据推算）
    # 如果是最后一页，total = (totalPages - 1) * perPage + len(events)
    # 否则 total = totalPages * perPage（估算）
    if total_pages > 0:
        if current_page >= total_pages:
            total = (total_pages - 1) * per_page + len(events)
        else:
            total = total_pages * per_page
    else:
        total = len(events)

    return {
        "events": events,
        "page": current_page,
        "perPage": per_page,
        "total": total,
        "totalPages": total_pages,
    }


def query_all_events(appkey: str, start: date, end: date, per_page: int = 100) -> list[dict]:
    """查询全部事件（自动分页）。"""
    all_events = []
    page = 1

    while True:
        result = query_event_list(appkey, start, end, page=page, per_page=per_page)
        events = result.get("events", [])
        if not events:
            break
        all_events.extend(events)
        if page >= result.get("totalPages", 1):
            break
        page += 1

    return all_events


# -------------------------
# 事件统计查询
# -------------------------


def query_event_data(appkey: str, event_name: str, start: date, end: date) -> list[dict]:
    """查询事件触发次数趋势。"""
    from aop import api

    req = api.UmengUappEventGetDataRequest()
    req.appkey = appkey
    req.eventName = event_name
    req.startDate = start.strftime("%Y-%m-%d")
    req.endDate = end.strftime("%Y-%m-%d")

    resp = req.get_response()
    if not isinstance(resp, dict):
        return []

    # 响应格式：{"eventData": [{"data": [123, 456], "dates": ["2026-03-01", "2026-03-02"]}]}
    data_arr = resp.get("eventData", []) or resp.get("data", [])
    if not data_arr:
        return []

    # 转换为日期序列
    result = []
    for item in data_arr:
        dates = item.get("dates", [])
        values = item.get("data", [])
        for i, d in enumerate(dates):
            result.append({
                "date": d,
                "count": values[i] if i < len(values) else None,
            })
    return result


def query_event_unique_users(appkey: str, event_name: str, start: date, end: date) -> list[dict]:
    """查询事件独立用户数趋势。"""
    from aop import api

    req = api.UmengUappEventGetUniqueUsersRequest()
    req.appkey = appkey
    req.eventName = event_name
    req.startDate = start.strftime("%Y-%m-%d")
    req.endDate = end.strftime("%Y-%m-%d")

    resp = req.get_response()
    if not isinstance(resp, dict):
        return []

    # 响应格式：{"uniqueUsers": [{"data": [123, 456], "dates": ["2026-03-01", "2026-03-02"]}]}
    data_arr = resp.get("uniqueUsers", []) or resp.get("data", [])
    if not data_arr:
        return []

    result = []
    for item in data_arr:
        dates = item.get("dates", [])
        values = item.get("data", [])
        for i, d in enumerate(dates):
            result.append({
                "date": d,
                "unique_users": values[i] if i < len(values) else None,
            })
    return result


def query_event_stats(appkey: str, event_name: str, start: date, end: date, metric: str = "all") -> list[dict]:
    """查询事件统计（支持 count/unique_users/all）。"""
    if metric == "count":
        return query_event_data(appkey, event_name, start, end)
    elif metric == "unique_users":
        return query_event_unique_users(appkey, event_name, start, end)
    else:  # all
        count_data = query_event_data(appkey, event_name, start, end)
        users_data = query_event_unique_users(appkey, event_name, start, end)

        # 合并数据
        users_map = {item["date"]: item.get("unique_users") for item in users_data}
        result = []
        for item in count_data:
            result.append({
                "date": item["date"],
                "count": item.get("count"),
                "unique_users": users_map.get(item["date"]),
            })
        return result


# -------------------------
# 事件参数查询
# -------------------------


def query_event_param_list(appkey: str, event_id: str, start: date, end: date) -> list[dict]:
    """查询事件参数列表。

    注意：此 API 需要 eventId（非 eventName）。
    """
    from aop import api

    req = api.UmengUappEventParamListRequest()
    req.appkey = appkey
    req.eventId = event_id
    req.startDate = start.strftime("%Y-%m-%d")
    req.endDate = end.strftime("%Y-%m-%d")

    resp = req.get_response()
    if not isinstance(resp, dict):
        return []

    # 响应格式：{"paramInfos": [{"paramId": "...", "name": "...", "displayName": "..."}, ...]}
    return resp.get("paramInfos", []) or resp.get("parameters", []) or resp.get("params", []) or []


def query_param_value_list(appkey: str, event_name: str, param_name: str, start: date, end: date) -> list[dict]:
    """查询参数值列表（分布）。"""
    from aop import api

    req = api.UmengUappEventParamGetValueListRequest()
    req.appkey = appkey
    req.eventName = event_name
    req.eventParamName = param_name
    req.startDate = start.strftime("%Y-%m-%d")
    req.endDate = end.strftime("%Y-%m-%d")

    resp = req.get_response()
    if not isinstance(resp, dict):
        return []

    # 响应格式：{"paramInfos": [{"name": "...", "count": 123, "percent": 10.5}, ...]}
    return resp.get("paramInfos", []) or resp.get("paramValueList", []) or resp.get("values", []) or []


def query_param_duration_list(appkey: str, event_name: str, param_name: str, start: date, end: date) -> list[dict]:
    """查询参数值时长统计。"""
    from aop import api

    req = api.UmengUappEventParamGetValueDurationListRequest()
    req.appkey = appkey
    req.eventName = event_name
    req.eventParamName = param_name
    req.startDate = start.strftime("%Y-%m-%d")
    req.endDate = end.strftime("%Y-%m-%d")

    resp = req.get_response()
    if not isinstance(resp, dict):
        return []

    # 响应格式：{"paramInfos": [{"name": "...", "count": 123, "duration": 10.5}, ...]}
    return resp.get("paramInfos", []) or resp.get("durationList", []) or resp.get("durations", []) or []


def query_param_value_data(appkey: str, event_name: str, param_name: str, param_value: str, start: date, end: date) -> list[dict]:
    """查询参数值统计趋势。"""
    from aop import api

    req = api.UmengUappEventParamGetDataRequest()
    req.appkey = appkey
    req.eventName = event_name
    req.eventParamName = param_name
    req.paramValueName = param_value
    req.startDate = start.strftime("%Y-%m-%d")
    req.endDate = end.strftime("%Y-%m-%d")

    resp = req.get_response()
    if not isinstance(resp, dict):
        return []

    # 响应格式：{"paramValueData": [{"data": [123, 456], "dates": ["2026-03-01", "2026-03-02"]}]}
    data_arr = resp.get("paramValueData", []) or resp.get("data", [])
    if not data_arr:
        return []

    result = []
    for item in data_arr:
        dates = item.get("dates", [])
        values = item.get("data", [])
        for i, d in enumerate(dates):
            result.append({
                "date": d,
                "count": values[i] if i < len(values) else None,
            })
    return result


# -------------------------
# 事件名称解析
# -------------------------


def resolve_event_id(appkey: str, event_name: str, start: date, end: date) -> str | None:
    """根据事件名称解析 eventId。

    用于 param.list API，该 API 需要 eventId 而非 eventName。
    """
    event = find_event_by_name(appkey, event_name, start, end)
    return event.get("id") or event.get("eventId") if event else None


def find_event_by_name(appkey: str, event_name: str, start: date, end: date) -> dict | None:
    """根据事件名称查找事件详情。

    返回完整的事件信息字典，包含 id, name, displayName, count 等。
    如果未找到返回 None。
    """
    # 先查询事件列表
    events = query_all_events(appkey, start, end, per_page=100)

    for event in events:
        # API 返回字段：name, displayName, id, count
        # 兼容两种字段名：eventName/eventId 或 name/id
        evt_name = event.get("name") or event.get("eventName")
        evt_display = event.get("displayName")

        # 精确匹配
        if evt_name == event_name or evt_display == event_name:
            return event
        # 忽略大小写匹配
        if evt_name and evt_name.lower() == event_name.lower():
            return event
        if evt_display and evt_display.lower() == event_name.lower():
            return event

    return None


def find_event_by_display_name(appkey: str, display_name: str, start: date, end: date) -> dict | None:
    """根据显示名称查找事件详情（对人类更友好）。

    只匹配 displayName 字段，返回完整的事件信息字典。
    如果未找到返回 None。
    """
    # 先查询事件列表
    events = query_all_events(appkey, start, end, per_page=100)

    for event in events:
        evt_display = event.get("displayName")

        # 精确匹配
        if evt_display == display_name:
            return event
        # 忽略大小写匹配
        if evt_display and evt_display.lower() == display_name.lower():
            return event

    return None


def get_event_name_id_map(appkey: str, start: date, end: date) -> dict[str, str]:
    """获取事件名称到 ID 的映射表。"""
    events = query_all_events(appkey, start, end, per_page=100)
    return {
        event.get("eventName"): event.get("eventId")
        for event in events
        if event.get("eventName") and event.get("eventId")
    }


# -------------------------
# 输出格式化
# -------------------------


def build_event_list_table(result: dict, show_page_hint: bool = True) -> str:
    """构建事件列表表格输出。"""
    events = result.get("events", [])
    page = result.get("page", 1)
    total_pages = result.get("totalPages", 1)

    if not events:
        return "未查询到事件数据。"

    lines = []
    lines.append(f"事件列表（第 {page}/{total_pages} 页，本页 {len(events)} 个事件）")
    lines.append("-" * 100)
    lines.append(f"{'序号':<6} {'事件ID':<26} {'事件名称':<35} {'显示名称'}")
    lines.append("-" * 100)

    start_idx = (page - 1) * result.get("perPage", 50)
    for i, event in enumerate(events):
        idx = start_idx + i + 1
        # 兼容两种字段名
        event_id = event.get("id") or event.get("eventId", "")
        event_name = event.get("name") or event.get("eventName", "")
        display_name = event.get("displayName", "")
        
        # 事件名称：超过32字符截断，追加"..."
        if len(event_name) > 32:
            event_name = event_name[:32] + "..."
        # 显示名称：超过64字符截断，追加"..."
        if len(display_name) > 64:
            display_name = display_name[:64] + "..."
        
        lines.append(f"{idx:<6} {event_id:<26} {event_name:<35} {display_name}")

    if show_page_hint and total_pages > 1:
        lines.append("-" * 100)
        if page < total_pages:
            lines.append(f"提示：使用 --page {page + 1} 查看下一页，或 --all 查看全部")

    return "\n".join(lines)


def build_event_list_json(result: dict) -> dict:
    """构建事件列表 JSON 输出。"""
    return {
        "events": result.get("events", []),
        "pagination": {
            "page": result.get("page"),
            "perPage": result.get("perPage"),
            "currentPageCount": len(result.get("events", [])),
            "totalPages": result.get("totalPages"),
        }
    }


def build_event_stats_summary(app_name: str, event_name: str, series: list[dict], metric: str) -> str:
    """构建事件统计摘要输出。"""
    if not series:
        return f"事件 {event_name} 在指定时间范围内暂无数据。"

    metric_labels = {
        "count": "触发次数",
        "unique_users": "独立用户数",
        "all": "综合统计",
    }
    metric_label = metric_labels.get(metric, metric)

    # 计算统计值
    if metric == "all":
        counts = [s.get("count") for s in series if s.get("count") is not None]
        users = [s.get("unique_users") for s in series if s.get("unique_users") is not None]
        total_count = sum(counts) if counts else 0
        total_users = sum(users) if users else 0
        avg_count = total_count / len(counts) if counts else 0
        avg_users = total_users / len(users) if users else 0

        return (
            f"事件 {event_name} 统计摘要：\n"
            f"  时间范围：{series[0]['date']} 至 {series[-1]['date']}\n"
            f"  总触发次数：{int(total_count)}\n"
            f"  日均触发次数：{int(avg_count)}\n"
            f"  总独立用户数：{int(total_users)}\n"
            f"  日均独立用户数：{int(avg_users)}"
        )
    else:
        values = [s.get(metric) for s in series if s.get(metric) is not None]
        if not values:
            return f"事件 {event_name} 的 {metric_label} 暂无数据。"

        total = sum(values)
        avg = total / len(values)
        first_val = values[0]
        last_val = values[-1]

        trend = ""
        if first_val > 0:
            change = (last_val - first_val) / first_val
            if change > 0.1:
                trend = f"，呈上升趋势（{change*100:.1f}%）"
            elif change < -0.1:
                trend = f"，呈下降趋势（{change*100:.1f}%）"
            else:
                trend = "，基本持平"

        return (
            f"事件 {event_name} 的 {metric_label}：\n"
            f"  时间范围：{series[0]['date']} 至 {series[-1]['date']}\n"
            f"  总计：{int(total)}\n"
            f"  日均：{int(avg)}\n"
            f"  趋势：{first_val} → {last_val}{trend}"
        )


def build_event_stats_json(app_info: dict, event_name: str, series: list[dict], metric: str, start: date, end: date) -> dict:
    """构建事件统计 JSON 输出。"""
    return {
        "app": {
            "name": app_info["app"].get("name"),
            "appkey": app_info["app"].get("appkey"),
        },
        "event": event_name,
        "metric": metric,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "series": series,
    }


def build_param_list_table(params: list[dict]) -> str:
    """构建参数列表表格输出。"""
    if not params:
        return "该事件暂无参数数据。"

    lines = []
    lines.append(f"参数列表（共 {len(params)} 个参数）")
    lines.append("-" * 100)
    lines.append(f"{'序号':<6} {'参数ID':<26} {'参数名称':<35} {'显示名称'}")
    lines.append("-" * 100)

    for i, param in enumerate(params):
        # 兼容两种字段名
        param_id = param.get("paramId", "")
        param_name = param.get("name") or param.get("paramName", "")
        display_name = param.get("displayName", "")
        
        # 参数名称：超过32字符截断，追加"..."
        if len(param_name) > 32:
            param_name = param_name[:32] + "..."
        # 显示名称：超过64字符截断，追加"..."
        if len(display_name) > 64:
            display_name = display_name[:64] + "..."
        
        lines.append(f"{i+1:<6} {param_id:<26} {param_name:<35} {display_name}")

    return "\n".join(lines)


def build_param_value_table(values: list[dict], param_name: str) -> str:
    """构建参数值分布表格输出。"""
    if not values:
        return f"参数 {param_name} 暂无数据。"

    lines = []
    lines.append(f"参数 {param_name} 值分布（共 {len(values)} 个值）")
    lines.append("-" * 60)
    lines.append(f"{'序号':<6} {'参数值':<30} {'次数':<10} {'占比':<10}")
    lines.append("-" * 60)

    for i, item in enumerate(values):
        # 兼容两种字段名：name 或 value
        val = str(item.get("name") or item.get("value", ""))[:28]
        count = item.get("count", 0)
        percent = item.get("percent", 0)
        lines.append(f"{i+1:<6} {val:<30} {count:<10} {percent:.1f}%")

    return "\n".join(lines)


def build_param_duration_table(durations: list[dict], param_name: str) -> str:
    """构建参数值时长表格输出。"""
    if not durations:
        return f"参数 {param_name} 暂无时长数据。"

    lines = []
    lines.append(f"参数 {param_name} 值时长统计（共 {len(durations)} 个值）")
    lines.append("-" * 60)
    lines.append(f"{'序号':<6} {'参数值':<30} {'次数':<10} {'时长':<10}")
    lines.append("-" * 60)

    for i, item in enumerate(durations):
        # 兼容两种字段名：name 或 value
        val = str(item.get("name") or item.get("value", ""))[:28]
        count = item.get("count", 0)
        duration = item.get("duration", 0)
        lines.append(f"{i+1:<6} {val:<30} {count:<10} {duration:.1f}s")

    return "\n".join(lines)


# -------------------------
# CLI 入口
# -------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="uapp-event: 友盟 App 自定义事件查询入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 查询事件列表
  python3 scripts/event.py --list-events --app "MyApp"

  # 分页查询
  python3 scripts/event.py --list-events --page 2 --per-page 20 --app "MyApp"

  # 检查事件是否存在（通过事件名称）
  python3 scripts/event.py --check-event "click_button" --app "MyApp"

  # 检查事件是否存在（通过显示名称，对人类更友好）
  python3 scripts/event.py --check-display "开始" --app "MyApp"

  # 查询事件统计
  python3 scripts/event.py --query "click_button" --metric count --app "MyApp"

  # 查询事件参数列表
  python3 scripts/event.py --list-params "click_button" --app "MyApp"

  # 查询参数值分布
  python3 scripts/event.py --query "click_button" --param "button_id" --app "MyApp"

  # JSON 输出
  python3 scripts/event.py --list-events --app "MyApp" --json
"""
    )

    # 配置与应用
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--app", help="应用名称（支持模糊匹配）")
    parser.add_argument("--account", help="账号 ID")
    parser.add_argument("--platform", help="平台标识")

    # 时间范围
    parser.add_argument("--range", dest="time_range", default="last_7_days",
                        help="时间范围：yesterday/last_7_days/last_30_days 或 yyyy-mm-dd（默认 last_7_days）")

    # 查询模式
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--list-events", action="store_true", help="查询事件列表")
    mode_group.add_argument("--query", metavar="EVENT_NAME", help="查询事件统计或参数分析")
    mode_group.add_argument("--list-params", metavar="EVENT_NAME", help="查询事件参数列表")
    mode_group.add_argument("--check-event", metavar="EVENT_NAME", help="检查事件是否存在（通过事件名称）")
    mode_group.add_argument("--check-display", metavar="DISPLAY_NAME", help="检查事件是否存在（通过显示名称，对人类更友好）")

    # 事件列表参数
    parser.add_argument("--page", type=int, default=1, help="页码（默认 1）")
    parser.add_argument("--per-page", type=int, default=50, help="每页数量（默认 50，最大 100）")
    parser.add_argument("--all", action="store_true", help="查询全部事件")

    # 事件统计参数
    parser.add_argument("--metric", choices=["count", "unique_users", "all"], default="all",
                        help="事件指标类型（默认 all）")

    # 参数分析
    parser.add_argument("--param", help="参数名称")
    parser.add_argument("--param-metric", choices=["count", "duration"], default="count",
                        help="参数指标类型（默认 count）")
    parser.add_argument("--param-value", help="参数值（用于查询趋势）")

    # 输出格式
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    try:
        args = parse_args(argv)

        # 解析配置与应用
        config_path = resolve_config_path(args.config)
        config = load_config(config_path)
        app_info = resolve_app(config, app_name=args.app, account_id=args.account, platform=args.platform)

        appkey = app_info["app"].get("appkey")
        if not appkey:
            raise ValueError("应用配置缺少 appkey")

        # 解析时间范围
        start, end = resolve_time_range(args.time_range)

        # 初始化 SDK
        init_sdk(app_info["apiKey"], app_info["apiSecurity"])

        # 模式一：事件列表查询
        if args.list_events:
            if args.all:
                # 查询全部事件
                events = query_all_events(appkey, start, end, per_page=100)
                result = {
                    "events": events,
                    "page": 1,
                    "perPage": len(events),
                    "total": len(events),
                    "totalPages": 1,
                }
            else:
                # 限制 per_page 最大 100
                per_page = min(args.per_page, 100)
                result = query_event_list(appkey, start, end, page=args.page, per_page=per_page)

            if args.json:
                output = build_event_list_json(result)
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(build_event_list_table(result))

        # 模式二：检查事件是否存在
        elif args.check_event:
            event_name = args.check_event
            event = find_event_by_name(appkey, event_name, start, end)

            if args.json:
                if event:
                    output = {
                        "exists": True,
                        "event": {
                            "id": event.get("id") or event.get("eventId"),
                            "name": event.get("name") or event.get("eventName"),
                            "displayName": event.get("displayName"),
                            "count": event.get("count"),
                        }
                    }
                else:
                    output = {
                        "exists": False,
                        "eventName": event_name,
                    }
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                if event:
                    evt_id = event.get("id") or event.get("eventId")
                    evt_name = event.get("name") or event.get("eventName")
                    evt_display = event.get("displayName")
                    evt_count = event.get("count", 0)
                    print(f"事件存在：")
                    print(f"  事件ID：{evt_id}")
                    print(f"  事件名称：{evt_name}")
                    print(f"  显示名称：{evt_display}")
                    print(f"  触发次数：{evt_count}")
                else:
                    print(f"事件不存在：{event_name}")

        # 模式二-B：通过显示名称检查事件是否存在
        elif args.check_display:
            display_name = args.check_display
            event = find_event_by_display_name(appkey, display_name, start, end)

            if args.json:
                if event:
                    output = {
                        "exists": True,
                        "event": {
                            "id": event.get("id") or event.get("eventId"),
                            "name": event.get("name") or event.get("eventName"),
                            "displayName": event.get("displayName"),
                            "count": event.get("count"),
                        }
                    }
                else:
                    output = {
                        "exists": False,
                        "displayName": display_name,
                    }
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                if event:
                    evt_id = event.get("id") or event.get("eventId")
                    evt_name = event.get("name") or event.get("eventName")
                    evt_display = event.get("displayName")
                    evt_count = event.get("count", 0)
                    print(f"事件存在：")
                    print(f"  事件ID：{evt_id}")
                    print(f"  事件名称：{evt_name}")
                    print(f"  显示名称：{evt_display}")
                    print(f"  触发次数：{evt_count}")
                else:
                    print(f"未找到显示名称为 \"{display_name}\" 的事件")

        # 模式三：参数列表查询
        elif args.list_params:
            event_name = args.list_params
            # 需要先解析 eventId
            event_id = resolve_event_id(appkey, event_name, start, end)
            if not event_id:
                raise ValueError(f"未找到事件: {event_name}，请使用 --list-events 查看可用事件")

            params = query_event_param_list(appkey, event_id, start, end)

            if args.json:
                print(json.dumps({"params": params}, ensure_ascii=False, indent=2))
            else:
                print(build_param_list_table(params))

        # 模式四：事件统计或参数分析
        elif args.query:
            event_name = args.query

            # 先验证事件是否存在（通过查询事件列表）
            event_id = resolve_event_id(appkey, event_name, start, end)
            if not event_id:
                # 尝试获取一些可用事件名称作为提示
                events = query_event_list(appkey, start, end, page=1, per_page=10)
                available_names = []
                for e in events.get("events", [])[:5]:
                    name = e.get("name") or e.get("eventName")
                    if name:
                        available_names.append(name)
                hint = f"，可用事件示例：{', '.join(available_names)}" if available_names else "，使用 --list-events 查看所有可用事件"
                raise ValueError(f"未找到事件: {event_name}{hint}")

            # 有 --param 则为参数分析
            if args.param:
                param_name = args.param

                # 指定参数值时，查询趋势
                if args.param_value:
                    series = query_param_value_data(appkey, event_name, param_name, args.param_value, start, end)
                    if args.json:
                        output = {
                            "event": event_name,
                            "param": param_name,
                            "paramValue": args.param_value,
                            "series": series,
                        }
                        print(json.dumps(output, ensure_ascii=False, indent=2))
                    else:
                        print(f"参数 {param_name}={args.param_value} 的趋势：")
                        for item in series:
                            print(f"  {item['date']}: {item.get('count', 'N/A')}")
                else:
                    # 参数值分析
                    if args.param_metric == "duration":
                        data = query_param_duration_list(appkey, event_name, param_name, start, end)
                        if args.json:
                            print(json.dumps({"durations": data}, ensure_ascii=False, indent=2))
                        else:
                            print(build_param_duration_table(data, param_name))
                    else:
                        data = query_param_value_list(appkey, event_name, param_name, start, end)
                        if args.json:
                            print(json.dumps({"values": data}, ensure_ascii=False, indent=2))
                        else:
                            print(build_param_value_table(data, param_name))
            else:
                # 事件统计查询
                series = query_event_stats(appkey, event_name, start, end, args.metric)

                if args.json:
                    output = build_event_stats_json(app_info, event_name, series, args.metric, start, end)
                    print(json.dumps(output, ensure_ascii=False, indent=2))
                else:
                    app_name = app_info["app"].get("name", "")
                    print(build_event_stats_summary(app_name, event_name, series, args.metric))

        return 0

    except ValueError as e:
        error_result = {
            "success": False,
            "error_type": "ValueError",
            "message": str(e),
        }
        if hasattr(args, 'json') and args.json:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"[错误] {e}", file=sys.stderr)
            print("\n提示：使用 --help 查看可用选项", file=sys.stderr)
        return 1

    except FileNotFoundError as e:
        error_result = {
            "success": False,
            "error_type": "FileNotFoundError",
            "message": str(e),
        }
        if hasattr(args, 'json') and args.json:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"[配置错误] {e}", file=sys.stderr)
        return 1

    except Exception as e:
        error_result = {
            "success": False,
            "error_type": type(e).__name__,
            "message": str(e),
        }
        if hasattr(args, 'json') and args.json:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"[错误] {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
