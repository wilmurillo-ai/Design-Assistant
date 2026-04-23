#!/usr/bin/env python3
"""行情推送订阅脚本。

说明:
  - 这是长连接脚本，会持续接收 SDK 打印出的推送消息。
  - 默认订阅 30 秒后退出；可通过 --duration 0 保持常驻。
  - 市场状态主题使用市场代码，如 hk / us / cn；其他主题使用证券代码，如 hk00700 / usAAPL。

用法:
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python market_push.py quote hk00700 usAAPL --duration 30
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python market_push.py orderbook hk00700 --duration 10
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python market_push.py market-status hk us cn --duration 15
"""

import argparse
import asyncio

from _client import add_common_args, get_client


async def _subscribe_and_wait(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    await client.market_push.connect()
    try:
        if args.command == "quote":
            await client.market_push.subscribeQuote(args.codes)
        elif args.command == "min":
            await client.market_push.subscribeMin(args.codes)
        elif args.command == "tick":
            await client.market_push.subscribeTick(args.codes)
        elif args.command == "orderbook":
            await client.market_push.subscribeOrderbook(args.codes)
        elif args.command == "broker":
            await client.market_push.subscribeBrokerQueue(args.codes)
        elif args.command == "market-status":
            await client.market_push.subscribeMarketStatus(args.codes)

        if args.duration == 0:
            await asyncio.Event().wait()
        else:
            await asyncio.sleep(args.duration)

        if args.auto_unsubscribe:
            if args.command == "quote":
                await client.market_push.unsubscribeQuote(args.codes)
            elif args.command == "min":
                await client.market_push.unsubscribeMin(args.codes)
            elif args.command == "tick":
                await client.market_push.unsubscribeTick(args.codes)
            elif args.command == "orderbook":
                await client.market_push.unsubscribeOrderbook(args.codes)
            elif args.command == "broker":
                await client.market_push.unsubscribeBrokerQueue(args.codes)
            elif args.command == "market-status":
                await client.market_push.unsubscribeMarketStatus(args.codes)
    finally:
        await client.market_push.close()


def _add_topic_parser(sub, name, help_text):
    p = sub.add_parser(name, help=help_text)
    p.add_argument("codes", nargs="+", help="订阅代码列表")
    p.add_argument("--duration", type=int, default=30, help="订阅持续秒数；0 表示常驻")
    p.add_argument("--auto-unsubscribe", action="store_true", help="退出前自动退订")
    p.set_defaults(func=lambda args: asyncio.run(_subscribe_and_wait(args)))


def main():
    parser = argparse.ArgumentParser(description="行情推送订阅（WebSocket）")
    add_common_args(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    _add_topic_parser(sub, "quote", "订阅报价推送")
    _add_topic_parser(sub, "min", "订阅分时推送")
    _add_topic_parser(sub, "tick", "订阅逐笔成交推送")
    _add_topic_parser(sub, "orderbook", "订阅盘口推送")
    _add_topic_parser(sub, "broker", "订阅经纪队列推送")
    _add_topic_parser(sub, "market-status", "订阅市场状态推送")

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
