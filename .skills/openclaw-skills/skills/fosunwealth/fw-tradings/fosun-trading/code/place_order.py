#!/usr/bin/env python3
"""股票下单，支持普通单、条件单、跟踪止损单、止盈止损组合单和期权单，覆盖港/美/A 股市场。

订单类型:
  auction_limit (1)  竞价限价单（港股）
  auction       (2)  竞价单（港股）
  limit         (3)  限价单
  enhanced_limit(4)  增强限价单
  special_limit (5)  特别限价单
  dark          (6)  暗盘订单
  market        (9)  市价单
  stop_loss_limit (31) 止损限价单
  take_profit_limit (32) 止盈限价单
  trailing_stop (33) 跟踪止损单
  take_profit_stop_loss (35) 止盈止损单

用法:
  # 港股限价买入
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock 00700 --direction buy --quantity 100 --price 350.000 --order-type limit

  # 港股市价买入
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock 00700 --direction buy --quantity 100 --order-type market

  # 美股市价买入（盘中，不需要 price）
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock AAPL --market us --direction buy --quantity 5 --order-type market

  # 美股限价卖出
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock AAPL --market us --direction sell --quantity 5 --price 180.00 --currency USD --order-type limit

  # 美股盘前盘后限价买入
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock AAPL --market us --direction buy --quantity 5 --order-type limit --price 180.00 --time-in-force 2

  # A 股（港股通）限价买入
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock 600519 --market sh --direction buy --quantity 100 --price 1800.00 --order-type limit

  # 港股止损限价单
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock 00700 --direction sell --quantity 100 --order-type stop_loss_limit --price 380.000 --trig-price 385.000

  # 港股跟踪止损单（按比例）
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock 00700 --direction sell --quantity 100 --order-type trailing_stop --tail-type 2 --tail-pct 0.05

  # 港股止盈止损组合单
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock 00700 --direction sell --quantity 100 --order-type take_profit_stop_loss --price 400.000 --profit-price 420.000 --profit-quantity 100 --stop-loss-price 390.000 --stop-loss-quantity 100

  # 美股期权限价买入
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock AAPL --market us --direction buy --quantity 1 --order-type limit --price 5.50 --product-type 15 --expiry 20260630 --strike 200.00 --right CALL

  # 下单前校验（不实际下单）
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python place_order.py --stock 00700 --direction buy --quantity 100 --price 350.000 --order-type limit --check-only
"""

import argparse
import sys
from _client import get_client, get_sub_account_id, dump_json, add_common_args


DIRECTION_MAP = {"buy": 1, "sell": 2, "1": 1, "2": 2}

MARKET_CURRENCY = {"hk": "HKD", "us": "USD", "sh": "CHY", "sz": "CHY"}

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

PRICE_NOT_REQUIRED = {2, 9, 33}
TRIGGER_PRICE_REQUIRED = {31, 32}
OPTION_RIGHTS = {"CALL", "PUT"}


