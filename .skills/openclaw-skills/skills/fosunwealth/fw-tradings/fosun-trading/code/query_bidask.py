#!/usr/bin/env python3
"""查询股票买卖信息（每手股数、最大可买/可卖数量、购买力、可提现金等）。

调用 BidAskInfo 接口，返回下单前需要的关键参数。
响应包含：lotSize、maxQuantityBuy/maxQuantitySell、购买力、可用/可提现金、币种等。

用法:
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --direction buy --order-type limit
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --direction sell --order-type limit
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock AAPL --market us --order-type limit
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 600519 --market sh --order-type limit
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --price 350.000 --order-type limit
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --order-type market             # 市价单
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --order-type enhanced_limit     # 增强限价单
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --order-type special_limit      # 特别限价单
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --order-type dark               # 暗盘订单
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --order-type auction_limit      # 竞价限价单
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --order-type auction            # 竞价单
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --order-type stop_loss_limit --trig-price 385.000
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock AAPL --market us --time-in-force 2       # 美股盘前盘后校验
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock AAPL --market us --product-type 15 --expiry 20260630 --strike 200.00 --right CALL
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_bidask.py --stock 00700 --lot-size-only           # 仅输出每手股数
"""

import argparse
import sys
from _client import get_client, get_sub_account_id, dump_json, add_common_args


DIRECTION_MAP = {"buy": 1, "sell": 2, "1": 1, "2": 2}

ORDER_TYPE_MAP = {
    "auction_limit": 1,
    "auction": 2,
    "limit": 3,
    "enhanced_limit": 4,
    "special_limit": 5,
    "dark": 6,
    "6": 6,
    "market": 9,
    "stop_loss_limit": 31,
    "take_profit_limit": 32,
    "trailing_stop": 33,
    "take_profit_stop_loss": 35,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "9": 9, "31": 31, "32": 32, "33": 33, "35": 35,
}

ORDER_TYPE_LABELS = {
    1: "竞价限价单",
    2: "竞价单",
    3: "限价单",
    4: "增强限价单",
    5: "特别限价单",
    6: "暗盘订单",
    9: "市价单",
    31: "止损限价单",
    32: "止盈限价单",
    33: "跟踪止损单",
    35: "止盈止损单",
}

MARKET_ORDER_TYPES = {
    "hk": {1, 2, 3, 4, 5, 6, 9, 31, 32, 33, 35},
    "us": {3, 9, 31, 32, 33, 35},
    "sh": {3, 31, 32, 33},
    "sz": {3, 31, 32, 33},
}

TRIGGER_PRICE_REQUIRED = {31, 32}
OPTION_RIGHTS = {"CALL", "PUT"}


