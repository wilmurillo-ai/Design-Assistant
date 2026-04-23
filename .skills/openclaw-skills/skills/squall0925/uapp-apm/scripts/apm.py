#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""uapp-apm: 友盟 APM 数据查询脚本

功能目标：
- 读取 umeng-config.json（支持 --config / UMENG_CONFIG_PATH / 当前目录 / .env）
- 解析应用（支持 --app / --account，含模糊匹配）
- 支持8个APM API接口查询
- 支持7种稳定性类型筛选
- 输出：文本表格 / JSON

依赖说明：
- 首次运行时会自动安装 alibabacloud_umeng_apm20220214 SDK
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta

# -------------------------
# 依赖安装
# -------------------------

APM_SDK_PACKAGE = "alibabacloud_umeng_apm20220214"


def check_tea_module_conflict():
    """检查 Tea 模块冲突问题。

    问题说明：
    - 第三方 tea 包（utility library）与阿里云 alibabacloud-tea 包冲突
    - alibabacloud-tea 安装后的模块名是大写 Tea
    - 在 MacOS 不区分大小写的文件系统上，tea 和 Tea 目录会冲突
    """
    import importlib.util

    # 检查是否能正确导入大写 Tea 模块
    tea_spec = importlib.util.find_spec("Tea")
    lowercase_tea_spec = importlib.util.find_spec("tea")

    if tea_spec is None:
        # Tea 模块不存在，可能是被小写 tea 覆盖了
        if lowercase_tea_spec is not None:
            # 检查小写 tea 是否来自第三方包（非阿里云）
            tea_path = lowercase_tea_spec.origin
            if tea_path and "alibabacloud" not in tea_path:
                print("检测到 Tea 模块冲突：系统中存在第三方 tea 包，与阿里云 SDK 冲突")
                print("正在修复：卸载冲突的 tea 包并重新安装 alibabacloud-tea...")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "uninstall", "-y", "tea"
                    ])
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", "--quiet", "alibabacloud-tea"
                    ])
                    print("修复完成。")
                    import importlib
                    importlib.invalidate_caches()
                except subprocess.CalledProcessError as e:
                    print(f"自动修复失败: {e}", file=sys.stderr)
                    print("请手动执行以下命令修复：")
                    print("  pip3 uninstall tea -y")
                    print("  pip3 install alibabacloud-tea")
                    sys.exit(1)


def ensure_apm_sdk_installed():
    """确保 APM SDK 已安装，如未安装则自动安装。"""
    import importlib

    try:
        importlib.import_module("alibabacloud_umeng_apm20220214")
    except ImportError:
        print(f"正在安装 {APM_SDK_PACKAGE}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--quiet", APM_SDK_PACKAGE
            ])
            print("SDK 安装完成。")
            # 安装后清除缓存，确保能导入新安装的模块
            importlib.invalidate_caches()
        except subprocess.CalledProcessError as e:
            print(f"SDK 安装失败: {e}", file=sys.stderr)
            sys.exit(1)

    # 检查并修复 Tea 模块冲突
    check_tea_module_conflict()

    # 确保 Tea 模块可用
    try:
        import Tea  # noqa: F401
    except ImportError:
        print("错误: Tea 模块未正确安装，请检查 alibabacloud-tea 包", file=sys.stderr)
        sys.exit(1)


# 在导入APM相关模块前确保SDK已安装
ensure_apm_sdk_installed()

# -------------------------
# 常量定义
# -------------------------

# 稳定性类型枚举
ERROR_TYPES = {
    0: "全部崩溃",
    1: "java/ios崩溃",
    2: "native崩溃",
    3: "ANR",
    4: "自定义异常",
    5: "卡顿",
}

ERROR_TYPE_NAMES = {
    "all": 0,
    "java_ios": 1,
    "native": 2,
    "anr": 3,
    "custom": 4,
    "lag": 5,
}

# 查询类型
QUERY_TYPES = {
    "today_stability": "今日稳定性统计",
    "history_stability": "历史稳定性统计",
    "launch": "启动性能统计",
    "network": "网络性能统计",
    "native_page": "原生页面性能统计",
    "h5_page": "H5页面性能统计",
    "network_minute": "分钟粒度网络统计",
    "error_minute": "分钟粒度稳定性统计",
}

# 时间范围
TIME_RANGES = {
    "yesterday": "昨天",
    "last_7_days": "过去7天",
    "last_30_days": "过去30天",
}


# -------------------------
# 工具函数：路径 & 配置加载
# -------------------------


