#!/usr/bin/env python3
"""撤销订单（支持港/美/A 股）。

用法:
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python cancel_order.py ORDER_ID
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python cancel_order.py ORDER_ID --sub-account-id 366226737
"""

import argparse
from _client import get_client, get_sub_account_id, dump_json, add_common_args


def main():
    parser = argparse.ArgumentParser(description="撤销订单（港/美/A 股通用）")
    add_common_args(parser)
    parser.add_argument("order_id", help="要撤销的订单 ID")
    parser.add_argument("--client-id", type=int, help="客户 ID")
    parser.add_argument("--product-type", type=int, help="产品类型，如 15=期权")
    parser.add_argument("--apply-account-id", help="申请账户 ID")

    args = parser.parse_args()

    client = get_client(args.api_key, args.base_url, args.sdk_type)
    sub_id = args.sub_account_id or get_sub_account_id(client)

    result = client.trade.cancel_order(
        order_id=args.order_id,
        sub_account_id=sub_id,
        client_id=args.client_id,
        product_type=args.product_type,
        apply_account_id=args.apply_account_id,
    )
    dump_json(result)


if __name__ == "__main__":
    main()