def main():
    parser = argparse.ArgumentParser(
        description="查询股票买卖信息（每手股数 lotSize、最大可买/可卖数量、购买力）",
    )
    add_common_args(parser)

    parser.add_argument("--stock", required=True, help="股票代码（不含市场前缀），如 00700 / AAPL / 600519")
    parser.add_argument("--market", default="hk", choices=["hk", "us", "sh", "sz"],
                        help="市场: hk(默认) / us / sh / sz")
    parser.add_argument("--direction", default="buy", help="方向: buy(默认) / sell（或 1 / 2）")
    parser.add_argument("--order-type", required=True,
                        help="订单类型: auction_limit(1) / auction(2) / limit(3) / enhanced_limit(4) / special_limit(5) / dark(6) / market(9) / stop_loss_limit(31) / take_profit_limit(32) / trailing_stop(33) / take_profit_stop_loss(35)")
    parser.add_argument("--price", help="委托价格（可选，传入可得到更精确的可买数量）")
    parser.add_argument("--quantity", help="委托数量（可选）")
    parser.add_argument("--trig-price", help="触发价（条件单/高级校验场景）")
    parser.add_argument(
        "--time-in-force",
        type=int,
        choices=[0, 2, 4],
        help="时段控制: 0=当日有效 2=允许美股盘前盘后 4=允许夜盘",
    )
    parser.add_argument("--client-id", type=int, help="客户 ID")
    parser.add_argument("--product-type", type=int, help="产品类型，如 15=期权")
    parser.add_argument("--expiry", help="期权到期日，如 20260327")
    parser.add_argument("--strike", help="期权行权价")
    parser.add_argument("--right", help="期权方向，如 CALL / PUT")
    parser.add_argument("--lot-size-only", action="store_true", help="仅输出每手股数（lotSize）")

    args = parser.parse_args()

    direction = DIRECTION_MAP.get(args.direction.lower())
    if direction is None:
        print(f"错误: 无效方向 '{args.direction}'，请使用 buy/sell 或 1/2", file=sys.stderr)
        sys.exit(1)

    order_type = ORDER_TYPE_MAP.get(args.order_type.lower())
    if order_type is None:
        print(
            f"错误: 无效订单类型 '{args.order_type}'，可选: auction_limit/auction/limit/enhanced_limit/special_limit/"
            f"dark/market/stop_loss_limit/take_profit_limit/trailing_stop/take_profit_stop_loss 或 1/2/3/4/5/6/9/31/32/33/35",
            file=sys.stderr,
        )
        sys.exit(1)

    supported_order_types = MARKET_ORDER_TYPES[args.market]
    if order_type not in supported_order_types:
        supported_labels = " / ".join(
            f"{value}={ORDER_TYPE_LABELS[value]}" for value in sorted(supported_order_types)
        )
        print(
            f"错误: 市场 '{args.market}' 不支持 {ORDER_TYPE_LABELS[order_type]}({order_type})。"
            f"该市场仅支持: {supported_labels}",
            file=sys.stderr,
        )
        sys.exit(1)

    if order_type in TRIGGER_PRICE_REQUIRED and not args.trig_price:
        print("错误: 止损/止盈条件单校验时必须提供 --trig-price", file=sys.stderr)
        sys.exit(1)

    is_option_order = args.product_type == 15 or any([args.expiry, args.strike, args.right])
    if is_option_order:
        if args.product_type != 15:
            print("错误: 传入期权字段时，必须指定 --product-type 15", file=sys.stderr)
            sys.exit(1)
        missing = [
            name
            for name, value in [("--expiry", args.expiry), ("--strike", args.strike), ("--right", args.right)]
            if not value
        ]
        if missing:
            print(f"错误: 期权校验必须同时提供 {' / '.join(missing)}", file=sys.stderr)
            sys.exit(1)

    right = args.right.upper() if args.right else None
    if right and right not in OPTION_RIGHTS:
        print("错误: --right 仅支持 CALL 或 PUT", file=sys.stderr)
        sys.exit(1)

    client = get_client(args.api_key, args.base_url, args.sdk_type)
    sub_id = args.sub_account_id or get_sub_account_id(client)

    kwargs = dict(
        sub_account_id=sub_id,
        stock_code=args.stock,
        order_type=order_type,
        market_code=args.market,
        direction=direction,
    )
    if args.price:
        kwargs["price"] = args.price
    if args.quantity:
        kwargs["quantity"] = args.quantity
    if args.trig_price:
        kwargs["trig_price"] = args.trig_price
    if args.time_in_force is not None:
        kwargs["time_in_force"] = args.time_in_force
    if args.client_id is not None:
        kwargs["client_id"] = args.client_id
    if args.product_type is not None:
        kwargs["product_type"] = args.product_type
    if args.expiry:
        kwargs["expiry"] = args.expiry
    if args.strike:
        kwargs["strike"] = args.strike
    if args.right:
        kwargs["right"] = right

    result = client.trade.get_bid_ask_info(**kwargs)

    if args.lot_size_only:
        data = result.get("data", result)
        lot_size = data.get("lotSize", "N/A")
        print(lot_size)
        return

    dump_json(result)


if __name__ == "__main__":
    main()
