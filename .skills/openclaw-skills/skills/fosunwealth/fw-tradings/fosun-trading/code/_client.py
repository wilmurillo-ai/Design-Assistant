"""
SDK 客户端初始化公共模块。

环境变量要求:
  FSOPENAPI_SERVER_PUBLIC_KEY  - 服务端公钥 (PEM 或纯 base64)
  FSOPENAPI_CLIENT_PRIVATE_KEY - 客户端私钥 (PEM 或纯 base64)
  FSOPENAPI_BASE_URL           - 网关地址
  FSOPENAPI_API_KEY            - API Key (可选, 也可通过 --api-key 传入)
  FSOPENAPI_MAC_ID             - 本地持久化设备唯一编码
  SDK_TYPE                     - 可选: ops / default
"""

from decimal import Decimal, InvalidOperation
import json
import sys

from credential_flow import prepare_client_runtime


def get_client(api_key=None, base_url=None, sdk_type=None):
    """返回已初始化的 SDKClient 实例。"""
    runtime = prepare_client_runtime(api_key=api_key, base_url=base_url, sdk_type=sdk_type)

    try:
        from fsopenapi import SDKClient
    except ImportError:
        print("错误：fsopenapi SDK 未安装。请先在既有环境中执行:", file=sys.stderr)
        print(
            "  /Users/admin/.openclaw/workspace/.venv-fosun/bin/pip install /Users/admin/.openclaw/workspace/skills/fosun-sdk-setup/openapi-sdk",
            file=sys.stderr,
        )
        print("禁止新建虚拟环境；请复用 workspace .venv-fosun", file=sys.stderr)
        sys.exit(1)

    return SDKClient(runtime["base_url"], runtime["api_key"])


def get_sub_account_id(client):
    """获取第一个子账户 ID。"""
    accounts = client.account.list_accounts()
    data = accounts.get("data", accounts)
    subs = data.get("subAccounts", [])
    if not subs:
        print("错误: 未找到子账户。", file=sys.stderr)
        sys.exit(1)
    return subs[0]["subAccountId"]


def dump_json(data):
    """格式化输出 JSON。"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


# 来自“需要用到power的字段.xls”：这些字段跟随响应中的 power 缩放。
_DYNAMIC_POWER_FIELDS = {
    "ask",
    "avg",
    "bid",
    "breakEvenPrice",
    "callPrice",
    "chgVal",
    "close",
    "convertPrice",
    "high",
    "IEP",
    "IEV",
    "latestClose",
    "limitDown",
    "limitUp",
    "low",
    "lowerPrice",
    "lowerStrike",
    "open",
    "pClose",
    "postPClose",
    "prePClose",
    "price",
    "refPrice",
    "strikePrice",
    "turnover",
    "upperStrike",
    "upperPrice",
    "vol",
    "week52High",
    "week52Low",
}

# 来自“需要用到power的字段.xls”：这些字段固定按 2 位小数缩放。
_FIXED_POWER_FIELDS = {
    "amp": 2,
    "bidAskRatio": 2,
    "chgPct": 2,
    "chgPct5d": 2,
    "chgPct20d": 2,
    "chgPctYtd": 2,
    "dpsTTM": 2,
    "dyrStatic": 2,
    "dyrTTM": 2,
    "floatMktCap": 2,
    "mktCap": 2,
    "pb": 2,
    "peStatic": 2,
    "peTTM": 2,
    "tor": 2,
    "volRatio": 2,
}


def _parse_power(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            numeric = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
        if numeric != numeric.to_integral():
            return None
        return int(numeric)


def _scale_price_by_power(value, power):
    if power in (None, 0) or value is None or isinstance(value, bool):
        return value
    try:
        scaled = Decimal(str(value)) / (Decimal(10) ** power)
    except (InvalidOperation, ValueError):
        return value
    if scaled == scaled.to_integral():
        return int(scaled)
    return float(scaled)


def normalize_market_data_by_power(data, inherited_power=None):
    """按字段规则自动还原行情数值字段，并隐藏内部精度字段。"""
    if isinstance(data, list):
        return [normalize_market_data_by_power(item, inherited_power) for item in data]

    if not isinstance(data, dict):
        return data

    current_power = _parse_power(data.get("power"))
    if current_power is None:
        current_power = inherited_power

    normalized = {}
    for key, value in data.items():
        if key == "power":
            continue
        fixed_power = _FIXED_POWER_FIELDS.get(key)
        should_use_dynamic_power = key in _DYNAMIC_POWER_FIELDS or (
            key == "p" and {"p", "v"}.issubset(data.keys())
        )
        if fixed_power is not None:
            normalized[key] = _scale_price_by_power(value, fixed_power)
        elif should_use_dynamic_power:
            normalized[key] = _scale_price_by_power(value, current_power)
        else:
            normalized[key] = normalize_market_data_by_power(value, current_power)
    return normalized


def dump_market_json(data):
    """格式化输出已还原真实价格的行情 JSON。"""
    dump_json(normalize_market_data_by_power(data))


def add_common_args(parser):
    """添加所有脚本共用的 CLI 参数。"""
    parser.add_argument(
        "--api-key", help="Fosun API Key (或设置 FSOPENAPI_API_KEY 环境变量)"
    )
    parser.add_argument(
        "--base-url", help="网关地址 (或设置 FSOPENAPI_BASE_URL 环境变量)"
    )
    parser.add_argument("--sub-account-id", help="子账户 ID (不传则自动获取第一个)")
    parser.add_argument(
        "--sdk-type",
        choices=["default", "ops"],
        help="SDK 模式: default=普通交易接口, ops=走 /api/ops 前缀",
    )