def main():
    parser = argparse.ArgumentParser(
        description="股票下单（支持普通单/条件单/跟踪止损单/止盈止损组合单/期权单）",
    )
    add_common_args(parser)

    parser.add_argument("--stock", required=True, help="股票代码（不含市场前缀），如 00700 / AAPL / 600519")
    parser.add_argument("--direction", required=True, help="方向: buy / sell（或 1 / 2）")
    parser.add_argument("--quantity", required=True, help="委托数量")
    parser.add_argument(
        "--order-type", required=True,
        help="订单类型: auction_limit(1) / auction(2) / limit(3) / enhanced_limit(4) / special_limit(5) / dark(6) / market(9) / stop_loss_limit(31) / take_profit_limit(32) / trailing_stop(33) / take_profit_stop_loss(35)",
    )
    parser.add_argument("--price", help="委托价格（市价单可不传；港股 3 位小数，美股 2 位小数，A 股 2 位小数）")
    parser.add_argument("--market", default="hk", choices=["hk", "us", "sh", "sz"],
                        help="市场: hk(默认) / us / sh / sz")
    parser.add_argument("--currency", help="币种（默认根据市场自动选择: HKD/USD/CHY）")
    parser.add_argument("--check-only", action="store_true", help="仅查询买卖信息，不实际下单")
    parser.add_argument("--exp-type", type=int, help="订单时效类型，如 1=当日有效")
    parser.add_argument(
        "--time-in-force",
        type=int,
        choices=[0, 2, 4],
        default=0,
        help="时段控制: 0=当日有效 2=允许美股盘前盘后 4=允许夜盘",
    )
    parser.add_argument("--client-id", type=int, help="客户 ID")
    parser.add_argument("--apply-account-id", help="下单申购账号")
    parser.add_argument("--short-sell-type", help="沽空类型，如 A/B/C/F/M/N/S/Y")
    parser.add_argument("--trig-price", help="条件单触发价，止损/止盈单必填")
    parser.add_argument("--tail-type", type=int, choices=[1, 2], help="跟踪止损类型: 1=金额 2=比例")
    parser.add_argument("--tail-amount", help="跟踪止损固定价差")
    parser.add_argument("--tail-pct", help="跟踪止损百分比")
    parser.add_argument("--spread", help="追踪止损单价差")
    parser.add_argument("--profit-price", help="止盈触发价格，止盈止损组合单必填")
    parser.add_argument("--profit-quantity", help="止盈触发数量，止盈止损组合单必填")
    parser.add_argument("--stop-loss-price", help="止损触发价格，止盈止损组合单必填")
    parser.add_argument("--stop-loss-quantity", help="止损触发数量，止盈止损组合单必填")
    parser.add_argument("--product-type", type=int, help="产品类型，如 15=期权")
    parser.add_argument("--expiry", help="期权到期日，如 20260327")
    parser.add_argument("--strike", help="期权行权价")
    parser.add_argument("--right", help="期权方向，如 CALL / PUT")

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
              file=sys.stderr)
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

    if order_type not in PRICE_NOT_REQUIRED and not args.price:
        print(f"错误: {ORDER_TYPE_LABELS[order_type]}必须提供 --price 参数", file=sys.stderr)
        sys.exit(1)

    if order_type in TRIGGER_PRICE_REQUIRED and not args.trig_price:
        print(f"错误: {ORDER_TYPE_LABELS[order_type]}必须提供 --trig-price 参数", file=sys.stderr)
        sys.exit(1)

    if order_type == 33:
        if args.tail_type is None:
            print("错误: 跟踪止损单必须提供 --tail-type（1=金额，2=比例）", file=sys.stderr)
            sys.exit(1)
        if args.tail_type == 1 and not args.tail_amount:
            print("错误: 跟踪止损单在 --tail-type 1 时必须提供 --tail-amount", file=sys.stderr)
            sys.exit(1)
        if args.tail_type == 2 and not args.tail_pct:
            print("错误: 跟踪止损单在 --tail-type 2 时必须提供 --tail-pct", file=sys.stderr)
            sys.exit(1)

    if order_type == 35:
        missing = [
            name
            for name, value in [
                ("--profit-price", args.profit_price),
                ("--profit-quantity", args.profit_quantity),
                ("--stop-loss-price", args.stop_loss_price),
                ("--stop-loss-quantity", args.stop_loss_quantity),
            ]
            if not value
        ]
        if missing:
            print(f"错误: 止盈止损单必须同时提供 {' / '.join(missing)}", file=sys.stderr)
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
            print(f"错误: 期权单必须同时提供 {' / '.join(missing)}", file=sys.stderr)
            sys.exit(1)

    right = args.right.upper() if args.right else None
    if right and right not in OPTION_RIGHTS:
        print("错误: --right 仅支持 CALL 或 PUT", file=sys.stderr)
        sys.exit(1)

    currency = args.currency or MARKET_CURRENCY.get(args.market, "HKD")

    client = get_client(args.api_key, args.base_url, args.sdk_type)
    sub_id = args.sub_account_id or get_sub_account_id(client)

    if args.check_only:
        kwargs = dict(
            sub_account_id=sub_id,
            stock_code=args.stock,
            order_type=order_type,
            market_code=args.market,
            direction=direction,
        )
        if args.quantity:
            kwargs["quantity"] = args.quantity
        if args.price:
            kwargs["price"] = args.price
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
        dump_json(result)
        return

    kwargs = dict(
        sub_account_id=sub_id,
        stock_code=args.stock,
        direction=direction,
        order_type=order_type,
        quantity=args.quantity,
        market_code=args.market,
        currency=currency,
    )
    if args.price:
        kwargs["price"] = args.price
    if args.exp_type is not None:
        kwargs["exp_type"] = args.exp_type
    if args.time_in_force is not None:
        kwargs["time_in_force"] = args.time_in_force
    if args.client_id is not None:
        kwargs["client_id"] = args.client_id
    if args.apply_account_id:
        kwargs["apply_account_id"] = args.apply_account_id
    if args.short_sell_type:
        kwargs["short_sell_type"] = args.short_sell_type
    if args.trig_price:
        kwargs["trig_price"] = args.trig_price
    if args.tail_type is not None:
        kwargs["tail_type"] = args.tail_type
    if args.tail_amount:
        kwargs["tail_amount"] = args.tail_amount
    if args.tail_pct:
        kwargs["tail_pct"] = args.tail_pct
    if args.spread:
        kwargs["spread"] = args.spread
    if args.profit_price:
        kwargs["profit_trig_price"] = args.profit_price
    if args.profit_quantity:
        kwargs["profit_quantity"] = args.profit_quantity
    if args.stop_loss_price:
        kwargs["stop_loss_trig_price"] = args.stop_loss_price
    if args.stop_loss_quantity:
        kwargs["stop_loss_quantity"] = args.stop_loss_quantity
    if args.product_type is not None:
        kwargs["product_type"] = args.product_type
    if args.expiry:
        kwargs["expiry"] = args.expiry
    if args.strike:
        kwargs["strike"] = args.strike
    if args.right:
        kwargs["right"] = right

    order = client.trade.create_order(**kwargs)
    dump_json(order)


if __name__ == "__main__":
    main()
