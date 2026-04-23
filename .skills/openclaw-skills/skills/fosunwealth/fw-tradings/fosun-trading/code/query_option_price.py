#!/usr/bin/env python3
"""查询期权行情。

期权代码格式示例:
  "usAAPL 20260320 270.0 CALL"

用法:
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_option_price.py quote "usAAPL 20260320 270.0 CALL"
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_option_price.py orderbook "usAAPL 20260320 270.0 CALL"
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_option_price.py kline "usAAPL 20260320 270.0 CALL" --ktype day -n 10
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_option_price.py tick "usAAPL 20260320 270.0 CALL" -n 20
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python query_option_price.py day-min "usAAPL 20260320 270.0 CALL" --days 3
"""

import argparse

from _client import add_common_args, dump_market_json, get_client


def cmd_quote(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    dump_market_json(client.optmarket.quote(codes=args.codes, fields=args.fields))


def cmd_orderbook(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    dump_market_json(client.optmarket.orderbook(args.code))


def cmd_kline(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    dump_market_json(
        client.optmarket.kline(
            args.code,
            ktype=args.ktype,
            end_time=args.end_time,
            interval=args.interval,
            num=args.num,
            start_time=args.start_time,
            suspension=args.suspension,
            time=args.time,
        )
    )


def cmd_tick(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    dump_market_json(client.optmarket.tick(args.code, count=args.num, id=args.start_id))


def cmd_day_min(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    dump_market_json(client.optmarket.day_min(args.code, num=args.days))


def main():
    parser = argparse.ArgumentParser(description="查询期权行情（optmarket）")
    add_common_args(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    p_quote = sub.add_parser("quote", help="期权批量报价")
    p_quote.add_argument(
        "codes", nargs="+", help='期权代码列表，如 "usAAPL 20260320 270.0 CALL"'
    )
    p_quote.add_argument("--fields", nargs="*", help="指定返回字段")
    p_quote.set_defaults(func=cmd_quote)

    p_ob = sub.add_parser("orderbook", help="期权盘口")
    p_ob.add_argument("code", help='期权代码，如 "usAAPL 20260320 270.0 CALL"')
    p_ob.set_defaults(func=cmd_orderbook)

    p_kl = sub.add_parser("kline", help="期权 K 线")
    p_kl.add_argument("code", help='期权代码，如 "usAAPL 20260320 270.0 CALL"')
    p_kl.add_argument("--ktype", default="day", help="K 线类型，如 day / 1 / 5 / 15")
    p_kl.add_argument("-n", "--num", type=int, default=10, help="返回条数")
    p_kl.add_argument("--time", type=int, help="指定时间戳")
    p_kl.add_argument("--start-time", type=int, help="开始时间戳")
    p_kl.add_argument("--end-time", type=int, help="结束时间戳")
    p_kl.add_argument("--interval", type=int, help="K 线间隔")
    p_kl.add_argument("--suspension", type=int, help="停牌处理方式")
    p_kl.set_defaults(func=cmd_kline)

    p_tick = sub.add_parser("tick", help="期权逐笔成交")
    p_tick.add_argument("code", help='期权代码，如 "usAAPL 20260320 270.0 CALL"')
    p_tick.add_argument("-n", "--num", type=int, default=20, help="返回条数")
    p_tick.add_argument("--start-id", type=int, default=-1, help="起始 ID，-1 为最新")
    p_tick.set_defaults(func=cmd_tick)

    p_day = sub.add_parser("day-min", help="期权多日分时")
    p_day.add_argument("code", help='期权代码，如 "usAAPL 20260320 270.0 CALL"')
    p_day.add_argument("--days", type=int, default=5, help="查询天数 1~10")
    p_day.set_defaults(func=cmd_day_min)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