def resolve_workspace_root() -> str:
    """解析 workspace 根目录。"""
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
    """解析配置文件路径。"""
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


def find_app_by_name(config: dict, app_name: str, account_id: str | None = None):
    """按应用名称查找应用配置，支持精确匹配 + 去空格模糊匹配。"""
    matches = []
    normalized_input = normalize_app_name(app_name)

    for account in config.get("accounts", []):
        if account_id and account.get("id") != account_id:
            continue
        for app in account.get("apps", []):
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


def resolve_app(config: dict, app_name: str | None, account_id: str | None) -> dict:
    """解析最终使用的应用配置。"""
    if app_name:
        result = find_app_by_name(config, app_name, account_id=account_id)
        if not result:
            available = []
            for account in config.get("accounts", []):
                for app in account.get("apps", []):
                    available.append(app.get("name", ""))
            raise ValueError(f"未找到名称匹配的应用: {app_name}，可用应用: {', '.join(available)}")
        if isinstance(result, list):
            raise ValueError("存在多个同名应用，请通过 --account 进一步限定")
        return result

    raise ValueError("未指定应用，请使用 --app 指定应用名称")


# -------------------------
# 时间范围解析
# -------------------------


def parse_date(s: str) -> date:
    """解析日期字符串。"""
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
# APM SDK 初始化与调用
# -------------------------


def init_apm_client(api_key: str, api_security: str):
    """初始化 APM SDK Client。

    使用阿里云 OpenAPI 认证方式。
    apiKey -> access_key_id
    apiSecurity -> access_key_secret
    """
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_umeng_apm20220214.client import Client

    config = open_api_models.Config(
        access_key_id=api_key,
        access_key_secret=api_security,
    )
    # 友盟APM的endpoint
    config.endpoint = "apm.openapi.umeng.com"

    return Client(config)


def query_today_stability(client, data_source_id: str, error_type: int = 0, app_version: str | None = None) -> dict:
    """查询今日稳定性统计数据。"""
    from alibabacloud_umeng_apm20220214 import models as apm_models

    request = apm_models.GetTodayStatTrendRequest(
        data_source_id=data_source_id,
        type=error_type,
        app_version=app_version,
    )
    response = client.get_today_stat_trend(request)
    return response.body.to_map() if response.body else {}


def query_history_stability(client, data_source_id: str, start_date: str, end_date: str,
                            error_type: int = 0, app_version: str | None = None) -> dict:
    """查询历史稳定性统计数据。"""
    from alibabacloud_umeng_apm20220214 import models as apm_models

    request = apm_models.GetStatTrendRequest(
        data_source_id=data_source_id,
        start_date=start_date,
        end_date=end_date,
        type=error_type,
        app_version=app_version,
    )
    response = client.get_stat_trend(request)
    return response.body.to_map() if response.body else {}


def query_launch_trend(client, data_source_id: str, start_date: str, end_date: str,
                       time_unit: str = "day", app_version: str | None = None) -> dict:
    """查询启动性能统计数据。"""
    from alibabacloud_umeng_apm20220214 import models as apm_models

    request = apm_models.GetLaunchTrendRequest(
        data_source_id=data_source_id,
        start_date=start_date,
        end_date=end_date,
        time_unit=time_unit,
        app_version=app_version,
    )
    response = client.get_launch_trend(request)
    return response.body.to_map() if response.body else {}


def query_network_trend(client, data_source_id: str, start_date: str, end_date: str,
                        time_unit: str = "day", app_version: str | None = None) -> dict:
    """查询网络性能统计数据。"""
    from alibabacloud_umeng_apm20220214 import models as apm_models

    request = apm_models.GetNetworkTrendRequest(
        data_source_id=data_source_id,
        start_date=start_date,
        end_date=end_date,
        time_unit=time_unit,
        app_version=app_version,
    )
    response = client.get_network_trend(request)
    return response.body.to_map() if response.body else {}


def query_native_page_trend(client, data_source_id: str, start_date: str, end_date: str,
                            time_unit: str = "day", app_version: str | None = None) -> dict:
    """查询原生页面性能统计数据。"""
    from alibabacloud_umeng_apm20220214 import models as apm_models

    request = apm_models.GetNativePageTrendRequest(
        data_source_id=data_source_id,
        start_date=start_date,
        end_date=end_date,
        time_unit=time_unit,
        app_version=app_version,
    )
    response = client.get_native_page_trend(request)
    return response.body.to_map() if response.body else {}


