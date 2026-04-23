#!/usr/bin/env python3
"""改单脚本。

用法:
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python modify_order.py --order-id 123456 --modify-type 1 --price 351.00
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python modify_order.py --order-id 123456 --modify-type 1 --quantity 200 --price 351.00
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python modify_order.py --order-id 123456 --modify-type 2 --trig-price 350.00
"""

import argparse
import sys

from _client import add_common_args, dump_json, get_client, get_sub_account_id


def main():
    parser = argparse.ArgumentParser(description="改单（普通订单/条件单）")
    add_common_args(parser)
    parser.add_argument("--order-id", required=True, help="订单 ID")
    parser.add_argument("--modify-type", required=True, type=int, choices=[1, 2], help="1=普通订单参数修改 2=条件单参数修改")
    parser.add_argument("--client-id", type=int, help="客户 ID")
    parser.add_argument("--quantity", help="修改后的委托数量")
    parser.add_argument("--price", help="修改后的委托价格")
    parser.add_argument("--trig-price", help="触发价")
    parser.add_argument("--tail-type", type=int, help="跟踪止损类型")
    parser.add_argument("--tail-amount", help="跟踪止损固定价差")
    parser.add_argument("--tail-pct", help="跟踪止损百分比")
    parser.add_argument("--spread", help="价差")
    parser.add_argument("--profit-trig-price", help="止盈触发价")
    parser.add_argument("--profit-quantity", help="止盈数量")
    parser.add_argument("--stop-loss-trig-price", help="止损触发价")
    parser.add_argument("--stop-loss-quantity", help="止损数量")
    parser.add_argument("--product-type", type=int, help="产品类型，如 15=期权")
    parser.add_argument("--apply-account-id", help="申请账户 ID")

    args = parser.parse_args()

    if not any(
        value is not None
        for value in [
            args.quantity,
            args.price,
            args.trig_price,
            args.tail_type,
            args.tail_amount,
            args.tail_pct,
            args.spread,
            args.profit_trig_price,
            args.profit_quantity,
            args.stop_loss_trig_price,
            args.stop_loss_quantity,
        ]
    ):
        print("错误: 至少需要传入一个修改字段，如 --price / --quantity / --trig-price", file=sys.stderr)
        sys.exit(1)

    client = get_client(args.api_key, args.base_url, args.sdk_type)
    sub_id = args.sub_account_id or get_sub_account_id(client)

    result = client.trade.order_modify(
        sub_account_id=sub_id,
        order_id=args.order_id,
        modify_type=args.modify_type,
        client_id=args.client_id,
        quantity=args.quantity,
        price=args.price,
        trig_price=args.trig_price,
        tail_type=args.tail_type,
        tail_amount=args.tail_amount,
        tail_pct=args.tail_pct,
        spread=args.spread,
        profit_trig_price=args.profit_trig_price,
        profit_quantity=args.profit_quantity,
        stop_loss_trig_price=args.stop_loss_trig_price,
        stop_loss_quantity=args.stop_loss_quantity,
        product_type=args.product_type,
        apply_account_id=args.apply_account_id,
    )
    dump_json(result)


if __name__ == "__main__":
    main()