def query_h5_page_trend(client, data_source_id: str, start_date: str, end_date: str,
                        time_unit: str = "day", app_version: str | None = None) -> dict:
    """查询H5页面性能统计数据。"""
    from alibabacloud_umeng_apm20220214 import models as apm_models

    request = apm_models.GetH5PageTrendRequest(
        data_source_id=data_source_id,
        start_date=start_date,
        end_date=end_date,
        time_unit=time_unit,
        app_version=app_version,
    )
    response = client.get_h5page_trend(request)
    return response.body.to_map() if response.body else {}


def query_network_minute_trend(client, data_source_id: str, start_time: str) -> dict:
    """查询分钟粒度网络统计数据。"""
    from alibabacloud_umeng_apm20220214 import models as apm_models

    request = apm_models.GetNetworkMinuteTrendRequest(
        data_source_id=data_source_id,
        start_time=start_time,
    )
    response = client.get_network_minute_trend(request)
    return response.body.to_map() if response.body else {}


def query_error_minute_trend(client, data_source_id: str, start_time: str, error_type: int = 0) -> dict:
    """查询分钟粒度稳定性统计数据。"""
    from alibabacloud_umeng_apm20220214 import models as apm_models

    request = apm_models.GetErrorMinuteStatTrendRequest(
        data_source_id=data_source_id,
        start_time=start_time,
        type=error_type,
    )
    response = client.get_error_minute_stat_trend(request)
    return response.body.to_map() if response.body else {}


# -------------------------
# 输出格式化
# -------------------------


def format_number(n) -> str:
    """格式化数字，添加千分位。"""
    if n is None:
        return "-"
    try:
        return f"{int(n):,}"
    except (ValueError, TypeError):
        return str(n)


def format_percent(n) -> str:
    """格式化百分比。"""
    if n is None:
        return "-"
    try:
        return f"{float(n):.2f}%"
    except (ValueError, TypeError):
        return str(n)


def format_duration(n) -> str:
    """格式化时长（毫秒）。"""
    if n is None:
        return "-"
    try:
        return f"{float(n):.1f}ms"
    except (ValueError, TypeError):
        return str(n)


def extract_data(result: dict) -> list:
    """从 API 响应中提取数据列表。"""
    data = result.get("data", [])
    if isinstance(data, list):
        return data
    return []


def build_stability_table(result: dict, app_name: str, error_type: int, is_today: bool = True) -> str:
    """构建稳定性统计表格。"""
    data = extract_data(result)
    error_type_name = ERROR_TYPES.get(error_type, f"类型{error_type}")
    time_desc = "今日实时" if is_today else "历史"

    lines = []
    lines.append(f"应用 [{app_name}] 的 {time_desc} {error_type_name} 统计数据：")
    lines.append("")

    if not data:
        lines.append("暂无数据。")
        return "\n".join(lines)

    # 表头
    lines.append(f"{'时间点':<20} {'错误数':<12} {'错误率':<12} {'影响用户数':<12} {'影响用户率'}")
    lines.append("-" * 75)

    # 数据行
    for item in data:
        time_point = item.get("timePoint", "")
        error_count = item.get("errorCount", 0)
        error_rate = item.get("errorRate", 0)
        affected_user_count = item.get("affectedUserCount", 0)
        affected_user_rate = item.get("affectedUserRate", 0)
        lines.append(
            f"{time_point:<20} {format_number(error_count):<12} "
            f"{format_percent(error_rate):<12} {format_number(affected_user_count):<12} "
            f"{format_percent(affected_user_rate)}"
        )

    return "\n".join(lines)


def build_launch_table(result: dict, app_name: str) -> str:
    """构建启动性能统计表格。"""
    data = extract_data(result)

    lines = []
    lines.append(f"应用 [{app_name}] 的启动性能统计数据：")
    lines.append("")

    if not data:
        lines.append("暂无数据。")
        return "\n".join(lines)

    # 表头
    lines.append(f"{'时间点':<15} {'冷启动耗时':<15} {'冷启动次数':<12} {'热启动耗时':<15} {'热启动次数':<12} {'首次启动耗时'}")
    lines.append("-" * 90)

    # 数据行
    for item in data:
        time_point = item.get("timePoint", "")
        cold_duration = item.get("coldLaunchDuration")
        cold_count = item.get("coldLaunchCount", 0)
        hot_duration = item.get("hotLaunchDuration")
        hot_count = item.get("hotLaunchCount", 0)
        first_duration = item.get("firstLaunchDuration")
        lines.append(
            f"{time_point:<15} {format_duration(cold_duration):<15} {format_number(cold_count):<12} "
            f"{format_duration(hot_duration):<15} {format_number(hot_count):<12} {format_duration(first_duration)}"
        )

    return "\n".join(lines)


def build_network_table(result: dict, app_name: str) -> str:
    """构建网络性能统计表格。"""
    data = extract_data(result)

    lines = []
    lines.append(f"应用 [{app_name}] 的网络性能统计数据：")
    lines.append("")

    if not data:
        lines.append("暂无数据。")
        return "\n".join(lines)

    # 表头
    lines.append(f"{'时间点':<15} {'平均响应时间':<15} {'平均耗时':<12} {'每分钟请求数':<15} {'平均传输字节'}")
    lines.append("-" * 75)

    # 数据行
    for item in data:
        time_point = item.get("timePoint", "")
        avg_response_time = item.get("avgResponseTime")
        avg_cost = item.get("avgCost")
        request_per_minute = item.get("requestPerMinute")
        avg_transform_bytes = item.get("avgTransformBytes")
        lines.append(
            f"{time_point:<15} {format_duration(avg_response_time):<15} {format_duration(avg_cost):<12} "
            f"{format_number(request_per_minute):<15} {format_number(avg_transform_bytes)}"
        )

    return "\n".join(lines)


def build_native_page_table(result: dict, app_name: str) -> str:
    """构建原生页面性能统计表格。"""
    data = extract_data(result)

    lines = []
    lines.append(f"应用 [{app_name}] 的原生页面性能统计数据：")
    lines.append("")

    if not data:
        lines.append("暂无数据。")
        return "\n".join(lines)

    # 表头
    lines.append(f"{'时间点':<15} {'平均加载耗时':<15} {'加载次数':<12} {'慢加载率':<12} {'崩溃率'}")
    lines.append("-" * 70)

    # 数据行
    for item in data:
        time_point = item.get("timePoint", "")
        avg_load_duration = item.get("avgLoadDuration")
        load_cnt = item.get("loadCnt", 0)
        slow_load_rate = item.get("slowLoadRate")
        crash_rate = item.get("crashRate")
        lines.append(
            f"{time_point:<15} {format_duration(avg_load_duration):<15} {format_number(load_cnt):<12} "
            f"{format_percent(slow_load_rate):<12} {format_percent(crash_rate)}"
        )

    return "\n".join(lines)


def build_h5_page_table(result: dict, app_name: str) -> str:
    """构建H5页面性能统计表格。"""
    data = extract_data(result)

    lines = []
    lines.append(f"应用 [{app_name}] 的H5页面性能统计数据：")
    lines.append("")

    if not data:
        lines.append("暂无数据。")
        return "\n".join(lines)

    # 表头
    lines.append(f"{'时间点':<12} {'DNS':<10} {'TCP':<10} {'首字节':<10} {'DOM就绪':<10} {'页面加载'}")
    lines.append("-" * 65)

    # 数据行
    for item in data:
        time_point = item.get("timePoint", "")
        dns = item.get("dns")
        tcp = item.get("tcp")
        first_byte = item.get("firstByte")
        dom_ready = item.get("domReady")
        load_finish = item.get("loadFinish")
        lines.append(
            f"{time_point:<12} {format_duration(dns):<10} {format_duration(tcp):<10} "
            f"{format_duration(first_byte):<10} {format_duration(dom_ready):<10} {format_duration(load_finish)}"
        )

    return "\n".join(lines)


def build_minute_table(result: dict, app_name: str, is_network: bool = True) -> str:
    """构建分钟级数据表格。"""
    data = extract_data(result)
    type_name = "网络" if is_network else "稳定性"

    lines = []
    lines.append(f"应用 [{app_name}] 的分钟级 {type_name} 统计数据：")
    lines.append("")

    if not data:
        lines.append("暂无数据。")
        return "\n".join(lines)

    if is_network:
        # 表头
        lines.append(f"{'时间点':<20} {'请求数':<15} {'错误数'}")
        lines.append("-" * 50)
        # 数据行
        for item in data:
            time_point = item.get("timePoint", "")
            request_count = item.get("requestCount", 0)
            error_count = item.get("errorCount", 0)
            lines.append(f"{time_point:<20} {format_number(request_count):<15} {format_number(error_count)}")
    else:
        # 表头
        lines.append(f"{'时间点':<20} {'错误数':<12} {'启动数':<12}")
        lines.append("-" * 50)
        # 数据行
        for item in data:
            time_point = item.get("timePoint", "")
            error_count = item.get("errorCount", 0)
            launch_count = item.get("launchCount", 0)
            lines.append(f"{time_point:<20} {format_number(error_count):<12} {format_number(launch_count)}")

    return "\n".join(lines)


def build_json_output(result: dict, success: bool = True) -> str:
    """构建 JSON 输出。"""
    output = {"success": success, "data": result}
    return json.dumps(output, ensure_ascii=False, indent=2)


# -------------------------
# CLI 入口
# -------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="uapp-apm: 友盟 APM 数据查询",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 配置与应用
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--app", required=True, help="应用名称")
    parser.add_argument("--account", help="账号 ID")

    # 查询类型
    parser.add_argument(
        "--query-type", "-t",
        required=True,
        choices=list(QUERY_TYPES.keys()),
        help="查询类型"
    )

    # 稳定性类型
    parser.add_argument(
        "--error-type",
        type=int,
        choices=list(ERROR_TYPES.keys()),
        default=0,
        help="稳定性类型：0-全部崩溃，1-java/ios崩溃，2-native崩溃，3-ANR，4-自定义异常，5-卡顿（默认0）"
    )

    # 时间参数
    parser.add_argument("--range", default="yesterday", help="时间范围：yesterday/last_7_days/last_30_days 或 yyyy-mm-dd")
    parser.add_argument("--start-time", help="分钟级时间参数，格式：yyyy-mm-dd HH:MM")
    parser.add_argument("--app-version", help="应用版本（可选）")
    parser.add_argument("--time-unit", default="day", choices=["day", "hour"], help="时间单位（默认day）")

    # 输出格式
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    try:
        args = parse_args(argv)

        # 加载配置
        config_path = resolve_config_path(args.config)
        config = load_config(config_path)

        # 解析应用
        app_info = resolve_app(config, args.app, args.account)
        data_source_id = app_info["app"].get("appkey")

        if not data_source_id:
            raise ValueError("应用配置缺少 appkey")

        # 初始化 APM Client
        client = init_apm_client(app_info["apiKey"], app_info["apiSecurity"])

        # 解析时间范围
        start, end = resolve_time_range(args.range)
        start_date = start.strftime("%Y-%m-%d")
        end_date = end.strftime("%Y-%m-%d")

        result = None
        output = ""
        app_name = app_info["app"].get("name", args.app)

        # 根据查询类型执行查询
        query_type = args.query_type

        if query_type == "today_stability":
            result = query_today_stability(client, data_source_id, args.error_type, args.app_version)
            output = build_stability_table(result, app_name, args.error_type, is_today=True)

        elif query_type == "history_stability":
            result = query_history_stability(client, data_source_id, start_date, end_date,
                                             args.error_type, args.app_version)
            output = build_stability_table(result, app_name, args.error_type, is_today=False)

        elif query_type == "launch":
            result = query_launch_trend(client, data_source_id, start_date, end_date,
                                        args.time_unit, args.app_version)
            output = build_launch_table(result, app_name)

        elif query_type == "network":
            result = query_network_trend(client, data_source_id, start_date, end_date,
                                         args.time_unit, args.app_version)
            output = build_network_table(result, app_name)

        elif query_type == "native_page":
            result = query_native_page_trend(client, data_source_id, start_date, end_date,
                                             args.time_unit, args.app_version)
            output = build_native_page_table(result, app_name)

        elif query_type == "h5_page":
            result = query_h5_page_trend(client, data_source_id, start_date, end_date,
                                         args.time_unit, args.app_version)
            output = build_h5_page_table(result, app_name)

        elif query_type == "network_minute":
            if not args.start_time:
                raise ValueError("分钟级查询需要 --start-time 参数")
            result = query_network_minute_trend(client, data_source_id, args.start_time)
            output = build_minute_table(result, app_name, is_network=True)

        elif query_type == "error_minute":
            if not args.start_time:
                raise ValueError("分钟级查询需要 --start-time 参数")
            result = query_error_minute_trend(client, data_source_id, args.start_time, args.error_type)
            output = build_minute_table(result, app_name, is_network=False)

        # 输出结果
        if args.json:
            print(build_json_output(result))
        else:
            print(output)

        return 0

    except ValueError as e:
        if hasattr(args, 'json') and args.json:
            print(build_json_output({"error": str(e)}, success=False))
        else:
            print(f"[错误] {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        if hasattr(args, 'json') and args.json:
            print(build_json_output({"error": str(e)}, success=False))
        else:
            print(f"[配置错误] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        if hasattr(args, 'json') and args.json:
            print(build_json_output({"error": str(e)}, success=False))
        else:
            print(f"[错误] {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
